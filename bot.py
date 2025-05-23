"""Bot module to send periodic system stats with visualizations via Telegram."""

import asyncio
import logging
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile

from config import BOT_TOKEN, USER_ID, DF_PATH
from utils import get_memory_usage_from_api, get_processors_info_from_api
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


def get_status_load(load):
    """Return emoji status based on system load percentage."""
    if load <= 20:
        return '🟢'
    if load <= 40:
        return '🟡'
    if load <= 60:
        return '🟠'
    if load <= 80:
        return '🔴'
    return '⚫'


def get_status_temp(temp):
    """Return emoji status based on temperature."""
    if temp <= 55:
        return '🟢'
    if temp <= 65:
        return '🟡'
    if temp <= 75:
        return '🟠'
    if temp <= 90:
        return '🔴'
    return '⚫'


def generate_stats_graph(df_system_stats):
    """Generate a plot of system stats over the last 24 hours."""
    now = datetime.now()
    start_time = now - timedelta(hours=24)

    df_system_stats['timestamp'] = pd.to_datetime(df_system_stats['timestamp'])
    filtered_df = df_system_stats[df_system_stats['timestamp'] >= start_time]

    if filtered_df.empty:
        logging.warning('Нет данных за последние 24 часа')
        return False

    fig, axes = plt.subplots(4, 1, figsize=(12, 16))
    fig.suptitle('Системные показатели за последние 24 часа', fontsize=16)

    ax = axes[0]
    ax.plot(filtered_df['timestamp'], filtered_df['used_gb'], label='Использовано (GB)')
    ax.plot(filtered_df['timestamp'], filtered_df['total_gb'], label='Всего (GB)')
    ax.fill_between(filtered_df['timestamp'], 0, filtered_df['used_gb'], alpha=0.3)
    ax.set_ylabel('Память (GB)')
    ax.legend()
    ax.grid(True)
    ax.set_title('Использование памяти')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    ax = axes[1]
    for i in [1, 2]:
        ax.plot(filtered_df['timestamp'],
                filtered_df[f'processor_{i}_load'],
                label=filtered_df[f'processor_{i}_name'].iloc[0])
    ax.set_ylabel('Загрузка (%)')
    ax.legend()
    ax.grid(True)
    ax.set_title('Загрузка процессоров')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    ax = axes[2]
    for i in [1, 2]:
        ax.plot(filtered_df['timestamp'],
                filtered_df[f'processor_{i}_temp'],
                label=f'CPU {i} Temp')
    ax.plot(filtered_df['timestamp'], filtered_df['motherboard_temp'], label='Материнская плата')
    ax.set_ylabel('Температура (°C)')
    ax.legend()
    ax.grid(True)
    ax.set_title('Температуры')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    ax = axes[3]
    for i in [1, 2]:
        ax.plot(filtered_df['timestamp'],
                filtered_df[f'processor_{i}_frequency'],
                label=f'CPU {i} Freq')
    ax.set_ylabel('Частота (MHz)')
    ax.legend()
    ax.grid(True)
    ax.set_title('Частота процессоров')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    plt.tight_layout()
    plt.subplots_adjust(top=0.94)
    plt.savefig('system_stats_24h.png')
    return True


def generate_message_text(df_system_stats):
    """Generate a message text with current system stats and update CSV."""
    used_gb, total_gb, percent = get_memory_usage_from_api()
    (
        processor_1_name, processor_1_load, processor_1_frequency, processor_1_temp,
        processor_2_name, processor_2_load, processor_2_frequency, processor_2_temp,
        motherboard_temp
    ) = get_processors_info_from_api()

    record = {
        'timestamp': datetime.now(),
        'used_gb': used_gb,
        'total_gb': total_gb,
        'memory_percent': percent,
        'processor_1_name': processor_1_name[:-9],
        'processor_1_load': processor_1_load,
        'processor_1_frequency': processor_1_frequency,
        'processor_1_temp': processor_1_temp,
        'processor_2_name': processor_2_name[:-9],
        'processor_2_load': processor_2_load,
        'processor_2_frequency': processor_2_frequency,
        'processor_2_temp': processor_2_temp,
        'motherboard_temp': motherboard_temp
    }

    df_system_stats = pd.concat([df_system_stats, pd.DataFrame([record])], ignore_index=True)
    df_system_stats.to_csv(DF_PATH, index=False)

    return f'''
    {get_status_load(percent)} Memory Usage: {used_gb:.2f} GB / {total_gb:.2f} GB ({percent}%)
    ----------------------------------------
    🔲 Processor 1:
     -  📋 Name: {processor_1_name[:-9]}
     -  {get_status_load(processor_1_load)} Load: {processor_1_load}%
     -  〰️ Frequency: {processor_1_frequency} MHz
     -  {get_status_temp(processor_1_temp)} Temperature: {processor_1_temp}°C
    ----------------------------------------
    🔲 Processor 2:
     -  📋 Name: {processor_2_name[:-9]}
     -  {get_status_load(processor_2_load)} Load: {processor_2_load}%
     -  〰️ Frequency: {processor_2_frequency} MHz
     -  {get_status_temp(processor_2_temp)} Temperature: {processor_2_temp}°C
    ----------------------------------------
    {get_status_temp(motherboard_temp)} Motherboard Temperature: {motherboard_temp}°C
    '''


async def send_periodic_message():
    """Send system stats to the user every hour."""
    last_message_id = None
    while True:
        try:
            if last_message_id:
                try:
                    await bot.delete_message(USER_ID, last_message_id)
                    logging.info('Сообщение %s удалено', last_message_id)
                except (TypeError, ValueError) as del_error:
                    logging.error('Ошибка при удалении сообщения: %s', del_error)
            df_system_stats = pd.read_csv(DF_PATH)
            generate_stats_graph(df_system_stats)
            photo = FSInputFile("system_stats_24h.png")
            message = await bot.send_photo(
                USER_ID,
                photo,
                caption=generate_message_text(df_system_stats)
            )
            last_message_id = message.message_id
            logging.info('Сообщение отправлено пользователю %s, ID: %s', USER_ID, last_message_id)
        except Exception as error:  # pylint: disable=broad-exception-caught
            logging.error('Ошибка при отправке сообщения: %s', error)

        await asyncio.sleep(3600)


async def main():
    """Start the bot polling and message sending task."""
    await asyncio.create_task(send_periodic_message())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
