import streamlit as st

from career_navigator import (
    find_similar_players,
    get_league_options,
    prepare_dataset,
    recommended_countries,
    recommended_leagues,
)
from config import APP_ICON, APP_TITLE
from database import read_table
from utils import load_data


@st.cache_data
def load_navigator_data():
    return prepare_dataset(load_data().copy())


@st.cache_data
def load_intelligence_counts():
    tables = {
        "Transfers analysed": "master_dataset",
        "Transfer corridors": "transfer_corridors",
        "Stepping clubs": "stepping_clubs",
        "Player archetypes": "player_archetypes",
        "Agencies": "agency_networks",
        "League networks": "league_flows",
    }
    return {
        label: len(read_table(table))
        for label, table in tables.items()
    }


st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

        :root { --red: #ff4b4b; --panel: #151517; --muted: #a5a5aa; }
        .stApp { background: #0a0a0b; color: #f6f6f7; font-family: 'Manrope', sans-serif; }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { max-width: 1180px; padding: 1.4rem 2rem 5rem; }
        .hero { padding: 3.8rem 0 2rem; }
        .section { padding: 4.7rem 0; }
        .eyebrow { color: var(--red); font: 500 .72rem 'DM Mono', monospace; letter-spacing: .13em; text-transform: uppercase; }
        .hero h1 { max-width: 780px; margin: 1rem 0 1.4rem; font-size: clamp(3.25rem, 7vw, 6.7rem); line-height: .98; letter-spacing: -.075em; font-weight: 800; }
        .hero h1 span { color: var(--red); }
        .lede { max-width: 620px; color: #b5b5ba; font-size: 1.2rem; line-height: 1.7; }
        .small-label { color: var(--muted); font: 500 .72rem 'DM Mono', monospace; letter-spacing: .1em; text-transform: uppercase; }
        .section-title { max-width: 750px; margin: .75rem 0 0; font-size: clamp(2.25rem, 4vw, 4rem); line-height: 1.06; letter-spacing: -.06em; }
        .section-copy { max-width: 605px; margin-top: 1.25rem; color: #b5b5ba; font-size: 1.05rem; line-height: 1.75; }
        .nav-links { display: flex; justify-content: flex-end; align-items: center; gap: 1.1rem; font-size: .78rem; }
        .nav-links a { color: #a8a8ad; text-decoration: none; transition: color .16s ease; }
        .nav-links a:hover { color: #f6f6f7; }
        .nav-links a:last-child { color: #f6f6f7; font-weight: 700; }
        .metric { border-left: 1px solid #353538; padding: .15rem 0 .15rem 1.15rem; }
        .metric-number { font-size: clamp(2.85rem, 5vw, 5.2rem); line-height: .95; font-weight: 800; letter-spacing: -.07em; }
        .metric-label { margin-top: .45rem; color: var(--muted); font-size: .92rem; }
        .line { height: 1px; margin: .8rem 0; background: linear-gradient(90deg, transparent, #303033, transparent); }
        .mockup { overflow: hidden; border: 1px solid #343438; border-radius: 20px; background: linear-gradient(145deg, #1b1b1e, #0e0e10 68%); box-shadow: 0 28px 80px rgba(0,0,0,.45); }
        .mock-top { display: flex; align-items: center; gap: .45rem; padding: .85rem 1rem; border-bottom: 1px solid #303034; color: #9b9ba1; font: .7rem 'DM Mono', monospace; }
        .dot { width: 7px; height: 7px; border-radius: 50%; background: #44444a; } .dot:first-child { background: var(--red); }
        .mock-body { display: grid; grid-template-columns: 170px 1fr; min-height: 330px; }
        .mock-side { padding: 1.2rem; border-right: 1px solid #303034; background: rgba(255,255,255,.015); }
        .side-mark { margin-bottom: 1rem; color: #77777c; font-size: .7rem; } .side-mark.active { color: white; }
        .mock-main { padding: 1.4rem; } .mock-heading { font-size: 1.05rem; font-weight: 700; }
        .filter-row { display: flex; gap: .6rem; margin: 1rem 0 1.4rem; } .pill { border: 1px solid #3b3b3f; border-radius: 30px; padding: .37rem .65rem; color: #b6b6bb; font-size: .67rem; }
        .path-card { border: 1px solid #333337; border-radius: 12px; padding: .8rem; margin-top: .65rem; background: rgba(255,255,255,.025); }
        .path-top { display: flex; justify-content: space-between; font-size: .72rem; } .path-top span:last-child { color: var(--red); }
        .route { display: flex; align-items: center; gap: .5rem; margin-top: .8rem; color: #c5c5ca; font: .66rem 'DM Mono', monospace; } .route i { width: 20px; height: 1px; background: #515158; }
        .feature-card, .audience-card { height: 100%; border: 1px solid #303034; border-radius: 16px; padding: 1.45rem; background: #111113; }
        .feature-index { color: var(--red); font: .7rem 'DM Mono', monospace; } .feature-card h3, .audience-card h3 { margin: 1.15rem 0 .65rem; font-size: 1.1rem; letter-spacing: -.03em; }
        .feature-card p, .audience-card p { margin: 0; color: var(--muted); line-height: 1.65; font-size: .88rem; }
        .step { position: relative; min-height: 155px; border-top: 1px solid #39393d; padding: 1rem 1rem 1rem 0; }
        .step b { display: block; margin-bottom: .75rem; font-size: 1rem; } .step p { color: var(--muted); font-size: .88rem; }
        .step-number { color: var(--red); font: .7rem 'DM Mono', monospace; }
        .navigator { margin-top: 2rem; overflow: hidden; border: 1px solid #343438; border-radius: 20px; background: linear-gradient(145deg, #1b1b1e, #0e0e10 68%); box-shadow: 0 28px 80px rgba(0,0,0,.45); }
        .navigator-head { display: flex; justify-content: space-between; align-items: center; padding: 1.1rem 1.35rem; border-bottom: 1px solid #303034; } .navigator-head b { font-size: 1.05rem; } .navigator-tag { color: var(--red); font: .67rem 'DM Mono', monospace; letter-spacing: .08em; text-transform: uppercase; }
        .navigator-body { display: grid; grid-template-columns: 1.1fr .9fr; } .profile-panel, .result-panel { padding: 1.5rem; } .result-panel { border-left: 1px solid #303034; background: rgba(255,255,255,.018); }
        .panel-title { font-size: 1.2rem; font-weight: 800; letter-spacing: -.04em; } .panel-intro { color: var(--muted); font-size: .9rem; line-height: 1.6; }
        .field { margin-top: .8rem; padding: .8rem .9rem; border: 1px solid #38383c; border-radius: 10px; background: #111113; } .field-label { display: block; margin-bottom: .23rem; color: #85858b; font: .62rem 'DM Mono', monospace; letter-spacing: .08em; text-transform: uppercase; } .field-value { font-size: .86rem; color: #ececef; }
        .outcome { display: flex; gap: .7rem; align-items: flex-start; margin-top: .95rem; } .outcome-dot { flex: 0 0 23px; height: 23px; border-radius: 50%; display: grid; place-items: center; background: rgba(255,75,75,.13); color: var(--red); font-size: .72rem; } .outcome b { display: block; font-size: .83rem; } .outcome span { display: block; margin-top: .13rem; color: var(--muted); font-size: .75rem; line-height: 1.45; }
        .story-card { min-height: 210px; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #303034; border-radius: 16px; padding: 1.4rem; background: linear-gradient(145deg, #151518, #101012); } .story-placeholder { color: var(--red); font: .67rem 'DM Mono', monospace; letter-spacing: .08em; text-transform: uppercase; } .story-card p { color: #d5d5d9; font-size: 1rem; line-height: 1.55; } .story-meta { color: var(--muted); font-size: .78rem; }
        .explorer { margin: 1.5rem 0 4.5rem; padding: 1.5rem; border: 1px solid #343438; border-radius: 20px; background: linear-gradient(145deg, #18181a, #101012); } .explorer-intro { max-width: 650px; color: var(--muted); font-size: .92rem; line-height: 1.6; }
        .preview { margin-top: 1.1rem; padding: 1.35rem; border: 1px solid rgba(255,75,75,.35); border-radius: 14px; background: rgba(255,75,75,.045); } .preview h3 { margin: 0; font-size: 1.25rem; letter-spacing: -.04em; } .preview-copy { margin: .4rem 0 1rem; color: var(--muted); font-size: .9rem; }
        .found-number { color: #fff; font-size: clamp(2.2rem, 5vw, 4.6rem); line-height: .95; font-weight: 800; letter-spacing: -.07em; }
        .found-label { color: var(--muted); font-size: .86rem; margin-top: .35rem; }
        .route-list { margin: .75rem 0 0; padding: 0; list-style: none; } .route-list li { display: flex; justify-content: space-between; gap: 1rem; padding: .7rem 0; border-top: 1px solid #303034; color: #f0f0f2; font-size: .93rem; } .route-list span { color: var(--red); font: .72rem 'DM Mono', monospace; white-space: nowrap; }
        .result-list { margin: 0; padding: 0; list-style: none; } .result-list li { display: flex; justify-content: space-between; gap: 1rem; padding: .55rem 0; border-top: 1px solid #303034; color: #e5e5e8; font-size: .84rem; } .result-list li span { color: var(--red); font: .72rem 'DM Mono', monospace; white-space: nowrap; }
        [data-testid="stSelectbox"] label { color: #e8e8eb !important; font-size: .86rem !important; font-weight: 700 !important; } [data-testid="stSelectbox"] [data-baseweb="select"] > div { min-height: 47px; border-color: #444449; border-radius: 9px; background: #101012; }
        .audience-list { margin: .9rem 0 0; padding-left: 1.05rem; color: #d7d7da; line-height: 1.9; font-size: .9rem; }
        .quote { border-left: 2px solid var(--red); margin: 2rem 0 0; padding: .2rem 0 .2rem 1.25rem; color: #d9d9dc; font-size: 1.2rem; line-height: 1.55; }
        .cta { padding: 4rem 2.25rem; border: 1px solid #3a2929; border-radius: 22px; background: radial-gradient(circle at 78% 15%, rgba(255,75,75,.22), transparent 27%), #121214; text-align: center; }
        .cta h2 { max-width: 650px; margin: .5rem auto 1rem; font-size: clamp(2.3rem, 4vw, 4.3rem); line-height: 1.04; letter-spacing: -.065em; }
        .cta p { max-width: 500px; margin: 0 auto 1.5rem; color: var(--muted); }
        .stButton > button { min-height: 46px; border: 0; border-radius: 9px; background: var(--red); color: white; font: 700 .86rem 'Manrope', sans-serif; padding: 0 1.1rem; transition: transform .18s ease, background .18s ease; }
        .stButton > button:hover { background: #ff6262; transform: translateY(-2px); color: white; }
        [data-testid="stPageLink"] > a { display: inline-flex; min-height: 46px; align-items: center; justify-content: center; border: 0; border-radius: 9px; background: var(--red); color: white; font: 700 .86rem 'Manrope', sans-serif; padding: 0 1.1rem; text-decoration: none; transition: transform .18s ease, background .18s ease; }
        [data-testid="stPageLink"] > a:hover { background: #ff6262; transform: translateY(-2px); color: white; text-decoration: none; }
        .secondary .stButton > button { border: 1px solid #3a3a3d; background: transparent; color: #f1f1f2; }
        .secondary .stButton > button:hover { border-color: #737378; background: #1a1a1d; }
        @media (max-width: 700px) { .block-container { padding: 1rem 1.15rem 3rem; } .hero, .section { padding: 3rem 0; } .hero h1 { font-size: 3.25rem; } .nav-links { display: none; } .mock-body { grid-template-columns: 92px 1fr; } .mock-side { padding: .8rem; } .mock-main { padding: 1rem; } .side-mark { font-size: .58rem; } .filter-row { flex-wrap: wrap; } .navigator-body { grid-template-columns: 1fr; } .result-panel { border-left: 0; border-top: 1px solid #303034; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_landing_preview():
    navigator_data = load_navigator_data()
    country_options = sorted(navigator_data["from_country_name"].dropna().unique())
    default_country_index = country_options.index("Germany") if "Germany" in country_options else 0

    with st.container(border=True):
        st.markdown(
            "<div class='navigator-head'><b>Career Navigator</b><span class='navigator-tag'>Start with your situation</span></div>",
            unsafe_allow_html=True,
        )
        form_column, explanation_column = st.columns([1.1, 0.9], gap="large")
        with form_column:
            st.markdown(
                "<div class='panel-title'>Choose your profile</div><p class='panel-intro'>Start with where you play now. KickWays finds professional players who previously stood in a similar career situation and shows how comparable players continued their careers over the following years.</p>",
                unsafe_allow_html=True,
            )
            selected_country = st.selectbox(
                "What country are you currently playing in?",
                country_options,
                index=default_country_index,
                placeholder="Select a country",
                key="landing_country",
            )
            league_options = (
                get_league_options(navigator_data, selected_country)
                if selected_country
                else []
            )
            default_league_index = 0 if league_options else None
            selected_league = st.selectbox(
                "What league are you currently playing in?",
                league_options,
                index=default_league_index,
                placeholder="Select your country first" if not selected_country else "Select a league",
                disabled=not selected_country,
                key="landing_league",
            )
        with explanation_column:
            st.markdown(
                "<div class='panel-title'>What can you discover?</div><p class='panel-intro'>Football careers are shaped by timing, opportunities and difficult decisions. KickWays doesn&#39;t predict what you should do. It helps you understand what comparable professionals actually did&mdash;and how their careers unfolded afterwards.</p><div class='outcome'><div class='outcome-dot'>01</div><div><b>Comparable players</b><span>Find careers that started from a similar country and league context.</span></div></div><div class='outcome'><div class='outcome-dot'>02</div><div><b>Common career outcomes</b><span>See which countries and leagues appeared most often as next steps.</span></div></div><div class='outcome'><div class='outcome-dot'>03</div><div><b>Complete career journeys</b><span>Open the full navigator to follow the clubs, leagues and countries behind each route.</span></div></div>",
                unsafe_allow_html=True,
            )

        if selected_country and selected_league:
            matching_players = find_similar_players(
                navigator_data,
                current_country=selected_country,
                current_league=selected_league,
            )
            destination_countries = recommended_countries(matching_players, top_n=3)
            destination_leagues = recommended_leagues(matching_players, top_n=3)
            if destination_countries.empty:
                top_country_routes = "<li>No next-country routes available yet<span>0 players</span></li>"
            else:
                top_country_routes = "".join(
                    f"<li>{selected_country} &rarr; {row.Country}<span>{row.Players} players</span></li>"
                    for row in destination_countries.itertuples(index=False)
                )
            st.markdown(
                f"<div class='preview'><div class='small-label'>Comparable players found</div><div class='found-number'>{matching_players['player_id'].nunique():,}</div><div class='found-label'>professional careers included {selected_league} in {selected_country}</div><h3 style='margin-top:1.25rem'>Most common next moves</h3><p class='preview-copy'>The first layer of insight: where players from this starting point actually continued their careers.</p><ul class='route-list'>{top_country_routes}</ul></div>",
                unsafe_allow_html=True,
            )
            country_results, league_results = st.columns(2, gap="large")
            with country_results:
                st.markdown("<div class='small-label' style='margin:1rem 0 .35rem'>Common next countries</div>", unsafe_allow_html=True)
                if destination_countries.empty:
                    st.caption("No destination countries are available for this selection yet.")
                else:
                    country_rows = "".join(
                        f"<li>{row.Country}<span>{row.Players} players</span></li>"
                        for row in destination_countries.itertuples(index=False)
                    )
                    st.markdown(f"<ul class='result-list'>{country_rows}</ul>", unsafe_allow_html=True)
            with league_results:
                st.markdown("<div class='small-label' style='margin:1rem 0 .35rem'>Common next leagues</div>", unsafe_allow_html=True)
                if destination_leagues.empty:
                    st.caption("No next leagues are available for this selection yet.")
                else:
                    league_rows = "".join(
                        f"<li>{row.League}<span>{row.Players} players</span></li>"
                        for row in destination_leagues.itertuples(index=False)
                    )
                    st.markdown(f"<ul class='result-list'>{league_rows}</ul>", unsafe_allow_html=True)
            st.page_link("pages/7_Career_Navigator.py", label="Explore full career paths →")
        else:
            st.markdown("<p style='margin:1.2rem 0 0;color:#85858b;font-size:.82rem'>Select both fields to reveal a live preview from the KickWays career database.</p>", unsafe_allow_html=True)


nav_left, nav_features, nav_how, nav_players, nav_agents, nav_open = st.columns([3.3, 1, 1.25, 1.15, 1.05, 1.5])
with nav_left:
    st.markdown("<div style='font-weight:800;letter-spacing:-.05em;font-size:1.2rem'>Kick<span style='color:#ff4b4b'>Ways</span></div>", unsafe_allow_html=True)
with nav_features:
    st.markdown("<div class='nav-links'><a href='#features'>Features</a></div>", unsafe_allow_html=True)
with nav_how:
    st.markdown("<div class='nav-links'><a href='#how-it-works'>How it works</a></div>", unsafe_allow_html=True)
with nav_players:
    st.markdown("<div class='nav-links'><a href='#for-players'>For Players</a></div>", unsafe_allow_html=True)
with nav_agents:
    st.markdown("<div class='nav-links'><a href='#for-agents'>For Agents</a></div>", unsafe_allow_html=True)
with nav_open:
    st.page_link("pages/7_Career_Navigator.py", label="Open Platform")

st.markdown("""
<section class="hero">
  <div class="eyebrow">Career Intelligence for Professional Football</div>
  <h1>Football Career <span>Intelligence.</span></h1>
  <p class="lede">Understand how football careers actually happen. Explore historical transfers, career pathways, stepping clubs, league networks, and player archetypes.</p>
</section>
""", unsafe_allow_html=True)

hero_primary, _ = st.columns([1.7, 7.3])
with hero_primary:
    st.page_link("pages/7_Career_Navigator.py", label="Explore Career Paths →")

st.markdown("<div id='how-it-works'></div>", unsafe_allow_html=True)
render_landing_preview()

st.markdown("<div style='height:2.2rem'></div>", unsafe_allow_html=True)
intelligence_counts = load_intelligence_counts()
metrics = st.columns(3)
for column, (label, value) in zip(metrics, list(intelligence_counts.items())[:3]):
    with column:
        st.markdown(f"<div class='metric'><div class='metric-number'>{value:,}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)

metrics = st.columns(3)
for column, (label, value) in zip(metrics, list(intelligence_counts.items())[3:]):
    with column:
        st.markdown(f"<div class='metric'><div class='metric-number'>{value:,}</div><div class='metric-label'>{label}</div></div>", unsafe_allow_html=True)

st.markdown("<div id='features'></div>", unsafe_allow_html=True)
solution_copy, solution_mock = st.columns([.85, 1.15], gap="large")
with solution_copy:
    st.markdown("<div class='small-label'>The platform</div><h2 class='section-title'>Career intelligence, built on real player journeys.</h2><p class='section-copy'>KickWays makes historical movement easier to explore. Start with a profile, find comparable players, then trace the clubs, leagues and countries that formed their careers.</p><p class='section-copy'>No predictions. No transfer recommendations. Just transparent, useful context for better decisions.</p>", unsafe_allow_html=True)
with solution_mock:
    st.markdown("""
    <div class="mockup" style="margin-top:.4rem"><div class="mock-top"><i class="dot"></i><i class="dot"></i><i class="dot"></i><span style="margin-left:.4rem">similar player profile</span></div><div class="mock-main" style="min-height:275px"><div class="mock-heading">Players with a similar starting point</div><div class="path-card"><div class="path-top"><b>CM · 24 · Denmark</b><span>91% match</span></div><div class="route">FC MIDTJYLLAND <i></i> KAA GENT <i></i> FC UTRECHT</div></div><div class="path-card"><div class="path-top"><b>CM · 23 · Sweden</b><span>88% match</span></div><div class="route">MALMÖ FF <i></i> FC NÜRNBERG <i></i> RAPID WIEN</div></div></div></div>
    """, unsafe_allow_html=True)

st.markdown("<div class='section'><div class='small-label'>The problem</div><h2 class='section-title'>Football careers are shaped by decisions whose long-term consequences are often impossible to see.</h2><p class='section-copy'>Players know today&#39;s offer&mdash;but rarely know what similar moves have led to for others.</p><div class='quote'>&ldquo;I can finally see what happened after players like me made similar career decisions.&rdquo;</div></div>", unsafe_allow_html=True)

st.markdown("<section class='section'><div class='small-label'>Built for the people making the move</div><h2 class='section-title'>Different perspectives. The same clearer picture.</h2></section>", unsafe_allow_html=True)
audience = [
    ("Players", ["Compare yourself", "Explore destinations", "Learn from real careers"]),
    ("Agents", ["Prepare client conversations", "Map realistic pathways", "Support decisions with context"]),
    ("Clubs", ["Understand career routes", "See source markets", "Explore league pathways"]),
]
audience_columns = st.columns(3, gap="medium")
for column, (title, bullets) in zip(audience_columns, audience):
    with column:
        bullet_items = "".join(f"<li>{bullet}</li>" for bullet in bullets)
        anchor = " id='for-players'" if title == "Players" else " id='for-agents'" if title == "Agents" else ""
        st.markdown(f"<div class='audience-card'{anchor}><div class='feature-index'>FOR {title.upper()}</div><h3>{title}</h3><ul class='audience-list'>{bullet_items}</ul></div>", unsafe_allow_html=True)

st.markdown("<div style='height:4rem'></div><section class='cta'><div class='eyebrow'>A clearer way forward</div><h2>Discover where players like you actually went next.</h2><p>Explore historical career context for professional football without pretending to predict the future.</p></section>", unsafe_allow_html=True)
cta_left, _ = st.columns([2, 8])
with cta_left:
    st.page_link("pages/7_Career_Navigator.py", label="Explore Career Paths →")

st.markdown("<div class='line'></div><p style='color:#737378;font-size:.72rem;padding-top:.5rem'>© 2026 KickWays · Career intelligence for professional football.</p>", unsafe_allow_html=True)
