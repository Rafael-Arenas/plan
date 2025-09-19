# src/planificador/repositories/alert/query_operations.py

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import pendulum

from ...models.alert import Alert, AlertType, AlertStatus
from ...models.employee import Employee
from ..base_repository import BaseRepository
from ...exceptions.repository_exceptions import (
    RepositoryError,
    convert_sqlalchemy_error
)


class QueryOperations(BaseRepository[Alert]):
    """Operaciones de consulta para el repositorio de alertas."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa las operaciones de consulta para alertas.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        super().__init__(session, Alert)
        self._logger = logger.bind(component="AlertQueryOperations")

    # ==========================================
    # CONSULTAS POR TIPO Y ESTADO
    # ==========================================

    async def find_by_type(self, alert_type: AlertType) -> List[Alert]:
        """
        Obtiene alertas por tipo específico.
        
        Args:
            alert_type: Tipo de alerta a buscar
            
        Returns:
            List[Alert]: Lista de alertas del tipo especificado
        """
        try:
            self._logger.debug(f"Buscando alertas por tipo: {alert_type.value}")
            
            stmt = select(Alert).where(Alert.alert_type == alert_type)
            result = await self.session.execute(stmt)
            alerts = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(alerts)} alertas del tipo {alert_type.value}")
            return list(alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando alertas por tipo {alert_type.value}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_by_type",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando por tipo: {e}")
            raise RepositoryError(
                message=f"Error inesperado buscando alertas por tipo: {e}",
                operation="find_by_type",
                entity_type="Alert",
                original_error=e
            )

    async def find_by_status(self, status: AlertStatus) -> List[Alert]:
        """
        Obtiene alertas por estado específico.
        
        Args:
            status: Estado de alerta a buscar
            
        Returns:
            List[Alert]: Lista de alertas con el estado especificado
        """
        try:
            self._logger.debug(f"Buscando alertas por estado: {status.value}")
            
            stmt = select(Alert).where(Alert.status == status)
            result = await self.session.execute(stmt)
            alerts = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(alerts)} alertas con estado {status.value}")
            return list(alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando alertas por estado {status.value}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_by_status",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando por estado: {e}")
            raise RepositoryError(
                message=f"Error inesperado buscando alertas por estado: {e}",
                operation="find_by_status",
                entity_type="Alert",
                original_error=e
            )

    async def get_active_alerts(self) -> List[Alert]:
        """
        Obtiene todas las alertas activas (NEW y READ).
        
        Returns:
            List[Alert]: Lista de alertas activas
        """
        try:
            self._logger.debug("Buscando alertas activas")
            
            stmt = select(Alert).where(
                Alert.status.in_([AlertStatus.NEW, AlertStatus.READ])
            ).order_by(desc(Alert.created_at))
            
            result = await self.session.execute(stmt)
            alerts = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(alerts)} alertas activas")
            return list(alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo alertas activas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_active_alerts",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo alertas activas: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo alertas activas: {e}",
                operation="get_active_alerts",
                entity_type="Alert",
                original_error=e
            )

    async def get_critical_alerts(self) -> List[Alert]:
        """
        Obtiene alertas críticas activas.
        
        Returns:
            List[Alert]: Lista de alertas críticas
        """
        try:
            self._logger.debug("Buscando alertas críticas")
            
            critical_types = [
                AlertType.CONFLICT,
                AlertType.SYSTEM_ERROR,
                AlertType.VALIDATION_ERROR,
                AlertType.DEADLINE_WARNING
            ]
            
            stmt = select(Alert).where(
                and_(
                    Alert.alert_type.in_(critical_types),
                    Alert.status.in_([AlertStatus.NEW, AlertStatus.READ])
                )
            ).order_by(desc(Alert.created_at))
            
            result = await self.session.execute(stmt)
            alerts = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(alerts)} alertas críticas")
            return list(alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo alertas críticas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_critical_alerts",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo alertas críticas: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo alertas críticas: {e}",
                operation="get_critical_alerts",
                entity_type="Alert",
                original_error=e
            )

    async def get_unread_alerts(self) -> List[Alert]:
        """
        Obtiene alertas no leídas (estado NEW).
        
        Returns:
            List[Alert]: Lista de alertas no leídas
        """
        try:
            self._logger.debug("Buscando alertas no leídas")
            
            stmt = select(Alert).where(
                Alert.status == AlertStatus.NEW
            ).order_by(desc(Alert.created_at))
            
            result = await self.session.execute(stmt)
            alerts = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(alerts)} alertas no leídas")
            return list(alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo alertas no leídas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_unread_alerts",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo alertas no leídas: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo alertas no leídas: {e}",
                operation="get_unread_alerts",
                entity_type="Alert",
                original_error=e
            )

    async def get_alerts_with_relations(self) -> List[Alert]:
        """
        Obtiene todas las alertas con sus relaciones cargadas.
        
        Returns:
            List[Alert]: Lista de alertas con relaciones
        """
        try:
            self._logger.debug("Obteniendo alertas con relaciones")
            
            stmt = select(Alert).options(
                selectinload(Alert.user)
            ).order_by(desc(Alert.created_at))
            
            result = await self.session.execute(stmt)
            alerts = result.scalars().all()
            
            self._logger.debug(f"Obtenidas {len(alerts)} alertas con relaciones")
            return list(alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo alertas con relaciones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_alerts_with_relations",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo alertas con relaciones: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo alertas con relaciones: {e}",
                operation="get_alerts_with_relations",
                entity_type="Alert",
                original_error=e
            )

    async def get_with_relations(self, alert_id: int) -> Optional[Alert]:
        """
        Obtiene alerta específica con todas sus relaciones cargadas.
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            Optional[Alert]: La alerta con relaciones o None
        """
        try:
            self._logger.debug(f"Obteniendo alerta {alert_id} con relaciones")
            
            stmt = select(Alert).options(
                selectinload(Alert.user)
            ).where(Alert.id == alert_id)
            
            result = await self.session.execute(stmt)
            alert = result.scalar_one_or_none()
            
            if alert:
                self._logger.debug(f"Alerta {alert_id} obtenida con relaciones")
            else:
                self._logger.debug(f"Alerta {alert_id} no encontrada")
                
            return alert
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo alerta {alert_id} con relaciones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_relations",
                entity_type="Alert",
                entity_id=alert_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo alerta con relaciones: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo alerta con relaciones: {e}",
                operation="get_with_relations",
                entity_type="Alert",
                entity_id=alert_id,
                original_error=e
            )

    # ==========================================
    # CONSULTAS POR ENTIDADES RELACIONADAS
    # ==========================================

    async def find_by_employee(self, employee_id: int) -> List[Alert]:
        """
        Obtiene alertas asociadas a un empleado específico.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            List[Alert]: Lista de alertas del empleado
        """
        try:
            self._logger.debug(f"Buscando alertas del empleado {employee_id}")
            
            stmt = select(Alert).where(
                Alert.user_id == employee_id
            ).order_by(desc(Alert.created_at))
            
            result = await self.session.execute(stmt)
            alerts = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(alerts)} alertas para empleado {employee_id}")
            return list(alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando alertas del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_by_employee",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando alertas del empleado: {e}")
            raise RepositoryError(
                message=f"Error inesperado buscando alertas del empleado: {e}",
                operation="find_by_employee",
                entity_type="Alert",
                original_error=e
            )

    async def find_by_project(self, project_id: int) -> List[Alert]:
        """
        Obtiene alertas asociadas a un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            List[Alert]: Lista de alertas del proyecto
        """
        try:
            self._logger.debug(f"Buscando alertas del proyecto {project_id}")
            
            stmt = select(Alert).where(
                and_(
                    Alert.related_entity_type == "Project",
                    Alert.related_entity_id == project_id
                )
            ).order_by(desc(Alert.created_at))
            
            result = await self.session.execute(stmt)
            alerts = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(alerts)} alertas para proyecto {project_id}")
            return list(alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando alertas del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_by_project",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando alertas del proyecto: {e}")
            raise RepositoryError(
                message=f"Error inesperado buscando alertas del proyecto: {e}",
                operation="find_by_project",
                entity_type="Alert",
                original_error=e
            )

    # ==========================================
    # CONSULTAS TEMPORALES
    # ==========================================

    async def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Alert]:
        """
        Obtiene alertas en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            List[Alert]: Lista de alertas en el rango
        """
        try:
            self._logger.debug(f"Buscando alertas entre {start_date} y {end_date}")
            
            stmt = select(Alert).where(
                and_(
                    Alert.created_at >= start_date,
                    Alert.created_at <= end_date
                )
            ).order_by(desc(Alert.created_at))
            
            result = await self.session.execute(stmt)
            alerts = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(alerts)} alertas en el rango de fechas")
            return list(alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando alertas por rango de fechas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_by_date_range",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando por rango de fechas: {e}")
            raise RepositoryError(
                message=f"Error inesperado buscando alertas por rango de fechas: {e}",
                operation="find_by_date_range",
                entity_type="Alert",
                original_error=e
            )

    async def get_old_resolved_alerts(self, days_old: int = 30) -> List[Alert]:
        """
        Obtiene alertas resueltas antiguas para limpieza.
        
        Args:
            days_old: Número de días de antigüedad
            
        Returns:
            List[Alert]: Lista de alertas resueltas antiguas
        """
        try:
            self._logger.debug(f"Buscando alertas resueltas de más de {days_old} días")
            
            cutoff_date = pendulum.now().subtract(days=days_old)
            
            stmt = select(Alert).where(
                and_(
                    Alert.status.in_([AlertStatus.RESOLVED, AlertStatus.IGNORED]),
                    Alert.updated_at < cutoff_date
                )
            ).order_by(asc(Alert.updated_at))
            
            result = await self.session.execute(stmt)
            alerts = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(alerts)} alertas resueltas antiguas")
            return list(alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando alertas resueltas antiguas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_old_resolved_alerts",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando alertas resueltas antiguas: {e}")
            raise RepositoryError(
                message=f"Error inesperado buscando alertas resueltas antiguas: {e}",
                operation="get_old_resolved_alerts",
                entity_type="Alert",
                original_error=e
            )

    async def get_current_week_alerts(self) -> List[Alert]:
        """
        Obtiene alertas de la semana actual.
        
        Returns:
            List[Alert]: Lista de alertas de la semana actual
        """
        try:
            self._logger.debug("Obteniendo alertas de la semana actual")
            
            now = pendulum.now()
            start_of_week = now.start_of('week')
            end_of_week = now.end_of('week')
            
            return await self.find_by_date_range(start_of_week, end_of_week)
            
        except Exception as e:
            self._logger.error(f"Error obteniendo alertas de la semana actual: {e}")
            raise RepositoryError(
                message=f"Error obteniendo alertas de la semana actual: {e}",
                operation="get_current_week_alerts",
                entity_type="Alert",
                original_error=e
            )

    async def get_current_month_alerts(self) -> List[Alert]:
        """
        Obtiene alertas del mes actual.
        
        Returns:
            List[Alert]: Lista de alertas del mes actual
        """
        try:
            self._logger.debug("Obteniendo alertas del mes actual")
            
            now = pendulum.now()
            start_of_month = now.start_of('month')
            end_of_month = now.end_of('month')
            
            return await self.find_by_date_range(start_of_month, end_of_month)
            
        except Exception as e:
            self._logger.error(f"Error obteniendo alertas del mes actual: {e}")
            raise RepositoryError(
                message=f"Error obteniendo alertas del mes actual: {e}",
                operation="get_current_month_alerts",
                entity_type="Alert",
                original_error=e
            )

    # ==========================================
    # CONSULTAS CON FILTROS DINÁMICOS
    # ==========================================

    async def get_all_with_filters(self, filters: Dict[str, Any]) -> List[Alert]:
        """
        Obtiene alertas con filtros dinámicos.
        
        Args:
            filters: Diccionario de filtros a aplicar
            
        Returns:
            List[Alert]: Lista de alertas filtradas
        """
        try:
            self._logger.debug(f"Aplicando filtros dinámicos: {filters}")
            
            stmt = select(Alert)
            conditions = []
            
            # Aplicar filtros dinámicamente
            if 'user_id' in filters and filters['user_id'] is not None:
                conditions.append(Alert.user_id == filters['user_id'])
                
            if 'alert_type' in filters and filters['alert_type'] is not None:
                conditions.append(Alert.alert_type == filters['alert_type'])
                
            if 'status' in filters and filters['status'] is not None:
                conditions.append(Alert.status == filters['status'])
                
            if 'is_read' in filters and filters['is_read'] is not None:
                conditions.append(Alert.is_read == filters['is_read'])
                
            if 'related_entity_type' in filters and filters['related_entity_type'] is not None:
                conditions.append(Alert.related_entity_type == filters['related_entity_type'])
                
            if 'related_entity_id' in filters and filters['related_entity_id'] is not None:
                conditions.append(Alert.related_entity_id == filters['related_entity_id'])
            
            # Aplicar condiciones si existen
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            # Ordenar por fecha de creación descendente
            stmt = stmt.order_by(desc(Alert.created_at))
            
            result = await self.session.execute(stmt)
            alerts = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(alerts)} alertas con filtros aplicados")
            return list(alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error aplicando filtros dinámicos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_all_with_filters",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado aplicando filtros: {e}")
            raise RepositoryError(
                message=f"Error inesperado aplicando filtros: {e}",
                operation="get_all_with_filters",
                entity_type="Alert",
                original_error=e
            )

    async def count_alerts_by_date_range(self, start_date: datetime, end_date: datetime) -> int:
        """
        Cuenta alertas en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            int: Número de alertas en el rango
        """
        try:
            self._logger.debug(f"Contando alertas entre {start_date} y {end_date}")
            
            stmt = select(func.count(Alert.id)).where(
                and_(
                    Alert.created_at >= start_date,
                    Alert.created_at <= end_date
                )
            )
            
            result = await self.session.execute(stmt)
            count = result.scalar() or 0
            
            self._logger.debug(f"Contadas {count} alertas en el rango de fechas")
            return count
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error contando alertas por rango de fechas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_alerts_by_date_range",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado contando alertas: {e}")
            raise RepositoryError(
                message=f"Error inesperado contando alertas: {e}",
                operation="count_alerts_by_date_range",
                entity_type="Alert",
                original_error=e
            )