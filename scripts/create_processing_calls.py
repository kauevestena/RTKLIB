import os, subprocess, glob, datetime
from gnsscal import date2gpswd
from lib import *
from tqdm import tqdm

# TO MODIFY:
proc_scenario = "orig"

####################################

rnx2rtkp_path = proc_sc_execs[proc_scenario]

basepath = rootpath_data

epochs = ["VERAO", "INVERNO"]

stations = list(estacoes.keys())

custom_op_modes = {
    # "ztd": False,
    "ztdgrad": True
}

# fixed filenames
satant_filename = "igs14.atx"

# subfolders = ['fixos','relogios','efemerides','param_terra','RINEX']


def checkpath(input_path):
    if not os.path.exists(input_path):
        raise Exception(f"Arquivo\n {input_path} \nInexistente!!")


def check_listofpaths(inputlist):
    for path in inputlist:
        checkpath(path)


def date_from_rnxdateline(inputrnxline):
    as_list = inputrnxline.split()

    year, month, day = as_list[:3]

    return datetime.date(year=int(year), month=int(month), day=int(day))


def get_rinex_date(inputpath, key="TIME OF FIRST OBS"):
    with open(inputpath) as inputfile:
        for line in inputfile:
            if key in line:
                return date_from_rnxdateline(line)


def create_dir_ifnotexists(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def select_by_key_in_list(inputlist, inputkey):
    for inputstring in inputlist:
        if inputkey in inputstring:
            return inputstring


def compose_path_selecting_bykey(basepath, inputlist, inputkey):
    filename = select_by_key_in_list(inputlist, inputkey)
    return os.path.join(basepath, filename)


def create_conf_file(eop_filepath, outpath, ztd_default_mode=True):

    ztd_mode = "est-ztd"

    if not ztd_default_mode:
        ztd_mode = "est-ztdgrad"

    file_as_string = f""" # rtkpost options
pos1-posmode       =ppp-kine  # (0:single,1:dgps,2:kinematic,3:static,4:movingbase,5:fixed,6:ppp-kine,7:ppp-static)
pos1-frequency     =l1+l2      # (1:l1,2:l1+l2,3:l1+l2+l5)
pos1-soltype       =combined    # (0:forward,1:backward,2:combined)
pos1-elmask        =7         # (deg)
pos1-dynamics      =off        # (0:off,1:on)
pos1-tidecorr      =on        # (0:off,1:on)
pos1-ionoopt       =dual-freq       # (0:off,1:brdc,2:sbas,3:dual-freq,4:est-stec)
pos1-tropopt       ={ztd_mode}      # (0:off,1:saas,2:sbas,3:est-ztd,4:est-ztdgrad)
pos1-sateph        =precise       # (0:brdc,1:precise,2:brdc+sbas,3:brdc+ssrapc,4:brdc+ssrcom)
pos1-exclsats      =           # (prn ...)
pos1-navsys        =5          # (1:gps+2:sbas+4:glo+8:gal+16:qzs+32:comp)
pos2-armode        =off # (0:off,1:continous,2:instantaneous,3:fix-and-hold,4:ppp-ar)
pos2-arthres       =3
pos2-arlockcnt     =10
pos2-arelmask      =10          # (deg)
pos2-aroutcnt      =5
pos2-arminfix      =10
pos2-slipthres     =0.05       # (m)
pos2-maxage        =30         # (s)
pos2-rejionno      =30         # (m)
pos2-niter         =1
out-solformat      =llh        # (0:llh,1:xyz,2:enu,3:nmea)
out-outhead        =on         # (0:off,1:on)
out-outopt         =on         # (0:off,1:on)
out-timesys        =gpst       # (0:gpst,1:utc,2:jst)
out-timeform       =hms        # (0:tow,1:hms)
out-timendec       =3
out-degform        =dms        # (0:deg,1:dms)
out-fieldsep       =
out-height         =ellipsoidal # (0:ellipsoidal,1:geodetic)
out-geoid          =internal   # (0:internal,1:egm96,2:egm08_2.5,3:egm08_1,4:gsi2000)
#out-solstatic      =all        # (0:all,1:single)
out-solstatic      =single     # (0:all,1:single)
out-nmeaintv1      =0          # (s)
out-nmeaintv2      =0          # (s)
out-outstat        =off        # (0:off,1:state,2:residual)
stats-errratio     =100
stats-errphase     =0.003      # (m)
stats-errphaseel   =0.003      # (m)
stats-errphasebl   =0          # (m/10km)
stats-errdoppler   =10         # (Hz)
stats-stdbias      =30         # (m)
stats-stdiono      =0.03       # (m)
stats-stdtrop      =0.3        # (m)
stats-prnaccelh    =1          # (m/s^2)
stats-prnaccelv    =0.1        # (m/s^2)
stats-prnbias      =0.0001     # (m)
stats-prniono      =0.001      # (m)
stats-prntrop      =0.0001     # (m)
stats-clkstab      =5e-12      # (s/s)
ant1-postype       =llh        # (0:llh,1:xyz,2:single,3:posfile,4:rinexhead,5:rtcm)
ant1-pos1          =0          # (deg|m)
ant1-pos2          =0          # (deg|m)
ant1-pos3          =0          # (m|m)
ant1-anttype       =*
ant1-antdele       =0          # (m)
ant1-antdeln       =0          # (m)
ant1-antdelu       =0          # (m)
ant2-postype       =single     # (0:llh,1:xyz,2:single,3:posfile,4:rinexhead,5:rtcm)
ant2-pos1          =0          # (deg|m)
ant2-pos2          =0          # (deg|m)
ant2-pos3          =0          # (m|m)
ant2-anttype       =*
ant2-antdele       =0          # (m)
ant2-antdeln       =0          # (m)
ant2-antdelu       =0          # (m)
misc-timeinterp    =on         # (0:off,1:on)
misc-sbasatsel     =0          # (0:all)
file-eopfile       ={eop_filepath} """

    # file-outztdfile    ={delays_outpath}

    with open(outpath, "w+") as outfile:
        outfile.write(file_as_string)


# doing the processing stuff
with open("app_calls.txt", "w+", encoding="utf-8") as calls_file:
    for epoch in tqdm(epochs):
        epochpath = os.path.join(basepath, epoch)

        for station in tqdm(stations):

            # basepath for subfolders with input files
            station_epoch_path = os.path.join(epochpath, "RBMC", station)
            station_epoch_path_list = os.listdir(station_epoch_path)

            # subfolders paths
            rinex_folderpath = os.path.join(station_epoch_path, "RINEX")
            clock_path = os.path.join(epochpath, "Relogio", "igs")
            ephem_path = os.path.join(epochpath, "sp3")
            eop_path = os.path.join(epochpath, "erp")
            station_param_files_path = os.path.join(epochpath, "fixos")

            # list of files in subfolders:
            rinexfilelist = os.listdir(rinex_folderpath)
            eop_filelist = os.listdir(eop_path)
            clock_filelist = os.listdir(clock_path)
            ephem_filelist = os.listdir(ephem_path)
            station_param_files_list = os.listdir(station_param_files_path)

            # creating configuration files dir:
            configurations_outpath = os.path.join(station_epoch_path, "confs")
            create_dir_ifnotexists(configurations_outpath)

            # creating out_dirs
            otput_dirpath = os.path.join(station_epoch_path, "saidas")

            specific_outdirpaths = {}

            # specific for each subconfiguration:
            for conf in custom_op_modes:
                conf_outpath = os.path.join(otput_dirpath, conf)
                create_dir_ifnotexists(conf_outpath)
                specific_outdirpaths[conf] = conf_outpath

            # files that are fixed by station in epoch of year
            dcb_file_path = compose_path_selecting_bykey(
                station_param_files_path, station_param_files_list, "DCB"
            )

            blq_filepath = compose_path_selecting_bykey(
                station_epoch_path, station_epoch_path_list, "blq"
            )

            rcv_ant_path = compose_path_selecting_bykey(
                station_epoch_path, station_epoch_path_list, "atx"
            )

            # rcv_ant_filename = station.lower() + ".atx"
            # rcv_ant_path = os.path.join(station_param_files_path, rcv_ant_filename)

            # if not os.path.exists(rcv_ant_path):
            #     rcv_ant_filename = station.upper() + ".atx"
            #     rcv_ant_path = os.path.join(station_param_files_path, rcv_ant_filename)

            sat_ant_path = os.path.join(rootpath_data, satant_filename)

            bystation_filestocheck = [
                dcb_file_path,
                blq_filepath,
                rcv_ant_path,
                sat_ant_path,
            ]

            check_listofpaths(bystation_filestocheck)

            for rinexfilename in tqdm(rinexfilelist):
                # if "corr2" in rinexfilename:
                if not rinexfilename.endswith("d"):
                    continue

                if not ".pos" in rinexfilename:
                    for option in custom_op_modes:

                        rinex_basename = rinexfilename.split(".")[0]

                        rinex_ext_base = rinexfilename.split(".")[1][0:-1]

                        rinex_uni_base = rinex_basename + "." + rinex_ext_base

                        # os.path.join(station_epoch_path,)

                        # rinex_file_path = os.path.join(rinex_folderpath, rinexfilename)
                        rinex_file_path = os.path.join(
                            rinex_folderpath, rinex_uni_base + "d"
                        )
                        print(rinex_file_path, " - ", option)

                        rinex_date = get_rinex_date(rinex_file_path)

                        rinex_gpsweek, rinex_dayofweek = date2gpswd(rinex_date)

                        rinex_gpsweek = str(rinex_gpsweek)
                        rinex_dayofweek = str(rinex_dayofweek)

                        rinex_composed_gpsday = (
                            rinex_gpsweek + rinex_dayofweek
                        )  # also known as "GPS Week Number"

                        eop_filepath = compose_path_selecting_bykey(
                            eop_path, eop_filelist, rinex_gpsweek
                        )

                        # generating configuration file
                        configuration_path = os.path.join(
                            configurations_outpath,
                            rinex_basename + "_" + option + ".conf",
                        )

                        outpath_delays = os.path.join(
                            specific_outdirpaths[option],
                            rinex_basename + "_atrasos.txt",
                        )

                        create_conf_file(
                            eop_filepath,
                            configuration_path,
                            custom_op_modes[option],
                        )

                        rinex_n_path = os.path.join(
                            rinex_folderpath, rinex_uni_base + "n"
                        )

                        rinex_g_path = os.path.join(
                            rinex_folderpath, rinex_uni_base + "g"
                        )

                        outfolderpath = os.path.join(
                            proc_sc_root[proc_scenario], epoch, station
                        )

                        create_dir_ifnotexists(outfolderpath)

                        outpath = os.path.join(
                            outfolderpath,
                            rinex_basename + "_res.pos",
                        )

                        igs_filename = f"igs{rinex_composed_gpsday}.sp3.Z"
                        sp3_igs_path = os.path.join(ephem_path, igs_filename)

                        igl_filename = f"igl{rinex_composed_gpsday}.sp3.Z"
                        sp3_igl_path = os.path.join(ephem_path, igl_filename)

                        clk_path = compose_path_selecting_bykey(
                            clock_path, clock_filelist, rinex_composed_gpsday
                        )

                        by_rinex_folderpaths_to_check = [
                            rinex_n_path,
                            rinex_g_path,
                            sp3_igl_path,
                            sp3_igs_path,
                            eop_filepath,
                            rinex_file_path,
                            clk_path,
                            configuration_path,
                        ]
                        check_listofpaths(by_rinex_folderpaths_to_check)

                        app_call = f"{rnx2rtkp_path} -k {configuration_path} -o {outpath} {rinex_file_path} {rinex_n_path} {rinex_g_path} {sp3_igs_path} {sp3_igl_path} {clk_path} {blq_filepath} {sat_ant_path} {rcv_ant_path} {dcb_file_path}"

                        # calls_file.write(app_call+'\n')
                        calls_file.write(f"{outpath_delays},{app_call}\n")

                        calls_file.flush()

                        # end
