# src/planificador/repositories/alert/crud_operations.py

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from planificador.models.alert import Alert, AlertType, AlertStatus
from planificador.schemas.alert.alert import AlertCreate, AlertUpdate
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions import (
    RepositoryError,
    NotFoundError,
    ValidationError,
    convert_sqlalchemy_error
)


class CrudOperations(BaseRepository[Alert]):
    """Operaciones CRUD para el repositorio de alertas."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa las operaciones CRUD para alertas.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        super().__init__(session, Alert)
        self._logger = logger.bind(component="AlertCrudOperations")

    async def create_alert(self, alert_data: Dict[str, Any]) -> Alert:
        """
        Crea una nueva alerta con validaciones completas.
        
        Args:
            alert_data: Datos de la alerta a crear
            
        Returns:
            Alert: La alerta creada
            
        Raises:
            ValidationError: Si los datos no son válidos
            RepositoryError: Si ocurre un error en la base de datos
        """
        try:
            self._logger.info(f"Creando nueva alerta para usuario {alert_data.get('user_id')}")
            
            # Validar datos usando el esquema Pydantic
            alert_schema = AlertCreate(**alert_data)
            validated_data = alert_schema.model_dump(exclude_unset=True)
            
            # Crear la alerta
            alert = Alert(**validated_data)
            result = await self.create(alert)
            
            self._logger.info(f"Alerta creada exitosamente con ID: {result.id}")
            return result
            
        except ValueError as e:
            self._logger.error(f"Error de validación al crear alerta: {e}")
            raise ValidationError(
                message=f"Datos de alerta inválidos: {e}",
                operation="create_alert",
                entity_type="Alert",
                original_error=e
            )
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al crear alerta: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_alert",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al crear alerta: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado al crear alerta: {e}",
                operation="create_alert",
                entity_type="Alert",
                original_error=e
            )

    async def update_alert(self, alert_id: int, update_data: Dict[str, Any]) -> Alert:
        """
        Actualiza una alerta existente con validaciones.
        
        Args:
            alert_id: ID de la alerta a actualizar
            update_data: Datos a actualizar
            
        Returns:
            Alert: La alerta actualizada
            
        Raises:
            NotFoundError: Si la alerta no existe
            ValidationError: Si los datos no son válidos
            RepositoryError: Si ocurre un error en la base de datos
        """
        try:
            self._logger.info(f"Actualizando alerta con ID: {alert_id}")
            
            # Verificar que la alerta existe
            existing_alert = await self.get_by_id(alert_id)
            if not existing_alert:
                raise NotFoundError(
                    message=f"Alerta con ID {alert_id} no encontrada",
                    resource_type="Alert",
                    resource_id=alert_id
                )
            
            # Validar datos de actualización usando el esquema Pydantic
            alert_schema = AlertUpdate(**update_data)
            validated_data = alert_schema.model_dump(exclude_unset=True)
            
            # Actualizar la alerta
            result = await self.update(alert_id, validated_data)
            
            self._logger.info(f"Alerta {alert_id} actualizada exitosamente")
            return result
            
        except NotFoundError:
            raise
        except ValueError as e:
            self._logger.error(f"Error de validación al actualizar alerta {alert_id}: {e}")
            raise ValidationError(
                message=f"Datos de actualización inválidos: {e}",
                operation="update_alert",
                entity_type="Alert",
                entity_id=alert_id,
                original_error=e
            )
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al actualizar alerta {alert_id}: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_alert",
                entity_type="Alert",
                entity_id=alert_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al actualizar alerta {alert_id}: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado al actualizar alerta: {e}",
                operation="update_alert",
                entity_type="Alert",
                entity_id=alert_id,
                original_error=e
            )

    async def delete_alert(self, alert_id: int) -> bool:
        """
        Elimina una alerta del sistema.
        
        Args:
            alert_id: ID de la alerta a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Raises:
            NotFoundError: Si la alerta no existe
            RepositoryError: Si ocurre un error en la base de datos
        """
        try:
            self._logger.info(f"Eliminando alerta con ID: {alert_id}")
            
            # Verificar que la alerta existe
            existing_alert = await self.get_by_id(alert_id)
            if not existing_alert:
                raise NotFoundError(
                    message=f"Alerta con ID {alert_id} no encontrada",
                    resource_type="Alert",
                    resource_id=alert_id
                )
            
            # Eliminar la alerta
            result = await self.delete(alert_id)
            
            self._logger.info(f"Alerta {alert_id} eliminada exitosamente")
            return result
            
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al eliminar alerta {alert_id}: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="delete_alert",
                entity_type="Alert",
                entity_id=alert_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al eliminar alerta {alert_id}: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado al eliminar alerta: {e}",
                operation="delete_alert",
                entity_type="Alert",
                entity_id=alert_id,
                original_error=e
            )

    async def bulk_create_alerts(self, alerts_data: List[Dict[str, Any]]) -> List[Alert]:
        """
        Crea múltiples alertas en lote con validaciones.
        
        Args:
            alerts_data: Lista de datos de alertas a crear
            
        Returns:
            List[Alert]: Lista de alertas creadas
            
        Raises:
            ValidationError: Si algún dato no es válido
            RepositoryError: Si ocurre un error en la base de datos
        """
        try:
            self._logger.info(f"Creando {len(alerts_data)} alertas en lote")
            
            # Validar todos los datos usando esquemas Pydantic
            validated_alerts = []
            for i, alert_data in enumerate(alerts_data):
                try:
                    alert_schema = AlertCreate(**alert_data)
                    validated_data = alert_schema.model_dump(exclude_unset=True)
                    validated_alerts.append(Alert(**validated_data))
                except ValueError as e:
                    raise ValidationError(
                        message=f"Error en alerta {i + 1}: {e}",
                        operation="bulk_create_alerts",
                        entity_type="Alert",
                        original_error=e
                    )
            
            # Crear todas las alertas en lote
            results = await self.bulk_create(validated_alerts)
            
            self._logger.info(f"{len(results)} alertas creadas exitosamente en lote")
            return results
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en creación en lote: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="bulk_create_alerts",
                entity_type="Alert"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en creación en lote: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado en creación en lote: {e}",
                operation="bulk_create_alerts",
                entity_type="Alert",
                original_error=e
            )

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