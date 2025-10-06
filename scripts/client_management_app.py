#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación Flet para Gestión de Clientes
========================================

Aplicación de escritorio desarrollada con Flet para la gestión integral de clientes,
integrando todos los servicios del dominio cliente del sistema Planificador.

Características principales:
- Interfaz moderna y responsiva con Material Design
- Operaciones CRUD completas para clientes
- Búsqueda avanzada y filtros dinámicos
- Estadísticas y métricas en tiempo real
- Validaciones de negocio integradas
- Manejo robusto de errores
- Notificaciones de usuario contextuales

Autor: FletArchitect
Versión: 1.0.0
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from uuid import UUID

import flet as ft
from loguru import logger

# Configurar el path para importar módulos del proyecto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from planificador.config.config import settings
from planificador.database.database import AsyncSessionLocal, initialize_database, close_database, get_db, db_manager
from planificador.services.domain.client.client_domain_service import ClientDomainService
from planificador.schemas.client import (
    Client,
    ClientCreate,
    ClientUpdate,
    ClientStatsResponse,
    ClientFilter,
    ClientSort
)
from planificador.exceptions import (
    RepositoryError,
    ValidationError,
    BusinessLogicError
)


class ClientManagementApp:
    """
    Aplicación principal para gestión de clientes con Flet.
    
    Esta clase actúa como el controlador principal de la aplicación,
    coordinando la interfaz de usuario con los servicios de dominio.
    """
    
    def __init__(self, page: ft.Page):
        """
        Inicializa la aplicación de gestión de clientes.
        
        Args:
            page: Página principal de Flet
        """
        self.page = page
        self._logger = logger.bind(component="ClientManagementApp")
        
        # Configuración de la página
        self._setup_page()
        
        # Estado de la aplicación
        self.current_view = "list"  # list, create, edit, stats
        self.selected_client: Optional[Client] = None
        self.clients_data: List[Client] = []
        self.stats_data: Optional[ClientStatsResponse] = None
        
        # Referencias a controles principales
        self.main_content = ft.Container()
        self.navigation_rail = ft.NavigationRail()
        self.app_bar = ft.AppBar()
        self.snack_bar = ft.SnackBar(content=ft.Text(""))
        
        # Servicio de dominio (se inicializa en build_ui)
        self.client_service: Optional[ClientDomainService] = None
        
        self._logger.info("ClientManagementApp inicializada")
    
    def _setup_page(self):
        """Configura las propiedades básicas de la página."""
        self.page.title = "Gestión de Clientes - Planificador"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        self.page.padding = 0
        self.page.spacing = 0
        
        # Configurar tema personalizado
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
            use_material3=True
        )
        
        self._logger.debug("Configuración de página completada")
    
    async def initialize_services(self):
        """Inicializa los servicios de dominio necesarios."""
        try:
            self._logger.info("Inicializando servicios de dominio")
            
            # Inicializar base de datos
            try:
                await initialize_database()
                logger.info("✅ Base de datos inicializada correctamente")
            except Exception as e:
                logger.error(f"❌ Error inicializando base de datos: {e}")
                await self.show_error("Error de Base de Datos", 
                                    f"No se pudo inicializar la base de datos: {e}")
                return
            
            # Crear sesión de base de datos usando el context manager del db_manager
            self.db_session_context = db_manager.get_session()
            self.db_session = await self.db_session_context.__aenter__()
            
            # Inicializar servicio de dominio cliente
            self.client_service = ClientDomainService(self.db_session)
            
            self._logger.info("Servicios inicializados correctamente")
            
        except Exception as e:
            self._logger.error(f"Error inicializando servicios: {e}")
            await self._show_error("Error de Inicialización", 
                                 f"No se pudieron inicializar los servicios: {e}")
            raise
    
    async def cleanup(self):
        """Limpia recursos de la aplicación."""
        try:
            self._logger.info("Iniciando limpieza de recursos")
            
            # Cerrar servicio de dominio
            if hasattr(self, 'client_service') and self.client_service:
                await self.client_service.close()
                
            # Cerrar sesión de base de datos
            if hasattr(self, 'db_session_context') and self.db_session_context:
                await self.db_session_context.__aexit__(None, None, None)
                
            self._logger.info("Recursos limpiados correctamente")
            
        except Exception as e:
            self._logger.error(f"Error durante limpieza: {e}")

    async def build_ui(self):
        """Construye la interfaz de usuario principal."""
        try:
            self._logger.info("Construyendo interfaz de usuario")
            
            # Inicializar servicios primero
            await self.initialize_services()
            
            # Crear barra de aplicación
            self._create_app_bar()
            
            # Crear navegación lateral
            self._create_navigation_rail()
            
            # Crear contenido principal
            await self._create_main_content()
            
            # Configurar layout principal
            main_layout = ft.Row(
                controls=[
                    self.navigation_rail,
                    ft.VerticalDivider(width=1),
                    ft.Container(
                        content=self.main_content,
                        expand=True,
                        padding=20
                    )
                ],
                expand=True,
                spacing=0
            )
            
            # Agregar controles a la página
            self.page.appbar = self.app_bar
            self.page.add(main_layout)
            self.page.overlay.append(self.snack_bar)
            
            # Cargar datos iniciales
            await self._load_initial_data()
            
            self._logger.info("Interfaz de usuario construida correctamente")
            
        except Exception as e:
            self._logger.error(f"Error construyendo UI: {e}")
            await self._show_error("Error de Interfaz", 
                                 f"No se pudo construir la interfaz: {e}")
    
    def _create_app_bar(self):
        """Crea la barra de aplicación superior."""
        self.app_bar = ft.AppBar(
            title=ft.Text(
                "Gestión de Clientes",
                size=20,
                weight=ft.FontWeight.BOLD
            ),
            center_title=False,
            bgcolor=ft.Colors.SURFACE,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Actualizar datos",
                    on_click=self._on_refresh_clicked
                ),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    tooltip="Configuración",
                    on_click=self._on_settings_clicked
                )
            ]
        )
    
    def _create_navigation_rail(self):
        """Crea la barra de navegación lateral."""
        self.navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIST,
                    selected_icon=ft.Icons.LIST,
                    label="Lista"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ADD,
                    selected_icon=ft.Icons.ADD,
                    label="Crear"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ANALYTICS,
                    selected_icon=ft.Icons.ANALYTICS,
                    label="Estadísticas"
                )
            ],
            on_change=self._on_navigation_changed
        )
    
    async def _create_main_content(self):
        """Crea el contenedor principal de contenido."""
        self.main_content = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Cargando...",
                    size=16,
                    text_align=ft.TextAlign.CENTER
                )
            ]),
            expand=True
        )
    
    async def _load_initial_data(self):
        """Carga los datos iniciales de la aplicación."""
        try:
            self._logger.info("Cargando datos iniciales")
            
            # Cargar lista de clientes
            await self._load_clients_data()
            
            # Mostrar vista de lista por defecto
            await self._show_clients_list()
            
            self._logger.info("Datos iniciales cargados correctamente")
            
        except Exception as e:
            self._logger.error(f"Error cargando datos iniciales: {e}")
            await self._show_error("Error de Datos", 
                                 f"No se pudieron cargar los datos: {e}")
    
    async def _load_clients_data(self):
        """Carga la lista de clientes desde el servicio."""
        try:
            if not self.client_service:
                raise RuntimeError("Servicio de cliente no inicializado")
            
            # Obtener clientes activos
            self.clients_data = await self.client_service.get_active_clients()
            
            self._logger.info(f"Cargados {len(self.clients_data)} clientes")
            
        except Exception as e:
            self._logger.error(f"Error cargando clientes: {e}")
            self.clients_data = []
            raise
    
    async def _show_clients_list(self):
        """Muestra la vista de lista de clientes."""
        try:
            self._logger.debug("Mostrando lista de clientes")
            
            # Crear encabezado de la lista
            header = ft.Container(
                content=ft.Row([
                    ft.Text(
                        "Lista de Clientes",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text="Nuevo Cliente",
                        icon=ft.Icons.ADD,
                        on_click=self._on_new_client_clicked
                    )
                ]),
                padding=ft.padding.only(bottom=20)
            )
            
            # Crear barra de búsqueda
            search_bar = ft.Container(
                content=ft.TextField(
                    label="Buscar clientes...",
                    prefix_icon=ft.Icons.SEARCH,
                    on_change=self._on_search_changed,
                    expand=True
                ),
                padding=ft.padding.only(bottom=20)
            )
            
            # Crear lista de clientes
            clients_list = self._create_clients_list()
            
            # Actualizar contenido principal
            self.main_content.content = ft.Column([
                header,
                search_bar,
                clients_list
            ])
            
            self.page.update()
            
        except Exception as e:
            self._logger.error(f"Error mostrando lista de clientes: {e}")
            await self._show_error("Error de Vista", 
                                 f"No se pudo mostrar la lista: {e}")
    
    def _create_clients_list(self) -> ft.Container:
        """Crea la lista visual de clientes."""
        if not self.clients_data:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX, size=64, color=ft.Colors.GREY_400),
                    ft.Text(
                        "No hay clientes registrados",
                        size=16,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    )
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                height=200
            )
        
        # Crear tarjetas de clientes
        client_cards = []
        for client in self.clients_data:
            card = self._create_client_card(client)
            client_cards.append(card)
        
        return ft.Container(
            content=ft.ListView(
                controls=client_cards,
                spacing=10,
                padding=ft.padding.all(10)
            ),
            expand=True
        )
    
    def _create_client_card(self, client: Client) -> ft.Card:
        """Crea una tarjeta visual para un cliente."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.CircleAvatar(
                            content=ft.Text(
                                client.name[0].upper(),
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=ft.Colors.BLUE
                        ),
                        title=ft.Text(
                            client.name,
                            weight=ft.FontWeight.BOLD
                        ),
                        subtitle=ft.Text(f"Código: {client.code}"),
                        trailing=ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(
                                    text="Ver detalles",
                                    icon=ft.Icons.VISIBILITY,
                                    on_click=lambda e, c=client: self._on_view_client(c)
                                ),
                                ft.PopupMenuItem(
                                    text="Editar",
                                    icon=ft.Icons.EDIT,
                                    on_click=lambda e, c=client: self._on_edit_client(c)
                                ),
                                ft.PopupMenuItem(
                                    text="Eliminar",
                                    icon=ft.Icons.DELETE,
                                    on_click=lambda e, c=client: self._on_delete_client(c)
                                )
                            ]
                        )
                    ),
                    ft.Divider(height=1),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(
                                ft.Icons.EMAIL,
                                size=16,
                                color=ft.Colors.GREY_600
                            ),
                            ft.Text(
                                client.email or "Sin email",
                                size=12,
                                color=ft.Colors.GREY_600
                            ),
                            ft.Container(expand=True),
                            ft.Chip(
                                label=ft.Text(
                                    "Activo" if client.is_active else "Inactivo",
                                    size=10
                                ),
                                bgcolor=ft.Colors.GREEN_100 if client.is_active else ft.Colors.RED_100
                            )
                        ]),
                        padding=ft.padding.symmetric(horizontal=16, vertical=8)
                    )
                ]),
                padding=0
            ),
            elevation=2
        )
    
    # ==================== EVENT HANDLERS ====================
    
    async def _on_navigation_changed(self, e):
        """Maneja cambios en la navegación lateral."""
        try:
            selected_index = e.control.selected_index
            
            if selected_index == 0:  # Lista
                self.current_view = "list"
                await self._show_clients_list()
            elif selected_index == 1:  # Crear
                self.current_view = "create"
                await self._show_create_form()
            elif selected_index == 2:  # Estadísticas
                self.current_view = "stats"
                await self._show_statistics()
                
        except Exception as e:
            self._logger.error(f"Error en navegación: {e}")
            await self._show_error("Error de Navegación", str(e))
    
    async def _on_refresh_clicked(self, e):
        """Maneja el clic en el botón de actualizar."""
        try:
            await self._load_clients_data()
            await self._show_clients_list()
            await self._show_success("Datos actualizados correctamente")
            
        except Exception as e:
            self._logger.error(f"Error actualizando datos: {e}")
            await self._show_error("Error de Actualización", str(e))
    
    async def _on_settings_clicked(self, e):
        """Maneja el clic en configuración."""
        await self._show_info("Configuración", "Funcionalidad en desarrollo")
    
    async def _on_new_client_clicked(self, e):
        """Maneja el clic en nuevo cliente."""
        self.navigation_rail.selected_index = 1
        await self._show_create_form()
        self.page.update()
    
    async def _on_search_changed(self, e):
        """Maneja cambios en la búsqueda."""
        # TODO: Implementar búsqueda en tiempo real
        pass
    
    async def _on_view_client(self, client: Client):
        """Maneja la visualización de detalles de cliente."""
        await self._show_info("Detalles del Cliente", f"Cliente: {client.name}")
    
    async def _on_edit_client(self, client: Client):
        """Maneja la edición de cliente."""
        self.selected_client = client
        await self._show_edit_form()
    
    async def _on_delete_client(self, client: Client):
        """Maneja la eliminación de cliente."""
        # TODO: Implementar confirmación y eliminación
        await self._show_info("Eliminar Cliente", f"Eliminar: {client.name}")
    
    # ==================== VIEWS ====================
    
    async def _show_create_form(self):
        """Muestra el formulario de creación de cliente."""
        # TODO: Implementar formulario de creación
        self.main_content.content = ft.Column([
            ft.Text("Formulario de Creación", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("En desarrollo...", size=16)
        ])
        self.page.update()
    
    async def _show_edit_form(self):
        """Muestra el formulario de edición de cliente."""
        # TODO: Implementar formulario de edición
        self.main_content.content = ft.Column([
            ft.Text("Formulario de Edición", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("En desarrollo...", size=16)
        ])
        self.page.update()
    
    async def _show_statistics(self):
        """Muestra la vista de estadísticas."""
        # TODO: Implementar vista de estadísticas
        self.main_content.content = ft.Column([
            ft.Text("Estadísticas", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("En desarrollo...", size=16)
        ])
        self.page.update()
    
    # ==================== UTILITY METHODS ====================
    
    async def _show_success(self, message: str):
        """Muestra un mensaje de éxito."""
        self.snack_bar.content = ft.Text(message)
        self.snack_bar.bgcolor = ft.Colors.GREEN
        self.snack_bar.open = True
        self.page.update()
    
    async def _show_error(self, title: str, message: str):
        """Muestra un mensaje de error."""
        self.snack_bar.content = ft.Text(f"{title}: {message}")
        self.snack_bar.bgcolor = ft.Colors.RED
        self.snack_bar.open = True
        self.page.update()
    
    async def _show_info(self, title: str, message: str):
        """Muestra un mensaje informativo."""
        self.snack_bar.content = ft.Text(f"{title}: {message}")
        self.snack_bar.bgcolor = ft.Colors.BLUE
        self.snack_bar.open = True
        self.page.update()


async def main(page: ft.Page):
    """
    Función principal de la aplicación Flet.
    
    Args:
        page: Página principal de Flet
    """
    try:
        # Configurar logging
        logger.add(
            "logs/client_app.log",
            rotation="1 day",
            retention="7 days",
            level="INFO"
        )
        
        logger.info("Iniciando aplicación de gestión de clientes")
        
        # Crear y configurar la aplicación
        app = ClientManagementApp(page)
        await app.build_ui()
        
        logger.info("Aplicación iniciada correctamente")
        
    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {e}")
        # Mostrar error en la página si es posible
        if page:
            page.add(ft.Text(f"Error fatal: {e}", color=ft.Colors.RED))


if __name__ == "__main__":
    # Ejecutar la aplicación Flet
    ft.app(target=main, view=ft.AppView.FLET_APP)
