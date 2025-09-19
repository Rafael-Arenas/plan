# src/planificador/repositories/alert/__init__.py

"""
Módulo de repositorio de alertas.

Este módulo proporciona una implementación completa del patrón Repository
para la gestión de alertas, incluyendo operaciones CRUD, consultas avanzadas,
estadísticas, gestión de estados y validaciones.

Componentes principales:
- AlertRepositoryFacade: Facade principal que integra todos los módulos
- IAlertRepository: Interfaz que define el contrato del repositorio
- Módulos especializados: CRUD, consultas, estadísticas, estados, validaciones

Ejemplo de uso:
    from planificador.repositories.alert import AlertRepositoryFacade
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async def example_usage(session: AsyncSession):
        alert_repo = AlertRepositoryFacade(session)
        alerts = await alert_repo.get_active_alerts()
        return alerts

Compatibilidad con versión anterior:
    # Las clases anteriores siguen disponibles para compatibilidad
    from planificador.repositories.alert import AlertRepository
"""

# Nuevas implementaciones con patrón Facade
from .alert_repository_facade import AlertRepositoryFacade
from .interfaces.alert_repository_interface import IAlertRepository
from .modules.crud_operations import CrudOperations
from .modules.query_operations import QueryOperations
from .modules.statistics_operations import StatisticsOperations
from .modules.state_manager import StateManager
from .modules.validation_operations import ValidationOperations

# Implementaciones anteriores (compatibilidad)
try:
    from .alert_repository import AlertRepository
    from .alert_query_builder import AlertQueryBuilder
    from .alert_statistics import AlertStatistics
    from .alert_state_manager import AlertStateManager
    from .alert_validator import AlertValidator
    
    # Alias para compatibilidad con el repositorio original
    AlertRepositoryRefactored = AlertRepository
    
    _legacy_available = True
except ImportError:
    _legacy_available = False

# Exportaciones principales
__all__ = [
    # Nuevas implementaciones (recomendadas)
    "AlertRepositoryFacade",
    "IAlertRepository",
    "CrudOperations",
    "QueryOperations", 
    "StatisticsOperations",
    "StateManager",
    "ValidationOperations",
]

# Agregar exportaciones legacy si están disponibles
if _legacy_available:
    __all__.extend([
        "AlertRepository",
        "AlertRepositoryRefactored",
        "AlertQueryBuilder",
        "AlertStatistics", 
        "AlertStateManager",
        "AlertValidator"
    ])

# Información del módulo
__version__ = "2.0.0"
__author__ = "AkGroup Development Team"
__description__ = "Repositorio completo para gestión de alertas con patrón Facade"