# src/planificador/repositories/team_membership/modules/query_module.py

"""
Módulo de consultas para el repositorio TeamMembership.

Este módulo implementa las operaciones de consulta y búsqueda
para la entidad TeamMembership, siguiendo los patrones establecidos del proyecto.
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
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de consultas de TeamMembership.
        """
        super().__init__(session, TeamMembership)
        self._logger = logger.bind(module="TeamMembershipQueryModule")

    async def get_membership_by_id(self, membership_id: int) -> Optional[TeamMembership]:
        """
        Obtiene una membresía por su ID.
        """
        try:
            self._logger.debug(f"Obteniendo membresía por ID: {membership_id}")
            return await self.get_by_id(membership_id)
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener membresía por ID: {e}")
            raise convert_sqlalchemy_error(e, "get_membership_by_id", "TeamMembership", entity_id=membership_id)
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresía por ID: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_membership_by_id",
                entity_type="TeamMembership",
                entity_id=membership_id,
                original_error=e
            )

    async def get_memberships_by_employee(
        self, 
        employee_id: int,
        active_only: bool = True
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías de un empleado.
        """
        try:
            self._logger.debug(f"Obteniendo membresías para el empleado {employee_id}")
            query = select(self.model_class).where(self.model_class.employee_id == employee_id)
            if active_only:
                query = query.where(and_(
                    self.model_class.start_date <= date.today(),
                    or_(
                        self.model_class.end_date.is_(None),
                        self.model_class.end_date >= date.today()
                    )
                ))
            result = await self.session.execute(query)
            memberships = result.scalars().all()
            return list(memberships)
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener membresías por empleado: {e}")
            raise convert_sqlalchemy_error(e, "get_memberships_by_employee", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresías por empleado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_memberships_by_employee",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_memberships_by_team(
        self, 
        team_id: int,
        active_only: bool = True
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías de un equipo.
        """
        try:
            self._logger.debug(f"Obteniendo membresías para el equipo {team_id}")
            query = select(self.model_class).where(self.model_class.team_id == team_id)
            if active_only:
                query = query.where(and_(
                    self.model_class.start_date <= date.today(),
                    or_(
                        self.model_class.end_date.is_(None),
                        self.model_class.end_date >= date.today()
                    )
                ))
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener membresías por equipo: {e}")
            raise convert_sqlalchemy_error(e, "get_memberships_by_team", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresías por equipo: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_memberships_by_team",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_membership_by_employee_and_team(
        self,
        employee_id: int,
        team_id: int,
        active_only: bool = True
    ) -> Optional[TeamMembership]:
        """
        Obtiene la membresía específica de un empleado en un equipo.
        """
        try:
            self._logger.debug(f"Obteniendo membresía para empleado {employee_id} y equipo {team_id}")
            query = select(self.model_class).where(
                and_(
                    self.model_class.employee_id == employee_id,
                    self.model_class.team_id == team_id
                )
            )
            if active_only:
                query = query.where(and_(
                    self.model_class.start_date <= date.today(),
                    or_(
                        self.model_class.end_date.is_(None),
                        self.model_class.end_date >= date.today()
                    )
                ))
            result = await self.session.execute(query)
            return result.scalars().first()
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener membresía por empleado y equipo: {e}")
            raise convert_sqlalchemy_error(e, "get_membership_by_employee_and_team", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_membership_by_employee_and_team",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_memberships_by_role(
        self, 
        role: MembershipRole,
        active_only: bool = True
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías con un rol específico.
        """
        try:
            self._logger.debug(f"Obteniendo membresías para el rol {role}")
            query = select(self.model_class).where(self.model_class.role == role)
            if active_only:
                query = query.where(and_(
                    self.model_class.start_date <= date.today(),
                    or_(
                        self.model_class.end_date.is_(None),
                        self.model_class.end_date >= date.today()
                    )
                ))
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener membresías por rol: {e}")
            raise convert_sqlalchemy_error(e, "get_memberships_by_role", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_memberships_by_role",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_active_memberships(self) -> List[TeamMembership]:
        """
        Obtiene todas las membresías activas del sistema.
        """
        try:
            self._logger.debug("Obteniendo todas las membresías activas")
            today = date.today()
            query = select(self.model_class).where(
                and_(
                    self.model_class.start_date <= today,
                    or_(
                        self.model_class.end_date.is_(None),
                        self.model_class.end_date >= today
                    )
                )
            )
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener membresías activas: {e}")
            raise convert_sqlalchemy_error(e, "get_active_memberships", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener membresías activas: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_active_memberships",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_memberships_by_date_range(
        self,
        start_date: date,
        end_date: date,
        include_overlapping: bool = True
    ) -> List[TeamMembership]:
        """
        Obtiene membresías en un rango de fechas.
        """
        try:
            self._logger.debug(f"Obteniendo membresías entre {start_date} y {end_date}")
            if include_overlapping:
                query = select(self.model_class).where(
                    and_(
                        self.model_class.start_date <= end_date,
                        or_(
                            self.model_class.end_date.is_(None),
                            self.model_class.end_date >= start_date
                        )
                    )
                )
            else:
                query = select(self.model_class).where(
                    and_(
                        self.model_class.start_date >= start_date,
                        self.model_class.end_date <= end_date
                    )
                )
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener membresías por rango de fechas: {e}")
            raise convert_sqlalchemy_error(e, "get_memberships_by_date_range", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_memberships_by_date_range",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_current_memberships(self, as_of_date: Optional[date] = None) -> List[TeamMembership]:
        """
        Obtiene membresías vigentes en una fecha específica.
        """
        ref_date = as_of_date or date.today()
        try:
            self._logger.debug(f"Obteniendo membresías vigentes a fecha de {ref_date}")
            query = select(self.model_class).where(
                and_(
                    self.model_class.start_date <= ref_date,
                    or_(
                        self.model_class.end_date.is_(None),
                        self.model_class.end_date >= ref_date
                    )
                )
            )
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener membresías vigentes: {e}")
            raise convert_sqlalchemy_error(e, "get_current_memberships", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_current_memberships",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_future_memberships(self, from_date: Optional[date] = None) -> List[TeamMembership]:
        """
        Obtiene membresías futuras desde una fecha.
        """
        ref_date = from_date or date.today()
        try:
            self._logger.debug(f"Obteniendo membresías futuras desde {ref_date}")
            query = select(self.model_class).where(self.model_class.start_date > ref_date)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener membresías futuras: {e}")
            raise convert_sqlalchemy_error(e, "get_future_memberships", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_future_memberships",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_past_memberships(self, until_date: Optional[date] = None) -> List[TeamMembership]:
        """
        Obtiene membresías pasadas hasta una fecha.
        """
        ref_date = until_date or date.today()
        try:
            self._logger.debug(f"Obteniendo membresías pasadas hasta {ref_date}")
            query = select(self.model_class).where(self.model_class.end_date < ref_date)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener membresías pasadas: {e}")
            raise convert_sqlalchemy_error(e, "get_past_memberships", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_past_memberships",
                entity_type="TeamMembership",
                original_error=e
            )

    async def search_memberships(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TeamMembership]:
        """
        Busca membresías con filtros avanzados.
        """
        try:
            self._logger.debug(f"Buscando membresías con filtros: {filters}")
            query = select(self.model_class)
            
            conditions = []
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    conditions.append(getattr(self.model_class, key) == value)
            
            if conditions:
                query = query.where(and_(*conditions))

            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)
                
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al buscar membresías por filtros: {e}")
            raise convert_sqlalchemy_error(e, "search_memberships", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="search_memberships",
                entity_type="TeamMembership",
                original_error=e
            )

    async def count_memberships(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número de membresías que cumplen los criterios.
        """
        try:
            self._logger.debug(f"Contando membresías con filtros: {filters}")
            query = select(func.count(self.model_class.id))
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    if hasattr(self.model_class, key):
                        conditions.append(getattr(self.model_class, key) == value)
                if conditions:
                    query = query.where(and_(*conditions))
            
            result = await self.session.execute(query)
            count = result.scalar_one_or_none()
            return count if count is not None else 0
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al contar membresías por filtros: {e}")
            raise convert_sqlalchemy_error(e, "count_memberships", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="count_memberships",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_all_memberships(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías del sistema.
        """
        try:
            self._logger.debug(f"Obteniendo todas las membresías con límite {limit} y offset {offset}")
            query = select(self.model_class)
            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)
            
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener todas las membresías: {e}")
            raise convert_sqlalchemy_error(e, "get_all_memberships", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener todas las membresías: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_all_memberships",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[TeamMembership]:
        """
        Obtiene una entidad por un campo único específico.
        """
        try:
            self._logger.debug(f"Obteniendo membresía por campo único: {field_name}={value}")
            if not hasattr(self.model_class, field_name):
                raise TeamMembershipRepositoryError(f"Campo '{field_name}' no existe en el modelo.")

            query = select(self.model_class).where(getattr(self.model_class, field_name) == value)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener por campo único: {e}")
            raise convert_sqlalchemy_error(e, "get_by_unique_field", "TeamMembership")
        except Exception as e:
            self._logger.error(f"Error inesperado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_by_unique_field",
                entity_type="TeamMembership",
                original_error=e
            )