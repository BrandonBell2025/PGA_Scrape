from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
from dotenv import load_dotenv
import os

def scrape(url):
    #Setup driver and try to load the webpage based on the user input
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
    #Capture html for all of the titles of the stats we are scraping
    allStatTitles = soup.find_all('span', class_='chakra-text css-h2dnm1')
    statTitle = [item.text.strip() for item in allStatTitles]

    #Capture html for all the stats we are scraping
    allStatValues = soup.find_all('span', class_='chakra-text css-1psnea4')
    statValues = [item.text.strip() for item in allStatValues]

    #Pair stat title with stat value
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
    #Search player_IDs.csv for the inputted player name to retrieve player ID required for url
    df = pd.read_csv(csv_file)
    
    # Clean up whitespace issues in player names
    df['Player Name'] = df['Player Name'].str.strip()

    # Search for the player by name (ignoring case)
    result = df[df['Player Name'].str.contains(playerName.strip(), case=False, na=False)]
    
    if not result.empty:
        # Return the first matching player ID if found
        return result['Player ID'].values[0]
    else:
        print(f"Player '{playerName}' not found.")
        return None

def createCSV(stats, playerName, temperature, has_precipitation, precipitation_type, wind_speed, visibility):
    df = pd.DataFrame(stats, columns=['Stat Name', 'Stat Value', 'PGA Rank'])

    # Weather related stats will have 1.0x as a placeholder value. Weather API data is reflected in title of column
    if has_precipitation:
        precipitation = precipitation_type
    else: 
        precipitation = "Sunny"
    df[f'Temp Impact ({temperature}°F)'] = "1.0x"
    df[f'Precipitation Impact ({precipitation})'] = "1.0x"
    df[f'Wind Impact ({wind_speed}mph)'] = "1.0x"
    df[f'Visibility ({visibility}m)'] = "1.0x"

    #Create csv file with player name in the title
    newPlayerName = playerName.replace(" ", "_")
    df.to_csv(f'{newPlayerName}_stats.csv', index=False)
    print("Data saved to player_stats.csv.")

def weather(cityName):
    #retrieve the unique identifier for the inputted city to be used in subsequent weather function
    load_dotenv()
    WEATHER_API = os.getenv('WEATHER_API')
    
    url = "http://dataservice.accuweather.com/locations/v1/cities/search"
    params = {
        "apikey": WEATHER_API,
        "q": cityName,
        "language": "en-us",
        "details": "false"
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            location_key = data[0]['Key']  # Assuming we want the first match
            print(f"Location Key for {cityName}: {location_key}")
            return location_key
        else:
            print("No results found.")
    else:
        print(f"Error in retrieving city key: {response.status_code}")
    
def get_current_conditions(location_key):
    load_dotenv()
    WEATHER_API = os.getenv('WEATHER_API')
    
    # Define the API endpoint for current conditions using the location key
    url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
    params = {
        "apikey": WEATHER_API,
        "language": "en-us",
        "details": "true"
    }
    
    # Make the GET request to the API to get current conditions
    response = requests.get(url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if data:
            current_conditions = data[0]
        else:
            print("No current conditions data available.")
    else:
        print(f"Error fetching current conditions: {response.status_code}")

    return current_conditions


def main ():
    #prompt the user for the player and location they would like to analyze
    playerName = input("Enter player of interest: ")
    city = input("Enter the location (city) of the golf tournament: ")

    #Retrieve player ID, necessary for URL and scrape player data
    csv_file = 'player_IDs.csv'
    ID = searchPlayerID(csv_file, playerName)
    if ID: 
        url = f"https://www.pgatour.com/player/{ID}/{playerName}/stats"
        soup = scrape(url)
        stats = scrapeStats(soup)
    else:
        return
    
    #Retrieve the location key and current conditions from weather API
    locationKey = weather(city)
    if locationKey:
        currentConditions = get_current_conditions(locationKey)
        temperature = currentConditions['Temperature']['Imperial']['Value']  
        has_precipitation = currentConditions['HasPrecipitation']
        precipitation_type = currentConditions.get('PrecipitationType', 'None')
        wind_speed = currentConditions['Wind']['Speed']['Imperial']['Value']  
        visibility = currentConditions['Visibility']['Imperial']['Value']  

        #Create a csv cleanly outlining the data set
        createCSV(stats, playerName, temperature, has_precipitation, precipitation_type, wind_speed, visibility)

if __name__ == "__main__":
    main()