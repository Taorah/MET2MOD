# Delft3D / Delft3D-FM Conversion Framework

This folder converts yearly ERA5 NetCDF data into Delft3D meteorological forcing.

## Input

```text
era5_YYYY.nc
```

## Output

```text
era5_YYYY_Delft3D.amu
era5_YYYY_Delft3D.amv
era5_YYYY_Delft3D.ampr
```

| File | Quantity | ERA5 variable |
|---|---|---|
| `.amu` | x/eastward wind | `u10` |
| `.amv` | y/northward wind | `v10` |
| `.ampr` | atmospheric pressure | `msl` |

Pressure is converted from Pa to mbar.

Choose either `Matlab_Workflow` or `Python_Workflow` and follow the README inside that folder.
