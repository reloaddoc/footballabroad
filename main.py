import re
import json
import logging
from pathlib import Path
from time import sleep

import pandas as pd
import requests
from tqdm import tqdm

# =====================================================
# Einstellungen
# =====================================================

BASE_URL = "https://tmapi.transfermarkt.technology/transfer/history/player/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

INPUT_FILE = "players.csv"

OUTPUT = Path("output")
RAW = OUTPUT / "json"

OUTPUT.mkdir(exist_ok=True)
RAW.mkdir(exist_ok=True)

TRANSFER_CSV = OUTPUT / "transfers.csv"
CLUB_CSV = OUTPUT / "club_ids.csv"
COMP_CSV = OUTPUT / "competition_ids.csv"
COACH_CSV = OUTPUT / "coach_ids.csv"
ERROR_CSV = OUTPUT / "errors.csv"

AUTOSAVE_EVERY = 25

# =====================================================
# Logging
# =====================================================

logging.basicConfig(
    filename="collector.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# =====================================================
# Hilfsfunktionen
# =====================================================


def extract_player_id(value):

    value = str(value).strip()

    m = re.search(r"/spieler/(\d+)", value)

    if m:
        return m.group(1)

    if value.isdigit():
        return value

    return None


def download(player_id):

    url = BASE_URL + player_id

    last_exception = None

    for attempt in range(5):

        try:

            r = requests.get(
                url,
                headers=HEADERS,
                timeout=30
            )

            r.raise_for_status()

            return r.json()

        except Exception as e:

            last_exception = e

            logging.warning(
                f"{player_id} Versuch {attempt+1}/5 fehlgeschlagen."
            )

            sleep(2)

    raise last_exception


def autosave(
    transfers,
    clubs,
    competitions,
    coaches,
    errors
):

    pd.DataFrame(transfers).drop_duplicates().to_csv(
        TRANSFER_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame({
        "club_id": sorted(clubs, key=str)
    }).to_csv(
        CLUB_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame({
        "competition_id": sorted(competitions, key=str)
    }).to_csv(
        COMP_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame({
        "coach_id": sorted(coaches, key=str)
    }).to_csv(
        COACH_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    pd.DataFrame({
        "player_id": errors
    }).to_csv(
        ERROR_CSV,
        index=False,
        encoding="utf-8-sig"
    )


# =====================================================
# Spieler laden
# =====================================================

players = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig"
)

player_column = players.columns[0]

players["player_id"] = (
    players[player_column]
    .apply(extract_player_id)
)

players = players.dropna(
    subset=["player_id"]
)

players = players.drop_duplicates(
    subset=["player_id"]
)

print()
print(f"{len(players):,} eindeutige Spieler gefunden.")

# =====================================================
# Bereits vorhandene Transfers laden
# =====================================================

if TRANSFER_CSV.exists():

    existing = pd.read_csv(
        TRANSFER_CSV,
        encoding="utf-8-sig"
    )

    all_transfers = existing.to_dict("records")

    done_players = set(
        existing["player_id"]
        .astype(str)
    )

    print(
        f"{len(done_players):,} Spieler bereits vorhanden."
    )

else:

    all_transfers = []

    done_players = set()

# =====================================================
# Bereits vorhandene IDs laden
# =====================================================

if CLUB_CSV.exists():

    club_ids = set(
        pd.read_csv(
            CLUB_CSV,
            encoding="utf-8-sig"
        )["club_id"].dropna().astype(str)
    )

else:

    club_ids = set()

if COMP_CSV.exists():

    competition_ids = set(
        pd.read_csv(
            COMP_CSV,
            encoding="utf-8-sig"
        )["competition_id"].dropna().astype(str)
    )

else:

    competition_ids = set()

if COACH_CSV.exists():

    coach_ids = set(
        pd.read_csv(
            COACH_CSV,
            encoding="utf-8-sig"
        )["coach_id"].dropna().astype(str)
    )

else:

    coach_ids = set()

errors = []

processed = 0

# =====================================================
# Hauptschleife
# =====================================================

for _, row in tqdm(
    players.iterrows(),
    total=len(players),
    desc="Spieler"
):

    player_id = str(row["player_id"])

    # ---------------------------------------------
    # Resume
    # ---------------------------------------------

    if player_id in done_players:
        continue

    json_file = RAW / f"{player_id}.json"

    # ---------------------------------------------
    # JSON laden
    # ---------------------------------------------

    if json_file.exists():

        with open(
            json_file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

    else:

        try:

            data = download(player_id)

        except Exception:

            logging.exception(
                f"Downloadfehler Spieler {player_id}"
            )

            errors.append(player_id)

            continue

        with open(
            json_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

        sleep(0.8)

    # ---------------------------------------------
    # Transfers lesen
    # ---------------------------------------------

    try:

        transfers = data["data"]["history"]["terminated"]

    except Exception:

        logging.exception(
            f"Keine Transferhistorie für {player_id}"
        )

        errors.append(player_id)

        continue

    # ---------------------------------------------
    # Transfers verarbeiten
    # ---------------------------------------------

    for t in transfers:

        try:

            source = t.get("transferSource", {})
            dest = t.get("transferDestination", {})
            details = t.get("details", {})

            if source.get("clubId"):
                club_ids.add(str(source["clubId"]))

            if dest.get("clubId"):
                club_ids.add(str(dest["clubId"]))

            if source.get("competitionId"):
                competition_ids.add(str(source["competitionId"]))

            if dest.get("competitionId"):
                competition_ids.add(str(dest["competitionId"]))

            if source.get("coachId"):
                coach_ids.add(str(source["coachId"]))

            if dest.get("coachId"):
                coach_ids.add(str(dest["coachId"]))
                coach_ids.add(dest["coachId"])

            all_transfers.append({

                "player_id":
                    details.get("playerId"),

                "season":
                    details.get("season", {}).get("display"),

                "date":
                    details.get("date"),

                "age":
                    details.get("age"),

                "from_country":
                    source.get("countryId"),

                "from_club":
                    source.get("clubId"),

                "from_competition":
                    source.get("competitionId"),

                "from_coach":
                    source.get("coachId"),

                "to_country":
                    dest.get("countryId"),

                "to_club":
                    dest.get("clubId"),

                "to_competition":
                    dest.get("competitionId"),

                "to_coach":
                    dest.get("coachId"),

                "market_value":
                    details.get("marketValue", {}).get("value"),

                "fee":
                    details.get("fee", {}).get("value"),

                "contract_until":
                    details.get("contractUntilDate"),

                "transfer_type":
                    t.get("typeDetails", {}).get("type"),

                "relative_url":
                    t.get("relativeUrl")

            })

        except Exception:

            logging.exception(
                f"Transferfehler Spieler {player_id}"
            )

            continue

    processed += 1

    done_players.add(player_id)

    # ---------------------------------------------
    # Autosave
    # ---------------------------------------------

    if processed % AUTOSAVE_EVERY == 0:

        autosave(
            all_transfers,
            club_ids,
            competition_ids,
            coach_ids,
            errors
        )

        print(
            f"\nAutosave nach {processed} neuen Spielern."
        )

        # =====================================================
# Letztes Speichern
# =====================================================

autosave(
    all_transfers,
    club_ids,
    competition_ids,
    coach_ids,
    errors
)

# =====================================================
# Statistik
# =====================================================

transfer_df = (
    pd.DataFrame(all_transfers)
    .drop_duplicates()
)

print()
print("=" * 60)
print("TRANSFER COLLECTOR")
print("=" * 60)

print(f"Spieler in players.csv       : {len(players):,}")
print(f"Bereits vorhanden           : {len(done_players) - processed:,}")
print(f"Neu verarbeitet             : {processed:,}")
print(f"Transfers gesamt            : {len(transfer_df):,}")
print(f"Vereine gefunden            : {len(club_ids):,}")
print(f"Wettbewerbe gefunden        : {len(competition_ids):,}")
print(f"Trainer gefunden            : {len(coach_ids):,}")
print(f"Fehler                      : {len(errors):,}")

print()
print("Gespeichert:")

print(f"  {TRANSFER_CSV}")
print(f"  {CLUB_CSV}")
print(f"  {COMP_CSV}")
print(f"  {COACH_CSV}")
print(f"  {ERROR_CSV}")

print("=" * 60)
