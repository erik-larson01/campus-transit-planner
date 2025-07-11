from typing import List, Dict, Any
from utils.time_utils import is_time_before
import pandas as pd

def load_schedule(csv_path: str = "data/class_schedule.txt") -> List[Dict[str, Any]]:
    """
    Load user's class schedule from a CSV file into .
    :param csv_path: path to schedule CSV file
    :return: list of class dicts with time, building, day info
    """
    required_columns = ["course_code", "class_name", "day", "start_time", "end_time", "building"]
    df = pd.read_csv(csv_path)
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}' in class_schedule.txt.")

    schedule_data = df.to_dict(orient="records")
    return schedule_data


def validate_schedule_data(schedule_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validates each row of schedule data: time format and day.
    :param schedule_data: list of parsed records
    :return: list of validated records to be compared with the original csv
    """
    valid_days = {
        "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday"
    }
    validated = []

    for item in schedule_data:
        day = item["day"].strip().lower()

        if day not in valid_days:
            print(f"Invalid day: {item['day']} in {item}")
            continue

        # Check if both times are in HH:MM:SS format
        start_time = item.get("start_time")
        end_time = item.get("end_time")

        valid_time = True

        for time_str in [start_time, end_time]:
            if time_str.count(":") != 2:
                valid_time = False
                break

            parts = time_str.split(":")
            if len(parts) != 3:
                valid_time = False
                break

            try:
                hour = int(parts[0])
                minute = int(parts[1])
                second = int(parts[2])

                if not (0 <= hour <= 23):
                    valid_time = False
                if not (0 <= minute <= 59):
                    valid_time = False
                if not (0 <= second <= 59):
                    valid_time = False
            except ValueError:
                valid_time = False
                break

        if valid_time:
            if not is_time_before(start_time, end_time):
                print(f"Start time is not before end time in {item}")
                valid_time = False

        if not valid_time:
            print(f"Invalid time format in {item}")
            continue

        # Update day to lowercase for consistency
        item["day"] = day
        validated.append(item)

    return validated