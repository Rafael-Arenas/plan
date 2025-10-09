# src/planificador/services/domain/team/interfaces/relationship_operations.py

"""
Interfaz para operaciones relacionales del servicio de dominio de Team.

Define los métodos para búsquedas basadas en relaciones con empleados,
proyectos, habilidades y análisis de fechas específicas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Set
from datetime import datetime
import pendulum

from .....schemas.team.team import Team
from .....schemas.team.team_advanced_schemas import TeamSchema


class ITeamDomainRelationshipOperations(ABC):
    """
    Interfaz para operaciones relacionales del servicio de dominio de Team.
    
    Define los métodos para realizar búsquedas y análisis basados en
    relaciones con otras entidades del sistema.
    """

    @abstractmethod
    async def find_teams_by_leader(
        self,
        leader_id: int
    ) -> List[TeamSchema]:
        """
        Encuentra todos los equipos liderados por una persona específica.
        
        Args:
            leader_id: Identificador único del líder
            
        Returns:
            List[TeamSchema]: Lista de equipos liderados por la persona
            
        Raises:
            NotFoundError: Si el líder no existe
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def find_teams_by_project(
        self,
        project_id: int
    ) -> List[TeamSchema]:
        """
        Encuentra equipos asociados a un proyecto específico.
        
        Args:
            project_id: Identificador único del proyecto
            
        Returns:
            List[TeamSchema]: Lista de equipos del proyecto
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def find_teams_by_skill_set(
        self,
        required_skills: Set[str]
    ) -> List[TeamSchema]:
        """
        Encuentra equipos que poseen un conjunto específico de habilidades.
        
        Args:
            required_skills: Conjunto de habilidades requeridas
            
        Returns:
            List[TeamSchema]: Lista de equipos con las habilidades
            
        Raises:
            ValidationError: Si las habilidades no son válidas
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def find_teams_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[TeamSchema]:
        """
        Encuentra equipos creados dentro de un rango de fechas específico.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            
        Returns:
            List[TeamSchema]: Lista de equipos en el rango de fechas
            
        Raises:
            ValidationError: Si el rango de fechas es inválido
            RepositoryError: Si hay error en la consulta
        """
        pass