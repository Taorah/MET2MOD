# MET2MOD

## Meteorological Forcing Toolkit for Coastal Ocean Models

MET2MOD is an open-source workflow for downloading ERA5 atmospheric reanalysis data and converting it into meteorological forcing files for coastal ocean models.

**Current supported format:**

* ADCIRC Oceanweather (OWI) (`*.pre`, `*.win`)

* Delft3D / Delft3D-FM meteorological forcing (`*.amu`, `*.amv`, `*.ampr`)

---

# Overview

MET2MOD automates the workflow:

```
ERA5 Download
      ↓
NetCDF Files (.nc)
      ↓
Select Coastal Model
(ADCIRC/DELFT3D)
      ↓
Convert ERA5 → OWI
      ↓
Yearly .pre and .win files
      ↓
Remove duplicate headers
      ↓
Concatenate yearly files
      ↓
Multi-decadal coastal model forcing
```

The example workflow included in this repository demonstrates the generation of long-term Oceanweather (OWI) meteorological forcing for coastal models, using ERA5 atmospheric reanalysis data for any location of interest across the world
Case Study Example/Application: Gulf of Mexico, Caribbean Sea, and Western North Atlantic.

---

# Workflow Flexibility

The Example Application provides a complete, reproducible workflow using ERA5 data and coastal model Oceanweather (OWI) forcing. While this example serves as the reference implementation, MET2MOD has been designed so that users can adapt key components of the workflow to suit different applications.

The table below summarizes the primary user-configurable parameters available throughout the workflow.

| Workflow Step | User-configurable Parameters |
| :------------ | :--------------------------- |
| **ERA5 Download** | Start year, end year, geographic domain, output directory |
| **ERA5 → OWI Conversion** | Input directory, output directory, years to process, MATLAB or Python implementation |
| **Remove Duplicate Headers** | Start year, end year |
| **Concatenate Files** | Start year, end year, output filename |

Throughout this README, user-configurable parameters are highlighted within each workflow step.

---

# Repository Structure

```text
MET2MOD
│
├── README.md
│
└── Scripts
    │
    ├── 1_Script_to_Download_Era5
    │   │
    │   ├── Download_ERA5_Hourly_Monthly_to_Yearly.py
    │   ├── GrabFilesEra5_1979.py
    │   ├── GrabFilesEra5_1980.py
    │   ├── ...
    │   └── GrabFilesEra5_2025.py
    │
    ├── 2_Script_to_Convert_to_OWI
    │   │
    │   ├── ADCIRC
    │   │   │
    │   │   ├── matlab_workflow
    │   │   │   ├── Convert2OWI_ALL_YEARS.m
    │   │   │   ├── WriteOwi.m
    │   │   │   └── Readme.txt
    │   │   │
    │   │   └── python_workflow
    │   │       └── convert_era5_to_owi.py
    │   │
    │   └── DELFT3D
    │       │
    │       ├── Matlab_Workflow
    │       │   ├── Convert2Delft3DOWI_ALL_YEARS.m
    │       │   └── WriteOwiDelft3D.m
    │       │
    │       └── Python_Workflow
    │           └── ConvertERA52Delft3D_ALL_YEARS.py
    │
    └── 3_Scripts_to_postprocess_
        │
        ├── ADCIRC_Concatenate_Files
        │   ├── ProcessRemoveHeaderLinesPre.sh
        │   ├── ProcessRemoveHeaderLinesWin.sh
        │   ├── ProcessConcatenateFiles.sh
        │   └── Readme.txt
        │
        └── DELFT3D_Concatenate_Files
            └── Concatenate_Delft3D_ALL_YEARS.py
```
```
---

# Software Requirements

| Software | Purpose                                        |
| -------- | ---------------------------------------------- |
| Python   | Download ERA5 data |
| MATLAB   | Convert ERA5 NetCDF files to ADCIRC OWI format |
|          | Optional **Python** Script for same purpose
| Git Bash | Run post-processing scripts on Windows         |
| ADCIRC   | Optinal Python script for DELFT3D Forcings     |

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
## Download ERA5 Data

### User-configurable parameters

The download workflow allows users to specify:

* Start year
* End year
* Geographic domain
* Output directory

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
era5_2025.nc
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

# Step 2 — Convert ERA5 NetCDF Files to Model Forcing Formats

MET2MOD provides separate ADCIRC and Delft3D-FM conversion frameworks. Both frameworks include MATLAB and Python implementations.

### User-configurable parameters

Users may specify:

* Input directory
* Output directory
* Years to process
* MATLAB or Python implementation
 
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

---

## Python Workflow

Python users can alternatively run:

```bash
python convert_era5_to_owi.py
```

The Python implementation follows the same logic as the MATLAB workflow:

Reads ERA5 NetCDF files.
Converts pressure from Pa to mb.
Reorients ERA5 grids to OWI conventions.
Generates yearly ADCIRC OWI pressure and wind files.

The Python implementation is intended for users who do not have access to MATLAB and aims to produce output equivalent to the MATLAB workflow.
---

# Step 3 — Remove Duplicate Headers

Each yearly OWI file contains an Oceanweather header.

Before yearly files can be concatenated into a continuous forcing record, duplicate file headers must be removed.

### User-configurable parameters

Users may specify:

* Start year
* End year

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
### User-configurable parameters

Users may specify:

* Start year
* End year

```bash
bash ProcessConcatenateFiles.sh
```

Output:

```text
era5_StartYear/date_EndYear/date_formatOWI_Basin.pre

era5_StartYear/date_EndYear/date_formatOWI_Basin.win
```

---

## Final OWI Header

The final forcing files begin with:

```text
Oceanweather WIN/PRE Format                          1979010100       2025010100
```

This header is required by ADCIRC and is automatically inserted during concatenation.

---

# ADCIRC Usage

Place:

```text
era5_StartYear/date_EndYear/date_formatOWI_Basin.pre

era5_StartYear/date_EndYear/date_formatOWI_Basin.win
```

into your ADCIRC simulation directory.

Configure meteorological forcing within:

```text
fort.15
```

according to your ADCIRC version and simulation setup.


---

# Delft3D usage 

```markdown
---

# Delft3D / Delft3D-FM Usage

Use the generated files:

```text
*.amu
*.amv
*.ampr
---

# Example Application

The example application included in this repository demonstrates the generation of hourly Oceanweather (OWI) meteorological forcing for coastal/ocean models from ERA5 atmospheric reanalysis data.

Example configuration:

* Atmospheric dataset: ERA5
* Temporal resolution: Hourly
* Supported output formats:
  * ADCIRC Oceanweather (`.pre`, `.win`)
  * Delft3D-FM (`.amu`, `.amv`, `.ampr`)
* Region: Gulf of Mexico, Caribbean Sea, and Western North Atlantic

The example is intended as a reference implementation for reproducing the complete workflow. Users may adapt the workflow to different study regions, simulation periods, or project-specific requirements by modifying the user-configurable parameters identified throughout this README.

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

# Acknowledgements

MET2MOD was developed using:

* Copernicus Climate Change Service (C3S)
* ERA5 Reanalysis Dataset
* ADCIRC Modeling System
* Delft3D Modeling System

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

Yusuf, T., Bacopoulos, P., and Brand, M. (2026). **MET2MOD: A workflow for downloading ERA5 meteorological forcing and generating Oceanweather (OWI) forcing files for coastal models.**  GitHub repository: _https://github.com/Taorah/MET2MOD
_

Please also cite:

* Copernicus Climate Change Service (C3S) ERA5 Reanalysis Dataset
* ADCIRC Modeling System publications relevant to your application
* Delft3D or Delft3D-FM publications relevant to their application


# Contact

Repository Maintainer:

Yusuf Taofiq
Louisiana State University
Email: tyusuf1@lsu.edu
