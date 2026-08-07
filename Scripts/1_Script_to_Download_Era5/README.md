# Download Hourly ERA5 Data

This folder contains the ERA5 download utilities.

## Recommended script

```text
Download_ERA5_Hourly_Monthly_to_Yearly.py
```

It downloads one month at a time, requests all 24 hourly records per day, merges the 12 monthly NetCDF files into `era5_YYYY.nc`, checks for 8760 records in a normal year or 8784 in a leap year, verifies continuous hourly spacing, and resumes by skipping completed monthly files.

## Variables

- `10m_u_component_of_wind` → `u10`
- `10m_v_component_of_wind` → `v10`
- `mean_sea_level_pressure` → `msl`

## Main settings

```python
START_YEAR = 1979
END_YEAR = 2025
OUTPUT_FOLDER = Path(r"PATH_TO_OUTPUT_FOLDER")
AREA = [NORTH, WEST, SOUTH, EAST]
OVERWRITE_YEARLY_FILE = False
DELETE_MONTHLY_FILES_AFTER_MERGE = True
```

The year range is inclusive.

## Install

```bash
python -m pip install cdsapi xarray netCDF4 numpy
```

A valid CDS API configuration is required.

## Run

```bash
python Download_ERA5_Hourly_Monthly_to_Yearly.py
```

## Output

```text
era5_1979.nc
era5_1980.nc
...
era5_2025.nc
```

Temporary monthly files are written under `_monthly_parts/YYYY/` and are deleted after a successful merge when `DELETE_MONTHLY_FILES_AFTER_MERGE = True`.

## Other scripts

- `GrabFilesEra5_YYYY.py` contains individual full-year request examples. Large hourly requests may exceed CDS limits.
- `download_era5_all.py` runs available yearly scripts sequentially from 1979 through 2025 and stops if one returns an error.

For large hourly domains, use the monthly-to-yearly script.
