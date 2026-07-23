import streamlit as st

from analytics_ui import add_money_columns, add_share_columns, apply_equal_filter, intelligence_links, load_table, metric_row, page_header, select_filter


page_header(
    "Which agencies dominate a market?",
    "Reveal agency specialisation by destination, corridor, player profile, and transfer behaviour.",
)

agencies = load_table("agency_networks")
master = load_table("master_dataset")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        destination_country = select_filter("Destination country", master["to_country_name"])
    with c2:
        position = select_filter("Position", master["position"])
    with c3:
        nationality = select_filter("Nationality", master["primary_nationality"])

filtered_master = master[master["agent"].notna()].copy()
filtered_master = apply_equal_filter(filtered_master, "to_country_name", destination_country)
filtered_master = apply_equal_filter(filtered_master, "position", position)
filtered_master = apply_equal_filter(filtered_master, "primary_nationality", nationality)

if destination_country != "All" or position != "All" or nationality != "All":
    filtered_master["corridor"] = (
        filtered_master["from_country_name"].fillna("Unknown")
        + " / "
        + filtered_master["from_league"].fillna("Unknown")
        + " -> "
        + filtered_master["to_country_name"].fillna("Unknown")
        + " / "
        + filtered_master["to_league"].fillna("Unknown")
    )
    filtered = (
        filtered_master
        .groupby("agent", dropna=False)
        .agg(
            clients=("player_id", "nunique"),
            transfers=("player_id", "size"),
            average_market_value=("market_value", "mean"),
            average_age=("age", "mean"),
            most_common_corridor=("corridor", lambda values: values.mode().iloc[0] if len(values.mode()) else None),
            international_transfer_share=("international", "mean"),
        )
        .reset_index()
        .sort_values("transfers", ascending=False)
    )
else:
    filtered = agencies.copy()

metric_row([
    ("Agencies", len(filtered)),
    ("Transfers", int(filtered["transfers"].sum()) if not filtered.empty else 0),
    ("Clients", int(filtered["clients"].sum()) if not filtered.empty else 0),
])

st.subheader("Key insight")
if filtered.empty:
    st.info("No agency patterns match this market yet.")
else:
    top = filtered.iloc[0]
    st.success(f"{top['agent']} leads this view with {int(top['transfers']):,} transfers.")

display_cols = ["agent", "clients", "transfers", "most_common_corridor", "average_market_value", "average_age", "international_transfer_share"]
display = filtered.head(30)[[col for col in display_cols if col in filtered.columns]].copy()
display = add_money_columns(display, ["average_market_value"])
display = add_share_columns(display, ["international_transfer_share"])
st.subheader("Top agencies")
st.dataframe(display, hide_index=True, use_container_width=True)

intelligence_links()
