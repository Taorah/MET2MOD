#!/usr/bin/env python3
"""
MET2MOD: ERA5 to Delft3D meteorological forcing converter.

Creates one yearly set of Delft3D files from each ERA5 NetCDF file:

    era5_YYYY_Delft3D.amu   x/eastward wind
    era5_YYYY_Delft3D.amv   y/northward wind
    era5_YYYY_Delft3D.ampr  mean sea-level air pressure

Required packages:
    pip install numpy netCDF4

The script reads one time slice at a time, so it does not load an entire
multi-year ERA5 dataset into memory. All years use the same TIME reference,
which allows the yearly files to be concatenated later without resetting time.
"""

from __future__ import annotations

import sys
import time as walltime
from contextlib import ExitStack
from datetime import datetime, timedelta
from pathlib import Path
from typing import Sequence, TextIO

import numpy as np
from netCDF4 import Dataset, num2date


# =============================================================================
# USER SETTINGS
# =============================================================================

START_YEAR = 2020
END_YEAR = 2021

# Input files must follow INPUT_FILE_PATTERN, for example era5_2020.nc.
INPUT_FOLDER = Path(r"C:\Users\tyusuf1.LSU\OneDrive - Louisiana State University\RESEARCH\ADCIRC_GULF_BC\ADCIRC_BC_LARGE_FILES\ERA5_YEARLY_DATA")
OUTPUT_FOLDER = Path(r"D:\RESEARCH\GULF_PROJECT\MET2MOD")

INPUT_FILE_PATTERN = "era5_{year}.nc"
OUTPUT_PREFIX_PATTERN = "era5_{year}_Delft3D"

# A fixed reference is used for every year. This is important when yearly
# Delft3D files will later be concatenated.
TIME_REFERENCE = datetime(1970, 1, 1, 0, 0, 0)
TIME_ZONE_SUFFIX = "+00:00"

# ERA5 coordinates are longitude/latitude, so their grid unit is degrees.
# Change to "m" only when the NetCDF coordinates are projected coordinates.
GRID_UNIT = "degree"

# ERA5 mean sea-level pressure is normally stored in Pa. The MATLAB workflow
# converts it to mbar using 0.01, so this Python version does the same.
PRESSURE_SCALE = 0.01
PRESSURE_UNIT = "mbar"

NODATA_VALUE = -9999.0
OVERWRITE_EXISTING = True
PROGRESS_INTERVAL = 100

# If False, a missing requested year stops the run. If True, it is skipped.
SKIP_MISSING_FILES = False


# =============================================================================
# NETCDF NAME ALIASES
# =============================================================================

TIME_NAMES = ("valid_time", "time")
LATITUDE_NAMES = ("latitude", "lat")
LONGITUDE_NAMES = ("longitude", "lon")

REQUIRED_MET_VARIABLES = ("u10", "v10", "msl")


# =============================================================================
# GENERAL HELPERS
# =============================================================================


def find_variable_name(dataset: Dataset, candidates: Sequence[str]) -> str:
    """Return the first variable name present in the dataset."""
    for name in candidates:
        if name in dataset.variables:
            return name
    raise KeyError(
        "None of the expected variables were found: " + ", ".join(candidates)
    )


def ensure_required_variables(dataset: Dataset) -> None:
    """Confirm that all required ERA5 meteorological variables exist."""
    missing = [name for name in REQUIRED_MET_VARIABLES if name not in dataset.variables]
    if missing:
        raise KeyError("Missing required NetCDF variable(s): " + ", ".join(missing))


def as_python_datetime(value: object) -> datetime:
    """Convert a netCDF4/cftime datetime-like value to datetime."""
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)

    required = ("year", "month", "day", "hour", "minute", "second")
    if all(hasattr(value, attr) for attr in required):
        second_float = float(getattr(value, "second"))
        second = int(second_float)
        microsecond = int(round((second_float - second) * 1_000_000))
        microsecond += int(getattr(value, "microsecond", 0) or 0)

        if microsecond >= 1_000_000:
            second += microsecond // 1_000_000
            microsecond %= 1_000_000

        base = datetime(
            int(getattr(value, "year")),
            int(getattr(value, "month")),
            int(getattr(value, "day")),
            int(getattr(value, "hour")),
            int(getattr(value, "minute")),
            0,
            microsecond,
        )
        return base + timedelta(seconds=second)

    raise TypeError(f"Cannot convert time value to datetime: {value!r}")


def decode_time_variable(time_variable) -> list[datetime]:
    """Decode an ERA5 time coordinate using its NetCDF metadata."""
    raw = np.asarray(time_variable[:], dtype=np.float64).reshape(-1)
    if raw.size == 0:
        raise ValueError("The NetCDF time variable is empty.")

    units = getattr(time_variable, "units", None)
    calendar = getattr(time_variable, "calendar", "standard")

    if units:
        decoded = num2date(raw, units=units, calendar=calendar)
        return [as_python_datetime(value) for value in np.atleast_1d(decoded)]

    # Fallback for ERA5 files that omit the units attribute. Current CDS ERA5
    # valid_time is commonly Unix seconds. Older products may use hours since
    # 1900-01-01.
    magnitude = float(np.nanmedian(np.abs(raw)))
    if magnitude >= 10_000_000:
        origin = datetime(1970, 1, 1)
        return [origin + timedelta(seconds=float(value)) for value in raw]

    origin = datetime(1900, 1, 1)
    return [origin + timedelta(hours=float(value)) for value in raw]


def compact_number(value: float) -> str:
    """Format header numbers similarly to MATLAB num2str without extra zeros."""
    return f"{float(value):.12g}"


def format_elapsed_hours(timestamp: datetime, reference: datetime) -> str:
    """Return elapsed hours in compact Delft3D TIME-line form."""
    hours = (timestamp - reference).total_seconds() / 3600.0
    nearest_integer = round(hours)

    if abs(hours - nearest_integer) < 1.0e-9:
        return str(int(nearest_integer))

    return f"{hours:.10f}".rstrip("0").rstrip(".")


def validate_year_range() -> None:
    if START_YEAR > END_YEAR:
        raise ValueError("START_YEAR must be less than or equal to END_YEAR.")


def validate_regular_coordinate(values: np.ndarray, name: str) -> float:
    """Validate a one-dimensional regular coordinate and return spacing."""
    values = np.asarray(values, dtype=np.float64).reshape(-1)
    if values.size < 2:
        raise ValueError(f"{name} must contain at least two points.")
    if not np.all(np.isfinite(values)):
        raise ValueError(f"{name} contains non-finite values.")

    differences = np.diff(values)
    spacing = float(np.median(np.abs(differences)))
    tolerance = max(1.0e-10, spacing * 1.0e-6)

    if spacing <= 0.0 or not np.allclose(
        np.abs(differences), spacing, rtol=1.0e-6, atol=tolerance
    ):
        raise ValueError(f"{name} is not regularly spaced.")

    return spacing


# =============================================================================
# GRID AND FIELD HANDLING
# =============================================================================


def read_grid(dataset: Dataset, latitude_name: str, longitude_name: str):
    """Read coordinates and create ascending south-to-north/west-to-east order."""
    latitude_raw = np.asarray(dataset.variables[latitude_name][:], dtype=np.float64).reshape(-1)
    longitude_raw = np.asarray(dataset.variables[longitude_name][:], dtype=np.float64).reshape(-1)

    latitude_order = np.argsort(latitude_raw)
    longitude_order = np.argsort(longitude_raw)

    latitude = latitude_raw[latitude_order]
    longitude = longitude_raw[longitude_order]

    dy = validate_regular_coordinate(latitude, "latitude")
    dx = validate_regular_coordinate(longitude, "longitude")

    return {
        "latitude": latitude,
        "longitude": longitude,
        "latitude_order": latitude_order,
        "longitude_order": longitude_order,
        "n_rows": int(latitude.size),
        "n_cols": int(longitude.size),
        "dy": dy,
        "dx": dx,
        "y_llcenter": float(latitude[0]),
        "x_llcenter": float(longitude[0]),
    }


def read_time_slice(
    variable,
    time_index: int,
    time_dimension: str,
    latitude_dimension: str,
    longitude_dimension: str,
    latitude_order: np.ndarray,
    longitude_order: np.ndarray,
) -> np.ndarray:
    """
    Read one time slice and return a [latitude, longitude] array.

    Dimension names are used rather than assuming a fixed NetCDF dimension
    order. Any extra dimensions must be singleton dimensions.
    """
    dimensions = list(variable.dimensions)

    if time_dimension not in dimensions:
        raise ValueError(
            f"Variable {variable.name!r} does not use time dimension "
            f"{time_dimension!r}; dimensions are {dimensions}."
        )
    if latitude_dimension not in dimensions or longitude_dimension not in dimensions:
        raise ValueError(
            f"Variable {variable.name!r} must contain dimensions "
            f"{latitude_dimension!r} and {longitude_dimension!r}; "
            f"dimensions are {dimensions}."
        )

    indexer: list[object] = [slice(None)] * variable.ndim
    time_axis = dimensions.index(time_dimension)
    indexer[time_axis] = int(time_index)

    array = np.ma.asarray(variable[tuple(indexer)])
    remaining_dimensions = [
        dimension for axis, dimension in enumerate(dimensions) if axis != time_axis
    ]

    # Remove extra singleton dimensions, such as an expver dimension of size 1.
    for axis in range(len(remaining_dimensions) - 1, -1, -1):
        dimension = remaining_dimensions[axis]
        if dimension in (latitude_dimension, longitude_dimension):
            continue
        if array.shape[axis] != 1:
            raise ValueError(
                f"Variable {variable.name!r} has unsupported non-singleton "
                f"dimension {dimension!r} with size {array.shape[axis]}."
            )
        array = np.ma.squeeze(array, axis=axis)
        remaining_dimensions.pop(axis)

    if set(remaining_dimensions) != {latitude_dimension, longitude_dimension}:
        raise ValueError(
            f"Could not reduce variable {variable.name!r} to latitude/longitude; "
            f"remaining dimensions are {remaining_dimensions}."
        )

    latitude_axis = remaining_dimensions.index(latitude_dimension)
    longitude_axis = remaining_dimensions.index(longitude_dimension)
    array = np.ma.transpose(array, axes=(latitude_axis, longitude_axis))

    array = array[latitude_order, :]
    array = array[:, longitude_order]

    output = np.ma.filled(array, fill_value=NODATA_VALUE).astype(np.float64, copy=False)
    output[~np.isfinite(output)] = NODATA_VALUE
    return output


# =============================================================================
# DELFT3D WRITING
# =============================================================================


def write_header(
    file_handle: TextIO,
    quantity: str,
    unit: str,
    grid: dict,
) -> None:
    """Write a Delft3D meteo_on_equidistant_grid header."""
    lines = [
        "### START OF HEADER",
        "### This file is created by MET2MOD",
        "### ERA5 meteorological forcing converted by Python",
        "FileVersion = 1.03",
        "filetype = meteo_on_equidistant_grid",
        f"NODATA_value = {NODATA_VALUE:.1f}",
        f"n_cols = {grid['n_cols']}",
        f"n_rows = {grid['n_rows']}",
        f"grid_unit = {GRID_UNIT}",
        f"x_llcenter = {compact_number(grid['x_llcenter'])}",
        f"y_llcenter = {compact_number(grid['y_llcenter'])}",
        f"dx = {compact_number(grid['dx'])}",
        f"dy = {compact_number(grid['dy'])}",
        "n_quantity = 1",
        f"quantity1 = {quantity}",
        f"unit1 = {unit}",
        "### END OF HEADER",
    ]
    file_handle.write("\n".join(lines) + "\n")


def write_field(file_handle: TextIO, field: np.ndarray, timestamp: datetime) -> None:
    """Write one Delft3D TIME record and its two-dimensional field."""
    elapsed = format_elapsed_hours(timestamp, TIME_REFERENCE)
    reference_text = TIME_REFERENCE.strftime("%Y-%m-%d %H:%M:%S")
    file_handle.write(
        f"TIME = {elapsed} hours since {reference_text} {TIME_ZONE_SUFFIX}\n"
    )

    # This matches MATLAB fprintf(fid, '%12.4f', row) followed by a newline.
    np.savetxt(file_handle, field, fmt="%12.4f", delimiter="", newline="\n")


def output_paths(year: int) -> dict[str, Path]:
    prefix = OUTPUT_FOLDER / OUTPUT_PREFIX_PATTERN.format(year=year)
    return {
        "u10": Path(str(prefix) + ".amu"),
        "v10": Path(str(prefix) + ".amv"),
        "msl": Path(str(prefix) + ".ampr"),
    }


def temporary_path(final_path: Path) -> Path:
    return final_path.with_name(final_path.name + ".tmp")


def check_output_permissions(paths: dict[str, Path]) -> None:
    existing = [path for path in paths.values() if path.exists()]
    if existing and not OVERWRITE_EXISTING:
        names = "\n".join(str(path) for path in existing)
        raise FileExistsError(
            "Output file(s) already exist and OVERWRITE_EXISTING is False:\n" + names
        )


# =============================================================================
# YEAR PROCESSING
# =============================================================================


def process_year(year: int, input_path: Path) -> None:
    started = walltime.perf_counter()
    final_paths = output_paths(year)
    check_output_permissions(final_paths)

    temp_paths = {name: temporary_path(path) for name, path in final_paths.items()}
    for path in temp_paths.values():
        path.unlink(missing_ok=True)

    try:
        with Dataset(input_path, mode="r") as dataset:
            ensure_required_variables(dataset)

            time_name = find_variable_name(dataset, TIME_NAMES)
            latitude_name = find_variable_name(dataset, LATITUDE_NAMES)
            longitude_name = find_variable_name(dataset, LONGITUDE_NAMES)

            time_variable = dataset.variables[time_name]
            if len(time_variable.dimensions) != 1:
                raise ValueError(
                    f"Time variable {time_name!r} must be one-dimensional; "
                    f"dimensions are {time_variable.dimensions}."
                )

            time_dimension = time_variable.dimensions[0]
            latitude_dimension = dataset.variables[latitude_name].dimensions[0]
            longitude_dimension = dataset.variables[longitude_name].dimensions[0]

            timestamps = decode_time_variable(time_variable)
            time_order = np.argsort(np.asarray(timestamps, dtype="datetime64[us]"))
            sorted_timestamps = [timestamps[int(index)] for index in time_order]

            if any(
                sorted_timestamps[index] <= sorted_timestamps[index - 1]
                for index in range(1, len(sorted_timestamps))
            ):
                raise ValueError("Time coordinate contains duplicate or non-increasing values.")

            grid = read_grid(dataset, latitude_name, longitude_name)

            print(f"Input : {input_path}")
            print(f"Grid  : {grid['n_rows']} rows x {grid['n_cols']} columns")
            print(f"Times : {len(timestamps)}")
            print(f"Start : {sorted_timestamps[0]}")
            print(f"End   : {sorted_timestamps[-1]}")

            with ExitStack() as stack:
                handles = {
                    name: stack.enter_context(
                        open(path, mode="w", encoding="utf-8", newline="\n")
                    )
                    for name, path in temp_paths.items()
                }

                write_header(handles["u10"], "x_wind", "m s-1", grid)
                write_header(handles["v10"], "y_wind", "m s-1", grid)
                write_header(handles["msl"], "air_pressure", PRESSURE_UNIT, grid)

                u_variable = dataset.variables["u10"]
                v_variable = dataset.variables["v10"]
                p_variable = dataset.variables["msl"]

                total = len(time_order)
                for output_index, source_index_value in enumerate(time_order, start=1):
                    source_index = int(source_index_value)
                    timestamp = timestamps[source_index]

                    u_field = read_time_slice(
                        u_variable,
                        source_index,
                        time_dimension,
                        latitude_dimension,
                        longitude_dimension,
                        grid["latitude_order"],
                        grid["longitude_order"],
                    )
                    v_field = read_time_slice(
                        v_variable,
                        source_index,
                        time_dimension,
                        latitude_dimension,
                        longitude_dimension,
                        grid["latitude_order"],
                        grid["longitude_order"],
                    )
                    p_field = read_time_slice(
                        p_variable,
                        source_index,
                        time_dimension,
                        latitude_dimension,
                        longitude_dimension,
                        grid["latitude_order"],
                        grid["longitude_order"],
                    )

                    valid_pressure = p_field != NODATA_VALUE
                    p_field[valid_pressure] *= PRESSURE_SCALE

                    write_field(handles["u10"], u_field, timestamp)
                    write_field(handles["v10"], v_field, timestamp)
                    write_field(handles["msl"], p_field, timestamp)

                    if (
                        output_index == 1
                        or output_index == total
                        or output_index % PROGRESS_INTERVAL == 0
                    ):
                        print(f"  Wrote timestep {output_index:,} of {total:,}")

        # Replace final files only after the complete year was written successfully.
        for name, final_path in final_paths.items():
            if final_path.exists():
                final_path.unlink()
            temp_paths[name].replace(final_path)

        elapsed = walltime.perf_counter() - started
        print(f"Finished {year} in {elapsed / 60.0:.2f} minutes.")
        for path in final_paths.values():
            print(f"Output: {path}")

    except Exception:
        for path in temp_paths.values():
            path.unlink(missing_ok=True)
        raise


# =============================================================================
# MAIN PROGRAM
# =============================================================================


def main() -> int:
    validate_year_range()
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("MET2MOD: ERA5 -> Delft3D meteorological forcing")
    print(f"Years          : {START_YEAR}-{END_YEAR}")
    print(f"Time reference : {TIME_REFERENCE:%Y-%m-%d %H:%M:%S} {TIME_ZONE_SUFFIX}")
    print("=" * 78)

    processed = 0
    skipped = 0

    for year in range(START_YEAR, END_YEAR + 1):
        print("\n" + "=" * 78)
        print(f"Processing year {year}")
        print("=" * 78)

        input_path = INPUT_FOLDER / INPUT_FILE_PATTERN.format(year=year)
        if not input_path.is_file():
            message = f"Input file not found: {input_path}"
            if SKIP_MISSING_FILES:
                print("WARNING: " + message)
                skipped += 1
                continue
            raise FileNotFoundError(message)

        process_year(year, input_path)
        processed += 1

    print("\n" + "=" * 78)
    print(f"Completed successfully. Processed: {processed}; skipped: {skipped}.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nConversion cancelled by user.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
