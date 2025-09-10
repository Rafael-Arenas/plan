"""Fixtures para testing de schemas de Response."""

import pytest
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import List

from planificador.models.employee import EmployeeStatus
from planificador.models.project import ProjectStatus, ProjectPriority
from planificador.models.vacation import VacationType, VacationStatus


# ==========================================
# FIXTURES PARA SCHEMAS DE LISTADOS
# ==========================================

@pytest.fixture
def valid_employee_list_response_data() -> dict:
    """Datos válidos para EmployeeListResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "full_name": f"Test Employee {unique_id}",
        "employee_code": f"EMP-{unique_id}",
        "email": f"employee-{unique_id.lower()}@test.com",
        "status": EmployeeStatus.ACTIVE.value,
        "position": "Software Developer",
        "department": "IT",
        "is_available": True
    }


@pytest.fixture
def valid_project_list_response_data() -> dict:
    """Datos válidos para ProjectListResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "name": f"Test Project {unique_id}",
        "reference": f"PRJ-{unique_id}",
        "trigram": unique_id[:3],
        "status": ProjectStatus.IN_PROGRESS.value,
        "priority": ProjectPriority.MEDIUM.value,
        "start_date": date.today(),
        "end_date": date(2025, 12, 31),
        "client_name": f"Test Client {unique_id}",
        "client_id": 1
    }


@pytest.fixture
def valid_client_list_response_data() -> dict:
    """Datos válidos para ClientListResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "name": f"Test Client {unique_id}",
        "contact_person": f"Contact {unique_id}",
        "email": f"client-{unique_id.lower()}@test.com",
        "phone": "+56912345678",
        "is_active": True,
        "projects_count": 3
    }


@pytest.fixture
def valid_team_list_response_data() -> dict:
    """Datos válidos para TeamListResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "name": f"Test Team {unique_id}",
        "description": f"Test team description {unique_id}",
        "color": "#FF5733",
        "is_active": True,
        "members_count": 5
    }


@pytest.fixture
def valid_schedule_list_response_data() -> dict:
    """Datos válidos para ScheduleListResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "date": date.today(),
        "start_time": time(9, 0),
        "end_time": time(17, 0),
        "hours_worked": Decimal("8.0"),
        "employee_name": f"Employee {unique_id}",
        "employee_id": 1,
        "project_name": f"Project {unique_id}",
        "project_id": 1,
        "team_name": f"Team {unique_id}",
        "team_id": 1,
        "status_code": "CONFIRMED",
        "is_confirmed": True,
        "location": "Office"
    }


@pytest.fixture
def valid_vacation_list_response_data() -> dict:
    """Datos válidos para VacationListResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "employee_name": f"Employee {unique_id}",
        "employee_id": 1,
        "start_date": date(2025, 6, 1),
        "end_date": date(2025, 6, 15),
        "vacation_type": VacationType.ANNUAL.value,
        "status": VacationStatus.APPROVED.value,
        "total_days": 15,
        "business_days": 11,
        "requested_date": datetime(2025, 5, 1, 10, 0),
        "approved_date": datetime(2025, 5, 2, 14, 30)
    }


@pytest.fixture
def valid_workload_list_response_data() -> dict:
    """Datos válidos para WorkloadListResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "employee_name": f"Employee {unique_id}",
        "employee_id": 1,
        "project_name": f"Project {unique_id}",
        "project_id": 1,
        "date": date.today(),
        "planned_hours": Decimal("8.0"),
        "actual_hours": Decimal("7.5"),
        "utilization_percentage": Decimal("93.75"),
        "efficiency_score": Decimal("0.94"),
        "is_billable": True
    }


@pytest.fixture
def valid_project_assignment_list_response_data() -> dict:
    """Datos válidos para ProjectAssignmentListResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "employee_name": f"Employee {unique_id}",
        "employee_id": 1,
        "project_name": f"Project {unique_id}",
        "project_id": 1,
        "start_date": date.today(),
        "end_date": date(2025, 12, 31),
        "allocated_hours_per_day": Decimal("6.0"),
        "percentage_allocation": Decimal("75.0"),
        "role_in_project": "Developer",
        "is_active": True
    }


# ==========================================
# FIXTURES PARA SCHEMAS DE BÚSQUEDA
# ==========================================

@pytest.fixture
def valid_employee_search_response_data() -> dict:
    """Datos válidos para EmployeeSearchResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "full_name": f"Test Employee {unique_id}",
        "employee_code": f"EMP-{unique_id}",
        "email": f"employee-{unique_id.lower()}@test.com",
        "phone": "+56912345678",
        "status": EmployeeStatus.ACTIVE.value,
        "position": "Software Developer",
        "department": "IT",
        "is_available": True,
        "current_projects": ["Project A", "Project B"],
        "current_teams": ["Team Alpha", "Team Beta"]
    }


@pytest.fixture
def valid_project_search_response_data() -> dict:
    """Datos válidos para ProjectSearchResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "name": f"Test Project {unique_id}",
        "reference": f"PRJ-{unique_id}",
        "trigram": unique_id[:3],
        "status": ProjectStatus.IN_PROGRESS.value,
        "priority": ProjectPriority.HIGH.value,
        "start_date": date.today(),
        "end_date": date(2025, 12, 31),
        "client_name": f"Test Client {unique_id}",
        "client_id": 1,
        "assigned_employees": ["Employee A", "Employee B"],
        "total_assignments": 2
    }


@pytest.fixture
def valid_schedule_search_response_data() -> dict:
    """Datos válidos para ScheduleSearchResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "date": date.today(),
        "start_time": time(9, 0),
        "end_time": time(17, 0),
        "hours_worked": Decimal("8.0"),
        "employee_name": f"Employee {unique_id}",
        "employee_id": 1,
        "project_name": f"Project {unique_id}",
        "project_id": 1,
        "team_name": f"Team {unique_id}",
        "team_id": 1,
        "status_code": "CONFIRMED",
        "is_confirmed": True,
        "location": "Office",
        "description": f"Schedule description {unique_id}"
    }


# ==========================================
# FIXTURES PARA SCHEMAS DE RESUMEN
# ==========================================

@pytest.fixture
def valid_employee_summary_response_data() -> dict:
    """Datos válidos para EmployeeSummaryResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "full_name": f"Test Employee {unique_id}",
        "employee_code": f"EMP-{unique_id}",
        "status": EmployeeStatus.ACTIVE.value,
        "position": "Software Developer",
        "department": "IT",
        "total_projects": 5,
        "active_projects": 3,
        "total_teams": 2,
        "current_utilization": Decimal("85.5"),
        "avg_efficiency": Decimal("0.92"),
        "pending_vacations": 1
    }


@pytest.fixture
def valid_project_summary_response_data() -> dict:
    """Datos válidos para ProjectSummaryResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "name": f"Test Project {unique_id}",
        "reference": f"PRJ-{unique_id}",
        "status": ProjectStatus.IN_PROGRESS.value,
        "priority": ProjectPriority.HIGH.value,
        "start_date": date.today(),
        "end_date": date(2025, 12, 31),
        "client_name": f"Test Client {unique_id}",
        "total_assignments": 5,
        "active_assignments": 3,
        "total_hours_planned": Decimal("1000.0"),
        "total_hours_actual": Decimal("750.0"),
        "progress_percentage": Decimal("75.0")
    }


@pytest.fixture
def valid_team_summary_response_data() -> dict:
    """Datos válidos para TeamSummaryResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "id": 1,
        "name": f"Test Team {unique_id}",
        "description": f"Test team description {unique_id}",
        "is_active": True,
        "total_members": 8,
        "active_members": 6,
        "current_projects": ["Project A", "Project B", "Project C"],
        "avg_utilization": Decimal("82.5")
    }


@pytest.fixture
def valid_workload_summary_response_data() -> dict:
    """Datos válidos para WorkloadSummaryResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "employee_id": 1,
        "employee_name": f"Employee {unique_id}",
        "period_start": date(2025, 1, 1),
        "period_end": date(2025, 1, 31),
        "total_planned_hours": Decimal("160.0"),
        "total_actual_hours": Decimal("152.0"),
        "avg_utilization": Decimal("95.0"),
        "avg_efficiency": Decimal("0.95"),
        "billable_hours": Decimal("144.0"),
        "billable_percentage": Decimal("94.7"),
        "projects_count": 3
    }


# ==========================================
# FIXTURES PARA SCHEMAS DE PAGINACIÓN
# ==========================================

@pytest.fixture
def valid_paginated_response_data() -> dict:
    """Datos válidos para PaginatedResponse schema."""
    return {
        "total": 100,
        "page": 1,
        "size": 10,
        "pages": 10,
        "has_next": True,
        "has_prev": False
    }


@pytest.fixture
def valid_paginated_employee_response_data(
    valid_paginated_response_data,
    valid_employee_list_response_data
) -> dict:
    """Datos válidos para PaginatedEmployeeResponse schema."""
    data = valid_paginated_response_data.copy()
    data["items"] = [valid_employee_list_response_data]
    return data


@pytest.fixture
def valid_paginated_project_response_data(
    valid_paginated_response_data,
    valid_project_list_response_data
) -> dict:
    """Datos válidos para PaginatedProjectResponse schema."""
    data = valid_paginated_response_data.copy()
    data["items"] = [valid_project_list_response_data]
    return data


# ==========================================
# FIXTURES PARA SCHEMAS DE DASHBOARD
# ==========================================

@pytest.fixture
def valid_dashboard_stats_response_data() -> dict:
    """Datos válidos para DashboardStatsResponse schema."""
    return {
        "total_employees": 50,
        "active_employees": 45,
        "total_projects": 25,
        "active_projects": 18,
        "total_clients": 15,
        "active_clients": 12,
        "pending_vacations": 8,
        "today_schedules": 35,
        "overdue_projects": 3,
        "high_priority_projects": 7
    }


@pytest.fixture
def valid_employee_utilization_response_data() -> dict:
    """Datos válidos para EmployeeUtilizationResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "employee_id": 1,
        "employee_name": f"Employee {unique_id}",
        "current_utilization": Decimal("85.0"),
        "target_utilization": Decimal("80.0"),
        "variance": Decimal("5.0"),
        "status": "Óptima"
    }


@pytest.fixture
def valid_project_progress_response_data() -> dict:
    """Datos válidos para ProjectProgressResponse schema."""
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "project_id": 1,
        "project_name": f"Project {unique_id}",
        "progress_percentage": Decimal("75.5"),
        "days_remaining": 45,
        "status": ProjectStatus.IN_PROGRESS.value,
        "is_on_track": True,
        "risk_level": "Bajo"
    }


# ==========================================
# FIXTURES PARA CASOS EDGE
# ==========================================

@pytest.fixture
def minimal_employee_list_response_data() -> dict:
    """Datos mínimos para EmployeeListResponse schema."""
    return {
        "id": 1,
        "full_name": "Minimal Employee",
        "employee_code": "MIN001",
        "email": "minimal@test.com",
        "status": EmployeeStatus.ACTIVE.value,
        "is_available": True
    }


@pytest.fixture
def empty_paginated_response_data() -> dict:
    """Datos para respuesta paginada vacía."""
    return {
        "total": 0,
        "page": 1,
        "size": 10,
        "pages": 0,
        "has_next": False,
        "has_prev": False,
        "items": []
    }


@pytest.fixture
def invalid_enum_values() -> dict:
    """Valores inválidos para enums en response schemas."""
    return {
        "employee_status": ["INVALID_STATUS", "", None, 123],
        "project_status": ["INVALID_PROJECT", "", None, 456],
        "project_priority": ["INVALID_PRIORITY", "", None, 789],
        "vacation_type": ["INVALID_TYPE", "", None, 101],
        "vacation_status": ["INVALID_STATUS", "", None, 202]
    }


@pytest.fixture
def invalid_decimal_values() -> list:
    """Valores inválidos para campos Decimal."""
    return [
        "invalid_decimal",
        "abc",
        [],
        {},
        float('inf'),
        float('-inf')
    ]


@pytest.fixture
def invalid_date_values() -> list:
    """Valores inválidos para campos de fecha."""
    return [
        "invalid_date",
        "2025-13-01",  # Mes inválido
        "2025-02-30",  # Día inválido
        "not-a-date",
        123,
        [],
        {}
    ]


@pytest.fixture
def invalid_time_values() -> list:
    """Valores inválidos para campos de tiempo."""
    return [
        "invalid_time",
        "25:00:00",  # Hora inválida
        "12:60:00",  # Minuto inválido
        "12:30:60",  # Segundo inválido
        "not-a-time",
        # Nota: 123 es válido para Pydantic (se interpreta como segundos desde medianoche)
        [],
        {}
    ]