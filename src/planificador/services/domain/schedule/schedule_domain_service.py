"""
Servicio de Dominio Principal para Horarios (Schedule).

Este módulo implementa el patrón Facade proporcionando un punto de acceso
unificado a todas las operaciones del dominio de horarios.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import date, time
import pendulum
from loguru import logger

from ...repositories.schedule.schedule_repository_facade import ScheduleRepositoryFacade
from .interfaces import IScheduleDomainService
from .modules import (
    ScheduleDomainCrudOperations,
    ScheduleDomainEmployeeOperations,
    ScheduleDomainProjectOperations,
    ScheduleDomainTeamOperations,
    ScheduleDomainSearchOperations,
    ScheduleDomainConfirmationOperations,
    ScheduleDomainStatisticsOperations,
    ScheduleDomainProductivityOperations,
    ScheduleDomainValidationOperations,
    ScheduleDomainDiagnosticOperations
)
from planificador.exceptions import RepositoryError, ValidationError, NotFoundError
from planificador.models.schedule import Schedule
from planificador.schemas.schedule import (
    ScheduleListResponse,
    ScheduleSearchResponse,
    ScheduleResponseSchema,
    ScheduleConfirmationSchema,
    BulkConfirmationSchema,
    BulkConfirmationResultSchema,
    PendingConfirmationSchema,
    ProductivityMetricsSchema,
    UtilizationReportSchema,
    ScheduleDistributionSchema,
    EmployeeHoursSummarySchema,
    ProjectHoursSummarySchema,
    TeamHoursSummarySchema,
    OvertimeAnalysisSchema,
    ValidationResultSchema,
    ConflictValidationSchema,
    TeamCoordinationValidationSchema,
    WorkloadValidationSchema
)


class ScheduleDomainService(IScheduleDomainService):
    """
    Servicio de Dominio Principal para Horarios (Schedule).
    
    Implementa el patrón Facade proporcionando una interfaz unificada
    para todas las operaciones del dominio de horarios.
    
    Organización modular según funcionalidades disponibles:
    1. Operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
    2. Operaciones de Empleado (Consultas y análisis por empleado)
    3. Operaciones de Proyecto (Consultas y análisis por proyecto)
    4. Operaciones de Equipo (Consultas y análisis por equipo)
    5. Operaciones de Búsqueda (Filtrado y búsqueda avanzada)
    6. Operaciones de Confirmación (Aprobación y confirmación de horarios)
    7. Operaciones de Estadísticas (Métricas y reportes estadísticos)
    8. Operaciones de Productividad (Análisis de rendimiento y productividad)
    9. Operaciones de Validación (Reglas de negocio y validaciones)
    10. Operaciones de Diagnóstico (Salud del sistema y diagnósticos)
    
    Características principales:
    - Punto de acceso único para todas las operaciones
    - Encapsulación de la complejidad interna
    - Coordinación entre múltiples módulos especializados
    - Manejo centralizado de transacciones y errores
    - Logging estructurado y trazabilidad completa
    """
    
    def __init__(self, repository_facade: ScheduleRepositoryFacade):
        """
        Inicializa el servicio de dominio con todos sus módulos.
        
        Args:
            repository_facade: Fachada del repositorio para acceso a datos
        """
        self._repository = repository_facade
        self._logger = logger.bind(service="schedule_domain")
        
        # Inicializar todos los módulos especializados
        self._crud_ops = ScheduleDomainCrudOperations(repository_facade)
        self._employee_ops = ScheduleDomainEmployeeOperations(repository_facade)
        self._project_ops = ScheduleDomainProjectOperations(repository_facade)
        self._team_ops = ScheduleDomainTeamOperations(repository_facade)
        self._search_ops = ScheduleDomainSearchOperations(repository_facade)
        self._confirmation_ops = ScheduleDomainConfirmationOperations(repository_facade)
        self._statistics_ops = ScheduleDomainStatisticsOperations(repository_facade)
        self._productivity_ops = ScheduleDomainProductivityOperations(repository_facade)
        self._validation_ops = ScheduleDomainValidationOperations(repository_facade)
        self._diagnostic_ops = ScheduleDomainDiagnosticOperations(repository_facade)
        
        # Aliases for consistency with interface methods
        self._project_operations = self._project_ops
        self._team_operations = self._team_ops
        self._confirmation_operations = self._confirmation_ops
        self._productivity_operations = self._productivity_ops
        self._statistics_operations = self._statistics_ops
        self._validation_operations = self._validation_ops
        
        self._logger.info("Servicio de dominio de horarios inicializado")

    async def initialize_service(self) -> None:
        """
        Inicializa el servicio de dominio y sus dependencias.
        
        Este método debe ser llamado antes de usar cualquier funcionalidad
        del servicio para garantizar que todas las dependencias estén
        correctamente configuradas.
        """
        self._logger.info("Inicializando servicio de dominio de horarios")
        # Aquí se pueden agregar inicializaciones adicionales si es necesario
        self._logger.info("Servicio de dominio de horarios inicializado correctamente")

    def get_service_info(self) -> Dict[str, Any]:
        """
        Obtiene información general del servicio.
        
        Returns:
            Dict con información del servicio incluyendo versión,
            configuración y estado de las dependencias.
        """
        return {
            "service_name": "ScheduleDomainService",
            "version": "1.0.0",
            "description": "Servicio de dominio principal para gestión de horarios",
            "modules": [
                "crud_operations",
                "employee_operations", 
                "project_operations",
                "team_operations",
                "search_operations",
                "confirmation_operations",
                "statistics_operations",
                "productivity_operations",
                "validation_operations",
                "diagnostic_operations"
            ],
            "status": "active",
            "initialized": True
        }

    # ==========================================
    # 1. OPERACIONES CRUD
    # ==========================================
    
    async def create_schedule(self, schedule_data: Dict[str, Any]) -> Schedule:
        """Crea un nuevo horario con validaciones completas de negocio."""
        self._logger.info(f"Creando horario para empleado {schedule_data.get('employee_id')}")
        return await self._crud_ops.create_schedule(schedule_data)
    
    async def update_schedule(self, schedule_id: int, schedule_data: Dict[str, Any]) -> Schedule:
        """Actualiza un horario existente con validaciones de conflictos."""
        self._logger.info(f"Actualizando horario {schedule_id}")
        return await self._crud_ops.update_schedule(schedule_id, schedule_data)
    
    async def delete_schedule(self, schedule_id: int) -> bool:
        """Elimina un horario después de validar dependencias e impacto."""
        self._logger.info(f"Eliminando horario {schedule_id}")
        return await self._crud_ops.delete_schedule(schedule_id)

    # ==========================================
    # 2. OPERACIONES DE EMPLEADO
    # ==========================================
    
    async def get_employee_schedules(
        self, 
        employee_id: int, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """Obtiene todos los horarios de un empleado específico."""
        self._logger.info(f"Obteniendo horarios del empleado {employee_id}")
        return await self._employee_ops.get_employee_schedules(employee_id, start_date, end_date)
    
    async def get_employee_schedules_with_details(
        self, 
        employee_id: int,
        include_projects: bool = True,
        include_teams: bool = True,
        include_status_codes: bool = True
    ) -> List[Schedule]:
        """Obtiene horarios de empleado con información detallada."""
        self._logger.info(f"Obteniendo horarios detallados del empleado {employee_id}")
        return await self._employee_ops.get_employee_schedules_with_details(
            employee_id, include_projects, include_teams, include_status_codes
        )
    
    async def get_employee_current_week_schedule(self, employee_id: int) -> List[Schedule]:
        """Obtiene el horario de la semana actual de un empleado."""
        self._logger.info(f"Obteniendo horario de semana actual del empleado {employee_id}")
        return await self._employee_ops.get_employee_current_week_schedule(employee_id)
    
    async def get_employee_schedule_conflicts(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Detecta conflictos en los horarios de un empleado."""
        self._logger.info(f"Detectando conflictos de horario para empleado {employee_id}")
        return await self._employee_ops.get_employee_schedule_conflicts(employee_id, start_date, end_date)

    # ==========================================
    # 3. OPERACIONES DE BÚSQUEDA
    # ==========================================
    
    async def search_schedules_by_date(
        self, 
        target_date: date, 
        confirmed_only: bool = False
    ) -> List[Schedule]:
        """Busca horarios por fecha específica."""
        self._logger.info(f"Buscando horarios para la fecha {target_date}")
        return await self._search_ops.search_schedules_by_date(target_date, confirmed_only)
    
    async def search_schedules_by_confirmed_status(
        self, 
        start_date: date, 
        end_date: date, 
        confirmed: bool = True
    ) -> List[Schedule]:
        """Busca horarios por estado de confirmación."""
        self._logger.info(f"Buscando horarios confirmados entre {start_date} y {end_date}")
        return await self._search_ops.search_schedules_by_confirmed_status(start_date, end_date, confirmed)
    
    async def search_schedules_advanced(
        self, 
        filters: Dict[str, Any], 
        limit: Optional[int] = None, 
        offset: Optional[int] = None
    ) -> List[Schedule]:
        """Realiza búsqueda avanzada de horarios con filtros múltiples."""
        self._logger.info("Realizando búsqueda avanzada de horarios")
        return await self._search_ops.search_schedules_advanced(filters, limit, offset)

    # ==========================================
    # 4. OPERACIONES DE ESTADÍSTICAS (Legacy methods for backward compatibility)
    # ==========================================
    
    async def get_employee_hours_summary_legacy(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Obtiene resumen de horas trabajadas por empleado (legacy)."""
        self._logger.info(f"Calculando resumen de horas para empleado {employee_id}")
        return await self._statistics_ops.get_employee_hours_summary(employee_id, start_date, end_date)
    
    async def get_project_hours_summary_legacy(
        self, 
        project_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Obtiene resumen de horas por proyecto (legacy)."""
        self._logger.info(f"Calculando resumen de horas para proyecto {project_id}")
        return await self._statistics_ops.get_project_hours_summary(project_id, start_date, end_date)
    
    async def get_team_hours_summary_legacy(
        self, 
        team_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Obtiene resumen de horas por equipo (legacy)."""
        self._logger.info(f"Calculando resumen de horas para equipo {team_id}")
        return await self._statistics_ops.get_team_hours_summary(team_id, start_date, end_date)
    
    async def get_overtime_analysis_legacy(
        self, 
        start_date: date, 
        end_date: date, 
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analiza las horas extra en un período específico (legacy)."""
        self._logger.info("Analizando horas extra")
        return await self._statistics_ops.get_overtime_analysis(start_date, end_date, employee_id)

    # ==========================================
    # 5. OPERACIONES DE VALIDACIÓN (Legacy methods for backward compatibility)
    # ==========================================
    
    async def validate_schedule_business_rules_legacy(
        self, 
        schedule_data: Dict[str, Any], 
        exclude_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Valida que un horario cumple con las reglas de negocio (legacy)."""
        self._logger.info("Validando reglas de negocio para horario")
        return await self._validation_ops.validate_schedule_business_rules(schedule_data, exclude_id)
    
    async def validate_schedule_conflicts_legacy(
        self, 
        employee_id: int, 
        schedule_date: date, 
        start_time: time, 
        end_time: time, 
        exclude_schedule_id: Optional[int] = None
    ) -> bool:
        """Valida que no existan conflictos de horario para un empleado (legacy)."""
        self._logger.info(f"Validando conflictos de horario para empleado {employee_id}")
        return await self._validation_ops.validate_schedule_conflicts(
            employee_id, schedule_date, start_time, end_time, exclude_schedule_id
        )
    
    async def validate_team_schedule_coordination_legacy(
        self, 
        team_id: int, 
        schedule_date: date
    ) -> Dict[str, Any]:
        """Valida la coordinación de horarios dentro de un equipo (legacy)."""
        self._logger.info(f"Validando coordinación de horarios para equipo {team_id}")
        return await self._validation_ops.validate_team_schedule_coordination(team_id, schedule_date)
    
    async def validate_workload_distribution_legacy(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Valida la distribución de carga de trabajo de un empleado (legacy)."""
        self._logger.info(f"Validando distribución de carga para empleado {employee_id}")
        return await self._validation_ops.validate_workload_distribution(employee_id, start_date, end_date)

    # ===== IScheduleDomainProjectOperations Methods =====
    
    async def get_project_schedules(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ScheduleListResponse]:
        """Obtiene horarios de un proyecto específico."""
        return await self._project_operations.get_project_schedules(
            project_id, start_date, end_date
        )

    async def get_project_team_schedules(
        self,
        project_id: int,
        include_employee_details: bool = True
    ) -> ScheduleListResponse:
        """Obtiene horarios completos del equipo asignado al proyecto."""
        return await self._project_operations.get_project_team_schedules(
            project_id, include_employee_details
        )

    async def get_project_schedule_timeline(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> ScheduleSearchResponse:
        """Genera una línea de tiempo visual de horarios del proyecto."""
        return await self._project_operations.get_project_schedule_timeline(
            project_id, start_date, end_date
        )

    # ===== IScheduleDomainTeamOperations Methods =====
    
    async def get_team_schedules(
        self,
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ScheduleListResponse]:
        """Obtiene horarios de un equipo específico."""
        return await self._team_operations.get_team_schedules(
            team_id, start_date, end_date
        )

    async def get_team_schedule_coordination(
        self,
        team_id: int,
        coordination_date: date
    ) -> ScheduleSearchResponse:
        """Analiza la coordinación de horarios del equipo para una fecha específica."""
        return await self._team_operations.get_team_schedule_coordination(
            team_id, coordination_date
        )

    async def get_team_availability_analysis(
        self,
        team_id: int,
        analysis_period_start: date,
        analysis_period_end: date
    ) -> ScheduleSearchResponse:
        """Realiza análisis completo de disponibilidad del equipo en un período."""
        return await self._team_operations.get_team_availability_analysis(
            team_id, analysis_period_start, analysis_period_end
        )

    # ===== IScheduleDomainConfirmationOperations Methods =====
    
    async def confirm_schedule(
        self,
        schedule_id: int,
        confirmation_data: ScheduleConfirmationSchema
    ) -> ScheduleResponseSchema:
        """Confirma un horario específico con validaciones adicionales."""
        return await self._confirmation_operations.confirm_schedule(
            schedule_id, confirmation_data
        )

    async def bulk_confirm_schedules(
        self,
        schedule_ids: List[int],
        confirmation_data: BulkConfirmationSchema
    ) -> BulkConfirmationResultSchema:
        """Confirma múltiples horarios en una operación transaccional."""
        return await self._confirmation_operations.bulk_confirm_schedules(
            schedule_ids, confirmation_data
        )

    async def get_pending_confirmations(
        self,
        employee_id: Optional[int] = None,
        days_ahead: int = 7
    ) -> List[PendingConfirmationSchema]:
        """Obtiene horarios pendientes de confirmación con alertas de vencimiento."""
        return await self._confirmation_operations.get_pending_confirmations(
            employee_id, days_ahead
        )

    # ===== IScheduleDomainProductivityOperations Methods =====
    
    async def get_productivity_metrics(
        self,
        employee_id: Optional[int] = None,
        team_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_trends: bool = False
    ) -> ProductivityMetricsSchema:
        """Calcula métricas de productividad basadas en horarios."""
        return await self._productivity_operations.get_productivity_metrics(
            employee_id, team_id, start_date, end_date, include_trends
        )

    async def get_utilization_report(
        self,
        resource_type: str,
        resource_id: int,
        period_start: date,
        period_end: date,
        include_breakdown: bool = True
    ) -> UtilizationReportSchema:
        """Genera reporte de utilización de recursos."""
        return await self._productivity_operations.get_utilization_report(
            resource_type, resource_id, period_start, period_end, include_breakdown
        )

    async def get_schedule_distribution_analysis(
        self,
        analysis_scope: str,
        scope_id: int,
        analysis_date: date,
        include_recommendations: bool = False
    ) -> ScheduleDistributionSchema:
        """Analiza la distribución de horarios y carga de trabajo."""
        return await self._productivity_operations.get_schedule_distribution_analysis(
            analysis_scope, scope_id, analysis_date, include_recommendations
        )

    # ===== IScheduleDomainStatisticsOperations Methods (Updated) =====
    
    async def get_employee_hours_summary(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> EmployeeHoursSummarySchema:
        """Obtiene resumen de horas trabajadas por empleado."""
        return await self._statistics_operations.get_employee_hours_summary(
            employee_id, start_date, end_date
        )

    async def get_project_hours_summary(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> ProjectHoursSummarySchema:
        """Obtiene resumen de horas invertidas en un proyecto específico."""
        return await self._statistics_operations.get_project_hours_summary(
            project_id, start_date, end_date
        )

    async def get_team_hours_summary(
        self,
        team_id: int,
        start_date: date,
        end_date: date
    ) -> TeamHoursSummarySchema:
        """Calcula distribución de horas trabajadas por equipo."""
        return await self._statistics_operations.get_team_hours_summary(
            team_id, start_date, end_date
        )

    async def get_overtime_analysis(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> OvertimeAnalysisSchema:
        """Analiza patrones de horas extra y sobrecarga de trabajo."""
        return await self._statistics_operations.get_overtime_analysis(
            start_date, end_date, employee_id
        )

    # ===== ValidationOperationsInterface Methods (Updated) =====
    
    async def validate_schedule_business_rules(
        self,
        schedule_data: Dict[str, Any],
        exclude_id: Optional[int] = None
    ) -> ValidationResultSchema:
        """Valida reglas de negocio para horarios."""
        return await self._validation_operations.validate_schedule_business_rules(
            schedule_data, exclude_id
        )

    async def validate_schedule_conflicts(
        self,
        employee_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: Optional[int] = None
    ) -> ConflictValidationSchema:
        """Detecta y valida conflictos de horarios con análisis detallado."""
        return await self._validation_operations.validate_schedule_conflicts(
            employee_id, schedule_date, start_time, end_time, exclude_schedule_id
        )

    async def validate_team_schedule_coordination(
        self,
        team_id: int,
        target_date: date
    ) -> TeamCoordinationValidationSchema:
        """Valida la coordinación de horarios del equipo para proyectos colaborativos."""
        return await self._validation_operations.validate_team_schedule_coordination(
            team_id, target_date
        )

    async def validate_workload_distribution(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> WorkloadValidationSchema:
        """Valida la distribución de carga de trabajo de un empleado."""
        return await self._validation_operations.validate_workload_distribution(
            employee_id, start_date, end_date
        )