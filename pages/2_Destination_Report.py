from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Career Navigator | Kickways",
    page_icon="⚽",
    layout="wide",  # <--- THIS STRETCHES THE APP FULL WIDTH
)

from analytics_ui import (
    add_opta_scores,
    calculate_destination_statistics,
    load_table,
    render_navigation_sidebar,
)
from components.ui import (
    inject_kickways_theme,
    journey_steps,
    product_header,
    section_header,
    stat_row,
)
from services.destination_service import load_knowledge
from utils.league_translation import is_selectable_league_name, translate_league_name

inject_kickways_theme()
render_navigation_sidebar()


def league_column(frame: pd.DataFrame, prefix: str) -> str:
    aggregate_column = f"{prefix}_aggregation"
    league_column_name = f"{prefix}_league"
    return aggregate_column if aggregate_column in frame.columns else league_column_name


def player_count(frame: pd.DataFrame) -> int:
    return frame["player_id"].nunique() if "player_id" in frame.columns else len(frame)


def format_percent(value) -> str:
    return f"{float(value):.0f}%" if pd.notna(value) else "-"


def player_name(row) -> str:
    if hasattr(row, "get"):
        return row.get("full_name") or row.get("player_name") or str(row.get("player_id", "Unknown"))
    return "Unknown"


def next_transfer_rows(scope: pd.DataFrame, full_history: pd.DataFrame) -> pd.DataFrame:
    required = {"player_id", "date", "to_country_name"}
    if scope.empty or not required.issubset(scope.columns) or not required.issubset(full_history.columns):
        return pd.DataFrame()

    history = full_history[full_history["player_id"].isin(
        scope["player_id"].dropna().unique())].copy()
    history["date"] = pd.to_datetime(history["date"], errors="coerce")
    scope_keys = scope[["player_id", "date"]].copy()
    scope_keys["date"] = pd.to_datetime(scope_keys["date"], errors="coerce")

    history = history.sort_values(["player_id", "date"])
    shifted = history.groupby("player_id").shift(-1)
    next_rows = history[["player_id", "date"]].copy()
    for column in [
        "to_country_name",
        "to_aggregation",
        "to_league",
        "to_club_name",
        "agent",
    ]:
        if column in shifted.columns:
            next_rows[f"next_{column}"] = shifted[column]

    return scope_keys.merge(next_rows, on=["player_id", "date"], how="left").dropna(
        subset=["next_to_country_name"]
    )


def average_next_move_seasons(scope: pd.DataFrame, full_history: pd.DataFrame):
    if scope.empty or not {"player_id", "date"}.issubset(scope.columns):
        return None

    history = full_history[full_history["player_id"].isin(
        scope["player_id"].dropna().unique())].copy()
    history["date"] = pd.to_datetime(history["date"], errors="coerce")
    history = history.sort_values(["player_id", "date"])
    history["next_date"] = history.groupby("player_id")["date"].shift(-1)

    scope_dates = scope[["player_id", "date"]].copy()
    scope_dates["date"] = pd.to_datetime(scope_dates["date"], errors="coerce")
    matched = scope_dates.merge(history[["player_id", "date", "next_date"]], on=[
                                "player_id", "date"], how="left")
    durations = (matched["next_date"] - matched["date"]
                 ).dt.days.dropna() / 365.25

    return round(durations.mean(), 1) if len(durations) else None


def google_url(query: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(query)}"


def google_images_url(query: str) -> str:
    return f"https://www.google.com/search?udm=2&q={quote_plus(query)}"


def valid_destination_value(value) -> bool:
    invalid_values = {"without a club", "nan", "without a club (nan)", "none", ""}
    return pd.notna(value) and str(value).strip().lower() not in invalid_values


def filter_valid_next_destinations(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame

    valid = frame["next_to_country_name"].apply(valid_destination_value)
    if "next_to_aggregation" in frame.columns:
        valid &= frame["next_to_aggregation"].apply(valid_destination_value)
    return frame[valid].copy()


def exact_destination_scope(scope, country: str, league: str, to_league_col: str) -> pd.DataFrame:
    if not isinstance(scope, pd.DataFrame) or scope.empty:
        return pd.DataFrame()

    if "to_country_name" not in scope.columns or to_league_col not in scope.columns:
        return pd.DataFrame()

    result = scope[scope["to_country_name"] == country].copy()
    if league:
        result = result[result[to_league_col].astype(str) == str(league)].copy()

    return result


def apply_navigator_profile(frame: pd.DataFrame, profile: dict, from_league_col: str) -> pd.DataFrame:
    result = frame.copy()

    country = profile.get("country")
    if country and country != "All":
        result = result[result["from_country_name"] == country].copy()

    league = profile.get("league")
    if league and league != "All":
        result = result[result[from_league_col].astype(str) == str(league)].copy()

    nationality = profile.get("nationality")
    if nationality and nationality != "All":
        result = result[result["primary_nationality"] == nationality].copy()

    age_range = profile.get("age_range")
    if age_range and "age" in result.columns:
        result = result[result["age"].between(age_range[0], age_range[1])].copy()

    return result


def navigator_profile_label(profile: dict) -> str:
    parts = []
    country = profile.get("country")
    league = profile.get("league")
    nationality = profile.get("nationality")
    age_range = profile.get("age_range")

    if country and country != "All":
        parts.append(str(country))
    if league and league != "All":
        parts.append(translate_league_name(str(league)))
    if nationality and nationality != "All":
        parts.append(str(nationality))
    if age_range:
        parts.append(f"age {age_range[0]}-{age_range[1]}")

    return " · ".join(parts) if parts else "your selected profile"


def scope_origin_label(scope: pd.DataFrame, from_league_col: str) -> str:
    if not isinstance(scope, pd.DataFrame) or scope.empty:
        return "your selected profile"
    if "from_country_name" not in scope.columns or from_league_col not in scope.columns:
        return "your selected profile"

    countries = scope["from_country_name"].dropna().astype(str).unique()
    leagues = scope[from_league_col].dropna().astype(str).unique()

    if len(countries) == 1 and len(leagues) == 1:
        return f"{countries[0]} · {translate_league_name(str(leagues[0]))}"
    if len(countries) == 1:
        return str(countries[0])
    return "your selected profile"


dest_country = st.session_state.get("destination_country", "India")
dest_league = st.session_state.get("destination_league", "Indian Super League")
if pd.isna(dest_league) or str(dest_league).strip().lower() in ["nan", "none", ""]:
    dest_league = ""
orig_country = st.session_state.get("user_origin_country", "Germany")
orig_league = st.session_state.get("user_origin_league", "Verbandsliga")
destination_source = st.session_state.get("destination_source", "start")
destination_scope = st.session_state.get("destination_scope")
career_navigator_profile = st.session_state.get("career_navigator_profile", {})
career_navigator_destination_scope = st.session_state.get(
    "career_navigator_destination_scope"
)

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

profile_country = career_navigator_profile.get("country") if career_navigator_profile else None
profile_league = career_navigator_profile.get("league") if career_navigator_profile else None
default_origin_country = profile_country if profile_country and profile_country != "All" else orig_country
default_origin_league = profile_league if profile_league and profile_league != "All" else orig_league

origin_countries = sorted(master["from_country_name"].dropna().astype(str).unique())
origin_country_index = (
    origin_countries.index(default_origin_country)
    if default_origin_country in origin_countries
    else 0
)
report_origin_key = f"{dest_country}_{dest_league}"

origin_control_left, origin_control_right = st.columns([1, 1.4])
with origin_control_left:
    report_origin_country = st.selectbox(
        "Origin country",
        origin_countries,
        index=origin_country_index,
        key=f"report_origin_country_{report_origin_key}",
    )

origin_country_rows = master[master["from_country_name"] == report_origin_country]
origin_leagues = ["All"] + sorted(
    (
        league_name
        for league_name in origin_country_rows[from_league_col].dropna().astype(str).unique()
        if is_selectable_league_name(league_name)
    ),
    key=translate_league_name,
)
origin_league_index = (
    origin_leagues.index(default_origin_league)
    if default_origin_league in origin_leagues
    else 0
)
with origin_control_right:
    report_origin_league = st.selectbox(
        "Origin league",
        origin_leagues,
        index=origin_league_index,
        format_func=translate_league_name,
        key=f"report_origin_league_{report_origin_key}",
    )

exact_scope = exact_destination_scope(destination_scope, dest_country, dest_league, to_league_col)
legacy_exact_scope = exact_destination_scope(
    career_navigator_destination_scope,
    dest_country,
    dest_league,
    to_league_col,
)
origin_changed = (
    str(report_origin_country) != str(default_origin_country)
    or str(report_origin_league) != str(default_origin_league)
)

if not origin_changed and not exact_scope.empty:
    cohort = exact_scope.copy()
    origin_label = navigator_profile_label(career_navigator_profile)
    if origin_label == "your selected profile":
        origin_label = scope_origin_label(exact_scope, from_league_col)
elif not origin_changed and not legacy_exact_scope.empty:
    cohort = legacy_exact_scope.copy()
    origin_label = navigator_profile_label(career_navigator_profile)
    if origin_label == "your selected profile":
        origin_label = scope_origin_label(legacy_exact_scope, from_league_col)
elif destination_source == "career_navigator" and career_navigator_profile:
    adjusted_profile = dict(career_navigator_profile)
    adjusted_profile["country"] = report_origin_country
    adjusted_profile["league"] = report_origin_league
    profile_scope = apply_navigator_profile(master, adjusted_profile, from_league_col)
    cohort = profile_scope[profile_scope["to_country_name"] == dest_country].copy()
    if dest_league:
        cohort = cohort[cohort[to_league_col].astype(str) == str(dest_league)].copy()
    origin_label = navigator_profile_label(adjusted_profile)
else:
    cohort = master[
        (master["from_country_name"] == report_origin_country)
        & (master["to_country_name"] == dest_country)
    ].copy()
    if report_origin_league != "All":
        cohort = cohort[cohort[from_league_col].astype(str) == str(report_origin_league)].copy()

    if dest_league:
        league_cohort = cohort[cohort[to_league_col].astype(
            str) == str(dest_league)]
        if not league_cohort.empty:
            cohort = league_cohort.copy()

    origin_label = (
        f"{report_origin_country} · {translate_league_name(str(report_origin_league))}"
        if report_origin_league != "All"
        else report_origin_country
    )

destination_matches = master[
    (master["to_country_name"] == dest_country)
    & (master[to_league_col].astype(str) == str(dest_league))
].copy()
stats_scope = cohort if not cohort.empty else destination_matches
stats = calculate_destination_statistics(stats_scope, master)

p_count = player_count(cohort)
avg_age = round(cohort["age"].mean(
), 1) if "age" in cohort.columns and not cohort.empty else "-"
avg_duration = average_next_move_seasons(cohort, master)
duration_label = f"{avg_duration} seasons" if avg_duration is not None else "-"
next_rows = next_transfer_rows(cohort, master)
next_rows = filter_valid_next_destinations(next_rows)

back_col, title_col = st.columns([1, 5])
with back_col:
    if st.button("← Back", use_container_width=False):
        st.switch_page("pages/1_Career_Navigator.py")

with title_col:
    report_title = f"{dest_country} · {translate_league_name(str(dest_league))}" if dest_league else dest_country
    product_header(
        report_title,
        f"Career intelligence for players matching {origin_label}.",
        eyebrow="Destination intelligence",
    )
    journey_steps("Destination")

stat_row(
    [
        ("Comparable players", f"{p_count:,}"),
        ("Profile", origin_label),
        ("Destination", report_title),
    ]
)

st.markdown("<br>", unsafe_allow_html=True)
section_header(
    "Should this destination be on your shortlist?",
    "Start with the career signal, then review pathway evidence and market realities.",
)
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Level-Up Rate", format_percent(stats.get("moved_up", 0)))
m2.metric("Same Level", format_percent(stats.get("stayed_level", 0)))
m3.metric("Level-Down Rate", format_percent(stats.get("moved_down", 0)))
m4.metric("Country Retention", format_percent(
    stats.get("country_retention", 0)))
m5.metric("Average Age", avg_age)
m6.metric("Average Duration", duration_label)
st.caption("Historical transfer patterns derived from comparable player careers and Opta league strength ratings.")

with st.expander("How to interpret these metrics"):
    st.markdown("""
    - **Level Up Rate:** Percentage of next recorded moves after this destination to a league with a **higher Opta strength rating**.
    - **Same Level:** Percentage of next recorded moves after this destination to a league with the **same Opta strength rating**.
    - **Level Down Rate:** Percentage of next recorded moves after this destination to a league with a **lower Opta strength rating**.
    - **Country Retention:** Percentage of players whose **next recorded transfer** remained within the destination country.
    - **Moved Abroad:** Percentage of players whose **next recorded transfer** was to a club in another country.
    - **Opta Ratings:** League strength is measured using standardized Opta Power Rankings.
    """)
st.info(
    f"Based on historical careers, {dest_country} has been a stepping stone for "
    f"**{format_percent(stats.get('moved_up', 0))} of comparable players** by Opta league movement."
)

st.divider()

section_header(
    f"What happened after {dest_country}?",
    "The next recorded move shows whether this destination tends to be a platform, a hold, or a detour.",
)
if next_rows.empty:
    st.caption(
        "No recorded next destination is available for this exact corridor yet.")
else:
    top_next = (
        next_rows.groupby(
            ["next_to_country_name", "next_to_aggregation"], dropna=False)
        .size()
        .reset_index(name="players")
        .sort_values("players", ascending=False)
        .head(4)
    )
    st.write(
        f"After leaving {dest_country}, comparable players most frequently moved to:")
    if top_next.empty:
        st.caption("No valid recorded next destinations are available yet.")
    else:
        cols = st.columns(len(top_next))
        for idx, (_, row) in enumerate(top_next.iterrows()):
            label = f"{row['next_to_country_name']} ({translate_league_name(str(row['next_to_aggregation']))})"
            if cols[idx].button(label, key=f"after_{idx}", use_container_width=True):
                st.session_state["destination_source"] = "destination_report"
                st.session_state.pop("destination_scope", None)
                st.session_state.pop("career_navigator_destination_scope", None)
                st.session_state["destination_country"] = row["next_to_country_name"]
                st.session_state["destination_league"] = row["next_to_aggregation"]
                st.rerun()

st.divider()

section_header(
    "Clubs that opened doors",
    "These clubs appear most often in comparable moves into this destination.",
)
if cohort.empty or "to_club_name" not in cohort.columns:
    st.caption("No club-level data is available for this corridor yet.")
else:
    club_rows = []
    for club, group in cohort.dropna(subset=["to_club_name"]).groupby("to_club_name"):
        club_next = next_transfer_rows(group, master)
        exits = (
            club_next["next_to_country_name"]
            .dropna()
            .value_counts()
            .head(3)
            .index
            .tolist()
        )
        club_rows.append(
            {
                "club": club,
                "players": player_count(group),
                "exits": exits,
                "examples": group.drop_duplicates("player_id").head(2),
            }
        )

    club_rows = sorted(
        club_rows, key=lambda item: item["players"], reverse=True)[:4]
    cols = st.columns(2)
    for idx, club in enumerate(club_rows):
        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"### {club['club']}")
                st.caption(f"{club['players']} comparable player(s)")
                exit_text = " → ".join(
                    club["exits"]) if club["exits"] else "No recorded exits yet"
                st.markdown(f"**Primary exits:** {exit_text}")
                names = [player_name(row)
                         for _, row in club["examples"].iterrows()]
                if names:
                    st.caption("Examples: " + ", ".join(names))

st.divider()

section_header(
    "Agencies active in this market",
    f"Agencies most active in arranging comparable transfers into {dest_country}.",
)
if "agent" not in stats_scope.columns:
    st.caption("No agency data is available for this destination yet.")
else:
    agent_exclusions = {"", "-", "Unknown", "ohne Berater", "ohne berater"}
    agents = (
        stats_scope["agent"]
        .dropna()
        .astype(str)
        .loc[lambda series: ~series.isin(agent_exclusions)]
        .value_counts()
        .head(3)
    )
    if agents.empty:
        st.caption("No named agencies are available for this destination yet.")
    else:
        cols = st.columns(len(agents))
        for column, (agency, deals) in zip(cols, agents.items()):
            column.metric(agency, f"{deals} transfers")

st.divider()

section_header(
    f"Life in {dest_country} & contract realities",
    "Practical context that affects whether the move is sustainable, not just possible.",
)
try:
    dossier = load_knowledge(dest_country)
except Exception:
    dossier = {}
    st.info("No living dossier is available for this country yet.")

for section in dossier.get("sections", []):
    icon = section.get("icon", "📄")
    title = section.get("title", "Overview")
    with st.expander(f"{icon} {title}"):
        if section.get("summary"):
            st.write(section["summary"])

        if section.get("salary_range_usd"):
            salary = section["salary_range_usd"]
            s1, s2, s3 = st.columns(3)
            s1.metric("Low", f"${salary.get('low', 0):,.0f}")
            s2.metric("Mid", f"${salary.get('mid_estimate', 0):,.0f}")
            s3.metric("High", f"${salary.get('high', 0):,.0f}")
            if salary.get("note"):
                st.caption(salary["note"])

        if section.get("official_information"):
            st.markdown("**Official Regulations:**")
            for item in section["official_information"]:
                st.markdown(f"- {item}")

        if section.get("community_insights"):
            st.markdown("**Community Insights:**")
            for item in section["community_insights"]:
                st.markdown(f"- {item}")

        with st.expander("Sources & References"):
            st.markdown("""
            - Source 1: Official League Governance & Contract Regulations
            - Source 2: Regional Association Financial Benchmarks
            - Source 3: Verified Player/Agent Field Data
            """)

st.divider()

section_header(
    f"Inspect {dest_country} visually",
    "Use external media searches to understand facilities, stadium context, and player experiences.",
)
col_a, col_b, col_c = st.columns(3)
col_a.link_button(
    "Training & Facilities",
    google_images_url(f"{dest_country} {dest_league} training facilities"),
    use_container_width=True,
)
col_b.link_button(
    "Stadiums & Crowds",
    google_images_url(f"{dest_country} {dest_league} stadiums crowds"),
    use_container_width=True,
)
col_c.link_button(
    "Player Interviews",
    google_url(f"{dest_country} {dest_league} player experience interview"),
    use_container_width=True,
)

if not next_rows.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    section_header(
        "Continue exploring next destinations",
        "Follow the most common next moves from this market.",
    )
    top_next = (
        next_rows.groupby(
            ["next_to_country_name", "next_to_aggregation"], dropna=False)
        .size()
        .reset_index(name="players")
        .sort_values("players", ascending=False)
        .head(3)
    )
    if top_next.empty:
        st.caption("No valid next destinations to explore yet.")
    else:
        next_cols = st.columns(len(top_next))
        for idx, (_, row) in enumerate(top_next.iterrows()):
            label = f"{row['next_to_country_name']} ({translate_league_name(str(row['next_to_aggregation']))})"
            if next_cols[idx].button(label, key=f"next_{idx}", use_container_width=True):
                st.session_state["destination_source"] = "destination_report"
                st.session_state.pop("destination_scope", None)
                st.session_state.pop("career_navigator_destination_scope", None)
                st.session_state["destination_country"] = row["next_to_country_name"]
                st.session_state["destination_league"] = row["next_to_aggregation"]
                st.rerun()
