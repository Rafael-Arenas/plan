# src/planificador/repositories/team/modules/relationship_module.py

"""
Módulo de relaciones para operaciones de membresías del repositorio Team.

Este módulo implementa las operaciones de gestión de membresías, liderazgo
y relaciones entre equipos y empleados con validaciones de negocio.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de relaciones y membresías
    - Business Logic: Validaciones específicas del dominio
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    relationship_module = TeamRelationshipModule(session)
    membership = await relationship_module.add_team_member(team_id, employee_id, role)
    leader = await relationship_module.assign_team_leader(team_id, employee_id)
    members = await relationship_module.get_team_members(team_id)
    ```
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.team import Team
from planificador.models.team_membership import TeamMembership
from planificador.repositories.team.interfaces.relationship_interface import ITeamRelationshipOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    TeamRepositoryError,
    convert_sqlalchemy_error
)
import pendulum


class TeamRelationshipModule(BaseRepository[Team], ITeamRelationshipOperations):
    """
    Módulo para operaciones de relaciones del repositorio Team.
    
    Implementa las operaciones de gestión de membresías, liderazgo
    y relaciones entre equipos y empleados con validaciones de negocio
    y manejo de fechas usando Pendulum.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Team
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de relaciones para equipos.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Team)
        self._logger = self._logger.bind(component="TeamRelationshipModule")
        self._logger.debug("TeamRelationshipModule inicializado")

    async def add_team_member(
        self, 
        team_id: int, 
        employee_id: int, 
        role: str,
        start_date: Optional[date] = None,
        is_leader: bool = False
    ) -> TeamMembership:
        """
        Agrega un miembro a un equipo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            role: Rol del miembro en el equipo
            start_date: Fecha de inicio (opcional, default hoy)
            is_leader: Si es líder del equipo
        
        Returns:
            TeamMembership: La membresía creada
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la creación
        """
        try:
            self._logger.debug(
                f"Agregando miembro {employee_id} al equipo {team_id} "
                f"con rol {role}, líder: {is_leader}"
            )
            
            # Usar fecha actual si no se proporciona
            if start_date is None:
                start_date = pendulum.now().date()
            
            # Crear la membresía
            membership_data = {
                'team_id': team_id,
                'employee_id': employee_id,
                'role': role,
                'start_date': start_date,
                'is_leader': is_leader,
                'is_active': True
            }
            
            membership = TeamMembership(**membership_data)
            self.session.add(membership)
            await self.session.flush()
            
            self._logger.info(
                f"Miembro agregado exitosamente: empleado {employee_id} "
                f"al equipo {team_id} como {role}"
            )
            
            return membership
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al agregar miembro al equipo: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="add_team_member",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al agregar miembro: {e}")
            await self.session.rollback()
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="add_team_member",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}",
                original_error=e
            )

    async def remove_team_member(
        self, 
        team_id: int, 
        employee_id: int,
        end_date: Optional[date] = None
    ) -> bool:
        """
        Remueve un miembro de un equipo (marca como inactivo).
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            end_date: Fecha de fin (opcional, default hoy)
        
        Returns:
            bool: True si fue removido exitosamente
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la remoción
        """
        try:
            self._logger.debug(
                f"Removiendo miembro {employee_id} del equipo {team_id}"
            )
            
            # Usar fecha actual si no se proporciona
            if end_date is None:
                end_date = pendulum.now().date()
            
            # Buscar la membresía activa
            stmt = (
                select(TeamMembership)
                .where(
                    and_(
                        TeamMembership.team_id == team_id,
                        TeamMembership.employee_id == employee_id,
                        TeamMembership.is_active == True
                    )
                )
            )
            
            result = await self.session.execute(stmt)
            membership = result.scalar_one_or_none()
            
            if not membership:
                raise TeamRepositoryError(
                    message=f"Membresía activa no encontrada para empleado {employee_id} en equipo {team_id}",
                    operation="remove_team_member",
                    entity_type="TeamMembership",
                    entity_id=f"team_{team_id}_employee_{employee_id}"
                )
            
            # Marcar como inactiva y establecer fecha de fin
            membership.is_active = False
            membership.end_date = end_date
            
            await self.session.flush()
            
            self._logger.info(
                f"Miembro removido exitosamente: empleado {employee_id} "
                f"del equipo {team_id}"
            )
            
            return True
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al remover miembro del equipo: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="remove_team_member",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al remover miembro: {e}")
            await self.session.rollback()
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="remove_team_member",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}",
                original_error=e
            )

    async def assign_team_leader(
        self, 
        team_id: int, 
        employee_id: int,
        start_date: Optional[date] = None
    ) -> TeamMembership:
        """
        Asigna un líder a un equipo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado que será líder
            start_date: Fecha de inicio del liderazgo
        
        Returns:
            TeamMembership: La membresía de liderazgo
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la asignación
        """
        try:
            self._logger.debug(
                f"Asignando líder {employee_id} al equipo {team_id}"
            )
            
            # Usar fecha actual si no se proporciona
            if start_date is None:
                start_date = pendulum.now().date()
            
            # Verificar si ya existe un líder activo
            existing_leader_stmt = (
                select(TeamMembership)
                .where(
                    and_(
                        TeamMembership.team_id == team_id,
                        TeamMembership.is_leader == True,
                        TeamMembership.is_active == True
                    )
                )
            )
            
            result = await self.session.execute(existing_leader_stmt)
            existing_leader = result.scalar_one_or_none()
            
            # Si existe un líder activo, marcarlo como inactivo
            if existing_leader:
                existing_leader.is_active = False
                existing_leader.end_date = start_date
                self._logger.info(
                    f"Líder anterior {existing_leader.employee_id} "
                    f"marcado como inactivo en equipo {team_id}"
                )
            
            # Buscar si el empleado ya es miembro del equipo
            member_stmt = (
                select(TeamMembership)
                .where(
                    and_(
                        TeamMembership.team_id == team_id,
                        TeamMembership.employee_id == employee_id,
                        TeamMembership.is_active == True
                    )
                )
            )
            
            result = await self.session.execute(member_stmt)
            existing_membership = result.scalar_one_or_none()
            
            if existing_membership:
                # Actualizar membresía existente para hacerla líder
                existing_membership.is_leader = True
                leadership = existing_membership
            else:
                # Crear nueva membresía como líder
                leadership = await self.add_team_member(
                    team_id=team_id,
                    employee_id=employee_id,
                    role="Leader",
                    start_date=start_date,
                    is_leader=True
                )
            
            await self.session.flush()
            
            self._logger.info(
                f"Líder asignado exitosamente: empleado {employee_id} "
                f"al equipo {team_id}"
            )
            
            return leadership
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al asignar líder: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="assign_team_leader",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_leader_{employee_id}"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al asignar líder: {e}")
            await self.session.rollback()
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="assign_team_leader",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_leader_{employee_id}",
                original_error=e
            )

    async def get_team_members(
        self, 
        team_id: int, 
        active_only: bool = True
    ) -> List[TeamMembership]:
        """
        Obtiene todos los miembros de un equipo.
        
        Args:
            team_id: ID del equipo
            active_only: Si solo incluir miembros activos
        
        Returns:
            List[TeamMembership]: Lista de membresías
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(
                f"Obteniendo miembros del equipo {team_id}, "
                f"solo activos: {active_only}"
            )
            
            stmt = (
                select(TeamMembership)
                .options(
                    selectinload(TeamMembership.employee),
                    selectinload(TeamMembership.team)
                )
                .where(TeamMembership.team_id == team_id)
                .order_by(
                    TeamMembership.is_leader.desc(),
                    TeamMembership.start_date.asc()
                )
            )
            
            if active_only:
                stmt = stmt.where(TeamMembership.is_active == True)
            
            result = await self.session.execute(stmt)
            memberships = result.scalars().all()
            
            self._logger.debug(
                f"Encontradas {len(memberships)} membresías para equipo {team_id}"
            )
            
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener miembros del equipo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_members",
                entity_type="TeamMembership",
                entity_id=str(team_id)
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener miembros: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_team_members",
                entity_type="TeamMembership",
                entity_id=str(team_id),
                original_error=e
            )

    async def get_team_leader(self, team_id: int) -> Optional[TeamMembership]:
        """
        Obtiene el líder actual de un equipo.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            Optional[TeamMembership]: La membresía del líder o None
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Obteniendo líder del equipo {team_id}")
            
            stmt = (
                select(TeamMembership)
                .options(
                    selectinload(TeamMembership.employee),
                    selectinload(TeamMembership.team)
                )
                .where(
                    and_(
                        TeamMembership.team_id == team_id,
                        TeamMembership.is_leader == True,
                        TeamMembership.is_active == True
                    )
                )
            )
            
            result = await self.session.execute(stmt)
            leader = result.scalar_one_or_none()
            
            if leader:
                self._logger.debug(
                    f"Líder encontrado para equipo {team_id}: "
                    f"empleado {leader.employee_id}"
                )
            else:
                self._logger.debug(f"No se encontró líder para equipo {team_id}")
            
            return leader
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener líder del equipo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_leader",
                entity_type="TeamMembership",
                entity_id=str(team_id)
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener líder: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_team_leader",
                entity_type="TeamMembership",
                entity_id=str(team_id),
                original_error=e
            )

    async def get_employee_teams(
        self, 
        employee_id: int, 
        active_only: bool = True
    ) -> List[TeamMembership]:
        """
        Obtiene todos los equipos de un empleado.
        
        Args:
            employee_id: ID del empleado
            active_only: Si solo incluir membresías activas
        
        Returns:
            List[TeamMembership]: Lista de membresías del empleado
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(
                f"Obteniendo equipos del empleado {employee_id}, "
                f"solo activos: {active_only}"
            )
            
            stmt = (
                select(TeamMembership)
                .options(
                    selectinload(TeamMembership.team),
                    selectinload(TeamMembership.employee)
                )
                .where(TeamMembership.employee_id == employee_id)
                .order_by(
                    TeamMembership.is_active.desc(),
                    TeamMembership.start_date.desc()
                )
            )
            
            if active_only:
                stmt = stmt.where(TeamMembership.is_active == True)
            
            result = await self.session.execute(stmt)
            memberships = result.scalars().all()
            
            self._logger.debug(
                f"Encontradas {len(memberships)} membresías para empleado {employee_id}"
            )
            
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener equipos del empleado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_teams",
                entity_type="TeamMembership",
                entity_id=str(employee_id)
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener equipos del empleado: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_employee_teams",
                entity_type="TeamMembership",
                entity_id=str(employee_id),
                original_error=e
            )

    async def get_teams_with_members_details(self) -> List[Dict[str, Any]]:
        """
        Obtiene equipos con detalles de sus miembros.
        
        Returns:
            List[Dict[str, Any]]: Lista de equipos con información de miembros
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo equipos con detalles de miembros")
            
            # Obtener todos los equipos activos
            teams_stmt = (
                select(Team)
                .where(Team.is_active == True)
                .order_by(Team.name.asc())
            )
            
            teams_result = await self.session.execute(teams_stmt)
            teams = teams_result.scalars().all()
            
            teams_with_details = []
            
            for team in teams:
                # Obtener miembros del equipo
                members = await self.get_team_members(team.id, active_only=True)
                leader = await self.get_team_leader(team.id)
                
                team_details = {
                    'team': team,
                    'member_count': len(members),
                    'members': members,
                    'leader': leader,
                    'has_leader': leader is not None
                }
                
                teams_with_details.append(team_details)
            
            self._logger.debug(
                f"Obtenidos {len(teams_with_details)} equipos con detalles"
            )
            
            return teams_with_details
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener equipos con detalles: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_teams_with_members_details",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener equipos con detalles: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_teams_with_members_details",
                entity_type="Team",
                original_error=e
            )

    async def update_member_role(
        self, 
        team_id: int, 
        employee_id: int, 
        new_role: str
    ) -> TeamMembership:
        """
        Actualiza el rol de un miembro en un equipo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            new_role: Nuevo rol del miembro
        
        Returns:
            TeamMembership: La membresía actualizada
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la actualización
        """
        try:
            self._logger.debug(
                f"Actualizando rol del miembro {employee_id} "
                f"en equipo {team_id} a {new_role}"
            )
            
            # Buscar la membresía activa
            stmt = (
                select(TeamMembership)
                .where(
                    and_(
                        TeamMembership.team_id == team_id,
                        TeamMembership.employee_id == employee_id,
                        TeamMembership.is_active == True
                    )
                )
            )
            
            result = await self.session.execute(stmt)
            membership = result.scalar_one_or_none()
            
            if not membership:
                raise TeamRepositoryError(
                    message=f"Membresía activa no encontrada para empleado {employee_id} en equipo {team_id}",
                    operation="update_member_role",
                    entity_type="TeamMembership",
                    entity_id=f"team_{team_id}_employee_{employee_id}"
                )
            
            # Actualizar el rol
            old_role = membership.role
            membership.role = new_role
            
            await self.session.flush()
            
            self._logger.info(
                f"Rol actualizado exitosamente: empleado {employee_id} "
                f"en equipo {team_id} de {old_role} a {new_role}"
            )
            
            return membership
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al actualizar rol del miembro: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_member_role",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al actualizar rol: {e}")
            await self.session.rollback()
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="update_member_role",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}",
                original_error=e
            )