import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_data, sidebar_filters
from config import PLOT_TEMPLATE

# ----------------------------------------------------
# Load
# ----------------------------------------------------

df = load_data()
df = sidebar_filters(df)

# ----------------------------------------------------
# Sample
# ----------------------------------------------------

df = df[df["international"]].copy()

TARGET_MARKETS = [

    "Thailand",

    "Malaysia",

    "Indonesien",

    "Vietnam",

    "Singapur",

    "Philippinen",

    "Hongkong",

    "Indien",

    "Südkorea",

    "Finnland",

    "Kanada",

    "Puerto Rico",

]

df = df[
    df["to_country_name"].isin(
        TARGET_MARKETS
    )
]

# ausreichend große Märkte

MIN_MARKET_TRANSFERS = 20

market_counts = (

    df["to_country_name"]

    .value_counts()

)

valid_markets = market_counts[
    market_counts >= MIN_MARKET_TRANSFERS
].index

df = df[
    df["to_country_name"].isin(valid_markets)
]

# Herkunftsvereine

df = df[
    ~df["from_club_name"].isin(
        [
            "Vereinslos",
            "Unbekannt"
        ]
    )
]

st.title("🧪 H3 – Gateway Clubs")

st.markdown("""

### Research Question

Do gateway clubs repeatedly facilitate transfers into emerging football markets?

This analysis investigates whether a relatively small number of clubs
regularly function as stepping stones into specific international
football markets.

""")

st.divider()

# ----------------------------------------------------
# KPIs
# ----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "Transfers",

    len(df)

)

c2.metric(

    "Players",

    df.player_id.nunique()

)

c3.metric(

    "Source Clubs",

    df.from_club.nunique()

)

c4.metric(

    "Markets",

    df.to_country_name.nunique()

)

st.divider()

# ----------------------------------------------------
# Destination Market
# ----------------------------------------------------

selected_market = st.selectbox(

    "Destination Market",

    sorted(valid_markets)

)

market_df = df[
    df["to_country_name"] == selected_market
]

# ----------------------------------------------------
# Market KPIs
# ----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "Transfers",

    len(market_df)

)

c2.metric(

    "Players",

    market_df.player_id.nunique()

)

c3.metric(

    "Source Clubs",

    market_df.from_club.nunique()

)

c4.metric(

    "Origin Countries",

    market_df.from_country_name.nunique()

)

st.divider()

# ----------------------------------------------------
# Gateway Club Ranking
# ----------------------------------------------------

st.header(f"Gateway Clubs for {selected_market}")

club_market = (

    market_df

    .groupby(

        [

            "from_club",

            "from_club_name"

        ]

    )

    .agg(

        Transfers=("player_id", "count"),

        Players=("player_id", "nunique"),

        Avg_Age=("age", "mean"),

        Top_Nationality=(

            "primary_nationality",

            lambda x: x.mode().iat[0]
            if not x.mode().empty
            else None

        ),

        Top_Position=(

            "position",

            lambda x: x.mode().iat[0]
            if not x.mode().empty
            else None

        )

    )

    .reset_index()

    .sort_values(

        "Transfers",

        ascending=False

    )

)

# ----------------------------------------------------
# Gateway Index
# ----------------------------------------------------

international_club = (

    df

    .groupby("from_club")

    .size()

    .rename("International_Transfers")

)

club_market = club_market.merge(

    international_club,

    on="from_club",

    how="left"

)

club_market["Gateway Index (%)"] = (

    club_market["Transfers"]

    /

    club_market["International_Transfers"]

    * 100

).round(1)

club_market["Market Share (%)"] = (

    club_market["Transfers"]

    /

    club_market["Transfers"].sum()

    * 100

).round(1)

# ----------------------------------------------------
# Ranking
# ----------------------------------------------------

st.dataframe(

    club_market,

    width="stretch",

    height=450

)

# ----------------------------------------------------
# Top Gateway Clubs
# ----------------------------------------------------

fig = px.bar(

    club_market.head(20),

    x="Transfers",

    y="from_club_name",

    orientation="h",

    template=PLOT_TEMPLATE,

    title=f"Top Gateway Clubs into {selected_market}"

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="gateway_clubs"

)

st.divider()

# ----------------------------------------------------
# Gateway Index
# ----------------------------------------------------

st.header("Gateway Index")

fig = px.bar(

    club_market.head(20),

    x="Gateway Index (%)",

    y="from_club_name",

    orientation="h",

    template=PLOT_TEMPLATE,

    title="Gateway Index"

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="gateway_index"

)

st.divider()

# ----------------------------------------------------
# Market Share
# ----------------------------------------------------

st.header("Market Share")

fig = px.pie(

    club_market.head(10),

    names="from_club_name",

    values="Transfers",

    hole=0.45,

    template=PLOT_TEMPLATE,

    title=f"Top Source Clubs into {selected_market}"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="gateway_market_share"

)

st.divider()

# ----------------------------------------------------
# Preliminary Evidence
# ----------------------------------------------------

leader = club_market.iloc[0]

top5_share = club_market.head(5)["Market Share (%)"].sum()

st.success(f"""

### Preliminary Evidence

The strongest gateway club into **{selected_market}** is

**{leader['from_club_name']}**

with

- **{leader['Transfers']} international transfers**
- **{leader['Players']} unique players**
- **{leader['Market Share (%)']:.1f}% market share**
- **Gateway Index:** **{leader['Gateway Index (%)']:.1f}%**

Most frequently transferred player profile

- Nationality: **{leader['Top_Nationality']}**
- Position: **{leader['Top_Position']}**

The five largest gateway clubs account for

**{top5_share:.1f}%**

of all documented international transfers into **{selected_market}**.

This provides preliminary evidence that certain clubs repeatedly function
as gateways into this football market.

""")

st.divider()

# ----------------------------------------------------
# Gateway Club Explorer
# ----------------------------------------------------

st.header("Gateway Club Explorer")

clubs = sorted(

    club_market["from_club_name"]

    .dropna()

    .unique()

)

selected_club = st.selectbox(

    "Gateway Club",

    clubs

)

club_df = market_df[
    market_df["from_club_name"] == selected_club
]

st.divider()

# ----------------------------------------------------
# Club KPIs
# ----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Transfers",
    len(club_df)
)

c2.metric(
    "Players",
    club_df.player_id.nunique()
)

c3.metric(
    "Nationalities",
    club_df.primary_nationality.nunique()
)

c4.metric(
    "Origin Countries",
    club_df.from_country_name.nunique()
)

st.divider()

# ----------------------------------------------------
# Nationalities
# ----------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Nationalities")

    nationality = (

        club_df["primary_nationality"]

        .fillna("Unknown")

        .value_counts()

        .reset_index()

    )

    nationality.columns = [

        "Nationality",

        "Players"

    ]

    st.dataframe(

        nationality,

        width="stretch",

        height=300

    )

    fig = px.bar(

        nationality,

        x="Players",

        y="Nationality",

        orientation="h",

        template=PLOT_TEMPLATE

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    st.plotly_chart(

        fig,

        width="stretch",

        key="club_nat"

    )

with right:

    st.subheader("Positions")

    position = (

        club_df["position"]

        .fillna("Unknown")

        .value_counts()

        .reset_index()

    )

    position.columns = [

        "Position",

        "Players"

    ]

    st.dataframe(

        position,

        width="stretch",

        height=300

    )

    fig = px.bar(

        position,

        x="Players",

        y="Position",

        orientation="h",

        template=PLOT_TEMPLATE

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    st.plotly_chart(

        fig,

        width="stretch",

        key="club_pos"

    )

st.divider()

# ----------------------------------------------------
# Previous Leagues
# ----------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Origin Countries")

    origin = (

        club_df["from_country_name"]

        .fillna("Unknown")

        .value_counts()

        .reset_index()

    )

    origin.columns = [

        "Country",

        "Transfers"

    ]

    st.dataframe(

        origin,

        width="stretch",

        height=300

    )

with right:

    st.subheader("Origin Leagues")

    leagues = (

        club_df["from_league"]

        .fillna("Unknown")

        .value_counts()

        .reset_index()

    )

    leagues.columns = [

        "League",

        "Transfers"

    ]

    st.dataframe(

        leagues,

        width="stretch",

        height=300

    )

st.divider()

# ----------------------------------------------------
# Age Distribution
# ----------------------------------------------------

st.subheader("Age Distribution")

fig = px.histogram(

    club_df,

    x="age",

    nbins=12,

    template=PLOT_TEMPLATE

)

st.plotly_chart(

    fig,

    width="stretch",

    key="club_age"

)

st.divider()

# ----------------------------------------------------
# Destination Clubs
# ----------------------------------------------------

st.subheader("Destination Clubs")

destination = (

    club_df["to_club_name"]

    .value_counts()

    .reset_index()

)

destination.columns = [

    "Club",

    "Transfers"

]

st.dataframe(

    destination,

    width="stretch",

    height=350

)

fig = px.bar(

    destination,

    x="Transfers",

    y="Club",

    orientation="h",

    template=PLOT_TEMPLATE

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="destination_clubs"

)

st.divider()

# ----------------------------------------------------
# Hypothesis Evaluation
# ----------------------------------------------------

st.header("Hypothesis Evaluation")

# ----------------------------------------------------
# Market Statistics
# ----------------------------------------------------

total_transfers = len(market_df)

total_clubs = club_market["from_club"].nunique()

largest_share = club_market["Market Share (%)"].max()

top3_share = club_market.head(3)["Market Share (%)"].sum()

top5_share = club_market.head(5)["Market Share (%)"].sum()

gateway_mean = club_market["Gateway Index (%)"].mean()

gateway_max = club_market["Gateway Index (%)"].max()

# ----------------------------------------------------
# Gateway Score
# ----------------------------------------------------

club_market["Gateway Score"] = (

    0.6 * club_market["Gateway Index (%)"]

    +

    0.4 * club_market["Market Share (%)"]

)

club_market = club_market.sort_values(

    "Gateway Score",

    ascending=False

)

best = club_market.iloc[0]

# ----------------------------------------------------
# Score Interpretation
# ----------------------------------------------------

score = best["Gateway Score"]

if score >= 60:

    classification = "Strong Gateway Club"

elif score >= 35:

    classification = "Moderate Gateway Club"

else:

    classification = "Occasional Gateway Club"

# ----------------------------------------------------
# KPIs
# ----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "Largest Club Share",

    f"{largest_share:.1f}%"

)

c2.metric(

    "Top 3 Clubs",

    f"{top3_share:.1f}%"

)

c3.metric(

    "Top 5 Clubs",

    f"{top5_share:.1f}%"

)

c4.metric(

    "Mean Gateway Index",

    f"{gateway_mean:.1f}%"

)

st.divider()

# ----------------------------------------------------
# Best Gateway Club
# ----------------------------------------------------

st.subheader("Highest Ranked Gateway Club")

summary = pd.DataFrame({

    "Metric": [

        "Club",

        "Transfers",

        "Players",

        "Market Share",

        "Gateway Index",

        "Gateway Score",

        "Classification"

    ],

    "Value": [

        best["from_club_name"],

        int(best["Transfers"]),

        int(best["Players"]),

        f"{best['Market Share (%)']:.1f}%",

        f"{best['Gateway Index (%)']:.1f}%",

        f"{best['Gateway Score']:.1f}",

        classification

    ]

})

st.dataframe(

    summary,

    width="stretch",

    hide_index=True

)

st.divider()

# ----------------------------------------------------
# Scientific Interpretation
# ----------------------------------------------------

supported = top5_share >= 40

if supported:

    verdict = "SUPPORTED"

else:

    verdict = "PARTIALLY SUPPORTED"

st.success(f"""

## Hypothesis H3

### {verdict}

For the selected market (**{selected_market}**):

- Total international transfers: **{total_transfers}**
- Source clubs: **{total_clubs}**
- Largest source club share: **{largest_share:.1f}%**
- Top five clubs account for **{top5_share:.1f}%** of all transfers.

The highest-ranked gateway club is

**{best['from_club_name']}**

with

- **{best['Transfers']} transfers**
- **Gateway Index: {best['Gateway Index (%)']:.1f}%**
- **Gateway Score: {best['Gateway Score']:.1f}**
- Classification: **{classification}**

These findings indicate that transfers into **{selected_market}**
are not evenly distributed across all clubs. Instead, a relatively
small number of clubs repeatedly facilitate player movements into
this football market.

""")

st.divider()

st.caption("FootballAbroad Research – Hypothesis H3")
