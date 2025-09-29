"""Fixtures para las pruebas del repositorio de membresías de equipo."""

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.team_membership import MembershipRole, TeamMembership
from planificador.repositories.team_membership import TeamMembershipRepositoryFacade
from planificador.repositories.team_membership.modules import (
    TeamMembershipCrudModule,
    TeamMembershipQueryModule,
    TeamMembershipRelationshipModule,
    TeamMembershipStatisticsModule,
    TeamMembershipValidationModule,
)


@pytest.fixture
def mock_session() -> AsyncMock:
    """Fixture que proporciona una sesión de base de datos mockeada."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def team_membership_repository(
    mock_session: AsyncMock,
) -> TeamMembershipRepositoryFacade:
    """Fixture para obtener una instancia del facade del repositorio con módulos mockeados."""
    # Crear mocks para cada módulo
    mock_crud = AsyncMock()
    mock_query = AsyncMock()
    mock_relationship = AsyncMock()
    mock_statistics = AsyncMock()
    mock_validation = AsyncMock()
    
    with (
        patch(
            "planificador.repositories.team_membership.team_membership_repository_facade.TeamMembershipCrudModule",
            return_value=mock_crud,
        ),
        patch(
            "planificador.repositories.team_membership.team_membership_repository_facade.TeamMembershipQueryModule",
            return_value=mock_query,
        ),
        patch(
            "planificador.repositories.team_membership.team_membership_repository_facade.TeamMembershipRelationshipModule",
            return_value=mock_relationship,
        ),
        patch(
            "planificador.repositories.team_membership.team_membership_repository_facade.TeamMembershipStatisticsModule",
            return_value=mock_statistics,
        ),
        patch(
            "planificador.repositories.team_membership.team_membership_repository_facade.TeamMembershipValidationModule",
            return_value=mock_validation,
        ),
    ):
        return TeamMembershipRepositoryFacade(session=mock_session)


@pytest.fixture
def sample_membership_create() -> dict:
    """Fixture que proporciona datos de ejemplo para crear una membresía."""
    return {
        "employee_id": 1,
        "team_id": 1,
        "role": MembershipRole.MEMBER,
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 12, 31),
        "is_active": True,
    }


@pytest.fixture
def sample_membership_update() -> dict:
    """Fixture que proporciona datos de ejemplo para actualizar una membresía."""
    return {
        "role": MembershipRole.LEAD,
        "end_date": date(2025, 6, 30),
    }


@pytest.fixture
def sample_membership_data() -> dict:
    """Fixture que proporciona datos de membresía en formato diccionario."""
    return {
        "id": 1,
        "employee_id": 1,
        "team_id": 1,
        "role": MembershipRole.MEMBER,
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 12, 31),
        "is_active": True,
    }


@pytest.fixture
def sample_membership_list() -> list[TeamMembership]:
    """Fixture que proporciona una lista de objetos TeamMembership."""
    membership1 = TeamMembership(
        id=1,
        employee_id=1,
        team_id=1,
        role=MembershipRole.MEMBER,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        is_active=True,
    )
    membership2 = TeamMembership(
        id=2,
        employee_id=2,
        team_id=1,
        role=MembershipRole.LEAD,
        start_date=date(2024, 2, 1),
        end_date=None,
        is_active=True,
    )
    membership3 = TeamMembership(
        id=3,
        employee_id=3,
        team_id=2,
        role=MembershipRole.MEMBER,
        start_date=date(2024, 1, 15),
        end_date=date(2024, 6, 30),
        is_active=False,
    )
    return [membership1, membership2, membership3]


@pytest.fixture
def sample_date_range() -> tuple[date, date]:
    """Fixture que proporciona un rango de fechas de ejemplo."""
    return date(2024, 1, 1), date(2024, 12, 31)