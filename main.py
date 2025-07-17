import json

import core.cli as cli
import core.schedule_parser as parser
import core.buildings as buildings_util
def main():
    print("=== Campus Transit Planner ===")
    print()

    validated_schedule = cli.run_schedule_validation()
    buildings_data = buildings_util.load_buildings()

    final_schedule = parser.update_schedule_with_coordinates(validated_schedule, buildings_data)
    max_walking_dist = cli.get_user_walking_preference()
    print(f"Max walking distance of {max_walking_dist}m set.")
    print("\nReady to begin transit planning...\n")

if __name__ == "__main__":
    main()
