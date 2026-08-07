# Delft3D Python Workflow

File:

```text
ConvertERA52Delft3D_ALL_YEARS.py
```

## Install

```bash
python -m pip install numpy netCDF4
```

## Configure

```python
START_YEAR = 2020
END_YEAR = 2021
INPUT_FOLDER = Path(r"PATH_TO_YEARLY_NETCDF_FILES")
OUTPUT_FOLDER = Path(r"PATH_TO_OUTPUT_FOLDER")
```

Optional controls include `OVERWRITE_EXISTING`, `SKIP_MISSING_FILES`, and `PROGRESS_INTERVAL`.

## Run

```bash
python ConvertERA52Delft3D_ALL_YEARS.py
```

## Output

```text
era5_YYYY_Delft3D.amu
era5_YYYY_Delft3D.amv
era5_YYYY_Delft3D.ampr
```

## What the script does

- Supports `valid_time` or `time`, `latitude` or `lat`, and `longitude` or `lon`.
- Requires `u10`, `v10`, and `msl`.
- Reads one time slice at a time to reduce memory use.
- Sorts timestamps and rejects duplicates or non-increasing values.
- Confirms regular coordinate spacing.
- Fills missing values with `-9999.0`.
- Converts pressure from Pa to mbar.
- Uses `grid_unit = degree` for ERA5 geographic coordinates.
- Uses the fixed reference `1970-01-01 00:00:00 +00:00` for all years.
- Writes temporary files and replaces final outputs only after a complete successful year.

The common time reference supports later multi-year concatenation.
