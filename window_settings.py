import flet as ft

def configure_page(page: ft.Page):
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.title = "WHETHERWEATHER!"


def show_alert(page:ft.Page, e=None): 
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
        ], 
        vertical_alignment=ft.CrossAxisAlignment.CENTER), 
        content=ft.Text("Are you sure you want to go home?", size=20), 
        actions=[ 
            ft.TextButton("Yes", on_click=on_yes), 
            ft.TextButton("No", on_click=on_no), 
        ], 
    ) 
    if alert_dialog not in page.overlay: 
        page.overlay.append(alert_dialog) 
    page.dialog = alert_dialog 
    page.dialog.open = True 
    page.update() 
