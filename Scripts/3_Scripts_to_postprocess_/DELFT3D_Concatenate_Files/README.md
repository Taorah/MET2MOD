# Concatenate Delft3D Forcing Files

File:

```text
Concatenate_Delft3D_ALL_YEARS.py
```

## Configure

```python
START_YEAR = 2020
END_YEAR = 2021
INPUT_FOLDER = Path(r"PATH_TO_YEARLY_DELFT3D_FILES")
OUTPUT_FOLDER = Path(r"PATH_TO_COMBINED_OUTPUTS")
```

Expected yearly names:

```text
era5_YYYY_Delft3D.amu
era5_YYYY_Delft3D.amv
era5_YYYY_Delft3D.ampr
```

## Run

```bash
python Concatenate_Delft3D_ALL_YEARS.py
```

## Output

```text
era5_2020_2021_Delft3D.amu
era5_2020_2021_Delft3D.amv
era5_2020_2021_Delft3D.ampr
```

## What the script checks

For each extension, it:

1. Confirms that every yearly input exists.
2. Retains the complete header from the first year.
3. Removes headers from later years.
4. Confirms grid-compatible headers.
5. Confirms one common TIME reference.
6. Confirms strictly increasing TIME records.
7. Rejects overlapping or non-chronological files.
8. Writes through a temporary file before replacing the final output.

The `.amu`, `.amv`, and `.ampr` files are processed independently.

All yearly inputs must use one common TIME reference and actual chronologically increasing elapsed-hour values. The Python Delft3D converter satisfies this requirement.
