#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Componente ClientForm para Flet
===============================

Formulario reutilizable para crear y editar clientes con validaciones
completas, siguiendo los principios de Material Design y las mejores
prácticas de Flet.

Características:
- Validación en tiempo real
- Soporte para creación y edición
- Interfaz intuitiva y responsiva
- Manejo de errores integrado
- Estados de carga y éxito
- Campos obligatorios y opcionales
- Integración con esquemas Pydantic

Autor: FletArchitect
"""

from typing import Optional, Callable, Any, Dict
from enum import Enum
import re

import flet as ft
from loguru import logger

# Importar esquemas del proyecto
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from planificador.schemas.client import Client, ClientCreate, ClientUpdate


class FormMode(Enum):
    """Modos de operación del formulario."""
    CREATE = "create"
    EDIT = "edit"


class ClientForm(ft.Container):
    """
    Formulario para crear y editar clientes.
    
    Este componente proporciona una interfaz completa para la gestión
    de datos de clientes, incluyendo validación en tiempo real,
    manejo de errores y estados de carga.
    
    Attributes:
        mode: Modo del formulario (CREATE o EDIT)
        client: Cliente a editar (solo en modo EDIT)
        on_submit: Callback para envío del formulario
        on_cancel: Callback para cancelación
        show_cancel: Si mostrar botón de cancelar
        auto_validate: Si validar automáticamente los campos
    """
    
    def __init__(
        self,
        mode: FormMode = FormMode.CREATE,
        client: Optional[Client] = None,
        on_submit: Optional[Callable[[Dict[str, Any]], Any]] = None,
        on_cancel: Optional[Callable[[], Any]] = None,
        show_cancel: bool = True,
        auto_validate: bool = True,
        **kwargs
    ):
        """
        Inicializa el formulario de cliente.
        
        Args:
            mode: Modo de operación del formulario
            client: Cliente a editar (requerido en modo EDIT)
            on_submit: Función callback para envío
            on_cancel: Función callback para cancelación
            show_cancel: Si mostrar botón cancelar
            auto_validate: Si validar automáticamente
            **kwargs: Argumentos adicionales para ft.Container
        """
        super().__init__(**kwargs)
        
        self.mode = mode
        self.client = client
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        self.show_cancel = show_cancel
        self.auto_validate = auto_validate
        
        self._logger = logger.bind(
            component="ClientForm", 
            mode=mode.value,
            client_id=client.id if client else None
        )
        
        # Estado del formulario
        self._is_loading = False
        self._validation_errors: Dict[str, str] = {}
        
        # Referencias a los campos del formulario
        self._name_field = ft.Ref[ft.TextField]()
        self._code_field = ft.Ref[ft.TextField]()
        self._email_field = ft.Ref[ft.TextField]()
        self._phone_field = ft.Ref[ft.TextField]()
        self._contact_person_field = ft.Ref[ft.TextField]()
        self._address_field = ft.Ref[ft.TextField]()
        self._notes_field = ft.Ref[ft.TextField]()
        self._is_active_field = ft.Ref[ft.Switch]()
        
        # Referencias a elementos de UI
        self._submit_button = ft.Ref[ft.ElevatedButton]()
        self._cancel_button = ft.Ref[ft.TextButton]()
        self._progress_indicator = ft.Ref[ft.ProgressRing]()
        self._error_banner = ft.Ref[ft.Banner]()
        
        # Configurar propiedades del contenedor
        self.padding = ft.padding.all(20)
        self.border_radius = ft.border_radius.all(8)
        self.bgcolor = ft.Colors.SURFACE
        
        # Construir el formulario
        self._build_form()
        
        self._logger.debug(f"ClientForm inicializado en modo: {mode.value}")
    
    def _build_form(self):
        """Construye la estructura del formulario."""
        try:
            self.content = ft.Column([
                # Encabezado del formulario
                self._build_header(),
                
                # Banner de errores (oculto inicialmente)
                ft.Banner(
                    ref=self._error_banner,
                    bgcolor=ft.Colors.ERROR_CONTAINER,
                    leading=ft.Icon(ft.Icons.ERROR, color=ft.Colors.ERROR),
                    content=ft.Text(""),
                    actions=[
                        ft.TextButton(
                            "Cerrar",
                            on_click=lambda e: self._hide_error_banner()
                        )
                    ]
                ),
                
                # Campos del formulario
                self._build_form_fields(),
                
                # Botones de acción
                self._build_action_buttons()
            ], 
            spacing=20,
            scroll=ft.ScrollMode.AUTO)
            
        except Exception as e:
            self._logger.error(f"Error construyendo formulario: {e}")
            self.content = self._build_error_content()
    
    def _build_header(self) -> ft.Container:
        """Construye el encabezado del formulario."""
        title = "Crear Cliente" if self.mode == FormMode.CREATE else "Editar Cliente"
        subtitle = "Complete la información del cliente" if self.mode == FormMode.CREATE else f"Modificando: {self.client.name if self.client else ''}"
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    title,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PRIMARY
                ),
                ft.Text(
                    subtitle,
                    size=14,
                    color=ft.Colors.GREY_600
                )
            ], spacing=4),
            padding=ft.padding.only(bottom=10)
        )
    
    def _build_form_fields(self) -> ft.Container:
        """Construye los campos del formulario."""
        return ft.Container(
            content=ft.Column([
                # Información básica
                self._build_basic_info_section(),
                
                ft.Divider(height=20),
                
                # Información de contacto
                self._build_contact_info_section(),
                
                ft.Divider(height=20),
                
                # Información adicional
                self._build_additional_info_section()
            ], spacing=16)
        )
    
    def _build_basic_info_section(self) -> ft.Container:
        """Construye la sección de información básica."""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Información Básica",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PRIMARY
                ),
                
                # Nombre (obligatorio)
                ft.TextField(
                    ref=self._name_field,
                    label="Nombre del Cliente *",
                    hint_text="Ingrese el nombre completo del cliente",
                    prefix_icon=ft.Icons.BUSINESS,
                    value=self.client.name if self.client else "",
                    on_change=lambda e: self._validate_field("name", e.control.value) if self.auto_validate else None,
                    error_text=self._validation_errors.get("name"),
                    max_length=100,
                    counter_text=""
                ),
                
                # Código (obligatorio)
                ft.TextField(
                    ref=self._code_field,
                    label="Código del Cliente *",
                    hint_text="Código único identificador",
                    prefix_icon=ft.Icons.TAG,
                    value=self.client.code if self.client else "",
                    on_change=lambda e: self._validate_field("code", e.control.value) if self.auto_validate else None,
                    error_text=self._validation_errors.get("code"),
                    max_length=20,
                    counter_text=""
                ),
                
                # Estado activo/inactivo
                ft.Row([
                    ft.Switch(
                        ref=self._is_active_field,
                        label="Cliente Activo",
                        value=self.client.is_active if self.client else True,
                        active_color=ft.Colors.GREEN
                    ),
                    ft.Container(width=20),
                    ft.Text(
                        "Determina si el cliente está activo en el sistema",
                        size=12,
                        color=ft.Colors.GREY_600,
                        expand=True
                    )
                ], alignment=ft.MainAxisAlignment.START)
            ], spacing=12)
        )
    
    def _build_contact_info_section(self) -> ft.Container:
        """Construye la sección de información de contacto."""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Información de Contacto",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PRIMARY
                ),
                
                # Email
                ft.TextField(
                    ref=self._email_field,
                    label="Email",
                    hint_text="correo@ejemplo.com",
                    prefix_icon=ft.Icons.EMAIL,
                    value=self.client.email if self.client else "",
                    on_change=lambda e: self._validate_field("email", e.control.value) if self.auto_validate else None,
                    error_text=self._validation_errors.get("email"),
                    keyboard_type=ft.KeyboardType.EMAIL,
                    max_length=100,
                    counter_text=""
                ),
                
                # Teléfono
                ft.TextField(
                    ref=self._phone_field,
                    label="Teléfono",
                    hint_text="+1234567890",
                    prefix_icon=ft.Icons.PHONE,
                    value=self.client.phone if self.client else "",
                    on_change=lambda e: self._validate_field("phone", e.control.value) if self.auto_validate else None,
                    error_text=self._validation_errors.get("phone"),
                    keyboard_type=ft.KeyboardType.PHONE,
                    max_length=20,
                    counter_text=""
                ),
                
                # Persona de contacto
                ft.TextField(
                    ref=self._contact_person_field,
                    label="Persona de Contacto",
                    hint_text="Nombre del contacto principal",
                    prefix_icon=ft.Icons.PERSON,
                    value=self.client.contact_person if self.client else "",
                    max_length=100,
                    counter_text=""
                ),
                
                # Dirección
                ft.TextField(
                    ref=self._address_field,
                    label="Dirección",
                    hint_text="Dirección completa del cliente",
                    prefix_icon=ft.Icons.LOCATION_ON,
                    value=self.client.address if self.client else "",
                    multiline=True,
                    min_lines=2,
                    max_lines=4,
                    max_length=200,
                    counter_text=""
                )
            ], spacing=12)
        )
    
    def _build_additional_info_section(self) -> ft.Container:
        """Construye la sección de información adicional."""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Información Adicional",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PRIMARY
                ),
                
                # Notas
                ft.TextField(
                    ref=self._notes_field,
                    label="Notas",
                    hint_text="Información adicional sobre el cliente",
                    prefix_icon=ft.Icons.NOTE,
                    value=self.client.notes if self.client else "",
                    multiline=True,
                    min_lines=3,
                    max_lines=6,
                    max_length=500,
                    counter_text="",
                    expand=True
                )
            ], spacing=12)
        )
    
    def _build_action_buttons(self) -> ft.Container:
        """Construye los botones de acción del formulario."""
        buttons = []
        
        # Botón de cancelar (si está habilitado)
        if self.show_cancel:
            buttons.append(
                ft.TextButton(
                    ref=self._cancel_button,
                    text="Cancelar",
                    icon=ft.Icons.CANCEL,
                    on_click=lambda e: self._handle_cancel(),
                    disabled=self._is_loading
                )
            )
        
        # Botón de enviar
        submit_text = "Crear Cliente" if self.mode == FormMode.CREATE else "Actualizar Cliente"
        submit_icon = ft.Icons.ADD if self.mode == FormMode.CREATE else ft.Icons.SAVE
        
        buttons.append(
            ft.ElevatedButton(
                ref=self._submit_button,
                text=submit_text,
                icon=submit_icon,
                on_click=lambda e: self._handle_submit(),
                disabled=self._is_loading,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.ON_PRIMARY
                )
            )
        )
        
        # Indicador de progreso
        progress_row = ft.Row([
            ft.ProgressRing(
                ref=self._progress_indicator,
                visible=False,
                width=20,
                height=20,
                stroke_width=2
            ),
            ft.Text(
                "Procesando...",
                size=12,
                color=ft.Colors.GREY_600,
                visible=False
            )
        ], spacing=8)
        
        return ft.Container(
            content=ft.Column([
                progress_row,
                ft.Row(
                    buttons,
                    alignment=ft.MainAxisAlignment.END,
                    spacing=12
                )
            ], spacing=12),
            padding=ft.padding.only(top=20)
        )
    
    def _build_error_content(self) -> ft.Column:
        """Construye contenido de error cuando falla la construcción."""
        return ft.Column([
            ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED, size=48),
            ft.Text(
                "Error cargando formulario",
                color=ft.Colors.RED,
                size=16,
                text_align=ft.TextAlign.CENTER
            )
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER)
    
    # ==================== VALIDATION METHODS ====================
    
    def _validate_field(self, field_name: str, value: str) -> bool:
        """
        Valida un campo específico.
        
        Args:
            field_name: Nombre del campo a validar
            value: Valor del campo
            
        Returns:
            True si el campo es válido, False en caso contrario
        """
        try:
            error_message = None
            
            if field_name == "name":
                error_message = self._validate_name(value)
            elif field_name == "code":
                error_message = self._validate_code(value)
            elif field_name == "email":
                error_message = self._validate_email(value)
            elif field_name == "phone":
                error_message = self._validate_phone(value)
            
            # Actualizar estado de validación
            if error_message:
                self._validation_errors[field_name] = error_message
            else:
                self._validation_errors.pop(field_name, None)
            
            # Actualizar campo visual
            field_ref = getattr(self, f"_{field_name}_field", None)
            if field_ref and field_ref.current:
                field_ref.current.error_text = error_message
                field_ref.current.update()
            
            return error_message is None
            
        except Exception as e:
            self._logger.error(f"Error validando campo {field_name}: {e}")
            return False
    
    def _validate_name(self, value: str) -> Optional[str]:
        """Valida el nombre del cliente."""
        if not value or not value.strip():
            return "El nombre es obligatorio"
        if len(value.strip()) < 2:
            return "El nombre debe tener al menos 2 caracteres"
        if len(value.strip()) > 100:
            return "El nombre no puede exceder 100 caracteres"
        return None
    
    def _validate_code(self, value: str) -> Optional[str]:
        """Valida el código del cliente."""
        if not value or not value.strip():
            return "El código es obligatorio"
        if len(value.strip()) < 2:
            return "El código debe tener al menos 2 caracteres"
        if len(value.strip()) > 20:
            return "El código no puede exceder 20 caracteres"
        if not re.match(r'^[A-Za-z0-9_-]+$', value.strip()):
            return "El código solo puede contener letras, números, guiones y guiones bajos"
        return None
    
    def _validate_email(self, value: str) -> Optional[str]:
        """Valida el email del cliente."""
        if not value or not value.strip():
            return None  # Email es opcional
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value.strip()):
            return "Formato de email inválido"
        
        if len(value.strip()) > 100:
            return "El email no puede exceder 100 caracteres"
        
        return None
    
    def _validate_phone(self, value: str) -> Optional[str]:
        """Valida el teléfono del cliente."""
        if not value or not value.strip():
            return None  # Teléfono es opcional
        
        # Permitir números, espacios, guiones, paréntesis y el signo +
        phone_pattern = r'^[\+]?[0-9\s\-\(\)]{7,20}$'
        if not re.match(phone_pattern, value.strip()):
            return "Formato de teléfono inválido"
        
        return None
    
    def _validate_all_fields(self) -> bool:
        """
        Valida todos los campos del formulario.
        
        Returns:
            True si todos los campos son válidos, False en caso contrario
        """
        try:
            is_valid = True
            
            # Obtener valores actuales de los campos
            name_value = self._name_field.current.value if self._name_field.current else ""
            code_value = self._code_field.current.value if self._code_field.current else ""
            email_value = self._email_field.current.value if self._email_field.current else ""
            phone_value = self._phone_field.current.value if self._phone_field.current else ""
            
            # Validar cada campo
            is_valid &= self._validate_field("name", name_value)
            is_valid &= self._validate_field("code", code_value)
            is_valid &= self._validate_field("email", email_value)
            is_valid &= self._validate_field("phone", phone_value)
            
            return is_valid
            
        except Exception as e:
            self._logger.error(f"Error validando todos los campos: {e}")
            return False
    
    # ==================== EVENT HANDLERS ====================
    
    def _handle_submit(self):
        """Maneja el envío del formulario."""
        try:
            # Validar todos los campos
            if not self._validate_all_fields():
                self._show_error_banner("Por favor, corrija los errores en el formulario")
                return
            
            # Mostrar estado de carga
            self._set_loading_state(True)
            
            # Recopilar datos del formulario
            form_data = self._collect_form_data()
            
            # Llamar al callback de envío
            if self.on_submit:
                self.on_submit(form_data)
            
            self._logger.debug(f"Formulario enviado en modo: {self.mode.value}")
            
        except Exception as e:
            self._logger.error(f"Error enviando formulario: {e}")
            self._show_error_banner(f"Error procesando formulario: {str(e)}")
            self._set_loading_state(False)
    
    def _handle_cancel(self):
        """Maneja la cancelación del formulario."""
        try:
            if self.on_cancel:
                self.on_cancel()
            self._logger.debug("Formulario cancelado")
        except Exception as e:
            self._logger.error(f"Error cancelando formulario: {e}")
    
    # ==================== UTILITY METHODS ====================
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """Recopila los datos del formulario."""
        try:
            data = {
                "name": self._name_field.current.value.strip() if self._name_field.current else "",
                "code": self._code_field.current.value.strip() if self._code_field.current else "",
                "email": self._email_field.current.value.strip() if self._email_field.current else None,
                "phone": self._phone_field.current.value.strip() if self._phone_field.current else None,
                "contact_person": self._contact_person_field.current.value.strip() if self._contact_person_field.current else None,
                "address": self._address_field.current.value.strip() if self._address_field.current else None,
                "notes": self._notes_field.current.value.strip() if self._notes_field.current else None,
                "is_active": self._is_active_field.current.value if self._is_active_field.current else True
            }
            
            # Limpiar valores vacíos
            for key, value in list(data.items()):
                if isinstance(value, str) and not value:
                    data[key] = None
            
            return data
            
        except Exception as e:
            self._logger.error(f"Error recopilando datos del formulario: {e}")
            return {}
    
    def _set_loading_state(self, loading: bool):
        """Establece el estado de carga del formulario."""
        try:
            self._is_loading = loading
            
            # Actualizar botones
            if self._submit_button.current:
                self._submit_button.current.disabled = loading
                self._submit_button.current.update()
            
            if self._cancel_button.current:
                self._cancel_button.current.disabled = loading
                self._cancel_button.current.update()
            
            # Actualizar indicador de progreso
            if self._progress_indicator.current:
                self._progress_indicator.current.visible = loading
                self._progress_indicator.current.update()
            
        except Exception as e:
            self._logger.error(f"Error estableciendo estado de carga: {e}")
    
    def _show_error_banner(self, message: str):
        """Muestra un banner de error."""
        try:
            if self._error_banner.current:
                self._error_banner.current.content.value = message
                self._error_banner.current.open = True
                self._error_banner.current.update()
        except Exception as e:
            self._logger.error(f"Error mostrando banner de error: {e}")
    
    def _hide_error_banner(self):
        """Oculta el banner de error."""
        try:
            if self._error_banner.current:
                self._error_banner.current.open = False
                self._error_banner.current.update()
        except Exception as e:
            self._logger.error(f"Error ocultando banner de error: {e}")
    
    # ==================== PUBLIC METHODS ====================
    
    def reset_form(self):
        """Resetea el formulario a su estado inicial."""
        try:
            # Limpiar errores de validación
            self._validation_errors.clear()
            
            # Resetear campos
            if self._name_field.current:
                self._name_field.current.value = self.client.name if self.client else ""
                self._name_field.current.error_text = None
                self._name_field.current.update()
            
            if self._code_field.current:
                self._code_field.current.value = self.client.code if self.client else ""
                self._code_field.current.error_text = None
                self._code_field.current.update()
            
            # ... resetear otros campos de manera similar
            
            # Ocultar banner de error
            self._hide_error_banner()
            
            # Resetear estado de carga
            self._set_loading_state(False)
            
            self._logger.debug("Formulario reseteado")
            
        except Exception as e:
            self._logger.error(f"Error reseteando formulario: {e}")
    
    def set_client_data(self, client: Client):
        """
        Establece los datos del cliente en el formulario.
        
        Args:
            client: Cliente cuyos datos se van a cargar
        """
        try:
            self.client = client
            self.mode = FormMode.EDIT
            
            # Actualizar campos con los datos del cliente
            if self._name_field.current:
                self._name_field.current.value = client.name
                self._name_field.current.update()
            
            if self._code_field.current:
                self._code_field.current.value = client.code
                self._code_field.current.update()
            
            # ... actualizar otros campos
            
            self._logger.debug(f"Datos del cliente cargados: {client.name}")
            
        except Exception as e:
            self._logger.error(f"Error cargando datos del cliente: {e}")
    
    def get_form_data(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos actuales del formulario sin validar.
        
        Returns:
            Diccionario con los datos del formulario o None si hay error
        """
        try:
            return self._collect_form_data()
        except Exception as e:
            self._logger.error(f"Error obteniendo datos del formulario: {e}")
            return None
