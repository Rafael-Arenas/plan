"""Tests para schemas de Response.

Este módulo contiene tests completos para todos los schemas de respuesta
del sistema, incluyendo validación de campos, serialización/deserialización,
casos edge y validación de enums.

Arquitectura de Testing:
- Tests de validación básica para cada schema
- Tests de enums y tipos especiales
- Tests de serialización/deserialización
- Tests de casos edge y límites
- Tests de schemas con relaciones

Cobertura:
- Schemas de listados (Employee, Project, Client, etc.)
- Schemas de búsqueda (Search responses)
- Schemas de resumen (Summary responses)
- Schemas de paginación (Paginated responses)
- Schemas de dashboard y métricas
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, time
from typing import List
from pydantic import ValidationError

from planificador.schemas.response.response_schemas import (
    # Schemas de listados
    EmployeeListResponse,
    ProjectListResponse,
    ClientListResponse,
    TeamListResponse,
    ScheduleListResponse,
    VacationListResponse,
    WorkloadListResponse,
    ProjectAssignmentListResponse,
    
    # Schemas de búsqueda
    EmployeeSearchResponse,
    ProjectSearchResponse,
    ScheduleSearchResponse,
    
    # Schemas de resumen
    EmployeeSummaryResponse,
    ProjectSummaryResponse,
    TeamSummaryResponse,
    WorkloadSummaryResponse,
    
    # Schemas de paginación
    PaginatedResponse,
    PaginatedEmployeeResponse,
    PaginatedProjectResponse,
    PaginatedClientResponse,
    PaginatedScheduleResponse,
    PaginatedVacationResponse,
    PaginatedWorkloadResponse,
    
    # Schemas de dashboard
    DashboardStatsResponse,
    EmployeeUtilizationResponse,
    ProjectProgressResponse
)
from planificador.models.employee import EmployeeStatus
from planificador.models.project import ProjectStatus, ProjectPriority
from planificador.models.vacation import VacationType, VacationStatus


# ==========================================
# TESTS DE SCHEMAS DE LISTADOS
# ==========================================

class TestEmployeeListResponse:
    """Tests para el schema EmployeeListResponse."""
    
    def test_valid_creation(self, valid_employee_list_response_data):
        """Test creación válida del schema."""
        schema = EmployeeListResponse(**valid_employee_list_response_data)
        
        assert schema.id == valid_employee_list_response_data["id"]
        assert schema.full_name == valid_employee_list_response_data["full_name"]
        assert schema.employee_code == valid_employee_list_response_data["employee_code"]
        assert schema.email == valid_employee_list_response_data["email"]
        assert schema.status == EmployeeStatus(valid_employee_list_response_data["status"])
        assert schema.position == valid_employee_list_response_data["position"]
        assert schema.department == valid_employee_list_response_data["department"]
        assert schema.is_available == valid_employee_list_response_data["is_available"]
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            EmployeeListResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["id", "full_name", "employee_code", "email", "status"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_optional_fields_defaults(self, minimal_employee_list_response_data):
        """Test valores por defecto de campos opcionales."""
        schema = EmployeeListResponse(**minimal_employee_list_response_data)
        
        assert schema.position is None
        assert schema.department is None
        assert schema.is_available is True
    
    def test_employee_status_enum_validation(self, valid_employee_list_response_data):
        """Test validación del enum EmployeeStatus."""
        # Test valor válido
        valid_employee_list_response_data["status"] = EmployeeStatus.INACTIVE.value
        schema = EmployeeListResponse(**valid_employee_list_response_data)
        assert schema.status == EmployeeStatus.INACTIVE
        
        # Test valor inválido
        valid_employee_list_response_data["status"] = "INVALID_STATUS"
        with pytest.raises(ValidationError) as exc_info:
            EmployeeListResponse(**valid_employee_list_response_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("status",) for error in errors)
    
    def test_serialization(self, valid_employee_list_response_data):
        """Test serialización del schema."""
        schema = EmployeeListResponse(**valid_employee_list_response_data)
        
        # Test model_dump
        data_dict = schema.model_dump(mode='json')
        assert isinstance(data_dict, dict)
        assert data_dict["id"] == valid_employee_list_response_data["id"]
        assert data_dict["status"] == valid_employee_list_response_data["status"]
        
        # Test model_dump_json
        json_str = schema.model_dump_json()
        assert isinstance(json_str, str)
        assert str(valid_employee_list_response_data["id"]) in json_str


class TestProjectListResponse:
    """Tests para el schema ProjectListResponse."""
    
    def test_valid_creation(self, valid_project_list_response_data):
        """Test creación válida del schema."""
        schema = ProjectListResponse(**valid_project_list_response_data)
        
        assert schema.id == valid_project_list_response_data["id"]
        assert schema.name == valid_project_list_response_data["name"]
        assert schema.reference == valid_project_list_response_data["reference"]
        assert schema.trigram == valid_project_list_response_data["trigram"]
        assert schema.status == ProjectStatus(valid_project_list_response_data["status"])
        assert schema.priority == ProjectPriority(valid_project_list_response_data["priority"])
        assert schema.client_name == valid_project_list_response_data["client_name"]
        assert schema.client_id == valid_project_list_response_data["client_id"]
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectListResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["id", "name", "reference", "trigram", "status", "priority", "client_name", "client_id"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_project_enums_validation(self, valid_project_list_response_data):
        """Test validación de enums ProjectStatus y ProjectPriority."""
        # Test ProjectStatus válido
        valid_project_list_response_data["status"] = ProjectStatus.COMPLETED.value
        valid_project_list_response_data["priority"] = ProjectPriority.LOW.value
        schema = ProjectListResponse(**valid_project_list_response_data)
        assert schema.status == ProjectStatus.COMPLETED
        assert schema.priority == ProjectPriority.LOW
        
        # Test ProjectStatus inválido
        valid_project_list_response_data["status"] = "INVALID_STATUS"
        with pytest.raises(ValidationError) as exc_info:
            ProjectListResponse(**valid_project_list_response_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("status",) for error in errors)
    
    def test_date_fields_validation(self, valid_project_list_response_data):
        """Test validación de campos de fecha."""
        # Test fechas válidas
        schema = ProjectListResponse(**valid_project_list_response_data)
        assert isinstance(schema.start_date, date)
        assert isinstance(schema.end_date, date)
        
        # Test fechas opcionales None
        valid_project_list_response_data["start_date"] = None
        valid_project_list_response_data["end_date"] = None
        schema = ProjectListResponse(**valid_project_list_response_data)
        assert schema.start_date is None
        assert schema.end_date is None


class TestClientListResponse:
    """Tests para el schema ClientListResponse."""
    
    def test_valid_creation(self, valid_client_list_response_data):
        """Test creación válida del schema."""
        schema = ClientListResponse(**valid_client_list_response_data)
        
        assert schema.id == valid_client_list_response_data["id"]
        assert schema.name == valid_client_list_response_data["name"]
        assert schema.contact_person == valid_client_list_response_data["contact_person"]
        assert schema.email == valid_client_list_response_data["email"]
        assert schema.phone == valid_client_list_response_data["phone"]
        assert schema.is_active == valid_client_list_response_data["is_active"]
        assert schema.projects_count == valid_client_list_response_data["projects_count"]
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            ClientListResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["id", "name"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_optional_fields_defaults(self):
        """Test valores por defecto de campos opcionales."""
        minimal_data = {"id": 1, "name": "Test Client"}
        schema = ClientListResponse(**minimal_data)
        
        assert schema.contact_person is None
        assert schema.email is None
        assert schema.phone is None
        assert schema.is_active is True
        assert schema.projects_count == 0


class TestTeamListResponse:
    """Tests para el schema TeamListResponse."""
    
    def test_valid_creation(self, valid_team_list_response_data):
        """Test creación válida del schema."""
        schema = TeamListResponse(**valid_team_list_response_data)
        
        assert schema.id == valid_team_list_response_data["id"]
        assert schema.name == valid_team_list_response_data["name"]
        assert schema.description == valid_team_list_response_data["description"]
        assert schema.color == valid_team_list_response_data["color"]
        assert schema.is_active == valid_team_list_response_data["is_active"]
        assert schema.members_count == valid_team_list_response_data["members_count"]
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            TeamListResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["id", "name"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_optional_fields_defaults(self):
        """Test valores por defecto de campos opcionales."""
        minimal_data = {"id": 1, "name": "Test Team"}
        schema = TeamListResponse(**minimal_data)
        
        assert schema.description is None
        assert schema.color is None
        assert schema.is_active is True
        assert schema.members_count == 0


class TestScheduleListResponse:
    """Tests para el schema ScheduleListResponse."""
    
    def test_valid_creation(self, valid_schedule_list_response_data):
        """Test creación válida del schema."""
        schema = ScheduleListResponse(**valid_schedule_list_response_data)
        
        assert schema.id == valid_schedule_list_response_data["id"]
        assert schema.date == valid_schedule_list_response_data["date"]
        assert schema.start_time == valid_schedule_list_response_data["start_time"]
        assert schema.end_time == valid_schedule_list_response_data["end_time"]
        assert schema.hours_worked == valid_schedule_list_response_data["hours_worked"]
        assert schema.employee_name == valid_schedule_list_response_data["employee_name"]
        assert schema.employee_id == valid_schedule_list_response_data["employee_id"]
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleListResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["id", "date", "start_time", "end_time", "employee_name", "employee_id"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_time_fields_validation(self, valid_schedule_list_response_data):
        """Test validación de campos de tiempo."""
        schema = ScheduleListResponse(**valid_schedule_list_response_data)
        
        assert isinstance(schema.date, date)
        assert isinstance(schema.start_time, time)
        assert isinstance(schema.end_time, time)
        assert isinstance(schema.hours_worked, Decimal)
    
    def test_decimal_fields_validation(self, valid_schedule_list_response_data, invalid_decimal_values):
        """Test validación de campos Decimal."""
        for invalid_value in invalid_decimal_values:
            valid_schedule_list_response_data["hours_worked"] = invalid_value
            with pytest.raises(ValidationError) as exc_info:
                ScheduleListResponse(**valid_schedule_list_response_data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("hours_worked",) for error in errors)


class TestVacationListResponse:
    """Tests para el schema VacationListResponse."""
    
    def test_valid_creation(self, valid_vacation_list_response_data):
        """Test creación válida del schema."""
        schema = VacationListResponse(**valid_vacation_list_response_data)
        
        assert schema.id == valid_vacation_list_response_data["id"]
        assert schema.employee_name == valid_vacation_list_response_data["employee_name"]
        assert schema.employee_id == valid_vacation_list_response_data["employee_id"]
        assert schema.start_date == valid_vacation_list_response_data["start_date"]
        assert schema.end_date == valid_vacation_list_response_data["end_date"]
        assert schema.vacation_type == VacationType(valid_vacation_list_response_data["vacation_type"])
        assert schema.status == VacationStatus(valid_vacation_list_response_data["status"])
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            VacationListResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["id", "employee_name", "employee_id", "start_date", "end_date", "vacation_type", "status", "requested_date"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_vacation_enums_validation(self, valid_vacation_list_response_data):
        """Test validación de enums VacationType y VacationStatus."""
        # Test valores válidos
        valid_vacation_list_response_data["vacation_type"] = VacationType.SICK.value
        valid_vacation_list_response_data["status"] = VacationStatus.PENDING.value
        schema = VacationListResponse(**valid_vacation_list_response_data)
        assert schema.vacation_type == VacationType.SICK
        assert schema.status == VacationStatus.PENDING
        
        # Test valor inválido
        valid_vacation_list_response_data["vacation_type"] = "INVALID_TYPE"
        with pytest.raises(ValidationError) as exc_info:
            VacationListResponse(**valid_vacation_list_response_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("vacation_type",) for error in errors)
    
    def test_datetime_fields_validation(self, valid_vacation_list_response_data):
        """Test validación de campos datetime."""
        schema = VacationListResponse(**valid_vacation_list_response_data)
        
        assert isinstance(schema.requested_date, datetime)
        assert isinstance(schema.approved_date, datetime)


class TestWorkloadListResponse:
    """Tests para el schema WorkloadListResponse."""
    
    def test_valid_creation(self, valid_workload_list_response_data):
        """Test creación válida del schema."""
        schema = WorkloadListResponse(**valid_workload_list_response_data)
        
        assert schema.id == valid_workload_list_response_data["id"]
        assert schema.employee_name == valid_workload_list_response_data["employee_name"]
        assert schema.employee_id == valid_workload_list_response_data["employee_id"]
        assert schema.project_name == valid_workload_list_response_data["project_name"]
        assert schema.project_id == valid_workload_list_response_data["project_id"]
        assert schema.date == valid_workload_list_response_data["date"]
        assert schema.planned_hours == valid_workload_list_response_data["planned_hours"]
        assert schema.is_billable == valid_workload_list_response_data["is_billable"]
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadListResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["id", "employee_name", "employee_id", "project_name", "project_id", "date", "planned_hours"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_decimal_fields_precision(self, valid_workload_list_response_data):
        """Test precisión de campos Decimal."""
        schema = WorkloadListResponse(**valid_workload_list_response_data)
        
        assert isinstance(schema.planned_hours, Decimal)
        assert isinstance(schema.actual_hours, Decimal)
        assert isinstance(schema.utilization_percentage, Decimal)
        assert isinstance(schema.efficiency_score, Decimal)
    
    def test_boolean_field_validation(self, valid_workload_list_response_data):
        """Test validación de campo booleano is_billable."""
        # Test valor por defecto
        del valid_workload_list_response_data["is_billable"]
        schema = WorkloadListResponse(**valid_workload_list_response_data)
        assert schema.is_billable is True
        
        # Test valor explícito
        valid_workload_list_response_data["is_billable"] = False
        schema = WorkloadListResponse(**valid_workload_list_response_data)
        assert schema.is_billable is False


class TestProjectAssignmentListResponse:
    """Tests para el schema ProjectAssignmentListResponse."""
    
    def test_valid_creation(self, valid_project_assignment_list_response_data):
        """Test creación válida del schema."""
        schema = ProjectAssignmentListResponse(**valid_project_assignment_list_response_data)
        
        assert schema.id == valid_project_assignment_list_response_data["id"]
        assert schema.employee_name == valid_project_assignment_list_response_data["employee_name"]
        assert schema.employee_id == valid_project_assignment_list_response_data["employee_id"]
        assert schema.project_name == valid_project_assignment_list_response_data["project_name"]
        assert schema.project_id == valid_project_assignment_list_response_data["project_id"]
        assert schema.start_date == valid_project_assignment_list_response_data["start_date"]
        assert schema.is_active == valid_project_assignment_list_response_data["is_active"]
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentListResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["id", "employee_name", "employee_id", "project_name", "project_id", "start_date"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_optional_fields_defaults(self):
        """Test valores por defecto de campos opcionales."""
        minimal_data = {
            "id": 1,
            "employee_name": "Test Employee",
            "employee_id": 1,
            "project_name": "Test Project",
            "project_id": 1,
            "start_date": date.today()
        }
        schema = ProjectAssignmentListResponse(**minimal_data)
        
        assert schema.end_date is None
        assert schema.allocated_hours_per_day is None
        assert schema.percentage_allocation is None
        assert schema.role_in_project is None
        assert schema.is_active is True


# ==========================================
# TESTS DE SCHEMAS DE BÚSQUEDA
# ==========================================

class TestEmployeeSearchResponse:
    """Tests para el schema EmployeeSearchResponse."""
    
    def test_valid_creation(self, valid_employee_search_response_data):
        """Test creación válida del schema."""
        schema = EmployeeSearchResponse(**valid_employee_search_response_data)
        
        assert schema.id == valid_employee_search_response_data["id"]
        assert schema.full_name == valid_employee_search_response_data["full_name"]
        assert schema.current_projects == valid_employee_search_response_data["current_projects"]
        assert schema.current_teams == valid_employee_search_response_data["current_teams"]
    
    def test_list_fields_validation(self, valid_employee_search_response_data):
        """Test validación de campos de lista."""
        schema = EmployeeSearchResponse(**valid_employee_search_response_data)
        
        assert isinstance(schema.current_projects, list)
        assert isinstance(schema.current_teams, list)
        assert len(schema.current_projects) == 2
        assert len(schema.current_teams) == 2
    
    def test_empty_lists_default(self):
        """Test valores por defecto de listas vacías."""
        minimal_data = {
            "id": 1,
            "full_name": "Test Employee",
            "employee_code": "EMP001",
            "email": "test@test.com",
            "status": EmployeeStatus.ACTIVE.value
        }
        schema = EmployeeSearchResponse(**minimal_data)
        
        assert schema.current_projects == []
        assert schema.current_teams == []


class TestProjectSearchResponse:
    """Tests para el schema ProjectSearchResponse."""
    
    def test_valid_creation(self, valid_project_search_response_data):
        """Test creación válida del schema."""
        schema = ProjectSearchResponse(**valid_project_search_response_data)
        
        assert schema.id == valid_project_search_response_data["id"]
        assert schema.name == valid_project_search_response_data["name"]
        assert schema.assigned_employees == valid_project_search_response_data["assigned_employees"]
        assert schema.total_assignments == valid_project_search_response_data["total_assignments"]
    
    def test_list_fields_validation(self, valid_project_search_response_data):
        """Test validación de campos de lista."""
        schema = ProjectSearchResponse(**valid_project_search_response_data)
        
        assert isinstance(schema.assigned_employees, list)
        assert len(schema.assigned_employees) == 2
        assert isinstance(schema.total_assignments, int)
    
    def test_empty_lists_default(self):
        """Test valores por defecto de listas vacías."""
        minimal_data = {
            "id": 1,
            "name": "Test Project",
            "reference": "PRJ001",
            "trigram": "TST",
            "status": ProjectStatus.IN_PROGRESS.value,
            "priority": ProjectPriority.MEDIUM.value,
            "client_name": "Test Client",
            "client_id": 1
        }
        schema = ProjectSearchResponse(**minimal_data)
        
        assert schema.assigned_employees == []
        assert schema.total_assignments == 0


class TestScheduleSearchResponse:
    """Tests para el schema ScheduleSearchResponse."""
    
    def test_valid_creation(self, valid_schedule_search_response_data):
        """Test creación válida del schema."""
        schema = ScheduleSearchResponse(**valid_schedule_search_response_data)
        
        assert schema.id == valid_schedule_search_response_data["id"]
        assert schema.description == valid_schedule_search_response_data["description"]
        # Hereda todos los campos de ScheduleListResponse
        assert schema.date == valid_schedule_search_response_data["date"]
        assert schema.employee_name == valid_schedule_search_response_data["employee_name"]
    
    def test_additional_field_description(self, valid_schedule_search_response_data):
        """Test campo adicional description."""
        schema = ScheduleSearchResponse(**valid_schedule_search_response_data)
        
        assert schema.description == valid_schedule_search_response_data["description"]
        
        # Test description opcional
        del valid_schedule_search_response_data["description"]
        schema = ScheduleSearchResponse(**valid_schedule_search_response_data)
        assert schema.description is None


# ==========================================
# TESTS DE SCHEMAS DE RESUMEN
# ==========================================

class TestEmployeeSummaryResponse:
    """Tests para el schema EmployeeSummaryResponse."""
    
    def test_valid_creation(self, valid_employee_summary_response_data):
        """Test creación válida del schema."""
        schema = EmployeeSummaryResponse(**valid_employee_summary_response_data)
        
        assert schema.id == valid_employee_summary_response_data["id"]
        assert schema.total_projects == valid_employee_summary_response_data["total_projects"]
        assert schema.active_projects == valid_employee_summary_response_data["active_projects"]
        assert schema.total_teams == valid_employee_summary_response_data["total_teams"]
        assert schema.current_utilization == valid_employee_summary_response_data["current_utilization"]
        assert schema.avg_efficiency == valid_employee_summary_response_data["avg_efficiency"]
        assert schema.pending_vacations == valid_employee_summary_response_data["pending_vacations"]
    
    def test_integer_fields_defaults(self):
        """Test valores por defecto de campos enteros."""
        minimal_data = {
            "id": 1,
            "full_name": "Test Employee",
            "employee_code": "EMP001",
            "status": EmployeeStatus.ACTIVE.value
        }
        schema = EmployeeSummaryResponse(**minimal_data)
        
        assert schema.total_projects == 0
        assert schema.active_projects == 0
        assert schema.total_teams == 0
        assert schema.pending_vacations == 0
    
    def test_decimal_fields_optional(self, valid_employee_summary_response_data):
        """Test campos Decimal opcionales."""
        # Test con valores
        schema = EmployeeSummaryResponse(**valid_employee_summary_response_data)
        assert isinstance(schema.current_utilization, Decimal)
        assert isinstance(schema.avg_efficiency, Decimal)
        
        # Test sin valores (None)
        del valid_employee_summary_response_data["current_utilization"]
        del valid_employee_summary_response_data["avg_efficiency"]
        schema = EmployeeSummaryResponse(**valid_employee_summary_response_data)
        assert schema.current_utilization is None
        assert schema.avg_efficiency is None


class TestProjectSummaryResponse:
    """Tests para el schema ProjectSummaryResponse."""
    
    def test_valid_creation(self, valid_project_summary_response_data):
        """Test creación válida del schema."""
        schema = ProjectSummaryResponse(**valid_project_summary_response_data)
        
        assert schema.id == valid_project_summary_response_data["id"]
        assert schema.total_assignments == valid_project_summary_response_data["total_assignments"]
        assert schema.active_assignments == valid_project_summary_response_data["active_assignments"]
        assert schema.total_hours_planned == valid_project_summary_response_data["total_hours_planned"]
        assert schema.total_hours_actual == valid_project_summary_response_data["total_hours_actual"]
        assert schema.progress_percentage == valid_project_summary_response_data["progress_percentage"]
    
    def test_integer_fields_defaults(self):
        """Test valores por defecto de campos enteros."""
        minimal_data = {
            "id": 1,
            "name": "Test Project",
            "reference": "PRJ001",
            "status": ProjectStatus.IN_PROGRESS.value,
            "priority": ProjectPriority.MEDIUM.value,
            "client_name": "Test Client"
        }
        schema = ProjectSummaryResponse(**minimal_data)
        
        assert schema.total_assignments == 0
        assert schema.active_assignments == 0
    
    def test_decimal_fields_optional(self, valid_project_summary_response_data):
        """Test campos Decimal opcionales."""
        # Test con valores
        schema = ProjectSummaryResponse(**valid_project_summary_response_data)
        assert isinstance(schema.total_hours_planned, Decimal)
        assert isinstance(schema.total_hours_actual, Decimal)
        assert isinstance(schema.progress_percentage, Decimal)
        
        # Test sin valores (None)
        del valid_project_summary_response_data["total_hours_planned"]
        del valid_project_summary_response_data["total_hours_actual"]
        del valid_project_summary_response_data["progress_percentage"]
        schema = ProjectSummaryResponse(**valid_project_summary_response_data)
        assert schema.total_hours_planned is None
        assert schema.total_hours_actual is None
        assert schema.progress_percentage is None


class TestTeamSummaryResponse:
    """Tests para el schema TeamSummaryResponse."""
    
    def test_valid_creation(self, valid_team_summary_response_data):
        """Test creación válida del schema."""
        schema = TeamSummaryResponse(**valid_team_summary_response_data)
        
        assert schema.id == valid_team_summary_response_data["id"]
        assert schema.total_members == valid_team_summary_response_data["total_members"]
        assert schema.active_members == valid_team_summary_response_data["active_members"]
        assert schema.current_projects == valid_team_summary_response_data["current_projects"]
        assert schema.avg_utilization == valid_team_summary_response_data["avg_utilization"]
    
    def test_list_field_validation(self, valid_team_summary_response_data):
        """Test validación de campo de lista current_projects."""
        schema = TeamSummaryResponse(**valid_team_summary_response_data)
        
        assert isinstance(schema.current_projects, list)
        assert len(schema.current_projects) == 3
        
        # Test lista vacía por defecto
        del valid_team_summary_response_data["current_projects"]
        schema = TeamSummaryResponse(**valid_team_summary_response_data)
        assert schema.current_projects == []
    
    def test_integer_fields_defaults(self):
        """Test valores por defecto de campos enteros."""
        minimal_data = {
            "id": 1,
            "name": "Test Team"
        }
        schema = TeamSummaryResponse(**minimal_data)
        
        assert schema.total_members == 0
        assert schema.active_members == 0
        assert schema.is_active is True


class TestWorkloadSummaryResponse:
    """Tests para el schema WorkloadSummaryResponse."""
    
    def test_valid_creation(self, valid_workload_summary_response_data):
        """Test creación válida del schema."""
        schema = WorkloadSummaryResponse(**valid_workload_summary_response_data)
        
        assert schema.employee_id == valid_workload_summary_response_data["employee_id"]
        assert schema.employee_name == valid_workload_summary_response_data["employee_name"]
        assert schema.period_start == valid_workload_summary_response_data["period_start"]
        assert schema.period_end == valid_workload_summary_response_data["period_end"]
        assert schema.total_planned_hours == valid_workload_summary_response_data["total_planned_hours"]
        assert schema.projects_count == valid_workload_summary_response_data["projects_count"]
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadSummaryResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["employee_id", "employee_name", "period_start", "period_end", "total_planned_hours"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_decimal_fields_precision(self, valid_workload_summary_response_data):
        """Test precisión de campos Decimal."""
        schema = WorkloadSummaryResponse(**valid_workload_summary_response_data)
        
        assert isinstance(schema.total_planned_hours, Decimal)
        assert isinstance(schema.total_actual_hours, Decimal)
        assert isinstance(schema.avg_utilization, Decimal)
        assert isinstance(schema.avg_efficiency, Decimal)
        assert isinstance(schema.billable_hours, Decimal)
        assert isinstance(schema.billable_percentage, Decimal)
    
    def test_integer_field_default(self):
        """Test valor por defecto de campo entero projects_count."""
        minimal_data = {
            "employee_id": 1,
            "employee_name": "Test Employee",
            "period_start": date(2025, 1, 1),
            "period_end": date(2025, 1, 31),
            "total_planned_hours": Decimal("160.0")
        }
        schema = WorkloadSummaryResponse(**minimal_data)
        
        assert schema.projects_count == 0


# ==========================================
# TESTS DE SCHEMAS DE PAGINACIÓN
# ==========================================

class TestPaginatedResponse:
    """Tests para el schema PaginatedResponse."""
    
    def test_valid_creation(self, valid_paginated_response_data):
        """Test creación válida del schema."""
        schema = PaginatedResponse(**valid_paginated_response_data)
        
        assert schema.total == valid_paginated_response_data["total"]
        assert schema.page == valid_paginated_response_data["page"]
        assert schema.size == valid_paginated_response_data["size"]
        assert schema.pages == valid_paginated_response_data["pages"]
        assert schema.has_next == valid_paginated_response_data["has_next"]
        assert schema.has_prev == valid_paginated_response_data["has_prev"]
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            PaginatedResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["total", "page", "size", "pages", "has_next", "has_prev"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_field_descriptions(self, valid_paginated_response_data):
        """Test que los campos tienen las descripciones correctas."""
        schema = PaginatedResponse(**valid_paginated_response_data)
        
        # Verificar que el schema se crea correctamente
        assert schema.total >= 0
        assert schema.page >= 1
        assert schema.size >= 1
        assert schema.pages >= 0
        assert isinstance(schema.has_next, bool)
        assert isinstance(schema.has_prev, bool)
    
    def test_edge_cases_pagination(self):
        """Test casos edge de paginación."""
        # Primera página
        first_page_data = {
            "total": 100,
            "page": 1,
            "size": 10,
            "pages": 10,
            "has_next": True,
            "has_prev": False
        }
        schema = PaginatedResponse(**first_page_data)
        assert schema.has_prev is False
        assert schema.has_next is True
        
        # Última página
        last_page_data = {
            "total": 100,
            "page": 10,
            "size": 10,
            "pages": 10,
            "has_next": False,
            "has_prev": True
        }
        schema = PaginatedResponse(**last_page_data)
        assert schema.has_prev is True
        assert schema.has_next is False
        
        # Sin resultados
        empty_data = {
            "total": 0,
            "page": 1,
            "size": 10,
            "pages": 0,
            "has_next": False,
            "has_prev": False
        }
        schema = PaginatedResponse(**empty_data)
        assert schema.total == 0
        assert schema.pages == 0


class TestPaginatedEmployeeResponse:
    """Tests para el schema PaginatedEmployeeResponse."""
    
    def test_valid_creation(self, valid_paginated_employee_response_data):
        """Test creación válida del schema."""
        schema = PaginatedEmployeeResponse(**valid_paginated_employee_response_data)
        
        assert isinstance(schema.items, list)
        assert len(schema.items) == 1
        assert isinstance(schema.items[0], EmployeeListResponse)
        # Hereda campos de PaginatedResponse
        assert schema.total == valid_paginated_employee_response_data["total"]
        assert schema.page == valid_paginated_employee_response_data["page"]
    
    def test_empty_items_list(self, empty_paginated_response_data):
        """Test lista de items vacía."""
        schema = PaginatedEmployeeResponse(**empty_paginated_response_data)
        
        assert schema.items == []
        assert schema.total == 0
    
    def test_items_default_value(self, valid_paginated_response_data):
        """Test valor por defecto de items."""
        schema = PaginatedEmployeeResponse(**valid_paginated_response_data)
        
        assert schema.items == []


class TestPaginatedProjectResponse:
    """Tests para el schema PaginatedProjectResponse."""
    
    def test_valid_creation(self, valid_paginated_project_response_data):
        """Test creación válida del schema."""
        schema = PaginatedProjectResponse(**valid_paginated_project_response_data)
        
        assert isinstance(schema.items, list)
        assert len(schema.items) == 1
        assert isinstance(schema.items[0], ProjectListResponse)
        # Hereda campos de PaginatedResponse
        assert schema.total == valid_paginated_project_response_data["total"]
        assert schema.page == valid_paginated_project_response_data["page"]
    
    def test_empty_items_list(self, empty_paginated_response_data):
        """Test lista de items vacía."""
        schema = PaginatedProjectResponse(**empty_paginated_response_data)
        
        assert schema.items == []
        assert schema.total == 0


# ==========================================
# TESTS DE SCHEMAS DE DASHBOARD
# ==========================================

class TestDashboardStatsResponse:
    """Tests para el schema DashboardStatsResponse."""
    
    def test_valid_creation(self, valid_dashboard_stats_response_data):
        """Test creación válida del schema."""
        schema = DashboardStatsResponse(**valid_dashboard_stats_response_data)
        
        assert schema.total_employees == valid_dashboard_stats_response_data["total_employees"]
        assert schema.active_employees == valid_dashboard_stats_response_data["active_employees"]
        assert schema.total_projects == valid_dashboard_stats_response_data["total_projects"]
        assert schema.active_projects == valid_dashboard_stats_response_data["active_projects"]
        assert schema.total_clients == valid_dashboard_stats_response_data["total_clients"]
        assert schema.active_clients == valid_dashboard_stats_response_data["active_clients"]
        assert schema.pending_vacations == valid_dashboard_stats_response_data["pending_vacations"]
        assert schema.today_schedules == valid_dashboard_stats_response_data["today_schedules"]
        assert schema.overdue_projects == valid_dashboard_stats_response_data["overdue_projects"]
        assert schema.high_priority_projects == valid_dashboard_stats_response_data["high_priority_projects"]
    
    def test_integer_fields_defaults(self):
        """Test valores por defecto de todos los campos enteros."""
        schema = DashboardStatsResponse()
        
        assert schema.total_employees == 0
        assert schema.active_employees == 0
        assert schema.total_projects == 0
        assert schema.active_projects == 0
        assert schema.total_clients == 0
        assert schema.active_clients == 0
        assert schema.pending_vacations == 0
        assert schema.today_schedules == 0
        assert schema.overdue_projects == 0
        assert schema.high_priority_projects == 0
    
    def test_non_negative_values(self, valid_dashboard_stats_response_data):
        """Test que todos los valores son no negativos."""
        schema = DashboardStatsResponse(**valid_dashboard_stats_response_data)
        
        assert schema.total_employees >= 0
        assert schema.active_employees >= 0
        assert schema.total_projects >= 0
        assert schema.active_projects >= 0
        assert schema.total_clients >= 0
        assert schema.active_clients >= 0
        assert schema.pending_vacations >= 0
        assert schema.today_schedules >= 0
        assert schema.overdue_projects >= 0
        assert schema.high_priority_projects >= 0


class TestEmployeeUtilizationResponse:
    """Tests para el schema EmployeeUtilizationResponse."""
    
    def test_valid_creation(self, valid_employee_utilization_response_data):
        """Test creación válida del schema."""
        schema = EmployeeUtilizationResponse(**valid_employee_utilization_response_data)
        
        assert schema.employee_id == valid_employee_utilization_response_data["employee_id"]
        assert schema.employee_name == valid_employee_utilization_response_data["employee_name"]
        assert schema.current_utilization == valid_employee_utilization_response_data["current_utilization"]
        assert schema.target_utilization == valid_employee_utilization_response_data["target_utilization"]
        assert schema.variance == valid_employee_utilization_response_data["variance"]
        assert schema.status == valid_employee_utilization_response_data["status"]
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            EmployeeUtilizationResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["employee_id", "employee_name", "current_utilization", "variance", "status"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_target_utilization_default(self):
        """Test valor por defecto de target_utilization."""
        minimal_data = {
            "employee_id": 1,
            "employee_name": "Test Employee",
            "current_utilization": Decimal("85.0"),
            "variance": Decimal("5.0"),
            "status": "Óptima"
        }
        schema = EmployeeUtilizationResponse(**minimal_data)
        
        assert schema.target_utilization == Decimal('80.0')
    
    def test_decimal_fields_precision(self, valid_employee_utilization_response_data):
        """Test precisión de campos Decimal."""
        schema = EmployeeUtilizationResponse(**valid_employee_utilization_response_data)
        
        assert isinstance(schema.current_utilization, Decimal)
        assert isinstance(schema.target_utilization, Decimal)
        assert isinstance(schema.variance, Decimal)
    
    def test_status_values(self, valid_employee_utilization_response_data):
        """Test valores válidos para el campo status."""
        valid_statuses = ["Óptima", "Baja", "Alta", "Sobrecarga"]
        
        for status in valid_statuses:
            valid_employee_utilization_response_data["status"] = status
            schema = EmployeeUtilizationResponse(**valid_employee_utilization_response_data)
            assert schema.status == status


class TestProjectProgressResponse:
    """Tests para el schema ProjectProgressResponse."""
    
    def test_valid_creation(self, valid_project_progress_response_data):
        """Test creación válida del schema."""
        schema = ProjectProgressResponse(**valid_project_progress_response_data)
        
        assert schema.project_id == valid_project_progress_response_data["project_id"]
        assert schema.project_name == valid_project_progress_response_data["project_name"]
        assert schema.progress_percentage == valid_project_progress_response_data["progress_percentage"]
        assert schema.days_remaining == valid_project_progress_response_data["days_remaining"]
        assert schema.status == ProjectStatus(valid_project_progress_response_data["status"])
        assert schema.is_on_track == valid_project_progress_response_data["is_on_track"]
        assert schema.risk_level == valid_project_progress_response_data["risk_level"]
    
    def test_required_fields(self):
        """Test validación de campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            ProjectProgressResponse()
        
        errors = exc_info.value.errors()
        required_fields = ["project_id", "project_name", "progress_percentage", "status", "risk_level"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors)
    
    def test_optional_fields_defaults(self):
        """Test valores por defecto de campos opcionales."""
        minimal_data = {
            "project_id": 1,
            "project_name": "Test Project",
            "progress_percentage": Decimal("50.0"),
            "status": ProjectStatus.IN_PROGRESS.value,
            "risk_level": "Bajo"
        }
        schema = ProjectProgressResponse(**minimal_data)
        
        assert schema.days_remaining is None
        assert schema.is_on_track is True
    
    def test_project_status_enum_validation(self, valid_project_progress_response_data):
        """Test validación del enum ProjectStatus."""
        # Test valor válido
        valid_project_progress_response_data["status"] = ProjectStatus.COMPLETED.value
        schema = ProjectProgressResponse(**valid_project_progress_response_data)
        assert schema.status == ProjectStatus.COMPLETED
        
        # Test valor inválido
        valid_project_progress_response_data["status"] = "INVALID_STATUS"
        with pytest.raises(ValidationError) as exc_info:
            ProjectProgressResponse(**valid_project_progress_response_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("status",) for error in errors)
    
    def test_risk_level_values(self, valid_project_progress_response_data):
        """Test valores válidos para el campo risk_level."""
        valid_risk_levels = ["Bajo", "Medio", "Alto"]
        
        for risk_level in valid_risk_levels:
            valid_project_progress_response_data["risk_level"] = risk_level
            schema = ProjectProgressResponse(**valid_project_progress_response_data)
            assert schema.risk_level == risk_level
    
    def test_progress_percentage_validation(self, valid_project_progress_response_data):
        """Test validación del porcentaje de progreso."""
        schema = ProjectProgressResponse(**valid_project_progress_response_data)
        
        assert isinstance(schema.progress_percentage, Decimal)
        assert schema.progress_percentage >= Decimal('0.0')
        assert schema.progress_percentage <= Decimal('100.0')


# ==========================================
# TESTS DE CASOS EDGE Y VALIDACIONES ESPECIALES
# ==========================================

class TestResponseSchemasEdgeCases:
    """Tests de casos edge para todos los response schemas."""
    
    def test_invalid_enum_values_handling(self, invalid_enum_values):
        """Test manejo de valores inválidos en enums."""
        # Test EmployeeStatus inválido
        for invalid_status in invalid_enum_values["employee_status"]:
            with pytest.raises(ValidationError):
                EmployeeListResponse(
                    id=1,
                    full_name="Test",
                    employee_code="TEST",
                    email="test@test.com",
                    status=invalid_status
                )
        
        # Test ProjectStatus inválido
        for invalid_status in invalid_enum_values["project_status"]:
            with pytest.raises(ValidationError):
                ProjectListResponse(
                    id=1,
                    name="Test",
                    reference="TEST",
                    trigram="TST",
                    status=invalid_status,
                    priority=ProjectPriority.MEDIUM.value,
                    client_name="Test Client",
                    client_id=1
                )
    
    def test_invalid_decimal_values_handling(self, invalid_decimal_values):
        """Test manejo de valores inválidos en campos Decimal."""
        for invalid_value in invalid_decimal_values:
            with pytest.raises(ValidationError):
                WorkloadListResponse(
                    id=1,
                    employee_name="Test",
                    employee_id=1,
                    project_name="Test",
                    project_id=1,
                    date=date.today(),
                    planned_hours=invalid_value
                )
    
    def test_invalid_date_values_handling(self, invalid_date_values):
        """Test manejo de valores inválidos en campos de fecha."""
        for invalid_date in invalid_date_values:
            with pytest.raises(ValidationError):
                ScheduleListResponse(
                    id=1,
                    date=invalid_date,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    employee_name="Test",
                    employee_id=1
                )
    
    def test_invalid_time_values_handling(self, invalid_time_values):
        """Test manejo de valores inválidos en campos de tiempo."""
        for invalid_time in invalid_time_values:
            with pytest.raises(ValidationError):
                ScheduleListResponse(
                    id=1,
                    date=date.today(),
                    start_time=invalid_time,
                    end_time=time(17, 0),
                    employee_name="Test",
                    employee_id=1
                )
    
    def test_large_list_fields_handling(self):
        """Test manejo de listas grandes en campos de lista."""
        # Lista grande de proyectos actuales
        large_projects_list = [f"Project {i}" for i in range(100)]
        
        data = {
            "id": 1,
            "full_name": "Test Employee",
            "employee_code": "EMP001",
            "email": "test@test.com",
            "status": EmployeeStatus.ACTIVE.value,
            "current_projects": large_projects_list
        }
        
        schema = EmployeeSearchResponse(**data)
        assert len(schema.current_projects) == 100
        assert schema.current_projects[0] == "Project 0"
        assert schema.current_projects[99] == "Project 99"
    
    def test_boundary_values_pagination(self):
        """Test valores límite en paginación."""
        # Página 1 con 1 elemento
        boundary_data = {
            "total": 1,
            "page": 1,
            "size": 1,
            "pages": 1,
            "has_next": False,
            "has_prev": False
        }
        schema = PaginatedResponse(**boundary_data)
        assert schema.total == 1
        assert schema.pages == 1
        
        # Página muy grande
        large_page_data = {
            "total": 10000,
            "page": 1000,
            "size": 10,
            "pages": 1000,
            "has_next": False,
            "has_prev": True
        }
        schema = PaginatedResponse(**large_page_data)
        assert schema.total == 10000
        assert schema.page == 1000
    
    def test_extreme_decimal_values(self):
        """Test valores extremos en campos Decimal."""
        # Valores muy pequeños
        small_value_data = {
            "employee_id": 1,
            "employee_name": "Test Employee",
            "current_utilization": Decimal("0.01"),
            "target_utilization": Decimal("0.01"),
            "variance": Decimal("-0.01"),
            "status": "Baja"
        }
        schema = EmployeeUtilizationResponse(**small_value_data)
        assert schema.current_utilization == Decimal("0.01")
        
        # Valores muy grandes
        large_value_data = {
            "employee_id": 1,
            "employee_name": "Test Employee",
            "current_utilization": Decimal("999.99"),
            "target_utilization": Decimal("100.00"),
            "variance": Decimal("899.99"),
            "status": "Sobrecarga"
        }
        schema = EmployeeUtilizationResponse(**large_value_data)
        assert schema.current_utilization == Decimal("999.99")
        assert schema.variance == Decimal("899.99")
    
    def test_unicode_string_fields(self):
        """Test manejo de caracteres Unicode en campos de texto."""
        unicode_data = {
            "id": 1,
            "full_name": "José María Ñoño",
            "employee_code": "EMP001",
            "email": "josé.maría@test.com",
            "status": EmployeeStatus.ACTIVE.value,
            "position": "Desarrollador Senior",
            "department": "Tecnología"
        }
        
        schema = EmployeeListResponse(**unicode_data)
        assert schema.full_name == "José María Ñoño"
        assert schema.email == "josé.maría@test.com"
        assert schema.position == "Desarrollador Senior"
        assert schema.department == "Tecnología"
    
    def test_empty_string_fields_handling(self):
        """Test manejo de campos de texto vacíos."""
        empty_string_data = {
            "id": 1,
            "name": "",  # String vacío
            "contact_person": "",
            "email": "",
            "phone": ""
        }
        
        # Algunos campos pueden aceptar strings vacíos
        schema = ClientListResponse(**empty_string_data)
        assert schema.name == ""
        assert schema.contact_person == ""
        assert schema.email == ""
        assert schema.phone == ""
    
    def test_null_vs_none_handling(self):
        """Test diferencia entre null y None en campos opcionales."""
        # Campos opcionales con None explícito
        none_data = {
            "id": 1,
            "full_name": "Test Employee",
            "employee_code": "EMP001",
            "email": "test@test.com",
            "status": EmployeeStatus.ACTIVE.value,
            "position": None,
            "department": None
        }
        
        schema = EmployeeListResponse(**none_data)
        assert schema.position is None
        assert schema.department is None
    
    def test_serialization_with_special_values(self):
        """Test serialización con valores especiales (None, Decimal, etc.)."""
        special_data = {
            "id": 1,
            "employee_name": "Test Employee",
            "employee_id": 1,
            "project_name": "Test Project",
            "project_id": 1,
            "date": date(2025, 1, 15),
            "planned_hours": Decimal("8.50"),
            "actual_hours": None,  # Valor None
            "utilization_percentage": Decimal("85.75"),
            "efficiency_score": None,  # Valor None
            "is_billable": True
        }
        
        schema = WorkloadListResponse(**special_data)
        
        # Test model_dump con valores especiales
        data_dict = schema.model_dump()
        assert data_dict["actual_hours"] is None
        assert data_dict["efficiency_score"] is None
        assert isinstance(data_dict["planned_hours"], Decimal)
        
        # Test model_dump_json
        json_str = schema.model_dump_json()
        assert "null" in json_str  # None se serializa como null en JSON
        assert "8.50" in json_str  # Decimal se serializa como string


# ==========================================
# TESTS DE PERFORMANCE Y MEMORIA
# ==========================================

class TestResponseSchemasPerformance:
    """Tests de performance para response schemas."""
    
    def test_large_dataset_creation_performance(self):
        """Test performance con datasets grandes."""
        import time
        
        # Crear 1000 empleados
        start_time = time.time()
        employees = []
        
        for i in range(1000):
            employee_data = {
                "id": i + 1,
                "full_name": f"Employee {i + 1}",
                "employee_code": f"EMP{i + 1:04d}",
                "email": f"employee{i + 1}@test.com",
                "status": EmployeeStatus.ACTIVE.value,
                "position": f"Position {i + 1}",
                "department": f"Department {(i % 10) + 1}",
                "is_available": True
            }
            employees.append(EmployeeListResponse(**employee_data))
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Verificar que se crearon correctamente
        assert len(employees) == 1000
        assert employees[0].full_name == "Employee 1"
        assert employees[999].full_name == "Employee 1000"
        
        # Performance: debería crear 1000 schemas en menos de 1 segundo
        assert creation_time < 1.0, f"Creation took {creation_time:.2f} seconds, expected < 1.0"
    
    def test_serialization_performance(self, valid_employee_list_response_data):
        """Test performance de serialización."""
        import time
        
        schema = EmployeeListResponse(**valid_employee_list_response_data)
        
        # Test model_dump performance
        start_time = time.time()
        for _ in range(1000):
            schema.model_dump()
        end_time = time.time()
        dump_time = end_time - start_time
        
        # Test model_dump_json performance
        start_time = time.time()
        for _ in range(1000):
            schema.model_dump_json()
        end_time = time.time()
        json_time = end_time - start_time
        
        # Performance: 1000 serializaciones en menos de 0.5 segundos cada una
        assert dump_time < 0.5, f"model_dump took {dump_time:.2f} seconds for 1000 calls"
        assert json_time < 0.5, f"model_dump_json took {json_time:.2f} seconds for 1000 calls"
    
    def test_memory_usage_with_large_lists(self):
        """Test uso de memoria con listas grandes."""
        import sys
        
        # Crear schema con lista grande
        large_projects = [f"Project {i}" for i in range(10000)]
        large_teams = [f"Team {i}" for i in range(5000)]
        
        data = {
            "id": 1,
            "full_name": "Test Employee",
            "employee_code": "EMP001",
            "email": "test@test.com",
            "status": EmployeeStatus.ACTIVE.value,
            "current_projects": large_projects,
            "current_teams": large_teams
        }
        
        schema = EmployeeSearchResponse(**data)
        
        # Verificar que las listas se mantienen correctamente
        assert len(schema.current_projects) == 10000
        assert len(schema.current_teams) == 5000
        
        # Verificar que el objeto no consume memoria excesiva
        schema_size = sys.getsizeof(schema)
        assert schema_size < 1000000, f"Schema size {schema_size} bytes is too large"


# ==========================================
# TESTS DE COMPATIBILIDAD Y MIGRACIÓN
# ==========================================

class TestResponseSchemasCompatibility:
    """Tests de compatibilidad para response schemas."""
    
    def test_backward_compatibility_with_missing_fields(self):
        """Test compatibilidad hacia atrás con campos faltantes."""
        # Datos mínimos que podrían venir de versiones anteriores
        minimal_employee_data = {
            "id": 1,
            "full_name": "Test Employee",
            "employee_code": "EMP001",
            "email": "test@test.com",
            "status": EmployeeStatus.ACTIVE.value
            # Faltan campos opcionales como position, department
        }
        
        schema = EmployeeListResponse(**minimal_employee_data)
        
        # Verificar que los campos opcionales tienen valores por defecto
        assert schema.position is None
        assert schema.department is None
        assert schema.is_available is True
    
    def test_forward_compatibility_with_extra_fields(self):
        """Test compatibilidad hacia adelante con campos extra."""
        # Datos con campos extra que podrían venir de versiones futuras
        extended_employee_data = {
            "id": 1,
            "full_name": "Test Employee",
            "employee_code": "EMP001",
            "email": "test@test.com",
            "status": EmployeeStatus.ACTIVE.value,
            "position": "Developer",
            "department": "IT",
            "is_available": True,
            # Campos extra que no existen en el schema actual
            "future_field_1": "some_value",
            "future_field_2": 123
        }
        
        # Pydantic debería ignorar campos extra por defecto
        schema = EmployeeListResponse(**extended_employee_data)
        
        # Verificar que los campos conocidos se procesan correctamente
        assert schema.id == 1
        assert schema.full_name == "Test Employee"
        assert schema.position == "Developer"
        
        # Verificar que los campos extra no están presentes
        assert not hasattr(schema, "future_field_1")
        assert not hasattr(schema, "future_field_2")
    
    def test_enum_value_compatibility(self):
        """Test compatibilidad de valores de enum."""
        # Test con valores de enum como string
        string_enum_data = {
            "id": 1,
            "full_name": "Test Employee",
            "employee_code": "EMP001",
            "email": "test@test.com",
            "status": "active"  # String en lugar de enum
        }
        
        schema = EmployeeListResponse(**string_enum_data)
        assert schema.status == EmployeeStatus.ACTIVE
        
        # Test con valores de enum como objeto enum
        enum_object_data = {
            "id": 1,
            "full_name": "Test Employee",
            "employee_code": "EMP001",
            "email": "test@test.com",
            "status": EmployeeStatus.INACTIVE  # Objeto enum directo
        }
        
        schema = EmployeeListResponse(**enum_object_data)
        assert schema.status == EmployeeStatus.INACTIVE