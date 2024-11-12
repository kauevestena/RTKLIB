import subprocess
import time, os
import ntpath
from tqdm import tqdm
from lib import *

print(calls_path)
curr_delay_path_store = "curr_delaypath.txt"
curr_station_path_store = "curr_station_name.txt"


with open(calls_path) as calls_file:
    for entry in tqdm(calls_file, total=621):

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

        subprocess.run(call, shell=True)
