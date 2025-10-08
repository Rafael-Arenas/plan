"""
Servicio de Dominio Principal para Asignaciones de Proyecto.

Este módulo implementa el patrón Facade proporcionando un punto de acceso
unificado a todas las operaciones del dominio de asignaciones de proyecto.
"""

from typing import Dict, List, Any, Optional, Union
import pendulum
from loguru import logger

from ....repositories.project_assignment.project_assignment_repository_facade import ProjectAssignmentRepositoryFacade
from .interfaces import IProjectAssignmentDomainService
from .modules import (
    CrudOperations,
    EmployeeQueries,
    ProjectQueries,
    SearchOperations,
    ResourceManagement,
    StatisticsOperations,
    ValidationOperations,
    DiagnosticOperations
)
from planificador.exceptions import RepositoryError, ValidationError, NotFoundError
from planificador.schemas import (
    ProjectAssignmentCreate,
    ProjectAssignmentUpdate,
    ProjectAssignment
)
from planificador.schemas.assignment.advanced_schemas import AssignmentAdvancedFilters


class ProjectAssignmentDomainService(IProjectAssignmentDomainService):
    """
    Servicio de Dominio Principal para Asignaciones de Proyecto.
    
    Implementa el patrón Facade proporcionando una interfaz unificada
    para todas las operaciones del dominio de asignaciones de proyecto.
    
    Organización modular según documentación oficial:
    1. Operaciones CRUD Principales (4 métodos)
    2. Operaciones CRUD Especializadas (3 métodos)  
    3. Operaciones de Consulta por Empleado (5 métodos)
    4. Operaciones de Consulta por Proyecto (4 métodos)
    5. Operaciones de Búsqueda y Filtrado (4 métodos)
    6. Operaciones de Gestión de Recursos (3 métodos)
    7. Operaciones de Estadísticas Básicas (4 métodos)
    8. Operaciones de Estadísticas Avanzadas (4 métodos)
    9. Operaciones de Validación y Reglas de Negocio (5 métodos)
    10. Operaciones de Diagnóstico y Salud (2 métodos)
    
    Características principales:
    - Punto de acceso único para todas las operaciones
    - Encapsulación de la complejidad interna
    - Coordinación entre múltiples módulos especializados
    - Manejo centralizado de transacciones y errores
    - Logging estructurado y trazabilidad completa
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """
        Inicializa el servicio de dominio con todos sus módulos.
        
        Args:
            repository_facade: Fachada del repositorio para acceso a datos
        """
        self._repository = repository_facade
        self._logger = logger.bind(service="project_assignment_domain")
        
        # Inicializar todos los módulos especializados
        self._crud_ops = CrudOperations(repository_facade)
        self._employee_queries = EmployeeQueries(repository_facade)
        self._project_queries = ProjectQueries(repository_facade)
        self._search_ops = SearchOperations(repository_facade)
        self._resource_mgmt = ResourceManagement(repository_facade)
        self._statistics_ops = StatisticsOperations(repository_facade)
        self._validation_ops = ValidationOperations(repository_facade)
        self._diagnostic_ops = DiagnosticOperations(repository_facade)
        
        self._logger.info("Servicio de dominio de asignaciones de proyecto inicializado")

    # ==========================================
    # 1. OPERACIONES CRUD PRINCIPALES (4 métodos)
    # ==========================================
    
    async def create_assignment(
        self, 
        assignment_data: ProjectAssignmentCreate
    ) -> ProjectAssignment:
        """Crea una nueva asignación con validaciones completas de negocio."""
        self._logger.info(f"Creando asignación para empleado {assignment_data.employee_id}")
        return await self._crud_ops.create_assignment(assignment_data)
    
    async def update_assignment(
        self, 
        assignment_id: int, 
        update_data: ProjectAssignmentUpdate
    ) -> ProjectAssignment:
        """Actualiza una asignación existente con validaciones de solapamiento."""
        self._logger.info(f"Actualizando asignación {assignment_id}")
        return await self._crud_ops.update_assignment(assignment_id, update_data)
    
    async def delete_assignment(self, assignment_id: int) -> bool:
        """Elimina una asignación después de validar dependencias y impacto."""
        self._logger.info(f"Eliminando asignación {assignment_id}")
        return await self._crud_ops.delete_assignment(assignment_id)
    
    async def get_assignment_by_id(self, assignment_id: int) -> Optional[ProjectAssignment]:
        """Obtiene una asignación por su ID único con datos relacionados."""
        return await self._crud_ops.get_assignment_by_id(assignment_id)
    
    # ==========================================
    # 2. OPERACIONES CRUD ESPECIALIZADAS (3 métodos)
    # ==========================================
    
    async def bulk_create_assignments(
        self, 
        assignments_data: List[ProjectAssignmentCreate]
    ) -> List[ProjectAssignment]:
        """Crea múltiples asignaciones en una operación transaccional con validaciones cruzadas."""
        self._logger.info(f"Creando {len(assignments_data)} asignaciones en lote")
        return await self._crud_ops.bulk_create_assignments(assignments_data)
    
    async def duplicate_assignment(
        self, 
        assignment_id: int, 
        modifications: Optional[Dict[str, Any]] = None
    ) -> ProjectAssignment:
        """Duplica una asignación existente con nuevos parámetros."""
        self._logger.info(f"Duplicando asignación {assignment_id}")
        return await self._crud_ops.duplicate_assignment(assignment_id, modifications)
    
    async def archive_assignment(self, assignment_id: int) -> ProjectAssignment:
        """Archiva una asignación manteniendo el historial para auditoría."""
        self._logger.info(f"Archivando asignación {assignment_id}")
        return await self._crud_ops.archive_assignment(assignment_id)
    
    # ==========================================
    # 3. OPERACIONES DE CONSULTA POR EMPLEADO (5 métodos)
    # ==========================================
    
    async def get_assignments_by_employee(
        self, 
        employee_id: int, 
        include_inactive: bool = False
    ) -> List[ProjectAssignment]:
        """Obtiene todas las asignaciones de un empleado específico."""
        self._logger.info(f"Obteniendo asignaciones del empleado {employee_id}")
        return await self._employee_queries.get_assignments_by_employee(
            employee_id, include_inactive
        )
    
    async def get_active_assignments_by_employee(
        self, 
        employee_id: int, 
        reference_date: Optional[pendulum.Date] = None
    ) -> List[ProjectAssignment]:
        """Obtiene las asignaciones activas de un empleado en una fecha específica."""
        self._logger.info(f"Obteniendo asignaciones activas del empleado {employee_id}")
        return await self._employee_queries.get_active_assignments_by_employee(
            employee_id, reference_date
        )
    
    async def get_employee_workload_summary(
        self, 
        employee_id: int, 
        start_date: pendulum.Date, 
        end_date: pendulum.Date
    ) -> Dict[str, Any]:
        """Genera un resumen completo de la carga de trabajo de un empleado."""
        self._logger.info(f"Generando resumen de carga de trabajo para empleado {employee_id}")
        return await self._employee_queries.get_employee_workload_summary(
            employee_id, start_date, end_date
        )
    
    async def get_employee_assignment_history(
        self, 
        employee_id: int, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene el historial cronológico de asignaciones de un empleado."""
        self._logger.info(f"Obteniendo historial de asignaciones del empleado {employee_id}")
        return await self._employee_queries.get_employee_assignment_history(
            employee_id, limit
        )
    
    async def get_employee_current_allocation(self, employee_id: int) -> Dict[str, Any]:
        """Obtiene la asignación actual detallada de un empleado."""
        self._logger.info(f"Obteniendo asignación actual del empleado {employee_id}")
        return await self._employee_queries.get_employee_current_allocation(employee_id)
    
    # ==========================================
    # 4. OPERACIONES DE CONSULTA POR PROYECTO (4 métodos)
    # ==========================================
    
    async def get_assignments_by_project(self, project_id: int) -> List[ProjectAssignment]:
        """Obtiene todas las asignaciones de un proyecto específico."""
        self._logger.info(f"Obteniendo asignaciones del proyecto {project_id}")
        return await self._project_queries.get_assignments_by_project(project_id)
    
    async def get_project_team_summary(self, project_id: int) -> Dict[str, Any]:
        """Obtiene un resumen completo del equipo asignado al proyecto."""
        self._logger.info(f"Generando resumen de equipo para proyecto {project_id}")
        return await self._project_queries.get_project_team_summary(project_id)
    
    async def get_project_resource_allocation(self, project_id: int) -> Dict[str, Any]:
        """Analiza la distribución de recursos y capacidades del proyecto."""
        self._logger.info(f"Analizando asignación de recursos para proyecto {project_id}")
        return await self._project_queries.get_project_resource_allocation(project_id)
    
    async def get_project_assignment_timeline(
        self, 
        project_id: int, 
        include_milestones: bool = True
    ) -> Dict[str, Any]:
        """Genera una línea de tiempo detallada de las asignaciones del proyecto."""
        self._logger.info(f"Generando timeline de asignaciones para proyecto {project_id}")
        return await self._project_queries.get_project_assignment_timeline(
            project_id, include_milestones
        )
    
    # ==========================================
    # 5. OPERACIONES DE BÚSQUEDA Y FILTRADO (4 métodos)
    # ==========================================
    
    async def search_assignments_by_criteria(
        self, 
        criteria: Dict[str, Any]
    ) -> List[ProjectAssignment]:
        """Busca asignaciones aplicando criterios múltiples de filtrado."""
        self._logger.info(f"Buscando asignaciones con criterios: {criteria}")
        return await self._search_ops.search_assignments_by_criteria(criteria)
    
    async def get_assignments_by_date_range(
        self, 
        start_date: pendulum.Date, 
        end_date: pendulum.Date,
        include_partial_overlap: bool = True
    ) -> List[ProjectAssignment]:
        """Obtiene asignaciones que se encuentran en un rango de fechas específico."""
        self._logger.info(f"Obteniendo asignaciones entre {start_date} y {end_date}")
        return await self._search_ops.get_assignments_by_date_range(
            start_date, end_date, include_partial_overlap
        )
    
    async def get_assignments_by_role(
        self, 
        role: str,
        exact_match: bool = False
    ) -> List[ProjectAssignment]:
        """Busca asignaciones por rol específico en el proyecto."""
        self._logger.info(f"Buscando asignaciones por rol: {role}")
        return await self._search_ops.get_assignments_by_role(role, exact_match)
    
    async def get_overlapping_assignments(
        self, 
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        threshold_percentage: float = 100.0
    ) -> List[Dict[str, Any]]:
        """Detecta solapamientos entre asignaciones de empleados o proyectos."""
        self._logger.info(f"Detectando solapamientos - empleado: {employee_id}, proyecto: {project_id}")
        return await self._search_ops.get_overlapping_assignments(
            employee_id, project_id, threshold_percentage
        )
    
    # ==========================================
    # 6. OPERACIONES DE GESTIÓN DE RECURSOS (3 métodos)
    # ==========================================
    
    async def assign_employee_to_project(
        self,
        employee_id: int,
        project_id: int,
        assignment_data: Dict[str, Any]
    ) -> ProjectAssignment:
        """Asigna un empleado a un proyecto específico."""
        return await self._resource_mgmt.assign_employee_to_project(
            employee_id, project_id, assignment_data
        )
    
    async def reassign_employee(
        self,
        assignment_id: int,
        new_project_id: int,
        reassignment_data: Optional[Dict[str, Any]] = None
    ) -> ProjectAssignment:
        """Reasigna un empleado de un proyecto a otro."""
        return await self._resource_mgmt.reassign_employee(
            assignment_id, new_project_id, reassignment_data
        )
    
    async def calculate_employee_utilization(
        self,
        employee_id: int,
        date_range: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calcula la utilización de recursos de un empleado específico."""
        return await self._resource_mgmt.calculate_employee_utilization(
            employee_id, date_range
        )
    
    # ==========================================
    # 7. OPERACIONES DE ESTADÍSTICAS BÁSICAS (4 métodos)
    # ==========================================
    
    async def get_total_assignments_count(
        self, 
        start_date: Optional[pendulum.Date] = None, 
        end_date: Optional[pendulum.Date] = None
    ) -> int:
        """Obtiene el conteo total de asignaciones en un rango de fechas."""
        return await self._statistics_ops.get_total_assignments_count(
            start_date, end_date
        )
    
    async def get_active_assignments_count(
        self, 
        reference_date: Optional[pendulum.Date] = None
    ) -> int:
        """Obtiene el conteo de asignaciones activas en una fecha específica."""
        return await self._statistics_ops.get_active_assignments_count(
            reference_date
        )
    
    async def get_assignments_by_status_count(self) -> Dict[str, int]:
        """Obtiene el conteo de asignaciones agrupadas por estado."""
        return await self._statistics_ops.get_assignments_by_status_count()
    
    async def get_assignments_by_allocation_category_count(self) -> Dict[str, int]:
        """Obtiene el conteo de asignaciones agrupadas por categoría de asignación."""
        return await self._statistics_ops.get_assignments_by_allocation_category_count()
    
    # ==========================================
    # 8. OPERACIONES DE ESTADÍSTICAS AVANZADAS (4 métodos)
    # ==========================================
    
    async def get_assignment_duration_analytics(
        self, 
        start_date: Optional[pendulum.Date] = None, 
        end_date: Optional[pendulum.Date] = None
    ) -> Dict[str, Any]:
        """Obtiene análisis de duración de asignaciones."""
        return await self._statistics_ops.get_assignment_duration_analytics(
            start_date, end_date
        )
    
    async def get_workload_distribution_analytics(self) -> Dict[str, Any]:
        """Obtiene análisis de distribución de carga de trabajo."""
        return await self._statistics_ops.get_workload_distribution_analytics()
    
    async def get_assignment_trends(
        self, 
        months_back: int = 12
    ) -> Dict[str, Any]:
        """Obtiene análisis de tendencias de asignaciones."""
        return await self._statistics_ops.get_assignment_trends(months_back)
    
    async def get_comprehensive_dashboard_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas completas para dashboard ejecutivo."""
        return await self._statistics_ops.get_comprehensive_dashboard_metrics()
    
    # ==========================================
    # 9. OPERACIONES DE VALIDACIÓN Y REGLAS DE NEGOCIO (5 métodos)
    # ==========================================
    
    async def validate_assignment_business_rules(
        self, 
        assignment_data: Dict[str, Any], 
        exclude_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Valida todas las reglas de negocio para asignaciones."""
        return await self._validation_ops.validate_assignment_business_rules(
            assignment_data, exclude_id
        )
    
    async def validate_no_overlapping_assignments(
        self, 
        employee_id: int, 
        start_date: pendulum.Date, 
        end_date: pendulum.Date, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """Verifica que no existan solapamientos en las asignaciones de un empleado."""
        return await self._validation_ops.validate_no_overlapping_assignments(
            employee_id, start_date, end_date, exclude_id
        )
    
    async def validate_workload_limits(
        self, 
        employee_id: int, 
        start_date: pendulum.Date, 
        end_date: pendulum.Date, 
        allocation_percentage: float
    ) -> bool:
        """Valida que la carga de trabajo no exceda los límites establecidos."""
        return await self._validation_ops.validate_workload_limits(
            employee_id, start_date, end_date, allocation_percentage
        )
    
    async def validate_assignment_deletion(self, assignment_id: int) -> Dict[str, Any]:
        """Valida si una asignación puede ser eliminada sin afectar la integridad."""
        return await self._validation_ops.validate_assignment_deletion(assignment_id)
    
    async def validate_employee_availability(
        self, 
        employee_id: int, 
        start_date: pendulum.Date, 
        end_date: pendulum.Date
    ) -> Dict[str, Any]:
        """Verifica la disponibilidad completa de un empleado en un período."""
        return await self._validation_ops.validate_employee_availability(
            employee_id, start_date, end_date
        )
    
    # ==========================================
    # 10. OPERACIONES DE DIAGNÓSTICO Y SALUD (2 métodos)
    # ==========================================
    
    async def get_system_health_status(
        self, 
        include_performance_metrics: bool = True,
        include_data_quality_checks: bool = True
    ) -> Dict[str, Any]:
        """Obtiene el estado de salud del sistema de asignaciones."""
        return await self._diagnostic_ops.get_system_health_status(
            include_performance_metrics, include_data_quality_checks
        )
    
    async def run_data_integrity_audit(
        self, 
        fix_issues: bool = False,
        audit_scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ejecuta una auditoría completa de integridad de datos."""
        return await self._diagnostic_ops.run_data_integrity_audit(
            fix_issues, audit_scope
        )