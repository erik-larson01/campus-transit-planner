import os
from typing import List, Dict, Any, final
import pandas as pd
from dotenv import load_dotenv

import core.gtfs_parser as gtfs
import utils.distance as dist
import utils.time_utils as time
import core.schedule_parser as parser

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


def find_nearby_stops(building_lat: float, building_long: float, stops_data: pd.DataFrame,
                      max_distance: float) -> pd.DataFrame:
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
        distance = dist.haversine_distance_meters(building_lat, building_long, lat_of_stop, long_of_stop)
        if distance <= max_distance:
            nearby_rows.append(stop)

    return pd.DataFrame(nearby_rows)


def filter_candidate_trip_ids(stop_times_df: pd.DataFrame, origin_stop_ids: List[str], trip_ids: List[str],
                              origin_class_end_time: str, earliest_offset_sec: int = 5 * 60,
                              latest_offset_sec: int = 45 * 60) -> List[str]:
    """
    Filters candidate trip_ids to only those that have a stop in origin_stop_ids and
    depart within a realistic time window after the origin class ends.
    :param stop_times_df: stop_times.txt DataFrame
    :param origin_stop_ids: list of stop_ids near origin building
    :param trip_ids: all active trip_ids for the day
    :param origin_class_end_time: class end time string
    :param earliest_offset_sec: min seconds after class ends (default: 5 minutes)
    :param latest_offset_sec: max seconds after class ends (default: 45 minutes)
    :return: list of trip_ids that meet the time window filter
    """

    filtered_ids = set()
    earliest_departure = time.add_time(origin_class_end_time, earliest_offset_sec)
    latest_departure = time.add_time(origin_class_end_time, latest_offset_sec)

    for trip_id in trip_ids:
        trip_stops = stop_times_df[stop_times_df["trip_id"] == trip_id].sort_values("stop_sequence")

        for _, row in trip_stops.iterrows():
            stop_id = row["stop_id"]
            departure_time = row["departure_time"]

            if (
                    stop_id in origin_stop_ids and
                    time.is_time_before(earliest_departure, departure_time) and
                    time.is_time_before(departure_time, latest_departure)
            ):
                filtered_ids.add(trip_id)
                break

    return list(filtered_ids)

def find_viable_trips(gmaps_client, candidate_trip_ids: List[str], origin_stops_df: pd.DataFrame,
                      origin_class: Dict[str, Any], destination_class: Dict[str, Any], stop_times_df: pd.DataFrame,
                      stops_df: pd.DataFrame, trips_df: pd.DataFrame, routes_df: pd.DataFrame,
                      max_walking_distance: float) -> List[Dict[str, Any]]:
    """
    Filters candidate trips based on timing and stop proximity to both origin and destination to create a list of
    possible trips for the user to take from an origin class building to a destination
    :param gmaps_client: the Google Maps API client
    :param candidate_trip_ids: a list of possible trip_ids that have a stop nearby the origin building
    :param origin_stops_df: nearby stops to the origin class building
    :param origin_class: a dict of coordinate data of a user's origin class
    :param destination_class: a dict of coordinate data of a user's destination
    :param stop_times_df: stop_times.txt DataFrame
    :param stops_df: stops.txt DataFrame
    :param trips_df: trips.txt DataFrame
    :param routes_df: routes.txt DataFrame
    :param max_walking_distance: user's max walking distance to a stop
    :return:
    """
    valid_trips = []

    origin_stop_ids = origin_stops_df["stop_id"].unique().tolist()
    origin_class_end = origin_class["end_time"]
    origin_lat = origin_class["lat"]
    origin_long = origin_class["long"]
    dest_lat = destination_class["lat"]
    dest_lng = destination_class["long"]
    dest_class_start = destination_class["start_time"]

    # For all possible candidate trips:
    for candidate_id in candidate_trip_ids:
        # Get all stop times for that trip sorted by stop sequence
        trip_stop_times_df = stop_times_df[stop_times_df["trip_id"] == candidate_id].sort_values(
            "stop_sequence").reset_index(drop=True)

        if len(trip_stop_times_df) == 0:
            continue

        # For all of those stops:
        for index, row in trip_stop_times_df.iterrows():
            stop_id = row["stop_id"]

            # Find the stops that are nearby the user
            if stop_id in origin_stop_ids:
                departure_time = row["departure_time"]

                # Ensure the stop time fits between the two classes
                time_check_1 = time.is_time_before(origin_class_end, departure_time)
                time_check_2 = time.is_time_before(departure_time, destination_class["start_time"])

                if not (time_check_1 and time_check_2):
                    continue

                stop_info = stops_df[stops_df["stop_id"] == stop_id]
                if stop_info.empty:
                    continue

                stop_lat = stop_info["stop_lat"].values[0]
                stop_long = stop_info["stop_lon"].values[0]

                # Get google walking data to check if a user can board on time
                walk_result = dist.get_walking_data(gmaps_client, origin_lat, origin_long,
                                                    stop_lat, stop_long)
                if not walk_result:
                    continue

                walking_time_to_boarding_stop = walk_result["duration_value"]
                walking_dist_to_boarding_stop = walk_result["distance_text"]  # For CLI output
                walk_time_in_meters = walk_result["distance_value"]

                if walk_time_in_meters > max_walking_distance:
                    continue

                arrival_at_stop = time.add_time(origin_class_end, walking_time_to_boarding_stop)

                # Check if the user can actually arrive to the stop on time
                if not (time.is_time_before(arrival_at_stop, departure_time)):
                    continue  # Not enough time to walk to the stop

                # Check if that stop is the last one before looping
                if index + 1 >= len(trip_stop_times_df):
                    continue

                # Origin/boarding stop is now valid, so check for destination stops where the entire trip fits
                for i in range(index + 1, len(trip_stop_times_df)):
                    dest_row = trip_stop_times_df.iloc[i]
                    dest_stop_id = dest_row["stop_id"]
                    dest_arrival_time = dest_row["arrival_time"]

                    dest_stop_info = stops_df[stops_df["stop_id"] == dest_stop_id]
                    if dest_stop_info.empty:
                        continue

                    # To reduce API calls, check if the destination stop is before the class start time
                    if not time.is_time_before(dest_arrival_time, dest_class_start):
                        continue

                    dest_stop_lat = dest_stop_info["stop_lat"].values[0]
                    dest_stop_long = dest_stop_info["stop_lon"].values[0]

                    # Check if the user stop is within walking distance to the destination class building
                    dist_to_dest_building = dist.haversine_distance_meters(dest_lat, dest_lng, dest_stop_lat,
                                                                           dest_stop_long)
                    if dist_to_dest_building > max_walking_distance:
                        continue

                    # Destination stop is within walking distance, so now check if the whole trip fits
                    dest_walk_result = dist.get_walking_data(gmaps_client, dest_stop_lat, dest_stop_long, dest_lat,
                                                             dest_lng)
                    if not dest_walk_result:
                        continue

                    walk_time_to_dest = dest_walk_result["duration_value"]
                    walk_dist_to_dest = dest_walk_result["distance_text"]
                    walk_time_in_meters = dest_walk_result["distance_value"]

                    if walk_time_in_meters > max_walking_distance:
                        continue

                    arrival_at_building = time.add_time(dest_arrival_time, walk_time_to_dest)

                    # Check if the user can actually arrive to the destination class building on time
                    if not (time.is_time_before(arrival_at_building, dest_class_start)):
                        continue

                    # If they can, the entire trip fits and is valid
                    waiting_time = time.time_difference(arrival_at_stop, departure_time)
                    total_ride_time = time.time_difference(departure_time, dest_arrival_time)
                    total_walk_time = walking_time_to_boarding_stop + walk_time_to_dest
                    total_travel_time = total_walk_time + total_ride_time
                    total_travel_time_with_waiting = total_travel_time + waiting_time
                    # Add stop descriptions for cli output
                    origin_stop_name = stop_info["stop_name"].values[0]
                    dest_stop_name = dest_stop_info["stop_name"].values[0]
                    leave_time = time.subtract_time(departure_time, walking_time_to_boarding_stop)

                    # Add route description
                    route_name = gtfs.get_route_for_trip(candidate_id, trips_df, routes_df)

                    valid_trips.append({
                        "trip_id": candidate_id,
                        "route_name": route_name,
                        "origin_stop_id": stop_id,
                        "origin_stop_name": origin_stop_name,
                        "time_to_leave": leave_time,
                        "origin_departure_time": departure_time,
                        "origin_walk_time": walking_time_to_boarding_stop,
                        "waiting_time_at_origin": waiting_time,
                        "origin_walk_distance": walking_dist_to_boarding_stop,
                        "destination_stop_id": dest_stop_id,
                        "destination_stop_name": dest_stop_name,
                        "destination_arrival_time": dest_arrival_time,
                        "dest_walk_time_sec": walk_time_to_dest,
                        "dest_walk_distance": walk_dist_to_dest,
                        "total_ride_time_sec": total_ride_time,
                        "total_walk_time_sec": total_walk_time,
                        "total_travel_time_sec": total_travel_time,
                        "total_time_with_waiting": total_travel_time_with_waiting,
                        "arrive_at_building_time": arrival_at_building
                    })
    return valid_trips

def select_best_trip(valid_trips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Select the best trip(s) and bus option based on minimum trip time and earliest arrival at destination
    :param valid_trips: list of valid trips a user can take
    :return: best bus option dict or None if no options
    """
    final_trips = []

    if not valid_trips:
        return []

    earliest_arrival = min(valid_trips, key= lambda trip: trip["arrive_at_building_time"])
    shortest_trip = min(valid_trips, key=lambda trip: trip["total_travel_time_sec"])

    if earliest_arrival == shortest_trip:
        print("Earliest arrival trip and shortest travel time trip are the same — presenting the best single option.")
        final_trips.append(earliest_arrival)
    else:
        final_trips.append(earliest_arrival)
        final_trips.append(shortest_trip)

    return final_trips


def plan_route(schedule: List[Dict[str, Any]], max_walking_distance: float, gtfs_data: dict) -> List[Dict[str, Any]]:
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
    day_order = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    schedule.sort(
        key=lambda entry: (day_order.index(entry["day"].lower()), entry["start_time"])
    )

    # Create gmaps client
    gmaps_client = dist.init_google_client(api_key)

    results = []

    for class_entry in schedule:
        origin_day = class_entry["day"]
        origin_lat = class_entry["lat"]
        origin_long = class_entry["long"]
        origin_start_time = class_entry["start_time"]
        origin_end_time  = class_entry["end_time"]

        # Ensure there is a next class to find a trip to before planning a route
        next_class = parser.find_next_class_for_same_day(schedule, origin_day, origin_start_time)
        if not next_class:
            continue

        # Get all unique and active (running) stops on a given day via service_id -> trip_id -> stop_id
        print("Loading GTFS service, trip, and stop data...")
        active_service_ids = gtfs.get_active_service_ids(origin_day, calendar_df)
        active_trip_ids = gtfs.filter_trips_by_service(trips_df, active_service_ids)
        active_stop_ids = gtfs.get_unique_stops_for_trips(active_trip_ids, stop_times_df)
        active_stops_df = gtfs.get_stop_details_for_stop_ids(active_stop_ids, stops_df)

        # Get all candidate trips (trips that stop by the origin building and run on the same day as the class)
        print(f"Locating nearby stops to {class_entry["building"]} for trip filtering...")
        origin_stops_df = find_nearby_stops(origin_lat, origin_long, active_stops_df, max_walking_distance)
        origin_stop_ids = origin_stops_df["stop_id"].unique().tolist()
        candidate_stop_times = stop_times_df[
            (stop_times_df["stop_id"].isin(origin_stop_ids)) & (stop_times_df["trip_id"].isin(active_trip_ids))
            ]
        candidate_trip_ids = candidate_stop_times["trip_id"].unique().tolist()
        print(f"{len(candidate_trip_ids)} candidate trips that stop near {class_entry["building"]}.\n")

        # Filter candidate trip ids to those who have at least one nearby stop 5-45 minutes after the class
        earliest_arrival = 5 * 60
        latest_arrival = 45 * 60
        print("Filtering trips by departure time (5–45 minutes after class ends)...")
        filtered_candidate_ids = filter_candidate_trip_ids(stop_times_df, origin_stop_ids, candidate_trip_ids,
                                                           origin_end_time, earliest_arrival, latest_arrival)
        print(f"{len(filtered_candidate_ids)} candidate trips remain after time filtering.\n")

        # Find all valid trips that fit in the time difference between classes
        print("Matching valid origin → destination stop combinations within each trip...")
        valid_trips = find_viable_trips(gmaps_client, filtered_candidate_ids, origin_stops_df, class_entry, next_class,
                                        stop_times_df, stops_df, trips_df, routes_df, max_walking_distance)

        # Finding best trips via arrival time and trip length
        print(f"Evaluating {len(valid_trips)} viable trip options to find earliest arrival and shortest travel time...")
        final_trips = select_best_trip(valid_trips)
        results.append({
            "from_class": class_entry,
            "to_class": next_class,
            "valid_trips": final_trips
        })
    return results