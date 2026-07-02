#!/bin/bash

echo "========================================="
echo "Creating ADCIRC PRE and WIN forcing files"
echo "========================================="

#############################################
# USER SETTINGS
#############################################

START_YEAR=1979
END_YEAR=2025

#############################################
# Header
#############################################

HEADER_START="${START_YEAR}010100"
HEADER_END="${END_YEAR}123123"

HEADER="Oceanweather WIN/PRE Format                          ${HEADER_START}       ${HEADER_END}"

#############################################
# Output filenames
#############################################

PRE_OUT="era5_${START_YEAR}0101_${END_YEAR}1231_formatOWI_Basin.pre"
WIN_OUT="era5_${START_YEAR}0101_${END_YEAR}1231_formatOWI_Basin.win"

#############################################
# PRE FILE
#############################################

echo "$HEADER" > "$PRE_OUT"

for YEAR in $(seq $START_YEAR $END_YEAR)
do
    echo "Adding PRE file for ${YEAR}..."
    cat "era5_${YEAR}_formatOWI_BasinRE.pre" >> "$PRE_OUT"
done

#############################################
# WIN FILE
#############################################

echo "$HEADER" > "$WIN_OUT"

for YEAR in $(seq $START_YEAR $END_YEAR)
do
    echo "Adding WIN file for ${YEAR}..."
    cat "era5_${YEAR}_formatOWI_BasinRE.win" >> "$WIN_OUT"
done

#############################################
# Finished
#############################################

echo
echo "========================================="
echo "Finished"
echo
echo "Created:"
echo "  $PRE_OUT"
echo "  $WIN_OUT"
echo
echo "Header:"
echo "  $HEADER"
echo "========================================="
