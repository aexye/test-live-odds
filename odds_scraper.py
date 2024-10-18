from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
from base64 import b64decode
import time
import streamlit as st

class HorseOddsScraper:
    def __init__(self):
        self.base_url = "https://www.oddschecker.com"
        self.odds_data = {}
    

    def get_html_content(self, url, max_retries=3, retry_delay=5):
        for attempt in range(max_retries):
            try:
                payload = {
                    "api_key": st.secrets["narf_api_key"],
                    "url": url,
                    # "render_js": "true",
                }

                response = requests.get("https://scraping.narf.ai/api/v1/", params=payload)
                print(f"Response code: {response.status_code}")
                #if any of 50* response code, retry
                if response.status_code // 100 == 5:
                    print(f"Received {response.status_code} error. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                
                response.raise_for_status()  # Raise an exception for other HTTP errors
                return response.content
                
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Unable to fetch content.")
        
        return None

    def scrape_race_options(self):
        html_content = self.get_html_content('https://www.oddschecker.com/')
        soup = BeautifulSoup(html_content, 'html.parser')
        race_meets = soup.find('div', class_='race-meets')
        race_details = race_meets.find_all('div', class_='race-details')
        
        results = []
        for race_detail in race_details:
            # Extract venue name
            venue_element = race_detail.find('a', class_='venue')
            venue_name = venue_element.text if venue_element else "Unknown Venue"
            
            # Extract race times and links
            race_times = race_detail.find_all('a', class_='race-time')
            races = []
            for race in race_times:
                time = race['data-event-name']
                link = race['href']
                races.append({'time': time, 'link': urljoin(self.base_url, link)})
            
            results.append({
                'venue': venue_name,
                'races': races
            })
        
        return results

    def extract_horse_odds(self, url):
        html_content = self.get_html_content(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all rows with the specified classes
        rows = soup.find_all('tr', class_=['diff-row', 'evTabRow', 'bc'])
        
        results = []
        for row in rows:
            # Extract horse name
            name_element = row.get('data-bname')
            if name_element:
                horse_name = name_element
            else:
                continue
            
            # Extract odds
            odds = {}
            odds_cells = row.find_all('td', class_=['bc', 'bs'])
            for cell in odds_cells:
                bookmaker = cell.get('data-bk')
                if bookmaker:
                    odds_value = cell.get('data-odig')
                    odds[bookmaker] = odds_value
            

            results.append({
                'horse': horse_name,
                'odds': odds
            })
        
        return results

