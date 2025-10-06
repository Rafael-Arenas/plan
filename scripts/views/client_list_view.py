#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vista de Lista de Clientes para Flet
====================================

Vista principal para mostrar, buscar y gestionar la lista de clientes,
siguiendo los principios de Material Design y las mejores prácticas de Flet.

Características:
- Lista paginada de clientes
- Búsqueda y filtrado avanzado
- Integración con ClientDomainService
- Estados de carga y error
- Acciones contextuales
- Interfaz responsiva
- Optimización de rendimiento
- Manejo de errores robusto

Autor: FletArchitect
"""

from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime
import math

import flet as ft
from loguru import logger

# Importar componentes y servicios del proyecto
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from planificador.schemas.client import Client, ClientFilter, ClientSort
from planificador.services.domain.client.client_domain_service import ClientDomainService

# Importar componentes locales
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.client_card import ClientCard
from components.search_bar import SearchBar


class LoadingState:
    """Estados de carga de la vista."""
    IDLE = "idle"
    LOADING = "loading"
    ERROR = "error"
    EMPTY = "empty"


class ClientListView(ft.Container):
    """
    Vista principal para la lista de clientes.
    
    Esta vista proporciona una interfaz completa para visualizar,
    buscar y gestionar clientes, incluyendo paginación, filtros
    avanzados y acciones contextuales.
    
    Attributes:
        client_service: Servicio de dominio para clientes
        on_client_selected: Callback cuando se selecciona un cliente
        on_client_edit: Callback para editar un cliente
        on_client_delete: Callback para eliminar un cliente
        on_client_create: Callback para crear un nuevo cliente
        items_per_page: Número de elementos por página
        show_actions: Si mostrar acciones en las tarjetas
    """
    
    def __init__(
        self,
        client_service: ClientDomainService,
        on_client_selected: Optional[callable] = None,
        on_client_edit: Optional[callable] = None,
        on_client_delete: Optional[callable] = None,
        on_client_create: Optional[callable] = None,
        items_per_page: int = 10,
        show_actions: bool = True,
        **kwargs
    ):
        """
        Inicializa la vista de lista de clientes.
        
        Args:
            client_service: Servicio de dominio para clientes
            on_client_selected: Callback para selección de cliente
            on_client_edit: Callback para edición de cliente
            on_client_delete: Callback para eliminación de cliente
            on_client_create: Callback para creación de cliente
            items_per_page: Elementos por página
            show_actions: Si mostrar acciones en tarjetas
            **kwargs: Argumentos adicionales para ft.Container
        """
        super().__init__(**kwargs)
        
        self.client_service = client_service
        self.on_client_selected = on_client_selected
        self.on_client_edit = on_client_edit
        self.on_client_delete = on_client_delete
        self.on_client_create = on_client_create
        self.items_per_page = items_per_page
        self.show_actions = show_actions
        
        self._logger = logger.bind(component="ClientListView")
        
        # Estado de la vista
        self._loading_state = LoadingState.IDLE
        self._clients: List[Client] = []
        self._total_clients = 0
        self._current_page = 1
        self._total_pages = 1
        self._current_filters = ClientFilter()
        self._current_sort = ClientSort(field="name", direction="asc")
        self._current_search_query = ""
        
        # Referencias a elementos de UI
        self._search_bar = ft.Ref[SearchBar]()
        self._clients_container = ft.Ref[ft.Container]()
        self._pagination_container = ft.Ref[ft.Container]()
        self._loading_indicator = ft.Ref[ft.ProgressRing]()
        self._error_container = ft.Ref[ft.Container]()
        self._empty_container = ft.Ref[ft.Container]()
        self._stats_container = ft.Ref[ft.Container]()
        
        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = ft.padding.all(16)
        
        # Construir la vista
        self._build_view()
        
        # Cargar datos iniciales
        asyncio.create_task(self._load_clients())
        
        self._logger.debug("ClientListView inicializada")
    
    def _build_view(self):
        """Construye la estructura de la vista."""
        try:
            self.content = ft.Column([
                # Encabezado con título y botón crear
                self._build_header(),
                
                # Barra de búsqueda y filtros
                SearchBar(
                    ref=self._search_bar,
                    on_search=self._handle_search,
                    on_filter_change=self._handle_filter_change,
                    on_sort_change=self._handle_sort_change,
                    placeholder="Buscar clientes por nombre, código o email..."
                ),
                
                # Estadísticas rápidas
                ft.Container(
                    ref=self._stats_container,
                    content=self._build_stats_row(),
                    padding=ft.padding.symmetric(vertical=8)
                ),
                
                # Contenedor principal de contenido
                ft.Container(
                    ref=self._clients_container,
                    content=self._build_loading_content(),
                    expand=True
                ),
                
                # Paginación
                ft.Container(
                    ref=self._pagination_container,
                    content=self._build_pagination(),
                    padding=ft.padding.symmetric(vertical=8)
                )
            ], 
            spacing=12,
            expand=True)
            
        except Exception as e:
            self._logger.error(f"Error construyendo vista: {e}")
            self.content = self._build_error_view()
    
    def _build_header(self) -> ft.Container:
        """Construye el encabezado de la vista."""
        return ft.Container(
            content=ft.Row([
                # Título y descripción
                ft.Column([
                    ft.Text(
                        "Gestión de Clientes",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.PRIMARY
                    ),
                    ft.Text(
                        "Administra y visualiza todos los clientes del sistema",
                        size=14,
                        color=ft.Colors.GREY_600
                    )
                ], spacing=4, expand=True),
                
                # Botón crear cliente
                ft.ElevatedButton(
                    text="Nuevo Cliente",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self._handle_create_client(),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY
                    )
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(bottom=16)
        )
    
    def _build_stats_row(self) -> ft.Row:
        """Construye la fila de estadísticas rápidas."""
        return ft.Row([
            # Total de clientes
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.BLUE, size=20),
                    ft.Column([
                        ft.Text(
                            str(self._total_clients),
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE
                        ),
                        ft.Text(
                            "Total Clientes",
                            size=12,
                            color=ft.Colors.GREY_600
                        )
                    ], spacing=2)
                ], spacing=8),
                padding=ft.padding.all(12),
                bgcolor=ft.Colors.BLUE_50,
                border_radius=ft.border_radius.all(8),
                border=ft.border.all(1, ft.Colors.BLUE_200)
            ),
            
            # Clientes activos
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=20),
                    ft.Column([
                        ft.Text(
                            str(len([c for c in self._clients if c.is_active])),
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREEN
                        ),
                        ft.Text(
                            "Activos",
                            size=12,
                            color=ft.Colors.GREY_600
                        )
                    ], spacing=2)
                ], spacing=8),
                padding=ft.padding.all(12),
                bgcolor=ft.Colors.GREEN_50,
                border_radius=ft.border_radius.all(8),
                border=ft.border.all(1, ft.Colors.GREEN_200)
            ),
            
            # Página actual
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PAGES, color=ft.Colors.ORANGE, size=20),
                    ft.Column([
                        ft.Text(
                            f"{self._current_page}/{self._total_pages}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ORANGE
                        ),
                        ft.Text(
                            "Página",
                            size=12,
                            color=ft.Colors.GREY_600
                        )
                    ], spacing=2)
                ], spacing=8),
                padding=ft.padding.all(12),
                bgcolor=ft.Colors.ORANGE_50,
                border_radius=ft.border_radius.all(8),
                border=ft.border.all(1, ft.Colors.ORANGE_200)
            )
        ], spacing=16)
    
    def _build_loading_content(self) -> ft.Container:
        """Construye el contenido de carga."""
        return ft.Container(
            content=ft.Column([
                ft.ProgressRing(
                    ref=self._loading_indicator,
                    width=50,
                    height=50,
                    stroke_width=4
                ),
                ft.Text(
                    "Cargando clientes...",
                    size=16,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.CENTER
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16),
            alignment=ft.alignment.center,
            expand=True
        )
    
    def _build_clients_grid(self) -> ft.Container:
        """Construye la grilla de clientes."""
        if not self._clients:
            return self._build_empty_content()
        
        # Crear tarjetas de clientes
        client_cards = []
        for client in self._clients:
            card = ClientCard(
                client=client,
                on_view=lambda c: self._handle_client_selected(c),
                on_edit=lambda c: self._handle_client_edit(c),
                on_delete=lambda c: self._handle_client_delete(c),
                show_actions=self.show_actions,
                compact_mode=False
            )
            client_cards.append(card)
        
        # Organizar en grilla responsiva
        return ft.Container(
            content=ft.Column([
                ft.GridView(
                    controls=client_cards,
                    runs_count=0,  # Auto-ajustar columnas
                    max_extent=400,  # Ancho máximo por tarjeta
                    child_aspect_ratio=1.2,  # Relación aspecto
                    spacing=12,
                    run_spacing=12,
                    expand=True
                )
            ], expand=True),
            expand=True
        )
    
    def _build_empty_content(self) -> ft.Container:
        """Construye el contenido cuando no hay clientes."""
        return ft.Container(
            ref=self._empty_container,
            content=ft.Column([
                ft.Icon(
                    ft.Icons.PEOPLE_OUTLINE,
                    size=80,
                    color=ft.Colors.GREY_400
                ),
                ft.Text(
                    "No se encontraron clientes",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Intenta ajustar los filtros de búsqueda o crear un nuevo cliente",
                    size=14,
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                ft.ElevatedButton(
                    text="Crear Primer Cliente",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self._handle_create_client(),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY
                    )
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12),
            alignment=ft.alignment.center,
            expand=True
        )
    
    def _build_error_content(self, error_message: str) -> ft.Container:
        """Construye el contenido de error."""
        return ft.Container(
            ref=self._error_container,
            content=ft.Column([
                ft.Icon(
                    ft.Icons.ERROR_OUTLINE,
                    size=80,
                    color=ft.Colors.RED_400
                ),
                ft.Text(
                    "Error cargando clientes",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.RED_600,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    error_message,
                    size=14,
                    color=ft.Colors.RED_500,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                ft.ElevatedButton(
                    text="Reintentar",
                    icon=ft.Icons.REFRESH,
                    on_click=lambda e: asyncio.create_task(self._load_clients()),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.RED,
                        color=ft.Colors.ON_ERROR
                    )
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12),
            alignment=ft.alignment.center,
            expand=True
        )
    
    def _build_error_view(self) -> ft.Column:
        """Construye la vista de error general."""
        return ft.Column([
            ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED, size=48),
            ft.Text(
                "Error inicializando vista de clientes",
                color=ft.Colors.RED,
                size=16,
                text_align=ft.TextAlign.CENTER
            )
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True)
    
    def _build_pagination(self) -> ft.Row:
        """Construye los controles de paginación."""
        if self._total_pages <= 1:
            return ft.Row([])
        
        pagination_controls = []
        
        # Botón primera página
        pagination_controls.append(
            ft.IconButton(
                icon=ft.Icons.FIRST_PAGE,
                tooltip="Primera página",
                on_click=lambda e: self._go_to_page(1),
                disabled=self._current_page == 1
            )
        )
        
        # Botón página anterior
        pagination_controls.append(
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                tooltip="Página anterior",
                on_click=lambda e: self._go_to_page(self._current_page - 1),
                disabled=self._current_page == 1
            )
        )
        
        # Información de página actual
        pagination_controls.append(
            ft.Container(
                content=ft.Text(
                    f"Página {self._current_page} de {self._total_pages}",
                    size=14,
                    weight=ft.FontWeight.BOLD
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=8)
            )
        )
        
        # Botón página siguiente
        pagination_controls.append(
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                tooltip="Página siguiente",
                on_click=lambda e: self._go_to_page(self._current_page + 1),
                disabled=self._current_page == self._total_pages
            )
        )
        
        # Botón última página
        pagination_controls.append(
            ft.IconButton(
                icon=ft.Icons.LAST_PAGE,
                tooltip="Última página",
                on_click=lambda e: self._go_to_page(self._total_pages),
                disabled=self._current_page == self._total_pages
            )
        )
        
        return ft.Row(
            pagination_controls,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8
        )
    
    # ==================== EVENT HANDLERS ====================
    
    def _handle_search(self, query: str):
        """Maneja eventos de búsqueda."""
        try:
            self._current_search_query = query
            self._current_page = 1  # Resetear a primera página
            asyncio.create_task(self._load_clients())
            self._logger.debug(f"Búsqueda ejecutada: '{query}'")
        except Exception as e:
            self._logger.error(f"Error manejando búsqueda: {e}")
    
    def _handle_filter_change(self, filters: ClientFilter):
        """Maneja cambios en los filtros."""
        try:
            self._current_filters = filters
            self._current_page = 1  # Resetear a primera página
            asyncio.create_task(self._load_clients())
            self._logger.debug("Filtros actualizados")
        except Exception as e:
            self._logger.error(f"Error manejando cambio de filtros: {e}")
    
    def _handle_sort_change(self, sort_config: ClientSort):
        """Maneja cambios en el ordenamiento."""
        try:
            self._current_sort = sort_config
            asyncio.create_task(self._load_clients())
            self._logger.debug(f"Ordenamiento actualizado: {sort_config.field} {sort_config.direction}")
        except Exception as e:
            self._logger.error(f"Error manejando cambio de ordenamiento: {e}")
    
    def _handle_client_selected(self, client: Client):
        """Maneja la selección de un cliente."""
        try:
            if self.on_client_selected:
                self.on_client_selected(client)
            self._logger.debug(f"Cliente seleccionado: {client.name}")
        except Exception as e:
            self._logger.error(f"Error manejando selección de cliente: {e}")
    
    def _handle_client_edit(self, client: Client):
        """Maneja la edición de un cliente."""
        try:
            if self.on_client_edit:
                self.on_client_edit(client)
            self._logger.debug(f"Edición de cliente solicitada: {client.name}")
        except Exception as e:
            self._logger.error(f"Error manejando edición de cliente: {e}")
    
    def _handle_client_delete(self, client: Client):
        """Maneja la eliminación de un cliente."""
        try:
            if self.on_client_delete:
                self.on_client_delete(client)
            self._logger.debug(f"Eliminación de cliente solicitada: {client.name}")
        except Exception as e:
            self._logger.error(f"Error manejando eliminación de cliente: {e}")
    
    def _handle_create_client(self):
        """Maneja la creación de un nuevo cliente."""
        try:
            if self.on_client_create:
                self.on_client_create()
            self._logger.debug("Creación de cliente solicitada")
        except Exception as e:
            self._logger.error(f"Error manejando creación de cliente: {e}")
    
    # ==================== DATA LOADING ====================
    
    async def _load_clients(self):
        """Carga los clientes desde el servicio de dominio."""
        try:
            self._set_loading_state(LoadingState.LOADING)
            
            # Preparar parámetros de consulta
            skip = (self._current_page - 1) * self.items_per_page
            limit = self.items_per_page
            
            # Aplicar filtros de búsqueda
            if self._current_search_query.strip():
                self._current_filters.search_query = self._current_search_query.strip()
            
            # Obtener clientes del servicio
            clients_response = await self.client_service.get_clients_paginated(
                skip=skip,
                limit=limit,
                filters=self._current_filters,
                sort=self._current_sort
            )
            
            # Actualizar estado
            self._clients = clients_response.items
            self._total_clients = clients_response.total
            self._total_pages = math.ceil(self._total_clients / self.items_per_page) if self._total_clients > 0 else 1
            
            # Determinar estado final
            if self._clients:
                self._set_loading_state(LoadingState.IDLE)
            else:
                self._set_loading_state(LoadingState.EMPTY)
            
            self._logger.debug(f"Clientes cargados: {len(self._clients)} de {self._total_clients}")
            
        except Exception as e:
            self._logger.error(f"Error cargando clientes: {e}")
            self._set_loading_state(LoadingState.ERROR)
            self._update_error_content(str(e))
    
    def _set_loading_state(self, state: str):
        """Establece el estado de carga y actualiza la UI."""
        try:
            self._loading_state = state
            
            # Actualizar contenido según el estado
            if state == LoadingState.LOADING:
                content = self._build_loading_content()
            elif state == LoadingState.ERROR:
                content = self._build_error_content("Error desconocido")
            elif state == LoadingState.EMPTY:
                content = self._build_empty_content()
            else:  # IDLE
                content = self._build_clients_grid()
            
            # Actualizar contenedor principal
            if self._clients_container.current:
                self._clients_container.current.content = content
                self._clients_container.current.update()
            
            # Actualizar estadísticas
            if self._stats_container.current:
                self._stats_container.current.content = self._build_stats_row()
                self._stats_container.current.update()
            
            # Actualizar paginación
            if self._pagination_container.current:
                self._pagination_container.current.content = self._build_pagination()
                self._pagination_container.current.update()
                
        except Exception as e:
            self._logger.error(f"Error estableciendo estado de carga: {e}")
    
    def _update_error_content(self, error_message: str):
        """Actualiza el contenido de error con un mensaje específico."""
        try:
            if self._loading_state == LoadingState.ERROR and self._clients_container.current:
                self._clients_container.current.content = self._build_error_content(error_message)
                self._clients_container.current.update()
        except Exception as e:
            self._logger.error(f"Error actualizando contenido de error: {e}")
    
    # ==================== NAVIGATION ====================
    
    def _go_to_page(self, page: int):
        """Navega a una página específica."""
        try:
            if 1 <= page <= self._total_pages and page != self._current_page:
                self._current_page = page
                asyncio.create_task(self._load_clients())
                self._logger.debug(f"Navegando a página: {page}")
        except Exception as e:
            self._logger.error(f"Error navegando a página: {e}")
    
    # ==================== PUBLIC METHODS ====================
    
    async def refresh_clients(self):
        """Refresca la lista de clientes."""
        try:
            await self._load_clients()
            self._logger.debug("Lista de clientes refrescada")
        except Exception as e:
            self._logger.error(f"Error refrescando clientes: {e}")
    
    def get_selected_clients(self) -> List[Client]:
        """
        Obtiene los clientes actualmente mostrados.
        
        Returns:
            Lista de clientes actuales
        """
        return self._clients.copy()
    
    def get_current_page(self) -> int:
        """
        Obtiene la página actual.
        
        Returns:
            Número de página actual
        """
        return self._current_page
    
    def get_total_pages(self) -> int:
        """
        Obtiene el total de páginas.
        
        Returns:
            Número total de páginas
        """
        return self._total_pages
    
    def get_total_clients(self) -> int:
        """
        Obtiene el total de clientes.
        
        Returns:
            Número total de clientes
        """
        return self._total_clients
    
    def set_items_per_page(self, items: int):
        """
        Establece el número de elementos por página.
        
        Args:
            items: Número de elementos por página
        """
        try:
            if items > 0 and items != self.items_per_page:
                self.items_per_page = items
                self._current_page = 1
                asyncio.create_task(self._load_clients())
                self._logger.debug(f"Elementos por página actualizado: {items}")
        except Exception as e:
            self._logger.error(f"Error estableciendo elementos por página: {e}")
    
    def search_clients(self, query: str):
        """
        Busca clientes con una consulta específica.
        
        Args:
            query: Consulta de búsqueda
        """
        try:
            if self._search_bar.current:
                self._search_bar.current.set_search_query(query)
        except Exception as e:
            self._logger.error(f"Error buscando clientes: {e}")
    
    def clear_search(self):
        """Limpia la búsqueda actual."""
        try:
            if self._search_bar.current:
                self._search_bar.current.set_search_query("")
        except Exception as e:
            self._logger.error(f"Error limpiando búsqueda: {e}")
    
    def get_loading_state(self) -> str:
        """
        Obtiene el estado de carga actual.
        
        Returns:
            Estado de carga actual
        """
        return self._loading_state
