# src/planificador/repositories/alert/validation_operations.py

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, exists
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import pendulum

from ...models.alert import Alert, AlertType, AlertStatus
from ...models.employee import Employee
from ...models.project import Project
from ..base_repository import BaseRepository
from ...schemas.alert.alert import AlertCreate, AlertUpdate
from ...exceptions.repository_exceptions import (
    RepositoryError,
    ValidationError,
    convert_sqlalchemy_error
)


class ValidationOperations(BaseRepository[Alert]):
    """Operaciones de validación para el repositorio de alertas."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa las operaciones de validación para alertas.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        super().__init__(session, Alert)
        self._logger = logger.bind(component="AlertValidationOperations")

    # ==========================================
    # VALIDACIONES DE EXISTENCIA
    # ==========================================

    async def validate_alert_exists(self, alert_id: int) -> bool:
        """
        Valida que una alerta existe.
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            bool: True si la alerta existe
        """
        try:
            self._logger.debug(f"Validando existencia de alerta {alert_id}")
            
            stmt = select(exists().where(Alert.id == alert_id))
            result = await self.session.execute(stmt)
            exists_result = result.scalar()
            
            self._logger.debug(f"Alerta {alert_id} existe: {exists_result}")
            return exists_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando existencia de alerta {alert_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_alert_exists",
                entity_type="Alert",
                entity_id=alert_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando existencia de alerta: {e}")
            raise RepositoryError(
                message=f"Error inesperado validando existencia de alerta: {e}",
                operation="validate_alert_exists",
                entity_type="Alert",
                entity_id=alert_id,
                original_error=e
            )

    async def validate_employee_exists(self, employee_id: int) -> bool:
        """
        Valida que un empleado existe.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            bool: True si el empleado existe
        """
        try:
            self._logger.debug(f"Validando existencia de empleado {employee_id}")
            
            stmt = select(exists().where(Employee.id == employee_id))
            result = await self.session.execute(stmt)
            exists_result = result.scalar()
            
            self._logger.debug(f"Empleado {employee_id} existe: {exists_result}")
            return exists_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando existencia de empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_employee_exists",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando existencia de empleado: {e}")
            raise RepositoryError(
                message=f"Error inesperado validando existencia de empleado: {e}",
                operation="validate_employee_exists",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )

    async def validate_project_exists(self, project_id: int) -> bool:
        """
        Valida que un proyecto existe.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            bool: True si el proyecto existe
        """
        try:
            self._logger.debug(f"Validando existencia de proyecto {project_id}")
            
            stmt = select(exists().where(Project.id == project_id))
            result = await self.session.execute(stmt)
            exists_result = result.scalar()
            
            self._logger.debug(f"Proyecto {project_id} existe: {exists_result}")
            return exists_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando existencia de proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_project_exists",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando existencia de proyecto: {e}")
            raise RepositoryError(
                message=f"Error inesperado validando existencia de proyecto: {e}",
                operation="validate_project_exists",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )

    # ==========================================
    # VALIDACIONES DE DATOS DE ALERTA
    # ==========================================

    async def validate_alert_data(self, alert_data: Union[AlertCreate, AlertUpdate]) -> List[str]:
        """
        Valida los datos de una alerta.
        
        Args:
            alert_data: Datos de la alerta a validar
            
        Returns:
            List[str]: Lista de errores de validación (vacía si es válida)
        """
        try:
            self._logger.debug("Validando datos de alerta")
            errors = []
            
            # Validar título
            if hasattr(alert_data, 'title') and alert_data.title:
                if len(alert_data.title.strip()) < 3:
                    errors.append("El título debe tener al menos 3 caracteres")
                elif len(alert_data.title) > 200:
                    errors.append("El título no puede exceder 200 caracteres")
            
            # Validar mensaje
            if hasattr(alert_data, 'message') and alert_data.message:
                if len(alert_data.message.strip()) < 5:
                    errors.append("El mensaje debe tener al menos 5 caracteres")
                elif len(alert_data.message) > 1000:
                    errors.append("El mensaje no puede exceder 1000 caracteres")
            
            # Validar tipo de alerta
            if hasattr(alert_data, 'type') and alert_data.type:
                if alert_data.type not in AlertType:
                    errors.append(f"Tipo de alerta inválido: {alert_data.type}")
            
            # Validar estado (solo para updates)
            if hasattr(alert_data, 'status') and alert_data.status:
                if alert_data.status not in AlertStatus:
                    errors.append(f"Estado de alerta inválido: {alert_data.status}")
            
            # Validar empleado si está presente
            if hasattr(alert_data, 'user_id') and alert_data.user_id:
                employee_exists = await self.validate_employee_exists(alert_data.user_id)
                if not employee_exists:
                    errors.append(f"El empleado con ID {alert_data.user_id} no existe")
            
            # Validar proyecto si está presente
            if hasattr(alert_data, 'project_id') and alert_data.project_id:
                project_exists = await self.validate_project_exists(alert_data.project_id)
                if not project_exists:
                    errors.append(f"El proyecto con ID {alert_data.project_id} no existe")
            
            # Validar fechas
            if hasattr(alert_data, 'read_at') and alert_data.read_at:
                if alert_data.read_at > pendulum.now():
                    errors.append("La fecha de lectura no puede ser futura")
            
            self._logger.debug(f"Validación completada. Errores encontrados: {len(errors)}")
            return errors
            
        except Exception as e:
            self._logger.error(f"Error inesperado validando datos de alerta: {e}")
            raise RepositoryError(
                message=f"Error inesperado validando datos de alerta: {e}",
                operation="validate_alert_data",
                entity_type="Alert",
                original_error=e
            )

    async def validate_alert_consistency(self, alert_id: int) -> List[str]:
        """
        Valida la consistencia interna de una alerta.
        
        Args:
            alert_id: ID de la alerta
            
        Returns:
            List[str]: Lista de errores de consistencia
        """
        try:
            self._logger.debug(f"Validando consistencia de alerta {alert_id}")
            
            alert = await self.get_by_id(alert_id)
            if not alert:
                return [f"Alerta con ID {alert_id} no encontrada"]
            
            errors = []
            
            # Validar consistencia de estado de lectura
            if alert.is_read and not alert.read_at:
                errors.append("Alerta marcada como leída pero sin fecha de lectura")
            
            if not alert.is_read and alert.read_at:
                errors.append("Alerta con fecha de lectura pero no marcada como leída")
            
            # Validar consistencia de estado
            if alert.status == AlertStatus.NEW and alert.is_read:
                errors.append("Alerta en estado NEW no puede estar marcada como leída")
            
            if alert.status in [AlertStatus.READ, AlertStatus.RESOLVED, AlertStatus.IGNORED] and not alert.is_read:
                errors.append(f"Alerta en estado {alert.status.value} debe estar marcada como leída")
            
            # Validar fechas
            if alert.read_at and alert.created_at and alert.read_at < alert.created_at:
                errors.append("La fecha de lectura no puede ser anterior a la fecha de creación")
            
            if alert.updated_at and alert.created_at and alert.updated_at < alert.created_at:
                errors.append("La fecha de actualización no puede ser anterior a la fecha de creación")
            
            # Validar relaciones
            if alert.user_id:
                employee_exists = await self.validate_employee_exists(alert.user_id)
                if not employee_exists:
                    errors.append(f"Empleado referenciado (ID: {alert.user_id}) no existe")
            
            if alert.project_id:
                project_exists = await self.validate_project_exists(alert.project_id)
                if not project_exists:
                    errors.append(f"Proyecto referenciado (ID: {alert.project_id}) no existe")
            
            self._logger.debug(f"Validación de consistencia completada. Errores: {len(errors)}")
            return errors
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando consistencia de alerta {alert_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_alert_consistency",
                entity_type="Alert",
                entity_id=alert_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando consistencia de alerta: {e}")
            raise RepositoryError(
                message=f"Error inesperado validando consistencia de alerta: {e}",
                operation="validate_alert_consistency",
                entity_type="Alert",
                entity_id=alert_id,
                original_error=e
            )

    # ==========================================
    # VALIDACIONES DE REGLAS DE NEGOCIO
    # ==========================================

    async def validate_duplicate_alert(self, title: str, user_id: int, type_alert: AlertType) -> bool:
        """
        Valida si existe una alerta duplicada activa.
        
        Args:
            title: Título de la alerta
            user_id: ID del usuario
            type_alert: Tipo de alerta
            
        Returns:
            bool: True si existe una alerta duplicada activa
        """
        try:
            self._logger.debug(f"Validando alerta duplicada para usuario {user_id}")
            
            # Buscar alertas similares activas (no resueltas ni ignoradas)
            stmt = select(exists().where(
                and_(
                    Alert.title == title,
                    Alert.user_id == user_id,
                    Alert.type == type_alert,
                    Alert.status.in_([AlertStatus.NEW, AlertStatus.READ])
                )
            ))
            
            result = await self.session.execute(stmt)
            has_duplicate = result.scalar()
            
            self._logger.debug(f"Alerta duplicada encontrada: {has_duplicate}")
            return has_duplicate
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando alerta duplicada: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_duplicate_alert",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando alerta duplicada: {e}")
            raise RepositoryError(
                message=f"Error inesperado validando alerta duplicada: {e}",
                operation="validate_duplicate_alert",
                entity_type="Alert",
                original_error=e
            )

    async def validate_alert_limit_per_user(self, user_id: int, limit: int = 50) -> bool:
        """
        Valida que un usuario no exceda el límite de alertas activas.
        
        Args:
            user_id: ID del usuario
            limit: Límite máximo de alertas activas
            
        Returns:
            bool: True si está dentro del límite
        """
        try:
            self._logger.debug(f"Validando límite de alertas para usuario {user_id}")
            
            stmt = select(func.count(Alert.id)).where(
                and_(
                    Alert.user_id == user_id,
                    Alert.status.in_([AlertStatus.NEW, AlertStatus.READ])
                )
            )
            
            result = await self.session.execute(stmt)
            current_count = result.scalar()
            
            within_limit = current_count < limit
            
            self._logger.debug(f"Usuario {user_id} tiene {current_count}/{limit} alertas activas")
            return within_limit
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando límite de alertas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_alert_limit_per_user",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando límite de alertas: {e}")
            raise RepositoryError(
                message=f"Error inesperado validando límite de alertas: {e}",
                operation="validate_alert_limit_per_user",
                entity_type="Alert",
                original_error=e
            )

    async def validate_critical_alert_escalation(self, alert_id: int, hours_threshold: int = 24) -> bool:
        """
        Valida si una alerta crítica necesita escalación.
        
        Args:
            alert_id: ID de la alerta
            hours_threshold: Umbral en horas para escalación
            
        Returns:
            bool: True si necesita escalación
        """
        try:
            self._logger.debug(f"Validando escalación para alerta crítica {alert_id}")
            
            alert = await self.get_by_id(alert_id)
            if not alert:
                return False
            
            # Solo alertas críticas no resueltas
            if alert.type != AlertType.CRITICAL or alert.status in [AlertStatus.RESOLVED, AlertStatus.IGNORED]:
                return False
            
            # Calcular tiempo transcurrido
            now = pendulum.now()
            hours_elapsed = (now - alert.created_at).total_hours()
            
            needs_escalation = hours_elapsed >= hours_threshold
            
            self._logger.debug(f"Alerta {alert_id}: {hours_elapsed:.1f}h transcurridas, escalación: {needs_escalation}")
            return needs_escalation
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando escalación de alerta {alert_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_critical_alert_escalation",
                entity_type="Alert",
                entity_id=alert_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando escalación de alerta: {e}")
            raise RepositoryError(
                message=f"Error inesperado validando escalación de alerta: {e}",
                operation="validate_critical_alert_escalation",
                entity_type="Alert",
                entity_id=alert_id,
                original_error=e
            )

    # ==========================================
    # VALIDACIONES MASIVAS
    # ==========================================

    async def validate_multiple_alerts(self, alert_ids: List[int]) -> Dict[int, List[str]]:
        """
        Valida múltiples alertas y retorna errores por alerta.
        
        Args:
            alert_ids: Lista de IDs de alertas
            
        Returns:
            Dict[int, List[str]]: Diccionario con errores por alerta
        """
        try:
            self._logger.debug(f"Validando {len(alert_ids)} alertas")
            
            validation_results = {}
            
            for alert_id in alert_ids:
                try:
                    errors = await self.validate_alert_consistency(alert_id)
                    validation_results[alert_id] = errors
                except Exception as e:
                    validation_results[alert_id] = [f"Error validando alerta: {str(e)}"]
            
            total_errors = sum(len(errors) for errors in validation_results.values())
            self._logger.debug(f"Validación masiva completada. Total errores: {total_errors}")
            
            return validation_results
            
        except Exception as e:
            self._logger.error(f"Error inesperado en validación masiva: {e}")
            raise RepositoryError(
                message=f"Error inesperado en validación masiva: {e}",
                operation="validate_multiple_alerts",
                entity_type="Alert",
                original_error=e
            )

    async def get_data_integrity_report(self) -> Dict[str, Any]:
        """
        Genera un reporte de integridad de datos de alertas.
        
        Returns:
            Dict[str, Any]: Reporte de integridad
        """
        try:
            self._logger.debug("Generando reporte de integridad de datos")
            
            # Contar alertas por estado
            status_stmt = select(
                Alert.status,
                func.count(Alert.id).label('count')
            ).group_by(Alert.status)
            status_result = await self.session.execute(status_stmt)
            status_counts = {status.value: count for status, count in status_result.all()}
            
            # Alertas con inconsistencias de lectura
            inconsistent_read_stmt = select(func.count(Alert.id)).where(
                or_(
                    and_(Alert.is_read == True, Alert.read_at.is_(None)),
                    and_(Alert.is_read == False, Alert.read_at.isnot(None))
                )
            )
            inconsistent_read_result = await self.session.execute(inconsistent_read_stmt)
            inconsistent_read_count = inconsistent_read_result.scalar()
            
            # Alertas con estados inconsistentes
            inconsistent_status_stmt = select(func.count(Alert.id)).where(
                or_(
                    and_(Alert.status == AlertStatus.NEW, Alert.is_read == True),
                    and_(Alert.status.in_([AlertStatus.READ, AlertStatus.RESOLVED, AlertStatus.IGNORED]), Alert.is_read == False)
                )
            )
            inconsistent_status_result = await self.session.execute(inconsistent_status_stmt)
            inconsistent_status_count = inconsistent_status_result.scalar()
            
            # Alertas con referencias rotas
            broken_employee_refs_stmt = select(func.count(Alert.id)).where(
                and_(
                    Alert.user_id.isnot(None),
                    ~exists().where(Employee.id == Alert.user_id)
                )
            )
            broken_employee_refs_result = await self.session.execute(broken_employee_refs_stmt)
            broken_employee_refs_count = broken_employee_refs_result.scalar()
            
            broken_project_refs_stmt = select(func.count(Alert.id)).where(
                and_(
                    Alert.project_id.isnot(None),
                    ~exists().where(Project.id == Alert.project_id)
                )
            )
            broken_project_refs_result = await self.session.execute(broken_project_refs_stmt)
            broken_project_refs_count = broken_project_refs_result.scalar()
            
            # Total de alertas
            total_stmt = select(func.count(Alert.id))
            total_result = await self.session.execute(total_stmt)
            total_count = total_result.scalar()
            
            report = {
                'total_alerts': total_count,
                'status_distribution': status_counts,
                'integrity_issues': {
                    'inconsistent_read_status': inconsistent_read_count,
                    'inconsistent_alert_status': inconsistent_status_count,
                    'broken_employee_references': broken_employee_refs_count,
                    'broken_project_references': broken_project_refs_count
                },
                'health_score': self._calculate_health_score(
                    total_count,
                    inconsistent_read_count + inconsistent_status_count + 
                    broken_employee_refs_count + broken_project_refs_count
                ),
                'generated_at': pendulum.now().isoformat()
            }
            
            self._logger.info(f"Reporte de integridad generado. Salud: {report['health_score']:.1f}%")
            return report
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error generando reporte de integridad: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_data_integrity_report",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado generando reporte de integridad: {e}")
            raise RepositoryError(
                message=f"Error inesperado generando reporte de integridad: {e}",
                operation="get_data_integrity_report",
                entity_type="Alert",
                original_error=e
            )

    def _calculate_health_score(self, total: int, issues: int) -> float:
        """
        Calcula el puntaje de salud de los datos.
        
        Args:
            total: Total de registros
            issues: Número de problemas
            
        Returns:
            float: Puntaje de salud (0-100)
        """
        if total == 0:
            return 100.0
        
        health_percentage = ((total - issues) / total) * 100
        return max(0.0, min(100.0, health_percentage))