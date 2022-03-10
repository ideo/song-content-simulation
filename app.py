import streamlit as st
import pandas as pd

from src.story import STORY
import src.logic as lg
from src.simulation import Simulation
from src.simulation_unknown_best import Simulation_unknown_best
# from src.tuning import tune_simulation, create_histogram


st.set_page_config(
    page_title="Guacamole Contest",
    page_icon="img/avocado-emoji.png",
    initial_sidebar_state="collapsed")

lg.initialize_session_state()
num_townspeople, st_dev, fullness_factor = lg.sidebar()


st.title("The Allegory of the Avocados")
st.write("""
Here is the link to our 
[Google Doc](https://docs.google.com/document/d/1CA9NXp8I9b6ds16khcJLrY1ZL7ZBABK6KRu9SvBL5JI/edit?usp=sharing) 
where we're developing and commenting on the story.""")

st.subheader("Welcome to Sunnyvale")
lg.write_story("Introduction")


st.subheader("Let’s Play Guac God")
lg.write_story("Guac God")
lg.write_instructions("Guac God")
guac_df = lg.choose_scenario()

# create_histogram(guac_df)
st.subheader("Let's Taste and Vote!")
section_title = "simulation_1"
lg.write_story(section_title)
lg.write_instructions(section_title)
sim1 = Simulation(guac_df, num_townspeople, st_dev, fullness_factor=fullness_factor)
sim1.simulate()
lg.animate_results(sim1, key=section_title)


st.markdown("---")
lg.write_story("transition_1_to_2")
st.subheader("Not Enough Guac to Go Around")
section_title = "simulation_2"
lg.write_story(section_title)

col1, col2 = st.columns(2)
lg.write_instructions(section_title, col1)
guac_limit = col2.slider(
    "How many guacs do we limit people to?",
    value=18, 
    min_value=1, 
    max_value=20)


sim2 = Simulation(guac_df, num_townspeople, st_dev, assigned_guacs=guac_limit)
sim2.simulate()
lg.animate_results(sim2, key=section_title)


# # st.text("Let's see what the townspeople thought!")
# # chosen_method = lg.tally_votes(sim2, key="sim2")
# # lg.declare_a_winner(sim2, chosen_method)



# # st.subheader("A Fair Voting Process")
# # for paragraph in STORY["Voting"]:
# #     st.write(paragraph)


