import sys

sys.path.append("/home/RTKLIB/scripts")


from interpolate_ah import *
from scripts.vm3_func import *

import numpy as np

# import argparse, os
from math import sin, cos

# import struct

import logging

from math import floor

logging.basicConfig(
    level=logging.DEBUG,
    filename="/home/RTKLIB/scripts/logs/vmf_processing.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    filemode="w",
    encoding="utf-8",
)


# HOST = "127.0.0.1"
# PORT = 5000







def process(data_as_str, station, delaypath):
    # station = os.environ["CURRENT_STATION"]

    time, _, az, el = tuple(map(float, data_as_str.split(",")))

    mjd = unix_to_mjd(time)

    # ZD in radians
    zd = (90 * DEG2RAD) - el


    # new order: LAT LON ALT AH AW ZHD ZWD GN_H GE_H GN_W GE_W
    lat, lon, h_ell, ah, aw, zhd, zwd, gn_h, ge_h, gn_w, ge_w = interpolate_ah(
        station, time
    )

    lat_rad = lat * DEG2RAD
    lon_rad = lon * DEG2RAD

    # mfh, mfw, bh, bw, ch, cw, el = vmf3_ht(ah, aw, mjd, lat, lon, h_ell, zd)
    mfh, mfw, _, _, _, _, el, _ = vmf3_ht(
        mjd=mjd, lat=lat_rad, lon=lon_rad, h_ell=h_ell, zd=zd, ah=ah, aw=aw
    )

    # getting the day-of-year
    dt_obs = unix_to_utc(time)
    _, doy = date_to_year_doy(dt_obs)

    # checking/fixing delaypath:
    if not station.upper() in delaypath:
        part_of_the_year = "INVERNO" if doy > 180 else "VERAO"
        delaypath = os.path.join(delaypath,part_of_the_year,station.upper(),"delays",f"{station.lower()}{floor(doy):03d}_delays.txt")

    cos_az = cos(az)
    sin_az = sin(az)

    mfw_grads = mfw * (gn_w * cos_az + ge_w * sin_az)
    mfh_grads = mfh * (gn_h * cos_az + ge_h * sin_az)


    trop_corr_nograd = mfh * zhd + mfw * zwd

    trop_corr = trop_corr_nograd + mfh_grads + mfw_grads


    with open(delaypath, "a") as f:



        f.write(
            f"{ge_h+ge_w:.6f},{gn_h+gn_w:.6f},{mfh:.6f},{mfw:.6f},{mfw_grads:.6f},{zhd:.6f},{zwd:.6f},0,0,0,{trop_corr:5f},{time},{mjd},{az*RAD2DEG},{el*RAD2DEG},{zd*RAD2DEG},{ah},{aw},{trop_corr:.6f}\n"
        )

    return trop_corr

