"""
Interfaz para operaciones de validación de horarios.

Este módulo define la interfaz abstracta para las operaciones de validación
de horarios, incluyendo validación de reglas de negocio, detección de conflictos,
coordinación de equipos y distribución de carga de trabajo.
"""

from abc import ABC, abstractmethod
from datetime import date, time
from typing import Dict, Any, Optional

from planificador.schemas.schedule.schedule import (
    ValidationResultSchema,
    ConflictValidationSchema,
    TeamCoordinationValidationSchema,
    WorkloadValidationSchema
)
from planificador.exceptions.validation import ValidationError
from planificador.exceptions.repository import RepositoryError


class IScheduleDomainValidationOperations(ABC):
    """
    Interfaz abstracta para operaciones de validación de horarios.
    
    Define los métodos necesarios para validar reglas de negocio,
    detectar conflictos, coordinar equipos y analizar distribución
    de carga de trabajo en el sistema de horarios.
    """

    @abstractmethod
    async def validate_schedule_business_rules(
        self,
        schedule_data: Dict[str, Any],
        exclude_id: Optional[int] = None
    ) -> ValidationResultSchema:
        """
        Valida todas las reglas de negocio para horarios.
        
        Args:
            schedule_data: Datos del horario a validar
            exclude_id: ID de horario a excluir de validación (para actualizaciones)
            
        Returns:
            ValidationResultSchema: Resultado detallado de la validación
            
        Raises:
            ValidationError: Si los parámetros básicos no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def validate_schedule_conflicts(
        self,
        employee_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        exclude_schedule_id: Optional[int] = None
    ) -> ConflictValidationSchema:
        """
        Detecta y valida conflictos de horarios con análisis detallado.
        
        Args:
            employee_id: ID del empleado
            schedule_date: Fecha del horario
            start_time: Hora de inicio
            end_time: Hora de fin
            exclude_schedule_id: ID de horario a excluir de validación (para actualizaciones)
            
        Returns:
            ConflictValidationSchema: Resultado detallado de detección de conflictos
            
        Raises:
            ValidationError: Si los parámetros básicos no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def validate_team_schedule_coordination(
        self,
        team_id: int,
        target_date: date
    ) -> TeamCoordinationValidationSchema:
        """
        Valida la coordinación de horarios del equipo para proyectos colaborativos.
        
        Args:
            team_id: ID del equipo
            target_date: Fecha objetivo para validar coordinación
            
        Returns:
            TeamCoordinationValidationSchema: Resultado de validación de coordinación
            
        Raises:
            ValidationError: Si los parámetros básicos no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def validate_workload_distribution(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> WorkloadValidationSchema:
        """
        Valida que la distribución de carga de trabajo sea equilibrada y sostenible.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            WorkloadValidationSchema: Resultado de validación de carga de trabajo
            
        Raises:
            ValidationError: Si los parámetros básicos no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass