"""
Tests unitarios para las operaciones CRUD del ClientDomainService.

Este módulo contiene todas las pruebas unitarias para las operaciones CRUD
(Create, Read, Update, Delete) del servicio de dominio de clientes.

Operaciones probadas:
- create_client: Creación de un nuevo cliente
- get_client_by_id: Obtención de cliente por ID
- update_client: Actualización de cliente existente
- delete_client: Eliminación de cliente
- bulk_create_clients: Creación en lote de clientes
"""

import pytest
from typing import List

from planificador.services.domain.client.client_domain_service import ClientDomainService
from planificador.schemas.client import ClientCreate, ClientUpdate, Client
from planificador.exceptions import RepositoryError, ValidationError, BusinessLogicError


class TestClientDomainServiceCrud:
    """
    Clase de tests para las operaciones CRUD del ClientDomainService.
    
    Agrupa todos los tests relacionados con operaciones básicas de
    creación, lectura, actualización y eliminación de clientes.
    """

    # ==================== TESTS CREATE_CLIENT ====================

    @pytest.mark.asyncio
    async def test_create_client_success(
        self,
        client_domain_service: ClientDomainService,
        sample_client_create_data: ClientCreate,
        sample_client_response: Client
    ):
        """
        Test: Creación exitosa de un cliente.
        
        Verifica que el método create_client delegue correctamente
        al módulo CRUD y retorne el cliente creado.
        """
        # Arrange
        client_domain_service.crud.create_client.return_value = sample_client_response
        
        # Act
        result = await client_domain_service.create_client(sample_client_create_data)
        
        # Assert
        assert result == sample_client_response
        client_domain_service.crud.create_client.assert_called_once_with(sample_client_create_data)

    @pytest.mark.asyncio
    async def test_create_client_validation_error(
        self,
        client_domain_service: ClientDomainService,
        sample_client_create_data: ClientCreate
    ):
        """
        Test: Error de validación al crear cliente.
        
        Verifica que se propague correctamente un error de validación
        desde el módulo CRUD.
        """
        # Arrange
        validation_error = ValidationError(
            message="Email ya existe",
            field="email",
            value=sample_client_create_data.email
        )
        client_domain_service.crud.create_client.side_effect = validation_error
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await client_domain_service.create_client(sample_client_create_data)
        
        assert exc_info.value.message == "Email ya existe"
        assert exc_info.value.field == "email"

    @pytest.mark.asyncio
    async def test_create_client_repository_error(
        self,
        client_domain_service: ClientDomainService,
        sample_client_create_data: ClientCreate
    ):
        """
        Test: Error de repositorio al crear cliente.
        
        Verifica que se propague correctamente un error de repositorio
        desde el módulo CRUD.
        """
        # Arrange
        repository_error = RepositoryError(
            message="Error de base de datos",
            operation="create_client",
            entity_type="Client"
        )
        client_domain_service.crud.create_client.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.create_client(sample_client_create_data)
        
        assert exc_info.value.message == "Error de base de datos"
        assert exc_info.value.operation == "create_client"
        client_domain_service.crud.create_client.assert_called_once_with(sample_client_create_data)

    # ==================== TESTS GET_CLIENT_BY_ID ====================

    @pytest.mark.asyncio
    async def test_get_client_by_id_success(
        self,
        client_domain_service: ClientDomainService,
        sample_client_id: int,
        sample_client_response: Client
    ):
        """
        Test: Obtención exitosa de cliente por ID.
        
        Verifica que el método get_client_by_id delegue correctamente
        al módulo CRUD y retorne el cliente encontrado.
        """
        # Arrange
        client_domain_service.crud.get_client_by_id.return_value = sample_client_response
        
        # Act
        result = await client_domain_service.get_client_by_id(sample_client_id)
        
        # Assert
        assert result == sample_client_response
        client_domain_service.crud.get_client_by_id.assert_called_once_with(sample_client_id)

    @pytest.mark.asyncio
    async def test_get_client_by_id_not_found(
        self,
        client_domain_service: ClientDomainService,
        sample_client_id: int
    ):
        """
        Test: Cliente no encontrado por ID.
        
        Verifica que se retorne None cuando el cliente no existe.
        """
        # Arrange
        client_domain_service.crud.get_client_by_id.return_value = None
        
        # Act
        result = await client_domain_service.get_client_by_id(sample_client_id)
        
        # Assert
        assert result is None
        client_domain_service.crud.get_client_by_id.assert_called_once_with(sample_client_id)

    @pytest.mark.asyncio
    async def test_get_client_by_id_repository_error(
        self,
        client_domain_service: ClientDomainService,
        sample_client_id: int
    ):
        """
        Test: Error de repositorio al obtener cliente por ID.
        
        Verifica que se propague correctamente un error de repositorio
        desde el módulo CRUD.
        """
        # Arrange
        repository_error = RepositoryError(
            message="Error de conexión a base de datos",
            operation="get_client_by_id",
            entity_type="Client",
            entity_id=sample_client_id
        )
        client_domain_service.crud.get_client_by_id.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.get_client_by_id(sample_client_id)
        
        assert exc_info.value.message == "Error de conexión a base de datos"
        assert exc_info.value.operation == "get_client_by_id"
        assert exc_info.value.entity_id == sample_client_id
        client_domain_service.crud.get_client_by_id.assert_called_once_with(sample_client_id)

    # ==================== TESTS UPDATE_CLIENT ====================

    @pytest.mark.asyncio
    async def test_update_client_success(
        self,
        client_domain_service: ClientDomainService,
        sample_client_id: int,
        sample_client_update_data: ClientUpdate,
        sample_client_response: Client
    ):
        """
        Test: Actualización exitosa de cliente.
        
        Verifica que el método update_client delegue correctamente
        al módulo CRUD y retorne el cliente actualizado.
        """
        # Arrange
        client_domain_service.crud.update_client.return_value = sample_client_response
        
        # Act
        result = await client_domain_service.update_client(sample_client_id, sample_client_update_data)
        
        # Assert
        assert result == sample_client_response
        client_domain_service.crud.update_client.assert_called_once_with(
            sample_client_id, sample_client_update_data
        )

    @pytest.mark.asyncio
    async def test_update_client_not_found(
        self,
        client_domain_service: ClientDomainService,
        sample_client_id: int,
        sample_client_update_data: ClientUpdate
    ):
        """
        Test: Cliente no encontrado para actualización.
        
        Verifica que se retorne None cuando el cliente a actualizar no existe.
        """
        # Arrange
        client_domain_service.crud.update_client.return_value = None
        
        # Act
        result = await client_domain_service.update_client(sample_client_id, sample_client_update_data)
        
        # Assert
        assert result is None
        client_domain_service.crud.update_client.assert_called_once_with(
            sample_client_id, sample_client_update_data
        )

    @pytest.mark.asyncio
    async def test_update_client_validation_error(
        self,
        client_domain_service: ClientDomainService,
        sample_client_id: int,
        sample_client_update_data: ClientUpdate
    ):
        """
        Test: Error de validación al actualizar cliente.
        
        Verifica que se propague correctamente un error de validación
        desde el módulo CRUD.
        """
        # Arrange
        validation_error = ValidationError(
            message="Email ya está en uso por otro cliente",
            field="email",
            value=sample_client_update_data.email
        )
        client_domain_service.crud.update_client.side_effect = validation_error
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await client_domain_service.update_client(sample_client_id, sample_client_update_data)
        
        assert exc_info.value.message == "Email ya está en uso por otro cliente"
        assert exc_info.value.field == "email"

    # ==================== TESTS DELETE_CLIENT ====================

    @pytest.mark.asyncio
    async def test_delete_client_success(
        self,
        client_domain_service: ClientDomainService,
        sample_client_id: int
    ):
        """
        Test: Eliminación exitosa de cliente.
        
        Verifica que el método delete_client delegue correctamente
        al módulo CRUD y retorne True cuando la eliminación es exitosa.
        """
        # Arrange
        client_domain_service.crud.delete_client.return_value = True
        
        # Act
        result = await client_domain_service.delete_client(sample_client_id)
        
        # Assert
        assert result is True
        client_domain_service.crud.delete_client.assert_called_once_with(sample_client_id)

    @pytest.mark.asyncio
    async def test_delete_client_not_found(
        self,
        client_domain_service: ClientDomainService,
        sample_client_id: int
    ):
        """
        Test: Cliente no encontrado para eliminación.
        
        Verifica que se retorne False cuando el cliente a eliminar no existe.
        """
        # Arrange
        client_domain_service.crud.delete_client.return_value = False
        
        # Act
        result = await client_domain_service.delete_client(sample_client_id)
        
        # Assert
        assert result is False
        client_domain_service.crud.delete_client.assert_called_once_with(sample_client_id)

    @pytest.mark.asyncio
    async def test_delete_client_business_logic_error(
        self,
        client_domain_service: ClientDomainService,
        sample_client_id: int
    ):
        """
        Test: Error de lógica de negocio al eliminar cliente.
        
        Verifica que se propague correctamente un error de lógica de negocio
        cuando el cliente tiene proyectos asociados.
        """
        # Arrange
        business_error = BusinessLogicError(
            message="No se puede eliminar cliente con proyectos activos"
        )
        business_error.add_detail("operation", "delete_client")
        business_error.add_detail("entity_type", "Client")
        business_error.add_detail("entity_id", sample_client_id)
        client_domain_service.crud.delete_client.side_effect = business_error
        
        # Act & Assert
        with pytest.raises(BusinessLogicError) as exc_info:
            await client_domain_service.delete_client(sample_client_id)
        
        assert exc_info.value.message == "No se puede eliminar cliente con proyectos activos"
        assert exc_info.value.details["operation"] == "delete_client"
        assert exc_info.value.details["entity_id"] == sample_client_id
        client_domain_service.crud.delete_client.assert_called_once_with(sample_client_id)

    # ==================== TESTS BULK_CREATE_CLIENTS ====================

    @pytest.mark.asyncio
    async def test_bulk_create_clients_success(
        self,
        client_domain_service: ClientDomainService,
        bulk_client_create_data: List[ClientCreate],
        bulk_client_response_data: List[Client]
    ):
        """
        Test: Creación en lote exitosa de clientes.
        
        Verifica que el método bulk_create_clients delegue correctamente
        al módulo CRUD y retorne la lista de clientes creados.
        """
        # Arrange
        client_domain_service.crud.bulk_create_clients.return_value = bulk_client_response_data
        
        # Act
        result = await client_domain_service.bulk_create_clients(bulk_client_create_data)
        
        # Assert
        assert result == bulk_client_response_data
        assert len(result) == len(bulk_client_create_data)
        client_domain_service.crud.bulk_create_clients.assert_called_once_with(bulk_client_create_data)

    @pytest.mark.asyncio
    async def test_bulk_create_clients_empty_list(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Creación en lote con lista vacía.
        
        Verifica que se maneje correctamente una lista vacía de clientes.
        """
        # Arrange
        empty_list: List[ClientCreate] = []
        client_domain_service.crud.bulk_create_clients.return_value = []
        
        # Act
        result = await client_domain_service.bulk_create_clients(empty_list)
        
        # Assert
        assert result == []
        client_domain_service.crud.bulk_create_clients.assert_called_once_with(empty_list)

    @pytest.mark.asyncio
    async def test_bulk_create_clients_partial_failure(
        self,
        client_domain_service: ClientDomainService,
        bulk_client_create_data: List[ClientCreate]
    ):
        """
        Test: Fallo parcial en creación en lote.
        
        Verifica que se propague correctamente un error cuando
        algunos clientes no pueden ser creados.
        """
        # Arrange
        validation_error = ValidationError(
            message="Uno o más clientes tienen datos inválidos",
            field="bulk_validation",
            value="multiple_clients"
        )
        client_domain_service.crud.bulk_create_clients.side_effect = validation_error
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await client_domain_service.bulk_create_clients(bulk_client_create_data)
        
        assert exc_info.value.message == "Uno o más clientes tienen datos inválidos"
        assert exc_info.value.field == "bulk_validation"

    @pytest.mark.asyncio
    async def test_bulk_create_clients_repository_error(
        self,
        client_domain_service: ClientDomainService,
        bulk_client_create_data: List[ClientCreate]
    ):
        """
        Test: Error de repositorio en creación en lote.
        
        Verifica que se propague correctamente un error de repositorio
        durante la creación en lote.
        """
        # Arrange
        repository_error = RepositoryError(
            message="Error de transacción en base de datos",
            operation="bulk_create_clients",
            entity_type="Client"
        )
        client_domain_service.crud.bulk_create_clients.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.bulk_create_clients(bulk_client_create_data)
        
        assert exc_info.value.message == "Error de transacción en base de datos"
        assert exc_info.value.operation == "bulk_create_clients"
        client_domain_service.crud.bulk_create_clients.assert_called_once_with(bulk_client_create_data)

    # ==================== TESTS DE INTEGRACIÓN CRUD ====================

    @pytest.mark.asyncio
    async def test_crud_operations_integration(
        self,
        client_domain_service: ClientDomainService,
        sample_client_create_data: ClientCreate,
        sample_client_update_data: ClientUpdate,
        sample_client_response: Client,
        sample_client_id: int
    ):
        """
        Test: Integración de operaciones CRUD.
        
        Verifica que las operaciones CRUD funcionen correctamente
        en secuencia: crear, leer, actualizar, eliminar.
        """
        # Arrange
        updated_client = Client(
            id=sample_client_id,
            name=sample_client_update_data.name,
            code=sample_client_response.code,
            contact_person=sample_client_update_data.contact_person,
            email=sample_client_update_data.email,
            phone=sample_client_response.phone,
            is_active=sample_client_update_data.is_active,
            notes=sample_client_update_data.notes,
            created_at=sample_client_response.created_at,
            updated_at="2024-01-01T11:00:00"
        )
        
        # Configurar mocks para la secuencia
        client_domain_service.crud.create_client.return_value = sample_client_response
        client_domain_service.crud.get_client_by_id.return_value = sample_client_response
        client_domain_service.crud.update_client.return_value = updated_client
        client_domain_service.crud.delete_client.return_value = True
        
        # Act & Assert - Crear
        created_client = await client_domain_service.create_client(sample_client_create_data)
        assert created_client == sample_client_response
        
        # Act & Assert - Leer
        found_client = await client_domain_service.get_client_by_id(sample_client_id)
        assert found_client == sample_client_response
        
        # Act & Assert - Actualizar
        updated_result = await client_domain_service.update_client(sample_client_id, sample_client_update_data)
        assert updated_result == updated_client
        assert updated_result.name == sample_client_update_data.name
        
        # Act & Assert - Eliminar
        deleted = await client_domain_service.delete_client(sample_client_id)
        assert deleted is True
        
        # Verificar que todos los métodos fueron llamados
        client_domain_service.crud.create_client.assert_called_once()
        client_domain_service.crud.get_client_by_id.assert_called_once()
        client_domain_service.crud.update_client.assert_called_once()
        client_domain_service.crud.delete_client.assert_called_once()