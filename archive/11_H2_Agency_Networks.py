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
# Sample Definition
# ----------------------------------------------------

df = df[df["international"]].copy()

df = df.dropna(
    subset=[
        "agent",
        "to_country_name"
    ]
)

df = df[
    ~df["agent"].isin(
        [
            "",
            "Unbekannt",
            "ohne Berater"
        ]
    )
]

# ----------------------------------------------------
# Emerging Markets
# ----------------------------------------------------

TARGET_MARKETS = [

    "Thailand",

    "Malaysia",

    "Indonesien",

    "Vietnam",

    "Singapur",

    "Philippinen",

    "Hongkong",

    "Indien",

    "Südkorea",

    "Finnland",

    "Kanada",

    "Puerto Rico",

]

# ----------------------------------------------------
# Nur Emerging Markets
# ----------------------------------------------------

df = df[
    df["to_country_name"].isin(
        TARGET_MARKETS
    )
]

# ----------------------------------------------------
# Mindestgröße pro Markt
# ----------------------------------------------------

MIN_MARKET_TRANSFERS = 20

market_counts = (

    df["to_country_name"]

    .value_counts()

)

valid_markets = market_counts[

    market_counts >= MIN_MARKET_TRANSFERS

].index

df = df[

    df["to_country_name"]

    .isin(valid_markets)

]

st.title("🧪 H2 – Agency Networks in Emerging Markets")

st.markdown("""

### Research Question

Do specific football agencies dominate particular emerging football markets?

Instead of analysing agencies individually, this analysis investigates
each destination market and identifies the agencies that repeatedly
place players there.

""")

st.divider()

# ----------------------------------------------------
# KPIs
# ----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "Transfers",

    len(df)

)

c2.metric(

    "Players",

    df.player_id.nunique()

)

c3.metric(

    "Agencies",

    df.agent.nunique()

)

c4.metric(

    "Markets",

    df.to_country_name.nunique()

)

st.divider()

# ----------------------------------------------------
# Destination Markets
# ----------------------------------------------------

st.header("Destination Markets")

markets = (

    df["to_country_name"]

    .value_counts()

    .reset_index()

)

markets.columns = [

    "Market",

    "Transfers"

]

st.dataframe(

    markets,

    width="stretch",

    height=350

)

fig = px.bar(

    markets,

    x="Transfers",

    y="Market",

    orientation="h",

    template=PLOT_TEMPLATE,

    title="Transfers into Emerging Markets"

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="markets"

)

st.divider()

# ----------------------------------------------------
# Market Explorer
# ----------------------------------------------------

st.header("Market Explorer")

selected_market = st.selectbox(

    "Destination Market",

    sorted(

        valid_markets

    )

)

market_df = df[

    df["to_country_name"]

    == selected_market

]

# ----------------------------------------------------
# Market KPIs
# ----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "Transfers",

    len(market_df)

)

c2.metric(

    "Players",

    market_df.player_id.nunique()

)

c3.metric(

    "Agencies",

    market_df.agent.nunique()

)

c4.metric(

    "Origin Countries",

    market_df.from_country_name.nunique()

)

st.divider()

# ----------------------------------------------------
# Top Agencies in Selected Market
# ----------------------------------------------------

st.header(f"Top Agencies in {selected_market}")

agency_market = (

    market_df

    .groupby("agent")

    .agg(

        Transfers=("player_id", "count"),

        Players=("player_id", "nunique"),

        Top_Nationality=(

            "primary_nationality",

            lambda x: x.mode().iat[0]
            if not x.mode().empty
            else None

        ),

        Top_Origin=(

            "from_country_name",

            lambda x: x.mode().iat[0]
            if not x.mode().empty
            else None

        ),

        Top_League=(

            "from_league",

            lambda x: x.mode().iat[0]
            if not x.mode().empty
            else None

        ),

        Origin_Countries=("from_country_name", "nunique"),

        Origin_Leagues=("from_league", "nunique"),

        Avg_Age=("age", "mean")

    )

    .reset_index()

    .sort_values(

        "Transfers",

        ascending=False

    )

)

# Marktanteil berechnen

agency_market["Market Share (%)"] = (

    agency_market["Transfers"]

    / agency_market["Transfers"].sum()

    * 100

).round(1)

st.dataframe(

    agency_market,

    width="stretch",

    height=450

)

# ----------------------------------------------------
# Bar Chart
# ----------------------------------------------------

fig = px.bar(

    agency_market,

    x="Transfers",

    y="agent",

    orientation="h",

    template=PLOT_TEMPLATE,

    title=f"Top Agencies in {selected_market}"

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="market_agents"

)

st.divider()

# ----------------------------------------------------
# Market Share
# ----------------------------------------------------

st.header("Agency Market Share")

fig = px.pie(

    agency_market.head(10),

    names="agent",

    values="Transfers",

    hole=0.45,

    template=PLOT_TEMPLATE,

    title=f"Top 10 Agencies in {selected_market}"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="market_share"

)

st.divider()

# ----------------------------------------------------
# Concentration
# ----------------------------------------------------

st.header("Market Concentration")

top5 = agency_market.head(5).copy()

top5["Agency"] = top5["agent"]

fig = px.bar(

    top5,

    x="Agency",

    y="Market Share (%)",

    template=PLOT_TEMPLATE,

    text="Market Share (%)",

    title="Top 5 Agencies by Market Share"

)

fig.update_traces(

    textposition="outside"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="market_concentration"

)

st.divider()

# ----------------------------------------------------
# Preliminary Finding
# ----------------------------------------------------

leader = agency_market.iloc[0]

top_nat = leader["Top_Nationality"]

top_origin = leader["Top_Origin"]

top_league = leader["Top_League"]

st.success(f"""

### Preliminary Evidence

The largest agency operating in **{selected_market}** is

**{leader['agent']}**

with

- **{leader['Transfers']} international transfers**
- **{leader['Players']} unique players**
- **{leader['Market Share (%)']:.1f}% market share**

Most frequently represented player profile

- Nationality: **{top_nat}**
- Origin country: **{top_origin}**
- Origin league: **{top_league}**

The five largest agencies account for

**{agency_market.head(5)['Market Share (%)'].sum():.1f}%**

of all documented international transfers into **{selected_market}**.

This suggests that a relatively small number of agencies repeatedly
mediate player transfers into this football market.

""")

st.divider()

# ----------------------------------------------------
# Player Profile of Selected Market
# ----------------------------------------------------

st.header(f"Player Profile — {selected_market}")

left, right = st.columns(2)

# ----------------------------------------------------
# Nationalities
# ----------------------------------------------------

with left:

    st.subheader("Nationalities")

    nationality = (

        market_df["primary_nationality"]

        .fillna("Unknown")

        .value_counts()

        .reset_index()

    )

    nationality.columns = [

        "Nationality",

        "Players"

    ]

    st.dataframe(

        nationality,

        width="stretch",

        height=300

    )

    fig = px.bar(

        nationality.head(15),

        x="Players",

        y="Nationality",

        orientation="h",

        template=PLOT_TEMPLATE

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    st.plotly_chart(

        fig,

        width="stretch",

        key="market_nationality"

    )

# ----------------------------------------------------
# Positions
# ----------------------------------------------------

with right:

    st.subheader("Positions")

    position = (

        market_df["position"]

        .fillna("Unknown")

        .value_counts()

        .reset_index()

    )

    position.columns = [

        "Position",

        "Players"

    ]

    st.dataframe(

        position,

        width="stretch",

        height=300

    )

    fig = px.bar(

        position,

        x="Players",

        y="Position",

        orientation="h",

        template=PLOT_TEMPLATE

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    st.plotly_chart(

        fig,

        width="stretch",

        key="market_position"

    )

st.divider()

# ----------------------------------------------------
# Origin Countries
# ----------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Origin Countries")

    origin = (

        market_df["from_country_name"]

        .fillna("Unknown")

        .value_counts()

        .reset_index()

    )

    origin.columns = [

        "Country",

        "Transfers"

    ]

    st.dataframe(

        origin,

        width="stretch",

        height=300

    )

    fig = px.bar(

        origin.head(15),

        x="Transfers",

        y="Country",

        orientation="h",

        template=PLOT_TEMPLATE

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    st.plotly_chart(

        fig,

        width="stretch",

        key="origin_country"

    )

# ----------------------------------------------------
# Origin Leagues
# ----------------------------------------------------

with right:

    st.subheader("Origin Leagues")

    leagues = (

        market_df["from_league"]

        .fillna("Unknown")

        .value_counts()

        .reset_index()

    )

    leagues.columns = [

        "League",

        "Transfers"

    ]

    st.dataframe(

        leagues,

        width="stretch",

        height=300

    )

    fig = px.bar(

        leagues.head(15),

        x="Transfers",

        y="League",

        orientation="h",

        template=PLOT_TEMPLATE

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    st.plotly_chart(

        fig,

        width="stretch",

        key="origin_league"

    )

st.divider()

# ----------------------------------------------------
# Age Distribution
# ----------------------------------------------------

st.subheader("Age Distribution")

fig = px.histogram(

    market_df,

    x="age",

    nbins=12,

    template=PLOT_TEMPLATE

)

st.plotly_chart(

    fig,

    width="stretch",

    key="market_age"

)

st.divider()

# ----------------------------------------------------
# Most Common Clubs
# ----------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Origin Clubs")

    clubs = (

        market_df["from_club_name"]

        .fillna("Unknown")

        .value_counts()

        .head(15)

        .reset_index()

    )

    clubs.columns = [

        "Club",

        "Transfers"

    ]

    st.dataframe(

        clubs,

        width="stretch",

        height=300

    )

with right:

    st.subheader("Destination Clubs")

    clubs = (

        market_df["to_club_name"]

        .fillna("Unknown")

        .value_counts()

        .head(15)

        .reset_index()

    )

    clubs.columns = [

        "Club",

        "Transfers"

    ]

    st.dataframe(

        clubs,

        width="stretch",

        height=300

    )

st.divider()
