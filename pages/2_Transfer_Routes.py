import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    load_data,
    sidebar_filters,
)

from config import PLOT_TEMPLATE

# ------------------------------------------------------------
# Load
# ------------------------------------------------------------

df = load_data()
df = sidebar_filters(df)

# Nur Datensätze mit gültigen Ländern
df_routes = df.dropna(
    subset=[
        "from_country_name",
        "to_country_name",
    ]
).copy()

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.title("🌍 Transfer Corridors")

st.caption(
    """
Discover recurring international transfer routes between
countries, leagues and clubs.
"""
)

# ------------------------------------------------------------
# KPIs
# ------------------------------------------------------------

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "Transfers",
    f"{len(df_routes):,}",
)

k2.metric(
    "Players",
    df_routes.player_id.nunique(),
)

k3.metric(
    "Countries",
    pd.concat(
        [
            df_routes.from_country_name,
            df_routes.to_country_name,
        ]
    ).nunique(),
)

k4.metric(
    "International",
    int(df_routes.international.sum()),
)

k5.metric(
    "Domestic",
    int((~df_routes.international).sum()),
)

st.divider()

# ------------------------------------------------------------
# Corridor Summary
# ------------------------------------------------------------

corridors = (

    df_routes

    .groupby(

        [

            "from_country_name",

            "to_country_name",

        ]

    )

    .agg(

        Transfers=("player_id", "count"),

        Players=("player_id", "nunique"),

        AvgAge=("age", "mean"),

        Agents=("agent", "nunique"),

        Clubs=("to_club_name", "nunique"),

    )

    .reset_index()

)

corridors = corridors.sort_values(

    "Transfers",

    ascending=False,

)

st.header("Transfer Corridor Summary")

st.dataframe(

    corridors,

    width="stretch",

    height=450,

)

# ------------------------------------------------------------
# Top Corridors
# ------------------------------------------------------------

fig = px.bar(

    corridors.head(25),

    x="Transfers",

    y="to_country_name",

    color="from_country_name",

    orientation="h",

    template=PLOT_TEMPLATE,

    title="Top 25 Country Corridors",

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="top_country_corridors",

)

st.divider()

# ------------------------------------------------------------
# Corridor Explorer
# ------------------------------------------------------------

st.header("Corridor Explorer")

left, right = st.columns(2)

with left:

    origins = sorted(

        df_routes["from_country_name"]

        .unique()

    )

    origin = st.selectbox(

        "Origin Country",

        origins,

    )

with right:

    destinations = sorted(

        df_routes.loc[

            df_routes["from_country_name"] == origin,

            "to_country_name",

        ]

        .unique()

    )

    destination = st.selectbox(

        "Destination Country",

        destinations,

    )

corridor = df_routes[

    (df_routes["from_country_name"] == origin)

    &

    (df_routes["to_country_name"] == destination)

].copy()

# ------------------------------------------------------------
# Corridor KPIs
# ------------------------------------------------------------

st.subheader(f"{origin} → {destination}")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(

    "Transfers",

    len(corridor),

)

c2.metric(

    "Players",

    corridor.player_id.nunique(),

)

c3.metric(

    "Agents",

    corridor.agent.nunique(),

)

c4.metric(

    "Destination Clubs",

    corridor.to_club_name.nunique(),

)

c5.metric(

    "Destination Leagues",

    corridor.to_league.nunique(),

)

st.divider()

# ------------------------------------------------------------
# Season Development
# ------------------------------------------------------------

st.subheader("Transfers by Season")

season = (

    corridor

    .groupby("season")

    .size()

    .reset_index(name="Transfers")

)

fig = px.line(

    season,

    x="season",

    y="Transfers",

    markers=True,

    template=PLOT_TEMPLATE,

)

st.plotly_chart(

    fig,

    width="stretch",

    key="season_development",

)

st.divider()
# ------------------------------------------------------------
# Corridor Intelligence
# ------------------------------------------------------------

left, right = st.columns(2)

# --------------------------------------------------------
# Origin Clubs
# --------------------------------------------------------

with left:

    st.subheader("🏟 Origin Clubs")

    origin_clubs = (

        corridor["from_club_name"]

        .fillna("Unknown")

        .value_counts()

        .rename_axis("Club")

        .reset_index(name="Transfers")

    )

    st.dataframe(
        origin_clubs,
        width="stretch",
        height=300,
    )

# --------------------------------------------------------
# Destination Clubs
# --------------------------------------------------------

with right:

    st.subheader("🏟 Destination Clubs")

    destination_clubs = (

        corridor["to_club_name"]

        .fillna("Unknown")

        .value_counts()

        .rename_axis("Club")

        .reset_index(name="Transfers")

    )

    st.dataframe(
        destination_clubs,
        width="stretch",
        height=300,
    )

st.divider()

# ------------------------------------------------------------
# Agencies & Positions
# ------------------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("🤝 Agencies")

    agencies = (

        corridor["agent"]

        .fillna("Unknown")

        .value_counts()

        .rename_axis("Agency")

        .reset_index(name="Transfers")

    )

    st.dataframe(
        agencies,
        width="stretch",
        height=300,
    )

with right:

    st.subheader("👤 Positions")

    positions = (

        corridor["position"]

        .fillna("Unknown")

        .value_counts()

        .rename_axis("Position")

        .reset_index(name="Players")

    )

    fig = px.pie(
        positions,
        names="Position",
        values="Players",
        hole=0.45,
        template=PLOT_TEMPLATE,
    )

    st.plotly_chart(
        fig,
        width="stretch",
        key="corridor_positions",
    )

st.divider()

# ------------------------------------------------------------
# League Routes
# ------------------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("🏆 Origin Leagues")

    leagues_from = (

        corridor["from_league"]

        .fillna("Unknown")

        .value_counts()

        .rename_axis("League")

        .reset_index(name="Transfers")

    )

    st.dataframe(
        leagues_from,
        width="stretch",
        height=300,
    )

with right:

    st.subheader("🏆 Destination Leagues")

    leagues_to = (

        corridor["to_league"]

        .fillna("Unknown")

        .value_counts()

        .rename_axis("League")

        .reset_index(name="Transfers")

    )

    st.dataframe(
        leagues_to,
        width="stretch",
        height=300,
    )

st.divider()

# ------------------------------------------------------------
# Transfer List
# ------------------------------------------------------------

st.subheader("📋 Transfer List")

columns = [

    "date",

    "season",

    "full_name",

    "age",

    "position",

    "agent",

    "from_club_name",

    "to_club_name",

    "from_league",

    "to_league",

    "market_value",

    "transfer_type",

]

available_columns = [

    c for c in columns if c in corridor.columns

]

transfer_table = (

    corridor

    [available_columns]

    .sort_values(

        "date",

        ascending=False,

    )

)

st.dataframe(

    transfer_table,

    width="stretch",

    height=500,

)

st.download_button(

    label="📥 Download Corridor as CSV",

    data=transfer_table.to_csv(index=False).encode("utf-8-sig"),

    file_name=f"{origin}_{destination}_corridor.csv",

    mime="text/csv",

)

st.divider()

# ------------------------------------------------------------
# Corridor Interpretation
# ------------------------------------------------------------

st.subheader("🧠 Corridor Summary")

avg_age = corridor["age"].mean()

top_agent = agencies.iloc[0]["Agency"] if len(agencies) else "Unknown"

top_origin = origin_clubs.iloc[0]["Club"] if len(origin_clubs) else "Unknown"

top_destination = destination_clubs.iloc[0]["Club"] if len(
    destination_clubs) else "Unknown"

st.info(
    f"""
### Corridor Profile

- **Transfers:** {len(corridor)}
- **Players:** {corridor.player_id.nunique()}
- **Average age:** {avg_age:.1f}
- **Most active agency:** {top_agent}
- **Most common origin club:** {top_origin}
- **Most common destination club:** {top_destination}

This corridor can now be compared with other international transfer corridors
to identify recurring career patterns.
"""
)

st.caption(
    "Hypothesis H1 – Recurring transfer corridors between football markets."
)
