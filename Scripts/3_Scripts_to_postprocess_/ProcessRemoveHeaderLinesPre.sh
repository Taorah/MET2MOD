#!/bin/bash

# Years to process
START_YEAR=2020
END_YEAR=2025

for YEAR in $(seq $START_YEAR $END_YEAR)
do
    sed '1d' "era5_${YEAR}_formatOWI_Basin.pre" > "era5_${YEAR}_formatOWI_BasinRE.pre"
done