from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import pandas as pd

def scrapeID(url_ID):
    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url_ID)
    data = driver.page_source  # Capture the HTML after JavaScript has rendered
    driver.quit()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(data, 'html.parser')
    return soup

def parseID(soupID):
    player_data = []
    
    # Find player links
    player_links = soupID.find_all('a', class_='chakra-linkbox__overlay')
    for link in player_links:
        player_name = link.get('aria-label')  # Get player name from the aria-label
        player_url = link.get('href')  # Get the href attribute

        # Use regex to extract the player ID from the URL
        match = re.search(r'/player/(\d+)/', player_url)
        if match:
            player_id = match.group(1)  # Extract the player ID
            player_data.append({
                'Player Name': player_name,
                'Player ID': player_id,
            })
    
    return player_data

def save_to_styled_csv(player_data, filename='player_IDs.csv'):
    # Load the player data into a pandas DataFrame
    df = pd.DataFrame(player_data)
    
    df = df.sort_values(by='Player Name')
    
    # Save the styled DataFrame to a CSV file
    df.to_csv(filename, index=False)
    
    print(f"Styled player data saved to {filename}.")

def main():
    url_ID = "https://www.pgatour.com/players"
    
    # Scrape and parse player data
    soupID = scrapeID(url_ID)
    player_data = parseID(soupID)
    
    # Save the player data to a styled CSV
    save_to_styled_csv(player_data)

if __name__ == "__main__":
    main()
