
MAX_WALKING_DISTANCE_METERS = 800 #Temp
def suggest_transport_option(distance: float):
    """
    Suggest whether to walk or take bus based on distance.
    :param distance: distance in meters from origin to destination
    :return: 'walk' or 'bus'
    """
    if distance < MAX_WALKING_DISTANCE_METERS:
        return "Walk"
    else:
        return "Take the bus"
