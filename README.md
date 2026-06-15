# MET2MOD

## Meteorological Forcing Toolkit for Coastal Ocean Models

MET2MOD is an open-source workflow for downloading ERA5 atmospheric reanalysis data and converting it into meteorological forcing files for coastal ocean models.

**Current supported format:**

* ADCIRC OWI (`*.pre`, `*.win`)

Future planned support:

* Delft3D-FM
---

# Overview

MET2MOD automates the workflow:

```
ERA5 Download
      ↓
NetCDF Files (.nc)
      ↓
Convert ERA5 → OWI
      ↓
Yearly .pre and .win files
      ↓
Remove duplicate headers
      ↓
Concatenate yearly files
      ↓
Multi-decadal ADCIRC forcing
```

The workflow was developed for generating meteorological forcing for long-term ADCIRC simulations in the:

* Gulf of Mexico
* Caribbean Sea
* Western North Atlantic

---

# Repository Structure

```
MET2MOD
│
├── README.md
│
├── Data
├── Docs
├── Examples
│
└── Scripts
    │
    ├── 1_Download_ERA5
    │
    ├── 2_Convert_ERA5_to_OWI
    │   │
    │   ├── MATLAB
    │   │   ├── Convert2OWI_ALL_YEARS.m
    │   │   └── WriteOwi.m
    │
    └── 3_Postprocess_OWI
        ├── ProcessRemoveHeaderLinesPre.sh
        ├── ProcessRemoveHeaderLinesWin.sh
        └── ProcessConcatenateFiles.sh
```

---

# Software Requirements

| Software | Purpose                                        |
| -------- | ---------------------------------------------- |
| Python   | Download ERA5 data |
| MATLAB   | Convert ERA5 NetCDF files to ADCIRC OWI format |
|          | Optional Python Script for same purpose
| Git Bash | Run post-processing scripts on Windows         |
| ADCIRC   | Hydrodynamic simulations                       |

---

# Step 1 — Download ERA5 Forcing

**MET2MOD downloads:**

* Mean Sea Level Pressure (MSL)
* 10-m U Wind Component (U10)
* 10-m V Wind Component (V10)

from the Copernicus Climate Data Store (CDS).

**Create an account:**

_https://cds.climate.copernicus.eu_

Accept the ERA5 licence agreement.

Install CDS API:

```bash
pip install cdsapi
```

---

## Configure CDS API

After creating a CDS account, create a `.cdsapirc` file in your home directory.

Example:

```text
url: https://cds.climate.copernicus.eu/api
key: YOUR_UID:YOUR_API_KEY
```

This allows the Python download scripts to authenticate automatically.

---

## Why are downloads split by year?

Copernicus Climate Data Store (CDS) limits the maximum size of a single ERA5 request.

Attempting to download multiple decades of hourly atmospheric forcing in a single request may result in errors such as:

```text
cost limits exceeded
Your request is too large, please reduce your selection
```

**To avoid this limitation, MET2MOD downloads ERA5 data one year at a time.**

Each script:

```text
GrabFilesEra5_YYYY.py
```

**downloads:**

* Mean Sea Level Pressure (MSL)
* 10-m U Wind Component (U10)
* 10-m V Wind Component (V10)

**for a single year and writes:**

```text
era5_YYYY.nc
```

The yearly NetCDF files are later converted into ADCIRC forcing files.

---

## Download All Years automatically

Run:

```bash
python download_era5_all.py
```

Output:

```text
era5_1979.nc
era5_1980.nc
...
era5_2019.nc
era5_20200101.nc
```

---

## Verify Download

MATLAB:

```matlab
ncdisp('era5_1979.nc')
```

Expected variables:

```text
valid_time
latitude
longitude
u10
v10
msl
```

---

# Step 2 — Convert ERA5 NetCDF Files to ADCIRC OWI Format

MET2MOD supports both MATLAB and Python workflows.

Input:

```text
era5_YYYY.nc
```

Output:

```text
era5_YYYY_formatOWI_Basin.pre
era5_YYYY_formatOWI_Basin.win
```

---

## MATLAB Workflow

Run:

```matlab
Convert2OWI_ALL_YEARS
```

This script uses matlab function:

```matlab 
WriteOwi.m
```

**to generate yearly ADCIRC OWI forcing files.**

The MATLAB implementation is the original workflow used during development and validation of MET2MOD.

---

## Python Workflow

Python users can alternatively run:

```bash
python convert_era5_to_owi.py
```

The Python implementation follows the same logic as the MATLAB workflow:

---

# Step 3 — Remove Duplicate Headers

Each yearly OWI file contains an Oceanweather header.

Before concatenation, duplicate yearly headers must be removed.

Run:

```bash
bash ProcessRemoveHeaderLinesPre.sh

bash ProcessRemoveHeaderLinesWin.sh
```

Output:

```text
*_BasinRE.pre
*_BasinRE.win
```

These files are identical to the originals except that the first Oceanweather header line has been removed.

---

# Step 4 — Concatenate Files

Create continuous forcing records:

```bash
bash ProcessConcatenateFiles.sh
```

Output:

```text
era5_19790101_20200101_formatOWI_Basin.pre

era5_19790101_20200101_formatOWI_Basin.win
```

---

## Final OWI Header

The final forcing files begin with:

```text
Oceanweather WIN/PRE Format                          1979010100       2020010100
```

This header is required by ADCIRC and is automatically inserted during concatenation.

---

# ADCIRC Usage

Place:

```text
era5_19790101_20200101_formatOWI_Basin.pre

era5_19790101_20200101_formatOWI_Basin.win
```

into your ADCIRC simulation directory.

Configure meteorological forcing within:

```text
fort.15
```

according to your ADCIRC version and simulation setup.

---

# Example Application

The workflow has been used to generate:

* Hourly wind fields
* Hourly pressure fields
* 40+ year forcing records

for ADCIRC simulations covering:

* Gulf of Mexico
* Caribbean Sea
* Western North Atlantic

---

# Troubleshooting

## CDS License Error

```text
required licences not accepted
```

Solution:

Accept the ERA5 licence agreement at:

https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels

---

## CDS Request Too Large

```text
cost limits exceeded
```

Solution:

Use yearly downloads rather than requesting multiple decades in a single CDS request.

---

## NetCDF Variable Error

```text
Unable to find variable "time"
```

Solution:

Recent ERA5 downloads use:

```text
valid_time
```

instead of:

```text
time
```

Update conversion scripts accordingly.

---

## MATLAB Memory Error

```text
Java heap space
```

Solution:

Process data one year at a time or increase MATLAB Java heap allocation.

---

## Missing Python Packages

```text
ModuleNotFoundError: No module named 'numpy'
```

Solution:

Install required Python packages:

```bash
pip install numpy netCDF4 cdsapi
```

---

# Future Development

Planned additions include:

* Delft3D-FM forcing generation


---

# Acknowledgements

MET2MOD was developed using:

* Copernicus Climate Change Service (C3S)
* ERA5 Reanalysis Dataset
* ADCIRC Modeling System

Louisiana State University; Louisiana State University: Coastal Ecosystem Design Studio

Special thanks to the ADCIRC community and developers whose documentation and tools contributed to this workflow.

---
# Contributors

### Dr. Peter Bacopoulos
Louisiana State University: Coastal Ecosystem Design Studio (CEDS)
Louisiana State University: Department of Civil and Environmental Engineering

Original ERA5-to-OWI workflow and supporting scripts.

### Yusuf Taofiq
Department of Civil and Environmental Engineering
Louisiana State University

Repository development, workflow automation, documentation, testing, validation, and maintenance.

### Dr. Matthew Brand
Department of Civil and Environmental Engineering
Louisiana State University

Project oversight and scientific guidance

# Citation

If you use MET2MOD in your research, please cite:

Yusuf, T., Bacopoulos, P., and Brand, M. (2026). **MET2MOD: A workflow for downloading ERA5 meteorological forcing and generating ADCIRC Oceanweather (OWI) forcing files.**  GitHub repository: _https://github.com/Taorah/MET2MOD
_

Please also cite:

* Copernicus Climate Change Service (C3S) ERA5 Reanalysis Dataset
* ADCIRC Modeling System publications relevant to your application


# Contact

Repository Maintainer:

Yusuf Taofiq
Louisiana State University
Email: tyusuf1@lsu.edu
