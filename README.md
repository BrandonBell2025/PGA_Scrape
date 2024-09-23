# Player Performance & Weather Impact Analysis

## Overview

This program collects **PGA player statistics** and **real-time weather data** to create a unique dataset designed for sports bettors and data scientists. This dataset serves as a crucial input for machine learning models aimed at predicting player performance under varying weather conditions.

## Dataset Value

By integrating player stats with weather conditions (like temperature, wind, and precipitation), this dataset provides:
- **Enhanced Insights**: It allows users to explore how specific weather scenarios might impact player behavior.
- **Machine Learning Input**: The data can be utilized in predictive models to assess potential performance variations based on weather, enabling bettors to make more informed decisions.

The dataset also includes **1.0x multipliers** as placeholders for the output of machine learning models, which will apply these multipliers based on the weather conditions described in the column headers.

Such a comprehensive dataset is not widely available, offering a distinct advantage to those looking to incorporate weather factors into their betting strategies.

## How to Use

1. **Clone this repository**:
   ```bash
   git clone https://github.com/your-repository-link

2. **Install the required packages**:
   ```bash
   pip install -r requirements.txt

3. **Obtain an AccuWeather API Key**:
   - Sign up for an AccuWeather API account at AccuWeather Developer Portal.
   - Generate an API key and add it to your environment variables (e.g., .env file) as WEATHER_API.

4. **Run the updatePlayerIDs.py script to ensure the player ID database is up to date**:
   ```bash
   python updatePlayerIDs.py

5. **Run the program**:
   ```bash
   python main.py

6. **Input player name and location to generate a CSV report containing the combined player stats and weather data.**


