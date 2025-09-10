# src/planificador/ui/main_view.py

import flet as ft
from loguru import logger

class MainView(ft.UserControl):
    """Vista principal que contiene la navegación y el contenido."""

    def build(self):
        logger.info("Construyendo la vista principal de la aplicación.")
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            leading=ft.FloatingActionButton(icon=ft.icons.CREATE, text="Añadir"),
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.HOME_OUTLINED,
                    selected_icon=ft.icons.HOME,
                    label="Inicio",
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.BUSINESS_OUTLINED),
                    selected_icon_content=ft.Icon(ft.icons.BUSINESS),
                    label="Clientes",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.FOLDER_OUTLINED,
                    selected_icon=ft.icons.FOLDER,
                    label="Proyectos",
                ),
                 ft.NavigationRailDestination(
                    icon=ft.icons.PERSON_OUTLINE,
                    selected_icon=ft.icons.PERSON,
                    label="Empleados",
                ),
            ],
            on_change=self.nav_change,
        )

        self.content_area = ft.Column(
            [ft.Text("Contenido de Inicio", size=20)],
            alignment=ft.MainAxisAlignment.START,
            expand=True,
        )

        return ft.Row(
            [
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ],
            expand=True,
        )

    async def nav_change(self, e):
        """Cambia el contenido principal según la selección de navegación."""
        selected_index = e.control.selected_index
        self.content_area.controls.clear()

        if selected_index == 0:
            self.content_area.controls.append(ft.Text("Página de Inicio"))
        elif selected_index == 1:
            self.content_area.controls.append(ft.Text("Página de Clientes"))
        elif selected_index == 2:
            self.content_area.controls.append(ft.Text("Página de Proyectos"))
        elif selected_index == 3:
            self.content_area.controls.append(ft.Text("Página de Empleados"))

        await self.update_async()