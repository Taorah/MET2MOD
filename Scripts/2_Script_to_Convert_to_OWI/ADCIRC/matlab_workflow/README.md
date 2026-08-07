# ADCIRC MATLAB Workflow

Files:

```text
Convert2OWI_ALL_YEARS.m
WriteOwi.m
```

`Convert2OWI_ALL_YEARS.m` reads yearly ERA5 files, prepares the OWI structure, and calls `WriteOwi.m`.

## Input

```text
era5_YYYY.nc
```

Expected variables:

```text
valid_time
latitude
longitude
msl
u10
v10
```

The script interprets `valid_time` as seconds since `1970-01-01 00:00:00 UTC`.

## Configure

Edit:

```matlab
years = 1999:2019;
```

Run MATLAB from the folder containing the NetCDF files, or modify `ncName` to include the input path.

## Run

```matlab
Convert2OWI_ALL_YEARS
```

Keep `WriteOwi.m` in the same folder or on the MATLAB path.

## Output

```text
era5_YYYY_formatOWI_Basin.pre
era5_YYYY_formatOWI_Basin.win
```

The workflow converts pressure from Pa to mb, permutes the arrays, applies the latitude flip used by the existing OWI workflow, and clears large variables after each year.

`WriteOwi.m` writes one Oceanweather file header, one grid/time header per timestep, pressure values to `.pre`, and U-wind followed by V-wind values to `.win`.
