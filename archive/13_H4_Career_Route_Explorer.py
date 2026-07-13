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
# International Transfers Only
# ----------------------------------------------------

df = df[df["international"]].copy()

st.write("Nach international:", len(df))

st.write(
    "Spieler mit deutscher Nationalität:",
    df["nationality"]
    .fillna("")
    .str.contains("Deutschland", regex=False)
    .sum()
)

st.write(
    "Transfers aus Deutschland:",
    (df["from_country_name"] == "Deutschland").sum()
)

st.write("Internationale Transfers:", len(df))

st.write(
    "Deutsche Spieler:",
    len(df[df["primary_nationality"] == "Deutschland"])
)

st.write("Internationale Transfers:", len(df))

st.write(
    "Deutsche Spieler:",
    len(df[df["primary_nationality"] == "Deutschland"])
)

# Nur vollständige Datensätze

required = [

    "nationality",

    "position",

    "age",

    "to_country_name"

]

df = df.dropna(subset=required)

st.write("Nach dropna:", len(df))

st.write(
    "Spieler mit deutscher Nationalität nach dropna:",
    df["nationality"]
    .fillna("")
    .str.contains("Deutschland", regex=False)
    .sum()
)

st.write("Nach dropna:", len(df))

st.write(
    "Deutsche nach dropna:",
    len(df[df["primary_nationality"] == "Deutschland"])
)


# ----------------------------------------------------
# Age Groups
# ----------------------------------------------------

df["Age Group"] = pd.cut(

    df["age"],

    bins=[15, 20, 24, 28, 32, 40],

    labels=[

        "16-20",

        "21-24",

        "25-28",

        "29-32",

        "33+"

    ]

)

# ----------------------------------------------------
# Career Route
# ----------------------------------------------------

df["Career Route"] = (

    df["primary_nationality"]

    + " → "

    + df["from_country_name"]

    + " → "

    + df["from_league"]

    + " → "

    + df["position"]

    + " → "

    + df["Age Group"].astype(str)

    + " → "

    + df["to_country_name"]

)

# ----------------------------------------------------
# Header
# ----------------------------------------------------

st.title("🧪 H4 – Career Route Explorer")

st.markdown("""

### Research Question

Do recurring international career pathways exist that can be identified
from historical player transfers?

Instead of analysing countries, clubs or agencies individually,
this module investigates complete player career profiles.

""")

st.divider()

# ----------------------------------------------------
# KPIs
# ----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "International Transfers",

    len(df)

)

c2.metric(

    "Players",

    df.player_id.nunique()

)

c3.metric(

    "Career Routes",

    df["Career Route"].nunique()

)

c4.metric(

    "Destination Countries",

    df["to_country_name"].nunique()

)

st.divider()

# ----------------------------------------------------
# Career Profile Builder
# ----------------------------------------------------

st.header("Describe Your Player")

c1, c2 = st.columns(2)

with c1:

    nationality = st.selectbox(

        "Nationality",

        sorted(df["primary_nationality"].dropna().unique())


    )

with c2:

    positions = ["All"] + sorted(

        df["position"]

        .dropna()

        .unique()

    )

position = st.selectbox(

    "Position",

    positions

)

minimum = int(df["age"].min())
maximum = int(df["age"].max())

age = st.slider(

    "Age",

    minimum,

    maximum,

    (minimum, maximum)

)

profile = df[
    df["nationality"]
    .fillna("")
    .str.contains(
        nationality,
        regex=False
    )
    &
    (df["age"].between(age[0], age[1]))
].copy()

# --- HIER REINGEPACKT: Filter für Vereinslos / Unbekannt ---
profile = profile[
    ~profile["to_country_name"]
    .fillna("")
    .isin(
        [
            "Vereinslos",
            "Unbekannt"
        ]
    )
]

# Danach geht es ganz normal mit der Position weiter
if position != "All":
    profile = profile[
        profile["position"] == position
    ]

# ====================================================
# HIER GEHÖRT DER CHECK JETZT HIN!
# ====================================================
if profile.empty:
    st.warning(
        "No historical player profiles match the selected criteria."
    )
    st.stop()

# ----------------------------------------------------
# Historical Background
# ----------------------------------------------------

st.subheader("Historical Background")

left, right = st.columns(2)

with left:

    origin = (

        profile["from_country_name"]

        .value_counts()

        .reset_index()

    )

    origin.columns = [

        "Origin Country",

        "Transfers"

    ]

    st.dataframe(

        origin,

        width="stretch",

        height=250

    )

with right:

    leagues = (

        profile["from_league"]

        .value_counts()

        .reset_index()

    )

    leagues.columns = [

        "Origin League",

        "Transfers"

    ]

    st.dataframe(

        leagues,

        width="stretch",

        height=250

    )

st.divider()
# ----------------------------------------------------
# Profile KPIs
# ----------------------------------------------------

c1, c2, c3 = st.columns(3)

c1.metric(

    "Matching Transfers",

    len(profile)

)

c2.metric(

    "Matching Players",

    profile.player_id.nunique()

)

c3.metric(

    "Destination Markets",

    profile.to_country_name.nunique()

)

st.divider()

# ----------------------------------------------------
# Career Route Results
# ----------------------------------------------------

st.subheader("Historical Background")

left, right = st.columns(2)

with left:

    origin = (

        profile["from_country_name"]

        .value_counts()

        .reset_index()

    )

    origin.columns = [

        "Origin Country",

        "Transfers"

    ]

    st.dataframe(

        origin,

        width="stretch",

        height=250

    )

with right:

    leagues = (

        profile["from_league"]

        .value_counts()

        .reset_index()

    )

    leagues.columns = [

        "Origin League",

        "Transfers"

    ]

    st.dataframe(

        leagues,

        width="stretch",

        height=250

    )

st.divider()

st.header("Historical Career Outcomes")

if profile.empty:

    st.warning(
        "No historical transfers found for this career profile."
    )

    st.stop()

# ----------------------------------------------------
# Destination Countries
# ----------------------------------------------------

destinations = (

    profile

    .groupby("to_country_name")

    .agg(

        Transfers=("player_id", "count"),

        Players=("player_id", "nunique"),

        Avg_Age=("age", "mean")

    )

    .reset_index()

    .sort_values(

        "Transfers",

        ascending=False

    )

)

destinations["Probability (%)"] = (

    destinations["Transfers"]

    /

    destinations["Transfers"].sum()

    * 100

).round(1)

st.dataframe(

    destinations,

    width="stretch",

    height=300

)

# ----------------------------------------------------
# Destination Chart
# ----------------------------------------------------

fig = px.bar(

    destinations,

    x="Probability (%)",

    y="to_country_name",

    orientation="h",

    template=PLOT_TEMPLATE,

    title="Most Likely Destination Markets"

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="career_destinations"

)

st.divider()

# ----------------------------------------------------
# Destination Leagues
# ----------------------------------------------------

st.header("Most Frequent Destination Leagues")

leagues = (

    profile

    .groupby("to_league")

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

    leagues,

    width="stretch",

    height=300

)

fig = px.bar(

    leagues,

    x="Transfers",

    y="to_league",

    orientation="h",

    template=PLOT_TEMPLATE,

    title="Destination Leagues"

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="career_leagues"

)

st.divider()

# ----------------------------------------------------
# Destination Clubs
# ----------------------------------------------------

st.header("Most Frequent Destination Clubs")

clubs = (

    profile

    .groupby("to_club_name")

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

    clubs,

    width="stretch",

    height=300

)

fig = px.bar(

    clubs.head(20),

    x="Transfers",

    y="to_club_name",

    orientation="h",

    template=PLOT_TEMPLATE,

    title="Most Frequent Destination Clubs"

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="career_clubs"

)

st.divider()

# ----------------------------------------------------
# Preliminary Evidence
# ----------------------------------------------------

best_market = destinations.iloc[0]

st.success(f"""

### Historical Career Evidence

For the selected player profile, the most common destination market is

**{best_market['to_country_name']}**

with

- **{best_market['Transfers']} historical transfers**
- **{best_market['Players']} unique players**
- **{best_market['Probability (%)']:.1f}% probability**

This represents the historically most frequent international
career pathway observed in the current dataset.

""")

st.divider()

# ----------------------------------------------------
# Career Intelligence
# ----------------------------------------------------

st.header("Career Intelligence")

left, right = st.columns(2)

# ----------------------------------------------------
# Agencies
# ----------------------------------------------------

with left:

    st.subheader("Most Common Agencies")

    agents = (

        profile

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

        agents,

        width="stretch",

        height=300

    )

    fig = px.bar(

        agents.head(15),

        x="Transfers",

        y="agent",

        orientation="h",

        template=PLOT_TEMPLATE

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    st.plotly_chart(

        fig,

        width="stretch",

        key="career_agents"

    )

# ----------------------------------------------------
# Gateway Clubs
# ----------------------------------------------------

with right:

    st.subheader("Gateway Clubs")

    gateways = (

        profile

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

    fig = px.bar(

        gateways.head(15),

        x="Transfers",

        y="from_club_name",

        orientation="h",

        template=PLOT_TEMPLATE

    )

    fig.update_yaxes(

        categoryorder="total ascending"

    )

    st.plotly_chart(

        fig,

        width="stretch",

        key="career_gateway"

    )

st.divider()

# ----------------------------------------------------
# Similar Players
# ----------------------------------------------------

st.header("Historical Players")

players = profile[

    [

        "full_name",

        "age",

        "primary_nationality",

        "position",

        "from_club_name",

        "to_club_name",

        "to_country_name",

        "agent"

    ]

].drop_duplicates()

st.dataframe(

    players,

    width="stretch",

    height=500

)

st.divider()

# ----------------------------------------------------
# Similar Player Statistics
# ----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "Agencies",

    profile["agent"].nunique()

)

c2.metric(

    "Gateway Clubs",

    profile["from_club_name"].nunique()

)

c3.metric(

    "Destination Clubs",

    profile["to_club_name"].nunique()

)

c4.metric(

    "Destination Countries",

    profile["to_country_name"].nunique()

)

st.divider()

# ----------------------------------------------------
# Career Route Network
# ----------------------------------------------------

route_table = (

    profile

    .groupby(

        [

            "from_club_name",

            "to_country_name"

        ]

    )

    .size()

    .reset_index(name="Transfers")

    .sort_values(

        "Transfers",

        ascending=False

    )

)

st.subheader("Most Frequent Career Routes")

st.dataframe(

    route_table,

    width="stretch",

    height=350

)

fig = px.bar(

    route_table.head(20),

    x="Transfers",

    y="from_club_name",

    color="to_country_name",

    orientation="h",

    template=PLOT_TEMPLATE,

    title="Gateway Club → Destination Country"

)

fig.update_yaxes(

    categoryorder="total ascending"

)

st.plotly_chart(

    fig,

    width="stretch",

    key="career_route_network"

)

st.divider()

# ----------------------------------------------------
# Hypothesis Evaluation
# ----------------------------------------------------

st.header("Hypothesis Evaluation")

# ----------------------------------------------------
# Profile Statistics
# ----------------------------------------------------

matches = len(profile)

players = profile["player_id"].nunique()

countries = profile["to_country_name"].nunique()

clubs = profile["to_club_name"].nunique()

best = destinations.iloc[0]

probability = best["Probability (%)"]

# ----------------------------------------------------
# Career Fit Score
# ----------------------------------------------------

career_score = (

    probability * 0.6

    +

    min(matches, 20) / 20 * 40

)

career_score = round(career_score, 1)

# ----------------------------------------------------
# Interpretation
# ----------------------------------------------------

if career_score >= 80:

    fit = "Excellent"

elif career_score >= 60:

    fit = "Strong"

elif career_score >= 40:

    fit = "Moderate"

else:

    fit = "Weak"

# ----------------------------------------------------
# KPIs
# ----------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(

    "Matching Transfers",

    matches

)

c2.metric(

    "Matching Players",

    players

)

c3.metric(

    "Destination Countries",

    countries

)

c4.metric(

    "Career Fit Score",

    f"{career_score:.1f}"

)

st.divider()

# ----------------------------------------------------
# Recommendation
# ----------------------------------------------------

st.subheader("Recommended Career Destination")

summary = pd.DataFrame({

    "Metric": [

        "Recommended Market",

        "Historical Probability",

        "Historical Transfers",

        "Unique Players",

        "Career Fit Score",

        "Recommendation"

    ],

    "Value": [

        best["to_country_name"],

        f"{probability:.1f}%",

        int(best["Transfers"]),

        int(best["Players"]),

        career_score,

        fit

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

supported = (

    probability >= 40

    and

    matches >= 5

)

if supported:

    verdict = "SUPPORTED"

else:

    verdict = "PARTIALLY SUPPORTED"

st.success(f"""

## Hypothesis H4

### {verdict}

For the selected player profile

- Nationality: **{nationality}**
- Position: **{position}**
- Age: **{age[0]}–{age[1]} years**
For the selected player profile

- Nationality: **{nationality}**
- Position: **{position}**
- Age Range: **{age[0]}–{age[1]}**

the historically most frequent destination market is

## **{best['to_country_name']}**

with

- **{best['Transfers']} historical transfers**
- **{best['Players']} unique players**
- **{probability:.1f}% historical probability**

The calculated Career Fit Score is

# **{career_score:.1f}/100**

(**{fit}**)

These findings indicate that comparable player profiles repeatedly
follow similar international career pathways.

The results therefore provide evidence supporting the existence of
recurring historical career routes, consistent with Hypothesis H4.

""")

st.divider()

st.caption("FootballAbroad Research – Hypothesis H4")
