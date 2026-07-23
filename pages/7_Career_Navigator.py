from components.player_profile import render_player_profile
import pandas as pd
import streamlit as st

from analytics_ui import (
    apply_equal_filter,
    calculate_destination_statistics,
    load_table,
    metric_row,
    page_header,
)

# ============================================================
# PAGE HEADER
# ============================================================

page_header(
    "Where should I move next?",
    "Explore historical international career paths of comparable players.",
)

# ============================================================
# LOAD DATA & OPTA SCORES
# ============================================================

master = load_table("master_dataset")
mapping = load_table("league_mapping")

# AttachOpta scores if from_score/to_score columns are missing
if "from_score" not in master.columns and "league_quality_change" not in master.columns:
    mapping["opta_score"] = pd.to_numeric(
        mapping["opta_score"], errors="coerce")
    by_code = (
        mapping[["competition_code", "opta_score"]]
        .dropna(subset=["competition_code"])
        .drop_duplicates(subset="competition_code")
    )
    by_league = (
        mapping[["our_league", "opta_score"]]
        .dropna(subset=["our_league"])
        .drop_duplicates(subset="our_league")
    )

    master = master.merge(
        by_code,
        left_on="from_league_code",
        right_on="competition_code",
        how="left",
    ).rename(columns={"opta_score": "from_score"}).drop(columns="competition_code", errors="ignore")

    master = master.merge(
        by_code,
        left_on="to_league_code",
        right_on="competition_code",
        how="left",
    ).rename(columns={"opta_score": "to_score"}).drop(columns="competition_code", errors="ignore")

    master = master.merge(
        by_league,
        left_on="from_aggregation",
        right_on="our_league",
        how="left",
    ).rename(columns={"opta_score": "from_score_by_name"}).drop(columns="our_league", errors="ignore")

    master = master.merge(
        by_league,
        left_on="to_aggregation",
        right_on="our_league",
        how="left",
    ).rename(columns={"opta_score": "to_score_by_name"}).drop(columns="our_league", errors="ignore")

    master["from_score"] = master["from_score"].fillna(
        master["from_score_by_name"])
    master["to_score"] = master["to_score"].fillna(master["to_score_by_name"])
    master = master.drop(
        columns=["from_score_by_name", "to_score_by_name"], errors="ignore")

# Global exclusion of unwanted leagues
master = master[
    (master["from_aggregation"] != "DFB-Nachwuchsliga") &
    (master["to_aggregation"] != "DFB-Nachwuchsliga")
]

# ============================================================
# PLAYER PROFILE
# ============================================================

profile = render_player_profile(master)

# ============================================================
# COMPARABLE PLAYERS
# ============================================================

matches = master.copy()

matches = apply_equal_filter(
    matches,
    "from_country_name",
    profile["country"],
)

matches = apply_equal_filter(
    matches,
    "from_aggregation",
    profile["league"],
)

matches = apply_equal_filter(
    matches,
    "primary_nationality",
    profile["nationality"],
)

matches = matches[
    matches["age"].between(
        profile["age_range"][0],
        profile["age_range"][1],
    )
]

matches = matches[matches["to_country_name"].notna()]
matches = matches[matches["to_aggregation"].notna()]

# ============================================================
# OVERVIEW
# ============================================================

confidence = (
    "High"
    if matches["player_id"].nunique() >= 50
    else "Medium"
    if matches["player_id"].nunique() >= 15
    else "Low"
)

metric_row(
    [
        (
            "Comparable players",
            matches["player_id"].nunique(),
        ),
        (
            "Confidence",
            confidence,
        ),
    ]
)

if matches.empty:
    st.info("No comparable historical careers match this profile.")
    st.stop()

# ============================================================
# HISTORICAL DESTINATIONS WITH STATS
# ============================================================

st.subheader("Where did they go?")

filter_col1, filter_col2 = st.columns([3, 1])

with filter_col1:
    st.caption("Historical destinations of comparable players.")

with filter_col2:
    international_only = st.toggle("International only", value=False)

destination_list = []

# Group by target country & league, then calculate metrics using analytics_ui helper
for (country, league), group in matches.groupby(["to_country_name", "to_aggregation"]):
    stats = calculate_destination_statistics(group)

    destination_list.append({
        "to_country_name": country,
        "to_aggregation": league,
        "players": group["player_id"].nunique(),
        "transfers": len(group),
        "moved_up": stats["moved_up"],
        "stayed_level": stats["stayed_level"],
        "moved_down": stats["moved_down"],
        "stayed_6m": stats["stayed_6m"],
        "group_data": group
    })

destinations_df = pd.DataFrame(destination_list).sort_values(
    ["players", "transfers"], ascending=False
)

# Apply International Only toggle filter
if international_only and profile.get("country") and profile["country"] != "All":
    destinations_df = destinations_df[
        destinations_df["to_country_name"] != profile["country"]
    ]

destination_rows = destinations_df.to_dict("records")

# ============================================================
# RENDER DESTINATION CARDS
# ============================================================

if not destination_rows:
    st.info("No destinations match the selected filters.")
else:
    TOP_N = 5
    top_destinations = destination_rows[:TOP_N]
    other_destinations = destination_rows[TOP_N:]

    def render_card(row):
        country = row["to_country_name"]
        league = row["to_aggregation"]
        players = row["players"]
        transfers = row["transfers"]

        moved_up = row["moved_up"]
        stayed_level = row["stayed_level"]
        moved_down = row["moved_down"]

        with st.container(border=True):
            c1, c2 = st.columns([4, 1.2])

            with c1:
                st.markdown(f"### {country}\n**{league}**")
                st.caption(
                    f"👥 `{players}` players · 🔄 `{transfers}` transfers")

                # 📊 League Progression Stats Bar
                st.markdown(
                    f"📈 **Level Up:** `{moved_up}%` &nbsp;·&nbsp; "
                    f"➡️ **Same:** `{stayed_level}%` &nbsp;·&nbsp; "
                    f"📉 **Level Down:** `{moved_down}%`"
                )

            with c2:
                if st.button(
                    "Explore",
                    key=f"btn_{country}_{league}",
                    use_container_width=True,
                ):
                    st.session_state.destination_country = country
                    st.session_state.destination_league = league
                    st.switch_page("pages/3_Destination_Report.py")

    # Render top 5 cards directly
    for row in top_destinations:
        render_card(row)

    # Put remaining cards into an expander
    if other_destinations:
        with st.expander(f"See {len(other_destinations)} other destinations"):
            for row in other_destinations:
                render_card(row)
