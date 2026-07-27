import pandas as pd
import streamlit as st

from database import read_table
from components.ui import inject_kickways_theme
from utils.league_translation import is_selectable_league_name, translate_league_name


@st.cache_data
def load_table(table_name):
    return read_table(table_name)


def page_header(question, subtitle):
    inject_kickways_theme()
    render_navigation_sidebar()
    st.title(question)
    st.caption(subtitle)
    st.divider()


def render_navigation_sidebar():
    inject_kickways_theme()
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### Main Navigation")
        st.page_link("app2.py", label="Career path")
        st.page_link("pages/1_Career_Navigator.py", label="Opportunity explorer")
        st.page_link("pages/2_Destination_Report.py", label="Destination intelligence")
        with st.expander("Advanced Research Tools"):
            st.page_link("pages/4_Transfer_Corridors.py", label="Transfer Corridors")
            st.page_link("pages/5_League_Networks.py", label="League Networks")
            st.page_link("pages/6_Agency_Intelligence.py", label="Agency Intelligence")
            st.page_link("pages/7_Stepping_Clubs.py", label="Stepping Clubs")


def metric_row(metrics):
    columns = st.columns(len(metrics))
    for column, (label, value) in zip(columns, metrics):
        column.metric(label, format_number(value))


def format_number(value):
    if pd.isna(value):
        return "-"
    if isinstance(value, float):
        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.1f}m"
        if abs(value) >= 1_000:
            return f"{value / 1_000:.1f}k"
        return f"{value:.1f}"
    if isinstance(value, int):
        return f"{value:,}"
    return value


def money(value):
    if pd.isna(value):
        return "-"
    if abs(value) >= 1_000_000:
        return f"EUR {value / 1_000_000:.1f}m"
    if abs(value) >= 1_000:
        return f"EUR {value / 1_000:.0f}k"
    return f"EUR {value:,.0f}"


def percentage(value):
    if pd.isna(value):
        return "-"
    return f"{value * 100:.0f}%"


def select_filter(label, values, key=None):
    is_league_filter = "league" in label.lower()
    options = ["All"] + sorted(
        (
            value for value in pd.Series(values).dropna().astype(str).unique()
            if value.strip() and value != "nan"
            and (not is_league_filter or is_selectable_league_name(value))
        ),
        key=translate_league_name if is_league_filter else str,
    )
    formatter = translate_league_name if is_league_filter else str
    return st.selectbox(label, options, key=key, format_func=formatter)


def apply_equal_filter(frame, column, selected):
    if selected != "All" and column in frame.columns:
        return frame[frame[column].astype(str) == selected].copy()
    return frame


def add_share_columns(frame, columns):
    result = frame.copy()
    for column in columns:
        if column in result.columns:
            result[column] = result[column].apply(percentage)
    return result


def add_money_columns(frame, columns):
    result = frame.copy()
    for column in columns:
        if column in result.columns:
            result[column] = result[column].apply(money)
    return result


def intelligence_links():
    st.divider()
    st.caption("Related intelligence")
    columns = st.columns(5)
    links = [
        ("Corridors", "pages/4_Transfer_Corridors.py"),
        ("Stepping clubs", "pages/7_Stepping_Clubs.py"),
        ("League networks", "pages/5_League_Networks.py"),
        ("Agencies", "pages/6_Agency_Intelligence.py"),
        ("Players like me", "pages/8_Players_Like_Me.py"),
    ]
    for column, (label, path) in zip(columns, links):
        column.page_link(path, label=label)


# ============================================================
# OPTA SCORES PIPELINE (FROM APP2.PY)
# ============================================================


def add_opta_scores(master, mapping):
    """Merges Opta strength ratings into the master dataset using competition codes
    and fallback league names. Matches logic from app2.py.
    """
    master = master.copy()
    mapping = mapping.copy()
    mapping["opta_score"] = pd.to_numeric(
        mapping["opta_score"], errors="coerce"
    )

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

    # Match from/to scores by competition code
    if "from_league_code" in master.columns:
        master = master.merge(
            by_code,
            left_on="from_league_code",
            right_on="competition_code",
            how="left",
        ).rename(columns={"opta_score": "from_score"}).drop(columns=["competition_code"], errors="ignore")

    if "to_league_code" in master.columns:
        master = master.merge(
            by_code,
            left_on="to_league_code",
            right_on="competition_code",
            how="left",
        ).rename(columns={"opta_score": "to_score"}).drop(columns=["competition_code"], errors="ignore")

    # Match fallback scores by league name
    from_col = "from_league" if "from_league" in master.columns else "from_aggregation"
    to_col = "to_league" if "to_league" in master.columns else "to_aggregation"

    master = master.merge(
        by_league,
        left_on=from_col,
        right_on="our_league",
        how="left",
    ).rename(columns={"opta_score": "from_score_by_name"}).drop(columns=["our_league"], errors="ignore")

    master = master.merge(
        by_league,
        left_on=to_col,
        right_on="our_league",
        how="left",
    ).rename(columns={"opta_score": "to_score_by_name"}).drop(columns=["our_league"], errors="ignore")

    # Fill fallback values
    if "from_score" not in master.columns:
        master["from_score"] = master["from_score_by_name"]
    else:
        master["from_score"] = master["from_score"].fillna(
            master["from_score_by_name"]
        )

    if "to_score" not in master.columns:
        master["to_score"] = master["to_score_by_name"]
    else:
        master["to_score"] = master["to_score"].fillna(
            master["to_score_by_name"]
        )

    master = master.drop(
        columns=["from_score_by_name", "to_score_by_name"], errors="ignore"
    )
    master["league_quality_change"] = master["to_score"] - master["from_score"]

    return master


# ============================================================
# DESTINATION STATISTICS CALCULATOR
# ============================================================


def calculate_destination_statistics(
    destination_matches: pd.DataFrame,
    master: pd.DataFrame,
) -> dict:
    """Calculates onward progression and country retention statistics."""

    if destination_matches.empty:
        return {
            "sample_size": 0,
            "moved_up": 0.0,
            "stayed_level": 0.0,
            "moved_down": 0.0,
            "country_retention": 0.0,
            "exit_abroad": 0.0,
        }

    df = destination_matches.copy()
    total_records = len(df)
    df["_source_index"] = df.index

    # ============================================================
    # 1. Onward League Progression
    # ============================================================

    deltas = pd.Series(dtype=float)
    country_retention = 0.0
    exit_abroad = 0.0
    required = {"player_id", "date", "to_country_name"}

    if required.issubset(master.columns) and required.issubset(df.columns):
        target_players = df["player_id"].dropna().unique()
        history_columns = ["player_id", "date", "to_country_name"]
        if "to_score" in master.columns:
            history_columns.append("to_score")

        full_history = master.loc[
            master["player_id"].isin(target_players),
            history_columns,
        ].copy()
        full_history["_source_index"] = full_history.index
        full_history["_move_date"] = pd.to_datetime(
            full_history["date"], errors="coerce"
        )
        full_history = full_history.dropna(subset=["_move_date"]).sort_values(
            ["player_id", "_move_date", "_source_index"]
        )
        full_history["next_country"] = full_history.groupby("player_id")[
            "to_country_name"
        ].shift(-1)

        if "to_score" in full_history.columns and "to_score" in df.columns:
            full_history["next_to_score"] = full_history.groupby("player_id")[
                "to_score"
            ].shift(-1)
            next_scores = full_history.set_index("_source_index")[
                "next_to_score"
            ].reindex(df["_source_index"])
            current_scores = pd.to_numeric(df["to_score"], errors="coerce")
            deltas = (
                pd.to_numeric(next_scores, errors="coerce").reset_index(drop=True)
                - current_scores.reset_index(drop=True)
            ).dropna()

        next_countries = full_history.set_index("_source_index")[
            "next_country"
        ].reindex(df["_source_index"])
        finished = df.assign(
            next_country=next_countries.reset_index(drop=True).values
        ).dropna(subset=["next_country"])

        if len(finished):
            country_retention = round(
                (finished["next_country"] == finished["to_country_name"]).mean()
                * 100,
                1,
            )
            exit_abroad = round(
                (finished["next_country"] != finished["to_country_name"]).mean()
                * 100,
                1,
            )

    if len(deltas):
        moved_up = round((deltas > 0).mean() * 100, 1)
        moved_down = round((deltas < 0).mean() * 100, 1)
        stayed_level = round((deltas == 0).mean() * 100, 1)
    else:
        moved_up = stayed_level = moved_down = 0.0

    # ============================================================
    # Return
    # ============================================================

    return {
        "sample_size": total_records,
        "moved_up": moved_up,
        "stayed_level": stayed_level,
        "moved_down": moved_down,
        "country_retention": country_retention,
        "exit_abroad": exit_abroad,
    }
