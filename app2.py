import pandas as pd
import streamlit as st

from analytics_ui import load_table, render_navigation_sidebar


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


if "user_origin_country" not in st.session_state:
    st.session_state["user_origin_country"] = "Germany"
if "user_origin_league" not in st.session_state:
    st.session_state["user_origin_league"] = "Verbandsliga"
if "searched" not in st.session_state:
    st.session_state["searched"] = False


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
        leagues = sorted(country_rows[from_league_col].dropna().astype(str).unique())
        default_league = st.session_state.get("user_origin_league")
        default_league_idx = leagues.index(default_league) if default_league in leagues else 0

        league = st.selectbox("League", leagues, index=default_league_idx)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Show Career Paths →", use_container_width=True, type="primary"):
            st.session_state["user_origin_country"] = country
            st.session_state["user_origin_league"] = league
            st.session_state["searched"] = True
            st.rerun()

else:
    country = st.session_state["user_origin_country"]
    league = st.session_state["user_origin_league"]

    matches = master[
        (master["from_country_name"] == country)
        & (master[from_league_col].astype(str) == str(league))
    ].copy()
    total_careers = unique_players(matches)

    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("← Start over", use_container_width=True):
            st.session_state["searched"] = False
            st.rerun()

    st.markdown(f"### Players from **{country} - {league}**")
    st.markdown(f"## ⚡ **{total_careers:,} comparable careers found.**")
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
            dest_counts = dest_counts.sort_values(["players", "share"], ascending=False).head(5)

            for _, row in dest_counts.iterrows():
                destination_country = row["to_country_name"]
                destination_league = row[to_league_col]
                share = row["share"]

                st.write(f"**{destination_country}** ({destination_league}) - **{share}%**")
                st.progress(min(float(share) / 100.0, 1.0))

    with col_right:
        st.subheader("Key Benchmarks")
        avg_age = round(matches["age"].mean(), 1) if "age" in matches.columns and not matches.empty else "N/A"
        avg_value = money(matches["market_value"].mean()) if "market_value" in matches.columns and not matches.empty else "N/A"
        avg_seasons = round(matches["career_length"].mean(), 1) if "career_length" in matches.columns and not matches.empty else "N/A"

        st.metric("Average age when moving", avg_age)
        st.metric("Average market value", avg_value)
        st.metric("Average time until next move", f"{avg_seasons} seasons" if avg_seasons != "N/A" else "N/A")

    st.divider()

    if not dest_counts.empty:
        top_dest = dest_counts.iloc[0]["to_country_name"]
        top_dest_league = dest_counts.iloc[0][to_league_col]

        if st.button(f"Explore {top_dest} ({top_dest_league}) Dossier →", type="primary"):
            st.session_state["destination_country"] = top_dest
            st.session_state["destination_league"] = top_dest_league
            st.switch_page("pages/2_Destination_Report.py")
