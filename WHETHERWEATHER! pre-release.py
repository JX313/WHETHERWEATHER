import flet as ft
import mysql.connector as mysql
import python_weather
import datetime
import asyncio
import os

##----------------------JOBS REMAINING----------------------##
'''
1) fix the 'about' page container issue; also add scroll bar
2) fix positions for each widget in every page
3) add icons8 icons by calling the weather.kind attribute
4) implement loading screen to fix issue of  new weather fetching delay
5) checkout iOS theme (cupertino) compatibility and complexity
6) add MySQL support
'''

##----------------------REF LINKS----------------------##
'''
GETTING STARTED WITH FLET-->
https://www.geeksforgeeks.org/python/building-flutter-apps-in-python/
https://flet.dev/docs/getting-started/flet-controls/

REFERENCE CONVERSATIONS WITH BLACKBOX AI-->
https://www.blackbox.ai/chat/tMR0XWR
https://www.blackbox.ai/chat/hNsi41I (FOR CUPERTINO-STYLING)

ICONS-->
https://icons8.com/icons/set/weather--style-arcade--gradient
https://icons8.com/icons/set/weather--style-color-glass--os-windows
https://icons8.com/icons/set/weather--style-color--os-android
https://icons8.com/icons/set/weather-gradient--style-cute-clipart
'''

'''globals'''
globalargs, weather_today, forecast=None, None, None

'''python-weather'''
async def get_weather_api_result(place: str) -> None:
  
  # Declare the client. The measuring unit used defaults to the metric system (celcius, km/h, etc.)
  async with python_weather.Client(unit=python_weather.METRIC) as client:
    
    # Fetch a weather forecast from a city.
    weather = await client.get(place)
    
    # return the weather API result
    return weather

def extract_global_args(weather: python_weather.forecast.Forecast) -> dict:
    # extracts common info from the forecast output
    globalarg={
        'coords':weather.coordinates, # coordinates of forecast location
        'region':weather.region, # region of forecast
        'country': weather.country, # the country where the location is present
        'location':weather.location,# the location of forecast
        'date': weather.datetime.strftime("%Y-%m-%d") # date of query in YYYY-DD-MM format
        }
    return globalarg

def get_weather_today(weather: python_weather.forecast.Forecast) -> dict:
    # extract weather data for today
    weather_output = {}
    weather_output['description'] = weather.description # weather description
    weather_output['feels_like'] = weather.feels_like # temperature felt by people
    weather_output['humidity'] = weather.humidity # humidity
    weather_output['kind'] = weather.kind # the string rep. of the kind of weather
    weather_output['precipitation'] = weather.precipitation # precipitation in the unit system specified
    weather_output['temperature'] = weather.temperature # temperature today
    weather_output['wind_speed'] = weather.wind_speed # windspeed in 
    return weather_output

def extract_from_daily_forecast(forecast: python_weather.forecast.DailyForecast) -> dict:
    # extract the relevant parameters of each daily forecast
    daily_forecasts={
        'highest_temperature':forecast.highest_temperature,
        'lowest_temperature':forecast.lowest_temperature,
        'average_temperature':forecast.temperature
        }
    return daily_forecasts

def get_forecasts(weather: python_weather.forecast.Forecast) -> dict:
    # extract the forecasts for each date (till two days forward)
    forecasts = {daily.date.strftime("%Y-%m-%d"):extract_from_daily_forecast(daily) for daily in weather}
    return forecasts

## --------------------- MAIN FUNCTION ---------------------- ##

def process_weather(place: str) -> list:
    output = asyncio.run(get_weather_api_result(place))
    global_args = extract_global_args(output)
    weather_today = get_weather_today(output)
    forecasts = get_forecasts(output)
    return [global_args, weather_today, forecasts]


if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

'''extracting new weather info to variables'''
def get_weather(city):
    global globalargs, weather_today, forecast
    globalargs, weather_today, forecast=process_weather(city.value)

##-------------------------------FRONT-END-------------------------------##
def main(page:ft.Page):
    #initializing the homepage
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.title=("WHETHERWEATHER!")

    def home_page():
        return ft.Column(controls=
                         [ft.Text("Welcome to WHETHERWEATHER!", size=30),
                          ft.Button(text="Search for weather in a city...", on_click= lambda e: page.go("/fetchweather")),
                          ft.Button(text="Search for saved weather...", on_click=lambda e: page.go("/saved")),
                          ft.Button(text="About this app...", on_click= lambda e: page.go("/about")),
                          ft.Button(text="Quit app")],
                          alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          expand=True)
    def new_weather():
        global city
        city=ft.TextField(label="Enter the city name", width=500)
        return ft.Column(controls=
                         [ft.Text("Search for a city's weather", size=25),
                          ft.Text("(Enter the place name in title case. Specify the state )"),
                          city,
                          ft.Button("Search", on_click=lambda e: page.go("/fetchweather/weather")),
                          ft.Button("Back", on_click=lambda e: page.go("/"))],
                          alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          expand=True)
    def fetched_new_weather():
        if city != "":
            get_weather(city)
            contain=ft.Container(ft.Column(controls=[
                ft.Text("Coordinates: {}".format(globalargs['coords'])),
                ft.Text("Place: {}".format(globalargs['location'])),
                ft.Text("Date: {}".format(globalargs['date'])),
                ft.Text("Today's forecast:", size=22),
                ft.Text("Description: {}".format(weather_today['description'])),
                ft.Text("Temperature: {}".format(weather_today['temperature']))
                ]))
            return ft.Column(controls=
                             [ft.Text("Weather in %s: "%(city.value,), size=30),
                              contain,
                              ft.Button("Back", on_click=lambda e: page.go("/fetchweather")),
                              ft.IconButton(icon=ft.Icons.HOUSE_OUTLINED, on_click= lambda e:page.go("/"))],
                              alignment=ft.MainAxisAlignment.CENTER,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                              expand=True)


    def saved_weather():
        global search_city, search_ccode
        search_city=ft.TextField(label="Enter the city name", width=500)
        search_ccode=ft.TextField(label="Enter country code", width=500)
        return ft.Column(controls=
                         [ft.Text("Look up weather data that you saved.", size=25),
                          ft.Text("Back by MySQL™. Simple. Secure. Safe.", size=15),
                          search_city,
                          search_ccode,
                          ft.Button("Search", on_click= lambda e: page.go("/saved/fetchedsavedweather")),
                          ft.Button("Back", on_click= lambda e: page.go("/"))],
                          alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          expand=True)
    def fetched_saved_weather():
        if search_city !="" and search_ccode!="":
            return ft.Column(controls=[
                ft.Text("Here's a history of the city's weather:", size=30), 
                ft.Button("Back", on_click= lambda e: page.go("/")),
                ft.Button("Save today's weather..."),
                ft.IconButton(icon=ft.Icons.HOUSE_OUTLINED, on_click= lambda e:page.go("/"))],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True)
        
    def about_this_app():
        return ft.Column(controls=
                         [ft.Container(content=ft.Text(
                             """
                             This Python-based application, by the name of 'WHETHERWEATHER!', 
                             serves the purpose of retrieving weather data of a place and for storing
                             and reading the weather history at that place whenever you opt to store it.
                             This application runs on the python-weather module, a free and asynchronous weather 
                             Python API wrapper, and utilizes the flet module, a Flutter-substituent 
                             module for Python, available to Python, to make it user-friendly. 

                             Copyright © WHETHERWEATHER! 2025; No rights reserved.

                             This software is not provided AS IS, IF NOT, WORKING PROPERLY blah blah blah and totally
                             meets your expectations. 
                             Make sure to give this program's repo on GitHub a star so that this becomes popular. :)
                             """,
                size=20,
                text_align=ft.TextAlign.CENTER,
                color=ft.Colors.BLACK87
                ),
                width=750,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_50,
                padding=20,
                border_radius=10), ft.Button("Back", on_click= lambda e: page.go("/"))])
                
    def show_alert(e):
        page.dialog=ft.AlertDialog(title="Alert!", content=ft.Text("Are you sure you want to go home?", size=20), 
                                   controls=
                                   [ft.Button("Yes", on_click= lambda e: page.go("/")), 
                                    ft.Button("No", on_click= lambda e: page.dialog.close)])   
        page.dialog.open=True
        page.update() 

    def navig(e):
        page.controls.clear()
        if page.route == "/":
            page.add(home_page())
        elif page.route == "/fetchweather":
            page.add(new_weather())
        elif page.route == "/fetchweather/weather":
            page.add(fetched_new_weather())
        elif page.route == "/saved":
            page.add(saved_weather())
        elif page.route == "/saved/fetchedsavedweather":
            page.add(fetched_saved_weather())
        elif page.route == "/about":
            page.add(about_this_app())


    page.on_route_change = navig
    page.go(page.route or "/")


##-----------------------------START THE WINDOW-----------------------------##
ft.app(target=main)