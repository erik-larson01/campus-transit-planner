from utils.config import MAX_WALKING_DISTANCE_METERS
def suggest_transport_option(distance: float):
    """
    Suggest whether to walk or take bus based on distance.
    :param distance: distance in meters from origin to destination
    :param walking_threshold: max distance to prefer walking
    :return: 'walk' or 'bus'
    """
    if distance < MAX_WALKING_DISTANCE_METERS:
        return "Walk"
    else:
        return "Take the bus"
