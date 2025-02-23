import os
import time
import struct
import hashlib
from tqdm import tqdm

FILE_PATH = "/home/RTKLIB/delay_val.txt"


def read_value_and_hash():
    """
    Reads 8 bytes from the file (a double in binary form) and returns
    a tuple (value, hash) where value is the unpacked double and hash
    is an MD5 hex digest of the raw data.
    """
    with open(FILE_PATH, "rb") as f:
        data = f.read(8)
        if len(data) < 8:
            return None, None
        return hashlib.md5(data).hexdigest()


def main():
    # Get an initial value and hash.
    current_hash = read_value_and_hash()

    # Create a tqdm progress bar with a total of 100.0.
    pbar = tqdm(total=20000)

    try:
        while True:
            new_hash = read_value_and_hash()
            if new_hash != current_hash:
                # The file content has changed—update the progress bar in a single step.
                pbar.update(1)
                current_hash = new_hash
            # time.sleep(0.1)  # Poll every 100ms.
    except KeyboardInterrupt:
        pbar.close()


if __name__ == "__main__":
    main()
