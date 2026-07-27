import re

import pandas as pd
import streamlit as st

# 1. Page Config
st.set_page_config(
    page_title="Career Navigator | Kickways",
    page_icon="⚽",
    layout="wide",
)

# 2. Add the CSS right here!
st.markdown(
    """
    <style>
        /* Expand Streamlit container width */
        .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 95% !important;
        }
        
        /* Prevent metrics inside buttons/badges from wrapping onto 2 lines */
        div[data-testid="stHorizontalBlock"] {
            align-items: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
from components.player_profile import render_player_profile
from components.ui import (
    destination_card_shell,
    inject_kickways_theme,
    journey_steps,
    product_header,
    section_header,
    stat_row,
)

from analytics_ui import (
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
product_header(
    "Find the next move that matches your profile",
    "Compare your current context with historical player careers and inspect realistic international opportunities.",
    eyebrow="Opportunity explorer",
)
journey_steps("Profile")

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

master = load_table("master_dataset")
mapping = load_table("league_mapping")

# Attach Opta scores if from_score/to_score columns are missing
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
# OVERVIEW METRICS
# ============================================================

confidence = (
    "High"
    if matches["player_id"].nunique() >= 50
    else "Medium"
    if matches["player_id"].nunique() >= 15
    else "Low"
)

stat_row(
    [
        ("Comparable players", f"{matches['player_id'].nunique():,}"),
        ("Evidence strength", confidence),
    ]
)

if matches.empty:
    st.info("No comparable historical careers match this profile.")
    st.stop()

# ============================================================
# HISTORICAL DESTINATIONS WITH STATS
# ============================================================

section_header(
    "Career opportunities",
    "Destinations are ranked by comparable players who made this move.",
)

# Option A: Place the caption and toggle directly inside a container aligned with the destination card width
# Matches your col_left / col_right ratio
hdr_left, hdr_right = st.columns([2.0, 1.0])

with hdr_left:
    # Split the left section into text on the left, toggle on the right
    c_text, c_toggle = st.columns([1.5, 1])
    with c_text:
        st.caption("Historical destinations of comparable players.")
    with c_toggle:
        international_only = st.toggle("International only", value=False)

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
    st.info("No destinations match the selected filters.")
else:
    # 2-column layout: Left for Destinations, Right for Player Inspector
    col_left, col_right = st.columns([2.0, 1.0])

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
            origin_context = []
            if profile.get("country") and profile["country"] != "All":
                origin_context.append(str(profile["country"]))
            if profile.get("league") and profile["league"] != "All":
                origin_context.append(translate_league_name(str(profile["league"])))
            origin_label = " · ".join(origin_context) if origin_context else "your selected profile"

            moved_up = row["moved_up"]
            stayed_level = row["stayed_level"]
            moved_down = row["moved_down"]

            dest_key = f"{country}_{league}"

            with st.container(border=True):
                c1, c2 = st.columns([3.5, 1.2])

                with c1:
                    destination_card_shell(
                        country=country,
                        league=display_league,
                        evidence=f"{players:,} comparable players moved from {origin_label} to this destination across {transfers:,} recorded transfers.",
                        metrics=[
                            ("Level up", f"{moved_up}%"),
                            ("Same level", f"{stayed_level}%"),
                            ("Level down", f"{moved_down}%"),
                        ],
                    )

                    # CLICKABLE PLAYER COUNT BUTTON
                    btn_col, info_col = st.columns([1.5, 2])
                    with btn_col:
                        if st.button(f"👥 {players} players ▸", key=f"nav_btn_{dest_key}"):
                            if st.session_state["selected_destination"] == dest_key:
                                st.session_state["selected_destination"] = None
                            else:
                                st.session_state["selected_destination"] = dest_key
                                st.session_state["selected_player"] = None
                                st.session_state["selected_player_key"] = None

                    with info_col:
                        st.caption(f"🔄 `{transfers}` total transfers")

                    # League Progression Bar
                    st.markdown(
                        f"📈 **Level Up:** `{moved_up}%` &nbsp;·&nbsp; "
                        f"➡️ **Same:** `{stayed_level}%` &nbsp;·&nbsp; "
                        f"📉 **Level Down:** `{moved_down}%`"
                    )

                with c2:
                    if st.button(
                        "Show league/country dossier",
                        key=f"btn_exp_{country}_{league}",
                        use_container_width=True,
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

                # EXPANDER / DRILL-DOWN WHEN CLICKED
                if st.session_state["selected_destination"] == dest_key:
                    st.info(
                        f"Showing comparable players who moved to **{display_league}**:")

                    group_data = row["group_data"]
                    unique_players = group_data.drop_duplicates(
                        subset=["player_id"])

                    for _, p in unique_players.iterrows():
                        p_name = get_player_name(p)
                        p_id = p["player_id"]
                        p_key = get_player_key(p_id)
                        p_pos = p.get("position_group",
                                      p.get("position", "N/A"))
                        p_nat = p.get("primary_nationality", "")
                        from_l = p.get("from_aggregation",
                                       p.get("from_league", "N/A"))

                        pc1, pc2 = st.columns([2, 1])
                        with pc1:
                            # CLICKABLE PLAYER NAME BUTTON
                            if st.button(f"👤 {p_name}", key=f"nav_p_{p_id}_{dest_key}"):
                                st.session_state["selected_player"] = p_id
                                st.session_state["selected_player_key"] = p_key

                            st.caption(f"{p_nat} | From: {from_l}")

                        with pc2:
                            st.markdown("`Match 90%+`")

                        if st.session_state["selected_player_key"] == p_key:
                            render_player_summary_card(p)

                        st.markdown("<hr style='margin: 4px 0;'>",
                                    unsafe_allow_html=True)

        # Render top destinations
        for row in top_destinations:
            render_card(row)

        if other_destinations:
            with st.expander(f"Expand all leagues ({len(other_destinations)} more)"):
                for row in other_destinations:
                    render_card(row)

    with col_right:
        st.subheader("👤 Player Career Inspector")

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
                st.error("Player profile details not found in master dataset.")
        else:
            st.caption(
                "👈 Click on a player's name on the left to inspect their full career path here.")
