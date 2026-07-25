import streamlit as st

from analytics_ui import (
    add_money_columns,
    add_share_columns,
    apply_equal_filter,
    intelligence_links,
    load_table,
    metric_row,
    page_header,
    select_filter,
)


page_header(
    "Where do players from this league usually go?",
    "Explore recurring transfer corridors between countries and leagues.",
)

corridors = load_table("transfer_corridors")


master = load_table("master_dataset")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        origin_country = select_filter(
            "Origin country", corridors["from_country"]
        )

    filtered = apply_equal_filter(corridors, "from_country", origin_country)

    with c2:
        origin_league = select_filter(
            "Origin league",
            filtered["from_league"],
        )

    with c3:
        nationality = select_filter(
            "Nationality",
            master["primary_nationality"],
        )

    filtered = apply_equal_filter(filtered, "from_league", origin_league)

    examples = master.copy()
    examples = apply_equal_filter(
        examples, "from_country_name", origin_country
    )
    examples = apply_equal_filter(examples, "from_league", origin_league)
    examples = apply_equal_filter(examples, "primary_nationality", nationality)

    c4, c5 = st.columns(2)
    with c4:
        position = select_filter("Position", examples["position"])
    with c5:
        ages = examples["age"].dropna()
        age_range = (
            st.slider(
                "Age range",
                int(ages.min()),
                int(ages.max()),
                (18, 30),
            )
            if len(ages)
            else None
        )

    examples = apply_equal_filter(examples, "position", position)
    if age_range:
        examples = examples[
            examples["age"].between(age_range[0], age_range[1])
        ]

if not examples.empty and (nationality != "All" or position != "All" or age_range):
    filtered = (
        examples
        .groupby(["from_country_name", "from_league", "to_country_name", "to_league"], dropna=False)
        .agg(
            transfers=("player_id", "size"),
            average_age=("age", "mean"),
            average_fee=("fee", "mean"),
            international_share=("international", "mean"),
            unique_players=("player_id", "nunique"),
        )
        .reset_index()
        .rename(columns={
            "from_country_name": "from_country",
            "to_country_name": "to_country",
        })
        .sort_values("transfers", ascending=False)
    )

metric_row([
    ("Corridors found", len(filtered)),
    ("Transfers", int(filtered["transfers"].sum())
     if not filtered.empty else 0),
    ("Players", int(filtered["unique_players"].sum())
     if "unique_players" in filtered else 0),
])

st.subheader("Key insight")
if filtered.empty:
    st.info("No historical corridors match these refinements yet.")
else:
    top = filtered.iloc[0]
    st.success(
        f"The strongest corridor is {top['from_league']} to {top['to_league']} with {int(top['transfers']):,} transfers."
    )

display = filtered.head(25)[[
    "to_country",
    "to_league",
    "transfers",
    "average_age",
    "average_fee",
    "international_share",
]].copy()
display = add_share_columns(display, ["international_share"])

st.subheader("Ranked corridors")
st.dataframe(display, hide_index=True, use_container_width=True)

if not filtered.empty:
    st.bar_chart(filtered.head(12).set_index("to_league")["transfers"])

with st.expander("Example players behind this question"):
    player_cols = ["full_name", "age", "position", "primary_nationality",
                   "from_club_name", "to_club_name", "to_league"]
    st.dataframe(examples[player_cols].drop_duplicates().head(
        50), hide_index=True, use_container_width=True)

intelligence_links()
