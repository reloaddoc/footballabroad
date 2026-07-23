import re
import pandas as pd
import streamlit as st

from analytics_ui import (
    add_opta_scores,
    calculate_destination_statistics,
    load_table,
)
from services.destination_service import load_knowledge

# ============================================================
# SESSION STATE & DATA LOAD WITH OPTA ENRICHMENT
# ============================================================

country = st.session_state.get("destination_country", "India")
league = st.session_state.get("destination_league", "Indian Super League")

# Load Qualitative Knowledge JSON
knowledge = load_knowledge(country)

# Load Quantitative Master Dataset and League Mapping
master_raw = load_table("master_dataset")
mapping_raw = load_table("league_mapping")

# Attach Opta Scores to master dataset (exact app2 pipeline logic)
master = add_opta_scores(master_raw, mapping_raw)

# Filter Master Dataset for target destination
destination_matches = master[
    (master["to_country_name"] == country) &
    (master["to_aggregation"] == league)
].copy()

# Fallback icons map for sections
SECTION_ICONS = {
    "Accommodation": "🏠",
    "Salary Expectations": "💰",
    "Visa & Work Permit": "📝",
    "Foreign Player Rules": "⚽",
    "Lifestyle": "🌴",
    "Travel & Logistics": "✈️",
    "Infrastructure": "🏟️",
    "Culture & Language": "🗣️",
    "Safety": "🛡️",
}


def make_anchor_id(title: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "", title.lower().replace(" ", "-"))

# ============================================================
# HERO HEADER & NAVIGATION
# ============================================================


top_col1, top_col2 = st.columns([1, 5])

with top_col1:
    if st.button("← Back", use_container_width=True):
        try:
            st.switch_page("pages/7_Career_Navigator.py")
        except Exception:
            st.switch_page("app.py")

with top_col2:
    st.title(f"🌍 {country}")
    st.caption(f"Destination Market Intelligence · **{league}**")

st.divider()

# ============================================================
# TABLE OF CONTENTS
# ============================================================

st.markdown("##### 📌 Jump to Section")

toc_cols = st.columns(4)

# 1. First anchor: Database Statistics
toc_items = [("📊 Market Statistics", "market-statistics")]

# 2. Add JSON Qualitative Sections to TOC
if knowledge and "sections" in knowledge:
    for sec in knowledge.get("sections", []):
        t = sec.get("title", "Overview")
        icon = sec.get("icon") or SECTION_ICONS.get(t, "📌")
        toc_items.append((f"{icon} {t}", make_anchor_id(t)))

for idx, (label, anchor_id) in enumerate(toc_items):
    with toc_cols[idx % 4]:
        st.markdown(f"• [{label}](#{anchor_id})")

st.divider()

# ============================================================
# 📊 SECTION 1: DATABASE & OPTA MARKET STATISTICS
# ============================================================

st.markdown('<div id="market-statistics"></div>', unsafe_allow_html=True)
st.subheader("📊 Market & Career Path Statistics")
st.caption(
    "Historical transfer patterns computed from comparable player movements with Opta ratings.")

if destination_matches.empty:
    st.info("No historical transfer data available for this destination in the dataset.")
else:
    # Compute core statistics using central Opta helper function
    stats = calculate_destination_statistics(destination_matches)

    # 1. METRICS ROW OVERVIEW
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Recorded Transfers", len(destination_matches))
    m2.metric("Unique Players", destination_matches["player_id"].nunique())
    m3.metric("Level Up Rate 📈", f"{stats.get('moved_up', 0)}%")
    m4.metric("Stayed >6m ⏱️", f"{stats.get('stayed_6m', 0)}%")

    st.markdown("---")

    # 2. FEASIBILITY & NATIONALITIES
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("##### 🛫 Top Origin Corridors")
        st.caption("Leagues from which players most frequently move here.")

        origin_corridors = (
            destination_matches.groupby(
                ["from_country_name", "from_aggregation"])
            .size()
            .reset_index(name="Transfers")
            .sort_values("Transfers", ascending=False)
            .head(5)
        )
        origin_corridors["Corridor"] = (
            origin_corridors["from_country_name"] +
            " (" + origin_corridors["from_aggregation"] + ")"
        )
        st.dataframe(
            origin_corridors[["Corridor", "Transfers"]],
            use_container_width=True,
            hide_index=True,
        )

    with c2:
        st.markdown("##### 🌎 Foreign Nationality Mix")
        st.caption("Most represented foreign nationalities in this league.")

        nat_mix = (
            destination_matches["primary_nationality"]
            .value_counts(normalize=True)
            .head(5)
            .mul(100)
            .round(1)
            .reset_index()
        )
        nat_mix.columns = ["Nationality", "Share (%)"]
        nat_mix["Share (%)"] = nat_mix["Share (%)"].astype(str) + "%"
        st.dataframe(
            nat_mix,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")

    # 3. NEXT DESTINATIONS & CAREER MOBILITY
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("##### 🔄 Career Mobility (Opta Progression)")
        st.caption("Outcomes of players after completing their stint here.")

        st.markdown(
            f"• **Moved Up (Opta Delta > 5):** `{stats.get('moved_up', 0)}%`  \n"
            f"• **Stayed Level (±5):** `{stats.get('stayed_level', 0)}%`  \n"
            f"• **Moved Down (Opta Delta < -5):** `{stats.get('moved_down', 0)}%`  \n"
            f"• **Returned Home:** `{stats.get('returned_home', 0)}%`"
        )

    with c4:
        st.markdown("##### 🏢 Top Active Agencies")
        st.caption("Agencies with recorded deals into this destination.")

        if "agent" in destination_matches.columns:
            # 1. Übersetzungs-Mapping definieren
            agency_translation = {
                "ohne Berater": "Without Agent",
                "Familienangehörige": "Relatives",
                # Falls in deiner DB noch Varianten vorkommen:
                "ohne berater": "Without Agent",
                "Familienangehöriger": "Relatives",
            }

            # 2. DataFrame filtern & Werte ersetzen
            agents_df = destination_matches[
                ~destination_matches["agent"].isin(["", "-", "Unknown", None])
            ].copy()

            # Namen mappen/übersetzen
            agents_df["agent"] = agents_df["agent"].replace(agency_translation)

            # 3. Gruppieren & Aggregieren
            agents = (
                agents_df["agent"]
                .value_counts()
                .head(5)
                .reset_index()
            )
            agents.columns = ["Agency", "Deals"]

            st.dataframe(
                agents,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No agency data available.")

st.divider()

# ============================================================
# 📑 SECTION 2: QUALITATIVE DESTINATION INTELLIGENCE
# ============================================================

if knowledge and "sections" in knowledge:
    sections_list = knowledge.get("sections", [])

    for section in sections_list:
        section_title = section.get("title", "Overview")
        icon = section.get("icon") or SECTION_ICONS.get(section_title, "📌")
        anchor_id = make_anchor_id(section_title)

        # Invisible anchor tag for internal TOC navigation
        st.markdown(f'<div id="{anchor_id}"></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(f"### {icon} {section_title}")

            # Salary Metric Layout Box
            if "Salary" in section_title or "salary_range_usd" in section:
                salary_data = section.get("salary_range_usd", {})

                low = salary_data.get("low", 37000)
                mid = salary_data.get("mid_estimate", 90000)
                high = salary_data.get("high", 400000)
                note = salary_data.get(
                    "note",
                    "Approximate annual USD range compiled from public sources; exact pay varies by club, season, and role.",
                )

                st.markdown("#### Expected Annual Salary Range (USD)")

                sm1, sm2, sm3 = st.columns(3)
                sm1.metric("Low Entry", f"${low:,.0f}")
                sm2.metric("Mid Estimate", f"${mid:,.0f}")
                sm3.metric("High End", f"${high:,.0f}")

                st.caption(f"ℹ️ {note}")
                st.divider()

            # Summary Text
            if section.get("summary"):
                st.write(section["summary"])

            # Official Information
            official_info = section.get("official_information", [])
            if official_info:
                st.markdown("#### 📜 Official Rules & Information")
                for item in official_info:
                    st.markdown(f"* {item}")

            # Community Insights
            community_insights = section.get("community_insights", [])
            if community_insights:
                st.markdown("#### 💬 Community & Market Insights")
                for insight in community_insights:
                    st.markdown(f"* {insight}")

            # Player Cases
            experiences = section.get("player_experiences", [])

            # --- REPLACE valid_exp HERE ---
            valid_exp = []
            for exp in experiences:
                if isinstance(exp, dict) and exp.get("statement", "").strip():
                    valid_exp.append(exp)
                elif isinstance(exp, str) and exp.strip():
                    valid_exp.append({"statement": exp.strip()})
            # -------------------------------

            if valid_exp:
                st.markdown("#### 👤 Player & Club Cases")
                exp_rows = []
                for exp in valid_exp:
                    club = exp.get("club") or "General"
                    season = f" ({exp.get('season')})" if exp.get(
                        "season") else ""
                    statement = exp.get("statement", "")

                    exp_rows.append(
                        {"Club / Context": f"{club}{season}", "Insight": statement}
                    )

                df_exp = pd.DataFrame(exp_rows)
                st.dataframe(df_exp, use_container_width=True, hide_index=True)

            # Sources
            sources = section.get("sources", [])
            if sources:
                with st.expander(f"📚 Sources & Citations ({len(sources)})"):
                    for src in sources:
                        src_type = src.get(
                            "source_type", src.get("type", "Source"))
                        title = src.get("title", "Link")
                        url = src.get("url", "#")
                        date = f" ({src['date']})" if src.get("date") else ""

                        st.markdown(
                            f"* **[{title}]({url})** `{src_type}`{date}")
