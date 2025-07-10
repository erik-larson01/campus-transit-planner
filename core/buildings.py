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

def get_building_coordinates(building_name: str, buildings_data: List[Dict[str]]) -> Dict[str, Any]:
    """
    Retrieve lat/lng coordinates for a given building using fuzzy name matching.
    If an exact match is not found, suggests the closest known name.
    :param building_name: user-input building name
    :param buildings_data: list of building dictionaries
    :return: dict with name, lat, lon or None if not found
    """
    query = building_name.lower().strip()

    # Try exact match first
    for building in buildings_data:
        if building.get("name") and building["name"].lower() == query:
            if building.get("lat") and building.get("long"):
                return {"lat": building["lat"], "long": building["long"]}
            else:
                return {"error": "Coordinates not available for this building."}

    # If no exact match, suggest close matches using rapidfuzz
    building_names = []
    for building in buildings_data:
        if building.get("name"):
            building_names.append(building["name"])

    close_matches = process.extract(query, building_names, limit=3)
    filtered_matches = []
    for match in close_matches:
        if match[1] >= 65:
            filtered_matches.append(match)
    close_matches = filtered_matches

    if close_matches:
        suggestions = [match[0] for match in close_matches]
        return {"error": f"Did you mean: {', '.join(suggestions)}?"}

    return {"error": "No matching building found."}