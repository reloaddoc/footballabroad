import pandas as pd
import streamlit as st


def show(master_df, opta_df=None):
    st.title("🛠️ Master Dataset Overview")
    st.caption(
        "Developer Cockpit: Fast structural overview, data coverage, and health metrics.")

    if master_df.empty:
        st.warning("Master dataset is empty.")
        return

    # If opta_df was not passed, set it to an empty DataFrame
    if opta_df is None:
        opta_df = pd.DataFrame()

    # ==========================================
    # HELPER: AGGREGATE GERMAN AMATEUR LEAGUES
    # ==========================================
    import re

    def group_league_name(league_str):
        if not isinstance(league_str, str) or not league_str:
            return league_str

        s = league_str.lower()

        if "regionalliga" in s:
            return "Germany - Regionalliga (Aggregated)"
        if "oberliga" in s:
            return "Germany - Oberliga (Aggregated)"
        if "landesliga" in s:
            return "Germany - Landesliga (Aggregated)"
        if "verbandsliga" in s:
            return "Germany - Verbandsliga (Aggregated)"

        return league_str

    # ==========================================
    # SIMPLIFIED FILTER SIDEBAR WITH "1999 or older"
    # ==========================================
    st.sidebar.header("Data Overview Filters")

    df = master_df.copy()

    # Apply Aggregated League Names to DataFrame
    if "from_competition" in df.columns:
        df["from_competition_display"] = df["from_competition"].apply(
            group_league_name)
    if "to_competition" in df.columns:
        df["to_competition_display"] = df["to_competition"].apply(
            group_league_name)

    # 1. Season Filter (Helper function to group seasons <= 1999)
    def get_display_season(s):
        try:
            first_part = str(s).split("/")[0].strip()
            yr = int(first_part)
            start_year = 1900 + yr if yr >= 50 else 2000 + yr
            if start_year <= 1999:
                return "1999 or older"
            return str(s)
        except Exception:
            return str(s)

    if "season" in df.columns:
        df["season_display"] = df["season"].apply(get_display_season)
        raw_seasons = df["season_display"].dropna().unique()
        modern_seasons = sorted(
            [s for s in raw_seasons if s != "1999 or older"], reverse=True)
        available_seasons = modern_seasons + \
            (["1999 or older"] if "1999 or older" in raw_seasons else [])
    else:
        available_seasons = []

    selected_seasons = st.sidebar.multiselect(
        "Season", available_seasons, default=[], key="overview_seasons_grouped_v3"
    )

    # 2. Moved From (League) Filter
    if "from_competition_display" in df.columns:
        available_leagues = sorted(
            df["from_competition_display"].dropna().unique())
    else:
        available_leagues = []

    selected_league = st.sidebar.selectbox(
        "Moved From (League)",
        options=["All"] + available_leagues,
        key="overview_moved_from_league"
    )

    # 3. Age Filter
    min_age = int(
        df["age"].min()) if "age" in df.columns and not df["age"].isna().all() else 15
    max_age = int(
        df["age"].max()) if "age" in df.columns and not df["age"].isna().all() else 45
    age_range = st.sidebar.slider(
        "Age Range", min_age, max_age, (min_age, max_age))

    # 4. Nationality Filter
    all_nats = sorted(df["primary_nationality"].dropna(
    ).unique()) if "primary_nationality" in df.columns else []
    selected_nats = st.sidebar.multiselect("Nationality", all_nats, default=[])

    # 5. Position Filter
    all_pos = sorted(df["position_group"].dropna().unique()
                     ) if "position_group" in df.columns else []
    selected_pos = st.sidebar.multiselect("Position", all_pos, default=[])

    # ==========================================
    # APPLY FILTERS TO DATAFRAME
    # ==========================================
    if selected_seasons and "season_display" in df.columns:
        df = df[df["season_display"].isin(selected_seasons)]
    if selected_league != "All" and "from_competition_display" in df.columns:
        df = df[df["from_competition_display"] == selected_league]
    if "age" in df.columns:
        df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]
    if selected_nats and "primary_nationality" in df.columns:
        df = df[df["primary_nationality"].isin(selected_nats)]
    if selected_pos and "position_group" in df.columns:
        df = df[df["position_group"].isin(selected_pos)]

    # ==========================================
    # 1. DATASET HEALTH
    # ==========================================
    st.subheader("📊 Dataset Health")

    from_c = df["from_country_name"].dropna().unique(
    ) if "from_country_name" in df.columns else []
    to_c = df["to_country_name"].dropna().unique(
    ) if "to_country_name" in df.columns else []
    total_countries = len(set(from_c).union(set(to_c)))

    from_l = df["from_competition_display"].dropna().unique(
    ) if "from_competition_display" in df.columns else []
    to_l = df["to_competition_display"].dropna().unique(
    ) if "to_competition_display" in df.columns else []
    total_leagues = len(set(from_l).union(set(to_l)))

    agents_count = df["agent"].dropna(
    ).nunique() if "agent" in df.columns else 0

    h1, h2, h3, h4, h5, h6 = st.columns(6)
    h1.metric("Transfers", f"{len(df):,}")
    h2.metric(
        "Players", f"{df['player_id'].nunique():,}" if "player_id" in df.columns else "—")
    h3.metric(
        "Seasons", f"{df['season'].nunique():,}" if "season" in df.columns else "—")
    h4.metric("Countries", f"{total_countries:,}")
    h5.metric("Competitions", f"{total_leagues:,}")
    h6.metric("Agencies", f"{agents_count:,}")

    st.divider()

    # ==========================================
    # 2. COVERAGE
    # ==========================================
    st.subheader("🔎 Coverage")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("**Season Range**")
        if "season" in df.columns and not df["season"].dropna().empty:
            def parse_season_start(s):
                try:
                    first_part = str(s).split("/")[0].strip()
                    yr = int(first_part)
                    return 1900 + yr if yr >= 50 else 2000 + yr
                except Exception:
                    return 9999

            unique_seasons = df["season"].dropna().unique()
            sorted_seasons = sorted(unique_seasons, key=parse_season_start)
            st.write(f"📅 **{sorted_seasons[0]}** → **{sorted_seasons[-1]}**")
        else:
            st.write("N/A")

    with c2:
        st.markdown("**Age Range**")
        if "age" in df.columns and not df["age"].dropna().empty:
            st.write(
                f"👶 Min: **{int(df['age'].min())}** | 👴 Max: **{int(df['age'].max())}**")
            st.write(f"Ø Age: **{df['age'].mean():.1f} years**")
        else:
            st.write("N/A")

    with c3:
        st.markdown("**Top Nationalities**")
        if "primary_nationality" in df.columns:
            top_nats = df["primary_nationality"].value_counts().head(4)
            for nat, count in top_nats.items():
                st.write(f"• **{nat}**: {count:,}")
        else:
            st.write("N/A")

    with c4:
        st.markdown("**Transfer Types**")
        if "transfer_type" in df.columns:
            types = df["transfer_type"].value_counts().head(4)
            for t_type, count in types.items():
                clean_label = str(t_type).replace(
                    "_TRANSFER", "").replace("_", " ").title()
                st.write(f"• **{clean_label}**: {count:,}")
        else:
            st.write("N/A")

    st.divider()

    # ==========================================
    # 3. GEOGRAPHIC OVERVIEW
    # ==========================================
    st.subheader("📍 Geographic Flows & Corridors")

    country_map = {
        "Deutschland": "Germany", "Schweden": "Sweden", "Niederlande": "Netherlands",
        "Spanien": "Spain", "Frankreich": "France", "Italien": "Italy",
        "Dänemark": "Denmark", "Schottland": "Scotland", "Vereinigte Staaten": "United States",
        "Österreich": "Austria", "Schweiz": "Switzerland", "Belgien": "Belgium",
        "Portugal": "Portugal", "Türkei": "Turkey", "Brasilien": "Brazil"
    }

    g1, g2, g3 = st.columns(3)

    with g1:
        st.markdown("**Top 15 Export Countries**")
        if "from_country_name" in df.columns:
            mapped_from = df["from_country_name"].replace(country_map)
            exp_df = mapped_from.value_counts().head(15).reset_index()
            exp_df.columns = ["Country", "Transfers"]
            st.dataframe(exp_df, use_container_width=True, hide_index=True)

    with g2:
        st.markdown("**Top 15 Import Countries**")
        if "to_country_name" in df.columns:
            mapped_to = df["to_country_name"].replace(country_map)
            imp_df = mapped_to.value_counts().head(15).reset_index()
            imp_df.columns = ["Country", "Transfers"]
            st.dataframe(imp_df, use_container_width=True, hide_index=True)

    with g3:
        st.markdown("**Top 15 Corridors (League ➡️ League)**")
        if "from_competition_display" in df.columns and "to_competition_display" in df.columns:
            corridor_series = df["from_competition_display"] + \
                " ➡️ " + df["to_competition_display"]
            corr_df = corridor_series.value_counts().head(15).reset_index()
            corr_df.columns = ["Corridor", "Transfers"]
            st.dataframe(corr_df, use_container_width=True, hide_index=True)

    st.divider()

    # ==========================================
    # 4. LEAGUE QUALITY (USING PASSED OPTA DF) & 5. AGENTS
    # ==========================================
    l_col, a_col = st.columns(2)

    with l_col:
        st.subheader("📈 League Quality Changes")
        st.caption("Opta score trajectories across transfer moves.")

        if not opta_df.empty and ("league_name" in opta_df.columns or "league" in opta_df.columns) and "opta_score" in opta_df.columns:
            league_col = "league_name" if "league_name" in opta_df.columns else "league"

            opta_dict = {
                str(k).strip().lower(): v
                for k, v in zip(opta_df[league_col], opta_df["opta_score"])
                if pd.notna(k)
            }

            df_opta = df.copy()
            df_opta["from_key"] = df_opta["from_competition"].astype(
                str).str.strip().str.lower()
            df_opta["to_key"] = df_opta["to_competition"].astype(
                str).str.strip().str.lower()

            df_opta["from_opta"] = df_opta["from_key"].map(opta_dict)
            df_opta["to_opta"] = df_opta["to_key"].map(opta_dict)

            valid_opta = df_opta.dropna(subset=["from_opta", "to_opta"]).copy()
            total_opta = len(valid_opta)

            if total_opta > 0:
                up = (valid_opta["to_opta"] > valid_opta["from_opta"]).sum()
                same = (valid_opta["to_opta"] == valid_opta["from_opta"]).sum()
                down = (valid_opta["to_opta"] < valid_opta["from_opta"]).sum()

                pct_up = (up / total_opta) * 100
                pct_same = (same / total_opta) * 100
                pct_down = (down / total_opta) * 100

                avg_diff = (valid_opta["to_opta"] -
                            valid_opta["from_opta"]).mean()

                st.markdown(
                    f"""
                    <div style='background-color: rgba(255,255,255,0.03); padding: 12px; border-radius: 6px; margin-bottom: 8px;'>
                        <strong>↑ Stronger Leagues:</strong> {pct_up:.1f}% ({up:,})
                    </div>
                    <div style='background-color: rgba(255,255,255,0.03); padding: 12px; border-radius: 6px; margin-bottom: 8px;'>
                        <strong>→ Same Level:</strong> {pct_same:.1f}% ({same:,})
                    </div>
                    <div style='background-color: rgba(255,255,255,0.03); padding: 12px; border-radius: 6px; margin-bottom: 8px;'>
                        <strong>↓ Weaker Leagues:</strong> {pct_down:.1f}% ({down:,})
                    </div>
                    <div style='margin-top: 10px;'>
                        Average Quality Gain: <strong>{avg_diff:+.2f} pts</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info(
                    "No matching Opta scores found for current transfer competitions.")
        else:
            st.info("Opta rankings data not available.")

    with a_col:
        st.subheader("💼 Most Active Agencies")
        st.caption("Detailed Agency deals vs. unique represented players.")

        if "agent" in df.columns and "player_id" in df.columns:
            valid_agents_df = df[
                df["agent"].notna() &
                ~df["agent"].isin(
                    ["", "None", "unknown", "No Agent", "no agent"])
            ]

            if not valid_agents_df.empty:
                agent_stats = valid_agents_df.groupby("agent").agg(
                    Deals=("player_id", "count"),
                    Players=("player_id", "nunique")
                ).reset_index().sort_values("Deals", ascending=False).head(10)

                agent_stats.columns = ["Agency", "Deals", "Players"]
                st.dataframe(
                    agent_stats, use_container_width=True, hide_index=True)
            else:
                st.info("No valid agent data available.")
        else:
            st.info("Agent column or Player ID missing.")

    st.divider()

    # ==========================================
    # 6. DATA QUALITY (MISSING VALUES)
    # ==========================================
    st.subheader("⚠️ Data Quality & Missing Values")
    st.caption("Percentage of missing/NaN values across critical columns.")

    total_rows = len(df)
    if total_rows > 0:
        def get_missing_pct(col_name):
            if col_name not in df.columns:
                return "Not present"
            missing_count = df[col_name].isna().sum(
            ) + df[col_name].isin(["None", "", "unknown", "nan", "NaN"]).sum()
            pct = (missing_count / total_rows) * 100
            return f"{pct:.1f}%"

        dq_data = [
            {"Column": "Agent (`agent`)",
             "Missing Share": get_missing_pct("agent")},
            {"Column": "Market Value (`market_value`)", "Missing Share": get_missing_pct(
                "market_value")},
            {"Column": "Nationality (`primary_nationality`)", "Missing Share": get_missing_pct(
                "primary_nationality")},
            {"Column": "Age (`age`)", "Missing Share": get_missing_pct("age")},
            {"Column": "From Competition (`from_competition`)", "Missing Share": get_missing_pct(
                "from_competition")},
            {"Column": "To Competition (`to_competition`)", "Missing Share": get_missing_pct(
                "to_competition")},
        ]

        dq_df = pd.DataFrame(dq_data)
        st.dataframe(dq_df, use_container_width=True, hide_index=True)
