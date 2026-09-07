import flet as ft
from pages import (
    home_page,
    new_weather,
    fetched_new_weather,
    loading_page,
    manage_saved_weather,
    saved_successfully_page,
    show_city_history_page,
    return_to_weather,
    manage_saved_weather,
    about_app
)


def main(page:ft.Page):

    '''__________PAGE ORIENTATION + SETUP__________'''
    page.vertical_alignment=ft.CrossAxisAlignment.CENTER
    page.horizontal_alignment=ft.CrossAxisAlignment.CENTER
    page.theme_mode=ft.ThemeMode.DARK
    page.title=("WHETHERWEATHER!") 
    
    '''__________UNIVERSAL NAVIGATION__________'''
    def navigation(e):
        page.controls.clear()
        if page.route=="/":
            page.add(home_page(page))
        elif page.route=="/fetchweather":
            page.add(new_weather(page))
        elif page.route=="/fetchweather/result":
            page.add(fetched_new_weather(page))
        elif page.route=="/fetchweather/weather/view":
            page.add(return_to_weather(page))
        elif page.route=="/fetchweather/saved":
            page.add(saved_successfully_page(page))
        elif page.route=="/managedata":
            page.add(manage_saved_weather(page))
        elif page.route.startswith("/managedata/"):
            city_name = page.route.split("/")[-1]
            page.add(show_city_history_page(page, city_name))
        elif page.route=="/aboutapp":
            page.add(about_app(page))
        page.update()

    page.on_route_change = navigation
    navigation(None)


'''__________RUN APPLICATION__________'''
if __name__ == "__main__":
    ft.run(main)