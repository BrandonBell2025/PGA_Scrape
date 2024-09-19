from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

def scrape(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        driver.get(url)

    except:
        print("Error loading webpage")

    time.sleep(5)
    data = driver.page_source  # Capture the HTML after JavaScript has rendered
    driver.quit()

    soup = BeautifulSoup(data, 'html.parser')
    return soup

def scrapeStats(soup):
    allStatTitles = soup.find_all('span', class_='chakra-text css-h2dnm1')
    statTitle = [item.text.strip() for item in allStatTitles]

    allStatValues = soup.find_all('span', class_='chakra-text css-1psnea4')
    statValues = [item.text.strip() for item in allStatValues]

    data = []
    for i in range(len(statTitle)):
        # Assuming there are exactly 2 values for each title
        if i * 2 + 1 < len(statValues):
            value1 = statValues[i * 2]
            value2 = statValues[i * 2 + 1]
        else:
            value1 = 'N/A'
            value2 = 'N/A'
        data.append([statTitle[i], value1, value2])

    return data 

def searchPlayerID(csv_file, playerName):
    df = pd.read_csv(csv_file)
    
    # Search for the player by name
    result = df[df['Player Name'].str.contains(playerName, case=False, na=False)]
    
    if not result.empty:
        # Return the player ID if found
        return result['Player ID'].values[0]
    else:
        return None

def createCSV(stats, playerName):
    df = pd.DataFrame(stats, columns=['Title', 'Stat', 'Rank'])
    newPlayerName = playerName.replace(" ", "_")
    df.to_csv(f'{newPlayerName}_stats.csv', index=False)
    print("Data saved to player_stats.csv.")

def main ():
    playerName = input("Enter player of interest: ")
    csv_file = 'player_IDs.csv'
    ID = searchPlayerID(csv_file, playerName)

    url = f"https://www.pgatour.com/player/{ID}/{playerName}/stats"
    soup = scrape(url)
    
    stats = scrapeStats(soup)
    createCSV(stats, playerName)


if __name__ == "__main__":
    main()