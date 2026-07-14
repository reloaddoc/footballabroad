import streamlit as st

from utils import load_data

from career_navigator import (
    prepare_dataset,
    get_league_options,
    find_similar_players,
    recommended_countries,
    recommended_leagues,
    recommended_clubs,
    recommended_agents,
    recommended_paths,
)
import streamlit as st

from utils import load_data
from career_navigator import (
    prepare_dataset,
    get_league_options,
    find_similar_players,
    recommended_countries,
    recommended_leagues,
    recommended_clubs,
    recommended_agents,
    recommended_paths,
)

# --------------------------------------------------------
# Load
# --------------------------------------------------------
df = load_data()
df = prepare_dataset(df)

# --------------------------------------------------------
# Header
# --------------------------------------------------------
st.title("🧭 Career Navigator")
st.caption(
    """
Discover realistic international career paths based on historical football transfers.
"""
)
st.divider()

# --------------------------------------------------------
# Career Brief
# --------------------------------------------------------
st.header("📝 Career Brief")
st.markdown(
    """
Tell us where you are in your football career.

KickWays will identify players who started from a similar situation
and show the career paths they actually took.

This is **not** a prediction engine.
Every insight is based on historical transfers.
"""
)

st.info(
    """
### Your current situation

Think about your career today.

You don't need to complete every field.
KickWays works with partial information.
"""
)

st.subheader("Where are you playing today?")

# --------------------------------------------------------
# Age
# --------------------------------------------------------
ages = df["age"].dropna()
minimum = int(ages.min())
maximum = int(ages.max())

use_age = st.checkbox(
    "Include my age",
    value=False,
)

age_range = None
if use_age:
    age_range = st.slider(
        "Age",
        minimum,
        maximum,
        (20, 25),
    )


# --------------------------------------------------------
# Where are you playing today? (KORREKTUR: Spalten sauber definiert)
# --------------------------------------------------------
col_country, col_league = st.columns(2)

with col_country:
    current_country = st.selectbox(
        "Country",
        sorted(df["from_country_name"].dropna().unique()),
        index=None,
        placeholder="Select a country...",
    )

with col_league:

    if current_country is None:

        st.selectbox(
            "League",
            [],
            index=None,
            placeholder="Select a country first...",
            disabled=True,
        )

        current_league = None

    else:

        current_league = st.selectbox(

            "League",

            get_league_options(
                df,
                current_country,
            ),

            index=None,

            placeholder="Select a league...",

        )

# Position wird im MVP vorerst nicht verwendet
position = "Any"

# --------------------------------------------------------
# Agent
# --------------------------------------------------------
st.subheader("What are you looking for?")

career_goal = st.radio(

    "Career Goal",

    [

        "First professional contract",

        "Move abroad",

        "Reach a higher level",

        "Trial opportunities",

    ],

    label_visibility="collapsed",

)

# --------------------------------------------------------
# Button und Session State
# --------------------------------------------------------
analyse = st.button(
    "Find Comparable Careers",
    type="primary",
)

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if analyse:
    st.session_state.analysis_done = True

# --------------------------------------------------------
# Analyse & Ergebnisanzeige (KORREKTUR: Alles im korrekten Scope)
# --------------------------------------------------------
if st.session_state.analysis_done:

    if current_country is None:
        current_country = "Any"

    if current_league is None:
        current_league = "Any"

    matching = find_similar_players(
        df=df,
        age_range=age_range,
        position=position,
        current_country=current_country,
        current_league=current_league,
        agent="Any",
    )

    st.divider()
    st.header("Comparable Players")

    if career_goal == "Move abroad":
        st.info(
            "We'll focus on how comparable players made their first move abroad."
        )

    elif career_goal == "Reach a higher level":
        st.info(
            "We'll highlight how comparable players progressed to stronger leagues."
        )

    elif career_goal == "Trial opportunities":
        st.info(
            "We'll show players who found opportunities through different career routes."
        )

    else:
        st.info(
            "We'll explore how comparable players earned their first professional contract."
        )

    st.write(
        f"""
We found **{matching['player_id'].nunique()} comparable players**
with a similar career starting point.
"""
    )

    # ----------------------------------------------------
    # KPIs
    # ----------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Matching Players", matching["player_id"].nunique())
    c2.metric("Destination Countries", matching["to_country_name"].nunique())
    c3.metric("Destination Leagues", matching["to_league_group"].nunique())
    c4.metric("Destination Clubs", matching["to_club_name"].nunique())

    st.divider()

    # ----------------------------------------------------
    # Empfehlungen berechnen
    # ----------------------------------------------------
    countries = recommended_countries(matching)
    leagues = recommended_leagues(matching)
    clubs = recommended_clubs(matching)
    agents = recommended_agents(matching)
    paths = recommended_paths(matching)

    # ----------------------------------------------------
    # Countries / Leagues
    # ----------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌍 Countries Comparable Players Moved To")
        st.dataframe(
            countries,
            hide_index=True,
            height=300,
        )

    with col2:
        st.subheader("🏆 Leagues Comparable Players Joined")
        st.dataframe(
            leagues,
            hide_index=True,
            height=300,
        )

    st.divider()

    # ----------------------------------------------------
    # Top Career Paths
    # ----------------------------------------------------
    st.subheader("📖 Career Story")
    st.caption(
        "These are the most common career moves taken by comparable players.")

    st.dataframe(
        paths.head(10),
        hide_index=True,
        height=300,
    )

    st.divider()

    # ----------------------------------------------------
    # Explore Career Path
    # ----------------------------------------------------
    if not paths.empty:
        st.subheader("🔎 Explore Career Stories")

        selected_path = st.selectbox(
            "Select a career path",
            paths["Career Path"].tolist(),
            index=None,
            placeholder="Choose a career path...",
        )

        if selected_path is not None:
            path_players = matching.copy()
            path_players["Career Path"] = (
                path_players["from_league_group"]
                + " → "
                + path_players["to_league_group"]
            )
            path_players = path_players[path_players["Career Path"]
                                        == selected_path]

            st.caption(
                f"{path_players['player_id'].nunique()} players followed this path"
            )

            columns = [
                "full_name",
                "age",
                "position_group",
                "nationality",
                "from_club_name",
                "to_club_name",
                "agent",
            ]
            columns = [c for c in columns if c in path_players.columns]

            st.dataframe(
                path_players[columns].sort_values(["age", "full_name"]),
                hide_index=True,
                height=350,
            )

            # ----------------------------------------------------
            # Player Details
            # ----------------------------------------------------
            st.divider()

            selected_player = st.selectbox(
                "Explore Player", sorted(path_players["full_name"].unique())
            )

            if selected_player:
                player = path_players[path_players["full_name"]
                                      == selected_player]

                st.subheader("Player Details")
                p_c1, p_c2, p_c3 = st.columns(3)

                p_c1.metric("Nationality", player["nationality"].iloc[0])
                p_c2.metric("Position", player["position_group"].iloc[0])
                p_c3.metric("Agent", player["agent"].iloc[0])

                st.dataframe(
                    player[
                        [
                            "season",
                            "from_club_name",
                            "to_club_name",
                            "from_league_group",
                            "to_league_group",
                        ]
                    ].sort_values("season"),
                    hide_index=True,
                )

    st.divider()

    # ----------------------------------------------------
    # Recommended Clubs / Agents
    # ----------------------------------------------------
    col_clubs, col_agents = st.columns(2)

    with col_clubs:
        st.subheader("🏟 Clubs Comparable Players Joined")
        st.dataframe(
            clubs,
            hide_index=True,
            height=300,
        )

    with col_agents:
        st.subheader("🤝 Agents Used by Comparable Players")
        st.dataframe(
            agents,
            hide_index=True,
            height=300,
        )

    st.divider()

    # ----------------------------------------------------
    # Matching Players Table
    # ----------------------------------------------------
    st.subheader("👥 Matching Players")
    st.caption(f"{matching['player_id'].nunique():,} similar players found")

    all_display_cols = [
        "full_name",
        "age",
        "position_group",
        "nationality",
        "from_club_name",
        "from_league_group",
        "to_club_name",
        "to_league_group",
        "agent",
    ]
    all_display_cols = [c for c in all_display_cols if c in matching.columns]

    st.dataframe(
        matching[all_display_cols].sort_values(["age", "full_name"]),
        hide_index=True,
        height=500,
    )

# --------------------------------------------------------
# Footer
# --------------------------------------------------------
st.divider()
st.caption("KickWays • Career Navigator v2")
