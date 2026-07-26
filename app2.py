import pandas as pd
import streamlit as st

from analytics_ui import load_table, render_navigation_sidebar
from utils.league_translation import translate_league_name


st.set_page_config(
    page_title="Kickways | Career Paths",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_navigation_sidebar()


def league_column(frame: pd.DataFrame, prefix: str) -> str:
    aggregate_column = f"{prefix}_aggregation"
    league_column_name = f"{prefix}_league"
    return aggregate_column if aggregate_column in frame.columns else league_column_name


def unique_players(frame: pd.DataFrame) -> int:
    return frame["player_id"].nunique() if "player_id" in frame.columns else len(frame)


def money(value) -> str:
    if pd.isna(value):
        return "N/A"
    if abs(value) >= 1_000_000:
        return f"EUR {value / 1_000_000:.1f}m"
    if abs(value) >= 1_000:
        return f"EUR {value / 1_000:.0f}k"
    return f"EUR {value:,.0f}"


def open_destination_dossier(country: str, league: str) -> None:
    st.session_state["destination_country"] = country
    st.session_state["destination_league"] = league
    st.switch_page("pages/2_Destination_Report.py")


def render_destination_row(row: pd.Series, league_col: str, key_prefix: str) -> None:
    destination_country = row["to_country_name"]
    destination_league = row[league_col]
    share = row["share"]

    text_col, button_col = st.columns([3, 1.3])
    with text_col:
        st.write(
            f"**{destination_country}** ({translate_league_name(str(destination_league))}) - **{share}%**"
        )
        st.progress(min(float(share) / 100.0, 1.0))
    with button_col:
        if st.button(
            "Show league/country dossier",
            key=f"{key_prefix}_{destination_country}_{destination_league}",
            use_container_width=True,
        ):
            open_destination_dossier(destination_country, destination_league)


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


if "user_origin_country" not in st.session_state:
    st.session_state["user_origin_country"] = "Germany"
if "user_origin_league" not in st.session_state:
    st.session_state["user_origin_league"] = "Verbandsliga"
if "searched" not in st.session_state:
    st.session_state["searched"] = False
if "start_international_only" not in st.session_state:
    st.session_state["start_international_only"] = False


master = load_table("master_dataset")
from_league_col = league_column(master, "from")
to_league_col = league_column(master, "to")

valid_origins = master.dropna(subset=["from_country_name", from_league_col]).copy()


if not st.session_state["searched"]:
    st.markdown(
        "<h1 style='text-align:center;margin-top:3rem;'>Kickways</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h3 style='text-align:center;color:#888;'>Discover where football careers actually go.</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;font-size:1.2rem;margin-top:2rem;'>Where do you play today?</p>",
        unsafe_allow_html=True,
    )

    _, form_col, _ = st.columns([1, 2, 1])
    with form_col:
        countries = sorted(valid_origins["from_country_name"].dropna().unique())
        default_country = st.session_state.get("user_origin_country", "Germany")
        default_idx = countries.index(default_country) if default_country in countries else 0

        country = st.selectbox("Country", countries, index=default_idx)

        country_rows = valid_origins[valid_origins["from_country_name"] == country]
        leagues = sorted(
            country_rows[from_league_col].dropna().astype(str).unique(),
            key=translate_league_name,
        )
        default_league = st.session_state.get("user_origin_league")
        default_league_idx = leagues.index(default_league) if default_league in leagues else 0

        league = st.selectbox(
            "League",
            leagues,
            index=default_league_idx,
            format_func=translate_league_name,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Show Career Paths →", use_container_width=True, type="primary"):
            st.session_state["user_origin_country"] = country
            st.session_state["user_origin_league"] = league
            st.session_state["searched"] = True
            st.rerun()

else:
    country = st.session_state["user_origin_country"]
    league = st.session_state["user_origin_league"]

    origin_matches = master[
        (master["from_country_name"] == country)
        & (master[from_league_col].astype(str) == str(league))
    ].copy()

    back_col, toggle_col, _ = st.columns([1, 1.4, 3.6])
    with back_col:
        if st.button("← Start over", use_container_width=True):
            st.session_state["searched"] = False
            st.rerun()
    with toggle_col:
        international_only = st.toggle(
            "International only",
            key="start_international_only",
        )

    if international_only:
        matches = origin_matches[
            origin_matches["to_country_name"].notna()
            & (origin_matches["to_country_name"] != country)
        ].copy()
    else:
        matches = origin_matches.copy()

    total_careers = unique_players(matches)

    st.markdown(f"### Players from **{country} - {translate_league_name(str(league))}**")
    count_label = "international comparable careers" if international_only else "comparable careers"
    st.markdown(f"## ⚡ **{total_careers:,} {count_label} found.**")
    st.divider()

    col_left, col_right = st.columns([1.5, 1], gap="large")

    dest_counts = pd.DataFrame(columns=["to_country_name", to_league_col, "players", "share"])

    with col_left:
        st.subheader("Where did they go?")
        if matches.empty:
            st.info("No comparable career paths are available for this origin yet.")
        else:
            dest_counts = (
                matches.dropna(subset=["to_country_name", to_league_col])
                .groupby(["to_country_name", to_league_col], dropna=False)
                .agg(players=("player_id", "nunique") if "player_id" in matches.columns else (to_league_col, "count"))
                .reset_index()
            )
            dest_counts["share"] = (dest_counts["players"] / max(total_careers, 1) * 100).round(1)
            dest_counts = dest_counts.sort_values(["players", "share"], ascending=False)

            top_destinations = dest_counts.head(20)
            other_destinations = dest_counts.iloc[20:]

            for idx, (_, row) in enumerate(top_destinations.iterrows()):
                render_destination_row(row, to_league_col, f"start_top_{idx}")

            if not other_destinations.empty:
                with st.expander(f"Expand all leagues ({len(other_destinations)} more)"):
                    for idx, (_, row) in enumerate(other_destinations.iterrows()):
                        render_destination_row(row, to_league_col, f"start_more_{idx}")

    with col_right:
        st.subheader("Key Benchmarks")
        avg_age = round(matches["age"].mean(), 1) if "age" in matches.columns and not matches.empty else "N/A"
        avg_next_move = average_time_until_next_move(matches, master)

        st.metric("Average age when moving", avg_age)
        st.metric(
            "Average time until next move",
            f"{avg_next_move} seasons" if avg_next_move is not None else "N/A",
        )

    st.divider()

    if not dest_counts.empty:
        top_dest = dest_counts.iloc[0]["to_country_name"]
        top_dest_league = dest_counts.iloc[0][to_league_col]

        if st.button(
            f"Explore {top_dest} ({translate_league_name(str(top_dest_league))}) Dossier →",
            type="primary",
        ):
            open_destination_dossier(top_dest, top_dest_league)
