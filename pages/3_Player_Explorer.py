import streamlit as st

from analytics_ui import load_table, page_header


page_header(
    "Find a player career",
    "Search individual players and inspect their historical transfer timeline.",
)

master = load_table("master_dataset")

query = st.text_input("Search player", placeholder="Type a player name...")

if not query:
    st.info("Search for a player to view their career timeline.")
else:
    matches = master[
        master["full_name"]
        .fillna("")
        .str.contains(query, case=False, regex=False)
    ]

    players = sorted(matches["full_name"].dropna().unique())
    if not players:
        st.warning("No players found.")
    else:
        selected_player = st.selectbox("Player", players)
        player = master[master["full_name"] == selected_player].sort_values("date")

        c1, c2, c3 = st.columns(3)
        c1.metric("Transfers", len(player))
        c2.metric("Career length", int(player["career_length"].max()) if player["career_length"].notna().any() else "-")
        c3.metric("International moves", int(player["international_moves"].max()) if player["international_moves"].notna().any() else "-")

        st.subheader("Career timeline")
        cols = ["season", "age", "from_club_name", "from_league", "to_club_name", "to_league", "transfer_type", "market_value", "fee"]
        st.dataframe(player[cols], hide_index=True, use_container_width=True)
