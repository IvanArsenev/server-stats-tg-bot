```shell
  git clone https://github.com/IvanArsenev/server-stats-tg-bot.git
```

```shell
  cd .\server-stats-tg-bot\
```

```shell
  python3.11 -m venv .venv
```

```shell
  .\.venv\Scripts\activate
```

```shell
  pip install pywin32==310 wmi==1.5.1 uvicorn==0.34.2 fastapi==0.115.12 psutil==7.0.0
```
CREATE `config.py`
```python
    BOT_TOKEN = ''
    USER_ID = 0
    DF_PATH = 'df_system_stats.csv'
    API_HOST = '192.168.0.*'
    API_PORT = 1111
```

```shell
  python .\system_info_api.py
```

### IN NEW TERMINAL

```shell
  cd .\server-stats-tg-bot\
```

```shell
  .\.venv\Scripts\activate
```

```shell
  docker-compose up -d --build
```
