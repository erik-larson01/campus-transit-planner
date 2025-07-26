import sys
from typing import List, Dict, Any, Optional
import core.schedule_parser as schedule_parser
import core.building_matcher as buildings
import utils.time_utils as time

def load_and_validate_schedule() -> List[Dict[str, any]]:
    """
    Loads the class schedule CSV and validates its fields (day names, time format, start < end).
    If validation fails, exits the program.

    :return: List of validated class records (dicts).
    """
    try:
        print("Loading data/class_schedule.txt as a CSV...")
        raw_schedule_data = schedule_parser.load_schedule()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error loading schedule: {e}")
        sys.exit(1)

    try:
        print("Attempting to validate schedule data...")
        validated_schedule = schedule_parser.validate_schedule_data(raw_schedule_data)

        if len(validated_schedule) != len(raw_schedule_data):
            print(f"Schedule validation failed: {len(raw_schedule_data) - len(validated_schedule)} rows invalid.")
            print("Please fix your schedule CSV and try again.")
            sys.exit(1)

        if not validated_schedule:
            print("Validation failed: No valid schedule entries found.")
            sys.exit(1)
    except Exception as e:
        print(f"Error validating schedule: {e}")
        sys.exit(1)

    print("Validation successful!")
    return validated_schedule


def match_and_confirm_buildings(user_buildings: List[str], buildings_data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Performs exact and fuzzy matching against official building names, and prompts
    the user for confirmation if no exact match.

    :param buildings_data: The official buildings list from GeoJSON.
    :param user_buildings: List of unique building names extracted from the schedule
    :return: A name mapping dict of {user_input_name -> official_building_name}.
    """
    print("Mapping user building names to official building names in buildings.geojson...")
    match_results = buildings.match_building_names(user_buildings, buildings_data)

    exact_matches = match_results["exact_matches"]
    best_matches = match_results["best_matches"]
    suggestions = match_results["suggestions"]
    unmatched = match_results["unmatched"]

    name_mapping = {}

    # Accept all exact matches first
    for user_input, matched_name in exact_matches.items():
        name_mapping[user_input] = matched_name

    # Prompt for best fuzzy matches
    for user_input, best_match in best_matches.items():
        print(f"\nDid you mean '{best_match}' for '{user_input.strip()}'? (Y/n): ")
        choice = input().strip().lower()

        if choice in ("y", "yes", ""):
            name_mapping[user_input] = best_match
        else:
            # Show other suggestions
            alt_options = suggestions.get(user_input, [])
            if not alt_options:
                print(f"No other suggestions found for '{user_input}'. Please update this value in your CSV.")
                continue

            print(f"Other suggestions for '{user_input}':")
            i = 1
            for option in alt_options:
                print(f"{i}. {option}")
                i += 1

            # Ensure a user makes a selection or skips to change their schedule
            while True:
                try:
                    selected = int(input("Enter number of correct building (or 0 to skip): "))
                    if selected == 0:
                        print(f"No match selected for '{user_input}'. Please update your CSV and try again.")
                        sys.exit(1)

                    elif 1 <= selected <= len(alt_options):
                        selected_name = alt_options[selected - 1]
                        name_mapping[user_input] = selected_name
                        break
                    else:
                        print("Number out of range. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

    # Handle completely unmatched names
    for unmatched_name in unmatched:
        print(f"\nBuilding '{unmatched_name}' could not be matched to any known building.")
        print("Please fix this in your CSV and run the program again.")

    if unmatched:
        sys.exit(1)
    return name_mapping

def run_schedule_validation() -> List[Dict[str, Any]]:
    """
    High-level function that runs the complete flow of loading and validating the schedule, matches building data,
    confirms building names, and returns an updated schedule to be used by the program:

    :return: an updated and validated user schedule with confirmed building names
    """
    # Load schedule and building data
    print("Starting schedule validation and building name matching...")
    validated_schedule_data = load_and_validate_schedule()
    print(f"Loaded {len(validated_schedule_data)} valid schedule entries.")
    try:
        buildings_data = buildings.load_buildings()
        print(f"Loaded {len(buildings_data)} official campus buildings.")
        print()
    except FileNotFoundError as e:
        print(f"Error loading buildings: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error parsing buildings file: {e}")
        sys.exit(1)

    # Extract building names
    unique_user_buildings = schedule_parser.extract_unique_building_names(validated_schedule_data)

    print(f"Found {len(unique_user_buildings)} unique building names in your schedule:")
    for building in unique_user_buildings:
        print(f" - {building}")

    # Apply final names to schedule data
    mapped_buildings = match_and_confirm_buildings(unique_user_buildings, buildings_data)

    print("\nBuilding name mapping summary:")
    for user_input, official_name in mapped_buildings.items():
        print(f" '{user_input}'  -->  '{official_name}'")

    final_schedule = schedule_parser.apply_matched_building_names(validated_schedule_data, mapped_buildings)

    print(f"\nSchedule updated with confirmed building names.\n")
    return final_schedule


def get_user_walking_preference() -> float:
    """
    Gets a user's max walking distance to an origin bus stop, with the default set to 0.5mi or 800m
    :return: a user's set max walking distance
    """
    MIN_DISTANCE = 10.0
    MAX_DISTANCE = 1000.0
    DEFAULT_DISTANCE = 500.0

    print("To help filter bus stops based on your preferences, how far are you willing to walk to bus stops?:")
    print("- 400m (5 min walk)")
    print("- 600m (7-8 min walk)")
    print("- 800m (10 min walk)")
    print("- 1000m (12-13 min walk)")

    while True:
        try:
            user_input = input("Enter distance in meters (or press Enter for 500m default): ").strip()

            if not user_input:
                return 500.0

            distance = float(user_input)

            if distance <= 0:
                validated_distance = DEFAULT_DISTANCE
            else:
                validated_distance = max(MIN_DISTANCE, min(distance, MAX_DISTANCE))

            if validated_distance != distance:
                print(f"Distance adjusted to {validated_distance}m (within valid range {MIN_DISTANCE}-{MAX_DISTANCE}m)")

            return validated_distance

        except ValueError:
            print("Please enter a valid number or press Enter for default.")

def prompt_user_to_select_trip(final_trips: List[Dict[str, Any]], class_entry: Dict[str, Any],
                               next_class: Dict[str, Any], walking_option_data) -> Optional[Dict[str, Any]]:
    """
    Display 1-2 best trip options to the user and prompt them to select one.
    :param final_trips: list of 1 or 2 trip dicts
    :param class_entry: dict of origin class data
    :param next_class: dict of next class data
    :param walking_option_data: google API data if a user simply walked between classes
    :return: selected trip dict or None
    """
    walk_trip = None
    leave_by = None

    # Get walking data if it exists
    if walking_option_data:
        walk_time = walking_option_data['duration_value']
        walk_dist_km = walking_option_data['distance_text']
        leave_by = time.subtract_time(next_class['start_time'], walk_time)
        walk_trip = {
            "mode": "walk",
            "leave_by": leave_by,
            "walk_time_min": walk_time // 60,
            "walk_distance_km": walk_dist_km,
            "from": class_entry['building'],
            "to": next_class['building']
        }

    # If walking is the only option, print and return the walking data
    if not final_trips and walk_trip:
        print("\nNo valid trip options found between classes. Walking automatically selected.")
        print(f"\nOption 1: Walk Only")
        print(f"  To arrive at {next_class['building']} by {next_class['start_time']}, you should leave by {leave_by}")
        print(f"    • Walk Time: {walk_trip['walk_time_min']} min")
        print(f"    • Walk Distance: {walk_trip['walk_distance_km']}")
        return walk_trip

    print("\n--- Best Trip Option(s) ---")

    for idx, trip in enumerate(final_trips, start=1):
        strategy = "Earliest Arrival" if idx == 1 else "Shortest Travel Time"
        print(f"\nOption {idx}: {strategy}")
        print(f"  Route: {trip['route_name']}")
        print(f"  Leave {class_entry['building']} by: {trip['time_to_leave']}")
        print(f"  Arrive at {next_class['building']} by: {trip['arrive_at_building_time']}")
        print(f"  Boarding Stop: {trip['origin_stop_name']}")
        print(f"    • Departs from stop at: {trip['origin_departure_time']}")
        print(f"    • Walk Time: {trip['origin_walk_time'] // 60} min, Distance: {trip['origin_walk_distance']}")
        print(f"  Destination Stop: {trip['destination_stop_name']}")
        print(f"    • Arrives to stop at: {trip['destination_arrival_time']}")
        print(f"    • Walk Time: {trip['dest_walk_time_sec'] // 60} min, Distance: {trip['dest_walk_distance']}")
        print(f"  Total Travel Time: {trip['total_travel_time_sec'] // 60} min")

    if walk_trip:
        print(f"\nOption {len(final_trips) + 1}: Walk Only")
        print(f"  To arrive at {next_class['building']} by {next_class['start_time']}, you should leave by {leave_by}")
        print(f"    • Walk Time: {walk_trip['walk_time_min']} min")
        print(f"    • Walk Distance: {walk_trip['walk_distance_km']}")
    else:
        walk_trip = None

    # Prompt user to choose one of the options
    valid_options = []
    for i in range(len(final_trips)):
        valid_options.append(str(i + 1))
    if walk_trip:
        valid_options.append(str(len(valid_options) + 1))

    while True:
        # Ask the user to select an option
        choice = input(f"\nSelect your preferred option ({', '.join(valid_options)}): ").strip()
        if choice in valid_options:
            choice_idx = int(choice) - 1
            if choice_idx < len(final_trips):
                selected = final_trips[choice_idx]
                print(f"\nYou've selected Option {choice}: {selected['route_name']}.")
                return selected
            elif walk_trip and choice == str(len(valid_options)):
                print(f"\nYou selected Option {choice}: Walk Only.")
                return walk_trip
        print("Invalid input. Please enter a valid option.")


def output_final_schedule(results: List[Dict[str, Any]], file_path: str= "output/daily_plan.txt"):
    """
    Outputs the user picked trip options into the terminal as well as to a file daily_plan.txt for easier reading
    :param results: the user's decision options
    :param file_path: the file path of daily_plan.txt
    :return:
    """