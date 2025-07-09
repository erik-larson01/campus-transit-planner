# TODO: Implement full logic flow from earlier (find stop → route → trip)
# 1. For each class in schedule, find nearby stops
# 2. For each stop, find routes serving it
# 3. For each route, find viable trips before class time
# 4. Find boarding options for the user location
# 5. Calculate journey time and pick best option
# 6. Return summary for all classes

def find_nearby_stops(lat: float, lng: float, stops_data, max_distance: int):
    """
    Find bus stops within max_distance meters of given coordinates.
    :param lat: latitude of reference point
    :param lng: longitude of reference point
    :param stops_data: GTFS stops data
    :param max_distance: max walking distance in meters
    :return: list of nearby stops with distance info
    """
    pass

def get_routes_for_stops(stop_ids: list, gtfs_data: dict):
    """
    Get all bus routes that serve a list of stops.
    :param stop_ids: list of stop IDs
    :param gtfs_data: full GTFS dataset
    :return: list of route IDs serving these stops
    """
    pass

def find_viable_trips(destination_stops: list, target_arrival_time: str, day_of_week: str, gtfs_data: dict):
    """
    Find bus trips arriving before target time on given day.
    :param destination_stops: list of stops near destination building
    :param target_arrival_time: desired arrival time as HH:MM:SS
    :param day_of_week: day string (e.g. 'monday')
    :param gtfs_data: GTFS dataset
    :return: list of viable trip dicts with trip info
    """
    pass

def find_boarding_options(viable_trips: list, current_location: dict, gtfs_data: dict):
    """
    For each viable trip, find possible boarding stops accessible from user location.
    :param viable_trips: list of viable trips
    :param current_location: dict with lat/lng keys
    :param gtfs_data: GTFS dataset
    :return: list of boarding options with stop info and walking times
    """
    pass

def calculate_journey_time(option: dict):
    """
    Calculate total journey time including walking and bus ride.
    :param option: dict with boarding and trip details
    :return: dict with added total journey time and departure time from origin
    """
    pass

def select_best_bus_option(boarding_options: list):
    """
    Select the best bus option based on journey time and departure time.
    :param boarding_options: list of boarding options with journey times
    :return: best bus option dict or None if no options
    """
    pass

def plan_route(schedule: list, building_coords: dict, gtfs_data: dict):
    """
    Main planner to suggest best bus options for each class in schedule.
    :param schedule: list of class dicts
    :param building_coords: dict of building names to coordinates
    :param gtfs_data: loaded GTFS dataset
    :return: dict of class times mapped to suggested bus options
    """
    pass
