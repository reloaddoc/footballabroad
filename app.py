import streamlit as st

from config import APP_TITLE, APP_ICON

# --------------------------------------------------------
# Page Config
# --------------------------------------------------------

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------
# Header
# --------------------------------------------------------

st.title("⚽ FootballAbroad")

st.subheader("Football Transfer Intelligence Platform")

st.markdown(
    """
FootballAbroad analyses international football careers outside the traditional
top leagues.

Instead of focusing on individual transfers, the platform identifies recurring
career routes, transfer corridors, agency networks and stepping-stone clubs to
better understand how international football careers develop.
"""
)

st.divider()

# --------------------------------------------------------
# Current Database
# --------------------------------------------------------

st.header("Current Database")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Players", "699")
c2.metric("Transfers", "7,511")
c3.metric("Clubs", "3,770")
c4.metric("Agencies", "321")

st.divider()

# --------------------------------------------------------
# Research Questions
# --------------------------------------------------------

st.header("Research Questions")

col1, col2 = st.columns(2)

with col1:

    st.info(
        """
### H1 – Transfer Corridors

Do recurring international transfer corridors exist between countries,
leagues and clubs?
"""
    )

    st.info(
        """
### H2 – Agency Networks

Do specialised agencies dominate particular international football markets?
"""
    )

with col2:

    st.info(
        """
### H3 – Stepping-Stone Clubs

Which clubs repeatedly serve as gateways into international careers?
"""
    )

    st.info(
        """
### H4 – Career Route Intelligence

Can historical football transfers be transformed into career recommendations?
"""
    )

st.info(
    """
### H5 – Career Route Recommender

What recommendations can be derived from historical transfer data?
"""
)

st.divider()

# --------------------------------------------------------
# Dashboard Modules
# --------------------------------------------------------

st.header("Research Dashboard")

st.markdown(
    """
Use the navigation in the left sidebar.

### Available modules

- 📊 Overview
- 🌍 Transfer Corridors
- 🤝 Agency Intelligence
- 🏟 Club Intelligence *(coming next)*
- 👤 Player Explorer *(coming next)*
- 🧭 Career Navigator *(coming next)*
- 🔬 Hypothesis Testing *(coming next)*
"""
)

st.divider()

# --------------------------------------------------------
# Vision
# --------------------------------------------------------

st.header("Project Vision")

st.markdown(
    """
FootballAbroad is **not another football transfer database**.

The objective is to identify hidden international football networks and answer
questions such as:

- Which leagues act as stepping stones?
- Which agencies specialise in certain countries?
- Which clubs repeatedly export players abroad?
- Which career routes occur again and again?
- Which paths have previously been taken by players with similar profiles?

The long-term goal is to develop a **Football Transfer Intelligence Platform**
for players, clubs, agencies and researchers.
"""
)

st.divider()

st.success(
    """
👈 **Select a module from the sidebar to begin exploring the data.**
"""
)

st.caption("FootballAbroad Research Project • Version 1.0")
