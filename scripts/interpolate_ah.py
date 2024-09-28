import sys

sys.path.append(".")
sys.path.append("scripts")
from lib import *
from datetime import datetime

# inputs:
# - station name
# - GPS time in seconds

import argparse

intervals = [(0, 6), (6, 12), (12, 18), (18, 24)]

parser = argparse.ArgumentParser()
parser.add_argument("--station", type=str, help="station name", required=True)
parser.add_argument(
    "--time_seconds", type=float, help="GPS time in seconds", required=True
)
args = parser.parse_args()

station = args.station
time = float(args.time_seconds)


def main():
    datetime_obs = gps_time_to_utc(time)

    year = datetime_obs.year
    month = datetime_obs.month
    day = datetime_obs.day
    hour = datetime_obs.hour
    # minute = datetime_obs.minute
    # second = datetime_obs.second

    # the interval that the time is in
    begin, end = find_interval(hour, intervals)

    # time since the beginning of the interval:
    dt_begin = datetime_obs - datetime(year, month, day, begin, 0, 0)

    # path for the file at beginning of interval
    path_begin = os.path.join(
        base_folder, station, str(year), str(month), str(day), str(begin) + fileformat
    )

    end_hour = end
    end_day = day

    if end_hour == 24:
        end_hour = 0
        end_day += 1

    path_end = os.path.join(
        base_folder,
        station,
        str(year),
        str(month),
        str(end_day),
        str(end_hour) + fileformat,
    )

    # interpolation
    data_begin = parse_data_file(path_begin)
    data_end = parse_data_file(path_end)

    print(data_begin)
    print(data_end)

    lat = data_begin["data"]["lat"]
    lon = data_begin["data"]["lon"]
    alt = data_begin["data"]["alt"]

    # ah_begin = data_begin["data"]["ah"]
    # ah_end = data_end["data"]["ah"]

    # aw_begin = data_begin["data"]["aw"]
    # aw_end = data_end["data"]["aw"]

    # dif_ah = ah_end - ah_begin
    # dif_aw = aw_end - aw_begin

    # # interpolation, remembering that the interval is always of 6 hours, and the time from beginning is in dt_begin:
    # interpolated_ah = ah_begin + dif_ah * (
    #     dt_begin.total_seconds() / six_hours_in_seconds
    # )
    # interpolated_aw = aw_begin + dif_aw * (
    #     dt_begin.total_seconds() / six_hours_in_seconds
    # )

    final_data = {
        "lat": lat,
        "lon": lon,
        "alt": alt,
    }

    values_to_be_interpolated = [
        "ah",
        "aw",
        "zhd",
        "zwd",
        "gn_h",
        "ge_h",
        "gn_w",
        "ge_w",
    ]

    for value in values_to_be_interpolated:
        val_begin = data_begin["data"][value]
        val_end = data_end["data"][value]
        dif_val = val_end - val_begin
        final_data[value] = val_begin + dif_val * (
            dt_begin.total_seconds() / six_hours_in_seconds
        )

    # print all values in the final_data dictionary, in the same line, with 10 decimal places:
    final_data_str = ", ".join([f"{value:.10f}" for value in final_data.values()])
    print(final_data_str)


if __name__ == "__main__":
    main()
