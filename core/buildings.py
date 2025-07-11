import json
from typing import List, Dict, Any
from rapidfuzz import process
def load_buildings(json_path: str = "data/buildings.geojson") -> list[Dict[str, Any]]:
    """
    Load campus buildings data from JSON/GeoJSON.
    :param json_path: path to buildings JSON file
    :return: list of building info dicts with name, address, and coordinates
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    updated_building_info = get_building_info(data)
    return updated_building_info

def get_building_info(buildings_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts a list of a buildings geo info, such as name, street address and coordinates
    :param buildings_data: list of all buildings from loaded buildings.geojson
    :return: list of dicts with keys: name, street_address, lat, lon
    """
    results = []
    for building in buildings_data:
        name = building.get("name")
        street_address = building.get("street_address")
        latlng = building.get("latlng")
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

def get_building_coordinates(building_name: str, buildings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Retrieve lat/lng coordinates for a given building using fuzzy name matching.
    If an exact match is not found, suggests the closest known name.
    :param building_name: user-input building name
    :param buildings_data: list of building dictionaries
    :return: dict with name, lat, lon or None if not found
    """
    query = building_name.lower().strip()

    for building in buildings_data:
        if building.get("name") and building["name"].lower() == query:
            if building.get("lat") and building.get("long"):
                return {"lat": building["lat"], "long": building["long"]}
            else:
                return {"error": "Coordinates not available for this building."}

    return {"error": "No matching building found."}

def match_building_names(user_buildings: List[str], buildings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Matches user input building names to valid campus building names pulled from map.wisc.edu.

    :param user_buildings: list of raw user-entered building names
    :param buildings_data: list of building objects with "name" field from buildings.geojson
    :return: dict with 'exact_matches', 'best_matches', 'suggestions', and 'unmatched' to be used by cli.py
    """
    building_names = []
    for building in buildings_data:
        if "name" in building and building["name"]:
            building_names.append(building["name"])

    exact_matches = {}
    best_matches = {}
    suggestions = {}
    unmatched = []

    for user_building in user_buildings:
        match_found = False

        for official_name in building_names:
            if user_building.strip().lower() == official_name.strip().lower():
                exact_matches[user_building] = official_name
                match_found = True
                break

        if not match_found:
            fuzzy_matches = process.extract(user_building, building_names, limit=5)

            if len(fuzzy_matches) > 0 and fuzzy_matches[0][1] >= 80:
                best_match = fuzzy_matches[0][0]
                best_matches[user_building] = best_match

                suggestion_list = []
                for match in fuzzy_matches[1:]:
                        suggestion_list.append(match[0])
                suggestions[user_building] = suggestion_list
            else:
                unmatched.append(user_building)

    return {
        "exact_matches": exact_matches,
        "best_matches": best_matches,
        "suggestions": suggestions,
        "unmatched": unmatched
    }
