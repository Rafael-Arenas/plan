"""Módulo de operaciones de salud para el sistema de clientes.

Este módulo contiene la implementación de operaciones relacionadas con
el monitoreo y verificación de salud del sistema de repositorio de clientes.
"""

from typing import Any

import pendulum
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.repositories.base_repository import BaseRepository
from ..interfaces.health_interface import IHealthOperations


class HealthOperations(IHealthOperations):
    """Implementación de operaciones de salud para el sistema de clientes.

    Esta clase maneja todas las operaciones relacionadas con el monitoreo
    y verificación de salud del sistema de repositorio de clientes.
    """

    def __init__(self, session: AsyncSession, modules: dict[str, Any]) -> None:
        """Inicializa las operaciones de salud.

        Args:
            session: Sesión de base de datos asíncrona.
            modules: Diccionario con los módulos del sistema a monitorear.
        """
        self.session = session
        self.modules = modules
        self._logger = logger.bind(component="HealthOperations")
        self._logger.debug("HealthOperations inicializado")

    async def health_check(self) -> dict[str, Any]:
        """Realiza una verificación de salud del repositorio.

        Returns:
            Diccionario con información de salud del sistema.
        """
        self._logger.debug("Iniciando verificación de salud del sistema")
        health_status = {
            "facade_status": "healthy",
            "modules": {},
            "timestamp": pendulum.now().isoformat(),
        }

        for name, module in self.modules.items():
            await self._check_module(name, module, health_status)

        unhealthy = [
            k for k, v in health_status["modules"].items() if v != "healthy"
        ]
        if unhealthy:
            health_status["facade_status"] = (
                f"degraded - issues in: {', '.join(unhealthy)}"
            )

        self._logger.debug(
            f"Health check completado - Estado: {health_status['facade_status']}"
        )
        return health_status

    async def _check_module(
        self, name: str, module: Any, health_status: dict[str, Any]
    ) -> None:
        """Verifica un módulo de forma genérica."""
        try:
            if not module:
                health_status["modules"][name] = "error: module not loaded"
                return

            if isinstance(module, BaseRepository):
                # Realiza una operación de conteo simple y de bajo impacto
                await module.count()
                health_status["modules"][name] = "healthy"
            elif hasattr(module, "health_check") and callable(
                module.health_check
            ):
                # Si el módulo tiene su propio health_check, lo usamos
                await module.health_check()
                health_status["modules"][name] = "healthy"
            else:
                # Si no, asumimos que está bien si está cargado
                health_status["modules"][name] = "loaded (no check performed)"

        except Exception as e:
            self._logger.error(f"Error en health check para módulo {name}: {e}")
            health_status["modules"][name] = f"error: {e!s}"

    async def get_module_info(self) -> dict[str, Any]:
        """Obtiene información del módulo y sus capacidades.

        Returns:
            Diccionario con información del módulo.
        """
        self._logger.debug("Obteniendo información de módulos")
        module_info = {
            "facade_version": "2.0.0",  # Versión actualizada
            "initialized_at": pendulum.now().isoformat(),
            "modules": {},
        }

        for name, module in self.modules.items():
            if module:
                module_info["modules"][name] = {
                    "class_name": module.__class__.__name__,
                    "status": "loaded",
                    "methods": [
                        method
                        for method in dir(module)
                        if not method.startswith("_")
                    ],
                }
            else:
                module_info["modules"][name] = {
                    "class_name": "None",
                    "status": "not_loaded",
                    "methods": [],
                }

        return module_info