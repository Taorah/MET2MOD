# Concatenate ADCIRC OWI Files

Scripts:

```text
ProcessRemoveHeaderLinesPre.sh
ProcessRemoveHeaderLinesWin.sh
ProcessConcatenateFiles.sh
```

## Input

```text
era5_YYYY_formatOWI_Basin.pre
era5_YYYY_formatOWI_Basin.win
```

Run the scripts from the directory containing the yearly files, or update their paths.

## 1. Remove pressure headers

Edit the year range in `ProcessRemoveHeaderLinesPre.sh`:

```bash
START_YEAR=1979
END_YEAR=1980
```

Run:

```bash
bash ProcessRemoveHeaderLinesPre.sh
```

Output:

```text
era5_1979_formatOWI_BasinRE.pre
era5_1980_formatOWI_BasinRE.pre
```

## 2. Remove wind headers

Set the same range in `ProcessRemoveHeaderLinesWin.sh` and run:

```bash
bash ProcessRemoveHeaderLinesWin.sh
```

Output:

```text
era5_1979_formatOWI_BasinRE.win
era5_1980_formatOWI_BasinRE.win
```

Every year included in the final concatenation must have both header-removed files.

## 3. Concatenate

```bash
bash ProcessConcatenateFiles.sh
```

The script writes one overall OWI header and appends the `RE` files in order.

## Important note

The uploaded `ProcessConcatenateFiles.sh` is hard-coded for a 1979–2026 file list, output name, and header. This can be edited as will

NOTE: The header must match the actual first and last meteorological records.

## Example output

```text
era5_1979_1980_formatOWI_Basin.pre
era5_1979_1980_formatOWI_Basin.win
```

## Validation

```bash
wc -l era5_1979_formatOWI_BasinRE.win
wc -l era5_1980_formatOWI_BasinRE.win
wc -l era5_1979_1980_formatOWI_Basin.win
```

The combined line count should equal the sum of the header-removed inputs plus one new overall header.
