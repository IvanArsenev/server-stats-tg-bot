@echo off

echo Creating an environment
python -m venv .venv

echo Switching to the created environment
call .venv\Scripts\activate.bat

echo Installing dependencies
pip install pywin32==310 wmi==1.5.1 uvicorn==0.34.2 fastapi==0.115.12 psutil==7.0.0

echo Launching the service
start /B python .\system_info_api.py

echo Assembling and launching containers
docker-compose up -d --build

echo Done!
pause
