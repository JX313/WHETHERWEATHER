import flet as ft
import base64
import mysql.connector as mysql
import python_weather
import datetime
import asyncio
import os

'''globals'''
globalargs, weathertoday, forecast=None, None, None
three_dates=[]
three_days=[]

## --------------------- BACKEND FUNCTIONS ---------------------- ##
'''mysql'''
conn=mysql.connect(host="localhost", user="root", password="1234", database="whetherweather")
cur=conn.cursor()

def create_new_table(city):
    cur.execute('create table if not exists %s(' \
    'searched_location varchar(30),' \
    'fetched_location varchar(30),' \
    'latitude decimal(4,2),' \
    'longitude decimal(4,2),' \
    'temperature_in_celsius int,' \
    'temperature_in_fahrenheit int,' \
    'description varchar(30));'%(city.value))
    cur.commit()

def save_to_table(info):
    cur.execute('insert into %s values(%s, %s, %s, %s, %s, %s, %s);'%(info))
    cur.commit()

def display_tables():
    control=[]
    cur.execute('show tables')
    retrieved_tables=cur.fetchall()
    for record in retrieved_tables:
        city_name=record[0]
        control.append(ft.Text(city_name))
    return control


def remove_table(searching_city):
    cur.execute('drop table %s'%(searching_city.value,))
    cur.commit()

def delete_all_data():
    cur.execute('show tables')
    tables=cur.fetchall()
    for (table,) in tables:
        cur.execute(f"drop table '{table}'")
    cur.commit()



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
    forecasts = dict(list(forecasts.items())[1:])
    return forecasts

## --------------------- MAIN FUNCTIONS ---------------------- ##

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
    global globalargs, weathertoday, forecast, three_days, three_dates
    globalargs, weathertoday, forecast=process_weather(city.value)
    for key, value in forecast.items():
        three_dates.append(key)
        three_days.append(value)
        
'''defining different weather kinds'''

def kinda_weather():
    image=""
    kind_of_weather=weathertoday['kind']
    if kind_of_weather == 'Clear':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/ER5ywBR_1TVEhT48KmYe1zwB6TOaTvqR6G2pE0uYOKpw0g?e=YJMXdm"
    elif kind_of_weather == 'Sunny':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/Ec5mzmSquHxJvJDS55Y-IPMBgtoX7vwaYkylVIqfDaGQpA?e=H6HvZz"
    elif kind_of_weather == 'Partly Cloudy':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/ER2tYpoZRvZPlfJ6r6yJMAwBlmQ7tFg-u6F_49nZUjckvw?e=TZVmHh"
    elif kind_of_weather == 'Cloudy':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/Eb9IyoAPy0FOpQ_gIQUkZ7IBj085d6BQS85nWfrtXKN0ew?e=eZeNKf"
    elif kind_of_weather == 'Very Cloudy':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/EX9L0wDrrHFJsLjoAIcJ-l4BXGAg3TpXdc5ALP_8HGdQwQ?e=kwgcbG"
    elif kind_of_weather == 'Fog':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/EV_Q1ytxHdNNqJVyW0i32KwB1VEbVBJqDRU0Jz5yzW9Ilw?e=bLBPiG"
    elif kind_of_weather == 'Light Showers':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/EZbusNr9mQpCgonqZEkcpNABueEPnY8t5hkAgMI89sNg9A?e=39Aijz"
    elif kind_of_weather == 'Light Sleet Showers':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/ERGBP9m9imNMioUo-2h6fbIBKfBTStJjS3zLSPtooAb6hw?e=661FZa"
    elif kind_of_weather == 'Light Sleet':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/ERGBP9m9imNMioUo-2h6fbIBKfBTStJjS3zLSPtooAb6hw?e=661FZa"
    elif kind_of_weather == 'Thundery Showers':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/Ee3Ge5-hTuVNlVR0QwDAQ7wBBEV4joxmiSrvJpRahZkUJA?e=AOW9d4"
    elif kind_of_weather == 'Light Snow':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/ESuq7-9SfAFLrHFu1AwpDRIBS4bdKd53PPABG-jrdKY_bg?e=O4KnsY"
    elif kind_of_weather == 'Heavy Snow':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/EfevGoyDwLRBpasL9wWMzAsBu8yVTD9etWNFShjSGQkTYw?e=6b61zg"
    elif kind_of_weather == 'Light Rain':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/EZbusNr9mQpCgonqZEkcpNABueEPnY8t5hkAgMI89sNg9A?e=39Aijz"
    elif kind_of_weather == 'Heavy Showers':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/EUWJI7VsRRpNgJRJUaCEnjEB-tAlGzlFTF5ZSCb7oUw28Q?e=8FojPe"
    elif kind_of_weather == 'Heavy Rain':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/ESmPbIOXBudPm80pziSICOYBsCua_Xl__VOtVhFb91v10w?e=b7MvMb"
    elif kind_of_weather == 'Light Snow Showers':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/ESuq7-9SfAFLrHFu1AwpDRIBS4bdKd53PPABG-jrdKY_bg?e=O4KnsY"
    elif kind_of_weather == 'Heavy Snow Showers':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/EfevGoyDwLRBpasL9wWMzAsBu8yVTD9etWNFShjSGQkTYw?e=6b61zg"
    elif kind_of_weather == 'Thundery Heavy Rain':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/Ee3Ge5-hTuVNlVR0QwDAQ7wBBEV4joxmiSrvJpRahZkUJA?e=krSoQF"
    elif kind_of_weather == 'Thundery Snow Showers':
        image="https://1drv.ms/i/c/2b4cf875021e3a16/EWnjnRfW8ppNoEpVe-mMBz0BQErnf5xHZmSTcoqh3V_-dg?e=1s5JfX"
    return image

'''
def encodeImage():
    img=kinda_weather()
    if img is None or not os.path.exists(img):
        print(f"Error: Image path is invalid or None: {img}")
        return ""
    with open(img, 'rb') as img:
        img_encoded=base64.b64encode(img.read()).decode("utf-8")

    return img_encoded
'''


#reference links: 
#https://www.blackbox.ai/chat/tMR0XWR
#https://www.blackbox.ai/chat/nCcGI1G
#https://flet.dev/docs/getting-started/flet-controls/
#https://www.geeksforgeeks.org/python/building-flutter-apps-in-python/
#https://www.blackbox.ai/chat/hNsi41I

'''icons
https://icons8.com/icons/set/weather-gradient--style-cute-clipart
https://icons8.com/icons/set/weather--style-color-glass
'''

#frontend kinda shi feelin lowkey
def main(page:ft.Page):
    #initializing the homepage
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.title=("WHETHERWEATHER!")
    '''def progress_bar():
        loading_indicator = ft.ProgressBar(value=0.0, width=300, height=20, color=ft.Colors.BLUE)
        loading_indicator.value = 0.5  # Set progress to 50%
        page.update()
        page.sleep(3)
        loading_indicator.visible = False
        page.update()'''

    def home_page():
        return ft.Column(controls=
                         [ft.Text("Welcome to WHETHERWEATHER!", size=30),
                          ft.Button(text="Search for weather in a city", on_click= lambda e: page.go("/fetchweather")),
                          ft.Button(text="View & manage saved weather", on_click= lambda e: page.go("/managedata")),
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
        if city!='':
            get_weather(city)
            weather_kind=kinda_weather()
            column1=ft.Container(ft.Column(controls=[
                ft.Text("Today's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
                ft.Text("Date: {}".format(globalargs['date'])),
                ft.Text("Description: {}".format(weathertoday['description'])),
                ft.Text("Temperature: {}℃".format(weathertoday['temperature'])),
                ft.Image(src=weather_kind),
                ft.Button("Save today's weather...")
                ]),
                width=350,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_400,
                opacity= 0.9,
                padding=20,
                border_radius=10)
            column2=ft.Container(ft.Column(controls=[
                ft.Text("Tomorrow's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
                ft.Text("Date: {}".format(three_dates[0])),
                ft.Text("Highest Temperature: {}℃".format(three_days[0]['highest_temperature'])),
                ft.Text("Lowest Temperature: {}℃".format(three_days[0]['lowest_temperature'])),
                ft.Text("Average Temperature: {}℃".format(three_days[0]['average_temperature']))
                ]),
                width=350,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_400,
                opacity=0.9,
                padding=20,
                border_radius=10)
            column3=ft.Container(ft.Column(controls=[
                ft.Text("The day after tomorrow's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
                ft.Text("Date: {}".format(three_dates[1])),
                ft.Text("Highest Temperature: {}℃".format(three_days[1]['highest_temperature'])),
                ft.Text("Lowest Temperature: {}℃".format(three_days[1]['lowest_temperature'])),
                ft.Text("Average Temperature: {}℃".format(three_days[1]['average_temperature']))
                ]),
                width=350,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_400,
                opacity=0.9,
                padding=20,
                border_radius=10)
            container_row=ft.Row(controls=[
                column1,
                column2,
                column3
                ], alignment=ft.alignment.center, spacing=50)
            
            centered_container = ft.Container(
                content=container_row,
                alignment=ft.alignment.center,
                expand=True)

            return ft.Column(controls=
                             [ft.Text("Weather in %s: "%(city.value,), size=30),
                              centered_container,
                              ft.Button("Back", on_click=lambda e: page.go("/fetchweather")),
                              ft.IconButton(icon=ft.Icons.HOUSE_OUTLINED, on_click= lambda e:page.go("/"))],
                              alignment=ft.MainAxisAlignment.CENTER,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                              expand=True)

    
    def manage_saved_weather():
        global searching_city
        searching_city=ft.TextField(label="Enter a valid city name from the database to perform an action")
        row1=ft.Row(controls=[
            ft.Button("Delete city's saved history"),
            searching_city,
            ft.Button("View city's saved history")],
            alignment=ft.MainAxisAlignment.CENTER
            )
        return ft.Column(controls=[
            ft.Text("View and manage your previously saved weather info here.", size=25),
            ft.Text("Backed by MySQL™. Simple. Secure. Safe.", size=15),
            ft.Container(ft.Text("")),
            row1,
            ft.Button("Delete all saved data..."),
            ft.Button("Back", on_click=lambda e: page.go("/"))],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
            )
        
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
                bgcolor=ft.Colors.BLUE_GREY_600,
                opacity=0.8,
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
        elif page.route == "/managedata":
            page.add(manage_saved_weather())
        elif page.route == "/about":
            page.add(about_this_app())


    page.on_route_change = navig
    page.go(page.route or "/")

'''ios themes'''
'''
loading_indicator = ft.CupertinoActivityIndicator(radius=20, color=ft.Colors.BLUE)
    # Add the loading indicator to the page
    page.add(loading_indicator)
    # Simulate a loading process
    page.sleep(2)  # Simulate a delay (e.g., fetching data)
    
    # Optionally, you can hide the loading indicator after the process
    loading_indicator.visible = False
'''
    


ft.app(target=main)