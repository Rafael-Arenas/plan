"""
Interfaz para Operaciones de Validación y Reglas de Negocio del Servicio de Dominio Schedule.

Define los contratos para validaciones complejas, verificación de reglas de negocio,
detección de conflictos y validación de integridad de datos.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, time

from planificador.schemas.schedule.schedule import Schedule
from planificador.schemas.response.response_schemas import ScheduleSearchResponse


class IScheduleDomainValidationOperations(ABC):
    """
    Interfaz para operaciones de validación y reglas de negocio del servicio de dominio Schedule.
    
    Define los métodos para validaciones complejas, verificación de reglas
    de negocio y detección de conflictos con integridad de datos.
    """

    @abstractmethod
    async def validate_schedule_business_rules(
        self,
        employee_id: int,
        project_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: Optional[int] = None
    ) -> ScheduleSearchResponse:
        """
        Valida que un horario cumple todas las reglas de negocio establecidas.
        
        Args:
            employee_id: ID del empleado
            project_id: ID del proyecto
            schedule_date: Fecha del horario
            start_time: Hora de inicio
            end_time: Hora de fin
            exclude_schedule_id: ID de horario a excluir de validación (para actualizaciones)
            
        Returns:
            ScheduleSearchResponse: Resultado de validación con detalles
            
        Raises:
            ValidationError: Si los parámetros básicos no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def check_schedule_conflicts(
        self,
        employee_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: Optional[int] = None
    ) -> ScheduleSearchResponse:
        """
        Detecta conflictos de horarios para un empleado en una fecha específica.
        
        Args:
            employee_id: ID del empleado
            schedule_date: Fecha a verificar
            start_time: Hora de inicio propuesta
            end_time: Hora de fin propuesta
            exclude_schedule_id: ID de horario a excluir (para actualizaciones)
            
        Returns:
            ScheduleSearchResponse: Resultado de detección de conflictos
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def validate_employee_availability(
        self,
        employee_id: int,
        target_date: date,
        required_hours: float
    ) -> ScheduleSearchResponse:
        """
        Valida la disponibilidad de un empleado para horas adicionales.
        
        Args:
            employee_id: ID del empleado
            target_date: Fecha objetivo
            required_hours: Horas requeridas adicionales
            
        Returns:
            ScheduleSearchResponse: Resultado de validación de disponibilidad
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def validate_project_capacity(
        self,
        project_id: int,
        target_date: date,
        additional_hours: float
    ) -> ScheduleSearchResponse:
        """
        Valida la capacidad de un proyecto para horas adicionales.
        
        Args:
            project_id: ID del proyecto
            target_date: Fecha objetivo
            additional_hours: Horas adicionales propuestas
            
        Returns:
            ScheduleSearchResponse: Resultado de validación de capacidad
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def validate_schedule_time_constraints(
        self,
        start_time: time,
        end_time: time,
        schedule_date: date
    ) -> Tuple[bool, List[str]]:
        """
        Valida restricciones de tiempo para horarios (horarios laborales, duración mínima/máxima).
        
        Args:
            start_time: Hora de inicio
            end_time: Hora de fin
            schedule_date: Fecha del horario
            
        Returns:
            Tuple[bool, List[str]]: (Es válido, Lista de errores si los hay)
            
        Raises:
            ValidationError: Si los parámetros básicos no son válidos
        """
        pass

    @abstractmethod
    async def perform_schedule_integrity_check(
        self,
        check_scope: str,  # 'employee', 'project', 'team', 'all'
        scope_id: Optional[int] = None,
        check_date_range: Optional[Tuple[date, date]] = None
    ) -> ScheduleSearchResponse:
        """
        Realiza verificación de integridad de datos de horarios en un alcance específico.
        
        Args:
            check_scope: Alcance de la verificación ('employee', 'project', 'team', 'all')
            scope_id: ID del alcance (requerido si no es 'all')
            check_date_range: Rango de fechas para verificar (opcional)
            
        Returns:
            ScheduleSearchResponse: Resultado de verificación de integridad
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass