import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    load_data,
    sidebar_filters,
)

from config import PLOT_TEMPLATE

# --------------------------------------------------------
# Load
# --------------------------------------------------------

df = load_data()
df = sidebar_filters(df)

st.title("🤝 Agent Explorer")

st.caption(
    "Analyse internationaler Transfernetzwerke von Spielerberatern."
)

# --------------------------------------------------------
# KPIs
# --------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Known Agents",
    int(df["agent"].dropna().nunique())
)

c2.metric(
    "Transfers",
    int(df["agent"].notna().sum())
)

c3.metric(
    "Players",
    df.loc[df["agent"].notna(), "player_id"].nunique()
)

c4.metric(
    "Countries",
    df.loc[df["agent"].notna(), "to_country_name"].nunique()
)

st.divider()

# --------------------------------------------------------
# Top Agents
# --------------------------------------------------------

st.header("Top Agencies")

top_agents = (

    df["agent"]

    .dropna()

    .value_counts()

    .reset_index()

)

top_agents.columns = [

    "Agent",

    "Transfers",

]

st.dataframe(

    top_agents,

    use_container_width=True,

    height=500,

)

fig = px.bar(

    top_agents.head(25),

    x="Transfers",

    y="Agent",

    orientation="h",

    template=PLOT_TEMPLATE,

    title="Most Active Agencies",

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    use_container_width=True,

)

st.divider()

# --------------------------------------------------------
# Agent Explorer
# --------------------------------------------------------

st.header("Agency Explorer")

agents = sorted(

    df["agent"]

    .dropna()

    .unique()

)

agent = st.selectbox(

    "Select Agency",

    agents,

)

dfa = df[

    df["agent"] == agent

]

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "Transfers",

    len(dfa)

)

c2.metric(

    "Players",

    dfa["player_id"].nunique()

)

c3.metric(

    "Destination Countries",

    dfa["to_country_name"].nunique()

)

c4.metric(

    "Destination Clubs",

    dfa["to_club_name"].nunique()

)

st.divider()

# --------------------------------------------------------
# Destination Countries
# --------------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Destination Countries")

    countries = (

        dfa["to_country_name"]

        .value_counts()

        .rename_axis("Country")

        .reset_index(name="Transfers")

    )

    st.dataframe(

        countries,

        use_container_width=True,

    )

with right:

    fig = px.bar(

        countries,

        x="Transfers",

        y="Country",

        orientation="h",

        template=PLOT_TEMPLATE,

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

st.divider()

# --------------------------------------------------------
# Destination Leagues
# --------------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Destination Leagues")

    leagues = (

        dfa["to_league"]

        .value_counts()

        .rename_axis("League")

        .reset_index(name="Transfers")

    )

    st.dataframe(

        leagues,

        use_container_width=True,

    )

with right:

    fig = px.bar(

        leagues,

        x="Transfers",

        y="League",

        orientation="h",

        template=PLOT_TEMPLATE,

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

st.divider()

# --------------------------------------------------------
# Destination Clubs
# --------------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Destination Clubs")

    clubs = (

        dfa["to_club_name"]

        .value_counts()

        .rename_axis("Club")

        .reset_index(name="Transfers")

    )

    st.dataframe(

        clubs,

        use_container_width=True,

    )

with right:

    fig = px.bar(

        clubs.head(20),

        x="Transfers",

        y="Club",

        orientation="h",

        template=PLOT_TEMPLATE,

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

st.divider()

# --------------------------------------------------------
# Player Positions
# --------------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Player Positions")

    positions = (

        dfa["position"]

        .value_counts()

        .rename_axis("Position")

        .reset_index(name="Players")

    )

    st.dataframe(

        positions,

        use_container_width=True,

    )

with right:

    fig = px.pie(

        positions,

        names="Position",

        values="Players",

        hole=0.45,

        template=PLOT_TEMPLATE,

    )

    st.plotly_chart(

        fig,

        use_container_width=True,

    )

st.divider()

# --------------------------------------------------------
# Nationalities
# --------------------------------------------------------

st.subheader("Represented Nationalities")

nationalities = (

    dfa["nationality"]

    .value_counts()

    .rename_axis("Nationality")

    .reset_index(name="Players")

)

st.dataframe(

    nationalities,

    use_container_width=True,

)

st.divider()

st.caption(
    "Hypothesis H2: International football transfers are concentrated among a relatively small number of agencies."
)
