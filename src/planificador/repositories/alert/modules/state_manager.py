# src/planificador/repositories/alert/state_manager.py

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import pendulum

from planificador.models.alert import Alert, AlertStatus
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions import (
    RepositoryError,
    ValidationError,
    convert_sqlalchemy_error
)


class StateManager(BaseRepository[Alert]):
    """Gestor de estados para el repositorio de alertas."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa el gestor de estados para alertas.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        super().__init__(session, Alert)
        self._logger = logger.bind(component="AlertStateManager")

    async def get_by_unique_field(self, field_name: str, field_value: Any) -> Optional[Alert]:
        """
        Obtiene una alerta por un campo único específico.
        
        Args:
            field_name: Nombre del campo único
            field_value: Valor del campo
            
        Returns:
            Optional[Alert]: La alerta encontrada o None
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        try:
            self._logger.debug(f"Buscando alerta por {field_name}={field_value}")
            
            result = await self.get_by_field(field_name, field_value)
            
            if result:
                self._logger.debug(f"Alerta encontrada con {field_name}={field_value}")
            else:
                self._logger.debug(f"No se encontró alerta con {field_name}={field_value}")
                
            return result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos buscando por {field_name}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando por {field_name}: {e}")
            raise RepositoryError(
                message=f"Error inesperado buscando alerta: {e}",
                operation="get_by_unique_field",
                entity_type="Alert",
                original_error=e
            )

    # ==========================================
    # TRANSICIONES DE ESTADO INDIVIDUALES
    # ==========================================

    async def mark_as_read(self, alert_id: int) -> Alert:
        """
        Marca una alerta como leída.
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            Alert: La alerta actualizada
            
        Raises:
            ValidationError: Si la alerta no existe o ya está leída
        """
        try:
            self._logger.debug(f"Marcando alerta {alert_id} como leída")
            
            # Verificar que la alerta existe y está en estado NEW
            alert = await self.get_by_id(alert_id)
            if not alert:
                raise ValidationError(
                    message=f"Alerta con ID {alert_id} no encontrada",
                    field="alert_id",
                    value=alert_id
                )
            
            if alert.status != AlertStatus.NEW:
                raise ValidationError(
                    message=f"La alerta {alert_id} no está en estado NEW (estado actual: {alert.status.value})",
                    field="status",
                    value=alert.status.value
                )
            
            # Actualizar estado
            now = pendulum.now()
            stmt = update(Alert).where(
                Alert.id == alert_id
            ).values(
                status=AlertStatus.READ,
                is_read=True,
                read_at=now,
                updated_at=now
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Obtener la alerta actualizada
            updated_alert = await self.get_by_id(alert_id)
            
            self._logger.info(f"Alerta {alert_id} marcada como leída")
            return updated_alert
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error marcando alerta {alert_id} como leída: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="mark_as_read",
                entity_type="Alert",
                entity_id=alert_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado marcando alerta como leída: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado marcando alerta como leída: {e}",
                operation="mark_as_read",
                entity_type="Alert",
                entity_id=alert_id,
                original_error=e
            )

    async def mark_as_resolved(self, alert_id: int) -> Alert:
        """
        Marca una alerta como resuelta.
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            Alert: La alerta actualizada
            
        Raises:
            ValidationError: Si la alerta no existe o ya está resuelta
        """
        try:
            self._logger.debug(f"Marcando alerta {alert_id} como resuelta")
            
            # Verificar que la alerta existe y no está ya resuelta
            alert = await self.get_by_id(alert_id)
            if not alert:
                raise ValidationError(
                    message=f"Alerta con ID {alert_id} no encontrada",
                    field="alert_id",
                    value=alert_id
                )
            
            if alert.status in [AlertStatus.RESOLVED, AlertStatus.IGNORED]:
                raise ValidationError(
                    message=f"La alerta {alert_id} ya está en estado final (estado actual: {alert.status.value})",
                    field="status",
                    value=alert.status.value
                )
            
            # Actualizar estado
            now = pendulum.now()
            stmt = update(Alert).where(
                Alert.id == alert_id
            ).values(
                status=AlertStatus.RESOLVED,
                is_read=True,
                read_at=alert.read_at or now,  # Mantener read_at si ya existe
                updated_at=now
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Obtener la alerta actualizada
            updated_alert = await self.get_by_id(alert_id)
            
            self._logger.info(f"Alerta {alert_id} marcada como resuelta")
            return updated_alert
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error marcando alerta {alert_id} como resuelta: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="mark_as_resolved",
                entity_type="Alert",
                entity_id=alert_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado marcando alerta como resuelta: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado marcando alerta como resuelta: {e}",
                operation="mark_as_resolved",
                entity_type="Alert",
                entity_id=alert_id,
                original_error=e
            )

    async def mark_as_ignored(self, alert_id: int) -> Alert:
        """
        Marca una alerta como ignorada.
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            Alert: La alerta actualizada
            
        Raises:
            ValidationError: Si la alerta no existe o ya está en estado final
        """
        try:
            self._logger.debug(f"Marcando alerta {alert_id} como ignorada")
            
            # Verificar que la alerta existe y no está ya en estado final
            alert = await self.get_by_id(alert_id)
            if not alert:
                raise ValidationError(
                    message=f"Alerta con ID {alert_id} no encontrada",
                    field="alert_id",
                    value=alert_id
                )
            
            if alert.status in [AlertStatus.RESOLVED, AlertStatus.IGNORED]:
                raise ValidationError(
                    message=f"La alerta {alert_id} ya está en estado final (estado actual: {alert.status.value})",
                    field="status",
                    value=alert.status.value
                )
            
            # Actualizar estado
            now = pendulum.now()
            stmt = update(Alert).where(
                Alert.id == alert_id
            ).values(
                status=AlertStatus.IGNORED,
                is_read=True,
                read_at=alert.read_at or now,  # Mantener read_at si ya existe
                updated_at=now
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Obtener la alerta actualizada
            updated_alert = await self.get_by_id(alert_id)
            
            self._logger.info(f"Alerta {alert_id} marcada como ignorada")
            return updated_alert
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error marcando alerta {alert_id} como ignorada: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="mark_as_ignored",
                entity_type="Alert",
                entity_id=alert_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado marcando alerta como ignorada: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado marcando alerta como ignorada: {e}",
                operation="mark_as_ignored",
                entity_type="Alert",
                entity_id=alert_id,
                original_error=e
            )

    async def reactivate_alert(self, alert_id: int) -> Alert:
        """
        Reactiva una alerta resuelta o ignorada.
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            Alert: La alerta reactivada
            
        Raises:
            ValidationError: Si la alerta no existe o no está en estado final
        """
        try:
            self._logger.debug(f"Reactivando alerta {alert_id}")
            
            # Verificar que la alerta existe y está en estado final
            alert = await self.get_by_id(alert_id)
            if not alert:
                raise ValidationError(
                    message=f"Alerta con ID {alert_id} no encontrada",
                    field="alert_id",
                    value=alert_id
                )
            
            if alert.status not in [AlertStatus.RESOLVED, AlertStatus.IGNORED]:
                raise ValidationError(
                    message=f"La alerta {alert_id} no está en estado final (estado actual: {alert.status.value})",
                    field="status",
                    value=alert.status.value
                )
            
            # Actualizar estado
            now = pendulum.now()
            stmt = update(Alert).where(
                Alert.id == alert_id
            ).values(
                status=AlertStatus.READ,  # Reactivar como leída
                updated_at=now
            )
            
            await self.session.execute(stmt)
            await self.session.commit()
            
            # Obtener la alerta actualizada
            updated_alert = await self.get_by_id(alert_id)
            
            self._logger.info(f"Alerta {alert_id} reactivada")
            return updated_alert
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error reactivando alerta {alert_id}: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="reactivate_alert",
                entity_type="Alert",
                entity_id=alert_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado reactivando alerta: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado reactivando alerta: {e}",
                operation="reactivate_alert",
                entity_type="Alert",
                entity_id=alert_id,
                original_error=e
            )

    # ==========================================
    # OPERACIONES MASIVAS DE ESTADO
    # ==========================================

    async def mark_multiple_as_read(self, alert_ids: List[int]) -> List[Alert]:
        """
        Marca múltiples alertas como leídas.
        
        Args:
            alert_ids: Lista de IDs de alertas
            
        Returns:
            List[Alert]: Lista de alertas actualizadas
        """
        try:
            self._logger.debug(f"Marcando {len(alert_ids)} alertas como leídas")
            
            if not alert_ids:
                return []
            
            # Verificar que todas las alertas existen y están en estado NEW
            stmt = select(Alert).where(
                and_(
                    Alert.id.in_(alert_ids),
                    Alert.status == AlertStatus.NEW
                )
            )
            result = await self.session.execute(stmt)
            valid_alerts = result.scalars().all()
            
            valid_ids = [alert.id for alert in valid_alerts]
            
            if len(valid_ids) != len(alert_ids):
                invalid_ids = set(alert_ids) - set(valid_ids)
                self._logger.warning(f"Alertas no válidas para marcar como leídas: {invalid_ids}")
            
            if not valid_ids:
                self._logger.warning("No hay alertas válidas para marcar como leídas")
                return []
            
            # Actualizar estado
            now = pendulum.now()
            update_stmt = update(Alert).where(
                Alert.id.in_(valid_ids)
            ).values(
                status=AlertStatus.READ,
                is_read=True,
                read_at=now,
                updated_at=now
            )
            
            await self.session.execute(update_stmt)
            await self.session.commit()
            
            # Obtener las alertas actualizadas
            updated_stmt = select(Alert).where(Alert.id.in_(valid_ids))
            updated_result = await self.session.execute(updated_stmt)
            updated_alerts = updated_result.scalars().all()
            
            self._logger.info(f"{len(updated_alerts)} alertas marcadas como leídas")
            return list(updated_alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error marcando alertas múltiples como leídas: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="mark_multiple_as_read",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado marcando alertas múltiples como leídas: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado marcando alertas múltiples como leídas: {e}",
                operation="mark_multiple_as_read",
                entity_type="Alert",
                original_error=e
            )

    async def mark_all_as_read_for_employee(self, employee_id: int) -> int:
        """
        Marca todas las alertas no leídas de un empleado como leídas.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            int: Número de alertas marcadas como leídas
        """
        try:
            self._logger.debug(f"Marcando todas las alertas del empleado {employee_id} como leídas")
            
            now = pendulum.now()
            stmt = update(Alert).where(
                and_(
                    Alert.user_id == employee_id,
                    Alert.status == AlertStatus.NEW
                )
            ).values(
                status=AlertStatus.READ,
                is_read=True,
                read_at=now,
                updated_at=now
            )
            
            result = await self.session.execute(stmt)
            count = result.rowcount
            await self.session.commit()
            
            self._logger.info(f"{count} alertas del empleado {employee_id} marcadas como leídas")
            return count
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error marcando alertas del empleado {employee_id} como leídas: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="mark_all_as_read_for_employee",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado marcando alertas del empleado como leídas: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado marcando alertas del empleado como leídas: {e}",
                operation="mark_all_as_read_for_employee",
                entity_type="Alert",
                original_error=e
            )

    async def resolve_multiple_alerts(self, alert_ids: List[int]) -> List[Alert]:
        """
        Resuelve múltiples alertas.
        
        Args:
            alert_ids: Lista de IDs de alertas
            
        Returns:
            List[Alert]: Lista de alertas resueltas
        """
        try:
            self._logger.debug(f"Resolviendo {len(alert_ids)} alertas")
            
            if not alert_ids:
                return []
            
            # Verificar que todas las alertas existen y no están ya resueltas
            stmt = select(Alert).where(
                and_(
                    Alert.id.in_(alert_ids),
                    Alert.status.in_([AlertStatus.NEW, AlertStatus.READ])
                )
            )
            result = await self.session.execute(stmt)
            valid_alerts = result.scalars().all()
            
            valid_ids = [alert.id for alert in valid_alerts]
            
            if len(valid_ids) != len(alert_ids):
                invalid_ids = set(alert_ids) - set(valid_ids)
                self._logger.warning(f"Alertas no válidas para resolver: {invalid_ids}")
            
            if not valid_ids:
                self._logger.warning("No hay alertas válidas para resolver")
                return []
            
            # Actualizar estado
            now = pendulum.now()
            update_stmt = update(Alert).where(
                Alert.id.in_(valid_ids)
            ).values(
                status=AlertStatus.RESOLVED,
                is_read=True,
                updated_at=now
            )
            
            # También actualizar read_at si no está establecido
            for alert in valid_alerts:
                if not alert.read_at:
                    update_read_stmt = update(Alert).where(
                        Alert.id == alert.id
                    ).values(read_at=now)
                    await self.session.execute(update_read_stmt)
            
            await self.session.execute(update_stmt)
            await self.session.commit()
            
            # Obtener las alertas actualizadas
            updated_stmt = select(Alert).where(Alert.id.in_(valid_ids))
            updated_result = await self.session.execute(updated_stmt)
            updated_alerts = updated_result.scalars().all()
            
            self._logger.info(f"{len(updated_alerts)} alertas resueltas")
            return list(updated_alerts)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error resolviendo alertas múltiples: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="resolve_multiple_alerts",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado resolviendo alertas múltiples: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado resolviendo alertas múltiples: {e}",
                operation="resolve_multiple_alerts",
                entity_type="Alert",
                original_error=e
            )

    # ==========================================
    # OPERACIONES DE LIMPIEZA
    # ==========================================

    async def cleanup_old_resolved_alerts(self, days_old: int = 30) -> int:
        """
        Elimina alertas resueltas antiguas.
        
        Args:
            days_old: Número de días de antigüedad
            
        Returns:
            int: Número de alertas eliminadas
        """
        try:
            self._logger.debug(f"Limpiando alertas resueltas de más de {days_old} días")
            
            cutoff_date = pendulum.now().subtract(days=days_old)
            
            # Contar primero
            count_stmt = select(Alert).where(
                and_(
                    Alert.status.in_([AlertStatus.RESOLVED, AlertStatus.IGNORED]),
                    Alert.updated_at < cutoff_date
                )
            )
            count_result = await self.session.execute(count_stmt)
            alerts_to_delete = count_result.scalars().all()
            count = len(alerts_to_delete)
            
            if count == 0:
                self._logger.debug("No hay alertas resueltas antiguas para eliminar")
                return 0
            
            # Eliminar
            for alert in alerts_to_delete:
                await self.session.delete(alert)
            
            await self.session.commit()
            
            self._logger.info(f"{count} alertas resueltas antiguas eliminadas")
            return count
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error limpiando alertas resueltas antiguas: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="cleanup_old_resolved_alerts",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado limpiando alertas resueltas antiguas: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado limpiando alertas resueltas antiguas: {e}",
                operation="cleanup_old_resolved_alerts",
                entity_type="Alert",
                original_error=e
            )

    # ==========================================
    # UTILIDADES DE ESTADO
    # ==========================================

    async def get_state_transition_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de las transiciones de estado disponibles.
        
        Returns:
            Dict[str, Any]: Resumen de transiciones de estado
        """
        try:
            self._logger.debug("Generando resumen de transiciones de estado")
            
            # Contar alertas por estado
            stmt = select(
                Alert.status,
                func.count(Alert.id).label('count')
            ).group_by(Alert.status)
            
            result = await self.session.execute(stmt)
            rows = result.all()
            
            status_counts = {status.value: count for status, count in rows}
            
            # Definir transiciones válidas
            valid_transitions = {
                'NEW': ['READ', 'RESOLVED', 'IGNORED'],
                'READ': ['RESOLVED', 'IGNORED'],
                'RESOLVED': ['READ'],  # Reactivación
                'IGNORED': ['read']    # Reactivación
            }
            
            summary = {
                'current_counts': status_counts,
                'valid_transitions': valid_transitions,
                'actionable_alerts': {
                    'can_mark_as_read': status_counts.get('NEW', 0),
                    'can_resolve': status_counts.get('NEW', 0) + status_counts.get('read', 0),
                    'can_ignore': status_counts.get('NEW', 0) + status_counts.get('read', 0),
                    'can_reactivate': status_counts.get('RESOLVED', 0) + status_counts.get('IGNORED', 0)
                }
            }
            
            self._logger.debug("Resumen de transiciones de estado generado")
            return summary
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error generando resumen de transiciones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_state_transition_summary",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado generando resumen de transiciones: {e}")
            raise RepositoryError(
                message=f"Error inesperado generando resumen de transiciones: {e}",
                operation="get_state_transition_summary",
                entity_type="Alert",
                original_error=e
            )