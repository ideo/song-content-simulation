import os
from copy import deepcopy
from collections import Counter

import numpy as np
import pandas as pd

from src import logic as lg
from src import Simulation, load_or_generate_objective_scores, DATA_DIR


def repeat_N_times(sim, num_contests):
    """
    Run the first simulation num_contests times and compare the list of nominees.

    This is done rather clunkily, but oh well
    """
    sim = deepcopy(sim)

    filename = lg.format_repeated_results_filename(sim, num_contests)
    filepath = DATA_DIR / filename

    df = pd.DataFrame(index=range(sim.num_winners))
    df.index.name = "Winners"
    long_col_name = f"How Many Times a Song Made it into the Top {sim.num_winners}"
    
    for ii in range(num_contests):
        sim.simulate()
        df[f"Contest {ii}"] = sim.condorcet.top_nominee_ids
        print(f"Contest {ii} complete. Winners are: {sim.condorcet.top_nominee_ids}.")

        # Save results every ten iterations
        if ii % 10 == 0 and ii > 0:
            # How many times did each song make it into the top 10?
            contest_tallies = Counter(np.concatenate(df.values))

            if os.path.exists(filepath):
                chart_df = pd.read_pickle(filepath)
                for key, value in contest_tallies.items():
                    chart_df.at[key, long_col_name] = value

            else:
                chart_df = pd.DataFrame(
                    index=contest_tallies.keys(), 
                    data=contest_tallies.values(),
                    columns=[long_col_name])
                
                chart_df = chart_df.merge(sim.song_df, 
                    left_index=True, 
                    right_index=True,
                    how="left")

            chart_df.to_pickle(filepath)
            print(chart_df)

    # This returns the top N noninees specifed by sim.num_winners
    # unique_orderings = set([tuple(winners) for winners in df.T.values])
    # unique_winners = set([tuple(sorted(winners)) for winners in df.T.values])
    # return unique_orderings, unique_winners    
    return sim, num_contests


# Run repeated contests ahead of time, not in the streamlit app.
if __name__ == "__main__":
    num_voters = 2000
    num_songs = 2000
    num_winners = 20

    # The results of these repeated contests are only valid as long as 
    # these pickled dataframes don't change. So we'll need to push the final 
    # one we want to use to the repo.
    song_df = load_or_generate_objective_scores(num_songs)
    sim = Simulation(song_df,
        num_voters=num_voters,
        num_winners=num_winners)

    num_contests=100
    repeat_N_times(sim, num_contests)


