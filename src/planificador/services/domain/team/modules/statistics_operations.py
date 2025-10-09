# src/planificador/services/domain/team/modules/statistics_operations.py

"""
Módulo de Operaciones de Estadísticas del Dominio Team.

Este módulo implementa las operaciones de estadísticas y métricas de equipos,
proporcionando análisis cuantitativos sobre la composición, distribución
y tendencias de los equipos en el sistema.

Características:
    - Conteo de miembros por equipo
    - Distribución de equipos por estado
    - Análisis de tamaño promedio de equipos
    - Tendencias de creación de equipos
    - Métricas agregadas del sistema

Principios de Diseño:
    - Data-Driven: Decisiones basadas en datos reales
    - Performance: Consultas optimizadas para agregaciones
    - Accuracy: Cálculos precisos y confiables
    - Insights: Métricas útiles para la gestión

Uso:
    ```python
    stats_ops = TeamDomainStatisticsOperations(team_repo, membership_repo)
    member_counts = await stats_ops.get_team_member_counts()
    avg_size = await stats_ops.get_average_team_size()
    ```
"""

from typing import List, Dict, Optional
from datetime import datetime
import pendulum
from loguru import logger

from planificador.repositories.team import TeamRepositoryFacade
from planificador.repositories.team_membership import TeamMembershipRepositoryFacade
from planificador.services.domain.team.interfaces.statistics_operations_interface import (
    ITeamDomainStatisticsOperations, TeamCreationTrend
)
from planificador.exceptions.domain import (
    TeamDomainError, ValidationError
)
from planificador.exceptions.repository import (
    TeamRepositoryError, TeamMembershipRepositoryError
)


class TeamDomainStatisticsOperations(ITeamDomainStatisticsOperations):
    """
    Implementación de operaciones de estadísticas del dominio Team.
    
    Proporciona análisis cuantitativos y métricas sobre equipos,
    incluyendo conteos, promedios y tendencias temporales.
    
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
        Inicializa las operaciones de estadísticas del dominio Team.
        
        Args:
            team_repo: Repositorio de equipos
            membership_repo: Repositorio de membresías
        """
        self._team_repo = team_repo
        self._membership_repo = membership_repo
        self._logger = logger.bind(module="TeamDomainStatisticsOperations")
        
        self._logger.debug("TeamDomainStatisticsOperations inicializado")

    async def get_team_member_count(
        self,
        team_id: int
    ) -> int:
        """
        Obtiene el conteo de miembros de un equipo específico.
        
        Args:
            team_id: ID del equipo
            
        Returns:
            int: Número de miembros del equipo
            
        Raises:
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            logger.debug(f"Obteniendo conteo de miembros para equipo {team_id}")
            
            # Obtener conteo de miembros del equipo
            count = await self.membership_repository.count_team_members(team_id)
            
            logger.debug(f"Equipo {team_id} tiene {count} miembros")
            return count
            
        except TeamMembershipRepositoryError as e:
            logger.error(f"Error de repositorio al contar miembros del equipo {team_id}: {e}")
            raise TeamDomainError(
                f"Error al obtener conteo de miembros: {e.message}",
                operation="get_team_member_count",
                entity_type="Team",
                entity_id=str(team_id),
                original_error=e
            )
        except Exception as e:
            logger.error(f"Error inesperado al contar miembros del equipo {team_id}: {e}")
            raise TeamDomainError(
                f"Error inesperado al obtener conteo de miembros: {str(e)}",
                operation="get_team_member_count",
                entity_type="Team",
                entity_id=str(team_id),
                original_error=e
            )

    async def get_teams_count_by_status(self) -> Dict[str, int]:
        """
        Obtiene el conteo de equipos agrupados por estado.
        
        Returns:
            Dict[str, int]: Diccionario {status: count}
            
        Raises:
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            logger.debug("Obteniendo conteos de equipos por estado")
            
            # Obtener conteos por estado
            active_count = await self.team_repository.count_active_teams()
            inactive_count = await self.team_repository.count_inactive_teams()
            total_count = active_count + inactive_count
            
            status_counts = {
                "active": active_count,
                "inactive": inactive_count,
                "total": total_count
            }
            
            logger.debug(f"Conteos por estado: {status_counts}")
            
            return status_counts
            
        except TeamRepositoryError as e:
            logger.error(f"Error de repositorio en conteos por estado: {e}")
            raise TeamDomainError(
                f"Error al obtener conteos por estado: {e.message}",
                operation="get_teams_count_by_status",
                entity_type="Team",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Error inesperado en conteos por estado: {e}")
            raise TeamDomainError(
                f"Error inesperado al obtener conteos por estado: {str(e)}",
                operation="get_teams_count_by_status",
                entity_type="Team",
                original_error=e
            )

    async def get_average_team_size(
        self,
        active_only: bool = True
    ) -> float:
        """
        Calcula el tamaño promedio de los equipos.
        
        Args:
            active_only: Si solo incluir equipos activos
            
        Returns:
            float: Tamaño promedio de equipos
            
        Raises:
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            logger.debug(
                f"Calculando tamaño promedio de equipos "
                f"({'activos' if active_only else 'todos'})"
            )
            
            # Obtener todos los equipos según el filtro
            if active_only:
                teams = await self.team_repository.get_active_teams()
            else:
                teams = await self.team_repository.get_all_teams()
            
            if not teams:
                logger.warning("No hay equipos para calcular promedio")
                return 0.0
            
            # Obtener conteos de miembros para cada equipo
            total_members = 0
            for team in teams:
                try:
                    count = await self.membership_repository.count_team_members(team.id)
                    total_members += count
                except TeamMembershipRepositoryError as e:
                    logger.warning(f"Error al contar miembros del equipo {team.id}: {e}")
                    # Continuar con el siguiente equipo
            
            # Calcular promedio
            total_teams = len(teams)
            average_size = total_members / total_teams if total_teams > 0 else 0.0
            
            logger.debug(
                f"Tamaño promedio calculado: {average_size:.2f} "
                f"({total_members} miembros en {total_teams} equipos)"
            )
            
            return round(average_size, 2)
            
        except TeamRepositoryError as e:
            logger.error(f"Error de repositorio en cálculo de promedio: {e}")
            raise TeamDomainError(
                f"Error al calcular tamaño promedio: {e.message}",
                operation="get_average_team_size",
                entity_type="Team",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Error inesperado en cálculo de promedio: {e}")
            raise TeamDomainError(
                f"Error inesperado al calcular tamaño promedio: {str(e)}",
                operation="get_average_team_size",
                entity_type="Team",
                original_error=e
            )

    async def get_team_creation_trends(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "month"
    ) -> List[TeamCreationTrend]:
        """
        Obtiene las tendencias de creación de equipos en un período.
        
        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            group_by: Agrupación temporal ("day", "week", "month", "year")
            
        Returns:
            List[TeamCreationTrend]: Lista de tendencias por período
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            logger.debug(
                f"Obteniendo tendencias de creación: {start_date} a {end_date}, "
                f"agrupado por {group_by}"
            )
            
            # Validar parámetros
            if group_by not in ["day", "week", "month", "year"]:
                raise ValidationError(
                    "group_by debe ser 'day', 'week', 'month' o 'year'"
                )
            
            # Establecer fechas por defecto si no se proporcionan
            if end_date is None:
                end_date = pendulum.now()
            if start_date is None:
                # Por defecto, últimos 12 meses
                start_date = end_date.subtract(months=12)
            
            # Validar rango de fechas
            if start_date >= end_date:
                raise ValidationError(
                    "La fecha de inicio debe ser anterior a la fecha de fin"
                )
            
            # Obtener equipos en el rango de fechas
            teams = await self.team_repository.get_teams_by_date_range(
                start_date, end_date
            )
            
            # Agrupar por período
            trends = await self._group_teams_by_period(teams, group_by)
            
            logger.debug(
                f"Tendencias calculadas: {len(trends)} períodos"
            )
            
            return trends
            
        except TeamRepositoryError as e:
            logger.error(f"Error de repositorio en tendencias: {e}")
            raise TeamDomainError(
                f"Error al obtener tendencias de creación: {e.message}",
                operation="get_team_creation_trends",
                entity_type="Team",
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado en tendencias: {e}")
            raise TeamDomainError(
                f"Error inesperado al obtener tendencias: {str(e)}",
                operation="get_team_creation_trends",
                entity_type="Team",
                original_error=e
            )

    async def _group_teams_by_period(
        self,
        teams: List,
        group_by: str
    ) -> List[TeamCreationTrend]:
        """
        Agrupa equipos por período temporal.
        
        Args:
            teams: Lista de equipos
            group_by: Tipo de agrupación temporal
            
        Returns:
            List[TeamCreationTrend]: Tendencias agrupadas
        """
        # Diccionario para agrupar por período
        period_groups = {}
        
        for team in teams:
            # Convertir fecha de creación a Pendulum
            created_at = pendulum.instance(team.created_at)
            
            # Determinar clave del período
            if group_by == "day":
                period_key = created_at.format("YYYY-MM-DD")
                period_start = created_at.start_of('day')
                period_end = created_at.end_of('day')
            elif group_by == "week":
                period_key = f"{created_at.year}-W{created_at.week_of_year:02d}"
                period_start = created_at.start_of('week')
                period_end = created_at.end_of('week')
            elif group_by == "month":
                period_key = created_at.format("YYYY-MM")
                period_start = created_at.start_of('month')
                period_end = created_at.end_of('month')
            else:  # year
                period_key = str(created_at.year)
                period_start = created_at.start_of('year')
                period_end = created_at.end_of('year')
            
            # Agregar al grupo
            if period_key not in period_groups:
                period_groups[period_key] = {
                    "period": period_key,
                    "start_date": period_start.to_datetime_string(),
                    "end_date": period_end.to_datetime_string(),
                    "teams_created": 0,
                    "active_teams": 0,
                    "inactive_teams": 0
                }
            
            period_groups[period_key]["teams_created"] += 1
            if team.is_active:
                period_groups[period_key]["active_teams"] += 1
            else:
                period_groups[period_key]["inactive_teams"] += 1
        
        # Convertir a lista de TeamCreationTrend
        trends = []
        for period_data in sorted(period_groups.values(), key=lambda x: x["period"]):
            trend = TeamCreationTrend(
                period=period_data["period"],
                start_date=period_data["start_date"],
                end_date=period_data["end_date"],
                teams_created=period_data["teams_created"],
                active_teams=period_data["active_teams"],
                inactive_teams=period_data["inactive_teams"]
            )
            trends.append(trend)
        
        return trends