# src/planificador/repositories/team/modules/statistics_module.py

"""
Módulo de estadísticas para operaciones analíticas del repositorio Team.

Este módulo implementa las operaciones de análisis estadístico, métricas
y reportes de equipos con cálculos avanzados y agregaciones.

Principios de Diseño:
    - Single Responsibility: Solo operaciones estadísticas y analíticas
    - Performance: Consultas optimizadas con agregaciones en BD
    - Business Intelligence: Métricas relevantes para toma de decisiones

Uso:
    ```python
    stats_module = TeamStatisticsModule(session)
    total_teams = await stats_module.count_total_teams()
    distribution = await stats_module.get_team_size_distribution()
    trends = await stats_module.get_membership_trends()
    ```
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime
from sqlalchemy import select, func, and_, or_, case, distinct
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.team import Team
from planificador.models.team_membership import TeamMembership
from planificador.repositories.team.interfaces.statistics_interface import ITeamStatisticsOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    TeamRepositoryError,
    convert_sqlalchemy_error
)
import pendulum


class TeamStatisticsModule(BaseRepository[Team], ITeamStatisticsOperations):
    """
    Módulo para operaciones estadísticas del repositorio Team.
    
    Implementa las operaciones de análisis estadístico, métricas
    y reportes de equipos con cálculos avanzados usando Pendulum
    para manejo de fechas y agregaciones optimizadas.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Team
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de estadísticas para equipos.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Team)
        self._logger = self._logger.bind(component="TeamStatisticsModule")
        self._logger.debug("TeamStatisticsModule inicializado")

    async def count_total_teams(self, active_only: bool = True) -> int:
        """
        Cuenta el total de equipos.
        
        Args:
            active_only: Si solo contar equipos activos
        
        Returns:
            int: Número total de equipos
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el conteo
        """
        try:
            self._logger.debug(f"Contando equipos, solo activos: {active_only}")
            
            stmt = select(func.count(Team.id))
            
            if active_only:
                stmt = stmt.where(Team.is_active == True)
            
            result = await self.session.execute(stmt)
            count = result.scalar() or 0
            
            self._logger.debug(f"Total de equipos encontrados: {count}")
            
            return count
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al contar equipos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_total_teams",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al contar equipos: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="count_total_teams",
                entity_type="Team",
                original_error=e
            )

    async def count_active_teams(self) -> int:
        """
        Cuenta equipos activos.
        
        Returns:
            int: Número de equipos activos
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el conteo
        """
        return await self.count_total_teams(active_only=True)

    async def count_inactive_teams(self) -> int:
        """
        Cuenta equipos inactivos.
        
        Returns:
            int: Número de equipos inactivos
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el conteo
        """
        try:
            self._logger.debug("Contando equipos inactivos")
            
            stmt = (
                select(func.count(Team.id))
                .where(Team.is_active == False)
            )
            
            result = await self.session.execute(stmt)
            count = result.scalar() or 0
            
            self._logger.debug(f"Total de equipos inactivos: {count}")
            
            return count
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al contar equipos inactivos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_inactive_teams",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al contar equipos inactivos: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="count_inactive_teams",
                entity_type="Team",
                original_error=e
            )

    async def get_team_size_distribution(self) -> Dict[str, int]:
        """
        Obtiene la distribución de tamaños de equipos.
        
        Returns:
            Dict[str, int]: Distribución por rangos de tamaño
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el análisis
        """
        try:
            self._logger.debug("Obteniendo distribución de tamaños de equipos")
            
            # Consulta para obtener el tamaño de cada equipo
            stmt = (
                select(
                    Team.id,
                    Team.name,
                    func.count(TeamMembership.id).label('member_count')
                )
                .outerjoin(
                    TeamMembership,
                    and_(
                        TeamMembership.team_id == Team.id,
                        TeamMembership.is_active == True
                    )
                )
                .where(Team.is_active == True)
                .group_by(Team.id, Team.name)
            )
            
            result = await self.session.execute(stmt)
            team_sizes = result.all()
            
            # Categorizar por rangos de tamaño
            distribution = {
                'sin_miembros': 0,
                'pequenos_1_5': 0,
                'medianos_6_15': 0,
                'grandes_16_30': 0,
                'muy_grandes_31_plus': 0
            }
            
            for team_id, team_name, member_count in team_sizes:
                if member_count == 0:
                    distribution['sin_miembros'] += 1
                elif 1 <= member_count <= 5:
                    distribution['pequenos_1_5'] += 1
                elif 6 <= member_count <= 15:
                    distribution['medianos_6_15'] += 1
                elif 16 <= member_count <= 30:
                    distribution['grandes_16_30'] += 1
                else:
                    distribution['muy_grandes_31_plus'] += 1
            
            self._logger.debug(
                f"Distribución de tamaños calculada: {distribution}"
            )
            
            return distribution
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener distribución de tamaños: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_size_distribution",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener distribución: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_team_size_distribution",
                entity_type="Team",
                original_error=e
            )

    async def get_teams_by_department_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene estadísticas de equipos por departamento.
        
        Returns:
            Dict[str, Dict[str, Any]]: Estadísticas por departamento
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el análisis
        """
        try:
            self._logger.debug("Obteniendo estadísticas por departamento")
            
            # Consulta para obtener estadísticas por departamento
            stmt = (
                select(
                    Team.department,
                    func.count(distinct(Team.id)).label('total_teams'),
                    func.count(
                        case(
                            (Team.is_active == True, Team.id),
                            else_=None
                        )
                    ).label('active_teams'),
                    func.count(
                        case(
                            (Team.is_active == False, Team.id),
                            else_=None
                        )
                    ).label('inactive_teams'),
                    func.count(distinct(TeamMembership.employee_id)).label('total_members')
                )
                .outerjoin(
                    TeamMembership,
                    and_(
                        TeamMembership.team_id == Team.id,
                        TeamMembership.is_active == True
                    )
                )
                .group_by(Team.department)
                .order_by(Team.department.asc())
            )
            
            result = await self.session.execute(stmt)
            dept_stats = result.all()
            
            # Formatear resultados
            department_statistics = {}
            
            for dept, total_teams, active_teams, inactive_teams, total_members in dept_stats:
                department_statistics[dept or 'Sin Departamento'] = {
                    'total_teams': total_teams,
                    'active_teams': active_teams,
                    'inactive_teams': inactive_teams,
                    'total_members': total_members or 0,
                    'avg_members_per_team': (
                        round((total_members or 0) / active_teams, 2) 
                        if active_teams > 0 else 0
                    )
                }
            
            self._logger.debug(
                f"Estadísticas por departamento calculadas para "
                f"{len(department_statistics)} departamentos"
            )
            
            return department_statistics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener estadísticas por departamento: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_teams_by_department_stats",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas por departamento: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_teams_by_department_stats",
                entity_type="Team",
                original_error=e
            )

    async def get_membership_trends(
        self, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene tendencias de membresías en un período.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
        
        Returns:
            Dict[str, Any]: Tendencias y métricas de membresías
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el análisis
        """
        try:
            # Usar fechas por defecto si no se proporcionan
            if end_date is None:
                end_date = pendulum.now().date()
            if start_date is None:
                start_date = pendulum.now().subtract(months=6).date()
            
            self._logger.debug(
                f"Obteniendo tendencias de membresías desde {start_date} hasta {end_date}"
            )
            
            # Membresías iniciadas en el período
            new_memberships_stmt = (
                select(func.count(TeamMembership.id))
                .where(
                    and_(
                        TeamMembership.start_date >= start_date,
                        TeamMembership.start_date <= end_date
                    )
                )
            )
            
            # Membresías terminadas en el período
            ended_memberships_stmt = (
                select(func.count(TeamMembership.id))
                .where(
                    and_(
                        TeamMembership.end_date >= start_date,
                        TeamMembership.end_date <= end_date,
                        TeamMembership.is_active == False
                    )
                )
            )
            
            # Membresías activas actuales
            active_memberships_stmt = (
                select(func.count(TeamMembership.id))
                .where(TeamMembership.is_active == True)
            )
            
            # Ejecutar consultas
            new_result = await self.session.execute(new_memberships_stmt)
            ended_result = await self.session.execute(ended_memberships_stmt)
            active_result = await self.session.execute(active_memberships_stmt)
            
            new_memberships = new_result.scalar() or 0
            ended_memberships = ended_result.scalar() or 0
            active_memberships = active_result.scalar() or 0
            
            # Calcular métricas
            net_change = new_memberships - ended_memberships
            turnover_rate = (
                (ended_memberships / active_memberships * 100) 
                if active_memberships > 0 else 0
            )
            
            trends = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days
                },
                'memberships': {
                    'new_memberships': new_memberships,
                    'ended_memberships': ended_memberships,
                    'active_memberships': active_memberships,
                    'net_change': net_change
                },
                'metrics': {
                    'turnover_rate_percent': round(turnover_rate, 2),
                    'growth_rate_percent': (
                        round((net_change / active_memberships * 100), 2)
                        if active_memberships > 0 else 0
                    ),
                    'avg_new_per_month': (
                        round(new_memberships / ((end_date - start_date).days / 30), 2)
                        if (end_date - start_date).days > 0 else 0
                    )
                }
            }
            
            self._logger.debug(
                f"Tendencias calculadas: {new_memberships} nuevas, "
                f"{ended_memberships} terminadas, cambio neto: {net_change}"
            )
            
            return trends
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener tendencias de membresías: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_membership_trends",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener tendencias: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_membership_trends",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_leadership_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de liderazgo de equipos.
        
        Returns:
            Dict[str, Any]: Estadísticas de liderazgo
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el análisis
        """
        try:
            self._logger.debug("Obteniendo estadísticas de liderazgo")
            
            # Equipos con y sin líder
            teams_with_leader_stmt = (
                select(func.count(distinct(Team.id)))
                .join(
                    TeamMembership,
                    and_(
                        TeamMembership.team_id == Team.id,
                        TeamMembership.is_leader == True,
                        TeamMembership.is_active == True
                    )
                )
                .where(Team.is_active == True)
            )
            
            total_active_teams_stmt = (
                select(func.count(Team.id))
                .where(Team.is_active == True)
            )
            
            # Líderes únicos
            unique_leaders_stmt = (
                select(func.count(distinct(TeamMembership.employee_id)))
                .where(
                    and_(
                        TeamMembership.is_leader == True,
                        TeamMembership.is_active == True
                    )
                )
            )
            
            # Ejecutar consultas
            teams_with_leader_result = await self.session.execute(teams_with_leader_stmt)
            total_teams_result = await self.session.execute(total_active_teams_stmt)
            unique_leaders_result = await self.session.execute(unique_leaders_stmt)
            
            teams_with_leader = teams_with_leader_result.scalar() or 0
            total_active_teams = total_teams_result.scalar() or 0
            unique_leaders = unique_leaders_result.scalar() or 0
            
            teams_without_leader = total_active_teams - teams_with_leader
            
            # Calcular métricas
            leadership_coverage = (
                (teams_with_leader / total_active_teams * 100)
                if total_active_teams > 0 else 0
            )
            
            avg_teams_per_leader = (
                (teams_with_leader / unique_leaders)
                if unique_leaders > 0 else 0
            )
            
            leadership_stats = {
                'teams': {
                    'total_active_teams': total_active_teams,
                    'teams_with_leader': teams_with_leader,
                    'teams_without_leader': teams_without_leader
                },
                'leaders': {
                    'unique_leaders': unique_leaders,
                    'avg_teams_per_leader': round(avg_teams_per_leader, 2)
                },
                'metrics': {
                    'leadership_coverage_percent': round(leadership_coverage, 2),
                    'teams_needing_leader': teams_without_leader
                }
            }
            
            self._logger.debug(
                f"Estadísticas de liderazgo: {teams_with_leader}/{total_active_teams} "
                f"equipos con líder, {unique_leaders} líderes únicos"
            )
            
            return leadership_stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener estadísticas de liderazgo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_leadership_statistics",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de liderazgo: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_leadership_statistics",
                entity_type="TeamMembership",
                original_error=e
            )

    async def generate_teams_summary_report(self) -> Dict[str, Any]:
        """
        Genera un reporte resumen completo de equipos.
        
        Returns:
            Dict[str, Any]: Reporte completo con todas las métricas
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la generación
        """
        try:
            self._logger.debug("Generando reporte resumen de equipos")
            
            # Obtener todas las estadísticas
            total_teams = await self.count_total_teams(active_only=False)
            active_teams = await self.count_active_teams()
            inactive_teams = await self.count_inactive_teams()
            
            size_distribution = await self.get_team_size_distribution()
            department_stats = await self.get_teams_by_department_stats()
            membership_trends = await self.get_membership_trends()
            leadership_stats = await self.get_leadership_statistics()
            
            # Generar timestamp del reporte
            report_timestamp = pendulum.now()
            
            summary_report = {
                'report_info': {
                    'generated_at': report_timestamp.isoformat(),
                    'generated_by': 'TeamStatisticsModule',
                    'report_type': 'teams_summary'
                },
                'overview': {
                    'total_teams': total_teams,
                    'active_teams': active_teams,
                    'inactive_teams': inactive_teams,
                    'activity_rate_percent': (
                        round((active_teams / total_teams * 100), 2)
                        if total_teams > 0 else 0
                    )
                },
                'size_distribution': size_distribution,
                'department_statistics': department_stats,
                'membership_trends': membership_trends,
                'leadership_statistics': leadership_stats
            }
            
            self._logger.info(
                f"Reporte resumen generado exitosamente: {total_teams} equipos totales, "
                f"{active_teams} activos, {len(department_stats)} departamentos"
            )
            
            return summary_report
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al generar reporte resumen: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="generate_teams_summary_report",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al generar reporte: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="generate_teams_summary_report",
                entity_type="Team",
                original_error=e
            )

    async def get_team_performance_metrics(
        self, 
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento de un equipo específico.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
        
        Returns:
            Dict[str, Any]: Métricas de rendimiento del equipo
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el análisis
        """
        try:
            # Usar fechas por defecto si no se proporcionan
            if end_date is None:
                end_date = pendulum.now().date()
            if start_date is None:
                start_date = pendulum.now().subtract(months=3).date()
            
            self._logger.debug(
                f"Obteniendo métricas de rendimiento para equipo {team_id} "
                f"desde {start_date} hasta {end_date}"
            )
            
            # Verificar que el equipo existe
            team = await self.get_by_id(team_id)
            if not team:
                raise TeamRepositoryError(
                    message=f"Equipo {team_id} no encontrado",
                    operation="get_team_performance_metrics",
                    entity_type="Team",
                    entity_id=str(team_id)
                )
            
            # Miembros actuales
            current_members_stmt = (
                select(func.count(TeamMembership.id))
                .where(
                    and_(
                        TeamMembership.team_id == team_id,
                        TeamMembership.is_active == True
                    )
                )
            )
            
            # Cambios de membresía en el período
            new_members_stmt = (
                select(func.count(TeamMembership.id))
                .where(
                    and_(
                        TeamMembership.team_id == team_id,
                        TeamMembership.start_date >= start_date,
                        TeamMembership.start_date <= end_date
                    )
                )
            )
            
            departed_members_stmt = (
                select(func.count(TeamMembership.id))
                .where(
                    and_(
                        TeamMembership.team_id == team_id,
                        TeamMembership.end_date >= start_date,
                        TeamMembership.end_date <= end_date,
                        TeamMembership.is_active == False
                    )
                )
            )
            
            # Ejecutar consultas
            current_result = await self.session.execute(current_members_stmt)
            new_result = await self.session.execute(new_members_stmt)
            departed_result = await self.session.execute(departed_members_stmt)
            
            current_members = current_result.scalar() or 0
            new_members = new_result.scalar() or 0
            departed_members = departed_result.scalar() or 0
            
            # Calcular métricas
            net_change = new_members - departed_members
            turnover_rate = (
                (departed_members / current_members * 100)
                if current_members > 0 else 0
            )
            
            stability_score = max(0, 100 - turnover_rate)
            
            performance_metrics = {
                'team_info': {
                    'team_id': team_id,
                    'team_name': team.name,
                    'department': team.department,
                    'is_active': team.is_active
                },
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days
                },
                'membership': {
                    'current_members': current_members,
                    'new_members': new_members,
                    'departed_members': departed_members,
                    'net_change': net_change
                },
                'metrics': {
                    'turnover_rate_percent': round(turnover_rate, 2),
                    'stability_score': round(stability_score, 2),
                    'growth_rate_percent': (
                        round((net_change / current_members * 100), 2)
                        if current_members > 0 else 0
                    )
                }
            }
            
            self._logger.debug(
                f"Métricas calculadas para equipo {team_id}: "
                f"{current_members} miembros actuales, {turnover_rate:.2f}% rotación"
            )
            
            return performance_metrics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al obtener métricas de rendimiento: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_performance_metrics",
                entity_type="Team",
                entity_id=str(team_id)
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener métricas de rendimiento: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_team_performance_metrics",
                entity_type="Team",
                entity_id=str(team_id),
                original_error=e
            )