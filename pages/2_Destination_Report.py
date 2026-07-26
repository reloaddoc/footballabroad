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
from services.destination_service import load_knowledge
from utils.league_translation import translate_league_name

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


dest_country = st.session_state.get("destination_country", "India")
dest_league = st.session_state.get("destination_league", "Indian Super League")
if pd.isna(dest_league) or str(dest_league).strip().lower() in ["nan", "none", ""]:
    dest_league = ""
orig_country = st.session_state.get("user_origin_country", "Germany")
orig_league = st.session_state.get("user_origin_league", "Verbandsliga")

master_raw = load_table("master_dataset")
try:
    mapping_raw = load_table("league_mapping")
    master = add_opta_scores(master_raw, mapping_raw)
except Exception:
    master = master_raw.copy()

from_league_col = league_column(master, "from")
to_league_col = league_column(master, "to")

cohort = master[
    (master["from_country_name"] == orig_country)
    & (master[from_league_col].astype(str) == str(orig_league))
    & (master["to_country_name"] == dest_country)
].copy()

if dest_league:
    league_cohort = cohort[cohort[to_league_col].astype(
        str) == str(dest_league)]
    if not league_cohort.empty:
        cohort = league_cohort.copy()

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
    if st.button("← Back", use_container_width=True):
        st.switch_page("pages/1_Career_Navigator.py")

with title_col:
    report_title = f"{dest_country} - {translate_league_name(str(dest_league))}" if dest_league else dest_country
    st.markdown(f"# {report_title}")
    st.caption("Career Intelligence Due-Diligence Report")

st.success(
    f"**{p_count:,} comparable players** from **{orig_country} ({orig_league})** successfully moved here."
)

st.divider()

st.subheader("1. Can this move improve my career?")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Level-Up Rate", format_percent(stats.get("moved_up", 0)))
m2.metric("Country Retention", format_percent(
    stats.get("country_retention", 0)))
m3.metric("Average Age", avg_age)
m4.metric("Average Duration", duration_label)
st.caption("Historical transfer patterns derived from comparable player careers and Opta league strength ratings.")

with st.expander("How to interpret these metrics"):
    st.markdown("""
    - **Level Up Rate:** Percentage of transfers to a league with an Opta strength rating at least **5 points higher** than the player's previous league.
    - **Country Retention:** Percentage of players whose **next recorded transfer** remained within the destination country.
    - **Moved Abroad:** Percentage of players whose **next recorded transfer** was to a club in another country.
    - **Opta Ratings:** League strength is measured using standardized Opta Power Rankings.
    """)
st.info(
    f"Based on historical careers, {dest_country} has been a stepping stone for "
    f"**{format_percent(stats.get('moved_up', 0))} of comparable players** by Opta league movement."
)

st.divider()

st.subheader(f"2. What happened after {dest_country}?")
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
                st.session_state["destination_country"] = row["next_to_country_name"]
                st.session_state["destination_league"] = row["next_to_aggregation"]
                st.rerun()

st.divider()

st.subheader("3. Which clubs opened the most doors?")
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

st.subheader("4. Who makes these transfers happen?")
st.write(f"Agencies most active in arranging transfers into {dest_country}:")
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

st.subheader(f"5. Life in {dest_country} & Contract Realities")
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

st.subheader(f"6. Experience {dest_country} & Next Steps")
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
    st.subheader("Continue Exploring Next Destinations")
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
                st.session_state["destination_country"] = row["next_to_country_name"]
                st.session_state["destination_league"] = row["next_to_aggregation"]
                st.rerun()
