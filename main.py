import argparse
from datetime import datetime
import time

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument(
    "-s",
    "--start",
    help="The start date of the analysis as an ISO 8601 date: 2023-01-01",
)
parser.add_argument(
    "-e", "--end", help="The end date of the analysis as an ISO 8601 date: 2023-01-01."
)
args = parser.parse_args()


def validate_input(start: str, end: str) -> tuple:
    """
    Validates the input and transforms it to usable start and end times
    :param start: The start time input
    :param end: The end time input
    :return: A tuple with the start and end time for information gathering.
    """
    if start is None:
        start_time = datetime(datetime.now().year, 1, 1)
    else:
        try:
            start_time = datetime.fromisoformat(start)
        except Exception as exp:
            start_time = datetime(datetime.now().year, 1, 1)

    if end is None:
        end_time = datetime(datetime.now().year, 12, 31)
    else:
        try:
            end_time = datetime.fromisoformat(end)
        except Exception as exp:
            end_time = datetime(datetime.now().year, 12, 31)
    # dates = (int(time.mktime(start_time.timetuple())), int(time.mktime(end_time.timetuple())))
    dates = (start_time, end_time)
    return dates


def main_routine():
    """
    The program entry point
    :return: None
    """
    dates = validate_input(args.start, args.end)
    print(dates[0])
    print(dates[1])


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    main_routine()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
