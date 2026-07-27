import importlib

import pandas as pd
import streamlit as st

from analytics_ui import (
    add_opta_scores,
    calculate_destination_statistics,
    load_table,
    render_navigation_sidebar,
)
import components.ui as kw_ui
from utils.league_translation import is_selectable_league_name, translate_league_name

kw_ui = importlib.reload(kw_ui)
destination_card_shell = kw_ui.destination_card_shell
empty_state = kw_ui.empty_state
evidence_brief = kw_ui.evidence_brief
inject_kickways_theme = kw_ui.inject_kickways_theme
journey_steps = kw_ui.journey_steps
product_header = kw_ui.product_header
command_brief = kw_ui.command_brief
section_header = kw_ui.section_header
start_note = kw_ui.start_note
stat_row = kw_ui.stat_row


st.set_page_config(
    page_title="Kickways | Career Intelligence",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_kickways_theme()
render_navigation_sidebar()


def league_column(frame: pd.DataFrame, prefix: str) -> str:
    aggregate_column = f"{prefix}_aggregation"
    league_column_name = f"{prefix}_league"
    return aggregate_column if aggregate_column in frame.columns else league_column_name


def unique_players(frame: pd.DataFrame) -> int:
    return frame["player_id"].nunique() if "player_id" in frame.columns else len(frame)


def get_player_name(row) -> str:
    for column in ["full_name", "player_name", "name"]:
        if column in row and pd.notna(row[column]) and str(row[column]).strip():
            return str(row[column]).strip()
    return f"Player {row.get('player_id', 'Unknown')}"


def get_player_link(row):
    for column in ["player_link", "profile_url"]:
        if column in row and pd.notna(row[column]) and str(row[column]).strip():
            return str(row[column]).strip()
    return None


def format_rate(value) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "N/A"
    if numeric.is_integer():
        return f"{int(numeric)}%"
    return f"{numeric:.1f}%"


def build_destination_rows(matches: pd.DataFrame, league_col: str, full_history: pd.DataFrame) -> pd.DataFrame:
    rows = []
    grouped = matches.dropna(subset=["to_country_name", league_col]).groupby(
        ["to_country_name", league_col],
        dropna=False,
    )
    for (dest_country, dest_league), group in grouped:
        rows.append(
            {
                "to_country_name": dest_country,
                league_col: dest_league,
                "players": group["player_id"].nunique() if "player_id" in group.columns else len(group),
                "group_data": group.copy(),
                "stats": calculate_destination_statistics(group, full_history),
            }
        )
    return pd.DataFrame(rows)


def average_time_until_next_move(matches: pd.DataFrame, full_history: pd.DataFrame):
    required_columns = {"player_id", "date"}
    if matches.empty or not required_columns.issubset(matches.columns) or not required_columns.issubset(full_history.columns):
        return None

    player_ids = matches["player_id"].dropna().unique()
    history = full_history.loc[
        full_history["player_id"].isin(player_ids),
        ["player_id", "date"],
    ].copy()
    history["_source_index"] = history.index
    history["_move_date"] = pd.to_datetime(history["date"], errors="coerce")
    history = history.dropna(subset=["_move_date"]).sort_values(
        ["player_id", "_move_date", "_source_index"]
    )
    distinct_dates = history[["player_id", "_move_date"]].drop_duplicates().sort_values(
        ["player_id", "_move_date"]
    )
    distinct_dates["_next_move_date"] = distinct_dates.groupby("player_id")["_move_date"].shift(-1)
    history = history.merge(distinct_dates, on=["player_id", "_move_date"], how="left")

    next_dates = history.set_index("_source_index")["_next_move_date"].reindex(matches.index)
    move_dates = pd.to_datetime(matches["date"], errors="coerce")
    durations = (next_dates - move_dates).dt.days / 365.25
    durations = durations[durations > 0]

    return round(durations.mean(), 1) if len(durations) else None


def open_destination_dossier(country: str, league: str, destination_scope: pd.DataFrame | None = None) -> None:
    st.session_state["destination_source"] = "start"
    st.session_state.pop("career_navigator_profile", None)
    st.session_state.pop("career_navigator_destination_scope", None)
    for key in list(st.session_state.keys()):
        if key.startswith("report_origin_country_") or key.startswith("report_origin_league_"):
            st.session_state.pop(key, None)
    if destination_scope is not None and not destination_scope.empty:
        st.session_state["destination_scope"] = destination_scope.copy()
    else:
        st.session_state.pop("destination_scope", None)
    st.session_state["destination_country"] = country
    st.session_state["destination_league"] = league
    st.switch_page("pages/2_Destination_Report.py")


def render_comparable_players(group_data: pd.DataFrame, dest_key: str) -> None:
    unique_players = group_data.drop_duplicates(subset=["player_id"]).head(12)
    with st.container(border=True):
        section_header(
            "Comparable players",
            "These are examples behind the destination signal.",
        )
        for _, player in unique_players.iterrows():
            name = get_player_name(player)
            age = player.get("age", "N/A")
            nationality = player.get("primary_nationality", "N/A")
            from_league = translate_league_name(str(player.get("from_aggregation", player.get("from_league", "N/A"))))
            link = get_player_link(player)
            text_col, action_col = st.columns([2.2, 1])
            with text_col:
                st.write(f"**{name}**")
                st.caption(f"{nationality} · age {age} · from {from_league}")
            with action_col:
                if link:
                    st.link_button(
                        "Transfermarkt profile",
                        link,
                        use_container_width=False,
                    )
            st.divider()
        if len(group_data.drop_duplicates(subset=["player_id"])) > len(unique_players):
            start_note("Open destination intelligence to inspect the broader destination context.")


def render_destination_opportunity(row: pd.Series, league_col: str, key_prefix: str, primary: bool = False) -> None:
    country = row["to_country_name"]
    league = row[league_col]
    players = int(row["players"])
    share = float(row["share"])
    display_league = translate_league_name(str(league))
    stats = row.get("stats", {})
    evidence = (
        f"{players:,} comparable players moved from {st.session_state.get('user_origin_country', 'your current country')} "
        f"- {translate_league_name(str(st.session_state.get('user_origin_league', 'your current league')))} to this destination. "
        f"It represents {share:.1f}% of the observed next moves."
    )

    if destination_card_shell(
        country=country,
        league=display_league,
        evidence=evidence,
        metrics=[
            ("Comparable players", f"{players:,}"),
            ("Level up", format_rate(stats.get("moved_up"))),
            ("Same level", format_rate(stats.get("stayed_level"))),
            ("Level down", format_rate(stats.get("moved_down"))),
        ],
        primary=primary,
        action_label="View destination intelligence",
        action_key=f"{key_prefix}_{country}_{league}",
    ):
        open_destination_dossier(country, league, row.get("group_data"))

    player_key = f"players_{key_prefix}_{country}_{league}"
    if st.button(f"Show comparable players ({players})", key=player_key):
        selected_key = f"{country}_{league}"
        if st.session_state.get("selected_start_destination") == selected_key:
            st.session_state["selected_start_destination"] = None
        else:
            st.session_state["selected_start_destination"] = selected_key

    if st.session_state.get("selected_start_destination") == f"{country}_{league}":
        render_comparable_players(row.get("group_data", pd.DataFrame()), f"{key_prefix}_{country}_{league}")



if "user_origin_country" not in st.session_state:
    st.session_state["user_origin_country"] = "Germany"
if "user_origin_league" not in st.session_state:
    st.session_state["user_origin_league"] = "Verbandsliga"
if "searched" not in st.session_state:
    st.session_state["searched"] = False
if "start_international_only" not in st.session_state:
    st.session_state["start_international_only"] = False
if "user_age_range" not in st.session_state:
    st.session_state["user_age_range"] = (20, 25)
if "selected_start_destination" not in st.session_state:
    st.session_state["selected_start_destination"] = None


master_raw = load_table("master_dataset")
try:
    mapping_raw = load_table("league_mapping")
    master = add_opta_scores(master_raw, mapping_raw)
except Exception:
    master = master_raw.copy()

if {"from_aggregation", "to_aggregation"}.issubset(master.columns):
    master = master[
        (master["from_aggregation"] != "DFB-Nachwuchsliga")
        & (master["to_aggregation"] != "DFB-Nachwuchsliga")
    ].copy()

from_league_col = league_column(master, "from")
to_league_col = league_column(master, "to")
valid_origins = master.dropna(subset=["from_country_name", from_league_col]).copy()


if not st.session_state["searched"]:
    command_brief(
        "Where could your career realistically go next?",
        "Start with your current league. Kickways turns historical transfer paths into a shortlist of destinations that comparable players actually reached.",
        ["Profile", "Opportunities", "Destination intelligence"],
        "Profile",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    form_col, insight_col = st.columns([1.08, 0.92], gap="large")

    with form_col:
        with st.container(border=True):
            section_header("Current football context", "Choose the league you play in today.")
            countries = sorted(valid_origins["from_country_name"].dropna().unique())
            default_country = st.session_state.get("user_origin_country", "Germany")
            default_idx = countries.index(default_country) if default_country in countries else 0

            country = st.selectbox("Country", countries, index=default_idx)
            country_rows = valid_origins[valid_origins["from_country_name"] == country]
            leagues = sorted(
                (
                    league_name
                    for league_name in country_rows[from_league_col].dropna().astype(str).unique()
                    if is_selectable_league_name(league_name)
                ),
                key=translate_league_name,
            )
            if not leagues:
                empty_state("No selectable leagues are available for this country yet.")
                st.stop()

            default_league = st.session_state.get("user_origin_league")
            default_league_idx = leagues.index(default_league) if default_league in leagues else 0

            league = st.selectbox(
                "League",
                leagues,
                index=default_league_idx,
                format_func=translate_league_name,
            )

            age_values = country_rows["age"].dropna()
            min_age = int(age_values.min()) if len(age_values) else 15
            max_age = int(age_values.max()) if len(age_values) else 45
            default_age_range = st.session_state.get("user_age_range", (20, 25))
            default_age_range = (
                max(min_age, int(default_age_range[0])),
                min(max_age, int(default_age_range[1])),
            )
            if default_age_range[0] > default_age_range[1]:
                default_age_range = (min_age, max_age)

            age_range = st.slider(
                "Age",
                min_age,
                max_age,
                default_age_range,
            )

            start_note("Kickways compares this origin and age band with historical next moves from players in the same football context.")

            if st.button("Find realistic opportunities", use_container_width=True, type="primary"):
                st.session_state["user_origin_country"] = country
                st.session_state["user_origin_league"] = league
                st.session_state["user_age_range"] = age_range
                st.session_state["selected_start_destination"] = None
                st.session_state["searched"] = True
                st.rerun()

    with insight_col:
        with st.container(border=True):
            section_header("Career evidence", "The first result is an opportunity map, not a database search.")
            stat_row(
                [
                    ("Transfers", f"{len(master):,}"),
                    ("Players", f"{master['player_id'].nunique():,}"),
                    ("Signal", "historical next moves"),
                ]
            )
            evidence_brief(
                [
                    ("Comparable paths", "Players are grouped by their current football context before destinations are ranked."),
                    ("Career movement", "Level up, same level, and level down describe the next move after a destination."),
                    ("Decision page", "Each destination opens a report with comparable players, clubs, agencies, and next moves."),
                ]
            )

else:
    country = st.session_state["user_origin_country"]
    league = st.session_state["user_origin_league"]
    age_range = st.session_state.get("user_age_range", (20, 25))
    display_league = translate_league_name(str(league))

    origin_matches = master[
        (master["from_country_name"] == country)
        & (master[from_league_col].astype(str) == str(league))
    ].copy()
    if "age" in origin_matches.columns:
        origin_matches = origin_matches[
            origin_matches["age"].between(age_range[0], age_range[1])
        ].copy()

    back_col, filter_col = st.columns([1, 4])
    with back_col:
        if st.button("Start over", use_container_width=False):
            st.session_state["searched"] = False
            st.rerun()
    with filter_col:
        international_only = st.toggle("International opportunities only", key="start_international_only")

    if international_only:
        matches = origin_matches[
            origin_matches["to_country_name"].notna()
            & (origin_matches["to_country_name"] != country)
        ].copy()
    else:
        matches = origin_matches.copy()

    total_careers = unique_players(matches)
    avg_age = round(matches["age"].mean(), 1) if "age" in matches.columns and not matches.empty else "N/A"
    avg_next_move = average_time_until_next_move(matches, master)

    product_header(
        f"Opportunities from {country} - {display_league}",
        "These destinations are ranked by how often comparable players actually moved there.",
        eyebrow="Career opportunities",
    )
    journey_steps("Opportunities")
    stat_row(
        [
            ("Comparable careers", f"{total_careers:,}"),
            ("Age band", f"{age_range[0]}-{age_range[1]}"),
            ("Average age", str(avg_age)),
            ("Typical next move", f"{avg_next_move} seasons" if avg_next_move is not None else "N/A"),
        ]
    )

    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Recommended destinations", "Start with the strongest historical signal, then inspect the destination intelligence.")

    dest_counts = pd.DataFrame(columns=["to_country_name", to_league_col, "players", "share"])
    if matches.empty:
        empty_state("No comparable career paths are available for this origin yet. Try another current league or turn off the international-only filter.")
    else:
        dest_counts = build_destination_rows(matches, to_league_col, master)
        if dest_counts.empty:
            empty_state("No recorded destination leagues are available for this origin yet.")
        else:
            dest_counts["share"] = (dest_counts["players"] / max(total_careers, 1) * 100).round(1)
            dest_counts = dest_counts.sort_values(["players", "share"], ascending=False)

            top_destinations = dest_counts.head(6)
            other_destinations = dest_counts.iloc[6:]

            for idx, (_, row) in enumerate(top_destinations.iterrows()):
                render_destination_opportunity(row, to_league_col, f"start_top_{idx}", primary=idx == 0)

            if not other_destinations.empty:
                with st.expander(f"Show {len(other_destinations)} more destinations"):
                    for idx, (_, row) in enumerate(other_destinations.iterrows()):
                        render_destination_opportunity(row, to_league_col, f"start_more_{idx}")
