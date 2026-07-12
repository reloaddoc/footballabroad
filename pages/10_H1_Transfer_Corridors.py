import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_data, sidebar_filters
from config import PLOT_TEMPLATE

# ----------------------------------------------------
# Load
# ----------------------------------------------------

df = load_data()
df = sidebar_filters(df)

# ----------------------------------------------------
# H1 Sample Definition
# ----------------------------------------------------

# Nur internationale Transfers
df = df[df["international"]].copy()

# Nur echte Vereinswechsel
df = df[
    (df["from_club"] != "515") &
    (df["to_club"] != "515")
].copy()

# Nur vollständige Länder
df = df.dropna(
    subset=[
        "from_country_name",
        "to_country_name"
    ]
)

df = df[
    (df["from_country_name"] != "Unbekannt") &
    (df["to_country_name"] != "Unbekannt")
]

# Nur vollständige Ligen
df = df.dropna(
    subset=[
        "from_league",
        "to_league"
    ]
)

df = df[
    (df["from_league"] != "Vereinslos") &
    (df["to_league"] != "Vereinslos")
]

st.title("🧪 H1 – Transfer Corridors")

st.markdown("""
### Research Question

Do recurring international transfer corridors exist between countries and leagues?

A transfer corridor is defined as repeated transfers between the same
origin and destination country (or league).
""")

st.divider()

corridors = (
    df.groupby(
        [
            "from_country_name",
            "to_country_name"
        ]
    )
    .size()
    .reset_index(name="Transfers")
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Transfers",
    len(df)
)

c2.metric(
    "Players",
    df.player_id.nunique()
)

c3.metric(
    "Country Corridors",
    len(corridors)
)

c4.metric(
    "Origin Countries",
    df["from_country_name"].nunique()
)

c5.metric(
    "Destination Countries",
    df["to_country_name"].nunique()
)

st.divider()

# ----------------------------------------------------
# Country Corridors
# ----------------------------------------------------

st.header("Country Corridors")

country = (

    df.groupby(

        [

            "from_country_name",

            "to_country_name"

        ]

    )

    .agg(

        Transfers=("player_id", "count"),

        Players=("player_id", "nunique"),

        Avg_Age=("age", "mean"),

        Avg_From_Level=("from_league_level", "mean"),

        Avg_To_Level=("to_league_level", "mean"),

    )

    .reset_index()

    .sort_values(

        "Transfers",

        ascending=False

    )

)

st.dataframe(

    country,

    width="stretch",

    height=500,

)

fig = px.bar(

    country.head(20),

    x="Transfers",

    y="to_country_name",

    color="from_country_name",

    orientation="h",

    template=PLOT_TEMPLATE,

    title="Top 20 International Country Corridors"

)

fig.update_yaxes(categoryorder="total ascending")

st.plotly_chart(

    fig,

    width="stretch",

    key="country_corridors"

)

st.divider()

# ----------------------------------------------------
# League Corridors
# ----------------------------------------------------

st.header("League Corridors")

league = (

    df.groupby(

        [

            "from_league",

            "to_league"

        ]

    )

    .agg(

        Transfers=("player_id", "count"),

        Players=("player_id", "nunique"),

        Avg_Age=("age", "mean"),

    )

    .reset_index()

    .sort_values(

        "Transfers",

        ascending=False

    )

)

st.dataframe(

    league,

    width="stretch",

    height=500,

)

fig = px.bar(

    league.head(20),

    x="Transfers",

    y="to_league",

    color="from_league",

    orientation="h",

    template=PLOT_TEMPLATE,

    title="Top 20 League Corridors"

)

fig.update_yaxes(categoryorder="total ascending")

st.plotly_chart(

    fig,

    width="stretch",

    key="league_corridors"

)

st.divider()

# ----------------------------------------------------
# First Evidence
# ----------------------------------------------------

st.header("Interpretation")

top = country.iloc[0]

share = top["Transfers"] / len(df) * 100

st.success(
    f"""
### Preliminary Evidence

After excluding free-agent moves and incomplete records, the most frequent
international transfer corridor is

**{top['from_country_name']} → {top['to_country_name']}**

- Transfers: **{top['Transfers']}**
- Unique Players: **{top['Players']}**
- Average Age: **{top['Avg_Age']:.1f} years**

This corridor represents **{share:.2f}%** of all analysed international
transfers.

These results provide initial evidence that international transfers are
concentrated in recurring corridors instead of being randomly distributed.

**Hypothesis H1 is provisionally supported.**
"""
)

st.divider()

st.caption(
    "FootballAbroad Research – Hypothesis H1"
)
