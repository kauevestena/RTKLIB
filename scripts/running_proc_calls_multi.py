import subprocess
import time, os
import ntpath
from tqdm import tqdm
from lib import *
import concurrent.futures
import logging

n_processes = 36

curr_delay_path_store = "curr_delaypath.txt"
curr_station_path_store = "curr_station_name.txt"


def exec_call(call_entry):
    curr_delay_filepath, call = call_entry.strip("\n").split(",")

    filename = ntpath.basename(curr_delay_filepath)

    stationname = filename[0:4]

    # if the file already exists...
    remove_file_if_exists(curr_delay_filepath)

    with open(curr_delay_path_store, "w+") as curr_path_storage:
        curr_path_storage.write(curr_delay_filepath)

    with open(curr_station_path_store, "w+") as curr_station_storage:
        curr_station_storage.write(stationname)

    time.sleep(0.1)

    subprocess.run(call, shell=True)


def main():
    with open(calls_path) as calls_file:
        all_calls = calls_file.readlines()

    with tqdm(total=len(tiles_gdf), desc=state_acronym) as pbar:

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=num_processes
        ) as executor:
            futures = [executor.submit(cell_exec, entry) for entry in to_be_iter]

            for future in concurrent.futures.as_completed(futures):
                try:
                    pbar.update()
                    future.result()  # Ensures the future is completed

                except Exception as exc:
                    logging.error(f"{state_acronym} : {exc}")


if __name__ == "__main__":
    main()
