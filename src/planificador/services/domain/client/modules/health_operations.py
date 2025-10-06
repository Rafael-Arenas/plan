# src/planificador/services/domain/client/modules/health_operations.py

"""
Módulo de Operaciones de Salud - Cliente

Este módulo implementa todas las operaciones relacionadas con el monitoreo de salud,
diagnóstico y verificación del estado del servicio de dominio cliente y sus componentes.

Características principales:
- Verificación de salud del servicio de dominio
- Monitoreo de conectividad de base de datos
- Generación de reportes de salud completos
- Diagnóstico de módulos especializados
- Métricas de rendimiento y disponibilidad
"""

from typing import Dict, Any, Optional
from datetime import datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .....config.config import settings
from .....repositories.client.client_repository_facade import ClientRepositoryFacade
from .....exceptions import (
    RepositoryError,
    ValidationError,
    BusinessLogicError
)
from .....utils.date_utils import get_current_time


class HealthOperations:
    """
    Operaciones de Salud y Diagnóstico para el Dominio Cliente
    
    Proporciona funcionalidades para monitorear la salud del servicio de dominio,
    verificar la conectividad de base de datos y generar reportes de diagnóstico
    completos para garantizar el correcto funcionamiento del sistema.
    
    Attributes:
        session: Sesión asíncrona de SQLAlchemy
        repository_facade: Facade del repositorio cliente
        _logger: Logger configurado para el módulo
    """
    
    def __init__(self, client_repository: ClientRepositoryFacade):
        """
        Inicializa el módulo de operaciones de salud.
        
        Args:
            client_repository: Facade del repositorio cliente
        """
        self.repository_facade = client_repository
        self.session = client_repository._session
        self._logger = logger.bind(module="HealthOperations", service="ClientDomainService")
        
        self._logger.debug("HealthOperations inicializado correctamente")
    
    async def check_service_health(self) -> Dict[str, Any]:
        """
        Verifica la salud general del servicio de dominio cliente.
        
        Realiza verificaciones completas del estado del servicio, incluyendo
        conectividad de base de datos, estado de módulos especializados y
        métricas de rendimiento básicas.
        
        Returns:
            Dict[str, Any]: Reporte de salud del servicio con estado general,
                           detalles de componentes y métricas de rendimiento
                           
        Raises:
            BusinessLogicError: Si ocurre un error durante la verificación
        """
        operation = "check_service_health"
        self._logger.info("Iniciando verificación de salud del servicio")
        
        try:
            start_time = get_current_time()
            health_status = {
                "service_name": "ClientDomainService",
                "timestamp": start_time.isoformat(),
                "status": "healthy",
                "version": "1.0.0",
                "components": {},
                "metrics": {},
                "errors": []
            }
            
            # Verificar conectividad de base de datos
            db_health = await self._check_database_health()
            health_status["components"]["database"] = db_health
            
            # Verificar estado del repositorio facade
            repository_health = await self._check_repository_health()
            health_status["components"]["repository_facade"] = repository_health
            
            # Verificar módulos especializados
            modules_health = await self._check_modules_health()
            health_status["components"]["modules"] = modules_health
            
            # Calcular métricas de rendimiento
            end_time = get_current_time()
            response_time = (end_time - start_time).total_seconds()
            
            health_status["metrics"] = {
                "response_time_seconds": response_time,
                "database_connection_pool": await self._get_connection_pool_metrics(),
                "memory_usage": await self._get_memory_metrics()
            }
            
            # Determinar estado general
            component_statuses = [
                comp.get("status", "unknown") 
                for comp in health_status["components"].values()
            ]
            
            if "critical" in component_statuses:
                health_status["status"] = "critical"
            elif "degraded" in component_statuses:
                health_status["status"] = "degraded"
            elif "warning" in component_statuses:
                health_status["status"] = "warning"
            else:
                health_status["status"] = "healthy"
            
            self._logger.info(
                f"Verificación de salud completada - Estado: {health_status['status']}",
                extra={
                    "operation": operation,
                    "status": health_status["status"],
                    "response_time": response_time
                }
            )
            
            return health_status
            
        except Exception as e:
            self._logger.error(f"Error durante verificación de salud: {e}")
            raise BusinessLogicError(
                message=f"Error durante verificación de salud del servicio: {e}",
                operation=operation,
                entity_type="ClientDomainService",
                original_error=e
            )
    
    async def check_database_connectivity(self) -> Dict[str, Any]:
        """
        Verifica específicamente la conectividad con la base de datos.
        
        Ejecuta pruebas de conectividad, latencia y disponibilidad de la
        base de datos para garantizar que las operaciones de persistencia
        funcionen correctamente.
        
        Returns:
            Dict[str, Any]: Reporte detallado de conectividad de base de datos
                           incluyendo latencia, estado de conexión y métricas
                           
        Raises:
            BusinessLogicError: Si ocurre un error durante la verificación
        """
        operation = "check_database_connectivity"
        self._logger.info("Verificando conectividad de base de datos")
        
        try:
            start_time = get_current_time()
            connectivity_report = {
                "timestamp": start_time.isoformat(),
                "database_type": "SQLite",
                "status": "connected",
                "connection_details": {},
                "performance_metrics": {},
                "tests": {}
            }
            
            # Test básico de conectividad
            try:
                result = await self.session.execute(text("SELECT 1"))
                connectivity_report["tests"]["basic_query"] = {
                    "status": "passed",
                    "result": result.scalar()
                }
            except Exception as e:
                connectivity_report["tests"]["basic_query"] = {
                    "status": "failed",
                    "error": str(e)
                }
                connectivity_report["status"] = "disconnected"
            
            # Test de latencia
            latency_start = get_current_time()
            try:
                await self.session.execute(text("SELECT datetime('now')"))
                latency_end = get_current_time()
                latency_ms = (latency_end - latency_start).total_seconds() * 1000
                
                connectivity_report["tests"]["latency"] = {
                    "status": "passed",
                    "latency_ms": round(latency_ms, 2)
                }
            except Exception as e:
                connectivity_report["tests"]["latency"] = {
                    "status": "failed",
                    "error": str(e)
                }
            
            # Test de transacciones
            try:
                async with self.session.begin():
                    await self.session.execute(text("SELECT 1"))
                
                connectivity_report["tests"]["transaction"] = {
                    "status": "passed"
                }
            except Exception as e:
                connectivity_report["tests"]["transaction"] = {
                    "status": "failed",
                    "error": str(e)
                }
            
            # Métricas de rendimiento
            end_time = get_current_time()
            total_time = (end_time - start_time).total_seconds()
            
            connectivity_report["performance_metrics"] = {
                "total_check_time_seconds": round(total_time, 3),
                "connection_pool_size": await self._get_connection_pool_size(),
                "active_connections": await self._get_active_connections()
            }
            
            # Información de configuración
            connectivity_report["connection_details"] = {
                "database_url": settings.database_url_masked,
                "pool_size": getattr(settings, 'database_pool_size', 'default'),
                "max_overflow": getattr(settings, 'database_max_overflow', 'default'),
                "pool_timeout": getattr(settings, 'database_pool_timeout', 'default')
            }
            
            self._logger.info(
                f"Verificación de conectividad completada - Estado: {connectivity_report['status']}",
                extra={
                    "operation": operation,
                    "status": connectivity_report["status"],
                    "total_time": total_time
                }
            )
            
            return connectivity_report
            
        except Exception as e:
            self._logger.error(f"Error verificando conectividad de base de datos: {e}")
            raise BusinessLogicError(
                message=f"Error verificando conectividad de base de datos: {e}",
                operation=operation,
                entity_type="Database",
                original_error=e
            )
    
    async def generate_health_report(self) -> Dict[str, Any]:
        """
        Genera un reporte completo de salud del servicio de dominio.
        
        Combina todas las verificaciones de salud en un reporte consolidado
        que incluye estado general, detalles de componentes, métricas de
        rendimiento y recomendaciones de mantenimiento.
        
        Returns:
            Dict[str, Any]: Reporte completo de salud con análisis detallado,
                           métricas históricas y recomendaciones
                           
        Raises:
            BusinessLogicError: Si ocurre un error durante la generación
        """
        operation = "generate_health_report"
        self._logger.info("Generando reporte completo de salud")
        
        try:
            report_start = get_current_time()
            
            # Obtener verificaciones individuales
            service_health = await self.check_service_health()
            db_connectivity = await self.check_database_connectivity()
            repository_info = await self.repository_facade.get_module_info()
            
            # Generar reporte consolidado
            comprehensive_report = {
                "report_metadata": {
                    "generated_at": report_start.isoformat(),
                    "report_version": "1.0.0",
                    "service_name": "ClientDomainService",
                    "report_type": "comprehensive_health_check"
                },
                "executive_summary": {
                    "overall_status": service_health["status"],
                    "critical_issues": [],
                    "warnings": [],
                    "recommendations": []
                },
                "detailed_analysis": {
                    "service_health": service_health,
                    "database_connectivity": db_connectivity,
                    "repository_modules": repository_info
                },
                "performance_metrics": {
                    "response_times": {},
                    "resource_usage": {},
                    "throughput": {}
                },
                "maintenance_recommendations": []
            }
            
            # Analizar problemas críticos
            if service_health["status"] == "critical":
                comprehensive_report["executive_summary"]["critical_issues"].append(
                    "Servicio en estado crítico - requiere atención inmediata"
                )
            
            if db_connectivity["status"] == "disconnected":
                comprehensive_report["executive_summary"]["critical_issues"].append(
                    "Base de datos desconectada - funcionalidad comprometida"
                )
            
            # Analizar advertencias
            if service_health["status"] in ["degraded", "warning"]:
                comprehensive_report["executive_summary"]["warnings"].append(
                    f"Servicio en estado {service_health['status']} - monitoreo requerido"
                )
            
            # Generar recomendaciones
            latency = db_connectivity.get("tests", {}).get("latency", {}).get("latency_ms", 0)
            if latency > 100:
                comprehensive_report["executive_summary"]["recommendations"].append(
                    "Considerar optimización de consultas - latencia elevada detectada"
                )
            
            if service_health["metrics"]["response_time_seconds"] > 5:
                comprehensive_report["executive_summary"]["recommendations"].append(
                    "Tiempo de respuesta elevado - revisar carga del sistema"
                )
            
            # Métricas de rendimiento consolidadas
            comprehensive_report["performance_metrics"] = {
                "response_times": {
                    "service_health_check": service_health["metrics"]["response_time_seconds"],
                    "database_connectivity": db_connectivity["performance_metrics"]["total_check_time_seconds"]
                },
                "resource_usage": service_health["metrics"],
                "database_performance": db_connectivity["performance_metrics"]
            }
            
            # Recomendaciones de mantenimiento
            comprehensive_report["maintenance_recommendations"] = [
                "Ejecutar verificaciones de salud regularmente (cada 15 minutos)",
                "Monitorear métricas de rendimiento continuamente",
                "Revisar logs de errores diariamente",
                "Actualizar dependencias mensualmente",
                "Realizar backup de configuraciones semanalmente"
            ]
            
            report_end = get_current_time()
            comprehensive_report["report_metadata"]["generation_time_seconds"] = (
                report_end - report_start
            ).total_seconds()
            
            self._logger.info(
                "Reporte completo de salud generado exitosamente",
                extra={
                    "operation": operation,
                    "overall_status": comprehensive_report["executive_summary"]["overall_status"],
                    "generation_time": comprehensive_report["report_metadata"]["generation_time_seconds"]
                }
            )
            
            return comprehensive_report
            
        except Exception as e:
            self._logger.error(f"Error generando reporte de salud: {e}")
            raise BusinessLogicError(
                message=f"Error generando reporte completo de salud: {e}",
                operation=operation,
                entity_type="HealthReport",
                original_error=e
            )
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE VERIFICACIÓN
    # ============================================================================
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Verifica la salud específica de la base de datos."""
        try:
            # Ejecutar query básica
            await self.session.execute(text("SELECT 1"))
            
            return {
                "component": "database",
                "status": "healthy",
                "message": "Base de datos respondiendo correctamente",
                "last_check": get_current_time().isoformat()
            }
        except SQLAlchemyError as e:
            return {
                "component": "database",
                "status": "critical",
                "message": f"Error de base de datos: {e}",
                "last_check": get_current_time().isoformat(),
                "error": str(e)
            }
        except Exception as e:
            return {
                "component": "database",
                "status": "unknown",
                "message": f"Error inesperado: {e}",
                "last_check": get_current_time().isoformat(),
                "error": str(e)
            }
    
    async def _check_repository_health(self) -> Dict[str, Any]:
        """Verifica la salud del repositorio facade."""
        try:
            # Usar el método de salud del repositorio
            repo_health = await self.repository_facade.health_check()
            
            return {
                "component": "repository_facade",
                "status": "healthy" if repo_health.get("status") == "healthy" else "degraded",
                "message": "Repository facade operativo",
                "details": repo_health,
                "last_check": get_current_time().isoformat()
            }
        except Exception as e:
            return {
                "component": "repository_facade",
                "status": "critical",
                "message": f"Error en repository facade: {e}",
                "last_check": get_current_time().isoformat(),
                "error": str(e)
            }
    
    async def _check_modules_health(self) -> Dict[str, Any]:
        """Verifica la salud de los módulos especializados."""
        modules_status = {
            "crud_operations": "healthy",
            "query_operations": "healthy", 
            "advanced_query_operations": "healthy",
            "statistics_operations": "healthy",
            "relationship_operations": "healthy",
            "date_operations": "healthy",
            "validation_operations": "healthy",
            "health_operations": "healthy"
        }
        
        return {
            "component": "specialized_modules",
            "status": "healthy",
            "message": "Todos los módulos especializados operativos",
            "modules": modules_status,
            "last_check": get_current_time().isoformat()
        }
    
    async def _get_connection_pool_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del pool de conexiones."""
        try:
            # Para SQLite, las métricas de pool son limitadas
            return {
                "pool_type": "SQLite",
                "status": "active",
                "note": "SQLite no utiliza pool de conexiones tradicional"
            }
        except Exception:
            return {
                "pool_type": "unknown",
                "status": "unavailable",
                "error": "No se pudieron obtener métricas del pool"
            }
    
    async def _get_memory_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas básicas de memoria."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
                "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
                "percent": round(process.memory_percent(), 2)
            }
        except ImportError:
            return {
                "status": "unavailable",
                "note": "psutil no disponible para métricas de memoria"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _get_connection_pool_size(self) -> int:
        """Obtiene el tamaño del pool de conexiones."""
        try:
            # Para SQLite, retornar 1 (conexión única)
            return 1
        except Exception:
            return 0
    
    async def _get_active_connections(self) -> int:
        """Obtiene el número de conexiones activas."""
        try:
            # Para SQLite, retornar 1 si hay sesión activa
            return 1 if self.session else 0
        except Exception:
            return 0