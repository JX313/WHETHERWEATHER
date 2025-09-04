import flet as ft
import mysql.connector as mysql
import python_weather
from datetime import datetime
import asyncio
import os

'''globals'''
globalargs, weathertoday, forecast=None, None, None
three_dates=[]
three_days=[]

## --------------------- BACKEND FUNCTIONS ---------------------- ##
'''mysql'''
def get_connection():
    try:
        conn = mysql.connect(host="localhost", user="root", password="1234", database="whetherweather")
        return conn
    except mysql.Error as er:
        print("Connection failed:", er)
        return None


def save_to_table(city, data):
    city_name=city.lower()
    conn=get_connection()
    if conn:
        cur=conn.cursor()
        section = 'create'
        try:
            cur.execute(f"""
            create table if not exists {city_name}(
            search_date date,
            search_time time,
            searched_location varchar(30),
            fetched_location varchar(30),
            latitude decimal(4,2),
            longitude decimal(4,2),
            temp_in_celsius int,
            temp_in_fahrenheit int,
            description varchar(30)
            );
            """)
### ADD LOADING INDICATOR FOR SEARCH
            section = 'insert'
            cur.execute("insert into %s values ('%s', '%s', '%s', '%s', %f, %f, %d, %d, '%s');"%(city_name, *data))
            conn.commit()
            message="Saved successfully!"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message)
                f_log.write("\n")
                f_log.flush()
        except mysql.Error as err:
            message=f"Save failed at {section} stage!"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message)
                f_log.write(str(err))
                f_log.write("\n")
                f_log.flush()
            
def show_history(searching_city):
    city_name=searching_city.value
    table_name=city_name.lower()
    conn=get_connection()
    if conn:
        cur=conn.cursor()
        try:
            cur.execute("select * from `{}`".format(table_name))
            message="Accessed successfully!"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message)
                f_log.write("\n")
                f_log.flush()
        except mysql.Error as err:
            message="Access failed!"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message)
                f_log.write(str(err))
                f_log.write("\n")
                f_log.flush()


def display_tables():
    conn=get_connection()
    control=[]
    if conn:
        cur=conn.cursor()
        cur.execute('show tables;')
        retrieved_tables=cur.fetchall()
        for record in retrieved_tables:
            city_name=record[0]
            control.append(ft.Text(city_name))
        return control


def remove_table(searching_city):
    conn=get_connection()
    if conn:
        cur=conn.cursor()
        try:
            cur.execute(f"drop table `{searching_city.value}`;")
            conn.commit()
            message="Removed successfully!"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message)
                f_log.write("\n")
                f_log.flush()
        except mysql.Error as err:
            message="Couldn't remove data, try again later"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message)
                f_log.write(str(err))
                f_log.write("\n")
                f_log.flush()


def delete_all_data():
    conn=get_connection()
    cur=conn.cursor()
    if conn:
        cur=conn.cursor()
        try:
            cur.execute('show tables;')
            tables=cur.fetchall()
            for (table,) in tables:
                cur.execute(f"drop table `{table}`;")
            conn.commit()
            message="History cleared!"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message)
                f_log.write("\n")
                f_log.flush()
        except mysql.Error as err:
            message="Couldn't clear history, try again later"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message)
                f_log.write(str(err))
                f_log.write("\n")
                f_log.flush()


'''python-weather-conversion'''
def c_to_f(celsius):
    fahr=(celsius*1.8)+32
    return fahr

'''python-weather'''
async def get_weather_api_result(place: str) -> None:
  
  # Declare the client. The measuring unit used defaults to the metric system (celcius, km/h, etc.)
    try:
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            # Fetch a weather forecast from a city.
            weather = await client.get(place)
            # return the weather API result
            return weather
    except Exception as e:
        return {'error': str(e)}

def extract_global_args(weather: python_weather.forecast.Forecast) -> dict:
    # extracts common info from the forecast output
    globalarg={
        'coords':weather.coordinates, # coordinates of forecast location
        'region':weather.region, # region of forecast
        'country': weather.country, # the country where the location is present
        'location':weather.location,# the location of forecast
        'date': weather.datetime.strftime("%Y-%m-%d"), # date of query in YYYY-DD-MM format
        'time': weather.datetime.strftime("%H:%M:%S") # time of query in HH:MM:SS format
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
    if isinstance(output, dict) and 'error' in output:
        return [{'error': output['error']}, None, None]
    global_args = extract_global_args(output)
    weather_today = get_weather_today(output)
    forecasts = get_forecasts(output)
    return [global_args, weather_today, forecasts]


if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

'''extracting new weather info to variables'''
def get_weather(city):
    global globalargs, weathertoday, forecast, three_days, three_dates
    # Clear previous data to avoid repeated appends and index errors
    three_dates.clear()
    three_days.clear()
    globalargs, weathertoday, forecast = process_weather(city.value)
    for key, value in forecast.items():
        three_dates.append(key)
        three_days.append(value)
        
'''defining different weather kinds'''
def kinda_weather():
    image=""
    kind_of_weather=str(weathertoday['kind'])
    if kind_of_weather == 'Clear':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/ER5ywBR_1TVEhT48KmYe1zwB6TOaTvqR6G2pE0uYOKpw0g?e=YJMXdm"
        image="https://i.postimg.cc/J0xKJRwL/clear.png"
    elif kind_of_weather == 'Sunny':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/Ec5mzmSquHxJvJDS55Y-IPMBgtoX7vwaYkylVIqfDaGQpA?e=H6HvZz"
        image="https://i.postimg.cc/PfyMSfcG/sunny.png"
    elif kind_of_weather == 'Partly Cloudy':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/ER2tYpoZRvZPlfJ6r6yJMAwBlmQ7tFg-u6F_49nZUjckvw?e=TZVmHh"
        image="https://i.postimg.cc/6qWfBF81/partly-cloudy.png"
    elif kind_of_weather == 'Cloudy':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/Eb9IyoAPy0FOpQ_gIQUkZ7IBj085d6BQS85nWfrtXKN0ew?e=eZeNKf"
        image="https://i.postimg.cc/9FfYK55D/cloudy.png"
    elif kind_of_weather == 'Very Cloudy':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/EX9L0wDrrHFJsLjoAIcJ-l4BXGAg3TpXdc5ALP_8HGdQwQ?e=kwgcbG"
        image="https://i.postimg.cc/qq1XqQnB/very-cloudy.png"
    elif kind_of_weather == 'Fog':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/EV_Q1ytxHdNNqJVyW0i32KwB1VEbVBJqDRU0Jz5yzW9Ilw?e=bLBPiG"
        image="https://i.postimg.cc/63LhJBpv/fog.png"
    elif kind_of_weather == 'Light Showers':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/EZbusNr9mQpCgonqZEkcpNABueEPnY8t5hkAgMI89sNg9A?e=39Aijz"
        image="https://i.postimg.cc/PJT2PPRy/light-showers.png"
    elif kind_of_weather == 'Light Sleet Showers':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/ERGBP9m9imNMioUo-2h6fbIBKfBTStJjS3zLSPtooAb6hw?e=661FZa"
        image="https://i.postimg.cc/nhCTj80y/sleet-or-sleet-showers.png"
    elif kind_of_weather == 'Light Sleet':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/ERGBP9m9imNMioUo-2h6fbIBKfBTStJjS3zLSPtooAb6hw?e=661FZa"
        image="https://i.postimg.cc/nhCTj80y/sleet-or-sleet-showers.png"
    elif kind_of_weather == 'Thundery Showers':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/Ee3Ge5-hTuVNlVR0QwDAQ7wBBEV4joxmiSrvJpRahZkUJA?e=AOW9d4"
        image="https://i.postimg.cc/pVJs3Jm6/thundery-showers.png"
    elif kind_of_weather == 'Light Snow':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/ESuq7-9SfAFLrHFu1AwpDRIBS4bdKd53PPABG-jrdKY_bg?e=O4KnsY"
        image="https://i.postimg.cc/B6GCVj43/light-snow.png"
    elif kind_of_weather == 'Heavy Snow':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/EfevGoyDwLRBpasL9wWMzAsBu8yVTD9etWNFShjSGQkTYw?e=6b61zg"
        image="https://i.postimg.cc/TPb90V8Q/snow.png"
    elif kind_of_weather == 'Light Rain':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/EZbusNr9mQpCgonqZEkcpNABueEPnY8t5hkAgMI89sNg9A?e=39Aijz"
        image="https://i.postimg.cc/bNYmPSbN/rain.png"
    elif kind_of_weather == 'Heavy Showers':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/EUWJI7VsRRpNgJRJUaCEnjEB-tAlGzlFTF5ZSCb7oUw28Q?e=8FojPe"
        image="https://i.postimg.cc/fTHBRWj7/heavy-showers.png"
    elif kind_of_weather == 'Heavy Rain':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/ESmPbIOXBudPm80pziSICOYBsCua_Xl__VOtVhFb91v10w?e=b7MvMb"
        image="https://i.postimg.cc/YCZRQXPh/heavy-rain.png"
    elif kind_of_weather == 'Light Snow Showers':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/ESuq7-9SfAFLrHFu1AwpDRIBS4bdKd53PPABG-jrdKY_bg?e=O4KnsY"
        image="https://i.postimg.cc/B6GCVj43/light-snow.png"
    elif kind_of_weather == 'Heavy Snow Showers':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/EfevGoyDwLRBpasL9wWMzAsBu8yVTD9etWNFShjSGQkTYw?e=6b61zg"
        image="https://i.postimg.cc/B6GCVj43/light-snow.png"
    elif kind_of_weather == 'Thundery Heavy Rain':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/Ee3Ge5-hTuVNlVR0QwDAQ7wBBEV4joxmiSrvJpRahZkUJA?e=krSoQF"
        image="https://i.postimg.cc/pVJs3Jm6/thundery-showers.png"
    elif kind_of_weather == 'Thundery Snow Showers':
        #image="https://1drv.ms/i/c/2b4cf875021e3a16/EWnjnRfW8ppNoEpVe-mMBz0BQErnf5xHZmSTcoqh3V_-dg?e=1s5JfX"
        image="https://i.postimg.cc/ydFL1FvW/thundery-rain.png"
    return image


#reference links: 
#https://www.blackbox.ai/chat/tMR0XWR
#https://www.blackbox.ai/chat/nCcGI1G
#https://flet.dev/docs/getting-started/flet-controls/
#https://www.geeksforgeeks.org/python/building-flutter-apps-in-python/
#https://www.blackbox.ai/chat/hNsi41I
#image gallery- https://postimg.cc/gallery/G4Skdzg

'''icons
https://icons8.com/icons/set/weather-gradient--style-cute-clipart
https://icons8.com/icons/set/weather--style-color-glass
'''

#frontend kinda shi feelin lowkey
def main(page:ft.Page):
    def show_alert(e=None):
        def on_yes(ev):
            page.dialog.open = False
            page.update()
            page.go("/")

        def on_no(ev):
            page.dialog.open = False
            page.update()

        alert_dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, size=32),
                ft.Text("Alert!", size=22, weight=ft.FontWeight.BOLD),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            content=ft.Text("Are you sure you want to go home?", size=20),
            actions=[
                ft.TextButton("Yes", on_click=on_yes),
                ft.TextButton("No", on_click=on_no),
            ],
        )
        # Add dialog to overlay if not already present
        if alert_dialog not in page.overlay:
            page.overlay.append(alert_dialog)
        page.dialog = alert_dialog
        page.dialog.open = True
        page.update()
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
                          ft.Button(text="Quit app", on_click=lambda e:page.window.close())],
                          alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          expand=True)
    def new_weather():
        global city
        city = ft.TextField(label="Enter the city name", width=500)
        def on_search(e):
            page.controls.clear()
            page.add(loading_page(text="Fetching weather..."))
            page.update()
            async def do_search():
                await asyncio.sleep(2)
                page.go("/fetchweather/weather")
            page.run_task(do_search)
        return ft.Column(controls=[
            ft.Text("Search for a city's weather", size=25),
            ft.Text("(Enter the place name in title case. Specify the state)"),
            city,
            ft.Button("Search", on_click=on_search),
            ft.Button("Back", on_click=lambda e: page.go("/"))
        ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True)
    def fetched_new_weather():
        if city != '':
            get_weather(city)
            if isinstance(globalargs, dict) and 'error' in globalargs:
                return ft.Column(controls=[
                    ft.Text("Error fetching weather data:", size=22, color=ft.Colors.RED),
                    ft.Text(globalargs['error'], color=ft.Colors.RED),
                    ft.Button("Back", on_click=lambda e: page.go("/fetchweather"))
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
            weather_kind = kinda_weather()
            time_now = datetime.now()
            searched_loc, fetched_loc, temp_cels_today, desc_today = city.value, globalargs['region'], weathertoday['temperature'], weathertoday['description']
            temp_fahr_today = c_to_f(temp_cels_today)
            lat = float(globalargs['coords'][0])
            lon = float(globalargs['coords'][1])
            data = (globalargs['date'], time_now.strftime("%H:%M:%S"), searched_loc, fetched_loc, lat, lon, temp_cels_today, temp_fahr_today, desc_today)
            container_width = 350
            container_height = 220
            column1 = ft.Container(
                ft.Column(
                    controls=[
                        ft.Text("Today's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
                        ft.Text(f"Date: `{globalargs['date']}`", text_align=ft.TextAlign.CENTER),
                        ft.Text(f"Description: `{weathertoday['description']}`", text_align=ft.TextAlign.CENTER),
                        ft.Text(f"Temperature: `{weathertoday['temperature']}`℃", text_align=ft.TextAlign.CENTER)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=container_width,
                height=container_height,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_400,
                opacity=0.9,
                padding=20,
                border_radius=10
            )
            column2 = ft.Container(
                ft.Column(
                    controls=[
                        ft.Text("Tomorrow's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
                        ft.Text("Date: {}".format(three_dates[0]), text_align=ft.TextAlign.CENTER),
                        ft.Text("Highest Temperature: {}℃".format(three_days[0]['highest_temperature']), text_align=ft.TextAlign.CENTER),
                        ft.Text("Lowest Temperature: {}℃".format(three_days[0]['lowest_temperature']), text_align=ft.TextAlign.CENTER),
                        ft.Text("Average Temperature: {}℃".format(three_days[0]['average_temperature']), text_align=ft.TextAlign.CENTER)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=container_width,
                height=container_height,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_400,
                opacity=0.9,
                padding=20,
                border_radius=10
            )
            column3 = ft.Container(
                ft.Column(
                    controls=[
                        ft.Text("The day after tomorrow's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
                        ft.Text("Date: {}".format(three_dates[1]), text_align=ft.TextAlign.CENTER),
                        ft.Text("Highest Temperature: {}℃".format(three_days[1]['highest_temperature']), text_align=ft.TextAlign.CENTER),
                        ft.Text("Lowest Temperature: {}℃".format(three_days[1]['lowest_temperature']), text_align=ft.TextAlign.CENTER),
                        ft.Text("Average Temperature: {}℃".format(three_days[1]['average_temperature']), text_align=ft.TextAlign.CENTER)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=container_width,
                height=container_height,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_400,
                opacity=0.9,
                padding=20,
                border_radius=10
            )
            container_row = ft.Row(
                controls=[column1, column2, column3],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=50
            )

            return ft.Column(
                controls=[
                    ft.Row(
                        controls=[ft.Column(controls=[
                            ft.Text("Weather in %s today: " % (city.value,), size=30, text_align=ft.TextAlign.CENTER),
                            ft.Text("Coordinates: ({}, {})".format(globalargs['coords'][0], globalargs['coords'][1]), size=20, text_align=ft.TextAlign.CENTER)
                        ]),
                            ft.Image(src=weather_kind)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    container_row,
                    ft.Container(
                        ft.Button("Save today's weather...", on_click=lambda e: show_loading_and_save(searched_loc, data)),
                        alignment=ft.alignment.center
                    ),
                    ft.Container(
                        ft.Button("Back", on_click=lambda e: page.go("/fetchweather")),
                        alignment=ft.alignment.center
                    ),
                    ft.Container(
                        ft.IconButton(icon=ft.Icons.HOUSE_OUTLINED, on_click=show_alert),
                        alignment=ft.alignment.center
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )

    # Loading bar page
    def loading_page(text="Saving today's weather..."):
        return ft.Column(controls=[
            ft.Text(text, size=25, text_align=ft.TextAlign.CENTER),
            ft.ProgressBar(width=400, color=ft.Colors.BLUE, bgcolor=ft.Colors.BLUE_GREY_100),
        ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True)

    # Show loading, then save, then show weather page
    def show_loading_and_save(searched_loc, data):
        async def do_save():
            page.controls.clear()
            page.add(loading_page())
            page.update()
            await asyncio.sleep(3)
            save_to_table(searched_loc, data)
            page.controls.clear()
            page.add(saved_successfully_page())
            page.update()
        page.run_task(do_save)

    def saved_successfully_page():
        return ft.Column(controls=[
            ft.Text("Saved successfully!", size=28, color=ft.Colors.GREEN, text_align=ft.TextAlign.CENTER),
            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, color=ft.Colors.GREEN, size=60),
            ft.Button("View Weather", on_click=lambda e: page.go("/fetchweather/weather/result")),
            ft.Button("Back to Home", on_click=lambda e: page.go("/"))
        ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True)

    # Show the weather result page after saving
    def fetched_weather_result():
        # Just show the same as fetched_new_weather but without the save button
        if city != '':
            weather_kind = kinda_weather()
            container_width = 350
            container_height = 220
            column1 = ft.Container(
                ft.Column(
                    controls=[
                        ft.Text("Today's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
                        ft.Text(f"Date: `{globalargs['date']}`", text_align=ft.TextAlign.CENTER),
                        ft.Text(f"Description: `{weathertoday['description']}`", text_align=ft.TextAlign.CENTER),
                        ft.Text(f"Temperature: `{weathertoday['temperature']}`℃", text_align=ft.TextAlign.CENTER)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=container_width,
                height=container_height,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_400,
                opacity=0.9,
                padding=20,
                border_radius=10
            )
            column2 = ft.Container(
                ft.Column(
                    controls=[
                        ft.Text("Tomorrow's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
                        ft.Text("Date: {}".format(three_dates[0]), text_align=ft.TextAlign.CENTER),
                        ft.Text("Highest Temperature: {}℃".format(three_days[0]['highest_temperature']), text_align=ft.TextAlign.CENTER),
                        ft.Text("Lowest Temperature: {}℃".format(three_days[0]['lowest_temperature']), text_align=ft.TextAlign.CENTER),
                        ft.Text("Average Temperature: {}℃".format(three_days[0]['average_temperature']), text_align=ft.TextAlign.CENTER)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=container_width,
                height=container_height,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_400,
                opacity=0.9,
                padding=20,
                border_radius=10
            )
            column3 = ft.Container(
                ft.Column(
                    controls=[
                        ft.Text("The day after tomorrow's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
                        ft.Text("Date: {}".format(three_dates[1]), text_align=ft.TextAlign.CENTER),
                        ft.Text("Highest Temperature: {}℃".format(three_days[1]['highest_temperature']), text_align=ft.TextAlign.CENTER),
                        ft.Text("Lowest Temperature: {}℃".format(three_days[1]['lowest_temperature']), text_align=ft.TextAlign.CENTER),
                        ft.Text("Average Temperature: {}℃".format(three_days[1]['average_temperature']), text_align=ft.TextAlign.CENTER)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=container_width,
                height=container_height,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_400,
                opacity=0.9,
                padding=20,
                border_radius=10
            )
            container_row = ft.Row(
                controls=[column1, column2, column3],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=50
            )
            return ft.Column(
                controls=[
                    ft.Row(
                        controls=[ft.Column(controls=[
                            ft.Text("Weather in %s today: " % (city.value,), size=30, text_align=ft.TextAlign.CENTER),
                            ft.Text("Coordinates: ({}, {})".format(globalargs['coords'][0], globalargs['coords'][1]), size=20, text_align=ft.TextAlign.CENTER)
                        ]),
                            ft.Image(src=weather_kind)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    container_row,
                    ft.Container(
                        ft.Button("Back", on_click=lambda e: page.go("/fetchweather")),
                        alignment=ft.alignment.center
                    ),
                    ft.Container(
                        ft.IconButton(icon=ft.Icons.HOUSE_OUTLINED, on_click=show_alert),
                        alignment=ft.alignment.center
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )

    

    def manage_saved_weather():
        global searching_city
        searching_city = ft.TextField(label="Enter a valid city name from the database to perform an action")
        # Get list of tables (cities)
        tables_controls = display_tables() or []
        if not tables_controls:
            tables_list = ft.Column(controls=[
                ft.Text("Saved cities in database:", size=18),
                ft.Text("No tables currently. Search up the weather in a city to get started!", color=ft.Colors.YELLOW, size=16)
            ], alignment=ft.MainAxisAlignment.START)
        else:
            tables_list = ft.Column(controls=[ft.Text("Saved cities in database:", size=18)] + tables_controls, alignment=ft.MainAxisAlignment.START)
        def on_delete_city_history(e):
            remove_table(searching_city)
            page.go("/managedata")

        def on_delete_all_data(e):
            delete_all_data()
            page.go("/managedata")

        row1 = ft.Row(
            controls=[
                ft.Button("Delete city's saved history", on_click=on_delete_city_history),
                searching_city,
                ft.Button("View city's saved history", on_click=lambda e: page.go(f"/managedata/{searching_city.value}"))
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        return ft.Column(controls=[
            ft.Text("View and manage your previously saved weather info here.", size=25),
            ft.Text("Backed by MySQL™. Simple. Secure. Safe.", size=15),
            ft.Container(
                content = tables_list,
                width=450,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_600,
                opacity=0.8,
                padding=20,
                border_radius=10
            ),
            row1,
            ft.Button("Delete all saved data...", on_click=on_delete_all_data),
            ft.Button("Back", on_click=lambda e: page.go("/"))
        ], alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True)

    def show_city_history_page(city_name):
        # Fetch data from the table and render it
        conn = get_connection()
        controls = []
        if conn:
            cur = conn.cursor()
            try:
                cur.execute(f"SELECT * FROM `{city_name}`;")
                rows = cur.fetchall() or []
                columns = [desc[0] for desc in (cur.description or [])]
                controls.append(ft.Text(f"History for city: {city_name}", size=25))
                if columns and rows:
                    # Build DataTable columns
                    dt_columns = [ft.DataColumn(ft.Text(col)) for col in columns]
                    # Build DataTable rows
                    dt_rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row]) for row in rows]
                    controls.append(ft.DataTable(columns=dt_columns, rows=dt_rows))
                elif columns and not rows:
                    controls.append(ft.Text("No data found for this city.", color=ft.Colors.YELLOW))
            except mysql.Error as err:
                controls.append(ft.Text(f"Error fetching data: {err}", color=ft.Colors.RED))
        else:
            controls.append(ft.Text("Database connection failed.", color=ft.Colors.RED))
        controls.append(ft.Button("Back", on_click=lambda e: page.go("/managedata")))
        return ft.Column(controls=controls, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        
    def about_this_app():
        about_text = (
            "    This Python-based application, by the name of 'WHETHERWEATHER!',\n"
            "    serves the purpose of retrieving weather data of a place and for storing\n"
            "    and reading the weather history at that place whenever you opt to store it.\n"
            "    This application runs on the python-weather module, a free and asynchronous weather\n"
            "    Python API wrapper, and utilizes the flet module, a Flutter-substituent\n"
            "    module for Python, available to Python, to make it user-friendly.\n\n"
            "    Copyright © WHETHERWEATHER! 2025; No rights reserved.\n\n"
            "    This software is not provided AS IS, IF NOT, WORKING PROPERLY blah blah blah and totally\n"
            "    meets your expectations.\n"
            "    Make sure to give this program's repo on GitHub a star so that this becomes popular. :)"
        )
        return ft.Container(
            content=ft.Column([
                ft.Text(about_text,
                        size=20,
                        text_align=ft.TextAlign.LEFT,
                        color=ft.Colors.BLACK87,
                        selectable=True),
                ft.Button("Back", on_click=lambda e: page.go("/"))
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.BLUE_GREY_600,
            opacity=0.8,
            padding=30,
            border_radius=10,
            expand=True,
            width=None,
            height=None
        )
                
    def navig(e):
        page.controls.clear()
        if page.route == "/":
            page.add(home_page())
        elif page.route == "/fetchweather":
            page.add(new_weather())
        elif page.route == "/fetchweather/weather":
            page.add(fetched_new_weather())
        elif page.route == "/fetchweather/weather/result":
            page.add(fetched_weather_result())
        elif page.route.startswith("/managedata/"):
            city_name = page.route.split("/managedata/")[1]
            page.add(show_city_history_page(city_name))
        elif page.route == "/managedata":
            page.add(manage_saved_weather())
        elif page.route == "/about":
            page.add(about_this_app())


    page.on_route_change = navig
    page.go(page.route or "/")

if __name__ == "__main__":
    ft.app(target=main)
