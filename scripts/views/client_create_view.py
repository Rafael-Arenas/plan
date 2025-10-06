#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vista de Creación de Clientes para Flet
=======================================

Vista especializada para crear nuevos clientes con formulario completo,
validaciones en tiempo real y manejo de errores robusto.

Características:
- Formulario completo de cliente
- Validación en tiempo real
- Estados de carga y error
- Integración con ClientDomainService
- Navegación fluida
- Feedback visual
- Manejo de errores detallado
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

from planificador.schemas.client import ClientCreate, Client
from planificador.services.domain.client.client_domain_service import ClientDomainService

# Importar componentes locales
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.client_form import ClientForm


class ClientCreateView(ft.Container):
    """
    Vista para crear nuevos clientes.
    
    Esta vista proporciona una interfaz completa para crear clientes,
    incluyendo validación en tiempo real, manejo de errores y
    navegación fluida.
    
    Attributes:
        client_service: Servicio de dominio para clientes
        on_client_created: Callback cuando se crea un cliente exitosamente
        on_cancel: Callback cuando se cancela la creación
        show_navigation: Si mostrar controles de navegación
    """
    
    def __init__(
        self,
        client_service: ClientDomainService,
        on_client_created: Optional[callable] = None,
        on_cancel: Optional[callable] = None,
        show_navigation: bool = True,
        **kwargs
    ):
        """
        Inicializa la vista de creación de clientes.
        
        Args:
            client_service: Servicio de dominio para clientes
            on_client_created: Callback para cliente creado exitosamente
            on_cancel: Callback para cancelación
            show_navigation: Si mostrar controles de navegación
            **kwargs: Argumentos adicionales para ft.Container
        """
        super().__init__(**kwargs)
        
        self.client_service = client_service
        self.on_client_created = on_client_created
        self.on_cancel = on_cancel
        self.show_navigation = show_navigation
        
        self._logger = logger.bind(component="ClientCreateView")
        
        # Estado de la vista
        self._is_creating = False
        self._creation_error: Optional[str] = None
        
        # Referencias a elementos de UI
        self._client_form = ft.Ref[ClientForm]()
        self._create_button = ft.Ref[ft.ElevatedButton]()
        self._cancel_button = ft.Ref[ft.OutlinedButton]()
        self._error_banner = ft.Ref[ft.Banner]()
        self._success_banner = ft.Ref[ft.Banner]()
        
        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = ft.padding.all(20)
        
        # Construir la vista
        self._build_view()
        
        self._logger.debug("ClientCreateView inicializada")
    
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
                
                # Formulario principal
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                # Título del formulario
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.PERSON_ADD, size=24, color=ft.Colors.PRIMARY),
                                        ft.Text(
                                            "Información del Cliente",
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
                                    mode="create",
                                    on_submit=self._handle_form_submit,
                                    on_cancel=self._handle_form_cancel,
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
                    ft.Text("Nuevo Cliente", color=ft.Colors.GREY_600)
                ], spacing=4) if self.show_navigation else ft.Container(),
                
                # Título principal
                ft.Row([
                    ft.Column([
                        ft.Text(
                            "Crear Nuevo Cliente",
                            size=32,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.PRIMARY
                        ),
                        ft.Text(
                            "Complete la información para registrar un nuevo cliente en el sistema",
                            size=16,
                            color=ft.Colors.GREY_600
                        )
                    ], spacing=8, expand=True),
                    
                    # Icono decorativo
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.PERSON_ADD_ALT_1,
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
    
    def _build_action_buttons(self) -> ft.Container:
        """Construye los botones de acción."""
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        # Información de ayuda
                        ft.Column([
                            ft.Text(
                                "💡 Consejos:",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700
                            ),
                            ft.Text(
                                "• El código del cliente debe ser único\n• El email es opcional pero recomendado\n• Puede editar la información después",
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
                                disabled=self._is_creating
                            ),
                            ft.ElevatedButton(
                                ref=self._create_button,
                                text="Crear Cliente" if not self._is_creating else "Creando...",
                                icon=ft.Icons.SAVE if not self._is_creating else ft.Icons.HOURGLASS_EMPTY,
                                on_click=self._handle_create_clicked,
                                disabled=self._is_creating,
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
                "Error inicializando vista de creación",
                color=ft.Colors.RED,
                size=16,
                text_align=ft.TextAlign.CENTER
            )
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True)
    
    # ==================== EVENT HANDLERS ====================
    
    def _handle_form_submit(self, client_data: ClientCreate):
        """Maneja el envío del formulario."""
        asyncio.create_task(self._create_client(client_data))
    
    def _handle_form_cancel(self):
        """Maneja la cancelación del formulario."""
        self._handle_cancel_clicked(None)
    
    def _handle_create_clicked(self, e):
        """Maneja el clic en el botón crear."""
        try:
            if self._client_form.current:
                self._client_form.current.submit_form()
        except Exception as ex:
            self._logger.error(f"Error manejando clic crear: {ex}")
            self._show_error_banner("Error procesando formulario")
    
    def _handle_cancel_clicked(self, e):
        """Maneja el clic en el botón cancelar."""
        try:
            if self.on_cancel:
                self.on_cancel()
            else:
                self._handle_navigation_back()
        except Exception as ex:
            self._logger.error(f"Error manejando cancelación: {ex}")
    
    def _handle_navigation_back(self):
        """Maneja la navegación hacia atrás."""
        try:
            if self.on_cancel:
                self.on_cancel()
            self._logger.debug("Navegación hacia atrás solicitada")
        except Exception as e:
            self._logger.error(f"Error navegando hacia atrás: {e}")
    
    # ==================== CLIENT CREATION ====================
    
    async def _create_client(self, client_data: ClientCreate):
        """
        Crea un nuevo cliente usando el servicio de dominio.
        
        Args:
            client_data: Datos del cliente a crear
        """
        try:
            self._set_creating_state(True)
            self._hide_error_banner()
            self._hide_success_banner()
            
            self._logger.debug(f"Creando cliente: {client_data.name}")
            
            # Crear cliente usando el servicio de dominio
            created_client = await self.client_service.create_client(client_data)
            
            # Mostrar mensaje de éxito
            self._show_success_banner(
                f"Cliente '{created_client.name}' creado exitosamente"
            )
            
            # Notificar éxito
            if self.on_client_created:
                self.on_client_created(created_client)
            
            # Limpiar formulario después de un breve delay
            await asyncio.sleep(1.5)
            if self._client_form.current:
                self._client_form.current.clear_form()
            
            self._logger.info(f"Cliente creado exitosamente: {created_client.name} (ID: {created_client.id})")
            
        except Exception as e:
            error_message = str(e)
            self._logger.error(f"Error creando cliente: {error_message}")
            self._show_error_banner(f"Error creando cliente: {error_message}")
            
        finally:
            self._set_creating_state(False)
    
    def _set_creating_state(self, is_creating: bool):
        """
        Establece el estado de creación y actualiza la UI.
        
        Args:
            is_creating: Si está en proceso de creación
        """
        try:
            self._is_creating = is_creating
            
            # Actualizar botón crear
            if self._create_button.current:
                self._create_button.current.text = "Creando..." if is_creating else "Crear Cliente"
                self._create_button.current.icon = ft.Icons.HOURGLASS_EMPTY if is_creating else ft.Icons.SAVE
                self._create_button.current.disabled = is_creating
                self._create_button.current.update()
            
            # Actualizar botón cancelar
            if self._cancel_button.current:
                self._cancel_button.current.disabled = is_creating
                self._cancel_button.current.update()
            
            # Actualizar formulario
            if self._client_form.current:
                self._client_form.current.set_loading_state(is_creating)
                
        except Exception as e:
            self._logger.error(f"Error estableciendo estado de creación: {e}")
    
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
    
    def clear_form(self):
        """Limpia el formulario de creación."""
        try:
            if self._client_form.current:
                self._client_form.current.clear_form()
            self._hide_error_banner()
            self._hide_success_banner()
            self._logger.debug("Formulario limpiado")
        except Exception as e:
            self._logger.error(f"Error limpiando formulario: {e}")
    
    def set_initial_data(self, data: Dict[str, Any]):
        """
        Establece datos iniciales en el formulario.
        
        Args:
            data: Datos iniciales para el formulario
        """
        try:
            if self._client_form.current:
                self._client_form.current.set_initial_data(data)
            self._logger.debug("Datos iniciales establecidos")
        except Exception as e:
            self._logger.error(f"Error estableciendo datos iniciales: {e}")
    
    def get_form_data(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos actuales del formulario.
        
        Returns:
            Datos del formulario o None si hay error
        """
        try:
            if self._client_form.current:
                return self._client_form.current.get_form_data()
            return None
        except Exception as e:
            self._logger.error(f"Error obteniendo datos del formulario: {e}")
            return None
    
    def is_form_valid(self) -> bool:
        """
        Verifica si el formulario es válido.
        
        Returns:
            True si el formulario es válido
        """
        try:
            if self._client_form.current:
                return self._client_form.current.is_form_valid()
            return False
        except Exception as e:
            self._logger.error(f"Error verificando validez del formulario: {e}")
            return False
    
    def get_creating_state(self) -> bool:
        """
        Obtiene el estado de creación actual.
        
        Returns:
            True si está creando un cliente
        """
        return self._is_creating
    
    def focus_first_field(self):
        """Enfoca el primer campo del formulario."""
        try:
            if self._client_form.current:
                self._client_form.current.focus_first_field()
        except Exception as e:
            self._logger.error(f"Error enfocando primer campo: {e}")
