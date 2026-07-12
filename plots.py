import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import (
    PLOT_TEMPLATE,
    COLOR_PRIMARY,
    TOP_N
)

# --------------------------------------------------------
# Globale Ausschlussliste für Klubs (NEU)
# --------------------------------------------------------
EXCLUDED_CLUBS = {
    "Unknown",
    "Unbekannt",
    "Without a club",
    "Retired",
    "Career break",
}


# --------------------------------------------------------
# Generic Layout
# --------------------------------------------------------

def style(fig):
    fig.update_layout(
        template=PLOT_TEMPLATE,
        height=550,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
        legend_title="",
    )
    return fig


# --------------------------------------------------------
# Horizontal Ranking
# --------------------------------------------------------

def ranking_bar(
    data,
    x,
    y,
    title,
    color=None,
):
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        orientation="h",
        title=title,
    )
    fig.update_yaxes(
        categoryorder="total ascending"
    )
    return style(fig)


# --------------------------------------------------------
# Top Countries
# --------------------------------------------------------

def top_destination_countries(df):
    data = (
        df["to_country_name"]
        .value_counts()
        .head(TOP_N)
        .rename_axis("Country")
        .reset_index(name="Transfers")
    )
    return ranking_bar(
        data,
        "Transfers",
        "Country",
        "Top Destination Countries",
    )


# --------------------------------------------------------
# Top Leagues
# --------------------------------------------------------

def top_destination_leagues(df):
    data = (
        df["to_league"]
        .value_counts()
        .head(TOP_N)
        .rename_axis("League")
        .reset_index(name="Transfers")
    )
    return ranking_bar(
        data,
        "Transfers",
        "League",
        "Top Destination Leagues",
    )


# --------------------------------------------------------
# Transfer Corridors
# --------------------------------------------------------

def transfer_corridors(df):
    data = (
        df.groupby(
            [
                "from_country_name",
                "to_country_name",
            ]
        )
        .size()
        .reset_index(name="Transfers")
        .sort_values(
            "Transfers",
            ascending=False,
        )
        .head(TOP_N)
    )
    fig = px.bar(
        data,
        x="Transfers",
        y="to_country_name",
        color="from_country_name",
        orientation="h",
        title="Top Transfer Corridors",
    )
    return style(fig)


# --------------------------------------------------------
# League Corridors
# --------------------------------------------------------

def league_corridors(df):
    data = (
        df.groupby(
            [
                "from_league",
                "to_league",
            ]
        )
        .size()
        .reset_index(name="Transfers")
        .sort_values(
            "Transfers",
            ascending=False,
        )
        .head(TOP_N)
    )
    fig = px.bar(
        data,
        x="Transfers",
        y="to_league",
        color="from_league",
        orientation="h",
        title="Top League Corridors",
    )
    return style(fig)


# --------------------------------------------------------
# Top Agents
# --------------------------------------------------------

def top_agents(df):
    data = (
        df["agent"]
        .dropna()
        .value_counts()
        .head(TOP_N)
        .rename_axis("Agent")
        .reset_index(name="Transfers")
    )
    return ranking_bar(
        data,
        "Transfers",
        "Agent",
        "Most Active Agents",
    )


# --------------------------------------------------------
# Export Clubs (GEÄNDERT)
# --------------------------------------------------------

def export_clubs(df):
    filtered = df.loc[
        ~df["from_club_name"].isin(EXCLUDED_CLUBS)
    ]

    data = (
        filtered["from_club_name"]
        .value_counts()
        .head(TOP_N)
        .rename_axis("Club")
        .reset_index(name="Transfers")
    )

    return ranking_bar(
        data,
        "Transfers",
        "Club",
        "Top Export Clubs",
    )


# --------------------------------------------------------
# Import Clubs (GEÄNDERT)
# --------------------------------------------------------

def import_clubs(df):
    filtered = df.loc[
        ~df["to_club_name"].isin(EXCLUDED_CLUBS)
    ]

    data = (
        filtered["to_club_name"]
        .value_counts()
        .head(TOP_N)
        .rename_axis("Club")
        .reset_index(name="Transfers")
    )

    return ranking_bar(
        data,
        "Transfers",
        "Club",
        "Top Import Clubs",
    )


# --------------------------------------------------------
# Position Distribution
# --------------------------------------------------------

def position_distribution(df):
    data = (
        df["position"]
        .value_counts()
        .reset_index()
    )
    data.columns = [
        "Position",
        "Players",
    ]

    fig = px.pie(
        data,
        names="Position",
        values="Players",
        title="Position Distribution",
    )
    return style(fig)


# --------------------------------------------------------
# Nationality Distribution
# --------------------------------------------------------

def nationality_distribution(df):
    data = (
        df["nationality"]
        .dropna()
        .value_counts()
        .head(20)
        .rename_axis("Nationality")
        .reset_index(name="Players")
    )
    return ranking_bar(
        data,
        "Players",
        "Nationality",
        "Most Common Nationalities",
    )


# --------------------------------------------------------
# International vs Domestic
# --------------------------------------------------------

def international_share(df):
    data = (
        df["international"]
        .value_counts()
        .rename(
            {
                True: "International",
                False: "Domestic",
            }
        )
        .reset_index()
    )
    data.columns = [
        "Transfer",
        "Count",
    ]

    fig = px.pie(
        data,
        names="Transfer",
        values="Count",
        title="Domestic vs International",
    )
    return style(fig)


# --------------------------------------------------------
# Missing Values
# --------------------------------------------------------

def missing_values(df):
    data = (
        df
        .isna()
        .sum()
        .sort_values(
            ascending=False,
        )
        .head(20)
        .rename_axis("Column")
        .reset_index(name="Missing")
    )
    return ranking_bar(
        data,
        "Missing",
        "Column",
        "Missing Values",
    )
