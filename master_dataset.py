import pandas as pd
from pathlib import Path

OUTPUT = Path("output")

# --------------------------------------------------------
# Daten laden
# --------------------------------------------------------

print("Lade Daten...")

transfers = pd.read_csv(OUTPUT / "transfers.csv", encoding="utf-8-sig")
clubs = pd.read_csv(OUTPUT / "clubs.csv", encoding="utf-8-sig")
profiles = pd.read_csv(OUTPUT / "player_profiles.csv", encoding="utf-8-sig")
career = pd.read_csv(OUTPUT / "career_paths.csv", encoding="utf-8-sig")
club_profiles = pd.read_csv(OUTPUT / "club_profiles.csv", encoding="utf-8-sig")

# --------------------------------------------------------
# Datentypen
# --------------------------------------------------------

for df, col in [
    (transfers, "player_id"),
    (profiles, "player_id"),
    (career, "player_id"),
    (clubs, "club_id"),
    (club_profiles, "club_id"),
]:
    df[col] = df[col].astype(str)

transfers["from_club"] = transfers["from_club"].astype(str)
transfers["to_club"] = transfers["to_club"].astype(str)

# --------------------------------------------------------
# Duplicate Checks
# --------------------------------------------------------

print("\nPrüfe eindeutige Schlüssel...")

assert clubs["club_id"].duplicated().sum(
) == 0, "Duplicate club_id in clubs.csv"
assert club_profiles["club_id"].duplicated().sum(
) == 0, "Duplicate club_id in club_profiles.csv"
assert profiles["player_id"].duplicated().sum(
) == 0, "Duplicate player_id in player_profiles.csv"
assert career["player_id"].duplicated().sum(
) == 0, "Duplicate player_id in career_paths.csv"

print("OK")

original_rows = len(transfers)
print(f"Transfers geladen: {original_rows:,}")

# --------------------------------------------------------
# Merge Helper
# --------------------------------------------------------


def merge_lookup(df, lookup, side):
    tmp = lookup.rename(columns={
        "club_id": f"{side}_club",
        "name": f"{side}_club_name",
        "slug": f"{side}_club_slug"
    })

    return df.merge(
        tmp[[f"{side}_club", f"{side}_club_name", f"{side}_club_slug"]],
        on=f"{side}_club",
        how="left"
    )


def merge_profiles(df, profile, side):
    tmp = profile.rename(columns={
        "club_id": f"{side}_club",
        "official_name": f"{side}_official_name",
        "city": f"{side}_city",
        "country": f"{side}_country_name",
        "league": f"{side}_league",
        "league_code": f"{side}_league_code",
        "league_level": f"{side}_league_level",
        "league_country": f"{side}_league_country",
    })

    cols = [
        f"{side}_club",
        f"{side}_official_name",
        f"{side}_city",
        f"{side}_country_name",
        f"{side}_league",
        f"{side}_league_code",
        f"{side}_league_level",
        f"{side}_league_country",
    ]

    return df.merge(tmp[cols], on=f"{side}_club", how="left")


def check_rows(df, step):
    assert len(df) == original_rows, f"Zeilenzahl nach {step} geändert!"
    print(f"{step:<30}: {len(df):,}")

# --------------------------------------------------------
# Club Merge
# --------------------------------------------------------


transfers = merge_lookup(transfers, clubs, "from")
check_rows(transfers, "FROM Club Lookup")

transfers = merge_profiles(transfers, club_profiles, "from")
check_rows(transfers, "FROM Club Profile")

transfers = merge_lookup(transfers, clubs, "to")
check_rows(transfers, "TO Club Lookup")

transfers = merge_profiles(transfers, club_profiles, "to")
check_rows(transfers, "TO Club Profile")

# --------------------------------------------------------
# Player Merge
# --------------------------------------------------------

transfers = transfers.merge(profiles, on="player_id", how="left")
check_rows(transfers, "Player Profiles")

# --------------------------------------------------------
# Nationality Features
# --------------------------------------------------------

nationalities = (
    transfers["nationality"]
    .fillna("")
    .str.split(";")
)

transfers["primary_nationality"] = nationalities.str[0].str.strip()

transfers["secondary_nationality"] = (
    nationalities.str[1]
    .str.strip()
    if nationalities.str.len().max() > 1
    else None
)

transfers["dual_nationality"] = nationalities.str.len() > 1

transfers = transfers.merge(career, on="player_id", how="left")
check_rows(transfers, "Career Paths")


# --------------------------------------------------------
# Vereinslos
# --------------------------------------------------------

for side in ["from", "to"]:
    transfers[f"{side}_club_name"] = transfers[f"{side}_club_name"].fillna(
        "Unknown")

    transfers.loc[transfers[f"{side}_club"] == "515", [
        f"{side}_club_name",
        f"{side}_official_name",
        f"{side}_country_name",
        f"{side}_city",
        f"{side}_league"
    ]] = "Without a club"

# --------------------------------------------------------
# Datentypen
# --------------------------------------------------------

transfers["age"] = pd.to_numeric(transfers["age"], errors="coerce")
transfers["market_value"] = pd.to_numeric(
    transfers["market_value"], errors="coerce")
transfers["date"] = pd.to_datetime(
    transfers["date"], errors="coerce", utc=True)

if "from_league_level" in transfers.columns:
    transfers["from_league_level"] = pd.to_numeric(
        transfers["from_league_level"], errors="coerce")

if "to_league_level" in transfers.columns:
    transfers["to_league_level"] = pd.to_numeric(
        transfers["to_league_level"], errors="coerce")

# --------------------------------------------------------
# Features
# --------------------------------------------------------

transfers["international"] = transfers["from_country"] != transfers["to_country"]
transfers["domestic_transfer"] = ~transfers["international"]

transfers["league_change"] = (
    transfers["from_league_code"] != transfers["to_league_code"]
)

transfers["country_change"] = (
    transfers["from_country_name"] != transfers["to_country_name"]
)

transfers["from_free_agent"] = transfers["from_club"] == "515"
transfers["to_free_agent"] = transfers["to_club"] == "515"

# --------------------------------------------------------
# Career Path Type
# --------------------------------------------------------

transfers["path_type"] = "Club Transfer"

# Spieler war vor dem Wechsel vereinslos
transfers.loc[
    transfers["from_club"] == "515",
    "path_type"
] = "Free Agent"

# Spieler wurde nach dem Wechsel vereinslos
transfers.loc[
    transfers["to_club"] == "515",
    "path_type"
] = "Released"

transfers["career_move"] = (
    transfers["from_country_name"].fillna("Unbekannt")
    + " → "
    + transfers["to_country_name"].fillna("Unbekannt")
)

if "from_league_level" in transfers.columns and "to_league_level" in transfers.columns:
    transfers["league_level_change"] = (
        transfers["to_league_level"] - transfers["from_league_level"]
    )

# --------------------------------------------------------
# Kategorien
# --------------------------------------------------------

category_columns = [
    "position",
    "foot",
    "agent",
    "nationality",
    "primary_nationality",
    "secondary_nationality",
    "transfer_type",
    "from_country_name",
    "to_country_name",
    "from_league",
    "to_league",
    "from_league_code",
    "to_league_code",
]

for col in category_columns:
    if col in transfers.columns:
        transfers[col] = transfers[col].astype("category")

# --------------------------------------------------------
# Sanity Checks
# --------------------------------------------------------

print("\n" + "=" * 60)
print("SANITY CHECKS")
print("=" * 60)

for col in [
    "from_league",
    "to_league",
    "agent",
    "nationality",
]:
    if col in transfers.columns:
        print(f"Missing {col:<18}: {transfers[col].isna().sum()}")

# --------------------------------------------------------
# Speichern
# --------------------------------------------------------

outfile = OUTPUT / "master_dataset.csv"
transfers.to_csv(outfile, index=False, encoding="utf-8-sig")

print("\n" + "=" * 60)
print("MASTER DATASET")
print("=" * 60)

print(f"Transfers : {len(transfers):,}")
print(f"Spieler   : {transfers.player_id.nunique():,}")
print(f"Vereine   : {clubs.club_id.nunique():,}")

if "agent" in transfers.columns:
    print(f"Agenturen : {transfers.agent.nunique():,}")

print(f"\nGespeichert:\n{outfile}")
