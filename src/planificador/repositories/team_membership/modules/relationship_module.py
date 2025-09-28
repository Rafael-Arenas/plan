# src/planificador/repositories/team_membership/relationship_module.py

"""
Módulo de relaciones para el repositorio TeamMembership.

Este módulo implementa las operaciones de gestión de relaciones
entre membresías de equipos, empleados y equipos, siguiendo los patrones establecidos del proyecto.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de relaciones
    - Dependency Injection: Recibe dependencias por constructor
    - Error Handling: Manejo robusto de excepciones con logging estructurado
    - Async/Await: Operaciones asíncronas para mejor performance

Uso:
    ```python
    relationship_module = TeamMembershipRelationshipModule(session, logger)
    memberships = await relationship_module.get_memberships_with_employee_and_team()
    ```
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date

from loguru import logger
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload, joinedload

from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.repositories.base_repository import BaseRepository
from planificador.repositories.team_membership.interfaces.relationship_interface import ITeamMembershipRelationshipOperations
from planificador.exceptions.repository import TeamMembershipRepositoryError, convert_sqlalchemy_error


class TeamMembershipRelationshipModule(BaseRepository[TeamMembership], ITeamMembershipRelationshipOperations):
    """
    Módulo para operaciones de relaciones de membresías de equipos.
    
    Hereda de BaseRepository para operaciones estándar y implementa
    la interfaz ITeamMembershipRelationshipOperations para gestión de relaciones.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        _logger: Logger para registro de eventos
        model_class: Clase del modelo TeamMembership
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de relaciones de TeamMembership.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, TeamMembership)
        self._logger = logger.bind(module="TeamMembershipRelationshipModule")
    
    async def get_memberships_with_employee_and_team(
        self,
        membership_ids: Optional[List[int]] = None
    ) -> List[TeamMembership]:
        """
        Obtiene membresías con relaciones de empleado y equipo cargadas.
        
        Args:
            membership_ids: Lista de IDs de membresías (opcional, todas si None)
        
        Returns:
            List[TeamMembership]: Lista de membresías con relaciones cargadas
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo membresías con relaciones cargadas, IDs: {membership_ids}")
            
            query = select(TeamMembership).options(
                joinedload(TeamMembership.employee),
                joinedload(TeamMembership.team)
            )
            
            if membership_ids:
                query = query.where(TeamMembership.id.in_(membership_ids))
            
            query = query.order_by(TeamMembership.start_date.desc())
            
            result = await self.session.execute(query)
            memberships = result.unique().scalars().all()
            
            self._logger.debug(f"Obtenidas {len(memberships)} membresías con relaciones")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener membresías con relaciones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_memberships_with_employee_and_team",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresías con relaciones: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener membresías: {e}",
                operation="get_memberships_with_employee_and_team",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_employee_memberships_with_teams(
        self,
        employee_id: int
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías de un empleado con información del equipo.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            List[TeamMembership]: Lista de membresías con información del equipo
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo membresías del empleado {employee_id} con equipos")
            
            query = select(TeamMembership).options(
                joinedload(TeamMembership.team)
            ).where(
                TeamMembership.employee_id == employee_id
            ).order_by(TeamMembership.start_date.desc())
            
            result = await self.session.execute(query)
            memberships = result.unique().scalars().all()
            
            self._logger.debug(f"Obtenidas {len(memberships)} membresías con equipos para empleado {employee_id}")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener membresías del empleado con equipos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_memberships_with_teams",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresías del empleado con equipos: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener membresías: {e}",
                operation="get_employee_memberships_with_teams",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_team_memberships_with_employees(
        self,
        team_id: int
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías de un equipo con información del empleado.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            List[TeamMembership]: Lista de membresías con información del empleado
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo membresías del equipo {team_id} con empleados")
            
            query = select(TeamMembership).options(
                joinedload(TeamMembership.employee)
            ).where(
                TeamMembership.team_id == team_id
            ).order_by(TeamMembership.start_date.desc())
            
            result = await self.session.execute(query)
            memberships = result.unique().scalars().all()
            
            self._logger.debug(f"Obtenidas {len(memberships)} membresías con empleados para equipo {team_id}")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener membresías del equipo con empleados: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_memberships_with_employees",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresías del equipo con empleados: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener membresías: {e}",
                operation="get_team_memberships_with_employees",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def transfer_employee_between_teams(
        self,
        employee_id: int,
        from_team_id: int,
        to_team_id: int,
        transfer_date: date,
        new_role: Optional[MembershipRole] = None
    ) -> Tuple[TeamMembership, TeamMembership]:
        """
        Transfiere un empleado de un equipo a otro.
        
        Args:
            employee_id: ID del empleado
            from_team_id: ID del equipo origen
            to_team_id: ID del equipo destino
            transfer_date: Fecha de transferencia
            new_role: Nuevo rol en el equipo destino (opcional)
        
        Returns:
            Tuple[TeamMembership, TeamMembership]: Membresía finalizada y nueva membresía
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la transferencia
        """
        try:
            self._logger.debug(f"Transfiriendo empleado {employee_id} del equipo {from_team_id} al {to_team_id}")
            
            # Buscar la membresía activa en el equipo origen
            query = select(TeamMembership).where(
                and_(
                    TeamMembership.employee_id == employee_id,
                    TeamMembership.team_id == from_team_id,
                    TeamMembership.is_active == True
                )
            )
            
            result = await self.session.execute(query)
            current_membership = result.scalar_one_or_none()
            
            if not current_membership:
                raise TeamMembershipRepositoryError(
                    message=f"No se encontró membresía activa para empleado {employee_id} en equipo {from_team_id}",
                    operation="transfer_employee_between_teams",
                    entity_type="TeamMembership"
                )
            
            # Finalizar la membresía actual
            current_membership.end_date = transfer_date
            current_membership.is_active = False
            
            # Crear nueva membresía en el equipo destino
            new_membership = TeamMembership(
                employee_id=employee_id,
                team_id=to_team_id,
                role=new_role or current_membership.role,
                start_date=transfer_date,
                is_active=True
            )
            
            self.session.add(new_membership)
            await self.session.flush()
            
            self._logger.info(f"Empleado {employee_id} transferido exitosamente del equipo {from_team_id} al {to_team_id}")
            return current_membership, new_membership
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en transferencia de empleado: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="transfer_employee_between_teams",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en transferencia de empleado: {e}")
            await self.session.rollback()
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado en transferencia: {e}",
                operation="transfer_employee_between_teams",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_overlapping_memberships(
        self,
        employee_id: int,
        start_date: date,
        end_date: Optional[date] = None
    ) -> List[TeamMembership]:
        """
        Obtiene membresías que se solapan con un período específico para un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período (opcional)
        
        Returns:
            List[TeamMembership]: Lista de membresías que se solapan
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Buscando membresías solapadas para empleado {employee_id} en período {start_date} - {end_date}")
            
            end_ref = end_date or date.today()
            
            query = select(TeamMembership).where(
                and_(
                    TeamMembership.employee_id == employee_id,
                    TeamMembership.start_date <= end_ref,
                    or_(
                        TeamMembership.end_date.is_(None),
                        TeamMembership.end_date >= start_date
                    )
                )
            ).order_by(TeamMembership.start_date)
            
            result = await self.session.execute(query)
            memberships = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(memberships)} membresías solapadas")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al buscar membresías solapadas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_overlapping_memberships",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar membresías solapadas: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al buscar solapamientos: {e}",
                operation="get_overlapping_memberships",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_membership_conflicts(
        self,
        employee_id: int,
        exclude_membership_id: Optional[int] = None
    ) -> List[TeamMembership]:
        """
        Identifica conflictos de membresías activas para un empleado.
        
        Args:
            employee_id: ID del empleado
            exclude_membership_id: ID de membresía a excluir (opcional)
        
        Returns:
            List[TeamMembership]: Lista de membresías en conflicto
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Identificando conflictos de membresías para empleado {employee_id}")
            
            query = select(TeamMembership).where(
                and_(
                    TeamMembership.employee_id == employee_id,
                    TeamMembership.is_active == True
                )
            )
            
            if exclude_membership_id:
                query = query.where(TeamMembership.id != exclude_membership_id)
            
            result = await self.session.execute(query)
            active_memberships = result.scalars().all()
            
            # Si hay más de una membresía activa, hay conflicto
            conflicts = list(active_memberships) if len(active_memberships) > 1 else []
            
            self._logger.debug(f"Encontrados {len(conflicts)} conflictos de membresías")
            return conflicts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al identificar conflictos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_membership_conflicts",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al identificar conflictos: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al identificar conflictos: {e}",
                operation="get_membership_conflicts",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_membership_history(
        self,
        employee_id: int
    ) -> List[TeamMembership]:
        """
        Obtiene el historial completo de membresías de un empleado.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            List[TeamMembership]: Lista ordenada cronológicamente de membresías
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo historial de membresías para empleado {employee_id}")
            
            query = select(TeamMembership).options(
                joinedload(TeamMembership.team)
            ).where(
                TeamMembership.employee_id == employee_id
            ).order_by(TeamMembership.start_date.asc())
            
            result = await self.session.execute(query)
            memberships = result.unique().scalars().all()
            
            self._logger.debug(f"Obtenido historial de {len(memberships)} membresías")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener historial de membresías: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_membership_history",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener historial de membresías: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener historial: {e}",
                operation="get_membership_history",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_role_change_history(
        self,
        employee_id: int
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de cambios de rol de un empleado.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            List[Dict[str, Any]]: Lista de cambios de rol con detalles
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo historial de cambios de rol para empleado {employee_id}")
            
            # Obtener todas las membresías ordenadas por fecha
            memberships = await self.get_membership_history(employee_id)
            
            role_changes = []
            previous_role = None
            
            for membership in memberships:
                if previous_role and previous_role != membership.role:
                    role_changes.append({
                        'membership_id': membership.id,
                        'team_id': membership.team_id,
                        'team_name': membership.team.name if membership.team else None,
                        'previous_role': previous_role,
                        'new_role': membership.role,
                        'change_date': membership.start_date,
                        'is_active': membership.is_active
                    })
                
                previous_role = membership.role
            
            self._logger.debug(f"Identificados {len(role_changes)} cambios de rol")
            return role_changes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener historial de cambios de rol: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_role_change_history",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener historial de cambios de rol: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener cambios de rol: {e}",
                operation="get_role_change_history",
                entity_type="TeamMembership",
                original_error=e
            )