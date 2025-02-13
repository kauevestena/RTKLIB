import sys

sys.path.append(".")
sys.path.append("scripts")

import requests
import numpy as np
import calendar, os
import pandas as pd
from io import StringIO
from tqdm import tqdm
from astropy.time import Time
import logging


# TO MODIFY:
proc_scenario = "orig_nograd"

# other constants:

calls_path = "app_calls.txt"

# don't forget to create the symlink to the VMF3 data!
rootpath_data = "/home/gnss_data"

outputs_path = os.path.join(rootpath_data, "saidas")

delays_header = "grad_e,grad_n,m_h,m_w_orig,m_w,zhd,zwd,x_0,x_1,x_2,tot_delay"

proc_sc_root = {
    "orig": os.path.join(outputs_path, "orig"),
    "orig_nograd": os.path.join(outputs_path, "orig_nograd"),
    "vmf3_grads": os.path.join(outputs_path, "vmf3_grads"),
    "mod_vmf3_grads": os.path.join(outputs_path, "mod_vmf3_grads"),
    # "mod_vmf3_ztd_orig": os.path.join(outputs_path, "mod_vmf3_ztd_orig"),
}

exec_paths = {
    "mod": "/home/RTKLIB/app/rnx2rtkp/gcc/rnx2rtkp",
    "orig": "/home/RTKLIB/rtklib_orig/RTKLIB/app/rnx2rtkp/gcc/rnx2rtkp",
}

proc_sc_execs = {
    "orig": exec_paths["orig"],
    "orig_nograd": exec_paths["orig"],
    "vmf3_grads": exec_paths["mod"],
    "mod_vmf3_grads": exec_paths["mod"],
    # "mod_vmf3_ztd_orig": exec_paths["mod"],
}

# from vmf3 import *

six_hours_in_seconds = 21600

fileformat = ".ac3"


horarios = [0, 6, 12, 18]

anos = [2020]

meses = [1, 6]

estacoes = {
    "BRAZ": (-15.947475341666668, -47.877869, 1106.02),
    "CUIB": (-15.55526355, -56.06986655, 237.444),
    "UFPR": (-25.44836915277778, -49.23095476944445, 925.807),
    "NAUS": (-3.022919663888889, -60.05501664444444, 93.89),
    "POAL": (-30.074042433333334, -51.11976478888889, 76.745),
    "PERC": (-8.05880088888889, -34.950384683333334, 12.212),
    "ONRJ": (-22.895700561111112, -43.224331597222224, 35.636),
    "SSA1": (-12.975158247222223, -38.51648463888889, -2.091),
    "SAGA": (-0.14385446666666668, -67.05778104166667, 94.886),
    "POLI": (-23.555648966666667, -46.73031199722222, 730.622),
}

estacoes_coord_fixas_mes = {
    "UFPR": {
        1: (-25.448366330, -49.230955455, 925.7937),
        7: (-25.448366312, -49.230955487, 925.7908),
    },
    "BRAZ": {
        1: (-15.947473053, -47.877869648, 1106.0139),
        7: (-15.947473023, -47.877869701, 1106.0065),
    },
    "CUIB": {
        1: (-15.555260742, -56.069867125, 237.4547),
        7: (-15.555260754, -56.069867137, 237.4481),
    },
    "NAUS": {
        1: (-3.022917473, -60.055017176, 93.8946),
        7: (-3.022917447, -60.055017222, 93.8603),
    },
    "ONRJ": {
        1: (-22.895698316, -43.224332344, 35.6385),
        7: (-22.895698284, -43.224332372, 35.6312),
    },
    "PERC": {
        1: (-8.058798649, -34.950385460, 12.2648),
        7: (-8.058798626, -34.950385510, 12.2525),
    },
    "POAL": {
        1: (-30.074040221, -51.119765334, 76.7476),
        7: (-30.074040185, -51.119765409, 76.7358),
    },
    "POLI": {
        1: (-23.555645502, -46.730312584, 730.6143),
        7: (-23.555645479, -46.730312597, 730.6135),
    },
    "SAGA": {
        1: (-0.143852298, -67.057781654, 94.8920),
        7: (-0.143852264, -67.057781693, 94.8773),
    },
    "SSA1": {
        1: (-12.975155975, -38.516485496, -2.1002),
        7: (-12.975155941, -38.516485520, -2.1078),
    },
}

base_folder = "vmf_grid"


def ajustar_longitude(lon):
    """
    Ajusta a longitude fornecida para estar no intervalo [0, 360).

    Parameters
    ----------
    lon : float
        Longitude em graus decimais.

    Returns
    -------
    float
        Longitude ajustada para estar no intervalo [0, 360).
    """
    if lon < 0:
        lon += 360
    return lon


def remove_file_if_exists(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


# Função para baixar o arquivo de uma URL
def baixar_arquivo_bruto(dia, mes, ano, horario, caminho_da_pasta=None):
    url = f"https://vmf.geo.tuwien.ac.at/trop_products/GRID/1x1/V3GR/V3GR_OP/{ano}/V3GR_{ano}{mes:02d}{dia:02d}.H{horario:02d}"

    try:
        resposta = requests.get(url)
        resposta.raise_for_status()

        if caminho_da_pasta:

            caminho_do_arquivo = os.path.join(
                caminho_da_pasta, f"{horario}{fileformat}"
            )

            gravar_arquivo(caminho_do_arquivo, resposta.text)

        return resposta.text
    except requests.HTTPError as e:
        print(f"Erro ao baixar o arquivo: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None


# Função para calcular a distância euclidiana entre dois pontos
def calcular_distancia(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


# Função para obter os 4 pontos mais próximos que formam um retângulo ao redor do ponto de interpolação
def obter_pontos_proximos(df, lat_alvo, lon_alvo):
    lon_alvo = ajustar_longitude(lon_alvo)

    df_lat_prox = df[(df["lat"] >= lat_alvo - 1) & (df["lat"] <= lat_alvo + 1)]
    df_lon_prox = df_lat_prox[
        (df_lat_prox["lon"] >= lon_alvo - 1) & (df_lat_prox["lon"] <= lon_alvo + 1)
    ]

    lat_min = df_lon_prox["lat"].min()
    lat_max = df_lon_prox["lat"].max()
    lon_min = df_lon_prox["lon"].min()
    lon_max = df_lon_prox["lon"].max()

    pontos_retangulo = df_lon_prox[
        ((df_lon_prox["lat"] == lat_min) | (df_lon_prox["lat"] == lat_max))
        & ((df_lon_prox["lon"] == lon_min) | (df_lon_prox["lon"] == lon_max))
    ]

    if len(pontos_retangulo) < 4:
        raise ValueError(
            "Não foi possível encontrar 4 pontos adequados para a interpolação."
        )

    # Verificar se a latitude e longitude alvo estão dentro dos intervalos encontrados
    if not (lat_min <= lat_alvo <= lat_max and lon_min <= lon_alvo <= lon_max):
        raise ValueError(
            "As coordenadas fornecidas estão fora do intervalo dos pontos disponíveis."
        )

    print(f"Coordenadas dos 4 pontos usados para interpolação (Lat, Lon):")
    for index, row in pontos_retangulo.iterrows():
        print(
            f"({row['lat']}, {row['lon']}) -> Distância: {calcular_distancia(row['lat'], row['lon'], lat_alvo, lon_alvo)}"
        )

    return pontos_retangulo


# Função para interpolação bilinear
def bilinear_interpolation(latd, lond, pontos):
    try:
        x1, y1, v1 = (
            pontos.iloc[0]["lon"],
            pontos.iloc[0]["lat"],
            pontos.iloc[0]["valor"],
        )
        x2, y2, v2 = (
            pontos.iloc[1]["lon"],
            pontos.iloc[1]["lat"],
            pontos.iloc[1]["valor"],
        )
        x3, y3, v3 = (
            pontos.iloc[2]["lon"],
            pontos.iloc[2]["lat"],
            pontos.iloc[2]["valor"],
        )
        x4, y4, v4 = (
            pontos.iloc[3]["lon"],
            pontos.iloc[3]["lat"],
            pontos.iloc[3]["valor"],
        )

        print(f"Pontos para interpolação:")
        print(f"Ponto 1: x1={x1}, y1={y1}, v1={v1}")
        print(f"Ponto 2: x2={x2}, y2={y2}, v2={v2}")
        print(f"Ponto 3: x3={x3}, y3={y3}, v3={v3}")
        print(f"Ponto 4: x4={x4}, y4={y4}, v4={v4}")

        # Calcular ga e gb
        ga = ((lond - x1) * (v2 - v1) / (x4 - x3)) + v1
        gb = ((lond - x1) * (v4 - v3) / (x4 - x3)) + v3

        # Calcular gi
        gi = (((y3 - y1) - (latd - y1)) * (ga - gb) / (y3 - y1)) + gb

        print(f"Resultado da interpolação: {gi}")
        return gi
    except IndexError:
        raise ValueError("Erro na seleção dos pontos para interpolação.")


# Função para processar o conteúdo do arquivo e salvar como ACE3
def processar_arquivo(
    conteudo,
    caminho_pasta,
    lat_alvo,
    lon_alvo,
    h_alvo,
    ano,
    mes,
    dia,
    horario_inicial,
    horario_final,
):

    caminho_arquivo = os.path.join(caminho_pasta, f"{horario_inicial}{fileformat}")

    print("Primeiras linhas do arquivo:")
    print(conteudo[:500])

    try:
        linhas = conteudo.splitlines()
        dados_inicio = False
        linhas_dados = []

        for linha in linhas:
            if linha.startswith("!"):
                continue
            if linha.strip() == "":
                continue
            if not dados_inicio:
                if len(linha.split()) >= 10:
                    dados_inicio = True
            if dados_inicio:
                linhas_dados.append(linha)

        dados = StringIO("\n".join(linhas_dados))
        df = pd.read_csv(dados, delim_whitespace=True, header=None)

        colunas = [
            "lat",
            "lon",
            "ah",
            "aw",
            "zhd",
            "zwd",
            "Gn_h",
            "Ge_h",
            "Gn_w",
            "Ge_w",
        ]
        if len(df.columns) == len(colunas):
            df.columns = colunas

            pontos_proximos = obter_pontos_proximos(df, lat_alvo, lon_alvo)

            precisao = {
                col: df[col]
                .apply(lambda x: len(str(x).split(".")[1]) if "." in str(x) else 0)
                .max()
                for col in colunas[2:]
            }

            precisao["ah"] = 10
            precisao["aw"] = 10

            valores_interpolados = {}
            for col in colunas[2:]:
                pontos_coluna = pontos_proximos[["lat", "lon", col]].rename(
                    columns={col: "valor"}
                )
                try:
                    interpolado = bilinear_interpolation(
                        lat_alvo, ajustar_longitude(lon_alvo), pontos_coluna
                    )
                    if pd.isna(interpolado):
                        print(
                            f"Não foi possível interpolar o valor para a variável {col} nas coordenadas fornecidas."
                        )
                    else:
                        valores_interpolados[col] = interpolado
                except ValueError as e:
                    print(f"Erro na interpolação da variável {col}: {e}")

            with open(caminho_arquivo, "w") as f:
                f.write(
                    f"ACECOR {ano} {mes:02d} {dia:02d} {horario_inicial:02d} {horario_final if horario_final else horario_inicial:02d}\n"
                )
                f.write("LAT LON ALT AH AW ZHD ZWD GN_H GE_H GN_W GE_W\n")

                f.write(f"{lat_alvo:6.8f} {lon_alvo:7.8f} {h_alvo:6.3f}")
                for col in colunas[2:]:
                    if col in valores_interpolados:
                        f.write(
                            f" {valores_interpolados[col]:.{precisao.get(col, 6)}f}"
                        )
                    else:
                        f.write("  NaN")
                f.write("\n")

            print(f"Arquivo ACE3 '{caminho_arquivo}' gerado com sucesso.")
        else:
            print("O formato dos dados no arquivo não corresponde ao esperado.")
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")


def days_of_month(month, year):
    # Check if the month and year are valid
    if month < 1 or month > 12:
        return "Invalid month. Please enter a month between 1 and 12."
    if year < 1:
        return "Invalid year. Please enter a valid year."

    # Get the number of days in the month
    _, num_days = calendar.monthrange(year, month)

    # Return a list of day numbers
    return list(range(1, num_days + 1))


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


create_dir(base_folder)


def gravar_arquivo(caminho_arquivo, conteudo):
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo)


def ler_arquivo(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        return f.read()


def gps_time_to_utc(gps_seconds):
    """
    Convert GPS time in seconds since GPS epoch to UTC datetime.

    Parameters:
        gps_seconds (float): GPS time in seconds since GPS epoch (1980-01-06T00:00:00Z)

    Returns:
        datetime.datetime: UTC datetime corresponding to the given GPS time.
    """
    # Create a Time object in GPS format and TAI scale
    t = Time(gps_seconds, format="gps", scale="tai")
    # Convert to UTC scale
    t_utc = t.utc
    # Return as a naive datetime object (no timezone info)
    return t_utc.datetime


def find_interval(hour, intervals):
    for interval in intervals:
        if interval[0] <= hour < interval[1]:
            return interval
    return None  # In case the hour doesn't match any interval


def parse_data_file(file_path):
    result = {}

    with open(file_path, "r") as file:
        # Read the first line (Station, Date, Time info)
        header_line = file.readline().strip()
        station, year, month, day, hour, minute = header_line.split()

        # Store the station and time info
        result["station"] = station
        result["date"] = f"{year}-{month}-{day}"
        result["time"] = f"{hour}:{minute}"

        # Read the second line (column headers)
        headers = file.readline().strip().lower().split()

        # Read the third line (values)
        values = file.readline().strip().split()

        # Combine headers and values into a dictionary
        data_dict = {headers[i]: float(values[i]) for i in range(len(headers))}

        # Add the data dictionary to the result
        result["data"] = data_dict

    return result
