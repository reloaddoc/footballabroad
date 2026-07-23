import streamlit as st

from analytics_ui import (
    apply_equal_filter,
    select_filter,
)


def render_player_profile(master):

    with st.container(border=True):

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

        c3, c4 = st.columns(2)

        with c3:

            nationality = select_filter(
                "Nationality",
                master["primary_nationality"],
            )

        with c4:

            ages = master["age"].dropna()

            age_range = st.slider(
                "Age",
                int(ages.min()),
                int(ages.max()),
                (20, 25),
            )

    return {
        "country": current_country,
        "league": current_league,
        "nationality": nationality,
        "age_range": age_range,
    }
