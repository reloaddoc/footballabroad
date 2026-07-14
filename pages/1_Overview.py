import streamlit as st

from utils import load_data

# --------------------------------------------------------
# Load
# --------------------------------------------------------

df = load_data()

# --------------------------------------------------------
# Header
# --------------------------------------------------------

st.title("🧭 KickWays")

st.subheader("Career Intelligence")

st.caption(
    """
Explore international football careers based on historical transfer evidence.
"""
)

st.divider()

# --------------------------------------------------------
# What is KickWays?
# --------------------------------------------------------

st.header("What is KickWays?")

st.markdown(
    """
KickWays helps professional football players, agents and clubs explore
international career opportunities by analysing historical transfer data.

Instead of predicting the future, KickWays answers one question:

> **What career paths have comparable players actually taken?**

Every recommendation is based on real historical transfers.
"""
)

st.divider()

# --------------------------------------------------------
# Current MVP
# --------------------------------------------------------

st.header("Current MVP")

col1, col2 = st.columns(2)

with col1:

    st.success("✅ Similar Players")

    st.success("✅ Career Paths")

    st.success("✅ Recommended Countries")

    st.success("✅ Recommended Leagues")

with col2:

    st.success("✅ Recommended Clubs")

    st.success("✅ Recommended Agents")

    st.info("🚧 Player Explorer")

st.divider()

# --------------------------------------------------------
# Workflow
# --------------------------------------------------------

st.header("How it works")

st.markdown(
    """
1. Create a player profile.

2. Find comparable players.

3. Explore historical career paths.

4. Discover countries, leagues, clubs and agents.

5. Open individual player careers.
"""
)

st.divider()

# --------------------------------------------------------
# Database
# --------------------------------------------------------

st.header("Database")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Transfers",
    f"{len(df):,}"
)

c2.metric(
    "Players",
    f"{df['player_id'].nunique():,}"
)

c3.metric(
    "Countries",
    f"{df['to_country_name'].nunique():,}"
)

st.divider()

# --------------------------------------------------------
# Design Principles
# --------------------------------------------------------

st.header("Design Principles")

st.markdown(
    """
- Historical evidence instead of predictions

- Transparent career exploration

- Built for players, agents and clubs

- Explainable insights

- Career Intelligence
"""
)

st.divider()

st.caption("KickWays • Career Intelligence MVP")
