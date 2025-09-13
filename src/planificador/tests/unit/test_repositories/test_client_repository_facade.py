import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from planificador.schemas.client import ClientCreate, ClientUpdate
from planificador.models.client import Client
from planificador.repositories.client import ClientRepositoryFacade
from planificador.repositories.client.modules.crud_operations import CrudOperations
from planificador.repositories.client.modules.date_operations import DateOperations
from planificador.repositories.client.modules.query_operations import (
    QueryOperations,
)
from planificador.repositories.client.modules.validation_operations import (
    ValidationOperations,
)
from planificador.repositories.client.modules.relationship_operations import (
    RelationshipOperations,
)
from planificador.repositories.client.modules.advanced_query_operations import (
    AdvancedQueryOperations,
)
from planificador.repositories.client.modules.statistics_operations import (
    StatisticsOperations,
)
from datetime import datetime


@pytest.fixture
def mock_session() -> AsyncMock:
    """
    Fixture que mockea una sesión de base de datos asíncrona.
    """
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_crud_operations() -> MagicMock:
    """
    Fixture que mockea la clase `CrudOperations`.
    Devuelve un mock de la clase que al ser instanciado retorna un `AsyncMock`.
    """
    mock_instance = AsyncMock(spec=CrudOperations)
    mock_instance.create_client = AsyncMock(return_value=MagicMock(spec=Client))

    mock_class = MagicMock(spec=CrudOperations)
    mock_class.return_value = mock_instance
    return mock_class


@pytest.fixture
def mock_query_operations() -> MagicMock:
    """Fixture para simular QueryOperations."""
    mock_instance = AsyncMock(spec=QueryOperations)
    mock_instance.get_client_by_id = AsyncMock(return_value=MagicMock(spec=Client))
    mock_instance.get_client_by_name = AsyncMock(return_value=MagicMock(spec=Client))
    mock_instance.get_client_by_code = AsyncMock(return_value=MagicMock(spec=Client))
    mock_instance.get_client_by_email = AsyncMock(return_value=MagicMock(spec=Client))
    mock_instance.search_clients_by_name = AsyncMock(
        return_value=[MagicMock(spec=Client)]
    )
    mock_instance.get_all_clients = AsyncMock(return_value=[MagicMock(spec=Client)])

    mock_class = MagicMock(spec=QueryOperations)
    mock_class.return_value = mock_instance
    return mock_class


@pytest.fixture
def mock_advanced_query_operations() -> MagicMock:
    """
    Fixture que mockea la clase `AdvancedQueryOperations`.
    """
    mock_instance = AsyncMock(spec=AdvancedQueryOperations)
    mock_class = MagicMock(spec=AdvancedQueryOperations)
    mock_class.return_value = mock_instance
    return mock_class


@pytest.fixture
def mock_validation_operations() -> MagicMock:
    """Fixture to mock ValidationOperations."""
    mock_instance = AsyncMock(spec=ValidationOperations)
    mock_instance.validate_unique_fields.return_value = None
    mock_instance.validate_email_format.return_value = None
    mock_instance.validate_phone_format.return_value = None
    mock_instance.validate_required_fields.return_value = None
    mock_instance.validate_field_lengths.return_value = None
    mock_instance.validate_client_data.return_value = None
    mock_instance.validate_code_format.return_value = None
    mock_instance.validate_business_rules.return_value = None
    mock_instance.validate_client_name_unique.return_value = True
    mock_instance.validate_client_code_unique.return_value = True
    mock_instance.validate_client_deletion.return_value = True
    mock_class = MagicMock(spec=ValidationOperations)
    mock_class.return_value = mock_instance
    return mock_class


@pytest.fixture
def mock_statistics_operations() -> MagicMock:
    """
    Fixture que mockea la clase `StatisticsOperations`.
    """
    mock_instance = AsyncMock(spec=StatisticsOperations)
    mock_class = MagicMock(spec=StatisticsOperations)
    mock_class.return_value = mock_instance
    return mock_class


@pytest.fixture
def mock_relationship_operations() -> MagicMock:
    """
    Fixture que mockea la clase `RelationshipOperations`.
    """
    mock_instance = AsyncMock(spec=RelationshipOperations)
    mock_class = MagicMock(spec=RelationshipOperations)
    mock_class.return_value = mock_instance
    return mock_class


@pytest.fixture
def mock_date_operations() -> MagicMock:
    """Fixture to mock DateOperations."""
    mock_instance = AsyncMock(spec=DateOperations)
    mock_instance.get_clients_created_in_date_range.return_value = [
        MagicMock(spec=Client)
    ]
    mock_instance.get_clients_updated_in_date_range.return_value = [
        MagicMock(spec=Client)
    ]
    mock_class = MagicMock(spec=DateOperations)
    mock_class.return_value = mock_instance
    return mock_class


@pytest.fixture
def client_facade(
    mock_session: AsyncMock,
    mock_crud_operations: MagicMock,
    mock_query_operations: MagicMock,
    mock_validation_operations: MagicMock,
    mock_advanced_query_operations: MagicMock,
    mock_statistics_operations: MagicMock,
    mock_relationship_operations: MagicMock,
    mock_date_operations: MagicMock,
) -> ClientRepositoryFacade:
    """
    Fixture que crea una instancia de `ClientRepositoryFacade` con módulos mockeados.
    """
    with patch(
        "planificador.repositories.client.client_repository_facade.CrudOperations",
        new=mock_crud_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.ValidationOperations",
        new=mock_validation_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.QueryOperations",
        new=mock_query_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.AdvancedQueryOperations",
        new=mock_advanced_query_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.StatisticsOperations",
        new=mock_statistics_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.RelationshipOperations",
        new=mock_relationship_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.DateOperations",
        new=mock_date_operations,
    ):
        facade = ClientRepositoryFacade(session=mock_session)
        return facade


@pytest.mark.asyncio
async def test_create_client_success(client_facade: ClientRepositoryFacade):
    """
    Verifica que el método `create_client` del facade delega correctamente
    la llamada al módulo `_crud_operations`.
    """
    client_data = ClientCreate(
        name="Test Client",
        code="TC-001",
        email="test@example.com",
        address="123 Test St",
        phone="1234567890",
        client_type="Individual",
        status="Active",
    )

    # Llamar al método del facade que queremos probar
    result = await client_facade.create_client(client_data=client_data)

    # Verificar que el método mockeado en el módulo interno fue llamado
    client_facade._crud_operations.create_client.assert_awaited_once_with(
        client_data.model_dump()
    )

    # Verificar que el resultado es el esperado (el que devuelve el mock)
    assert result == client_facade._crud_operations.create_client.return_value


@pytest.mark.asyncio
async def test_update_client_success(client_facade: ClientRepositoryFacade):
    """
    Verifica que el método `update_client` del facade delega correctamente
    la llamada al módulo `_crud_operations`.
    """
    client_id = 1
    client_data = ClientUpdate(name="Updated Client")

    # Configurar el mock para que devuelva un valor
    expected_result = MagicMock(spec=Client)
    client_facade._crud_operations.update_client.return_value = expected_result

    # Llamar al método del facade
    result = await client_facade.update_client(client_id, client_data)

    # Verificar que el método mockeado fue llamado con los argumentos correctos
    client_facade._crud_operations.update_client.assert_awaited_once_with(
        client_id, client_data
    )

    # Verificar que el resultado es el esperado
    assert result == expected_result


@pytest.mark.asyncio
async def test_delete_client_success(client_facade: ClientRepositoryFacade):
    """
    Verifica que el método `delete_client` del facade delega correctamente
    la llamada al módulo `_crud_operations`.
    """
    client_id = 1

    # Configurar el mock para que devuelva un valor
    client_facade._crud_operations.delete_client.return_value = True

    # Llamar al método del facade
    result = await client_facade.delete_client(client_id)

    # Verificar que el método mockeado fue llamado con los argumentos correctos
    client_facade._crud_operations.delete_client.assert_awaited_once_with(client_id)

    # Verificar que el resultado es el esperado
    assert result is True


@pytest.mark.asyncio
async def test_get_clients_created_in_date_range_success(
    client_facade: ClientRepositoryFacade,
):
    """
    Verifica que el método `get_clients_created_in_date_range` del facade
    delega correctamente la llamada al módulo `_date_operations`.
    """
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)

    expected_clients = [MagicMock(spec=Client), MagicMock(spec=Client)]
    client_facade._date_operations.get_clients_created_in_date_range.return_value = (
        expected_clients
    )

    result = await client_facade.get_clients_created_in_date_range(
        start_date, end_date
    )

    client_facade._date_operations.get_clients_created_in_date_range.assert_awaited_once_with(
        start_date, end_date
    )

    assert result == expected_clients


@pytest.mark.asyncio
async def test_get_clients_updated_in_date_range_success(
    client_facade: ClientRepositoryFacade,
):
    """
    Verifica que el método `get_clients_updated_in_date_range` del facade
    delega correctamente la llamada al módulo `_date_operations`.
    """
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)

    expected_clients = [MagicMock(spec=Client), MagicMock(spec=Client)]
    client_facade._date_operations.get_clients_updated_in_date_range.return_value = (
        expected_clients
    )

    result = await client_facade.get_clients_updated_in_date_range(
        start_date, end_date
    )

    client_facade._date_operations.get_clients_updated_in_date_range.assert_awaited_once_with(
        start_date, end_date
    )

    assert result == expected_clients


@pytest.mark.asyncio
async def test_get_client_by_id_success(client_facade: ClientRepositoryFacade):
    """Verifica que get_client_by_id delega a _query_operations."""
    client_id = 1
    await client_facade.get_client_by_id(client_id)
    client_facade._query_operations.get_client_by_id.assert_called_once_with(
        client_id
    )


@pytest.mark.asyncio
async def test_get_client_by_name_success(client_facade: ClientRepositoryFacade):
    """Verifica que get_client_by_name delega a _query_operations."""
    name = "Test Client"
    await client_facade.get_client_by_name(name)
    client_facade._query_operations.get_client_by_name.assert_called_once_with(name)


@pytest.mark.asyncio
async def test_get_client_by_code_success(client_facade: ClientRepositoryFacade):
    """Verifica que get_client_by_code delega a _query_operations."""
    code = "TC-01"
    await client_facade.get_client_by_code(code)
    client_facade._query_operations.get_client_by_code.assert_called_once_with(code)


@pytest.mark.asyncio
async def test_get_client_by_email_success(client_facade: ClientRepositoryFacade):
    """Verifica que get_client_by_email delega a _query_operations."""
    email = "test@example.com"
    await client_facade.get_client_by_email(email)
    client_facade._query_operations.get_client_by_email.assert_called_once_with(email)


@pytest.mark.asyncio
async def test_search_clients_by_name_success(client_facade: ClientRepositoryFacade):
    """Verifica que search_clients_by_name delega a _query_operations."""
    pattern = "Test"
    await client_facade.search_clients_by_name(pattern)
    client_facade._query_operations.search_clients_by_name.assert_called_once_with(
        pattern
    )


@pytest.mark.asyncio
async def test_get_all_clients_success(client_facade: ClientRepositoryFacade):
    """Verifica que get_all_clients delega a _query_operations."""
    await client_facade.get_all_clients(limit=10, offset=0)
    client_facade._query_operations.get_all_clients.assert_called_once_with(10, 0)


@pytest.mark.asyncio
async def test_transfer_projects_to_client_success(
    client_facade: ClientRepositoryFacade,
):
    """Verifica que transfer_projects_to_client delega a _relationship_operations."""
    from_client_id = 1
    to_client_id = 2
    await client_facade.transfer_projects_to_client(
        from_client_id, to_client_id
    )
    client_facade._relationship_operations.transfer_projects_to_client.assert_called_once_with(
        from_client_id, to_client_id
    )


@pytest.mark.asyncio
async def test_get_client_projects_success(client_facade: ClientRepositoryFacade):
    """Verifica que get_client_projects delega a _relationship_operations."""
    client_id = 1
    await client_facade.get_client_projects(client_id)
    client_facade._relationship_operations.get_client_projects.assert_called_once_with(
        client_id
    )


@pytest.mark.asyncio
async def test_get_client_project_count_success(client_facade: ClientRepositoryFacade):
    """Verifica que get_client_project_count delega a _relationship_operations."""
    client_id = 1
    await client_facade.get_client_project_count(client_id)
    client_facade._relationship_operations.get_client_project_count.assert_called_once_with(
        client_id
    )


@pytest.mark.asyncio
async def test_validate_unique_fields_success(client_facade: ClientRepositoryFacade):
    """Test that validate_unique_fields delegates to _validation_operations."""
    client_data = {"name": "Test Client"}
    await client_facade.validate_unique_fields(client_data, exclude_id=1)
    client_facade._validation_operations.validate_unique_fields.assert_called_once_with(
        client_data, 1
    )


@pytest.mark.asyncio
async def test_validate_email_format_success(client_facade: ClientRepositoryFacade):
    """Test that validate_email_format delegates to _validation_operations."""
    email = "test@example.com"
    client_facade.validate_email_format(email)
    client_facade._validation_operations.validate_email_format.assert_called_once_with(
        email
    )


@pytest.mark.asyncio
async def test_validate_phone_format_success(client_facade: ClientRepositoryFacade):
    """Test that validate_phone_format delegates to _validation_operations."""
    phone = "123456789"
    client_facade.validate_phone_format(phone)
    client_facade._validation_operations.validate_phone_format.assert_called_once_with(
        phone
    )


@pytest.mark.asyncio
async def test_validate_required_fields_success(
    client_facade: ClientRepositoryFacade,
):
    """Test that validate_required_fields delegates to _validation_operations."""
    client_data = {"name": "Test Client"}
    client_facade.validate_required_fields(client_data)
    client_facade._validation_operations.validate_required_fields.assert_called_once_with(
        client_data
    )


@pytest.mark.asyncio
async def test_validate_field_lengths_success(
    client_facade: ClientRepositoryFacade,
):
    """Test that validate_field_lengths delegates to _validation_operations."""
    client_data = {"name": "Test Client"}
    client_facade.validate_field_lengths(client_data)
    client_facade._validation_operations.validate_field_lengths.assert_called_once_with(
        client_data
    )


@pytest.mark.asyncio
async def test_validate_client_data_success(client_facade: ClientRepositoryFacade):
    """Test that validate_client_data delegates to _validation_operations."""
    client_data = {"name": "Test Client"}
    await client_facade.validate_client_data(client_data, exclude_id=1)
    client_facade._validation_operations.validate_client_data.assert_called_once_with(
        client_data, 1, True
    )


@pytest.mark.asyncio
async def test_validate_code_format_success(client_facade: ClientRepositoryFacade):
    """Test that validate_code_format delegates to _validation_operations."""
    code = "C-001"
    client_facade.validate_code_format(code)
    client_facade._validation_operations.validate_code_format.assert_called_once_with(
        code
    )


@pytest.mark.asyncio
async def test_validate_business_rules_success(
    client_facade: ClientRepositoryFacade,
):
    """Test that validate_business_rules delegates to _validation_operations."""
    client_data = {"name": "Test Client"}
    await client_facade.validate_business_rules(client_data, exclude_id=1)
    client_facade._validation_operations.validate_business_rules.assert_called_once_with(
        client_data, 1
    )


@pytest.mark.asyncio
async def test_validate_client_name_unique_success(
    client_facade: ClientRepositoryFacade,
):
    """Test that validate_client_name_unique delegates to _validation_operations."""
    name = "Test Client"
    result = await client_facade.validate_client_name_unique(name, exclude_id=1)
    client_facade._validation_operations.validate_client_name_unique.assert_called_once_with(
        name, 1
    )
    assert result is True


@pytest.mark.asyncio
async def test_validate_client_code_unique_success(
    client_facade: ClientRepositoryFacade,
):
    """Test that validate_client_code_unique delegates to _validation_operations."""
    code = "C-001"
    result = await client_facade.validate_client_code_unique(code, exclude_id=1)
    client_facade._validation_operations.validate_client_code_unique.assert_called_once_with(
        code, 1
    )
    assert result is True


@pytest.mark.asyncio
async def test_validate_client_deletion_success(
    client_facade: ClientRepositoryFacade,
):
    """Test that validate_client_deletion delegates to _validation_operations."""
    client_id = 1
    result = await client_facade.validate_client_deletion(client_id)
    client_facade._validation_operations.validate_client_deletion.assert_called_once_with(
        client_id
    )
    assert result is True


@pytest.mark.asyncio
async def test_get_client_statistics_success(client_facade: ClientRepositoryFacade):
    """Test that get_client_statistics delegates to _statistics_operations."""
    await client_facade.get_client_statistics()
    client_facade._statistics_operations.get_client_statistics.assert_called_once()


@pytest.mark.asyncio
async def test_get_client_counts_by_status_success(
    client_facade: ClientRepositoryFacade,
):
    """Test that get_client_counts_by_status delegates to _statistics_operations."""
    await client_facade.get_client_counts_by_status()
    client_facade._statistics_operations.get_client_counts_by_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_client_count_success(client_facade: ClientRepositoryFacade):
    """Test that get_client_count delegates to _statistics_operations."""
    await client_facade.get_client_count()
    client_facade._statistics_operations.get_client_count.assert_called_once()


@pytest.mark.asyncio
async def test_get_client_stats_by_id_success(
    client_facade: ClientRepositoryFacade,
):
    """Test that get_client_stats_by_id delegates to _statistics_operations."""
    client_id = 1
    await client_facade.get_client_stats_by_id(client_id)
    client_facade._statistics_operations.get_client_stats_by_id.assert_called_once_with(
        client_id
    )


@pytest.mark.asyncio
async def test_get_client_creation_trends_success(
    client_facade: ClientRepositoryFacade,
):
    """Test that get_client_creation_trends delegates to _statistics_operations."""
    await client_facade.get_client_creation_trends(days=30, group_by="day")
    client_facade._statistics_operations.get_client_creation_trends.assert_called_once_with(
        30, "day"
    )


@pytest.mark.asyncio
async def test_get_clients_by_project_count_success(
    client_facade: ClientRepositoryFacade,
):
    """Test that get_clients_by_project_count delegates to _statistics_operations."""
    await client_facade.get_clients_by_project_count(limit=10)
    client_facade._statistics_operations.get_clients_by_project_count.assert_called_once_with(
        10
    )


@pytest.mark.asyncio
async def test_get_comprehensive_dashboard_metrics_success(
    client_facade: ClientRepositoryFacade,
):
    """Test that get_comprehensive_dashboard_metrics delegates to _statistics_operations."""
    client_facade.get_comprehensive_dashboard_metrics()
    client_facade._statistics_operations.get_comprehensive_dashboard_metrics.assert_called_once()