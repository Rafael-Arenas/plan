"""Fixtures para los esquemas de Vacation."""

from typing import Any, Dict
from datetime import date, datetime

import pytest
from planificador.models.vacation import VacationType, VacationStatus


@pytest.fixture
def valid_vacation_base_data() -> Dict[str, Any]:
    """Datos base válidos para Vacation."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 8, 1),
        "end_date": date(2024, 8, 10),
        "vacation_type": VacationType.ANNUAL,
        "status": VacationStatus.APPROVED,
        "notes": "Vacaciones de verano",
        "requested_date": date(2024, 7, 1),
        "approved_date": date(2024, 7, 5),
        "approved_by": "manager_user",
        "total_days": 10,
        "business_days": 8,
        "reason": "Annual leave"
    }


@pytest.fixture
def valid_vacation_create_data(valid_vacation_base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para VacationCreate."""
    return valid_vacation_base_data.copy()


@pytest.fixture
def valid_vacation_update_data(valid_vacation_base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para VacationUpdate."""
    data = valid_vacation_base_data.copy()
    data.update({
        "notes": "Vacaciones de invierno.",
        "status": VacationStatus.PENDING,
        "approved_date": None,
        "approved_by": None
    })
    return data


@pytest.fixture
def valid_vacation_data(valid_vacation_base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para Vacation."""
    data = valid_vacation_base_data.copy()
    data["id"] = 1
    data["created_at"] = datetime(2024, 7, 1, 0, 0, 0)
    data["updated_at"] = datetime(2024, 7, 1, 0, 0, 0)
    return data


@pytest.fixture
def valid_vacation_search_filter_data(valid_vacation_base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para VacationSearchFilter."""
    data = valid_vacation_base_data.copy()
    data.update({
        "start_date_from": date(2024, 8, 1),
        "start_date_to": date(2024, 8, 31),
        "end_date_from": date(2024, 9, 1),
        "end_date_to": date(2024, 9, 30),
        "status": VacationStatus.APPROVED
    })
    return data


@pytest.fixture
def invalid_vacation_dates() -> Dict[str, Any]:
    """Datos inválidos: fecha de fin antes de fecha de inicio."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 8, 10),
        "end_date": date(2024, 8, 1),
        "vacation_type": VacationType.ANNUAL,
        "requested_date": date(2024, 7, 1),
        "total_days": 10,
        "business_days": 8
    }


@pytest.fixture
def invalid_vacation_future_requested_date() -> Dict[str, Any]:
    """Datos inválidos: fecha de solicitud en el futuro."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 8, 1),
        "end_date": date(2024, 8, 10),
        "vacation_type": VacationType.ANNUAL,
        "requested_date": date(2025, 1, 1),
        "total_days": 10,
        "business_days": 8
    }


@pytest.fixture
def invalid_vacation_approval_without_approved_status() -> Dict[str, Any]:
    """Datos inválidos: aprobación sin estado 'Aprobado'."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 8, 1),
        "end_date": date(2024, 8, 10),
        "vacation_type": VacationType.ANNUAL,
        "status": VacationStatus.PENDING,
        "approved_date": date(2024, 7, 5),
        "approved_by": "manager_user",
        "requested_date": date(2024, 7, 1),
        "total_days": 10,
        "business_days": 8
    }


@pytest.fixture
def invalid_vacation_negative_days() -> Dict[str, Any]:
    """Datos inválidos: días negativos."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 8, 1),
        "end_date": date(2024, 8, 10),
        "vacation_type": VacationType.ANNUAL,
        "requested_date": date(2024, 7, 1),
        "total_days": -5,
        "business_days": -3
    }


@pytest.fixture
def invalid_vacation_zero_days() -> Dict[str, Any]:
    """Datos inválidos: cero días."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 8, 1),
        "end_date": date(2024, 8, 10),
        "vacation_type": VacationType.ANNUAL,
        "requested_date": date(2024, 7, 1),
        "total_days": 0,
        "business_days": 0
    }


@pytest.fixture
def invalid_vacation_long_approved_by() -> Dict[str, Any]:
    """Datos inválidos: `approved_by` demasiado largo."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 8, 1),
        "end_date": date(2024, 8, 10),
        "vacation_type": VacationType.ANNUAL,
        "status": VacationStatus.APPROVED,
        "approved_by": "a" * 101,
        "requested_date": date(2024, 7, 1),
        "approved_date": date(2024, 7, 5),
        "total_days": 10,
        "business_days": 8
    }


@pytest.fixture
def minimal_vacation_data() -> Dict[str, Any]:
    """Datos mínimos para crear vacaciones."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 8, 1),
        "end_date": date(2024, 8, 10),
        "vacation_type": VacationType.ANNUAL,
        "requested_date": date(2024, 7, 1),
        "total_days": 10,
        "business_days": 8
    }


@pytest.fixture
def maximal_vacation_data() -> Dict[str, Any]:
    """Datos máximos para crear vacaciones."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 8, 1),
        "end_date": date(2024, 8, 10),
        "vacation_type": VacationType.OTHER,
        "status": VacationStatus.APPROVED,
        "notes": "a" * 1000,
        "reason": "a" * 1000,
        "requested_date": date(2024, 7, 1),
        "approved_date": date(2024, 7, 5),
        "approved_by": "a" * 100,
        "total_days": 10,
        "business_days": 8
    }


@pytest.fixture
def vacation_data_with_none_optionals() -> Dict[str, Any]:
    """Datos de vacaciones con opcionales en None."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 8, 1),
        "end_date": date(2024, 8, 10),
        "vacation_type": VacationType.PERSONAL,
        "status": VacationStatus.PENDING,
        "notes": None,
        "reason": None,
        "requested_date": date(2024, 7, 1),
        "approved_date": None,
        "approved_by": None,
        "total_days": 10,
        "business_days": 8
    }


@pytest.fixture(params=list(VacationType))
def vacation_type_variations(request) -> VacationType:
    """Variaciones de tipos de vacaciones."""
    return request.param


@pytest.fixture(params=list(VacationStatus))
def vacation_status_variations(request) -> VacationStatus:
    """Variaciones de estados de vacaciones."""
    return request.param


@pytest.fixture(params=[
    {"start_date": date(2024, 8, 1), "end_date": date(2024, 8, 2), "total_days": 1, "business_days": 1},
    {"start_date": date(2024, 8, 1), "end_date": date(2024, 8, 10), "total_days": 9, "business_days": 7}
])
def vacation_edge_cases(request) -> Dict[str, Any]:
    """Casos límite para vacaciones."""
    base_data = {
        "employee_id": 1,
        "vacation_type": VacationType.SICK,
        "requested_date": date(2024, 7, 1)
    }
    base_data.update(request.param)
    return base_data