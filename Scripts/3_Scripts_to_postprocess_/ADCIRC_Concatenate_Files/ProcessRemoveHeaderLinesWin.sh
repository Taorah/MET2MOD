#!/bin/bash

# Years to process
START_YEAR=1979
END_YEAR=1980

for YEAR in $(seq $START_YEAR $END_YEAR)
do
    sed '1d' "era5_${YEAR}_formatOWI_Basin.win" > "era5_${YEAR}_formatOWI_BasinRE.win"
done