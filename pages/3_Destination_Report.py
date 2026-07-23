import streamlit as st

from services.destination_service import load_knowledge

country = st.session_state.get("destination_country", "India")
league = st.session_state.get("destination_league", "Indian Super League")

knowledge = load_knowledge(country)

st.title("Destination Report")

st.write(country)
st.write(league)

st.divider()

import pandas as pd

if knowledge:

    for section in knowledge["sections"]:

        st.subheader(section["title"])

        if section.get("summary"):
            st.write(section["summary"])

        # ------------------------
        # Insights
        # ------------------------

        insights = section.get("insights", [])

        if insights:

            st.markdown("#### Key Insights")

            for insight in insights:

                confidence = insight["confidence"]

                icon = {
                    "High": "🟢",
                    "Medium": "🟡",
                    "Low": "⚪"
                }.get(confidence, "⚪")

                st.markdown(
                    f"**{icon} {insight['text']}**"
                )

        # ------------------------
        # Club Examples
        # ------------------------

        examples = section.get("examples", [])

        if examples:

            st.markdown("#### Club Examples")

            df = pd.DataFrame(
                [
                    {
                        "Club": e["club"],
                        "Example": e["fact"]
                    }
                    for e in examples
                ]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        # ------------------------
        # Sources
        # ------------------------

        sources = section.get("sources", [])

        if sources:

            with st.expander("Sources"):

                for source in sources:

                    st.markdown(f"**{source['type']}**")

                    if source.get("title"):
                        st.write(source["title"])

                    if source.get("evidence"):
                        st.caption(source["evidence"])

                    if source.get("url"):
                        st.link_button(
                            "Open source",
                            source["url"],
                            use_container_width=True
                        )

                    st.divider()
