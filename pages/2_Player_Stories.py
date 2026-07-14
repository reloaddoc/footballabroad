import streamlit as st

from config import APP_ICON


st.set_page_config(
    page_title="Player Stories · KickWays",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
        .stApp { background: #0a0a0b; color: #f6f6f7; font-family: 'Manrope', sans-serif; }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { max-width: 1080px; padding: 2rem 2rem 5rem; }
        .eyebrow { color: #ff4b4b; font: 500 .72rem 'DM Mono', monospace; letter-spacing: .13em; text-transform: uppercase; }
        h1 { max-width: 720px; margin: 1rem 0; font-size: clamp(3rem, 6vw, 5.5rem); line-height: .98; letter-spacing: -.07em; }
        .lede { max-width: 620px; color: #adadb2; font-size: 1.12rem; line-height: 1.7; }
        .notice { margin-top: 3rem; border: 1px solid #343438; border-radius: 18px; padding: 2rem; background: linear-gradient(145deg, #171719, #101012); }
        .notice h2 { margin: 0 0 .8rem; font-size: 1.5rem; letter-spacing: -.04em; } .notice p { max-width: 660px; margin: 0; color: #adadb2; line-height: 1.65; }
        [data-testid="stPageLink"] > a { display: inline-flex; min-height: 44px; align-items: center; justify-content: center; border: 1px solid #3b3b3f; border-radius: 9px; color: white; font: 700 .84rem 'Manrope', sans-serif; padding: 0 1rem; text-decoration: none; }
        [data-testid="stPageLink"] > a:hover { background: #19191b; color: white; text-decoration: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.page_link("app.py", label="← Back to KickWays")
st.markdown(
    """
    <div style="height:3.5rem"></div>
    <div class="eyebrow">Player stories</div>
    <h1>The experiences behind the career path.</h1>
    <p class="lede">KickWays will feature first-hand stories from professional players: moving abroad, choosing a new league, adapting to a different football culture, and looking back on the decisions that shaped their careers.</p>
    <div class="notice"><h2>Stories are coming soon.</h2><p>We are building this space around real people and real experiences. Until stories are published, KickWays remains focused on the historical career paths in the Career Navigator.</p></div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.page_link("pages/7_Career_Navigator.py", label="Explore Career Paths →")
