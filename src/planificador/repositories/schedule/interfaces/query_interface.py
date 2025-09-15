# src/planificador/repositories/schedule/interfaces/query_interface.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.models.schedule import Schedule
from planificador.exceptions.repository_exceptions import ScheduleRepositoryError


class IScheduleQueryOperations(ABC):
    """
    Interfaz para operaciones de consulta del repositorio Schedule.
    
    Define los métodos abstractos para consultar y recuperar
    registros de horarios desde la base de datos.
    
    Raises:
        ScheduleRepositoryError: Para errores específicos del repositorio de horarios
    """

    @abstractmethod
    async def get_schedule_by_id(self, schedule_id: int) -> Optional[Schedule]:
        """
        Obtiene un horario por su ID.
        
        Args:
            schedule_id: ID del horario a buscar
            
        Returns:
            Optional[Schedule]: El horario encontrado o None
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_schedules_by_employee(
        self,
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Obtiene horarios de un empleado en un rango de fechas.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            List[Schedule]: Lista de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_schedules_by_date(
        self,
        target_date: date,
        employee_id: Optional[int] = None
    ) -> List[Schedule]:
        """
        Obtiene horarios para una fecha específica.
        
        Args:
            target_date: Fecha objetivo
            employee_id: ID del empleado (opcional, para filtrar)
            
        Returns:
            List[Schedule]: Lista de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_schedules_by_project(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Obtiene horarios asociados a un proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            List[Schedule]: Lista de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_schedules_by_team(
        self,
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Schedule]:
        """
        Obtiene horarios asociados a un equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            List[Schedule]: Lista de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_confirmed_schedules(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> List[Schedule]:
        """
        Obtiene horarios confirmados en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            employee_id: ID del empleado (opcional, para filtrar)
            
        Returns:
            List[Schedule]: Lista de horarios confirmados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def search_schedules(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Schedule]:
        """
        Busca horarios con filtros personalizados.
        
        Args:
            filters: Diccionario de filtros a aplicar
            limit: Límite de resultados (opcional)
            offset: Desplazamiento para paginación (opcional)
            
        Returns:
            List[Schedule]: Lista de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la búsqueda
        """
        pass

    @abstractmethod
    async def count_schedules(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número de horarios que coinciden con los filtros.
        
        Args:
            filters: Diccionario de filtros a aplicar (opcional)
            
        Returns:
            int: Número de horarios encontrados
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante el conteo
        """
        pass