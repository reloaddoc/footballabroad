country = st.session_state.destination_country
league = st.session_state.destination_league

master = load_table("master_dataset")

destination = get_destination_data(
    master,
    country,
    league,
)

render_destination_header(destination)

render_executive_summary(destination)

render_career_impact(destination)

render_gateway_clubs(destination)

render_career_examples(destination)

render_money(destination)

render_environment(destination)

render_sources(destination)
