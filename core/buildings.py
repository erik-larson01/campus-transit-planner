import json

def load_buildings(json_path: str):
    """
    Load campus buildings data from JSON/GeoJSON.
    :param json_path: path to buildings JSON file
    :return: dict of building info with coordinates
    """
    pass

def get_building_coordinates(building_name: str, buildings_data: dict):
    """
    Retrieve lat/lng coordinates for a given building.
    :param building_name: name or ID of building
    :param buildings_data: dict of loaded building info
    :return:dict of a buildings name and coordinates
    """
    #TODO return a dict of name and latlng for every building
    #TODO handle names that do not exactly match the data

    pass
