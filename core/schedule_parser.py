import sys
from typing import List, Dict, Any
from utils.time_utils import is_time_before
from core.buildings import get_building_coordinates
import pandas as pd

def load_schedule(csv_path: str = "data/class_schedule.txt") -> List[Dict[str, Any]]:
    """
    Load user's class schedule from a CSV file into .
    :param csv_path: path to schedule CSV file
    :return: list of class dicts with time, building, day info
    """
    required_columns = ["course_code", "class_name", "day", "start_time", "end_time", "building"]
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Schedule file not found: {csv_path}")
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

def extract_unique_building_names(schedule_data: List[Dict[str, Any]]) -> List[str]:
    """
    Extracts a list of unique building names from the schedule data.

    :param schedule_data: list of class records from validated schedule
    :return: list of unique building names
    """
    result = []

    for item in schedule_data:
        building = item.get("building")
        already_in_result = False

        for existing in result:
            if building == existing:
                already_in_result = True
                break
        if building and not already_in_result:
            result.append(building)

    return result


def apply_matched_building_names(schedule_data: List[Dict[str, Any]],
                                 name_mapping: Dict[str, str]
                                 ) -> List[Dict[str, Any]]:
    """
    Updates the building field in schedule_data based on correct name mapping to be used for
    the rest of the program

    :param schedule_data: List of dicts, each representing a class with a building key
    :param name_mapping: Dict mapping user input building names to official building names in buildings.geojson
    :return: Updated list of dicts with corrected building names
    """
    updated_schedule = []

    for user_class in schedule_data:
        original_building = user_class.get("building")
        corrected_building = name_mapping.get(original_building)

        updated_item = dict(user_class)
        updated_item["building"] = corrected_building
        updated_schedule.append(updated_item)

    return updated_schedule

def update_schedule_with_coordinates(schedule_data: List[Dict[str, Any]], buildings_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Adds two new rows to the schedule data with every building's unique coordinates and returns the schedule as
    an updated list of dictionaries for every class
    :param schedule_data: the validated and building-matched user schedule
    :param buildings_data: the list of building dictionaries
    :return: an updated schedule including the coordinates of every building
    """
    updated_schedule = []

    for user_class in schedule_data:
        user_building = user_class.get("building")
        coords_for_building = get_building_coordinates(user_building, buildings_data)

        if "error" in coords_for_building:
            print(f"Error attaching coordinates for '{user_building}': {coords_for_building['error']}")
            sys.exit(1)

        updated_class = dict(user_class)
        updated_class["lat"] = coords_for_building["lat"]
        updated_class["long"] = coords_for_building["long"]
        updated_schedule.append(updated_class)

    return updated_schedule
