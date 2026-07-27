import streamlit as st

from analytics_ui import (
    apply_equal_filter,
    select_filter,
)
from components.ui import section_header, start_note


def render_player_profile(master):

    with st.container(border=True):
        section_header(
            "Profile workbench",
            "Define the player context Kickways should compare against historical career paths.",
        )

        c1, c2 = st.columns(2)

        with c1:

            current_country = select_filter(
                "Current country",
                master["from_country_name"],
            )

        country_players = apply_equal_filter(
            master,
            "from_country_name",
            current_country,
        )

        with c2:

            current_league = select_filter(
                "Current league",
                country_players["from_aggregation"],
            )

        ages = master["age"].dropna()

        age_range = st.slider(
            "Age",
            int(ages.min()),
            int(ages.max()),
            (20, 25),
        )

        start_note(
            "Use a broad profile to discover more markets, or narrow it when you want stronger comparables."
        )

    return {
        "country": current_country,
        "league": current_league,
        "age_range": age_range,
    }
