import flet as ft
import asyncio
from state import state
from datetime import datetime
from weather_service import c_to_f, get_weather
from window_settings import show_alert
from assets import kinda_weather
from history_storage import save_history

async def fetched_new_weather(page:ft.Page): 
        if state.city.value != '': 
            await get_weather(state.city) 
            if isinstance(state.globalargs, dict) and 'error' in state.globalargs: 
                return ft.Column(controls=[ 
                    ft.Text("Error fetching weather data:", size=22, color=ft.Colors.RED), 
                    ft.Text(state.globalargs['error'], color=ft.Colors.RED), 
                    ft.Button("Back", on_click=lambda e: page.go("/fetchweather")) 
                ], 
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True) 
            weather_kind = kinda_weather() 
            time_now = datetime.now() 
            searched_loc, fetched_loc, temp_cels_today, desc_today = state.city.value, state.globalargs['region'], state.weathertoday['temperature'], state.weathertoday['description'] 
            temp_fahr_today = c_to_f(temp_cels_today) 
            lat = float(state.globalargs['coords'][0]) 
            lon = float(state.globalargs['coords'][1]) 
            data_set = (state.globalargs['date'], time_now.strftime("%H:%M:%S"), searched_loc, fetched_loc, temp_cels_today, temp_fahr_today, desc_today) 
            container_width = 350 
            container_height = 220 
            column1 = ft.Container( 
                ft.Column( 
                    controls=[ 
                        ft.Text("Today's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE), 
                        ft.Text(f"Date: `{state.globalargs['date']}`", text_align=ft.TextAlign.CENTER), 
                        ft.Text(f"Description: `{state.weathertoday['description']}`", text_align=ft.TextAlign.CENTER), 
                        ft.Text(f"Temperature: `{state.weathertoday['temperature']}`℃", text_align=ft.TextAlign.CENTER) 
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                ), 
                width=container_width, 
                height=container_height, 
                alignment=ft.Alignment(0, 0), 
                bgcolor=ft.Colors.BLUE_GREY_400, 
                opacity=0.9, 
                padding=20, 
                border_radius=10 
            ) 
    
            column2 = ft.Container( 
                ft.Column( 
                    controls=[ 
                        ft.Text("Tomorrow's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE), 
                        ft.Text("Date: {}".format(state.three_dates[0]), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Highest Temperature: {}℃".format(state.three_days[0]['highest_temperature']), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Lowest Temperature: {}℃".format(state.three_days[0]['lowest_temperature']), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Average Temperature: {}℃".format(state.three_days[0]['average_temperature']), text_align=ft.TextAlign.CENTER) 
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ), 
                width=container_width, 
                height=container_height, 
                alignment=ft.Alignment(0, 0), 
                bgcolor=ft.Colors.BLUE_GREY_400, 
                opacity=0.9, 
                padding=20, 
                border_radius=10 
            ) 
    
            column3 = ft.Container( 
                ft.Column( 
                    controls=[ 
                        ft.Text("The day after tomorrow's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE), 
                        ft.Text("Date: {}".format(state.three_dates[1]), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Highest Temperature: {}℃".format(state.three_days[1]['highest_temperature']), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Lowest Temperature: {}℃".format(state.three_days[1]['lowest_temperature']), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Average Temperature: {}℃".format(state.three_days[1]['average_temperature']), text_align=ft.TextAlign.CENTER) 
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                ), 
                width=container_width, 
                height=container_height, 
                alignment=ft.Alignment(0, 0), 
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
                            ft.Text("Weather in %s today: " % (state.city.value,), size=30, text_align=ft.TextAlign.CENTER), 
                            ft.Text("Coordinates: ({}, {})".format(state.globalargs['coords'][0], state.globalargs['coords'][1]), size=20, text_align=ft.TextAlign.CENTER)
                        ]), 
                            ft.Image(src=weather_kind) 
                        ], 
                        alignment=ft.MainAxisAlignment.CENTER, 
                        vertical_alignment=ft.CrossAxisAlignment.CENTER 
                    ), 
                    container_row, 
                    ft.Container( 
                        ft.Button("Save today's weather...", on_click=lambda e: show_loading_and_save(data_set, page)), 
                        alignment=ft.Alignment(0, 0) 
                    ), 
                    ft.Container( 
                        ft.Button("Back", on_click=lambda e: page.go("/fetchweather")), 
                        alignment=ft.Alignment(0, 0) 
                    ), 
                    ft.Container( 
                        ft.IconButton(icon=ft.Icons.HOUSE_OUTLINED, on_click=lambda e:show_alert(page)), 
                        alignment=ft.Alignment(0, 0) 
                    ) 
                ], 
                alignment=ft.MainAxisAlignment.CENTER, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                expand=True 
            ) 
            
def loading_page(page:ft.Page, text="Saving today's weather...", ): 
        return ft.Column(controls=[ 
            ft.Text(text, size=25, text_align=ft.TextAlign.CENTER), 
            ft.ProgressBar(width=400, color=ft.Colors.BLUE, bgcolor=ft.Colors.BLUE_GREY_100),
        ], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
            expand=True) 
        
def show_loading_and_save(data_set, page:ft.Page): 
        async def do_save(): 
            page.controls.clear() 
            page.add(loading_page(page)) 
            page.update() 
            await asyncio.sleep(3) 
            save_history(data_set)
            page.controls.clear() 
            page.add(saved_successfully_page(page)) 
            page.update() 
        page.run_task(do_save) 
    
def saved_successfully_page(page:ft.Page): 
        return ft.Column(controls=[ 
            ft.Text("Saved successfully!", size=28, color=ft.Colors.GREEN, text_align=ft.TextAlign.CENTER), 
            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, color=ft.Colors.GREEN, size=60), 
            ft.Button("View Weather", on_click=lambda e: page.go("/fetchweather/weather/view")), 
            ft.Button("Back to Home", on_click=lambda e: page.go("/"))
        ], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
            expand=True) 
    
def return_to_weather(page:ft.Page): 
        if state.city.value != '': 
            weather_kind = kinda_weather() 
            container_width = 350 
            container_height = 220 
            column1 = ft.Container( 
                ft.Column( 
                    controls=[
                        ft.Text("Today's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE), 
                        ft.Text(f"Date: {state.globalargs['date']}", text_align=ft.TextAlign.CENTER), 
                        ft.Text(f"Description: {state.weathertoday['description']}", text_align=ft.TextAlign.CENTER), 
                        ft.Text(f"Temperature: {state.weathertoday['temperature']}℃", text_align=ft.TextAlign.CENTER) 
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                ), 
                width=container_width, 
                height=container_height, 
                alignment=ft.Alignment(0, 0), 
                bgcolor=ft.Colors.BLUE_GREY_400, 
                opacity=0.9, 
                padding=20, 
                border_radius=10 
            ) 
    
            column2 = ft.Container( 
                ft.Column( 
                    controls=[ 
                        ft.Text("Tomorrow's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE), 
                        ft.Text("Date: {}".format(state.three_dates[0]), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Highest Temperature: {}℃".format(state.three_days[0]['highest_temperature']), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Lowest Temperature: {}℃".format(state.three_days[0]['lowest_temperature']), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Average Temperature: {}℃".format(state.three_days[0]['average_temperature']), text_align=ft.TextAlign.CENTER) 
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                ), 
                width=container_width, 
                height=container_height, 
                alignment=ft.Alignment(0, 0), 
                bgcolor=ft.Colors.BLUE_GREY_400, 
                opacity=0.9, 
                padding=20, 
                border_radius=10 
            ) 
    
            column3 = ft.Container( 
                ft.Column( 
                    controls=[ 
                        ft.Text("The day after tomorrow's forecast:", size=22, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE), 
                        ft.Text("Date: {}".format(state.three_dates[1]), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Highest Temperature: {}℃".format(state.three_days[1]['highest_temperature']), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Lowest Temperature: {}℃".format(state.three_days[1]['lowest_temperature']), text_align=ft.TextAlign.CENTER), 
                        ft.Text("Average Temperature: {}℃".format(state.three_days[1]['average_temperature']), text_align=ft.TextAlign.CENTER) 
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER, 
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                ), 
                width=container_width, 
                height=container_height, 
                alignment=ft.Alignment(0, 0), 
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
                            ft.Text("Weather in %s today: " % (state.city.value,), size=30, text_align=ft.TextAlign.CENTER), 
                            ft.Text("Coordinates: ({}, {})".format(state.globalargs['coords'][0], state.globalargs['coords'][1]), size=20, text_align=ft.TextAlign.CENTER) 
                        ]), 
                            ft.Image(src=weather_kind)
                        ], 
                        alignment=ft.MainAxisAlignment.CENTER, 
                        vertical_alignment=ft.CrossAxisAlignment.CENTER 
                ),
                    container_row, 
                    ft.Container( 
                        ft.Button("Back", on_click=lambda e: page.go("/fetchweather")), 
                        alignment=ft.Alignment(0, 0)
                    ), 
                    ft.Container( 
                        ft.IconButton(icon=ft.Icons.HOUSE_OUTLINED, on_click=lambda e:show_alert(page)), 
                        alignment=ft.Alignment(0, 0)
                    )
                ], 
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                expand=True 
            ) 
    