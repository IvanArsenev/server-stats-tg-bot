"""Module for getting system information including memory usage and processor details."""

import wmi  # pylint: disable=unused-import
import psutil  # pylint: disable=unused-import


def get_memory_usage():
    """
    Get system memory usage information.

    Returns:
        tuple: Used memory in GB: float, total memory in GB: float, usage percentage: float
    """
    return 50.5, 60.5, 70.5


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
    return [
        'testtesttesttest',
        50,
        3000,
        50.5,
        'testtesttesttest',
        50,
        3000,
        50.5,
        50.5
    ]
