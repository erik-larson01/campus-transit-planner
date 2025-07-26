import core.cli as cli
import core.schedule_parser as parser
import core.building_matcher as buildings_util
import core.gtfs_parser as gtfs
import core.route_planner as planner
def main():
    print("=== Campus Transit Planner ===")
    print()

    validated_schedule = cli.run_schedule_validation()
    buildings_data = buildings_util.load_buildings()

    final_schedule = parser.update_schedule_with_coordinates(validated_schedule, buildings_data)
    max_walking_dist = cli.get_user_walking_preference()
    print(f"Max walking distance of {max_walking_dist}m set.")
    gtfs_dict = gtfs.load_gtfs_files()
    print("\nReady to begin transit planning...\n")
    results = planner.plan_route(final_schedule, max_walking_dist, gtfs_dict)
    cli.output_final_schedule(results, file_path="output/daily_plan.txt")
    print("\nFull transit plan output to output/daily_plan.txt")
if __name__ == "__main__":
    main()
