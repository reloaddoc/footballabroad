import pandas as pd

from database import read_table

# ==========================================================
# League Dimension
# ==========================================================


def load_league_dimension():
    return read_table("league_dimension")

# ==========================================================
# Dataset vorbereiten
# ==========================================================


def prepare_dataset(df):
    leagues = load_league_dimension()

    # Harmonisierung bei fehlerhafter Groß-/Kleinschreibung
    if "Level" in leagues.columns and "level" not in leagues.columns:
        leagues = leagues.rename(columns={"Level": "level"})

    # Fallbacks für Pflichtspalten
    if "level" not in leagues.columns:
        leagues["level"] = pd.NA
    if "league_group" not in leagues.columns:
        leagues["league_group"] = pd.NA

    # Abfangen unterschiedlicher Schlüssel-Benennungen im Eingabe-DataFrame
    if "from_league_code" not in df.columns and "competition_code" in df.columns:
        df = df.rename(columns={"competition_code": "from_league_code"})
    if "to_league_code" not in df.columns and "competition_code" in df.columns:
        df = df.rename(columns={"competition_code": "to_league_code"})

    # ------------------------------------------------------
    # Positions-Mapping (NEU)
    # ------------------------------------------------------
    position_mapping = {
        # Goalkeeper
        "Torwart": "Goalkeeper",
        "Goalkeeper": "Goalkeeper",

        # Defense
        "Innenverteidiger": "Defense",
        "Linker Verteidiger": "Defense",
        "Rechter Verteidiger": "Defense",
        "Außenverteidiger": "Defense",
        "Abwehr": "Defense",

        # Midfield
        "Defensives Mittelfeld": "Midfield",
        "Zentrales Mittelfeld": "Midfield",
        "Offensives Mittelfeld": "Midfield",
        "Linkes Mittelfeld": "Midfield",
        "Rechtes Mittelfeld": "Midfield",
        "Mittelfeld": "Midfield",

        # Offense
        "Mittelstürmer": "Offense",
        "Linksaußen": "Offense",
        "Rechtsaußen": "Offense",
        "Hängende Spitze": "Offense",
        "Sturm": "Offense"
    }

    # Neue Spalte "position_group" erzeugen, ohne das Original zu überschreiben
    if "position" in df.columns:
        df["position_group"] = df["position"].map(
            position_mapping).fillna("Unknown")
    else:
        df["position_group"] = "Unknown"

    # ------------------------------------------------------
    # FROM
    # ------------------------------------------------------
    from_lookup = leagues[
        [
            "competition_code",
            "league_group",
            "level",
        ]
    ].rename(
        columns={
            "competition_code": "from_league_code",
            "league_group": "from_league_group",
            "level": "from_level",
        }
    )

    data = df.merge(
        from_lookup,
        on="from_league_code",
        how="left",
    )

    # ------------------------------------------------------
    # TO
    # ------------------------------------------------------
    to_lookup = leagues[
        [
            "competition_code",
            "league_group",
            "level",
        ]
    ].rename(
        columns={
            "competition_code": "to_league_code",
            "league_group": "to_league_group",
            "level": "to_level",
        }
    )

    data = data.merge(
        to_lookup,
        on="to_league_code",
        how="left",
    )

    # ------------------------------------------------------
    # Level Difference
    # ------------------------------------------------------
    data["level_change"] = pd.NA

    if "from_level" in data.columns and "to_level" in data.columns:
        data["from_level"] = pd.to_numeric(data["from_level"], errors="coerce")
        data["to_level"] = pd.to_numeric(data["to_level"], errors="coerce")

        mask = (
            data["from_level"].notna()
            & data["to_level"].notna()
        )

        data.loc[mask, "level_change"] = (
            data.loc[mask, "from_level"]
            - data.loc[mask, "to_level"]
        )

    # ------------------------------------------------------
    # Career Step
    # ------------------------------------------------------
    data["career_step"] = "Unknown"

    if "level_change" in data.columns and not data["level_change"].isna().all():

        data.loc[
            data["level_change"] > 0,
            "career_step",
        ] = "Step Up"

        data.loc[
            data["level_change"] == 0,
            "career_step",
        ] = "Same Level"

        data.loc[
            data["level_change"] < 0,
            "career_step",
        ] = "Step Down"

    return data

# ==========================================================
# Dropdown Optionen
# ==========================================================


def get_league_options(
    df,
    current_country="Any",
):

    leagues = df.copy()

    if current_country != "Any":

        leagues = leagues[
            leagues["from_country_name"] == current_country
        ]

    return sorted(

        leagues["from_league_group"]

        .dropna()

        .unique()

    )

# ==========================================================
# Similar Players (Filtert jetzt nach position_group)
# ==========================================================


def find_similar_players(
    df,
    age_range=None,
    position="Any",
    current_country="Any",
    current_league="Any",
    agent="Any",
):
    data = df.copy()

    # ------------------------------------------------------
    # Age (optional)
    # ------------------------------------------------------
    if age_range is not None:
        data = data[
            data["age"].between(
                age_range[0],
                age_range[1]
            )
        ]

    # ------------------------------------------------------
    # Position (KORRIGIERT: Filtert nach position_group)
    # ------------------------------------------------------
    if position != "Any":
        data = data[
            data["position_group"] == position
        ]

    # ------------------------------------------------------
    # Current Country
    # ------------------------------------------------------
    if current_country != "Any":
        data = data[
            data["from_country_name"] == current_country
        ]

    # ------------------------------------------------------
    # Current League Group
    # ------------------------------------------------------
    if current_league != "Any":
        data = data[
            data["from_league_group"] == current_league
        ]

    # ------------------------------------------------------
    # Agent
    # ------------------------------------------------------
    if agent != "Any":
        data = data[
            data["agent"] == agent
        ]

    # ------------------------------------------------------
    # Einen Datensatz pro Spieler
    # ------------------------------------------------------
    data = (
        data
        .sort_values(
            [
                "player_id",
                "age",
            ]
        )
        .drop_duplicates(
            subset="player_id",
            keep="last",
        )
        .reset_index(
            drop=True
        )
    )

    return data

# ==========================================================
# Recommended Countries
# ==========================================================


def recommended_countries(
    matches,
    top_n=10,
):
    if matches.empty:
        return pd.DataFrame(
            columns=["Country", "Players"]
        )

    exclude = [
        "Unknown",
        "Unbekannt",
        "Vereinslos",
    ]

    return (
        matches
        .loc[
            ~matches["to_country_name"].isin(exclude),
            "to_country_name"
        ]
        .dropna()
        .value_counts()
        .head(top_n)
        .rename_axis("Country")
        .reset_index(name="Players")
    )


# ==========================================================
# Recommended Leagues
# ==========================================================

def recommended_leagues(
    matches,
    top_n=20,
):

    if matches.empty:
        return pd.DataFrame(
            columns=[
                "League",
                "Players",
            ]
        )

    exclude = [
        "",
        "Unknown",
        "Unbekannt",
        "Vereinslos",
        "Unattached",
        "Retired",
        "Career break",
    ]

    valid = matches.copy()

    valid = valid[
        ~valid["to_league_group"]
        .fillna("")
        .isin(exclude)
    ]

    valid = valid[
        valid["from_league_group"]
        != valid["to_league_group"]
    ]

    valid = valid[
        ~valid["to_club_name"]
        .fillna("")
        .isin([
            "Without a club",
            "Unattached",
            "Retired",
            "Career break",
        ])
    ]

    summary = (
        valid
        .groupby("to_league_group")
        .agg(
            Players=("player_id", "nunique"),
        )
        .reset_index()
        .sort_values(
            by=["Players", "to_league_group"],
            ascending=[False, True],
        )
        .head(top_n)
    )

    summary = summary.rename(
        columns={
            "to_league_group": "League",
        }
    )

    return summary

# ==========================================================
# Recommended Clubs
# ==========================================================


def recommended_clubs(
    matches,
    top_n=10,
):
    if matches.empty:
        return pd.DataFrame(
            columns=["Club", "Players"]
        )

    exclude = [
        "Unknown",
        "Unbekannt",
        "Vereinslos",
        "Retired",
        "Career break",
    ]

    return (
        matches
        .loc[
            ~matches["to_club_name"].isin(exclude),
            "to_club_name"
        ]
        .dropna()
        .value_counts()
        .head(top_n)
        .rename_axis("Club")
        .reset_index(name="Players")
    )

# ==========================================================
# Recommended Agents
# ==========================================================


def recommended_agents(
    matches,
    top_n=10,
):
    if matches.empty:
        return pd.DataFrame(
            columns=["Agent", "Players"]
        )

    exclude = [
        "",
        "Unknown",
        "Unbekannt",
        "ohne Berater",
    ]

    return (
        matches
        .loc[
            ~matches["agent"].fillna("").isin(exclude),
            "agent"
        ]
        .value_counts()
        .head(top_n)
        .rename_axis("Agent")
        .reset_index(name="Players")
    )

# ==========================================================
# Top Career Paths
# ==========================================================


def recommended_paths(
    matches,
    top_n=10,
):

    if matches.empty:
        return pd.DataFrame(
            columns=[
                "Career Path",
                "Players",
            ]
        )

    exclude = [
        "",
        "Unknown",
        "Unbekannt",
        "Vereinslos",
        "Unattached",
        "Retired",
        "Career break",
    ]

    valid = matches.copy()

    # Nur gültige Startligen
    valid = valid[
        ~valid["from_league_group"]
        .fillna("")
        .isin(exclude)
    ]

    # Nur gültige Zielligen
    valid = valid[
        ~valid["to_league_group"]
        .fillna("")
        .isin(exclude)
    ]

    # Nur echte Ligawechsel
    valid = valid[
        valid["from_league_group"]
        != valid["to_league_group"]
    ]

    # Vereine ohne sportlichen Mehrwert ausschließen
    valid = valid[
        ~valid["to_club_name"]
        .fillna("")
        .isin([
            "Without a club",
            "Unattached",
            "Retired",
            "Career break",
        ])
    ]

    # Karrierepfad erzeugen
    valid["Career Path"] = (
        valid["from_league_group"]
        + " → "
        + valid["to_league_group"]
    )

    paths = (

        valid

        .groupby("Career Path")

        .agg(

            Players=("player_id", "nunique"),

        )

        .reset_index()

        .sort_values(
            ["Players", "Career Path"],
            ascending=[False, True],
        )

    )

    return paths
