# src/planificador/repositories/team_membership/query_module.py

"""
Módulo de consultas para el repositorio TeamMembership.

Este módulo implementa las operaciones de consulta y búsqueda
para la entidad TeamMembership, siguiendo los patrones establecidos del proyecto.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de consulta
    - Dependency Injection: Recibe dependencias por constructor
    - Error Handling: Manejo robusto de excepciones con logging estructurado
    - Async/Await: Operaciones asíncronas para mejor performance

Uso:
    ```python
    query_module = TeamMembershipQueryModule(session, logger)
    memberships = await query_module.get_by_employee_id(employee_id)
    ```
"""

from typing import List, Optional, Dict, Any
from datetime import date

from loguru import logger
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.repositories.base_repository import BaseRepository
from planificador.repositories.team_membership.interfaces.query_interface import ITeamMembershipQueryOperations
from planificador.exceptions.repository import TeamMembershipRepositoryError, convert_sqlalchemy_error


class TeamMembershipQueryModule(BaseRepository[TeamMembership], ITeamMembershipQueryOperations):
    """
    Módulo para operaciones de consulta de membresías de equipos.
    
    Hereda de BaseRepository para operaciones estándar y implementa
    la interfaz ITeamMembershipQueryOperations para consultas específicas.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        _logger: Logger para registro de eventos
        model_class: Clase del modelo TeamMembership
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de consultas de TeamMembership.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, TeamMembership)
        self._logger = logger.bind(module="TeamMembershipQueryModule")
    
    async def get_by_id(self, membership_id: int) -> Optional[TeamMembership]:
        """
        Obtiene una membresía por su ID.
        
        Args:
            membership_id: ID de la membresía
        
        Returns:
            Optional[TeamMembership]: Membresía encontrada o None
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo membresía por ID: {membership_id}")
            
            # Usar el método get_by_id del BaseRepository
            membership = await self.get_by_id(membership_id)
            
            if membership:
                self._logger.debug(f"Membresía encontrada: ID {membership.id}")
            else:
                self._logger.debug(f"No se encontró membresía con ID {membership_id}")
            
            return membership
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener membresía ID {membership_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_id",
                entity_type="TeamMembership",
                entity_id=membership_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresía ID {membership_id}: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener membresía: {e}",
                operation="get_by_id",
                entity_type="TeamMembership",
                entity_id=membership_id,
                original_error=e
            )
    
    async def get_by_employee_id(
        self, 
        employee_id: int,
        active_only: bool = False
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías de un empleado.
        
        Args:
            employee_id: ID del empleado
            active_only: Si solo incluir membresías activas
        
        Returns:
            List[TeamMembership]: Lista de membresías del empleado
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo membresías del empleado ID {employee_id}, activas: {active_only}")
            
            query = select(TeamMembership).where(TeamMembership.employee_id == employee_id)
            
            if active_only:
                query = query.where(TeamMembership.is_active == True)
            
            query = query.order_by(TeamMembership.start_date.desc())
            
            result = await self.session.execute(query)
            memberships = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(memberships)} membresías para empleado ID {employee_id}")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener membresías del empleado ID {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_employee_id",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresías del empleado ID {employee_id}: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener membresías: {e}",
                operation="get_by_employee_id",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_by_team_id(
        self, 
        team_id: int,
        active_only: bool = False
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías de un equipo.
        
        Args:
            team_id: ID del equipo
            active_only: Si solo incluir membresías activas
        
        Returns:
            List[TeamMembership]: Lista de membresías del equipo
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo membresías del equipo ID {team_id}, activas: {active_only}")
            
            query = select(TeamMembership).where(TeamMembership.team_id == team_id)
            
            if active_only:
                query = query.where(TeamMembership.is_active == True)
            
            query = query.order_by(TeamMembership.start_date.desc())
            
            result = await self.session.execute(query)
            memberships = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(memberships)} membresías para equipo ID {team_id}")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener membresías del equipo ID {team_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_team_id",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresías del equipo ID {team_id}: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener membresías: {e}",
                operation="get_by_team_id",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_by_role(
        self, 
        role: MembershipRole,
        active_only: bool = False
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías con un rol específico.
        
        Args:
            role: Rol a buscar
            active_only: Si solo incluir membresías activas
        
        Returns:
            List[TeamMembership]: Lista de membresías con el rol
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo membresías con rol {role}, activas: {active_only}")
            
            query = select(TeamMembership).where(TeamMembership.role == role)
            
            if active_only:
                query = query.where(TeamMembership.is_active == True)
            
            query = query.order_by(TeamMembership.start_date.desc())
            
            result = await self.session.execute(query)
            memberships = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(memberships)} membresías con rol {role}")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener membresías con rol {role}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_role",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresías con rol {role}: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener membresías: {e}",
                operation="get_by_role",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_active_memberships(
        self, 
        as_of_date: Optional[date] = None
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías activas en una fecha específica.
        
        Args:
            as_of_date: Fecha de referencia (opcional, default hoy)
        
        Returns:
            List[TeamMembership]: Lista de membresías activas
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            reference_date = as_of_date or date.today()
            self._logger.debug(f"Obteniendo membresías activas al {reference_date}")
            
            query = select(TeamMembership).where(
                and_(
                    TeamMembership.is_active == True,
                    TeamMembership.start_date <= reference_date,
                    or_(
                        TeamMembership.end_date.is_(None),
                        TeamMembership.end_date >= reference_date
                    )
                )
            ).order_by(TeamMembership.start_date.desc())
            
            result = await self.session.execute(query)
            memberships = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(memberships)} membresías activas al {reference_date}")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener membresías activas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_active_memberships",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresías activas: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener membresías activas: {e}",
                operation="get_active_memberships",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: Optional[date] = None
    ) -> List[TeamMembership]:
        """
        Obtiene membresías que se solapan con un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango (opcional)
        
        Returns:
            List[TeamMembership]: Lista de membresías en el rango
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            end_ref = end_date or date.today()
            self._logger.debug(f"Obteniendo membresías en rango {start_date} - {end_ref}")
            
            query = select(TeamMembership).where(
                and_(
                    TeamMembership.start_date <= end_ref,
                    or_(
                        TeamMembership.end_date.is_(None),
                        TeamMembership.end_date >= start_date
                    )
                )
            ).order_by(TeamMembership.start_date.desc())
            
            result = await self.session.execute(query)
            memberships = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(memberships)} membresías en el rango")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener membresías por rango de fechas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_date_range",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresías por rango de fechas: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener membresías: {e}",
                operation="get_by_date_range",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def search_memberships(
        self,
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TeamMembership]:
        """
        Busca membresías según criterios específicos.
        
        Args:
            criteria: Diccionario con criterios de búsqueda
            limit: Límite de resultados (opcional)
            offset: Desplazamiento de resultados (opcional)
        
        Returns:
            List[TeamMembership]: Lista de membresías que cumplen los criterios
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la búsqueda
        """
        try:
            self._logger.debug(f"Buscando membresías con criterios: {criteria}")
            
            query = select(TeamMembership)
            
            # Aplicar filtros según criterios
            if 'employee_id' in criteria:
                query = query.where(TeamMembership.employee_id == criteria['employee_id'])
            
            if 'team_id' in criteria:
                query = query.where(TeamMembership.team_id == criteria['team_id'])
            
            if 'role' in criteria:
                query = query.where(TeamMembership.role == criteria['role'])
            
            if 'is_active' in criteria:
                query = query.where(TeamMembership.is_active == criteria['is_active'])
            
            if 'start_date_from' in criteria:
                query = query.where(TeamMembership.start_date >= criteria['start_date_from'])
            
            if 'start_date_to' in criteria:
                query = query.where(TeamMembership.start_date <= criteria['start_date_to'])
            
            if 'end_date_from' in criteria:
                query = query.where(TeamMembership.end_date >= criteria['end_date_from'])
            
            if 'end_date_to' in criteria:
                query = query.where(TeamMembership.end_date <= criteria['end_date_to'])
            
            # Ordenar por fecha de inicio descendente
            query = query.order_by(TeamMembership.start_date.desc())
            
            # Aplicar límite y offset si se especifican
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            result = await self.session.execute(query)
            memberships = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(memberships)} membresías con los criterios")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al buscar membresías: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_memberships",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar membresías: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al buscar membresías: {e}",
                operation="search_memberships",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def count_memberships(
        self,
        criteria: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Cuenta membresías según criterios específicos.
        
        Args:
            criteria: Diccionario con criterios de filtrado (opcional)
        
        Returns:
            int: Número de membresías que cumplen los criterios
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el conteo
        """
        try:
            self._logger.debug(f"Contando membresías con criterios: {criteria}")
            
            query = select(func.count(TeamMembership.id))
            
            # Aplicar filtros si se proporcionan criterios
            if criteria:
                if 'employee_id' in criteria:
                    query = query.where(TeamMembership.employee_id == criteria['employee_id'])
                
                if 'team_id' in criteria:
                    query = query.where(TeamMembership.team_id == criteria['team_id'])
                
                if 'role' in criteria:
                    query = query.where(TeamMembership.role == criteria['role'])
                
                if 'is_active' in criteria:
                    query = query.where(TeamMembership.is_active == criteria['is_active'])
            
            result = await self.session.execute(query)
            count = result.scalar()
            
            self._logger.debug(f"Contadas {count} membresías")
            return count or 0
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al contar membresías: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_memberships",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al contar membresías: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al contar membresías: {e}",
                operation="count_memberships",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías con paginación opcional.
        
        Args:
            limit: Límite de resultados (opcional)
            offset: Desplazamiento de resultados (opcional)
        
        Returns:
            List[TeamMembership]: Lista de todas las membresías
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo todas las membresías, limit: {limit}, offset: {offset}")
            
            # Usar el método get_all del BaseRepository con paginación
            memberships = await super().get_all(limit=limit, offset=offset)
            
            self._logger.debug(f"Obtenidas {len(memberships)} membresías")
            return memberships
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener todas las membresías: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_all",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener todas las membresías: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener membresías: {e}",
                operation="get_all",
                entity_type="TeamMembership",
                original_error=e
            )