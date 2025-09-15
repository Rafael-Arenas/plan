"""Tests para ProjectRepositoryFacade.

Este módulo contiene tests unitarios que verifican que ProjectRepositoryFacade
delegue correctamente las operaciones a sus módulos especializados.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from planificador.repositories.project.project_repository_facade import (
    ProjectRepositoryFacade,
)
from .fixtures import (
    mock_session,
    project_repository,
    sample_project,
    sample_project_data,
)


class TestProjectRepositoryFacade:
    """Tests para ProjectRepositoryFacade."""

    # ============================================================================
    # TESTS PARA CRUD OPERATIONS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_create_project_delegates_to_crud_operations(
        self, project_repository, sample_project_data, sample_project
    ):
        """Test que verifica que create_project delegue a _crud_operations."""
        # Arrange
        project_repository._crud_operations.create_project.return_value = sample_project

        # Act
        result = await project_repository.create_project(sample_project_data)

        # Assert
        project_repository._crud_operations.create_project.assert_called_once_with(
            sample_project_data
        )
        assert result == sample_project

    @pytest.mark.asyncio
    async def test_update_project_delegates_to_crud_operations(
        self, project_repository, sample_project_data, sample_project
    ):
        """Test que verifica que update_project delegue a _crud_operations."""
        # Arrange
        project_id = 1
        project_repository._crud_operations.update_project.return_value = sample_project

        # Act
        result = await project_repository.update_project(project_id, sample_project_data)

        # Assert
        project_repository._crud_operations.update_project.assert_called_once_with(
            project_id, sample_project_data
        )
        assert result == sample_project

    @pytest.mark.asyncio
    async def test_delete_project_delegates_to_crud_operations(
        self, project_repository
    ):
        """Test que verifica que delete_project delegue a _crud_operations."""
        # Arrange
        project_id = 1
        project_repository._crud_operations.delete_project.return_value = True

        # Act
        result = await project_repository.delete_project(project_id)

        # Assert
        project_repository._crud_operations.delete_project.assert_called_once_with(
            project_id
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_archive_project_delegates_to_crud_operations(
        self, project_repository, sample_project
    ):
        """Test que verifica que archive_project delegue a _crud_operations."""
        # Arrange
        project_id = 1
        project_repository._crud_operations.archive_project.return_value = sample_project

        # Act
        result = await project_repository.archive_project(project_id)

        # Assert
        project_repository._crud_operations.archive_project.assert_called_once_with(
            project_id
        )
        assert result == sample_project

    # ============================================================================
    # TESTS PARA QUERY OPERATIONS
    # ============================================================================

    def test_base_query_delegates_to_query_operations(self, project_repository):
        """Test que verifica que _base_query delegue a _query_operations."""
        # Arrange
        include_archived = True
        mock_query = MagicMock()
        project_repository._query_operations._base_query.return_value = mock_query

        # Act
        result = project_repository._base_query(include_archived)

        # Assert
        project_repository._query_operations._base_query.assert_called_once_with(
            include_archived
        )
        assert result == mock_query

    def test_with_client_delegates_to_query_operations(self, project_repository):
        """Test que verifica que with_client delegue a _query_operations."""
        # Arrange
        mock_query = MagicMock()
        modified_query = MagicMock()
        project_repository._query_operations.with_client.return_value = modified_query

        # Act
        result = project_repository.with_client(mock_query)

        # Assert
        project_repository._query_operations.with_client.assert_called_once_with(
            mock_query
        )
        assert result == modified_query

    def test_with_assignments_delegates_to_query_operations(self, project_repository):
        """Test que verifica que with_assignments delegue a _query_operations."""
        # Arrange
        mock_query = MagicMock()
        modified_query = MagicMock()
        project_repository._query_operations.with_assignments.return_value = modified_query

        # Act
        result = project_repository.with_assignments(mock_query)

        # Assert
        project_repository._query_operations.with_assignments.assert_called_once_with(
            mock_query
        )
        assert result == modified_query

    @pytest.mark.asyncio
    async def test_get_with_full_details_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_with_full_details delegue a _query_operations."""
        # Arrange
        project_id = 1
        expected_project = MagicMock()
        project_repository._query_operations.get_with_full_details.return_value = expected_project

        # Act
        result = await project_repository.get_with_full_details(project_id)

        # Assert
        project_repository._query_operations.get_with_full_details.assert_called_once_with(
            project_id
        )
        assert result == expected_project

    def test_filter_by_reference_delegates_to_query_operations(self, project_repository):
        """Test que verifica que filter_by_reference delegue a _query_operations."""
        # Arrange
        mock_query = MagicMock()
        reference = "PRJ-001"
        filtered_query = MagicMock()
        project_repository._query_operations.filter_by_reference.return_value = filtered_query

        # Act
        result = project_repository.filter_by_reference(mock_query, reference)

        # Assert
        project_repository._query_operations.filter_by_reference.assert_called_once_with(
            mock_query, reference
        )
        assert result == filtered_query

    @pytest.mark.asyncio
    async def test_get_by_trigram_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_by_trigram delegue a _query_operations."""
        # Arrange
        trigram = "ABC"
        expected_project = MagicMock()
        project_repository._query_operations.get_by_trigram.return_value = expected_project

        # Act
        result = await project_repository.get_by_trigram(trigram)

        # Assert
        project_repository._query_operations.get_by_trigram.assert_called_once_with(
            trigram
        )
        assert result == expected_project

    def test_filter_by_name_delegates_to_query_operations(self, project_repository):
        """Test que verifica que filter_by_name delegue a _query_operations."""
        # Arrange
        mock_query = MagicMock()
        name = "Proyecto Test"
        filtered_query = MagicMock()
        project_repository._query_operations.filter_by_name.return_value = filtered_query

        # Act
        result = project_repository.filter_by_name(mock_query, name)

        # Assert
        project_repository._query_operations.filter_by_name.assert_called_once_with(
            mock_query, name
        )
        assert result == filtered_query

    @pytest.mark.asyncio
    async def test_get_by_client_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_by_client delegue a _query_operations."""
        # Arrange
        client_id = 1
        expected_projects = [MagicMock()]
        project_repository._query_operations.get_by_client.return_value = expected_projects

        # Act
        result = await project_repository.get_by_client(client_id)

        # Assert
        project_repository._query_operations.get_by_client.assert_called_once_with(
            client_id
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_by_date_range_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_by_date_range delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        from datetime import date
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        expected_projects = [MagicMock()]
        project_repository._query_operations.get_by_date_range = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.get_by_date_range(start_date, end_date)

        # Assert
        project_repository._query_operations.get_by_date_range.assert_called_once_with(
            start_date, end_date
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_projects_starting_current_week_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_projects_starting_current_week delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        expected_projects = [MagicMock()]
        kwargs = {"limit": 10}
        project_repository._query_operations.get_projects_starting_current_week = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.get_projects_starting_current_week(**kwargs)

        # Assert
        project_repository._query_operations.get_projects_starting_current_week.assert_called_once_with(
            **kwargs
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_projects_ending_current_week_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_projects_ending_current_week delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        expected_projects = [MagicMock()]
        kwargs = {"limit": 5}
        project_repository._query_operations.get_projects_ending_current_week = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.get_projects_ending_current_week(**kwargs)

        # Assert
        project_repository._query_operations.get_projects_ending_current_week.assert_called_once_with(
            **kwargs
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_projects_starting_current_month_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_projects_starting_current_month delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        expected_projects = [MagicMock()]
        kwargs = {"include_archived": False}
        project_repository._query_operations.get_projects_starting_current_month = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.get_projects_starting_current_month(**kwargs)

        # Assert
        project_repository._query_operations.get_projects_starting_current_month.assert_called_once_with(
            **kwargs
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_projects_starting_business_days_only_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_projects_starting_business_days_only delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        from datetime import date
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        expected_projects = [MagicMock()]
        kwargs = {"limit": 20}
        project_repository._query_operations.get_projects_starting_business_days_only = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.get_projects_starting_business_days_only(
            start_date, end_date, **kwargs
        )

        # Assert
        project_repository._query_operations.get_projects_starting_business_days_only.assert_called_once_with(
            start_date, end_date, **kwargs
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_by_status_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_by_status delegue a _query_operations."""
        # Arrange
        from planificador.models.project import ProjectStatus
        status = ProjectStatus.IN_PROGRESS
        expected_projects = [MagicMock()]
        project_repository._query_operations.get_by_status.return_value = expected_projects

        # Act
        result = await project_repository.get_by_status(status)

        # Assert
        project_repository._query_operations.get_by_status.assert_called_once_with(
            status
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_by_priority_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_by_priority delegue a _query_operations."""
        # Arrange
        from planificador.models.project import ProjectPriority
        priority = ProjectPriority.HIGH
        expected_projects = [MagicMock()]
        project_repository._query_operations.get_by_priority.return_value = expected_projects

        # Act
        result = await project_repository.get_by_priority(priority)

        # Assert
        project_repository._query_operations.get_by_priority.assert_called_once_with(
            priority
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_filter_by_date_range_delegates_to_query_operations(self, project_repository):
        """Test que verifica que filter_by_date_range delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        from datetime import date
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        limit = 10
        expected_projects = [MagicMock()]
        project_repository._query_operations.filter_by_date_range = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.filter_by_date_range(start_date, end_date, limit)

        # Assert
        project_repository._query_operations.filter_by_date_range.assert_called_once_with(
            start_date, end_date, limit
        )
        assert result == expected_projects

    # ============================================================================
    # TESTS PARA RELATIONSHIP OPERATIONS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_get_with_client_delegates_to_query_operations(
        self, project_repository
    ):
        """Test que verifica la delegación de get_with_client a query operations."""
        # Arrange
        project_id = 1
        expected_result = MagicMock()
        project_repository._query_operations.get_with_client.return_value = expected_result

        # Act
        result = await project_repository.get_with_client(project_id)

        # Assert
        project_repository._query_operations.get_with_client.assert_called_once_with(
            project_id
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_with_assignments_delegates_to_query_operations(
        self, project_repository
    ):
        """Test que verifica la delegación de get_with_assignments a query operations."""
        # Arrange
        project_id = 1
        expected_result = MagicMock()
        project_repository._query_operations.get_with_assignments.return_value = expected_result

        # Act
        result = await project_repository.get_with_assignments(project_id)

        # Assert
        project_repository._query_operations.get_with_assignments.assert_called_once_with(
            project_id
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_with_full_details_delegates_to_query_operations(
        self, project_repository
    ):
        """Test que verifica la delegación de get_with_full_details a query operations."""
        # Arrange
        project_id = 1
        expected_result = MagicMock()
        project_repository._query_operations.get_with_full_details.return_value = expected_result

        # Act
        result = await project_repository.get_with_full_details(project_id)

        # Assert
        project_repository._query_operations.get_with_full_details.assert_called_once_with(
            project_id
        )
        assert result == expected_result

    # ============================================================================
    # TESTS PARA STATISTICS OPERATIONS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_get_status_summary_delegates_to_statistics_operations(
        self, project_repository
    ):
        """Test que verifica que get_status_summary delegue a _statistics_operations."""
        # Arrange
        expected_summary = {"active": 5, "completed": 3, "planning": 2}
        project_repository._statistics_operations.get_status_summary.return_value = expected_summary

        # Act
        result = await project_repository.get_status_summary()

        # Assert
        project_repository._statistics_operations.get_status_summary.assert_called_once()
        assert result == expected_summary

    @pytest.mark.asyncio
    async def test_get_overdue_projects_summary_delegates_to_statistics_operations(
        self, project_repository
    ):
        """Test que verifica que get_overdue_projects_summary delegue a _statistics_operations."""
        # Arrange
        expected_summary = [
            {"id": 1, "name": "Proyecto Atrasado 1", "days_overdue": 5},
            {"id": 2, "name": "Proyecto Atrasado 2", "days_overdue": 10}
        ]
        project_repository._statistics_operations.get_overdue_projects_summary.return_value = expected_summary

        # Act
        result = await project_repository.get_overdue_projects_summary()

        # Assert
        project_repository._statistics_operations.get_overdue_projects_summary.assert_called_once()
        assert result == expected_summary

    # ============================================================================
    # TESTS PARA VALIDATION OPERATIONS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_validate_project_creation_delegates_to_validation_operations(
        self, project_repository, sample_project_data
    ):
        """Test que verifica que validate_project_creation delegue a _validation_operations."""
        # Arrange
        project_repository._validation_operations.validate_project_creation.return_value = None

        # Act
        result = await project_repository.validate_project_creation(sample_project_data)

        # Assert
        project_repository._validation_operations.validate_project_creation.assert_called_once_with(
            sample_project_data
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_validate_project_update_delegates_to_validation_operations(
        self, project_repository, sample_project_data
    ):
        """Test que verifica que validate_project_update delegue a _validation_operations."""
        # Arrange
        project_id = 1
        project_repository._validation_operations.validate_project_update.return_value = None

        # Act
        result = await project_repository.validate_project_update(project_id, sample_project_data)

        # Assert
        project_repository._validation_operations.validate_project_update.assert_called_once_with(
            project_id, sample_project_data
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_reference_exists_delegates_to_validation_operations(
        self, project_repository
    ):
        """Test que verifica que reference_exists delegue a _validation_operations."""
        # Arrange
        reference = "PRJ-001"
        exclude_id = 1
        project_repository._validation_operations.reference_exists.return_value = True

        # Act
        result = await project_repository.reference_exists(reference, exclude_id)

        # Assert
        project_repository._validation_operations.reference_exists.assert_called_once_with(
            reference, exclude_id
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_reference_exists_without_exclude_id_delegates_to_validation_operations(
        self, project_repository
    ):
        """Test que verifica que reference_exists sin exclude_id delegue a _validation_operations."""
        # Arrange
        reference = "PRJ-002"
        project_repository._validation_operations.reference_exists.return_value = False

        # Act
        result = await project_repository.reference_exists(reference)

        # Assert
        project_repository._validation_operations.reference_exists.assert_called_once_with(
            reference, None
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_trigram_exists_delegates_to_validation_operations(
        self, project_repository
    ):
        """Test que verifica que trigram_exists delegue a _validation_operations."""
        # Arrange
        trigram = "ABC"
        exclude_id = 2
        project_repository._validation_operations.trigram_exists.return_value = True

        # Act
        result = await project_repository.trigram_exists(trigram, exclude_id)

        # Assert
        project_repository._validation_operations.trigram_exists.assert_called_once_with(
            trigram, exclude_id
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_trigram_exists_without_exclude_id_delegates_to_validation_operations(
        self, project_repository
    ):
        """Test que verifica que trigram_exists sin exclude_id delegue a _validation_operations."""
        # Arrange
        trigram = "XYZ"
        project_repository._validation_operations.trigram_exists.return_value = False

        # Act
        result = await project_repository.trigram_exists(trigram)

        # Assert
        project_repository._validation_operations.trigram_exists.assert_called_once_with(
            trigram, None
        )
        assert result is False

    def test_format_project_dates_delegates_to_query_operations(
        self, project_repository, sample_project
    ):
        """Test que verifica la delegación de format_project_dates a query operations."""
        expected_result = {"start_date": "2024-01-01", "end_date": "2024-12-31"}
        project_repository._query_operations.format_project_dates.return_value = (
            expected_result
        )

        result = project_repository.format_project_dates(sample_project)

        project_repository._query_operations.format_project_dates.assert_called_once_with(
            sample_project
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_filter_by_dates_delegates_to_query_operations(self, project_repository):
        """Test que verifica que filter_by_dates delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        from datetime import date
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        expected_result = [MagicMock()]
        project_repository._query_operations.filter_by_dates = AsyncMock(return_value=expected_result)

        # Act
        result = await project_repository.filter_by_dates(start_date, end_date)

        # Assert
        project_repository._query_operations.filter_by_dates.assert_called_once_with(
            start_date, end_date
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_search_projects_delegates_to_query_operations(self, project_repository):
        """Test que verifica que search_projects delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        search_term = "test project"
        limit = 10
        expected_projects = [MagicMock()]
        project_repository._query_operations.search_projects = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.search_projects(search_term, limit)

        # Assert
        project_repository._query_operations.search_projects.assert_called_once_with(
            search_term, limit
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_overdue_projects_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_overdue_projects delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        limit = 5
        expected_projects = [MagicMock()]
        project_repository._query_operations.get_overdue_projects = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.get_overdue_projects(limit)

        # Assert
        project_repository._query_operations.get_overdue_projects.assert_called_once_with(
            limit
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_active_projects_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_active_projects delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        limit = 10
        expected_projects = [MagicMock()]
        project_repository._query_operations.get_active_projects = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.get_active_projects(limit)

        # Assert
        project_repository._query_operations.get_active_projects.assert_called_once_with(
            limit
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_by_id_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_by_id delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        project_id = 1
        expected_project = MagicMock()
        project_repository._query_operations.get_by_id = AsyncMock(return_value=expected_project)

        # Act
        result = await project_repository.get_by_id(project_id)

        # Assert
        project_repository._query_operations.get_by_id.assert_called_once_with(
            project_id
        )
        assert result == expected_project

    @pytest.mark.asyncio
    async def test_get_by_reference_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_by_reference delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        reference = "PRJ-001"
        expected_project = MagicMock()
        project_repository._query_operations.get_by_reference = AsyncMock(return_value=expected_project)

        # Act
        result = await project_repository.get_by_reference(reference)

        # Assert
        project_repository._query_operations.get_by_reference.assert_called_once_with(
            reference
        )
        assert result == expected_project

    @pytest.mark.asyncio
    async def test_search_by_name_delegates_to_query_operations(self, project_repository):
        """Test que verifica que search_by_name delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        search_term = "project name"
        expected_projects = [MagicMock()]
        project_repository._query_operations.search_by_name = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.search_by_name(search_term)

        # Assert
        project_repository._query_operations.search_by_name.assert_called_once_with(
            search_term
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_by_trigram_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_by_trigram delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        trigram = "PRJ"
        expected_project = MagicMock()
        project_repository._query_operations.get_by_trigram = AsyncMock(return_value=expected_project)

        # Act
        result = await project_repository.get_by_trigram(trigram)

        # Assert
        project_repository._query_operations.get_by_trigram.assert_called_once_with(
            trigram
        )
        assert result == expected_project

    @pytest.mark.asyncio
    async def test_get_by_client_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_by_client delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        client_id = 1
        expected_projects = [MagicMock()]
        project_repository._query_operations.get_by_client = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.get_by_client(client_id)

        # Assert
        project_repository._query_operations.get_by_client.assert_called_once_with(
            client_id
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_by_status_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_by_status delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        from planificador.models.project import ProjectStatus
        status = ProjectStatus.IN_PROGRESS
        expected_projects = [MagicMock()]
        project_repository._query_operations.get_by_status = AsyncMock(return_value=expected_projects)

        # Act
        result = await project_repository.get_by_status(status)

        # Assert
        project_repository._query_operations.get_by_status.assert_called_once_with(
            status
        )
        assert result == expected_projects

    @pytest.mark.asyncio
    async def test_get_with_client_delegates_to_query_operations(self, project_repository):
        """Test que verifica que get_with_client delegue a _query_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        project_id = 1
        expected_project = MagicMock()
        project_repository._query_operations.get_with_client = AsyncMock(return_value=expected_project)

        # Act
        result = await project_repository.get_with_client(project_id)

        # Assert
        project_repository._query_operations.get_with_client.assert_called_once_with(
            project_id
        )
        assert result == expected_project

    @pytest.mark.asyncio
    async def test_trigram_exists_delegates_to_validation_operations(self, project_repository):
        """Test que verifica que trigram_exists delegue a _validation_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        trigram = "PRJ"
        exclude_id = 1
        project_repository._validation_operations.trigram_exists = AsyncMock(return_value=True)

        # Act
        result = await project_repository.trigram_exists(trigram, exclude_id)

        # Assert
        project_repository._validation_operations.trigram_exists.assert_called_once_with(
            trigram, exclude_id
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_trigram_exists_without_exclude_id_delegates_to_validation_operations(self, project_repository):
        """Test que verifica que trigram_exists sin exclude_id delegue a _validation_operations."""
        # Arrange
        from unittest.mock import AsyncMock
        trigram = "ABC"
        project_repository._validation_operations.trigram_exists = AsyncMock(return_value=False)

        # Act
        result = await project_repository.trigram_exists(trigram)

        # Assert
        project_repository._validation_operations.trigram_exists.assert_called_once_with(
            trigram, None
        )
        assert result is False