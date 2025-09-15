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

    def test_with_full_details_delegates_to_query_operations(self, project_repository):
        """Test que verifica que with_full_details delegue a _query_operations."""
        # Arrange
        mock_query = MagicMock()
        modified_query = MagicMock()
        project_repository._query_operations.with_full_details.return_value = modified_query

        # Act
        result = project_repository.with_full_details(mock_query)

        # Assert
        project_repository._query_operations.with_full_details.assert_called_once_with(
            mock_query
        )
        assert result == modified_query

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

    def test_filter_by_trigram_delegates_to_query_operations(self, project_repository):
        """Test que verifica que filter_by_trigram delegue a _query_operations."""
        # Arrange
        mock_query = MagicMock()
        trigram = "ABC"
        filtered_query = MagicMock()
        project_repository._query_operations.filter_by_trigram.return_value = filtered_query

        # Act
        result = project_repository.filter_by_trigram(mock_query, trigram)

        # Assert
        project_repository._query_operations.filter_by_trigram.assert_called_once_with(
            mock_query, trigram
        )
        assert result == filtered_query

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

    def test_filter_by_client_delegates_to_query_operations(self, project_repository):
        """Test que verifica que filter_by_client delegue a _query_operations."""
        # Arrange
        mock_query = MagicMock()
        client_id = 1
        filtered_query = MagicMock()
        project_repository._query_operations.filter_by_client.return_value = filtered_query

        # Act
        result = project_repository.filter_by_client(mock_query, client_id)

        # Assert
        project_repository._query_operations.filter_by_client.assert_called_once_with(
            mock_query, client_id
        )
        assert result == filtered_query

    def test_filter_by_status_delegates_to_query_operations(self, project_repository):
        """Test que verifica que filter_by_status delegue a _query_operations."""
        # Arrange
        mock_query = MagicMock()
        status = "active"
        filtered_query = MagicMock()
        project_repository._query_operations.filter_by_status.return_value = filtered_query

        # Act
        result = project_repository.filter_by_status(mock_query, status)

        # Assert
        project_repository._query_operations.filter_by_status.assert_called_once_with(
            mock_query, status
        )
        assert result == filtered_query

    def test_filter_by_priority_delegates_to_query_operations(self, project_repository):
        """Test que verifica que filter_by_priority delegue a _query_operations."""
        # Arrange
        mock_query = MagicMock()
        priority = "high"
        filtered_query = MagicMock()
        project_repository._query_operations.filter_by_priority.return_value = filtered_query

        # Act
        result = project_repository.filter_by_priority(mock_query, priority)

        # Assert
        project_repository._query_operations.filter_by_priority.assert_called_once_with(
            mock_query, priority
        )
        assert result == filtered_query

    def test_filter_by_date_range_delegates_to_query_operations(self, project_repository):
        """Test que verifica que filter_by_date_range delegue a _query_operations."""
        # Arrange
        mock_query = MagicMock()
        start_date = "2024-01-01"
        end_date = "2024-12-31"
        filtered_query = MagicMock()
        project_repository._query_operations.filter_by_date_range.return_value = filtered_query

        # Act
        result = project_repository.filter_by_date_range(mock_query, start_date, end_date)

        # Assert
        project_repository._query_operations.filter_by_date_range.assert_called_once_with(
            mock_query, start_date, end_date
        )
        assert result == filtered_query

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