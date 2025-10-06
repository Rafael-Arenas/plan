#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Componente SearchBar para Flet
==============================

Barra de búsqueda avanzada y reutilizable con capacidades de filtrado,
siguiendo los principios de Material Design y las mejores prácticas de Flet.

Características:
- Búsqueda en tiempo real
- Filtros avanzados
- Sugerencias automáticas
- Historial de búsquedas
- Búsqueda fuzzy opcional
- Estados de carga
- Interfaz responsiva
- Accesibilidad completa

Autor: FletArchitect
"""

from typing import Optional, Callable, Any, List, Dict
from enum import Enum
import asyncio
from datetime import datetime, timedelta

import flet as ft
from loguru import logger

# Importar esquemas del proyecto
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from planificador.schemas.client import ClientFilter, ClientSort


class SearchMode(Enum):
    """Modos de búsqueda disponibles."""
    SIMPLE = "simple"
    ADVANCED = "advanced"
    FUZZY = "fuzzy"


class SortDirection(Enum):
    """Direcciones de ordenamiento."""
    ASC = "asc"
    DESC = "desc"


class SearchBar(ft.Container):
    """
    Barra de búsqueda avanzada para clientes.
    
    Este componente proporciona una interfaz completa para búsqueda
    y filtrado de clientes, incluyendo búsqueda en tiempo real,
    filtros avanzados y opciones de ordenamiento.
    
    Attributes:
        on_search: Callback para eventos de búsqueda
        on_filter_change: Callback para cambios en filtros
        on_sort_change: Callback para cambios en ordenamiento
        search_delay: Retraso en milisegundos para búsqueda en tiempo real
        show_filters: Si mostrar panel de filtros avanzados
        show_sort: Si mostrar opciones de ordenamiento
        placeholder: Texto placeholder para el campo de búsqueda
    """
    
    def __init__(
        self,
        on_search: Optional[Callable[[str], Any]] = None,
        on_filter_change: Optional[Callable[[ClientFilter], Any]] = None,
        on_sort_change: Optional[Callable[[ClientSort], Any]] = None,
        search_delay: int = 500,
        show_filters: bool = True,
        show_sort: bool = True,
        placeholder: str = "Buscar clientes...",
        **kwargs
    ):
        """
        Inicializa la barra de búsqueda.
        
        Args:
            on_search: Función callback para búsqueda
            on_filter_change: Función callback para filtros
            on_sort_change: Función callback para ordenamiento
            search_delay: Retraso para búsqueda en tiempo real (ms)
            show_filters: Si mostrar filtros avanzados
            show_sort: Si mostrar opciones de ordenamiento
            placeholder: Texto placeholder
            **kwargs: Argumentos adicionales para ft.Container
        """
        super().__init__(**kwargs)
        
        self.on_search = on_search
        self.on_filter_change = on_filter_change
        self.on_sort_change = on_sort_change
        self.search_delay = search_delay
        self.show_filters = show_filters
        self.show_sort = show_sort
        self.placeholder = placeholder
        
        self._logger = logger.bind(component="SearchBar")
        
        # Estado de la búsqueda
        self._current_query = ""
        self._search_mode = SearchMode.SIMPLE
        self._is_searching = False
        self._search_timer = None
        self._filters_expanded = False
        
        # Historial de búsquedas (últimas 10)
        self._search_history: List[str] = []
        
        # Referencias a elementos de UI
        self._search_field = ft.Ref[ft.TextField]()
        self._search_button = ft.Ref[ft.IconButton]()
        self._clear_button = ft.Ref[ft.IconButton]()
        self._progress_indicator = ft.Ref[ft.ProgressRing]()
        self._filters_panel = ft.Ref[ft.Container]()
        self._filters_toggle = ft.Ref[ft.IconButton]()
        
        # Referencias a filtros
        self._active_filter = ft.Ref[ft.Dropdown]()
        self._sort_field = ft.Ref[ft.Dropdown]()
        self._sort_direction = ft.Ref[ft.Dropdown]()
        self._date_from = ft.Ref[ft.TextField]()
        self._date_to = ft.Ref[ft.TextField]()
        
        # Configurar propiedades del contenedor
        self.padding = ft.padding.all(12)
        self.border_radius = ft.border_radius.all(8)
        self.bgcolor = ft.Colors.SURFACE
        self.border = ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
        
        # Construir la barra de búsqueda
        self._build_search_bar()
        
        self._logger.debug("SearchBar inicializada")
    
    def _build_search_bar(self):
        """Construye la estructura de la barra de búsqueda."""
        try:
            self.content = ft.Column([
                # Barra principal de búsqueda
                self._build_main_search_bar(),
                
                # Panel de filtros avanzados (colapsable)
                self._build_filters_panel() if self.show_filters else ft.Container(height=0)
            ], spacing=8)
            
        except Exception as e:
            self._logger.error(f"Error construyendo barra de búsqueda: {e}")
            self.content = self._build_error_content()
    
    def _build_main_search_bar(self) -> ft.Container:
        """Construye la barra principal de búsqueda."""
        return ft.Container(
            content=ft.Row([
                # Campo de búsqueda principal
                ft.TextField(
                    ref=self._search_field,
                    hint_text=self.placeholder,
                    prefix_icon=ft.Icons.SEARCH,
                    suffix=ft.Row([
                        # Indicador de progreso
                        ft.ProgressRing(
                            ref=self._progress_indicator,
                            width=16,
                            height=16,
                            stroke_width=2,
                            visible=False
                        ),
                        # Botón limpiar
                        ft.IconButton(
                            ref=self._clear_button,
                            icon=ft.Icons.CLEAR,
                            tooltip="Limpiar búsqueda",
                            on_click=lambda e: self._clear_search(),
                            visible=False
                        )
                    ], spacing=4, tight=True),
                    on_change=lambda e: self._handle_search_change(e.control.value),
                    on_submit=lambda e: self._handle_search_submit(e.control.value),
                    expand=True,
                    border_radius=ft.border_radius.all(8)
                ),
                
                # Botón de búsqueda manual
                ft.IconButton(
                    ref=self._search_button,
                    icon=ft.Icons.SEARCH,
                    tooltip="Buscar",
                    on_click=lambda e: self._handle_search_submit(self._search_field.current.value),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY
                    )
                ),
                
                # Botón de filtros (si están habilitados)
                ft.IconButton(
                    ref=self._filters_toggle,
                    icon=ft.Icons.FILTER_LIST,
                    tooltip="Filtros avanzados",
                    on_click=lambda e: self._toggle_filters(),
                    selected=self._filters_expanded
                ) if self.show_filters else ft.Container(width=0),
                
                # Opciones de ordenamiento rápido (si están habilitadas)
                self._build_quick_sort() if self.show_sort else ft.Container(width=0)
            ], spacing=8)
        )
    
    def _build_quick_sort(self) -> ft.PopupMenuButton:
        """Construye el menú de ordenamiento rápido."""
        return ft.PopupMenuButton(
            icon=ft.Icons.SORT,
            tooltip="Ordenar",
            items=[
                ft.PopupMenuItem(
                    text="Nombre A-Z",
                    icon=ft.Icons.SORT_BY_ALPHA,
                    on_click=lambda e: self._handle_quick_sort("name", SortDirection.ASC)
                ),
                ft.PopupMenuItem(
                    text="Nombre Z-A",
                    icon=ft.Icons.SORT_BY_ALPHA,
                    on_click=lambda e: self._handle_quick_sort("name", SortDirection.DESC)
                ),
                ft.PopupMenuItem(
                    text="Código A-Z",
                    icon=ft.Icons.TAG,
                    on_click=lambda e: self._handle_quick_sort("code", SortDirection.ASC)
                ),
                ft.PopupMenuItem(
                    text="Más recientes",
                    icon=ft.Icons.ACCESS_TIME,
                    on_click=lambda e: self._handle_quick_sort("created_at", SortDirection.DESC)
                ),
                ft.PopupMenuItem(
                    text="Más antiguos",
                    icon=ft.Icons.ACCESS_TIME,
                    on_click=lambda e: self._handle_quick_sort("created_at", SortDirection.ASC)
                )
            ]
        )
    
    def _build_filters_panel(self) -> ft.Container:
        """Construye el panel de filtros avanzados."""
        return ft.Container(
            ref=self._filters_panel,
            content=ft.Column([
                ft.Divider(height=1),
                
                ft.Text(
                    "Filtros Avanzados",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PRIMARY
                ),
                
                # Primera fila de filtros
                ft.Row([
                    # Filtro por estado
                    ft.Dropdown(
                        ref=self._active_filter,
                        label="Estado",
                        hint_text="Todos los estados",
                        options=[
                            ft.dropdown.Option("all", "Todos"),
                            ft.dropdown.Option("true", "Activos"),
                            ft.dropdown.Option("false", "Inactivos")
                        ],
                        value="all",
                        on_change=lambda e: self._handle_filter_change(),
                        width=150
                    ),
                    
                    # Filtro por campo de ordenamiento
                    ft.Dropdown(
                        ref=self._sort_field,
                        label="Ordenar por",
                        hint_text="Campo",
                        options=[
                            ft.dropdown.Option("name", "Nombre"),
                            ft.dropdown.Option("code", "Código"),
                            ft.dropdown.Option("created_at", "Fecha creación"),
                            ft.dropdown.Option("updated_at", "Fecha modificación")
                        ],
                        value="name",
                        on_change=lambda e: self._handle_sort_change(),
                        width=150
                    ),
                    
                    # Dirección de ordenamiento
                    ft.Dropdown(
                        ref=self._sort_direction,
                        label="Dirección",
                        hint_text="Orden",
                        options=[
                            ft.dropdown.Option("asc", "Ascendente"),
                            ft.dropdown.Option("desc", "Descendente")
                        ],
                        value="asc",
                        on_change=lambda e: self._handle_sort_change(),
                        width=130
                    )
                ], spacing=12),
                
                # Segunda fila de filtros (fechas)
                ft.Row([
                    ft.TextField(
                        ref=self._date_from,
                        label="Desde",
                        hint_text="dd/mm/yyyy",
                        prefix_icon=ft.Icons.DATE_RANGE,
                        on_change=lambda e: self._handle_filter_change(),
                        width=150
                    ),
                    
                    ft.TextField(
                        ref=self._date_to,
                        label="Hasta",
                        hint_text="dd/mm/yyyy",
                        prefix_icon=ft.Icons.DATE_RANGE,
                        on_change=lambda e: self._handle_filter_change(),
                        width=150
                    ),
                    
                    # Botones de acción para filtros
                    ft.TextButton(
                        text="Limpiar filtros",
                        icon=ft.Icons.CLEAR_ALL,
                        on_click=lambda e: self._clear_filters()
                    )
                ], spacing=12)
            ], spacing=12),
            visible=self._filters_expanded,
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.SURFACE,
            border_radius=ft.border_radius.all(8)
        )
    
    def _build_error_content(self) -> ft.Container:
        """Construye contenido de error cuando falla la construcción."""
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED),
                ft.Text(
                    "Error cargando barra de búsqueda",
                    color=ft.Colors.RED
                )
            ], spacing=8),
            padding=ft.padding.all(12)
        )
    
    # ==================== EVENT HANDLERS ====================
    
    def _handle_search_change(self, query: str):
        """Maneja cambios en el campo de búsqueda (búsqueda en tiempo real)."""
        try:
            self._current_query = query
            
            # Mostrar/ocultar botón limpiar
            if self._clear_button.current:
                self._clear_button.current.visible = bool(query.strip())
                self._clear_button.current.update()
            
            # Cancelar timer anterior si existe
            if self._search_timer:
                self._search_timer.cancel()
            
            # Configurar nuevo timer para búsqueda retrasada
            if query.strip():
                self._search_timer = asyncio.get_event_loop().call_later(
                    self.search_delay / 1000.0,
                    lambda: self._execute_search(query)
                )
            else:
                # Si la query está vacía, ejecutar búsqueda inmediatamente
                self._execute_search(query)
                
        except Exception as e:
            self._logger.error(f"Error manejando cambio de búsqueda: {e}")
    
    def _handle_search_submit(self, query: str):
        """Maneja el envío manual de búsqueda."""
        try:
            # Cancelar timer si existe
            if self._search_timer:
                self._search_timer.cancel()
                self._search_timer = None
            
            # Ejecutar búsqueda inmediatamente
            self._execute_search(query)
            
        except Exception as e:
            self._logger.error(f"Error manejando envío de búsqueda: {e}")
    
    def _handle_filter_change(self):
        """Maneja cambios en los filtros."""
        try:
            if self.on_filter_change:
                filters = self._collect_filters()
                self.on_filter_change(filters)
                self._logger.debug("Filtros actualizados")
                
        except Exception as e:
            self._logger.error(f"Error manejando cambio de filtros: {e}")
    
    def _handle_sort_change(self):
        """Maneja cambios en el ordenamiento."""
        try:
            if self.on_sort_change:
                sort_config = self._collect_sort_config()
                self.on_sort_change(sort_config)
                self._logger.debug("Ordenamiento actualizado")
                
        except Exception as e:
            self._logger.error(f"Error manejando cambio de ordenamiento: {e}")
    
    def _handle_quick_sort(self, field: str, direction: SortDirection):
        """Maneja ordenamiento rápido."""
        try:
            # Actualizar dropdowns si están disponibles
            if self._sort_field.current:
                self._sort_field.current.value = field
                self._sort_field.current.update()
            
            if self._sort_direction.current:
                self._sort_direction.current.value = direction.value
                self._sort_direction.current.update()
            
            # Ejecutar cambio de ordenamiento
            self._handle_sort_change()
            
        except Exception as e:
            self._logger.error(f"Error manejando ordenamiento rápido: {e}")
    
    # ==================== UTILITY METHODS ====================
    
    def _execute_search(self, query: str):
        """Ejecuta la búsqueda."""
        try:
            # Mostrar indicador de carga
            self._set_searching_state(True)
            
            # Agregar al historial si no está vacía
            if query.strip() and query not in self._search_history:
                self._search_history.insert(0, query)
                # Mantener solo las últimas 10 búsquedas
                self._search_history = self._search_history[:10]
            
            # Ejecutar callback de búsqueda
            if self.on_search:
                self.on_search(query)
            
            self._logger.debug(f"Búsqueda ejecutada: '{query}'")
            
            # Ocultar indicador de carga después de un breve delay
            asyncio.get_event_loop().call_later(
                0.5,
                lambda: self._set_searching_state(False)
            )
            
        except Exception as e:
            self._logger.error(f"Error ejecutando búsqueda: {e}")
            self._set_searching_state(False)
    
    def _collect_filters(self) -> ClientFilter:
        """Recopila la configuración actual de filtros."""
        try:
            # Estado activo
            active_value = self._active_filter.current.value if self._active_filter.current else "all"
            is_active = None
            if active_value == "true":
                is_active = True
            elif active_value == "false":
                is_active = False
            
            # Fechas (implementación básica, se puede mejorar con validación)
            date_from = None
            date_to = None
            
            if self._date_from.current and self._date_from.current.value:
                try:
                    date_from = datetime.strptime(self._date_from.current.value, "%d/%m/%Y")
                except ValueError:
                    pass
            
            if self._date_to.current and self._date_to.current.value:
                try:
                    date_to = datetime.strptime(self._date_to.current.value, "%d/%m/%Y")
                except ValueError:
                    pass
            
            return ClientFilter(
                is_active=is_active,
                created_from=date_from,
                created_to=date_to,
                search_query=self._current_query if self._current_query.strip() else None
            )
            
        except Exception as e:
            self._logger.error(f"Error recopilando filtros: {e}")
            return ClientFilter()
    
    def _collect_sort_config(self) -> ClientSort:
        """Recopila la configuración actual de ordenamiento."""
        try:
            field = self._sort_field.current.value if self._sort_field.current else "name"
            direction = self._sort_direction.current.value if self._sort_direction.current else "asc"
            
            return ClientSort(
                field=field,
                direction=direction
            )
            
        except Exception as e:
            self._logger.error(f"Error recopilando configuración de ordenamiento: {e}")
            return ClientSort(field="name", direction="asc")
    
    def _set_searching_state(self, searching: bool):
        """Establece el estado de búsqueda."""
        try:
            self._is_searching = searching
            
            if self._progress_indicator.current:
                self._progress_indicator.current.visible = searching
                self._progress_indicator.current.update()
                
        except Exception as e:
            self._logger.error(f"Error estableciendo estado de búsqueda: {e}")
    
    def _toggle_filters(self):
        """Alterna la visibilidad del panel de filtros."""
        try:
            self._filters_expanded = not self._filters_expanded
            
            if self._filters_panel.current:
                self._filters_panel.current.visible = self._filters_expanded
                self._filters_panel.current.update()
            
            if self._filters_toggle.current:
                self._filters_toggle.current.selected = self._filters_expanded
                self._filters_toggle.current.update()
                
        except Exception as e:
            self._logger.error(f"Error alternando filtros: {e}")
    
    def _clear_search(self):
        """Limpia la búsqueda actual."""
        try:
            if self._search_field.current:
                self._search_field.current.value = ""
                self._search_field.current.update()
            
            self._current_query = ""
            
            if self._clear_button.current:
                self._clear_button.current.visible = False
                self._clear_button.current.update()
            
            # Ejecutar búsqueda vacía
            self._execute_search("")
            
        except Exception as e:
            self._logger.error(f"Error limpiando búsqueda: {e}")
    
    def _clear_filters(self):
        """Limpia todos los filtros."""
        try:
            # Resetear dropdowns
            if self._active_filter.current:
                self._active_filter.current.value = "all"
                self._active_filter.current.update()
            
            if self._sort_field.current:
                self._sort_field.current.value = "name"
                self._sort_field.current.update()
            
            if self._sort_direction.current:
                self._sort_direction.current.value = "asc"
                self._sort_direction.current.update()
            
            # Limpiar campos de fecha
            if self._date_from.current:
                self._date_from.current.value = ""
                self._date_from.current.update()
            
            if self._date_to.current:
                self._date_to.current.value = ""
                self._date_to.current.update()
            
            # Ejecutar cambios
            self._handle_filter_change()
            self._handle_sort_change()
            
        except Exception as e:
            self._logger.error(f"Error limpiando filtros: {e}")
    
    # ==================== PUBLIC METHODS ====================
    
    def set_search_query(self, query: str):
        """
        Establece la consulta de búsqueda programáticamente.
        
        Args:
            query: Consulta de búsqueda
        """
        try:
            if self._search_field.current:
                self._search_field.current.value = query
                self._search_field.current.update()
            
            self._current_query = query
            self._execute_search(query)
            
        except Exception as e:
            self._logger.error(f"Error estableciendo consulta de búsqueda: {e}")
    
    def get_current_query(self) -> str:
        """
        Obtiene la consulta de búsqueda actual.
        
        Returns:
            Consulta de búsqueda actual
        """
        return self._current_query
    
    def get_current_filters(self) -> ClientFilter:
        """
        Obtiene los filtros actuales.
        
        Returns:
            Configuración actual de filtros
        """
        return self._collect_filters()
    
    def get_current_sort(self) -> ClientSort:
        """
        Obtiene la configuración de ordenamiento actual.
        
        Returns:
            Configuración actual de ordenamiento
        """
        return self._collect_sort_config()
    
    def get_search_history(self) -> List[str]:
        """
        Obtiene el historial de búsquedas.
        
        Returns:
            Lista con el historial de búsquedas
        """
        return self._search_history.copy()
    
    def clear_search_history(self):
        """Limpia el historial de búsquedas."""
        self._search_history.clear()
        self._logger.debug("Historial de búsquedas limpiado")
    
    def set_filters_expanded(self, expanded: bool):
        """
        Establece el estado de expansión de los filtros.
        
        Args:
            expanded: Si los filtros deben estar expandidos
        """
        try:
            if self._filters_expanded != expanded:
                self._toggle_filters()
        except Exception as e:
            self._logger.error(f"Error estableciendo estado de filtros: {e}")
    
    def focus_search_field(self):
        """Enfoca el campo de búsqueda."""
        try:
            if self._search_field.current:
                self._search_field.current.focus()
        except Exception as e:
            self._logger.error(f"Error enfocando campo de búsqueda: {e}")
