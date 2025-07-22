def time_to_seconds(time_str: str) -> int:
    """
    Convert HH:MM:SS time string to total seconds.
    :param time_str: time string e.g. '10:30:00'
    :return: total seconds as int
    """
    parts = time_str.split(":")
    h = int(parts[0])
    m = int(parts[1])
    s = int(parts[2])
    return (h * 3600) + (m * 60) + s

def seconds_to_time(seconds: int) -> str:
    """
    Convert seconds to HH:MM:SS string.
    :param seconds: total seconds
    :return: time string
    """
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

def add_time(time_str: str, seconds: int) -> str:
    """
    Add seconds to a HH:MM:SS time string.
    :param time_str: time string
    :param seconds: seconds to add
    :return: new time string
    """
    total_seconds = time_to_seconds(time_str) + seconds
    return seconds_to_time(total_seconds)

def subtract_time(time_str: str, seconds: int) -> str:
    """
    Subtract seconds from a HH:MM:SS time string.
    :param time_str: time string
    :param seconds: seconds to subtract
    :return: new time string
    """
    total_seconds = time_to_seconds(time_str)
    new_seconds = max(0, total_seconds - seconds)
    return seconds_to_time(new_seconds)

def is_time_before(time_str1: str, time_str2: str) -> bool:
    """
    Returns True if time_str1 is strictly before time_str2.
    Both strings should be in HH:MM:SS format.

    :param time_str1: First time string
    :param time_str2: Second time string
    :return: True if time_str1 < time_str2, else False
    """
    seconds1 = time_to_seconds(time_str1)
    seconds2 = time_to_seconds(time_str2)

    return seconds1 < seconds2

def time_difference(start_time: str, end_time: str) -> int:
    """
    Calculate difference in seconds between two HH:MM:SS times.
    :param start_time: HH:MM:SS string
    :param end_time: HH:MM:SS string
    :return: difference in seconds (int)
    """
    start_sec = time_to_seconds(start_time)
    end_sec = time_to_seconds(end_time)
    return max(0, end_sec - start_sec)

def time_to_minutes(time_str: str) -> int:
    """
    Convert HH:MM:SS time string to total minutes.
    :param time_str: time string
    :return: total minutes as int
    """
    return time_to_seconds(time_str) // 60
