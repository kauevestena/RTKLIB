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




def calcular_derivadas_mapeamento(a, b, c, el):
    """
    Calcula a primeira e segunda derivadas da função de mapeamento VMF3
    Retorna: (primeira_derivada, segunda_derivada)
    """
    sin_el = sin(el)
    cos_el = cos(el)

    # Termos intermediários
    temp1 = sin_el + c
    temp2 = sin_el + b / temp1
    temp3 = sin_el + a / temp2

    # Primeira derivada
    term4 = (b * cos_el) / (temp1**2)
    term5 = cos_el - term4
    term6 = a * term5
    term7 = temp2**2
    term8 = term6 / term7
    primeira_derivada = -(cos_el - term8) / (temp3**2)

    # Segunda derivada (cálculo simplificado)
    d_temp1 = cos_el
    d_temp2 = cos_el - (b * d_temp1) / (temp1**2)
    d_temp3 = cos_el - (a * d_temp2) / (temp2**2)

    d_term4 = (-b * sin_el * (temp1 * 2) - 2 * b * cos_el * temp1 * d_temp1) / (
        temp1 * 4
    )
    d_term5 = -sin_el - d_term4
    d_term6 = a * d_term5
    d_term7 = 2 * temp2 * d_temp2
    d_term8 = (d_term6 * term7 - term6 * d_term7) / (
        term7**2
    )  # Corrigido: term7 em vez de temp7

    d_numerador = -(-sin_el - d_term8)
    d_denominador = 2 * temp3 * d_temp3

    segunda_derivada = (
        d_numerador * (temp3 * 2) - (-(cos_el - term8)) * d_denominador
    ) / (temp3 * 4)

    return primeira_derivada, segunda_derivada





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
    mfh, mfw, bh, bw, ch, cw, el, doy = vmf3_ht(
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
    # mfh_grads = mfh * (gn_h * cos_az + ge_h * sin_az)


    trop_corr_nograd = mfh * zhd + mfw * zwd

    prim_deriv_w, _ = calcular_derivadas_mapeamento(
        aw,bw,cw, el
    )  

    trop_corr = trop_corr_nograd + prim_deriv_w * (gn_w * cos_az + ge_w * sin_az)


    with open(delaypath, "a") as f:



        f.write(
            f"{ge_h+ge_w:.6f},{gn_h+gn_w:.6f},{mfh:.6f},{mfw:.6f},{mfw_grads:.6f},{zhd:.6f},{zwd:.6f},0,0,0,{trop_corr:5f},{time},{mjd},{az*RAD2DEG},{el*RAD2DEG},{zd*RAD2DEG},{ah},{aw},{trop_corr:.6f}\n"
        )

    return trop_corr

