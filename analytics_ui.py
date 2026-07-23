import pandas as pd
import streamlit as st

from database import read_table


@st.cache_data
def load_table(table_name):
    return read_table(table_name)


def page_header(question, subtitle):
    st.title(question)
    st.caption(subtitle)
    st.divider()


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
    options = ["All"] + sorted(
        value for value in pd.Series(values).dropna().astype(str).unique()
        if value.strip() and value != "nan"
    )
    return st.selectbox(label, options, key=key)


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
        ("Corridors", "pages/3_Transfer_Corridors.py"),
        ("Stepping clubs", "pages/4_Stepping_Clubs.py"),
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
            master["from_score_by_name"])

    if "to_score" not in master.columns:
        master["to_score"] = master["to_score_by_name"]
    else:
        master["to_score"] = master["to_score"].fillna(
            master["to_score_by_name"])

    master = master.drop(
        columns=["from_score_by_name", "to_score_by_name"], errors="ignore")
    master["league_quality_change"] = master["to_score"] - master["from_score"]

    return master


# ============================================================
# DESTINATION STATISTICS CALCULATOR
# ============================================================


def calculate_destination_statistics(df: pd.DataFrame) -> dict:
    """Calculates progression, stability, and outcome stats for a given subset of transfers."""
    if df.empty:
        return {
            "sample_size": 0,
            "moved_up": 0.0,
            "stayed_level": 0.0,
            "moved_down": 0.0,
            "stayed_6m": 0.0,
            "stayed_2y": 0.0,
            "returned_home": 0.0,
            "still_in_destination_3y": 0.0,
        }

    total_records = len(df)

    # 1. League Progression Delta (threshold of 5.0)
    if "league_quality_change" in df.columns:
        deltas = pd.to_numeric(
            df["league_quality_change"], errors="coerce").dropna()
    elif "to_score" in df.columns and "from_score" in df.columns:
        deltas = (
            pd.to_numeric(df["to_score"], errors="coerce")
            - pd.to_numeric(df["from_score"], errors="coerce")
        ).dropna()
    else:
        deltas = pd.Series(dtype=float)

    if len(deltas) > 0:
        threshold = 5.0
        moved_up = round((deltas > threshold).mean() * 100, 1)
        moved_down = round((deltas < -threshold).mean() * 100, 1)
        stayed_level = round(
            (deltas.between(-threshold, threshold)).mean() * 100, 1)
    else:
        moved_up = stayed_level = moved_down = 0.0

    # 2. Career Stability (Stayed >= 6 Months / 2 Years)
    stayed_6m = stayed_2y = 0.0
    if "days_at_destination" in df.columns:
        days = pd.to_numeric(df["days_at_destination"], errors="coerce")
        stayed_6m = round((days >= 180).mean() * 100, 1)
        stayed_2y = round((days >= 730).mean() * 100, 1)
    elif "stint_months" in df.columns:
        months = pd.to_numeric(df["stint_months"], errors="coerce")
        stayed_6m = round((months >= 6).mean() * 100, 1)
        stayed_2y = round((months >= 24).mean() * 100, 1)

    # 3. Returned Home
    returned_home = 0.0
    if "primary_nationality" in df.columns and "to_country_name" in df.columns:
        returned_home = round(
            (df["primary_nationality"] == df["to_country_name"]).mean() * 100, 1
        )

    # 4. Trajectory After 3 Years
    still_in_destination_3y = 0.0
    if "country_after_3y" in df.columns and "to_country_name" in df.columns:
        still_in_destination_3y = round(
            (df["country_after_3y"] == df["to_country_name"]).mean() * 100, 1
        )

    return {
        "sample_size": total_records,
        "moved_up": moved_up,
        "stayed_level": stayed_level,
        "moved_down": moved_down,
        "stayed_6m": stayed_6m,
        "stayed_2y": stayed_2y,
        "returned_home": returned_home,
        "still_in_destination_3y": still_in_destination_3y,
    }
