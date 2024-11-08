import subprocess
import time, os
import ntpath


# make path:
make_path = "/home/lape04/RTKLIB/app/rnx2rtkp/gcc"


# to remake before run:
subprocess.run(f"cd {make_path} && make", shell=True)


calls_path = "app_calls.txt"
print(calls_path)
curr_delay_path_store = "curr_delaypath.txt"
curr_station_path_store = "curr_station_name.txt"


def print_rem_time_info(total_it, curent_it, ref_time):
    # "it" stands for 'iteration'
    it_time = time.time() - ref_time
    rem_its = total_it - curent_it
    rem_time = it_time * rem_its
    print(
        "took {:.4f} seconds, estimated remaining time: {:.4f} minutes or {:.4f} hours, iteration {} of {}".format(
            it_time, rem_time / 60.0, rem_time / 3600.0, curent_it, total_it
        )
    )


def line_count(filename):
    # thx: https://stackoverflow.com/a/43179213/4436950
    return int(subprocess.check_output(["wc", "-l", filename]).split()[0])


numberoflines = line_count(calls_path)


with open(calls_path) as calls_file:
    for i, entry in enumerate(calls_file):
        t1 = time.time()

        curr_delay_filepath, call = entry.strip("\n").split(",")

        filename = ntpath.basename(curr_delay_filepath)

        stationname = filename[0:4]

        # if the file already exists...
        if os.path.exists(curr_delay_filepath):
            os.remove(curr_delay_filepath)

        with open(curr_delay_path_store, "w+") as curr_path_storage:
            curr_path_storage.write(curr_delay_filepath)

        with open(curr_station_path_store, "w+") as curr_station_storage:
            curr_station_storage.write(stationname)

        time.sleep(0.5)

        print("current call: ", call)
        subprocess.run(call, shell=True)

        print()
        print_rem_time_info(numberoflines, i, t1)
        print()
