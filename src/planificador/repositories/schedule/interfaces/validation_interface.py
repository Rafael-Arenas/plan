# src/planificador/repositories/schedule/interfaces/validation_interface.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import date, time

from planificador.exceptions.repository_exceptions import ScheduleRepositoryError


class IScheduleValidationOperations(ABC):
    """
    Interfaz para operaciones de validación del repositorio Schedule.
    
    Define los métodos abstractos para validar datos de horarios
    antes de realizar operaciones en la base de datos.
    
    Raises:
        ScheduleRepositoryError: Para errores específicos del repositorio de horarios
    """

    @abstractmethod
    def validate_schedule_data(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida los datos de un horario antes de crear o actualizar.
        
        Args:
            schedule_data: Datos del horario a validar
            
        Returns:
            Dict[str, Any]: Datos validados y normalizados
            
        Raises:
            ScheduleRepositoryError: Si los datos no son válidos
        """
        pass

    @abstractmethod
    def validate_schedule_id(self, schedule_id: int) -> int:
        """
        Valida que el ID del horario sea válido.
        
        Args:
            schedule_id: ID del horario a validar
            
        Returns:
            int: ID validado
            
        Raises:
            ScheduleRepositoryError: Si el ID no es válido
        """
        pass

    @abstractmethod
    def validate_employee_id(self, employee_id: int) -> int:
        """
        Valida que el ID del empleado sea válido.
        
        Args:
            employee_id: ID del empleado a validar
            
        Returns:
            int: ID validado
            
        Raises:
            ScheduleRepositoryError: Si el ID no es válido
        """
        pass

    @abstractmethod
    def validate_date_range(
        self,
        start_date: Optional[date],
        end_date: Optional[date]
    ) -> tuple[Optional[date], Optional[date]]:
        """
        Valida un rango de fechas.
        
        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            
        Returns:
            tuple: Tupla con fechas validadas
            
        Raises:
            ScheduleRepositoryError: Si el rango de fechas no es válido
        """
        pass

    @abstractmethod
    def validate_time_range(
        self,
        start_time: Optional[time],
        end_time: Optional[time]
    ) -> tuple[Optional[time], Optional[time]]:
        """
        Valida un rango de horas.
        
        Args:
            start_time: Hora de inicio (opcional)
            end_time: Hora de fin (opcional)
            
        Returns:
            tuple: Tupla con horas validadas
            
        Raises:
            ScheduleRepositoryError: Si el rango de horas no es válido
        """
        pass

    @abstractmethod
    async def validate_schedule_conflicts(
        self,
        employee_id: int,
        schedule_date: date,
        start_time: Optional[time],
        end_time: Optional[time],
        exclude_schedule_id: Optional[int] = None
    ) -> bool:
        """
        Valida que no existan conflictos de horarios para un empleado.
        
        Args:
            employee_id: ID del empleado
            schedule_date: Fecha del horario
            start_time: Hora de inicio (opcional)
            end_time: Hora de fin (opcional)
            exclude_schedule_id: ID del horario a excluir de la validación (opcional)
            
        Returns:
            bool: True si no hay conflictos
            
        Raises:
            ScheduleRepositoryError: Si existen conflictos o error en validación
        """
        pass

    @abstractmethod
    def validate_project_assignment(
        self,
        employee_id: int,
        project_id: Optional[int],
        schedule_date: date
    ) -> bool:
        """
        Valida que el empleado esté asignado al proyecto en la fecha dada.
        
        Args:
            employee_id: ID del empleado
            project_id: ID del proyecto (opcional)
            schedule_date: Fecha del horario
            
        Returns:
            bool: True si la asignación es válida
            
        Raises:
            ScheduleRepositoryError: Si la asignación no es válida
        """
        pass

    @abstractmethod
    def validate_team_membership(
        self,
        employee_id: int,
        team_id: Optional[int],
        schedule_date: date
    ) -> bool:
        """
        Valida que el empleado sea miembro del equipo en la fecha dada.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo (opcional)
            schedule_date: Fecha del horario
            
        Returns:
            bool: True si la membresía es válida
            
        Raises:
            ScheduleRepositoryError: Si la membresía no es válida
        """
        pass

    @abstractmethod
    def validate_search_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida los filtros de búsqueda.
        
        Args:
            filters: Diccionario de filtros a validar
            
        Returns:
            Dict[str, Any]: Filtros validados y normalizados
            
        Raises:
            ScheduleRepositoryError: Si los filtros no son válidos
        """
        pass