"""Tests para schemas de Schedule.

Este módulo contiene tests unitarios para validar los schemas
relacionados con horarios: ScheduleBase, ScheduleCreate, ScheduleUpdate, 
Schedule y ScheduleSearchFilter.

Author: Assistant
Date: 2025-08-22
"""

import pytest
from datetime import datetime, date, time
from typing import Dict, Any
from pydantic import ValidationError

from planificador.schemas.schedule.schedule import (
    ScheduleBase,
    ScheduleCreate,
    ScheduleUpdate,
    Schedule,
    ScheduleSearchFilter
)


class TestScheduleBase:
    """Tests para el schema ScheduleBase."""

    def test_valid_schedule_base(self, valid_schedule_base_data: Dict[str, Any]):
        """Test: ScheduleBase con datos válidos.
        
        Args:
            valid_schedule_base_data: Fixture con datos válidos
        """
        schedule = ScheduleBase(**valid_schedule_base_data)
        
        assert schedule.employee_id == valid_schedule_base_data["employee_id"]
        assert schedule.project_id == valid_schedule_base_data["project_id"]
        assert schedule.team_id == valid_schedule_base_data["team_id"]
        assert schedule.status_code_id == valid_schedule_base_data["status_code_id"]
        assert schedule.date == date(2024, 2, 15)
        assert schedule.start_time == time(9, 0, 0)
        assert schedule.end_time == time(17, 0, 0)
        assert schedule.description == valid_schedule_base_data["description"]
        assert schedule.location == valid_schedule_base_data["location"]
        assert schedule.is_confirmed == valid_schedule_base_data["is_confirmed"]
        assert schedule.notes == valid_schedule_base_data["notes"]

    def test_schedule_base_with_minimal_data(self, schedule_minimal_data: Dict[str, Any]):
        """Test: ScheduleBase con datos mínimos requeridos."""
        schedule = ScheduleBase(**schedule_minimal_data)
        
        assert schedule.employee_id == 1
        assert schedule.project_id == 1
        assert schedule.team_id is None
        assert schedule.date == date(2024, 2, 15)
        # Verificar valores por defecto
        assert schedule.status_code_id is None
        assert schedule.start_time is None
        assert schedule.end_time is None
        assert schedule.description is None
        assert schedule.location is None
        assert schedule.is_confirmed is False
        assert schedule.notes is None

    def test_schedule_base_with_team_only(self, schedule_with_team_only: Dict[str, Any]):
        """Test: ScheduleBase con solo team_id (sin project_id)."""
        schedule = ScheduleBase(**schedule_with_team_only)
        
        assert schedule.employee_id == 1
        assert schedule.project_id is None
        assert schedule.team_id == 1
        assert schedule.date == date(2024, 2, 15)
        assert schedule.start_time == time(9, 0, 0)
        assert schedule.end_time == time(17, 0, 0)

    def test_schedule_base_without_times(self, schedule_without_times: Dict[str, Any]):
        """Test: ScheduleBase sin horarios específicos."""
        schedule = ScheduleBase(**schedule_without_times)
        
        assert schedule.employee_id == 1
        assert schedule.project_id == 1
        assert schedule.date == date(2024, 2, 15)
        assert schedule.start_time is None
        assert schedule.end_time is None
        assert schedule.description == "Trabajo todo el día"
        assert schedule.is_confirmed is True

    def test_schedule_base_no_project_or_team_fails(
        self, 
        invalid_schedule_no_project_or_team: Dict[str, Any]
    ):
        """Test: ScheduleBase falla sin project_id ni team_id."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**invalid_schedule_no_project_or_team)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Debe especificarse al menos un proyecto o equipo" in str(errors[0]["ctx"]["error"])

    def test_schedule_base_end_before_start_fails(
        self, 
        invalid_schedule_end_before_start: Dict[str, Any]
    ):
        """Test: ScheduleBase falla con end_time antes que start_time."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**invalid_schedule_end_before_start)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "La hora de fin debe ser posterior a la hora de inicio" in str(errors[0]["ctx"]["error"])

    def test_schedule_base_only_start_time_fails(
        self, 
        invalid_schedule_only_start_time: Dict[str, Any]
    ):
        """Test: ScheduleBase falla con solo start_time."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**invalid_schedule_only_start_time)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Debe especificarse tanto la hora de inicio como la de fin" in str(errors[0]["ctx"]["error"])

    def test_schedule_base_only_end_time_fails(
        self, 
        invalid_schedule_only_end_time: Dict[str, Any]
    ):
        """Test: ScheduleBase falla con solo end_time."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**invalid_schedule_only_end_time)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Debe especificarse tanto la hora de inicio como la de fin" in str(errors[0]["ctx"]["error"])

    def test_schedule_base_long_location_fails(
        self, 
        invalid_schedule_long_location: Dict[str, Any]
    ):
        """Test: ScheduleBase falla con location muy larga."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**invalid_schedule_long_location)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("location",)
        assert "String should have at most 200 characters" in errors[0]["msg"]

    def test_schedule_base_edge_cases(self, schedule_edge_cases):
        """Test: ScheduleBase con casos límite."""
        # schedule_edge_cases es un diccionario individual debido a la parametrización
        case_data = schedule_edge_cases
        
        # Estos casos deberían fallar la validación
        with pytest.raises(ValidationError):
            ScheduleBase(**case_data)

    def test_schedule_base_missing_employee_id_fails(self):
        """Test: ScheduleBase falla sin employee_id."""
        invalid_data = {
            "project_id": 1,
            "date": "2024-02-15"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("employee_id",)
        assert errors[0]["type"] == "missing"

    def test_schedule_base_missing_date_fails(self):
        """Test: ScheduleBase falla sin date."""
        invalid_data = {
            "employee_id": 1,
            "project_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("date",)
        assert errors[0]["type"] == "missing"

    def test_schedule_base_invalid_date_format_fails(self):
        """Test: ScheduleBase falla con formato de fecha inválido."""
        invalid_data = {
            "employee_id": 1,
            "project_id": 1,
            "date": "invalid-date"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("date",)
        assert "Input should be a valid date" in errors[0]["msg"]

    def test_schedule_base_invalid_time_format_fails(self):
        """Test: ScheduleBase falla con formato de hora inválido."""
        invalid_data = {
            "employee_id": 1,
            "project_id": 1,
            "date": "2024-02-15",
            "start_time": "invalid-time",
            "end_time": "17:00:00"
        }

        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**invalid_data)

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("start_time",)
        # El mensaje puede variar según la versión de Pydantic
        assert "time" in errors[0]["msg"].lower()


class TestScheduleCreate:
    """Tests para el schema ScheduleCreate."""

    def test_valid_schedule_create(self, valid_schedule_create_data: Dict[str, Any]):
        """Test: ScheduleCreate con datos válidos.
        
        Args:
            valid_schedule_create_data: Fixture con datos válidos
        """
        schedule = ScheduleCreate(**valid_schedule_create_data)
        
        assert schedule.employee_id == valid_schedule_create_data["employee_id"]
        assert schedule.project_id == valid_schedule_create_data["project_id"]
        assert schedule.team_id == valid_schedule_create_data["team_id"]
        assert schedule.status_code_id == valid_schedule_create_data["status_code_id"]
        assert schedule.date == date(2024, 2, 16)
        assert schedule.start_time == time(8, 30, 0)
        assert schedule.end_time == time(16, 30, 0)
        assert schedule.description == valid_schedule_create_data["description"]
        assert schedule.location == valid_schedule_create_data["location"]
        assert schedule.is_confirmed == valid_schedule_create_data["is_confirmed"]
        assert schedule.notes == valid_schedule_create_data["notes"]

    def test_schedule_create_inherits_validations(self):
        """Test: ScheduleCreate hereda validaciones de ScheduleBase."""
        # Test validación de project_or_team
        invalid_data = {
            "employee_id": 1,
            "date": "2024-02-15"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreate(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Debe especificarse al menos un proyecto o equipo" in str(errors[0]["ctx"]["error"])

    def test_schedule_create_with_minimal_data(self):
        """Test: ScheduleCreate con datos mínimos."""
        minimal_data = {
            "employee_id": 1,
            "project_id": 1,
            "date": "2024-02-15"
        }
        
        schedule = ScheduleCreate(**minimal_data)
        
        assert schedule.employee_id == 1
        assert schedule.project_id == 1
        assert schedule.date == date(2024, 2, 15)
        assert schedule.is_confirmed is False  # Valor por defecto


class TestScheduleUpdate:
    """Tests para el schema ScheduleUpdate."""

    def test_valid_schedule_update(self, valid_schedule_update_data: Dict[str, Any]):
        """Test: ScheduleUpdate con datos válidos.
        
        Args:
            valid_schedule_update_data: Fixture con datos válidos
        """
        schedule = ScheduleUpdate(**valid_schedule_update_data)
        
        assert schedule.employee_id == valid_schedule_update_data["employee_id"]
        assert schedule.project_id == valid_schedule_update_data["project_id"]
        assert schedule.status_code_id == valid_schedule_update_data["status_code_id"]
        assert schedule.start_time == time(10, 0, 0)
        assert schedule.end_time == time(18, 0, 0)
        assert schedule.description == valid_schedule_update_data["description"]
        assert schedule.is_confirmed == valid_schedule_update_data["is_confirmed"]

    def test_schedule_update_all_fields_optional(self):
        """Test: ScheduleUpdate permite todos los campos opcionales."""
        # Crear con datos vacíos
        schedule = ScheduleUpdate()
        
        assert schedule.employee_id is None
        assert schedule.project_id is None
        assert schedule.team_id is None
        assert schedule.status_code_id is None
        assert schedule.date is None
        assert schedule.start_time is None
        assert schedule.end_time is None
        assert schedule.description is None
        assert schedule.location is None
        assert schedule.is_confirmed is None
        assert schedule.notes is None

    def test_schedule_update_partial_data(self):
        """Test: ScheduleUpdate con datos parciales."""
        partial_data = {
            "description": "Descripción actualizada",
            "is_confirmed": True
        }
        
        schedule = ScheduleUpdate(**partial_data)
        
        assert schedule.description == "Descripción actualizada"
        assert schedule.is_confirmed is True
        assert schedule.employee_id is None
        assert schedule.project_id is None

    def test_schedule_update_location_validation(self):
        """Test: ScheduleUpdate valida longitud de location."""
        invalid_data = {
            "location": "A" * 201  # Excede el máximo
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ScheduleUpdate(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("location",)
        assert "String should have at most 200 characters" in errors[0]["msg"]


class TestSchedule:
    """Tests para el schema Schedule completo."""

    def test_valid_schedule(self, valid_schedule_data: Dict[str, Any]):
        """Test: Schedule con datos válidos.
        
        Args:
            valid_schedule_data: Fixture con datos válidos
        """
        schedule = Schedule(**valid_schedule_data)
        
        assert schedule.id == valid_schedule_data["id"]
        assert schedule.employee_id == valid_schedule_data["employee_id"]
        assert schedule.project_id == valid_schedule_data["project_id"]
        assert schedule.team_id == valid_schedule_data["team_id"]
        assert schedule.status_code_id == valid_schedule_data["status_code_id"]
        assert schedule.date == date(2024, 2, 15)
        assert schedule.start_time == time(9, 0, 0)
        assert schedule.end_time == time(17, 0, 0)
        assert schedule.description == valid_schedule_data["description"]
        assert schedule.location == valid_schedule_data["location"]
        assert schedule.is_confirmed == valid_schedule_data["is_confirmed"]
        assert schedule.notes == valid_schedule_data["notes"]
        assert schedule.created_at == datetime(2024, 2, 1, 10, 0, 0)
        assert schedule.updated_at == datetime(2024, 2, 1, 10, 0, 0)

    def test_schedule_missing_id_fails(self):
        """Test: Schedule falla sin id."""
        invalid_data = {
            "employee_id": 1,
            "project_id": 1,
            "date": "2024-02-15",
            "created_at": "2024-02-01T10:00:00",
            "updated_at": "2024-02-01T10:00:00"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Schedule(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("id",)
        assert errors[0]["type"] == "missing"

    def test_schedule_missing_timestamps_fails(self):
        """Test: Schedule falla sin timestamps."""
        invalid_data = {
            "id": 1,
            "employee_id": 1,
            "project_id": 1,
            "date": "2024-02-15"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Schedule(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 2
        error_locs = [error["loc"] for error in errors]
        assert ("created_at",) in error_locs
        assert ("updated_at",) in error_locs


class TestScheduleSearchFilter:
    """Tests para el schema ScheduleSearchFilter."""

    def test_valid_schedule_search_filter(
        self, 
        valid_schedule_search_filter_data: Dict[str, Any]
    ):
        """Test: ScheduleSearchFilter con datos válidos.
        
        Args:
            valid_schedule_search_filter_data: Fixture con datos válidos
        """
        filter_obj = ScheduleSearchFilter(**valid_schedule_search_filter_data)
        
        assert filter_obj.employee_id == valid_schedule_search_filter_data["employee_id"]
        assert filter_obj.project_id == valid_schedule_search_filter_data["project_id"]
        assert filter_obj.date_from == date(2024, 2, 1)
        assert filter_obj.date_to == date(2024, 2, 29)
        assert filter_obj.is_confirmed == valid_schedule_search_filter_data["is_confirmed"]

    def test_schedule_search_filter_all_fields_optional(self):
        """Test: ScheduleSearchFilter permite todos los campos opcionales."""
        filter_obj = ScheduleSearchFilter()
        
        assert filter_obj.employee_id is None
        assert filter_obj.project_id is None
        assert filter_obj.team_id is None
        assert filter_obj.status_code_id is None
        assert filter_obj.date_from is None
        assert filter_obj.date_to is None
        assert filter_obj.is_confirmed is None

    def test_schedule_search_filter_partial_data(self):
        """Test: ScheduleSearchFilter con datos parciales."""
        partial_data = {
            "employee_id": 1,
            "is_confirmed": True
        }
        
        filter_obj = ScheduleSearchFilter(**partial_data)
        
        assert filter_obj.employee_id == 1
        assert filter_obj.is_confirmed is True
        assert filter_obj.project_id is None
        assert filter_obj.date_from is None

    def test_schedule_search_filter_date_range(self):
        """Test: ScheduleSearchFilter con rango de fechas."""
        date_range_data = {
            "date_from": "2024-01-01",
            "date_to": "2024-12-31"
        }
        
        filter_obj = ScheduleSearchFilter(**date_range_data)
        
        assert filter_obj.date_from == date(2024, 1, 1)
        assert filter_obj.date_to == date(2024, 12, 31)

    def test_schedule_search_filter_invalid_date_format_fails(self):
        """Test: ScheduleSearchFilter falla con formato de fecha inválido."""
        invalid_data = {
            "date_from": "invalid-date"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ScheduleSearchFilter(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("date_from",)
        assert "Input should be a valid date" in errors[0]["msg"]


class TestScheduleValidations:
    """Tests específicos para validaciones personalizadas de Schedule."""

    def test_time_range_validation_success(self):
        """Test: Validación exitosa de rango de tiempo."""
        valid_data = {
            "employee_id": 1,
            "project_id": 1,
            "date": "2024-02-15",
            "start_time": "09:00:00",
            "end_time": "17:00:00"
        }
        
        schedule = ScheduleBase(**valid_data)
        assert schedule.start_time == time(9, 0, 0)
        assert schedule.end_time == time(17, 0, 0)

    def test_time_range_validation_equal_times_fails(self):
        """Test: Validación falla con horarios iguales."""
        invalid_data = {
            "employee_id": 1,
            "project_id": 1,
            "date": "2024-02-15",
            "start_time": "09:00:00",
            "end_time": "09:00:00"  # Igual a start_time
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "La hora de fin debe ser posterior a la hora de inicio" in str(errors[0]["ctx"]["error"])

    def test_project_or_team_validation_both_provided_success(self):
        """Test: Validación exitosa con ambos project_id y team_id."""
        valid_data = {
            "employee_id": 1,
            "project_id": 1,
            "team_id": 1,
            "date": "2024-02-15"
        }
        
        schedule = ScheduleBase(**valid_data)
        assert schedule.project_id == 1
        assert schedule.team_id == 1

    def test_project_or_team_validation_only_project_success(self):
        """Test: Validación exitosa con solo project_id."""
        valid_data = {
            "employee_id": 1,
            "project_id": 1,
            "date": "2024-02-15"
        }
        
        schedule = ScheduleBase(**valid_data)
        assert schedule.project_id == 1
        assert schedule.team_id is None

    def test_project_or_team_validation_only_team_success(self):
        """Test: Validación exitosa con solo team_id."""
        valid_data = {
            "employee_id": 1,
            "team_id": 1,
            "date": "2024-02-15"
        }
        
        schedule = ScheduleBase(**valid_data)
        assert schedule.project_id is None
        assert schedule.team_id == 1

    def test_time_consistency_validation_both_none_success(self):
        """Test: Validación exitosa con ambos horarios None."""
        valid_data = {
            "employee_id": 1,
            "project_id": 1,
            "date": "2024-02-15"
            # start_time y end_time son None por defecto
        }
        
        schedule = ScheduleBase(**valid_data)
        assert schedule.start_time is None
        assert schedule.end_time is None

    def test_time_consistency_validation_both_provided_success(self):
        """Test: Validación exitosa con ambos horarios proporcionados."""
        valid_data = {
            "employee_id": 1,
            "project_id": 1,
            "date": "2024-02-15",
            "start_time": "09:00:00",
            "end_time": "17:00:00"
        }
        
        schedule = ScheduleBase(**valid_data)
        assert schedule.start_time == time(9, 0, 0)
        assert schedule.end_time == time(17, 0, 0)

    def test_multiple_validation_errors(self):
        """Test: Múltiples errores de validación simultáneos."""
        invalid_data = {
            "employee_id": 1,
            # Falta project_id y team_id
            "date": "2024-02-15",
            "start_time": "17:00:00",  # Hora de inicio posterior a fin
            "end_time": "09:00:00"    # Hora de fin anterior a inicio
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ScheduleBase(**invalid_data)
        
        errors = exc_info.value.errors()
        # Los validadores se ejecutan en orden, el primero que falla detiene la validación
        # En este caso, validate_time_range se ejecuta antes que validate_project_or_team
        assert len(errors) >= 1
        assert 'hora de fin debe ser posterior' in str(errors[0]['msg'])