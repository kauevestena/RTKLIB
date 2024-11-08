from lib import *

for e in ["INVERNO", "VERAO"]:
    rbmc_path = os.path.join(rootpath_data, e, "RBMC")
    for station in os.listdir(rbmc_path):
        for filename in os.listdir(os.path.join(rbmc_path, station)):
            if "cargas" in filename:
                filepath = os.path.join(rbmc_path, station, filename)
                print(filepath)
                if filepath.endswith(".txt"):
                    os.rename(filepath, filepath.replace(".txt", ".blq"))
