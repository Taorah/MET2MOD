# Convert ERA5 to Coastal-Model Forcing

This directory contains separate conversion frameworks for ADCIRC and Delft3D/Delft3D-FM.

## Input

```text
era5_YYYY.nc
```

Expected variables include `valid_time` or `time`, latitude, longitude, `u10`, `v10`, and `msl`.

## Frameworks

### ADCIRC

Produces:

```text
*.pre
*.win
```

### Delft3D / Delft3D-FM

Produces:

```text
*.amu
*.amv
*.ampr
```

Both model frameworks include MATLAB and Python implementations.
