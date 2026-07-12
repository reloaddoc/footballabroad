from country_mapping import COUNTRY_MAP
import pandas as pd
import streamlit as st

from config import MASTER_DATASET


# ---------------------------------------------------
# Load Master Dataset
# ---------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv(
        MASTER_DATASET,
        encoding="utf-8-sig",
        low_memory=False,
    )

    # KORREKTUR: Ab hier alles sauber in die Funktion einrücken!
    # Länder vereinheitlichen
    for col in [
        "from_country_name",
        "to_country_name",
        "nationality",
        "primary_nationality",
        "secondary_nationality",
    ]:
        if col in df.columns:
            df[col] = df[col].replace(COUNTRY_MAP)

    return df


# ---------------------------------------------------
# Sidebar Filter
# ---------------------------------------------------

def sidebar_filters(df):
    st.sidebar.header("Filters")

    data = df.copy()

    filter_columns = [
        "position",
        "nationality",
        "agent",
        "from_country_name",
        "to_country_name",
        "from_league",
        "to_league",
        "transfer_type",
    ]

    for col in filter_columns:
        if col not in data.columns:
            continue

        # --- Values-Ermittlung je nach Spalte ---
        if col == "nationality":
            values = sorted(
                data[col]
                .dropna()
                .astype(str)
                .str.split(";")
                .explode()
                .str.strip()
                .unique()
            )
        else:
            values = sorted(
                data[col]
                .dropna()
                .astype(str)
                .unique()
            )

        # --- Multiselect-Auswahl und Filterung ---
        selection = st.sidebar.multiselect(
            col.replace("_", " ").title(),
            values,
        )

        if selection:
            if col == "nationality":
                pattern = "|".join(
                    rf"(^|;){value}(;|$)"
                    for value in selection
                )
                data = data[
                    data["nationality"]
                    .fillna("")
                    .str.contains(
                        pattern,
                        regex=True
                    )
                ]
            else:
                data = data[
                    data[col]
                    .astype(str)
                    .isin(selection)
                ]

    # --- KORREKTUR: Dieser gesamte Block muss INNERHALB der Funktion eingerückt sein ---
    if "age" in data.columns:
        ages = data["age"].dropna()

        if len(ages):
            minimum = int(ages.min())
            maximum = int(ages.max())

            # FALL 1: Es gibt verschiedene Altersstufen (Normalfall)
            if minimum < maximum:
                age = st.sidebar.slider(
                    "Age",
                    min_value=minimum,
                    max_value=maximum,
                    value=(minimum, maximum),
                    key="sidebar_age_slider"
                )
                # Nur in diesem Fall filtern wir die Daten anhand des Sliders
                data = data[data["age"].between(age[0], age[1])]

            # FALL 2: Alle verbleibenden Spieler haben exakt dasselbe Alter (z.B. 17)
            else:
                # Wir zeichnen ein künstlich deaktiviertes Widget mit min < max,
                # damit Streamlit unter der Haube glücklich ist, filtern aber nicht mehr.
                st.sidebar.slider(
                    "Age",
                    min_value=minimum,
                    max_value=minimum + 1,
                    value=(minimum, minimum),
                    disabled=True,
                    key="sidebar_age_slider_disabled"  # Anderer Key!
                )
                st.sidebar.info(
                    f"Age: {minimum} (Only this age available for current filters)")

    return data


# ---------------------------------------------------
# KPI Helper
# ---------------------------------------------------

def create_kpis(df):
    return {
        "Transfers": len(df),
        "Players": df.player_id.nunique(),
        "Agents": df.agent.nunique(),
        "Countries":
            pd.concat(
                [
                    df.from_country_name,
                    df.to_country_name,
                ]
        ).nunique(),
        "Leagues":
            pd.concat(
                [
                    df.from_league_code,
                    df.to_league_code,
                ]
        ).nunique(),
        "Clubs":
            pd.concat(
                [
                    df.from_club,
                    df.to_club,
                ]
        ).nunique(),
    }


# ---------------------------------------------------
# Missing Values
# ---------------------------------------------------

def missing_values(df):
    return (
        df
        .isna()
        .sum()
        .sort_values(
            ascending=False
        )
        .to_frame(
            "Missing"
        )
    )
