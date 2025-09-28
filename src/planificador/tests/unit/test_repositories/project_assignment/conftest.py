"""Configuración de pruebas para el repositorio de asignaciones de proyecto."""

import pytest

# Importar fixtures desde el módulo fixtures
from .fixtures import (
    mock_session,
    project_assignment_repository,
    sample_assignment_create,
    sample_assignment_update,
    sample_assignment_data,
    sample_date_range,
)

# Hacer disponibles los fixtures para todas las pruebas en este directorio
__all__ = [
    "mock_session",
    "project_assignment_repository",
    "sample_assignment_create",
    "sample_assignment_update",
    "sample_assignment_data",
    "sample_date_range",
]