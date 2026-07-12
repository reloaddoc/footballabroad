import subprocess
import sys
import time
from pathlib import Path

# =====================================================
# Einstellungen
# =====================================================

PROJECT = Path(__file__).parent

PIPELINE = [

    ("Transfer Collector", "main.py"),

    ("Club Resolver", "club_resolver.py"),

    ("Club Profiles", "club_profile_scraper.py"),

    ("Player Profiles", "player_profile_scraper.py"),

    ("Career Paths", "career_paths.py"),

    ("Career Networks", "career_network.py"),

    ("Master Dataset", "master_dataset.py"),

]

# =====================================================
# Start
# =====================================================

print()
print("=" * 70)
print("FOOTBALLABROAD DATABASE UPDATE")
print("=" * 70)

start = time.time()

# =====================================================
# Pipeline
# =====================================================

for i, (title, script) in enumerate(PIPELINE, start=1):

    print()
    print("=" * 70)
    print(f"[{i}/{len(PIPELINE)}] {title}")
    print("=" * 70)

    script_start = time.time()

    result = subprocess.run(
        [sys.executable, str(PROJECT / script)]
    )

    runtime_script = time.time() - script_start

    minutes = int(runtime_script // 60)
    seconds = int(runtime_script % 60)

    if result.returncode != 0:

        print()
        print("=" * 70)
        print("UPDATE ABGEBROCHEN")
        print("=" * 70)
        print(f"Script      : {script}")
        print(f"Return Code : {result.returncode}")
        sys.exit(result.returncode)

    print()
    print(f"✓ {title} abgeschlossen ({minutes:02d}:{seconds:02d})")

# =====================================================
# Fertig
# =====================================================

runtime = time.time() - start

hours = int(runtime // 3600)
minutes = int((runtime % 3600) // 60)
seconds = int(runtime % 60)

print()
print("=" * 70)
print("DATABASE UPDATE ERFOLGREICH")
print("=" * 70)

print(f"Dauer: {hours:02d}:{minutes:02d}:{seconds:02d}")

print()
print("Alle Datensätze wurden aktualisiert.")

print("=" * 70)

# =====================================================
# Dashboard starten
# =====================================================

try:

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py"
        ],
        check=True
    )

except Exception as e:

    print()
    print("Dashboard konnte nicht gestartet werden.")
    print(e)
