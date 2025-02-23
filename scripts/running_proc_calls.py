import subprocess
import time, os
import ntpath
from tqdm import tqdm

try:
    from scripts.lib import *
except ImportError:
    from lib import *

logging.basicConfig(
    level=logging.DEBUG,
    filename="scripts/logs/proc_calls.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    filemode="w",
)

print(calls_path)
curr_delay_path_store = "curr_delaypath.txt"
curr_station_path_store = "curr_station_name.txt"


# set the environment variables that are going to be called on the C program:
os.environ["PYTHONPATH_RTKLIB"] = python_path = "/home/RTKLIB/.venv/bin/python"
os.environ["AH_SCRIPT_PATH"] = ah_path = "/home/RTKLIB/scripts/interpolate_ah.py"
os.environ["VMF3_PATH"] = vmf3_path = "/home/RTKLIB/scripts/vmf3.py"

if proc_scenario not in ("orig", "orig_nograd"):
    inner_command = f"'{python_path} {vmf3_path}'"
    subprocess.run(f'xterm -hold -e "bash -c {inner_command}" &', shell=True)
    logging.info("VMF3 script executed, sleeping for 5 seconds")
    time.sleep(5)

# resuming capabilities:
processed_dict = read_json_file("processed_list.json")

with open(calls_path) as calls_file:
    for entry in tqdm(calls_file, total=621):

        # if not "inverno" in entry.lower():
        #     continue

        curr_delay_filepath, call = entry.strip("\n").split(",")

        if curr_delay_filepath in processed_dict:
            logging.info(f"{curr_delay_filepath} already processed, skipping...")
            continue

        filename = ntpath.basename(curr_delay_filepath)

        stationname = filename[0:4]

        # setting "CURRENT_STATION" and "CURRENT_DELAYPATH" environment variables:
        os.environ["CURRENT_STATION"] = stationname
        os.environ["CURRENT_DELAYPATH"] = curr_delay_filepath

        # if the file already exists...
        if proc_scenario not in ("orig", "orig_nograd"):
            with open(curr_delay_filepath, "w+") as f:
                f.write(delays_header + "\n")
        else:
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

            logging.info(f"{curr_delay_filepath} processed")

            processed_dict[curr_delay_filepath] = call

            dump_json_file("processed_list.json", processed_dict)

        except subprocess.CalledProcessError as e:
            error_details = []

            error_details.append(f"Return code: {e.returncode}")
            error_details.append(f"Stdout: {e.stdout.strip()}")
            error_details.append(f"Stderr: {e.stderr.strip()}")

            error_message = "; ".join(error_details)

            logging.error(error_message)

        except Exception as e:
            logging.error(f"An unexpected error occurred while executing: {e}")
