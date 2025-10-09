"""
Interfaz para Operaciones de Empleado del Servicio de Dominio Schedule.

Define los contratos para consultas y análisis centrados en empleados específicos
con detección de conflictos y análisis de disponibilidad.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.schemas.schedule.schedule import Schedule
from planificador.schemas.response.response_schemas import (
    ScheduleListResponse,
    ScheduleSearchResponse
)


class IScheduleDomainEmployeeOperations(ABC):
    """
    Interfaz para operaciones de empleado del servicio de dominio Schedule.
    
    Define los métodos para consultas y análisis centrados en empleados
    específicos con gestión de conflictos y disponibilidad.
    """

    @abstractmethod
    async def get_employee_schedules(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ScheduleListResponse]:
        """
        Obtiene horarios de un empleado en un rango de fechas específico.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            List[ScheduleListResponse]: Lista de horarios del empleado
            
        Raises:
            ValidationError: Si el employee_id no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_employee_schedules_with_details(
        self,
        employee_id: int,
        include_projects: bool = True,
        include_teams: bool = True
    ) -> List[Schedule]:
        """
        Obtiene horarios de un empleado con información detallada de relaciones.
        
        Args:
            employee_id: ID del empleado
            include_projects: Si incluir información de proyectos
            include_teams: Si incluir información de equipos
            
        Returns:
            List[Schedule]: Horarios con detalles completos
            
        Raises:
            ValidationError: Si el employee_id no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_employee_current_week_schedule(
        self,
        employee_id: int
    ) -> ScheduleSearchResponse:
        """
        Obtiene la programación semanal actual del empleado con resumen de horas.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            ScheduleSearchResponse: Programación semanal con resumen
            
        Raises:
            ValidationError: Si el employee_id no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_employee_schedule_conflicts(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """
        Detecta y analiza conflictos de horarios para un empleado específico.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
            
        Returns:
            List[Schedule]: Lista de conflictos detectados
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass