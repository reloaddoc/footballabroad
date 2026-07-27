import re

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Career Navigator | Kickways",
    page_icon="⚽",
    layout="wide",
)

from components.player_profile import render_player_profile
from components.ui import (
    command_brief,
    destination_card_shell,
    empty_state,
    inject_kickways_theme,
    section_header,
    start_note,
    stat_row,
)

from analytics_ui import (
    add_opta_scores,
    apply_equal_filter,
    calculate_destination_statistics,
    load_table,
    render_navigation_sidebar,
)
from utils.league_translation import translate_league_name

# MUST BE THE FIRST STREAMLIT COMMAND ON THE PAGE
# st.set_page_config(
#    page_title="Career Navigator | Kickways",
#    page_icon="⚽",
#    layout="wide"  # <--- THIS ENABLES FULL SCREEN WIDTH
# )

inject_kickways_theme()
render_navigation_sidebar()
command_brief(
    "Build a player profile. Inspect real career paths.",
    "Tune the current context, then compare destinations reached by similar players and open the exact careers behind each signal.",
    ["Profile", "Opportunities", "Players"],
    "Profile",
)

# ============================================================
# SESSION STATE FOR INTERACTIVE DRILL-DOWN
# ============================================================
if "selected_destination" not in st.session_state:
    st.session_state["selected_destination"] = None

if "selected_player" not in st.session_state:
    st.session_state["selected_player"] = None

if "selected_player_key" not in st.session_state:
    st.session_state["selected_player_key"] = None

# ============================================================
# LOAD DATA & OPTA SCORES
# ============================================================

master = add_opta_scores(load_table("master_dataset"), load_table("league_mapping"))

# Global exclusion of unwanted leagues
master = master[
    (master["from_aggregation"] != "DFB-Nachwuchsliga") &
    (master["to_aggregation"] != "DFB-Nachwuchsliga")
]

# Helper function to reliably get player display name


def get_player_name(row):
    for col in ["full_name", "player_name", "name"]:
        if col in row and pd.notna(row[col]) and str(row[col]).strip() != "":
            return str(row[col]).strip()
    return f"Player {row.get('player_id', 'Unknown')}"


def get_player_key(player_id) -> str:
    if pd.isna(player_id):
        return ""
    return str(player_id)


def derive_transfermarkt_profile_url(relative_url):
    if pd.isna(relative_url):
        return None

    url = str(relative_url).strip()
    if not url:
        return None

    path = re.sub(r"^https?://(?:www\.)?transfermarkt\.[^/]+", "", url)
    profile_path = re.sub(
        r"/transfers/spieler/([0-9]+)(?:/transfer_id/[0-9]+)?",
        r"/profil/spieler/\1",
        path,
    )

    if profile_path == path and "/profil/spieler/" not in profile_path:
        return None

    return f"https://www.transfermarkt.com{profile_path}"


def render_player_summary_card(player_row):
    display_name = get_player_name(player_row)
    player_url = (
        player_row.get("player_link")
        or player_row.get("profile_url")
        or derive_transfermarkt_profile_url(player_row.get("relative_url"))
    )

    with st.container(border=True):
        st.subheader(display_name)
        st.write(f"**Nationality:** {player_row.get('primary_nationality', 'N/A')}")
        st.write(f"**Age:** {player_row.get('age', 'N/A')}")
        if player_url:
            st.link_button(
                "Open player profile on Transfermarkt",
                player_url,
                use_container_width=False,
            )


def format_rate(value) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "N/A"
    if numeric.is_integer():
        return f"{int(numeric)}%"
    return f"{numeric:.1f}%"


def profile_label(profile):
    parts = []
    if profile.get("country") and profile["country"] != "All":
        parts.append(str(profile["country"]))
    if profile.get("league") and profile["league"] != "All":
        parts.append(translate_league_name(str(profile["league"])))
    age_range = profile.get("age_range")
    if age_range:
        parts.append(f"age {age_range[0]}-{age_range[1]}")
    return " · ".join(parts) if parts else "broad player profile"


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

matches = matches[
    matches["age"].between(
        profile["age_range"][0],
        profile["age_range"][1],
    )
]

matches = matches[matches["to_country_name"].notna()]
matches = matches[matches["to_aggregation"].notna()]

# ============================================================
# OVERVIEW METRICS
# ============================================================

confidence = (
    "High"
    if matches["player_id"].nunique() >= 50
    else "Medium"
    if matches["player_id"].nunique() >= 15
    else "Low"
)

if matches.empty:
    empty_state("No comparable historical careers match this profile. Broaden the profile or choose another current league.")
    st.stop()

# ============================================================
# HISTORICAL DESTINATIONS WITH STATS
# ============================================================

section_header(
    "Opportunity desk",
    "Destinations are ranked by comparable players. Open a destination or inspect the player careers behind it.",
)
desk_stat_col, desk_toggle_col = st.columns([2.4, 1])
with desk_stat_col:
    stat_row(
        [
            ("Comparable players", f"{matches['player_id'].nunique():,}"),
            ("Profile", profile_label(profile)),
            ("Evidence strength", confidence),
        ]
    )
with desk_toggle_col:
    international_only = st.toggle("International only", value=False)
    start_note("Hide domestic moves when you only want foreign markets.")

destination_list = []

for (country, league), group in matches.groupby(["to_country_name", "to_aggregation"]):
    stats = calculate_destination_statistics(group, master)

    destination_list.append({
        "to_country_name": country,
        "to_aggregation": league,
        "players": group["player_id"].nunique(),
        "transfers": len(group),
        "moved_up": stats["moved_up"],
        "stayed_level": stats["stayed_level"],
        "moved_down": stats["moved_down"],
        "country_retention": stats["country_retention"],
        "exit_abroad": stats["exit_abroad"],
        "group_data": group
    })

destinations_df = pd.DataFrame(destination_list).sort_values(
    ["players", "transfers"], ascending=False
)

if international_only and profile.get("country") and profile["country"] != "All":
    destinations_df = destinations_df[
        destinations_df["to_country_name"] != profile["country"]
    ]

destination_rows = destinations_df.to_dict("records")

# ============================================================
# RENDER DESTINATIONS & CAREER INSPECTOR
# ============================================================

if not destination_rows:
    empty_state("No destinations match the selected filters. Turn off international-only or broaden the profile.")
else:
    col_left, col_right = st.columns([1.65, 0.95], gap="large")

    with col_left:
        TOP_N = 20
        top_destinations = destination_rows[:TOP_N]
        other_destinations = destination_rows[TOP_N:]

        def render_card(row):
            country = row["to_country_name"]
            league = row["to_aggregation"]
            display_league = translate_league_name(str(league))
            players = row["players"]
            transfers = row["transfers"]
            origin_label = profile_label(profile)

            moved_up = row["moved_up"]
            stayed_level = row["stayed_level"]
            moved_down = row["moved_down"]

            dest_key = f"{country}_{league}"

            if destination_card_shell(
                country=country,
                league=display_league,
                evidence=f"{players:,} comparable players moved from {origin_label} to this destination across {transfers:,} recorded transfers.",
                metrics=[
                    ("Players", f"{players:,}"),
                    ("Transfers", f"{transfers:,}"),
                    ("Level up", format_rate(moved_up)),
                    ("Same", format_rate(stayed_level)),
                    ("Level down", format_rate(moved_down)),
                ],
                action_label="Open destination intelligence",
                action_key=f"btn_exp_{country}_{league}",
            ):
                for state_key in list(st.session_state.keys()):
                    if state_key.startswith("report_origin_country_") or state_key.startswith("report_origin_league_"):
                        st.session_state.pop(state_key, None)
                st.session_state["destination_source"] = "career_navigator"
                st.session_state["career_navigator_profile"] = profile
                st.session_state["career_navigator_destination_scope"] = row["group_data"].copy()
                st.session_state["destination_scope"] = row["group_data"].copy()
                st.session_state.destination_country = country
                st.session_state.destination_league = league
                st.switch_page("pages/2_Destination_Report.py")

            if st.button(f"Show comparable players ({players})", key=f"nav_btn_{dest_key}"):
                if st.session_state["selected_destination"] == dest_key:
                    st.session_state["selected_destination"] = None
                else:
                    st.session_state["selected_destination"] = dest_key
                    st.session_state["selected_player"] = None
                    st.session_state["selected_player_key"] = None

            if st.session_state["selected_destination"] == dest_key:
                with st.container(border=True):
                    section_header(
                        "Comparable players",
                        f"Players from this cohort who moved to {display_league}.",
                    )

                    group_data = row["group_data"]
                    unique_players = group_data.drop_duplicates(
                        subset=["player_id"])

                    for _, p in unique_players.iterrows():
                        p_name = get_player_name(p)
                        p_id = p["player_id"]
                        p_key = get_player_key(p_id)
                        p_nat = p.get("primary_nationality", "")
                        from_l = p.get("from_aggregation",
                                       p.get("from_league", "N/A"))

                        pc1, pc2 = st.columns([2, 1])
                        with pc1:
                            # CLICKABLE PLAYER NAME BUTTON
                            if st.button(p_name, key=f"nav_p_{p_id}_{dest_key}"):
                                st.session_state["selected_player"] = p_id
                                st.session_state["selected_player_key"] = p_key

                            st.caption(f"{p_nat} | From: {from_l}")

                        with pc2:
                            st.markdown("`Match 90%+`")

                        if st.session_state["selected_player_key"] == p_key:
                            render_player_summary_card(p)

                        st.divider()

        # Render top destinations
        for row in top_destinations:
            render_card(row)

        if other_destinations:
            with st.expander(f"Expand all leagues ({len(other_destinations)} more)"):
                for row in other_destinations:
                    render_card(row)

    with col_right:
        with st.container(border=True):
            section_header(
                "Player inspector",
                "Select a comparable player to open their profile and Transfermarkt link.",
            )

            if st.session_state["selected_player"]:
                selected_pid = st.session_state["selected_player"]
                selected_key = (
                    st.session_state["selected_player_key"]
                    or get_player_key(selected_pid)
                )

                # Fetch career history for the selected player
                p_history = master[master["player_id"].apply(get_player_key) == selected_key]

                if not p_history.empty:
                    p_first = p_history.iloc[0]
                    render_player_summary_card(p_first)
                else:
                    empty_state("Player profile details were not found in the master dataset.")
            else:
                start_note("Open a destination's comparable-player list, then choose a player here.")
