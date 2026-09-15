import python_weather
from datetime import datetime
import asyncio
#import nest_asyncio
#nest_asyncio.apply()
import os
from state import state

async def get_weather_api_result(place: str) -> None:
    try:
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            weather = await client.get(place)
            return weather 

    except Exception as e:
        return {'error': str(e)}
 
def extract_global_args(weather: python_weather.forecast.Forecast) -> dict:
    globalarg={
        'coords':weather.coordinates,
        'region':weather.region,
        'country': weather.country,
        'location':weather.location,
        'date': weather.datetime.strftime("%Y-%m-%d"),
        'time': weather.datetime.strftime("%H:%M:%S")
        }
    return globalarg

def get_weather_today(weather: python_weather.forecast.Forecast) -> dict:
    weather_output = {}
    weather_output['description'] = weather.description
    weather_output['feels_like'] = weather.feels_like
    weather_output['humidity'] = weather.humidity
    weather_output['kind'] = weather.kind
    weather_output['precipitation'] = weather.precipitation
    weather_output['temperature'] = weather.temperature
    weather_output['wind_speed'] = weather.wind_speed
    return weather_output 

 
def extract_from_daily_forecast(forecast: python_weather.forecast.DailyForecast) -> dict:
    daily_forecasts={
        'highest_temperature':forecast.highest_temperature,
        'lowest_temperature':forecast.lowest_temperature,
        'average_temperature':forecast.temperature
        }
    return daily_forecasts 


def get_forecasts(weather: python_weather.forecast.Forecast) -> dict:
    forecasts = {daily.date.strftime("%Y-%m-%d"):extract_from_daily_forecast(daily) for daily in weather}
    forecasts = dict(list(forecasts.items())[1:])
    return forecasts

 
## --------------------- WEATHER-PROCESSING FUNCTIONS ---------------------- ## 

def c_to_f(celsius):
    fahr=(celsius*1.8)+32
    return fahr 


async def process_weather(place: str) -> list:
    output = await get_weather_api_result(place)
    if isinstance(output, dict) and 'error' in output:
        return [{'error': output['error']}, None, None]
    global_args = extract_global_args(output)
    weather_today = get_weather_today(output)
    forecasts = get_forecasts(output) 

    return [global_args, weather_today, forecasts] 

 

#if os.name == 'nt':
#    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

'''extracting new weather info to variables''' 

async def get_weather(city):
    state.three_dates.clear()
    state.three_days.clear()
    (state.globalargs, state.weathertoday, state.forecast) = await process_weather(city.value)
    for key, value in state.forecast.items():
        state.three_dates.append(key)
        state.three_days.append(value)


        