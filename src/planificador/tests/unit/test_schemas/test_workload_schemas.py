"""Tests para schemas de Workload.

Este módulo contiene tests unitarios para validar los schemas
relacionados con cargas de trabajo: WorkloadBase, WorkloadCreate y Workload.

Author: Assistant
Date: 2025-01-22
"""

import pytest
from datetime import datetime, date
from typing import Dict, Any
from decimal import Decimal
from pydantic import ValidationError

from planificador.schemas.workload.workload import (
    WorkloadBase,
    WorkloadCreate,
    Workload
)


class TestWorkloadBase:
    """Tests para el schema WorkloadBase."""

    def test_valid_workload_base(self, valid_workload_base_data: Dict[str, Any]):
        """Test: WorkloadBase con datos válidos.
        
        Args:
            valid_workload_base_data: Fixture con datos válidos
        """
        workload = WorkloadBase(**valid_workload_base_data)
        
        assert workload.employee_id == valid_workload_base_data["employee_id"]
        assert workload.project_id == valid_workload_base_data["project_id"]
        assert workload.date == valid_workload_base_data["date"]
        assert workload.week_number == valid_workload_base_data["week_number"]
        assert workload.month == valid_workload_base_data["month"]
        assert workload.year == valid_workload_base_data["year"]
        assert workload.planned_hours == valid_workload_base_data["planned_hours"]
        assert workload.actual_hours == valid_workload_base_data["actual_hours"]
        assert workload.utilization_percentage == valid_workload_base_data["utilization_percentage"]
        assert workload.efficiency_score == valid_workload_base_data["efficiency_score"]
        assert workload.productivity_index == valid_workload_base_data["productivity_index"]
        assert workload.is_billable == valid_workload_base_data["is_billable"]
        assert workload.notes == valid_workload_base_data["notes"]

    def test_workload_base_with_minimal_data(self, workload_minimal_data: Dict[str, Any]):
        """Test: WorkloadBase con datos mínimos requeridos."""
        workload = WorkloadBase(**workload_minimal_data)
        
        assert workload.employee_id == 1
        assert workload.project_id is None
        assert workload.date == date(2024, 3, 10)
        assert workload.week_number == 10
        assert workload.month == 3
        assert workload.year == 2024
        # Verificar valores por defecto
        assert workload.planned_hours is None
        assert workload.actual_hours is None
        assert workload.utilization_percentage is None
        assert workload.efficiency_score is None
        assert workload.productivity_index is None
        assert workload.is_billable is False  # Valor por defecto
        assert workload.notes is None

    def test_workload_base_without_project(self, workload_without_project: Dict[str, Any]):
        """Test: WorkloadBase sin proyecto específico."""
        workload = WorkloadBase(**workload_without_project)
        
        assert workload.employee_id == 1
        assert workload.project_id is None
        assert workload.date == date(2024, 4, 5)
        assert workload.planned_hours == Decimal("4.0")
        assert workload.actual_hours == Decimal("3.5")
        assert workload.is_billable is False
        assert workload.notes == "Tiempo administrativo"

    def test_workload_base_with_high_efficiency(self, workload_with_high_efficiency: Dict[str, Any]):
        """Test: WorkloadBase con alta eficiencia."""
        workload = WorkloadBase(**workload_with_high_efficiency)
        
        assert workload.employee_id == 2
        assert workload.project_id == 2
        assert workload.planned_hours == Decimal("6.0")
        assert workload.actual_hours == Decimal("6.0")
        assert workload.efficiency_score == Decimal("100.0")
        assert workload.productivity_index == Decimal("95.0")
        assert workload.is_billable is True

    def test_workload_base_boundary_values(self, workload_boundary_values: Dict[str, Any]):
        """Test: WorkloadBase con valores en los límites."""
        workload = WorkloadBase(**workload_boundary_values)
        
        assert workload.week_number == 53  # Máximo
        assert workload.month == 12  # Máximo
        assert workload.planned_hours == Decimal("24.0")  # Máximo
        assert workload.actual_hours == Decimal("24.0")  # Máximo
        assert workload.utilization_percentage == Decimal("100.0")  # Máximo
        assert workload.efficiency_score == Decimal("100.0")  # Máximo
        assert workload.productivity_index == Decimal("100.0")  # Máximo

    def test_workload_base_zero_hours(self, workload_zero_hours: Dict[str, Any]):
        """Test: WorkloadBase con cero horas."""
        workload = WorkloadBase(**workload_zero_hours)
        
        assert workload.planned_hours == Decimal("0.0")
        assert workload.actual_hours == Decimal("0.0")
        assert workload.utilization_percentage == Decimal("0.0")
        assert workload.efficiency_score == Decimal("0.0")
        assert workload.productivity_index == Decimal("0.0")
        assert workload.is_billable is False
        assert workload.notes == "Día festivo"

    def test_workload_base_required_fields(self):
        """Test: WorkloadBase falla sin campos obligatorios."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase()
        
        errors = exc_info.value.errors()
        required_fields = ["employee_id", "date", "week_number", "month", "year"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors), f"Campo {field} debería ser obligatorio"

    def test_workload_base_employee_id_required(self):
        """Test: WorkloadBase requiere employee_id."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(
                date=date(2024, 2, 15),
                week_number=7,
                month=2,
                year=2024
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("employee_id",) for error in errors)


class TestWorkloadBaseValidations:
    """Tests para validaciones específicas de WorkloadBase."""

    def test_date_consistency_month_mismatch(self, invalid_workload_inconsistent_date: Dict[str, Any]):
        """Test: WorkloadBase falla con fecha inconsistente (mes)."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(**invalid_workload_inconsistent_date)
        
        errors = exc_info.value.errors()
        assert any("El mes de la fecha debe coincidir con el campo month" in str(error["ctx"]["error"]) for error in errors)

    def test_date_consistency_year_mismatch(self, invalid_workload_year_mismatch: Dict[str, Any]):
        """Test: WorkloadBase falla con fecha inconsistente (año)."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(**invalid_workload_year_mismatch)
        
        errors = exc_info.value.errors()
        assert any("El año de la fecha debe coincidir con el campo year" in str(error["ctx"]["error"]) for error in errors)

    def test_hours_consistency_excessive_actual(self, invalid_workload_excessive_hours: Dict[str, Any]):
        """Test: WorkloadBase falla con horas reales excesivas."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(**invalid_workload_excessive_hours)
        
        errors = exc_info.value.errors()
        assert any("Las horas reales no pueden ser más del doble de las horas planificadas" in str(error["ctx"]["error"]) for error in errors)

    def test_efficiency_metrics_inconsistent(self, invalid_workload_inconsistent_efficiency: Dict[str, Any]):
        """Test: WorkloadBase falla con eficiencia inconsistente."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(**invalid_workload_inconsistent_efficiency)
        
        errors = exc_info.value.errors()
        assert any("El score de eficiencia no es consistente" in str(error["ctx"]["error"]) for error in errors)

    def test_negative_hours_validation(self, invalid_workload_negative_hours: Dict[str, Any]):
        """Test: WorkloadBase falla con horas negativas."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(**invalid_workload_negative_hours)
        
        errors = exc_info.value.errors()
        # Verificar que hay errores de validación para campos con valores negativos
        planned_hours_errors = [error for error in errors if error["loc"] == ("planned_hours",)]
        actual_hours_errors = [error for error in errors if error["loc"] == ("actual_hours",)]
        
        assert len(planned_hours_errors) > 0, "Debería haber error para planned_hours negativo"
        assert len(actual_hours_errors) > 0, "Debería haber error para actual_hours negativo"

    def test_excessive_percentage_validation(self, invalid_workload_excessive_percentage: Dict[str, Any]):
        """Test: WorkloadBase falla con porcentajes excesivos."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(**invalid_workload_excessive_percentage)
        
        errors = exc_info.value.errors()
        # Verificar que hay errores para porcentajes > 100
        percentage_fields = ["utilization_percentage", "efficiency_score", "productivity_index"]
        
        for field in percentage_fields:
            field_errors = [error for error in errors if error["loc"] == (field,)]
            assert len(field_errors) > 0, f"Debería haber error para {field} > 100"

    def test_week_number_out_of_range(self, invalid_workload_out_of_range_week: Dict[str, Any]):
        """Test: WorkloadBase falla con week_number fuera de rango."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(**invalid_workload_out_of_range_week)
        
        errors = exc_info.value.errors()
        week_errors = [error for error in errors if error["loc"] == ("week_number",)]
        assert len(week_errors) > 0, "Debería haber error para week_number > 53"

    def test_month_out_of_range(self, invalid_workload_out_of_range_month: Dict[str, Any]):
        """Test: WorkloadBase falla con month fuera de rango."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(**invalid_workload_out_of_range_month)
        
        errors = exc_info.value.errors()
        month_errors = [error for error in errors if error["loc"] == ("month",)]
        assert len(month_errors) > 0, "Debería haber error para month > 12"

    def test_year_out_of_range(self, invalid_workload_out_of_range_year: Dict[str, Any]):
        """Test: WorkloadBase falla con year fuera de rango."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(**invalid_workload_out_of_range_year)
        
        errors = exc_info.value.errors()
        year_errors = [error for error in errors if error["loc"] == ("year",)]
        assert len(year_errors) > 0, "Debería haber error para year > 2050"

    def test_hours_maximum_24(self):
        """Test: WorkloadBase falla con horas > 24."""
        test_date = date(2024, 2, 15)
        
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(
                employee_id=1,
                date=test_date,
                week_number=7,
                month=2,
                year=2024,
                planned_hours=Decimal("25.0")  # > 24
            )
        
        errors = exc_info.value.errors()
        planned_hours_errors = [error for error in errors if error["loc"] == ("planned_hours",)]
        assert len(planned_hours_errors) > 0, "Debería haber error para planned_hours > 24"

    def test_week_number_minimum_1(self):
        """Test: WorkloadBase falla con week_number < 1."""
        test_date = date(2024, 2, 15)
        
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(
                employee_id=1,
                date=test_date,
                week_number=0,  # < 1
                month=2,
                year=2024
            )
        
        errors = exc_info.value.errors()
        week_errors = [error for error in errors if error["loc"] == ("week_number",)]
        assert len(week_errors) > 0, "Debería haber error para week_number < 1"

    def test_month_minimum_1(self):
        """Test: WorkloadBase falla con month < 1."""
        test_date = date(2024, 2, 15)
        
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(
                employee_id=1,
                date=test_date,
                week_number=7,
                month=0,  # < 1
                year=2024
            )
        
        errors = exc_info.value.errors()
        month_errors = [error for error in errors if error["loc"] == ("month",)]
        assert len(month_errors) > 0, "Debería haber error para month < 1"

    def test_year_minimum_2020(self):
        """Test: WorkloadBase falla con year < 2020."""
        test_date = date(2024, 2, 15)
        
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(
                employee_id=1,
                date=test_date,
                week_number=7,
                month=2,
                year=2019  # < 2020
            )
        
        errors = exc_info.value.errors()
        year_errors = [error for error in errors if error["loc"] == ("year",)]
        assert len(year_errors) > 0, "Debería haber error para year < 2020"


class TestWorkloadBaseFieldTypes:
    """Tests para validación de tipos de campos en WorkloadBase."""

    def test_employee_id_type_validation(self):
        """Test: WorkloadBase valida tipo de employee_id."""
        test_date = date(2024, 2, 15)
        
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(
                employee_id="invalid",  # String en lugar de int
                date=test_date,
                week_number=7,
                month=2,
                year=2024
            )
        
        errors = exc_info.value.errors()
        employee_id_errors = [error for error in errors if error["loc"] == ("employee_id",)]
        assert len(employee_id_errors) > 0, "Debería haber error de tipo para employee_id"

    def test_date_type_validation(self):
        """Test: WorkloadBase valida tipo de date."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(
                employee_id=1,
                date="invalid-date",  # String inválido
                week_number=7,
                month=2,
                year=2024
            )
        
        errors = exc_info.value.errors()
        date_errors = [error for error in errors if error["loc"] == ("date",)]
        assert len(date_errors) > 0, "Debería haber error de tipo para date"

    def test_decimal_fields_type_validation(self):
        """Test: WorkloadBase valida tipos de campos Decimal."""
        test_date = date(2024, 2, 15)
        
        with pytest.raises(ValidationError) as exc_info:
            WorkloadBase(
                employee_id=1,
                date=test_date,
                week_number=7,
                month=2,
                year=2024,
                planned_hours="invalid",  # String en lugar de Decimal
                actual_hours="invalid"
            )
        
        errors = exc_info.value.errors()
        planned_hours_errors = [error for error in errors if error["loc"] == ("planned_hours",)]
        actual_hours_errors = [error for error in errors if error["loc"] == ("actual_hours",)]
        
        assert len(planned_hours_errors) > 0, "Debería haber error de tipo para planned_hours"
        assert len(actual_hours_errors) > 0, "Debería haber error de tipo para actual_hours"

    def test_boolean_field_type_validation(self):
        """Test: WorkloadBase valida tipo de is_billable."""
        test_date = date(2024, 2, 15)
        
        # Pydantic es flexible con booleanos, pero probemos con un tipo claramente inválido
        workload = WorkloadBase(
            employee_id=1,
            date=test_date,
            week_number=7,
            month=2,
            year=2024,
            is_billable="true"  # String que se puede convertir
        )
        
        assert workload.is_billable is True  # Pydantic convierte "true" a True


class TestWorkloadCreate:
    """Tests para el schema WorkloadCreate."""

    def test_valid_workload_create(self, valid_workload_create_data: Dict[str, Any]):
        """Test: WorkloadCreate con datos válidos."""
        workload = WorkloadCreate(**valid_workload_create_data)
        
        assert workload.employee_id == valid_workload_create_data["employee_id"]
        assert workload.project_id == valid_workload_create_data["project_id"]
        assert workload.date == valid_workload_create_data["date"]
        assert workload.week_number == valid_workload_create_data["week_number"]
        assert workload.month == valid_workload_create_data["month"]
        assert workload.year == valid_workload_create_data["year"]
        assert workload.planned_hours == valid_workload_create_data["planned_hours"]
        assert workload.actual_hours == valid_workload_create_data["actual_hours"]
        assert workload.is_billable == valid_workload_create_data["is_billable"]

    def test_workload_create_inherits_validations(self, invalid_workload_inconsistent_date: Dict[str, Any]):
        """Test: WorkloadCreate hereda validaciones de WorkloadBase."""
        with pytest.raises(ValidationError) as exc_info:
            WorkloadCreate(**invalid_workload_inconsistent_date)
        
        errors = exc_info.value.errors()
        assert any("El mes de la fecha debe coincidir con el campo month" in str(error["ctx"]["error"]) for error in errors)

    def test_workload_create_minimal_data(self, workload_minimal_data: Dict[str, Any]):
        """Test: WorkloadCreate con datos mínimos."""
        workload = WorkloadCreate(**workload_minimal_data)
        
        assert workload.employee_id == 1
        assert workload.date == date(2024, 3, 10)
        assert workload.is_billable is False  # Valor por defecto


class TestWorkload:
    """Tests para el schema Workload (completo con ID y timestamps)."""

    def test_valid_workload(self, valid_workload_data: Dict[str, Any]):
        """Test: Workload con datos válidos."""
        workload = Workload(**valid_workload_data)
        
        # Verificar campos heredados de WorkloadBase
        assert workload.employee_id == valid_workload_data["employee_id"]
        assert workload.project_id == valid_workload_data["project_id"]
        assert workload.date == valid_workload_data["date"]
        assert workload.week_number == valid_workload_data["week_number"]
        assert workload.month == valid_workload_data["month"]
        assert workload.year == valid_workload_data["year"]
        
        # Verificar campos adicionales
        assert workload.id == valid_workload_data["id"]
        assert workload.created_at == valid_workload_data["created_at"]
        assert workload.updated_at == valid_workload_data["updated_at"]

    def test_workload_required_id_and_timestamps(self):
        """Test: Workload requiere id, created_at y updated_at."""
        test_date = date(2024, 2, 15)
        
        with pytest.raises(ValidationError) as exc_info:
            Workload(
                employee_id=1,
                date=test_date,
                week_number=7,
                month=2,
                year=2024
                # Faltan id, created_at, updated_at
            )
        
        errors = exc_info.value.errors()
        required_fields = ["id", "created_at", "updated_at"]
        
        for field in required_fields:
            assert any(error["loc"] == (field,) for error in errors), f"Campo {field} debería ser obligatorio"

    def test_workload_inherits_validations(self, invalid_workload_excessive_hours: Dict[str, Any]):
        """Test: Workload hereda validaciones de WorkloadBase."""
        # Agregar campos requeridos para Workload
        invalid_workload_excessive_hours.update({
            "id": 1,
            "created_at": datetime(2024, 2, 15, 10, 30, 0),
            "updated_at": datetime(2024, 2, 15, 10, 30, 0)
        })
        
        with pytest.raises(ValidationError) as exc_info:
            Workload(**invalid_workload_excessive_hours)
        
        errors = exc_info.value.errors()
        assert any("Las horas reales no pueden ser más del doble de las horas planificadas" in str(error["ctx"]["error"]) for error in errors)


class TestWorkloadSerialization:
    """Tests de serialización para schemas de Workload."""

    def test_workload_base_model_dump(self, valid_workload_base_data: Dict[str, Any]):
        """Test: WorkloadBase serialización a diccionario."""
        workload = WorkloadBase(**valid_workload_base_data)
        data = workload.model_dump()
        
        assert isinstance(data, dict)
        assert data["employee_id"] == valid_workload_base_data["employee_id"]
        assert data["project_id"] == valid_workload_base_data["project_id"]
        assert data["date"] == valid_workload_base_data["date"]
        assert data["week_number"] == valid_workload_base_data["week_number"]
        assert data["is_billable"] == valid_workload_base_data["is_billable"]

    def test_workload_base_model_dump_json(self, valid_workload_base_data: Dict[str, Any]):
        """Test: WorkloadBase serialización a JSON."""
        workload = WorkloadBase(**valid_workload_base_data)
        json_data = workload.model_dump_json()
        
        assert isinstance(json_data, str)
        assert '"employee_id":1' in json_data
        assert '"is_billable":true' in json_data

    def test_workload_model_dump(self, valid_workload_data: Dict[str, Any]):
        """Test: Workload serialización a diccionario."""
        workload = Workload(**valid_workload_data)
        data = workload.model_dump()
        
        assert isinstance(data, dict)
        assert data["id"] == valid_workload_data["id"]
        assert data["employee_id"] == valid_workload_data["employee_id"]
        assert data["created_at"] == valid_workload_data["created_at"]
        assert data["updated_at"] == valid_workload_data["updated_at"]

    def test_workload_model_dump_json(self, valid_workload_data: Dict[str, Any]):
        """Test: Workload serialización a JSON."""
        workload = Workload(**valid_workload_data)
        json_data = workload.model_dump_json()
        
        assert isinstance(json_data, str)
        assert '"id":1' in json_data
        assert '"employee_id":1' in json_data

    def test_workload_model_validate(self, valid_workload_data: Dict[str, Any]):
        """Test: Workload deserialización desde diccionario."""
        workload = Workload.model_validate(valid_workload_data)
        
        assert isinstance(workload, Workload)
        assert workload.id == valid_workload_data["id"]
        assert workload.employee_id == valid_workload_data["employee_id"]
        assert workload.date == valid_workload_data["date"]

    def test_workload_model_validate_json(self, valid_workload_data: Dict[str, Any]):
        """Test: Workload deserialización desde JSON."""
        # Convertir datetime a string para JSON
        json_data = valid_workload_data.copy()
        json_data["date"] = json_data["date"].isoformat()
        json_data["created_at"] = json_data["created_at"].isoformat()
        json_data["updated_at"] = json_data["updated_at"].isoformat()
        json_data["planned_hours"] = str(json_data["planned_hours"])
        json_data["actual_hours"] = str(json_data["actual_hours"])
        json_data["utilization_percentage"] = str(json_data["utilization_percentage"])
        json_data["efficiency_score"] = str(json_data["efficiency_score"])
        json_data["productivity_index"] = str(json_data["productivity_index"])
        
        import json
        json_string = json.dumps(json_data)
        
        workload = Workload.model_validate_json(json_string)
        
        assert isinstance(workload, Workload)
        assert workload.id == valid_workload_data["id"]
        assert workload.employee_id == valid_workload_data["employee_id"]
        assert workload.date == valid_workload_data["date"]


class TestWorkloadEdgeCases:
    """Tests de casos límite para schemas de Workload."""

    def test_workload_with_none_optional_fields(self):
        """Test: WorkloadBase con campos opcionales en None."""
        test_date = date(2024, 2, 15)
        
        workload = WorkloadBase(
            employee_id=1,
            project_id=None,
            date=test_date,
            week_number=7,
            month=2,
            year=2024,
            planned_hours=None,
            actual_hours=None,
            utilization_percentage=None,
            efficiency_score=None,
            productivity_index=None,
            notes=None
        )
        
        assert workload.project_id is None
        assert workload.planned_hours is None
        assert workload.actual_hours is None
        assert workload.utilization_percentage is None
        assert workload.efficiency_score is None
        assert workload.productivity_index is None
        assert workload.notes is None
        assert workload.is_billable is False  # Valor por defecto

    def test_workload_with_empty_string_notes(self):
        """Test: WorkloadBase con notes como string vacío."""
        test_date = date(2024, 2, 15)
        
        workload = WorkloadBase(
            employee_id=1,
            date=test_date,
            week_number=7,
            month=2,
            year=2024,
            notes=""  # String vacío
        )
        
        assert workload.notes == ""

    def test_workload_with_very_long_notes(self):
        """Test: WorkloadBase con notes muy largas."""
        test_date = date(2024, 2, 15)
        long_notes = "A" * 1000  # String muy largo
        
        workload = WorkloadBase(
            employee_id=1,
            date=test_date,
            week_number=7,
            month=2,
            year=2024,
            notes=long_notes
        )
        
        assert workload.notes == long_notes
        assert len(workload.notes) == 1000

    def test_workload_decimal_precision(self):
        """Test: WorkloadBase maneja precisión de Decimal correctamente."""
        test_date = date(2024, 2, 15)
        
        workload = WorkloadBase(
            employee_id=1,
            date=test_date,
            week_number=7,
            month=2,
            year=2024,
            planned_hours=Decimal("8.123456789"),  # Alta precisión
            actual_hours=Decimal("7.987654321")
        )
        
        assert workload.planned_hours == Decimal("8.123456789")
        assert workload.actual_hours == Decimal("7.987654321")

    def test_workload_efficiency_calculation_edge_case(self):
        """Test: WorkloadBase con cálculo de eficiencia en caso límite."""
        test_date = date(2024, 2, 15)
        
        # Caso donde planned_hours > 0 pero actual_hours = 0 (división por cero)
        workload = WorkloadBase(
            employee_id=1,
            date=test_date,
            week_number=7,
            month=2,
            year=2024,
            planned_hours=Decimal("8.0"),
            actual_hours=Decimal("0.0"),
            efficiency_score=None  # No especificamos para evitar validación
        )
        
        assert workload.planned_hours == Decimal("8.0")
        assert workload.actual_hours == Decimal("0.0")
        assert workload.efficiency_score is None

    def test_workload_leap_year_date(self):
        """Test: WorkloadBase con fecha de año bisiesto."""
        leap_year_date = date(2024, 2, 29)  # 2024 es año bisiesto
        
        workload = WorkloadBase(
            employee_id=1,
            date=leap_year_date,
            week_number=9,  # Semana 9 de 2024
            month=2,
            year=2024
        )
        
        assert workload.date == leap_year_date
        assert workload.month == 2
        assert workload.year == 2024

    def test_workload_week_53_validation(self):
        """Test: WorkloadBase con semana 53 válida."""
        # 2024 tiene 53 semanas
        week_53_date = date(2024, 12, 30)  # Lunes de la semana 53
        
        workload = WorkloadBase(
            employee_id=1,
            date=week_53_date,
            week_number=53,
            month=12,
            year=2024
        )
        
        assert workload.week_number == 53
        assert workload.date == week_53_date