import streamlit as st

from analytics_ui import (
    add_money_columns,
    add_share_columns,
    apply_equal_filter,
    intelligence_links,
    load_table,
    metric_row,
    page_header,
    select_filter,
)
from analytics.common import age_bucket, league_level_bucket


page_header(
    "What happened to players like me?",
    "Use historical player archetypes as a recommendation-style view of typical next moves.",
)

archetypes = load_table("player_archetypes")
master = load_table("master_dataset")
corridors = load_table("transfer_corridors")
stepping_clubs = load_table("stepping_clubs")

# ----------------------------------------------------------
# FILTER CONTAINER
# ----------------------------------------------------------
with st.container(border=True):
    c1, c2, c3 = st.columns(3)

    with c1:
        current_country = select_filter(
            "Current country",
            master["from_country_name"],
        )

    with c2:
        nationality = select_filter(
            "Nationality",
            master["primary_nationality"],
        )

    # Filter leagues based on selected country
    filtered = apply_equal_filter(
        master,
        "from_country_name",
        current_country,
    )

    c4, c5, c6 = st.columns(3)

    with c4:
        current_league = select_filter(
            "Current league",
            filtered["from_aggregation"],
        )

    with c5:
        age = st.number_input(
            "Age",
            min_value=14,
            max_value=45,
            value=22,
        )


# ----------------------------------------------------------
# DATA MATCHING & PROCESSING
# ----------------------------------------------------------
profile = archetypes.copy()
profile = apply_equal_filter(profile, "primary_nationality", nationality)
profile = profile[profile["age_bucket"] == age_bucket(age)]


league_levels = master[
    master["from_aggregation"].astype(str) == str(current_league)
]["from_league_level"].dropna()

if current_league != "All" and len(league_levels):
    profile = profile[
        profile["league_level"] == league_level_bucket(league_levels.iloc[0])
    ]

matches = master.copy()
matches = apply_equal_filter(matches, "primary_nationality", nationality)
matches = apply_equal_filter(matches, "from_country_name", current_country)
matches = apply_equal_filter(matches, "from_aggregation", current_league)
matches = matches[matches["age"].between(age - 2, age + 2)]

# ----------------------------------------------------------
# UI OUTPUT & METRICS
# ----------------------------------------------------------
metric_row([
    ("Similar transfers", len(matches)),
    ("Similar players", matches["player_id"].nunique()),
    ("Archetypes", len(profile)),
])

st.subheader("Historically similar players usually move to")
if matches.empty:
    st.info(
        "No close historical matches yet. Broaden one input to increase confidence."
    )
else:
    next_leagues = (
        matches["to_league"]
        .dropna()
        .value_counts(normalize=True)
        .head(5)
        .rename_axis("Move to")
        .reset_index(name="Historical probability")
    )
    next_leagues["Historical probability"] = next_leagues[
        "Historical probability"
    ].apply(lambda value: f"{value * 100:.0f}%")
    st.dataframe(next_leagues, hide_index=True, use_container_width=True)

    confidence = (
        "High"
        if matches["player_id"].nunique() >= 50
        else "Medium"
        if matches["player_id"].nunique() >= 15
        else "Low"
    )
    st.success(
        f"Confidence: {confidence}, based on {matches['player_id'].nunique():,} similar players."
    )

if not profile.empty:
    st.subheader("Closest archetypes")
    display = profile.head(10)[[
        "primary_nationality",
        "age_bucket",
        "league_level",
        "number_of_players",
        "most_common_next_country",
        "most_common_next_league",
        "average_transfer_fee",
        "average_age",
        "international_share",
    ]].copy()
    display = add_money_columns(display, ["average_transfer_fee"])
    display = add_share_columns(display, ["international_share"])
    st.dataframe(display, hide_index=True, use_container_width=True)

with st.expander("Example players"):
    cols = [
        "full_name",
        "age",
        "primary_nationality",
        "from_club_name",
        "from_league",
        "to_club_name",
        "to_league",
        "career_path",
    ]
    st.dataframe(
        matches[cols].drop_duplicates().head(50),
        hide_index=True,
        use_container_width=True,
    )

with st.expander("Related transfer corridors and stepping clubs"):
    related_corridors = corridors.copy()
    related_corridors = apply_equal_filter(
        related_corridors, "from_country", current_country
    )
    related_corridors = apply_equal_filter(
        related_corridors, "from_league", current_league
    )
    st.dataframe(
        related_corridors.head(10), hide_index=True, use_container_width=True
    )

    related_clubs = stepping_clubs.copy()
    related_clubs = apply_equal_filter(
        related_clubs, "country", current_country
    )
    related_clubs = apply_equal_filter(
        related_clubs, "league", current_league
    )
    st.dataframe(
        related_clubs.head(10), hide_index=True, use_container_width=True
    )

intelligence_links()
