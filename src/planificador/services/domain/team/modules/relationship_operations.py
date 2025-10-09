# src/planificador/services/domain/team/modules/relationship_operations.py

"""
Módulo de Operaciones de Relaciones del Dominio Team.

Este módulo implementa las operaciones para gestionar y consultar las relaciones
de los equipos con otras entidades del sistema, como líderes, proyectos,
habilidades y rangos de fechas.

Características:
    - Búsqueda de equipos por líder
    - Consulta de equipos por proyecto
    - Filtrado por conjunto de habilidades
    - Búsqueda por rangos de fechas
    - Análisis de relaciones complejas

Principios de Diseño:
    - Relationship-Centric: Enfoque en conexiones entre entidades
    - Flexible Queries: Consultas adaptables a diferentes criterios
    - Performance: Optimización para consultas relacionales
    - Comprehensive: Cobertura completa de relaciones

Uso:
    ```python
    relationship_ops = TeamDomainRelationshipOperations(team_repo, membership_repo)
    teams = await relationship_ops.find_teams_by_leader(leader_id)
    project_teams = await relationship_ops.find_teams_by_project(project_id)
    ```
"""

from typing import List, Optional, Set
from datetime import datetime
import pendulum
from loguru import logger

from planificador.repositories.team import TeamRepositoryFacade
from planificador.repositories.team_membership import TeamMembershipRepositoryFacade
from planificador.services.domain.team.interfaces.relationship_operations_interface import (
    ITeamDomainRelationshipOperations
)
from planificador.schemas.team.team_advanced_schemas import TeamSchema
from planificador.exceptions.domain import (
    TeamDomainError
)
from planificador.exceptions.base import (
    ValidationError
)
from planificador.exceptions.repository import (
    TeamRepositoryError, TeamMembershipRepositoryError
)


class TeamDomainRelationshipOperations(ITeamDomainRelationshipOperations):
    """
    Implementación de operaciones de relaciones del dominio Team.
    
    Proporciona funcionalidades para consultar equipos basándose en sus
    relaciones con otras entidades del sistema.
    
    Attributes:
        _team_repo: Repositorio de equipos
        _membership_repo: Repositorio de membresías
        _logger: Logger para registro de eventos
    """

    def __init__(
        self,
        team_repo: TeamRepositoryFacade,
        membership_repo: TeamMembershipRepositoryFacade
    ):
        """
        Inicializa las operaciones de relaciones del dominio Team.
        
        Args:
            team_repo: Repositorio de equipos
            membership_repo: Repositorio de membresías
        """
        self._team_repo = team_repo
        self._membership_repo = membership_repo
        self._logger = logger.bind(module="TeamDomainRelationshipOperations")
        
        self._logger.debug("TeamDomainRelationshipOperations inicializado")

    async def find_teams_by_leader(
        self,
        leader_id: int,
        include_team_details: bool = True
    ) -> List[TeamSchema]:
        """
        Encuentra todos los equipos liderados por una persona específica.
        
        Args:
            leader_id: Identificador único del líder
            include_team_details: Si incluir detalles completos del equipo
            
        Returns:
            List[TeamSchema]: Lista de equipos liderados por la persona
            
        Raises:
            ValidationError: Si el leader_id no es válido
            NotFoundError: Si el líder no existe
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(f"Buscando equipos liderados por empleado: {leader_id}")
            
            # Validar parámetros
            if not isinstance(leader_id, int) or leader_id <= 0:
                raise ValidationError("El ID del líder debe ser un entero positivo")
            
            # Obtener membresías de liderazgo del empleado
            leadership_memberships = await self._membership_repo.get_memberships_by_employee_and_role(
                employee_id=leader_id,
                role="leader"
            )
            
            if not leadership_memberships:
                self._logger.debug(f"No se encontraron liderazgos para empleado: {leader_id}")
                return []
            
            # Obtener equipos correspondientes
            team_ids = [membership.team_id for membership in leadership_memberships]
            teams = []
            
            for team_id in team_ids:
                try:
                    team = await self._team_repo.get_team_by_id(team_id)
                    if team and team.is_active:
                        teams.append(team)
                except TeamRepositoryError as e:
                    self._logger.warning(
                        f"Error al obtener equipo {team_id} para líder {leader_id}: {e}"
                    )
                    continue
            
            # Convertir a schemas de salida
            team_schemas = [TeamSchema.model_validate(team) for team in teams]
            
            # Ordenar por nombre para consistencia
            team_schemas.sort(key=lambda t: t.name.lower())
            
            self._logger.debug(
                f"Encontrados {len(team_schemas)} equipos liderados por empleado: {leader_id}"
            )
            
            return team_schemas
            
        except TeamMembershipRepositoryError as e:
            self._logger.error(f"Error de repositorio al buscar equipos por líder: {e}")
            raise TeamDomainError(
                f"Error al buscar equipos por líder: {e.message}",
                operation="find_teams_by_leader",
                entity_type="Team",
                entity_id=str(leader_id),
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar equipos por líder: {e}")
            raise TeamDomainError(
                f"Error inesperado al buscar equipos por líder: {str(e)}",
                operation="find_teams_by_leader",
                entity_type="Team",
                entity_id=str(leader_id),
                original_error=e
            )

    async def find_teams_by_project(
        self,
        project_id: int,
        active_only: bool = True
    ) -> List[TeamSchema]:
        """
        Encuentra equipos asignados a un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            active_only: Si solo incluir equipos activos
            
        Returns:
            List[TeamSchema]: Lista de equipos asignados al proyecto
            
        Raises:
            ValidationError: Si el ID del proyecto no es válido
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(f"Buscando equipos asignados al proyecto: {project_id}")
            
            # Validar parámetros
            if not isinstance(project_id, int) or project_id <= 0:
                raise ValidationError("El ID del proyecto debe ser un entero positivo")
            
            # En una implementación real, aquí consultaríamos una tabla de
            # asignaciones proyecto-equipo. Por ahora, simulamos la búsqueda
            # basándose en metadatos o campos relacionados en el equipo
            
            all_teams = await self._team_repo.get_all_teams()
            project_teams = []
            
            for team in all_teams:
                # Simulamos que los equipos tienen información de proyecto
                # En implementación real, esto sería una consulta JOIN
                if await self._is_team_assigned_to_project(team.id, project_id):
                    project_teams.append(team)
            
            # Filtrar equipos según estado si es necesario
            if active_only:
                project_teams = [team for team in project_teams if team.is_active]
            
            # Convertir a schemas de salida
            team_schemas = [TeamSchema.model_validate(team) for team in project_teams]
            
            # Ordenar por nombre para consistencia
            team_schemas.sort(key=lambda t: t.name.lower())
            
            self._logger.debug(
                f"Encontrados {len(team_schemas)} equipos asignados al proyecto: {project_id}"
            )
            
            return team_schemas
            
        except TeamRepositoryError as e:
            self._logger.error(f"Error de repositorio al buscar equipos por proyecto: {e}")
            raise TeamDomainError(
                f"Error al buscar equipos por proyecto: {e.message}",
                operation="find_teams_by_project",
                entity_type="Team",
                entity_id=str(project_id),
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar equipos por proyecto: {e}")
            raise TeamDomainError(
                f"Error inesperado al buscar equipos por proyecto: {str(e)}",
                operation="find_teams_by_project",
                entity_type="Team",
                entity_id=str(project_id),
                original_error=e
            )

    async def find_teams_by_skill_set(
        self,
        required_skills: List[str],
        match_all: bool = False
    ) -> List[TeamSchema]:
        """
        Encuentra equipos que poseen un conjunto específico de habilidades.
        
        Args:
            required_skills: Lista de habilidades requeridas
            match_all: Si debe coincidir con todas las habilidades (True) o al menos una (False)
            
        Returns:
            List[TeamSchema]: Lista de equipos que cumplen con los criterios de habilidades
            
        Raises:
            ValidationError: Si las habilidades no son válidas
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(f"Buscando equipos con habilidades: {required_skills}")
            
            # Validar parámetros
            if not required_skills:
                raise ValidationError("Debe especificar al menos una habilidad")
            
            if not isinstance(required_skills, list):
                raise ValidationError("required_skills debe ser una lista")
            
            # Validar que las habilidades sean strings no vacías
            for skill in required_skills:
                if not isinstance(skill, str) or not skill.strip():
                    raise ValidationError("Todas las habilidades deben ser strings no vacías")
            
            # Normalizar habilidades (lowercase, sin espacios extra)
            normalized_skills = {skill.strip().lower() for skill in required_skills}
            
            all_teams = await self._team_repo.get_all_teams()
            matching_teams = []
            
            for team in all_teams:
                # Solo incluir equipos activos (sin parámetro include_inactive)
                if not team.is_active:
                    continue
                    
                # Obtener habilidades del equipo basándose en sus miembros
                team_skills = await self._get_team_skills(team.id)
                
                # Verificar si el equipo cumple con los criterios de habilidades
                if match_all:
                    # Debe tener todas las habilidades requeridas
                    if normalized_skills.issubset(team_skills):
                        matching_teams.append(team)
                else:
                    # Debe tener al menos una habilidad requerida
                    if normalized_skills.intersection(team_skills):
                        matching_teams.append(team)
            
            # Convertir a schemas de salida
            team_schemas = [TeamSchema.model_validate(team) for team in matching_teams]
            
            # Ordenar por nombre para consistencia
            team_schemas.sort(key=lambda t: t.name.lower())
            
            self._logger.debug(
                f"Encontrados {len(team_schemas)} equipos con habilidades requeridas: "
                f"{', '.join(required_skills)}"
            )
            
            return team_schemas
            
        except TeamRepositoryError as e:
            self._logger.error(f"Error de repositorio al buscar equipos por habilidades: {e}")
            raise TeamDomainError(
                f"Error al buscar equipos por habilidades: {e.message}",
                operation="find_teams_by_skill_set",
                entity_type="Team",
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar equipos por habilidades: {e}")
            raise TeamDomainError(
                f"Error inesperado al buscar equipos por habilidades: {str(e)}",
                operation="find_teams_by_skill_set",
                entity_type="Team",
                original_error=e
            )

    async def find_teams_by_date_range(
        self,
        start_date: pendulum.DateTime,
        end_date: pendulum.DateTime,
        include_inactive: bool = False
    ) -> List[TeamSchema]:
        """
        Encuentra equipos dentro de un rango de fechas específico.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            include_inactive: Si incluir equipos inactivos en la búsqueda
            
        Returns:
            List[TeamSchema]: Lista de equipos creados dentro del rango de fechas
            
        Raises:
            ValidationError: Si las fechas no son válidas
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(
                f"Buscando equipos por rango de fechas: {start_date} - {end_date}"
            )
            
            # Validar parámetros
            if not isinstance(start_date, pendulum.DateTime) or not isinstance(end_date, pendulum.DateTime):
                raise ValidationError("Las fechas deben ser objetos pendulum.DateTime")
            
            if start_date >= end_date:
                raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
            
            # Validar que el rango no sea excesivamente amplio (más de 10 años)
            if (end_date - start_date).total_seconds() > 10 * 365 * 24 * 3600:
                raise ValidationError("El rango de fechas no puede exceder 10 años")
            
            all_teams = await self._team_repo.get_all_teams()
            matching_teams = []
            
            for team in all_teams:
                # Filtrar equipos según estado
                if not include_inactive and not team.is_active:
                    continue
                    
                # Usar siempre created_at como campo de fecha
                team_date = team.created_at
                
                if team_date:
                    # Convertir a pendulum para comparación consistente
                    team_pendulum = pendulum.instance(team_date)
                    
                    # Verificar si está dentro del rango
                    if start_date <= team_pendulum <= end_date:
                        matching_teams.append(team)
            
            # Convertir a schemas de salida
            team_schemas = [TeamSchema.model_validate(team) for team in matching_teams]
            
            # Ordenar por fecha de creación (más reciente primero)
            team_schemas.sort(
                key=lambda t: t.created_at,
                reverse=True
            )
            
            self._logger.debug(
                f"Encontrados {len(team_schemas)} equipos en rango de fechas: "
                f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}"
            )
            
            return team_schemas
            
        except TeamRepositoryError as e:
            self._logger.error(f"Error de repositorio al buscar equipos por fecha: {e}")
            raise TeamDomainError(
                f"Error al buscar equipos por rango de fechas: {e.message}",
                operation="find_teams_by_date_range",
                entity_type="Team",
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar equipos por fecha: {e}")
            raise TeamDomainError(
                f"Error inesperado al buscar equipos por rango de fechas: {str(e)}",
                operation="find_teams_by_date_range",
                entity_type="Team",
                original_error=e
            )

    # Métodos auxiliares privados

    async def _is_team_assigned_to_project(
        self, team_id: int, project_id: int
    ) -> bool:
        """
        Verifica si un equipo está asignado a un proyecto específico.
        
        En una implementación real, esto consultaría una tabla de
        asignaciones proyecto-equipo.
        """
        try:
            # Simulación: asumimos que algunos equipos están asignados
            # basándose en una lógica simple (en implementación real sería una consulta)
            
            # Por ejemplo, equipos con ID par están asignados a proyectos con ID impar
            # y viceversa (solo para simulación)
            return (team_id % 2) != (project_id % 2)
            
        except Exception as e:
            self._logger.warning(
                f"Error al verificar asignación equipo-proyecto: {e}"
            )
            return False

    async def _get_team_skills(self, team_id: int) -> Set[str]:
        """
        Obtiene el conjunto de habilidades de un equipo basándose en sus miembros.
        
        En una implementación real, esto consultaría las habilidades
        de los empleados miembros del equipo.
        """
        try:
            # Obtener miembros del equipo
            members = await self._membership_repo.get_team_members(team_id)
            
            # Simulación: generar habilidades basándose en roles y departamento
            team_skills = set()
            
            for member in members:
                # En implementación real, consultaríamos las habilidades del empleado
                # Por ahora, simulamos basándose en el rol
                if member.role == "leader":
                    team_skills.update(["leadership", "management", "communication"])
                elif member.role == "coordinator":
                    team_skills.update(["coordination", "planning", "organization"])
                elif member.role == "specialist":
                    team_skills.update(["technical", "analysis", "problem_solving"])
                else:  # member
                    team_skills.update(["collaboration", "execution", "support"])
            
            # Agregar habilidades generales del equipo
            team = await self._team_repo.get_team_by_id(team_id)
            if team and team.department:
                dept_lower = team.department.lower()
                if "it" in dept_lower:
                    team_skills.update(["programming", "systems", "technology"])
                elif "hr" in dept_lower:
                    team_skills.update(["recruitment", "training", "policies"])
                elif "finance" in dept_lower:
                    team_skills.update(["accounting", "budgeting", "analysis"])
                elif "marketing" in dept_lower:
                    team_skills.update(["campaigns", "branding", "digital"])
            
            return team_skills
            
        except Exception as e:
            self._logger.warning(f"Error al obtener habilidades del equipo {team_id}: {e}")
            return set()