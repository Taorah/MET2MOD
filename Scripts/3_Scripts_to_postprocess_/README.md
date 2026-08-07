# Postprocessing and Multi-Year Concatenation

This directory contains optional tools for combining yearly model-forcing files into continuous multi-year records.

```text
ADCIRC_Concatenate_Files
DELFT3D_Concatenate_Files
```

## ADCIRC

The ADCIRC workflow removes the first Oceanweather header from each yearly `.pre` and `.win` file, writes one new overall header, and concatenates the yearly data in chronological order.

## Delft3D / Delft3D-FM

The Delft3D workflow uses one Python script to process `.amu`, `.amv`, and `.ampr` independently. It retains the first year's complete header and appends only the TIME records and grids from later years.

Concatenation is optional. Annual forcing files can remain the master archive and be combined only for runs that cross year boundaries.
