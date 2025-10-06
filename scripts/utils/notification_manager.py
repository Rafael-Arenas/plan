#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de Notificaciones para Flet
==================================

Sistema centralizado para manejar notificaciones, errores y mensajes
de usuario de manera consistente en toda la aplicación.

Características:
- Notificaciones toast no intrusivas
- Banners contextuales
- Diálogos de confirmación
- Snack bars temporales
- Gestión de estados de error
- Logging integrado
- Personalización de estilos
- Queue de notificaciones
- Auto-dismiss configurable

Autor: FletArchitect
"""

from typing import Optional, Dict, Any, List, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import uuid

import flet as ft
from loguru import logger


class NotificationType(Enum):
    """Tipos de notificación disponibles."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    LOADING = "loading"


class NotificationPosition(Enum):
    """Posiciones para las notificaciones."""
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


@dataclass
class NotificationConfig:
    """Configuración para una notificación."""
    type: NotificationType
    title: str
    message: str = ""
    duration: Optional[int] = None  # None = no auto-dismiss
    position: NotificationPosition = NotificationPosition.TOP_RIGHT
    show_close_button: bool = True
    show_icon: bool = True
    actions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActiveNotification:
    """Notificación activa en el sistema."""
    id: str
    config: NotificationConfig
    created_at: datetime
    dismiss_at: Optional[datetime] = None
    is_dismissed: bool = False
    control: Optional[ft.Control] = None


class NotificationManager:
    """
    Gestor centralizado de notificaciones para la aplicación Flet.
    
    Proporciona una interfaz unificada para mostrar diferentes tipos
    de notificaciones, manejar errores y gestionar el feedback del usuario.
    """
    
    def __init__(self, page: ft.Page):
        """
        Inicializa el gestor de notificaciones.
        
        Args:
            page: Página principal de Flet
        """
        self.page = page
        self._logger = logger.bind(component="NotificationManager")
        
        # Estado interno
        self._active_notifications: Dict[str, ActiveNotification] = {}
        self._notification_queue: List[NotificationConfig] = []
        self._max_concurrent_notifications = 5
        self._default_duration = 5000  # 5 segundos
        
        # Contenedores para diferentes tipos de notificaciones
        self._toast_container = ft.Ref[ft.Container]()
        self._banner_container = ft.Ref[ft.Container]()
        self._overlay_container = ft.Ref[ft.Container]()
        
        # Configuración de estilos
        self._setup_styles()
        
        # Inicializar contenedores en la página
        self._setup_containers()
        
        # Iniciar el procesador de cola
        asyncio.create_task(self._process_notification_queue())
        
        self._logger.debug("NotificationManager inicializado")
    
    def _setup_styles(self):
        """Configura los estilos para diferentes tipos de notificación."""
        self._styles = {
            NotificationType.SUCCESS: {
                "bgcolor": ft.Colors.GREEN_100,
                "border_color": ft.Colors.GREEN,
                "icon": ft.Icons.CHECK_CIRCLE,
                "icon_color": ft.Colors.GREEN,
                "text_color": ft.Colors.GREEN_800
            },
            NotificationType.ERROR: {
                "bgcolor": ft.Colors.RED_100,
                "border_color": ft.Colors.RED,
                "icon": ft.Icons.ERROR,
                "icon_color": ft.Colors.RED,
                "text_color": ft.Colors.RED_800
            },
            NotificationType.WARNING: {
                "bgcolor": ft.Colors.ORANGE_100,
                "border_color": ft.Colors.ORANGE,
                "icon": ft.Icons.WARNING,
                "icon_color": ft.Colors.ORANGE,
                "text_color": ft.Colors.ORANGE_800
            },
            NotificationType.INFO: {
                "bgcolor": ft.Colors.BLUE_100,
                "border_color": ft.Colors.BLUE,
                "icon": ft.Icons.INFO,
                "icon_color": ft.Colors.BLUE,
                "text_color": ft.Colors.BLUE_800
            },
            NotificationType.LOADING: {
                "bgcolor": ft.Colors.GREY_100,
                "border_color": ft.Colors.GREY,
                "icon": ft.Icons.HOURGLASS_EMPTY,
                "icon_color": ft.Colors.GREY,
                "text_color": ft.Colors.GREY_800
            }
        }
    
    def _setup_containers(self):
        """Configura los contenedores de notificación en la página."""
        try:
            # Contenedor para toasts (esquina superior derecha)
            toast_container = ft.Container(
                ref=self._toast_container,
                content=ft.Column([], spacing=8),
                right=20,
                top=20,
                width=350
            )
            
            # Contenedor para banners (parte superior)
            banner_container = ft.Container(
                ref=self._banner_container,
                content=ft.Column([], spacing=4),
                left=0,
                right=0,
                top=0
            )
            
            # Contenedor para overlays (centro)
            overlay_container = ft.Container(
                ref=self._overlay_container,
                content=ft.Stack([]),
                left=0,
                right=0,
                top=0,
                bottom=0
            )
            
            # Agregar contenedores a la página como overlays
            if not hasattr(self.page, 'overlay'):
                self.page.overlay = []
            
            self.page.overlay.extend([
                banner_container,
                toast_container,
                overlay_container
            ])
            
            self.page.update()
            
        except Exception as e:
            self._logger.error(f"Error configurando contenedores: {e}")
    
    # ==================== PUBLIC API ====================
    
    def show_success(
        self,
        title: str,
        message: str = "",
        duration: Optional[int] = None,
        actions: List[Dict[str, Any]] = None
    ) -> str:
        """
        Muestra una notificación de éxito.
        
        Args:
            title: Título de la notificación
            message: Mensaje detallado (opcional)
            duration: Duración en milisegundos (None = no auto-dismiss)
            actions: Lista de acciones disponibles
            
        Returns:
            ID de la notificación
        """
        return self._queue_notification(NotificationConfig(
            type=NotificationType.SUCCESS,
            title=title,
            message=message,
            duration=duration or self._default_duration,
            actions=actions or []
        ))
    
    def show_error(
        self,
        title: str,
        message: str = "",
        duration: Optional[int] = None,
        actions: List[Dict[str, Any]] = None
    ) -> str:
        """
        Muestra una notificación de error.
        
        Args:
            title: Título del error
            message: Mensaje detallado del error
            duration: Duración en milisegundos (None = no auto-dismiss)
            actions: Lista de acciones disponibles
            
        Returns:
            ID de la notificación
        """
        return self._queue_notification(NotificationConfig(
            type=NotificationType.ERROR,
            title=title,
            message=message,
            duration=duration,  # Los errores no se auto-dismiss por defecto
            actions=actions or []
        ))
    
    def show_warning(
        self,
        title: str,
        message: str = "",
        duration: Optional[int] = None,
        actions: List[Dict[str, Any]] = None
    ) -> str:
        """
        Muestra una notificación de advertencia.
        
        Args:
            title: Título de la advertencia
            message: Mensaje detallado
            duration: Duración en milisegundos
            actions: Lista de acciones disponibles
            
        Returns:
            ID de la notificación
        """
        return self._queue_notification(NotificationConfig(
            type=NotificationType.WARNING,
            title=title,
            message=message,
            duration=duration or self._default_duration * 2,  # Warnings duran más
            actions=actions or []
        ))
    
    def show_info(
        self,
        title: str,
        message: str = "",
        duration: Optional[int] = None,
        actions: List[Dict[str, Any]] = None
    ) -> str:
        """
        Muestra una notificación informativa.
        
        Args:
            title: Título de la información
            message: Mensaje detallado
            duration: Duración en milisegundos
            actions: Lista de acciones disponibles
            
        Returns:
            ID de la notificación
        """
        return self._queue_notification(NotificationConfig(
            type=NotificationType.INFO,
            title=title,
            message=message,
            duration=duration or self._default_duration,
            actions=actions or []
        ))
    
    def show_loading(
        self,
        title: str,
        message: str = "",
        actions: List[Dict[str, Any]] = None
    ) -> str:
        """
        Muestra una notificación de carga.
        
        Args:
            title: Título de la operación en curso
            message: Mensaje detallado
            actions: Lista de acciones disponibles (ej. cancelar)
            
        Returns:
            ID de la notificación
        """
        return self._queue_notification(NotificationConfig(
            type=NotificationType.LOADING,
            title=title,
            message=message,
            duration=None,  # Loading no se auto-dismiss
            actions=actions or []
        ))
    
    def dismiss_notification(self, notification_id: str):
        """
        Descarta una notificación específica.
        
        Args:
            notification_id: ID de la notificación a descartar
        """
        try:
            if notification_id in self._active_notifications:
                notification = self._active_notifications[notification_id]
                notification.is_dismissed = True
                self._remove_notification_from_ui(notification)
                del self._active_notifications[notification_id]
                
                self._logger.debug(f"Notificación descartada: {notification_id}")
        except Exception as e:
            self._logger.error(f"Error descartando notificación {notification_id}: {e}")
    
    def dismiss_all_notifications(self):
        """Descarta todas las notificaciones activas."""
        try:
            notification_ids = list(self._active_notifications.keys())
            for notification_id in notification_ids:
                self.dismiss_notification(notification_id)
            
            self._logger.debug("Todas las notificaciones descartadas")
        except Exception as e:
            self._logger.error(f"Error descartando todas las notificaciones: {e}")
    
    def show_confirmation_dialog(
        self,
        title: str,
        message: str,
        on_confirm: Callable,
        on_cancel: Optional[Callable] = None,
        confirm_text: str = "Confirmar",
        cancel_text: str = "Cancelar"
    ):
        """
        Muestra un diálogo de confirmación.
        
        Args:
            title: Título del diálogo
            message: Mensaje del diálogo
            on_confirm: Callback para confirmación
            on_cancel: Callback para cancelación
            confirm_text: Texto del botón confirmar
            cancel_text: Texto del botón cancelar
        """
        try:
            def handle_confirm(e):
                self.page.dialog.open = False
                self.page.update()
                if on_confirm:
                    on_confirm()
            
            def handle_cancel(e):
                self.page.dialog.open = False
                self.page.update()
                if on_cancel:
                    on_cancel()
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(title),
                content=ft.Text(message),
                actions=[
                    ft.TextButton(cancel_text, on_click=handle_cancel),
                    ft.ElevatedButton(confirm_text, on_click=handle_confirm)
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            
        except Exception as e:
            self._logger.error(f"Error mostrando diálogo de confirmación: {e}")
    
    def show_snack_bar(
        self,
        message: str,
        action_label: Optional[str] = None,
        on_action: Optional[Callable] = None,
        duration: int = 4000
    ):
        """
        Muestra una snack bar temporal.
        
        Args:
            message: Mensaje a mostrar
            action_label: Etiqueta del botón de acción (opcional)
            on_action: Callback para la acción (opcional)
            duration: Duración en milisegundos
        """
        try:
            action = None
            if action_label and on_action:
                action = ft.SnackBarAction(action_label, on_action)
            
            snack_bar = ft.SnackBar(
                content=ft.Text(message),
                action=action,
                duration=duration
            )
            
            self.page.snack_bar = snack_bar
            snack_bar.open = True
            self.page.update()
            
        except Exception as e:
            self._logger.error(f"Error mostrando snack bar: {e}")
    
    # ==================== INTERNAL METHODS ====================
    
    def _queue_notification(self, config: NotificationConfig) -> str:
        """
        Agrega una notificación a la cola de procesamiento.
        
        Args:
            config: Configuración de la notificación
            
        Returns:
            ID de la notificación
        """
        try:
            notification_id = str(uuid.uuid4())
            config.metadata["id"] = notification_id
            
            self._notification_queue.append(config)
            
            self._logger.debug(f"Notificación agregada a la cola: {notification_id}")
            return notification_id
            
        except Exception as e:
            self._logger.error(f"Error agregando notificación a la cola: {e}")
            return ""
    
    async def _process_notification_queue(self):
        """Procesa la cola de notificaciones de manera asíncrona."""
        while True:
            try:
                if (self._notification_queue and 
                    len(self._active_notifications) < self._max_concurrent_notifications):
                    
                    config = self._notification_queue.pop(0)
                    await self._show_notification(config)
                
                await asyncio.sleep(0.1)  # Pequeña pausa para no saturar
                
            except Exception as e:
                self._logger.error(f"Error procesando cola de notificaciones: {e}")
                await asyncio.sleep(1)  # Pausa más larga en caso de error
    
    async def _show_notification(self, config: NotificationConfig):
        """
        Muestra una notificación en la UI.
        
        Args:
            config: Configuración de la notificación
        """
        try:
            notification_id = config.metadata.get("id", str(uuid.uuid4()))
            
            # Crear la notificación activa
            notification = ActiveNotification(
                id=notification_id,
                config=config,
                created_at=datetime.now()
            )
            
            # Configurar auto-dismiss si es necesario
            if config.duration:
                notification.dismiss_at = datetime.now() + timedelta(milliseconds=config.duration)
            
            # Crear el control de UI
            notification.control = self._create_notification_control(notification)
            
            # Agregar a notificaciones activas
            self._active_notifications[notification_id] = notification
            
            # Agregar a la UI
            self._add_notification_to_ui(notification)
            
            # Programar auto-dismiss si es necesario
            if notification.dismiss_at:
                asyncio.create_task(self._auto_dismiss_notification(notification))
            
            self._logger.debug(f"Notificación mostrada: {notification_id}")
            
        except Exception as e:
            self._logger.error(f"Error mostrando notificación: {e}")
    
    def _create_notification_control(self, notification: ActiveNotification) -> ft.Control:
        """
        Crea el control de UI para una notificación.
        
        Args:
            notification: Notificación activa
            
        Returns:
            Control de Flet para la notificación
        """
        try:
            config = notification.config
            style = self._styles[config.type]
            
            # Contenido principal
            content_items = []
            
            # Fila principal con icono y texto
            main_row = []
            
            # Icono
            if config.show_icon:
                main_row.append(
                    ft.Icon(
                        style["icon"],
                        color=style["icon_color"],
                        size=24
                    )
                )
            
            # Textos
            text_column = [
                ft.Text(
                    config.title,
                    weight=ft.FontWeight.BOLD,
                    color=style["text_color"],
                    size=14
                )
            ]
            
            if config.message:
                text_column.append(
                    ft.Text(
                        config.message,
                        color=style["text_color"],
                        size=12
                    )
                )
            
            main_row.append(
                ft.Column(text_column, spacing=4, expand=True)
            )
            
            # Botón cerrar
            if config.show_close_button:
                main_row.append(
                    ft.IconButton(
                        ft.Icons.CLOSE,
                        icon_size=16,
                        on_click=lambda e: self.dismiss_notification(notification.id),
                        tooltip="Cerrar"
                    )
                )
            
            content_items.append(
                ft.Row(main_row, spacing=12, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
            
            # Acciones
            if config.actions:
                action_buttons = []
                for action in config.actions:
                    button = ft.TextButton(
                        text=action.get("text", "Acción"),
                        on_click=action.get("on_click"),
                        style=ft.ButtonStyle(
                            color=style["text_color"]
                        )
                    )
                    action_buttons.append(button)
                
                content_items.append(
                    ft.Row(
                        action_buttons,
                        alignment=ft.MainAxisAlignment.END,
                        spacing=8
                    )
                )
            
            # Crear el contenedor principal
            return ft.Container(
                content=ft.Column(content_items, spacing=8),
                bgcolor=style["bgcolor"],
                border=ft.border.all(1, style["border_color"]),
                border_radius=ft.border_radius.all(8),
                padding=ft.padding.all(16),
                margin=ft.margin.only(bottom=8),
                animate_opacity=300,
                animate_scale=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
            )
            
        except Exception as e:
            self._logger.error(f"Error creando control de notificación: {e}")
            return ft.Container()  # Contenedor vacío como fallback
    
    def _add_notification_to_ui(self, notification: ActiveNotification):
        """
        Agrega una notificación a la UI.
        
        Args:
            notification: Notificación a agregar
        """
        try:
            if self._toast_container.current and notification.control:
                self._toast_container.current.content.controls.append(notification.control)
                self._toast_container.current.update()
                
        except Exception as e:
            self._logger.error(f"Error agregando notificación a UI: {e}")
    
    def _remove_notification_from_ui(self, notification: ActiveNotification):
        """
        Remueve una notificación de la UI.
        
        Args:
            notification: Notificación a remover
        """
        try:
            if (self._toast_container.current and 
                notification.control and 
                notification.control in self._toast_container.current.content.controls):
                
                self._toast_container.current.content.controls.remove(notification.control)
                self._toast_container.current.update()
                
        except Exception as e:
            self._logger.error(f"Error removiendo notificación de UI: {e}")
    
    async def _auto_dismiss_notification(self, notification: ActiveNotification):
        """
        Auto-descarta una notificación después del tiempo especificado.
        
        Args:
            notification: Notificación a auto-descartar
        """
        try:
            if notification.dismiss_at:
                # Calcular tiempo de espera
                wait_time = (notification.dismiss_at - datetime.now()).total_seconds()
                
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                
                # Verificar si la notificación aún existe y no ha sido descartada
                if (notification.id in self._active_notifications and 
                    not notification.is_dismissed):
                    self.dismiss_notification(notification.id)
                    
        except Exception as e:
            self._logger.error(f"Error en auto-dismiss de notificación: {e}")
    
    # ==================== UTILITY METHODS ====================
    
    def get_active_notifications_count(self) -> int:
        """
        Obtiene el número de notificaciones activas.
        
        Returns:
            Número de notificaciones activas
        """
        return len(self._active_notifications)
    
    def get_queued_notifications_count(self) -> int:
        """
        Obtiene el número de notificaciones en cola.
        
        Returns:
            Número de notificaciones en cola
        """
        return len(self._notification_queue)
    
    def clear_notification_queue(self):
        """Limpia la cola de notificaciones pendientes."""
        try:
            self._notification_queue.clear()
            self._logger.debug("Cola de notificaciones limpiada")
        except Exception as e:
            self._logger.error(f"Error limpiando cola de notificaciones: {e}")
    
    def set_max_concurrent_notifications(self, max_count: int):
        """
        Establece el número máximo de notificaciones concurrentes.
        
        Args:
            max_count: Número máximo de notificaciones concurrentes
        """
        if max_count > 0:
            self._max_concurrent_notifications = max_count
            self._logger.debug(f"Máximo de notificaciones concurrentes establecido: {max_count}")
    
    def set_default_duration(self, duration: int):
        """
        Establece la duración por defecto para las notificaciones.
        
        Args:
            duration: Duración en milisegundos
        """
        if duration > 0:
            self._default_duration = duration
            self._logger.debug(f"Duración por defecto establecida: {duration}ms")
