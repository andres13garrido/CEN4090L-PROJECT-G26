import os
from dotenv import load_dotenv
from aiohttp import ClientSession

# Load and access the api key 
load_dotenv(dotenv_path="../.env")

# constants 
api_key = os.getenv("WEATHER_API_KEY")
base_url = "http://dataservice.accuweather.com"


# Helper function to get the location ID where we want to find the weather
async def location_id(location):
    async with ClientSession() as session:
        location_search_url = f"{base_url}/locations/v1/cities/search"
        params = {
            "apikey": api_key,
            "q": location,
        }
        async with session.get(location_search_url, params=params) as response:
            locations = await response.json()
            if locations and len(locations) > 0:
                location_key = locations[0]["Key"]
                return location_key
            return None


# Call the weather API and then return weather
async def get_weather(city: str) -> str:
    """ 
    Give me the weather for the city that the user gave you using this function. 
    """
    try:
        # First get the location key
        city_key = await location_id(city)
        if not city_key:
            return f"Did not find city: {city}"
            
        # Get current conditions
        async with ClientSession() as session:
            current_conditions_url = f"{base_url}/currentconditions/v1/{city_key}"
            params = {
                "apikey": api_key,
                "metric": "true",
            }

            async with session.get(current_conditions_url, params=params) as response:
                current_conditions = await response.json()
                
                if current_conditions and len(current_conditions) > 0:
                #     # Return the weather information as a formatted string
                #     weather_text = current_conditions[0].get("WeatherText", "Unknown")
                #     temperature = current_conditions[0].get("Temperature", {}).get("Metric", {}).get("Value", "Unknown")
                    
                    # return f"Current weather in {city}: {weather_text}, Temperature: {temperature}°C"
                    return current_conditions
    except Exception as e:
        return f"Error retrieving weather: {str(e)}"

