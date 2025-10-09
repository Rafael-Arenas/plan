"""
Implementación de Operaciones de Búsqueda y Filtrado del Servicio de Dominio Schedule.

Implementa búsquedas avanzadas, filtrado por múltiples criterios
y consultas complejas según la documentación oficial.
"""

from typing import List, Optional, Dict, Any
from datetime import date
from loguru import logger

from planificador.schemas.response.response_schemas import ScheduleResponseSchema
from planificador.schemas.schedule.schedule_advanced_filters import ScheduleAdvancedFilters
from planificador.services.domain.schedule.interfaces.search_operations_interface import (
    IScheduleDomainSearchOperations
)
from planificador.repositories.schedule.schedule_repository_facade import ScheduleRepositoryFacade
from planificador.exceptions.base import ValidationError
from planificador.exceptions.repository.base_repository_exceptions import RepositoryError


class ScheduleDomainSearchOperations(IScheduleDomainSearchOperations):
    """
    Implementación de operaciones de búsqueda y filtrado del servicio de dominio Schedule.
    
    Proporciona funcionalidad completa para búsquedas avanzadas y filtrado
    por múltiples criterios según la documentación oficial.
    """

    def __init__(self, repository_facade: ScheduleRepositoryFacade):
        """
        Inicializa las operaciones de búsqueda.
        
        Args:
            repository_facade: Fachada del repositorio de horarios
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="schedule_search_operations")

    # ============================================================================
    # MÉTODOS SEGÚN LA DOCUMENTACIÓN OFICIAL
    # ============================================================================

    async def get_schedules_by_date(
        self,
        target_date: date,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None
    ) -> List[ScheduleResponseSchema]:
        """
        Obtiene horarios para una fecha específica con filtros opcionales.
        
        Args:
            target_date: Fecha objetivo para la búsqueda
            employee_id: ID del empleado (opcional)
            project_id: ID del proyecto (opcional)
            
        Returns:
            List[ScheduleResponseSchema]: Lista de horarios encontrados
            
        Raises:
            ValidationError: Si la fecha no es válida
            RepositoryError: Si hay error en la base de datos
        """
        try:
            self._logger.info(
                f"Obteniendo horarios para fecha {target_date}",
                extra={
                    "target_date": str(target_date),
                    "employee_id": employee_id,
                    "project_id": project_id
                }
            )
            
            # Construir filtros para el repositorio
            filters = {"date": target_date}
            if employee_id:
                filters["employee_id"] = employee_id
            if project_id:
                filters["project_id"] = project_id
            
            # Obtener horarios del repositorio
            schedules = await self._repository.search_schedules(filters)
            
            self._logger.info(f"Encontrados {len(schedules)} horarios para la fecha {target_date}")
            return schedules
            
        except ValidationError:
            self._logger.error(f"Error de validación al buscar horarios por fecha {target_date}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar horarios por fecha: {str(e)}")
            raise RepositoryError(f"Error al buscar horarios por fecha: {str(e)}")

    async def get_confirmed_schedules(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        employee_id: Optional[int] = None
    ) -> List[ScheduleResponseSchema]:
        """
        Obtiene horarios confirmados con filtros opcionales de fecha y empleado.
        
        Args:
            date_from: Fecha de inicio del rango (opcional)
            date_to: Fecha de fin del rango (opcional)
            employee_id: ID del empleado (opcional)
            
        Returns:
            List[ScheduleResponseSchema]: Lista de horarios confirmados
            
        Raises:
            ValidationError: Si el rango de fechas no es válido
            RepositoryError: Si hay error en la base de datos
        """
        try:
            self._logger.info(
                "Obteniendo horarios confirmados",
                extra={
                    "date_from": str(date_from) if date_from else None,
                    "date_to": str(date_to) if date_to else None,
                    "employee_id": employee_id
                }
            )
            
            # Validar rango de fechas
            if date_from and date_to and date_from > date_to:
                raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin")
            
            # Construir filtros para el repositorio
            filters = {"confirmed": True}
            if date_from:
                filters["date_from"] = date_from
            if date_to:
                filters["date_to"] = date_to
            if employee_id:
                filters["employee_id"] = employee_id
            
            # Obtener horarios confirmados del repositorio
            schedules = await self._repository.search_schedules(filters)
            
            self._logger.info(f"Encontrados {len(schedules)} horarios confirmados")
            return schedules
            
        except ValidationError:
            self._logger.error("Error de validación al buscar horarios confirmados")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar horarios confirmados: {str(e)}")
            raise RepositoryError(f"Error al buscar horarios confirmados: {str(e)}")

    async def search_schedules_advanced(
        self,
        filters: ScheduleAdvancedFilters
    ) -> List[ScheduleResponseSchema]:
        """
        Realiza búsqueda avanzada de horarios con filtros complejos.
        
        Args:
            filters: Filtros avanzados para la búsqueda
            
        Returns:
            List[ScheduleResponseSchema]: Lista de horarios encontrados
            
        Raises:
            ValidationError: Si los filtros no son válidos
            RepositoryError: Si hay error en la base de datos
        """
        try:
            self._logger.info("Realizando búsqueda avanzada de horarios")
            
            # Convertir filtros avanzados al formato del repositorio
            repository_filters = await self._convert_advanced_filters_to_repository_format(filters)
            
            # Realizar búsqueda en el repositorio
            schedules = await self._repository.search_schedules(repository_filters)
            
            self._logger.info(f"Búsqueda avanzada completada: {len(schedules)} horarios encontrados")
            return schedules
            
        except ValidationError:
            self._logger.error("Error de validación en búsqueda avanzada")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en búsqueda avanzada: {str(e)}")
            raise RepositoryError(f"Error en búsqueda avanzada: {str(e)}")

    # ============================================================================
    # MÉTODOS PRIVADOS DE UTILIDAD
    # ============================================================================

    async def _convert_advanced_filters_to_repository_format(
        self, 
        filters: ScheduleAdvancedFilters
    ) -> Dict[str, Any]:
        """
        Convierte filtros avanzados al formato esperado por el repositorio.
        
        Args:
            filters: Filtros avanzados de entrada
            
        Returns:
            Dict[str, Any]: Filtros en formato del repositorio
        """
        repository_filters = {}
        
        # Filtros básicos
        if filters.employee_ids:
            repository_filters["employee_ids"] = filters.employee_ids
        if filters.project_ids:
            repository_filters["project_ids"] = filters.project_ids
        if filters.team_ids:
            repository_filters["team_ids"] = filters.team_ids
        if filters.status_ids:
            repository_filters["status_ids"] = filters.status_ids
            
        # Filtros de fecha
        if filters.date_from:
            repository_filters["date_from"] = filters.date_from
        if filters.date_to:
            repository_filters["date_to"] = filters.date_to
        if filters.specific_dates:
            repository_filters["specific_dates"] = filters.specific_dates
            
        # Filtros de tiempo
        if filters.start_time_from:
            repository_filters["start_time_from"] = filters.start_time_from
        if filters.start_time_to:
            repository_filters["start_time_to"] = filters.start_time_to
        if filters.end_time_from:
            repository_filters["end_time_from"] = filters.end_time_from
        if filters.end_time_to:
            repository_filters["end_time_to"] = filters.end_time_to
            
        # Filtros de horas trabajadas
        if filters.hours_worked_min is not None:
            repository_filters["hours_worked_min"] = filters.hours_worked_min
        if filters.hours_worked_max is not None:
            repository_filters["hours_worked_max"] = filters.hours_worked_max
            
        # Filtros de confirmación
        if filters.confirmed is not None:
            repository_filters["confirmed"] = filters.confirmed
        if filters.pending_confirmation is not None:
            repository_filters["pending_confirmation"] = filters.pending_confirmation
            
        # Filtros de búsqueda de texto
        if filters.search_text:
            repository_filters["search_text"] = filters.search_text
        if filters.description_contains:
            repository_filters["description_contains"] = filters.description_contains
            
        # Filtros de exclusión
        if filters.exclude_employee_ids:
            repository_filters["exclude_employee_ids"] = filters.exclude_employee_ids
        if filters.exclude_project_ids:
            repository_filters["exclude_project_ids"] = filters.exclude_project_ids
            
        # Filtros de solapamiento
        if filters.overlapping_date_from and filters.overlapping_date_to:
            repository_filters["overlapping_date_from"] = filters.overlapping_date_from
            repository_filters["overlapping_date_to"] = filters.overlapping_date_to
            
        # Filtros de productividad
        if filters.productivity_score_min is not None:
            repository_filters["productivity_score_min"] = filters.productivity_score_min
        if filters.productivity_score_max is not None:
            repository_filters["productivity_score_max"] = filters.productivity_score_max
            
        # Filtros de días de la semana
        if filters.weekdays:
            repository_filters["weekdays"] = filters.weekdays
            
        # Filtros especiales
        if filters.overtime_only is not None:
            repository_filters["overtime_only"] = filters.overtime_only
        if filters.weekend_only is not None:
            repository_filters["weekend_only"] = filters.weekend_only
        if filters.holiday_schedules is not None:
            repository_filters["holiday_schedules"] = filters.holiday_schedules
            
        return repository_filters