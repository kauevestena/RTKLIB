import subprocess
import time, os
import ntpath
from tqdm import tqdm

N_PROCESSES = 2

try:
    from scripts.lib import *
except ImportError:
    from lib import *

logging.basicConfig(
    level=logging.DEBUG,
    filename="scripts/logs/proc_calls_multi.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    filemode="w",
)

print(calls_path)
curr_delay_path_store = "curr_delaypath.txt"
curr_station_path_store = "curr_station_name.txt"


def entry_proc(runstring):
    logging.info(f"Processing {runstring}...")
    result = subprocess.run(
        runstring,
        shell=True,
        check=True,
        capture_output=True,
        text=True,
    )

    logging.info(f"{runstring} processed")

    append_to_file(already_done_calls_path, runstring)

    return result


if proc_scenario in ("orig", "orig_nograd"):
    logging.error("This script is not meant to be run in 'orig' or 'orig_nograd' mode")
    exit(1)

launch_proc_server(False)


def main():
    # Resuming capabilities: read the list of already processed stations to avoid reprocessing them
    processed_station_list = read_file_as_list(already_done_stations_path)

    # Processing is now done on a per-station basis:
    stationwise_calls = read_json_file(stationwise_calls_path)

    # setting the environment for "PROC_SCENARIO"
    os.environ["PROC_SCENARIO"] = proc_scenario
    send_environ("PROC_SCENARIO")

    for stationname in tqdm(stationwise_calls):
        os.environ["CURRENT_STATION"] = stationname

        if stationname in processed_station_list:
            logging.info(f"{stationname} already processed, skipping...")
            continue
        else:
            send_environ("CURRENT_STATION")

            list_to_process = stationwise_calls[stationname]

            list_to_process = clean_unfinished_outputs(list_to_process)

            logging.info(
                f"Processing station {stationname} with {len(list_to_process)} calls"
            )

            results = parallel_exec(list_to_process, entry_proc, N_PROCESSES)

            logging.info(
                f"Finished processing station {stationname}, results: \n {results}"
            )

            processed_station_list.append(stationname)

            write_list_to_file(processed_station_list, already_done_stations_path)


if __name__ == "__main__":
    main()
