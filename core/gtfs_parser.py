import pandas as pd
import os
from typing import Dict, List


def load_gtfs_files(gtfs_folder: str = "data/gtfs/") -> Dict[str, pd.DataFrame]:
    """
    Load all GTFS CSV files from folder into a dict of dataframes.
    :param gtfs_folder: path to folder containing GTFS txt files
    :return: dict with keys: stops, routes, trips, stop_times, calendar
    """
    gtfs_data = {}

    for filename in os.listdir(gtfs_folder):
        if filename.endswith(".txt"):
            # Replace .txt for the key in gtfs_data
            key = filename.replace(".txt", "")
            full_path = os.path.join(gtfs_folder, filename)
            df = pd.read_csv(full_path)
            for col in df.columns:
                if col.endswith("_id"):
                    # Ensure ids such as trip_id, service_id, stop_id are treated as strings
                    df[col] = df[col].astype(str)
            gtfs_data[key] = df

    return gtfs_data


def get_active_service_ids(day_of_week: str, calendar_df: pd.DataFrame) -> List[str]:
    """
    Filters calendar to return list of service_ids running on a given day of the week.
    :param day_of_week: "monday", "tuesday", etc.
    :param calendar_df: calendar.txt DataFrame
    :return: list of active service_ids
    """
    day_of_week = day_of_week.lower()
    filtered = calendar_df[calendar_df[day_of_week] == 1]

    active_ids = filtered["service_id"].tolist()
    return active_ids


def filter_trips_by_service(trips_df: pd.DataFrame, active_services: List[str]) -> List[str]:
    """
    Filters trips using active service_ids to return a list of all trip_ids that run on
    a given day of the week.
    :param trips_df: trips.txt DataFrame
    :param active_services: list of active service_ids
    :return: list of active trips via trip_ids
    """
    filtered = trips_df[trips_df["service_id"].isin(active_services)]
    active_trips = filtered["trip_id"].tolist()
    return active_trips


def get_stop_times_for_trip(trip_id: str, stop_times_df: pd.DataFrame) -> List[str]:
    """
    Retrieves all stop times from a specific trip, ordered by stop sequence from stop_times.txt
    :param trip_id: the ID of the trip to retrieve stops for
    :param stop_times_df: stop_times.txt DataFrame
    :return: list of stop_ids in the order visited by the trip
    """
    filtered = stop_times_df[stop_times_df["trip_id"] == trip_id]

    # Get all stops in chronological order
    filtered = filtered.sort_values("stop_sequence")

    stop_times_in_trip = filtered["stop_id"].tolist()
    return stop_times_in_trip


def get_route_for_trip(trip_id: str, trips_df: pd.DataFrame, routes_df: pd.DataFrame) -> str:
    """
    Provides readable route names for CLI output based on a trip found via trip_id
    :param trip_id: the ID of the trip to retrieve name for
    :param trips_df: trips.txt DataFrame
    :param routes_df: routes.txt DataFrame
    :return: string name/description of route the trip is a part of
    """
    trip_row = trips_df[trips_df["trip_id"] == trip_id]
    if trip_row.empty:
        return f"Trip ID '{trip_id}' not found."
    route_id = trip_row["route_id"].item()
    trip_headsign = trip_row["trip_headsign"].item()
    trip_direction = trip_row["trip_direction_name"].item()

    route_row = routes_df[routes_df["route_id"] == route_id]
    if route_row.empty:
        return f"Route ID '{route_id}' not found."

    route_long_name = route_row["route_long_name"].item()

    parts = [f"{route_long_name}"]
    if trip_headsign:
        parts.append(trip_headsign)
    if trip_direction:
        parts.append(trip_direction)
    full_output = " ".join(parts)
    return full_output
