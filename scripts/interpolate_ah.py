import os
from datetime import datetime, timezone
from functools import lru_cache
import numpy as np


DEG2RAD = np.pi / 180
RAD2DEG = 180 / np.pi

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


# def find_interval(hour):
#     intervals = ((0, 6), (6, 12), (12, 18), (18, 24))

#     for interval in intervals:
#         if interval[0] <= hour < interval[1]:
#             return interval


def find_interval(hour):
    # Ensure hour is in [0, 24) if needed
    # Compute index by integer division; each interval is 6 hours
    index = int(hour // 6)
    # This returns the interval tuple corresponding to the hour
    return ((0, 6), (6, 12), (12, 18), (18, 24))[index]


# def parse_data_file(file_path):
#     with open(file_path, "r") as f:
#         # Skip first two lines
#         next(f)
#         next(f)
#         # Read the third line
#         third_line = next(f, None)
#         # if third_line is None:
#         #     raise ValueError("The file does not contain a third line.")
#     # LAT LON ALT AH AW ZHD ZWD GN_H GE_H GN_W GE_W
#     return tuple(map(float, third_line.split()))


def parse_data_file(filename):
    with open(filename, "r") as f:
        # Skip the first two lines
        next(f)
        next(f)
        third_line = f.readline()
    # Convert the string directly to a NumPy array
    return np.fromstring(third_line, sep=" ")


# # # # Define a handler for the SIGPIPE signal
# # # def sigpipe_handler(signum, frame):
# # #     sys.stderr.write("Broken pipe error occurred.\n")
# # #     sys.exit(1)


# def interpolate_ah(station, time):

#     station = station.upper()

#     datetime_obs = unix_to_utc(time)

#     year = datetime_obs.year
#     month = datetime_obs.month
#     day = datetime_obs.day
#     hour = datetime_obs.hour
#     # minute = datetime_obs.minute
#     # second = datetime_obs.second

#     # the interval that the time is in
#     begin, end = find_interval(hour)

#     # time since the beginning of the interval:
#     dt_begin = datetime_obs - datetime(
#         year, month, day, begin, 0, 0, tzinfo=timezone.utc
#     )

#     # path for the file at beginning of interval
#     path_begin = os.path.join(
#         base_folder,
#         station,
#         str(year),
#         str(month),
#         str(day),
#         str(begin) + fileformat,
#     )

#     end_hour = end
#     end_day = day

#     if end_hour == 24:
#         end_hour = 0
#         end_day += 1

#     path_end = os.path.join(
#         base_folder,
#         station,
#         str(year),
#         str(month),
#         str(end_day),
#         str(end_hour) + fileformat,
#     )

#     # interpolation
#     data_begin = parse_data_file(path_begin)
#     data_end = parse_data_file(path_end)

#     # print(data_begin)
#     # print(data_end)

#     lat = data_begin["data"]["lat"]
#     lon = data_begin["data"]["lon"]
#     alt = data_begin["data"]["alt"]

#     # ah_begin = data_begin["data"]["ah"]
#     # ah_end = data_end["data"]["ah"]

#     # aw_begin = data_begin["data"]["aw"]
#     # aw_end = data_end["data"]["aw"]

#     # dif_ah = ah_end - ah_begin
#     # dif_aw = aw_end - aw_begin

#     # # interpolation, remembering that the interval is always of 6 hours, and the time from beginning is in dt_begin:
#     # interpolated_ah = ah_begin + dif_ah * (
#     #     dt_begin.total_seconds() / six_hours_in_seconds
#     # )
#     # interpolated_aw = aw_begin + dif_aw * (
#     #     dt_begin.total_seconds() / six_hours_in_seconds
#     # )

#     final_data = {
#         "lat": lat,
#         "lon": lon,
#         "alt": alt,
#     }

#     values_to_be_interpolated = [
#         "ah",
#         "aw",
#         "zhd",
#         "zwd",
#         "gn_h",
#         "ge_h",
#         "gn_w",
#         "ge_w",
#     ]

#     proportion = dt_begin.total_seconds() / six_hours_in_seconds

#     for value in values_to_be_interpolated:
#         val_begin = data_begin["data"][value]
#         val_end = data_end["data"][value]
#         dif_val = val_end - val_begin
#         final_data[value] = val_begin + dif_val * proportion

#     # # print all values in the final_data dictionary, in the same line, with 10 decimal places:
#     # final_data_str = " ".join([f"{value:.10f}" for value in final_data.values()])

#     # # logging.info(final_data_str)

#     # print(final_data_str)

#     return final_data


# if __name__ == "__main__":
#     for i in tqdm(range(100000)):
#         main()


@lru_cache(maxsize=2500)
def cached_parse_data_file(path):
    """Cache the parsed data file (returns a NumPy array of 11 floats)."""
    return parse_data_file(path)


def unix_to_mjd(unix_timestamp):
    # Convert Unix timestamp to datetime in UTC
    dt = datetime.fromtimestamp(unix_timestamp, timezone.utc)

    # Julian Date calculation
    jd = dt.timestamp() / 86400.0 + 2440587.5

    # Modified Julian Date calculation
    mjd = jd - 2400000.5

    return mjd


def interpolate_ah(station, time):
    """
    Interpolate meteorological parameters between two data files using NumPy arrays.
    Caches file reads to optimize performance when processing many timestamps.

    Parameters:
      station (str): Station code (case-insensitive).
      time (float): Unix timestamp (seconds since 1970-01-01).

    Returns:
      numpy.ndarray: An array of 11 interpolated values in the order:
                     [LAT, LON, ALT, AH, AW, ZHD, ZWD, GN_H, GE_H, GN_W, GE_W]
    """
    station = station.upper()
    dt_obs = unix_to_utc(time)
    year, month, day, hour = dt_obs.year, dt_obs.month, dt_obs.day, dt_obs.hour

    # Determine the 6-hour interval
    begin, end = find_interval(hour)

    # Compute time since the beginning of the interval
    dt_begin = (
        dt_obs - datetime(year, month, day, begin, 0, 0, tzinfo=timezone.utc)
    ).total_seconds()
    proportion = dt_begin / six_hours_in_seconds

    # Build file path for the beginning of the interval
    path_begin = os.path.join(
        base_folder, station, str(year), str(month), str(day), f"{begin}{fileformat}"
    )

    # Determine file path for the end of the interval, accounting for day rollover
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
        f"{end_hour}{fileformat}",
    )

    # Read data using cached file parsing (assumes each returns a NumPy array of 11 values)
    data_begin = cached_parse_data_file(path_begin)
    data_end = cached_parse_data_file(path_end)

    # Interpolate: first three values (lat, lon, alt) remain constant.
    final_data = np.empty_like(data_begin)
    final_data[:3] = data_begin[:3]
    final_data[3:] = data_begin[3:] + (data_end[3:] - data_begin[3:]) * proportion

    return final_data
