"""
==========================================================================

MET2MOD
ERA5 -> ADCIRC OWI Converter (Python Version)

This script reproduces the functionality of

    Convert2OWI_ALL_YEARS.m
    WriteOwi.m

using Python.

Author:
Yusuf Taofiq

==========================================================================

Workflow

ERA5 NetCDF
        ↓
Read meteorological variables
        ↓
Reorient ERA5 grids
        ↓
Convert pressure (Pa -> mb)
        ↓
Write ADCIRC OWI (*.pre, *.win)

==========================================================================

"""

from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
from netCDF4 import Dataset



# ======================================================================
# USER SETTINGS
# ======================================================================

# Folder containing yearly ERA5 NetCDF files: Update location of your .nc files
INPUT_DIR = Path(
    r"C:\Users\tyusuf1.LSU\OneDrive - Louisiana State University"
    r"\RESEARCH\ADCIRC_GULF_BC\ADCIRC_BC_LARGE_FILES\ERA5_YEARLY_DATA\2009_TO_2018"
)

# Folder where OWI files will be written: change to your desired folder
OUTPUT_DIR = Path(
    r"C:\Users\tyusuf1.LSU\OneDrive - Louisiana State University"
    r"\RESEARCH\ADCIRC_GULF_BC\ADCIRC_BC_LARGE_FILES\ERA5_YEARLY_DATA\2009_TO_2018\2009_2018_WIN_AND_PRE_FILES"
)

# Years to process
START_YEAR = 2009
END_YEAR   = 2018 #2025

# ======================================================================



def matlab_datestr30(dt):
    """
    Reproduce MATLAB:

        datestr(time,30)

    followed by

        t([9 14 15])=[]

    giving

        YYYYMMDDHH
    """

    return dt.strftime("%Y%m%d%H%M")
def matlab_file_header_time(dt):
    """
    MATLAB equivalent for the first OWI file header.

    Returns:
        YYYYMMDDHH
    """
    return dt.strftime("%Y%m%d%H")

# ======================================================================


def print_banner():

    print()
    print("=" * 70)
    print(" MET2MOD : ERA5 -> ADCIRC OWI Converter")
    print("=" * 70)
    print(f"Input Folder : {INPUT_DIR}")
    print(f"Output Folder: {OUTPUT_DIR}")
    print(f"Years        : {START_YEAR} - {END_YEAR}")
    print("=" * 70)
    print()


# ======================================================================


def check_directories():

    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"\nInput directory does not exist:\n{INPUT_DIR}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ======================================================================


def build_filename(year):

    return INPUT_DIR / f"era5_{year}.nc"


# ======================================================================


def output_prefix(year):

    return OUTPUT_DIR / f"era5_{year}_formatOWI"


# ======================================================================


def matlab_time_vector(seconds_since_1970):

    """
    Convert ERA5 valid_time

        seconds since 1970-01-01

    into Python datetime objects.
    """

    origin = datetime(1970, 1, 1)

    return [
        origin + timedelta(seconds=int(s))
        for s in seconds_since_1970
    ]
# ======================================================================
# READ ERA5 NETCDF
# ======================================================================

def read_era5(nc_file):
    """
    Reads one ERA5 NetCDF file and returns data formatted exactly
    as required by ADCIRC OWI.

    MATLAB equivalent:

        time = ncread(...)
        lat  = ncread(...)
        lon  = ncread(...)
        msl  = ncread(...)
        u10  = ncread(...)
        v10  = ncread(...)

        msl = permute(msl,[2 1 3]);
        u10 = permute(u10,[2 1 3]);
        v10 = permute(v10,[2 1 3]);

        msl = flipud(msl);
        u10 = flipud(u10);
        v10 = flipud(v10);
    """

    print(f"Reading {nc_file.name}")

    ds = Dataset(nc_file, "r")

    print("\nNetCDF variable shapes:")
    print("msl :", ds.variables["msl"].shape)
    print("u10 :", ds.variables["u10"].shape)
    print("v10 :", ds.variables["v10"].shape)
    print("lat :", ds.variables["latitude"].shape)
    print("lon :", ds.variables["longitude"].shape)
    print()
    # --------------------------------------------------------------
    # Read ERA5 time
    # --------------------------------------------------------------

    seconds_since_1970 = ds.variables["valid_time"][:]

    time = matlab_time_vector(seconds_since_1970)

    # --------------------------------------------------------------
    # Coordinates
    # --------------------------------------------------------------

    lat = ds.variables["latitude"][:].astype(np.float64)

    lon = ds.variables["longitude"][:].astype(np.float64)

    # --------------------------------------------------------------
    # Meteorological variables
    # --------------------------------------------------------------

    msl = ds.variables["msl"][:].astype(np.float64)

    u10 = ds.variables["u10"][:].astype(np.float64)

    v10 = ds.variables["v10"][:].astype(np.float64)

    ds.close()

    # --------------------------------------------------------------
    # Convert pressure
    #
    # MATLAB:
    #
    # msl = msl * 0.01;
    # --------------------------------------------------------------

    msl *= 0.01

    # --------------------------------------------------------------
    # ERA5
    #
    # longitude × latitude × time
    #
    # MATLAB:
    #
    # permute(...,[2 1 3])
    # --------------------------------------------------------------

    msl = np.transpose(msl, (1, 2, 0))

    u10 = np.transpose(u10, (1, 2, 0))

    v10 = np.transpose(v10, (1, 2, 0))

    # --------------------------------------------------------------
    # MATLAB:
    #
    # flipud(...)
    #
    # Flip latitude so northernmost row is first.
    # --------------------------------------------------------------

    msl = np.flipud(msl)

    u10 = np.flipud(u10)

    v10 = np.flipud(v10)

    # --------------------------------------------------------------
    # Grid information
    # --------------------------------------------------------------

    nlat = len(lat)

    nlon = len(lon)

    dx = abs(lon[1] - lon[0])

    dy = abs(lat[1] - lat[0])

    swlat = lat[-1]

    swlon = lon[0]

    ygrid = np.flip(lat)

    xgrid = lon.copy()

    print(f"Grid : {nlat} x {nlon}")
    print(f"Times: {len(time)}")

    return {

        "time": time,

        "lat": lat,

        "lon": lon,

        "xgrid": xgrid,

        "ygrid": ygrid,

        "nlat": nlat,

        "nlon": nlon,

        "dx": dx,

        "dy": dy,

        "swlat": swlat,

        "swlon": swlon,

        "msl": msl,

        "u10": u10,

        "v10": v10

    }# ======================================================================
# WRITE OWI FILES
# ======================================================================

def write_owi(data, out_prefix):
    """
    Python equivalent of MATLAB WriteOwi.m

    Produces:

        *_Basin.pre
        *_Basin.win

    using the exact same formatting.
    """

    pre_file = Path(str(out_prefix) + "_Basin.pre")
    win_file = Path(str(out_prefix) + "_Basin.win")

    # --------------------------------------------------------------
    # Construct first header line
    #
    # MATLAB:
    #
    # header=sprintf(
    # 'Oceanweather WIN/PRE Format                          %10s       %10s',
    # t1,t2)
    # --------------------------------------------------------------

    t1 = matlab_file_header_time(data["time"][0])
    t2 = matlab_file_header_time(data["time"][-1])

    first_header = (
        f"Oceanweather WIN/PRE Format"
        f"{'':26}"
        f"{t1:>10}"
        f"       "
        f"{t2:>10}"
    )

    fp = open(pre_file, "w")
    fw = open(win_file, "w")

    fp.write(first_header + "\n")
    fw.write(first_header + "\n")

    print(f"Writing {pre_file.name}")
    print(f"Writing {win_file.name}")

    # --------------------------------------------------------------
    # Loop through every timestep
    # --------------------------------------------------------------

    for k in range(len(data["time"])):

        dt = matlab_datestr30(data["time"][k])

        # ----------------------------------------------------------
        # MATLAB:
        #
        # sprintf(time_string,...)
        # ----------------------------------------------------------

        header = (
            f"iLat={data['nlat']:4d}"
            f"iLong={data['nlon']:4d}"
            f"DX={data['dx']:6.4f}"
            f"DY={data['dy']:6.4f}"
            f"SWLat={data['swlat']:8.4f}"
            f"SWLon={data['swlon']:8.4f}"
            f"DT={dt}"
        )

        # ==========================================================
        # PRESSURE
        # ==========================================================

        fp.write(header + "\n")

        pressure = data["msl"][:, :, k]

        # MATLAB:
        # fprintf(...,out')
        pressure = pressure.T.flatten(order="F")

        for i in range(0, len(pressure), 8):

            line = "".join(
                f" {v:9.4f}"
                for v in pressure[i:i+8]
            )

            fp.write(line + "\n")

        # nothing

        # ==========================================================
        # WIND U
        # ==========================================================

        fw.write(header + "\n")

        u = data["u10"][:, :, k]

        u = u.T.flatten(order="F")

        for i in range(0, len(u), 8):

            line = "".join(
                f" {v:9.4f}"
                for v in u[i:i+8]
            )

            fw.write(line + "\n")

        # nothing

        # ==========================================================
        # WIND V
        # ==========================================================

        v = data["v10"][:, :, k]

        v = v.T.flatten(order="F")

        for i in range(0, len(v), 8):

            line = "".join(
                f" {vv:9.4f}"
                for vv in v[i:i+8]
            )

            fw.write(line + "\n")

        # nothing

    fp.close()
    fw.close()

    print("Finished writing OWI files.")# ======================================================================
# MAIN PROGRAM
# ======================================================================

def main():

    print_banner()

    check_directories()

    total_years = END_YEAR - START_YEAR + 1

    print(f"Processing {total_years} year(s)...\n")

    for year in range(START_YEAR, END_YEAR + 1):

        print("=" * 70)
        print(f"YEAR : {year}")
        print("=" * 70)

        nc_file = build_filename(year)

        if not nc_file.exists():

            print(f"WARNING: {nc_file.name} not found.")
            print("Skipping.\n")

            continue

        try:

            # ------------------------------------------------------
            # Read ERA5 NetCDF
            # ------------------------------------------------------

            data = read_era5(nc_file)

            # ------------------------------------------------------
            # Output filename
            # ------------------------------------------------------

            out_prefix = output_prefix(year)

            # ------------------------------------------------------
            # Write ADCIRC OWI files
            # ------------------------------------------------------

            write_owi(data, out_prefix)

            print(f"{year} completed successfully.\n")

        except Exception:

            import traceback

            print(f"\nERROR processing {year}")

            traceback.print_exc()

            continue

    print("=" * 70)
    print("MET2MOD ERA5 -> OWI conversion completed.")
    print("=" * 70)


# ======================================================================

if __name__ == "__main__":
    main()