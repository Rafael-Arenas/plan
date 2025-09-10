# src/planificador/main.py

import flet as ft
from .config.logging_config import setup_logging
from .ui.main_view import MainView

async def main(page: ft.Page):
    """Función principal para inicializar la aplicación Flet."""
    # Configurar el logging al inicio de la aplicación
    setup_logging()
    page.title = "Planificador de Proyectos"
    page.window_width = 1200
    page.window_height = 800
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Inicializar la vista principal
    main_view = MainView()
    page.add(main_view)

    await page.update()

if __name__ == "__main__":
    ft.app_async(target=main)