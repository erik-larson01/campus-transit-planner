import pandas as pd

def load_gtfs_files(gtfs_folder: str):
    """
    Load all GTFS CSV files from folder into dataframes or dicts.
    :param gtfs_folder: path to folder containing GTFS txt files
    :return: dict with keys: stops, routes, trips, stop_times, calendar
    """
    pass

def filter_gtfs_by_date(gtfs_data: dict, target_date: str):
    """
    Filter GTFS calendar and trips data by target date (weekday).
    :param gtfs_data: full GTFS dataset dict
    :param target_date: date string (YYYYMMDD) to filter service
    :return: filtered GTFS data relevant for target date
    """
    pass