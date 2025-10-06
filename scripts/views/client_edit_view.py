#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vista de Edición de Clientes para Flet
======================================

Vista especializada para editar clientes existentes con formulario pre-poblado,
validaciones en tiempo real y manejo de actualizaciones robusto.

Características:
- Formulario pre-poblado con datos existentes
- Validación en tiempo real
- Estados de carga y error
- Integración con ClientDomainService
- Navegación fluida
- Feedback visual
- Manejo de errores detallado
- Comparación de cambios
- Interfaz responsiva

Autor: FletArchitect
"""

from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

import flet as ft
from loguru import logger

# Importar componentes y servicios del proyecto
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from planificador.schemas.client import ClientUpdate, Client
from planificador.services.domain.client.client_domain_service import ClientDomainService

# Importar componentes locales
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.client_form import ClientForm


class ClientEditView(ft.Container):
    """
    Vista para editar clientes existentes.
    
    Esta vista proporciona una interfaz completa para editar clientes,
    incluyendo validación en tiempo real, manejo de errores,
    comparación de cambios y navegación fluida.
    
    Attributes:
        client_service: Servicio de dominio para clientes
        client: Cliente a editar
        on_client_updated: Callback cuando se actualiza un cliente exitosamente
        on_cancel: Callback cuando se cancela la edición
        show_navigation: Si mostrar controles de navegación
    """
    
    def __init__(
        self,
        client_service: ClientDomainService,
        client: Client,
        on_client_updated: Optional[callable] = None,
        on_cancel: Optional[callable] = None,
        show_navigation: bool = True,
        **kwargs
    ):
        """
        Inicializa la vista de edición de clientes.
        
        Args:
            client_service: Servicio de dominio para clientes
            client: Cliente a editar
            on_client_updated: Callback para cliente actualizado exitosamente
            on_cancel: Callback para cancelación
            show_navigation: Si mostrar controles de navegación
            **kwargs: Argumentos adicionales para ft.Container
        """
        super().__init__(**kwargs)
        
        self.client_service = client_service
        self.client = client
        self.on_client_updated = on_client_updated
        self.on_cancel = on_cancel
        self.show_navigation = show_navigation
        
        self._logger = logger.bind(component="ClientEditView", client_id=client.id)
        
        # Estado de la vista
        self._is_updating = False
        self._has_changes = False
        self._original_data: Dict[str, Any] = {}
        self._update_error: Optional[str] = None
        
        # Referencias a elementos de UI
        self._client_form = ft.Ref[ClientForm]()
        self._update_button = ft.Ref[ft.ElevatedButton]()
        self._cancel_button = ft.Ref[ft.OutlinedButton]()
        self._reset_button = ft.Ref[ft.TextButton]()
        self._error_banner = ft.Ref[ft.Banner]()
        self._success_banner = ft.Ref[ft.Banner]()
        self._changes_indicator = ft.Ref[ft.Container]()
        
        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = ft.padding.all(20)
        
        # Guardar datos originales
        self._store_original_data()
        
        # Construir la vista
        self._build_view()
        
        self._logger.debug(f"ClientEditView inicializada para cliente: {client.name}")
    
    def _store_original_data(self):
        """Almacena los datos originales del cliente."""
        try:
            self._original_data = {
                "name": self.client.name,
                "code": self.client.code,
                "email": self.client.email,
                "phone": self.client.phone,
                "address": self.client.address,
                "contact_person": self.client.contact_person,
                "notes": self.client.notes,
                "is_active": self.client.is_active
            }
        except Exception as e:
            self._logger.error(f"Error almacenando datos originales: {e}")
    
    def _build_view(self):
        """Construye la estructura de la vista."""
        try:
            self.content = ft.Column([
                # Encabezado
                self._build_header(),
                
                # Banners de notificación
                ft.Banner(
                    ref=self._error_banner,
                    bgcolor=ft.Colors.RED_100,
                    leading=ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED, size=40),
                    content=ft.Text(""),
                    actions=[
                        ft.TextButton("Cerrar", on_click=self._hide_error_banner)
                    ]
                ),
                
                ft.Banner(
                    ref=self._success_banner,
                    bgcolor=ft.Colors.GREEN_100,
                    leading=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=40),
                    content=ft.Text(""),
                    actions=[
                        ft.TextButton("Cerrar", on_click=self._hide_success_banner)
                    ]
                ),
                
                # Indicador de cambios
                ft.Container(
                    ref=self._changes_indicator,
                    content=self._build_changes_indicator(),
                    visible=False
                ),
                
                # Formulario principal
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                # Título del formulario
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.EDIT, size=24, color=ft.Colors.PRIMARY),
                                        ft.Text(
                                            "Editar Información del Cliente",
                                            size=18,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.PRIMARY
                                        )
                                    ], spacing=8),
                                    padding=ft.padding.only(bottom=16)
                                ),
                                
                                # Formulario de cliente
                                ClientForm(
                                    ref=self._client_form,
                                    mode="edit",
                                    client=self.client,
                                    on_submit=self._handle_form_submit,
                                    on_cancel=self._handle_form_cancel,
                                    on_change=self._handle_form_change,
                                    show_cancel_button=False  # Manejamos los botones aquí
                                )
                            ], spacing=16),
                            padding=ft.padding.all(24)
                        ),
                        elevation=2
                    ),
                    expand=True
                ),
                
                # Botones de acción
                self._build_action_buttons() if self.show_navigation else ft.Container()
                
            ], spacing=16, expand=True)
            
        except Exception as e:
            self._logger.error(f"Error construyendo vista: {e}")
            self.content = self._build_error_view()
    
    def _build_header(self) -> ft.Container:
        """Construye el encabezado de la vista."""
        return ft.Container(
            content=ft.Column([
                # Breadcrumb/navegación
                ft.Row([
                    ft.TextButton(
                        text="Clientes",
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self._handle_navigation_back(),
                        style=ft.ButtonStyle(
                            color=ft.Colors.PRIMARY
                        )
                    ),
                    ft.Text(" / ", color=ft.Colors.GREY_400),
                    ft.Text(f"{self.client.name}", color=ft.Colors.GREY_600),
                    ft.Text(" / ", color=ft.Colors.GREY_400),
                    ft.Text("Editar", color=ft.Colors.GREY_600)
                ], spacing=4) if self.show_navigation else ft.Container(),
                
                # Título principal
                ft.Row([
                    ft.Column([
                        ft.Text(
                            f"Editar Cliente: {self.client.name}",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.PRIMARY
                        ),
                        ft.Row([
                            ft.Text(
                                f"Código: {self.client.code}",
                                size=14,
                                color=ft.Colors.GREY_600
                            ),
                            ft.Text(" • ", color=ft.Colors.GREY_400),
                            ft.Text(
                                f"Creado: {self.client.created_at.strftime('%d/%m/%Y')}",
                                size=14,
                                color=ft.Colors.GREY_600
                            ),
                            ft.Text(" • ", color=ft.Colors.GREY_400),
                            ft.Container(
                                content=ft.Text(
                                    "Activo" if self.client.is_active else "Inactivo",
                                    size=12,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD
                                ),
                                bgcolor=ft.Colors.GREEN if self.client.is_active else ft.Colors.RED,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=ft.border_radius.all(12)
                            )
                        ], spacing=8)
                    ], spacing=8, expand=True),
                    
                    # Icono decorativo
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.EDIT_NOTE,
                            size=48,
                            color=ft.Colors.PRIMARY_CONTAINER
                        ),
                        bgcolor=ft.Colors.PRIMARY_CONTAINER,
                        border_radius=ft.border_radius.all(12),
                        padding=ft.padding.all(12)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=12),
            padding=ft.padding.only(bottom=20)
        )
    
    def _build_changes_indicator(self) -> ft.Container:
        """Construye el indicador de cambios."""
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.EDIT, color=ft.Colors.ORANGE, size=20),
                        ft.Text(
                            "Hay cambios sin guardar",
                            size=14,
                            color=ft.Colors.ORANGE_700,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.TextButton(
                            ref=self._reset_button,
                            text="Deshacer cambios",
                            icon=ft.Icons.UNDO,
                            on_click=self._handle_reset_clicked,
                            style=ft.ButtonStyle(
                                color=ft.Colors.ORANGE_700
                            )
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.all(12)
                ),
                color=ft.Colors.ORANGE_100,
                elevation=1
            ),
            margin=ft.margin.only(bottom=16)
        )
    
    def _build_action_buttons(self) -> ft.Container:
        """Construye los botones de acción."""
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        # Información de ayuda
                        ft.Column([
                            ft.Text(
                                "💡 Información:",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700
                            ),
                            ft.Text(
                                f"• Cliente creado: {self.client.created_at.strftime('%d/%m/%Y %H:%M')}\n• Última modificación: {self.client.updated_at.strftime('%d/%m/%Y %H:%M') if self.client.updated_at else 'Nunca'}",
                                size=12,
                                color=ft.Colors.GREY_600
                            )
                        ], spacing=4, expand=True),
                        
                        # Botones
                        ft.Row([
                            ft.OutlinedButton(
                                ref=self._cancel_button,
                                text="Cancelar",
                                icon=ft.Icons.CANCEL,
                                on_click=self._handle_cancel_clicked,
                                disabled=self._is_updating
                            ),
                            ft.ElevatedButton(
                                ref=self._update_button,
                                text="Guardar Cambios" if not self._is_updating else "Guardando...",
                                icon=ft.Icons.SAVE if not self._is_updating else ft.Icons.HOURGLASS_EMPTY,
                                on_click=self._handle_update_clicked,
                                disabled=self._is_updating or not self._has_changes,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.PRIMARY,
                                    color=ft.Colors.ON_PRIMARY
                                )
                            )
                        ], spacing=12)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.all(16)
                ),
                elevation=1
            ),
            margin=ft.margin.only(top=16)
        )
    
    def _build_error_view(self) -> ft.Column:
        """Construye la vista de error general."""
        return ft.Column([
            ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED, size=48),
            ft.Text(
                "Error inicializando vista de edición",
                color=ft.Colors.RED,
                size=16,
                text_align=ft.TextAlign.CENTER
            )
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True)
    
    # ==================== EVENT HANDLERS ====================
    
    def _handle_form_submit(self, client_data: ClientUpdate):
        """Maneja el envío del formulario."""
        asyncio.create_task(self._update_client(client_data))
    
    def _handle_form_cancel(self):
        """Maneja la cancelación del formulario."""
        self._handle_cancel_clicked(None)
    
    def _handle_form_change(self, form_data: Dict[str, Any]):
        """Maneja cambios en el formulario."""
        try:
            # Verificar si hay cambios
            has_changes = self._detect_changes(form_data)
            
            if has_changes != self._has_changes:
                self._has_changes = has_changes
                self._update_changes_indicator()
                self._update_action_buttons()
                
        except Exception as e:
            self._logger.error(f"Error manejando cambios del formulario: {e}")
    
    def _handle_update_clicked(self, e):
        """Maneja el clic en el botón actualizar."""
        try:
            if self._client_form.current:
                self._client_form.current.submit_form()
        except Exception as ex:
            self._logger.error(f"Error manejando clic actualizar: {ex}")
            self._show_error_banner("Error procesando formulario")
    
    def _handle_cancel_clicked(self, e):
        """Maneja el clic en el botón cancelar."""
        try:
            if self._has_changes:
                # Mostrar confirmación si hay cambios
                self._show_cancel_confirmation()
            else:
                self._perform_cancel()
        except Exception as ex:
            self._logger.error(f"Error manejando cancelación: {ex}")
    
    def _handle_reset_clicked(self, e):
        """Maneja el clic en el botón resetear."""
        try:
            if self._client_form.current:
                self._client_form.current.set_initial_data(self._original_data)
                self._has_changes = False
                self._update_changes_indicator()
                self._update_action_buttons()
            self._logger.debug("Formulario reseteado a valores originales")
        except Exception as ex:
            self._logger.error(f"Error reseteando formulario: {ex}")
    
    def _handle_navigation_back(self):
        """Maneja la navegación hacia atrás."""
        try:
            if self._has_changes:
                self._show_cancel_confirmation()
            else:
                self._perform_cancel()
        except Exception as e:
            self._logger.error(f"Error navegando hacia atrás: {e}")
    
    # ==================== CLIENT UPDATE ====================
    
    async def _update_client(self, client_data: ClientUpdate):
        """
        Actualiza el cliente usando el servicio de dominio.
        
        Args:
            client_data: Datos actualizados del cliente
        """
        try:
            self._set_updating_state(True)
            self._hide_error_banner()
            self._hide_success_banner()
            
            self._logger.debug(f"Actualizando cliente: {self.client.name}")
            
            # Actualizar cliente usando el servicio de dominio
            updated_client = await self.client_service.update_client(
                client_id=self.client.id,
                client_data=client_data
            )
            
            # Actualizar cliente local
            self.client = updated_client
            self._store_original_data()
            self._has_changes = False
            
            # Mostrar mensaje de éxito
            self._show_success_banner(
                f"Cliente '{updated_client.name}' actualizado exitosamente"
            )
            
            # Actualizar UI
            self._update_changes_indicator()
            self._update_action_buttons()
            
            # Notificar éxito
            if self.on_client_updated:
                self.on_client_updated(updated_client)
            
            self._logger.info(f"Cliente actualizado exitosamente: {updated_client.name} (ID: {updated_client.id})")
            
        except Exception as e:
            error_message = str(e)
            self._logger.error(f"Error actualizando cliente: {error_message}")
            self._show_error_banner(f"Error actualizando cliente: {error_message}")
            
        finally:
            self._set_updating_state(False)
    
    def _set_updating_state(self, is_updating: bool):
        """
        Establece el estado de actualización y actualiza la UI.
        
        Args:
            is_updating: Si está en proceso de actualización
        """
        try:
            self._is_updating = is_updating
            
            # Actualizar botón actualizar
            if self._update_button.current:
                self._update_button.current.text = "Guardando..." if is_updating else "Guardar Cambios"
                self._update_button.current.icon = ft.Icons.HOURGLASS_EMPTY if is_updating else ft.Icons.SAVE
                self._update_button.current.disabled = is_updating or not self._has_changes
                self._update_button.current.update()
            
            # Actualizar botón cancelar
            if self._cancel_button.current:
                self._cancel_button.current.disabled = is_updating
                self._cancel_button.current.update()
            
            # Actualizar botón reset
            if self._reset_button.current:
                self._reset_button.current.disabled = is_updating
                self._reset_button.current.update()
            
            # Actualizar formulario
            if self._client_form.current:
                self._client_form.current.set_loading_state(is_updating)
                
        except Exception as e:
            self._logger.error(f"Error estableciendo estado de actualización: {e}")
    
    # ==================== CHANGE DETECTION ====================
    
    def _detect_changes(self, current_data: Dict[str, Any]) -> bool:
        """
        Detecta si hay cambios en los datos del formulario.
        
        Args:
            current_data: Datos actuales del formulario
            
        Returns:
            True si hay cambios
        """
        try:
            for key, original_value in self._original_data.items():
                current_value = current_data.get(key)
                
                # Normalizar valores para comparación
                if original_value != current_value:
                    # Manejar casos especiales (None vs "", etc.)
                    if (original_value is None and current_value == "") or \
                       (original_value == "" and current_value is None):
                        continue
                    return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Error detectando cambios: {e}")
            return False
    
    def _update_changes_indicator(self):
        """Actualiza el indicador de cambios."""
        try:
            if self._changes_indicator.current:
                self._changes_indicator.current.visible = self._has_changes
                self._changes_indicator.current.update()
        except Exception as e:
            self._logger.error(f"Error actualizando indicador de cambios: {e}")
    
    def _update_action_buttons(self):
        """Actualiza el estado de los botones de acción."""
        try:
            if self._update_button.current:
                self._update_button.current.disabled = self._is_updating or not self._has_changes
                self._update_button.current.update()
        except Exception as e:
            self._logger.error(f"Error actualizando botones de acción: {e}")
    
    # ==================== CONFIRMATION DIALOGS ====================
    
    def _show_cancel_confirmation(self):
        """Muestra diálogo de confirmación para cancelar."""
        # TODO: Implementar diálogo de confirmación
        # Por ahora, cancelar directamente
        self._perform_cancel()
    
    def _perform_cancel(self):
        """Realiza la cancelación."""
        try:
            if self.on_cancel:
                self.on_cancel()
            self._logger.debug("Cancelación realizada")
        except Exception as e:
            self._logger.error(f"Error realizando cancelación: {e}")
    
    # ==================== BANNER MANAGEMENT ====================
    
    def _show_error_banner(self, message: str):
        """
        Muestra el banner de error.
        
        Args:
            message: Mensaje de error a mostrar
        """
        try:
            if self._error_banner.current:
                self._error_banner.current.content.value = message
                self._error_banner.current.open = True
                self._error_banner.current.update()
        except Exception as e:
            self._logger.error(f"Error mostrando banner de error: {e}")
    
    def _hide_error_banner(self, e=None):
        """Oculta el banner de error."""
        try:
            if self._error_banner.current:
                self._error_banner.current.open = False
                self._error_banner.current.update()
        except Exception as ex:
            self._logger.error(f"Error ocultando banner de error: {ex}")
    
    def _show_success_banner(self, message: str):
        """
        Muestra el banner de éxito.
        
        Args:
            message: Mensaje de éxito a mostrar
        """
        try:
            if self._success_banner.current:
                self._success_banner.current.content.value = message
                self._success_banner.current.open = True
                self._success_banner.current.update()
        except Exception as e:
            self._logger.error(f"Error mostrando banner de éxito: {e}")
    
    def _hide_success_banner(self, e=None):
        """Oculta el banner de éxito."""
        try:
            if self._success_banner.current:
                self._success_banner.current.open = False
                self._success_banner.current.update()
        except Exception as ex:
            self._logger.error(f"Error ocultando banner de éxito: {ex}")
    
    # ==================== PUBLIC METHODS ====================
    
    def get_client(self) -> Client:
        """
        Obtiene el cliente actual.
        
        Returns:
            Cliente actual
        """
        return self.client
    
    def has_unsaved_changes(self) -> bool:
        """
        Verifica si hay cambios sin guardar.
        
        Returns:
            True si hay cambios sin guardar
        """
        return self._has_changes
    
    def get_updating_state(self) -> bool:
        """
        Obtiene el estado de actualización actual.
        
        Returns:
            True si está actualizando el cliente
        """
        return self._is_updating
    
    def refresh_client_data(self, updated_client: Client):
        """
        Refresca los datos del cliente.
        
        Args:
            updated_client: Cliente actualizado
        """
        try:
            self.client = updated_client
            self._store_original_data()
            self._has_changes = False
            
            if self._client_form.current:
                self._client_form.current.set_client_data(updated_client)
            
            self._update_changes_indicator()
            self._update_action_buttons()
            
            self._logger.debug("Datos del cliente refrescados")
        except Exception as e:
            self._logger.error(f"Error refrescando datos del cliente: {e}")
