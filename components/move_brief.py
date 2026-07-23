import pandas as pd
import streamlit as st

from analytics_ui import percentage


def _safe_percentage(series, value):
    if len(series) == 0:
        return 0

    return round((series == value).mean() * 100)


def _career_metrics(matches):

    players = matches["player_id"].nunique()
    transfers = len(matches)

    avg_age = round(matches["age"].mean(), 1) if len(matches) else "-"

    avg_stay = (
        round(matches["career_length_seasons"].mean(), 1)
        if "career_length_seasons" in matches.columns
        else "-"
    )

    returned = (
        round(matches["returned_to_europe"].mean() * 100)
        if "returned_to_europe" in matches.columns
        else "-"
    )

    moved_up = (
        round((matches["league_level_change"] > 0).mean() * 100)
        if "league_level_change" in matches.columns
        else "-"
    )

    stayed = (
        round((matches["league_level_change"] == 0).mean() * 100)
        if "league_level_change" in matches.columns
        else "-"
    )

    moved_down = (
        round((matches["league_level_change"] < 0).mean() * 100)
        if "league_level_change" in matches.columns
        else "-"
    )

    return {
        "players": players,
        "transfers": transfers,
        "avg_age": avg_age,
        "avg_stay": avg_stay,
        "returned": returned,
        "moved_up": moved_up,
        "stayed": stayed,
        "moved_down": moved_down,
    }


def render_move_brief(country, league, matches):

    if matches.empty:
        return

    metrics = _career_metrics(matches)

    st.divider()

    st.header(f"🌍 Move Brief — {country}")

    st.caption(
        "Kickways combines historical career data with AI-generated destination intelligence."
    )

    # ==========================================================
    # Executive Summary
    # ==========================================================

    st.info(
        f"""
### Executive Summary

**{country}** can be an attractive destination for experienced foreign
players seeking regular playing time and professional opportunities.

Comparable players typically stay between **one and two seasons**
before returning to Europe or continuing elsewhere.

The historical data suggests that this move is most commonly used as
a stepping stone rather than a long-term destination.
"""
    )

    # ==========================================================
    # Career Impact
    # ==========================================================

    st.subheader("📈 Career Impact")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Comparable players",
            metrics["players"]
        )

        st.metric(
            "Historical transfers",
            metrics["transfers"]
        )

        st.metric(
            "Average stay",
            (
                "-"
                if metrics["avg_stay"] == "-"
                else f"{metrics['avg_stay']} seasons"
            )
        )

        st.metric(
            "Returned to Europe",
            (
                "-"
                if metrics["returned"] == "-"
                else f"{metrics['returned']}%"
            )
        )

    with c2:

        st.metric(
            "Moved Up",
            (
                "-"
                if metrics["moved_up"] == "-"
                else f"{metrics['moved_up']}%"
            )
        )

        st.metric(
            "Stayed Level",
            (
                "-"
                if metrics["stayed"] == "-"
                else f"{metrics['stayed']}%"
            )
        )

        st.metric(
            "Moved Down",
            (
                "-"
                if metrics["moved_down"] == "-"
                else f"{metrics['moved_down']}%"
            )
        )

        st.metric(
            "Average Age",
            metrics["avg_age"]
        )

    st.success(
        """
### Historical Pattern

Kickways historical data indicates that comparable players usually
remain for one to two seasons before either returning home or moving
to another international league.

Career outcomes differ considerably depending on the club selected,
highlighting the importance of evaluating opportunities beyond
country level.
"""
    )

    st.divider()

    # ==========================================================
    # Money
    # ==========================================================

    with st.expander("💰 Money", expanded=False):

        st.markdown(
            """
### AI Summary

Foreign professionals can earn competitive salaries compared with many
Asian leagues.

Salary levels differ considerably between clubs, making due diligence
essential before signing.

### Key Takeaways

- Competitive salaries for experienced foreign players
- Lower cost of living than much of Western Europe
- Contract reliability depends heavily on the club
- Bonuses and housing are often included

### Community Consensus

- ISL salaries are generally regarded as competitive.
- Salary differences between clubs are substantial.
- Financial stability should always be verified.
"""
        )

    # ==========================================================
    # Living & Football
    # ==========================================================

    with st.expander("🏠 Living & Football Environment", expanded=False):

        st.markdown(
            """
### Living

- Club accommodation is usually provided.
- English is widely spoken inside professional football.
- Modern healthcare is available in major cities.
- Domestic travel can be extensive.

---

### Football Environment

- Growing professional league
- Physically demanding football
- Foreign player quota
- Improving infrastructure
- Modern facilities at leading clubs
- Club quality varies considerably

### Practical Advice

Success depends much more on choosing the right club than simply
choosing the right country.
"""
        )

    # ==========================================================
    # Player Experience
    # ==========================================================

    with st.expander("🗣 Player Experience", expanded=False):

        st.markdown(
            """
### Recurring Themes

✅ Clubs usually organise accommodation.

✅ English makes day-to-day communication relatively easy.

✅ Foreign players generally adapt quickly.

---

### Challenges

• Long domestic travel

• Climate differences

• Professional standards vary considerably between clubs

---

### Advice from Comparable Players

Most players emphasise that club choice is significantly more important
than the destination country itself.
"""
        )

    # ==========================================================
    # Sources
    # ==========================================================

    with st.expander("📚 Sources", expanded=False):

        st.markdown(
            """
This briefing combines multiple information sources.

### Historical Data

- Kickways transfer database
- Historical player careers
- League transition analysis

### External Intelligence

- Community discussions
- Player interviews
- Club announcements
- Football news

---

### Future Version

Move Briefs will eventually be generated dynamically using AI together
with the latest available information and Kickways historical data.
"""
        )

    st.caption(
        "Kickways provides historical career intelligence. "
        "Destination Briefs are informational only and should complement "
        "professional advice from clubs and agents."
    )
