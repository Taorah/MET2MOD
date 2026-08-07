# ADCIRC Python Workflow

File:

```text
convert_era5_to_owi.py
```

This script reproduces the MATLAB ERA5-to-OWI workflow.

## Install

```bash
python -m pip install numpy netCDF4
```

## Configure

```python
INPUT_DIR = Path(r"PATH_TO_YEARLY_NETCDF_FILES")
OUTPUT_DIR = Path(r"PATH_TO_OUTPUT_FOLDER")
START_YEAR = 2009
END_YEAR = 2018
```

The year range is inclusive.

## Run

```bash
python convert_era5_to_owi.py
```

## Input

```text
era5_YYYY.nc
```

The current code expects `valid_time`, `latitude`, `longitude`, `msl`, `u10`, and `v10`.

## Output

```text
era5_YYYY_formatOWI_Basin.pre
era5_YYYY_formatOWI_Basin.win
```

The script converts pressure from Pa to mb, reproduces the MATLAB grid orientation and fixed-width formatting, skips missing yearly files, and continues to the next year after a processing error.

## Memory note

The full yearly `msl`, `u10`, and `v10` arrays are loaded into memory. Process one year at a time and ensure sufficient RAM is available.
