"""Tests para los esquemas de Vacation.

Este módulo contiene tests unitarios para validar el comportamiento
de los esquemas Pydantic relacionados con vacaciones.
"""

import pytest
from datetime import date, datetime
from typing import Dict, Any
from pydantic import ValidationError

from planificador.schemas.vacation import (
    VacationBase,
    VacationCreate,
    VacationUpdate,
    Vacation,
    VacationSearchFilter
)
from planificador.models.vacation import VacationType, VacationStatus


class TestVacationBase:
    """Tests para el schema VacationBase."""

    def test_valid_vacation_base_creation(self, valid_vacation_base_data: Dict[str, Any]):
        """Test de creación válida de VacationBase.
        
        Args:
            valid_vacation_base_data: Datos válidos para VacationBase
        """
        vacation = VacationBase(**valid_vacation_base_data)
        
        assert vacation.employee_id == valid_vacation_base_data["employee_id"]
        assert vacation.start_date == valid_vacation_base_data["start_date"]
        assert vacation.end_date == valid_vacation_base_data["end_date"]
        assert vacation.vacation_type == valid_vacation_base_data["vacation_type"]
        assert vacation.status == valid_vacation_base_data["status"]
        assert vacation.requested_date == valid_vacation_base_data["requested_date"]
        assert vacation.reason == valid_vacation_base_data["reason"]
        assert vacation.notes == valid_vacation_base_data["notes"]
        assert vacation.total_days == valid_vacation_base_data["total_days"]
        assert vacation.business_days == valid_vacation_base_data["business_days"]

    def test_minimal_vacation_base_creation(self, minimal_vacation_data: Dict[str, Any]):
        """Test de creación con datos mínimos requeridos.
        
        Args:
            minimal_vacation_data: Datos mínimos para VacationBase
        """
        vacation = VacationBase(**minimal_vacation_data)
        
        assert vacation.employee_id == minimal_vacation_data["employee_id"]
        assert vacation.start_date == minimal_vacation_data["start_date"]
        assert vacation.end_date == minimal_vacation_data["end_date"]
        assert vacation.vacation_type == VacationType.ANNUAL
        assert vacation.status == VacationStatus.PENDING  # Valor por defecto
        assert vacation.requested_date == minimal_vacation_data["requested_date"]
        assert vacation.reason is None  # Campo opcional
        assert vacation.notes is None  # Campo opcional
        assert vacation.total_days == minimal_vacation_data["total_days"]
        assert vacation.business_days == minimal_vacation_data["business_days"]

    def test_vacation_base_with_none_optionals(self, vacation_data_with_none_optionals: Dict[str, Any]):
        """Test de creación con campos opcionales en None.
        
        Args:
            vacation_data_with_none_optionals: Datos con campos opcionales en None
        """
        vacation = VacationBase(**vacation_data_with_none_optionals)
        
        assert vacation.approved_date is None
        assert vacation.approved_by is None
        assert vacation.reason is None
        assert vacation.notes is None

    def test_vacation_base_missing_required_fields(self):
        """Test de validación con campos requeridos faltantes."""
        with pytest.raises(ValidationError) as exc_info:
            VacationBase()
        
        errors = exc_info.value.errors()
        required_fields = {"employee_id", "start_date", "end_date", "vacation_type", "requested_date", "total_days", "business_days"}
        error_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        
        assert required_fields.issubset(error_fields)

    def test_vacation_base_invalid_employee_id(self, valid_vacation_base_data: Dict[str, Any]):
        """Test de validación con employee_id inválido.
        
        Args:
            valid_vacation_base_data: Datos válidos base
        """
        invalid_data = valid_vacation_base_data.copy()
        invalid_data["employee_id"] = 0  # Debe ser positivo
        
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("employee_id",) for error in errors)

    def test_vacation_base_invalid_total_days(self, invalid_vacation_negative_days: Dict[str, Any]):
        """Test de validación con total_days negativo.
        
        Args:
            invalid_vacation_negative_days: Datos con días negativos
        """
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(**invalid_vacation_negative_days)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("total_days",) for error in errors)

    def test_vacation_base_invalid_business_days(self, invalid_vacation_negative_days: Dict[str, Any]):
        """Test de validación con business_days negativo.
        
        Args:
            invalid_vacation_negative_days: Datos con días negativos
        """
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(**invalid_vacation_negative_days)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("business_days",) for error in errors)

    def test_vacation_base_zero_days(self, invalid_vacation_zero_days: Dict[str, Any]):
        """Test de validación con días en cero.
        
        Args:
            invalid_vacation_zero_days: Datos con días en cero
        """
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(**invalid_vacation_zero_days)
        
        errors = exc_info.value.errors()
        day_errors = [error for error in errors if error["loc"][0] in ("total_days", "business_days")]
        assert len(day_errors) > 0

    def test_vacation_base_invalid_approved_by_length(self, invalid_vacation_long_approved_by: Dict[str, Any]):
        """Test de validación con approved_by excediendo longitud máxima.
        
        Args:
            invalid_vacation_long_approved_by: Datos con approved_by muy largo
        """
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(**invalid_vacation_long_approved_by)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("approved_by",) for error in errors)

    def test_vacation_base_invalid_vacation_type(self, valid_vacation_base_data: Dict[str, Any]):
        """Test de validación con vacation_type inválido.
        
        Args:
            valid_vacation_base_data: Datos válidos base
        """
        invalid_data = valid_vacation_base_data.copy()
        invalid_data["vacation_type"] = "invalid_type"
        
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("vacation_type",) for error in errors)

    def test_vacation_base_invalid_status(self, valid_vacation_base_data: Dict[str, Any]):
        """Test de validación con status inválido.
        
        Args:
            valid_vacation_base_data: Datos válidos base
        """
        invalid_data = valid_vacation_base_data.copy()
        invalid_data["status"] = "invalid_status"
        
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("status",) for error in errors)

    def test_vacation_base_all_vacation_types(self, vacation_type_variations: VacationType, valid_vacation_base_data: Dict[str, Any]):
        """Test de creación con todos los tipos de vacación válidos.
        
        Args:
            vacation_type_variations: Tipo de vacación a probar
            valid_vacation_base_data: Datos válidos base
        """
        data = valid_vacation_base_data.copy()
        data["vacation_type"] = vacation_type_variations
        
        vacation = VacationBase(**data)
        assert vacation.vacation_type == vacation_type_variations

    def test_vacation_base_all_status_values(self, vacation_status_variations: VacationStatus, valid_vacation_base_data: Dict[str, Any]):
        """Test de creación con todos los estados de vacación válidos.
        
        Args:
            vacation_status_variations: Estado de vacación a probar
            valid_vacation_base_data: Datos válidos base
        """
        data = valid_vacation_base_data.copy()
        data["status"] = vacation_status_variations

        if vacation_status_variations != VacationStatus.APPROVED:
            data["approved_date"] = None
            data["approved_by"] = None
        
        vacation = VacationBase(**data)
        assert vacation.status == vacation_status_variations


class TestVacationValidations:
    """Tests para las validaciones específicas de Vacation."""

    def test_validate_date_range_invalid(self, invalid_vacation_dates: Dict[str, Any]):
        """Test de validación de rango de fechas inválido.
        
        Args:
            invalid_vacation_dates: Datos con fechas inválidas
        """
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(**invalid_vacation_dates)
        
        error_message = str(exc_info.value)
        assert "La fecha de fin debe ser posterior a la fecha de inicio" in error_message

    def test_validate_requested_date_future(self, invalid_vacation_future_requested_date: Dict[str, Any]):
        """Test de validación de requested_date en el futuro.
        
        Args:
            invalid_vacation_future_requested_date: Datos con requested_date futura
        """
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(**invalid_vacation_future_requested_date)
        
        error_message = str(exc_info.value)
        assert "La fecha de solicitud no puede ser posterior al inicio de vacaciones" in error_message

    def test_validate_approval_consistency_invalid(self, invalid_vacation_approval_without_approved_status: Dict[str, Any]):
        """Test de validación de consistencia de aprobación.
        
        Args:
            invalid_vacation_approval_without_approved_status: Datos con inconsistencia de aprobación
        """
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(**invalid_vacation_approval_without_approved_status)
        
        error_message = str(exc_info.value)
        assert "Las vacaciones pendientes no pueden tener datos de aprobación" in error_message

    def test_validate_approval_consistency_valid_approved(self, valid_vacation_base_data: Dict[str, Any]):
        """Test de validación de consistencia de aprobación válida.
        
        Args:
            valid_vacation_base_data: Datos válidos base
        """
        data = valid_vacation_base_data.copy()
        data["status"] = VacationStatus.APPROVED
        data["approved_date"] = date(2024, 6, 15)
        data["approved_by"] = "Manager Smith"
        
        vacation = VacationBase(**data)
        assert vacation.status == VacationStatus.APPROVED
        assert vacation.approved_date == date(2024, 6, 15)
        assert vacation.approved_by == "Manager Smith"

    def test_validate_approval_consistency_valid_pending(self, valid_vacation_base_data: Dict[str, Any]):
        """Test de validación de consistencia con status pending.
        
        Args:
            valid_vacation_base_data: Datos válidos base
        """
        data = valid_vacation_base_data.copy()
        data["status"] = VacationStatus.PENDING
        data["approved_date"] = None
        data["approved_by"] = None
        
        vacation = VacationBase(**data)
        assert vacation.status == VacationStatus.PENDING
        assert vacation.approved_date is None
        assert vacation.approved_by is None


class TestVacationCreate:
    """Tests para el schema VacationCreate."""

    def test_valid_vacation_create(self, valid_vacation_create_data: Dict[str, Any]):
        """Test de creación válida de VacationCreate.
        
        Args:
            valid_vacation_create_data: Datos válidos para VacationCreate
        """
        vacation = VacationCreate(**valid_vacation_create_data)
        
        assert vacation.employee_id == valid_vacation_create_data["employee_id"]
        assert vacation.start_date == valid_vacation_create_data["start_date"]
        assert vacation.end_date == valid_vacation_create_data["end_date"]
        assert vacation.vacation_type == valid_vacation_create_data["vacation_type"]

    def test_vacation_create_inherits_validations(self, invalid_vacation_dates: Dict[str, Any]):
        """Test que VacationCreate hereda las validaciones de VacationBase.
        
        Args:
            invalid_vacation_dates: Datos con fechas inválidas
        """
        with pytest.raises(ValidationError) as exc_info:
            VacationCreate(**invalid_vacation_dates)
        
        error_message = str(exc_info.value)
        assert "La fecha de fin debe ser posterior a la fecha de inicio" in error_message

    def test_vacation_create_minimal_data(self, minimal_vacation_data: Dict[str, Any]):
        """Test de creación con datos mínimos.
        
        Args:
            minimal_vacation_data: Datos mínimos requeridos
        """
        vacation = VacationCreate(**minimal_vacation_data)
        
        assert vacation.employee_id == minimal_vacation_data["employee_id"]
        assert vacation.total_days == minimal_vacation_data["total_days"]
        assert vacation.business_days == minimal_vacation_data["business_days"]


class TestVacationUpdate:
    """Tests para el schema VacationUpdate."""

    def test_valid_vacation_update(self, valid_vacation_update_data: Dict[str, Any]):
        """Test de actualización válida de VacationUpdate.
        
        Args:
            valid_vacation_update_data: Datos válidos para VacationUpdate
        """
        vacation = VacationUpdate(**valid_vacation_update_data)
        
        assert vacation.vacation_type == valid_vacation_update_data["vacation_type"]
        assert vacation.status == valid_vacation_update_data["status"]
        assert vacation.approved_date == valid_vacation_update_data["approved_date"]
        assert vacation.approved_by == valid_vacation_update_data["approved_by"]
        assert vacation.reason == valid_vacation_update_data["reason"]
        assert vacation.notes == valid_vacation_update_data["notes"]

    def test_vacation_update_empty_data(self):
        """Test de creación de VacationUpdate sin datos (todos opcionales)."""
        vacation = VacationUpdate()
        
        assert vacation.vacation_type is None
        assert vacation.status is None
        assert vacation.approved_date is None
        assert vacation.approved_by is None
        assert vacation.reason is None
        assert vacation.notes is None

    def test_vacation_update_partial_data(self):
        """Test de actualización parcial."""
        vacation = VacationUpdate(
            status=VacationStatus.APPROVED,
            approved_by="Manager Smith",
            approved_date=date(2024, 6, 15)
        )
        
        assert vacation.status == VacationStatus.APPROVED
        assert vacation.approved_by == "Manager Smith"
        assert vacation.approved_date == date(2024, 6, 15)
        assert vacation.vacation_type is None

    def test_vacation_update_invalid_status(self):
        """Test de validación con status inválido."""
        with pytest.raises(ValidationError) as exc_info:
            VacationUpdate(status="invalid_status")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("status",) for error in errors)

    def test_vacation_update_invalid_vacation_type(self):
        """Test de validación con vacation_type inválido."""
        with pytest.raises(ValidationError) as exc_info:
            VacationUpdate(vacation_type="invalid_type")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("vacation_type",) for error in errors)

    def test_vacation_update_long_approved_by(self):
        """Test de validación con approved_by muy largo."""
        with pytest.raises(ValidationError) as exc_info:
            VacationUpdate(approved_by="A" * 101)  # Excede max_length=100
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("approved_by",) for error in errors)


class TestVacation:
    """Tests para el schema Vacation completo."""

    def test_valid_vacation_complete(self, valid_vacation_data: Dict[str, Any]):
        """Test de creación válida de Vacation completo.
        
        Args:
            valid_vacation_data: Datos válidos para Vacation
        """
        vacation = Vacation(**valid_vacation_data)
        
        assert vacation.id == valid_vacation_data["id"]
        assert vacation.employee_id == valid_vacation_data["employee_id"]
        assert vacation.start_date == valid_vacation_data["start_date"]
        assert vacation.end_date == valid_vacation_data["end_date"]
        assert vacation.vacation_type == valid_vacation_data["vacation_type"]
        assert vacation.status == valid_vacation_data["status"]
        assert vacation.created_at == valid_vacation_data["created_at"]
        assert vacation.updated_at == valid_vacation_data["updated_at"]

    def test_vacation_inherits_validations(self, invalid_vacation_dates: Dict[str, Any]):
        """Test que Vacation hereda las validaciones de VacationBase.
        
        Args:
            invalid_vacation_dates: Datos con fechas inválidas
        """
        # Agregar campos requeridos para Vacation
        invalid_data = invalid_vacation_dates.copy()
        invalid_data["id"] = 1
        invalid_data["created_at"] = datetime.now()
        invalid_data["updated_at"] = datetime.now()
        
        with pytest.raises(ValidationError) as exc_info:
            Vacation(**invalid_data)
        
        error_message = str(exc_info.value)
        assert "La fecha de fin debe ser posterior a la fecha de inicio" in error_message

    def test_vacation_missing_database_fields(self, valid_vacation_base_data: Dict[str, Any]):
        """Test de validación con campos de BD faltantes.
        
        Args:
            valid_vacation_base_data: Datos válidos base
        """
        with pytest.raises(ValidationError) as exc_info:
            Vacation(**valid_vacation_base_data)
        
        errors = exc_info.value.errors()
        required_db_fields = {"id", "created_at", "updated_at"}
        error_fields = {error["loc"][0] for error in errors if error["type"] == "missing"}
        
        assert required_db_fields.issubset(error_fields)

    def test_vacation_invalid_id(self, valid_vacation_data: Dict[str, Any]):
        """Test de validación con ID inválido.
        
        Args:
            valid_vacation_data: Datos válidos para Vacation
        """
        invalid_data = valid_vacation_data.copy()
        invalid_data["id"] = 0  # Debe ser positivo
        
        with pytest.raises(ValidationError) as exc_info:
            Vacation(**invalid_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)


class TestVacationSearchFilter:
    """Tests para el schema VacationSearchFilter."""

    def test_valid_vacation_search_filter(self, valid_vacation_search_filter_data: Dict[str, Any]):
        """Test de creación válida de VacationSearchFilter.
        
        Args:
            valid_vacation_search_filter_data: Datos válidos para VacationSearchFilter
        """
        filter_obj = VacationSearchFilter(**valid_vacation_search_filter_data)
        
        assert filter_obj.employee_id == valid_vacation_search_filter_data["employee_id"]
        assert filter_obj.vacation_type == valid_vacation_search_filter_data["vacation_type"]
        assert filter_obj.status == valid_vacation_search_filter_data["status"]
        assert filter_obj.start_date_from == valid_vacation_search_filter_data["start_date_from"]
        assert filter_obj.start_date_to == valid_vacation_search_filter_data["start_date_to"]
        assert filter_obj.end_date_from == valid_vacation_search_filter_data["end_date_from"]
        assert filter_obj.end_date_to == valid_vacation_search_filter_data["end_date_to"]

    def test_vacation_search_filter_empty(self):
        """Test de creación de filtro vacío (todos los campos opcionales)."""
        filter_obj = VacationSearchFilter()
        
        assert filter_obj.employee_id is None
        assert filter_obj.vacation_type is None
        assert filter_obj.status is None
        assert filter_obj.start_date_from is None
        assert filter_obj.start_date_to is None
        assert filter_obj.end_date_from is None
        assert filter_obj.end_date_to is None

    def test_vacation_search_filter_partial(self):
        """Test de filtro parcial."""
        filter_obj = VacationSearchFilter(
            employee_id=1,
            status=VacationStatus.APPROVED
        )
        
        assert filter_obj.employee_id == 1
        assert filter_obj.status == VacationStatus.APPROVED
        assert filter_obj.vacation_type is None
        assert filter_obj.start_date_from is None

    def test_vacation_search_filter_invalid_employee_id(self):
        """Test de validación con employee_id inválido."""
        with pytest.raises(ValidationError) as exc_info:
            VacationSearchFilter(employee_id=0)  # Debe ser positivo
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("employee_id",) for error in errors)

    def test_vacation_search_filter_invalid_vacation_type(self):
        """Test de validación con vacation_type inválido."""
        with pytest.raises(ValidationError) as exc_info:
            VacationSearchFilter(vacation_type="invalid_type")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("vacation_type",) for error in errors)

    def test_vacation_search_filter_invalid_status(self):
        """Test de validación con status inválido."""
        with pytest.raises(ValidationError) as exc_info:
            VacationSearchFilter(status="invalid_status")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("status",) for error in errors)

    def test_vacation_search_filter_date_ranges(self):
        """Test de filtros con rangos de fechas."""
        filter_obj = VacationSearchFilter(
            start_date_from=date(2024, 1, 1),
            start_date_to=date(2024, 6, 30),
            end_date_from=date(2024, 7, 1),
            end_date_to=date(2024, 12, 31)
        )
        
        assert filter_obj.start_date_from == date(2024, 1, 1)
        assert filter_obj.start_date_to == date(2024, 6, 30)
        assert filter_obj.end_date_from == date(2024, 7, 1)
        assert filter_obj.end_date_to == date(2024, 12, 31)


class TestVacationEdgeCases:
    """Pruebas para casos límite y variaciones en los esquemas de Vacation."""

    def test_vacation_edge_cases(self, vacation_edge_cases: Dict[str, Any]):
        """Test de validación con casos límite.
        
        Args:
            vacation_edge_cases: Casos límite para vacaciones
        """
        vacation = VacationBase(**vacation_edge_cases)
        assert vacation.start_date == vacation_edge_cases["start_date"]
        assert vacation.end_date == vacation_edge_cases["end_date"]
        assert vacation.total_days == vacation_edge_cases["total_days"]
        assert vacation.business_days == vacation_edge_cases["business_days"]

    def test_vacation_single_day(self):
        """Test de validación para vacación de un solo día (debe fallar)."""
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(
                employee_id=1,
                start_date=date(2024, 7, 1),
                end_date=date(2024, 7, 1),  # Mismo día - debe fallar
                vacation_type=VacationType.SICK,
                requested_date=date(2024, 6, 30),
                total_days=1,
                business_days=1
            )
        
        error_message = str(exc_info.value)
        assert "La fecha de fin debe ser posterior a la fecha de inicio" in error_message

    def test_vacation_weekend_only(self):
        """Test de validación para vacación con business_days=0 (debe fallar)."""
        with pytest.raises(ValidationError) as exc_info:
            VacationBase(
                employee_id=1,
                start_date=date(2024, 7, 6),  # Sábado
                end_date=date(2024, 7, 7),    # Domingo
                vacation_type=VacationType.PERSONAL,
                requested_date=date(2024, 7, 1),
                total_days=2,
                business_days=0  # Sin días laborables - debe fallar
            )
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "greater_than_equal" for error in errors)
        assert any("business_days" in str(error) for error in errors)

    def test_vacation_maximal_data(self, maximal_vacation_data: Dict[str, Any]):
        """Test de vacación con datos máximos.
        
        Args:
            maximal_vacation_data: Datos máximos para vacación
        """
        vacation = VacationBase(**maximal_vacation_data)
        
        assert len(vacation.approved_by) == 100  # Máximo permitido
        assert vacation.reason is not None
        assert vacation.notes is not None
        assert vacation.status == VacationStatus.APPROVED
        assert vacation.approved_date is not None

    def test_vacation_type_enum_coverage(self, vacation_type_variations: VacationType):
        """Test de cobertura completa de tipos de vacación.
        
        Args:
            vacation_type_variations: Tipo de vacación a probar
        """
        base_data = {
            "employee_id": 1,
            "start_date": date(2024, 7, 1),
            "end_date": date(2024, 7, 15),
            "requested_date": date(2024, 6, 1),
            "total_days": 15,
            "business_days": 11
        }
        
        data = base_data.copy()
        data["vacation_type"] = vacation_type_variations
        
        vacation = VacationBase(**data)
        assert vacation.vacation_type == vacation_type_variations

    def test_vacation_status_enum_coverage(self, vacation_status_variations: VacationStatus):
        """Test de cobertura completa de estados de vacación.
        
        Args:
            vacation_status_variations: Estado de vacación a probar
        """
        base_data = {
            "employee_id": 1,
            "start_date": date(2024, 7, 1),
            "end_date": date(2024, 7, 15),
            "vacation_type": VacationType.ANNUAL,
            "requested_date": date(2024, 6, 1),
            "total_days": 15,
            "business_days": 11
        }
        
        data = base_data.copy()
        data["status"] = vacation_status_variations
        
        # Agregar campos de aprobación si es necesario
        if vacation_status_variations == VacationStatus.APPROVED:
            data["approved_date"] = date(2024, 6, 15)
            data["approved_by"] = "Manager Smith"
        
        vacation = VacationBase(**data)
        assert vacation.status == vacation_status_variations