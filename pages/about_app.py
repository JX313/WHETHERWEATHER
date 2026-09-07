import flet as ft

def about_app(page:ft.Page):
        about_text=(
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
                        size=14,
                        text_align=ft.TextAlign.LEFT,
                        color=ft.Colors.BLACK87,
                        selectable=True), 
                ft.Button("Back", on_click=lambda e: page.go("/")) 
            ], 
            alignment=ft.MainAxisAlignment.CENTER, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
            expand=True),
            alignment=ft.Alignment(0, 0),
            bgcolor=ft.Colors.BLUE_GREY_600,
            opacity=0.8,
            padding=30,
            border_radius=10,
            expand=True,
            width=None,
            height=None
        )
    
