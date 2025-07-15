from typing import List, Dict, Any

def load_and_validate_schedule() -> List[Dict[str, any]]:
    """
    Loads the class schedule CSV and validates its fields (day names, time format, start < end).
    If validation fails, exits the program.

    :return: List of validated class records (dicts).
    """
    pass

def match_and_confirm_buildings(schedule_data: List[Dict[str, Any]], buildings_data: List[Dict[str, Any]]) -> Dict[
    str, str]:
    """
    Extracts user-provided building names from the schedule, performs exact and fuzzy matching
    against official building names, and prompts the user for confirmation if no exact match.

    :param schedule_data: The validated schedule data.
    :param buildings_data: The official buildings list from GeoJSON.
    :return: A name mapping dict of {user_input_name -> official_building_name}.
    """
    pass

def update_schedule_with_matches(schedule_data: List[Dict[str, Any]], name_mapping: Dict[str, str]) -> List[
    Dict[str, Any]]:
    """
    Applies the building name mappings to the schedule so that all buildings align
    with official names.

    :param schedule_data: Original or validated schedule data.
    :param name_mapping: Dict of user input -> official building names.
    :return: Updated schedule data with fixed building names.
    """
    pass


def run_schedule_validation() -> List[Dict[str, Any]]:
    """
    High-level function that runs the complete flow of loading and validating the schedule, matches building data,
    confirms building names, and returns an updated schedule to be used by the program:

    :return: an updated and validated user schedule
    """
    pass