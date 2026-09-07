import flet as ft
from state import state

def new_weather(page:ft.Page):
    state.city=ft.TextField(label="Enter the city name", width=500)
    return ft.Column(controls=
                    [
                        ft.Text("Search for a city's weather", size=25),
                        ft.Text("Powered by wttr.in", size=15),
                        ft.Text("(Enter the place name in title case. Specify the state)"),
                        state.city,
                        ft.Button("Search", on_click=lambda e:page.go("/fetchweather/result")),
                        ft.Button("Back", on_click=lambda e:page.go("/"))
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
    )