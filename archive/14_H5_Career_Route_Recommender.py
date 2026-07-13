import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_data
from config import PLOT_TEMPLATE

# ----------------------------------------------------
# Load
# ----------------------------------------------------

df = load_data()

df = df[df["international"]].copy()

required = [

    "nationality",

    "position",

    "age",

    "to_country_name"

]

df = df.dropna(subset=required)

# ----------------------------------------------------
# Header
# ----------------------------------------------------

st.title("🚀 H5 – Career Recommendation Engine")

st.markdown("""

### Research Question

Can historical transfer data be transformed into actionable
career recommendations for professional football players?

This prototype demonstrates how historical transfer patterns
can be converted into personalised career recommendations.

""")

st.divider()

# ----------------------------------------------------
# Describe Your Player
# ----------------------------------------------------

st.header("Describe Your Player")

left, right = st.columns(2)

with left:

    nationalities = ["All"] + sorted(

        df["primary_nationality"]

        .dropna()

        .unique()

    )

nationality = st.selectbox(

    "Nationality",

    nationalities

)

position = st.selectbox(

    "Position",

    ["All"]

    +

    sorted(

        df["position"]

        .dropna()

        .unique()

    )

)

league_options = sorted(

    df["from_league"]

    .dropna()

    .unique()

)

origin_leagues = st.multiselect(

    "Current League(s)",

    league_options,

    default=[]

)

with right:

    minimum = int(df["age"].min())

    maximum = int(df["age"].max())

    age = st.slider(

        "Age",

        minimum,

        maximum,

        (21, 27)

    )


# ----------------------------------------------------
# Build Profile
# ----------------------------------------------------

profile = df.copy()

# Nationality
if nationality != "All":

    profile = profile[

        profile["nationality"]

        .fillna("")

        .str.contains(

            nationality,

            regex=False

        )

    ]

# Age
profile = profile[

    profile["age"].between(

        age[0],

        age[1]

    )

]

# Position
if position != "All":

    profile = profile[

        profile["position"] == position

    ]

# Current League(s)
if origin_leagues:

    profile = profile[

        profile["from_league"]

        .isin(origin_leagues)

    ]

# Remove invalid destination countries
profile = profile[

    ~profile["to_country_name"]

    .fillna("")

    .isin(

        [

            "Vereinslos",

            "Unknown",

            "Unbekannt"

        ]

    )

]

# ----------------------------------------------------
# KPIs
# ----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "Historical Transfers",

    len(profile)

)

c2.metric(

    "Historical Players",

    profile.player_id.nunique()

)

c3.metric(

    "Destination Countries",

    profile.to_country_name.nunique()

)

c4.metric(

    "Agencies",

    profile.agent.nunique()

)

st.divider()

if profile.empty:

    st.warning(

        "No comparable historical players found."

    )

    st.stop()

    # ----------------------------------------------------
# Recommendation Engine
# ----------------------------------------------------

st.header("Career Recommendations")

recommendations = (

    profile

    .groupby("to_country_name")

    .agg(

        Transfers=("player_id", "count"),

        Players=("player_id", "nunique"),

        Avg_Age=("age", "mean"),

        Agencies=("agent", "nunique"),

        Clubs=("to_club_name", "nunique")

    )

    .reset_index()

)

# ----------------------------------------------------
# Career Score
# ----------------------------------------------------

recommendations["Transfer Score"] = (

    recommendations["Transfers"]

    /

    recommendations["Transfers"].max()

    * 40

)

recommendations["Player Score"] = (

    recommendations["Players"]

    /

    recommendations["Players"].max()

    * 30

)

recommendations["Agency Score"] = (

    recommendations["Agencies"]

    /

    recommendations["Agencies"].max()

    * 15

)

recommendations["Club Score"] = (

    recommendations["Clubs"]

    /

    recommendations["Clubs"].max()

    * 15

)

recommendations["Career Score"] = (

    recommendations["Transfer Score"]

    +

    recommendations["Player Score"]

    +

    recommendations["Agency Score"]

    +

    recommendations["Club Score"]

).round(1)

recommendations = recommendations.sort_values(

    "Career Score",

    ascending=False

)

# ----------------------------------------------------
# Top Recommendations
# ----------------------------------------------------

st.subheader("Recommended Markets")

st.dataframe(

    recommendations[

        [

            "to_country_name",

            "Career Score",

            "Transfers",

            "Players",

            "Agencies",

            "Clubs"

        ]

    ],

    width="stretch",

    height=450

)

# ----------------------------------------------------
# Ranking
# ----------------------------------------------------

fig = px.bar(

    recommendations.head(10),

    x="Career Score",

    y="to_country_name",

    orientation="h",

    text="Career Score",

    template=PLOT_TEMPLATE,

    title="Top Career Recommendations"

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="career_recommendations"

)

st.divider()

# ----------------------------------------------------
# Best Recommendation
# ----------------------------------------------------

best = recommendations.iloc[0]

st.success(f"""

# Best Recommendation

## {best['to_country_name']}

Career Score: **{best['Career Score']:.1f}/100**

Based on comparable historical players:

- **{best['Transfers']} international transfers**
- **{best['Players']} unique players**
- **{best['Agencies']} active agencies**
- **{best['Clubs']} destination clubs**

This market currently represents the strongest historical career destination
for players matching the selected profile.

""")

st.divider()

# ----------------------------------------------------
# Why this Recommendation?
# ----------------------------------------------------

st.header("Why this Recommendation?")

selected_market = st.selectbox(

    "Inspect Recommendation",

    recommendations["to_country_name"]

)

market = profile[

    profile["to_country_name"] == selected_market

].copy()

# ----------------------------------------------------
# Agencies
# ----------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Top Agencies")

    agencies = (

        market

        .groupby("agent")

        .agg(

            Transfers=("player_id", "count"),

            Players=("player_id", "nunique")

        )

        .reset_index()

        .sort_values(

            "Transfers",

            ascending=False

        )

    )

    st.dataframe(

        agencies,

        width="stretch",

        height=300

    )

with right:

    st.subheader("Gateway Clubs")

    gateways = (

        market

        .groupby("from_club_name")

        .agg(

            Transfers=("player_id", "count"),

            Players=("player_id", "nunique")

        )

        .reset_index()

        .sort_values(

            "Transfers",

            ascending=False

        )

    )

    st.dataframe(

        gateways,

        width="stretch",

        height=300

    )

st.divider()

# ----------------------------------------------------
# Comparable Historical Players
# ----------------------------------------------------

st.subheader("Comparable Historical Players")

st.caption(

    f"{profile['player_id'].nunique()} comparable players found"

)

all_players = (

    profile[

        [

            "full_name",

            "age",

            "position",

            "from_club_name",

            "from_league",

            "to_club_name",

            "to_country_name",

            "agent"

        ]

    ]

    .drop_duplicates()

    .sort_values(

        "full_name"

    )

)

st.dataframe(

    all_players,

    width="stretch",

    height=450,

    hide_index=True

)

st.divider()

# ----------------------------------------------------
# Players by Recommended Market
# ----------------------------------------------------

st.subheader("Players by Recommended Market")

selected_market = st.selectbox(

    "Recommendation",

    recommendations["to_country_name"]

)

market = profile[

    profile["to_country_name"] == selected_market

]

st.caption(

    f"{market['player_id'].nunique()} comparable players moved to {selected_market}"

)

market_players = (

    market[

        [

            "full_name",

            "age",

            "position",

            "from_club_name",

            "to_club_name",

            "agent"

        ]

    ]

    .drop_duplicates()

    .sort_values(

        "full_name"

    )

)

st.subheader("Comparable Career Profiles")

for _, row in market_players.iterrows():

    with st.container(border=True):

        left, right = st.columns([3, 1])

        with left:

            st.markdown(f"### {row['full_name']}")

            st.write(f"**Age:** {int(row['age'])}")

            st.write(f"**Position:** {row['position']}")

            st.write("#### Career Route")

            st.markdown(

                f"""
**{row['from_club_name']}**

⬇️

**{row['to_club_name']}**

({selected_market})
"""
            )

        with right:

            st.metric(

                "Agent",

                row["agent"]

            )

st.divider()

# ----------------------------------------------------
# Origin Leagues
# ----------------------------------------------------

origin = (

    market

    .groupby("from_league")

    .agg(

        Transfers=("player_id", "count")

    )

    .reset_index()

    .sort_values(

        "Transfers",

        ascending=False

    )

)

fig = px.bar(

    origin.head(15),

    x="Transfers",

    y="from_league",

    orientation="h",

    template=PLOT_TEMPLATE,

    title="Most Common Origin Leagues"

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="origin_leagues"

)

st.divider()

# ----------------------------------------------------
# Recommendation Summary
# ----------------------------------------------------

top_agent = agencies.iloc[0]["agent"] if len(agencies) else "-"

top_gateway = gateways.iloc[0]["from_club_name"] if len(gateways) else "-"

st.success(f"""

## Recommendation Summary

The recommendation for **{selected_market}** is supported by

- **{len(market)} historical transfers**
- **{market['player_id'].nunique()} comparable players**
- **{market['agent'].nunique()} agencies**
- **{market['to_club_name'].nunique()} destination clubs**

Typical pathway:

**{top_gateway}**

↓

**{selected_market}**

Most active agency:

**{top_agent}**

""")

st.divider()

# ----------------------------------------------------
# FootballAbroad Recommendation
# ----------------------------------------------------

st.header("FootballAbroad Recommendation")

recommendation = recommendations.iloc[0]

score = recommendation["Career Score"]

if score >= 80:

    stars = "★★★★★"
    level = "Excellent Match"

elif score >= 60:

    stars = "★★★★☆"
    level = "Strong Match"

elif score >= 40:

    stars = "★★★☆☆"
    level = "Moderate Match"

else:

    stars = "★★☆☆☆"
    level = "Limited Evidence"

st.success(f"""

# {stars}

## Recommended Destination

### {recommendation['to_country_name']}

### Career Score

# **{score:.1f}/100**

**{level}**

---

### Why?

FootballAbroad identified this destination because historical players
with a similar profile most frequently transferred to this market.

Supporting evidence:

- **{recommendation['Transfers']} historical transfers**
- **{recommendation['Players']} comparable players**
- **{recommendation['Agencies']} agencies**
- **{recommendation['Clubs']} destination clubs**

The recommendation is based entirely on historical international
transfer patterns contained in the FootballAbroad database.

""")

st.divider()

st.subheader("Top 5 Recommended Markets")

ranking = recommendations.head(5).copy()

ranking.insert(

    0,

    "Rank",

    range(1, len(ranking)+1)

)

st.dataframe(

    ranking[

        [

            "Rank",

            "to_country_name",

            "Career Score",

            "Transfers",

            "Players"

        ]

    ],

    width="stretch",

    hide_index=True

)

st.divider()

st.header("Hypothesis Evaluation")

supported = recommendation["Career Score"] >= 60

verdict = "SUPPORTED" if supported else "PARTIALLY SUPPORTED"

st.success(f"""

## Hypothesis H5

### {verdict}

Historical transfer networks can be transformed into practical career
recommendations.

For the selected player profile, FootballAbroad identified

## **{recommendation['to_country_name']}**

as the strongest destination market.

The recommendation is supported by

- historical transfer frequency,
- comparable player careers,
- destination club diversity,
- agency activity.

These findings demonstrate that historical transfer data can provide
actionable decision support for professional football players and their
advisors.

""")

st.divider()

st.caption("FootballAbroad MVP – Career Recommendation Engine")
