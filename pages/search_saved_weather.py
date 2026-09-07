import flet as ft
from state import state
from history_storage import (
    read_history,
    read_full_history,
    delete_city_history,
    delete_all_history
    )

def manage_saved_weather(page:ft.Page):  
    state.searching_city = ft.TextField(label="Enter a valid city name from the database to perform an action") 
    history = read_full_history()

    if isinstance(history, str):
        tables_controls = []
    else:
        cities = sorted(
            set(item["searched location"] for item in history)
    )

    tables_controls = [
        ft.Text(city)
        for city in cities
    ] 
    if not tables_controls: 
        tables_list = ft.Column(controls=[ 
            ft.Text("Saved cities in database:", size=18), 
            ft.Text("No tables currently. Search up the weather in a city to get started!", color=ft.Colors.YELLOW, size=16) 
        ],
        alignment=ft.MainAxisAlignment.START) 
    else:
        tables_list = ft.Column(controls=[ft.Text("Saved cities in database:", size=18)] + tables_controls, alignment=ft.MainAxisAlignment.START) 

    def on_delete_city_history(e): 
        delete_city_history(state.searching_city.value) 
        page.go("/managedata") 


    def on_delete_all_data(e): 
        delete_all_history() 
        page.go("/managedata") 

    row1 = ft.Row( 
        controls=[ 
            ft.Button("Delete city's saved history", on_click=on_delete_city_history), 
            state.searching_city, 
            ft.Button("View city's saved history", on_click=lambda e: page.go(f"/managedata/{state.searching_city.value}")) 
        ], 
        alignment=ft.MainAxisAlignment.CENTER 
    ) 
    return ft.Column(controls=[ 
        ft.Text("View and manage your previously saved weather info here.", size=25),  
        ft.Container( 
            content = tables_list, 
            width=450, 
            alignment=ft.Alignment(0,0), 
            bgcolor=ft.Colors.BLUE_GREY_600, 
            opacity=0.8, 
            padding=20, 
            border_radius=10 
        ),
        row1,
        ft.Button("Delete all saved data...", on_click=on_delete_all_data), 
        ft.Button("Back", on_click=lambda e: page.go("/"))
    ],
    alignment=ft.MainAxisAlignment.CENTER, 
    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
    expand=True) 

def show_city_history_page(page, city_name):
    controls = []
    history = read_full_history()
    if isinstance(history, str):
        controls.append(ft.Text(history, color=ft.Colors.YELLOW))
    else:
        city_rows = [
            row
            for row in history
            if row["searched location"].lower()
            == city_name.lower()
        ]
        controls.append(
            ft.Text(
                f"History for city: {city_name}",
                size=25
            )
        )
        if city_rows:
            dt_columns = [
                ft.DataColumn(ft.Text("Date")),
                ft.DataColumn(ft.Text("Time")),
                ft.DataColumn(ft.Text("Fetched Location")),
                ft.DataColumn(ft.Text("Temp °C")),
                ft.DataColumn(ft.Text("Temp °F")),
                ft.DataColumn(ft.Text("Description"))
            ]
            dt_rows = []
            for row in city_rows:
                dt_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(row["date"]))),
                            ft.DataCell(ft.Text(str(row["time"]))),
                            ft.DataCell(ft.Text(str(row["fetched location"]))),
                            ft.DataCell(ft.Text(str(row["temp in celsius"]))),
                            ft.DataCell(ft.Text(str(row["temp in fahr"]))),
                            ft.DataCell(ft.Text(str(row["weather description"])))
                        ]
                    )
                )
            controls.append(
                ft.DataTable(
                    columns=dt_columns,
                    rows=dt_rows
                )
            )
        else:
            controls.append(
                ft.Text(
                    "No data found for this city.",
                    color=ft.Colors.YELLOW
                )
            )
    controls.append(
        ft.Button(
            "Back",
            on_click=lambda e: page.go("/managedata")
        )
    )
    return ft.Column(
        controls=controls,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    ) 
