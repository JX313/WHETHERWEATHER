import flet as ft
import os
import asyncio

def home_page(page:ft.Page):
    async def quit_app(e):
        await page.window.close()
    return ft.Column(controls=
                    [
                        ft.Text("Welcome to WHETHERWEATHER!", size=30),
                        ft.Button("Search for weather in a city", on_click=lambda e:page.go("/fetchweather")),
                        ft.Button("View and manage saved weather history", on_click=lambda e:page.go("/managedata")),
                        ft.Button("About this app...", on_click=lambda e:page.go("/aboutapp")),
                        ft.Button("Quit app", on_click=quit_app)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                    )