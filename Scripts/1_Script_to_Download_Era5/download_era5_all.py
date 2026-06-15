import os
import subprocess

def run_download(year):
    script = f"GrabFilesEra5_{year}.py"
    print(f"=== Running {script} ===")
    subprocess.run(["python", script], check=True)

if __name__ == "__main__":
    for yr in range(1979, 2020):
        run_download(yr)

    # Handle the special 20200101 script
    subprocess.run(["python", "GrabFilesEra5_20200101.py"], check=True)

    print("✅ All downloads finished")
