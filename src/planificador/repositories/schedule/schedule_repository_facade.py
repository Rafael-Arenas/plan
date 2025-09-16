# src/planificador/repositories/schedule/schedule_repository_facade.py

"""
Fachada del Repositorio Schedule.

Este módulo implementa el patrón Facade para el repositorio de horarios,
proporcionando una interfaz unificada y simplificada para todas las
operaciones relacionadas con la gestión de horarios.

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

Uso:
    ```python
    async with get_async_session() as session:
        facade = ScheduleRepositoryFacade(session)
        schedule = await facade.create_schedule(schedule_data)
        schedules = await facade.get_schedules_by_employee(employee_id)
    ```
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, time
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from planificador.models.schedule import Schedule
from planificador.models.employee import Employee
from planificador.models.project import Project
from planificador.repositories.schedule.interfaces import (
    IScheduleCrudOperations,
    IScheduleQueryOperations,
    IScheduleValidationOperations,
    IScheduleRelationshipOperations,
    IScheduleStatisticsOperations
)
from planificador.repositories.schedule.modules import (
    ScheduleCrudModule,
    ScheduleQueryModule,
    ScheduleValidationModule,
    ScheduleRelationshipModule,
    ScheduleStatisticsModule
)
from planificador.exceptions.repository import ScheduleRepositoryError


class ScheduleRepositoryFacade(
    IScheduleCrudOperations,
    IScheduleQueryOperations,
    IScheduleValidationOperations,
    IScheduleRelationshipOperations,
    IScheduleStatisticsOperations
):
    """
    Fachada del repositorio Schedule que unifica todas las operaciones.
    
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
        # Inicializa la fachada con sesión de BD y módulos especializados
        self.session = session
        self._logger = logger.bind(module="schedule_repository_facade")
        
        # Inicializar módulos especializados
        self.crud_module = ScheduleCrudModule(session)
        self.query_module = ScheduleQueryModule(session)
        self.validation_module = ScheduleValidationModule(session)
        self.relationship_module = ScheduleRelationshipModule(session)
        self.statistics_module = ScheduleStatisticsModule(session)
        
        self._logger.debug("ScheduleRepositoryFacade inicializada")

    # =============================================================================
    # OPERACIONES CRUD
    # =============================================================================

    async def create_schedule(self, schedule_data: Dict[str, Any]) -> Schedule:
        # Crea un nuevo horario
        return await self.crud_module.create_schedule(schedule_data)

    async def update_schedule(
        self,
        schedule_id: int,
        schedule_data: Dict[str, Any]
    ) -> Schedule:
        # Actualiza un horario existente
        return await self.crud_module.update_schedule(schedule_id, schedule_data)

    async def delete_schedule(self, schedule_id: int) -> bool:
        # Elimina un horario
        return await self.crud_module.delete_schedule(schedule_id)

    # =============================================================================
    # OPERACIONES DE CONSULTA
    # =============================================================================

    async def get_schedule_by_id(self, schedule_id: int) -> Optional[Schedule]:
        # Obtiene un horario por su ID
        return await self.query_module.get_schedule_by_id(schedule_id)

    async def get_schedules_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        # Obtiene horarios de un empleado en un rango de fechas
        return await self.query_module.get_schedules_by_employee(
            employee_id, start_date, end_date
        )

    async def get_schedules_by_date(
        self,
        target_date: date,
        employee_id: Optional[int] = None
    ) -> List[Schedule]:
        # Obtiene horarios para una fecha específica
        return await self.query_module.get_schedules_by_date(target_date, employee_id)

    async def get_schedules_by_project(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        # Obtiene horarios asociados a un proyecto
        return await self.query_module.get_schedules_by_project(
            project_id, start_date, end_date
        )

    async def get_schedules_by_team(
        self,
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        # Obtiene horarios asociados a un equipo
        return await self.query_module.get_schedules_by_team(
            team_id, start_date, end_date
        )

    async def get_confirmed_schedules(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> List[Schedule]:
        # Obtiene horarios confirmados en un rango de fechas
        return await self.query_module.get_confirmed_schedules(
            start_date, end_date, employee_id
        )

    async def search_schedules(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Schedule]:
        # Busca horarios con filtros personalizados
        return await self.query_module.search_schedules(filters, limit, offset)

    async def count_schedules(self, filters: Optional[Dict[str, Any]] = None) -> int:
        # Cuenta el número de horarios que coinciden con los filtros
        return await self.query_module.count_schedules(filters)


    # =============================================================================
    # OPERACIONES DE RELACIONES
    # =============================================================================

    # Gestión de relaciones con empleados
    async def get_employee_schedules_with_details(
        self,
        employee_id: int,
        include_projects: bool = True,
        include_teams: bool = True,
        include_status_codes: bool = True
    ) -> List[Schedule]:
        # Obtiene horarios de un empleado con detalles de relaciones
        return await self.relationship_module.get_employee_schedules_with_details(
            employee_id, include_projects, include_teams, include_status_codes
        )

    async def get_employees_with_schedules_in_period(
        self,
        start_date: date,
        end_date: date
    ) -> List[Tuple[Employee, List[Schedule]]]:
        # Obtiene empleados con sus horarios en un período
        return await self.relationship_module.get_employees_with_schedules_in_period(
            start_date, end_date
        )

    async def get_employee_schedules_in_period(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        # Obtiene horarios de un empleado en un período específico
        return await self.relationship_module.get_employee_schedules_in_period(
            employee_id, start_date, end_date
        )

    # Gestión de relaciones con proyectos
    async def get_project_schedules_with_details(
        self,
        project_id: int,
        include_employees: bool = True,
        include_teams: bool = True,
        include_status_codes: bool = True
    ) -> List[Schedule]:
        # Obtiene horarios de un proyecto con detalles de relaciones
        return await self.relationship_module.get_project_schedules_with_details(
            project_id, include_employees, include_teams, include_status_codes
        )

    async def get_projects_with_schedules_in_period(
        self,
        start_date: date,
        end_date: date
    ) -> List[Tuple[Project, List[Schedule]]]:
        # Obtiene proyectos con sus horarios en un período
        return await self.relationship_module.get_projects_with_schedules_in_period(
            start_date, end_date
        )

    async def get_project_schedules_in_period(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        # Obtiene horarios de un proyecto en un período específico
        return await self.relationship_module.get_project_schedules_in_period(
            project_id, start_date, end_date
        )

    # Gestión de relaciones con equipos
    async def get_team_schedules_with_details(
        self,
        team_id: int,
        include_employees: bool = True,
        include_projects: bool = True,
        include_status_codes: bool = True
    ) -> List[Schedule]:
        # Obtiene horarios de un equipo con detalles de relaciones
        return await self.relationship_module.get_team_schedules_with_details(
            team_id, include_employees, include_projects, include_status_codes
        )

    # Operaciones de asignación
    async def assign_schedule_to_project(
        self,
        schedule_id: int,
        project_id: int
    ) -> Schedule:
        # Asigna un horario a un proyecto
        return await self.relationship_module.assign_schedule_to_project(
            schedule_id, project_id
        )

    async def assign_schedule_to_team(
        self,
        schedule_id: int,
        team_id: int
    ) -> Schedule:
        # Asigna un horario a un equipo
        return await self.relationship_module.assign_schedule_to_team(
            schedule_id, team_id
        )

    async def remove_schedule_from_project(
        self,
        schedule_id: int
    ) -> Schedule:
        # Remueve un horario de un proyecto
        return await self.relationship_module.remove_schedule_from_project(
            schedule_id
        )

    async def remove_schedule_from_team(
        self,
        schedule_id: int
    ) -> Schedule:
        # Remueve un horario de un equipo
        return await self.relationship_module.remove_schedule_from_team(
            schedule_id
        )

    async def get_schedule_relationships_summary(
        self,
        schedule_id: int
    ) -> Dict[str, Any]:
        # Obtiene resumen de relaciones de un horario
        return await self.relationship_module.get_schedule_relationships_summary(
            schedule_id
        )

    async def validate_project_assignment(
        self,
        schedule_id: int,
        project_id: int
    ) -> bool:
        # Valida la asignación de un horario a un proyecto
        return await self.relationship_module.validate_project_assignment(
            schedule_id, project_id
        )

    async def validate_team_assignment(
        self,
        schedule_id: int,
        team_id: int
    ) -> bool:
        # Valida la asignación de un horario a un equipo
        return await self.relationship_module.validate_team_assignment(
            schedule_id, team_id
        )


    # =============================================================================
    # OPERACIONES DE ESTADÍSTICAS
    # =============================================================================

    async def get_employee_hours_summary(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Obtiene resumen de horas trabajadas por empleado."""
        return await self.statistics_module.get_employee_hours_summary(
            employee_id, start_date, end_date
        )

    async def get_project_hours_summary(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Obtiene resumen de horas por proyecto."""
        return await self.statistics_module.get_project_hours_summary(
            project_id, start_date, end_date
        )

    async def get_team_hours_summary(
        self,
        team_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Obtiene resumen de horas por equipo."""
        return await self.statistics_module.get_team_hours_summary(
            team_id, start_date, end_date
        )

    async def get_schedule_counts_by_status(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> Dict[str, int]:
        """Obtiene conteo de horarios por estado."""
        return await self.statistics_module.get_schedule_counts_by_status(
            start_date, end_date, employee_id
        )

    async def get_productivity_metrics(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obtiene métricas de productividad."""
        return await self.statistics_module.get_productivity_metrics(
            start_date, end_date, employee_id, project_id
        )

    async def get_utilization_report(
        self,
        start_date: date,
        end_date: date,
        group_by: str = "employee"
    ) -> List[Dict[str, Any]]:
        """Obtiene reporte de utilización."""
        return await self.statistics_module.get_utilization_report(
            start_date, end_date, group_by
        )

    async def get_confirmation_statistics(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de confirmación."""
        return await self.statistics_module.get_confirmation_statistics(
            start_date, end_date
        )

    async def get_overtime_analysis(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obtiene análisis de horas extra."""
        return await self.statistics_module.get_overtime_analysis(
            start_date, end_date, employee_id
        )

    async def get_schedule_distribution(
        self,
        start_date: date,
        end_date: date,
        distribution_type: str = "daily"
    ) -> List[Dict[str, Any]]:
        """Obtiene distribución de horarios."""
        return await self.statistics_module.get_schedule_distribution(
            start_date, end_date, distribution_type
        )

    async def get_top_performers(
        self,
        start_date: date,
        end_date: date,
        metric: str = "hours",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obtiene los mejores desempeños."""
        return await self.statistics_module.get_top_performers(
            start_date, end_date, metric, limit
        )
        
    # =============================================================================
    # OPERACIONES DE VALIDACIÓN
    # =============================================================================

    async def validate_schedule_data(self, schedule_data: Dict[str, Any]) -> bool:
        # Valida los datos de un horario
        return await self.validation_module.validate_schedule_data(schedule_data)

    async def validate_schedule_id(self, schedule_id: int) -> bool:
        # Valida que un ID de horario sea válido y exista
        return await self.validation_module.validate_schedule_id(schedule_id)

    async def validate_employee_id(self, employee_id: int) -> bool:
        # Valida que un ID de empleado sea válido y exista
        return await self.validation_module.validate_employee_id(employee_id)

    async def validate_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> bool:
        # Valida un rango de fechas
        return await self.validation_module.validate_date_range(start_date, end_date)

    async def validate_time_range(
        self,
        start_time: time,
        end_time: time
    ) -> bool:
        # Valida un rango de horas
        return await self.validation_module.validate_time_range(start_time, end_time)

    async def validate_schedule_conflicts(
        self,
        employee_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: Optional[int] = None
    ) -> bool:
        # Valida que no existan conflictos de horarios para un empleado
        return await self.validation_module.validate_schedule_conflicts(
            employee_id, schedule_date, start_time, end_time, exclude_schedule_id
        )



    async def validate_team_membership(
        self,
        employee_id: int,
        team_id: int
    ) -> bool:
        # Valida que un empleado pertenezca a un equipo
        return await self.validation_module.validate_team_membership(
            employee_id, team_id
        )

    async def validate_search_filters(
        self,
        filters: Dict[str, Any]
    ) -> bool:
        # Valida los filtros de búsqueda
        return await self.validation_module.validate_search_filters(filters)



    # =============================================================================
    # MÉTODOS DE CONVENIENCIA Y OPERACIONES COMPUESTAS
    # =============================================================================

    async def get_complete_schedule_info(
        self,
        schedule_id: int
    ) -> Optional[Dict[str, Any]]:
        """Obtiene información completa de un horario incluyendo relaciones."""
        # Obtener el horario básico
        schedule = await self.get_schedule_by_id(schedule_id)
        if not schedule:
            return None

        # Enriquecer con información de relaciones
        schedule_with_details = await self.get_employee_schedules_with_details(
            schedule['employee_id'],
            schedule['start_date'],
            schedule['end_date']
        )
        
        # Buscar el horario específico en los resultados
        for detailed_schedule in schedule_with_details:
            if detailed_schedule['id'] == schedule_id:
                return detailed_schedule
        
        return schedule

    async def create_schedule_with_validation(
        self,
        schedule_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crea un horario con validación completa."""
        # Validar los datos del horario
        validation_result = await self.validate_schedule_data(schedule_data)
        if not validation_result['is_valid']:
            raise ValueError(f"Datos de horario inválidos: {validation_result['errors']}")
        
        # Validar conflictos de horario
        conflicts = await self.validate_schedule_conflicts(
            schedule_data['employee_id'],
            schedule_data['start_date'],
            schedule_data['end_date'],
            schedule_data.get('start_time'),
            schedule_data.get('end_time')
        )
        
        if conflicts:
            raise ValueError(f"Conflictos de horario detectados: {conflicts}")
        
        # Crear el horario
        return await self.create_schedule(schedule_data)

    async def update_schedule_with_validation(
        self,
        schedule_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Actualiza un horario con validación completa."""
        # Obtener el horario actual
        current_schedule = await self.get_schedule_by_id(schedule_id)
        if not current_schedule:
            return None
        
        # Combinar datos actuales con actualizaciones
        merged_data = {**current_schedule, **update_data}
        
        # Validar los datos actualizados
        validation_result = await self.validate_schedule_data(merged_data)
        if not validation_result['is_valid']:
            raise ValueError(f"Datos de horario inválidos: {validation_result['errors']}")
        
        # Validar conflictos si se cambian fechas/horas
        if any(key in update_data for key in ['start_date', 'end_date', 'start_time', 'end_time']):
            conflicts = await self.validate_schedule_conflicts(
                merged_data['employee_id'],
                merged_data['start_date'],
                merged_data['end_date'],
                merged_data.get('start_time'),
                merged_data.get('end_time'),
                exclude_schedule_id=schedule_id
            )
            
            if conflicts:
                raise ValueError(f"Conflictos de horario detectados: {conflicts}")
        
        # Actualizar el horario
        return await self.update_schedule(schedule_id, update_data)

    async def get_employee_schedule_summary(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Obtiene resumen completo de horarios de un empleado."""
        # Obtener horarios con detalles
        schedules = await self.get_employee_schedules_with_details(
            employee_id, start_date, end_date
        )
        
        # Obtener estadísticas de horas
        hours_summary = await self.get_employee_hours_summary(
            employee_id, start_date, end_date
        )
        
        # Obtener conteo por estado
        status_counts = await self.get_schedule_counts_by_status(
            start_date, end_date, employee_id
        )
        
        return {
            'employee_id': employee_id,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'schedules': schedules,
            'hours_summary': hours_summary,
            'status_counts': status_counts,
            'total_schedules': len(schedules)
        }

    async def bulk_schedule_operation(
        self,
        operation: str,
        schedule_data_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Realiza operaciones en lote sobre múltiples horarios."""
        results = []
        
        for schedule_data in schedule_data_list:
            try:
                if operation == 'create':
                    result = await self.create_schedule_with_validation(schedule_data)
                elif operation == 'update':
                    schedule_id = schedule_data.pop('id')
                    result = await self.update_schedule_with_validation(schedule_id, schedule_data)
                elif operation == 'delete':
                    schedule_id = schedule_data['id']
                    result = await self.delete_schedule(schedule_id)
                else:
                    raise ValueError(f"Operación no soportada: {operation}")
                
                results.append({
                    'success': True,
                    'data': result,
                    'original_data': schedule_data
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'original_data': schedule_data
                })
        
        return results

    async def create_validated_schedule(self, schedule_data: Dict[str, Any]) -> Schedule:
        """Crea un horario después de validar todos los datos y reglas de negocio."""
        # Validar estructura y tipos de datos
        validation_result = await self.validate_schedule_data(schedule_data)
        if not validation_result['is_valid']:
            raise ValueError(f"Datos inválidos: {validation_result['errors']}")
        
        # Validar rango de fechas
        date_validation = await self.validate_date_range(
            schedule_data['start_date'],
            schedule_data['end_date']
        )
        if not date_validation['is_valid']:
            raise ValueError(f"Rango de fechas inválido: {date_validation['errors']}")
        
        # Validar conflictos de horario
        conflicts = await self.validate_schedule_conflicts(
            schedule_data['employee_id'],
            schedule_data['start_date'],
            schedule_data['end_date'],
            schedule_data.get('start_time'),
            schedule_data.get('end_time')
        )
        
        if conflicts:
            raise ValueError(f"Conflictos detectados: {conflicts}")
        
        # Crear el horario si todas las validaciones pasan
        return await self.create_schedule(schedule_data)