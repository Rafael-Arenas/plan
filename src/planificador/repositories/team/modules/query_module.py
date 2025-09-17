# src/planificador/repositories/team/modules/query_module.py

"""
Módulo de consultas para operaciones de búsqueda del repositorio Team.

Este módulo implementa las operaciones de consulta, búsqueda y recuperación
de registros de equipos desde la base de datos con filtros avanzados.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de consulta y búsqueda
    - Query Optimization: Uso de selectinload para relaciones
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    query_module = TeamQueryModule(session)
    team = await query_module.get_team_by_id(team_id)
    teams = await query_module.search_teams_by_criteria(criteria)
    active_teams = await query_module.get_active_teams()
    ```
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.team import Team
from planificador.repositories.team.interfaces.query_interface import ITeamQueryOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    TeamRepositoryError,
    convert_sqlalchemy_error
)


class TeamQueryModule(BaseRepository[Team], ITeamQueryOperations):
    """
    Módulo para operaciones de consulta del repositorio Team.
    
    Implementa las operaciones de consulta y recuperación de registros
    de equipos desde la base de datos con soporte para filtros avanzados,
    búsquedas por criterios y optimización de consultas.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Team
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de consultas para equipos.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Team)
        self._logger = self._logger.bind(component="TeamQueryModule")
        self._logger.debug("TeamQueryModule inicializado")

    async def get_team_by_id(self, team_id: int) -> Optional[Team]:
        """
        Obtiene un equipo por su ID usando BaseRepository.
        
        Args:
            team_id: ID del equipo a buscar
        
        Returns:
            Optional[Team]: El equipo encontrado o None
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo equipo con ID: {team_id}")
        return await self.get_by_id(team_id)

    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """
        Obtiene un equipo por su nombre.
        
        Args:
            name: Nombre del equipo a buscar
        
        Returns:
            Optional[Team]: El equipo encontrado o None
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Buscando equipo por nombre: {name}")
        return await self.get_by_field("name", name)

    async def get_teams_by_department(self, department: str) -> List[Team]:
        """
        Obtiene todos los equipos de un departamento específico.
        
        Args:
            department: Nombre del departamento
        
        Returns:
            List[Team]: Lista de equipos del departamento
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Buscando equipos del departamento: {department}")
            
            stmt = (
                select(Team)
                .where(Team.department == department)
                .order_by(Team.name.asc())
            )
            
            result = await self.session.execute(stmt)
            teams = result.scalars().all()
            
            self._logger.debug(
                f"Encontrados {len(teams)} equipos en departamento {department}"
            )
            
            return list(teams)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al buscar equipos por departamento: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_teams_by_department",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar equipos por departamento: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_teams_by_department",
                entity_type="Team",
                original_error=e
            )

    async def get_active_teams(self) -> List[Team]:
        """
        Obtiene todos los equipos activos.
        
        Returns:
            List[Team]: Lista de equipos activos
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo todos los equipos activos")
            
            stmt = (
                select(Team)
                .where(Team.is_active == True)
                .order_by(Team.name.asc())
            )
            
            result = await self.session.execute(stmt)
            teams = result.scalars().all()
            
            self._logger.debug(f"Encontrados {len(teams)} equipos activos")
            
            return list(teams)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener equipos activos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_active_teams",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener equipos activos: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_active_teams",
                entity_type="Team",
                original_error=e
            )

    async def get_inactive_teams(self) -> List[Team]:
        """
        Obtiene todos los equipos inactivos.
        
        Returns:
            List[Team]: Lista de equipos inactivos
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo todos los equipos inactivos")
            
            stmt = (
                select(Team)
                .where(Team.is_active == False)
                .order_by(Team.name.asc())
            )
            
            result = await self.session.execute(stmt)
            teams = result.scalars().all()
            
            self._logger.debug(f"Encontrados {len(teams)} equipos inactivos")
            
            return list(teams)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener equipos inactivos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_inactive_teams",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener equipos inactivos: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_inactive_teams",
                entity_type="Team",
                original_error=e
            )

    async def search_teams_by_criteria(
        self, 
        criteria: Dict[str, Any]
    ) -> List[Team]:
        """
        Busca equipos por múltiples criterios.
        
        Args:
            criteria: Diccionario con criterios de búsqueda
                - name: Nombre del equipo (búsqueda parcial)
                - department: Departamento exacto
                - is_active: Estado activo (True/False)
                - description: Descripción (búsqueda parcial)
        
        Returns:
            List[Team]: Lista de equipos que cumplen los criterios
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la búsqueda
        """
        try:
            self._logger.debug(f"Buscando equipos con criterios: {criteria}")
            
            stmt = select(Team)
            conditions = []
            
            # Filtro por nombre (búsqueda parcial, insensible a mayúsculas)
            if 'name' in criteria and criteria['name']:
                conditions.append(
                    Team.name.ilike(f"%{criteria['name']}%")
                )
            
            # Filtro por departamento (exacto)
            if 'department' in criteria and criteria['department']:
                conditions.append(
                    Team.department == criteria['department']
                )
            
            # Filtro por estado activo
            if 'is_active' in criteria:
                conditions.append(
                    Team.is_active == criteria['is_active']
                )
            
            # Filtro por descripción (búsqueda parcial)
            if 'description' in criteria and criteria['description']:
                conditions.append(
                    Team.description.ilike(f"%{criteria['description']}%")
                )
            
            # Aplicar condiciones si existen
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            stmt = stmt.order_by(Team.name.asc())
            
            result = await self.session.execute(stmt)
            teams = result.scalars().all()
            
            self._logger.debug(
                f"Encontrados {len(teams)} equipos que cumplen los criterios"
            )
            
            return list(teams)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al buscar equipos por criterios: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_teams_by_criteria",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar equipos por criterios: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="search_teams_by_criteria",
                entity_type="Team",
                original_error=e
            )

    async def get_teams_with_pagination(
        self, 
        limit: int = 10, 
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Team]:
        """
        Obtiene equipos con paginación y filtros opcionales.
        
        Args:
            limit: Número máximo de equipos a retornar
            offset: Número de equipos a omitir
            filters: Filtros opcionales a aplicar
        
        Returns:
            List[Team]: Lista paginada de equipos
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(
                f"Obteniendo equipos con paginación: limit={limit}, offset={offset}"
            )
            
            stmt = select(Team)
            
            # Aplicar filtros si se proporcionan
            if filters:
                conditions = []
                
                if 'department' in filters and filters['department']:
                    conditions.append(Team.department == filters['department'])
                
                if 'is_active' in filters:
                    conditions.append(Team.is_active == filters['is_active'])
                
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            
            stmt = (
                stmt
                .order_by(Team.name.asc())
                .limit(limit)
                .offset(offset)
            )
            
            result = await self.session.execute(stmt)
            teams = result.scalars().all()
            
            self._logger.debug(
                f"Obtenidos {len(teams)} equipos con paginación"
            )
            
            return list(teams)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener equipos con paginación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_teams_with_pagination",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener equipos con paginación: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_teams_with_pagination",
                entity_type="Team",
                original_error=e
            )

    async def count_teams(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número total de equipos con filtros opcionales.
        
        Args:
            filters: Filtros opcionales para el conteo
        
        Returns:
            int: Número total de equipos
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el conteo
        """
        try:
            self._logger.debug(f"Contando equipos con filtros: {filters}")
            
            stmt = select(func.count(Team.id))
            
            # Aplicar filtros si se proporcionan
            if filters:
                conditions = []
                
                if 'department' in filters and filters['department']:
                    conditions.append(Team.department == filters['department'])
                
                if 'is_active' in filters:
                    conditions.append(Team.is_active == filters['is_active'])
                
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            
            result = await self.session.execute(stmt)
            count = result.scalar() or 0
            
            self._logger.debug(f"Total de equipos encontrados: {count}")
            
            return count
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al contar equipos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_teams",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al contar equipos: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="count_teams",
                entity_type="Team",
                original_error=e
            )

    async def get_by_unique_field(
        self, 
        field_name: str, 
        value: Any
    ) -> Optional[Team]:
        """
        Obtiene un equipo por un campo único específico.
        
        Método de compatibilidad que delega en BaseRepository para
        mantener consistencia con otros módulos del sistema.
        
        Args:
            field_name: Nombre del campo único
            value: Valor a buscar en el campo
        
        Returns:
            Optional[Team]: El equipo encontrado o None
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(
            f"Buscando equipo por campo único {field_name} = {value}"
        )
        
        return await self.get_by_field(field_name, value)