import os
import sys
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Setze das Root-Verzeichnis für alle Subprozesse in den PYTHONPATH
env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT)

SCRIPTS = [
    "etl/import_source_tables.py",
    "etl/build_master_dataset.py",
    "analytics/build_transfer_corridors.py",
    "analytics/build_league_flows.py",
    "analytics/build_stepping_clubs.py",
    "analytics/build_player_archetypes.py",
    "analytics/build_agency_networks.py",
]

for script in SCRIPTS:
    print("=" * 70)
    print(f"Running {script}")
    print("=" * 70)

    start = time.time()

    # Hier wird env=env übergeben, damit Python das Hauptverzeichnis findet
    result = subprocess.run(
        [sys.executable, str(ROOT / script)],
        check=True,
        env=env,
    )

    print(f"✓ finished in {time.time() - start:.1f}s\n")

print("=" * 70)
print("✓ ALL DATASETS REBUILT")
print("=" * 70)
