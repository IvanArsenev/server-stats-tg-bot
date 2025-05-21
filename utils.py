"""Module for getting system information including memory usage and processor details."""

import wmi
import psutil


def get_memory_usage():
    """
    Get system memory usage information.

    Returns:
        tuple: Used memory in GB: float, total memory in GB: float, usage percentage: float
    """
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024 ** 3)
    used_gb = mem.used / (1024 ** 3)
    percent = mem.percent
    return used_gb, total_gb, percent


def get_processors_info():
    """
    Get processors and temperature information.

    Returns:
        list: Processors info and temperatures in the following format:
            [processor1_name: str, processor1_load: int, processor1_frequency: int,
             processor1_temp: float, processor2_name: str, processor2_load: int,
             processor2_frequency: int, processor2_temp: float, motherboard_temp: float
            ]
    """
    wmi_connection = wmi.WMI(namespace="root\\OpenHardwareMonitor")
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

    avg_cpu1_temp = (round(sum(cpu_1_cores_temp) / len(cpu_1_cores_temp), 1)
                     if cpu_1_cores_temp else 0)
    avg_cpu2_temp = (round(sum(cpu_2_cores_temp) / len(cpu_2_cores_temp), 1)
                     if cpu_2_cores_temp else 0)
    avg_motherboard_temp = (round(sum(motherboard_temp) / len(motherboard_temp), 1)
                           if motherboard_temp else 0)

    return [
        processors[0].Name.strip(),
        processors[0].LoadPercentage,
        processors[0].CurrentClockSpeed,
        avg_cpu1_temp,
        processors[1].Name.strip(),
        processors[1].LoadPercentage,
        processors[1].CurrentClockSpeed,
        avg_cpu2_temp,
        avg_motherboard_temp
    ]
