# src/planificador/services/infrastructure/logging_service.py

"""
Servicio de logging avanzado.

Este módulo proporciona funcionalidades de logging estructurado
y avanzado que complementan loguru para el proyecto.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager
import traceback
import asyncio
from functools import wraps

from loguru import logger

from ...exceptions.infrastructure import (
    FileSystemError,
    create_file_system_error
)
from ...utils.date_utils import get_current_datetime
from ...config.config import get_settings


class LogLevel(Enum):
    """
    Niveles de logging disponibles.
    """
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(Enum):
    """
    Formatos de logging disponibles.
    """
    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"
    STRUCTURED = "structured"


@dataclass
class LogContext:
    """
    Contexto adicional para logs.
    """
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    operation: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=get_current_datetime)


@dataclass
class PerformanceMetrics:
    """
    Métricas de rendimiento para logging.
    """
    operation: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    extra_metrics: Optional[Dict[str, Any]] = None


class LogFormatter:
    """
    Formateador personalizado para logs.
    """
    
    @staticmethod
    def simple_format(record: Dict[str, Any]) -> str:
        """
        Formato simple para logs.
        
        Args:
            record: Registro de log.
            
        Returns:
            Log formateado.
        """
        return (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} - "
            "{message}\n"
        )
    
    @staticmethod
    def detailed_format(record: Dict[str, Any]) -> str:
        """
        Formato detallado para logs.
        
        Args:
            record: Registro de log.
            
        Returns:
            Log formateado.
        """
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{process.id}:{thread.id} | "
            "{name}:{function}:{line} | "
            "{elapsed} - "
            "{message}\n"
            "{exception}"
        )
    
    @staticmethod
    def json_format(record: Dict[str, Any]) -> str:
        """
        Formato JSON para logs.
        
        Args:
            record: Registro de log.
            
        Returns:
            Log en formato JSON.
        """
        log_data = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "process_id": record["process"].id,
            "thread_id": record["thread"].id,
            "elapsed": str(record["elapsed"])
        }
        
        # Agregar excepción si existe
        if record["exception"]:
            log_data["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
                "traceback": record["exception"].traceback
            }
        
        # Agregar datos extra
        if "extra" in record and record["extra"]:
            log_data["extra"] = record["extra"]
        
        return json.dumps(log_data, ensure_ascii=False) + "\n"
    
    @staticmethod
    def structured_format(record: Dict[str, Any]) -> str:
        """
        Formato estructurado para logs.
        
        Args:
            record: Registro de log.
            
        Returns:
            Log estructurado.
        """
        base_format = (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line}"
        )
        
        # Agregar contexto si existe
        if "extra" in record and record["extra"]:
            extra_parts = []
            for key, value in record["extra"].items():
                if isinstance(value, (str, int, float, bool)):
                    extra_parts.append(f"{key}={value}")
            
            if extra_parts:
                base_format += " | " + " ".join(extra_parts)
        
        base_format += " - {message}\n{exception}"
        return base_format


class LoggingService:
    """
    Servicio de logging avanzado.
    
    Proporciona funcionalidades de logging estructurado,
    métricas de rendimiento y gestión de contexto.
    """
    
    def __init__(self):
        """
        Inicializa el servicio de logging.
        """
        self.settings = get_settings()
        self.context_stack: List[LogContext] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        self.handlers: Dict[str, int] = {}
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """
        Configura el sistema de logging.
        """
        try:
            # Remover handlers por defecto
            logger.remove()
            
            # Configurar handler para consola
            self._setup_console_handler()
            
            # Configurar handler para archivo si está configurado
            if self.settings.log_file:
                self._setup_file_handler()
            
            # Configurar handler para errores críticos
            self._setup_error_handler()
            
            logger.info("Sistema de logging configurado correctamente")
        
        except Exception as e:
            # Fallback a configuración básica
            logger.add(sys.stderr, level="INFO")
            logger.error(f"Error al configurar logging, usando configuración básica: {e}")
    
    def _setup_console_handler(self) -> None:
        """
        Configura el handler para consola.
        """
        format_func = LogFormatter.simple_format
        
        if self.settings.debug:
            format_func = LogFormatter.detailed_format
        
        handler_id = logger.add(
            sys.stderr,
            format=format_func,
            level=self.settings.log_level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        self.handlers["console"] = handler_id
    
    def _setup_file_handler(self) -> None:
        """
        Configura el handler para archivo.
        """
        try:
            log_file_path = Path(self.settings.log_file)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Handler para logs generales
            handler_id = logger.add(
                str(log_file_path),
                format=LogFormatter.structured_format,
                level=self.settings.log_level,
                rotation="10 MB",
                retention="30 days",
                compression="gz",
                backtrace=True,
                diagnose=True,
                enqueue=True  # Para thread safety
            )
            
            self.handlers["file"] = handler_id
        
        except Exception as e:
            logger.warning(f"No se pudo configurar logging a archivo: {e}")
    
    def _setup_error_handler(self) -> None:
        """
        Configura handler específico para errores críticos.
        """
        try:
            error_log_path = Path(self.settings.logs_dir) / "errors.log"
            error_log_path.parent.mkdir(parents=True, exist_ok=True)
            
            handler_id = logger.add(
                str(error_log_path),
                format=LogFormatter.json_format,
                level="ERROR",
                rotation="5 MB",
                retention="90 days",
                compression="gz",
                backtrace=True,
                diagnose=True,
                enqueue=True
            )
            
            self.handlers["error"] = handler_id
        
        except Exception as e:
            logger.warning(f"No se pudo configurar logging de errores: {e}")
    
    def add_custom_handler(self, name: str, sink: Any, **kwargs) -> None:
        """
        Agrega un handler personalizado.
        
        Args:
            name: Nombre del handler.
            sink: Destino del log (archivo, función, etc.).
            **kwargs: Argumentos adicionales para loguru.
        """
        try:
            handler_id = logger.add(sink, **kwargs)
            self.handlers[name] = handler_id
            logger.info(f"Handler personalizado agregado: {name}")
        except Exception as e:
            logger.error(f"Error al agregar handler {name}: {e}")
            raise create_file_system_error(
                message=f"Error al agregar handler de logging: {e}",
                operation="add_handler",
                file_path=str(sink) if isinstance(sink, (str, Path)) else "custom",
                original_error=e
            )
    
    def remove_handler(self, name: str) -> None:
        """
        Remueve un handler.
        
        Args:
            name: Nombre del handler a remover.
        """
        if name in self.handlers:
            try:
                logger.remove(self.handlers[name])
                del self.handlers[name]
                logger.info(f"Handler removido: {name}")
            except Exception as e:
                logger.warning(f"Error al remover handler {name}: {e}")
    
    @contextmanager
    def log_context(self, context: LogContext):
        """
        Context manager para agregar contexto a los logs.
        
        Args:
            context: Contexto a agregar.
        """
        self.context_stack.append(context)
        
        # Configurar contexto en loguru
        context_dict = {
            "user_id": context.user_id,
            "session_id": context.session_id,
            "request_id": context.request_id,
            "operation": context.operation,
            "module": context.module,
            "function": context.function
        }
        
        # Filtrar valores None
        context_dict = {k: v for k, v in context_dict.items() if v is not None}
        
        if context.extra_data:
            context_dict.update(context.extra_data)
        
        with logger.contextualize(**context_dict):
            try:
                yield
            finally:
                if self.context_stack:
                    self.context_stack.pop()
    
    def log_with_context(self, level: LogLevel, message: str, 
                        context: Optional[LogContext] = None, **kwargs) -> None:
        """
        Registra un log con contexto.
        
        Args:
            level: Nivel del log.
            message: Mensaje del log.
            context: Contexto adicional.
            **kwargs: Datos adicionales.
        """
        if context:
            with self.log_context(context):
                logger.log(level.value, message, **kwargs)
        else:
            # Usar contexto actual si existe
            current_context = self.context_stack[-1] if self.context_stack else None
            if current_context and current_context.extra_data:
                kwargs.update(current_context.extra_data)
            
            logger.log(level.value, message, **kwargs)
    
    def log_performance(self, metrics: PerformanceMetrics) -> None:
        """
        Registra métricas de rendimiento.
        
        Args:
            metrics: Métricas a registrar.
        """
        self.performance_metrics.append(metrics)
        
        # Calcular duración si no está calculada
        if metrics.end_time and not metrics.duration_ms:
            duration = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            metrics.duration_ms = duration
        
        log_data = {
            "operation": metrics.operation,
            "duration_ms": metrics.duration_ms,
            "success": metrics.success,
            "memory_usage_mb": metrics.memory_usage_mb,
            "cpu_usage_percent": metrics.cpu_usage_percent
        }
        
        if metrics.error_message:
            log_data["error_message"] = metrics.error_message
        
        if metrics.extra_metrics:
            log_data.update(metrics.extra_metrics)
        
        level = LogLevel.INFO if metrics.success else LogLevel.WARNING
        self.log_with_context(
            level=level,
            message=f"Performance: {metrics.operation}",
            **log_data
        )
    
    @contextmanager
    def performance_monitor(self, operation: str, **extra_metrics):
        """
        Context manager para monitorear rendimiento.
        
        Args:
            operation: Nombre de la operación.
            **extra_metrics: Métricas adicionales.
        """
        start_time = get_current_datetime()
        metrics = PerformanceMetrics(
            operation=operation,
            start_time=start_time,
            extra_metrics=extra_metrics
        )
        
        try:
            yield metrics
            metrics.success = True
        except Exception as e:
            metrics.success = False
            metrics.error_message = str(e)
            raise
        finally:
            metrics.end_time = get_current_datetime()
            self.log_performance(metrics)
    
    def log_exception(self, exception: Exception, context: Optional[LogContext] = None,
                     additional_info: Optional[Dict[str, Any]] = None) -> None:
        """
        Registra una excepción con contexto completo.
        
        Args:
            exception: Excepción a registrar.
            context: Contexto adicional.
            additional_info: Información adicional.
        """
        error_data = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc()
        }
        
        if additional_info:
            error_data.update(additional_info)
        
        self.log_with_context(
            level=LogLevel.ERROR,
            message=f"Excepción capturada: {type(exception).__name__}",
            context=context,
            **error_data
        )
    
    def get_performance_summary(self, operation_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene un resumen de las métricas de rendimiento.
        
        Args:
            operation_filter: Filtrar por operación específica.
            
        Returns:
            Resumen de métricas.
        """
        filtered_metrics = self.performance_metrics
        
        if operation_filter:
            filtered_metrics = [
                m for m in self.performance_metrics 
                if m.operation == operation_filter
            ]
        
        if not filtered_metrics:
            return {"total_operations": 0}
        
        durations = [m.duration_ms for m in filtered_metrics if m.duration_ms]
        successful = sum(1 for m in filtered_metrics if m.success)
        
        summary = {
            "total_operations": len(filtered_metrics),
            "successful_operations": successful,
            "failed_operations": len(filtered_metrics) - successful,
            "success_rate": successful / len(filtered_metrics) if filtered_metrics else 0
        }
        
        if durations:
            summary.update({
                "avg_duration_ms": sum(durations) / len(durations),
                "min_duration_ms": min(durations),
                "max_duration_ms": max(durations)
            })
        
        return summary
    
    def clear_performance_metrics(self) -> None:
        """
        Limpia las métricas de rendimiento almacenadas.
        """
        self.performance_metrics.clear()
        logger.debug("Métricas de rendimiento limpiadas")


def log_async_function(operation_name: Optional[str] = None):
    """
    Decorador para logging automático de funciones asíncronas.
    
    Args:
        operation_name: Nombre de la operación (opcional).
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            context = LogContext(
                operation=op_name,
                module=func.__module__,
                function=func.__name__
            )
            
            with logging_service.log_context(context):
                with logging_service.performance_monitor(op_name):
                    try:
                        logger.debug(f"Iniciando operación: {op_name}")
                        result = await func(*args, **kwargs)
                        logger.debug(f"Operación completada: {op_name}")
                        return result
                    except Exception as e:
                        logging_service.log_exception(e, context)
                        raise
        
        return wrapper
    return decorator


def log_function(operation_name: Optional[str] = None):
    """
    Decorador para logging automático de funciones síncronas.
    
    Args:
        operation_name: Nombre de la operación (opcional).
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            context = LogContext(
                operation=op_name,
                module=func.__module__,
                function=func.__name__
            )
            
            with logging_service.log_context(context):
                with logging_service.performance_monitor(op_name):
                    try:
                        logger.debug(f"Iniciando operación: {op_name}")
                        result = func(*args, **kwargs)
                        logger.debug(f"Operación completada: {op_name}")
                        return result
                    except Exception as e:
                        logging_service.log_exception(e, context)
                        raise
        
        return wrapper
    return decorator


# Instancia global del servicio de logging
logging_service = LoggingService()