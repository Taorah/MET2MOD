# Delft3D MATLAB Workflow

Files:

```text
Convert2Delft3DOWI_ALL_YEARS.m
WriteOwiDelft3D.m
```

The driver reads ERA5 meteorological variables and calls `WriteOwiDelft3D.m`.

## Configure

```matlab
years = 2020:2020;
```

Run MATLAB from the folder containing the NetCDF files, or modify `ncName` to include the input path.

## Run

```matlab
Convert2Delft3DOWI_ALL_YEARS
```

## Output

```text
era5_YYYY_Delft3D.amu
era5_YYYY_Delft3D.amv
era5_YYYY_Delft3D.ampr
```

The current writer generates all three files. The older driver comment stating that `.ampr` is not generated no longer matches the writer.

## Important implementation notes

Review these settings before production use:

1. `WriteOwiDelft3D.m` currently writes `grid_unit = m`, while the input coordinates are ERA5 longitude and latitude.
2. It currently writes `TIME = 0, 1, 2, ... hours since 2017-01-01 00:00:00 +00:00` and restarts the counter for every year.

Multi-year concatenation requires one common time reference and chronologically increasing TIME values. The Python Delft3D workflow already uses actual ERA5 timestamps relative to a fixed 1970 reference.
