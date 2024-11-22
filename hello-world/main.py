import flet as ft


def main(page: ft.Page):
    page.add(ft.SafeArea(ft.Text("Hello, Flet!")))
    page.title = "Hello, Flet!"

    page.update()

ft.app(main)
