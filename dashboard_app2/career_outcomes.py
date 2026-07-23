import pandas as pd
import streamlit as st

from dashboard_app2.outcome_engine import get_career_outcomes


def _percentage(outcomes, column):
    if outcomes.empty or column not in outcomes:
        return 0
    return outcomes[column].mean() * 100


def _percentage_of(outcomes, column, mask):
    filtered = outcomes[mask]
    if filtered.empty or column not in filtered:
        return 0
    return filtered[column].mean() * 100


def _selected_or_summary(filters, key, fallback):
    if filters and filters.get(key) != "All":
        return filters[key]
    return fallback


def _decision_text(filters):
    if not filters:
        return "broad filtered cohort"

    origin = filters.get("origin")
    destination = filters.get("destination")
    origin_country = filters.get("origin_country")
    destination_country = filters.get("destination_country")

    if origin != "All" and destination != "All":
        return f"move from {origin} to {destination}"
    if destination != "All":
        return f"move to {destination}"
    if destination_country != "All":
        return f"move to {destination_country}"
    if origin != "All":
        return f"moves after playing in {origin}"
    if origin_country != "All":
        return f"moves after playing in {origin_country}"
    return "broad filtered cohort"


def _typical_case_text(filters, destination_country, avg_age):
    if filters and filters.get("destination_country", "All") != "All":
        return f"outcome of moving to {filters.get('destination_country')} at age {avg_age:.0f}"

    if filters and filters.get("destination", "All") != "All":
        return f"outcome of moving to {filters.get('destination')} at age {avg_age:.0f}"

    return f"outcomes for comparable players aged around {avg_age:.0f}"


def show(master, filtered, filters=None):
    st.title("Historical Career Outcomes")
    st.caption("Typical career trajectories based on historical cohort pathways.")

    if filters is None:
        filters = {}

    # ========================================================
    # LOGIK: HERKUNFT & ZIEL PRÜFEN (LAND ODER LIGA)
    # ========================================================
    def is_selected(val):
        return val is not None and str(val).strip() not in ["All", "", "None"]

    # 1. Herkunft definiert? (Land ODER Liga gewählt)
    has_origin = is_selected(filters.get(
        "origin_country")) or is_selected(filters.get("origin"))

    # 2. Ziel definiert? (Land ODER Liga gewählt)
    has_destination = is_selected(filters.get(
        "destination_country")) or is_selected(filters.get("destination"))

    # Wenn NICHT mindestens ein Herkunfts- UND ein Zielmerkmal gewählt wurden -> Abbruch!
    if not (has_origin and has_destination):
        st.divider()
        st.info(
            "🎯 **Select a complete Career Decision to calculate predictions.**\n\n"
            "To calculate a reliable Risk Score and Outcome Probability, please specify both an origin and a destination:\n"
            "• **Moved From** (select at least a Country or League)\n"
            "• **Moved To** (select at least a Country or League)\n\n"
            "*(Nationality, Position, Age, etc. serve as optional profile filters.)*"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if has_origin:
                origin_text = filters.get('origin') if is_selected(
                    filters.get('origin')) else filters.get('origin_country')
                st.success(f"✅ Moved From: **{origin_text}**")
            else:
                st.warning("⚠️ Moved From: **Not selected**")

        with col_b:
            if has_destination:
                dest_text = filters.get('destination') if is_selected(
                    filters.get('destination')) else filters.get('destination_country')
                st.success(f"✅ Moved To: **{dest_text}**")
            else:
                st.warning("⚠️ Moved To: **Not selected**")

        st.divider()
        return  # Bricht ab, damit kein irreführender Risk Score berechnet wird!

    # ========================================================
    # KARRIEREENTSCHEIDUNG IST VOLLSTÄNDIG -> OUTCOMES BERECHNEN
    # ========================================================
    cohort = filtered

    if cohort.empty:
        st.warning("No matching players found for this career decision.")
        return

    outcomes = get_career_outcomes(master, cohort)

    if outcomes.empty:
        st.warning("No matching player outcomes recorded.")
        return

    # --- SICHERE BERECHNUNG MIT FALLBACKS BEI LEEREN DATEN ---
    if not cohort.empty and not cohort["primary_nationality"].dropna().empty:
        mode_nat = cohort["primary_nationality"].mode().iloc[0]
    else:
        mode_nat = "Unknown"

    nationality = _selected_or_summary(filters, "nationality", mode_nat)

    if not cohort.empty and not cohort["position_group"].dropna().empty:
        mode_pos = cohort["position_group"].mode().iloc[0]
    else:
        mode_pos = "Unknown"

    position = _selected_or_summary(filters, "position", mode_pos)

    if not cohort.empty and not cohort["to_country_name"].dropna().empty:
        destination_country = cohort["to_country_name"].mode().iloc[0]
    else:
        destination_country = "Unknown"

    avg_age = cohort["age"].mean() if not cohort.empty else 0

    decision = _decision_text(filters)
    typical_case = _typical_case_text(filters, destination_country, avg_age)

    players = len(outcomes)

    pct_stayed_6_months = _percentage(outcomes, "stayed_6_months")
    pct_stayed_2_years = _percentage(outcomes, "stayed_2_years")
    next_league_comparison = outcomes["next_league_quality_change"].notna()
    scored_next_moves = int(next_league_comparison.sum())
    pct_moved_up = _percentage_of(outcomes, "moved_up", next_league_comparison)
    pct_moved_down = _percentage_of(
        outcomes, "moved_down", next_league_comparison)
    pct_same_level = _percentage_of(
        outcomes, "stayed_level", next_league_comparison)
    # NACHHER (Korrigiert):
    pct_returned_home = _percentage(outcomes, "returned_home")
    pct_stayed_abroad = 100.0 - pct_returned_home  # Komplementär-Wert

    pct_free_agent = _percentage(outcomes, "became_free_agent")
    pct_retired = _percentage(outcomes, "retired_or_inactive")

    # ==========================================
    # 1. ERKLÄRBARE RISIKO-BERECHNUNG & SAMPLE CONFIDENCE
    # ==========================================
    sample_size = players

    if sample_size < 10:
        confidence_level = "Low Confidence"
        confidence_color = "#888888"
    elif sample_size < 30:
        confidence_level = "Medium Confidence"
        confidence_color = "#FFA500"
    else:
        confidence_level = "High Confidence"
        confidence_color = "#00CC66"

    short_stay_risk = max(0, min(100, 100 - pct_stayed_6_months))
    downward_risk = max(0, min(100, pct_moved_down))
    instability_risk = max(0, min(100, pct_free_agent + pct_retired))
    no_return_risk = max(0, min(100, 100 - pct_returned_home))

    w_stay = 0.35
    w_down = 0.35
    w_instab = 0.15
    w_return = 0.15

    numeric_risk_score = int(
        (short_stay_risk * w_stay) +
        (downward_risk * w_down) +
        (instability_risk * w_instab) +
        (no_return_risk * w_return)
    )

    if numeric_risk_score >= 55:
        risk_label = "High Risk"
        risk_color = "#FF4B4B"
    elif numeric_risk_score >= 30:
        risk_label = "Medium Risk"
        risk_color = "#FFA500"
    else:
        risk_label = "Low Risk"
        risk_color = "#00CC66"

    # ==========================================
    # 2. METRIC KACHELN ANZEIGEN (VERLÄSSLICHKEIT)
    # ==========================================
    col0, col1, col2, col3 = st.columns(4)

    with col0:
        if sample_size < 10:
            st.markdown(
                f"""
                <div style='background-color: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; border-left: 4px solid {confidence_color};'>
                    <p style='margin: 0px; font-size: 13px; color: #AAAAAA; font-weight: 500;'>Risk Score</p>
                    <p style='margin: 0px; font-size: 22px; font-weight: bold; color: {confidence_color};'>
                        Low Data
                    </p>
                    <p style='margin: 0px; font-size: 12px; color: #AAAAAA;'>Sample size too small</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style='background-color: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; border-left: 4px solid {risk_color};'>
                    <p style='margin: 0px; font-size: 13px; color: #AAAAAA; font-weight: 500;'>Risk Score</p>
                    <p style='margin: 0px; font-size: 28px; font-weight: bold; color: {risk_color};'>
                        {numeric_risk_score} <span style='font-size: 16px; color: #888;'>/ 100</span>
                    </p>
                    <p style='margin: 0px; font-size: 12px; color: {risk_color}; font-weight: 600;'>{risk_label}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    col1.metric("Cohort Sample", f"{sample_size} players")
    col2.metric("Data Confidence", confidence_level)
    col3.metric("Scored Moves", f"{scored_next_moves}")

    st.divider()

    # ==========================================
    # 3. EXPLICIT RISK DRIVERS OR SAMPLE WARNING
    # ==========================================
    if sample_size < 10:
        st.warning(
            f"⚠️ **Low Confidence Warning:** Only **{sample_size} historical example(s)** match this decision.\n\n"
            "A statistically reliable Risk Score cannot be calculated for sample sizes below 10. "
            "Try broadening your optional filters (e.g. set Age or Position to 'All') to increase the cohort size."
        )
    else:
        st.subheader("🔍 Observed Risk Indicators")
        st.caption(
            "Detailed breakdown of underlying risk factors for this career decision. These indicators are independent. A player may contribute to multiple indicators, so percentages do not add up to 100%.")

        def get_driver_badge(val, high_thresh=40, med_thresh=20):
            if val >= high_thresh:
                return "🔴 High Impact"
            elif val >= med_thresh:
                return "🟡 Medium Impact"
            else:
                return "🟢 Low Impact"

        driver_data = [
            {
                "Risk Driver": "📉 League Downgrade",
                "Observed Outcome": f"{pct_moved_down:.1f}% moved down afterwards",
                "Impact": get_driver_badge(pct_moved_down, 40, 20)
            },
            {
                "Risk Driver": "⏱️ Short Stay (< 6 Months)",
                "Observed Outcome": f"{short_stay_risk:.1f}% left in <6 months",
                "Impact": get_driver_badge(short_stay_risk, 30, 15)
            },
            {
                "Risk Driver": "⚠️ Free Agency & Inactivity",
                "Observed Outcome": f"{pct_free_agent + pct_retired:.1f}% became free agent/inactive",
                "Impact": get_driver_badge(pct_free_agent + pct_retired, 20, 10)
            },
            {
                "Risk Driver": "🏠 Did Not Return Home",
                "Observed Outcome": f"{no_return_risk:.1f}% did not return home",
                "Impact": get_driver_badge(no_return_risk, 70, 50)
            }
        ]

        st.dataframe(pd.DataFrame(driver_data),
                     use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("Historical Career Outcomes")

    # --- OUTCOME KACHELN & STATISTIK ---
    outcome_cols = st.columns(4)
    outcome_cols[0].metric("Moved Up", f"{pct_moved_up:.1f}%")
    outcome_cols[1].metric("Moved Down", f"{pct_moved_down:.1f}%")
    outcome_cols[2].metric("Stayed Level", f"{pct_same_level:.1f}%")
    outcome_cols[3].metric("Returned Home", f"{pct_returned_home:.1f}%")

    st.caption(
        f"{pct_stayed_6_months:.1f}% stayed at least 6 months after the decision. "
        "Moved up/down/level compares the destination league with the player's next league via Opta scores. "
        f"'Scored Next Moves' represents the sample size ({scored_next_moves}/{players}) with valid data available for this comparison."
    )

    st.divider()

    st.subheader("What happened after this decision?")

    st.caption(
        "Historical outcomes observed for players making this career decision."
    )

    # ======================================================
    # Career Stability
    # ======================================================
    st.markdown("### ⏳ Career Stability")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Stayed >6 Months",
        f"{pct_stayed_6_months:.1f}%"
    )

    c2.metric(
        "Stayed >2 Years",
        f"{pct_stayed_2_years:.1f}%"
    )

    c3.metric(
        "Moved Down",
        f"{pct_moved_down:.1f}%",
        delta="High",
        delta_color="inverse"
    )

    st.divider()

    # ======================================================
    # League Progression
    # ======================================================
    st.markdown("### 📈 League Progression")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Moved Up",
        f"{pct_moved_up:.1f}%"
    )

    c2.metric(
        "Stayed Level",
        f"{pct_same_level:.1f}%"
    )

    c3.metric(
        "Moved Down",
        f"{pct_moved_down:.1f}%"
    )

    st.divider()

    # ======================================================
    # ⏳ 3-YEAR CAREER TRAJECTORY SUMMARY
    # ======================================================
    st.divider()
    st.subheader("⏳ After 3 Years...")
    st.caption(
        "Observed player trajectories 3 years after making this career decision.")

    # Calculations based on cohort outcomes
    # Retained in league / country
    pct_still_in_league = pct_stayed_2_years
    # Moved to stronger league
    pct_moved_up_3y = pct_moved_up
    pct_returned_home_3y = pct_returned_home                   # Returned home
    pct_inactive_3y = pct_free_agent + pct_retired             # Free Agent / Retired

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div style='background-color: rgba(255,255,255,0.03); padding: 14px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #2196F3;'>
                <span style='font-size: 18px; color: #4CAF50;'>✓</span> 
                <strong style='font-size: 20px; color: #FFFFFF;'> {pct_still_in_league:.0f}%</strong> 
                <span style='color: #CCCCCC; font-size: 15px;'> were still playing in the destination league/country</span>
            </div>
            <div style='background-color: rgba(255,255,255,0.03); padding: 14px; border-radius: 8px; border-left: 4px solid #00CC66;'>
                <span style='font-size: 18px; color: #4CAF50;'>✓</span> 
                <strong style='font-size: 20px; color: #FFFFFF;'> {pct_moved_up_3y:.0f}%</strong> 
                <span style='color: #CCCCCC; font-size: 15px;'> moved to a stronger league</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style='background-color: rgba(255,255,255,0.03); padding: 14px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #FF9800;'>
                <span style='font-size: 18px; color: #4CAF50;'>✓</span> 
                <strong style='font-size: 20px; color: #FFFFFF;'> {pct_returned_home_3y:.0f}%</strong> 
                <span style='color: #CCCCCC; font-size: 15px;'> returned to their home country</span>
            </div>
            <div style='background-color: rgba(255,255,255,0.03); padding: 14px; border-radius: 8px; border-left: 4px solid #FF4B4B;'>
                <span style='font-size: 18px; color: #4CAF50;'>✓</span> 
                <strong style='font-size: 20px; color: #FFFFFF;'> {pct_inactive_3y:.0f}%</strong> 
                <span style='color: #CCCCCC; font-size: 15px;'> were free agents or retired</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ======================================================
    # Career Exit
    # ======================================================
    st.markdown("### 🚪 Career Exit")

    c1, c2 = st.columns(2)

    c1.metric(
        "Free Agent",
        f"{pct_free_agent:.1f}%"
    )

    c2.metric(
        "Retired",
        f"{pct_retired:.1f}%"
    )

    # ========================================================
    # FEATURE 4: STEPPING STONE ANALYSIS (FALLBACK TO COUNTRY)
    # ========================================================
    st.divider()
    st.subheader("Stepping Stone Analysis")
    st.caption("Where do players usually move next after making this decision?")

    if not outcomes.empty:
        outcomes_copy = outcomes.copy()

        # Hilfsfunktion für Fallback: Zeigt 'Land - Liga' oder nur 'Land' bei fehlender Liga
        def build_destination_label(row):
            country = str(row.get('next_country', '')).strip()
            league = str(row.get('next_league', '')).strip()

            valid_country = pd.notna(row.get('next_country')) and country not in [
                "None", "", "Unknown", "unknown", "nan", "NaN"]
            valid_league = pd.notna(row.get('next_league')) and league not in [
                "None", "", "Unknown", "unknown", "nan", "NaN"]

            if valid_country and valid_league:
                return f"{country} - {league}"
            elif valid_country:
                # FALLBACK: Zeigt nur das Land (z.B. "United States")
                return country
            elif valid_league:
                return league   # FALLBACK: Zeigt nur die Liga, falls Land fehlt
            else:
                return None     # Ausfiltern, falls beides fehlt

        outcomes_copy["next_full_destination"] = outcomes_copy.apply(
            build_destination_label, axis=1)

        # Nur valide Ziele berücksichtigen
        valid_destinations = outcomes_copy["next_full_destination"].dropna()

        if not valid_destinations.empty:
            from collections import Counter
            top_destinations = Counter(valid_destinations).most_common(3)

            for destination_label, count in top_destinations:
                pct = (count / len(outcomes)) * 100

                sub = outcomes_copy[outcomes_copy["next_full_destination"]
                                    == destination_label]
                status_texts = []

                if "became_free_agent" in sub.columns and (sub["became_free_agent"] == 1).any():
                    fa_pct = (sub["became_free_agent"] ==
                              1).sum() / len(sub) * 100
                    status_texts.append(f"{fa_pct:.0f}% Free Agent")

                if "retired_or_inactive" in sub.columns and (sub["retired_or_inactive"] == 1).any():
                    ret_pct = (sub["retired_or_inactive"]
                               == 1).sum() / len(sub) * 100
                    status_texts.append(f"{ret_pct:.0f}% Retired")

                status_suffix = f" ({', '.join(status_texts)})" if status_texts else ""

                st.markdown(
                    f"**{pct:.1f}%** of players used this as a stepping stone to:")
                st.info(f"➡️ **{destination_label}**{status_suffix}")
        else:
            st.info(
                "Not enough subsequent transfer history available to determine typical stepping stones.")
    else:
        st.info("No matching player pathways found.")

    # ========================================================
    # FEATURE 6: AGENT INTELLIGENCE
    # ========================================================
    st.divider()
    st.subheader("Agent Intelligence")
    st.caption(
        "Dominant player agencies representing players within this specific cohort.")

    if not outcomes.empty:
        if "agent" in cohort.columns:
            agent_map = cohort.set_index("player_id")["agent"].to_dict()
            outcomes_with_agents = outcomes.copy()
            outcomes_with_agents["agent"] = outcomes_with_agents["player_id"].map(
                agent_map)
        elif "agent" in master.columns:
            agent_map = master.set_index("player_id")["agent"].to_dict()
            outcomes_with_agents = outcomes.copy()
            outcomes_with_agents["agent"] = outcomes_with_agents["player_id"].map(
                agent_map)
        else:
            outcomes_with_agents = pd.DataFrame()

        if not outcomes_with_agents.empty and "agent" in outcomes_with_agents.columns:
            valid_agents = outcomes_with_agents[
                outcomes_with_agents["agent"].notna() &
                ~outcomes_with_agents["agent"].isin(
                    ["", "None", "unknown", "No Agent", "no agent"])
            ]

            if not valid_agents.empty:
                agent_counts = valid_agents["agent"].value_counts().head(5)

                agent_data = []
                for agent, count in agent_counts.items():
                    agent_data.append({
                        "Agency / Agent": agent,
                        "Analysed Transfers": count
                    })

                agent_df = pd.DataFrame(agent_data)
                st.dataframe(agent_df, use_container_width=True,
                             hide_index=True)

                st.info(
                    "💡 **How to read this:** This shows which agencies have the highest volume of historical "
                    "transfers for this specific type of player decision, indicating their market expertise."
                )
            else:
                st.info(
                    "No agency data available for the tracked players in this cohort.")
        else:
            st.info(
                "Agent variable ('agent') could not be mapped from the cohort data.")
    else:
        st.info("No matching player pathways found.")

    # ========================================================
    # FEATURE 11: LEAGUE ESCAPE RATES
    # ========================================================
    st.divider()
    st.subheader("League Escape Rates")
    st.caption(
        "Where do players actually go afterwards? Historical exit destinations by country.")

    if not outcomes.empty:
        if "next_country" in outcomes.columns:
            next_countries = outcomes["next_country"].dropna()
            next_countries = next_countries[~next_countries.isin(
                ["None", "", "Unknown", "unknown"])]

            total_players = len(outcomes)
            tracked_exits = len(next_countries)
            no_exit_count = total_players - tracked_exits

            escape_data = []

            if no_exit_count > 0:
                stay_pct = (no_exit_count / total_players) * 100
                escape_data.append({
                    "Exit Country": "Stayed in League / No further transfer",
                    "Escape Rate": f"{stay_pct:.1f}%"
                })

            if not next_countries.empty:
                from collections import Counter
                top_countries = Counter(next_countries).most_common(5)

                for country_name, count in top_countries:
                    escape_pct = (count / total_players) * 100
                    escape_data.append({
                        "Exit Country": f"➡️ {country_name}",
                        "Escape Rate": f"{escape_pct:.1f}%"
                    })

            escape_df = pd.DataFrame(escape_data)
            st.dataframe(escape_df, use_container_width=True, hide_index=True)

            st.info(
                "💡 **How to read this:** A high 'Stayed in League' percentage means this competition "
                "can become a career trap. Look for diverse country exits to ensure strong future mobility."
            )
        else:
            st.info(
                "Country exit data ('next_country') not found in the processed dataset.")
    else:
        st.info("No matching player pathways found.")

    # ========================================================
    # ORIGINALE TABELLE
    # ========================================================
    st.divider()
    st.subheader("Comparable Player Outcomes")
    st.caption("Rows with no later transfer recorded...")

    display = (
        outcomes
        .sort_values("transfer_date", ascending=False)
        .drop_duplicates(subset="player_id", keep="first")
    )

    cols_to_show = [
        "player_name",
        "next_country",
        "next_league",
        "last_country",
        "last_league",
        "years_until_next_transfer",
        "next_league_quality_change",
        "outcome_summary",
    ]

    valid_cols = [c for c in cols_to_show if c in display.columns]
    display = display[valid_cols].copy()

    st.dataframe(display, use_container_width=True)
