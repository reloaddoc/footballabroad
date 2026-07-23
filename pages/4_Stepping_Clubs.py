import streamlit as st

from analytics_ui import (
    add_money_columns,
    apply_equal_filter,
    intelligence_links,
    load_table,
    metric_row,
    page_header,
    select_filter,
)

page_header(
    "Which clubs consistently export players?",
    "Identify gateway clubs and the destination markets they connect to.",
)

clubs = load_table("club_export_corridors")

master = load_table("master_dataset")


with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        country = select_filter("Club country", clubs["country"])

    filtered = apply_equal_filter(clubs, "country", country)

    with c2:
        league = select_filter("Club league", filtered["league"])

    filtered = apply_equal_filter(filtered, "league", league)

    with c3:
        destination_country = select_filter(
            "Destination country",
            filtered["destination_country"],
        )

    filtered = apply_equal_filter(
        filtered,
        "destination_country",
        destination_country,
    )

    with c4:
        destination_league = select_filter(
            "Destination league",
            filtered["destination_league"],
        )

filtered = apply_equal_filter(
    filtered,
    "destination_league",
    destination_league,
)

metric_row(
    [
        ("Club corridors", len(filtered)),
        (
            "Transfers",
            int(filtered["transfers"].sum()) if not filtered.empty else 0,
        ),
        (
            "Unique players",
            int(filtered["unique_players"].sum()) if not filtered.empty else 0,
        ),
    ]
)

st.subheader("Key insight")

if filtered.empty:
    st.info("No club export corridors match these filters.")
else:
    top = filtered.sort_values("transfers", ascending=False).iloc[0]

    st.success(
        f"{top['club']} exported "
        f"{int(top['transfers'])} players "
        f"from {top['league']} to "
        f"{top['destination_league']} ({top['destination_country']})."
    )

display = filtered[
    [
        "club",
        "country",
        "league",
        "destination_country",
        "destination_league",
        "transfers",
        "unique_players",
        "average_age_departure",
        "average_market_value_departure",
        "top_destination_club",
    ]
].copy()

display = add_money_columns(
    display,
    ["average_market_value_departure"],
)

display = display.rename(
    columns={
        "club": "Club",
        "country": "Country",
        "league": "League",
        "destination_country": "Destination country",
        "destination_league": "Destination league",
        "transfers": "Transfers",
        "unique_players": "Players",
        "average_age_departure": "Avg. age",
        "average_market_value_departure": "Avg. market value",
        "top_destination_club": "Example destination club",
    }
)

st.subheader("Export corridors")

st.dataframe(
    display,
    hide_index=True,
    use_container_width=True,
)

if not filtered.empty:

    selected_club = st.selectbox(
        "Inspect a club",
        sorted(filtered["club"].dropna().unique()),
    )

    club_examples = master[
        (master["from_club_name"] == selected_club)
    ]

    if destination_country != "All":
        club_examples = club_examples[
            club_examples["to_country_name"] == destination_country
        ]

    if destination_league != "All":
        club_examples = club_examples[
            club_examples["to_aggregation"] == destination_league
        ]

    st.subheader("Career examples")

    cols = [
        "full_name",
        "age",
        "position",
        "from_aggregation",
        "to_country_name",
        "to_aggregation",
        "to_club_name",
        "agent",
    ]

    rename = {
        "full_name": "Player",
        "age": "Age",
        "position": "Position",
        "from_aggregation": "From league",
        "to_country_name": "Destination country",
        "to_aggregation": "Destination league",
        "to_club_name": "Destination club",
        "agent": "Agent",
    }

    st.dataframe(
        club_examples[cols]
        .rename(columns=rename)
        .head(100),
        hide_index=True,
        use_container_width=True,
    )

intelligence_links()
