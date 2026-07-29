#!/usr/bin/env python3
"""
MET2MOD: concatenate yearly Delft3D meteorological forcing files.

For the selected year range, this script creates three continuous files:

    era5_START_END_Delft3D.amu
    era5_START_END_Delft3D.amv
    era5_START_END_Delft3D.ampr

The complete header from the first year is retained. Headers from all later
files are removed before their TIME records and data grids are appended.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


# =============================================================================
# USER SETTINGS
# =============================================================================

START_YEAR = 2020
END_YEAR = 2021

# Folder containing the yearly Python Delft3D files.
INPUT_FOLDER = Path(r"D:\RESEARCH\GULF_PROJECT\MET2MOD")

# The three concatenated outputs will also be written here.
OUTPUT_FOLDER = Path(r"D:\RESEARCH\GULF_PROJECT\MET2MOD")

# Expected yearly names, for example: era5_2020_Delft3D.amu
INPUT_PREFIX_PATTERN = "era5_{year}_Delft3D"

# Combined name, for example: era5_2020_2021_Delft3D.amu
OUTPUT_PREFIX_PATTERN = "era5_{start_year}_{end_year}_Delft3D"

EXTENSIONS = ("amu", "amv", "ampr")
OVERWRITE_EXISTING = True

HEADER_END_MARKER = "### END OF HEADER"


# =============================================================================
# HELPERS
# =============================================================================


def validate_settings() -> None:
    if START_YEAR > END_YEAR:
        raise ValueError("START_YEAR must be less than or equal to END_YEAR.")


def input_path(year: int, extension: str) -> Path:
    prefix = INPUT_PREFIX_PATTERN.format(year=year)
    return INPUT_FOLDER / f"{prefix}.{extension}"


def output_path(extension: str) -> Path:
    prefix = OUTPUT_PREFIX_PATTERN.format(
        start_year=START_YEAR,
        end_year=END_YEAR,
    )
    return OUTPUT_FOLDER / f"{prefix}.{extension}"


def split_header_and_body(text: str, source: Path) -> tuple[str, str]:
    """Split a Delft3D file immediately after its header-end marker."""
    lines = text.splitlines(keepends=True)

    for index, line in enumerate(lines):
        if line.strip() == HEADER_END_MARKER:
            header = "".join(lines[: index + 1])
            body = "".join(lines[index + 1 :])

            if not header.endswith(("\n", "\r")):
                header += "\n"

            return header, body

    raise ValueError(f"Header-end marker not found in: {source}")


def normalized_header_signature(header: str) -> tuple[str, ...]:
    """
    Return the functional header lines used to confirm grid compatibility.

    Comment lines are ignored so harmless descriptive comments do not prevent
    concatenation. Key/value lines are normalized for spacing and case.
    """
    signature: list[str] = []

    for raw_line in header.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("###"):
            continue

        if "=" in line:
            key, value = line.split("=", 1)
            signature.append(f"{key.strip().lower()}={value.strip()}")
        else:
            signature.append(line.lower())

    return tuple(signature)


_TIME_RE = re.compile(
    r"^\s*TIME\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s+hours\s+since\s+(.+?)\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)


def extract_time_records(body: str, source: Path) -> list[tuple[float, str]]:
    """Extract Delft3D elapsed-hour TIME records from a file body."""
    records = [(float(match.group(1)), match.group(2).strip()) for match in _TIME_RE.finditer(body)]

    if not records:
        raise ValueError(f"No Delft3D TIME records found in: {source}")

    values = [record[0] for record in records]
    if any(current <= previous for previous, current in zip(values, values[1:])):
        raise ValueError(f"TIME records are not strictly increasing in: {source}")

    references = {record[1] for record in records}
    if len(references) != 1:
        raise ValueError(f"More than one TIME reference occurs in: {source}")

    return records


def ensure_final_newline(text: str) -> str:
    if not text:
        return text
    return text if text.endswith(("\n", "\r")) else text + "\n"


# =============================================================================
# CONCATENATION
# =============================================================================


def concatenate_extension(extension: str) -> Path:
    years = range(START_YEAR, END_YEAR + 1)
    sources = [input_path(year, extension) for year in years]

    missing = [path for path in sources if not path.is_file()]
    if missing:
        formatted = "\n".join(f"  {path}" for path in missing)
        raise FileNotFoundError(
            f"Missing .{extension} input file(s):\n{formatted}"
        )

    destination = output_path(extension)
    if destination.exists() and not OVERWRITE_EXISTING:
        raise FileExistsError(
            f"Output already exists and OVERWRITE_EXISTING is False: {destination}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.unlink(missing_ok=True)

    first_header: str | None = None
    first_signature: tuple[str, ...] | None = None
    common_time_reference: str | None = None
    previous_last_time: float | None = None
    total_records = 0

    try:
        with open(temporary, "w", encoding="utf-8", newline="\n") as output:
            for position, source in enumerate(sources):
                text = source.read_text(encoding="utf-8-sig")
                header, body = split_header_and_body(text, source)
                signature = normalized_header_signature(header)
                time_records = extract_time_records(body, source)

                current_reference = time_records[0][1]
                first_time = time_records[0][0]
                last_time = time_records[-1][0]

                if position == 0:
                    first_header = header
                    first_signature = signature
                    common_time_reference = current_reference
                    output.write(ensure_final_newline(header))
                else:
                    if signature != first_signature:
                        raise ValueError(
                            "Delft3D headers are not grid-compatible:\n"
                            f"  First file: {sources[0]}\n"
                            f"  Different:  {source}"
                        )

                    if current_reference != common_time_reference:
                        raise ValueError(
                            "TIME references are different:\n"
                            f"  First file: {sources[0]}\n"
                            f"  Different:  {source}"
                        )

                if previous_last_time is not None and first_time <= previous_last_time:
                    raise ValueError(
                        "TIME records overlap or are not chronological:\n"
                        f"  Previous last time: {previous_last_time}\n"
                        f"  Current first time: {first_time}\n"
                        f"  Current file: {source}"
                    )

                output.write(ensure_final_newline(body))
                previous_last_time = last_time
                total_records += len(time_records)

                print(
                    f"  Added {source.name}: {len(time_records):,} TIME records "
                    f"({first_time:g} to {last_time:g} hours)"
                )

        if destination.exists():
            destination.unlink()
        temporary.replace(destination)

    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    print(f"  Created {destination.name}: {total_records:,} TIME records")
    return destination


# =============================================================================
# MAIN PROGRAM
# =============================================================================


def main() -> int:
    validate_settings()

    print("=" * 78)
    print("MET2MOD: concatenate yearly Delft3D meteorological forcing")
    print(f"Years : {START_YEAR}-{END_YEAR}")
    print(f"Input : {INPUT_FOLDER}")
    print(f"Output: {OUTPUT_FOLDER}")
    print("=" * 78)

    outputs: list[Path] = []

    for extension in EXTENSIONS:
        print(f"\nConcatenating .{extension} files")
        outputs.append(concatenate_extension(extension))

    print("\n" + "=" * 78)
    print("Completed successfully. Combined files:")
    for path in outputs:
        print(f"  {path}")
    print("=" * 78)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nConcatenation cancelled by user.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
