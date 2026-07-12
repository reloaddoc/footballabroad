import streamlit as st

from utils import (
    load_data,
    sidebar_filters,
    create_kpis,
    missing_values,
)

from plots import (
    top_destination_countries,
    top_destination_leagues,
    top_agents,
    export_clubs,
    import_clubs,
    nationality_distribution,
    position_distribution,
    international_share,
)

# --------------------------------------------------------
# Hilfsfunktion für Quick Insights (NEU)
# --------------------------------------------------------


def first_valid(series, invalid):
    s = (
        series
        .dropna()
        .astype(str)
        .loc[lambda x: ~x.isin(invalid)]
    )
    if len(s) == 0:
        return "N/A"
    return s.value_counts().idxmax()


# --------------------------------------------------------
# Load
# --------------------------------------------------------

df = load_data()

df = sidebar_filters(df)

kpis = create_kpis(df)

# Berechnungen für Quick Insights mit der neuen Logik
top_country = first_valid(df["to_country_name"], ["Without a club", "Unknown"])
top_club = first_valid(df["from_club_name"], ["Without a club", "Unknown"])
top_agent = first_valid(df["agent"], ["no agent", "Unknown", "nan", ""])
top_league = first_valid(df["to_league"], ["Without a club", "Unknown"])


# --------------------------------------------------------
# Header
# --------------------------------------------------------

st.title("📊 Overview")

st.caption(
    "Interactive overview of the FootballAbroad research database."
)

# --------------------------------------------------------
# KPIs
# --------------------------------------------------------

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Transfers", f"{kpis['Transfers']:,}")
c2.metric("Players", f"{kpis['Players']:,}")
c3.metric("Agents", f"{kpis['Agents']:,}")
c4.metric("Countries", f"{kpis['Countries']:,}")
c5.metric("Leagues", f"{kpis['Leagues']:,}")
c6.metric("Clubs", f"{kpis['Clubs']:,}")

st.divider()

# --------------------------------------------------------
# Overview Charts
# --------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        top_destination_countries(df),
        width="stretch",
    )

with right:
    st.plotly_chart(
        top_destination_leagues(df),
        width="stretch",
    )

# --------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        top_agents(df),
        width="stretch",
    )

with right:
    st.plotly_chart(
        export_clubs(df),
        width="stretch",
    )

# --------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        import_clubs(df),
        width="stretch",
    )

with right:
    st.plotly_chart(
        international_share(df),
        width="stretch",
    )

# --------------------------------------------------------

left, right = st.columns(2)

with left:
    st.plotly_chart(
        nationality_distribution(df),
        width="stretch",
    )

with right:
    st.plotly_chart(
        position_distribution(df),
        width="stretch",
    )

# --------------------------------------------------------
# Matching Players
# --------------------------------------------------------

st.divider()

st.header("Matching Players")

st.caption(
    f"""
{len(df):,} transfers • {df['player_id'].nunique():,} unique players
"""
)

columns = [

    "full_name",

    "age",

    "position",

    "nationality",

    "from_club_name",

    "from_country_name",

    "to_club_name",

    "to_country_name",

    "agent"

]

columns = [

    c for c in columns

    if c in df.columns

]

st.dataframe(

    df[columns]

    .sort_values(

        "full_name"

    ),

    width="stretch",

    height=600,

    hide_index=True,

)

# --------------------------------------------------------
# Data Quality
# --------------------------------------------------------

st.divider()

st.header("Data Quality")

left, right = st.columns([2, 1])

with left:
    st.dataframe(
        missing_values(df),
        width="stretch",
        height=450,
    )

with right:
    st.metric(
        "Missing Agents",
        int(df["agent"].isna().sum()),
    )

    st.metric(
        "Missing Nationalities",
        int(df["nationality"].isna().sum()),
    )

    st.metric(
        "Missing From League",
        int(df["from_league"].isna().sum()),
    )

    st.metric(
        "Missing To League",
        int(df["to_league"].isna().sum()),
    )

# --------------------------------------------------------
# Quick Insights (GEÄNDERT)
# --------------------------------------------------------

st.divider()

st.header("Quick Insights")

col1, col2 = st.columns(2)

with col1:
    st.success(
        f"""
Top destination country:

**{top_country}**
"""
    )

    st.success(
        f"""
Most active agent:

**{top_agent}**
"""
    )

with col2:
    st.success(
        f"""
Top exporting club:

**{top_club}**
"""
    )

    st.success(
        f"""
Top destination league:

**{top_league}**
"""
    )

# --------------------------------------------------------

st.caption("FootballAbroad Research Dashboard")
