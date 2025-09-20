# src/planificador/tests/unit/test_repositories/vacation/conftest.py

"""
Configuración específica para tests del repositorio Vacation.

Este módulo contiene configuraciones, fixtures y utilidades específicas
para los tests del VacationRepositoryFacade y sus componentes.

Configuraciones:
    - Marcadores específicos para tests de vacation
    - Configuración de logging para tests
    - Fixtures de configuración específicas
"""

import pytest
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.repositories.vacation.vacation_repository_facade import VacationRepositoryFacade


@pytest.fixture
async def mock_vacation_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture que proporciona una sesión de base de datos mockeada específica para vacation.
    
    Yields:
        AsyncSession: Sesión mockeada con métodos asíncronos
    """
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.refresh = AsyncMock()
    session.merge = AsyncMock()
    session.add = MagicMock()
    session.delete = MagicMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    
    yield session


@pytest.fixture
def vacation_test_config() -> dict:
    """
    Fixture que proporciona configuración específica para tests de vacation.
    
    Returns:
        dict: Configuración de test para vacation
    """
    return {
        "test_employee_id": 1,
        "test_vacation_id": 1,
        "default_year": 2024,
        "max_vacation_days": 30,
        "min_advance_days": 7,
        "max_concurrent_vacations": 3
    }


# Marcadores específicos para tests de vacation
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.unit,
    pytest.mark.vacation_repository
]