import streamlit as st
import pandas as pd
import json
import time
from odds_scraper import HorseOddsScraper

scraper = HorseOddsScraper()

bookmakers = {
        'B3': 'Bet365',
        'SK': 'Skybet',
        'PP': 'Paddy Power',
        'WH': 'William Hill',
        'EE': 'Betfred',
        'FB': 'Betfair',
        'VC': 'Betvictor',
        'LD': 'Ladbrokes',
        'UN': 'Unibet',
        'SX': 'Spredex',
        'FR': 'BETFRED',
        'KN': 'BETMGM',
        'BY': 'Boylesports',
        'OE': '10Bet',
        'S6': 'StarSports',
        'DP': 'BetUK',
        'SI': 'SportingIndex',
        'LS': 'Livescore Bet',
        'QN': 'Quinnbet',
        'WA': 'Betway',
        'CE': 'Coral',
        'N4': 'Midnite',
        'G5': 'Bet Goodwin',
        'VT': 'Vbet',
        'AKB': 'AK Bets',
        'BF': 'Betfair Exchange',
        'MA': 'Matchbook Exchange'
    }


@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_race_options():
    return scraper.scrape_race_options()

st.title("Live odds for UK & IRE horse racing")
st.write("This app shows the live odds for UK & IRE horse racing")

race_options = get_race_options()

# Get list of venues
col1, col2 = st.columns(2)

with col1:
    venues = [option['venue'] for option in race_options]
    venue = st.selectbox("Select a venue", venues)

    # Find the selected venue's races
    selected_venue = next(option for option in race_options if option['venue'] == venue)
    races = selected_venue['races']
    times = [race['time'] for race in races]
    race_time = st.selectbox("Select a race", times)

with col2:
    bookmakers_df = pd.DataFrame(bookmakers.items(), columns=['Code', 'Name'])
    st.dataframe(bookmakers_df, height=200, hide_index=True)

# Find the selected race's odds
selected_race = next(race for race in races if race['time'] == race_time)



# Function to create a DataFrame from odds data
def create_odds_dataframe(odds_data):
    df = pd.DataFrame(odds_data)
    df_normalized = pd.json_normalize(df['odds'])
    result_df = pd.concat([df['horse'], df_normalized], axis=1)
    result_df.set_index('horse', inplace=True)
    return result_df

# Function to style the DataFrame based on odds changes
def style_dataframe(current_df, previous_df):
    def style_cell(value):
        if previous_df is None or value.name not in previous_df.index or value.name == 'horse':
            return [''] * len(value)
        
        styles = []
        for col, val in value.items():
            if col == 'horse':
                styles.append('')
                continue
            previous_value = previous_df.loc[value.name, col]
            if val > previous_value:
                styles.append('background-color: #d4edda; color: #155724')  # Light green background, dark green text
            elif val < previous_value:
                styles.append('background-color: #f8d7da; color: #721c24')  # Light red background, dark red text
            else:
                styles.append('')
        return styles

    return current_df.style.apply(style_cell, axis=1)

if st.button("Submit"):
    scraper = HorseOddsScraper()
    placeholder = st.empty()
    previous_df = None
    
    while True:
        # while odds_df is None, keep trying
        while odds_df is None:
            odds_df = scraper.extract_horse_odds(selected_race['link'])
        current_df = create_odds_dataframe(odds_df)
        
        styled_df = style_dataframe(current_df, previous_df)
        
        with placeholder.container():
            st.write("Last updated:", time.strftime("%H:%M:%S"))
            st.dataframe(styled_df)
        
        previous_df = current_df.copy()
        time.sleep(11)  # Wait for 10 seconds before the next update
