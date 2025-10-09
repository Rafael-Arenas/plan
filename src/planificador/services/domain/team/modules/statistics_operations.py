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
    TeamDomainError
)
from planificador.exceptions.base import (
    ValidationError
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
        team_id: int,
        active_only: bool = True
    ) -> int:
        """
        Obtiene el conteo de miembros de un equipo específico.
        
        Args:
            team_id: ID del equipo
            active_only: Si solo contar miembros activos
            
        Returns:
            int: Número de miembros del equipo
            
        Raises:
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(f"Obteniendo conteo de miembros para equipo {team_id}")
            
            # Obtener conteo de miembros del equipo
            count = await self._membership_repo.count_team_members(team_id, active_only)
            
            self._logger.debug(f"Equipo {team_id} tiene {count} miembros")
            return count
            
        except TeamMembershipRepositoryError as e:
            self._logger.error(f"Error de repositorio al contar miembros del equipo {team_id}: {e}")
            raise TeamDomainError(
                f"Error al obtener conteo de miembros: {e.message}",
                operation="get_team_member_count",
                entity_type="Team",
                entity_id=str(team_id),
                original_error=e
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al contar miembros del equipo {team_id}: {e}")
            raise TeamDomainError(
                f"Error inesperado al obtener conteo de miembros: {str(e)}",
                operation="get_team_member_count",
                entity_type="Team",
                entity_id=str(team_id),
                original_error=e
            )

    async def get_teams_count_by_status(
        self,
        include_details: bool = False
    ) -> Dict[str, int]:
        """
        Obtiene el conteo de equipos agrupados por estado.
        
        Args:
            include_details: Si incluir detalles adicionales
        
        Returns:
            Dict[str, int]: Diccionario {status: count}
            
        Raises:
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug("Obteniendo conteos de equipos por estado")
            
            # Obtener conteos por estado
            active_count = await self._team_repo.count_active_teams()
            inactive_count = await self._team_repo.count_inactive_teams()
            total_count = active_count + inactive_count
            
            status_counts = {
                "active": active_count,
                "inactive": inactive_count,
                "total": total_count
            }
            
            self._logger.debug(f"Conteos por estado: {status_counts}")
            
            return status_counts
            
        except TeamRepositoryError as e:
            self._logger.error(f"Error de repositorio en conteos por estado: {e}")
            raise TeamDomainError(
                f"Error al obtener conteos por estado: {e.message}",
                operation="get_teams_count_by_status",
                entity_type="Team",
                original_error=e
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en conteos por estado: {e}")
            raise TeamDomainError(
                f"Error inesperado al obtener conteos por estado: {str(e)}",
                operation="get_teams_count_by_status",
                entity_type="Team",
                original_error=e
            )

    async def get_average_team_size(
        self,
        active_teams_only: bool = True,
        exclude_empty: bool = True
    ) -> float:
        """
        Calcula el tamaño promedio de los equipos.
        
        Args:
            active_teams_only: Si solo incluir equipos activos
            exclude_empty: Si excluir equipos vacíos
            
        Returns:
            float: Tamaño promedio de equipos
            
        Raises:
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(
                f"Calculando tamaño promedio de equipos "
                f"({'activos' if active_teams_only else 'todos'})"
            )
            
            # Obtener todos los equipos según el filtro
            if active_teams_only:
                teams = await self._team_repo.get_active_teams()
            else:
                teams = await self._team_repo.get_all_teams()
            
            if not teams:
                self._logger.warning("No hay equipos para calcular promedio")
                return 0.0
            
            # Obtener conteos de miembros para cada equipo
            total_members = 0
            valid_teams = 0
            
            for team in teams:
                try:
                    count = await self._membership_repo.count_team_members(team.id)
                    if not exclude_empty or count > 0:
                        total_members += count
                        valid_teams += 1
                except TeamMembershipRepositoryError as e:
                    self._logger.warning(f"Error al contar miembros del equipo {team.id}: {e}")
                    # Continuar con el siguiente equipo
            
            # Calcular promedio
            average_size = total_members / valid_teams if valid_teams > 0 else 0.0
            
            self._logger.debug(
                f"Tamaño promedio calculado: {average_size:.2f} "
                f"({total_members} miembros en {valid_teams} equipos)"
            )
            
            return round(average_size, 2)
            
        except TeamRepositoryError as e:
            self._logger.error(f"Error de repositorio en cálculo de promedio: {e}")
            raise TeamDomainError(
                f"Error al calcular tamaño promedio: {e.message}",
                operation="get_average_team_size",
                entity_type="Team",
                original_error=e
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en cálculo de promedio: {e}")
            raise TeamDomainError(
                f"Error inesperado al calcular tamaño promedio: {str(e)}",
                operation="get_average_team_size",
                entity_type="Team",
                original_error=e
            )

    async def get_team_creation_trends(
        self,
        period: str = "month",
        months_back: int = 12
    ) -> List[TeamCreationTrend]:
        """
        Obtiene las tendencias de creación de equipos en un período.
        
        Args:
            period: Período de agrupación ("day", "week", "month", "year")
            months_back: Número de meses hacia atrás desde ahora
            
        Returns:
            List[TeamCreationTrend]: Lista de tendencias por período
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(
                f"Obteniendo tendencias de creación: {months_back} meses atrás, "
                f"agrupado por {period}"
            )
            
            # Validar parámetros
            if period not in ["day", "week", "month", "year"]:
                raise ValidationError(
                    "period debe ser 'day', 'week', 'month' o 'year'"
                )
            
            if months_back < 1:
                raise ValidationError("months_back debe ser mayor a 0")
            
            # Calcular fechas
            end_date = pendulum.now()
            start_date = end_date.subtract(months=months_back)
            
            # Obtener equipos en el rango de fechas
            teams = await self._team_repo.get_teams_by_date_range(
                start_date, end_date
            )
            
            # Agrupar por período
            trends = await self._group_teams_by_period(teams, period)
            
            self._logger.debug(
                f"Tendencias calculadas: {len(trends)} períodos"
            )
            
            return trends
            
        except TeamRepositoryError as e:
            self._logger.error(f"Error de repositorio en tendencias: {e}")
            raise TeamDomainError(
                f"Error al obtener tendencias de creación: {e.message}",
                operation="get_team_creation_trends",
                entity_type="Team",
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en tendencias: {e}")
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