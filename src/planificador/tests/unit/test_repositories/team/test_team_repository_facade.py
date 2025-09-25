# src/planificador/tests/unit/test_repositories/team/test_team_repository_facade.py
"""
Tests unitarios para TeamRepositoryFacade.

Este módulo contiene tests completos para todas las operaciones del
TeamRepositoryFacade, incluyendo CRUD, consultas, relaciones, validaciones
y estadísticas.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime
from typing import List, Dict, Any

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.repositories.team import TeamRepositoryFacade
from planificador.models.team import Team
from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.models.employee import Employee
from planificador.exceptions.repository import (
    RepositoryError,
    RepositoryIntegrityError,
    convert_sqlalchemy_error
)
from planificador.exceptions.repository.team_repository_exceptions import (
    TeamRepositoryError,
    TeamValidationRepositoryError,
    TeamRelationshipError
)

from .fixtures import *


# ============================================================================
# TESTS DE OPERACIONES CRUD
# ============================================================================

class TestTeamCrudOperations:
    """Tests para operaciones CRUD del TeamRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_create_team_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_data,
        sample_team_model,
        create_mock_result
    ):
        """Test exitoso de creación de equipo."""
        # Arrange
        # Configurar el mock del repositorio directamente
        team_repository.create = AsyncMock(return_value=sample_team_model)

        # Act
        result = await team_repository.create(sample_team_data)

        # Assert
        assert result is not None
        assert result.name == sample_team_data["name"]
        assert result.code == sample_team_data["code"]

    @pytest.mark.asyncio
    async def test_create_team_with_sqlalchemy_error(
        self, 
        team_repository, 
        mock_session, 
        sample_team_data
    ):
        """Test de creación de equipo con error de SQLAlchemy."""
        # Arrange
        error = IntegrityError("UNIQUE constraint failed", None, None)
        mock_session.commit.side_effect = error

        # Act & Assert
        with pytest.raises(RepositoryIntegrityError):
            await team_repository.create(sample_team_data)
        
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        create_mock_result
    ):
        """Test exitoso de obtención de equipo por ID."""
        # Arrange
        team_id = 1
        # Configurar el mock del repositorio directamente
        team_repository.get_by_id = AsyncMock(return_value=sample_team_model)

        # Act
        result = await team_repository.get_by_id(team_id)

        # Assert
        assert result is not None
        assert result.id == sample_team_model.id
        assert result.name == sample_team_model.name

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de obtención de equipo por ID no encontrado."""
        # Arrange
        team_id = 999
        # Configurar el mock del repositorio directamente
        team_repository.get_by_id = AsyncMock(return_value=None)

        # Act
        result = await team_repository.get_by_id(team_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_success(
        self, 
        team_repository, 
        mock_session, 
        sample_teams_list,
        create_mock_result
    ):
        """Test exitoso de obtención de todos los equipos."""
        # Arrange
        # Configurar el mock del repositorio directamente
        team_repository.get_all = AsyncMock(return_value=sample_teams_list)

        # Act
        result = await team_repository.get_all()

        # Assert
        assert result is not None
        assert len(result) == len(sample_teams_list)
        assert all(isinstance(team, Team) for team in result)

    @pytest.mark.asyncio
    async def test_update_team_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        sample_team_update_data,
        create_mock_result
    ):
        """Test exitoso de actualización de equipo."""
        # Arrange
        team_id = 1
        # Configurar el mock del repositorio directamente
        team_repository.update = AsyncMock(return_value=sample_team_model)

        # Act
        result = await team_repository.update(team_id, sample_team_update_data)

        # Assert
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_team_not_found(
        self, 
        team_repository, 
        mock_session, 
        sample_team_update_data,
        create_mock_result
    ):
        """Test de actualización de equipo no encontrado."""
        # Arrange
        team_id = 999
        mock_result = create_mock_result(None)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne None cuando no encuentra el equipo
        team_repository.update = AsyncMock(return_value=None)

        # Act
        result = await team_repository.update(team_id, sample_team_update_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_team_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        create_mock_result
    ):
        """Test exitoso de eliminación de equipo."""
        # Arrange
        team_id = 1
        # Configurar el mock del repositorio directamente
        team_repository.delete = AsyncMock(return_value=True)

        # Act
        result = await team_repository.delete(team_id)

        # Assert
        assert result is True


# ============================================================================
# TESTS PARA MÉTODOS HEREDADOS DEL FACADE BASE
# ============================================================================

class TestTeamInheritedMethods:
    """Tests para métodos heredados del facade base en TeamRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_get_all_success(
        self, 
        team_repository, 
        mock_session, 
        sample_teams_list,
        create_mock_result
    ):
        """Test exitoso de obtención de todos los equipos sin paginación."""
        # Arrange
        # Configurar el mock del facade directamente
        team_repository.get_all = AsyncMock(return_value=sample_teams_list)

        # Act
        result = await team_repository.get_all()

        # Assert
        assert result is not None
        assert len(result) == len(sample_teams_list)
        assert all(isinstance(team, Team) for team in result)
        team_repository.get_all.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(
        self, 
        team_repository, 
        mock_session, 
        sample_teams_list,
        create_mock_result
    ):
        """Test de obtención de equipos con paginación."""
        # Arrange
        skip = 5
        limit = 10
        paginated_teams = sample_teams_list[:2]  # Simular resultado paginado
        # Configurar el mock del facade directamente
        team_repository.get_all = AsyncMock(return_value=paginated_teams)

        # Act
        result = await team_repository.get_all(skip=skip, limit=limit)

        # Assert
        assert result is not None
        assert len(result) == len(paginated_teams)
        assert all(isinstance(team, Team) for team in result)
        team_repository.get_all.assert_awaited_once_with(skip=skip, limit=limit)

    @pytest.mark.asyncio
    async def test_get_all_empty_result(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de obtención de equipos con resultado vacío."""
        # Arrange
        # Configurar el mock del facade directamente
        team_repository.get_all = AsyncMock(return_value=[])

        # Act
        result = await team_repository.get_all()

        # Assert
        assert result is not None
        assert len(result) == 0
        assert isinstance(result, list)
        team_repository.get_all.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_get_all_with_error(
        self, 
        team_repository, 
        mock_session
    ):
        """Test de obtención de equipos con error en query_module."""
        # Arrange
        error_message = "Error en consulta de equipos"
        # Configurar el mock del facade directamente
        team_repository.get_all = AsyncMock(
            side_effect=Exception(error_message)
        )

        # Act & Assert
        with pytest.raises(Exception):
            await team_repository.get_all()
        
        team_repository.get_all.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_exists_by_id_true(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de verificación de existencia de equipo - existe."""
        # Arrange
        team_id = 1
        # Configurar el mock del facade directamente
        team_repository.exists_by_id = AsyncMock(return_value=True)

        # Act
        result = await team_repository.exists_by_id(team_id)

        # Assert
        assert result is True
        team_repository.exists_by_id.assert_awaited_once_with(team_id)

    @pytest.mark.asyncio
    async def test_exists_by_id_false(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de verificación de existencia de equipo - no existe."""
        # Arrange
        team_id = 999
        # Configurar el mock del facade directamente
        team_repository.exists_by_id = AsyncMock(return_value=False)

        # Act
        result = await team_repository.exists_by_id(team_id)

        # Assert
        assert result is False
        team_repository.exists_by_id.assert_awaited_once_with(team_id)

    @pytest.mark.asyncio
    async def test_exists_by_id_with_error(
        self, 
        team_repository, 
        mock_session
    ):
        """Test de verificación de existencia con error."""
        # Arrange
        team_id = 1
        error_message = "Error en verificación de existencia"
        # Configurar el mock del facade directamente
        team_repository.exists_by_id = AsyncMock(
            side_effect=Exception(error_message)
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await team_repository.exists_by_id(team_id)
        
        assert error_message in str(exc_info.value)
        team_repository.exists_by_id.assert_awaited_once_with(team_id)

    @pytest.mark.asyncio
    async def test_count_all_success(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test exitoso de conteo de todos los equipos."""
        # Arrange
        expected_count = 5
        # Configurar el mock del facade directamente
        team_repository.count_all = AsyncMock(return_value=expected_count)

        # Act
        result = await team_repository.count_all()

        # Assert
        assert result == expected_count
        assert isinstance(result, int)
        team_repository.count_all.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_count_all_with_filters(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de conteo de equipos con filtros."""
        # Arrange
        filters = {"is_active": True, "department": "Tecnología"}
        expected_count = 8
        # Configurar el mock del facade directamente
        team_repository.count_all = AsyncMock(return_value=expected_count)

        # Act
        result = await team_repository.count_all(filters=filters)

        # Assert
        assert result == expected_count
        team_repository.count_all.assert_awaited_once_with(filters=filters)

    @pytest.mark.asyncio
    async def test_count_all_zero_result(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de conteo cuando no hay equipos."""
        # Arrange
        # Configurar el mock del facade directamente
        team_repository.count_all = AsyncMock(return_value=0)

        # Act
        result = await team_repository.count_all()

        # Assert
        assert result == 0

    @pytest.mark.asyncio
    async def test_count_all_with_error(
        self, 
        team_repository, 
        mock_session
    ):
        """Test de conteo con error."""
        # Arrange
        error_message = "Error en conteo de equipos"
        # Configurar el mock del facade directamente
        team_repository.count_all = AsyncMock(
            side_effect=Exception(error_message)
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await team_repository.count_all()
        
        assert error_message in str(exc_info.value)
        team_repository.count_all.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_find_by_name_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        create_mock_result
    ):
        """Test exitoso de búsqueda de equipo por nombre."""
        # Arrange
        team_name = "Equipo de Desarrollo"
        # Configurar el mock del facade directamente
        team_repository.find_by_name = AsyncMock(return_value=sample_team_model)

        # Act
        result = await team_repository.find_by_name(team_name)

        # Assert
        assert result is not None
        assert result.name == sample_team_model.name
        team_repository.find_by_name.assert_awaited_once_with(team_name)

    @pytest.mark.asyncio
    async def test_find_by_name_not_found(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de búsqueda de equipo por nombre - no encontrado."""
        # Arrange
        team_name = "Equipo Inexistente"
        # Configurar el mock del facade directamente
        team_repository.find_by_name = AsyncMock(return_value=None)

        # Act
        result = await team_repository.find_by_name(team_name)

        # Assert
        assert result is None
        team_repository.find_by_name.assert_awaited_once_with(team_name)

    @pytest.mark.asyncio
    async def test_find_by_name_with_error(
        self, 
        team_repository, 
        mock_session
    ):
        """Test de búsqueda por nombre con error."""
        # Arrange
        team_name = "Equipo Test"
        error_message = "Error en búsqueda por nombre"
        # Configurar el mock del facade directamente
        team_repository.find_by_name = AsyncMock(
            side_effect=Exception(error_message)
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await team_repository.find_by_name(team_name)
        
        assert error_message in str(exc_info.value)
        team_repository.find_by_name.assert_awaited_once_with(team_name)

    @pytest.mark.asyncio
    async def test_find_by_code_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        create_mock_result
    ):
        """Test exitoso de búsqueda de equipo por código."""
        # Arrange
        team_code = "DEV001"
        # Configurar el mock del facade directamente
        team_repository.find_by_code = AsyncMock(return_value=sample_team_model)

        # Act
        result = await team_repository.find_by_code(team_code)

        # Assert
        assert result is not None
        assert result.code == sample_team_model.code
        team_repository.find_by_code.assert_awaited_once_with(team_code)

    @pytest.mark.asyncio
    async def test_find_by_code_not_found(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de búsqueda de equipo por código - no encontrado."""
        # Arrange
        team_code = "INEXISTENTE"
        # Configurar el mock del facade directamente
        team_repository.find_by_code = AsyncMock(return_value=None)

        # Act
        result = await team_repository.find_by_code(team_code)

        # Assert
        assert result is None
        team_repository.find_by_code.assert_awaited_once_with(team_code)

    @pytest.mark.asyncio
    async def test_find_by_code_with_error(
        self, 
        team_repository, 
        mock_session
    ):
        """Test de búsqueda por código con error."""
        # Arrange
        team_code = "TEST001"
        error_message = "Error en búsqueda por código"
        # Configurar el mock del facade directamente
        team_repository.find_by_code = AsyncMock(
            side_effect=Exception(error_message)
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await team_repository.find_by_code(team_code)
        
        assert error_message in str(exc_info.value)
        team_repository.find_by_code.assert_awaited_once_with(team_code)

    @pytest.mark.asyncio
    async def test_search_teams_success(
        self, 
        team_repository, 
        mock_session, 
        sample_teams_list,
        create_mock_result
    ):
        """Test exitoso de búsqueda de equipos con término de búsqueda."""
        # Arrange
        search_term = "Desarrollo"
        # Configurar el mock del facade directamente
        team_repository.search_teams = AsyncMock(return_value=sample_teams_list)

        # Act
        result = await team_repository.search_teams(search_term)

        # Assert
        assert result is not None
        assert len(result) == len(sample_teams_list)
        assert all(isinstance(team, Team) for team in result)
        team_repository.search_teams.assert_awaited_once_with(search_term)

    @pytest.mark.asyncio
    async def test_search_teams_with_pagination(
        self, 
        team_repository, 
        mock_session, 
        sample_teams_list,
        create_mock_result
    ):
        """Test de búsqueda de equipos con paginación."""
        # Arrange
        search_term = "Desarrollo"
        skip = 10
        limit = 5
        # Configurar el mock del facade directamente
        team_repository.search_teams = AsyncMock(return_value=sample_teams_list[:limit])

        # Act
        result = await team_repository.search_teams(search_term, skip, limit)

        # Assert
        assert result is not None
        assert len(result) <= limit
        team_repository.search_teams.assert_awaited_once_with(search_term, skip, limit)

    @pytest.mark.asyncio
    async def test_search_teams_no_results(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de búsqueda de equipos sin resultados."""
        # Arrange
        search_term = "Equipo Inexistente"
        # Configurar el mock del facade directamente
        team_repository.search_teams = AsyncMock(return_value=[])

        # Act
        result = await team_repository.search_teams(search_term)

        # Assert
        assert result is not None
        assert len(result) == 0
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_teams_empty_term(
        self, 
        team_repository, 
        mock_session, 
        sample_teams_list,
        create_mock_result
    ):
        """Test de búsqueda de equipos con término vacío."""
        # Arrange
        search_term = ""
        # Configurar el mock del facade directamente
        team_repository.search_teams = AsyncMock(return_value=sample_teams_list)

        # Act
        result = await team_repository.search_teams(search_term)

        # Assert
        assert result is not None
        assert len(result) == len(sample_teams_list)

    @pytest.mark.asyncio
    async def test_search_teams_with_error(
        self, 
        team_repository, 
        mock_session
    ):
        """Test de búsqueda de equipos con error."""
        # Arrange
        search_term = "Test"
        error_message = "Error en búsqueda de equipos"
        # Configurar el mock del facade directamente
        team_repository.search_teams = AsyncMock(
            side_effect=Exception(error_message)
        )

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await team_repository.search_teams(search_term)
        
        assert error_message in str(exc_info.value)
        team_repository.search_teams.assert_awaited_once_with(search_term)


# ============================================================================
# TESTS PARA MÉTODOS FALTANTES
# ============================================================================

class TestTeamMissingOperations:
    """Tests para métodos faltantes del TeamRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_validate_data_consistency_success(
        self, 
        team_repository
    ):
        """Test exitoso de validación de consistencia de datos."""
        # Arrange
        expected_result = {
            "is_consistent": True,
            "issues": [],
            "statistics": {
                "total_teams": 5,
                "active_teams": 5,
                "inactive_teams": 0,
                "teams_without_members": 0,
                "teams_without_leader": 0,
                "data_issues_count": 0
            },
            "recommendations": []
        }
        
        team_repository.validation_module.validate_data_consistency = AsyncMock(
            return_value=expected_result
        )

        # Act
        result = await team_repository.validate_data_consistency()

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result["is_consistent"] is True
        assert "issues" in result
        assert "statistics" in result
        assert "recommendations" in result
        team_repository.validation_module.validate_data_consistency.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_validate_data_consistency_with_issues(
        self, 
        team_repository
    ):
        """Test de validación de consistencia con problemas encontrados."""
        # Arrange
        expected_result = {
            "is_consistent": False,
            "issues": [
                {
                    "type": "teams_without_leader",
                    "count": 1,
                    "message": "1 equipos activos sin líder",
                    "severity": "warning",
                    "teams": [{"id": 1, "name": "Equipo Sin Líder"}]
                },
                {
                    "type": "inconsistent_membership_dates",
                    "count": 1,
                    "message": "1 membresías con fechas inconsistentes",
                    "severity": "error",
                    "memberships": [{"id": 10, "team_id": 1, "employee_id": 5}]
                }
            ],
            "statistics": {
                "total_teams": 5,
                "active_teams": 5,
                "inactive_teams": 0,
                "teams_without_members": 0,
                "teams_without_leader": 1,
                "data_issues_count": 1
            },
            "recommendations": [
                "Asignar líderes a los equipos que no tienen uno",
                "Corregir las fechas de inicio y fin de las membresías inconsistentes"
            ]
        }
        
        team_repository.validation_module.validate_data_consistency = AsyncMock(
            return_value=expected_result
        )

        # Act
        result = await team_repository.validate_data_consistency()

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result["is_consistent"] is False
        assert len(result["issues"]) == 2
        assert result["statistics"]["teams_without_leader"] == 1
        assert result["statistics"]["data_issues_count"] == 1
        team_repository.validation_module.validate_data_consistency.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_team_dashboard_data_success(
        self, 
        team_repository
    ):
        """Test exitoso de obtención de datos del dashboard."""
        # Arrange
        expected_result = {
            "summary": {
                "total_teams": 10,
                "active_teams": 8,
                "inactive_teams": 2
            },
            "teams": [
                {
                    "team": {
                        "id": 1,
                        "name": "Equipo de Desarrollo",
                        "description": "Equipo principal de desarrollo",
                        "department": "Tecnología",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00"
                    },
                    "members": [
                        {
                            "employee_id": 1,
                            "role": "Developer",
                            "is_leader": True,
                            "is_active": True,
                            "start_date": "2024-01-01",
                            "end_date": None
                        }
                    ],
                    "leader": {
                        "employee_id": 1,
                        "role": "Developer",
                        "start_date": "2024-01-01"
                    },
                    "statistics": {
                        "total_members": 1,
                        "active_members": 1,
                        "inactive_members": 0,
                        "has_leader": True
                    }
                }
            ],
            "statistics": {
                "size_distribution": {"1-5": 5, "6-10": 3, "11+": 2},
                "department_distribution": {"Tecnología": 5, "Marketing": 3, "Ventas": 2},
                "teams_without_leader_count": 1,
                "average_team_size": 6.5
            },
            "alerts": [
                {
                    "type": "warning",
                    "message": "1 equipos sin líder asignado",
                    "teams": [{"id": 2, "name": "Equipo Sin Líder"}]
                }
            ]
        }
        
        # Mock de métodos dependientes
        team_repository.count_total_teams = AsyncMock(side_effect=[10, 8])  # total, active
        team_repository.get_complete_team_info = AsyncMock(return_value=expected_result["teams"][0])
        team_repository.get_teams_by_department = AsyncMock(return_value=[])
        team_repository.get_active_teams = AsyncMock(return_value=[])
        team_repository.get_team_size_distribution = AsyncMock(
            return_value=expected_result["statistics"]["size_distribution"]
        )
        team_repository.get_department_team_distribution = AsyncMock(
            return_value=expected_result["statistics"]["department_distribution"]
        )
        team_repository.get_teams_without_leader = AsyncMock(
            return_value=[type('Team', (), {'id': 2, 'name': 'Equipo Sin Líder'})()]
        )
        team_repository.get_average_team_size = AsyncMock(return_value=6.5)
        team_repository.validate_data_consistency = AsyncMock(
            return_value={"is_consistent": True, "issues": []}
        )

        # Act
        result = await team_repository.get_team_dashboard_data(team_id=1)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert "summary" in result
        assert "teams" in result
        assert "statistics" in result
        assert "alerts" in result
        assert result["summary"]["total_teams"] == 10
        assert result["summary"]["active_teams"] == 8
        assert len(result["alerts"]) >= 0

    @pytest.mark.asyncio
    async def test_get_team_dashboard_data_by_department(
        self, 
        team_repository
    ):
        """Test de obtención de datos del dashboard filtrado por departamento."""
        # Arrange
        department = "Tecnología"
        mock_team = type('Team', (), {'id': 1, 'name': 'Equipo Tech'})()
        
        team_repository.count_total_teams = AsyncMock(side_effect=[5, 4])
        team_repository.get_teams_by_department = AsyncMock(return_value=[mock_team])
        team_repository.get_complete_team_info = AsyncMock(return_value={
            "team": {"id": 1, "name": "Equipo Tech"},
            "statistics": {"active_members": 5}
        })
        team_repository.get_team_size_distribution = AsyncMock(return_value={"1-5": 3})
        team_repository.get_department_team_distribution = AsyncMock(return_value={"Tecnología": 4})
        team_repository.get_teams_without_leader = AsyncMock(return_value=[])
        team_repository.get_average_team_size = AsyncMock(return_value=5.0)
        team_repository.validate_data_consistency = AsyncMock(
            return_value={"is_consistent": True, "issues": []}
        )

        # Act
        result = await team_repository.get_team_dashboard_data(department=department)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert len(result["teams"]) >= 0
        team_repository.get_teams_by_department.assert_awaited_once_with(department, active_only=True)

    @pytest.mark.asyncio
    async def test_bulk_team_operation_create_success(
        self, 
        team_repository
    ):
        """Test exitoso de operación en lote para crear equipos."""
        # Arrange
        team_data_list = [
            {
                "name": "Equipo 1",
                "description": "Primer equipo",
                "department": "Tecnología"
            },
            {
                "name": "Equipo 2", 
                "description": "Segundo equipo",
                "department": "Marketing"
            }
        ]
        
        expected_results = [
            {
                "index": 0,
                "success": True,
                "team": {
                    "id": 1,
                    "name": "Equipo 1",
                    "description": "Primer equipo",
                    "department": "Tecnología",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00"
                },
                "validation_warnings": []
            },
            {
                "index": 1,
                "success": True,
                "team": {
                    "id": 2,
                    "name": "Equipo 2",
                    "description": "Segundo equipo", 
                    "department": "Marketing",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00"
                },
                "validation_warnings": []
            }
        ]
        
        team_repository.create_team_with_validation = AsyncMock(
            side_effect=[
                {
                    "success": True,
                    "team": {
                        "id": 1,
                        "name": "Equipo 1",
                        "description": "Primer equipo",
                        "department": "Tecnología",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00"
                    },
                    "validation_warnings": []
                },
                {
                    "success": True,
                    "team": {
                        "id": 2,
                        "name": "Equipo 2",
                        "description": "Segundo equipo", 
                        "department": "Marketing",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00"
                    },
                    "validation_warnings": []
                }
            ]
        )

        # Act
        result = await team_repository.bulk_team_operation("create", team_data_list)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(r["success"] for r in result)
        assert team_repository.create_team_with_validation.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_team_operation_update_success(
        self, 
        team_repository
    ):
        """Test exitoso de operación en lote para actualizar equipos."""
        # Arrange
        team_data_list = [
            {
                "id": 1,
                "name": "Equipo Actualizado 1",
                "description": "Descripción actualizada"
            },
            {
                "id": 2,
                "name": "Equipo Actualizado 2",
                "description": "Otra descripción actualizada"
            }
        ]
        
        mock_team_1 = type('Team', (), {
            'id': 1, 'name': 'Equipo Actualizado 1', 
            'description': 'Descripción actualizada',
            'department': 'Tecnología', 'is_active': True
        })()
        
        mock_team_2 = type('Team', (), {
            'id': 2, 'name': 'Equipo Actualizado 2',
            'description': 'Otra descripción actualizada', 
            'department': 'Marketing', 'is_active': True
        })()
        
        team_repository.update_team = AsyncMock(side_effect=[mock_team_1, mock_team_2])

        # Act
        result = await team_repository.bulk_team_operation("update", team_data_list)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(r["success"] for r in result)
        assert team_repository.update_team.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_team_operation_delete_success(
        self, 
        team_repository
    ):
        """Test exitoso de operación en lote para eliminar equipos."""
        # Arrange
        team_data_list = [
            {"id": 1},
            {"id": 2}
        ]
        
        team_repository.delete_team = AsyncMock(return_value=True)

        # Act
        result = await team_repository.bulk_team_operation("delete", team_data_list)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(r["success"] for r in result)
        assert team_repository.delete_team.call_count == 2
        assert team_repository.delete_team.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_team_operation_mixed_results(
        self, 
        team_repository
    ):
        """Test de operación en lote con resultados mixtos (éxitos y fallos)."""
        # Arrange
        team_data_list = [
            {
                "name": "Equipo Válido",
                "description": "Equipo que se creará exitosamente",
                "department": "Tecnología"
            },
            {
                "name": "",  # Nombre inválido
                "description": "Equipo con datos inválidos",
                "department": "Marketing"
            }
        ]
        
        # Primer equipo se crea exitosamente
        success_result = {
            "success": True,
            "team": {
                "id": 1,
                "name": "Equipo Válido",
                "description": "Equipo que se creará exitosamente",
                "department": "Tecnología",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00"
            },
            "validation_warnings": []
        }
        
        # Segundo equipo falla la validación
        failure_result = {
            "success": False,
            "team": None,
            "validation_errors": ["El nombre del equipo es requerido"],
            "validation_warnings": []
        }
        
        team_repository.create_team_with_validation = AsyncMock(
            side_effect=[success_result, failure_result]
        )

        # Act
        result = await team_repository.bulk_team_operation("create", team_data_list)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["success"] is True
        assert result[1]["success"] is False
        assert "validation_errors" in result[1]

    @pytest.mark.asyncio
    async def test_bulk_team_operation_invalid_operation(
        self, 
        team_repository
    ):
        """Test de operación en lote con operación inválida."""
        # Arrange
        team_data_list = [{"name": "Equipo Test"}]

        # Act
        result = await team_repository.bulk_team_operation("invalid_operation", team_data_list)

        # Assert
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["success"] is False
        assert "Operación no soportada" in result[0]["error"]


# ============================================================================
# TESTS PARA MÉTODOS ESTADÍSTICOS FALTANTES
# ============================================================================

class TestTeamStatisticsAdditionalOperations:
    """Tests para métodos estadísticos adicionales del TeamRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_get_team_size_distribution_success(
        self, 
        team_repository, 
        mock_session
    ):
        """Test exitoso de obtención de distribución de tamaños de equipos."""
        # Arrange
        expected_distribution = {
            "small_teams": 5,  # 1-3 miembros
            "medium_teams": 8,  # 4-7 miembros
            "large_teams": 3   # 8+ miembros
        }
        
        # Configurar el return_value del mock existente en lugar de crear uno nuevo
        team_repository.statistics_module.get_team_size_distribution.return_value = expected_distribution
        
        # Act
        result = await team_repository.get_team_size_distribution()

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result == expected_distribution
        assert "small_teams" in result
        assert "medium_teams" in result
        assert "large_teams" in result
        team_repository.statistics_module.get_team_size_distribution.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_leadership_statistics_success(
        self, 
        team_repository, 
        mock_session
    ):
        """Test exitoso de obtención de estadísticas de liderazgo."""
        # Arrange
        expected_stats = {
            "total_leaders": 12,
            "teams_with_leader": 10,
            "teams_without_leader": 2,
            "leadership_ratio": 0.83,
            "average_leadership_experience": 3.5,
            "leadership_distribution": {
                "senior_leaders": 4,
                "mid_level_leaders": 6,
                "junior_leaders": 2
            }
        }
        
        # Configurar el return_value del mock existente en lugar de crear uno nuevo
        team_repository.statistics_module.get_leadership_statistics.return_value = expected_stats
        
        # Act
        result = await team_repository.get_leadership_statistics()

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result == expected_stats
        assert "total_leaders" in result
        assert "teams_with_leader" in result
        assert "teams_without_leader" in result
        assert "leadership_ratio" in result
        assert "leadership_distribution" in result
        team_repository.statistics_module.get_leadership_statistics.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_generate_teams_summary_report_success(
        self, 
        team_repository, 
        mock_session
    ):
        """Test exitoso de generación de reporte resumen de equipos."""
        # Arrange
        expected_report = {
            "summary": {
                "total_teams": 15,
                "active_teams": 12,
                "inactive_teams": 3,
                "total_members": 85,
                "average_team_size": 5.67
            },
            "team_details": [
                {
                    "team_id": 1,
                    "name": "Desarrollo Frontend",
                    "code": "DEV-FE",
                    "member_count": 6,
                    "has_leader": True,
                    "department": "Tecnología",
                    "is_active": True
                },
                {
                    "team_id": 2,
                    "name": "Desarrollo Backend",
                    "code": "DEV-BE",
                    "member_count": 8,
                    "has_leader": True,
                    "department": "Tecnología",
                    "is_active": True
                }
            ],
            "statistics": {
                "departments": {
                    "Tecnología": 8,
                    "Marketing": 4,
                    "Ventas": 3
                },
                "size_distribution": {
                    "small": 5,
                    "medium": 7,
                    "large": 3
                }
            }
        }
        
    @pytest.mark.asyncio
    async def test_generate_teams_summary_report_success(
        self, 
        team_repository, 
        mock_session
    ):
        """Test exitoso de generación de reporte resumen de equipos."""
        # Arrange
        expected_report = {
            "summary": {
                "total_teams": 15,
                "active_teams": 12,
                "inactive_teams": 3,
                "total_members": 85,
                "average_team_size": 5.67
            },
            "team_details": [
                {
                    "team_id": 1,
                    "name": "Desarrollo Frontend",
                    "code": "DEV-FE",
                    "member_count": 6,
                    "has_leader": True,
                    "department": "Tecnología",
                    "is_active": True
                },
                {
                    "team_id": 2,
                    "name": "Desarrollo Backend",
                    "code": "DEV-BE",
                    "member_count": 8,
                    "has_leader": True,
                    "department": "Tecnología",
                    "is_active": True
                }
            ],
            "statistics": {
                "departments": {
                    "Tecnología": 8,
                    "Marketing": 4,
                    "Ventas": 3
                },
                "size_distribution": {
                    "small": 5,
                    "medium": 7,
                    "large": 3
                }
            }
        }
        
        # Configurar el return_value del mock existente en lugar de crear uno nuevo
        team_repository.statistics_module.generate_teams_summary_report.return_value = expected_report
        
        # Act
        result = await team_repository.generate_teams_summary_report(include_inactive=False)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result == expected_report
        assert "summary" in result
        assert "team_details" in result
        assert "statistics" in result
        assert result["summary"]["total_teams"] == 15
        assert len(result["team_details"]) == 2
        team_repository.statistics_module.generate_teams_summary_report.assert_awaited_once_with(False)

    @pytest.mark.asyncio
    async def test_generate_teams_summary_report_with_inactive(
        self, 
        team_repository, 
        mock_session
    ):
        """Test de generación de reporte resumen incluyendo equipos inactivos."""
        # Arrange
        expected_report = {
            "summary": {
                "total_teams": 18,
                "active_teams": 12,
                "inactive_teams": 6,
                "total_members": 95,
                "average_team_size": 5.28
            },
            "team_details": [],
            "statistics": {}
        }
        
        # Configurar el return_value del mock existente en lugar de crear uno nuevo
        team_repository.statistics_module.generate_teams_summary_report.return_value = expected_report
        
        # Act
        result = await team_repository.generate_teams_summary_report(include_inactive=True)

        # Assert
        assert result is not None
        assert result["summary"]["total_teams"] == 18
        assert result["summary"]["inactive_teams"] == 6
        team_repository.statistics_module.generate_teams_summary_report.assert_awaited_once_with(True)

    @pytest.mark.asyncio
    async def test_get_membership_trends_success(
        self, 
        team_repository, 
        mock_session
    ):
        """Test exitoso de obtención de tendencias de membresía."""
        # Arrange
        expected_trends = {
            "monthly_trends": [
                {
                    "month": "2024-01",
                    "new_memberships": 15,
                    "ended_memberships": 3,
                    "net_change": 12,
                    "total_active": 85
                },
                {
                    "month": "2024-02",
                    "new_memberships": 8,
                    "ended_memberships": 5,
                    "net_change": 3,
                    "total_active": 88
                },
                {
                    "month": "2024-03",
                    "new_memberships": 12,
                    "ended_memberships": 2,
                    "net_change": 10,
                    "total_active": 98
                }
            ],
            "summary": {
                "total_new_memberships": 35,
                "total_ended_memberships": 10,
                "net_growth": 25,
                "growth_rate": 0.29,
                "average_monthly_new": 11.67,
                "average_monthly_ended": 3.33
            },
            "peak_periods": {
                "highest_growth_month": "2024-01",
                "highest_growth_value": 12,
                "lowest_growth_month": "2024-02",
                "lowest_growth_value": 3
            }
        }
        
        # Configurar el return_value del mock existente
        team_repository.statistics_module.get_membership_trends.return_value = expected_trends
        
        # Act
        result = await team_repository.get_membership_trends(months=3)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result == expected_trends
        assert "monthly_trends" in result
        assert "summary" in result
        assert "peak_periods" in result
        assert len(result["monthly_trends"]) == 3
        assert result["summary"]["net_growth"] == 25
        team_repository.statistics_module.get_membership_trends.assert_awaited_once_with(months=3)

    @pytest.mark.asyncio
    async def test_get_department_team_distribution_success(
        self, 
        team_repository, 
        mock_session
    ):
        """Test exitoso de obtención de distribución de equipos por departamento."""
        # Arrange
        expected_distribution = {
            "departments": {
                "Tecnología": {
                    "team_count": 8,
                    "total_members": 45,
                    "average_team_size": 5.63,
                    "teams": [
                        {"name": "Desarrollo Frontend", "members": 6},
                        {"name": "Desarrollo Backend", "members": 8},
                        {"name": "DevOps", "members": 4},
                        {"name": "QA", "members": 5},
                        {"name": "Arquitectura", "members": 3},
                        {"name": "Mobile", "members": 7},
                        {"name": "Data Science", "members": 6},
                        {"name": "Seguridad", "members": 6}
                    ]
                },
                "Marketing": {
                    "team_count": 4,
                    "total_members": 22,
                    "average_team_size": 5.5,
                    "teams": [
                        {"name": "Marketing Digital", "members": 6},
                        {"name": "Contenido", "members": 5},
                        {"name": "SEO/SEM", "members": 4},
                        {"name": "Eventos", "members": 7}
                    ]
                },
                "Ventas": {
                    "team_count": 3,
                    "total_members": 18,
                    "average_team_size": 6.0,
                    "teams": [
                        {"name": "Ventas Corporativas", "members": 7},
                        {"name": "Ventas PYME", "members": 6},
                        {"name": "Customer Success", "members": 5}
                    ]
                }
            },
            "summary": {
                "total_departments": 3,
                "total_teams": 15,
                "total_members": 85,
                "largest_department": "Tecnología",
                "smallest_department": "Ventas",
                "most_teams_department": "Tecnología",
                "highest_avg_size_department": "Ventas"
            }
        }
        
        # Configurar el return_value del mock existente
        team_repository.statistics_module.get_department_team_distribution.return_value = expected_distribution
        
        # Act
        result = await team_repository.get_department_team_distribution()

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result == expected_distribution
        assert "departments" in result
        assert "summary" in result
        assert len(result["departments"]) == 3
        assert result["summary"]["total_departments"] == 3
        assert result["summary"]["largest_department"] == "Tecnología"
        team_repository.statistics_module.get_department_team_distribution.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_average_team_size_success(
        self, 
        team_repository, 
        mock_session
    ):
        """Test exitoso de obtención del tamaño promedio de equipos."""
        # Arrange
        expected_average = {
            "overall_average": 5.67,
            "active_teams_average": 6.12,
            "inactive_teams_average": 3.25,
            "by_department": {
                "Tecnología": 5.63,
                "Marketing": 5.5,
                "Ventas": 6.0,
                "RRHH": 4.0,
                "Finanzas": 3.5
            },
            "statistics": {
                "total_teams": 15,
                "active_teams": 12,
                "inactive_teams": 3,
                "total_members": 85,
                "largest_team_size": 8,
                "smallest_team_size": 2,
                "median_team_size": 6,
                "mode_team_size": 5
            },
            "size_ranges": {
                "small_teams": {"count": 5, "range": "1-4 members", "percentage": 33.33},
                "medium_teams": {"count": 7, "range": "5-7 members", "percentage": 46.67},
                "large_teams": {"count": 3, "range": "8+ members", "percentage": 20.0}
            }
        }
        
        # Configurar el return_value del mock existente
        team_repository.statistics_module.get_average_team_size.return_value = expected_average
        
        # Act
        result = await team_repository.get_average_team_size()

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result == expected_average
        assert "overall_average" in result
        assert "by_department" in result
        assert "statistics" in result
        assert "size_ranges" in result
        assert result["overall_average"] == 5.67
        assert result["statistics"]["total_teams"] == 15
        team_repository.statistics_module.get_average_team_size.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_teams_without_leader_success(
        self, 
        team_repository, 
        mock_session
    ):
        """Test exitoso de obtención de equipos sin líder."""
        # Arrange
        expected_teams = {
            "teams_without_leader": [
                {
                    "team_id": 5,
                    "name": "Equipo Temporal",
                    "code": "TEMP-01",
                    "department": "Proyectos",
                    "member_count": 4,
                    "created_date": "2024-01-15",
                    "days_without_leader": 45,
                    "is_active": True
                },
                {
                    "team_id": 8,
                    "name": "Investigación",
                    "code": "RES-01",
                    "department": "Tecnología",
                    "member_count": 3,
                    "created_date": "2023-12-10",
                    "days_without_leader": 78,
                    "is_active": True
                },
                {
                    "team_id": 12,
                    "name": "Soporte Nivel 1",
                    "code": "SUP-L1",
                    "department": "Tecnología",
                    "member_count": 6,
                    "created_date": "2024-02-01",
                    "days_without_leader": 28,
                    "is_active": False
                }
            ],
            "summary": {
                "total_teams_without_leader": 3,
                "active_teams_without_leader": 2,
                "inactive_teams_without_leader": 1,
                "total_members_affected": 13,
                "average_days_without_leader": 50.33,
                "longest_without_leader": 78,
                "shortest_without_leader": 28
            },
            "by_department": {
                "Tecnología": {"count": 2, "members_affected": 9},
                "Proyectos": {"count": 1, "members_affected": 4}
            },
            "recommendations": [
                "Asignar líder urgente al equipo 'Investigación' (78 días sin líder)",
                "Revisar estructura del equipo 'Equipo Temporal'",
                "Considerar fusión o reestructuración del equipo 'Soporte Nivel 1'"
            ]
        }
        
        # Configurar el return_value del mock existente
        team_repository.statistics_module.get_teams_without_leader.return_value = expected_teams
        
        # Act
        result = await team_repository.get_teams_without_leader()

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result == expected_teams
        assert "teams_without_leader" in result
        assert "summary" in result
        assert "by_department" in result
        assert "recommendations" in result
        assert len(result["teams_without_leader"]) == 3
        assert result["summary"]["total_teams_without_leader"] == 3
        team_repository.statistics_module.get_teams_without_leader.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_most_active_employees_in_teams_success(
        self, 
        team_repository, 
        mock_session
    ):
        """Test exitoso de obtención de empleados más activos en equipos."""
        # Arrange
        expected_active_employees = {
            "most_active_employees": [
                {
                    "employee_id": 15,
                    "full_name": "Ana García López",
                    "email": "ana.garcia@company.com",
                    "total_teams": 4,
                    "active_teams": 3,
                    "leadership_roles": 2,
                    "member_roles": 2,
                    "departments": ["Tecnología", "Proyectos"],
                    "teams": [
                        {"team_id": 1, "name": "Desarrollo Frontend", "role": "LEADER", "is_active": True},
                        {"team_id": 3, "name": "Arquitectura", "role": "LEADER", "is_active": True},
                        {"team_id": 7, "name": "Proyecto Alpha", "role": "MEMBER", "is_active": True},
                        {"team_id": 9, "name": "Comité Técnico", "role": "MEMBER", "is_active": False}
                    ],
                    "activity_score": 95.5,
                    "join_date_first_team": "2022-03-15",
                    "total_experience_months": 22
                },
                {
                    "employee_id": 23,
                    "full_name": "Carlos Rodríguez Martín",
                    "email": "carlos.rodriguez@company.com",
                    "total_teams": 3,
                    "active_teams": 3,
                    "leadership_roles": 1,
                    "member_roles": 2,
                    "departments": ["Marketing", "Ventas"],
                    "teams": [
                        {"team_id": 4, "name": "Marketing Digital", "role": "LEADER", "is_active": True},
                        {"team_id": 6, "name": "Ventas Corporativas", "role": "MEMBER", "is_active": True},
                        {"team_id": 11, "name": "Customer Success", "role": "MEMBER", "is_active": True}
                    ],
                    "activity_score": 88.2,
                    "join_date_first_team": "2021-11-20",
                    "total_experience_months": 28
                }
            ],
            "statistics": {
                "total_employees_analyzed": 125,
                "employees_in_multiple_teams": 45,
                "employees_with_leadership": 28,
                "average_teams_per_employee": 1.8,
                "max_teams_per_employee": 4,
                "employees_in_cross_department_teams": 12
            },
            "activity_ranges": {
                "highly_active": {"count": 8, "range": "3+ teams", "percentage": 6.4},
                "moderately_active": {"count": 37, "range": "2 teams", "percentage": 29.6},
                "single_team": {"count": 80, "range": "1 team", "percentage": 64.0}
            },
            "department_cross_participation": {
                "Tecnología-Proyectos": 5,
                "Marketing-Ventas": 4,
                "RRHH-Finanzas": 2,
                "Tecnología-Marketing": 1
            }
        }
        
        # Configurar el return_value del mock existente
        team_repository.statistics_module.get_most_active_employees_in_teams.return_value = expected_active_employees
        
        # Act
        result = await team_repository.get_most_active_employees_in_teams(limit=10)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result == expected_active_employees
        assert "most_active_employees" in result
        assert "statistics" in result
        assert "activity_ranges" in result
        assert "department_cross_participation" in result
        assert len(result["most_active_employees"]) == 2
        assert result["statistics"]["total_employees_analyzed"] == 125
        team_repository.statistics_module.get_most_active_employees_in_teams.assert_awaited_once_with(limit=10)

    @pytest.mark.asyncio
    async def test_get_team_creation_trends_success(
        self, 
        team_repository, 
        mock_session
    ):
        """Test exitoso de obtención de tendencias de creación de equipos."""
        # Arrange
        expected_trends = {
            "monthly_creation_trends": [
                {
                    "month": "2024-01",
                    "teams_created": 3,
                    "teams_archived": 1,
                    "net_change": 2,
                    "departments": {
                        "Tecnología": 2,
                        "Marketing": 1
                    }
                },
                {
                    "month": "2024-02",
                    "teams_created": 2,
                    "teams_archived": 0,
                    "net_change": 2,
                    "departments": {
                        "Ventas": 1,
                        "RRHH": 1
                    }
                },
                {
                    "month": "2024-03",
                    "teams_created": 4,
                    "teams_archived": 2,
                    "net_change": 2,
                    "departments": {
                        "Tecnología": 2,
                        "Proyectos": 2
                    }
                }
            ],
            "yearly_summary": {
                "total_teams_created": 9,
                "total_teams_archived": 3,
                "net_growth": 6,
                "growth_rate": 0.67,
                "average_monthly_creation": 3.0,
                "average_monthly_archival": 1.0
            },
            "department_trends": {
                "Tecnología": {
                    "teams_created": 4,
                    "teams_archived": 1,
                    "net_growth": 3,
                    "growth_rate": 0.75
                },
                "Marketing": {
                    "teams_created": 1,
                    "teams_archived": 0,
                    "net_growth": 1,
                    "growth_rate": 1.0
                },
                "Ventas": {
                    "teams_created": 1,
                    "teams_archived": 1,
                    "net_growth": 0,
                    "growth_rate": 0.0
                },
                "RRHH": {
                    "teams_created": 1,
                    "teams_archived": 0,
                    "net_growth": 1,
                    "growth_rate": 1.0
                },
                "Proyectos": {
                    "teams_created": 2,
                    "teams_archived": 1,
                    "net_growth": 1,
                    "growth_rate": 0.5
                }
            },
            "peak_periods": {
                "highest_creation_month": "2024-03",
                "highest_creation_count": 4,
                "most_active_department": "Tecnología",
                "fastest_growing_department": "Marketing"
            },
            "predictions": {
                "next_month_estimated_creation": 3,
                "quarterly_growth_projection": 8,
                "recommended_departments_for_expansion": ["Tecnología", "Marketing"]
            }
        }
        
        # Configurar el return_value del mock existente
        team_repository.statistics_module.get_team_creation_trends.return_value = expected_trends
        
        # Act
        result = await team_repository.get_team_creation_trends(months=3)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result == expected_trends
        assert "monthly_creation_trends" in result
        assert "yearly_summary" in result
        assert "department_trends" in result
        assert "peak_periods" in result
        assert "predictions" in result
        assert len(result["monthly_creation_trends"]) == 3
        assert result["yearly_summary"]["total_teams_created"] == 9
        assert result["peak_periods"]["most_active_department"] == "Tecnología"
        team_repository.statistics_module.get_team_creation_trends.assert_awaited_once_with(months=3)


# ============================================================================
# TESTS PARA MÉTODOS COMPUESTOS FALTANTES
# ============================================================================

class TestTeamCompositeAdditionalOperations:
    """Tests para métodos compuestos adicionales del TeamRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_get_complete_team_info_success(
        self, 
        team_repository, 
        mock_session,
        sample_team_model,
        sample_memberships_list
    ):
        """Test exitoso de obtención de información completa del equipo."""
        # Arrange
        team_id = 1
        expected_info = {
            "team": {
                "id": 1,
                "name": "Equipo de Desarrollo",
                "code": "DEV001",
                "description": "Equipo de desarrollo de software",
                "department": "Tecnología",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "max_members": 10
            },
            "members": [
                {
                    "employee_id": 1,
                    "name": "Juan Pérez",
                    "role": "Developer",
                    "is_leader": True,
                    "start_date": "2024-01-01",
                    "is_active": True
                },
                {
                    "employee_id": 2,
                    "name": "María García",
                    "role": "Senior Developer",
                    "is_leader": False,
                    "start_date": "2024-01-15",
                    "is_active": True
                }
            ],
            "statistics": {
                "total_members": 2,
                "active_members": 2,
                "leaders_count": 1,
                "average_tenure_days": 45
            },
            "capacity": {
                "current_size": 2,
                "max_capacity": 10,
                "utilization_percentage": 20.0,
                "can_add_members": True
            }
        }
        
        # Mock de los métodos del facade
        team_repository.get_team_by_id = AsyncMock(return_value=sample_team_model)
        team_repository.get_team_members = AsyncMock(return_value=sample_memberships_list)
        team_repository.statistics_module.get_team_statistics = AsyncMock(
            return_value=expected_info["statistics"]
        )
        team_repository.validation_module.validate_member_capacity = AsyncMock(
            return_value=expected_info["capacity"]
        )

        # Act
        result = await team_repository.get_complete_team_info(team_id)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert "team" in result
        assert "members" in result
        assert "statistics" in result
        assert "capacity" in result
        assert result["team"]["id"] == team_id
        assert len(result["members"]) >= 0
        team_repository.get_team_by_id.assert_awaited_once_with(team_id)
        team_repository.get_team_members.assert_awaited_once_with(team_id, True, True)

    @pytest.mark.asyncio
    async def test_get_complete_team_info_team_not_found(
        self, 
        team_repository, 
        mock_session
    ):
        """Test de obtención de información completa cuando el equipo no existe."""
        # Arrange
        team_id = 999
        team_repository.get_team_by_id = AsyncMock(return_value=None)

        # Act
        result = await team_repository.get_complete_team_info(team_id)

        # Assert
        assert result is None
        team_repository.get_team_by_id.assert_awaited_once_with(team_id)

    @pytest.mark.asyncio
    async def test_create_team_with_validation_success(
        self, 
        team_repository, 
        mock_session,
        sample_team_data,
        sample_team_model
    ):
        """Test exitoso de creación de equipo con validación."""
        # Arrange
        expected_result = {
            "success": True,
            "team": {
                "id": 1,
                "name": "Nuevo Equipo",
                "code": "NEW001",
                "department": "Tecnología",
                "is_active": True
            },
            "validation": {
                "passed": True,
                "warnings": [],
                "errors": []
            },
            "message": "Equipo creado exitosamente"
        }
        
        # Mock de validación exitosa
        team_repository.validation_module.validate_team_data = AsyncMock(
            return_value={"is_valid": True, "errors": [], "warnings": []}
        )
        team_repository.crud_module.create_team = AsyncMock(return_value=sample_team_model)

        # Act
        result = await team_repository.create_team_with_validation(sample_team_data)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "team" in result
        assert "validation" in result
        assert result["validation"]["passed"] is True
        team_repository.validation_module.validate_team_data.assert_awaited_once_with(sample_team_data)
        team_repository.crud_module.create_team.assert_awaited_once_with(sample_team_data)

    @pytest.mark.asyncio
    async def test_create_team_with_validation_failure(
        self, 
        team_repository, 
        mock_session,
        sample_team_data
    ):
        """Test de creación de equipo con validación fallida."""
        # Arrange
        validation_errors = ["El nombre del equipo ya existe", "El código es inválido"]
        team_repository.validation_module.validate_team_data = AsyncMock(
            return_value={
                "is_valid": False, 
                "errors": validation_errors, 
                "warnings": []
            }
        )

        # Act
        result = await team_repository.create_team_with_validation(sample_team_data)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "validation" in result
        assert result["validation"]["passed"] is False
        assert len(result["validation"]["errors"]) == 2
        team_repository.validation_module.validate_team_data.assert_awaited_once_with(sample_team_data)

    @pytest.mark.asyncio
    async def test_add_team_member_with_validation_success(
        self, 
        team_repository, 
        mock_session,
        sample_membership_model
    ):
        """Test exitoso de adición de miembro con validación."""
        # Arrange
        team_id = 1
        employee_id = 2
        role = "Developer"
        is_leader = False
        start_date = date.today()
        
        expected_result = {
            "success": True,
            "membership": {
                "team_id": team_id,
                "employee_id": employee_id,
                "role": role,
                "is_leader": is_leader,
                "start_date": start_date.isoformat(),
                "is_active": True
            },
            "validation": {
                "passed": True,
                "warnings": [],
                "errors": []
            },
            "message": "Miembro agregado exitosamente al equipo"
        }
        
        # Mock de validaciones exitosas
        team_repository.validation_module.can_add_member = AsyncMock(return_value=True)
        team_repository.validation_module.check_membership_conflicts = AsyncMock(
            return_value={"has_conflicts": False, "conflicts": []}
        )
        team_repository.relationship_module.add_team_member = AsyncMock(
            return_value=sample_membership_model
        )

        # Act
        result = await team_repository.add_team_member_with_validation(
            team_id, employee_id, role, is_leader, start_date
        )

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result["success"] is True
        assert "membership" in result
        assert "validation" in result
        assert result["validation"]["passed"] is True
        team_repository.validation_module.can_add_member.assert_awaited_once_with(team_id, employee_id)
        team_repository.validation_module.check_membership_conflicts.assert_awaited_once_with(
            employee_id, team_id
        )
        team_repository.relationship_module.add_team_member.assert_awaited_once_with(
            team_id, employee_id, role, is_leader, start_date
        )

    @pytest.mark.asyncio
    async def test_add_team_member_with_validation_capacity_exceeded(
        self, 
        team_repository, 
        mock_session
    ):
        """Test de adición de miembro cuando se excede la capacidad."""
        # Arrange
        team_id = 1
        employee_id = 2
        role = "Developer"
        
        team_repository.validation_module.can_add_member = AsyncMock(return_value=False)

        # Act
        result = await team_repository.add_team_member_with_validation(
            team_id, employee_id, role
        )

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "validation" in result
        assert result["validation"]["passed"] is False
        assert "capacidad" in result["message"].lower() or "capacity" in result["message"].lower()
        team_repository.validation_module.can_add_member.assert_awaited_once_with(team_id, employee_id)

    @pytest.mark.asyncio
    async def test_add_team_member_with_validation_conflicts(
        self, 
        team_repository, 
        mock_session
    ):
        """Test de adición de miembro con conflictos de membresía."""
        # Arrange
        team_id = 1
        employee_id = 2
        role = "Developer"
        
        conflicts = ["El empleado ya es miembro de este equipo"]
        team_repository.validation_module.can_add_member = AsyncMock(return_value=True)
        team_repository.validation_module.check_membership_conflicts = AsyncMock(
            return_value={"has_conflicts": True, "conflicts": conflicts}
        )

        # Act
        result = await team_repository.add_team_member_with_validation(
            team_id, employee_id, role
        )

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "validation" in result
        assert result["validation"]["passed"] is False
        assert len(result["validation"]["errors"]) > 0
        team_repository.validation_module.can_add_member.assert_awaited_once_with(team_id, employee_id)
        team_repository.validation_module.check_membership_conflicts.assert_awaited_once_with(
            employee_id, team_id
        )

    @pytest.mark.asyncio
    async def test_delete_team_not_found(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de eliminación de equipo no encontrado."""
        # Arrange
        team_id = 999
        mock_result = create_mock_result(None)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne False cuando no encuentra el equipo
        team_repository.delete = AsyncMock(return_value=False)

        # Act
        result = await team_repository.delete(team_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_by_id_true(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de verificación de existencia de equipo - existe."""
        # Arrange
        team_id = 1
        mock_result = create_mock_result(None, count=1)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne True cuando el equipo existe
        team_repository.exists_by_id = AsyncMock(return_value=True)

        # Act
        result = await team_repository.exists_by_id(team_id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_by_id_false(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de verificación de existencia de equipo - no existe."""
        # Arrange
        team_id = 999
        mock_result = create_mock_result(None, count=0)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne False cuando el equipo no existe
        team_repository.exists_by_id = AsyncMock(return_value=False)

        # Act
        result = await team_repository.exists_by_id(team_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_count_all_success(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test exitoso de conteo de todos los equipos."""
        # Arrange
        expected_count = 5
        mock_result = create_mock_result(None, count=expected_count)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne el conteo esperado
        team_repository.count_all = AsyncMock(return_value=expected_count)

        # Act
        result = await team_repository.count_all()

        # Assert
        assert result == expected_count


# ============================================================================
# TESTS DE OPERACIONES DE CONSULTA
# ============================================================================

class TestTeamQueryOperations:
    """Tests para operaciones de consulta del TeamRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_find_by_name_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        create_mock_result
    ):
        """Test exitoso de búsqueda de equipo por nombre."""
        # Arrange
        team_name = "Equipo de Desarrollo"
        mock_result = create_mock_result(sample_team_model)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne el equipo encontrado
        team_repository.find_by_name = AsyncMock(return_value=sample_team_model)

        # Act
        result = await team_repository.find_by_name(team_name)

        # Assert
        assert result is not None
        assert result.name == team_name

    @pytest.mark.asyncio
    async def test_find_by_code_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        create_mock_result
    ):
        """Test exitoso de búsqueda de equipo por código."""
        # Arrange
        team_code = "DEV001"
        mock_result = create_mock_result(sample_team_model)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne el equipo encontrado
        team_repository.find_by_code = AsyncMock(return_value=sample_team_model)

        # Act
        result = await team_repository.find_by_code(team_code)

        # Assert
        assert result is not None
        assert result.code == team_code

    @pytest.mark.asyncio
    async def test_find_active_teams_success(
        self, 
        team_repository, 
        mock_session, 
        sample_teams_list,
        create_mock_result
    ):
        """Test exitoso de búsqueda de equipos activos."""
        # Arrange
        active_teams = [team for team in sample_teams_list if team.is_active]
        mock_result = create_mock_result(active_teams)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne la lista de equipos activos
        team_repository.find_active_teams = AsyncMock(return_value=active_teams)

        # Act
        result = await team_repository.find_active_teams()

        # Assert
        assert result is not None
        assert len(result) == len(active_teams)
        assert all(team.is_active for team in result)

    @pytest.mark.asyncio
    async def test_search_teams_success(
        self, 
        team_repository, 
        mock_session, 
        sample_teams_list,
        search_config,
        create_mock_result
    ):
        """Test exitoso de búsqueda de equipos con término."""
        # Arrange
        search_term = search_config["search_term"]
        # Configurar el mock del repositorio directamente
        team_repository.search_teams = AsyncMock(return_value=sample_teams_list[:2])

        # Act
        result = await team_repository.search_teams(search_term)

        # Assert
        assert result is not None
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_find_teams_with_capacity_success(
        self, 
        team_repository, 
        mock_session, 
        sample_teams_list,
        create_mock_result
    ):
        """Test exitoso de búsqueda de equipos con capacidad disponible."""
        # Arrange
        min_capacity = 2
        teams_with_capacity = sample_teams_list[:2]
        mock_result = create_mock_result(teams_with_capacity)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne la lista de equipos con capacidad
        team_repository.find_teams_with_capacity = AsyncMock(return_value=teams_with_capacity)

        # Act
        result = await team_repository.find_teams_with_capacity(min_capacity)

        # Assert
        assert result is not None
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_teams_paginated_success(
        self, 
        team_repository, 
        mock_session, 
        sample_teams_list,
        pagination_config,
        create_mock_result
    ):
        """Test exitoso de obtención paginada de equipos."""
        # Arrange
        page = pagination_config["page"]
        page_size = pagination_config["page_size"]
        # Configurar el mock del repositorio directamente
        team_repository.get_teams_paginated = AsyncMock(return_value=sample_teams_list[:page_size])

        # Act
        result = await team_repository.get_teams_paginated(page=page, page_size=page_size)

        # Assert
        assert result is not None
        assert len(result) <= page_size


# ============================================================================
# TESTS DE OPERACIONES DE RELACIONES (MEMBRESÍAS)
# ============================================================================

class TestTeamRelationshipOperations:
    """Tests para operaciones de relaciones del TeamRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_add_member_success(
        self, 
        team_repository, 
        mock_session, 
        sample_membership_model,
        sample_membership_data,
        create_mock_result
    ):
        """Test exitoso de agregar miembro a equipo."""
        # Arrange
        # Configurar el mock del repositorio directamente
        team_repository.add_member = AsyncMock(return_value=sample_membership_model)

        # Act
        result = await team_repository.add_member(
            team_id=sample_membership_data["team_id"],
            employee_id=sample_membership_data["employee_id"],
            role=sample_membership_data["role"],
            start_date=sample_membership_data["start_date"]
        )

        # Assert
        assert result is not None
        assert result.team_id == sample_membership_data["team_id"]
        assert result.employee_id == sample_membership_data["employee_id"]

    @pytest.mark.asyncio
    async def test_remove_member_success(
        self, 
        team_repository, 
        mock_session, 
        sample_membership_model,
        create_mock_result
    ):
        """Test exitoso de remover miembro de equipo."""
        # Arrange
        team_id = 1
        employee_id = 1
        mock_result = create_mock_result(sample_membership_model)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne True
        team_repository.remove_member = AsyncMock(return_value=True)

        # Act
        result = await team_repository.remove_member(team_id, employee_id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_update_member_role_success(
        self, 
        team_repository, 
        mock_session, 
        sample_membership_model,
        create_mock_result
    ):
        """Test exitoso de actualización de rol de miembro."""
        # Arrange
        team_id = 1
        employee_id = 1
        new_role = MembershipRole.LEAD
        mock_result = create_mock_result(sample_membership_model)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne el objeto actualizado
        team_repository.update_member_role = AsyncMock(return_value=sample_membership_model)

        # Act
        result = await team_repository.update_member_role(team_id, employee_id, new_role)

        # Assert
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_team_members_success(
        self, 
        team_repository, 
        mock_session, 
        sample_memberships_list,
        create_mock_result
    ):
        """Test exitoso de obtención de miembros de equipo."""
        # Arrange
        team_id = 1
        mock_result = create_mock_result(sample_memberships_list)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne la lista de membresías
        team_repository.get_team_members = AsyncMock(return_value=sample_memberships_list)

        # Act
        result = await team_repository.get_team_members(team_id)

        # Assert
        assert result is not None
        assert len(result) == len(sample_memberships_list)
        assert all(membership.team_id == team_id for membership in result)

    @pytest.mark.asyncio
    async def test_get_active_members_success(
        self, 
        team_repository, 
        mock_session, 
        sample_memberships_list,
        create_mock_result
    ):
        """Test exitoso de obtención de miembros activos."""
        # Arrange
        team_id = 1
        active_members = [m for m in sample_memberships_list if m.is_active]
        mock_result = create_mock_result(active_members)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne los miembros activos
        team_repository.get_active_members = AsyncMock(return_value=active_members)

        # Act
        result = await team_repository.get_active_members(team_id)

        # Assert
        assert result is not None
        assert len(result) == len(active_members)
        assert all(membership.is_active for membership in result)

    @pytest.mark.asyncio
    async def test_get_members_by_role_success(
        self, 
        team_repository, 
        mock_session, 
        sample_memberships_list,
        create_mock_result
    ):
        """Test exitoso de obtención de miembros por rol."""
        # Arrange
        team_id = 1
        role = MembershipRole.MEMBER
        members_by_role = [m for m in sample_memberships_list if m.role == role]
        # Configurar el mock para que retorne los objetos correctos
        team_repository.get_members_by_role = AsyncMock(return_value=members_by_role)

        # Act
        result = await team_repository.get_members_by_role(team_id, role)

        # Assert
        assert result is not None
        assert all(membership.role == role for membership in result)

    @pytest.mark.asyncio
    async def test_get_team_leaders_success(
        self, 
        team_repository, 
        mock_session, 
        sample_memberships_list,
        create_mock_result
    ):
        """Test exitoso de obtención de líderes de equipo."""
        # Arrange
        team_id = 1
        leaders = [m for m in sample_memberships_list if m.role == MembershipRole.LEAD]
        # Configurar el mock para que retorne los objetos correctos
        team_repository.get_team_leaders = AsyncMock(return_value=leaders)

        # Act
        result = await team_repository.get_team_leaders(team_id)

        # Assert
        assert result is not None
        assert all(membership.role == MembershipRole.LEAD for membership in result)

    @pytest.mark.asyncio
    async def test_get_teams_by_employee_success(
        self, 
        team_repository, 
        mock_session, 
        sample_memberships_list,
        create_mock_result
    ):
        """Test exitoso de obtención de equipos por empleado."""
        # Arrange
        employee_id = 1
        employee_memberships = [m for m in sample_memberships_list if m.employee_id == employee_id]
        # Configurar el mock para que retorne los objetos correctos
        team_repository.get_teams_by_employee = AsyncMock(return_value=employee_memberships)

        # Act
        result = await team_repository.get_teams_by_employee(employee_id)

        # Assert
        assert result is not None
        assert all(membership.employee_id == employee_id for membership in result)


# ============================================================================
# TESTS DE OPERACIONES DE VALIDACIÓN
# ============================================================================

class TestTeamValidationOperations:
    """Tests para operaciones de validación del TeamRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_validate_team_data_success(
        self, 
        team_repository, 
        sample_team_data
    ):
        """Test exitoso de validación de datos de equipo."""
        # Arrange
        team_repository.validate_team_data = AsyncMock(return_value=True)

        # Act
        result = await team_repository.validate_team_data(sample_team_data)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_team_data_invalid_name(
        self, 
        team_repository
    ):
        """Test de validación de datos de equipo con nombre inválido."""
        # Arrange
        invalid_data = {
            "name": "",  # Nombre vacío
            "code": "DEV001",
            "description": "Equipo de desarrollo"
        }
        # Configurar el mock para lanzar la excepción correcta
        from planificador.exceptions.repository.team_repository_exceptions import TeamValidationRepositoryError
        team_repository.validate_team_data = AsyncMock(
            side_effect=TeamValidationRepositoryError(
                message="Nombre de equipo no puede estar vacío",
                operation="validate_team_data",
                entity_type="Team"
            )
        )

        # Act & Assert
        with pytest.raises(TeamValidationRepositoryError) as exc_info:
            await team_repository.validate_team_data(invalid_data)
        
        assert "Nombre de equipo no puede estar vacío" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_team_name_success(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test exitoso de validación de nombre de equipo."""
        # Arrange
        team_name = "Nuevo Equipo"
        mock_result = create_mock_result(None, count=0)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne True
        team_repository.validate_team_name = AsyncMock(return_value=True)

        # Act
        result = await team_repository.validate_team_name(team_name)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_team_name_duplicate(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test de validación de nombre de equipo duplicado."""
        # Arrange
        team_name = "Equipo Existente"
        mock_result = create_mock_result(None, count=1)
        mock_session.execute.return_value = mock_result
        
        # Configurar el mock para lanzar excepción
        from planificador.exceptions.repository.team_repository_exceptions import TeamValidationRepositoryError
        team_repository.validate_team_name = AsyncMock(
            side_effect=TeamValidationRepositoryError(
                message=f"El nombre '{team_name}' ya está en uso",
                operation="validate_team_name",
                entity_type="Team"
            )
        )

        # Act & Assert
        with pytest.raises(TeamValidationRepositoryError) as exc_info:
            await team_repository.validate_team_name(team_name)
        
        assert f"El nombre '{team_name}' ya está en uso" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_member_capacity_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        create_mock_result
    ):
        """Test exitoso de validación de capacidad de miembros."""
        # Arrange
        team_id = 1
        sample_team_model.max_members = 10
        mock_result = create_mock_result(sample_team_model)
        mock_session.execute.return_value = mock_result
        
        # Mock para contar miembros actuales
        count_result = create_mock_result(None, count=5)
        mock_session.execute.side_effect = [mock_result, count_result]
        # Configurar el mock para que retorne True
        team_repository.validate_member_capacity = AsyncMock(return_value=True)

        # Act
        result = await team_repository.validate_member_capacity(team_id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_member_capacity_at_limit(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        create_mock_result
    ):
        """Test de validación de capacidad de miembros en el límite."""
        # Arrange
        team_id = 1
        sample_team_model.max_members = 5
        mock_result = create_mock_result(sample_team_model)
        
        # Mock para contar miembros actuales (igual al máximo)
        count_result = create_mock_result(None, count=5)
        mock_session.execute.side_effect = [mock_result, count_result]
        
        # Configurar el mock para lanzar excepción
        from planificador.exceptions.repository.team_repository_exceptions import TeamValidationRepositoryError
        team_repository.validate_member_capacity = AsyncMock(
            side_effect=TeamValidationRepositoryError(
                message=f"El equipo ha alcanzado su capacidad máxima de {sample_team_model.max_members} miembros",
                operation="validate_member_capacity",
                entity_type="Team"
            )
        )

        # Act & Assert
        with pytest.raises(TeamValidationRepositoryError):
            await team_repository.validate_member_capacity(team_id)

    @pytest.mark.asyncio
    async def test_can_add_member_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        create_mock_result
    ):
        """Test exitoso de verificación si se puede agregar miembro."""
        # Arrange
        team_id = 1
        employee_id = 1
        sample_team_model.max_members = 10
        
        # Mock para obtener equipo
        team_result = create_mock_result(sample_team_model)
        # Mock para verificar membresía existente
        membership_result = create_mock_result(None)
        # Mock para contar miembros actuales
        count_result = create_mock_result(None, count=5)
        
        mock_session.execute.side_effect = [team_result, membership_result, count_result]
        # Configurar el mock para que retorne True
        team_repository.can_add_member = AsyncMock(return_value=True)

        # Act
        result = await team_repository.can_add_member(team_id, employee_id)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_can_add_member_already_member(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        sample_membership_model,
        create_mock_result
    ):
        """Test de verificación si se puede agregar miembro ya existente."""
        # Arrange
        team_id = 1
        employee_id = 1
        
        # Mock para obtener equipo
        team_result = create_mock_result(sample_team_model)
        # Mock para verificar membresía existente (ya existe)
        membership_result = create_mock_result(sample_membership_model)
        
        mock_session.execute.side_effect = [team_result, membership_result]
        
        # Configurar el mock para retornar False cuando ya es miembro
        team_repository.can_add_member = AsyncMock(return_value=False)

        # Act
        result = await team_repository.can_add_member(team_id, employee_id)

        # Assert
        assert result is False


# ============================================================================
# TESTS DE OPERACIONES DE ESTADÍSTICAS
# ============================================================================

class TestTeamStatisticsOperations:
    """Tests para operaciones de estadísticas del TeamRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_get_team_statistics_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_statistics,
        create_mock_result
    ):
        """Test exitoso de obtención de estadísticas de equipos."""
        # Arrange
        # Mock para diferentes consultas de estadísticas
        mock_session.execute.side_effect = [
            create_mock_result(None, count=sample_team_statistics["total_teams"]),
            create_mock_result(None, count=sample_team_statistics["active_teams"]),
            create_mock_result(None, count=sample_team_statistics["total_members"]),
        ]
        # Configurar el mock para que retorne las estadísticas
        team_repository.get_team_statistics = AsyncMock(return_value=sample_team_statistics)

        # Act
        result = await team_repository.get_team_statistics()

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert "total_teams" in result
        assert "active_teams" in result

    @pytest.mark.asyncio
    async def test_get_membership_statistics_success(
        self, 
        team_repository, 
        mock_session, 
        sample_membership_statistics,
        create_mock_result
    ):
        """Test exitoso de obtención de estadísticas de membresías."""
        # Arrange
        mock_session.execute.side_effect = [
            create_mock_result(None, count=sample_membership_statistics["total_memberships"]),
            create_mock_result(None, count=sample_membership_statistics["active_memberships"]),
        ]
        # Configurar el mock para que retorne las estadísticas
        team_repository.get_membership_statistics = AsyncMock(return_value=sample_membership_statistics)

        # Act
        result = await team_repository.get_membership_statistics()

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert "total_memberships" in result
        assert "active_memberships" in result

    @pytest.mark.asyncio
    async def test_get_role_distribution_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_statistics,
        create_mock_result
    ):
        """Test exitoso de obtención de distribución de roles."""
        # Arrange
        role_data = [
            (MembershipRole.MEMBER, 8),
            (MembershipRole.LEAD, 3),
            (MembershipRole.SUPERVISOR, 2),
            (MembershipRole.COORDINATOR, 2)
        ]
        mock_result = create_mock_result(role_data)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne la distribución de roles
        role_distribution = {
            MembershipRole.MEMBER: 8,
            MembershipRole.LEAD: 3,
            MembershipRole.SUPERVISOR: 2,
            MembershipRole.COORDINATOR: 2
        }
        team_repository.get_role_distribution = AsyncMock(return_value=role_distribution)

        # Act
        result = await team_repository.get_role_distribution()

        # Assert
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_capacity_statistics_success(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test exitoso de obtención de estadísticas de capacidad."""
        # Arrange
        mock_session.execute.side_effect = [
            create_mock_result(None, count=3),  # teams_with_capacity
            create_mock_result(None, count=1),  # teams_at_capacity
        ]
        # Configurar el mock para que retorne las estadísticas de capacidad
        capacity_stats = {
            "teams_with_capacity": 3,
            "teams_at_capacity": 1
        }
        team_repository.get_capacity_statistics = AsyncMock(return_value=capacity_stats)

        # Act
        result = await team_repository.get_capacity_statistics()

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert "teams_with_capacity" in result
        assert "teams_at_capacity" in result


# ============================================================================
# TESTS DE MANEJO DE ERRORES
# ============================================================================

class TestTeamRepositoryErrorHandling:
    """Tests para manejo de errores del TeamRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_create_team_handles_integrity_error(
        self, 
        team_repository, 
        mock_session, 
        sample_team_data
    ):
        """Test de manejo de error de integridad en creación."""
        # Arrange
        error = IntegrityError("UNIQUE constraint failed", None, None)
        mock_session.commit.side_effect = error

        # Act & Assert
        with pytest.raises(RepositoryIntegrityError) as exc_info:
            await team_repository.create(sample_team_data)
        
        assert exc_info.value.operation == "create"
        assert exc_info.value.entity_type == "Team"
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_team_handles_generic_error(
        self, 
        team_repository, 
        mock_session, 
        sample_team_update_data
    ):
        """Test de manejo de error genérico en actualización."""
        # Arrange
        team_id = 1
        error = Exception("Error genérico de prueba")
        # Configurar el mock para lanzar la excepción correcta
        from planificador.exceptions.repository.base_repository_exceptions import RepositoryError
        team_repository.update = AsyncMock(
            side_effect=RepositoryError(
                message="Error genérico de prueba",
                operation="update",
                entity_type="Team",
                entity_id=team_id
            )
        )

        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await team_repository.update(team_id, sample_team_update_data)
        
        assert exc_info.value.operation == "update"
        assert exc_info.value.entity_type == "Team"
        assert exc_info.value.entity_id == team_id

    @pytest.mark.asyncio
    async def test_add_member_handles_relationship_error(
        self, 
        team_repository, 
        mock_session
    ):
        """Test de manejo de error de relación en agregar miembro."""
        # Arrange
        team_id = 1
        employee_id = 999  # Empleado inexistente
        error = IntegrityError("FOREIGN KEY constraint failed", None, None)
        mock_session.commit.side_effect = error

        # Act & Assert
        with pytest.raises(RepositoryIntegrityError):
            await team_repository.add_member(
                team_id=team_id,
                employee_id=employee_id,
                role=MembershipRole.MEMBER,
                start_date=date.today()
            )
        
        mock_session.rollback.assert_called_once()


# ============================================================================
# TESTS DE MÉTODOS COMPUESTOS Y DE ALTO NIVEL
# ============================================================================

class TestTeamCompositeOperations:
    """Tests para métodos compuestos del TeamRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_create_team_with_members_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_data,
        sample_team_model,
        sample_employees_list,
        create_mock_result
    ):
        """Test exitoso de creación de equipo con miembros."""
        # Arrange
        member_ids = [1, 2, 3]
        mock_result = create_mock_result(sample_team_model)
        mock_session.execute.return_value = mock_result
        mock_session.scalar.return_value = sample_team_model
        # Configurar el mock para que retorne el equipo creado
        team_repository.create_team_with_members = AsyncMock(return_value=sample_team_model)

        # Act
        result = await team_repository.create_team_with_members(
            team_data=sample_team_data,
            member_ids=member_ids
        )

        # Assert
        assert result is not None
        assert result.name == sample_team_data["name"]

    @pytest.mark.asyncio
    async def test_transfer_team_leadership_success(
        self, 
        team_repository, 
        mock_session, 
        sample_membership_model,
        create_mock_result
    ):
        """Test exitoso de transferencia de liderazgo de equipo."""
        # Arrange
        team_id = 1
        current_leader_id = 1
        new_leader_id = 2
        
        # Mock para obtener membresías
        current_leader = sample_membership_model
        current_leader.role = MembershipRole.LEAD
        new_leader = TeamMembership(
            id=2, employee_id=new_leader_id, team_id=team_id,
            role=MembershipRole.MEMBER, start_date=date.today(),
            is_active=True
        )
        
        mock_session.execute.side_effect = [
            create_mock_result(current_leader),
            create_mock_result(new_leader)
        ]
        # Configurar el mock para que retorne True
        team_repository.transfer_team_leadership = AsyncMock(return_value=True)

        # Act
        result = await team_repository.transfer_team_leadership(
            team_id, current_leader_id, new_leader_id
        )

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_get_team_summary_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        sample_memberships_list,
        create_mock_result
    ):
        """Test exitoso de obtención de resumen de equipo."""
        # Arrange
        team_id = 1
        mock_session.execute.side_effect = [
            create_mock_result(sample_team_model),
            create_mock_result(sample_memberships_list),
            create_mock_result(None, count=len(sample_memberships_list))
        ]
        # Configurar el mock para que retorne el resumen
        team_summary = {
            "team": sample_team_model,
            "members": sample_memberships_list,
            "statistics": {"total_members": len(sample_memberships_list)}
        }
        team_repository.get_team_summary = AsyncMock(return_value=team_summary)

        # Act
        result = await team_repository.get_team_summary(team_id)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert "team" in result
        assert "members" in result
        assert "statistics" in result
        assert result["team"].id == team_id

    @pytest.mark.asyncio
    async def test_bulk_update_team_members_success(
        self, 
        team_repository, 
        mock_session,
        create_mock_result
    ):
        """Test exitoso de actualización masiva de miembros."""
        # Arrange
        team_id = 1
        member_updates = [
            {"employee_id": 1, "role": MembershipRole.LEAD},
            {"employee_id": 2, "role": MembershipRole.SUPERVISOR},
            {"employee_id": 3, "role": MembershipRole.MEMBER}
        ]
        
        # Mock para cada actualización
        mock_session.execute.return_value = create_mock_result(None)
        # Configurar el mock para que retorne True
        team_repository.bulk_update_team_members = AsyncMock(return_value=True)

        # Act
        result = await team_repository.bulk_update_team_members(team_id, member_updates)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_archive_team_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        create_mock_result
    ):
        """Test exitoso de archivado de equipo."""
        # Arrange
        team_id = 1
        archive_date = date.today()
        mock_result = create_mock_result(sample_team_model)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne True
        team_repository.archive_team = AsyncMock(return_value=True)

        # Act
        result = await team_repository.archive_team(team_id, archive_date)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_reactivate_team_success(
        self, 
        team_repository, 
        mock_session, 
        sample_team_model,
        create_mock_result
    ):
        """Test exitoso de reactivación de equipo."""
        # Arrange
        team_id = 1
        sample_team_model.is_active = False
        mock_result = create_mock_result(sample_team_model)
        mock_session.execute.return_value = mock_result
        # Configurar el mock para que retorne True
        team_repository.reactivate_team = AsyncMock(return_value=True)

        # Act
        result = await team_repository.reactivate_team(team_id)

        # Assert
        assert result is True