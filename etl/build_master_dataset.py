import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from database import read_table, write_table
from translations import (
    COUNTRY_MAP,
    STATUS_MAP,
    FOOT_MAP,
)


league_inventory = pd.read_excel(ROOT / "league_inventory.xlsx")

league_inventory.columns = (
    league_inventory.columns.str.strip().str.lower()
)

for col in ["country", "league", "aggregation"]:
    league_inventory[col] = (
        league_inventory[col]
        .fillna("")
        .astype(str)
        .str.strip()
    )


league_inventory["aggregation"] = (
    league_inventory["aggregation"]
    .replace("", pd.NA)
    .fillna(league_inventory["league"])
)

league_lookup = league_inventory[
    ["competition_code", "aggregation"]
].copy()


def merge_lookup(df, lookup, side):
    tmp = lookup.rename(columns={
        "club_id": f"{side}_club",
        "name": f"{side}_club_name",
        "slug": f"{side}_club_slug",
    })

    return df.merge(
        tmp[[f"{side}_club", f"{side}_club_name", f"{side}_club_slug"]],
        on=f"{side}_club",
        how="left",
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


def build_master_dataset():
    print("Lade Daten aus DuckDB...")

    transfers = read_table("transfers")
    clubs = read_table("clubs")
    profiles = read_table("player_profiles")
    career = read_table("career_paths")
    club_profiles = read_table("club_profiles")

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

    print("\nPruefe eindeutige Schluessel...")

    assert clubs["club_id"].duplicated().sum(
    ) == 0, "Duplicate club_id in clubs"
    assert club_profiles["club_id"].duplicated().sum(
    ) == 0, "Duplicate club_id in club_profiles"
    assert profiles["player_id"].duplicated().sum(
    ) == 0, "Duplicate player_id in player_profiles"
    assert career["player_id"].duplicated().sum(
    ) == 0, "Duplicate player_id in career_paths"

    print("OK")

    original_rows = len(transfers)
    print(f"Transfers geladen: {original_rows:,}")

    def check_rows(df, step):
        assert len(df) == original_rows, f"Zeilenzahl nach {step} geaendert!"
        print(f"{step:<30}: {len(df):,}")

    transfers = merge_lookup(transfers, clubs, "from")
    check_rows(transfers, "FROM Club Lookup")

    transfers = merge_profiles(transfers, club_profiles, "from")
    check_rows(transfers, "FROM Club Profile")

    transfers = merge_lookup(transfers, clubs, "to")
    check_rows(transfers, "TO Club Lookup")

    transfers = merge_profiles(transfers, club_profiles, "to")
    check_rows(transfers, "TO Club Profile")

    debug = transfers[transfers["player_id"] == "93642"].copy()

    print("\n========== KARWOT AFTER CLUB MERGES ==========")

    print(
        debug[
            [
                "season",
                "date",
                "from_club",
                "from_club_name",
                "from_league",
                "from_league_code",
                "to_club",
                "to_club_name",
                "to_league",
                "to_league_code",
                "transfer_type",
            ]
        ].sort_values("date")
    )

    # ----------------------------------------------------------
    # 1. ERST DIE AGGREGATION ERSTELLEN
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # 1. ERST DIE AGGREGATION ERSTELLEN
    # ----------------------------------------------------------
    code_map = league_inventory.set_index("competition_code")[
        "aggregation"].dropna().to_dict()
    name_map = league_inventory.set_index(
        "league")["aggregation"].dropna().to_dict()

    # FROM league aggregation
    transfers["from_aggregation"] = transfers["from_league_code"].map(code_map)
    transfers["from_aggregation"] = transfers["from_aggregation"].fillna(
        transfers["from_league"].map(name_map)
    )
    transfers["from_aggregation"] = transfers["from_aggregation"].fillna(
        transfers["from_league"]
    )

    # TO league aggregation
    transfers["to_aggregation"] = transfers["to_league_code"].map(code_map)
    transfers["to_aggregation"] = transfers["to_aggregation"].fillna(
        transfers["to_league"].map(name_map)
    )
    transfers["to_aggregation"] = transfers["to_aggregation"].fillna(
        transfers["to_league"]
    )

    # ----------------------------------------------------------
    # 2. POKALE & PLAYOFFS FILTERN
    # ----------------------------------------------------------
    pokal_keywords = [
        "pokal",
        "cup",
        "beker",
        "copa",
        "coppa",
        "coupe",
        "taça",
        "kupa",
        "puchar",
        "trophy",
        "shield",
        "liguilla",
        "supercup",
        "supercopa",
        "relegation",
        "rel.",
        "play-off",
        "playoff",

        # internationale Wettbewerbe
        "champions league",
        "europa league",
        "conference league",

        # sonstige Wettbewerbe
        "bundesliga-news",
        "Amateurmeisterschaft",
    ]

    pattern = "|".join(pokal_keywords)

    is_cup_from = (
        transfers["from_league"].str.contains(pattern, case=False, na=False) |
        transfers["from_aggregation"].str.contains(
            pattern, case=False, na=False)
    )
    is_cup_to = (
        transfers["to_league"].str.contains(pattern, case=False, na=False) |
        transfers["to_aggregation"].str.contains(pattern, case=False, na=False)
    )

    transfers = transfers[~is_cup_from & ~is_cup_to].copy()

    # Referenz-Zeilenzahl nach dem Filtern aktualisieren!
    original_rows = len(transfers)
    print(f"Transfers nach Pokal-Filter: {original_rows:,}")

    check_rows(transfers, "League Aggregation")

    transfers = transfers.merge(profiles, on="player_id", how="left")
    check_rows(transfers, "Player Profiles")

    nationalities = (
        transfers["nationality"]
        .fillna("")
        .str.split(";")
    )

    transfers["primary_nationality"] = nationalities.str[0].str.strip()

    transfers["secondary_nationality"] = (
        nationalities.str[1].str.strip()
        if nationalities.str.len().max() > 1
        else None
    )

    transfers["dual_nationality"] = nationalities.str.len() > 1

    transfers = transfers.merge(career, on="player_id", how="left")
    check_rows(transfers, "Career Paths")

    for side in ["from", "to"]:
        transfers[f"{side}_club_name"] = transfers[f"{side}_club_name"].fillna(
            "Unknown"
        )

        transfers.loc[transfers[f"{side}_club"] == "515", [
            f"{side}_club_name",
            f"{side}_official_name",
            f"{side}_country_name",
            f"{side}_city",
            f"{side}_league",
        ]] = "Without a club"

    transfers["age"] = pd.to_numeric(transfers["age"], errors="coerce")

    transfers["date"] = pd.to_datetime(
        transfers["date"], errors="coerce", utc=True
    )

    if "from_league_level" in transfers.columns:
        transfers["from_league_level"] = pd.to_numeric(
            transfers["from_league_level"], errors="coerce"
        )

    if "to_league_level" in transfers.columns:
        transfers["to_league_level"] = pd.to_numeric(
            transfers["to_league_level"], errors="coerce"
        )

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

    transfers["path_type"] = "Club Transfer"

    transfers.loc[
        transfers["from_club"] == "515",
        "path_type",
    ] = "Free Agent"

    transfers.loc[
        transfers["to_club"] == "515",
        "path_type",
    ] = "Released"

    transfers["career_move"] = (
        transfers["from_country_name"].fillna("Unbekannt")
        + " \u2192 "
        + transfers["to_country_name"].fillna("Unbekannt")
    )

    if "from_league_level" in transfers.columns and "to_league_level" in transfers.columns:
        transfers["league_level_change"] = (
            transfers["to_league_level"] - transfers["from_league_level"]
        )

    # ==========================================================
    # TRANSLATIONS (Vor Category Conversion ausführen)
    # ==========================================================

    # Countries
    for col in [
        "from_country_name",
        "to_country_name",
        "primary_nationality",
        "secondary_nationality",
    ]:
        if col in transfers.columns:
            transfers[col] = transfers[col].replace(COUNTRY_MAP)

    # Player status
    for col in [
        "current_club",
        "last_club",
    ]:
        if col in transfers.columns:
            transfers[col] = transfers[col].replace(STATUS_MAP)

    # Preferred foot
    if "foot" in transfers.columns:
        transfers["foot"] = transfers["foot"].replace(FOOT_MAP)

    # ==========================================================
    # CATEGORIES
    # ==========================================================
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

    return transfers, clubs


def main():
    master, clubs = build_master_dataset()
    write_table("master_dataset", master)

    print("\n" + "=" * 60)
    print("MASTER DATASET")
    print("=" * 60)

    print(f"Transfers : {len(master):,}")
    print(f"Spieler   : {master.player_id.nunique():,}")
    print(f"Vereine   : {clubs.club_id.nunique():,}")

    if "agent" in master.columns:
        print(f"Agenturen : {master.agent.nunique():,}")

    print("\nGespeichert in DuckDB Tabelle: master_dataset")


if __name__ == "__main__":
    main()
