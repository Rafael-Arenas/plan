# src/planificador/repositories/team_membership/modules/statistics_module.py

"""
Módulo para operaciones estadísticas del repositorio TeamMembership.
"""

from typing import Any, Dict, List, Optional
from datetime import date
from uuid import UUID
from sqlalchemy import func, select, and_, or_, case, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import pendulum

from planificador.repositories.base_repository import BaseRepository
from planificador.models.team_membership import MembershipRole, TeamMembership
from planificador.repositories.team_membership.interfaces.statistics_interface import ITeamMembershipStatisticsOperations, StatisticsPeriod
from planificador.schemas.team_membership import MembershipStatus
from planificador.exceptions.repository import TeamMembershipRepositoryError, convert_sqlalchemy_error


class TeamMembershipStatisticsModule(BaseRepository, ITeamMembershipStatisticsOperations):
    """
    Implementación de operaciones estadísticas para membresías de equipos.
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de estadísticas.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, TeamMembership)

    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[TeamMembership]:
        """
        Obtiene una membresía por un campo único específico.
        
        Args:
            field_name: Nombre del campo único
            value: Valor del campo único
            
        Returns:
            Optional[TeamMembership]: Membresía encontrada o None
            
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo membresía por campo único: {field_name}={value}")
            
            if not hasattr(self.model_class, field_name):
                raise TeamMembershipRepositoryError(
                    message=f"Campo '{field_name}' no existe en el modelo TeamMembership",
                    operation="get_by_unique_field",
                    entity_type="TeamMembership"
                )

            field_attr = getattr(self.model_class, field_name)
            query = select(self.model_class).where(field_attr == value)
            result = await self.session.execute(query)
            membership = result.scalar_one_or_none()
            
            if membership:
                self._logger.debug(f"Membresía encontrada: ID {membership.id}")
            else:
                self._logger.debug(f"No se encontró membresía con {field_name}={value}")
            
            return membership
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener por campo único: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener por campo único: {e}")
            await self.session.rollback()
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_by_unique_field",
                entity_type="TeamMembership",
                original_error=e
            )

    async def count_memberships_by_role(
        self,
        active_only: bool = True,
        as_of_date: Optional[date] = None
    ) -> Dict[MembershipRole, int]:
        """
        Cuenta membresías agrupadas por rol.
        
        Args:
            active_only: Si solo contar membresías activas
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            Dict[MembershipRole, int]: Conteo por rol
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el conteo
        """
        try:
            self._logger.debug(f"Contando membresías por rol (activas: {active_only})")
            
            reference_date = as_of_date or pendulum.today().date()
            
            query = select(
                self.model_class.role,
                func.count(self.model_class.id).label('count')
            ).group_by(self.model_class.role)
            
            if active_only:
                query = query.where(
                    and_(
                        self.model_class.start_date <= reference_date,
                        or_(
                            self.model_class.end_date.is_(None),
                            self.model_class.end_date >= reference_date
                        )
                    )
                )
            
            result = await self.session.execute(query)
            role_counts = dict(result.fetchall())
            
            # Asegurar que todos los roles estén representados
            complete_counts = {role: role_counts.get(role, 0) for role in MembershipRole}
            
            self._logger.debug(f"Conteo por roles: {complete_counts}")
            return complete_counts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al contar por rol: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_memberships_by_role",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al contar por rol: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="count_memberships_by_role",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_employee_participation_stats(
        self,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de participación de empleados.
        
        Args:
            employee_id: ID del empleado específico (opcional)
        
        Returns:
            Dict[str, Any]: Estadísticas de participación
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo estadísticas de participación para empleado: {employee_id}")
            
            query = select(
                self.model_class.employee_id,
                func.count(self.model_class.id).label('total_memberships'),
                func.count(
                    case(
                        (self.model_class.end_date.is_(None), 1),
                        else_=None
                    )
                ).label('active_memberships'),
                func.avg(
                    func.julianday(
                        func.coalesce(self.model_class.end_date, func.date('now'))
                    ) - func.julianday(self.model_class.start_date)
                ).label('avg_duration_days')
            ).group_by(self.model_class.employee_id)
            
            if employee_id:
                query = query.where(self.model_class.employee_id == employee_id)
            
            result = await self.session.execute(query)
            stats = result.fetchall()
            
            if employee_id and stats:
                # Estadísticas para un empleado específico
                stat = stats[0]
                return {
                    'employee_id': stat.employee_id,
                    'total_memberships': stat.total_memberships,
                    'active_memberships': stat.active_memberships,
                    'average_duration_days': round(stat.avg_duration_days or 0, 2)
                }
            else:
                # Estadísticas agregadas
                total_employees = len(stats)
                total_memberships = sum(s.total_memberships for s in stats)
                total_active = sum(s.active_memberships for s in stats)
                
                return {
                    'total_employees_with_memberships': total_employees,
                    'total_memberships': total_memberships,
                    'total_active_memberships': total_active,
                    'average_memberships_per_employee': round(total_memberships / total_employees if total_employees > 0 else 0, 2)
                }
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener estadísticas de participación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_participation_stats",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de participación: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_employee_participation_stats",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_membership_duration_statistics(
        self,
        completed_only: bool = True
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de duración de membresías.
        
        Args:
            completed_only: Si solo incluir membresías completadas
        
        Returns:
            Dict[str, Any]: Estadísticas de duración
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo estadísticas de duración (completadas: {completed_only})")
            
            # Calcular duración en días
            duration_expr = func.julianday(
                func.coalesce(self.model_class.end_date, func.date('now'))
            ) - func.julianday(self.model_class.start_date)
            
            query = select(
                func.count(self.model_class.id).label('total_memberships'),
                func.avg(duration_expr).label('avg_duration'),
                func.min(duration_expr).label('min_duration'),
                func.max(duration_expr).label('max_duration')
            )
            
            if completed_only:
                query = query.where(self.model_class.end_date.is_not(None))
            
            result = await self.session.execute(query)
            stats = result.fetchone()
            
            return {
                'total_memberships': stats.total_memberships or 0,
                'average_duration_days': round(stats.avg_duration or 0, 2),
                'minimum_duration_days': round(stats.min_duration or 0, 2),
                'maximum_duration_days': round(stats.max_duration or 0, 2),
                'completed_only': completed_only
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener estadísticas de duración: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_membership_duration_statistics",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de duración: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_membership_duration_statistics",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_membership_overlap_statistics(
        self,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de solapamiento de membresías.
        
        Args:
            employee_id: ID del empleado específico (opcional)
        
        Returns:
            Dict[str, Any]: Estadísticas de solapamiento
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo estadísticas de solapamiento para empleado: {employee_id}")
            
            # Esta es una implementación básica - se puede expandir según necesidades
            query = select(
                self.model_class.employee_id,
                func.count(self.model_class.id).label('total_memberships')
            ).group_by(self.model_class.employee_id)
            
            if employee_id:
                query = query.where(self.model_class.employee_id == employee_id)
            
            result = await self.session.execute(query)
            stats = result.fetchall()
            
            # Contar empleados con múltiples membresías
            employees_with_multiple = sum(1 for s in stats if s.total_memberships > 1)
            
            return {
                'employees_analyzed': len(stats),
                'employees_with_multiple_memberships': employees_with_multiple,
                'percentage_with_overlaps': round(
                    (employees_with_multiple / len(stats) * 100) if stats else 0, 2
                )
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener estadísticas de solapamiento: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_membership_overlap_statistics",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de solapamiento: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_membership_overlap_statistics",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_membership_trends(
        self,
        period: StatisticsPeriod,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Obtiene tendencias de membresías por período.
        
        Args:
            period: Período de agrupación
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Returns:
            List[Dict[str, Any]]: Tendencias por período
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo tendencias de membresías ({period.value})")
            
            # Formato de fecha según el período
            date_format = {
                StatisticsPeriod.DAILY: '%Y-%m-%d',
                StatisticsPeriod.WEEKLY: '%Y-W%W',
                StatisticsPeriod.MONTHLY: '%Y-%m',
                StatisticsPeriod.QUARTERLY: '%Y-Q%q',
                StatisticsPeriod.YEARLY: '%Y'
            }.get(period, '%Y-%m-%d')
            
            query = select(
                func.strftime(date_format, self.model_class.start_date).label('period'),
                func.count(self.model_class.id).label('new_memberships')
            ).where(
                and_(
                    self.model_class.start_date >= start_date,
                    self.model_class.start_date <= end_date
                )
            ).group_by(
                func.strftime(date_format, self.model_class.start_date)
            ).order_by('period')
            
            result = await self.session.execute(query)
            trends = [
                {
                    'period': row.period,
                    'new_memberships': row.new_memberships
                }
                for row in result.fetchall()
            ]
            
            self._logger.debug(f"Encontradas {len(trends)} tendencias")
            return trends
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener tendencias: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_membership_trends",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener tendencias: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_membership_trends",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_retention_rate(
        self,
        team_id: Optional[int] = None,
        months_threshold: int = 12
    ) -> Dict[str, Any]:
        """
        Obtiene la tasa de retención.
        
        Args:
            team_id: ID del equipo específico (opcional)
            months_threshold: Umbral en meses para considerar retención
        
        Returns:
            Dict[str, Any]: Métricas de retención
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Calculando tasa de retención (equipo: {team_id}, umbral: {months_threshold} meses)")
            
            threshold_date = pendulum.today().subtract(months=months_threshold).date()
            
            # Membresías que comenzaron antes del umbral
            query_total = select(func.count(self.model_class.id)).where(
                self.model_class.start_date <= threshold_date
            )
            
            # Membresías que siguen activas o terminaron después del umbral
            query_retained = select(func.count(self.model_class.id)).where(
                and_(
                    self.model_class.start_date <= threshold_date,
                    or_(
                        self.model_class.end_date.is_(None),
                        self.model_class.end_date >= threshold_date
                    )
                )
            )
            
            if team_id:
                query_total = query_total.where(self.model_class.team_id == team_id)
                query_retained = query_retained.where(self.model_class.team_id == team_id)
            
            total_result = await self.session.execute(query_total)
            retained_result = await self.session.execute(query_retained)
            
            total_memberships = total_result.scalar() or 0
            retained_memberships = retained_result.scalar() or 0
            
            retention_rate = (retained_memberships / total_memberships * 100) if total_memberships > 0 else 0
            
            return {
                'team_id': team_id,
                'months_threshold': months_threshold,
                'total_memberships': total_memberships,
                'retained_memberships': retained_memberships,
                'retention_rate_percentage': round(retention_rate, 2)
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al calcular tasa de retención: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_retention_rate",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al calcular tasa de retención: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_retention_rate",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_role_transition_matrix(
        self,
        team_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene la matriz de transición de roles.
        
        Args:
            team_id: ID del equipo específico (opcional)
        
        Returns:
            Dict[str, Any]: Matriz de transición de roles
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo matriz de transición de roles (equipo: {team_id})")
            
            # Implementación básica - se puede expandir para análisis más complejos
            query = select(
                self.model_class.role,
                func.count(self.model_class.id).label('count')
            ).group_by(self.model_class.role)
            
            if team_id:
                query = query.where(self.model_class.team_id == team_id)
            
            result = await self.session.execute(query)
            role_distribution = dict(result.fetchall())
            
            return {
                'team_id': team_id,
                'role_distribution': {role.value: count for role, count in role_distribution.items()},
                'total_memberships': sum(role_distribution.values())
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener matriz de transición: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_role_transition_matrix",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener matriz de transición: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_role_transition_matrix",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_team_size_distribution(
        self,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene la distribución de tamaños de equipos.
        
        Args:
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            Dict[str, Any]: Distribución de tamaños
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo distribución de tamaños de equipos")
            
            reference_date = as_of_date or pendulum.today().date()
            
            # Contar miembros activos por equipo
            query = select(
                self.model_class.team_id,
                func.count(self.model_class.id).label('team_size')
            ).where(
                and_(
                    self.model_class.start_date <= reference_date,
                    or_(
                        self.model_class.end_date.is_(None),
                        self.model_class.end_date >= reference_date
                    )
                )
            ).group_by(self.model_class.team_id)
            
            result = await self.session.execute(query)
            team_sizes = [row.team_size for row in result.fetchall()]
            
            if not team_sizes:
                return {
                    'total_teams': 0,
                    'average_size': 0,
                    'min_size': 0,
                    'max_size': 0,
                    'size_distribution': {}
                }
            
            # Calcular distribución
            from collections import Counter
            size_distribution = Counter(team_sizes)
            
            return {
                'total_teams': len(team_sizes),
                'average_size': round(sum(team_sizes) / len(team_sizes), 2),
                'min_size': min(team_sizes),
                'max_size': max(team_sizes),
                'size_distribution': dict(size_distribution)
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener distribución de tamaños: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_size_distribution",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener distribución de tamaños: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_team_size_distribution",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_team_stability_metrics(
        self,
        team_id: int,
        analysis_period_months: int = 12
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de estabilidad del equipo.
        
        Args:
            team_id: ID del equipo
            analysis_period_months: Período de análisis en meses
        
        Returns:
            Dict[str, Any]: Métricas de estabilidad
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo métricas de estabilidad para equipo {team_id}")
            
            start_date = pendulum.today().subtract(months=analysis_period_months).date()
            end_date = pendulum.today().date()
            
            # Membresías en el período
            query = select(
                func.count(self.model_class.id).label('total_memberships'),
                func.count(
                    case(
                        (self.model_class.end_date.is_(None), 1),
                        else_=None
                    )
                ).label('active_memberships'),
                func.count(
                    case(
                        (and_(
                            self.model_class.end_date.is_not(None),
                            self.model_class.end_date >= start_date
                        ), 1),
                        else_=None
                    )
                ).label('departures')
            ).where(
                and_(
                    self.model_class.team_id == team_id,
                    self.model_class.start_date <= end_date
                )
            )
            
            result = await self.session.execute(query)
            stats = result.fetchone()
            
            total_memberships = stats.total_memberships or 0
            active_memberships = stats.active_memberships or 0
            departures = stats.departures or 0
            
            stability_rate = ((total_memberships - departures) / total_memberships * 100) if total_memberships > 0 else 0
            
            return {
                'team_id': team_id,
                'analysis_period_months': analysis_period_months,
                'total_memberships': total_memberships,
                'active_memberships': active_memberships,
                'departures': departures,
                'stability_rate_percentage': round(stability_rate, 2)
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener métricas de estabilidad: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_stability_metrics",
                entity_type="TeamMembership",
                entity_id=str(team_id)
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener métricas de estabilidad: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_team_stability_metrics",
                entity_type="TeamMembership",
                entity_id=str(team_id),
                original_error=e
            )

    async def get_turnover_rate(
        self,
        team_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene la tasa de rotación.
        
        Args:
            team_id: ID del equipo específico (opcional)
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
        
        Returns:
            Dict[str, Any]: Métricas de rotación
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Calculando tasa de rotación (equipo: {team_id})")
            
            # Usar período de 12 meses por defecto
            if not start_date:
                start_date = pendulum.today().subtract(months=12).date()
            if not end_date:
                end_date = pendulum.today().date()
            
            # Membresías que terminaron en el período
            query_departures = select(func.count(self.model_class.id)).where(
                and_(
                    self.model_class.end_date.is_not(None),
                    self.model_class.end_date >= start_date,
                    self.model_class.end_date <= end_date
                )
            )
            
            # Promedio de membresías activas en el período
            query_average = select(func.count(self.model_class.id)).where(
                and_(
                    self.model_class.start_date <= end_date,
                    or_(
                        self.model_class.end_date.is_(None),
                        self.model_class.end_date >= start_date
                    )
                )
            )
            
            if team_id:
                query_departures = query_departures.where(self.model_class.team_id == team_id)
                query_average = query_average.where(self.model_class.team_id == team_id)
            
            departures_result = await self.session.execute(query_departures)
            average_result = await self.session.execute(query_average)
            
            departures = departures_result.scalar() or 0
            average_memberships = average_result.scalar() or 0
            
            turnover_rate = (departures / average_memberships * 100) if average_memberships > 0 else 0
            
            return {
                'team_id': team_id,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'departures': departures,
                'average_memberships': average_memberships,
                'turnover_rate_percentage': round(turnover_rate, 2)
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al calcular tasa de rotación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_turnover_rate",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al calcular tasa de rotación: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_turnover_rate",
                entity_type="TeamMembership",
                original_error=e
            )

    async def count_total_memberships(
        self,
        active_only: bool = False,
        as_of_date: Optional[date] = None
    ) -> int:
        """
        Cuenta el total de membresías en el sistema.
        
        Args:
            active_only: Si solo contar membresías activas
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            int: Número total de membresías
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el conteo
        """
        try:
            self._logger.debug(
                f"Contando membresías totales - activas_solo: {active_only}, "
                f"fecha_referencia: {as_of_date}"
            )
            
            # Construir consulta base
            stmt = select(func.count(TeamMembership.id))
            
            # Aplicar filtros
            if active_only:
                stmt = stmt.where(TeamMembership.status == MembershipStatus.ACTIVE)
            
            if as_of_date:
                # Membresías que estaban activas en la fecha especificada
                stmt = stmt.where(
                    and_(
                        TeamMembership.start_date <= as_of_date,
                        or_(
                            TeamMembership.end_date.is_(None),
                            TeamMembership.end_date >= as_of_date
                        )
                    )
                )
            
            result = await self.session.execute(stmt)
            count = result.scalar() or 0
            
            self._logger.debug(f"Total de membresías encontradas: {count}")
            return count
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al contar membresías totales: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_total_memberships",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al contar membresías totales: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="count_total_memberships",
                entity_type="TeamMembership",
                original_error=e
            )

    async def count_memberships_by_status(
        self,
        as_of_date: Optional[date] = None
    ) -> Dict[MembershipStatus, int]:
        """
        Cuenta membresías agrupadas por estado.
        
        Args:
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            Dict[MembershipStatus, int]: Conteo por estado
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el conteo
        """
        try:
            self._logger.debug(f"Contando membresías por estado - fecha_referencia: {as_of_date}")
            
            # Construir consulta base
            stmt = select(
                TeamMembership.status,
                func.count(TeamMembership.id).label('count')
            ).group_by(TeamMembership.status)
            
            # Aplicar filtro de fecha si se especifica
            if as_of_date:
                stmt = stmt.where(
                    and_(
                        TeamMembership.start_date <= as_of_date,
                        or_(
                            TeamMembership.end_date.is_(None),
                            TeamMembership.end_date >= as_of_date
                        )
                    )
                )
            
            result = await self.session.execute(stmt)
            rows = result.all()
            
            # Construir diccionario de resultados
            status_counts = {}
            for row in rows:
                status_counts[row.status] = row.count
            
            # Asegurar que todos los estados estén representados
            for status in MembershipStatus:
                if status not in status_counts:
                    status_counts[status] = 0
            
            self._logger.debug(f"Conteo por estado: {status_counts}")
            return status_counts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al contar membresías por estado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_memberships_by_status",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al contar membresías por estado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="count_memberships_by_status",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_cross_team_participation(
        self,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analiza la participación cruzada entre equipos.
        
        Args:
            employee_id: ID del empleado específico (opcional)
        
        Returns:
            Dict[str, Any]: Análisis de participación cruzada
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el análisis
        """
        try:
            self._logger.debug(f"Analizando participación cruzada - empleado_id: {employee_id}")
            
            # Consulta base para participación cruzada
            stmt = select(
                TeamMembership.employee_id,
                func.count(func.distinct(TeamMembership.team_id)).label('teams_count'),
                func.count(TeamMembership.id).label('total_memberships'),
                func.avg(
                    case(
                        (TeamMembership.end_date.is_(None), 
                         func.julianday('now') - func.julianday(TeamMembership.start_date)),
                        else_=func.julianday(TeamMembership.end_date) - func.julianday(TeamMembership.start_date)
                    )
                ).label('avg_duration_days')
            ).group_by(TeamMembership.employee_id)
            
            # Filtrar por empleado específico si se proporciona
            if employee_id:
                stmt = stmt.where(TeamMembership.employee_id == employee_id)
            
            result = await self.session.execute(stmt)
            rows = result.all()
            
            # Procesar resultados
            participation_data = []
            multi_team_employees = 0
            total_employees = len(rows)
            
            for row in rows:
                teams_count = row.teams_count
                if teams_count > 1:
                    multi_team_employees += 1
                
                participation_data.append({
                    "employee_id": row.employee_id,
                    "teams_count": teams_count,
                    "total_memberships": row.total_memberships,
                    "avg_duration_days": round(row.avg_duration_days or 0, 2),
                    "is_multi_team": teams_count > 1
                })
            
            # Calcular estadísticas generales
            cross_participation_rate = (
                (multi_team_employees / total_employees * 100) 
                if total_employees > 0 else 0
            )
            
            analysis = {
                "total_employees_analyzed": total_employees,
                "multi_team_employees": multi_team_employees,
                "cross_participation_rate_percent": round(cross_participation_rate, 2),
                "participation_details": participation_data if employee_id else participation_data[:10],  # Limitar resultados
                "summary": {
                    "highest_team_count": max([p["teams_count"] for p in participation_data], default=0),
                    "avg_teams_per_employee": round(
                        sum([p["teams_count"] for p in participation_data]) / total_employees, 2
                    ) if total_employees > 0 else 0
                }
            }
            
            self._logger.debug(
                f"Análisis de participación cruzada completado: "
                f"{multi_team_employees}/{total_employees} empleados multi-equipo"
            )
            
            return analysis
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al analizar participación cruzada: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_cross_team_participation",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al analizar participación cruzada: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_cross_team_participation",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_leadership_statistics(
        self,
        team_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de liderazgo.
        
        Args:
            team_id: ID del equipo específico (opcional)
        
        Returns:
            Dict[str, Any]: Estadísticas de liderazgo
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        try:
            self._logger.debug(f"Obteniendo estadísticas de liderazgo - equipo_id: {team_id}")
            
            # Definir roles de liderazgo
            leadership_roles = [MembershipRole.TEAM_LEAD, MembershipRole.TECH_LEAD]
            
            # Consulta base para estadísticas de liderazgo
            stmt = select(
                TeamMembership.role,
                TeamMembership.team_id,
                func.count(TeamMembership.id).label('count'),
                func.avg(
                    case(
                        (TeamMembership.end_date.is_(None), 
                         func.julianday('now') - func.julianday(TeamMembership.start_date)),
                        else_=func.julianday(TeamMembership.end_date) - func.julianday(TeamMembership.start_date)
                    )
                ).label('avg_tenure_days')
            ).where(
                TeamMembership.role.in_(leadership_roles)
            ).group_by(TeamMembership.role, TeamMembership.team_id)
            
            # Filtrar por equipo específico si se proporciona
            if team_id:
                stmt = stmt.where(TeamMembership.team_id == team_id)
            
            result = await self.session.execute(stmt)
            rows = result.all()
            
            # Procesar resultados
            leadership_by_role = {}
            leadership_by_team = {}
            total_leaders = 0
            
            for row in rows:
                role = row.role
                team_id_key = row.team_id
                count = row.count
                avg_tenure = row.avg_tenure_days or 0
                
                total_leaders += count
                
                # Agrupar por rol
                if role not in leadership_by_role:
                    leadership_by_role[role] = {
                        "total_count": 0,
                        "teams_with_role": 0,
                        "avg_tenure_days": 0
                    }
                
                leadership_by_role[role]["total_count"] += count
                leadership_by_role[role]["teams_with_role"] += 1
                leadership_by_role[role]["avg_tenure_days"] = avg_tenure
                
                # Agrupar por equipo
                if team_id_key not in leadership_by_team:
                    leadership_by_team[team_id_key] = {
                        "leadership_roles": {},
                        "total_leaders": 0
                    }
                
                leadership_by_team[team_id_key]["leadership_roles"][role] = count
                leadership_by_team[team_id_key]["total_leaders"] += count
            
            # Calcular estadísticas adicionales
            teams_with_leaders = len(leadership_by_team)
            
            # Consulta para obtener total de equipos (para calcular cobertura)
            total_teams_stmt = select(func.count(func.distinct(TeamMembership.team_id)))
            if team_id:
                total_teams_stmt = total_teams_stmt.where(TeamMembership.team_id == team_id)
            
            total_teams_result = await self.session.execute(total_teams_stmt)
            total_teams = total_teams_result.scalar() or 0
            
            leadership_coverage = (
                (teams_with_leaders / total_teams * 100) 
                if total_teams > 0 else 0
            )
            
            statistics = {
                "total_leaders": total_leaders,
                "teams_with_leaders": teams_with_leaders,
                "total_teams": total_teams,
                "leadership_coverage_percent": round(leadership_coverage, 2),
                "leadership_by_role": {
                    role.value: {
                        "count": data["total_count"],
                        "teams_count": data["teams_with_role"],
                        "avg_tenure_days": round(data["avg_tenure_days"], 2)
                    }
                    for role, data in leadership_by_role.items()
                },
                "leadership_by_team": {
                    str(team_id): {
                        "total_leaders": data["total_leaders"],
                        "roles": {role.value: count for role, count in data["leadership_roles"].items()}
                    }
                    for team_id, data in leadership_by_team.items()
                } if not team_id else leadership_by_team
            }
            
            self._logger.debug(
                f"Estadísticas de liderazgo calculadas: {total_leaders} líderes en {teams_with_leaders} equipos"
            )
            
            return statistics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al obtener estadísticas de liderazgo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_leadership_statistics",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de liderazgo: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_leadership_statistics",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_membership_summary_report(
        self,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte resumen de membresías.
        
        Args:
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            Dict[str, Any]: Reporte resumen completo
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la generación
        """
        try:
            self._logger.debug(f"Generando reporte resumen de membresías - fecha_referencia: {as_of_date}")
            
            # Obtener datos básicos
            total_memberships = await self.count_total_memberships(as_of_date=as_of_date)
            active_memberships = await self.count_total_memberships(active_only=True, as_of_date=as_of_date)
            memberships_by_status = await self.count_memberships_by_status(as_of_date=as_of_date)
            memberships_by_role = await self.count_memberships_by_role(as_of_date=as_of_date)
            
            # Obtener estadísticas adicionales
            team_size_distribution = await self.get_team_size_distribution(as_of_date=as_of_date)
            leadership_stats = await self.get_leadership_statistics()
            cross_team_participation = await self.get_cross_team_participation()
            
            # Calcular métricas derivadas
            active_rate = (
                (active_memberships / total_memberships * 100) 
                if total_memberships > 0 else 0
            )
            
            # Construir reporte
            report = {
                "report_metadata": {
                    "generated_at": pendulum.now().isoformat(),
                    "as_of_date": as_of_date.isoformat() if as_of_date else None,
                    "report_type": "membership_summary"
                },
                "overview": {
                    "total_memberships": total_memberships,
                    "active_memberships": active_memberships,
                    "active_rate_percent": round(active_rate, 2)
                },
                "distribution": {
                    "by_status": {status.value: count for status, count in memberships_by_status.items()},
                    "by_role": {role.value: count for role, count in memberships_by_role.items()},
                    "team_sizes": team_size_distribution
                },
                "leadership": leadership_stats,
                "cross_team_participation": {
                    "total_employees": cross_team_participation["total_employees_analyzed"],
                    "multi_team_employees": cross_team_participation["multi_team_employees"],
                    "cross_participation_rate": cross_team_participation["cross_participation_rate_percent"]
                },
                "key_insights": []
            }
            
            # Generar insights automáticos
            insights = []
            
            if active_rate < 80:
                insights.append(f"Tasa de membresías activas baja: {active_rate:.1f}%")
            
            if leadership_stats["leadership_coverage_percent"] < 90:
                insights.append(
                    f"Cobertura de liderazgo baja: {leadership_stats['leadership_coverage_percent']:.1f}%"
                )
            
            if cross_team_participation["cross_participation_rate_percent"] > 30:
                insights.append(
                    f"Alta participación cruzada: {cross_team_participation['cross_participation_rate_percent']:.1f}%"
                )
            
            report["key_insights"] = insights
            
            self._logger.debug("Reporte resumen de membresías generado exitosamente")
            return report
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al generar reporte resumen: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_membership_summary_report",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al generar reporte resumen: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_membership_summary_report",
                entity_type="TeamMembership",
                original_error=e
            )

    async def get_team_composition_analysis(
        self,
        team_id: int,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Analiza la composición de un equipo específico.
        
        Args:
            team_id: ID del equipo
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            Dict[str, Any]: Análisis de composición del equipo
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el análisis
        """
        try:
            self._logger.debug(f"Analizando composición del equipo {team_id} - fecha_referencia: {as_of_date}")
            
            # Construir consulta base
            stmt = select(TeamMembership).where(TeamMembership.team_id == team_id)
            
            # Aplicar filtro de fecha si se especifica
            if as_of_date:
                stmt = stmt.where(
                    and_(
                        TeamMembership.start_date <= as_of_date,
                        or_(
                            TeamMembership.end_date.is_(None),
                            TeamMembership.end_date >= as_of_date
                        )
                    )
                )
            
            result = await self.session.execute(stmt)
            memberships = result.scalars().all()
            
            if not memberships:
                return {
                    "team_id": team_id,
                    "analysis_date": as_of_date.isoformat() if as_of_date else None,
                    "total_members": 0,
                    "composition": {},
                    "leadership": {},
                    "tenure_analysis": {},
                    "status_distribution": {}
                }
            
            # Análisis por rol
            role_composition = {}
            leadership_count = 0
            total_members = len(memberships)
            
            # Análisis de tenure
            tenure_days = []
            current_date = as_of_date or pendulum.now().date()
            
            # Análisis por estado
            status_distribution = {}
            
            for membership in memberships:
                # Composición por rol
                role = membership.role
                if role not in role_composition:
                    role_composition[role] = 0
                role_composition[role] += 1
                
                # Contar liderazgo
                if role in [MembershipRole.TEAM_LEAD, MembershipRole.TECH_LEAD]:
                    leadership_count += 1
                
                # Calcular tenure
                start_date = membership.start_date
                end_date = membership.end_date or current_date
                tenure = (end_date - start_date).days
                tenure_days.append(tenure)
                
                # Distribución por estado
                status = membership.status
                if status not in status_distribution:
                    status_distribution[status] = 0
                status_distribution[status] += 1
            
            # Calcular estadísticas de tenure
            avg_tenure = sum(tenure_days) / len(tenure_days) if tenure_days else 0
            min_tenure = min(tenure_days) if tenure_days else 0
            max_tenure = max(tenure_days) if tenure_days else 0
            
            # Construir análisis
            analysis = {
                "team_id": team_id,
                "analysis_date": as_of_date.isoformat() if as_of_date else None,
                "total_members": total_members,
                "composition": {
                    "by_role": {
                        role.value: {
                            "count": count,
                            "percentage": round((count / total_members * 100), 2)
                        }
                        for role, count in role_composition.items()
                    },
                    "role_diversity": len(role_composition),
                    "most_common_role": max(role_composition.items(), key=lambda x: x[1])[0].value if role_composition else None
                },
                "leadership": {
                    "total_leaders": leadership_count,
                    "leadership_ratio": round((leadership_count / total_members), 2) if total_members > 0 else 0,
                    "has_adequate_leadership": leadership_count >= 1
                },
                "tenure_analysis": {
                    "avg_tenure_days": round(avg_tenure, 2),
                    "min_tenure_days": min_tenure,
                    "max_tenure_days": max_tenure,
                    "tenure_range_days": max_tenure - min_tenure
                },
                "status_distribution": {
                    status.value: {
                        "count": count,
                        "percentage": round((count / total_members * 100), 2)
                    }
                    for status, count in status_distribution.items()
                },
                "team_health_indicators": {
                    "has_leadership": leadership_count > 0,
                    "role_balance": len(role_composition) >= 2,
                    "stable_membership": avg_tenure >= 90,  # 3 meses
                    "active_majority": status_distribution.get(MembershipStatus.ACTIVE, 0) / total_members > 0.8
                }
            }
            
            self._logger.debug(
                f"Análisis de composición completado para equipo {team_id}: "
                f"{total_members} miembros, {leadership_count} líderes"
            )
            
            return analysis
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD al analizar composición del equipo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_composition_analysis",
                entity_type="TeamMembership",
                entity_id=team_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al analizar composición del equipo: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_team_composition_analysis",
                entity_type="TeamMembership",
                entity_id=team_id,
                original_error=e
            )