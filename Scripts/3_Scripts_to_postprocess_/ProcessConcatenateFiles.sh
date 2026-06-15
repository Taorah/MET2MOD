#!/bin/bash

echo "========================================="
echo "Creating ADCIRC PRE and WIN forcing files"
echo "========================================="

HEADER="Oceanweather WIN/PRE Format                          1979010100       2020010100"

#############################################
# PRE FILE
#############################################

echo "$HEADER" > era5_19790101_20200101_formatOWI_Basin.pre

cat \
era5_1979_formatOWI_BasinRE.pre \
era5_1980_formatOWI_BasinRE.pre \
era5_1981_formatOWI_BasinRE.pre \
era5_1982_formatOWI_BasinRE.pre \
era5_1983_formatOWI_BasinRE.pre \
era5_1984_formatOWI_BasinRE.pre \
era5_1985_formatOWI_BasinRE.pre \
era5_1986_formatOWI_BasinRE.pre \
era5_1987_formatOWI_BasinRE.pre \
era5_1988_formatOWI_BasinRE.pre \
era5_1989_formatOWI_BasinRE.pre \
era5_1990_formatOWI_BasinRE.pre \
era5_1991_formatOWI_BasinRE.pre \
era5_1992_formatOWI_BasinRE.pre \
era5_1993_formatOWI_BasinRE.pre \
era5_1994_formatOWI_BasinRE.pre \
era5_1995_formatOWI_BasinRE.pre \
era5_1996_formatOWI_BasinRE.pre \
era5_1997_formatOWI_BasinRE.pre \
era5_1998_formatOWI_BasinRE.pre \
era5_1999_formatOWI_BasinRE.pre \
era5_2000_formatOWI_BasinRE.pre \
era5_2001_formatOWI_BasinRE.pre \
era5_2002_formatOWI_BasinRE.pre \
era5_2003_formatOWI_BasinRE.pre \
era5_2004_formatOWI_BasinRE.pre \
era5_2005_formatOWI_BasinRE.pre \
era5_2006_formatOWI_BasinRE.pre \
era5_2007_formatOWI_BasinRE.pre \
era5_2008_formatOWI_BasinRE.pre \
era5_2009_formatOWI_BasinRE.pre \
era5_2010_formatOWI_BasinRE.pre \
era5_2011_formatOWI_BasinRE.pre \
era5_2012_formatOWI_BasinRE.pre \
era5_2013_formatOWI_BasinRE.pre \
era5_2014_formatOWI_BasinRE.pre \
era5_2015_formatOWI_BasinRE.pre \
era5_2016_formatOWI_BasinRE.pre \
era5_2017_formatOWI_BasinRE.pre \
era5_2018_formatOWI_BasinRE.pre \
era5_2019_formatOWI_BasinRE.pre \
era5_20200101_formatOWI_BasinRE.pre \
>> era5_19790101_20200101_formatOWI_Basin.pre

#############################################
# WIN FILE
#############################################

echo "$HEADER" > era5_19790101_20200101_formatOWI_Basin.win

cat \
era5_1979_formatOWI_BasinRE.win \
era5_1980_formatOWI_BasinRE.win \
era5_1981_formatOWI_BasinRE.win \
era5_1982_formatOWI_BasinRE.win \
era5_1983_formatOWI_BasinRE.win \
era5_1984_formatOWI_BasinRE.win \
era5_1985_formatOWI_BasinRE.win \
era5_1986_formatOWI_BasinRE.win \
era5_1987_formatOWI_BasinRE.win \
era5_1988_formatOWI_BasinRE.win \
era5_1989_formatOWI_BasinRE.win \
era5_1990_formatOWI_BasinRE.win \
era5_1991_formatOWI_BasinRE.win \
era5_1992_formatOWI_BasinRE.win \
era5_1993_formatOWI_BasinRE.win \
era5_1994_formatOWI_BasinRE.win \
era5_1995_formatOWI_BasinRE.win \
era5_1996_formatOWI_BasinRE.win \
era5_1997_formatOWI_BasinRE.win \
era5_1998_formatOWI_BasinRE.win \
era5_1999_formatOWI_BasinRE.win \
era5_2000_formatOWI_BasinRE.win \
era5_2001_formatOWI_BasinRE.win \
era5_2002_formatOWI_BasinRE.win \
era5_2003_formatOWI_BasinRE.win \
era5_2004_formatOWI_BasinRE.win \
era5_2005_formatOWI_BasinRE.win \
era5_2006_formatOWI_BasinRE.win \
era5_2007_formatOWI_BasinRE.win \
era5_2008_formatOWI_BasinRE.win \
era5_2009_formatOWI_BasinRE.win \
era5_2010_formatOWI_BasinRE.win \
era5_2011_formatOWI_BasinRE.win \
era5_2012_formatOWI_BasinRE.win \
era5_2013_formatOWI_BasinRE.win \
era5_2014_formatOWI_BasinRE.win \
era5_2015_formatOWI_BasinRE.win \
era5_2016_formatOWI_BasinRE.win \
era5_2017_formatOWI_BasinRE.win \
era5_2018_formatOWI_BasinRE.win \
era5_2019_formatOWI_BasinRE.win \
era5_20200101_formatOWI_BasinRE.win \
>> era5_19790101_20200101_formatOWI_Basin.win

echo "========================================="
echo "Finished"
echo "Created:"
echo "  era5_19790101_20200101_formatOWI_Basin.pre"
echo "  era5_19790101_20200101_formatOWI_Basin.win"
echo "========================================="