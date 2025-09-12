"""Módulo de operaciones de salud para el sistema de clientes.

Este módulo contiene la implementación de operaciones relacionadas con
el monitoreo y verificación de salud del sistema de repositorio de clientes.
"""

from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.database.repositories.client.interfaces.health_interface import (
    IHealthOperations,
)
from planificador.exceptions.repository.client_repository_exceptions import ClientRepositoryError
from planificador.utils.date_utils import get_current_time


class HealthOperations(IHealthOperations):
    """Implementación de operaciones de salud para el sistema de clientes.
    
    Esta clase maneja todas las operaciones relacionadas con el monitoreo
    y verificación de salud del sistema de repositorio de clientes.
    """

    def __init__(self, session: AsyncSession, modules: dict[str, Any]) -> None:
        """Inicializa las operaciones de salud.
        
        Args:
            session: Sesión de base de datos asíncrona
            modules: Diccionario con los módulos del sistema a monitorear
        """
        self.session = session
        self.modules = modules
        self._logger = logger.bind(component="HealthOperations")

    async def health_check(self) -> dict[str, Any]:
        """Realiza una verificación de salud del repositorio.
        
        Returns:
            Diccionario con información de salud del sistema
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la verificación
        """
        try:
            self._logger.debug("Iniciando verificación de salud del sistema")
            
            health_status = {
                "facade_status": "healthy",
                "modules": {},
                "timestamp": get_current_time().isoformat(),
            }

            # Verificar cada módulo realizando una operación simple
            await self._check_statistics_module(health_status)
            await self._check_advanced_query_module(health_status)
            await self._check_relationship_module(health_status)
            await self._check_crud_ops_module(health_status)
            await self._check_date_ops_module(health_status)

            # Determinar estado general
            unhealthy_modules = [
                k
                for k, v in health_status["modules"].items()
                if v != "healthy"
            ]
            if unhealthy_modules:
                health_status["facade_status"] = (
                    f"degraded - modules with issues: "
                    f"{', '.join(unhealthy_modules)}"
                )

            self._logger.debug(
                f"Health check completado - Estado: "
                f"{health_status['facade_status']}"
            )
            return health_status

        except Exception as e:
            self._logger.error(f"Error en health check: {e}")
            return {
                "facade_status": f"error: {e!s}",
                "modules": {},
                "timestamp": get_current_time().isoformat(),
            }

    async def get_module_info(self) -> dict[str, Any]:
        """Obtiene información del módulo y sus capacidades.
        
        Returns:
            Diccionario con información del módulo
            
        Raises:
            ClientRepositoryError: Si ocurre un error obteniendo la información
        """
        try:
            self._logger.debug("Obteniendo información de módulos")
            
            module_info = {
                "facade_version": "1.0.0",
                "initialized_at": get_current_time().isoformat(),
                "modules": {},
            }
            
            # Obtener información de cada módulo
            for module_name, module_instance in self.modules.items():
                if module_instance:
                    module_info["modules"][module_name] = {
                        "class_name": module_instance.__class__.__name__,
                        "status": "loaded",
                        "methods": [method for method in dir(module_instance) 
                                  if not method.startswith('_')]
                    }
                else:
                    module_info["modules"][module_name] = {
                        "class_name": "None",
                        "status": "not_loaded",
                        "methods": []
                    }
            
            return module_info
            
        except Exception as e:
            self._logger.error(f"Error obteniendo información de módulos: {e}")
            raise ClientRepositoryError(
                message=f"Error obteniendo información de módulos: {e}",
                operation="get_module_info",
                entity_type="HealthOperations",
                original_error=e
            )

    async def _check_statistics_module(self, health_status: dict[str, Any]) -> None:
        """Verifica el módulo de estadísticas."""
        try:
            if "statistics" in self.modules and self.modules["statistics"]:
                await self.modules["statistics"].get_client_counts_by_status()
                health_status["modules"]["statistics"] = "healthy"
            else:
                health_status["modules"]["statistics"] = "error: module not loaded"
        except Exception as e:
            health_status["modules"]["statistics"] = f"error: {e!s}"

    async def _check_advanced_query_module(self, health_status: dict[str, Any]) -> None:
        """Verifica el módulo de advanced query."""
        try:
            if "advanced_query" in self.modules and self.modules["advanced_query"]:
                await self.modules["advanced_query"].get_active_clients()
                health_status["modules"]["advanced_query"] = "healthy"
            else:
                health_status["modules"]["advanced_query"] = "error: module not loaded"
        except Exception as e:
            health_status["modules"]["advanced_query"] = f"error: {e!s}"

    async def _check_relationship_module(self, health_status: dict[str, Any]) -> None:
        """Verifica el módulo de gestión de relaciones."""
        try:
            if "relationship" in self.modules and self.modules["relationship"]:
                await self.modules["relationship"].get_client_project_count(1)
                health_status["modules"]["relationship"] = "healthy"
            else:
                health_status["modules"]["relationship"] = "error: module not loaded"
        except Exception as e:
            health_status["modules"]["relationship"] = f"error: {e!s}"

    async def _check_crud_ops_module(self, health_status: dict[str, Any]) -> None:
        """Verifica el módulo de operaciones CRUD."""
        try:
            if "crud_ops" in self.modules and self.modules["crud_ops"]:
                if hasattr(self.modules["crud_ops"], 'get_client_by_id'):
                    health_status["modules"]["crud_ops"] = "healthy"
                else:
                    health_status["modules"]["crud_ops"] = "error: missing methods"
            else:
                health_status["modules"]["crud_ops"] = "error: module not loaded"
        except Exception as e:
            health_status["modules"]["crud_ops"] = f"error: {e!s}"

    async def _check_date_ops_module(self, health_status: dict[str, Any]) -> None:
        """Verifica el módulo de operaciones de fechas."""
        try:
            if "date_ops" in self.modules and self.modules["date_ops"]:
                if hasattr(self.modules["date_ops"], 'get_clients_created_in_date_range'):
                    health_status["modules"]["date_ops"] = "healthy"
                else:
                    health_status["modules"]["date_ops"] = "error: missing methods"
            else:
                health_status["modules"]["date_ops"] = "error: module not loaded"
        except Exception as e:
            health_status["modules"]["date_ops"] = f"error: {e!s}"