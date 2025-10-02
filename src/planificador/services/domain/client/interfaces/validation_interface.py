# -*- coding: utf-8 -*-
"""
Validation Operations Interface for Client Domain Service

Define las operaciones de validación y verificación para la entidad Client
con reglas de negocio y validaciones de integridad.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from uuid import UUID

from planificador.schemas.client import ClientCreate, ClientUpdate


class IValidationOperations(ABC):
    """
    Interfaz para operaciones de validación del dominio Client.
    
    Define métodos para validar datos, reglas de negocio
    e integridad de la información de clientes.
    """

    @abstractmethod
    async def validate_client_data(
        self,
        client_data: ClientCreate,
        check_duplicates: bool = True
    ) -> Dict[str, Any]:
        """
        Valida los datos de un cliente antes de la creación.
        
        Args:
            client_data: Datos del cliente a validar
            check_duplicates: Si verificar duplicados
            
        Returns:
            Dict[str, Any]: Resultado de la validación con detalles
        """
        pass

    @abstractmethod
    async def validate_client_update_data(
        self,
        client_id: UUID,
        update_data: ClientUpdate,
        check_conflicts: bool = True
    ) -> Dict[str, Any]:
        """
        Valida los datos de actualización de un cliente.
        
        Args:
            client_id: ID del cliente a actualizar
            update_data: Datos de actualización
            check_conflicts: Si verificar conflictos
            
        Returns:
            Dict[str, Any]: Resultado de la validación con detalles
        """
        pass

    @abstractmethod
    async def validate_client_business_rules(
        self,
        client_id: UUID,
        rules_to_check: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Valida las reglas de negocio de un cliente.
        
        Args:
            client_id: ID del cliente a validar
            rules_to_check: Lista específica de reglas (None = todas)
            
        Returns:
            Dict[str, Any]: Resultado de la validación de reglas de negocio
        """
        pass

    @abstractmethod
    async def check_client_email_uniqueness(
        self,
        email: str,
        exclude_client_id: Optional[UUID] = None
    ) -> bool:
        """
        Verifica la unicidad del email de un cliente.
        
        Args:
            email: Email a verificar
            exclude_client_id: ID del cliente a excluir de la verificación
            
        Returns:
            bool: True si el email es único
        """
        pass

    @abstractmethod
    async def check_client_phone_uniqueness(
        self,
        phone: str,
        exclude_client_id: Optional[UUID] = None
    ) -> bool:
        """
        Verifica la unicidad del teléfono de un cliente.
        
        Args:
            phone: Teléfono a verificar
            exclude_client_id: ID del cliente a excluir de la verificación
            
        Returns:
            bool: True si el teléfono es único
        """
        pass

    @abstractmethod
    async def validate_client_status_transition(
        self,
        client_id: UUID,
        new_status: str,
        current_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Valida la transición de estado de un cliente.
        
        Args:
            client_id: ID del cliente
            new_status: Nuevo estado propuesto
            current_status: Estado actual (None = obtener automáticamente)
            
        Returns:
            Dict[str, Any]: Resultado de la validación de transición
        """
        pass

    @abstractmethod
    async def validate_client_deletion_constraints(
        self,
        client_id: UUID
    ) -> Dict[str, Any]:
        """
        Valida las restricciones para eliminar un cliente.
        
        Args:
            client_id: ID del cliente a eliminar
            
        Returns:
            Dict[str, Any]: Resultado de la validación de eliminación
        """
        pass

    @abstractmethod
    async def validate_client_data_integrity(
        self,
        client_id: UUID,
        deep_check: bool = False
    ) -> Dict[str, Any]:
        """
        Valida la integridad de los datos de un cliente.
        
        Args:
            client_id: ID del cliente a validar
            deep_check: Si realizar verificación profunda
            
        Returns:
            Dict[str, Any]: Resultado de la validación de integridad
        """
        pass

    @abstractmethod
    async def validate_bulk_client_data(
        self,
        clients_data: List[ClientCreate],
        check_cross_duplicates: bool = True
    ) -> Dict[str, Any]:
        """
        Valida datos de múltiples clientes para creación en lote.
        
        Args:
            clients_data: Lista de datos de clientes
            check_cross_duplicates: Si verificar duplicados entre los datos
            
        Returns:
            Dict[str, Any]: Resultado de la validación en lote
        """
        pass

    @abstractmethod
    async def validate_client_field_format(
        self,
        field_name: str,
        field_value: Any,
        validation_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Valida el formato de un campo específico del cliente.
        
        Args:
            field_name: Nombre del campo a validar
            field_value: Valor del campo
            validation_rules: Reglas específicas de validación
            
        Returns:
            Dict[str, Any]: Resultado de la validación del campo
        """
        pass