"""
Tests unitarios para las operaciones de consulta del ClientDomainService.

Este módulo contiene todas las pruebas unitarias para las operaciones de consulta
del servicio de dominio de clientes.

Operaciones probadas:
- get_client_by_name: Obtención de cliente por nombre
- get_client_by_email: Obtención de cliente por email
- get_client_by_code: Obtención de cliente por código
- get_clients_by_status: Obtención de clientes por estado
- get_active_clients: Obtención de clientes activos
- get_inactive_clients: Obtención de clientes inactivos
- search_clients_basic: Búsqueda básica de clientes
- client_exists: Verificación de existencia de cliente
"""

import pytest
from typing import List

from planificador.services.domain.client.client_domain_service import ClientDomainService
from planificador.schemas.client import Client
from planificador.exceptions import RepositoryError


class TestClientDomainServiceQuery:
    """
    Clase de tests para las operaciones de consulta del ClientDomainService.
    
    Agrupa todos los tests relacionados con operaciones de consulta
    y búsqueda de clientes.
    """

    # ==================== TESTS GET_CLIENT_BY_NAME ====================

    @pytest.mark.asyncio
    async def test_get_client_by_name_success(
        self,
        client_domain_service: ClientDomainService,
        sample_client_response: Client
    ):
        """
        Test: Obtención exitosa de cliente por nombre.
        
        Verifica que el método get_client_by_name delegue correctamente
        al módulo query y retorne el cliente encontrado.
        """
        # Arrange
        client_name = sample_client_response.name
        client_domain_service.query.get_client_by_name.return_value = sample_client_response
        
        # Act
        result = await client_domain_service.get_client_by_name(client_name)
        
        # Assert
        assert result == sample_client_response
        assert result.name == client_name
        client_domain_service.query.get_client_by_name.assert_called_once_with(client_name)

    @pytest.mark.asyncio
    async def test_get_client_by_name_not_found(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Cliente no encontrado por nombre.
        
        Verifica que se retorne None cuando el cliente no existe.
        """
        # Arrange
        client_name = "Cliente Inexistente"
        client_domain_service.query.get_client_by_name.return_value = None
        
        # Act
        result = await client_domain_service.get_client_by_name(client_name)
        
        # Assert
        assert result is None
        client_domain_service.query.get_client_by_name.assert_called_once_with(client_name)

    @pytest.mark.asyncio
    async def test_get_client_by_name_repository_error(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Error de repositorio al obtener cliente por nombre.
        
        Verifica que se propague correctamente un error de repositorio
        desde el módulo query.
        """
        # Arrange
        client_name = "Test Client"
        repository_error = RepositoryError(
            message="Error de conexión a base de datos",
            operation="get_client_by_name",
            entity_type="Client"
        )
        client_domain_service.query.get_client_by_name.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.get_client_by_name(client_name)
        
        assert exc_info.value.message == "Error de conexión a base de datos"
        assert exc_info.value.operation == "get_client_by_name"
        client_domain_service.query.get_client_by_name.assert_called_once_with(client_name)

    # ==================== TESTS GET_CLIENT_BY_EMAIL ====================

    @pytest.mark.asyncio
    async def test_get_client_by_email_success(
        self,
        client_domain_service: ClientDomainService,
        sample_client_response: Client
    ):
        """
        Test: Obtención exitosa de cliente por email.
        
        Verifica que el método get_client_by_email delegue correctamente
        al módulo query y retorne el cliente encontrado.
        """
        # Arrange
        client_email = sample_client_response.email
        client_domain_service.query.get_client_by_email.return_value = sample_client_response
        
        # Act
        result = await client_domain_service.get_client_by_email(client_email)
        
        # Assert
        assert result == sample_client_response
        assert result.email == client_email
        client_domain_service.query.get_client_by_email.assert_called_once_with(client_email)

    @pytest.mark.asyncio
    async def test_get_client_by_email_not_found(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Cliente no encontrado por email.
        
        Verifica que se retorne None cuando el cliente no existe.
        """
        # Arrange
        client_email = "inexistente@example.com"
        client_domain_service.query.get_client_by_email.return_value = None
        
        # Act
        result = await client_domain_service.get_client_by_email(client_email)
        
        # Assert
        assert result is None
        client_domain_service.query.get_client_by_email.assert_called_once_with(client_email)

    @pytest.mark.asyncio
    async def test_get_client_by_email_repository_error(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Error de repositorio al obtener cliente por email.
        
        Verifica que se propague correctamente un error de repositorio
        desde el módulo query.
        """
        # Arrange
        client_email = "test@example.com"
        repository_error = RepositoryError(
            message="Error de consulta en base de datos",
            operation="get_client_by_email",
            entity_type="Client"
        )
        client_domain_service.query.get_client_by_email.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.get_client_by_email(client_email)
        
        assert exc_info.value.message == "Error de consulta en base de datos"
        assert exc_info.value.operation == "get_client_by_email"
        client_domain_service.query.get_client_by_email.assert_called_once_with(client_email)

    # ==================== TESTS GET_CLIENT_BY_CODE ====================

    @pytest.mark.asyncio
    async def test_get_client_by_code_success(
        self,
        client_domain_service: ClientDomainService,
        sample_client_response: Client
    ):
        """
        Test: Obtención exitosa de cliente por código.
        
        Verifica que el método get_client_by_code delegue correctamente
        al módulo query y retorne el cliente encontrado.
        """
        # Arrange
        client_code = sample_client_response.code
        client_domain_service.query.get_client_by_code.return_value = sample_client_response
        
        # Act
        result = await client_domain_service.get_client_by_code(client_code)
        
        # Assert
        assert result == sample_client_response
        assert result.code == client_code
        client_domain_service.query.get_client_by_code.assert_called_once_with(client_code)

    @pytest.mark.asyncio
    async def test_get_client_by_code_not_found(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Cliente no encontrado por código.
        
        Verifica que se retorne None cuando el cliente no existe.
        """
        # Arrange
        client_code = "INEXISTENTE"
        client_domain_service.query.get_client_by_code.return_value = None
        
        # Act
        result = await client_domain_service.get_client_by_code(client_code)
        
        # Assert
        assert result is None
        client_domain_service.query.get_client_by_code.assert_called_once_with(client_code)

    @pytest.mark.asyncio
    async def test_get_client_by_code_repository_error(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Error de repositorio al obtener cliente por código.
        
        Verifica que se propague correctamente un error de repositorio
        desde el módulo query.
        """
        # Arrange
        client_code = "TEST001"
        repository_error = RepositoryError(
            message="Error de índice en base de datos",
            operation="get_client_by_code",
            entity_type="Client"
        )
        client_domain_service.query.get_client_by_code.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.get_client_by_code(client_code)
        
        assert exc_info.value.message == "Error de índice en base de datos"
        assert exc_info.value.operation == "get_client_by_code"
        client_domain_service.query.get_client_by_code.assert_called_once_with(client_code)

    # ==================== TESTS GET_CLIENTS_BY_STATUS ====================

    @pytest.mark.asyncio
    async def test_get_clients_by_status_active_success(
        self,
        client_domain_service: ClientDomainService,
        sample_clients_list: List[Client]
    ):
        """
        Test: Obtención exitosa de clientes activos por estado.
        
        Verifica que el método get_clients_by_status delegue correctamente
        al módulo query y retorne la lista de clientes activos.
        """
        # Arrange
        active_clients = [client for client in sample_clients_list if client.is_active]
        client_domain_service.query.get_clients_by_status.return_value = active_clients
        
        # Act
        result = await client_domain_service.get_clients_by_status(True)
        
        # Assert
        assert result == active_clients
        assert len(result) > 0
        assert all(client.is_active for client in result)
        client_domain_service.query.get_clients_by_status.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_get_clients_by_status_inactive_success(
        self,
        client_domain_service: ClientDomainService,
        sample_clients_list: List[Client]
    ):
        """
        Test: Obtención exitosa de clientes inactivos por estado.
        
        Verifica que el método get_clients_by_status delegue correctamente
        al módulo query y retorne la lista de clientes inactivos.
        """
        # Arrange
        inactive_clients = [client for client in sample_clients_list if not client.is_active]
        client_domain_service.query.get_clients_by_status.return_value = inactive_clients
        
        # Act
        result = await client_domain_service.get_clients_by_status(False)
        
        # Assert
        assert result == inactive_clients
        assert all(not client.is_active for client in result)
        client_domain_service.query.get_clients_by_status.assert_called_once_with(False)

    @pytest.mark.asyncio
    async def test_get_clients_by_status_empty_result(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Resultado vacío al obtener clientes por estado.
        
        Verifica que se retorne una lista vacía cuando no hay clientes
        con el estado especificado.
        """
        # Arrange
        client_domain_service.query.get_clients_by_status.return_value = []
        
        # Act
        result = await client_domain_service.get_clients_by_status(True)
        
        # Assert
        assert result == []
        assert len(result) == 0
        client_domain_service.query.get_clients_by_status.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_get_clients_by_status_repository_error(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Error de repositorio al obtener clientes por estado.
        
        Verifica que se propague correctamente un error de repositorio
        desde el módulo query.
        """
        # Arrange
        repository_error = RepositoryError(
            message="Error de filtrado en base de datos",
            operation="get_clients_by_status",
            entity_type="Client"
        )
        client_domain_service.query.get_clients_by_status.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.get_clients_by_status(True)
        
        assert exc_info.value.message == "Error de filtrado en base de datos"
        assert exc_info.value.operation == "get_clients_by_status"
        client_domain_service.query.get_clients_by_status.assert_called_once_with(True)

    # ==================== TESTS GET_ACTIVE_CLIENTS ====================

    @pytest.mark.asyncio
    async def test_get_active_clients_success(
        self,
        client_domain_service: ClientDomainService,
        sample_clients_list: List[Client]
    ):
        """
        Test: Obtención exitosa de clientes activos.
        
        Verifica que el método get_active_clients delegue correctamente
        al módulo query y retorne la lista de clientes activos.
        """
        # Arrange
        active_clients = [client for client in sample_clients_list if client.is_active]
        client_domain_service.query.get_active_clients.return_value = active_clients
        
        # Act
        result = await client_domain_service.get_active_clients()
        
        # Assert
        assert result == active_clients
        assert len(result) > 0
        assert all(client.is_active for client in result)
        client_domain_service.query.get_active_clients.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_clients_empty_result(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Resultado vacío al obtener clientes activos.
        
        Verifica que se retorne una lista vacía cuando no hay clientes activos.
        """
        # Arrange
        client_domain_service.query.get_active_clients.return_value = []
        
        # Act
        result = await client_domain_service.get_active_clients()
        
        # Assert
        assert result == []
        assert len(result) == 0
        client_domain_service.query.get_active_clients.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_clients_repository_error(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Error de repositorio al obtener clientes activos.
        
        Verifica que se propague correctamente un error de repositorio
        desde el módulo query.
        """
        # Arrange
        repository_error = RepositoryError(
            message="Error de consulta de clientes activos",
            operation="get_active_clients",
            entity_type="Client"
        )
        client_domain_service.query.get_active_clients.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.get_active_clients()
        
        assert exc_info.value.message == "Error de consulta de clientes activos"
        assert exc_info.value.operation == "get_active_clients"
        client_domain_service.query.get_active_clients.assert_called_once()

    # ==================== TESTS GET_INACTIVE_CLIENTS ====================

    @pytest.mark.asyncio
    async def test_get_inactive_clients_success(
        self,
        client_domain_service: ClientDomainService,
        sample_clients_list: List[Client]
    ):
        """
        Test: Obtención exitosa de clientes inactivos.
        
        Verifica que el método get_inactive_clients delegue correctamente
        al módulo query y retorne la lista de clientes inactivos.
        """
        # Arrange
        inactive_clients = [client for client in sample_clients_list if not client.is_active]
        client_domain_service.query.get_inactive_clients.return_value = inactive_clients
        
        # Act
        result = await client_domain_service.get_inactive_clients()
        
        # Assert
        assert result == inactive_clients
        assert all(not client.is_active for client in result)
        client_domain_service.query.get_inactive_clients.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_inactive_clients_empty_result(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Resultado vacío al obtener clientes inactivos.
        
        Verifica que se retorne una lista vacía cuando no hay clientes inactivos.
        """
        # Arrange
        client_domain_service.query.get_inactive_clients.return_value = []
        
        # Act
        result = await client_domain_service.get_inactive_clients()
        
        # Assert
        assert result == []
        assert len(result) == 0
        client_domain_service.query.get_inactive_clients.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_inactive_clients_repository_error(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Error de repositorio al obtener clientes inactivos.
        
        Verifica que se propague correctamente un error de repositorio
        desde el módulo query.
        """
        # Arrange
        repository_error = RepositoryError(
            message="Error de consulta de clientes inactivos",
            operation="get_inactive_clients",
            entity_type="Client"
        )
        client_domain_service.query.get_inactive_clients.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.get_inactive_clients()
        
        assert exc_info.value.message == "Error de consulta de clientes inactivos"
        assert exc_info.value.operation == "get_inactive_clients"
        client_domain_service.query.get_inactive_clients.assert_called_once()

    # ==================== TESTS SEARCH_CLIENTS_BASIC ====================

    @pytest.mark.asyncio
    async def test_search_clients_basic_success(
        self,
        client_domain_service: ClientDomainService,
        sample_clients_list: List[Client]
    ):
        """
        Test: Búsqueda básica exitosa de clientes.
        
        Verifica que el método search_clients_basic delegue correctamente
        al módulo query y retorne los clientes encontrados.
        """
        # Arrange
        search_term = "Test"
        matching_clients = [client for client in sample_clients_list if search_term.lower() in client.name.lower()]
        client_domain_service.query.search_clients_basic.return_value = matching_clients
        
        # Act
        result = await client_domain_service.search_clients_basic(search_term)
        
        # Assert
        assert result == matching_clients
        assert len(result) > 0
        client_domain_service.query.search_clients_basic.assert_called_once_with(search_term)

    @pytest.mark.asyncio
    async def test_search_clients_basic_no_results(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Búsqueda básica sin resultados.
        
        Verifica que se retorne una lista vacía cuando no hay coincidencias.
        """
        # Arrange
        search_term = "NoExiste"
        client_domain_service.query.search_clients_basic.return_value = []
        
        # Act
        result = await client_domain_service.search_clients_basic(search_term)
        
        # Assert
        assert result == []
        assert len(result) == 0
        client_domain_service.query.search_clients_basic.assert_called_once_with(search_term)

    @pytest.mark.asyncio
    async def test_search_clients_basic_empty_term(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Búsqueda básica con término vacío.
        
        Verifica el comportamiento cuando se proporciona un término de búsqueda vacío.
        """
        # Arrange
        search_term = ""
        client_domain_service.query.search_clients_basic.return_value = []
        
        # Act
        result = await client_domain_service.search_clients_basic(search_term)
        
        # Assert
        assert result == []
        client_domain_service.query.search_clients_basic.assert_called_once_with(search_term)

    @pytest.mark.asyncio
    async def test_search_clients_basic_repository_error(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Error de repositorio en búsqueda básica.
        
        Verifica que se propague correctamente un error de repositorio
        desde el módulo query.
        """
        # Arrange
        search_term = "Test"
        repository_error = RepositoryError(
            message="Error de búsqueda en base de datos",
            operation="search_clients_basic",
            entity_type="Client"
        )
        client_domain_service.query.search_clients_basic.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.search_clients_basic(search_term)
        
        assert exc_info.value.message == "Error de búsqueda en base de datos"
        assert exc_info.value.operation == "search_clients_basic"
        client_domain_service.query.search_clients_basic.assert_called_once_with(search_term)

    # ==================== TESTS CLIENT_EXISTS ====================

    @pytest.mark.asyncio
    async def test_client_exists_true(
        self,
        client_domain_service: ClientDomainService,
        sample_client_id: int
    ):
        """
        Test: Verificación exitosa de existencia de cliente.
        
        Verifica que el método client_exists delegue correctamente
        al módulo query y retorne True cuando el cliente existe.
        """
        # Arrange
        client_domain_service.query.client_exists.return_value = True
        
        # Act
        result = await client_domain_service.client_exists(sample_client_id)
        
        # Assert
        assert result is True
        client_domain_service.query.client_exists.assert_called_once_with(sample_client_id)

    @pytest.mark.asyncio
    async def test_client_exists_false(
        self,
        client_domain_service: ClientDomainService
    ):
        """
        Test: Verificación de cliente inexistente.
        
        Verifica que el método client_exists delegue correctamente
        al módulo query y retorne False cuando el cliente no existe.
        """
        # Arrange
        non_existent_id = 99999
        client_domain_service.query.client_exists.return_value = False
        
        # Act
        result = await client_domain_service.client_exists(non_existent_id)
        
        # Assert
        assert result is False
        client_domain_service.query.client_exists.assert_called_once_with(non_existent_id)

    @pytest.mark.asyncio
    async def test_client_exists_repository_error(
        self,
        client_domain_service: ClientDomainService,
        sample_client_id: int
    ):
        """
        Test: Error de repositorio al verificar existencia de cliente.
        
        Verifica que se propague correctamente un error de repositorio
        desde el módulo query.
        """
        # Arrange
        repository_error = RepositoryError(
            message="Error de verificación en base de datos",
            operation="client_exists",
            entity_type="Client",
            entity_id=sample_client_id
        )
        client_domain_service.query.client_exists.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.client_exists(sample_client_id)
        
        assert exc_info.value.message == "Error de verificación en base de datos"
        assert exc_info.value.operation == "client_exists"
        assert exc_info.value.entity_id == sample_client_id
        client_domain_service.query.client_exists.assert_called_once_with(sample_client_id)