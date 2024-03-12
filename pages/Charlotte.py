import pandas as pd
import numpy as np
import streamlit as st

cross_reference = pd.read_csv('pages\Cross-Reference Sheet_Charlotte.csv')
winners_losers = pd.read_csv('pages\Winners and Losers_Charlotte.csv')
player_decks = cross_reference.drop("Unnamed: 0", axis=1)
match_results = winners_losers.drop("Unnamed: 0", axis=1)
#Assisted by ChatGPT 4.0
# Merge to add winner's deck
match_results = match_results.merge(player_decks, left_on='Winners', right_on='Name', how='left')
match_results.rename(columns={'Deck': 'winner_deck'}, inplace=True)
match_results.drop('Name', axis=1, inplace=True)

# Merge to add loser's deck
match_results = match_results.merge(player_decks, left_on='Losers', right_on='Name', how='left')
match_results.rename(columns={'Deck': 'loser_deck'}, inplace=True)
match_results.drop('Name', axis=1, inplace=True)

#Assisted by ChatGPT 4.0
# Fill NaN values with a placeholder string
match_results['winner_deck'] = match_results['winner_deck'].fillna('Unknown')
match_results['loser_deck'] = match_results['loser_deck'].fillna('Unknown')

# Create a new column for sorted matchups
match_results['matchup'] = match_results.apply(lambda row: tuple(sorted([row['winner_deck'], row['loser_deck']])), axis=1)

matchup_stats = match_results.groupby('matchup').apply(
    lambda group: pd.Series({
        'total_matches': len(group),
        'wins': sum(group['winner_deck'] == group['matchup'].apply(lambda x: x[0]))
    })
).reset_index()

# Calculate win rate
matchup_stats['win_rate'] = matchup_stats['wins'] / matchup_stats['total_matches']

#Assisted by ChatGPT 4.0
#import matplotlib.pyplot as plt
import plotly.express as px

# Extract unique decks
decks = set()
for matchup in matchup_stats['matchup']:
    decks.update(matchup)
decks = sorted(decks)

# Create a matrix for the heatmap
heatmap_data = pd.DataFrame(index=decks, columns=decks, data=0.0)
for index, row in matchup_stats.iterrows():
    deck1, deck2 = row['matchup']
    win_rate = row['wins'] / row['total_matches']
    heatmap_data.loc[deck1, deck2] = win_rate
    heatmap_data.loc[deck2, deck1] = 1 - win_rate  # Assuming symmetrical matchups

# Adjust for mirror matchups
for deck in decks:
    heatmap_data.loc[deck, deck] = 0.5

# Drop the 'Unknown' row and column
heatmap_data = heatmap_data.drop('Unknown', axis=0)  # Drop row
heatmap_data = heatmap_data.drop('Unknown', axis=1)  # Drop column

# Convert win rates to percentages
heatmap_data_percent = heatmap_data * 100

import plotly.express as px

# Create the heatmap with Plotly
fig = px.imshow(heatmap_data_percent,
                labels=dict(x='Deck 2', y='Deck 1', color='Deck 1 Win Rate (%)'),
                x=heatmap_data_percent.columns,
                y=heatmap_data_percent.index,
                text_auto='.1f',  # Automatically add text
                aspect='auto',  # Adjust the aspect ratio
                color_continuous_scale=['red', 'yellow', 'green'])  # Red to Blue color scale, reversed

fig.update_layout(title='Win Rates for Pokemon TCG Matchups at Charlotte Regional',
                  xaxis_title='Deck 2',
                  yaxis_title='Deck 1')

fig.update_layout(
    width=1500,  # Adjust the width of the figure
    height=700,  # Adjust the height of the figure
    font=dict(size=15)  # Adjust the font size
)

fig.update_traces(textfont_size=14)

st.set_page_config(layout="wide")
st.plotly_chart(fig, use_container_width=True)