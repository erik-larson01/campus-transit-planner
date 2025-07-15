import core.cli as cli

def main():
    print("=== Campus Transit Planner ===")
    print()

    updated_schedule = cli.run_schedule_validation()
    print("\nReady to begin transit planning...\n")


if __name__ == "__main__":
    main()
