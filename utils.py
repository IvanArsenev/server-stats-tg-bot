'''Module to get stats from API.'''

import requests

from config import API_HOST, API_PORT

def get_memory_usage_from_api():
    '''
    Получить информацию об использовании памяти через API.

    Returns:
        tuple: used_gb, total_gb, percent
    '''
    response = requests.get(f'http://{API_HOST}:{API_PORT}/memory')
    response.raise_for_status()
    data = response.json()
    return data['used_gb'], data['total_gb'], data['percent']


def get_processors_info_from_api():
    '''
    Получить информацию о процессорах и температуре через API.

    Returns:
        tuple: processor_1_name, processor_1_load, processor_1_frequency, processor_1_temp,
               processor_2_name, processor_2_load, processor_2_frequency, processor_2_temp,
               motherboard_temp
    '''
    response = requests.get(f'http://{API_HOST}:{API_PORT}/processors')
    response.raise_for_status()
    data = response.json()
    return (
        data['processor1_name'], data['processor1_load'], data['processor1_frequency'],
        data['processor1_temp'], data['processor2_name'], data['processor2_load'],
        data['processor2_frequency'], data['processor2_temp'], data['motherboard_temp']
    )
