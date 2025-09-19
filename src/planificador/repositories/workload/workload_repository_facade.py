# src/planificador/repositories/workload/workload_repository_facade.py

"""
Fachada del Repositorio Workload.

Este módulo implementa el patrón Facade para el repositorio de cargas de trabajo,
proporcionando una interfaz unificada y simplificada para todas las
operaciones relacionadas con la gestión de cargas de trabajo de empleados.

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
        facade = WorkloadRepositoryFacade(session)
        workload = await facade.create_workload(workload_data)
        workloads = await facade.get_workloads_by_employee(employee_id)
        stats = await facade.get_employee_workload_statistics(employee_id)
    ```
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from planificador.models.workload import Workload
from planificador.repositories.workload.interfaces import (
    IWorkloadCrudOperations,
    IWorkloadQueryOperations,
    IWorkloadValidationOperations,
    IWorkloadRelationshipOperations,
    IWorkloadStatisticsOperations
)
from planificador.repositories.workload.modules import (
    WorkloadCrudModule,
    WorkloadQueryModule,
    WorkloadValidationModule,
    WorkloadRelationshipModule,
    WorkloadStatisticsModule
)
from planificador.exceptions.repository import WorkloadRepositoryError


class WorkloadRepositoryFacade(
    IWorkloadCrudOperations,
    IWorkloadQueryOperations,
    IWorkloadValidationOperations,
    IWorkloadRelationshipOperations,
    IWorkloadStatisticsOperations
):
    """
    Fachada del repositorio Workload que unifica todas las operaciones.
    
    Implementa las interfaces de CRUD, consultas, validación, relaciones y estadísticas,
    delegando las operaciones a los módulos especializados correspondientes.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        crud_module: Módulo para operaciones CRUD
        query_module: Módulo para operaciones de consulta
        validation_module: Módulo para operaciones de validación
        relationship_module: Módulo para operaciones de relaciones
        statistics_module: Módulo para operaciones de estadísticas
    """

    def __init__(self, session: AsyncSession):
        """Inicializa la fachada con sesión de BD y módulos especializados."""
        self.session = session
        self._logger = logger.bind(module="workload_repository_facade")
        
        # Inicializar módulos especializados
        self.crud_module = WorkloadCrudModule(session)
        self.query_module = WorkloadQueryModule(session)
        self.validation_module = WorkloadValidationModule(session)
        self.relationship_module = WorkloadRelationshipModule(session)
        self.statistics_module = WorkloadStatisticsModule(session)
        
        self._logger.debug("WorkloadRepositoryFacade inicializada")

    # =============================================================================
    # OPERACIONES CRUD
    # =============================================================================

    async def create_workload(self, workload_data: Dict[str, Any]) -> Workload:
        """Crea una nueva carga de trabajo."""
        return await self.crud_module.create_workload(workload_data)

    async def update_workload(
        self,
        workload_id: int,
        workload_data: Dict[str, Any]
    ) -> Workload:
        """Actualiza una carga de trabajo existente."""
        return await self.crud_module.update_workload(workload_id, workload_data)

    async def delete_workload(self, workload_id: int) -> bool:
        """Elimina una carga de trabajo."""
        return await self.crud_module.delete_workload(workload_id)

    async def get_workload_by_id(self, workload_id: int) -> Optional[Workload]:
        """Obtiene una carga de trabajo por ID."""
        return await self.crud_module.get_workload_by_id(workload_id)

    async def get_by_unique_field(
        self,
        field_name: str,
        field_value: Any
    ) -> Optional[Workload]:
        """Obtiene una carga de trabajo por campo único."""
        return await self.crud_module.get_by_unique_field(field_name, field_value)

    # Alias para compatibilidad con la interfaz
    async def add_workload(self, workload_data: Dict[str, Any]) -> Workload:
        """Alias para create_workload."""
        return await self.create_workload(workload_data)

    async def find_workload_by_id(self, workload_id: int) -> Optional[Workload]:
        """Alias para get_workload_by_id."""
        return await self.get_workload_by_id(workload_id)

    async def modify_workload(
        self,
        workload_id: int,
        workload_data: Dict[str, Any]
    ) -> Workload:
        """Alias para update_workload."""
        return await self.update_workload(workload_id, workload_data)

    async def remove_workload(self, workload_id: int) -> bool:
        """Alias para delete_workload."""
        return await self.delete_workload(workload_id)

    # =============================================================================
    # OPERACIONES DE CONSULTA
    # =============================================================================

    async def get_workloads_by_employee(
        self,
        employee_id: int,
        active_only: bool = True
    ) -> List[Workload]:
        """Obtiene cargas de trabajo por empleado."""
        return await self.query_module.get_workloads_by_employee(employee_id, active_only)

    async def get_workloads_by_project(
        self,
        project_id: int,
        active_only: bool = True
    ) -> List[Workload]:
        """Obtiene cargas de trabajo por proyecto."""
        return await self.query_module.get_workloads_by_project(project_id, active_only)

    async def get_workloads_by_date_range(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> List[Workload]:
        """Obtiene cargas de trabajo por rango de fechas."""
        return await self.query_module.get_workloads_by_date_range(
            start_date, end_date, employee_id
        )

    async def get_workloads_by_status(
        self,
        status: str,
        employee_id: Optional[int] = None
    ) -> List[Workload]:
        """Obtiene cargas de trabajo por estado."""
        return await self.query_module.get_workloads_by_status(status, employee_id)

    async def search_workloads_by_criteria(
        self,
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Workload]:
        """Busca cargas de trabajo por criterios."""
        return await self.query_module.search_workloads_by_criteria(criteria, limit, offset)

    async def get_workloads_with_pagination(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Workload], int]:
        """Obtiene cargas de trabajo con paginación."""
        return await self.query_module.get_workloads_with_pagination(page, page_size, filters)

    async def count_workloads(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Cuenta cargas de trabajo con filtros opcionales."""
        return await self.query_module.count_workloads(filters)

    # Alias para compatibilidad con la interfaz
    async def find_workloads_by_employee(
        self,
        employee_id: int,
        active_only: bool = True
    ) -> List[Workload]:
        """Alias para get_workloads_by_employee."""
        return await self.get_workloads_by_employee(employee_id, active_only)

    async def find_workloads_by_project(
        self,
        project_id: int,
        active_only: bool = True
    ) -> List[Workload]:
        """Alias para get_workloads_by_project."""
        return await self.get_workloads_by_project(project_id, active_only)

    # =============================================================================
    # OPERACIONES DE VALIDACIÓN
    # =============================================================================

    async def validate_workload_data(self, workload_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida datos de carga de trabajo."""
        return await self.validation_module.validate_workload_data(workload_data)

    async def validate_workload_hours(
        self,
        employee_id: int,
        hours: float,
        work_date: date
    ) -> Dict[str, Any]:
        """Valida horas de trabajo."""
        return await self.validation_module.validate_workload_hours(employee_id, hours, work_date)

    async def validate_workload_status(self, status: str) -> Dict[str, Any]:
        """Valida estado de carga de trabajo."""
        return await self.validation_module.validate_workload_status(status)

    async def validate_workload_description(self, description: str) -> Dict[str, Any]:
        """Valida descripción de carga de trabajo."""
        return await self.validation_module.validate_workload_description(description)

    async def validate_workload_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Valida rango de fechas."""
        return await self.validation_module.validate_workload_date_range(start_date, end_date)

    async def check_workload_duplicates(
        self,
        employee_id: int,
        project_id: int,
        work_date: date,
        exclude_workload_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Verifica duplicados de carga de trabajo."""
        return await self.validation_module.check_workload_duplicates(
            employee_id, project_id, work_date, exclude_workload_id
        )

    async def validate_employee_daily_hours(
        self,
        employee_id: int,
        work_date: date,
        additional_hours: float,
        exclude_workload_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Valida horas diarias del empleado."""
        return await self.validation_module.validate_employee_daily_hours(
            employee_id, work_date, additional_hours, exclude_workload_id
        )

    async def validate_data_consistency(self) -> Dict[str, Any]:
        """Valida consistencia de datos."""
        return await self.validation_module.validate_data_consistency()

    # =============================================================================
    # OPERACIONES DE RELACIONES
    # =============================================================================

    async def get_workload_with_employee_details(
        self,
        workload_id: int
    ) -> Optional[Dict[str, Any]]:
        """Obtiene carga de trabajo con detalles del empleado."""
        return await self.relationship_module.get_workload_with_employee_details(workload_id)

    async def get_workload_with_project_details(
        self,
        workload_id: int
    ) -> Optional[Dict[str, Any]]:
        """Obtiene carga de trabajo con detalles del proyecto."""
        return await self.relationship_module.get_workload_with_project_details(workload_id)

    async def get_workloads_with_relationships(
        self,
        workload_ids: Optional[List[int]] = None,
        include_employee: bool = True,
        include_project: bool = True
    ) -> List[Dict[str, Any]]:
        """Obtiene cargas de trabajo con relaciones."""
        return await self.relationship_module.get_workloads_with_relationships(
            workload_ids, include_employee, include_project
        )

    async def validate_employee_exists(self, employee_id: int) -> bool:
        """Valida que el empleado existe."""
        return await self.relationship_module.validate_employee_exists(employee_id)

    async def validate_project_exists(self, project_id: int) -> bool:
        """Valida que el proyecto existe."""
        return await self.relationship_module.validate_project_exists(project_id)

    async def get_employee_project_associations(
        self,
        employee_id: int
    ) -> List[Dict[str, Any]]:
        """Obtiene asociaciones empleado-proyecto."""
        return await self.relationship_module.get_employee_project_associations(employee_id)

    async def analyze_workload_dependencies(
        self,
        workload_id: int
    ) -> Dict[str, Any]:
        """Analiza dependencias de carga de trabajo."""
        return await self.relationship_module.analyze_workload_dependencies(workload_id)

    # =============================================================================
    # OPERACIONES DE ESTADÍSTICAS
    # =============================================================================

    async def get_employee_workload_statistics(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de carga de trabajo por empleado."""
        return await self.statistics_module.get_employee_workload_statistics(
            employee_id, start_date, end_date
        )

    async def get_project_workload_statistics(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de carga de trabajo por proyecto."""
        return await self.statistics_module.get_project_workload_statistics(
            project_id, start_date, end_date
        )

    async def get_team_workload_statistics(
        self,
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de carga de trabajo por equipo."""
        return await self.statistics_module.get_team_workload_statistics(
            team_id, start_date, end_date
        )

    async def get_workload_trends_analysis(
        self,
        start_date: date,
        end_date: date,
        granularity: str = "weekly"
    ) -> List[Dict[str, Any]]:
        """Obtiene análisis de tendencias de carga de trabajo."""
        return await self.statistics_module.get_workload_trends_analysis(
            start_date, end_date, granularity
        )

    async def get_workload_distribution_analysis(
        self,
        analysis_type: str = "by_employee",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Obtiene análisis de distribución de carga de trabajo."""
        return await self.statistics_module.get_workload_distribution_analysis(
            analysis_type, start_date, end_date
        )

    async def calculate_productivity_metrics(
        self,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Calcula métricas de productividad."""
        return await self.statistics_module.calculate_productivity_metrics(
            employee_id, project_id, start_date, end_date
        )

    # =============================================================================
    # OPERACIONES COMPUESTAS Y AVANZADAS
    # =============================================================================

    async def create_workload_with_validation(
        self,
        workload_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea una carga de trabajo con validación completa.
        
        Realiza todas las validaciones necesarias antes de crear la carga de trabajo,
        incluyendo validación de datos, duplicados, horas diarias y reglas de negocio.
        
        Args:
            workload_data: Datos de la carga de trabajo a crear
            
        Returns:
            Dict con el resultado de la operación y la carga de trabajo creada
            
        Raises:
            WorkloadRepositoryError: Si hay errores en la validación o creación
        """
        try:
            self._logger.info(f"Iniciando creación de carga de trabajo con validación")
            
            # Validar datos básicos
            validation_result = await self.validate_workload_data(workload_data)
            if not validation_result.get("is_valid", False):
                return {
                    "success": False,
                    "error": "Datos de carga de trabajo inválidos",
                    "validation_errors": validation_result.get("errors", []),
                    "workload": None
                }
            
            # Validar duplicados
            duplicate_check = await self.check_workload_duplicates(
                workload_data["employee_id"],
                workload_data["project_id"],
                workload_data["work_date"]
            )
            if duplicate_check.get("has_duplicates", False):
                return {
                    "success": False,
                    "error": "Ya existe una carga de trabajo para este empleado, proyecto y fecha",
                    "validation_errors": [duplicate_check.get("message", "")],
                    "workload": None
                }
            
            # Validar horas diarias
            hours_validation = await self.validate_employee_daily_hours(
                workload_data["employee_id"],
                workload_data["work_date"],
                workload_data["hours"]
            )
            if not hours_validation.get("is_valid", False):
                return {
                    "success": False,
                    "error": "Las horas exceden el límite diario permitido",
                    "validation_errors": [hours_validation.get("message", "")],
                    "workload": None
                }
            
            # Crear la carga de trabajo
            workload = await self.create_workload(workload_data)
            
            self._logger.info(f"Carga de trabajo creada exitosamente: {workload.id}")
            
            return {
                "success": True,
                "message": "Carga de trabajo creada exitosamente",
                "workload": workload,
                "validation_results": {
                    "data_validation": validation_result,
                    "duplicate_check": duplicate_check,
                    "hours_validation": hours_validation
                }
            }
            
        except Exception as e:
            self._logger.error(f"Error en create_workload_with_validation: {e}")
            raise WorkloadRepositoryError(
                message=f"Error al crear carga de trabajo con validación: {e}",
                operation="create_workload_with_validation",
                entity_type="Workload",
                original_error=e
            )

    async def get_workload_dashboard_data(
        self,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        team_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene datos completos para el dashboard de cargas de trabajo.
        
        Combina estadísticas, tendencias y métricas para proporcionar
        una vista completa del estado de las cargas de trabajo.
        
        Args:
            employee_id: ID del empleado (opcional)
            project_id: ID del proyecto (opcional)
            team_id: ID del equipo (opcional)
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            
        Returns:
            Dict con datos completos del dashboard
        """
        try:
            self._logger.info("Obteniendo datos del dashboard de cargas de trabajo")
            
            dashboard_data = {
                "summary": {},
                "statistics": {},
                "trends": [],
                "distribution": {},
                "productivity": {}
            }
            
            # Obtener estadísticas según el contexto
            if employee_id:
                dashboard_data["statistics"] = await self.get_employee_workload_statistics(
                    employee_id, start_date, end_date
                )
            elif project_id:
                dashboard_data["statistics"] = await self.get_project_workload_statistics(
                    project_id, start_date, end_date
                )
            elif team_id:
                dashboard_data["statistics"] = await self.get_team_workload_statistics(
                    team_id, start_date, end_date
                )
            
            # Obtener análisis de tendencias si hay fechas
            if start_date and end_date:
                dashboard_data["trends"] = await self.get_workload_trends_analysis(
                    start_date, end_date, "weekly"
                )
            
            # Obtener análisis de distribución
            dashboard_data["distribution"] = await self.get_workload_distribution_analysis(
                "by_employee", start_date, end_date
            )
            
            # Calcular métricas de productividad
            dashboard_data["productivity"] = await self.calculate_productivity_metrics(
                employee_id, project_id, start_date, end_date
            )
            
            # Resumen general
            total_workloads = await self.count_workloads({
                "employee_id": employee_id,
                "project_id": project_id,
                "start_date": start_date,
                "end_date": end_date
            } if any([employee_id, project_id, start_date, end_date]) else None)
            
            dashboard_data["summary"] = {
                "total_workloads": total_workloads,
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                },
                "context": {
                    "employee_id": employee_id,
                    "project_id": project_id,
                    "team_id": team_id
                }
            }
            
            return dashboard_data
            
        except Exception as e:
            self._logger.error(f"Error en get_workload_dashboard_data: {e}")
            raise WorkloadRepositoryError(
                message=f"Error al obtener datos del dashboard: {e}",
                operation="get_workload_dashboard_data",
                entity_type="Workload",
                original_error=e
            )

    async def bulk_workload_operation(
        self,
        operation: str,
        workload_data_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Realiza operaciones en lote sobre cargas de trabajo.
        
        Permite crear, actualizar o eliminar múltiples cargas de trabajo
        en una sola operación, con manejo de errores individual.
        
        Args:
            operation: Tipo de operación ("create", "update", "delete")
            workload_data_list: Lista de datos de cargas de trabajo
            
        Returns:
            Lista de resultados de cada operación
        """
        try:
            self._logger.info(f"Iniciando operación en lote: {operation}")
            
            results = []
            
            for i, workload_data in enumerate(workload_data_list):
                try:
                    if operation == "create":
                        result = await self.create_workload_with_validation(workload_data)
                    elif operation == "update":
                        workload_id = workload_data.get("id")
                        if not workload_id:
                            raise ValueError("ID de carga de trabajo requerido para actualización")
                        workload = await self.update_workload(workload_id, workload_data)
                        result = {"success": True, "workload": workload}
                    elif operation == "delete":
                        workload_id = workload_data.get("id")
                        if not workload_id:
                            raise ValueError("ID de carga de trabajo requerido para eliminación")
                        success = await self.delete_workload(workload_id)
                        result = {"success": success, "workload_id": workload_id}
                    else:
                        raise ValueError(f"Operación no soportada: {operation}")
                    
                    results.append({
                        "index": i,
                        "success": True,
                        "result": result
                    })
                    
                except Exception as e:
                    self._logger.error(f"Error en operación {i}: {e}")
                    results.append({
                        "index": i,
                        "success": False,
                        "error": str(e),
                        "workload_data": workload_data
                    })
            
            self._logger.info(f"Operación en lote completada: {len(results)} elementos procesados")
            return results
            
        except Exception as e:
            self._logger.error(f"Error en bulk_workload_operation: {e}")
            raise WorkloadRepositoryError(
                message=f"Error en operación en lote: {e}",
                operation="bulk_workload_operation",
                entity_type="Workload",
                original_error=e
            )