# src/planificador/repositories/alert/statistics_operations.py

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case, desc
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import pendulum

from ...models.alert import Alert, AlertType, AlertStatus
from ..base_repository import BaseRepository
from ...exceptions.repository_exceptions import (
    RepositoryError,
    convert_sqlalchemy_error
)


class StatisticsOperations(BaseRepository[Alert]):
    """Operaciones estadísticas para el repositorio de alertas."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa las operaciones estadísticas para alertas.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        super().__init__(session, Alert)
        self._logger = logger.bind(component="AlertStatisticsOperations")

    # ==========================================
    # CONTEOS BÁSICOS
    # ==========================================

    async def count_total_alerts(self) -> int:
        """
        Cuenta el total de alertas en el sistema.
        
        Returns:
            int: Número total de alertas
        """
        try:
            self._logger.debug("Contando total de alertas")
            
            stmt = select(func.count(Alert.id))
            result = await self.session.execute(stmt)
            count = result.scalar() or 0
            
            self._logger.debug(f"Total de alertas: {count}")
            return count
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error contando total de alertas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_total_alerts",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado contando alertas: {e}")
            raise RepositoryError(
                message=f"Error inesperado contando alertas: {e}",
                operation="count_total_alerts",
                entity_type="Alert",
                original_error=e
            )

    async def count_by_status(self) -> Dict[str, int]:
        """
        Cuenta alertas agrupadas por estado.
        
        Returns:
            Dict[str, int]: Diccionario con conteos por estado
        """
        try:
            self._logger.debug("Contando alertas por estado")
            
            stmt = select(
                Alert.status,
                func.count(Alert.id).label('count')
            ).group_by(Alert.status)
            
            result = await self.session.execute(stmt)
            rows = result.all()
            
            counts = {status.value: count for status, count in rows}
            
            # Asegurar que todos los estados estén representados
            for status in AlertStatus:
                if status.value not in counts:
                    counts[status.value] = 0
            
            self._logger.debug(f"Conteos por estado: {counts}")
            return counts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error contando alertas por estado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_by_status",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado contando por estado: {e}")
            raise RepositoryError(
                message=f"Error inesperado contando alertas por estado: {e}",
                operation="count_by_status",
                entity_type="Alert",
                original_error=e
            )

    async def count_by_type(self) -> Dict[str, int]:
        """
        Cuenta alertas agrupadas por tipo.
        
        Returns:
            Dict[str, int]: Diccionario con conteos por tipo
        """
        try:
            self._logger.debug("Contando alertas por tipo")
            
            stmt = select(
                Alert.alert_type,
                func.count(Alert.id).label('count')
            ).group_by(Alert.alert_type)
            
            result = await self.session.execute(stmt)
            rows = result.all()
            
            counts = {alert_type.value: count for alert_type, count in rows}
            
            # Asegurar que todos los tipos estén representados
            for alert_type in AlertType:
                if alert_type.value not in counts:
                    counts[alert_type.value] = 0
            
            self._logger.debug(f"Conteos por tipo: {counts}")
            return counts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error contando alertas por tipo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_by_type",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado contando por tipo: {e}")
            raise RepositoryError(
                message=f"Error inesperado contando alertas por tipo: {e}",
                operation="count_by_type",
                entity_type="Alert",
                original_error=e
            )

    async def count_unread_alerts(self) -> int:
        """
        Cuenta alertas no leídas.
        
        Returns:
            int: Número de alertas no leídas
        """
        try:
            self._logger.debug("Contando alertas no leídas")
            
            stmt = select(func.count(Alert.id)).where(
                Alert.status == AlertStatus.NEW
            )
            
            result = await self.session.execute(stmt)
            count = result.scalar() or 0
            
            self._logger.debug(f"Alertas no leídas: {count}")
            return count
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error contando alertas no leídas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_unread_alerts",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado contando alertas no leídas: {e}")
            raise RepositoryError(
                message=f"Error inesperado contando alertas no leídas: {e}",
                operation="count_unread_alerts",
                entity_type="Alert",
                original_error=e
            )

    async def count_critical_alerts(self) -> int:
        """
        Cuenta alertas críticas activas.
        
        Returns:
            int: Número de alertas críticas
        """
        try:
            self._logger.debug("Contando alertas críticas")
            
            critical_types = [
                AlertType.CONFLICT,
                AlertType.SYSTEM_ERROR,
                AlertType.VALIDATION_ERROR,
                AlertType.DEADLINE_WARNING
            ]
            
            stmt = select(func.count(Alert.id)).where(
                and_(
                    Alert.alert_type.in_(critical_types),
                    Alert.status.in_([AlertStatus.NEW, AlertStatus.READ])
                )
            )
            
            result = await self.session.execute(stmt)
            count = result.scalar() or 0
            
            self._logger.debug(f"Alertas críticas: {count}")
            return count
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error contando alertas críticas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_critical_alerts",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado contando alertas críticas: {e}")
            raise RepositoryError(
                message=f"Error inesperado contando alertas críticas: {e}",
                operation="count_critical_alerts",
                entity_type="Alert",
                original_error=e
            )

    # ==========================================
    # ESTADÍSTICAS POR EMPLEADO
    # ==========================================

    async def count_by_employee(self) -> Dict[int, int]:
        """
        Cuenta alertas agrupadas por empleado.
        
        Returns:
            Dict[int, int]: Diccionario con conteos por empleado (user_id: count)
        """
        try:
            self._logger.debug("Contando alertas por empleado")
            
            stmt = select(
                Alert.user_id,
                func.count(Alert.id).label('count')
            ).where(
                Alert.user_id.is_not(None)
            ).group_by(Alert.user_id)
            
            result = await self.session.execute(stmt)
            rows = result.all()
            
            counts = {user_id: count for user_id, count in rows}
            
            self._logger.debug(f"Conteos por empleado: {len(counts)} empleados")
            return counts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error contando alertas por empleado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_by_employee",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado contando por empleado: {e}")
            raise RepositoryError(
                message=f"Error inesperado contando alertas por empleado: {e}",
                operation="count_by_employee",
                entity_type="Alert",
                original_error=e
            )

    async def get_employee_alert_summary(self, employee_id: int) -> Dict[str, Any]:
        """
        Obtiene resumen de alertas para un empleado específico.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Dict[str, Any]: Resumen de alertas del empleado
        """
        try:
            self._logger.debug(f"Obteniendo resumen de alertas para empleado {employee_id}")
            
            # Conteo total
            total_stmt = select(func.count(Alert.id)).where(
                Alert.user_id == employee_id
            )
            total_result = await self.session.execute(total_stmt)
            total = total_result.scalar() or 0
            
            # Conteo por estado
            status_stmt = select(
                Alert.status,
                func.count(Alert.id).label('count')
            ).where(
                Alert.user_id == employee_id
            ).group_by(Alert.status)
            
            status_result = await self.session.execute(status_stmt)
            status_rows = status_result.all()
            status_counts = {status.value: count for status, count in status_rows}
            
            # Conteo por tipo
            type_stmt = select(
                Alert.alert_type,
                func.count(Alert.id).label('count')
            ).where(
                Alert.user_id == employee_id
            ).group_by(Alert.alert_type)
            
            type_result = await self.session.execute(type_stmt)
            type_rows = type_result.all()
            type_counts = {alert_type.value: count for alert_type, count in type_rows}
            
            summary = {
                'employee_id': employee_id,
                'total_alerts': total,
                'by_status': status_counts,
                'by_type': type_counts,
                'unread_count': status_counts.get('NEW', 0),
                'active_count': status_counts.get('NEW', 0) + status_counts.get('READ', 0)
            }
            
            self._logger.debug(f"Resumen generado para empleado {employee_id}")
            return summary
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo resumen del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_alert_summary",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo resumen del empleado: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo resumen del empleado: {e}",
                operation="get_employee_alert_summary",
                entity_type="Alert",
                original_error=e
            )

    # ==========================================
    # ESTADÍSTICAS TEMPORALES
    # ==========================================

    async def get_daily_alert_counts(self, days: int = 30) -> Dict[str, int]:
        """
        Obtiene conteos diarios de alertas para los últimos N días.
        
        Args:
            days: Número de días a incluir
            
        Returns:
            Dict[str, int]: Conteos por día (fecha: count)
        """
        try:
            self._logger.debug(f"Obteniendo conteos diarios para {days} días")
            
            end_date = pendulum.now()
            start_date = end_date.subtract(days=days)
            
            stmt = select(
                func.date(Alert.created_at).label('date'),
                func.count(Alert.id).label('count')
            ).where(
                Alert.created_at >= start_date
            ).group_by(
                func.date(Alert.created_at)
            ).order_by(
                func.date(Alert.created_at)
            )
            
            result = await self.session.execute(stmt)
            rows = result.all()
            
            counts = {str(date): count for date, count in rows}
            
            self._logger.debug(f"Conteos diarios obtenidos: {len(counts)} días")
            return counts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo conteos diarios: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_daily_alert_counts",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo conteos diarios: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo conteos diarios: {e}",
                operation="get_daily_alert_counts",
                entity_type="Alert",
                original_error=e
            )

    async def get_weekly_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la semana actual.
        
        Returns:
            Dict[str, Any]: Estadísticas semanales
        """
        try:
            self._logger.debug("Obteniendo estadísticas semanales")
            
            now = pendulum.now()
            start_of_week = now.start_of('week')
            end_of_week = now.end_of('week')
            
            # Total de la semana
            total_stmt = select(func.count(Alert.id)).where(
                and_(
                    Alert.created_at >= start_of_week,
                    Alert.created_at <= end_of_week
                )
            )
            total_result = await self.session.execute(total_stmt)
            total = total_result.scalar() or 0
            
            # Por estado
            status_stmt = select(
                Alert.status,
                func.count(Alert.id).label('count')
            ).where(
                and_(
                    Alert.created_at >= start_of_week,
                    Alert.created_at <= end_of_week
                )
            ).group_by(Alert.status)
            
            status_result = await self.session.execute(status_stmt)
            status_rows = status_result.all()
            status_counts = {status.value: count for status, count in status_rows}
            
            # Por tipo
            type_stmt = select(
                Alert.alert_type,
                func.count(Alert.id).label('count')
            ).where(
                and_(
                    Alert.created_at >= start_of_week,
                    Alert.created_at <= end_of_week
                )
            ).group_by(Alert.alert_type)
            
            type_result = await self.session.execute(type_stmt)
            type_rows = type_result.all()
            type_counts = {alert_type.value: count for alert_type, count in type_rows}
            
            statistics = {
                'period': 'current_week',
                'start_date': start_of_week.isoformat(),
                'end_date': end_of_week.isoformat(),
                'total_alerts': total,
                'by_status': status_counts,
                'by_type': type_counts
            }
            
            self._logger.debug("Estadísticas semanales obtenidas")
            return statistics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo estadísticas semanales: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_weekly_statistics",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo estadísticas semanales: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo estadísticas semanales: {e}",
                operation="get_weekly_statistics",
                entity_type="Alert",
                original_error=e
            )

    async def get_monthly_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del mes actual.
        
        Returns:
            Dict[str, Any]: Estadísticas mensuales
        """
        try:
            self._logger.debug("Obteniendo estadísticas mensuales")
            
            now = pendulum.now()
            start_of_month = now.start_of('month')
            end_of_month = now.end_of('month')
            
            # Total del mes
            total_stmt = select(func.count(Alert.id)).where(
                and_(
                    Alert.created_at >= start_of_month,
                    Alert.created_at <= end_of_month
                )
            )
            total_result = await self.session.execute(total_stmt)
            total = total_result.scalar() or 0
            
            # Por estado
            status_stmt = select(
                Alert.status,
                func.count(Alert.id).label('count')
            ).where(
                and_(
                    Alert.created_at >= start_of_month,
                    Alert.created_at <= end_of_month
                )
            ).group_by(Alert.status)
            
            status_result = await self.session.execute(status_stmt)
            status_rows = status_result.all()
            status_counts = {status.value: count for status, count in status_rows}
            
            # Por tipo
            type_stmt = select(
                Alert.alert_type,
                func.count(Alert.id).label('count')
            ).where(
                and_(
                    Alert.created_at >= start_of_month,
                    Alert.created_at <= end_of_month
                )
            ).group_by(Alert.alert_type)
            
            type_result = await self.session.execute(type_stmt)
            type_rows = type_result.all()
            type_counts = {alert_type.value: count for alert_type, count in type_rows}
            
            statistics = {
                'period': 'current_month',
                'start_date': start_of_month.isoformat(),
                'end_date': end_of_month.isoformat(),
                'total_alerts': total,
                'by_status': status_counts,
                'by_type': type_counts
            }
            
            self._logger.debug("Estadísticas mensuales obtenidas")
            return statistics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo estadísticas mensuales: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_monthly_statistics",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo estadísticas mensuales: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo estadísticas mensuales: {e}",
                operation="get_monthly_statistics",
                entity_type="Alert",
                original_error=e
            )

    # ==========================================
    # ESTADÍSTICAS AVANZADAS
    # ==========================================

    async def get_alert_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtiene tendencias de alertas para análisis.
        
        Args:
            days: Número de días para el análisis
            
        Returns:
            Dict[str, Any]: Análisis de tendencias
        """
        try:
            self._logger.debug(f"Analizando tendencias de alertas para {days} días")
            
            end_date = pendulum.now()
            start_date = end_date.subtract(days=days)
            
            # Conteos diarios
            daily_counts = await self.get_daily_alert_counts(days)
            
            # Promedio diario
            total_alerts = sum(daily_counts.values())
            avg_daily = total_alerts / days if days > 0 else 0
            
            # Pico máximo
            max_day = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else (None, 0)
            
            # Día mínimo
            min_day = min(daily_counts.items(), key=lambda x: x[1]) if daily_counts else (None, 0)
            
            trends = {
                'period_days': days,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_alerts': total_alerts,
                'average_daily': round(avg_daily, 2),
                'peak_day': {
                    'date': max_day[0],
                    'count': max_day[1]
                },
                'lowest_day': {
                    'date': min_day[0],
                    'count': min_day[1]
                },
                'daily_counts': daily_counts
            }
            
            self._logger.debug("Análisis de tendencias completado")
            return trends
            
        except Exception as e:
            self._logger.error(f"Error analizando tendencias: {e}")
            raise RepositoryError(
                message=f"Error analizando tendencias de alertas: {e}",
                operation="get_alert_trends",
                entity_type="Alert",
                original_error=e
            )

    async def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas completas del sistema de alertas.
        
        Returns:
            Dict[str, Any]: Estadísticas completas
        """
        try:
            self._logger.debug("Generando estadísticas completas")
            
            # Obtener todas las estadísticas básicas
            total = await self.count_total_alerts()
            by_status = await self.count_by_status()
            by_type = await self.count_by_type()
            unread = await self.count_unread_alerts()
            critical = await self.count_critical_alerts()
            
            # Estadísticas temporales
            weekly_stats = await self.get_weekly_statistics()
            monthly_stats = await self.get_monthly_statistics()
            
            # Estadísticas por empleado
            by_employee = await self.count_by_employee()
            
            comprehensive = {
                'generated_at': pendulum.now().isoformat(),
                'totals': {
                    'all_alerts': total,
                    'unread_alerts': unread,
                    'critical_alerts': critical,
                    'active_alerts': by_status.get('NEW', 0) + by_status.get('read', 0)
                },
                'by_status': by_status,
                'by_type': by_type,
                'by_employee_count': len(by_employee),
                'current_week': weekly_stats,
                'current_month': monthly_stats,
                'employee_distribution': by_employee
            }
            
            self._logger.debug("Estadísticas completas generadas")
            return comprehensive
            
        except Exception as e:
            self._logger.error(f"Error generando estadísticas completas: {e}")
            raise RepositoryError(
                message=f"Error generando estadísticas completas: {e}",
                operation="get_comprehensive_statistics",
                entity_type="Alert",
                original_error=e
            )