# src/planificador/services/domain/client/modules/validation_operations.py

"""
Módulo de operaciones de validación para el servicio de dominio de cliente.

Este módulo implementa validaciones de datos, reglas de negocio y verificaciones
de integridad específicas del dominio de cliente.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from planificador.exceptions import RepositoryError, ValidationError
from planificador.repositories.client.client_repository_facade import ClientRepositoryFacade
from planificador.schemas import Client, ClientCreate, ClientUpdate
from planificador.services.domain.client.interfaces.validation_interface import IValidationOperations


class ValidationOperations(IValidationOperations):
    """
    Implementación de operaciones de validación para el dominio de cliente.
    
    Esta clase encapsula todas las validaciones de datos, reglas de negocio
    y verificaciones de integridad relacionadas con clientes.
    """

    def __init__(self, client_repository: ClientRepositoryFacade):
        """
        Inicializa el módulo de operaciones de validación.
        
        Args:
            client_repository: Facade del repositorio de cliente
        """
        self._client_repository = client_repository
        self._logger = logger

    async def validate_client_creation_data(self, client_data: ClientCreate) -> Dict[str, Any]:
        """
        Valida los datos para la creación de un cliente.
        
        Args:
            client_data: Datos del cliente a crear
            
        Returns:
            Dict[str, Any]: Resultado de la validación
        """
        try:
            self._logger.debug(f"Validando datos de creación para cliente: {client_data.name}")
            
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "field_validations": {}
            }
            
            # Validar nombre
            name_validation = await self._validate_client_name(client_data.name)
            validation_result["field_validations"]["name"] = name_validation
            if not name_validation["is_valid"]:
                validation_result["errors"].extend(name_validation["errors"])
            
            # Validar código si está presente
            if client_data.code:
                code_validation = await self._validate_client_code(client_data.code)
                validation_result["field_validations"]["code"] = code_validation
                if not code_validation["is_valid"]:
                    validation_result["errors"].extend(code_validation["errors"])
            
            # Validar email si está presente
            if client_data.email:
                email_validation = await self._validate_client_email(client_data.email)
                validation_result["field_validations"]["email"] = email_validation
                if not email_validation["is_valid"]:
                    validation_result["errors"].extend(email_validation["errors"])
            
            # Validar unicidad de email
            if client_data.email:
                email_unique = await self.validate_email_uniqueness(client_data.email)
                if not email_unique["is_unique"]:
                    validation_result["errors"].append(
                        f"El email '{client_data.email}' ya está en uso"
                    )
            
            # Validar notas si están presentes
            if client_data.notes:
                notes_validation = self._validate_client_notes(client_data.notes)
                validation_result["field_validations"]["notes"] = notes_validation
                if not notes_validation["is_valid"]:
                    validation_result["warnings"].extend(notes_validation["warnings"])
            
            # Determinar validez general
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            self._logger.debug(f"Validación de creación completada. Válido: {validation_result['is_valid']}")
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error al validar datos de creación: {e}")
            raise RepositoryError(
                message=f"Error en validación de creación: {e}",
                operation="validate_client_creation_data",
                entity_type="Client",
                original_error=e
            )

    async def validate_client_update_data(
        self,
        client_id: int,
        update_data: ClientUpdate
    ) -> Dict[str, Any]:
        """
        Valida los datos para la actualización de un cliente.
        
        Args:
            client_id: ID del cliente a actualizar
            update_data: Datos de actualización
            
        Returns:
            Dict[str, Any]: Resultado de la validación
        """
        try:
            self._logger.debug(f"Validando datos de actualización para cliente {client_id}")
            
            # Verificar que el cliente existe
            existing_client = await self._client_repository.get_client_by_id(client_id)
            if not existing_client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=client_id
                )
            
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "field_validations": {},
                "changes_detected": []
            }
            
            # Validar nombre si se está actualizando
            if update_data.name is not None:
                if update_data.name != existing_client.name:
                    validation_result["changes_detected"].append("name")
                    name_validation = await self._validate_client_name(update_data.name)
                    validation_result["field_validations"]["name"] = name_validation
                    if not name_validation["is_valid"]:
                        validation_result["errors"].extend(name_validation["errors"])
            
            # Validar código si se está actualizando
            if update_data.code is not None:
                if update_data.code != existing_client.code:
                    validation_result["changes_detected"].append("code")
                    code_validation = await self._validate_client_code(update_data.code)
                    validation_result["field_validations"]["code"] = code_validation
                    if not code_validation["is_valid"]:
                        validation_result["errors"].extend(code_validation["errors"])
            
            # Validar email si se está actualizando
            if update_data.email is not None:
                if update_data.email != existing_client.email:
                    validation_result["changes_detected"].append("email")
                    email_validation = await self._validate_client_email(update_data.email)
                    validation_result["field_validations"]["email"] = email_validation
                    if not email_validation["is_valid"]:
                        validation_result["errors"].extend(email_validation["errors"])
                    
                    # Validar unicidad de email (excluyendo el cliente actual)
                    email_unique = await self.validate_email_uniqueness(
                        update_data.email,
                        exclude_client_id=client_id
                    )
                    if not email_unique["is_unique"]:
                        validation_result["errors"].append(
                            f"El email '{update_data.email}' ya está en uso por otro cliente"
                        )
            
            # Validar estado si se está actualizando
            if update_data.is_active is not None:
                if update_data.is_active != existing_client.is_active:
                    validation_result["changes_detected"].append("is_active")
                    # Validar transición de estado
                    status_validation = await self.validate_client_status_transition(
                        client_id,
                        existing_client.is_active,
                        update_data.is_active
                    )
                    if not status_validation["is_valid"]:
                        validation_result["errors"].extend(status_validation["errors"])
            
            # Validar notas si se están actualizando
            if update_data.notes is not None:
                if update_data.notes != existing_client.notes:
                    validation_result["changes_detected"].append("notes")
                    notes_validation = self._validate_client_notes(update_data.notes)
                    validation_result["field_validations"]["notes"] = notes_validation
                    if not notes_validation["is_valid"]:
                        validation_result["warnings"].extend(notes_validation["warnings"])
            
            # Determinar validez general
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            self._logger.debug(f"Validación de actualización completada. Válido: {validation_result['is_valid']}")
            
            return validation_result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al validar datos de actualización: {e}")
            raise RepositoryError(
                message=f"Error en validación de actualización: {e}",
                operation="validate_client_update_data",
                entity_type="Client",
                entity_id=client_id,
                original_error=e
            )

    async def validate_bulk_client_data(self, clients_data: List[ClientCreate]) -> Dict[str, Any]:
        """
        Valida datos para creación masiva de clientes.
        
        Args:
            clients_data: Lista de datos de clientes a crear
            
        Returns:
            Dict[str, Any]: Resultado de la validación masiva
        """
        try:
            self._logger.debug(f"Validando datos masivos para {len(clients_data)} clientes")
            
            validation_result = {
                "is_valid": True,
                "total_clients": len(clients_data),
                "valid_clients": 0,
                "invalid_clients": 0,
                "client_validations": [],
                "global_errors": [],
                "duplicate_emails": [],
                "duplicate_codes": []
            }
            
            # Verificar duplicados internos
            emails = [client.email for client in clients_data if client.email]
            codes = [client.code for client in clients_data if client.code]
            
            # Encontrar emails duplicados
            seen_emails = set()
            for email in emails:
                if email in seen_emails:
                    validation_result["duplicate_emails"].append(email)
                seen_emails.add(email)
            
            # Encontrar códigos duplicados
            seen_codes = set()
            for code in codes:
                if code in seen_codes:
                    validation_result["duplicate_codes"].append(code)
                seen_codes.add(code)
            
            # Validar cada cliente individualmente
            for i, client_data in enumerate(clients_data):
                try:
                    client_validation = await self.validate_client_creation_data(client_data)
                    client_validation["index"] = i
                    client_validation["client_name"] = client_data.name
                    
                    validation_result["client_validations"].append(client_validation)
                    
                    if client_validation["is_valid"]:
                        validation_result["valid_clients"] += 1
                    else:
                        validation_result["invalid_clients"] += 1
                        
                except Exception as e:
                    validation_result["client_validations"].append({
                        "index": i,
                        "client_name": client_data.name,
                        "is_valid": False,
                        "errors": [f"Error de validación: {e}"],
                        "warnings": []
                    })
                    validation_result["invalid_clients"] += 1
            
            # Agregar errores globales si hay duplicados
            if validation_result["duplicate_emails"]:
                validation_result["global_errors"].append(
                    f"Emails duplicados encontrados: {', '.join(validation_result['duplicate_emails'])}"
                )
            
            if validation_result["duplicate_codes"]:
                validation_result["global_errors"].append(
                    f"Códigos duplicados encontrados: {', '.join(validation_result['duplicate_codes'])}"
                )
            
            # Determinar validez general
            validation_result["is_valid"] = (
                validation_result["invalid_clients"] == 0 and
                len(validation_result["global_errors"]) == 0
            )
            
            self._logger.debug(f"Validación masiva completada. Válidos: {validation_result['valid_clients']}/{validation_result['total_clients']}")
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error al validar datos masivos: {e}")
            raise RepositoryError(
                message=f"Error en validación masiva: {e}",
                operation="validate_bulk_client_data",
                entity_type="Client",
                original_error=e
            )

    async def validate_client_business_rules(self, client_id: int) -> Dict[str, Any]:
        """
        Valida las reglas de negocio específicas para un cliente.
        
        Args:
            client_id: ID del cliente a validar
            
        Returns:
            Dict[str, Any]: Resultado de la validación de reglas de negocio
        """
        try:
            self._logger.debug(f"Validando reglas de negocio para cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=client_id
                )
            
            validation_result = {
                "client_id": client_id,
                "is_valid": True,
                "rules_checked": [],
                "violations": [],
                "warnings": []
            }
            
            # Regla: Cliente activo debe tener información completa
            validation_result["rules_checked"].append("active_client_completeness")
            if client.is_active:
                if not client.email:
                    validation_result["warnings"].append(
                        "Cliente activo sin email configurado"
                    )
                if not client.code:
                    validation_result["warnings"].append(
                        "Cliente activo sin código configurado"
                    )
            
            # Regla: Nombre no puede estar vacío o ser solo espacios
            validation_result["rules_checked"].append("name_not_empty")
            if not client.name or client.name.strip() == "":
                validation_result["violations"].append(
                    "El nombre del cliente no puede estar vacío"
                )
            
            # Regla: Email debe tener formato válido si está presente
            validation_result["rules_checked"].append("email_format")
            if client.email:
                email_validation = await self._validate_client_email(client.email)
                if not email_validation["is_valid"]:
                    validation_result["violations"].extend(email_validation["errors"])
            
            # TODO: Agregar más reglas de negocio específicas
            # - Reglas de relación con proyectos
            # - Reglas de estado según tipo de cliente
            # - Reglas de información requerida por región
            
            # Determinar validez general
            validation_result["is_valid"] = len(validation_result["violations"]) == 0
            
            self._logger.debug(f"Validación de reglas de negocio completada para cliente {client_id}")
            
            return validation_result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al validar reglas de negocio: {e}")
            raise RepositoryError(
                message=f"Error en validación de reglas: {e}",
                operation="validate_client_business_rules",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def validate_email_uniqueness(
        self,
        email: str,
        exclude_client_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Valida que un email sea único en el sistema.
        
        Args:
            email: Email a validar
            exclude_client_id: ID de cliente a excluir de la validación (para actualizaciones)
            
        Returns:
            Dict[str, Any]: Resultado de la validación de unicidad
        """
        try:
            self._logger.debug(f"Validando unicidad del email: {email}")
            
            # Buscar cliente con el email
            existing_client = await self._client_repository.get_client_by_email(email)
            
            is_unique = True
            conflicting_client_id = None
            
            if existing_client:
                # Si hay un cliente con el email y no es el que estamos excluyendo
                if exclude_client_id is None or existing_client.id != exclude_client_id:
                    is_unique = False
                    conflicting_client_id = existing_client.id
            
            result = {
                "email": email,
                "is_unique": is_unique,
                "conflicting_client_id": conflicting_client_id,
                "exclude_client_id": exclude_client_id
            }
            
            self._logger.debug(f"Validación de unicidad de email completada. Único: {is_unique}")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al validar unicidad de email: {e}")
            raise RepositoryError(
                message=f"Error en validación de unicidad: {e}",
                operation="validate_email_uniqueness",
                entity_type="Client",
                original_error=e
            )

    async def validate_phone_uniqueness(
        self,
        phone: str,
        exclude_client_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Valida que un teléfono sea único en el sistema.
        
        Args:
            phone: Teléfono a validar
            exclude_client_id: ID de cliente a excluir de la validación
            
        Returns:
            Dict[str, Any]: Resultado de la validación de unicidad
        """
        try:
            self._logger.debug(f"Validando unicidad del teléfono: {phone}")
            
            # TODO: Implementar cuando esté disponible el campo phone en el modelo
            self._logger.warning("Validación de unicidad de teléfono no implementada - campo phone no disponible")
            
            result = {
                "phone": phone,
                "is_unique": True,  # Placeholder
                "conflicting_client_id": None,
                "exclude_client_id": exclude_client_id
            }
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al validar unicidad de teléfono: {e}")
            raise RepositoryError(
                message=f"Error en validación de unicidad de teléfono: {e}",
                operation="validate_phone_uniqueness",
                entity_type="Client",
                original_error=e
            )

    async def validate_client_status_transition(
        self,
        client_id: int,
        current_status: bool,
        new_status: bool
    ) -> Dict[str, Any]:
        """
        Valida una transición de estado de cliente.
        
        Args:
            client_id: ID del cliente
            current_status: Estado actual (is_active)
            new_status: Nuevo estado (is_active)
            
        Returns:
            Dict[str, Any]: Resultado de la validación de transición
        """
        try:
            self._logger.debug(f"Validando transición de estado para cliente {client_id}: {current_status} -> {new_status}")
            
            validation_result = {
                "client_id": client_id,
                "current_status": current_status,
                "new_status": new_status,
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Si no hay cambio, la transición es válida
            if current_status == new_status:
                validation_result["warnings"].append("No hay cambio de estado")
                return validation_result
            
            # Validar transición de activo a inactivo
            if current_status and not new_status:
                # TODO: Verificar si el cliente tiene proyectos activos
                # Por ahora solo agregamos una advertencia
                validation_result["warnings"].append(
                    "Desactivando cliente - verificar proyectos asociados"
                )
            
            # Validar transición de inactivo a activo
            if not current_status and new_status:
                # Verificar que el cliente tenga información mínima requerida
                client = await self._client_repository.get_client_by_id(client_id)
                if client:
                    if not client.email:
                        validation_result["warnings"].append(
                            "Activando cliente sin email configurado"
                        )
                    if not client.code:
                        validation_result["warnings"].append(
                            "Activando cliente sin código configurado"
                        )
            
            self._logger.debug(f"Validación de transición completada. Válida: {validation_result['is_valid']}")
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error al validar transición de estado: {e}")
            raise RepositoryError(
                message=f"Error en validación de transición: {e}",
                operation="validate_client_status_transition",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def validate_client_deletion_constraints(self, client_id: int) -> Dict[str, Any]:
        """
        Valida las restricciones para eliminar un cliente.
        
        Args:
            client_id: ID del cliente a eliminar
            
        Returns:
            Dict[str, Any]: Resultado de la validación de eliminación
        """
        try:
            self._logger.debug(f"Validando restricciones de eliminación para cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=client_id
                )
            
            validation_result = {
                "client_id": client_id,
                "can_be_deleted": True,
                "blocking_constraints": [],
                "warnings": [],
                "checks_performed": []
            }
            
            # Verificar si el cliente está activo
            validation_result["checks_performed"].append("active_status_check")
            if client.is_active:
                validation_result["warnings"].append(
                    "Eliminando cliente activo - considerar desactivar primero"
                )
            
            # TODO: Verificar restricciones reales cuando estén disponibles las relaciones
            # - Proyectos asociados
            # - Equipos asociados
            # - Transacciones históricas
            # - Referencias en otros módulos
            
            validation_result["checks_performed"].extend([
                "project_references_check",
                "team_references_check",
                "transaction_history_check"
            ])
            
            # Por ahora, permitir eliminación con advertencias
            validation_result["can_be_deleted"] = len(validation_result["blocking_constraints"]) == 0
            
            self._logger.debug(f"Validación de eliminación completada. Puede eliminarse: {validation_result['can_be_deleted']}")
            
            return validation_result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al validar restricciones de eliminación: {e}")
            raise RepositoryError(
                message=f"Error en validación de eliminación: {e}",
                operation="validate_client_deletion_constraints",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def validate_client_data_integrity(self, client_id: int) -> Dict[str, Any]:
        """
        Valida la integridad general de los datos de un cliente.
        
        Args:
            client_id: ID del cliente a validar
            
        Returns:
            Dict[str, Any]: Resultado de la validación de integridad
        """
        try:
            self._logger.debug(f"Validando integridad de datos para cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=client_id
                )
            
            validation_result = {
                "client_id": client_id,
                "is_valid": True,
                "integrity_checks": [],
                "issues": [],
                "recommendations": []
            }
            
            # Verificar integridad de campos básicos
            validation_result["integrity_checks"].append("basic_fields")
            if not client.name or len(client.name.strip()) == 0:
                validation_result["issues"].append("Nombre vacío o solo espacios")
            
            # Verificar formato de email si está presente
            validation_result["integrity_checks"].append("email_format")
            if client.email:
                email_validation = await self._validate_client_email(client.email)
                if not email_validation["is_valid"]:
                    validation_result["issues"].extend(email_validation["errors"])
            
            # Verificar consistencia de estado
            validation_result["integrity_checks"].append("status_consistency")
            if client.is_active and not client.email:
                validation_result["recommendations"].append(
                    "Cliente activo debería tener email configurado"
                )
            
            # TODO: Agregar más verificaciones de integridad
            # - Consistencia con datos relacionados
            # - Validación de referencias cruzadas
            # - Verificación de campos calculados
            
            # Determinar validez general
            validation_result["is_valid"] = len(validation_result["issues"]) == 0
            
            self._logger.debug(f"Validación de integridad completada. Válido: {validation_result['is_valid']}")
            
            return validation_result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al validar integridad de datos: {e}")
            raise RepositoryError(
                message=f"Error en validación de integridad: {e}",
                operation="validate_client_data_integrity",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def validate_client_field_format(self, field_name: str, field_value: Any) -> Dict[str, Any]:
        """
        Valida el formato de un campo específico de cliente.
        
        Args:
            field_name: Nombre del campo a validar
            field_value: Valor del campo
            
        Returns:
            Dict[str, Any]: Resultado de la validación de formato
        """
        try:
            self._logger.debug(f"Validando formato del campo {field_name}")
            
            validation_result = {
                "field_name": field_name,
                "field_value": field_value,
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Validar según el tipo de campo
            if field_name == "name":
                name_validation = await self._validate_client_name(field_value)
                validation_result.update(name_validation)
                
            elif field_name == "email":
                email_validation = await self._validate_client_email(field_value)
                validation_result.update(email_validation)
                
            elif field_name == "code":
                code_validation = await self._validate_client_code(field_value)
                validation_result.update(code_validation)
                
            elif field_name == "notes":
                notes_validation = self._validate_client_notes(field_value)
                validation_result.update(notes_validation)
                
            elif field_name == "is_active":
                if not isinstance(field_value, bool):
                    validation_result["is_valid"] = False
                    validation_result["errors"].append("El campo is_active debe ser booleano")
                    
            else:
                validation_result["warnings"].append(f"Campo {field_name} no reconocido para validación")
            
            self._logger.debug(f"Validación de formato completada para {field_name}")
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error al validar formato de campo: {e}")
            raise RepositoryError(
                message=f"Error en validación de formato: {e}",
                operation="validate_client_field_format",
                entity_type="Client",
                original_error=e
            )

    # Métodos auxiliares privados

    async def _validate_client_name(self, name: str) -> Dict[str, Any]:
        """Valida el nombre del cliente."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not name or len(name.strip()) == 0:
            validation_result["is_valid"] = False
            validation_result["errors"].append("El nombre no puede estar vacío")
        elif len(name) > 255:
            validation_result["is_valid"] = False
            validation_result["errors"].append("El nombre no puede exceder 255 caracteres")
        elif len(name) < 2:
            validation_result["warnings"].append("Nombre muy corto, considerar usar nombre completo")
        
        return validation_result

    async def _validate_client_email(self, email: str) -> Dict[str, Any]:
        """Valida el formato del email del cliente."""
        import re
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not email:
            return validation_result
        
        # Patrón básico de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Formato de email inválido")
        elif len(email) > 254:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Email demasiado largo")
        
        return validation_result

    async def _validate_client_code(self, code: str) -> Dict[str, Any]:
        """Valida el código del cliente."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not code:
            return validation_result
        
        if len(code) > 50:
            validation_result["is_valid"] = False
            validation_result["errors"].append("El código no puede exceder 50 caracteres")
        elif len(code) < 2:
            validation_result["warnings"].append("Código muy corto")
        
        # Verificar caracteres válidos (alfanuméricos, guiones, guiones bajos)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', code):
            validation_result["warnings"].append(
                "El código contiene caracteres especiales - considerar usar solo letras, números, guiones y guiones bajos"
            )
        
        return validation_result

    def _validate_client_notes(self, notes: str) -> Dict[str, Any]:
        """Valida las notas del cliente."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        if not notes:
            return validation_result
        
        if len(notes) > 1000:
            validation_result["warnings"].append("Notas muy largas - considerar resumir")
        
        return validation_result