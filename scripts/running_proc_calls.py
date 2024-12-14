import subprocess
import time, os
import ntpath
from tqdm import tqdm
from lib import *

# logging.basicConfig(
#     level=logging.DEBUG,
#     filename="scripts/logs/proc_calls.log",
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     datefmt="%d-%b-%y %H:%M:%S",
#     filemode="w",
# )

print(calls_path)
curr_delay_path_store = "curr_delaypath.txt"
curr_station_path_store = "curr_station_name.txt"


with open(calls_path) as calls_file:
    for entry in tqdm(calls_file, total=621):

        if not "inverno" in entry.lower():
            continue

        curr_delay_filepath, call = entry.strip("\n").split(",")

        filename = ntpath.basename(curr_delay_filepath)

        stationname = filename[0:4]

        # if the file already exists...
        remove_file_if_exists(curr_delay_filepath)

        with open(curr_delay_path_store, "w+") as curr_path_storage:
            curr_path_storage.write(curr_delay_filepath)

        with open(curr_station_path_store, "w+") as curr_station_storage:
            curr_station_storage.write(stationname)

        time.sleep(0.1)

        try:
            result = subprocess.run(
                call,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )

            logging.info(result.stdout)

        except subprocess.CalledProcessError as e:
            error_details = []

            error_details.append(f"Return code: {e.returncode}")
            error_details.append(f"Stdout: {e.stdout.strip()}")
            error_details.append(f"Stderr: {e.stderr.strip()}")

            error_message = "; ".join(error_details)

            logging.error(error_message)

        except Exception as e:
            logging.error(f"An unexpected error occurred while executing: {e}")
