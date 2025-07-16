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
    print(json.dumps(final_schedule))
    print("\nReady to begin transit planning...\n")

if __name__ == "__main__":
    main()
