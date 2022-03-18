from ssl import CHANNEL_BINDING_TYPES
import streamlit as st
import pandas as pd
import time

from .story import STORY, INSTRUCTIONS, SUCCESS_MESSAGES
from .config import COLORS, ENTRANTS


import warnings
warnings.simplefilter(action='ignore', category=UserWarning)


def initialize_session_state():
    initial_values = {
        "simulation_1_keep_chart_visible":  False,
        "simulation_2_keep_chart_visible":  False,
        "simulation_3_keep_chart_visible":  False,
        "condorcet_keep_chart_visible":     False,
    }

    for key, value in initial_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_visuals():
    for key in st.session_state:
        if "_keep_chart_visible" in key:
            st.session_state[key] = False


def write_story(section_title):
    for paragraph in STORY[section_title]:
        st.write(paragraph)


def write_instructions(section_title, st_col=None):
    for paragraph in INSTRUCTIONS[section_title]:
        if st_col is not None:
            st_col.caption(paragraph)
        else:
            st.caption(paragraph)


def sidebar():
    """
    Let's put all the sidebar controls here!
    """
    st.sidebar.subheader("Simulation Parameters")
    keep_out = """
        HEY! What are you doing it here? This area is off limits! Only Fra and 
        Joe are allowed in here! Get outta here ya meddling kids!
    """
    st.sidebar.write(keep_out)
    num_townspeople = st.sidebar.slider("How many townspeople are there?", 
        value=250, 
        min_value=10, 
        max_value=500,
        step=10)
    st_dev = st.sidebar.number_input("What is the st. dev. of their randomly generated scores?",
        value=1.0,
        min_value=0.1,
        max_value=5.0,
        step=0.1
        )
    fullness_factor = st.sidebar.number_input("What is the mean offset of the fullness factor?",
        value=1.0,
        min_value=0.1,
        max_value=3.0,
        step=0.1
        )
    return num_townspeople, st_dev, fullness_factor


def choose_scenario():
    """
    The user selects a scenario, which determines the 'objective ratings' to be
    used in the simulation.
    """

    #define the structure of the entry as 2 columns
    col1, col2 = st.columns([2,5])

    #one column has a widget with 2 options
    options = list(ENTRANTS[0].keys())
    options.remove("ID")
    options.remove("Entrant")

    scenario = col1.radio(
        "Choose a scenario", 
        # options=OBJECTIVE_RATINGS.keys(),
        options=options,
        index=0,
        on_change=reset_visuals)

    df = pd.DataFrame(data=ENTRANTS)
    df["Objective Ratings"] = df[scenario].copy()

    #pull data based on corresponding scenario
    # df = pd.DataFrame(
    #     columns=["Objective Ratings"], 
    #     data=OBJECTIVE_RATINGS[scenario])
    # df["Entrant"] = df.index
    # df["Entrant"] = df["Entrant"].apply(lambda x: ENTRANTS[x]["Name"])
    winner = df["Objective Ratings"].idxmax()
    winning_score = df["Objective Ratings"].max()
    df["Color"] = df["Objective Ratings"].apply(
        lambda x: COLORS["green"] if x==winning_score else COLORS["blue"])

    # st.write(df)
    #draw the chart
    spec = {
        "height":   275,
        "mark": {"type": "bar"},
        "encoding": {
            "x":    {
                "field": "Entrant", "type": "nominal", "sort": "ID", 
                "axis": {"labelAngle": 45}
                },
            "y":    {"field": "Objective Ratings", "type": "quantitative"},
            "color":    {"field": "Color", "type": "nomical", "scale": None}
        },
        "title":    {
            "text": scenario, 
            "subtitle": f"The Best Guac is Guac No. {winner}"},   
    }

    col2.vega_lite_chart(df, spec)
    return df


def animate_results(sim, key):
    """
    Creates the `Simulate` button, animated chart, and success/fail message
    """
    col1, col2 = st.columns([2,5])
    start_btn = col1.button("Simulate", key=key)

    results_df = sim.results_df.copy()
    results_df.drop(columns=["sum"], inplace=True)
    subtitle = "And the winner is... "
    y_max = int(sim.results_df["sum"].max())

    bar_chart = None
    if start_btn:
        st.session_state[f"{key}_keep_chart_visible"] = True
        for NN in range(results_df.shape[1]):
            chart_df, spec = format_spec(sim, subtitle, y_max, col_limit=NN)
            # overwrite_chart(col2, bar_chart, chart_df, spec)
            if bar_chart is not None:
                bar_chart.vega_lite_chart(chart_df, spec)
            else:
                bar_chart = col2.vega_lite_chart(chart_df, spec)
            time.sleep(0.01/2)

    if st.session_state[f"{key}_keep_chart_visible"]:
        # Ensure the final chart stays visible
        chart_df, spec = format_spec(sim, subtitle, y_max)
        # overwrite_chart(col2, bar_chart, chart_df, spec)
        if bar_chart is not None:
            bar_chart.vega_lite_chart(chart_df, spec)
        else:
            bar_chart = col2.vega_lite_chart(chart_df, spec)

        # message_var = None
        # if sim.assigned_guacs < results_df.shape[0]:
        #     message_var = results_df.shape[0] - sim.assigned_guacs
        # success_message(key, sim.success, message_var)


#this is an experiment, to include an image with the winner        
def get_winner_image(sim, key):
    col1, col2 = st.columns([2,5])
    start_btn = col1.button("Simulate", key=key)

    if start_btn:
        col1, col2, col3 = st.columns(3)
        col2.image("img/badge2.png", width=100, caption="badge test.")


def format_spec(sim, subtitle, y_max, col_limit=None):
    """Format the chart to be shown in each frame of the animation"""

    if col_limit:
        chart_df = sim.results_df.iloc[:, :col_limit].copy()
        chart_df["sum"] = chart_df.sum(axis=1)
    else:
        chart_df = sim.results_df.copy()

    color_spec = None
    chart_df["Entrant"] = sim.guac_df["Entrant"]
    if col_limit is None:
        subtitle += f"Guacamole No. {sim.sum_winner}!"
        chart_df = format_bar_colors(sim, chart_df)
        color_spec = {"field": "Color", "type": "nomical", "scale": None}

    spec = {
            "height":   275,
            "mark": {"type": "bar"},
            "encoding": {
                "x":    {
                    "field": "Entrant", "tupe": "nominal", "sort": "ID",
                    "axis": {"labelAngle": 45}},
                "y":    {
                    "field": "sum", "type": "quantitative", 
                    "scale": {"domain": [0, y_max]},
                    "title": "Vote Tallies"},
                "color":    color_spec,
            },
            "title":    {
                "text": f"Simulation Results",
                "subtitle": subtitle, 
            }  
        }
    return chart_df, spec


def format_bar_colors(sim, chart_df):
    chart_df["Color"] = pd.Series([COLORS["blue"]]*chart_df.shape[0])
    chart_df.at[sim.sum_winner, "Color"] = COLORS["red"]
    chart_df.at[sim.objective_winner, "Color"] = COLORS["green"]
    return chart_df


def success_message(section_key, success, guac_limit=None):
    for paragraph in SUCCESS_MESSAGES[section_key][success]:
        if guac_limit is not None:
            st.caption(paragraph.replace("GUAC_LIMIT", str(guac_limit)).replace("MISSING_GUACS", str(20-guac_limit)))
        else:
            st.caption(paragraph)


def tally_votes(sim, key):
    col1, col2 = st.columns([2,5])

    col1.button("Simulate!")
    y_field = "sum"
    chart_df = sim.results_df[[y_field]].copy()

    #this is to accomodate mine and joe's simulations
    winning_guac = chart_df.idxmax()[0]
    chart_df["Entrant"] = sim.guac_df["Entrant"]

    spec = {
        "mark": {"type": "bar"},
        "encoding": {
            "x":    {"field": "Entrant", "tupe": "nominal"},
            "y":    {"field": y_field, "type": "quantitative"},
        },
        "title":    f"Our Winner is Guacamole No. {winning_guac}!",   
    }
    col2.vega_lite_chart(chart_df, spec)
    # st.write(sim.results_df)
    return y_field


# def declare_a_winner(sim, y_field):
#     winning_guac = sim.results_df[[y_field]].idxmax()[0]
#     top_score = sim.results_df[[y_field]].max()

#     # Make sure only one guac got the top score
#     if (sim.results_df[[y_field]] == top_score).astype(int).sum(axis=0)[0] > 1:
#         st.text("Oh no! We have a tie!")
#     elif winning_guac == sim.objective_winner:
#         st.text("Hooray! Democracy Prevails!")
#     else:
#         st.text("Oh no! We done fucked up!")


def types_of_voters(key):
    col1, col2, col3 = st.columns(3)
    pepe = col1.slider(
        """
        What percentage of people in town are like Perky Pepe, who loves 
        guacamole so much he'll have a hard time giving anyone a bad score?
        """,
        value=10,
        min_value=0,
        max_value=30,
        format="%g%%",
        key=key+"pepe")

    fra = col2.slider(
        """
        What percentage of people in town are like Finicky Francisca, who
        thinks all guacamole is basically mush and won't score any entry too high?
        """,
        value=8,
        min_value=0,
        max_value=30,
        format="%g%%",
        key=key+"fra")

    carlos = col3.slider(
        """
        What percentage of people in town are friends with Cliquey Carlos, and
        will score high guacamole as high as possible no matter what?
        """,
        value=12,
        min_value=0,
        max_value=30,
        format="%g%%",
        key=key+"carlos")

    pepe /= 100
    fra /= 100
    carlos /= 100
    return pepe, fra, carlos


def num_people_and_guac_per_person_slider():
    col1, _, col2 = st.columns([4, 1, 4])
    num_townspeople = col1.slider("How many townspeople showed up?", 
        value=250, 
        min_value=10, 
        max_value=500)
    num_guac_per_person = col2.slider("How many guacs can everyone try?",
        value=10,
        min_value=1,
        max_value=20,
        )
    return num_townspeople, num_guac_per_person


def num_people_slider(key):
    num_townspeople = st.slider(key, 
        value=250, 
        min_value=10, 
        max_value=500)
    return num_townspeople


def num_guac_per_person_slider(key):
    num_guac_per_person = st.slider(key, 
        value=10, 
        min_value=1, 
        max_value=20)
    return num_guac_per_person


def plot_votes(sim, day_title = 1):
    
    y_field = 'Avg'
    chart_df = sim.results_df[[y_field]].copy()
    chart_df["Entrant"] = chart_df.index

    winning_guac = sim.sum_winner
        
    spec = {
        "mark": {"type": "bar"},
        "encoding": {
            "x":    {"field": "Entrant", "tupe": "nominal"},
            "y":    {"field": y_field, "type": "quantitative"},
        },
        "title":    f"Day {day_title}: Our Winner is Guacamole No. {winning_guac}!",   
    }
    st.vega_lite_chart(chart_df, spec)

    
def animate_condorcet_simulation(sim, key=None):
    col1, col2 = st.columns([2,5])
    start_btn = col1.button("Simulate", key=key)

    if start_btn:
        st.session_state[f"{key}_keep_chart_visible"] = True
        
    if st.session_state[f"{key}_keep_chart_visible"]:
        results_msg = format_condorcet_results(sim)
        col2.markdown(results_msg)


def format_condorcet_results(sim):
    if len(sim.condorcet_winners) > 1:
        msg = "And the winners are..."
        for ii, entrant_id in enumerate(sim.condorcet_winners):
            name = sim.guac_df["Entrant"].iloc[entrant_id]
            msg += f"\n - {ii}: Guacamole No. {entrant_id} by {name}!"
    
    else:
        entrant_id = sim.condorcet_winner
        name = sim.guac_df["Entrant"].iloc[entrant_id]
        msg = f"""
            And the winner is...
            1. Guacamole No. {entrant_id} by {name}!
        """
    return msg

