# src/planificador/repositories/status_code/status_code_repository_facade.py

"""
Fachada del Repositorio StatusCode.

Este módulo implementa el patrón Facade para el repositorio de códigos de estado,
proporcionando una interfaz unificada y simplificada para todas las
operaciones relacionadas con la gestión de códigos de estado del sistema.

Arquitectura:
    - Implementa múltiples interfaces especializadas
    - Delega operaciones a módulos específicos
    - Maneja la sesión de base de datos de forma centralizada
    - Proporciona logging y manejo de errores consistente

Principios de Diseño:
    - Single Responsibility: Cada módulo tiene una responsabilidad específica
    - Dependency Injection: Los módulos se inyectan como dependencias
    - Interface Segregation: Interfaces pequeñas y específicas
    - Open/Closed: Extensible sin modificar código existente
    - Facade Pattern: Interfaz unificada para subsistemas complejos

Uso:
    ```python
    async with get_async_session() as session:
        facade = StatusCodeRepositoryFacade(session)
        status_code = await facade.create_status_code(status_code_data)
        codes = await facade.get_all_status_codes()
        stats = await facade.get_status_code_statistics()
    ```
"""

from typing import List, Optional, Dict, Any, Tuple
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from planificador.models.status_code import StatusCode
from planificador.repositories.status_code.interfaces import (
    IStatusCodeCrudOperations,
    IStatusCodeQueryOperations,
    IStatusCodeValidationOperations,
    IStatusCodeStatisticsOperations
)
from planificador.repositories.status_code.modules import (
    StatusCodeCrudModule,
    StatusCodeQueryModule,
    StatusCodeValidationModule,
    StatusCodeStatisticsModule
)
from planificador.exceptions.repository import StatusCodeRepositoryError
from planificador.exceptions.repository.base_repository_exceptions import RepositoryError
from planificador.exceptions.base import ValidationError, NotFoundError, ConflictError, BusinessLogicError


def handle_repository_errors(operation_name: str):
    """
    Decorador para manejar errores de repositorio de forma consistente.
    
    Args:
        operation_name: Nombre de la operación para contexto en errores
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await func(self, *args, **kwargs)
            except (ValidationError, NotFoundError, ConflictError, BusinessLogicError) as e:
                # Las excepciones específicas del dominio se propagan sin modificar
                self._logger.debug(f"Excepción de dominio en {operation_name}: {e}")
                raise
            except SQLAlchemyError as e:
                self._logger.error(f"Error de SQLAlchemy en {operation_name}: {e}")
                raise RepositoryError(
                    message=f"Error de base de datos en {operation_name}: {str(e)}",
                    operation=operation_name,
                    entity_type="StatusCode",
                    original_error=e
                )
            except Exception as e:
                self._logger.error(f"Error inesperado en {operation_name}: {e}")
                raise RepositoryError(
                    message=f"Error inesperado en {operation_name}: {str(e)}",
                    operation=operation_name,
                    entity_type="StatusCode",
                    original_error=e
                )
        return wrapper
    return decorator


class StatusCodeRepositoryFacade(
    IStatusCodeCrudOperations,
    IStatusCodeQueryOperations,
    IStatusCodeValidationOperations,
    IStatusCodeStatisticsOperations
):
    """
    Fachada del repositorio StatusCode que unifica todas las operaciones.
    
    Implementa las interfaces de CRUD, consultas, validación y estadísticas,
    delegando las operaciones a los módulos especializados correspondientes.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        crud_module: Módulo para operaciones CRUD
        query_module: Módulo para operaciones de consulta
        validation_module: Módulo para operaciones de validación
        statistics_module: Módulo para operaciones de estadísticas
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el facade del repositorio StatusCode.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self._session = session
        self._logger = logger.bind(component="StatusCodeRepositoryFacade")
        
        # Inicializar módulos especializados
        self._crud_module = StatusCodeCrudModule(session)
        self._query_module = StatusCodeQueryModule(session)
        self._validation_module = StatusCodeValidationModule(session)
        self._statistics_module = StatusCodeStatisticsModule(session)
        
        self._logger.debug("StatusCodeRepositoryFacade inicializado")

    # ==========================================
    # OPERACIONES CRUD
    # ==========================================

    @handle_repository_errors("create_status_code")
    async def create_status_code(self, status_code_data: Dict[str, Any]) -> StatusCode:
        """Crea un nuevo código de estado."""
        return await self._crud_module.create_status_code(status_code_data)

    @handle_repository_errors("get_status_code_by_id")
    async def get_status_code_by_id(self, status_code_id: int) -> Optional[StatusCode]:
        """Obtiene un código de estado por su ID."""
        return await self._crud_module.get_status_code_by_id(status_code_id)

    @handle_repository_errors("get_all_status_codes")
    async def get_all_status_codes(self) -> List[StatusCode]:
        """Obtiene todos los códigos de estado."""
        return await self._crud_module.get_all_status_codes()

    @handle_repository_errors("update_status_code")
    async def update_status_code(self, status_code_id: int, updated_data: Dict[str, Any]) -> Optional[StatusCode]:
        """Actualiza un código de estado existente."""
        return await self._crud_module.update_status_code(status_code_id, updated_data)

    @handle_repository_errors("delete_status_code")
    async def delete_status_code(self, status_code_id: int) -> bool:
        """Elimina un código de estado."""
        return await self._crud_module.delete_status_code(status_code_id)

    # ==========================================
    # OPERACIONES DE CONSULTA
    # ==========================================

    async def find_by_code(self, code: str) -> Optional[StatusCode]:
        """Busca un código de estado por su código único."""
        return await self._query_module.find_by_code(code)

    async def find_by_name(self, name: str) -> Optional[StatusCode]:
        """Busca un código de estado por su nombre."""
        return await self._query_module.find_by_name(name)

    async def find_by_text_search(self, search_text: str) -> List[StatusCode]:
        """Busca códigos de estado por texto en código, nombre o descripción."""
        return await self._query_module.find_by_text_search(search_text)

    async def find_active_status_codes(self) -> List[StatusCode]:
        """Obtiene todos los códigos de estado activos."""
        return await self._query_module.find_active_status_codes()

    async def find_inactive_status_codes(self) -> List[StatusCode]:
        """Obtiene todos los códigos de estado inactivos."""
        return await self._query_module.find_inactive_status_codes()

    async def find_default_status_codes(self) -> List[StatusCode]:
        """Obtiene todos los códigos de estado marcados como por defecto."""
        return await self._query_module.find_default_status_codes()

    async def find_by_display_order_range(self, min_order: int, max_order: int) -> List[StatusCode]:
        """Busca códigos de estado en un rango de orden de visualización."""
        return await self._query_module.find_by_display_order_range(min_order, max_order)

    async def find_with_advanced_filters(self, filters: Dict[str, Any]) -> List[StatusCode]:
        """Busca códigos de estado con filtros avanzados."""
        return await self._query_module.find_with_advanced_filters(filters)

    async def get_status_codes_paginated(self, page: int, page_size: int, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[StatusCode], int]:
        """Obtiene códigos de estado paginados con filtros opcionales."""
        if filters is not None:
            return await self._query_module.get_status_codes_paginated(page, page_size, filters)
        else:
            return await self._query_module.get_status_codes_paginated(page, page_size)

    async def get_ordered_status_codes(self, order_by: str = "sort_order", ascending: bool = True) -> List[StatusCode]:
        """Obtiene códigos de estado ordenados."""
        return await self._query_module.get_ordered_status_codes(order_by, ascending)

    # ==========================================
    # OPERACIONES DE VALIDACIÓN
    # ==========================================

    async def validate_unique_code(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """Valida que un código sea único."""
        if exclude_id is not None:
            return await self._validation_module.validate_unique_code(code, exclude_id)
        else:
            return await self._validation_module.validate_unique_code(code)

    async def validate_unique_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Valida que un nombre sea único."""
        if exclude_id is not None:
            return await self._validation_module.validate_unique_name(name, exclude_id)
        else:
            return await self._validation_module.validate_unique_name(name)

    async def validate_status_code_data(self, status_code_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Valida los datos de un código de estado."""
        return await self._validation_module.validate_status_code_data(status_code_data)

    async def validate_display_order_conflicts(self, display_order: int) -> List[StatusCode]:
        """Valida conflictos en el orden de visualización."""
        return await self._validation_module.validate_display_order_conflicts(display_order)

    async def validate_default_status_rules(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida las reglas de negocio para códigos por defecto."""
        return await self._validation_module.validate_default_status_rules(status_data)

    # ==========================================
    # OPERACIONES DE ESTADÍSTICAS
    # ==========================================

    async def get_status_code_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de códigos de estado."""
        return await self._statistics_module.get_status_code_statistics()

    async def get_status_distribution_analysis(self) -> Dict[str, Any]:
        """Obtiene análisis de distribución de códigos de estado."""
        return await self._statistics_module.get_status_distribution_analysis()

    async def get_display_order_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del orden de visualización."""
        return await self._statistics_module.get_display_order_metrics()

    async def get_usage_performance_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de rendimiento de uso."""
        return await self._statistics_module.get_usage_performance_metrics()

    async def get_data_integrity_report(self) -> Dict[str, Any]:
        """Obtiene reporte de integridad de datos."""
        return await self._statistics_module.get_data_integrity_report()

    async def get_status_code_health_check(self) -> Dict[str, Any]:
        """Obtiene verificación de salud del sistema de códigos de estado."""
        return await self._statistics_module.get_status_code_health_check()

    # ==========================================
    # MÉTODOS DE UTILIDAD Y MANTENIMIENTO
    # ==========================================

    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud del facade y sus módulos.
        
        Returns:
            Dict con información del estado de cada módulo
        """
        health_status = {
            "facade": "healthy",
            "session": "connected" if self._session else "disconnected",
            "modules": {}
        }
        
        # Verificar cada módulo
        modules = {
            "crud": self._crud_module,
            "query": self._query_module,
            "validation": self._validation_module,
            "statistics": self._statistics_module
        }
        
        for module_name, module in modules.items():
            try:
                # Verificar que el módulo tenga los métodos esperados
                if hasattr(module, '__class__'):
                    health_status["modules"][module_name] = "healthy"
                else:
                    health_status["modules"][module_name] = "unhealthy"
            except Exception as e:
                health_status["modules"][module_name] = f"error: {str(e)}"
                self._logger.error(f"Error en health check del módulo {module_name}: {e}")
        
        return health_status

    def get_module_info(self) -> Dict[str, str]:
        """
        Obtiene información sobre los módulos cargados.
        
        Returns:
            Dict con información de cada módulo
        """
        return {
            "crud_module": str(self._crud_module.__class__.__name__),
            "query_module": str(self._query_module.__class__.__name__),
            "validation_module": str(self._validation_module.__class__.__name__),
            "statistics_module": str(self._statistics_module.__class__.__name__)
        }

    def __str__(self) -> str:
        """Representación en string del facade."""
        return f"StatusCodeRepositoryFacade(session={self._session})"

    def __repr__(self) -> str:
        """Representación detallada del facade."""
        return (
            f"StatusCodeRepositoryFacade("
            f"session={self._session}, "
            f"modules=['crud', 'query', 'validation', 'statistics']"
            f")"
        )


    # ==========================================
    # IMPLEMENTACIÓN DE INTERFACES CRUD
    # ==========================================

    @handle_repository_errors("create")
    async def create(self, entity_data: Dict[str, Any]) -> StatusCode:
        """Implementa IStatusCodeCrudOperations.create"""
        return await self._crud_module.create_status_code(entity_data)

    @handle_repository_errors("update")
    async def update(self, entity_id: int, **update_data) -> StatusCode:
        """Implementa IStatusCodeCrudOperations.update"""
        return await self._crud_module.update_status_code(entity_id, update_data)

    @handle_repository_errors("get_by_id")
    async def get_by_id(self, entity_id: int) -> Optional[StatusCode]:
        """Implementa IStatusCodeCrudOperations.get_by_id"""
        return await self._crud_module.get_status_code_by_id(entity_id)

    @handle_repository_errors("delete")
    async def delete(self, entity_id: int) -> bool:
        """Implementa IStatusCodeCrudOperations.delete"""
        return await self._crud_module.delete_status_code(entity_id)

    @handle_repository_errors("get_all")
    async def get_all(self) -> List[StatusCode]:
        """Implementa IStatusCodeCrudOperations.get_all"""
        return await self._crud_module.get_all_status_codes()

    @handle_repository_errors("exists")
    async def exists(self, entity_id: int) -> bool:
        """Implementa IStatusCodeCrudOperations.exists"""
        status_code = await self._crud_module.get_status_code_by_id(entity_id)
        return status_code is not None

    # ==========================================
    # IMPLEMENTACIÓN DE INTERFACES QUERY
    # ==========================================

    async def get_by_code(self, code: str) -> Optional[StatusCode]:
        """Implementa IStatusCodeQueryOperations.get_by_code"""
        return await self._query_module.get_by_code(code)

    async def search_by_name(self, search_term: str) -> List[StatusCode]:
        """Implementa IStatusCodeQueryOperations.search_by_name"""
        return await self._query_module.search_by_name(search_term)

    async def get_active_status_codes(self) -> List[StatusCode]:
        """Implementa IStatusCodeQueryOperations.get_active_status_codes"""
        return await self._query_module.get_by_is_active(True)

    async def get_billable_status_codes(self) -> List[StatusCode]:
        """Implementa IStatusCodeQueryOperations.get_billable_status_codes"""
        # Buscar códigos activos y facturables
        criteria = {"is_active": True, "is_billable": True}
        return await self._query_module.search_by_criteria(criteria)

    async def get_productive_status_codes(self) -> List[StatusCode]:
        """Implementa IStatusCodeQueryOperations.get_productive_status_codes"""
        # Buscar códigos activos y productivos
        criteria = {"is_active": True, "is_productive": True}
        return await self._query_module.search_by_criteria(criteria)

    async def get_status_codes_requiring_approval(self) -> List[StatusCode]:
        """Implementa IStatusCodeQueryOperations.get_status_codes_requiring_approval"""
        # Buscar códigos activos que requieren aprobación
        criteria = {"is_active": True, "requires_approval": True}
        return await self._query_module.search_by_criteria(criteria)

    # ==========================================
    # IMPLEMENTACIÓN DE INTERFACES VALIDATION
    # ==========================================

    async def validate_code_uniqueness(
        self, 
        code: str, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """Implementa IStatusCodeValidationOperations.validate_code_uniqueness"""
        return await self._validation_module.is_code_unique(code, exclude_id)

    async def validate_status_code_can_be_deleted(self, entity_id: int) -> bool:
        """Implementa IStatusCodeValidationOperations.validate_status_code_can_be_deleted"""
        # Verificar que el código de estado existe
        status_code = await self._crud_module.get_status_code_by_id(entity_id)
        if not status_code:
            return False
        
        # Verificar reglas de negocio para eliminación
        # Por ejemplo, no se puede eliminar si es el código por defecto
        if hasattr(status_code, 'is_default') and status_code.is_default:
            return False
        
        return True

    async def validate_status_code_can_be_deactivated(self, entity_id: int) -> bool:
        """Implementa IStatusCodeValidationOperations.validate_status_code_can_be_deactivated"""
        # Verificar que el código de estado existe
        status_code = await self._crud_module.get_status_code_by_id(entity_id)
        if not status_code:
            return False
        
        # Verificar reglas de negocio para desactivación
        # Por ejemplo, no se puede desactivar si es el código por defecto
        if hasattr(status_code, 'is_default') and status_code.is_default:
            return False
        
        return True

    async def validate_business_rules(self, entity_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Implementa IStatusCodeValidationOperations.validate_business_rules"""
        is_valid, errors = await self._validation_module.validate_status_code_data(entity_data)
        return {"errors": errors if not is_valid else []}

    async def validate_sort_order_uniqueness(
        self, 
        sort_order: int, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """Implementa IStatusCodeValidationOperations.validate_sort_order_uniqueness"""
        return await self._validation_module.is_display_order_unique(sort_order, exclude_id)

    # ==========================================
    # IMPLEMENTACIÓN DE INTERFACES STATISTICS
    # ==========================================

    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Implementa IStatusCodeStatisticsOperations.get_usage_statistics"""
        return await self._statistics_module.get_performance_metrics()

    async def get_distribution_by_characteristics(self) -> Dict[str, Any]:
        """Implementa IStatusCodeStatisticsOperations.get_distribution_by_characteristics"""
        return await self._statistics_module.get_status_distribution()

    async def get_sort_order_analysis(self) -> Dict[str, Any]:
        """Implementa IStatusCodeStatisticsOperations.get_sort_order_analysis"""
        return await self._statistics_module.get_display_order_statistics()

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Implementa IStatusCodeStatisticsOperations.get_performance_metrics"""
        return await self._statistics_module.get_performance_metrics()

    async def get_integrity_report(self) -> Dict[str, Any]:
        """Implementa IStatusCodeStatisticsOperations.get_integrity_report"""
        return await self._statistics_module.get_integrity_report()

    # ==========================================
    # IMPLEMENTACIÓN DE INTERFACES PRINCIPALES
    # ==========================================

    async def filter_by_criteria(
        self,
        is_active: Optional[bool] = None,
        is_billable: Optional[bool] = None,
        is_productive: Optional[bool] = None,
        requires_approval: Optional[bool] = None,
        search_term: Optional[str] = None
    ) -> List[StatusCode]:
        """Implementa IStatusCodeRepository.filter_by_criteria"""
        criteria = {}
        if is_active is not None:
            criteria["is_active"] = is_active
        if is_billable is not None:
            criteria["is_billable"] = is_billable
        if is_productive is not None:
            criteria["is_productive"] = is_productive
        if requires_approval is not None:
            criteria["requires_approval"] = requires_approval
        if search_term is not None:
            criteria["search_term"] = search_term
        
        return await self._query_module.search_by_criteria(criteria)

    async def get_max_sort_order(self) -> int:
        """Implementa IStatusCodeRepository.get_max_sort_order"""
        # Obtener estadísticas de orden de visualización
        order_stats = await self._statistics_module.get_display_order_statistics()
        return order_stats.get("max_display_order", 0)

    async def reorder_status_codes(self, code_order_mapping: Dict[str, int]) -> bool:
        """Implementa IStatusCodeRepository.reorder_status_codes"""
        try:
            # Actualizar cada código con su nuevo orden
            for code, new_order in code_order_mapping.items():
                status_code = await self._query_module.get_by_code(code)
                if status_code:
                    await self._crud_module.update_status_code(
                        status_code.id, 
                        {"display_order": new_order}
                    )
            return True
        except Exception as e:
            self._logger.error(f"Error reordenando códigos de estado: {e}")
            return False