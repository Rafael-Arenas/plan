"""
Servicio de Dominio Principal para Asignaciones de Proyecto.

Este módulo implementa el patrón Facade proporcionando un punto de acceso
unificado a todas las operaciones del dominio de asignaciones de proyecto.
"""

from typing import Dict, List, Any, Optional, Union
import pendulum
from loguru import logger

from ....repositories.project_assignment.project_assignment_repository_facade import ProjectAssignmentRepositoryFacade
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


class ProjectAssignmentDomainService:
    """
    Servicio de Dominio Principal para Asignaciones de Proyecto.
    
    Implementa el patrón Facade proporcionando una interfaz unificada
    para todas las operaciones del dominio de asignaciones de proyecto.
    
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
    # OPERACIONES CRUD PRINCIPALES
    # ==========================================
    
    async def create_assignment(
        self, 
        assignment_data: ProjectAssignmentCreate
    ) -> ProjectAssignment:
        # Crea una nueva asignación de proyecto
        self._logger.info(f"Creando asignación para empleado {assignment_data.employee_id}")
        return await self._crud_ops.create_assignment(assignment_data)
    
    async def update_assignment(
        self, 
        assignment_id: int, 
        update_data: ProjectAssignmentUpdate
    ) -> ProjectAssignment:
        # Actualiza una asignación existente
        self._logger.info(f"Actualizando asignación {assignment_id}")
        return await self._crud_ops.update_assignment(assignment_id, update_data)
    
    async def delete_assignment(self, assignment_id: int) -> bool:
        # Elimina una asignación
        self._logger.info(f"Eliminando asignación {assignment_id}")
        return await self._crud_ops.delete_assignment(assignment_id)
    
    async def get_assignment_by_id(self, assignment_id: int) -> Optional[ProjectAssignment]:
        # Obtiene una asignación por su ID
        return await self._crud_ops.get_assignment_by_id(assignment_id)
    
    async def bulk_create_assignments(
        self, 
        assignments_data: List[ProjectAssignmentCreate]
    ) -> List[ProjectAssignment]:
        # Crea múltiples asignaciones en lote
        self._logger.info(f"Creando {len(assignments_data)} asignaciones en lote")
        return await self._crud_ops.bulk_create_assignments(assignments_data)
    
    async def duplicate_assignment(
        self, 
        assignment_id: int, 
        modifications: Optional[Dict[str, Any]] = None
    ) -> ProjectAssignment:
        # Duplica una asignación existente
        self._logger.info(f"Duplicando asignación {assignment_id}")
        return await self._crud_ops.duplicate_assignment(assignment_id, modifications)
    
    async def archive_assignment(self, assignment_id: int) -> ProjectAssignment:
        # Archiva una asignación
        self._logger.info(f"Archivando asignación {assignment_id}")
        return await self._crud_ops.archive_assignment(assignment_id)
    
    # ==========================================
    # CONSULTAS CENTRADAS EN EMPLEADOS
    # ==========================================
    
    async def get_all_employee_assignments(
        self, 
        employee_id: int,
        include_archived: bool = False
    ) -> List[ProjectAssignment]:
        # Obtiene todas las asignaciones de un empleado
        return await self._employee_queries.get_all_employee_assignments(
            employee_id, include_archived
        )
    
    async def get_active_employee_assignments(
        self, 
        employee_id: int
    ) -> List[ProjectAssignment]:
        # Obtiene las asignaciones activas de un empleado
        return await self._employee_queries.get_active_employee_assignments(employee_id)
    
    async def get_employee_workload_summary(
        self, 
        employee_id: int,
        analysis_period: Optional[tuple] = None
    ) -> Dict[str, Any]:
        # Obtiene un resumen de la carga de trabajo de un empleado
        return await self._employee_queries.get_employee_workload_summary(
            employee_id, analysis_period
        )
    
    async def get_employee_assignment_history(
        self, 
        employee_id: int,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        # Obtiene el historial de asignaciones de un empleado
        return await self._employee_queries.get_employee_assignment_history(employee_id, limit)
    
    async def get_employee_current_allocation(self, employee_id: int) -> Dict[str, Any]:
        # Obtiene la asignación actual de un empleado
        return await self._employee_queries.get_employee_current_allocation(employee_id)
    
    # ==========================================
    # CONSULTAS CENTRADAS EN PROYECTOS
    # ==========================================
    
    async def get_all_project_assignments(
        self, 
        project_id: int,
        include_archived: bool = False
    ) -> List[ProjectAssignment]:
        # Obtiene todas las asignaciones de un proyecto
        return await self._project_queries.get_all_project_assignments(
            project_id, include_archived
        )
    
    async def get_project_team_summary(self, project_id: int) -> Dict[str, Any]:
        # Obtiene un resumen del equipo de un proyecto
        return await self._project_queries.get_project_team_summary(project_id)
    
    async def get_project_resource_allocation(self, project_id: int) -> Dict[str, Any]:
        # Obtiene la asignación de recursos de un proyecto
        return await self._project_queries.get_project_resource_allocation(project_id)
    
    async def get_project_assignment_timeline(self, project_id: int) -> Dict[str, Any]:
        # Obtiene la línea de tiempo de asignaciones de un proyecto
        return await self._project_queries.get_project_assignment_timeline(project_id)
    
    # ==========================================
    # OPERACIONES DE BÚSQUEDA Y FILTRADO
    # ==========================================
    
    async def get_assignments_with_filters(
        self, 
        filters: AssignmentAdvancedFilters
    ) -> List[ProjectAssignment]:
        # Busca asignaciones con filtros avanzados
        return await self._search_ops.get_assignments_with_filters(filters)
    
    async def get_assignments_by_date_range(
        self, 
        start_date: pendulum.Date, 
        end_date: pendulum.Date
    ) -> List[ProjectAssignment]:
        # Obtiene asignaciones en un rango de fechas
        return await self._search_ops.get_assignments_by_date_range(start_date, end_date)
    
    async def get_assignments_by_role(self, role: str) -> List[ProjectAssignment]:
        # Obtiene asignaciones por rol específico
        return await self._search_ops.get_assignments_by_role(role)
    
    async def get_overlapping_assignments(
        self, 
        employee_id: int, 
        start_date: pendulum.Date, 
        end_date: pendulum.Date,
        exclude_assignment_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        # Detecta asignaciones superpuestas para un empleado
        return await self._search_ops.get_overlapping_assignments(
            employee_id, start_date, end_date, exclude_assignment_id
        )
    
    # ==========================================
    # GESTIÓN DE RECURSOS
    # ==========================================
    
    async def optimize_resource_allocation(self, project_id: int) -> Dict[str, Any]:
        # Optimiza la asignación de recursos para un proyecto
        return await self._resource_mgmt.optimize_resource_allocation(project_id)
    
    async def calculate_team_capacity(
        self, 
        team_member_ids: List[int], 
        period_start: pendulum.Date, 
        period_end: pendulum.Date
    ) -> Dict[str, Any]:
        # Calcula la capacidad de un equipo en un período
        return await self._resource_mgmt.calculate_team_capacity(
            team_member_ids, period_start, period_end
        )
    
    async def balance_workload_across_team(self, project_id: int) -> Dict[str, Any]:
        # Balancea la carga de trabajo dentro de un equipo de proyecto
        return await self._resource_mgmt.balance_workload_across_team(project_id)
    
    # ==========================================
    # ESTADÍSTICAS Y ANÁLISIS
    # ==========================================
    
    async def get_assignment_count_by_status(
        self, 
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        # Obtiene el conteo de asignaciones por estado
        return await self._statistics_ops.get_assignment_count_by_status(filters)
    
    async def get_assignment_distribution_by_role(
        self, 
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Obtiene la distribución de asignaciones por rol
        return await self._statistics_ops.get_assignment_distribution_by_role(filters)
    
    async def get_average_allocation_metrics(
        self, 
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        # Obtiene métricas promedio de asignación
        return await self._statistics_ops.get_average_allocation_metrics(filters)
    
    async def get_assignment_duration_statistics(
        self, 
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Obtiene estadísticas de duración de asignaciones
        return await self._statistics_ops.get_assignment_duration_statistics(filters)
    
    async def analyze_assignment_trends(
        self, 
        period_months: int = 12,
        granularity: str = "monthly"
    ) -> Dict[str, Any]:
        # Analiza tendencias de asignaciones en el tiempo
        return await self._statistics_ops.analyze_assignment_trends(period_months, granularity)
    
    async def calculate_resource_utilization_metrics(
        self, 
        analysis_period: Optional[tuple] = None
    ) -> Dict[str, Any]:
        # Calcula métricas de utilización de recursos
        return await self._statistics_ops.calculate_resource_utilization_metrics(analysis_period)
    
    async def get_project_performance_metrics(
        self, 
        project_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        # Obtiene métricas de rendimiento de proyectos
        return await self._statistics_ops.get_project_performance_metrics(project_ids)
    
    async def generate_predictive_insights(
        self, 
        prediction_horizon_months: int = 3
    ) -> Dict[str, Any]:
        # Genera insights predictivos basados en datos históricos
        return await self._statistics_ops.generate_predictive_insights(prediction_horizon_months)
    
    # ==========================================
    # VALIDACIÓN Y REGLAS DE NEGOCIO
    # ==========================================
    
    async def validate_assignment_business_rules(
        self, 
        assignment_data: ProjectAssignmentCreate
    ) -> Dict[str, Any]:
        # Valida las reglas de negocio para una asignación
        return await self._validation_ops.validate_assignment_business_rules(assignment_data)
    
    async def check_workload_constraints(
        self, 
        employee_id: int, 
        additional_allocation: float,
        period_start: pendulum.Date, 
        period_end: pendulum.Date
    ) -> Dict[str, Any]:
        # Verifica las restricciones de carga de trabajo
        return await self._validation_ops.check_workload_constraints(
            employee_id, additional_allocation, period_start, period_end
        )
    
    async def validate_date_consistency(
        self, 
        start_date: pendulum.Date, 
        end_date: pendulum.Date
    ) -> Dict[str, Any]:
        # Valida la consistencia de fechas
        return await self._validation_ops.validate_date_consistency(start_date, end_date)
    
    async def check_assignment_conflicts(
        self, 
        assignment_data: ProjectAssignmentCreate,
        exclude_assignment_id: Optional[int] = None
    ) -> Dict[str, Any]:
        # Verifica conflictos con asignaciones existentes
        return await self._validation_ops.check_assignment_conflicts(
            assignment_data, exclude_assignment_id
        )
    
    async def validate_assignment_update_integrity(
        self, 
        assignment_id: int, 
        update_data: ProjectAssignmentUpdate
    ) -> Dict[str, Any]:
        # Valida la integridad de una actualización de asignación
        return await self._validation_ops.validate_assignment_update_integrity(
            assignment_id, update_data
        )
    
    # ==========================================
    # DIAGNÓSTICO Y SALUD DEL SISTEMA
    # ==========================================
    
    async def get_system_health_status(
        self, 
        include_performance_metrics: bool = True,
        include_data_quality_checks: bool = True
    ) -> Dict[str, Any]:
        # Obtiene el estado de salud del sistema
        return await self._diagnostic_ops.get_system_health_status(
            include_performance_metrics, include_data_quality_checks
        )
    
    async def run_data_integrity_audit(
        self, 
        fix_issues: bool = False,
        audit_scope: Optional[str] = None
    ) -> Dict[str, Any]:
        # Ejecuta una auditoría de integridad de datos
        return await self._diagnostic_ops.run_data_integrity_audit(fix_issues, audit_scope)
    
    async def analyze_performance_bottlenecks(
        self, 
        analysis_depth: str = "standard"
    ) -> Dict[str, Any]:
        # Analiza cuellos de botella de rendimiento
        return await self._diagnostic_ops.analyze_performance_bottlenecks(analysis_depth)
    
    async def get_resource_usage_report(
        self, 
        include_historical_data: bool = False
    ) -> Dict[str, Any]:
        # Obtiene un reporte de uso de recursos
        return await self._diagnostic_ops.get_resource_usage_report(include_historical_data)
    
    async def validate_system_configuration(self) -> Dict[str, Any]:
        # Valida la configuración del sistema
        return await self._diagnostic_ops.validate_system_configuration()
    
    # ==========================================
    # MÉTODOS DE UTILIDAD Y COORDINACIÓN
    # ==========================================
    
    async def get_service_statistics(self) -> Dict[str, Any]:
        # Obtiene estadísticas generales del servicio
        stats = {
            "service_name": "ProjectAssignmentDomainService",
            "version": "1.0.0",
            "modules_loaded": {
                "crud_operations": bool(self._crud_ops),
                "employee_queries": bool(self._employee_queries),
                "project_queries": bool(self._project_queries),
                "search_operations": bool(self._search_ops),
                "resource_management": bool(self._resource_mgmt),
                "statistics_operations": bool(self._statistics_ops),
                "validation_operations": bool(self._validation_ops),
                "diagnostic_operations": bool(self._diagnostic_ops)
            },
            "total_methods": 45,
            "categories": {
                "crud": 7,
                "employee_queries": 5,
                "project_queries": 4,
                "search_operations": 4,
                "resource_management": 3,
                "statistics": 8,
                "validation": 5,
                "diagnostics": 5,
                "utilities": 4
            }
        }
        
        self._logger.info("Estadísticas del servicio obtenidas")
        return stats
    
    async def validate_service_integrity(self) -> Dict[str, Any]:
        # Valida la integridad del servicio completo
        validation_results = {
            "service_status": "healthy",
            "modules_status": {},
            "validation_timestamp": pendulum.now().isoformat(),
            "issues_found": []
        }
        
        # Validar cada módulo
        modules = {
            "crud_operations": self._crud_ops,
            "employee_queries": self._employee_queries,
            "project_queries": self._project_queries,
            "search_operations": self._search_ops,
            "resource_management": self._resource_mgmt,
            "statistics_operations": self._statistics_ops,
            "validation_operations": self._validation_ops,
            "diagnostic_operations": self._diagnostic_ops
        }
        
        for module_name, module_instance in modules.items():
            if module_instance is None:
                validation_results["modules_status"][module_name] = "error"
                validation_results["issues_found"].append(f"Módulo {module_name} no inicializado")
                validation_results["service_status"] = "degraded"
            else:
                validation_results["modules_status"][module_name] = "healthy"
        
        self._logger.info(f"Validación de integridad completada: {validation_results['service_status']}")
        return validation_results
    
    async def get_available_operations(self) -> Dict[str, List[str]]:
        # Obtiene la lista de operaciones disponibles por categoría
        operations = {
            "crud_operations": [
                "create_assignment", "update_assignment", "delete_assignment",
                "get_assignment_by_id", "bulk_create_assignments", 
                "duplicate_assignment", "archive_assignment"
            ],
            "employee_queries": [
                "get_all_employee_assignments", "get_active_employee_assignments",
                "get_employee_workload_summary", "get_employee_assignment_history",
                "get_employee_current_allocation"
            ],
            "project_queries": [
                "get_all_project_assignments", "get_project_team_summary",
                "get_project_resource_allocation", "get_project_assignment_timeline"
            ],
            "search_operations": [
                "get_assignments_with_filters", "get_assignments_by_date_range",
                "get_assignments_by_role", "get_overlapping_assignments"
            ],
            "resource_management": [
                "optimize_resource_allocation", "calculate_team_capacity",
                "balance_workload_across_team"
            ],
            "statistics": [
                "get_assignment_count_by_status", "get_assignment_distribution_by_role",
                "get_average_allocation_metrics", "get_assignment_duration_statistics",
                "analyze_assignment_trends", "calculate_resource_utilization_metrics",
                "get_project_performance_metrics", "generate_predictive_insights"
            ],
            "validation": [
                "validate_assignment_business_rules", "check_workload_constraints",
                "validate_date_consistency", "check_assignment_conflicts",
                "validate_assignment_update_integrity"
            ],
            "diagnostics": [
                "get_system_health_status", "run_data_integrity_audit",
                "analyze_performance_bottlenecks", "get_resource_usage_report",
                "validate_system_configuration"
            ],
            "utilities": [
                "get_service_statistics", "validate_service_integrity",
                "get_available_operations", "cleanup_resources"
            ]
        }
        
        return operations
    
    async def cleanup_resources(self) -> Dict[str, Any]:
        # Limpia recursos y conexiones del servicio
        cleanup_results = {
            "cleanup_timestamp": pendulum.now().isoformat(),
            "modules_cleaned": [],
            "status": "success"
        }
        
        try:
            # Limpiar cada módulo si tiene método de limpieza
            modules = [
                ("crud_operations", self._crud_ops),
                ("employee_queries", self._employee_queries),
                ("project_queries", self._project_queries),
                ("search_operations", self._search_ops),
                ("resource_management", self._resource_mgmt),
                ("statistics_operations", self._statistics_ops),
                ("validation_operations", self._validation_ops),
                ("diagnostic_operations", self._diagnostic_ops)
            ]
            
            for module_name, module_instance in modules:
                if module_instance and hasattr(module_instance, 'cleanup'):
                    await module_instance.cleanup()
                    cleanup_results["modules_cleaned"].append(module_name)
            
            self._logger.info("Limpieza de recursos completada exitosamente")
            
        except Exception as e:
            cleanup_results["status"] = "error"
            cleanup_results["error"] = str(e)
            self._logger.error(f"Error durante la limpieza de recursos: {e}")
        
        return cleanup_results