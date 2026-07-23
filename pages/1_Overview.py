import streamlit as st

from analytics_ui import load_table, metric_row, page_header


page_header(
    "Football Career Intelligence",
    "Understand how football careers actually happen. Explore historical transfers, career pathways, stepping clubs, league networks, and player archetypes.",
)

master = load_table("master_dataset")
transfer_corridors = load_table("transfer_corridors")
stepping_clubs = load_table("stepping_clubs")
league_flows = load_table("league_flows")
agency_networks = load_table("agency_networks")
player_archetypes = load_table("player_archetypes")

metric_row([
    ("Transfers analysed", len(master)),
    ("Transfer corridors", len(transfer_corridors)),
    ("Stepping clubs", len(stepping_clubs)),
    ("Player archetypes", len(player_archetypes)),
    ("Agencies", len(agency_networks)),
    ("League networks", len(league_flows)),
])

st.divider()

st.subheader("Start with a career question")

cards = [
    (
        "Where should I move next?",
        "Find comparable careers and see where similar players actually went.",
        "pages/7_Career_Navigator.py",
        "Open Career Navigator",
    ),
    (
        "Where do players from this league usually go?",
        "Explore recurring corridors between countries, leagues, and clubs.",
        "pages/3_Transfer_Corridors.py",
        "Explore Transfer Corridors",
    ),
    (
        "Which clubs consistently export players?",
        "Identify gateway clubs and the markets they connect to.",
        "pages/4_Stepping_Clubs.py",
        "Find Stepping Clubs",
    ),
    (
        "Which agencies dominate a market?",
        "Understand agency specialisation by corridor, country, and player profile.",
        "pages/6_Agency_Intelligence.py",
        "Explore Agencies",
    ),
    (
        "What happened to players like me?",
        "Use archetypes to turn a player profile into historical next-step intelligence.",
        "pages/8_Players_Like_Me.py",
        "Find Players Like Me",
    ),
]

for first, second in zip(cards[::2], cards[1::2]):
    left, right = st.columns(2)
    for column, card in [(left, first), (right, second)]:
        with column:
            with st.container(border=True):
                st.markdown(f"### {card[0]}")
                st.write(card[1])
                st.page_link(card[2], label=card[3])

if len(cards) % 2:
    with st.container(border=True):
        title, body, path, label = cards[-1]
        st.markdown(f"### {title}")
        st.write(body)
        st.page_link(path, label=label)

st.divider()

st.subheader("Most active transfer corridors")
top_corridors = transfer_corridors.head(8).copy()
top_corridors["route"] = (
    top_corridors["from_country"].fillna("Unknown")
    + " / "
    + top_corridors["from_league"].fillna("Unknown")
    + " -> "
    + top_corridors["to_country"].fillna("Unknown")
    + " / "
    + top_corridors["to_league"].fillna("Unknown")
)

st.bar_chart(
    top_corridors.set_index("route")["transfers"]
)
