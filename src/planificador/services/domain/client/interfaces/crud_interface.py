# -*- coding: utf-8 -*-
"""
CRUD Operations Interface for Client Domain Service

Define las operaciones básicas de creación, lectura, actualización y eliminación
para la entidad Client a nivel de dominio.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from planificador.schemas.client import ClientCreate, ClientUpdate, Client


class ICrudOperations(ABC):
    """
    Interfaz para operaciones CRUD del dominio Client.
    
    Define los métodos básicos para gestionar el ciclo de vida
    de los clientes con validaciones de negocio.
    """

    @abstractmethod
    async def create_client(
        self,
        client_data: ClientCreate,
        validate_business_rules: bool = True
    ) -> Client:
        """
        Crea un nuevo cliente con validaciones de dominio.
        
        Args:
            client_data: Datos del cliente a crear
            validate_business_rules: Si aplicar validaciones de negocio
            
        Returns:
            Client: Cliente creado con datos completos
            
        Raises:
            ValidationError: Si los datos no cumplen las reglas de negocio
            DuplicateError: Si ya existe un cliente con los mismos datos únicos
        """
        pass

    @abstractmethod
    async def get_client_by_id(
        self,
        client_id: UUID,
        include_relationships: bool = False
    ) -> Optional[Client]:
        """
        Obtiene un cliente por su ID.
        
        Args:
            client_id: ID único del cliente
            include_relationships: Si incluir relaciones del cliente
            
        Returns:
            Optional[Client]: Cliente encontrado o None
        """
        pass

    @abstractmethod
    async def update_client(
        self,
        client_id: UUID,
        client_data: ClientUpdate,
        validate_business_rules: bool = True
    ) -> Client:
        """
        Actualiza un cliente existente con validaciones de dominio.
        
        Args:
            client_id: ID del cliente a actualizar
            client_data: Datos de actualización
            validate_business_rules: Si aplicar validaciones de negocio
            
        Returns:
            Client: Cliente actualizado
            
        Raises:
            NotFoundError: Si el cliente no existe
            ValidationError: Si los datos no cumplen las reglas de negocio
        """
        pass

    @abstractmethod
    async def delete_client(
        self,
        client_id: UUID,
        soft_delete: bool = True
    ) -> bool:
        """
        Elimina un cliente (lógica o físicamente).
        
        Args:
            client_id: ID del cliente a eliminar
            soft_delete: Si realizar eliminación lógica
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            NotFoundError: Si el cliente no existe
            BusinessLogicError: Si el cliente tiene dependencias activas
        """
        pass

    @abstractmethod
    async def get_all_clients(
        self,
        include_inactive: bool = False,
        include_relationships: bool = False
    ) -> List[Client]:
        """
        Obtiene todos los clientes del sistema.
        
        Args:
            include_inactive: Si incluir clientes inactivos
            include_relationships: Si incluir relaciones
            
        Returns:
            List[Client]: Lista de todos los clientes
        """
        pass

    @abstractmethod
    async def bulk_create_clients(
        self,
        clients_data: List[ClientCreate],
        validate_business_rules: bool = True,
        skip_duplicates: bool = False
    ) -> List[Client]:
        """
        Crea múltiples clientes en una operación transaccional.
        
        Args:
            clients_data: Lista de datos de clientes a crear
            validate_business_rules: Si aplicar validaciones de negocio
            skip_duplicates: Si omitir duplicados en lugar de fallar
            
        Returns:
            List[Client]: Lista de clientes creados
            
        Raises:
            ValidationError: Si algún cliente no cumple las reglas
            TransactionError: Si falla la operación transaccional
        """
        pass

    @abstractmethod
    async def bulk_update_clients(
        self,
        updates: Dict[UUID, ClientUpdate],
        validate_business_rules: bool = True
    ) -> List[Client]:
        """
        Actualiza múltiples clientes en una operación transaccional.
        
        Args:
            updates: Diccionario con ID del cliente y datos de actualización
            validate_business_rules: Si aplicar validaciones de negocio
            
        Returns:
            List[Client]: Lista de clientes actualizados
            
        Raises:
            ValidationError: Si alguna actualización no cumple las reglas
            TransactionError: Si falla la operación transaccional
        """
        pass

    @abstractmethod
    async def get_by_unique_field(
        self,
        field_name: str,
        field_value: Any
    ) -> Optional[Client]:
        """
        Obtiene un cliente por un campo único específico.
        
        Args:
            field_name: Nombre del campo único
            field_value: Valor del campo único
            
        Returns:
            Optional[Client]: Cliente encontrado o None
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass