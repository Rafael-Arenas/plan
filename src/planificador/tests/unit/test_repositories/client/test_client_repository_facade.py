import pytest
from typing import Generator
from unittest.mock import MagicMock, AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from planificador.schemas.client import ClientCreate, ClientUpdate
from planificador.models.client import Client
from planificador.repositories.client import ClientRepositoryFacade
from planificador.repositories.client.modules.crud_operations import (
    CrudOperations,
)
from planificador.repositories.client.modules.date_operations import (
    DateOperations,
)
from planificador.repositories.client.modules.health_operations import (
    HealthOperations,
)
from planificador.repositories.client.modules.query_operations import (
    QueryOperations,
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
from planificador.repositories.client.modules.validation_operations import (
    ValidationOperations,
)


@pytest.fixture
def mock_session() -> AsyncMock:
    """
    Fixture que mockea una sesión de base de datos asíncrona.
    """
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_crud_operations() -> AsyncMock:
    """Fixture para simular CrudOperations."""
    mock_instance = AsyncMock()
    mock_instance.create_client = AsyncMock(return_value=MagicMock(spec=Client))
    mock_instance.get_by_unique_field = AsyncMock(return_value=None)
    return mock_instance


@pytest.fixture
def mock_query_operations() -> AsyncMock:
    """Fixture para simular QueryOperations."""
    mock_instance = AsyncMock()
    mock_instance.get_client_by_id = AsyncMock(return_value=MagicMock(spec=Client))
    mock_instance.get_client_by_name = AsyncMock(return_value=MagicMock(spec=Client))
    mock_instance.get_client_by_code = AsyncMock(return_value=MagicMock(spec=Client))
    mock_instance.get_client_by_email = AsyncMock(return_value=MagicMock(spec=Client))
    mock_instance.search_clients_by_name = AsyncMock(
        return_value=[MagicMock(spec=Client)]
    )
    mock_instance.get_all_clients = AsyncMock(return_value=[MagicMock(spec=Client)])
    mock_instance.get_by_unique_field = AsyncMock(return_value=None)
    mock_instance.search_clients_by_text = AsyncMock(return_value=[])
    mock_instance.get_clients_by_filters = AsyncMock(return_value=[])
    mock_instance.get_clients_with_relationships = AsyncMock(return_value=[])
    mock_instance.count_clients_by_filters = AsyncMock(return_value=0)
    mock_instance.search_clients_fuzzy = AsyncMock(return_value=[])
    return mock_instance


@pytest.fixture
def mock_advanced_query_operations() -> AsyncMock:
    """Fixture para simular AdvancedQueryOperations."""
    mock = AsyncMock()
    mock.get_by_unique_field = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_validation_operations() -> AsyncMock:
    """Fixture para simular ValidationOperations."""
    mock_instance = AsyncMock()
    mock_instance.validate_unique_fields.return_value = None
    mock_instance.validate_email_format.return_value = None
    mock_instance.validate_phone_format.return_value = None
    mock_instance.validate_required_fields.return_value = None
    mock_instance.validate_all.return_value = None
    mock_instance.get_by_unique_field = AsyncMock(return_value=None)
    return mock_instance


@pytest.fixture
def mock_statistics_operations() -> AsyncMock:
    """Fixture para simular StatisticsOperations."""
    mock = AsyncMock()
    mock.get_by_unique_field = AsyncMock(return_value=None)
    mock.get_client_stats = AsyncMock(return_value={})
    return mock


@pytest.fixture
def mock_relationship_operations() -> AsyncMock:
    """Fixture para simular RelationshipOperations."""
    mock = AsyncMock()
    mock.get_by_unique_field = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_date_operations() -> AsyncMock:
    """Fixture para simular DateOperations."""
    mock_instance = AsyncMock()
    mock_instance.get_clients_created_in_date_range.return_value = [
        MagicMock(spec=Client)
    ]
    mock_instance.get_clients_updated_in_date_range.return_value = [
        MagicMock(spec=Client)
    ]
    mock_instance.get_by_unique_field = AsyncMock(return_value=None)
    return mock_instance


@pytest.fixture
def mock_health_operations() -> AsyncMock:
    """Fixture para crear un mock de `HealthOperations`."""
    return AsyncMock(spec=HealthOperations)


@pytest.fixture
def client_facade(
    mock_session: AsyncMock,
    mock_crud_operations: AsyncMock,
    mock_query_operations: AsyncMock,
    mock_validation_operations: AsyncMock,
    mock_advanced_query_operations: AsyncMock,
    mock_statistics_operations: AsyncMock,
    mock_relationship_operations: AsyncMock,
    mock_date_operations: AsyncMock,
    mock_health_operations: AsyncMock,
) -> Generator[ClientRepositoryFacade, None, None]:
    """
    Fixture que crea una instancia de `ClientRepositoryFacade` con módulos mock.

    Utiliza `patch` para reemplazar las clases de operaciones reales por mocks
    durante la instanciación del facade, evitando así el `TypeError` con clases
    abstractas.
    """
    with patch(
        "planificador.repositories.client.client_repository_facade.CrudOperations",
        return_value=mock_crud_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.QueryOperations",
        return_value=mock_query_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.AdvancedQueryOperations",
        return_value=mock_advanced_query_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.ValidationOperations",
        return_value=mock_validation_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.StatisticsOperations",
        return_value=mock_statistics_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.RelationshipOperations",
        return_value=mock_relationship_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.DateOperations",
        return_value=mock_date_operations,
    ), patch(
        "planificador.repositories.client.client_repository_facade.HealthOperations",
        return_value=mock_health_operations,
    ):
        facade = ClientRepositoryFacade(session=mock_session)
        yield facade


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


from datetime import datetime


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
    # El método en el facade es síncrono, pero el mock subyacente no lo es.
    # Se ajusta la prueba para reflejar la naturaleza síncrona de la llamada.
    client_facade._validation_operations.validate_email_format = MagicMock()
    client_facade.validate_email_format(email)
    client_facade._validation_operations.validate_email_format.assert_called_once_with(
        email
    )


@pytest.mark.asyncio
async def test_validate_phone_format_success(client_facade: ClientRepositoryFacade):
    """Test that validate_phone_format delegates to _validation_operations."""
    phone = "123456789"
    client_facade._validation_operations.validate_phone_format = MagicMock()
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
    client_facade._validation_operations.validate_required_fields = MagicMock()
    client_facade.validate_required_fields(client_data)
    client_facade._validation_operations.validate_required_fields.assert_called_once_with(
        client_data
    )



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
    client_facade._statistics_operations.get_comprehensive_dashboard_metrics = MagicMock()
    await client_facade.get_comprehensive_dashboard_metrics()
    client_facade._statistics_operations.get_comprehensive_dashboard_metrics.assert_called_once()


@pytest.mark.asyncio
async def test_get_client_stats_by_id_delegation(
    client_facade: ClientRepositoryFacade,
) -> None:
    """
    Verifica que get_client_stats_by_id delega la llamada correctamente.
    """
    client_id = 1
    await client_facade.get_client_stats_by_id(client_id)
    client_facade._statistics_operations.get_client_stats_by_id.assert_awaited_once_with(
        client_id
    )


@pytest.mark.asyncio
async def test_search_clients_by_text_delegation(
    client_facade: ClientRepositoryFacade,
    mock_advanced_query_operations: AsyncMock,
) -> None:
    """
    Verifica que search_clients_by_text delega la llamada correctamente.
    """
    await client_facade.search_clients_by_text("test")
    mock_advanced_query_operations.search_clients_by_text.assert_awaited_once_with(
        "test", None, 50, 0
    )


@pytest.mark.asyncio
async def test_get_clients_by_filters_delegation(
    client_facade: ClientRepositoryFacade,
    mock_advanced_query_operations: AsyncMock,
) -> None:
    """
    Verifica que get_clients_by_filters delega la llamada correctamente.
    """
    filters = {"country": "Spain"}
    await client_facade.get_clients_by_filters(filters)
    mock_advanced_query_operations.get_clients_by_filters.assert_awaited_once_with(
        filters, 50, 0, None
    )


@pytest.mark.asyncio
async def test_get_clients_with_relationships_delegation(
    client_facade: ClientRepositoryFacade,
    mock_advanced_query_operations: AsyncMock,
) -> None:
    """
    Verifica que get_clients_with_relationships delega la llamada.
    """
    await client_facade.get_clients_with_relationships()
    mock_advanced_query_operations.get_clients_with_relationships.assert_awaited_once_with(
        False, False, 50, 0
    )


@pytest.mark.asyncio
async def test_count_clients_by_filters_delegation(
    client_facade: ClientRepositoryFacade,
    mock_advanced_query_operations: AsyncMock,
) -> None:
    """
    Verifica que count_clients_by_filters delega la llamada correctamente.
    """
    filters = {"country": "Spain"}
    await client_facade.count_clients_by_filters(filters)
    mock_advanced_query_operations.count_clients_by_filters.assert_awaited_once_with(
        filters
    )


@pytest.mark.asyncio
async def test_search_clients_fuzzy_delegation(
    client_facade: ClientRepositoryFacade,
    mock_advanced_query_operations: AsyncMock,
) -> None:
    """
    Verifica que search_clients_fuzzy delega la llamada correctamente.
    """
    search_term = "test"
    similarity = 0.5
    await client_facade.search_clients_fuzzy(search_term, similarity)
    mock_advanced_query_operations.search_clients_fuzzy.assert_awaited_once_with(
        search_term, similarity
    )


# =========================================================================
# LEGACY TESTS (Aseguran compatibilidad hacia atrás)
# =========================================================================

@pytest.mark.asyncio
async def test_validate_client_data_delegation(
    client_facade: ClientRepositoryFacade,
    mock_validation_operations: AsyncMock,
) -> None:
    """Verifica que validate_client_data delega la llamada a _validation_operations."""
    client_data = {"name": "Test"}
    await client_facade.validate_client_data(client_data)
    mock_validation_operations.validate_client_data.assert_awaited_once_with(
        client_data, None, True
    )


@pytest.mark.asyncio
async def test_validate_business_rules_delegation(
    client_facade: ClientRepositoryFacade,
    mock_validation_operations: AsyncMock,
) -> None:
    """Verifica que validate_business_rules delega la llamada a _validation_operations."""
    client_data = {"name": "Test"}
    await client_facade.validate_business_rules(client_data)
    mock_validation_operations.validate_business_rules.assert_awaited_once_with(
        client_data, None
    )


@pytest.mark.asyncio
async def test_validate_client_name_unique_delegation(
    client_facade: ClientRepositoryFacade,
    mock_validation_operations: AsyncMock,
) -> None:
    """Verifica que validate_client_name_unique delega la llamada a _validation_operations."""
    name = "Test Client"
    await client_facade.validate_client_name_unique(name)
    mock_validation_operations.validate_client_name_unique.assert_awaited_once_with(
        name, None
    )


@pytest.mark.asyncio
async def test_validate_client_code_unique_delegation(
    client_facade: ClientRepositoryFacade,
    mock_validation_operations: AsyncMock,
) -> None:
    """Verifica que validate_client_code_unique delega la llamada a _validation_operations."""
    code = "TC-001"
    await client_facade.validate_client_code_unique(code)
    mock_validation_operations.validate_client_code_unique.assert_awaited_once_with(
        code, None
    )


@pytest.mark.asyncio
async def test_validate_client_deletion_success(
    client_facade: ClientRepositoryFacade,
    mock_validation_operations: AsyncMock,
) -> None:
    """Verifica que validate_client_deletion delega la llamada a _validation_operations."""
    await client_facade.validate_client_deletion(1)
    mock_validation_operations.validate_client_deletion.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_health_check_delegation(
    client_facade: ClientRepositoryFacade,
    mock_health_operations: AsyncMock,
) -> None:
    """
    Verifica que health_check delega la llamada correctamente.
    """
    await client_facade.health_check()
    mock_health_operations.health_check.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_module_info_delegation(
    client_facade: ClientRepositoryFacade,
    mock_health_operations: AsyncMock,
) -> None:
    """
    Verifica que get_module_info delega la llamada correctamente.
    """
    await client_facade.get_module_info()
    mock_health_operations.get_module_info.assert_awaited_once()


@pytest.mark.asyncio
async def test_validate_field_lengths_success(client_facade: ClientRepositoryFacade):
    """Test that validate_field_lengths delegates to _validation_operations."""
    client_data = {"name": "Test Client", "address": "123 Test Street"}
    client_facade._validation_operations.validate_field_lengths = MagicMock()
    client_facade.validate_field_lengths(client_data)
    client_facade._validation_operations.validate_field_lengths.assert_called_once_with(
        client_data
    )


@pytest.mark.asyncio
async def test_validate_code_format_success(client_facade: ClientRepositoryFacade):
    """Test that validate_code_format delegates to _validation_operations."""
    code = "TC-001"
    client_facade._validation_operations.validate_code_format = MagicMock()
    client_facade.validate_code_format(code)
    client_facade._validation_operations.validate_code_format.assert_called_once_with(
        code
    )
