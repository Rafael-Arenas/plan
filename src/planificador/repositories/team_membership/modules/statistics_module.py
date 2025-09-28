# src/planificador/repositories/team_membership/statistics_module.py

"""
Módulo de estadísticas para el repositorio TeamMembership.

Este módulo implementa las operaciones de análisis estadístico
para membresías de equipos, siguiendo los patrones establecidos del proyecto.

Principios de Diseño:
    - Single Responsibility: Solo operaciones estadísticas
    - Dependency Injection: Recibe dependencias por constructor
    - Error Handling: Manejo robusto de excepciones con logging estructurado
    - Async/Await: Operaciones asíncronas para mejor performance

Uso:
    ```python
    stats_module = TeamMembershipStatisticsModule(session, logger)
    stats = await stats_module.get_membership_count_by_status()
    ```
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal

from loguru import logger
from sqlalchemy import select, func, and_, or_, case, distinct, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.repositories.base_repository import BaseRepository
from planificador.repositories.team_membership.interfaces.statistics_interface import ITeamMembershipStatisticsOperations
from planificador.exceptions.repository import TeamMembershipRepositoryError, convert_sqlalchemy_error


class TeamMembershipStatisticsModule(BaseRepository[TeamMembership], ITeamMembershipStatisticsOperations):
    """
    Módulo para operaciones estadísticas de membresías de equipos.
    
    Hereda de BaseRepository para operaciones estándar y implementa
    la interfaz ITeamMembershipStatisticsOperations para análisis estadístico.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        _logger: Logger para registro de eventos
        model_class: Clase del modelo TeamMembership
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de estadísticas de TeamMembership.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, TeamMembership)
        self._logger = logger.bind(module="TeamMembershipStatisticsModule")
    
    async def get_membership_count_by_status(self) -> Dict[str, int]:
        """
        Obtiene el conteo de membresías por estado (activo/inactivo).
        
        Returns:
            Dict[str, int]: Diccionario con conteos por estado
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug("Obteniendo conteo de membresías por estado")
            
            query = select(
                TeamMembership.is_active,
                func.count(TeamMembership.id).label('count')
            ).group_by(TeamMembership.is_active)
            
            result = await self.session.execute(query)
            rows = result.all()
            
            stats = {
                'active': 0,
                'inactive': 0,
                'total': 0
            }
            
            for row in rows:
                if row.is_active:
                    stats['active'] = row.count
                else:
                    stats['inactive'] = row.count
                stats['total'] += row.count
            
            self._logger.debug(f"Estadísticas por estado: {stats}")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener conteo por estado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_membership_count_by_status",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener conteo por estado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener estadísticas: {e}",
                operation="get_membership_count_by_status",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_membership_count_by_role(self) -> Dict[str, int]:
        """
        Obtiene el conteo de membresías por rol.
        
        Returns:
            Dict[str, int]: Diccionario con conteos por rol
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug("Obteniendo conteo de membresías por rol")
            
            query = select(
                TeamMembership.role,
                func.count(TeamMembership.id).label('count')
            ).group_by(TeamMembership.role)
            
            result = await self.session.execute(query)
            rows = result.all()
            
            stats = {}
            total = 0
            
            for row in rows:
                role_name = row.role.value if row.role else 'unknown'
                stats[role_name] = row.count
                total += row.count
            
            stats['total'] = total
            
            self._logger.debug(f"Estadísticas por rol: {stats}")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener conteo por rol: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_membership_count_by_role",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener conteo por rol: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener estadísticas: {e}",
                operation="get_membership_count_by_role",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_membership_duration_analysis(self) -> Dict[str, Any]:
        """
        Analiza la duración de las membresías.
        
        Returns:
            Dict[str, Any]: Estadísticas de duración (promedio, mediana, etc.)
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el análisis
        """
        try:
            self._logger.debug("Analizando duración de membresías")
            
            # Obtener membresías con fechas de fin para calcular duración
            query = select(TeamMembership).where(
                TeamMembership.end_date.is_not(None)
            )
            
            result = await self.session.execute(query)
            memberships = result.scalars().all()
            
            if not memberships:
                return {
                    'count': 0,
                    'average_days': 0,
                    'min_days': 0,
                    'max_days': 0,
                    'total_days': 0
                }
            
            durations = []
            for membership in memberships:
                if membership.end_date and membership.start_date:
                    duration = (membership.end_date - membership.start_date).days
                    durations.append(duration)
            
            if not durations:
                return {
                    'count': 0,
                    'average_days': 0,
                    'min_days': 0,
                    'max_days': 0,
                    'total_days': 0
                }
            
            stats = {
                'count': len(durations),
                'average_days': sum(durations) / len(durations),
                'min_days': min(durations),
                'max_days': max(durations),
                'total_days': sum(durations)
            }
            
            self._logger.debug(f"Análisis de duración: {stats}")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al analizar duración: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_membership_duration_analysis",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al analizar duración: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al analizar duración: {e}",
                operation="get_membership_duration_analysis",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_team_size_distribution(self) -> Dict[int, Dict[str, Any]]:
        """
        Obtiene la distribución de tamaños de equipos.
        
        Returns:
            Dict[int, Dict[str, Any]]: Distribución por equipo con estadísticas
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug("Obteniendo distribución de tamaños de equipos")
            
            # Contar membresías activas por equipo
            query = select(
                TeamMembership.team_id,
                func.count(TeamMembership.id).label('active_members'),
                func.count(case((TeamMembership.role == MembershipRole.LEAD, 1))).label('leads'),
                func.count(case((TeamMembership.role == MembershipRole.SUPERVISOR, 1))).label('supervisors'),
                func.count(case((TeamMembership.role == MembershipRole.COORDINATOR, 1))).label('coordinators'),
                func.count(case((TeamMembership.role == MembershipRole.MEMBER, 1))).label('members')
            ).where(
                TeamMembership.is_active == True
            ).group_by(TeamMembership.team_id)
            
            result = await self.session.execute(query)
            rows = result.all()
            
            distribution = {}
            for row in rows:
                distribution[row.team_id] = {
                    'total_members': row.active_members,
                    'leads': row.leads,
                    'supervisors': row.supervisors,
                    'coordinators': row.coordinators,
                    'members': row.members
                }
            
            self._logger.debug(f"Distribución de equipos: {len(distribution)} equipos analizados")
            return distribution
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener distribución de equipos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_size_distribution",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener distribución de equipos: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener distribución: {e}",
                operation="get_team_size_distribution",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_employee_participation_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de participación de empleados en equipos.
        
        Returns:
            Dict[str, Any]: Estadísticas de participación
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug("Obteniendo estadísticas de participación de empleados")
            
            # Contar empleados únicos y sus membresías
            query = select(
                func.count(distinct(TeamMembership.employee_id)).label('unique_employees'),
                func.count(TeamMembership.id).label('total_memberships'),
                func.count(case((TeamMembership.is_active == True, 1))).label('active_memberships')
            )
            
            result = await self.session.execute(query)
            row = result.first()
            
            # Calcular empleados con múltiples membresías
            multi_membership_query = select(
                TeamMembership.employee_id,
                func.count(TeamMembership.id).label('membership_count')
            ).group_by(TeamMembership.employee_id).having(
                func.count(TeamMembership.id) > 1
            )
            
            multi_result = await self.session.execute(multi_membership_query)
            multi_employees = multi_result.all()
            
            stats = {
                'unique_employees': row.unique_employees or 0,
                'total_memberships': row.total_memberships or 0,
                'active_memberships': row.active_memberships or 0,
                'employees_with_multiple_memberships': len(multi_employees),
                'average_memberships_per_employee': (row.total_memberships / row.unique_employees) if row.unique_employees > 0 else 0
            }
            
            self._logger.debug(f"Estadísticas de participación: {stats}")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener estadísticas de participación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_participation_stats",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de participación: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener estadísticas: {e}",
                operation="get_employee_participation_stats",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_membership_trends(
        self,
        start_date: date,
        end_date: date,
        interval: str = 'month'
    ) -> List[Dict[str, Any]]:
        """
        Obtiene tendencias de membresías en un período.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
            interval: Intervalo de agrupación ('month', 'quarter', 'year')
        
        Returns:
            List[Dict[str, Any]]: Lista de tendencias por período
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el análisis
        """
        try:
            self._logger.debug(f"Obteniendo tendencias de membresías desde {start_date} hasta {end_date}")
            
            # Configurar formato de fecha según intervalo
            date_format = {
                'month': '%Y-%m',
                'quarter': '%Y-Q%q',
                'year': '%Y'
            }.get(interval, '%Y-%m')
            
            # Consulta para nuevas membresías por período
            new_memberships_query = select(
                func.strftime(date_format, TeamMembership.start_date).label('period'),
                func.count(TeamMembership.id).label('new_memberships')
            ).where(
                and_(
                    TeamMembership.start_date >= start_date,
                    TeamMembership.start_date <= end_date
                )
            ).group_by(func.strftime(date_format, TeamMembership.start_date))
            
            # Consulta para membresías finalizadas por período
            ended_memberships_query = select(
                func.strftime(date_format, TeamMembership.end_date).label('period'),
                func.count(TeamMembership.id).label('ended_memberships')
            ).where(
                and_(
                    TeamMembership.end_date >= start_date,
                    TeamMembership.end_date <= end_date,
                    TeamMembership.end_date.is_not(None)
                )
            ).group_by(func.strftime(date_format, TeamMembership.end_date))
            
            new_result = await self.session.execute(new_memberships_query)
            ended_result = await self.session.execute(ended_memberships_query)
            
            new_data = {row.period: row.new_memberships for row in new_result.all()}
            ended_data = {row.period: row.ended_memberships for row in ended_result.all()}
            
            # Combinar datos
            all_periods = set(new_data.keys()) | set(ended_data.keys())
            trends = []
            
            for period in sorted(all_periods):
                new_count = new_data.get(period, 0)
                ended_count = ended_data.get(period, 0)
                net_change = new_count - ended_count
                
                trends.append({
                    'period': period,
                    'new_memberships': new_count,
                    'ended_memberships': ended_count,
                    'net_change': net_change
                })
            
            self._logger.debug(f"Obtenidas tendencias para {len(trends)} períodos")
            return trends
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener tendencias: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_membership_trends",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener tendencias: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener tendencias: {e}",
                operation="get_membership_trends",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_turnover_rate(
        self,
        team_id: Optional[int] = None,
        period_days: int = 365
    ) -> Dict[str, Any]:
        """
        Calcula la tasa de rotación de membresías.
        
        Args:
            team_id: ID del equipo (opcional, todos si None)
            period_days: Período en días para el cálculo
        
        Returns:
            Dict[str, Any]: Estadísticas de rotación
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        try:
            self._logger.debug(f"Calculando tasa de rotación para equipo {team_id}, período {period_days} días")
            
            end_date = date.today()
            start_date = end_date - timedelta(days=period_days)
            
            # Consulta base
            base_query = select(TeamMembership)
            if team_id:
                base_query = base_query.where(TeamMembership.team_id == team_id)
            
            # Membresías que terminaron en el período
            ended_query = base_query.where(
                and_(
                    TeamMembership.end_date >= start_date,
                    TeamMembership.end_date <= end_date,
                    TeamMembership.end_date.is_not(None)
                )
            )
            
            # Membresías activas al inicio del período
            active_start_query = base_query.where(
                and_(
                    TeamMembership.start_date <= start_date,
                    or_(
                        TeamMembership.end_date.is_(None),
                        TeamMembership.end_date >= start_date
                    )
                )
            )
            
            ended_result = await self.session.execute(ended_query)
            active_start_result = await self.session.execute(active_start_query)
            
            ended_count = len(ended_result.scalars().all())
            active_start_count = len(active_start_result.scalars().all())
            
            # Calcular tasa de rotación
            turnover_rate = (ended_count / active_start_count * 100) if active_start_count > 0 else 0
            
            stats = {
                'period_days': period_days,
                'team_id': team_id,
                'memberships_ended': ended_count,
                'active_at_start': active_start_count,
                'turnover_rate_percent': round(turnover_rate, 2),
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
            
            self._logger.debug(f"Tasa de rotación calculada: {turnover_rate:.2f}%")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al calcular tasa de rotación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_turnover_rate",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al calcular tasa de rotación: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al calcular rotación: {e}",
                operation="get_turnover_rate",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_retention_rate(
        self,
        team_id: Optional[int] = None,
        period_days: int = 365
    ) -> Dict[str, Any]:
        """
        Calcula la tasa de retención de membresías.
        
        Args:
            team_id: ID del equipo (opcional, todos si None)
            period_days: Período en días para el cálculo
        
        Returns:
            Dict[str, Any]: Estadísticas de retención
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el cálculo
        """
        try:
            self._logger.debug(f"Calculando tasa de retención para equipo {team_id}, período {period_days} días")
            
            # Obtener tasa de rotación primero
            turnover_stats = await self.get_turnover_rate(team_id, period_days)
            
            # La retención es el complemento de la rotación
            retention_rate = 100 - turnover_stats['turnover_rate_percent']
            
            stats = {
                'period_days': period_days,
                'team_id': team_id,
                'active_at_start': turnover_stats['active_at_start'],
                'memberships_retained': turnover_stats['active_at_start'] - turnover_stats['memberships_ended'],
                'retention_rate_percent': round(retention_rate, 2),
                'start_date': turnover_stats['start_date'],
                'end_date': turnover_stats['end_date']
            }
            
            self._logger.debug(f"Tasa de retención calculada: {retention_rate:.2f}%")
            return stats
            
        except Exception as e:
            self._logger.error(f"Error al calcular tasa de retención: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error al calcular retención: {e}",
                operation="get_retention_rate",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def get_role_transition_matrix(self) -> Dict[str, Dict[str, int]]:
        """
        Obtiene matriz de transiciones entre roles.
        
        Returns:
            Dict[str, Dict[str, int]]: Matriz de transiciones rol origen -> rol destino
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en el análisis
        """
        try:
            self._logger.debug("Obteniendo matriz de transiciones de roles")
            
            # Obtener todas las membresías ordenadas por empleado y fecha
            query = select(TeamMembership).order_by(
                TeamMembership.employee_id,
                TeamMembership.start_date
            )
            
            result = await self.session.execute(query)
            memberships = result.scalars().all()
            
            # Agrupar por empleado
            employee_memberships = {}
            for membership in memberships:
                if membership.employee_id not in employee_memberships:
                    employee_memberships[membership.employee_id] = []
                employee_memberships[membership.employee_id].append(membership)
            
            # Construir matriz de transiciones
            transitions = {}
            
            for employee_id, emp_memberships in employee_memberships.items():
                for i in range(len(emp_memberships) - 1):
                    current_role = emp_memberships[i].role.value if emp_memberships[i].role else 'unknown'
                    next_role = emp_memberships[i + 1].role.value if emp_memberships[i + 1].role else 'unknown'
                    
                    if current_role not in transitions:
                        transitions[current_role] = {}
                    
                    if next_role not in transitions[current_role]:
                        transitions[current_role][next_role] = 0
                    
                    transitions[current_role][next_role] += 1
            
            self._logger.debug(f"Matriz de transiciones generada con {len(transitions)} roles origen")
            return transitions
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener matriz de transiciones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_role_transition_matrix",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener matriz de transiciones: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al obtener transiciones: {e}",
                operation="get_role_transition_matrix",
                entity_type="TeamMembership",
                original_error=e
            )