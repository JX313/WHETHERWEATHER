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
def get_connection():
    """Establishes and returns a MySQL database connection."""
    try:
        conn = mysql.connect(host="localhost", user="root", password="1234", database="whetherweather")
        return conn
    except mysql.Error as er:
        print("Connection failed:", er)
        # Log the error to runtime_logs.txt
        with open('runtime_logs.txt', 'a') as f_log:
            f_log.write(f"Connection failed: {er}\n")
            f_log.flush()
        return None

# Synchronous database functions to be run in a separate thread
def _save_to_table_sync(city_name_lower, data):
    """Synchronously saves weather data to a city-specific table."""
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS `{city_name_lower}`(
            searched_location VARCHAR(30),
            fetched_location VARCHAR(30),
            latitude DECIMAL(4,2),
            longitude DECIMAL(9,6),
            temperature_in_celsius INT,
            temperature_in_fahrenheit INT,
            description VARCHAR(30)
            );
            """)

            cur.execute(f"INSERT INTO `{city_name_lower}` VALUES (%s, %s, %s, %s, %s, %s, %s)", (city_name_lower, *data))
            conn.commit()
            message = "Saved successfully!"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message + "\n")
                f_log.flush()
            return True, message # Return success status and message
        except mysql.Error as err:
            message = "Save failed! Error: " + str(err)
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message + "\n")
                f_log.flush()
            return False, message # Return failure status and message
        finally:
            if conn and conn.is_connected(): # Check if conn is not None before calling is_connected()
                cur.close()
                conn.close()
    return False, "Database connection failed." # Return failure if connection fails

def _show_history_sync(table_name):
    """Synchronously fetches weather history for a given city."""
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT * FROM `{}`".format(table_name))
            records = cur.fetchall()
            message = "Accessed successfully!"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message + "\n")
                f_log.flush()
            return True, records, message
        except mysql.Error as err:
            message = "Access failed! Error: " + str(err)
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message + str(err) + "\n")
                f_log.flush()
            return False, [], message
        finally:
            if conn and conn.is_connected():
                cur.close()
                conn.close()
    return False, [], "Database connection failed."

def _remove_table_sync(table_name):
    """Synchronously removes a city's weather history table."""
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute(f"DROP TABLE `{table_name}`;")
            conn.commit()
            message = "Removed successfully!"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message + "\n")
                f_log.flush()
            return True, message
        except mysql.Error as err:
            message = "Couldn't remove data, try again later. Error: " + str(err)
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message + "\n")
                f_log.flush()
            return False, message
        finally:
            if conn and conn.is_connected():
                cur.close()
                conn.close()
    return False, "Database connection failed."

def _delete_all_data_sync():
    """Synchronously deletes all weather history tables."""
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute('SHOW TABLES;')
            tables = cur.fetchall()
            for (table,) in tables:
                cur.execute(f"DROP TABLE `{table}`;")
            conn.commit()
            message = "History cleared!"
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message + "\n")
                f_log.flush()
            return True, message
        except mysql.Error as err:
            message = "Couldn't clear history, try again later. Error: " + str(err)
            with open('runtime_logs.txt', 'a') as f_log:
                f_log.write(message + "\n")
                f_log.flush()
            return False, message
        finally:
            if conn and conn.is_connected():
                cur.close()
                conn.close()
    return False, "Database connection failed."


'''python-weather-conversion'''
def c_to_f(celsius):
    """Converts Celsius to Fahrenheit."""
    fahr=(celsius*1.8)+32
    return fahr

'''python-weather'''
async def get_weather_api_result(place: str) -> None:
  """Fetches weather forecast from python_weather API."""
  # Declare the client. The measuring unit used defaults to the metric system (celcius, km/h, etc.)
  async with python_weather.Client(unit=python_weather.METRIC) as client:
    
    # Fetch a weather forecast from a city.
    weather = await client.get(place)
    
    # return the weather API result
    return weather

def extract_global_args(weather: python_weather.forecast.Forecast) -> dict:
    """Extracts common information from the weather forecast output."""
    globalarg={
        'coords':weather.coordinates, # coordinates of forecast location
        'region':weather.region, # region of forecast
        'country': weather.country, # the country where the location is present
        'location':weather.location,# the location of forecast
        'date': weather.datetime.strftime("%Y-%m-%d") # date of query in YYYY-MM-DD format
        }
    return globalarg

def get_weather_today(weather: python_weather.forecast.Forecast) -> dict:
    """Extracts today's weather data."""
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
    """Extracts relevant parameters from a daily forecast."""
    daily_forecasts={
        'highest_temperature':forecast.highest_temperature,
        'lowest_temperature':forecast.lowest_temperature,
        'average_temperature':forecast.temperature
        }
    return daily_forecasts

def get_forecasts(weather: python_weather.forecast.Forecast) -> dict:
    """Extracts forecasts for the next two days."""
    forecasts = {daily.date.strftime("%Y-%m-%d"):extract_from_daily_forecast(daily) for daily in weather}
    forecasts = dict(list(forecasts.items())[1:]) # Exclude today's forecast
    return forecasts

## --------------------- MAIN FUNCTIONS ---------------------- ##

def process_weather(place: str) -> list:
    """Processes weather data for a given place."""
    output = asyncio.run(get_weather_api_result(place))
    global_args = extract_global_args(output)
    weather_today = get_weather_today(output)
    forecasts = get_forecasts(output)
    return [global_args, weather_today, forecasts]


if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

'''extracting new weather info to variables'''
def get_weather(city):
    """Fetches and stores weather information for a given city."""
    global globalargs, weathertoday, forecast, three_days, three_dates
    # Clear previous data to avoid accumulation on re-search
    three_dates.clear()
    three_days.clear()
    globalargs, weathertoday, forecast=process_weather(city.value)
    for key, value in forecast.items():
        three_dates.append(key)
        three_days.append(value)
        
'''defining different weather kinds'''
def kinda_weather():
    """Returns the URL for the weather icon based on the current weather kind."""
    image=""
    kind_of_weather=str(weathertoday['kind'])
    if kind_of_weather == 'Clear':
        image="https://i.postimg.cc/J0xKJRwL/clear.png"
    elif kind_of_weather == 'Sunny':
        image="https://i.postimg.cc/PfyMSfcG/sunny.png"
    elif kind_of_weather == 'Partly Cloudy':
        image="https://i.postimg.cc/6qWfBF81/partly-cloudy.png"
    elif kind_of_weather == 'Cloudy':
        image="https://i.postimg.cc/9FfYK55D/cloudy.png"
    elif kind_of_weather == 'Very Cloudy':
        image="https://i.postimg.cc/qq1XqQnB/very-cloudy.png"
    elif kind_of_weather == 'Fog':
        image="https://i.postimg.cc/63LhJBpv/fog.png"
    elif kind_of_weather == 'Light Showers':
        image="https://i.postimg.cc/PJT2PPRy/light-showers.png"
    elif kind_of_weather == 'Light Sleet Showers' or kind_of_weather == 'Light Sleet':
        image="https://i.postimg.cc/nhCTj80y/sleet-or-sleet-showers.png"
    elif kind_of_weather == 'Thundery Showers':
        image="https://i.postimg.cc/pVJs3Jm6/thundery-showers.png"
    elif kind_of_weather == 'Light Snow':
        image="https://i.postimg.cc/B6GCVj43/light-snow.png"
    elif kind_of_weather == 'Heavy Snow' or kind_of_weather == 'Heavy Snow Showers':
        image="https://i.postimg.cc/TPb90V8Q/snow.png"
    elif kind_of_weather == 'Light Rain':
        image="https://i.postimg.cc/bNYmPSbN/rain.png"
    elif kind_of_weather == 'Heavy Showers':
        image="https://i.postimg.cc/fTHBRWj7/heavy-showers.png"
    elif kind_of_weather == 'Heavy Rain':
        image="https://i.postimg.cc/YCZRQXPh/heavy-rain.png"
    elif kind_of_weather == 'Light Snow Showers':
        image="https://i.postimg.cc/B6GCVj43/light-snow.png"
    elif kind_of_weather == 'Thundery Heavy Rain':
        image="https://i.postimg.cc/pVJs3Jm6/thundery-showers.png"
    elif kind_of_weather == 'Thundery Snow Showers':
        image="https://i.postimg.cc/ydFL1FvW/thundery-rain.png"
    return image


#frontend kinda shi feelin lowkey
def main(page:ft.Page):
    #initializing the homepage
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.title=("WHETHERWEATHER!")

    # Define a loading indicator that can be shown/hidden
    loading_indicator = ft.ProgressBar(value=None, width=300, height=20, color=ft.Colors.BLUE, visible=False)
    page.add(loading_indicator) # Add it to the page once, then control its visibility

    # Define a SnackBar control to be used for messages
    # This is the old way if page.show_snack_bar is not available
    app_snackbar = ft.SnackBar(
        content=ft.Text(""), # Content will be set dynamically
        open=False,
        bgcolor=ft.Colors.BLUE_GREY_700 # Default background
    )
    page.overlay.append(app_snackbar) # Add it to the page's overlay

    # Helper function to show snackbar (for older Flet versions)
    def show_custom_snackbar(message, success):
        app_snackbar.content = ft.Text(message)
        app_snackbar.bgcolor = ft.Colors.GREEN_700 if success else ft.Colors.RED_700
        app_snackbar.open = True
        page.update()
        # Optionally, close after a delay
        # asyncio.create_task(close_snackbar_after_delay()) # If you want auto-close

    # async def close_snackbar_after_delay():
    #     await asyncio.sleep(3) # Adjust delay as needed
    #     app_snackbar.open = False
    #     page.update()


    def home_page():
        return ft.Column(controls=
                         [ft.Text("Welcome to WHETHERWEATHER!", size=30),
                          ft.Button(text="Search for weather in a city", on_click= lambda e: page.go("/fetchweather")),
                          ft.Button(text="View & manage saved weather", on_click= lambda e: page.go("/managedata")),
                          ft.Button(text="About this app...", on_click= lambda e: page.go("/about")),
                          ft.Button(text="Quit app", on_click=lambda e:page.window_close())],
                          alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          expand=True)

    def new_weather():
        global city
        city=ft.TextField(label="Enter the city name", width=500)
        return ft.Column(controls=
                         [ft.Text("Search for a city's weather", size=25),
                          ft.Text("(Enter the place name in title case. Specify the state)"),
                          city,
                          ft.Button("Search", on_click=lambda e: page.go("/fetchweather/weather")),
                          ft.Button("Back", on_click=lambda e: page.go("/"))],
                          alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          expand=True)

    # Async handler for saving data
    async def save_weather_data_handler(e, searched_loc, data):
        """Handles the saving of weather data asynchronously."""
        loading_indicator.visible = True
        page.update()

        success = False
        message = "An unknown error occurred."
        try:
            # page.run_thread returns a Future. If it fails to create the Future, it might return None.
            # We need to check for None before awaiting.
            future_result = page.run_thread(lambda: _save_to_table_sync(searched_loc.lower(), data))
            
            if future_result is None:
                success = False
                message = "Failed to schedule database save operation. Page context might be invalid or app is shutting down."
                print(f"Warning: page.run_thread returned None for save_weather_data_handler.")
            else:
                success, message = await future_result # Await the Future object
        except Exception as ex:
            success = False
            message = f"An unexpected error occurred during save: {ex}"
            print(f"Error in save_weather_data_handler: {ex}") # Log to console for debugging

        loading_indicator.visible = False
        page.update()

        # Use the custom snackbar function
        show_custom_snackbar(message, success)
        page.update()


    def fetched_new_weather():
        """Displays the fetched weather information and provides save option."""
        if city.value: # Check if city.value is not empty
            get_weather(city)
            weather_kind=kinda_weather()
            searched_loc, fetched_loc, temp_cels_today, desc_today=city.value, globalargs['region'], weathertoday['temperature'], weathertoday['description']
            temp_fahr_today= c_to_f(temp_cels_today)
            lat=float(globalargs['coords'][0])
            lon=float(globalargs['coords'][1])
            data=(fetched_loc, lat, lon, temp_cels_today, temp_fahr_today, desc_today)

            column1=ft.Container(ft.Column(controls=[
                ft.Text("Today's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
                ft.Text(f"Date: `{globalargs['date']}`"),
                ft.Text(f"Description: `{weathertoday['description']}`"),
                ft.Text(f"Temperature: `{weathertoday['temperature']}`℃"),
                ft.Image(src=weather_kind)
                ]),
                width=450,
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
                width=450,
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
                width=450,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.BLUE_GREY_400,
                opacity=0.9,
                padding=20,
                border_radius=10)
            container_row=ft.Row(controls=[
                column1,
                column2,
                column3
                ],
                alignment=ft.MainAxisAlignment.CENTER, # Changed to MainAxisAlignment for Row
                spacing=50)

            # Define the async handler directly within fetched_new_weather
            # This allows it to capture searched_loc and data from the outer scope
            async def on_save_button_click(e):
                await save_weather_data_handler(e, searched_loc, data)

            return ft.Column(controls=
                             [ft.Text("Weather in %s: "%(city.value,), size=30),
                              container_row,
                              # Assign the async function directly to on_click
                              ft.Button("Save today's weather...", on_click=on_save_button_click),
                              ft.Button("Back", on_click=lambda e: page.go("/fetchweather")),
                              ft.IconButton(icon=ft.Icons.HOUSE_OUTLINED, on_click= lambda e:page.go("/"))],
                              alignment=ft.MainAxisAlignment.CENTER,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                              expand=True)
        else:
            # Handle case where city is empty (e.g., show a message or redirect)
            return ft.Column(controls=[
                ft.Text("Please enter a city name to fetch weather.", size=20),
                ft.Button("Back to Search", on_click=lambda e: page.go("/fetchweather"))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)


    # Async handler for showing history
    async def show_history_handler(e):
        """Handles displaying weather history for a city asynchronously."""
        loading_indicator.visible = True
        page.update()

        city_name = searching_city.value
        if not city_name:
            loading_indicator.visible = False
            page.update()
            show_custom_snackbar("Please enter a city name to view history.", False)
            return

        success = False
        records = []
        message = "An unknown error occurred."
        try:
            future_result = page.run_thread(lambda: _show_history_sync(city_name.lower()))
            if future_result is None:
                success, records, message = False, [], "Failed to schedule database operation. Page context might be invalid."
                print(f"Warning: page.run_thread returned None for show_history_handler.")
            else:
                success, records, message = await future_result
        except Exception as ex:
            success, records, message = False, [], f"An unexpected error occurred during history fetch: {ex}"
            print(f"Error in show_history_handler: {ex}")

        loading_indicator.visible = False
        page.update()

        if success:
            history_controls = [ft.Text(f"History for {city_name}:", size=20)]
            if records:
                for record in records:
                    history_controls.append(ft.Text(f"Location: {record[1]}, Lat: {record[2]}, Lon: {record[3]}, Temp(C): {record[4]}, Temp(F): {record[5]}, Desc: {record[6]}"))
            else:
                history_controls.append(ft.Text("No history found for this city."))

            # Define a function to close the dialog
            def close_dialog(e):
                page.dialog.open = False
                page.update()

            page.dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Weather History"),
                content=ft.Column(history_controls, scroll=ft.ScrollMode.AUTO, height=300),
                actions=[ft.TextButton("Close", on_click=close_dialog)] # Use the defined function here
            )
            page.dialog.open = True
            page.update()
        else:
            show_custom_snackbar(message, False)
            page.update()

    # Async handler for removing table
    async def remove_table_handler(e):
        """Handles removing a city's weather history table asynchronously."""
        loading_indicator.visible = True
        page.update()

        city_name = searching_city.value
        if not city_name:
            loading_indicator.visible = False
            page.update()
            show_custom_snackbar("Please enter a city name to delete history.", False)
            return

        success = False
        message = "An unknown error occurred."
        try:
            future_result = page.run_thread(lambda: _remove_table_sync(city_name))
            if future_result is None:
                success = False
                message = "Failed to schedule database operation. Page context might be invalid."
                print(f"Warning: page.run_thread returned None for remove_table_handler.")
            else:
                success, message = await future_result
        except Exception as ex:
            success = False
            message = f"An unexpected error occurred during removal: {ex}"
            print(f"Error in remove_table_handler: {ex}")

        loading_indicator.visible = False
        page.update()

        show_custom_snackbar(message, success)
        page.update()

    # Async handler for deleting all data
    async def delete_all_data_handler(e):
        """Handles deleting all weather history tables asynchronously."""
        loading_indicator.visible = True
        page.update()

        success = False
        message = "An unknown error occurred."
        try:
            future_result = page.run_thread(_delete_all_data_sync)
            if future_result is None:
                success = False
                message = "Failed to schedule database operation. Page context might be invalid."
                print(f"Warning: page.run_thread returned None for delete_all_data_handler.")
            else:
                success, message = await future_result
        except Exception as ex:
            success = False
            message = f"An unexpected error occurred during clear all: {ex}"
            print(f"Error in delete_all_data_handler: {ex}")

        loading_indicator.visible = False
        page.update()

        show_custom_snackbar(message, success)
        page.update()


    def manage_saved_weather():
        """Manages the UI for viewing and managing saved weather data."""
        global searching_city
        searching_city=ft.TextField(label="Enter a valid city name from the database to perform an action")

        # Define async handlers for buttons in this scope
        async def on_delete_city_click(e):
            await remove_table_handler(e)

        async def on_view_history_click(e):
            await show_history_handler(e)

        async def on_delete_all_click(e):
            await delete_all_data_handler(e)

        row1=ft.Row(controls=[
            ft.Button("Delete city's saved history", on_click = on_delete_city_click),
            searching_city,
            ft.Button("View city's saved history", on_click = on_view_history_click)],
            alignment=ft.MainAxisAlignment.CENTER
            )
        return ft.Column(controls=[
            ft.Text("View and manage your previously saved weather info here.", size=25),
            ft.Text("Backed by MySQL™. Simple. Secure. Safe.", size=15),
            ft.Container(ft.Text("")),
            row1,
            ft.Button("Delete all saved data...", on_click=on_delete_all_click),
            ft.Button("Back", on_click=lambda e: page.go("/"))],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
            )
        
    def about_this_app():
        """Displays information about the application."""
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
                border_radius=10), ft.Button("Back", on_click= lambda e: page.go("/"))],
                alignment=ft.MainAxisAlignment.CENTER, # Added alignment for the column
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, # Added alignment for the column
                expand=True # Added expand for the column
                )
                
    def show_alert(e):
        """Displays an alert dialog for confirmation."""
        # Define a function to close the alert dialog
        def close_alert_dialog(e):
            page.dialog.open = False
            page.update()

        page.dialog=ft.AlertDialog(title="Alert!", content=ft.Text("Are you sure you want to go home?", size=20), 
                                   actions= # Changed controls to actions for AlertDialog buttons
                                   [ft.TextButton("Yes", on_click= lambda e: page.go("/")), 
                                    ft.TextButton("No", on_click= close_alert_dialog)]) # Use the defined function here
        page.dialog.open=True
        page.update() 

    def navig(e):
        """Handles page navigation based on the route."""
        page.controls.clear()
        # Always add the loading indicator and snackbar to the page's overlay
        # This ensures they are always available regardless of the current route's controls
        page.add(loading_indicator)
        # Ensure app_snackbar is added to overlay only once, or handle its presence
        if app_snackbar not in page.overlay:
            page.overlay.append(app_snackbar) 
        
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
        page.update() # Update the page after adding controls


    page.on_route_change = navig
    page.go(page.route or "/")

if __name__ == "__main__":
    ft.app(target=main)
