# ADCIRC Conversion Framework

This folder converts yearly ERA5 NetCDF data to ADCIRC Oceanweather forcing.

## Input

```text
era5_YYYY.nc
```

## Output

```text
era5_YYYY_formatOWI_Basin.pre
era5_YYYY_formatOWI_Basin.win
```

- `.pre` contains mean sea-level pressure converted from Pa to mb.
- `.win` contains 10-m U and V wind components in m/s.

Both implementations reorient the ERA5 grid, apply the pressure conversion `Pa × 0.01`, and write Basin-only forcing.

Choose either `matlab_workflow` or `python_workflow` and follow the README inside that folder.
