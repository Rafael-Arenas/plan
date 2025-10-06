#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manejador de Errores Centralizado para Flet
===========================================

Sistema centralizado para manejar errores, excepciones y estados de error
de manera consistente en toda la aplicación Flet.

Características:
- Manejo centralizado de excepciones
- Integración con NotificationManager
- Logging estructurado de errores
- Mapeo de excepciones a mensajes de usuario
- Estados de error recuperables
- Retry automático para operaciones
- Contexto de error enriquecido
- Fallbacks y degradación elegante
- Métricas de errores

Autor: FletArchitect
"""

from typing import Optional, Dict, Any, Callable, Type, Union, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import traceback
import asyncio
import functools
from contextlib import asynccontextmanager, contextmanager

import flet as ft
from loguru import logger

# Importar sistema de excepciones del proyecto
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from planificador.exceptions.base import PlanificadorError
from planificador.exceptions.repository import RepositoryError
from planificador.exceptions.service import ServiceError
from planificador.exceptions.validation import ValidationError

# Importar NotificationManager local
from .notification_manager import NotificationManager


class ErrorSeverity(Enum):
    """Niveles de severidad de errores."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categorías de errores."""
    VALIDATION = "validation"
    NETWORK = "network"
    DATABASE = "database"
    BUSINESS_LOGIC = "business_logic"
    UI = "ui"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Contexto enriquecido para errores."""
    operation: str
    component: str
    user_action: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ErrorMapping:
    """Mapeo de excepción a mensaje de usuario."""
    exception_type: Type[Exception]
    category: ErrorCategory
    severity: ErrorSeverity
    user_message: str
    technical_message: Optional[str] = None
    suggested_actions: List[str] = field(default_factory=list)
    is_recoverable: bool = True
    retry_allowed: bool = False


class ErrorHandler:
    """
    Manejador centralizado de errores para la aplicación Flet.
    
    Proporciona manejo consistente de errores, logging estructurado,
    notificaciones de usuario y estrategias de recuperación.
    """
    
    def __init__(self, notification_manager: NotificationManager):
        """
        Inicializa el manejador de errores.
        
        Args:
            notification_manager: Gestor de notificaciones
        """
        self.notification_manager = notification_manager
        self._logger = logger.bind(component="ErrorHandler")
        
        # Configuración
        self._max_retry_attempts = 3
        self._retry_delay_base = 1.0  # segundos
        self._show_technical_details = False  # En producción debería ser False
        
        # Métricas de errores
        self._error_counts: Dict[str, int] = {}
        self._last_errors: List[Dict[str, Any]] = []
        self._max_error_history = 100
        
        # Mapeos de errores predefinidos
        self._error_mappings: List[ErrorMapping] = []
        self._setup_default_error_mappings()
        
        self._logger.debug("ErrorHandler inicializado")
    
    def _setup_default_error_mappings(self):
        """Configura los mapeos de errores por defecto."""
        self._error_mappings = [
            # Errores de validación
            ErrorMapping(
                exception_type=ValidationError,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.LOW,
                user_message="Los datos ingresados no son válidos",
                suggested_actions=["Revise los campos marcados en rojo", "Corrija los errores y vuelva a intentar"],
                is_recoverable=True,
                retry_allowed=False
            ),
            
            # Errores de repositorio/base de datos
            ErrorMapping(
                exception_type=RepositoryError,
                category=ErrorCategory.DATABASE,
                severity=ErrorSeverity.MEDIUM,
                user_message="Error accediendo a los datos",
                suggested_actions=["Verifique su conexión", "Intente nuevamente en unos momentos"],
                is_recoverable=True,
                retry_allowed=True
            ),
            
            # Errores de servicio/lógica de negocio
            ErrorMapping(
                exception_type=ServiceError,
                category=ErrorCategory.BUSINESS_LOGIC,
                severity=ErrorSeverity.MEDIUM,
                user_message="Error procesando la operación",
                suggested_actions=["Verifique los datos ingresados", "Contacte al administrador si persiste"],
                is_recoverable=True,
                retry_allowed=True
            ),
            
            # Errores de conexión/red
            ErrorMapping(
                exception_type=ConnectionError,
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.HIGH,
                user_message="Error de conexión",
                suggested_actions=["Verifique su conexión a internet", "Intente nuevamente"],
                is_recoverable=True,
                retry_allowed=True
            ),
            
            # Errores de timeout
            ErrorMapping(
                exception_type=asyncio.TimeoutError,
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.MEDIUM,
                user_message="La operación tardó demasiado tiempo",
                suggested_actions=["Intente nuevamente", "Verifique su conexión"],
                is_recoverable=True,
                retry_allowed=True
            ),
            
            # Errores de valor
            ErrorMapping(
                exception_type=ValueError,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.LOW,
                user_message="Valor no válido",
                suggested_actions=["Revise los datos ingresados"],
                is_recoverable=True,
                retry_allowed=False
            ),
            
            # Errores genéricos del proyecto
            ErrorMapping(
                exception_type=PlanificadorError,
                category=ErrorCategory.BUSINESS_LOGIC,
                severity=ErrorSeverity.MEDIUM,
                user_message="Error en la aplicación",
                suggested_actions=["Intente nuevamente", "Contacte al soporte si persiste"],
                is_recoverable=True,
                retry_allowed=True
            ),
            
            # Errores no manejados
            ErrorMapping(
                exception_type=Exception,
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.HIGH,
                user_message="Error inesperado",
                suggested_actions=["Intente nuevamente", "Contacte al soporte técnico"],
                is_recoverable=False,
                retry_allowed=False
            )
        ]
    
    # ==================== PUBLIC API ====================
    
    def handle_error(
        self,
        error: Exception,
        context: ErrorContext,
        show_notification: bool = True,
        log_error: bool = True
    ) -> Dict[str, Any]:
        """
        Maneja un error de manera centralizada.
        
        Args:
            error: Excepción a manejar
            context: Contexto del error
            show_notification: Si mostrar notificación al usuario
            log_error: Si registrar el error en logs
            
        Returns:
            Información del error procesado
        """
        try:
            # Obtener mapeo del error
            error_mapping = self._get_error_mapping(error)
            
            # Crear información del error
            error_info = {
                "error": error,
                "mapping": error_mapping,
                "context": context,
                "timestamp": datetime.now(),
                "error_id": self._generate_error_id()
            }
            
            # Registrar error en logs
            if log_error:
                self._log_error(error_info)
            
            # Actualizar métricas
            self._update_error_metrics(error_info)
            
            # Mostrar notificación al usuario
            if show_notification:
                self._show_error_notification(error_info)
            
            # Agregar a historial
            self._add_to_error_history(error_info)
            
            return error_info
            
        except Exception as e:
            # Error manejando error - logging básico
            self._logger.critical(f"Error en ErrorHandler.handle_error: {e}")
            return {
                "error": error,
                "handler_error": e,
                "timestamp": datetime.now()
            }
    
    async def handle_async_error(
        self,
        error: Exception,
        context: ErrorContext,
        show_notification: bool = True,
        log_error: bool = True
    ) -> Dict[str, Any]:
        """
        Maneja un error de manera asíncrona.
        
        Args:
            error: Excepción a manejar
            context: Contexto del error
            show_notification: Si mostrar notificación al usuario
            log_error: Si registrar el error en logs
            
        Returns:
            Información del error procesado
        """
        return self.handle_error(error, context, show_notification, log_error)
    
    def with_error_handling(
        self,
        operation: str,
        component: str,
        show_notification: bool = True,
        retry_on_failure: bool = False,
        max_retries: Optional[int] = None
    ):
        """
        Decorador para manejo automático de errores en funciones síncronas.
        
        Args:
            operation: Nombre de la operación
            component: Componente donde ocurre
            show_notification: Si mostrar notificación de error
            retry_on_failure: Si reintentar en caso de fallo
            max_retries: Número máximo de reintentos
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                context = ErrorContext(
                    operation=operation,
                    component=component,
                    additional_data={"args": str(args), "kwargs": str(kwargs)}
                )
                
                attempts = 0
                max_attempts = max_retries or self._max_retry_attempts
                
                while attempts <= max_attempts:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        attempts += 1
                        error_info = self.handle_error(e, context, show_notification)
                        
                        # Verificar si se puede reintentar
                        if (retry_on_failure and 
                            attempts <= max_attempts and 
                            error_info["mapping"].retry_allowed):
                            
                            self._logger.warning(f"Reintentando operación {operation} (intento {attempts}/{max_attempts})")
                            continue
                        else:
                            raise e
                
                return None
            return wrapper
        return decorator
    
    def with_async_error_handling(
        self,
        operation: str,
        component: str,
        show_notification: bool = True,
        retry_on_failure: bool = False,
        max_retries: Optional[int] = None
    ):
        """
        Decorador para manejo automático de errores en funciones asíncronas.
        
        Args:
            operation: Nombre de la operación
            component: Componente donde ocurre
            show_notification: Si mostrar notificación de error
            retry_on_failure: Si reintentar en caso de fallo
            max_retries: Número máximo de reintentos
        """
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                context = ErrorContext(
                    operation=operation,
                    component=component,
                    additional_data={"args": str(args), "kwargs": str(kwargs)}
                )
                
                attempts = 0
                max_attempts = max_retries or self._max_retry_attempts
                
                while attempts <= max_attempts:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        attempts += 1
                        error_info = await self.handle_async_error(e, context, show_notification)
                        
                        # Verificar si se puede reintentar
                        if (retry_on_failure and 
                            attempts <= max_attempts and 
                            error_info["mapping"].retry_allowed):
                            
                            self._logger.warning(f"Reintentando operación {operation} (intento {attempts}/{max_attempts})")
                            
                            # Delay exponencial
                            delay = self._retry_delay_base * (2 ** (attempts - 1))
                            await asyncio.sleep(delay)
                            continue
                        else:
                            raise e
                
                return None
            return wrapper
        return decorator
    
    @contextmanager
    def error_context(
        self,
        operation: str,
        component: str,
        show_notification: bool = True,
        **context_data
    ):
        """
        Context manager para manejo de errores en bloques de código.
        
        Args:
            operation: Nombre de la operación
            component: Componente donde ocurre
            show_notification: Si mostrar notificación de error
            **context_data: Datos adicionales del contexto
        """
        context = ErrorContext(
            operation=operation,
            component=component,
            additional_data=context_data
        )
        
        try:
            yield context
        except Exception as e:
            self.handle_error(e, context, show_notification)
            raise
    
    @asynccontextmanager
    async def async_error_context(
        self,
        operation: str,
        component: str,
        show_notification: bool = True,
        **context_data
    ):
        """
        Context manager asíncrono para manejo de errores.
        
        Args:
            operation: Nombre de la operación
            component: Componente donde ocurre
            show_notification: Si mostrar notificación de error
            **context_data: Datos adicionales del contexto
        """
        context = ErrorContext(
            operation=operation,
            component=component,
            additional_data=context_data
        )
        
        try:
            yield context
        except Exception as e:
            await self.handle_async_error(e, context, show_notification)
            raise
    
    # ==================== ERROR MAPPING ====================
    
    def _get_error_mapping(self, error: Exception) -> ErrorMapping:
        """
        Obtiene el mapeo apropiado para un error.
        
        Args:
            error: Excepción a mapear
            
        Returns:
            Mapeo del error
        """
        try:
            # Buscar mapeo específico
            for mapping in self._error_mappings:
                if isinstance(error, mapping.exception_type):
                    return mapping
            
            # Fallback al mapeo genérico
            return self._error_mappings[-1]  # Exception genérico
            
        except Exception as e:
            self._logger.error(f"Error obteniendo mapeo de error: {e}")
            # Mapeo de emergencia
            return ErrorMapping(
                exception_type=Exception,
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.HIGH,
                user_message="Error inesperado",
                is_recoverable=False
            )
    
    def add_error_mapping(self, mapping: ErrorMapping):
        """
        Agrega un mapeo de error personalizado.
        
        Args:
            mapping: Mapeo de error a agregar
        """
        try:
            # Insertar antes del mapeo genérico (Exception)
            self._error_mappings.insert(-1, mapping)
            self._logger.debug(f"Mapeo de error agregado: {mapping.exception_type.__name__}")
        except Exception as e:
            self._logger.error(f"Error agregando mapeo de error: {e}")
    
    # ==================== LOGGING ====================
    
    def _log_error(self, error_info: Dict[str, Any]):
        """
        Registra un error en los logs.
        
        Args:
            error_info: Información del error
        """
        try:
            error = error_info["error"]
            mapping = error_info["mapping"]
            context = error_info["context"]
            
            # Preparar datos del log
            log_data = {
                "error_id": error_info["error_id"],
                "error_type": type(error).__name__,
                "error_message": str(error),
                "category": mapping.category.value,
                "severity": mapping.severity.value,
                "operation": context.operation,
                "component": context.component,
                "user_action": context.user_action,
                "entity_type": context.entity_type,
                "entity_id": context.entity_id,
                "additional_data": context.additional_data,
                "traceback": traceback.format_exc() if self._show_technical_details else None
            }
            
            # Log según severidad
            if mapping.severity == ErrorSeverity.CRITICAL:
                self._logger.critical("Error crítico", **log_data)
            elif mapping.severity == ErrorSeverity.HIGH:
                self._logger.error("Error alto", **log_data)
            elif mapping.severity == ErrorSeverity.MEDIUM:
                self._logger.warning("Error medio", **log_data)
            else:
                self._logger.info("Error bajo", **log_data)
                
        except Exception as e:
            self._logger.critical(f"Error registrando error en logs: {e}")
    
    # ==================== NOTIFICATIONS ====================
    
    def _show_error_notification(self, error_info: Dict[str, Any]):
        """
        Muestra una notificación de error al usuario.
        
        Args:
            error_info: Información del error
        """
        try:
            mapping = error_info["mapping"]
            context = error_info["context"]
            
            # Preparar mensaje
            title = f"Error en {context.operation}"
            message = mapping.user_message
            
            # Agregar detalles técnicos si está habilitado
            if self._show_technical_details and mapping.technical_message:
                message += f"\n\nDetalles técnicos: {mapping.technical_message}"
            
            # Preparar acciones
            actions = []
            
            # Acción de reintentar si está permitido
            if mapping.retry_allowed:
                actions.append({
                    "text": "Reintentar",
                    "on_click": lambda e: self._handle_retry_action(error_info)
                })
            
            # Acciones sugeridas
            for action_text in mapping.suggested_actions[:2]:  # Máximo 2 acciones
                actions.append({
                    "text": action_text,
                    "on_click": None  # Solo informativo
                })
            
            # Mostrar notificación según severidad
            if mapping.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                self.notification_manager.show_error(
                    title=title,
                    message=message,
                    actions=actions
                )
            elif mapping.severity == ErrorSeverity.MEDIUM:
                self.notification_manager.show_warning(
                    title=title,
                    message=message,
                    actions=actions
                )
            else:
                self.notification_manager.show_info(
                    title=title,
                    message=message,
                    actions=actions
                )
                
        except Exception as e:
            self._logger.error(f"Error mostrando notificación de error: {e}")
    
    def _handle_retry_action(self, error_info: Dict[str, Any]):
        """
        Maneja la acción de reintentar.
        
        Args:
            error_info: Información del error
        """
        try:
            # Por ahora solo mostrar mensaje
            self.notification_manager.show_info(
                title="Reintento",
                message="Para reintentar, vuelva a realizar la operación"
            )
        except Exception as e:
            self._logger.error(f"Error manejando acción de reintento: {e}")
    
    # ==================== METRICS ====================
    
    def _update_error_metrics(self, error_info: Dict[str, Any]):
        """
        Actualiza las métricas de errores.
        
        Args:
            error_info: Información del error
        """
        try:
            error_type = type(error_info["error"]).__name__
            self._error_counts[error_type] = self._error_counts.get(error_type, 0) + 1
        except Exception as e:
            self._logger.error(f"Error actualizando métricas: {e}")
    
    def _add_to_error_history(self, error_info: Dict[str, Any]):
        """
        Agrega un error al historial.
        
        Args:
            error_info: Información del error
        """
        try:
            # Preparar entrada del historial
            history_entry = {
                "error_id": error_info["error_id"],
                "timestamp": error_info["timestamp"],
                "error_type": type(error_info["error"]).__name__,
                "operation": error_info["context"].operation,
                "component": error_info["context"].component,
                "severity": error_info["mapping"].severity.value
            }
            
            # Agregar al historial
            self._last_errors.append(history_entry)
            
            # Mantener tamaño del historial
            if len(self._last_errors) > self._max_error_history:
                self._last_errors.pop(0)
                
        except Exception as e:
            self._logger.error(f"Error agregando al historial: {e}")
    
    def _generate_error_id(self) -> str:
        """
        Genera un ID único para el error.
        
        Returns:
            ID único del error
        """
        import uuid
        return str(uuid.uuid4())[:8]
    
    # ==================== PUBLIC UTILITIES ====================
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de errores.
        
        Returns:
            Estadísticas de errores
        """
        try:
            return {
                "total_errors": sum(self._error_counts.values()),
                "error_counts_by_type": self._error_counts.copy(),
                "recent_errors": len(self._last_errors),
                "error_history": self._last_errors[-10:]  # Últimos 10 errores
            }
        except Exception as e:
            self._logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def clear_error_history(self):
        """Limpia el historial de errores."""
        try:
            self._last_errors.clear()
            self._error_counts.clear()
            self._logger.debug("Historial de errores limpiado")
        except Exception as e:
            self._logger.error(f"Error limpiando historial: {e}")
    
    def set_technical_details_visibility(self, show_details: bool):
        """
        Configura la visibilidad de detalles técnicos.
        
        Args:
            show_details: Si mostrar detalles técnicos
        """
        self._show_technical_details = show_details
        self._logger.debug(f"Visibilidad de detalles técnicos: {show_details}")
