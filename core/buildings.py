import json
from typing import List, Dict, Any
from rapidfuzz import process, fuzz

def load_buildings(json_path: str = "data/buildings.geojson") -> List[Dict[str]]:
    """
    Load campus buildings data from JSON/GeoJSON.
    :param json_path: path to buildings JSON file
    :return: list of building info dicts with name, address, and coordinates
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    updated_building_info = get_building_info(data)
    return updated_building_info

def get_building_info(buildings_data: List[Dict[str]]) -> List[Dict[str]]:
    """
    Extracts a list of a buildings geo info, such as name, street address and coordinates
    :param buildings_data: list of all buildings from loaded buildings.geojson
    :return: list of dicts with keys: name, street_address, lat, lon
    """
    results = []
    for building in buildings_data:
        name = building.get("name")
        street_address = building.get("street_address")
        latlng = building.get("latlng", None)
        if latlng:
            lat, lon = latlng[0], latlng[1]
        else:
            lat, lon = None, None
        results.append({
            "name": name,
            "street_address": street_address,
            "lat": lat,
            "long": lon
        })
    return results
