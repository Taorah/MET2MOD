import os
import subprocess
from pathlib import Path

def run_download(year):
    script = Path(f"GrabFilesEra5_{year}.py")

    if not script.exists():
        print(f"⚠ Skipping {script.name} (not found)")
        return

    print(f"\n=== Running {script.name} ===")
    subprocess.run(["python", str(script)], check=True)

if __name__ == "__main__":

    for yr in range(1979, 2026):   # 1979–2025
        run_download(yr)

    print("\n✅ All ERA5 downloads completed.")
