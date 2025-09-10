# src/planificador/tests/unit/test_schemas/fixtures/assignment.py
"""
Fixtures para testing de schemas de Assignment.

Este módulo contiene fixtures para:
- ProjectAssignmentBase: Datos base para asignaciones
- ProjectAssignmentCreate: Datos para creación
- ProjectAssignmentUpdate: Datos para actualización
- ProjectAssignment: Datos completos con ID
- Casos edge y validaciones específicas
"""

import pytest
import uuid
from datetime import date, datetime
from decimal import Decimal


# =============================================================================
# Fixtures para ProjectAssignmentBase
# =============================================================================

@pytest.fixture
def valid_assignment_base_data() -> dict:
    """Datos válidos para ProjectAssignmentBase schema."""
    return {
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2025, 1, 1),
        "end_date": date(2025, 6, 30),
        "allocated_hours_per_day": Decimal("8"),
        "percentage_allocation": Decimal("100"),
        "role_in_project": "Senior Developer",
        "is_active": True,
        "notes": "Asignación principal al proyecto"
    }

@pytest.fixture
def minimal_assignment_base_data() -> dict:
    """Datos mínimos válidos para ProjectAssignmentBase schema."""
    return {
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2025, 1, 1)
    }

@pytest.fixture
def assignment_base_with_partial_allocation() -> dict:
    """Datos para asignación parcial."""
    return {
        "employee_id": 2,
        "project_id": 2,
        "start_date": date(2025, 2, 1),
        "end_date": date(2025, 4, 30),
        "allocated_hours_per_day": Decimal("4"),
        "percentage_allocation": Decimal("50"),
        "role_in_project": "Junior Developer",
        "is_active": True,
        "notes": "Asignación a tiempo parcial"
    }

@pytest.fixture
def assignment_base_without_end_date() -> dict:
    """Datos para asignación sin fecha de fin."""
    return {
        "employee_id": 3,
        "project_id": 3,
        "start_date": date(2025, 3, 1),
        "allocated_hours_per_day": Decimal("6"),
        "role_in_project": "Tech Lead",
        "is_active": True,
        "notes": "Asignación indefinida"
    }

@pytest.fixture
def assignment_base_only_percentage() -> dict:
    """Datos para asignación solo con porcentaje."""
    return {
        "employee_id": 4,
        "project_id": 4,
        "start_date": date(2025, 4, 1),
        "end_date": date(2025, 12, 31),
        "percentage_allocation": Decimal("75"),
        "role_in_project": "Project Manager",
        "is_active": True
    }

@pytest.fixture
def assignment_base_only_hours() -> dict:
    """Datos para asignación solo con horas."""
    return {
        "employee_id": 5,
        "project_id": 5,
        "start_date": date(2025, 5, 1),
        "allocated_hours_per_day": Decimal("2"),
        "role_in_project": "Consultant",
        "is_active": False,
        "notes": "Consultoría específica"
    }


# =============================================================================
# Fixtures para ProjectAssignmentCreate
# =============================================================================

@pytest.fixture
def valid_assignment_create_data(valid_assignment_base_data) -> dict:
    """Datos válidos para ProjectAssignmentCreate schema."""
    return valid_assignment_base_data.copy()

@pytest.fixture
def minimal_assignment_create_data(minimal_assignment_base_data) -> dict:
    """Datos mínimos para ProjectAssignmentCreate schema."""
    return minimal_assignment_base_data.copy()

@pytest.fixture
def assignment_create_full_time() -> dict:
    """Datos para crear asignación a tiempo completo."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "employee_id": int(unique_id[:4], 16) % 1000 + 1,
        "project_id": int(unique_id[4:], 16) % 1000 + 1,
        "start_date": date(2025, 1, 15),
        "end_date": date(2025, 7, 15),
        "allocated_hours_per_day": Decimal("8"),
        "percentage_allocation": Decimal("100"),
        "role_in_project": "Full Stack Developer",
        "is_active": True,
        "notes": f"Asignación completa - {unique_id}"
    }

@pytest.fixture
def assignment_create_part_time() -> dict:
    """Datos para crear asignación a tiempo parcial."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "employee_id": int(unique_id[:4], 16) % 1000 + 1,
        "project_id": int(unique_id[4:], 16) % 1000 + 1,
        "start_date": date(2025, 2, 1),
        "allocated_hours_per_day": Decimal("4"),
        "percentage_allocation": Decimal("50"),
        "role_in_project": "Part-time Developer",
        "is_active": True
    }


# =============================================================================
# Fixtures para ProjectAssignmentUpdate
# =============================================================================

@pytest.fixture
def valid_assignment_update_data() -> dict:
    """Datos válidos para ProjectAssignmentUpdate schema."""
    return {
        "role_in_project": "Senior Tech Lead",
        "is_active": False,
        "notes": "Rol actualizado por promoción"
    }

@pytest.fixture
def assignment_update_partial() -> dict:
    """Datos para actualización parcial."""
    return {
        "allocated_hours_per_day": Decimal("6"),
        "percentage_allocation": Decimal("75"),
        "notes": "Reducción de horas por otros compromisos"
    }

@pytest.fixture
def assignment_update_dates() -> dict:
    """Datos para actualizar fechas."""
    return {
        "start_date": date(2025, 2, 1),
        "end_date": date(2025, 8, 31),
        "notes": "Extensión del proyecto"
    }

@pytest.fixture
def assignment_update_deactivate() -> dict:
    """Datos para desactivar asignación."""
    return {
        "is_active": False,
        "notes": "Asignación finalizada anticipadamente"
    }

@pytest.fixture
def assignment_update_role_only() -> dict:
    """Datos para actualizar solo el rol."""
    return {
        "role_in_project": "Technical Architect"
    }

@pytest.fixture
def assignment_update_empty() -> dict:
    """Datos vacíos para actualización."""
    return {}


# =============================================================================
# Fixtures para ProjectAssignment
# =============================================================================

@pytest.fixture
def valid_assignment_data() -> dict:
    """Datos válidos para ProjectAssignment schema."""
    return {
        "id": 1,
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2025, 1, 1),
        "end_date": date(2025, 6, 30),
        "allocated_hours_per_day": Decimal("8"),
        "percentage_allocation": Decimal("100"),
        "role_in_project": "Senior Developer",
        "is_active": True,
        "notes": "Asignación principal al proyecto",
        "created_at": datetime(2025, 1, 1, 9, 0, 0),
        "updated_at": datetime(2025, 1, 1, 9, 0, 0)
    }

@pytest.fixture
def assignment_with_minimal_data() -> dict:
    """Datos mínimos para ProjectAssignment schema."""
    return {
        "id": 2,
        "employee_id": 2,
        "project_id": 2,
        "start_date": date(2025, 2, 1),
        "is_active": True,
        "created_at": datetime(2025, 2, 1, 10, 0, 0),
        "updated_at": datetime(2025, 2, 1, 10, 0, 0)
    }

@pytest.fixture
def assignment_inactive() -> dict:
    """Datos para asignación inactiva."""
    return {
        "id": 3,
        "employee_id": 3,
        "project_id": 3,
        "start_date": date(2024, 6, 1),
        "end_date": date(2024, 12, 31),
        "allocated_hours_per_day": Decimal("8"),
        "percentage_allocation": Decimal("100"),
        "role_in_project": "Former Developer",
        "is_active": False,
        "notes": "Proyecto finalizado",
        "created_at": datetime(2024, 6, 1, 8, 0, 0),
        "updated_at": datetime(2024, 12, 31, 17, 0, 0)
    }

@pytest.fixture
def assignment_part_time() -> dict:
    """Datos para asignación a tiempo parcial."""
    return {
        "id": 4,
        "employee_id": 4,
        "project_id": 4,
        "start_date": date(2025, 3, 1),
        "end_date": date(2025, 9, 30),
        "allocated_hours_per_day": Decimal("4"),
        "percentage_allocation": Decimal("50"),
        "role_in_project": "Part-time Consultant",
        "is_active": True,
        "notes": "Consultoría especializada",
        "created_at": datetime(2025, 3, 1, 9, 30, 0),
        "updated_at": datetime(2025, 3, 1, 9, 30, 0)
    }


# =============================================================================
# Fixtures para Casos Edge y Validaciones
# =============================================================================

@pytest.fixture
def assignment_invalid_date_range() -> dict:
    """Datos con rango de fechas inválido."""
    return {
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2025, 6, 30),
        "end_date": date(2025, 1, 1)  # Fecha de fin anterior a inicio
    }

@pytest.fixture
def assignment_invalid_hours() -> dict:
    """Datos con horas inválidas."""
    return {
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2025, 1, 1),
        "allocated_hours_per_day": Decimal("-1")  # Horas negativas
    }

@pytest.fixture
def assignment_invalid_percentage() -> dict:
    """Datos con porcentaje inválido."""
    return {
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2025, 1, 1),
        "percentage_allocation": Decimal("150")  # Porcentaje mayor a 100
    }

@pytest.fixture
def assignment_inconsistent_allocation() -> dict:
    """Datos con asignación inconsistente."""
    return {
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2025, 1, 1),
        "allocated_hours_per_day": Decimal("8"),
        "percentage_allocation": Decimal("25")  # 8 horas debería ser ~100%, no 25%
    }

@pytest.fixture
def assignment_long_role() -> dict:
    """Datos con rol muy largo."""
    return {
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2025, 1, 1),
        "role_in_project": "x" * 101  # Excede máximo de 100 caracteres
    }

@pytest.fixture
def assignment_boundary_hours() -> dict:
    """Datos con valores límite para horas."""
    return [
        {
            "employee_id": 1,
            "project_id": 1,
            "start_date": date(2025, 1, 1),
            "allocated_hours_per_day": Decimal("0")  # Mínimo
        },
        {
            "employee_id": 2,
            "project_id": 2,
            "start_date": date(2025, 1, 1),
            "allocated_hours_per_day": Decimal("24")  # Máximo
        }
    ]

@pytest.fixture
def assignment_boundary_percentage() -> dict:
    """Datos con valores límite para porcentaje."""
    return [
        {
            "employee_id": 1,
            "project_id": 1,
            "start_date": date(2025, 1, 1),
            "percentage_allocation": Decimal("0")  # Mínimo
        },
        {
            "employee_id": 2,
            "project_id": 2,
            "start_date": date(2025, 1, 1),
            "percentage_allocation": Decimal("100")  # Máximo
        }
    ]

@pytest.fixture
def assignment_consistent_allocations() -> dict:
    """Datos con asignaciones consistentes."""
    return [
        {
            "employee_id": 1,
            "project_id": 1,
            "start_date": date(2025, 1, 1),
            "allocated_hours_per_day": Decimal("4"),
            "percentage_allocation": Decimal("50")  # 4/8 = 50%
        },
        {
            "employee_id": 2,
            "project_id": 2,
            "start_date": date(2025, 1, 1),
            "allocated_hours_per_day": Decimal("6"),
            "percentage_allocation": Decimal("75")  # 6/8 = 75%
        },
        {
            "employee_id": 3,
            "project_id": 3,
            "start_date": date(2025, 1, 1),
            "allocated_hours_per_day": Decimal("8"),
            "percentage_allocation": Decimal("97")  # Dentro de tolerancia (5%)
        }
    ]

@pytest.fixture
def assignment_decimal_precision() -> dict:
    """Datos con precisión decimal."""
    return {
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2025, 1, 1),
        "allocated_hours_per_day": Decimal("7.5"),
        "percentage_allocation": Decimal("93.75")  # 7.5/8 = 93.75%
    }

@pytest.fixture
def assignment_empty_strings() -> dict:
    """Datos con strings vacíos."""
    return {
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2025, 1, 1),
        "role_in_project": "",
        "notes": ""
    }


# =============================================================================
# Fixtures para Serialización y Comparación
# =============================================================================

@pytest.fixture
def assignment_for_serialization() -> dict:
    """Datos para tests de serialización."""
    return {
        "id": 100,
        "employee_id": 10,
        "project_id": 20,
        "start_date": date(2025, 6, 1),
        "end_date": date(2025, 11, 30),
        "allocated_hours_per_day": Decimal("7.5"),
        "percentage_allocation": Decimal("93.75"),
        "role_in_project": "Senior Full Stack Developer",
        "is_active": True,
        "notes": "Proyecto estratégico de alta prioridad",
        "created_at": datetime(2025, 6, 1, 8, 30, 0),
        "updated_at": datetime(2025, 6, 1, 8, 30, 0)
    }

@pytest.fixture
def assignment_list_for_comparison() -> list:
    """Lista de asignaciones para tests de comparación."""
    return [
        {
            "id": 1,
            "employee_id": 1,
            "project_id": 1,
            "start_date": date(2025, 1, 1),
            "role_in_project": "Developer",
            "is_active": True,
            "created_at": datetime(2025, 1, 1, 9, 0, 0),
            "updated_at": datetime(2025, 1, 1, 9, 0, 0)
        },
        {
            "id": 2,
            "employee_id": 2,
            "project_id": 2,
            "start_date": date(2025, 2, 1),
            "role_in_project": "Designer",
            "is_active": False,
            "created_at": datetime(2025, 2, 1, 10, 0, 0),
            "updated_at": datetime(2025, 2, 1, 10, 0, 0)
        }
    ]


# =============================================================================
# Fixtures para Performance y Stress Testing
# =============================================================================

@pytest.fixture
def assignment_performance_data() -> list:
    """Datos para tests de performance."""
    assignments = []
    for i in range(100):
        assignments.append({
            "id": i + 1,
            "employee_id": (i % 10) + 1,
            "project_id": (i % 5) + 1,
            "start_date": date(2025, (i % 12) + 1, 1),
            "allocated_hours_per_day": Decimal(str(4 + (i % 5))),
            "percentage_allocation": Decimal(str(50 + (i % 51))),
            "role_in_project": f"Role {i}",
            "is_active": i % 2 == 0,
            "notes": f"Assignment notes {i}",
            "created_at": datetime(2025, 1, 1, 9, 0, 0),
            "updated_at": datetime(2025, 1, 1, 9, 0, 0)
        })
    return assignments