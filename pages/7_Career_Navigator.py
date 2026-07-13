from career_navigator import prepare_dataset
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
# Player Profile
# --------------------------------------------------------

st.header("Player Profile")

st.caption(
    """
Select the information you know.

All filters are optional.
"""
)

# --------------------------------------------------------
# Age
# --------------------------------------------------------

ages = df["age"].dropna()

minimum = int(ages.min())
maximum = int(ages.max())

use_age = st.checkbox(
    "Filter by Age",
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

st.divider()

# --------------------------------------------------------
# Position / Country / League
# --------------------------------------------------------

c1, c2, c3 = st.columns(3)

with c1:

    position = st.selectbox(

        "Position",

        ["Any"]

        + sorted(

            df["position_group"]

            .dropna()

            .unique()

        )

    )

with c2:

    current_country = st.selectbox(

        "Current Country",

        ["Any"]

        + sorted(

            df["from_country_name"]

            .dropna()

            .unique()

        )

    )

with c3:

    current_league = st.selectbox(

        "Current League",

        ["Any"]

        + get_league_options(df)

    )

# --------------------------------------------------------
# Agent
# --------------------------------------------------------

agent = st.selectbox(

    "Agent",

    ["Any"]

    + sorted(

        df["agent"]

        .dropna()

        .unique()

    )

)

st.divider()

# --------------------------------------------------------
# Button korrekt definieren (Beispielhafte Vervollständigung)
# --------------------------------------------------------
analyse = st.button(
    "Find Similar Careers",
    type="primary",
    width="stretch",
)

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if analyse:
    st.session_state.analysis_done = True

# --------------------------------------------------------
# Analyse
# --------------------------------------------------------
if st.session_state.analysis_done:

    # KORREKTUR 1: matching auf die gleiche Ebene wie den Rest bringen
    matching = find_similar_players(
        df=df,
        age_range=age_range,
        position=position,
        current_country=current_country,
        current_league=current_league,
        agent=agent,
    )

    st.divider()
    st.header("Career Analysis")

    # ----------------------------------------------------
    # KPIs
    # ----------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Matching Players",
        matching["player_id"].nunique()
    )

    c2.metric(
        "Destination Countries",
        matching["to_country_name"].nunique()
    )

    c3.metric(
        "Destination Leagues",
        matching["to_league_group"].nunique()
    )

    c4.metric(
        "Destination Clubs",
        matching["to_club_name"].nunique()
    )

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
        st.subheader("🌍 Recommended Countries")
        st.dataframe(
            countries,
            hide_index=True,
            width="stretch",
            height=300,
        )

    with col2:
        st.subheader("🏆 Recommended Leagues")
        st.dataframe(
            leagues,
            hide_index=True,
            width="stretch",
            height=300,
        )

    st.divider()

    # ----------------------------------------------------
    # Top Career Paths
    # ----------------------------------------------------
    st.subheader("🧭 Top Career Paths")
    st.caption(
        "Historical transfer paths taken by comparable players."
    )

    st.dataframe(
        paths.head(10),
        hide_index=True,
        width="stretch",
        height=300,
    )

    st.divider()

    # ----------------------------------------------------
    # Explore Career Path (KORREKTUR 2: Kommentar-Ebene begradigt)
    # ----------------------------------------------------
    if not paths.empty:
        st.subheader("🔎 Explore Career Path")

        selected_path = st.selectbox(
            "Select a career path",
            paths["Career Path"].tolist(),
            index=None,
            placeholder="Choose a career path...",
        )

        if selected_path is None:
            st.stop()
        path_players = matching.copy()

        path_players["Career Path"] = (
            path_players["from_league_group"]
            + " → "
            + path_players["to_league_group"]
        )

        path_players = path_players[
            path_players["Career Path"] == selected_path
        ]

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

        columns = [
            c
            for c in columns
            if c in path_players.columns
        ]

        st.dataframe(
            path_players[columns]
            .sort_values(
                [
                    "age",
                    "full_name",
                ]
            ),
            hide_index=True,
            width="stretch",
            height=350,
        )

        # ----------------------------------------------------
        # NEU: HIER WURDEN DIE NEUEN SCHRITTE EINGEFÜGT
        # ----------------------------------------------------
        st.divider()

        selected_player = st.selectbox(
            "Explore Player",
            sorted(path_players["full_name"].unique())
        )

        player = path_players[
            path_players["full_name"] == selected_player
        ]

        st.subheader("Player Details")
        p_c1, p_c2, p_c3 = st.columns(3)

        p_c1.metric(
            "Nationality",
            player["nationality"].iloc[0]
        )
        p_c2.metric(
            "Position",
            player["position_group"].iloc[0]
        )
        p_c3.metric(
            "Agent",
            player["agent"].iloc[0]
        )

        st.dataframe(
            player[
                [
                    "season",
                    "from_club_name",
                    "to_club_name",
                    "from_league_group",
                    "to_league_group",
                ]
            ]
            .sort_values("season"),
            hide_index=True,
            width="stretch",
        )

    st.divider()

    # ----------------------------------------------------
    # Recommended Clubs / Agents
    # ----------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏟 Recommended Clubs")
        st.dataframe(
            clubs,
            hide_index=True,
            width="stretch",
            height=300,
        )

    with col2:
        st.subheader("🤝 Recommended Agents")
        st.dataframe(
            agents,
            hide_index=True,
            width="stretch",
            height=300,
        )

    st.divider()

    # ----------------------------------------------------
    # Matching Players
    # ----------------------------------------------------
    st.subheader("👥 Matching Players")
    st.caption(
        f"{matching['player_id'].nunique():,} similar players found"
    )

    columns = [
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

    columns = [
        c
        for c in columns
        if c in matching.columns
    ]

    st.dataframe(
        matching[columns]
        .sort_values(
            [
                "age",
                "full_name",
            ]
        ),
        hide_index=True,
        width="stretch",
        height=500,
    )

# --------------------------------------------------------
# Footer
# --------------------------------------------------------

st.divider()

st.caption(
    "FootballAbroad • Career Navigator v2"
)
