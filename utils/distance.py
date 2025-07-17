import math
from typing import Dict, Any

import googlemaps
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# CITE: Haversine Distance Calculation
# Based on the Haversine formula (Wikipedia, https://en.wikipedia.org/wiki/Haversine_formula)
# Implemented using a Python snippet from Stack Overflow
# URL: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate straight-line distance in km between two lat/lng points.
    :param lat1: latitude of point 1
    :param lon1: longitude of point 1
    :param lat2: latitude of point 2
    :param lon2: longitude of point 2
    :return: distance in km
    """
    R = 6371.0  # Earth's radius in km

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    lat_diff = lat2_rad - lat1_rad
    lon_diff = lon2_rad - lon1_rad

    a = (math.sin(lat_diff / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(lon_diff / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # Distance in km


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2:float) -> float:
    """
    Calculate straight-line distance in km between two lat/lng points.
    :param lat1: latitude of point 1
    :param lon1: longitude of point 1
    :param lat2: latitude of point 2
    :param lon2: longitude of point 2
    :return: distance in meters
    """
    return haversine_distance(lat1, lon1, lat2, lon2) * 1000

def init_google_client(api_key: str):
    """
    Creates an instance of the Google Maps Distance Matrix API to be used to calculate walking times
    :param api_key: an api key from developers.google.com
    :return: a Google API client to be used in API calls
    """
    return googlemaps.Client(key=api_key)

def get_walking_distance(gmaps_client, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Dict[str, Any]:
    """
    Use Google Maps API to get walking distance and time between two points.
    :param gmaps_client: Google Maps client object
    :param origin_lat: origin latitude
    :param origin_lng: origin longitude
    :param dest_lat: destination latitude
    :param dest_lng: destination longitude
    :return: dict with distance and duration info or None if error
    """
    try:
        result = gmaps_client.distance_matrix(
            origins=[(origin_lat, origin_lng)],
            destinations=[(dest_lat, dest_lng)],
            mode="walking",
            units="metric"
        )
        if result["rows"]:
            info = result["rows"][0]["elements"][0]
            if info["status"] == "OK":
                return {
                    "distance_text": info["distance"]["text"],
                    "distance_value": info["distance"]["value"],
                    "duration_text": info["duration"]["text"],
                    "duration_value": info["duration"]["value"]
                }
        return None
    except Exception as e:
        print(f"Error calculating walking distance: {e}")
        return None
