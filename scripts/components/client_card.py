#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Componente ClientCard para Flet
==============================

Componente reutilizable que representa visualmente un cliente en forma de tarjeta,
siguiendo los principios de Material Design y las mejores prácticas de Flet.

Características:
- Diseño responsivo y moderno
- Información estructurada del cliente
- Acciones contextuales (ver, editar, eliminar)
- Estados visuales (activo/inactivo)
- Eventos personalizables
- Optimizado para rendimiento

Autor: FletArchitect
"""

from typing import Optional, Callable, Any
from datetime import datetime

import flet as ft
from loguru import logger

# Importar esquemas del proyecto
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from planificador.schemas.client import Client


class ClientCard(ft.Card):
    """
    Componente de tarjeta para mostrar información de un cliente.
    
    Esta clase encapsula la representación visual de un cliente en una tarjeta
    Material Design, proporcionando una interfaz consistente y reutilizable.
    
    Attributes:
        client: Datos del cliente a mostrar
        on_view: Callback para ver detalles del cliente
        on_edit: Callback para editar el cliente
        on_delete: Callback para eliminar el cliente
        show_actions: Si mostrar o no las acciones contextuales
        compact_mode: Si usar modo compacto (menos información)
    """
    
    def __init__(
        self,
        client: Client,
        on_view: Optional[Callable[[Client], Any]] = None,
        on_edit: Optional[Callable[[Client], Any]] = None,
        on_delete: Optional[Callable[[Client], Any]] = None,
        show_actions: bool = True,
        compact_mode: bool = False,
        **kwargs
    ):
        """
        Inicializa la tarjeta de cliente.
        
        Args:
            client: Datos del cliente a mostrar
            on_view: Función callback para ver detalles
            on_edit: Función callback para editar
            on_delete: Función callback para eliminar
            show_actions: Si mostrar acciones contextuales
            compact_mode: Si usar diseño compacto
            **kwargs: Argumentos adicionales para ft.Card
        """
        super().__init__(**kwargs)
        
        self.client = client
        self.on_view = on_view
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.show_actions = show_actions
        self.compact_mode = compact_mode
        
        self._logger = logger.bind(component="ClientCard", client_id=client.id)
        
        # Configurar propiedades de la tarjeta
        self.elevation = 2
        self.margin = ft.margin.all(4)
        
        # Construir el contenido de la tarjeta
        self._build_content()
        
        self._logger.debug(f"ClientCard creada para cliente: {client.name}")
    
    def _build_content(self):
        """Construye el contenido visual de la tarjeta."""
        try:
            if self.compact_mode:
                self.content = self._build_compact_content()
            else:
                self.content = self._build_full_content()
                
        except Exception as e:
            self._logger.error(f"Error construyendo contenido de tarjeta: {e}")
            self.content = self._build_error_content()
    
    def _build_full_content(self) -> ft.Container:
        """Construye el contenido completo de la tarjeta."""
        return ft.Container(
            content=ft.Column([
                # Encabezado principal
                self._build_header(),
                
                # Información de contacto
                self._build_contact_info(),
                
                # Información adicional
                self._build_additional_info(),
                
                # Acciones (si están habilitadas)
                self._build_actions() if self.show_actions else ft.Container(height=0)
            ], 
            spacing=8,
            tight=True),
            padding=ft.padding.all(16)
        )
    
    def _build_compact_content(self) -> ft.Container:
        """Construye el contenido compacto de la tarjeta."""
        return ft.Container(
            content=ft.Row([
                # Avatar y información básica
                self._build_avatar(),
                ft.Container(width=12),
                ft.Column([
                    ft.Text(
                        self.client.name,
                        weight=ft.FontWeight.BOLD,
                        size=14,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    ft.Text(
                        f"Código: {self.client.code}",
                        size=12,
                        color=ft.Colors.GREY_600,
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ], 
                spacing=2,
                expand=True),
                
                # Estado y acciones compactas
                self._build_status_chip(),
                self._build_compact_actions() if self.show_actions else ft.Container()
            ], 
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.all(12)
        )
    
    def _build_header(self) -> ft.Container:
        """Construye el encabezado de la tarjeta."""
        return ft.Container(
            content=ft.Row([
                # Avatar del cliente
                self._build_avatar(),
                
                ft.Container(width=16),
                
                # Información principal
                ft.Column([
                    ft.Text(
                        self.client.name,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        overflow=ft.TextOverflow.ELLIPSIS
                    ),
                    ft.Text(
                        f"Código: {self.client.code}",
                        size=14,
                        color=ft.Colors.GREY_600,
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                ], 
                spacing=4,
                expand=True),
                
                # Estado del cliente
                self._build_status_chip()
            ], 
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
    
    def _build_avatar(self) -> ft.CircleAvatar:
        """Construye el avatar del cliente."""
        # Obtener iniciales del nombre
        initials = self._get_client_initials()
        
        # Color basado en el estado del cliente
        bgcolor = ft.Colors.BLUE if self.client.is_active else ft.Colors.GREY
        
        return ft.CircleAvatar(
            content=ft.Text(
                initials,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
                size=16 if not self.compact_mode else 14
            ),
            bgcolor=bgcolor,
            radius=24 if not self.compact_mode else 20
        )
    
    def _build_contact_info(self) -> ft.Container:
        """Construye la información de contacto."""
        contact_items = []
        
        # Email
        if self.client.email:
            contact_items.append(
                ft.Row([
                    ft.Icon(ft.Icons.EMAIL, size=16, color=ft.Colors.GREY_600),
                    ft.Container(width=8),
                    ft.Text(
                        self.client.email,
                        size=13,
                        color=ft.Colors.GREY_700,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True
                    )
                ])
            )
        
        # Teléfono
        if self.client.phone:
            contact_items.append(
                ft.Row([
                    ft.Icon(ft.Icons.PHONE, size=16, color=ft.Colors.GREY_600),
                    ft.Container(width=8),
                    ft.Text(
                        self.client.phone,
                        size=13,
                        color=ft.Colors.GREY_700,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True
                    )
                ])
            )
        
        # Persona de contacto
        if self.client.contact_person:
            contact_items.append(
                ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=16, color=ft.Colors.GREY_600),
                    ft.Container(width=8),
                    ft.Text(
                        self.client.contact_person,
                        size=13,
                        color=ft.Colors.GREY_700,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True
                    )
                ])
            )
        
        if not contact_items:
            contact_items.append(
                ft.Text(
                    "Sin información de contacto",
                    size=12,
                    color=ft.Colors.GREY_500,
                    italic=True
                )
            )
        
        return ft.Container(
            content=ft.Column(contact_items, spacing=6),
            padding=ft.padding.symmetric(vertical=8)
        )
    
    def _build_additional_info(self) -> ft.Container:
        """Construye información adicional del cliente."""
        info_items = []
        
        # Fecha de creación
        created_date = self._format_date(self.client.created_at)
        info_items.append(
            ft.Row([
                ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=ft.Colors.GREY_500),
                ft.Container(width=6),
                ft.Text(
                    f"Creado: {created_date}",
                    size=11,
                    color=ft.Colors.GREY_500
                )
            ])
        )
        
        # Notas (si existen)
        if self.client.notes:
            notes_preview = self.client.notes[:50] + "..." if len(self.client.notes) > 50 else self.client.notes
            info_items.append(
                ft.Row([
                    ft.Icon(ft.Icons.NOTE, size=14, color=ft.Colors.GREY_500),
                    ft.Container(width=6),
                    ft.Text(
                        notes_preview,
                        size=11,
                        color=ft.Colors.GREY_500,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True
                    )
                ])
            )
        
        return ft.Container(
            content=ft.Column(info_items, spacing=4),
            padding=ft.padding.symmetric(vertical=4)
        )
    
    def _build_status_chip(self) -> ft.Chip:
        """Construye el chip de estado del cliente."""
        if self.client.is_active:
            return ft.Chip(
                label=ft.Text("Activo", size=10, color=ft.Colors.GREEN_800),
                bgcolor=ft.Colors.GREEN_100,
                leading=ft.Icon(ft.Icons.CHECK_CIRCLE, size=16, color=ft.Colors.GREEN_600)
            )
        else:
            return ft.Chip(
                label=ft.Text("Inactivo", size=10, color=ft.Colors.RED_800),
                bgcolor=ft.Colors.RED_100,
                leading=ft.Icon(ft.Icons.CANCEL, size=16, color=ft.Colors.RED_600)
            )
    
    def _build_actions(self) -> ft.Container:
        """Construye las acciones de la tarjeta."""
        actions = []
        
        if self.on_view:
            actions.append(
                ft.TextButton(
                    text="Ver",
                    icon=ft.Icons.VISIBILITY,
                    on_click=lambda e: self._handle_view()
                )
            )
        
        if self.on_edit:
            actions.append(
                ft.TextButton(
                    text="Editar",
                    icon=ft.Icons.EDIT,
                    on_click=lambda e: self._handle_edit()
                )
            )
        
        if self.on_delete:
            actions.append(
                ft.TextButton(
                    text="Eliminar",
                    icon=ft.Icons.DELETE,
                    style=ft.ButtonStyle(color=ft.Colors.RED),
                    on_click=lambda e: self._handle_delete()
                )
            )
        
        if not actions:
            return ft.Container(height=0)
        
        return ft.Container(
            content=ft.Row(
                actions,
                alignment=ft.MainAxisAlignment.END,
                spacing=8
            ),
            padding=ft.padding.only(top=12)
        )
    
    def _build_compact_actions(self) -> ft.PopupMenuButton:
        """Construye las acciones compactas (menú popup)."""
        menu_items = []
        
        if self.on_view:
            menu_items.append(
                ft.PopupMenuItem(
                    text="Ver detalles",
                    icon=ft.Icons.VISIBILITY,
                    on_click=lambda e: self._handle_view()
                )
            )
        
        if self.on_edit:
            menu_items.append(
                ft.PopupMenuItem(
                    text="Editar",
                    icon=ft.Icons.EDIT,
                    on_click=lambda e: self._handle_edit()
                )
            )
        
        if self.on_delete:
            menu_items.append(
                ft.PopupMenuItem(
                    text="Eliminar",
                    icon=ft.Icons.DELETE,
                    on_click=lambda e: self._handle_delete()
                )
            )
        
        if not menu_items:
            return ft.Container()
        
        return ft.PopupMenuButton(
            items=menu_items,
            icon=ft.Icons.MORE_VERT,
            tooltip="Más acciones"
        )
    
    def _build_error_content(self) -> ft.Container:
        """Construye contenido de error cuando falla la construcción."""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED, size=32),
                ft.Text(
                    "Error cargando cliente",
                    color=ft.Colors.RED,
                    text_align=ft.TextAlign.CENTER
                )
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(20),
            alignment=ft.alignment.center
        )
    
    # ==================== UTILITY METHODS ====================
    
    def _get_client_initials(self) -> str:
        """Obtiene las iniciales del nombre del cliente."""
        try:
            words = self.client.name.strip().split()
            if len(words) >= 2:
                return f"{words[0][0]}{words[1][0]}".upper()
            elif len(words) == 1:
                return words[0][:2].upper()
            else:
                return "CL"
        except (IndexError, AttributeError):
            return "CL"
    
    def _format_date(self, date: datetime) -> str:
        """Formatea una fecha para mostrar."""
        try:
            return date.strftime("%d/%m/%Y")
        except (AttributeError, ValueError):
            return "Fecha no disponible"
    
    # ==================== EVENT HANDLERS ====================
    
    def _handle_view(self):
        """Maneja el evento de ver detalles."""
        try:
            if self.on_view:
                self.on_view(self.client)
                self._logger.debug(f"Vista de cliente solicitada: {self.client.name}")
        except Exception as e:
            self._logger.error(f"Error manejando vista de cliente: {e}")
    
    def _handle_edit(self):
        """Maneja el evento de editar cliente."""
        try:
            if self.on_edit:
                self.on_edit(self.client)
                self._logger.debug(f"Edición de cliente solicitada: {self.client.name}")
        except Exception as e:
            self._logger.error(f"Error manejando edición de cliente: {e}")
    
    def _handle_delete(self):
        """Maneja el evento de eliminar cliente."""
        try:
            if self.on_delete:
                self.on_delete(self.client)
                self._logger.debug(f"Eliminación de cliente solicitada: {self.client.name}")
        except Exception as e:
            self._logger.error(f"Error manejando eliminación de cliente: {e}")
    
    # ==================== PUBLIC METHODS ====================
    
    def update_client(self, client: Client):
        """
        Actualiza los datos del cliente y reconstruye la tarjeta.
        
        Args:
            client: Nuevos datos del cliente
        """
        try:
            self.client = client
            self._build_content()
            self.update()
            self._logger.debug(f"Cliente actualizado: {client.name}")
        except Exception as e:
            self._logger.error(f"Error actualizando cliente: {e}")
    
    def set_callbacks(
        self,
        on_view: Optional[Callable[[Client], Any]] = None,
        on_edit: Optional[Callable[[Client], Any]] = None,
        on_delete: Optional[Callable[[Client], Any]] = None
    ):
        """
        Actualiza los callbacks de la tarjeta.
        
        Args:
            on_view: Nuevo callback para ver
            on_edit: Nuevo callback para editar
            on_delete: Nuevo callback para eliminar
        """
        if on_view is not None:
            self.on_view = on_view
        if on_edit is not None:
            self.on_edit = on_edit
        if on_delete is not None:
            self.on_delete = on_delete
        
        # Reconstruir contenido para actualizar acciones
        self._build_content()
        self.update()
