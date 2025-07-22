from typing import List, Dict, Any

import pandas as pd

import gtfs_parser as gtfs
import utils.distance as dist
import utils.time_utils as time
import core.cli as cli
import schedule_parser as parser

# TODO: Implement full logic flow from earlier (find stop → route → trip)
# 1. For each class in schedule, find nearby stops
# 2. For each stop, find routes serving it
# 3. For each route, find viable trips before class time
# 4. Find boarding options for the user location
# 5. Calculate journey time and pick best option
# 6. Return summary for all classes

def find_nearby_stops(building_lat: float, building_long: float, stops_data: pd.DataFrame,
                      max_distance: int) -> pd.DataFrame:
    """
    Find bus stops within max_distance meters of given coordinates.
    :param building_lat: latitude of reference point
    :param building_long: longitude of reference point
    :param stops_data: GTFS stops data
    :param max_distance: max walking distance in meters
    :return: a Dataframe containing rows of nearby stops to a campus building
    """
    nearby_rows = []
    for _, stop in stops_data.iterrows():
        lat_of_stop = stop["stop_lat"]
        long_of_stop = stop["stop_lon"]
        distance = dist.haversine_distance(building_lat, building_long, lat_of_stop, long_of_stop)
        if distance <= max_distance:
            nearby_rows.append(stop)

    return pd.DataFrame(nearby_rows)

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


def plan_route(schedule: List[Dict[str, Any]], max_walking_distance: int, gtfs_data: dict) -> None:
    """
    Main planner to suggest best bus options for each class in schedule.
    :param schedule: list of class dicts with updated coordinate data
    :param max_walking_distance: a user's max walking distance to any given bus stop
    :param gtfs_data: loaded GTFS dataset
    :return: dict of class times mapped to suggested bus options
    """
    stops_df = gtfs_data['stops']
    trips_df = gtfs_data['trips']
    stop_times_df = gtfs_data['stop_times']
    calendar_df = gtfs_data['calendar']
    routes_df = gtfs_data['routes']

    # Sort schedule by days and then class time for easier output
    DAY_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    schedule.sort(
        key=lambda entry: (DAY_ORDER.index(entry["day"].lower()), entry["start_time"])
    )

    for class_entry in schedule:
        origin_day = class_entry["day"]
        origin_lat = class_entry["lat"]
        origin_long = class_entry["long"]
        origin_start_time = class_entry["start_time"]

        next_class = parser.find_next_class_for_same_day(schedule, origin_day, origin_start_time)
        if not next_class:
            continue

        # Get all unique and active (running) stops on a given day via service_id -> trip_id -> stop_id
        active_service_ids = gtfs.get_active_service_ids(origin_day, calendar_df)
        active_trip_ids = gtfs.filter_trips_by_service(trips_df, active_service_ids)
        active_stop_ids = gtfs.get_unique_stops_for_trips(active_trip_ids, stop_times_df)
        active_stops_df = gtfs.get_stop_details_for_stop_ids(active_stop_ids, stops_df)

        # Get all candidate trips (trips that stop by the origin building and run on the same day as the class)
        nearby_stops_df = find_nearby_stops(origin_lat, origin_long, active_stops_df, max_walking_distance)
        origin_stop_ids = nearby_stops_df["stop_id"].unique.tolist()
        candidate_stop_times = stop_times_df[
            (stop_times_df["stop_id"].isin(origin_stop_ids)) & (stop_times_df["trip_id"].isin(active_trip_ids))
        ]
        candidate_trip_ids = candidate_stop_times["trip_id"].unique().tolist()