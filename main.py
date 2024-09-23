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
    # Initialize the web driver and load the webpage
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        driver.get(url)
    except:
        print("Error loading webpage")
    
    time.sleep(5)  # Allow time for page content to load
    data = driver.page_source
    driver.quit()

    soup = BeautifulSoup(data, 'html.parser')
    return soup

def scrapeStats(soup):
    # Capture the titles of the stats
    allStatTitles = soup.find_all('span', class_='chakra-text css-h2dnm1')
    statTitle = [item.text.strip() for item in allStatTitles]

    # Capture the stat values
    allStatValues = soup.find_all('span', class_='chakra-text css-1psnea4')
    statValues = [item.text.strip() for item in allStatValues]

    # Pair stat titles with stat values
    data = []
    for i in range(len(statTitle)):
        if i * 2 + 1 < len(statValues):
            value1 = statValues[i * 2]
            value2 = statValues[i * 2 + 1]
        else:
            value1 = 'N/A'
            value2 = 'N/A'
        data.append([statTitle[i], value1, value2])

    return data 

def searchPlayerID(csv_file, playerName):
    # Search for the player ID in the CSV file based on the player's name
    df = pd.read_csv(csv_file)
    df['Player Name'] = df['Player Name'].str.strip()

    result = df[df['Player Name'].str.contains(playerName.strip(), case=False, na=False)]
    
    if not result.empty:
        return result['Player ID'].values[0]
    else:
        print(f"Player '{playerName}' not found.")
        return None
    
def clean_stat_value(value):
    # Remove quotes and clean specific stat formats
    value = value.replace('"', '')

    if '$' in value:
        return value
    
    if "'" in value:
        value = value.replace(" ", "")
    
    return value

def createCSV(stats, playerName, temperature, has_precipitation, precipitation_type, wind_speed, visibility):
    df = pd.DataFrame(stats, columns=['Stat Name', 'Stat Value', 'PGA Rank'])

    # Clean the 'Stat Value' column
    df['Stat Value'] = df['Stat Value'].apply(clean_stat_value)

    # Add weather-related columns to the DataFrame
    precipitation = precipitation_type if has_precipitation else "Clear"
    df[f'Temp Impact ({temperature}°F)'] = "1.0x"
    df[f'Precipitation Impact ({precipitation})'] = "1.0x"
    df[f'Wind Impact ({wind_speed}mph)'] = "1.0x"
    df[f'Visibility ({visibility}m)'] = "1.0x"

    # Save the DataFrame to a CSV file
    newPlayerName = playerName.replace(" ", "_")
    df.to_csv(f'{newPlayerName}_stats.csv', index=False)
    print(f"Data saved to {newPlayerName}_stats.csv.")

def weather(cityName):
    # Retrieve the location key for the inputted city
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
            location_key = data[0]['Key']
            print(f"Location Key for {cityName}: {location_key}")
            return location_key
        else:
            print("No results found.")
    else:
        print(f"Error in retrieving city key: {response.status_code}")
    
def get_current_conditions(location_key):
    # Fetch the current weather conditions using the location key
    load_dotenv()
    WEATHER_API = os.getenv('WEATHER_API')
    
    url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
    params = {
        "apikey": WEATHER_API,
        "language": "en-us",
        "details": "true"
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            current_conditions = data[0]
            return current_conditions
        else:
            print("No current conditions data available.")
    else:
        print(f"Error fetching current conditions: {response.status_code}")

def main():
    # Prompt user for player and location input
    playerName = input("Enter player of interest: ")
    city = input("Enter the location (city) of the golf tournament: ")

    # Retrieve player ID and scrape data if ID is found
    csv_file = 'player_IDs.csv'
    ID = searchPlayerID(csv_file, playerName)
    if ID: 
        url = f"https://www.pgatour.com/player/{ID}/{playerName}/stats"
        soup = scrape(url)
        stats = scrapeStats(soup)
    else:
        return
    
    # Retrieve weather data and save the combined information to a CSV file
    locationKey = weather(city)
    if locationKey:
        currentConditions = get_current_conditions(locationKey)
        temperature = currentConditions['Temperature']['Imperial']['Value']  
        has_precipitation = currentConditions['HasPrecipitation']
        precipitation_type = currentConditions.get('PrecipitationType', 'None')
        wind_speed = currentConditions['Wind']['Speed']['Imperial']['Value']  
        visibility = currentConditions['Visibility']['Imperial']['Value']  

        createCSV(stats, playerName, temperature, has_precipitation, precipitation_type, wind_speed, visibility)

if __name__ == "__main__":
    main()
