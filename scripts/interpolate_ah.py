# import sys
# import os
# import mmap
# import struct

import os

# import mmap, struct

# import logging

# sys.path.append(".")
# sys.path.append("scripts")
from datetime import datetime, timezone


# inputs:
# - station name
# - GPS time in seconds

# logging.basicConfig(
#     level=logging.INFO,
#     filename="/home/RTKLIB/scripts/logs/interpolate_ah.log",
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     datefmt="%d-%b-%y %H:%M:%S",
#     filemode="a",
# )


intervals = [(0, 6), (6, 12), (12, 18), (18, 24)]

base_folder = "/home/RTKLIB/vmf_grid"
fileformat = ".ac3"

six_hours_in_seconds = 21600


# # Shared memory file
# SHM_NAME = "/shm_single_double"

# # Define the data format (1 double = 8 bytes)
# FORMAT = "d"
# DATA_SIZE = struct.calcsize(FORMAT)  # 8 bytes


# def write_shared_double(value):
#     """Writes a single double value to shared memory."""
#     # Create and open shared memory object with read/write permission.
#     fd = os.open(SHM_NAME, os.O_CREAT | os.O_RDWR, 0o666)
#     os.ftruncate(fd, DATA_SIZE)  # Ensure the size is correct
#     shm = mmap.mmap(fd, DATA_SIZE, mmap.MAP_SHARED, mmap.PROT_WRITE)
#     shm.seek(0)
#     shm.write(struct.pack(FORMAT, value))
#     shm.close()  # Close the mapping
#     os.close(fd)  # Close the file descriptor


# def read_shared_double(name=SHM_NAME):
#     """Reads a single double value from shared memory."""
#     fd = os.open(name, os.O_RDONLY)
#     shm = mmap.mmap(fd, DATA_SIZE, mmap.MAP_SHARED, mmap.PROT_READ)
#     shm.seek(0)
#     data = shm.read(DATA_SIZE)
#     value = struct.unpack(FORMAT, data)[0]
#     shm.close()
#     os.close(fd)
#     return value


def unix_to_utc(unix_seconds):
    """Convert Unix timestamp (seconds since 1970-01-01) to UTC datetime (timezone-aware)."""
    return datetime.fromtimestamp(unix_seconds, tz=timezone.utc)


def find_interval(hour, intervals):
    for interval in intervals:
        if interval[0] <= hour < interval[1]:
            return interval
    return None  # In case the hour doesn't match any interval


def parse_data_file(file_path):
    result = {}

    with open(file_path, "r") as file:
        # Read the first line (Station, Date, Time info)
        header_line = file.readline().strip()
        station, year, month, day, hour, minute = header_line.split()

        # Store the station and time info
        result["station"] = station
        result["date"] = f"{year}-{month}-{day}"
        result["time"] = f"{hour}:{minute}"

        # Read the second line (column headers)
        headers = file.readline().strip().lower().split()

        # Read the third line (values)
        values = file.readline().strip().split()

        # Combine headers and values into a dictionary
        data_dict = {headers[i]: float(values[i]) for i in range(len(headers))}

        # Add the data dictionary to the result
        result["data"] = data_dict

    return result


# # # # Define a handler for the SIGPIPE signal
# # # def sigpipe_handler(signum, frame):
# # #     sys.stderr.write("Broken pipe error occurred.\n")
# # #     sys.exit(1)


def interpolate_ah(station, time):

    station = station.upper()

    datetime_obs = unix_to_utc(time)

    year = datetime_obs.year
    month = datetime_obs.month
    day = datetime_obs.day
    hour = datetime_obs.hour
    # minute = datetime_obs.minute
    # second = datetime_obs.second

    # the interval that the time is in
    begin, end = find_interval(hour, intervals)

    # time since the beginning of the interval:
    dt_begin = datetime_obs - datetime(
        year, month, day, begin, 0, 0, tzinfo=timezone.utc
    )

    # path for the file at beginning of interval
    path_begin = os.path.join(
        base_folder,
        station,
        str(year),
        str(month),
        str(day),
        str(begin) + fileformat,
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

    # print(data_begin)
    # print(data_end)

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

    proportion = dt_begin.total_seconds() / six_hours_in_seconds

    for value in values_to_be_interpolated:
        val_begin = data_begin["data"][value]
        val_end = data_end["data"][value]
        dif_val = val_end - val_begin
        final_data[value] = val_begin + dif_val * proportion

    # # print all values in the final_data dictionary, in the same line, with 10 decimal places:
    # final_data_str = " ".join([f"{value:.10f}" for value in final_data.values()])

    # # logging.info(final_data_str)

    # print(final_data_str)

    return final_data


# if __name__ == "__main__":
#     for i in tqdm(range(100000)):
#         main()
