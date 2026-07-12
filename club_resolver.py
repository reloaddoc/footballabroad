import time
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

# =====================================================
# Einstellungen
# =====================================================

INPUT = "output/club_ids.csv"
OUTPUT = "output/clubs.csv"

BASE_URL = "https://tmapi.transfermarkt.technology/club/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

AUTOSAVE_EVERY = 100

# =====================================================
# Dateien
# =====================================================

Path("output").mkdir(exist_ok=True)

# =====================================================
# Club-IDs laden
# =====================================================

club_ids = pd.read_csv(
    INPUT,
    encoding="utf-8-sig"
)

club_ids["club_id"] = (
    club_ids["club_id"]
    .astype(str)
)

club_ids = club_ids.drop_duplicates(
    subset=["club_id"]
)

print()
print(f"{len(club_ids):,} eindeutige Clubs gefunden.")

# =====================================================
# Resume
# =====================================================

if Path(OUTPUT).exists():
    existing = pd.read_csv(
        OUTPUT,
        encoding="utf-8-sig"
    )
    rows = existing.to_dict("records")
    done = set(
        existing["club_id"]
        .astype(str)
    )
    print(f"{len(done):,} Clubs bereits vorhanden.")
else:
    rows = []
    done = set()

# =====================================================
# Session
# =====================================================

session = requests.Session()
session.headers.update(HEADERS)

processed = 0
errors = 0

# =====================================================
# Downloadfunktion (KORRIGIERT)
# =====================================================


def download_club(club_id):
    url = BASE_URL + club_id
    last_exception = None

    for attempt in range(5):
        try:
            r = session.get(
                url,
                timeout=30
            )
            r.raise_for_status()
            data = r.json().get("data", {})

            # KORREKTUR: Diese Logik befindet sich jetzt SICHER innerhalb des try-Blocks
            link = data.get("relativeUrl")
            if link:
                slug = link.split("/")[1]
            else:
                slug = "unbekannt"
                link = f"/unbekannt/startseite/verein/{club_id}"

            return {
                "club_id": club_id,
                "name": data.get("name"),
                "slug": slug,
                "link": link,
                "is_nt": (
                    data.get("baseDetails", {})
                    .get("isNationalTeam")
                )
            }

        except Exception as e:
            last_exception = e
            time.sleep(2)

    raise last_exception


# =====================================================
# Autosave
# =====================================================

def autosave(rows):
    if not rows:
        return
    df = pd.DataFrame(rows)
    df = df.drop_duplicates(
        subset=["club_id"]
    )
    df = df.sort_values(
        by="name",
        na_position="last"
    )
    df.to_csv(
        OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )


# =====================================================
# Hauptschleife
# =====================================================

for club_id in tqdm(
    club_ids["club_id"],
    desc="Clubs"
):
    club_id = str(club_id)

    if club_id in done:
        continue

    try:
        row = download_club(club_id)
        rows.append(row)
    except Exception:
        errors += 1
        rows.append({
            "club_id": club_id,
            "name": None,
            "slug": None,
            "link": None,
            "is_nt": None
        })

    done.add(club_id)
    processed += 1

    # Autosave-Intervall prüfen
    if processed % AUTOSAVE_EVERY == 0:
        autosave(rows)
        tqdm.write(f"Autosave nach {processed:,} neuen Clubs.")

    time.sleep(0.15)


# =====================================================
# Finales Speichern
# =====================================================

autosave(rows)

# =====================================================
# Statistik
# =====================================================

df = pd.read_csv(
    OUTPUT,
    encoding="utf-8-sig"
)

print()
print("=" * 70)
print("CLUB RESOLVER")
print("=" * 70)

print(f"Club-IDs gefunden      : {len(club_ids):,}")
print(f"Neu verarbeitet        : {processed:,}")
print(f"Clubs gesamt           : {len(df):,}")
print(f"Fehler                 : {errors:,}")
print()
print("Vorschau:")
print(df[["club_id", "name", "slug"]].head(15))
print()
print("Gespeichert:")
print(OUTPUT)
print("=" * 70)
