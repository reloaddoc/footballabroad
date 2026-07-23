import streamlit as st

from analytics_ui import add_money_columns, apply_equal_filter, intelligence_links, load_table, metric_row, page_header, select_filter


page_header(
    "How do careers move between leagues?",
    "Explore league-to-league flows that can later power network graphs and Sankey views.",
)

flows = load_table("league_flows")
master = load_table("master_dataset")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        starting_country = select_filter("Starting country", flows["from_country"])
    filtered = apply_equal_filter(flows, "from_country", starting_country)
    with c2:
        starting_league = select_filter("Starting league", filtered["from_league"])
    with c3:
        nationality = select_filter("Nationality", master["primary_nationality"])

filtered = apply_equal_filter(filtered, "from_league", starting_league)
examples = master.copy()
examples = apply_equal_filter(examples, "from_country_name", starting_country)
examples = apply_equal_filter(examples, "from_league", starting_league)
examples = apply_equal_filter(examples, "primary_nationality", nationality)

if nationality != "All":
    filtered = (
        examples
        .groupby(["from_country_name", "from_league", "to_country_name", "to_league"], dropna=False)
        .agg(
            moves=("player_id", "size"),
            average_age=("age", "mean"),
            average_market_value=("market_value", "mean"),
            average_fee=("fee", "mean"),
            unique_players=("player_id", "nunique"),
        )
        .reset_index()
        .rename(columns={"from_country_name": "from_country", "to_country_name": "to_country"})
        .sort_values("moves", ascending=False)
    )

metric_row([
    ("League flows", len(filtered)),
    ("Moves", int(filtered["moves"].sum()) if not filtered.empty else 0),
    ("Players", int(filtered["unique_players"].sum()) if "unique_players" in filtered else 0),
])

st.subheader("Most common next league")
if filtered.empty:
    st.info("No league flows match this question yet.")
else:
    top = filtered.iloc[0]
    st.success(f"{top['from_league']} most often flows into {top['to_league']} in this view.")

display = filtered.head(40)[["from_country", "from_league", "to_country", "to_league", "moves", "average_age", "average_market_value", "average_fee"]].copy()
display = add_money_columns(display, ["average_market_value", "average_fee"])
st.subheader("Ordered flow table")
st.dataframe(display, hide_index=True, use_container_width=True)

if not filtered.empty:
    st.bar_chart(filtered.head(12).set_index("to_league")["moves"])

intelligence_links()
