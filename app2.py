import re
from database import read_table
import pandas as pd
import streamlit as st
from country_mapping import COUNTRY_MAP
from dashboard_app2 import career_outcomes


def read_file(path):
    return pd.read_csv(
        path, sep=None, engine="python", encoding="utf-8-sig"
    )


def group_league_name(country, league_str):
    # League missing
    if pd.isna(league_str):
        return league_str

    clean_str = str(league_str).split(" (Opta")[0].strip()
    s = clean_str.lower()

    # Country missing
    if pd.isna(country):
        country = ""
    else:
        country = str(country).strip()

    # -------------------------
    # Germany
    # -------------------------
    if country == "Germany":

        german_patterns = {
            "dfb-nachwuchsliga": "Germany - DFB-Nachwuchsliga",
            "regionalliga": "Germany - Regionalliga",
            "oberliga": "Germany - Oberliga",
            "bayernliga": "Germany - Bayernliga",
            "verbandsliga": "Germany - Verbandsliga",
            "landesliga": "Germany - Landesliga",
            "bezirksoberliga": "Germany - Bezirksoberliga",
            "bezirksliga": "Germany - Bezirksliga",
            "kreisoberliga": "Germany - Kreisoberliga",
            "kreisliga": "Germany - Kreisliga",
        }

        for pattern, replacement in german_patterns.items():
            if pattern in s:
                return replacement

    # -------------------------
    # England
    # -------------------------
    elif country == "England":
        if "national league north" in s or "national league south" in s:
            return "England - National League North/South"

    # -------------------------
    # Spain
    # -------------------------
    elif country == "Spain":
        if "primera federación" in s or "primera federacion" in s:
            return "Spain - Primera Federación"

        if "segunda federación" in s or "segunda federacion" in s:
            return "Spain - Segunda Federación"

    # -------------------------
    # Italy
    # -------------------------
    elif country == "Italy":
        if re.search(r"serie c\s*-\s*girone", s):
            return "Italy - Serie C"

        if re.search(r"serie d\s*-\s*girone", s):
            return "Italy - Serie D"

        if "primavera 2" in s:
            return "Italy - Primavera 2"

    # -------------------------
    # Poland
    # -------------------------
    elif country == "Poland":
        if "betclic 3 liga" in s:
            return "Poland - Betclic 3 Liga"

    # -------------------------
    # Turkey
    # -------------------------
    elif country == "Turkey":
        if re.search(r"\b2\.?\s*lig\b", s):
            return "Turkey - 2.Lig"

        if re.search(r"\b3\.?\s*lig\b", s):
            return "Turkey - 3.Lig"

    return clean_str


def add_opta_scores(master, mapping):
    mapping = mapping.copy()
    mapping["opta_score"] = pd.to_numeric(
        mapping["opta_score"], errors="coerce")

    by_code = (
        mapping[["competition_code", "opta_score"]]
        .dropna(subset=["competition_code"])
        .drop_duplicates(subset="competition_code")
    )
    by_league = (
        mapping[["our_league", "opta_score"]]
        .dropna(subset=["our_league"])
        .drop_duplicates(subset="our_league")
    )

    master = master.merge(
        by_code,
        left_on="from_league_code",
        right_on="competition_code",
        how="left",
    ).rename(columns={"opta_score": "from_score"}).drop(columns="competition_code")

    master = master.merge(
        by_code,
        left_on="to_league_code",
        right_on="competition_code",
        how="left",
    ).rename(columns={"opta_score": "to_score"}).drop(columns="competition_code")

    master = master.merge(
        by_league,
        left_on="from_league",
        right_on="our_league",
        how="left",
    ).rename(columns={"opta_score": "from_score_by_name"}).drop(columns="our_league")

    master = master.merge(
        by_league,
        left_on="to_league",
        right_on="our_league",
        how="left",
    ).rename(columns={"opta_score": "to_score_by_name"}).drop(columns="our_league")

    master["from_score"] = master["from_score"].fillna(
        master["from_score_by_name"])
    master["to_score"] = master["to_score"].fillna(master["to_score_by_name"])
    master = master.drop(columns=["from_score_by_name", "to_score_by_name"])
    master["league_quality_change"] = master["to_score"] - master["from_score"]

    return master


def league_options(frame, league_col, country_col, score_col):
    options = frame[[league_col, country_col, score_col]].dropna(
        subset=[league_col]
    )
    options = options.drop_duplicates(subset=league_col).sort_values(
        [country_col, league_col],
        na_position="last",
    )

    labels = {"All": "All"}
    values = ["All"]

    for row in options.itertuples(index=False):
        league = getattr(row, league_col)
        country = getattr(row, country_col)
        score = getattr(row, score_col)
        score_label = f" (Opta {score:.2f})" if pd.notna(score) else ""

        # Verhindert doppelte Land-Präfixe (z. B. "Spain - Spain - Primera Federación")
        country_str = f"{country} - " if pd.notna(
            country) and str(country).strip() else ""
        if country_str and str(league).startswith(country_str):
            labels[league] = f"{league}{score_label}"
        else:
            labels[league] = f"{country_str}{league}{score_label}"

        values.append(league)

    return values, labels


@st.cache_data
def load_data():
    master = read_table("master_dataset")
    leagues = read_table("league_dimension")
    mapping = read_table("league_mapping")
    opta = read_table("opta_rankings")

    master = add_opta_scores(master, mapping)

    for col in [
        "primary_nationality",
        "secondary_nationality",
        "from_country_name",
        "to_country_name",
    ]:
        if col in master.columns:
            master[col] = master[col].replace(COUNTRY_MAP)

    position_map = {
        "Torwart": "Goalkeeper",
        "Abwehr": "Defence",
        "Mittelfeld": "Midfield",
        "Sturm": "Attack",
    }
    master["position_group"] = (
        master["position"]
        .fillna("Unknown")
        .str.split(" - ")
        .str[0]
        .replace(position_map)
    )

    master = master[master["position_group"] != "Unknown"].copy()

    # Apply grouping to league columns using the corresponding country column
    if "from_league" in master.columns and "from_country_name" in master.columns:
        master["from_league"] = master.apply(
            lambda row: group_league_name(
                row["from_country_name"],
                row["from_league"]
            ),
            axis=1,
        )

    if "to_league" in master.columns and "to_country_name" in master.columns:
        master["to_league"] = master.apply(
            lambda row: group_league_name(
                row["to_country_name"],
                row["to_league"]
            ),
            axis=1,
        )

    if "from_competition" in master.columns and "from_country_name" in master.columns:
        master["from_competition"] = master.apply(
            lambda row: group_league_name(
                row["from_country_name"],
                row["from_competition"]
            ),
            axis=1,
        )

    if "to_competition" in master.columns and "to_country_name" in master.columns:
        master["to_competition"] = master.apply(
            lambda row: group_league_name(
                row["to_country_name"],
                row["to_competition"]
            ),
            axis=1,
        )

    return master, leagues, mapping, opta


# Call load_data() AFTER defining helper functions
master, leagues, mapping, opta = load_data()


# ========================================================
# SIDEBAR FILTERS SETUP
# ========================================================
st.sidebar.header("Player Profile")

nationality = st.sidebar.selectbox(
    "Nationality",
    ["All"] + sorted(master["primary_nationality"].dropna().unique()),
)

position = st.sidebar.selectbox(
    "Position", ["All"] + sorted(master["position_group"].dropna().unique())
)

age = st.sidebar.slider(
    "Age", int(master["age"].min()), int(master["age"].max()), (18, 30)
)


st.sidebar.header("Career Decision")

origin_country = st.sidebar.selectbox(
    "Moved From (Country)",
    ["All"] + sorted(master["from_country_name"].dropna().unique()),
)

origin_source = master
if origin_country != "All":
    origin_source = origin_source[origin_source["from_country_name"]
                                  == origin_country]

origin_options, origin_labels = league_options(
    origin_source,
    "from_league",
    "from_country_name",
    "from_score",
)
origin = st.sidebar.selectbox(
    "Moved From (League)",
    origin_options,
    format_func=lambda value: origin_labels.get(value, value),
)

destination_country = st.sidebar.selectbox(
    "Moved To (Country)",
    ["All"] + sorted(master["to_country_name"].dropna().unique()),
)

destination_source = master
if destination_country != "All":
    destination_source = destination_source[
        destination_source["to_country_name"] == destination_country
    ]

destination_options, destination_labels = league_options(
    destination_source,
    "to_league",
    "to_country_name",
    "to_score",
)
destination = st.sidebar.selectbox(
    "Moved To (League)",
    destination_options,
    format_func=lambda value: destination_labels.get(value, value),
)

st.sidebar.caption(
    "Tip: choose a league country first, then pick from the shorter league list."
)

transfer = st.sidebar.selectbox(
    "Transfer Type", ["All"] +
    sorted(master["transfer_type"].dropna().unique())
)


# ========================================================
# FILTER APPLICATION
# ========================================================
filtered = master.copy()

if nationality != "All":
    filtered = filtered[filtered["primary_nationality"] == nationality]

if position != "All":
    filtered = filtered[filtered["position_group"] == position]

filtered = filtered[
    (filtered["age"] >= age[0]) & (filtered["age"] <= age[1])
]

if origin != "All":
    filtered = filtered[filtered["from_league"] == origin]

if origin_country != "All":
    filtered = filtered[filtered["from_country_name"] == origin_country]

if destination_country != "All":
    filtered = filtered[filtered["to_country_name"] == destination_country]

if destination != "All":
    filtered = filtered[filtered["to_league"] == destination]

if transfer != "All":
    filtered = filtered[filtered["transfer_type"] == transfer]


st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Players", len(filtered))
c2.metric("Nationalities", filtered["primary_nationality"].nunique())
c3.metric("Origin Leagues", filtered["from_league"].nunique())
c4.metric("Moved to (league)", filtered["to_league"].nunique())
st.divider()

# ========================================================
# RENDER CAREER OUTCOMES DASHBOARD
# ========================================================
current_filters = {
    "nationality": nationality,
    "position": position,
    "origin": origin,
    "destination": destination,
    "origin_country": origin_country,
    "destination_country": destination_country,
    "transfer_type": transfer,
}

career_outcomes.show(master, filtered, filters=current_filters)
