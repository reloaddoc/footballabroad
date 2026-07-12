import pandas as pd

# ==========================================================
# Daten laden
# ==========================================================

transfers = pd.read_csv(
    "output/transfers.csv",
    encoding="utf-8-sig"
)

clubs = pd.read_csv(
    "output/clubs.csv",
    encoding="utf-8-sig"
)

# ==========================================================
# Datentypen
# ==========================================================

transfers["from_club"] = transfers["from_club"].astype(str)
transfers["to_club"] = transfers["to_club"].astype(str)

clubs["club_id"] = clubs["club_id"].astype(str)

# ==========================================================
# Vereinslos ergänzen
# ==========================================================

if "515" not in clubs["club_id"].values:

    clubs.loc[len(clubs)] = {
        "club_id": "515",
        "name": "Vereinslos",
        "slug": "vereinslos",
        "link": "",
        "is_nt": False
    }

# ==========================================================
# Duplikate entfernen
# ==========================================================

print("=" * 60)
print("DATENBEREINIGUNG")
print("=" * 60)

print("Transfers vorher:", len(transfers))

transfers = transfers.drop_duplicates()

print("Transfers nachher:", len(transfers))
print()

# ==========================================================
# Vereinsnamen ergänzen
# ==========================================================

lookup = clubs[["club_id", "name"]]

from_lookup = lookup.rename(
    columns={
        "club_id": "from_club",
        "name": "from_name"
    }
)

to_lookup = lookup.rename(
    columns={
        "club_id": "to_club",
        "name": "to_name"
    }
)

transfers = transfers.merge(
    from_lookup,
    on="from_club",
    how="left"
)

transfers = transfers.merge(
    to_lookup,
    on="to_club",
    how="left"
)

transfers["from_name"] = transfers["from_name"].fillna("Unbekannt")
transfers["to_name"] = transfers["to_name"].fillna("Unbekannt")

# ==========================================================
# Datum
# ==========================================================

transfers["date"] = pd.to_datetime(
    transfers["date"],
    utc=True
)

transfers = transfers.sort_values(
    ["player_id", "date"]
)

# ==========================================================
# Karrierepfade erzeugen
# ==========================================================

career_steps = []
career_paths = []

for player_id, group in transfers.groupby("player_id"):

    group = group.sort_values("date")

    clubs_path = []

    international_moves = 0

    step = 1

    for _, row in group.iterrows():

        if row["from_country"] != row["to_country"]:
            international_moves += 1

        career_steps.append({

            "player_id": player_id,

            "step": step,

            "date": row["date"],

            "age": row["age"],

            "market_value": row["market_value"],

            "from_country": row["from_country"],
            "to_country": row["to_country"],

            "from_competition": row["from_competition"],
            "to_competition": row["to_competition"],

            "from_club_id": row["from_club"],
            "to_club_id": row["to_club"],

            "from_club": row["from_name"],
            "to_club": row["to_name"]

        })

        if len(clubs_path) == 0:
            clubs_path.append(row["from_name"])

        clubs_path.append(row["to_name"])

        step += 1

    # doppelte Vereine direkt hintereinander entfernen

    cleaned = []

    for club in clubs_path:

        if len(cleaned) == 0 or cleaned[-1] != club:
            cleaned.append(club)

    career_paths.append({

        "player_id": player_id,

        "career_length": len(cleaned),

        "international_moves": international_moves,

        "first_club": cleaned[0],

        "last_club": cleaned[-1],

        "career_path": " → ".join(cleaned)

    })

# ==========================================================
# DataFrames
# ==========================================================

career_steps = pd.DataFrame(career_steps)

career_paths = pd.DataFrame(career_paths)

# ==========================================================
# Speichern
# ==========================================================

career_steps.to_csv(
    "output/career_steps.csv",
    index=False,
    encoding="utf-8-sig"
)

career_paths.to_csv(
    "output/career_paths.csv",
    index=False,
    encoding="utf-8-sig"
)

# ==========================================================
# Ausgabe
# ==========================================================

print("=" * 60)
print("KARRIEREPFAD-DATENBANK")
print("=" * 60)

print(f"Spieler:                 {career_paths['player_id'].nunique():,}")
print(f"Karrierepfade:           {len(career_paths):,}")
print(f"Karriereschritte:        {len(career_steps):,}")

print()

print(
    "Ø Karrierelänge:",
    round(career_paths["career_length"].mean(), 2),
    "Stationen"
)

print(
    "Ø internationale Wechsel:",
    round(career_paths["international_moves"].mean(), 2)
)

print()

print("Beispiel:")

print(
    career_paths[
        [
            "player_id",
            "career_length",
            "international_moves",
            "first_club",
            "last_club"
        ]
    ].head(10)
)

print()

print("Dateien gespeichert:")

print("output/career_steps.csv")
print("output/career_paths.csv")
