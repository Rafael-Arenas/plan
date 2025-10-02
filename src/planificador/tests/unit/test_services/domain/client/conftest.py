"""
Configuración y fixtures para tests del ClientDomainService.

Este módulo proporciona fixtures reutilizables para las pruebas unitarias
del servicio de dominio de clientes, incluyendo mocks de dependencias
y datos de prueba.
"""

import pytest
import pendulum
from typing import Generator, Dict, Any, List
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from planificador.services.domain.client.client_domain_service import ClientDomainService
from planificador.repositories.client.client_repository_facade import ClientRepositoryFacade
from planificador.schemas.client import ClientCreate, ClientUpdate, Client, ClientStatsResponse
from planificador.models.client import Client as ClientModel


@pytest.fixture
def mock_session() -> AsyncMock:
    """
    Fixture que mockea una sesión de base de datos asíncrona.
    
    Returns:
        AsyncMock: Mock de AsyncSession
    """
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_repository_facade() -> AsyncMock:
    """
    Fixture que mockea el ClientRepositoryFacade.
    
    Returns:
        AsyncMock: Mock de ClientRepositoryFacade
    """
    return AsyncMock(spec=ClientRepositoryFacade)


@pytest.fixture
def sample_client_id() -> int:
    """
    Fixture que proporciona un ID de cliente de ejemplo.
    
    Returns:
        int: ID de cliente de ejemplo
    """
    return 1


@pytest.fixture
def sample_client_create_data() -> ClientCreate:
    """
    Fixture que proporciona datos válidos para crear un cliente.
    
    Returns:
        ClientCreate: Datos de creación de cliente
    """
    unique_id = "TEST001"
    return ClientCreate(
        name=f"Test Client {unique_id}",
        code=f"TC-{unique_id}",
        contact_person="John Doe",
        email=f"test-{unique_id.lower()}@example.com",
        phone="+1234567890",
        is_active=True,
        notes="Cliente de prueba para testing"
    )


@pytest.fixture
def sample_client_update_data() -> ClientUpdate:
    """
    Fixture que proporciona datos válidos para actualizar un cliente.
    
    Returns:
        ClientUpdate: Datos de actualización de cliente
    """
    unique_id = "UPD001"
    return ClientUpdate(
        name=f"Updated Client {unique_id}",
        contact_person="Jane Smith",
        email=f"updated-{unique_id.lower()}@example.com",
        is_active=False,
        notes="Cliente actualizado para testing"
    )


@pytest.fixture
def sample_client_response(sample_client_id: int) -> Client:
    """
    Fixture que proporciona una respuesta de cliente válida.

    Args:
        sample_client_id: ID del cliente de ejemplo

    Returns:
        Client: Respuesta de cliente con todos los campos requeridos
    """
    return Client(
        id=sample_client_id,
        name="Test Client",
        code="TC-001",
        contact_person="John Doe",
        email="test@example.com",
        phone="+1234567890",
        is_active=True,
        notes="Cliente de prueba",
        created_at=pendulum.now(),
        updated_at=pendulum.now()
    )


@pytest.fixture
def sample_clients_list(sample_client_id: int) -> List[Client]:
    """
    Fixture que proporciona una lista de clientes de ejemplo.
    
    Args:
        sample_client_id: ID del cliente de ejemplo
        
    Returns:
        List[Client]: Lista de clientes
    """
    return [
        Client(
            id=sample_client_id,
            name="Test Client 1",
            code="TC-001",
            contact_person="John Doe",
            email="test1@example.com",
            phone="+1234567890",
            is_active=True,
            notes="Cliente de prueba 1",
            created_at=pendulum.now(),
            updated_at=pendulum.now()
        ),
        Client(
            id=sample_client_id + 1,
            name="Test Client 2",
            code="TC-002",
            contact_person="Jane Smith",
            email="test2@example.com",
            phone="+0987654321",
            is_active=False,
            notes="Cliente de prueba 2",
            created_at=pendulum.now(),
            updated_at=pendulum.now()
        )
    ]


@pytest.fixture
def sample_client_stats() -> ClientStatsResponse:
    """
    Fixture que proporciona estadísticas de cliente de ejemplo.
    
    Returns:
        ClientStatsResponse: Estadísticas de cliente
    """
    return ClientStatsResponse(
        total_clients=10,
        active_clients=8,
        inactive_clients=2,
        clients_with_projects=6,
        clients_without_projects=4,
        average_projects_per_client=2.5,
        total_projects=25
    )


@pytest.fixture
def mock_crud_operations() -> AsyncMock:
    """
    Fixture que mockea las operaciones CRUD.
    
    Returns:
        AsyncMock: Mock de CrudOperations
    """
    mock = AsyncMock()
    mock.create_client = AsyncMock()
    mock.get_client_by_id = AsyncMock()
    mock.update_client = AsyncMock()
    mock.delete_client = AsyncMock()
    mock.bulk_create_clients = AsyncMock()
    return mock


@pytest.fixture
def client_domain_service(
    mock_session: AsyncMock,
    mock_repository_facade: AsyncMock
) -> Generator[ClientDomainService, None, None]:
    """
    Fixture que proporciona una instancia mockeada del ClientDomainService.
    
    Args:
        mock_session: Mock de la sesión de base de datos
        mock_repository_facade: Mock del repository facade
        
    Yields:
        ClientDomainService: Instancia del servicio de dominio
    """
    # Crear un mock del servicio completo para evitar la inicialización de módulos abstractos
    service = AsyncMock(spec=ClientDomainService)
    
    # Configurar atributos básicos
    service.session = mock_session
    service.repository_facade = mock_repository_facade
    
    # Mockear los módulos especializados con sus métodos específicos
    service.crud = AsyncMock()
    service.crud.create_client = AsyncMock()
    service.crud.get_client_by_id = AsyncMock()
    service.crud.update_client = AsyncMock()
    service.crud.delete_client = AsyncMock()
    service.crud.bulk_create_clients = AsyncMock()
    
    service.query = AsyncMock()
    service.query.get_client_by_name = AsyncMock()
    service.query.get_client_by_email = AsyncMock()
    service.query.get_client_by_code = AsyncMock()
    service.query.get_clients_by_status = AsyncMock()
    service.query.get_active_clients = AsyncMock()
    service.query.get_inactive_clients = AsyncMock()
    service.query.search_clients_basic = AsyncMock()
    service.query.client_exists = AsyncMock()
    
    service.advanced_query = AsyncMock()
    service.advanced_query.search_clients_advanced = AsyncMock()
    service.advanced_query.get_clients_paginated = AsyncMock()
    service.advanced_query.search_clients_fuzzy = AsyncMock()
    
    service.statistics = AsyncMock()
    service.statistics.get_client_statistics = AsyncMock()
    service.statistics.count_clients_by_status = AsyncMock()
    service.statistics.get_client_growth_statistics = AsyncMock()
    service.statistics.get_client_activity_metrics = AsyncMock()
    
    service.relationships = AsyncMock()
    service.dates = AsyncMock()
    
    service.validation = AsyncMock()
    service.validation.validate_client_creation = AsyncMock()
    service.validation.validate_client_update = AsyncMock()
    service.validation.validate_business_rules = AsyncMock()
    service.validation.validate_email_uniqueness = AsyncMock()
    
    service.health = AsyncMock()
    service.health.check_service_health = AsyncMock()
    service.health.check_database_connectivity = AsyncMock()
    service.health.generate_health_report = AsyncMock()
    
    # Configurar los métodos principales del servicio para que deleguen a los módulos
    async def create_client_mock(client_data):
        return await service.crud.create_client(client_data)
    
    async def get_client_by_id_mock(client_id):
        return await service.crud.get_client_by_id(client_id)
    
    async def update_client_mock(client_id, client_data):
        return await service.crud.update_client(client_id, client_data)
    
    async def delete_client_mock(client_id):
        return await service.crud.delete_client(client_id)
    
    async def bulk_create_clients_mock(clients_data):
        return await service.crud.bulk_create_clients(clients_data)
    
    # Métodos de consulta que delegan al módulo query
    async def get_client_by_name_mock(name):
        return await service.query.get_client_by_name(name)
    
    async def get_client_by_email_mock(email):
        return await service.query.get_client_by_email(email)
    
    async def get_client_by_code_mock(code):
        return await service.query.get_client_by_code(code)
    
    async def get_clients_by_status_mock(is_active):
        return await service.query.get_clients_by_status(is_active)
    
    async def get_active_clients_mock():
        return await service.query.get_active_clients()
    
    async def get_inactive_clients_mock():
        return await service.query.get_inactive_clients()
    
    async def search_clients_basic_mock(search_term):
        return await service.query.search_clients_basic(search_term)
    
    async def client_exists_mock(client_id):
        return await service.query.client_exists(client_id)
    
    # Asignar los métodos mockeados
    service.create_client = create_client_mock
    service.get_client_by_id = get_client_by_id_mock
    service.update_client = update_client_mock
    service.delete_client = delete_client_mock
    service.bulk_create_clients = bulk_create_clients_mock
    
    # Asignar métodos de consulta
    service.get_client_by_name = get_client_by_name_mock
    service.get_client_by_email = get_client_by_email_mock
    service.get_client_by_code = get_client_by_code_mock
    service.get_clients_by_status = get_clients_by_status_mock
    service.get_active_clients = get_active_clients_mock
    service.get_inactive_clients = get_inactive_clients_mock
    service.search_clients_basic = search_clients_basic_mock
    service.client_exists = client_exists_mock
    
    # Métodos avanzados que delegan a los módulos especializados
    async def search_clients_advanced_mock(filters=None, sort_by=None, sort_order="asc", page=1, page_size=10):
        return await service.advanced_query.search_clients_advanced(filters, sort_by, sort_order, page, page_size)
    
    async def get_clients_paginated_mock(page=1, page_size=10, sort_by=None):
        return await service.advanced_query.get_clients_paginated(page, page_size, sort_by)
    
    async def search_clients_fuzzy_mock(search_term, threshold=0.6):
        return await service.advanced_query.search_clients_fuzzy(search_term, threshold)
    
    async def get_client_statistics_mock():
        return await service.statistics.get_client_statistics()
    
    async def count_clients_by_status_mock():
        return await service.statistics.count_clients_by_status()
    
    async def get_client_growth_statistics_mock(days=30):
        return await service.statistics.get_client_growth_statistics(days)
    
    async def get_client_activity_metrics_mock():
        return await service.statistics.get_client_activity_metrics()
    
    async def validate_client_creation_mock(client_data):
        return await service.validation.validate_client_creation(client_data)
    
    async def validate_client_update_mock(client_id, client_data):
        return await service.validation.validate_client_update(client_id, client_data)
    
    async def validate_business_rules_mock(client_data):
        return await service.validation.validate_business_rules(client_data)
    
    async def validate_email_uniqueness_mock(email, exclude_client_id=None):
        return await service.validation.validate_email_uniqueness(email, exclude_client_id)
    
    async def check_service_health_mock():
        return await service.health.check_service_health()
    
    async def check_database_connectivity_mock():
        return await service.health.check_database_connectivity()
    
    async def generate_health_report_mock():
        return await service.health.generate_health_report()
    
    # Métodos de utilidad que no delegan a módulos
    async def get_service_info_mock():
        return {
            "service_name": "ClientDomainService",
            "version": "1.0.0",
            "modules": ["crud", "query", "advanced_query", "statistics", "relationships", "dates", "validation", "health"],
            "capabilities": ["create", "read", "update", "delete", "search", "validate", "health_check"],
            "status": "active"
        }
    
    async def close_mock():
        return True
    
    # Asignar métodos avanzados
    service.search_clients_advanced = search_clients_advanced_mock
    service.get_clients_paginated = get_clients_paginated_mock
    service.search_clients_fuzzy = search_clients_fuzzy_mock
    service.get_client_statistics = get_client_statistics_mock
    service.count_clients_by_status = count_clients_by_status_mock
    service.get_client_growth_statistics = get_client_growth_statistics_mock
    service.get_client_activity_metrics = get_client_activity_metrics_mock
    service.validate_client_creation = validate_client_creation_mock
    service.validate_client_update = validate_client_update_mock
    service.validate_business_rules = validate_business_rules_mock
    service.validate_email_uniqueness = validate_email_uniqueness_mock
    service.check_service_health = check_service_health_mock
    service.check_database_connectivity = check_database_connectivity_mock
    service.generate_health_report = generate_health_report_mock
    service.get_service_info = get_service_info_mock
    service.close = close_mock
    
    yield service


@pytest.fixture
def bulk_client_create_data() -> List[ClientCreate]:
    """
    Fixture que proporciona datos para creación en lote de clientes.
    
    Returns:
        List[ClientCreate]: Lista de datos de creación de clientes
    """
    clients = []
    for i in range(3):
        unique_id = f"BC{i+1:03d}"
        clients.append(ClientCreate(
            name=f"Bulk Client {i+1} {unique_id}",
            code=f"BC-{i+1}-{unique_id}",
            contact_person=f"Contact Person {i+1}",
            email=f"bulk{i+1}-{unique_id.lower()}@example.com",
            phone=f"+123456789{i}",
            is_active=True,
            notes=f"Cliente en lote {i+1} para testing"
        ))
    return clients


@pytest.fixture
def bulk_client_response_data(bulk_client_create_data: List[ClientCreate]) -> List[Client]:
    """
    Fixture que proporciona respuestas para creación en lote de clientes.
    
    Args:
        bulk_client_create_data: Datos de creación en lote
        
    Returns:
        List[Client]: Lista de respuestas de clientes creados
    """
    clients = []
    for i, create_data in enumerate(bulk_client_create_data):
        clients.append(Client(
            id=i + 1,  # Usar enteros secuenciales en lugar de UUID
            name=create_data.name,
            code=create_data.code,
            contact_person=create_data.contact_person,
            email=create_data.email,
            phone=create_data.phone,
            is_active=create_data.is_active,
            notes=create_data.notes,
            created_at=pendulum.now(),
            updated_at=pendulum.now()
        ))
    return clients