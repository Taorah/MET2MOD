#!/usr/bin/env python3
"""
MET2MOD - ERA5 hourly downloader, monthly retrieval, yearly merge.

Workflow
--------
1. Download one month at a time to avoid CDS request-size limits.
2. Merge the 12 monthly NetCDF files along the time dimension.
3. Save one yearly file named era5_YEAR.nc.
4. Continue to the next year sequentially.

Required packages
-----------------
python -m pip install cdsapi xarray netCDF4 numpy

Notes
-----
- This does NOT concatenate NetCDF files as raw text.
- NetCDF metadata are preserved while data are concatenated along valid_time
  or time.
- Existing monthly files are skipped, so an interrupted run can resume.
"""

from __future__ import annotations

import calendar
import sys
import time
from pathlib import Path

import cdsapi
import numpy as np
import xarray as xr


# =============================================================================
# USER SETTINGS
# =============================================================================

START_YEAR = 1982
END_YEAR = 2025

# Save final yearly files here:
OUTPUT_FOLDER = Path(
    r"C:\Users\tyusuf1.LSU\OneDrive - Louisiana State University"
    r"\RESEARCH\ADCIRC_GULF_BC\ADCIRC_BC_LARGE_FILES\ERA5_YEARLY_DATA"
)

# Monthly files are stored temporarily inside OUTPUT_FOLDER.
MONTHLY_FOLDER_NAME = "_monthly_parts"

# ERA5 geographic subset: [North, West, South, East]
AREA = [50, -99, 5, -59]

VARIABLES = [
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "mean_sea_level_pressure",
]

TIMES = [f"{hour:02d}:00" for hour in range(24)]

OVERWRITE_YEARLY_FILE = False
DELETE_MONTHLY_FILES_AFTER_MERGE = True

MAX_RETRIES = 4
RETRY_WAIT_SECONDS = 60


# =============================================================================
# CDS SETTINGS
# =============================================================================

DATASET = "reanalysis-era5-single-levels"


# =============================================================================
# HELPERS
# =============================================================================

def monthly_path(monthly_folder: Path, year: int, month: int) -> Path:
    return monthly_folder / f"era5_{year}_{month:02d}.nc"


def yearly_path(output_folder: Path, year: int) -> Path:
    return output_folder / f"era5_{year}.nc"


def build_request(year: int, month: int) -> dict:
    number_of_days = calendar.monthrange(year, month)[1]

    return {
        "product_type": "reanalysis",
        "variable": VARIABLES,
        "year": str(year),
        "month": f"{month:02d}",
        "day": [f"{day:02d}" for day in range(1, number_of_days + 1)],
        "time": TIMES,
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": AREA,
    }


def download_month(
    client: cdsapi.Client,
    year: int,
    month: int,
    target: Path,
) -> None:
    if target.is_file() and target.stat().st_size > 0:
        print(f"SKIP: {target.name} already exists.")
        return

    partial = target.with_suffix(target.suffix + ".part")
    partial.unlink(missing_ok=True)

    request = build_request(year, month)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(
                f"Downloading {year}-{month:02d} "
                f"(attempt {attempt}/{MAX_RETRIES})..."
            )

            client.retrieve(DATASET, request, str(partial))

            if not partial.is_file() or partial.stat().st_size == 0:
                raise RuntimeError("CDS returned an empty or missing file.")

            partial.replace(target)
            print(f"SAVED: {target}")
            return

        except Exception as error:
            partial.unlink(missing_ok=True)

            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"Failed to download {year}-{month:02d} "
                    f"after {MAX_RETRIES} attempts."
                ) from error

            print(f"WARNING: {error}")
            print(f"Retrying in {RETRY_WAIT_SECONDS} seconds...")
            time.sleep(RETRY_WAIT_SECONDS)


def detect_time_name(dataset: xr.Dataset) -> str:
    for candidate in ("valid_time", "time"):
        if candidate in dataset.coords or candidate in dataset.variables:
            return candidate

    raise KeyError(
        "No supported time coordinate was found. "
        "Expected 'valid_time' or 'time'."
    )


def merge_months(month_files: list[Path], output_file: Path, year: int) -> None:
    if output_file.exists() and not OVERWRITE_YEARLY_FILE:
        print(f"SKIP MERGE: {output_file.name} already exists.")
        return

    missing = [path for path in month_files if not path.is_file()]
    if missing:
        missing_text = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(
            "Cannot create the yearly file because monthly files are missing:\n"
            + missing_text
        )

    print(f"Merging 12 monthly files into {output_file.name}...")

    datasets: list[xr.Dataset] = []
    temporary_output = output_file.with_suffix(output_file.suffix + ".tmp")
    temporary_output.unlink(missing_ok=True)

    try:
        for path in month_files:
            datasets.append(xr.open_dataset(path, engine="netcdf4"))

        time_name = detect_time_name(datasets[0])

        for dataset, path in zip(datasets, month_files):
            current_time_name = detect_time_name(dataset)
            if current_time_name != time_name:
                raise ValueError(
                    f"Inconsistent time coordinate in {path.name}: "
                    f"{current_time_name!r} versus {time_name!r}."
                )

        combined = xr.concat(
            datasets,
            dim=time_name,
            data_vars="minimal",
            coords="minimal",
            compat="override",
            join="exact",
            combine_attrs="override",
        )

        combined = combined.sortby(time_name)

        # Remove duplicate timestamps, if any.
        time_values = np.asarray(combined[time_name].values)
        _, unique_indices = np.unique(time_values, return_index=True)
        unique_indices = np.sort(unique_indices)

        if unique_indices.size != time_values.size:
            combined = combined.isel({time_name: unique_indices})

        # Verify the expected number of hourly records.
        expected_records = 8784 if calendar.isleap(year) else 8760
        actual_records = int(combined.sizes[time_name])

        if actual_records != expected_records:
            raise ValueError(
                f"Unexpected number of hourly records for {year}: "
                f"found {actual_records}, expected {expected_records}."
            )

        # Verify continuous hourly spacing.
        hours = (
            np.asarray(combined[time_name].values)
            .astype("datetime64[h]")
            .astype(np.int64)
        )
        differences = np.diff(hours)

        if not np.all(differences == 1):
            bad_locations = np.where(differences != 1)[0]
            first_bad = int(bad_locations[0])
            raise ValueError(
                f"The merged time coordinate is not continuously hourly. "
                f"First problem occurs between indices "
                f"{first_bad} and {first_bad + 1}."
            )

        combined.to_netcdf(
            temporary_output,
            engine="netcdf4",
            format="NETCDF4",
            unlimited_dims=[time_name],
        )

        if output_file.exists():
            output_file.unlink()

        temporary_output.replace(output_file)

        print(f"YEARLY FILE CREATED: {output_file}")
        print(f"Hourly records: {actual_records}")

    finally:
        for dataset in datasets:
            dataset.close()

        temporary_output.unlink(missing_ok=True)


def process_year(client: cdsapi.Client, year: int) -> None:
    print("\n" + "=" * 78)
    print(f"PROCESSING YEAR {year}")
    print("=" * 78)

    monthly_folder = OUTPUT_FOLDER / MONTHLY_FOLDER_NAME / str(year)
    monthly_folder.mkdir(parents=True, exist_ok=True)

    month_files = [
        monthly_path(monthly_folder, year, month)
        for month in range(1, 13)
    ]

    for month, target in enumerate(month_files, start=1):
        download_month(client, year, month, target)

    output_file = yearly_path(OUTPUT_FOLDER, year)
    merge_months(month_files, output_file, year)

    if DELETE_MONTHLY_FILES_AFTER_MERGE and output_file.is_file():
        for path in month_files:
            path.unlink(missing_ok=True)

        try:
            monthly_folder.rmdir()
        except OSError:
            pass

        print(f"Deleted monthly parts for {year}.")


def main() -> int:
    if START_YEAR > END_YEAR:
        raise ValueError("START_YEAR must be less than or equal to END_YEAR.")

    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("MET2MOD ERA5 HOURLY DOWNLOADER")
    print(f"Years  : {START_YEAR}-{END_YEAR}")
    print(f"Output : {OUTPUT_FOLDER}")
    print("=" * 78)

    client = cdsapi.Client()

    for year in range(START_YEAR, END_YEAR + 1):
        process_year(client, year)

    print("\n" + "=" * 78)
    print("ALL REQUESTED YEARS COMPLETED SUCCESSFULLY")
    print("=" * 78)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nDownload cancelled by user.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
