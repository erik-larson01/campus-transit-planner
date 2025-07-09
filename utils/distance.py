def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float):
    """
    Calculate straight-line distance in meters between two lat/lng points.
    :param lat1: latitude of point 1
    :param lon1: longitude of point 1
    :param lat2: latitude of point 2
    :param lon2: longitude of point 2
    :return: distance in meters
    """
    pass

def get_walking_distance(gmaps_client, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float):
    """
    Use Google Maps API to get walking distance and time between two points.
    :param gmaps_client: Google Maps client object
    :param origin_lat: origin latitude
    :param origin_lng: origin longitude
    :param dest_lat: destination latitude
    :param dest_lng: destination longitude
    :return: dict with distance and duration info or None if error
    """
    pass