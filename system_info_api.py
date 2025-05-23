'''API for getting information about the system: memory usage and processor characteristics.'''


import pythoncom
from fastapi import FastAPI
from pydantic import BaseModel
import wmi
import psutil
import uvicorn

from config import API_HOST, API_PORT

app = FastAPI()


class MemoryUsageResponse(BaseModel):  # pylint: disable=too-few-public-methods
    '''Response model with information about RAM usage.'''
    used_gb: float
    total_gb: float
    percent: float


class ProcessorInfoResponse(BaseModel):  # pylint: disable=too-few-public-methods
    '''Response model with information about processors and component temperatures.'''
    processor1_name: str
    processor1_load: int
    processor1_frequency: int
    processor1_temp: float
    processor2_name: str
    processor2_load: int
    processor2_frequency: int
    processor2_temp: float
    motherboard_temp: float


@app.get('/memory', response_model=MemoryUsageResponse)
def memory_usage():
    '''Returns RAM usage in gigabytes and usage percentage.'''
    mem = psutil.virtual_memory()
    return {
        'used_gb': round(mem.used / (1024 ** 3), 2),
        'total_gb': round(mem.total / (1024 ** 3), 2),
        'percent': mem.percent
    }


@app.get('/processors', response_model=ProcessorInfoResponse)
def processors_info():
    '''Returns information about two processors and the temperature of the motherboard.'''
    pythoncom.CoInitialize()
    try:
        wmi_connection = wmi.WMI(namespace='root\\OpenHardwareMonitor')
        processors = wmi.WMI().Win32_Processor()
        sensors = wmi_connection.Sensor()

        cpu_1_cores_temp = []
        cpu_2_cores_temp = []
        motherboard_temp = []

        for sensor in sensors:
            if sensor.Identifier.startswith('/intelcpu/0/temperature'):
                cpu_1_cores_temp.append(sensor.Value)
            elif sensor.Identifier.startswith('/intelcpu/1/temperature'):
                cpu_2_cores_temp.append(sensor.Value)
            elif sensor.Identifier.startswith('/lpc/nct6779d/temperature'):
                motherboard_temp.append(sensor.Value)

        avg_cpu1_temp = (
            round(sum(cpu_1_cores_temp) / len(cpu_1_cores_temp), 1)
            if cpu_1_cores_temp else None
        )
        avg_cpu2_temp = (
            round(sum(cpu_2_cores_temp) / len(cpu_2_cores_temp), 1)
            if cpu_2_cores_temp else None
        )
        avg_motherboard_temp = (
            round(sum(motherboard_temp) / len(motherboard_temp), 1)
            if motherboard_temp else None
        )

        return {
            'processor1_name': processors[0].Name.strip(),
            'processor1_load': processors[0].LoadPercentage,
            'processor1_frequency': processors[0].CurrentClockSpeed,
            'processor1_temp': avg_cpu1_temp,
            'processor2_name': processors[1].Name.strip(),
            'processor2_load': processors[1].LoadPercentage,
            'processor2_frequency': processors[1].CurrentClockSpeed,
            'processor2_temp': avg_cpu2_temp,
            'motherboard_temp': avg_motherboard_temp
        }
    finally:
        pythoncom.CoUninitialize()


if __name__ == '__main__':
    uvicorn.run(app, host=API_HOST, port=API_PORT)
