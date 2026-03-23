import flet as ft
from frontend.app import AstlibraModApp


def main(page: ft.Page):
    """应用主入口"""
    app = AstlibraModApp(page)
    app.build()


if __name__ == "__main__":
    ft.app(target=main)
