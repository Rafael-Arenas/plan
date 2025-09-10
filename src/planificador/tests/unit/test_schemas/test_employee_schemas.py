"""Tests para schemas de Employee.

Este módulo contiene tests comprehensivos para validar los schemas
de Employee, incluyendo validación básica, casos edge, serialización
y deserialización.

Author: Sistema de Testing
Date: 2025-01-21
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List
from pydantic import ValidationError

from planificador.schemas.employee.employee import (
    EmployeeBase,
    EmployeeCreate,
    EmployeeUpdate,
    Employee,
    EmployeeWithTeams,
    EmployeeWithProjects,
    EmployeeWithSchedules,
    EmployeeWithVacations,
    EmployeeWithWorkloads,
    EmployeeWithDetails,
    EmployeeSearchFilter,
     EmployeeStatus
)
from planificador.schemas.base.base import BaseSchema


# ============================================================================
# TESTS DE VALIDACIÓN BÁSICA
# ============================================================================

class TestEmployeeBasicValidation:
    """Tests de validación básica para schemas de Employee."""

    def test_employee_base_valid_data(self, valid_employee_base_data: Dict[str, Any]):
        """Test que EmployeeBase acepta datos válidos.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        employee = EmployeeBase(**valid_employee_base_data)
        
        assert employee.first_name == valid_employee_base_data["first_name"]
        assert employee.last_name == valid_employee_base_data["last_name"]
        assert employee.employee_code == valid_employee_base_data["employee_code"]
        assert employee.email == valid_employee_base_data["email"]
        assert employee.phone == valid_employee_base_data["phone"]
        assert employee.status == EmployeeStatus.ACTIVE
        assert employee.position == valid_employee_base_data["position"]
        assert employee.department == valid_employee_base_data["department"]

    def test_employee_create_valid_data(self, valid_employee_create_data: Dict[str, Any]):
        """Test que EmployeeCreate acepta datos válidos.
        
        Args:
            valid_employee_create_data: Fixture con datos válidos para creación
        """
        employee = EmployeeCreate(**valid_employee_create_data)
        
        assert employee.first_name == valid_employee_create_data["first_name"]
        assert employee.last_name == valid_employee_create_data["last_name"]
        assert employee.employee_code == valid_employee_create_data["employee_code"]
        assert employee.email == valid_employee_create_data["email"]
        assert employee.status == EmployeeStatus.ACTIVE

    def test_employee_update_valid_data(self, valid_employee_update_data: Dict[str, Any]):
        """Test que EmployeeUpdate acepta datos válidos.
        
        Args:
            valid_employee_update_data: Fixture con datos válidos para actualización
        """
        employee = EmployeeUpdate(**valid_employee_update_data)
        
        assert employee.first_name == valid_employee_update_data["first_name"]
        assert employee.last_name == valid_employee_update_data["last_name"]
        assert employee.email == valid_employee_update_data["email"]
        assert employee.position == valid_employee_update_data["position"]
        assert employee.department == valid_employee_update_data["department"]
        assert employee.status == EmployeeStatus.ACTIVE

    def test_employee_valid_data(self, valid_employee_data: Dict[str, Any]):
        """Test que Employee acepta datos válidos con campos de BD.
        
        Args:
            valid_employee_data: Fixture con datos válidos completos
        """
        employee = Employee(**valid_employee_data)
        
        assert employee.id == valid_employee_data["id"]
        assert employee.first_name == valid_employee_data["first_name"]
        assert employee.last_name == valid_employee_data["last_name"]
        assert employee.employee_code == valid_employee_data["employee_code"]
        assert employee.email == valid_employee_data["email"]
        assert employee.phone == valid_employee_data["phone"]
        assert employee.status == EmployeeStatus.ACTIVE
        assert employee.position == valid_employee_data["position"]
        assert employee.department == valid_employee_data["department"]
        assert isinstance(employee.created_at, datetime)
        assert isinstance(employee.updated_at, datetime)

    def test_employee_create_inheritance_from_base_schema(self):
        """Test que EmployeeCreate hereda de BaseSchema."""
        assert issubclass(EmployeeCreate, BaseSchema)
        
        # Verificar que tiene los campos esperados
        expected_fields = {"first_name", "last_name", "employee_code", "email", "phone", "status", "position", "department"}
        actual_fields = set(EmployeeCreate.model_fields.keys())
        assert expected_fields.issubset(actual_fields)

    def test_employee_update_inheritance_from_base_schema(self):
        """Test que EmployeeUpdate hereda de BaseSchema."""
        assert issubclass(EmployeeUpdate, BaseSchema)
        
        # Verificar que tiene los campos esperados
        expected_fields = {"first_name", "last_name", "employee_code", "email", "phone", "status", "position", "department"}
        actual_fields = set(EmployeeUpdate.model_fields.keys())
        assert expected_fields.issubset(actual_fields)

    def test_employee_inheritance_from_base(self):
        """Test que Employee hereda de EmployeeBase."""
        assert issubclass(Employee, EmployeeBase)
        assert issubclass(Employee, BaseSchema)
        
        # Verificar que tiene los campos adicionales de BD
        expected_fields = {"id", "created_at", "updated_at"}
        actual_fields = set(Employee.model_fields.keys())
        assert expected_fields.issubset(actual_fields)


# ============================================================================
# TESTS DE VALIDACIÓN DE CAMPOS REQUERIDOS
# ============================================================================

class TestEmployeeRequiredFields:
    """Tests de validación de campos requeridos."""

    def test_employee_base_missing_first_name(self, valid_employee_base_data: Dict[str, Any]):
        """Test que EmployeeBase falla sin first_name.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        data = valid_employee_base_data.copy()
        del data["first_name"]
        
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("first_name",)

    def test_employee_base_missing_last_name(self, valid_employee_base_data: Dict[str, Any]):
        """Test que EmployeeBase falla sin last_name.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        data = valid_employee_base_data.copy()
        del data["last_name"]
        
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("last_name",)

    def test_employee_base_missing_employee_code(self, valid_employee_base_data: Dict[str, Any]):
        """Test que EmployeeBase falla sin employee_code.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        data = valid_employee_base_data.copy()
        del data["employee_code"]
        
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("employee_code",)

    def test_employee_base_missing_email(self, valid_employee_base_data: Dict[str, Any]):
        """Test que EmployeeBase falla sin email.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        data = valid_employee_base_data.copy()
        del data["email"]
        
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert errors[0]["loc"] == ("email",)


# ============================================================================
# TESTS DE VALIDACIÓN DE CAMPOS OPCIONALES
# ============================================================================

class TestEmployeeOptionalFields:
    """Tests de validación de campos opcionales."""

    def test_employee_base_optional_phone(self, valid_employee_base_data: Dict[str, Any]):
        """Test que phone es opcional en EmployeeBase.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        data = valid_employee_base_data.copy()
        del data["phone"]
        
        employee = EmployeeBase(**data)
        assert employee.phone is None

    def test_employee_base_optional_position(self, valid_employee_base_data: Dict[str, Any]):
        """Test que position es opcional en EmployeeBase.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        data = valid_employee_base_data.copy()
        del data["position"]
        
        employee = EmployeeBase(**data)
        assert employee.position is None

    def test_employee_base_optional_department(self, valid_employee_base_data: Dict[str, Any]):
        """Test que department es opcional en EmployeeBase.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        data = valid_employee_base_data.copy()
        del data["department"]
        
        employee = EmployeeBase(**data)
        assert employee.department is None

    def test_employee_base_default_status(self, valid_employee_base_data: Dict[str, Any]):
        """Test que status tiene valor por defecto ACTIVE.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        data = valid_employee_base_data.copy()
        del data["status"]
        
        employee = EmployeeBase(**data)
        assert employee.status == EmployeeStatus.ACTIVE

    def test_employee_update_all_fields_optional(self):
        """Test que todos los campos son opcionales en EmployeeUpdate."""
        # EmployeeUpdate debería permitir crear instancia sin ningún campo
        employee = EmployeeUpdate()
        
        assert employee.first_name is None
        assert employee.last_name is None
        assert employee.employee_code is None
        assert employee.email is None
        assert employee.phone is None
        assert employee.status is None
        assert employee.position is None
        assert employee.department is None

    def test_employee_update_partial_data(self):
        """Test que EmployeeUpdate acepta datos parciales."""
        partial_data = {
            "first_name": "Jane",
            "email": "jane@company.com"
        }
        
        employee = EmployeeUpdate(**partial_data)
        
        assert employee.first_name == "Jane"
        assert employee.email == "jane@company.com"
        assert employee.last_name is None
        assert employee.employee_code is None
        assert employee.phone is None
        assert employee.status is None
        assert employee.position is None
        assert employee.department is None


# ============================================================================
# TESTS DE CASOS EDGE
# ============================================================================

class TestEmployeeEdgeCases:
    """Tests de casos edge para schemas de Employee."""

    def test_employee_base_empty_first_name(self, invalid_employee_empty_first_name: Dict[str, Any]):
        """Test que EmployeeBase rechaza first_name vacío.
        
        Args:
            invalid_employee_empty_first_name: Fixture con first_name vacío
        """
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**invalid_employee_empty_first_name)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("first_name",) for error in errors)

    def test_employee_base_empty_last_name(self, invalid_employee_empty_last_name: Dict[str, Any]):
        """Test que EmployeeBase rechaza last_name vacío.
        
        Args:
            invalid_employee_empty_last_name: Fixture con last_name vacío
        """
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**invalid_employee_empty_last_name)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("last_name",) for error in errors)

    def test_employee_base_empty_employee_code(self, invalid_employee_empty_code: Dict[str, Any]):
        """Test que EmployeeBase rechaza employee_code vacío.
        
        Args:
            invalid_employee_empty_code: Fixture con employee_code vacío
        """
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**invalid_employee_empty_code)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("employee_code",) for error in errors)

    def test_employee_base_invalid_email(self, invalid_employee_invalid_email: Dict[str, Any]):
        """Test que EmployeeBase rechaza email inválido.
        
        Args:
            invalid_employee_invalid_email: Fixture con email inválido
        """
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**invalid_employee_invalid_email)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)

    def test_employee_base_long_first_name(self, invalid_employee_long_first_name: Dict[str, Any]):
        """Test que EmployeeBase rechaza first_name muy largo.
        
        Args:
            invalid_employee_long_first_name: Fixture con first_name muy largo
        """
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**invalid_employee_long_first_name)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("first_name",) and "string_too_long" in error["type"] for error in errors)

    def test_employee_base_long_last_name(self, invalid_employee_long_last_name: Dict[str, Any]):
        """Test que EmployeeBase rechaza last_name muy largo.
        
        Args:
            invalid_employee_long_last_name: Fixture con last_name muy largo
        """
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**invalid_employee_long_last_name)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("last_name",) and "string_too_long" in error["type"] for error in errors)

    def test_employee_base_long_employee_code(self, invalid_employee_long_code: Dict[str, Any]):
        """Test que EmployeeBase rechaza employee_code muy largo.
        
        Args:
            invalid_employee_long_code: Fixture con employee_code muy largo
        """
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**invalid_employee_long_code)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("employee_code",) and "string_too_long" in error["type"] for error in errors)

    def test_employee_base_long_phone(self, invalid_employee_long_phone: Dict[str, Any]):
        """Test que EmployeeBase rechaza phone muy largo.
        
        Args:
            invalid_employee_long_phone: Fixture con phone muy largo
        """
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**invalid_employee_long_phone)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("phone",) and "string_too_long" in error["type"] for error in errors)

    def test_employee_base_long_position(self, invalid_employee_long_position: Dict[str, Any]):
        """Test que EmployeeBase rechaza position muy largo.
        
        Args:
            invalid_employee_long_position: Fixture con position muy largo
        """
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**invalid_employee_long_position)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("position",) and "string_too_long" in error["type"] for error in errors)

    def test_employee_base_long_department(self, invalid_employee_long_department: Dict[str, Any]):
        """Test que EmployeeBase rechaza department muy largo.
        
        Args:
            invalid_employee_long_department: Fixture con department muy largo
        """
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**invalid_employee_long_department)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("department",) and "string_too_long" in error["type"] for error in errors)

    def test_employee_base_minimal_data(self, minimal_employee_data: Dict[str, Any]):
        """Test que EmployeeBase acepta datos mínimos válidos.
        
        Args:
            minimal_employee_data: Fixture con datos mínimos
        """
        employee = EmployeeBase(**minimal_employee_data)
        
        assert employee.first_name == "Ana"
        assert employee.last_name == "García"
        assert employee.employee_code == "EMP-002"
        assert employee.email == "ana.garcia@example.com"
        assert employee.phone is None
        assert employee.status == EmployeeStatus.ACTIVE
        assert employee.position is None
        assert employee.department is None

    def test_employee_base_maximal_data(self, maximal_employee_data: Dict[str, Any]):
        """Test que EmployeeBase acepta datos con longitudes máximas.
        
        Args:
            maximal_employee_data: Fixture con datos máximos
        """
        employee = EmployeeBase(**maximal_employee_data)
        
        assert len(employee.first_name) == 11  # "Maximiliano"
        assert len(employee.last_name) == 22  # "De la Cruz y Rodríguez"
        assert len(employee.employee_code) == 15  # "EMP-MAX-001-EXT"
        assert len(employee.phone) == 19  # "+34-91-123-4567-890"
        assert len(employee.position) == 63  # "Director General de Operaciones y Estrategia Corporativa Global"
        assert len(employee.department) == 65  # "Alta Dirección y Gestión Estratégica de Proyectos Internacionales"
        assert employee.status == EmployeeStatus.ACTIVE

    def test_employee_base_none_optionals(self, employee_data_with_none_optionals: Dict[str, Any]):
        """Test que EmployeeBase acepta None en campos opcionales.
        
        Args:
            employee_data_with_none_optionals: Fixture con campos opcionales en None
        """
        employee = EmployeeBase(**employee_data_with_none_optionals)
        
        assert employee.first_name == "Juan"
        assert employee.last_name == "Pérez"
        assert employee.employee_code == "EMP-001"
        assert employee.email == "juan.perez@example.com"
        assert employee.phone is None
        assert employee.position is None
        assert employee.department is None
        assert employee.status == EmployeeStatus.ACTIVE  # Default value


# ============================================================================
# TESTS DE VALIDACIÓN DE ENUM STATUS
# ============================================================================

class TestEmployeeStatusValidation:
    """Tests de validación del enum EmployeeStatus."""

    def test_valid_status_values(self, valid_employee_base_data: Dict[str, Any]):
        """Test que acepta todos los valores válidos de status.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        valid_statuses = ["active", "inactive", "on_leave", "on_vacation", "terminated"]
        
        for status in valid_statuses:
            data = valid_employee_base_data.copy()
            data["status"] = status
            
            employee = EmployeeBase(**data)
            assert employee.status.value == status

    def test_invalid_status_values(self, valid_employee_base_data: Dict[str, Any], employee_status_variations: List[str]):
        """Test que rechaza valores inválidos de status.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
            employee_status_variations: Fixture con variaciones de status
        """
        valid_statuses = {"active", "inactive", "on_leave", "on_vacation", "terminated"}
        invalid_statuses = [status for status in employee_status_variations if status not in valid_statuses]
        
        for status in invalid_statuses:
            data = valid_employee_base_data.copy()
            data["status"] = status
            
            with pytest.raises(ValidationError) as exc_info:
                EmployeeBase(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("status",) for error in errors)

    def test_status_enum_values(self):
        """Test que el enum EmployeeStatus tiene los valores correctos."""
        expected_values = {"active", "inactive", "on_leave", "on_vacation", "terminated"}
        actual_values = {status.value for status in EmployeeStatus}
        
        assert actual_values == expected_values
    
    def test_status_enum_attributes(self):
        """Test que el enum EmployeeStatus tiene los atributos correctos."""
        assert EmployeeStatus.ACTIVE.value == "active"
        assert EmployeeStatus.INACTIVE.value == "inactive"
        assert EmployeeStatus.ON_LEAVE.value == "on_leave"
        assert EmployeeStatus.ON_VACATION.value == "on_vacation"
        assert EmployeeStatus.TERMINATED.value == "terminated"
    
    def test_status_enum_membership(self):
        """Test que todos los estados son miembros válidos del enum."""
        assert EmployeeStatus.ACTIVE in EmployeeStatus
        assert EmployeeStatus.INACTIVE in EmployeeStatus
        assert EmployeeStatus.ON_LEAVE in EmployeeStatus
        assert EmployeeStatus.ON_VACATION in EmployeeStatus
        assert EmployeeStatus.TERMINATED in EmployeeStatus
    
    def test_status_case_sensitivity(self, valid_employee_base_data: Dict[str, Any]):
        """Test que el status es case-sensitive."""
        data = valid_employee_base_data.copy()
        
        # Test case-sensitive validation
        invalid_cases = ["ACTIVE", "Active", "InActive", "ON_LEAVE", "On_Leave"]
        
        for invalid_status in invalid_cases:
            data["status"] = invalid_status
            
            with pytest.raises(ValidationError) as exc_info:
                EmployeeBase(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("status",) for error in errors)


# ============================================================================
# TESTS DE VALIDACIÓN DE CAMPOS ESPECÍFICOS
# ============================================================================

class TestEmployeeSpecificFieldValidation:
    """Tests de validación para campos específicos de Employee."""
    
    def test_employee_code_format_validation(self, valid_employee_base_data: Dict[str, Any]):
        """Test validación de formato de employee_code."""
        data = valid_employee_base_data.copy()
        
        # Test códigos válidos
        valid_codes = ["EMP-12345", "EMP-ABCDE", "E-123", "EMPLOYEE-001"]
        
        for code in valid_codes:
            data["employee_code"] = code
            employee = EmployeeBase(**data)
            assert employee.employee_code == code
    
    def test_employee_code_length_validation(self, valid_employee_base_data: Dict[str, Any]):
        """Test validación de longitud de employee_code."""
        data = valid_employee_base_data.copy()
        
        # Test código muy largo (más de 20 caracteres)
        data["employee_code"] = "A" * 21
        
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("employee_code",) for error in errors)
    
    def test_phone_format_validation(self, valid_employee_base_data: Dict[str, Any]):
        """Test validación de formato de teléfono."""
        data = valid_employee_base_data.copy()
        
        # Test formatos válidos de teléfono
        valid_phones = [
            "+1234567890",
            "+56912345678",
            "+1-234-567-8900",
            "(123) 456-7890",
            "123-456-7890"
        ]
        
        for phone in valid_phones:
            data["phone"] = phone
            employee = EmployeeBase(**data)
            assert employee.phone == phone
    
    def test_position_validation(self, valid_employee_base_data: Dict[str, Any]):
        """Test validación del campo position."""
        data = valid_employee_base_data.copy()
        
        # Test posiciones válidas
        valid_positions = [
            "Software Developer",
            "Senior Engineer",
            "Project Manager",
            "QA Analyst",
            "DevOps Engineer"
        ]
        
        for position in valid_positions:
            data["position"] = position
            employee = EmployeeBase(**data)
            assert employee.position == position
    
    def test_department_validation(self, valid_employee_base_data: Dict[str, Any]):
        """Test validación del campo department."""
        data = valid_employee_base_data.copy()
        
        # Test departamentos válidos
        valid_departments = [
            "Engineering",
            "Human Resources",
            "Sales",
            "Marketing",
            "Finance"
        ]
        
        for department in valid_departments:
            data["department"] = department
            employee = EmployeeBase(**data)
            assert employee.department == department

    def test_field_length_limits(self, valid_employee_base_data: Dict[str, Any]):
        """Test límites de longitud para todos los campos de texto."""
        data = valid_employee_base_data.copy()
        
        # Test límites específicos
        field_limits = {
            "first_name": 50,
            "last_name": 50,
            "employee_code": 20,
            "phone": 20,
            "position": 100,
            "department": 100
        }
        
        for field, max_length in field_limits.items():
            # Test longitud exacta en el límite (debería pasar)
            data[field] = "A" * max_length
            employee = EmployeeBase(**data)
            assert len(getattr(employee, field)) == max_length
            
            # Test longitud que excede el límite (debería fallar)
            data[field] = "A" * (max_length + 1)
            
            with pytest.raises(ValidationError) as exc_info:
                EmployeeBase(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == (field,) for error in errors)
            
            # Restaurar valor válido para siguiente iteración
            data[field] = valid_employee_base_data[field]

    def test_email_uniqueness_assumption(self, valid_employee_base_data: Dict[str, Any]):
        """Test que el schema acepta emails (unicidad se valida en BD)."""
        data = valid_employee_base_data.copy()
        
        # El schema no valida unicidad, solo formato
        duplicate_email = "test@company.com"
        data["email"] = duplicate_email
        
        employee1 = EmployeeBase(**data)
        employee2 = EmployeeBase(**data)
        
        assert employee1.email == duplicate_email
        assert employee2.email == duplicate_email
        # La unicidad se valida a nivel de base de datos, no en el schema
        """Test que status es case-sensitive.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        data = valid_employee_base_data.copy()
        data["status"] = "ACTIVE"  # Uppercase - should be invalid
        
        with pytest.raises(ValidationError) as exc_info:
            EmployeeBase(**data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("status",) for error in errors)


# ============================================================================
# TESTS DE VALIDACIÓN DE EMAIL
# ============================================================================

class TestEmployeeEmailValidation:
    """Tests de validación específica de email."""

    def test_valid_email_formats(self, valid_employee_base_data: Dict[str, Any]):
        """Test que acepta formatos válidos de email.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        valid_emails = [
            "user@domain.com",
            "user.name@domain.com",
            "user+tag@domain.com",
            "user123@domain123.com",
            "user@subdomain.domain.com"
        ]
        
        for email in valid_emails:
            data = valid_employee_base_data.copy()
            data["email"] = email
            
            employee = EmployeeBase(**data)
            assert employee.email == email

    def test_mixed_case_email_normalization(self, valid_employee_base_data: Dict[str, Any]):
        """Test que EmailStr normaliza el dominio a minúsculas.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        test_cases = [
            ("User@DOMAIN.COM", "User@domain.com"),
            ("USER@Domain.Com", "USER@domain.com"),
            ("user@SUBDOMAIN.DOMAIN.COM", "user@subdomain.domain.com")
        ]
        
        for input_email, expected_email in test_cases:
            data = valid_employee_base_data.copy()
            data["email"] = input_email
            
            employee = EmployeeBase(**data)
            assert employee.email == expected_email

    def test_invalid_email_formats(self, valid_employee_base_data: Dict[str, Any]):
        """Test que rechaza formatos inválidos de email.
        
        Args:
            valid_employee_base_data: Fixture con datos válidos
        """
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user..name@domain.com",
            "user@domain",
            "",
            "user@domain..com"
        ]
        
        for email in invalid_emails:
            data = valid_employee_base_data.copy()
            data["email"] = email
            
            with pytest.raises(ValidationError) as exc_info:
                EmployeeBase(**data)
            
            errors = exc_info.value.errors()
            assert any(error["loc"] == ("email",) for error in errors)


# ============================================================================
# TESTS DE SERIALIZACIÓN Y DESERIALIZACIÓN
# ============================================================================

class TestEmployeeSerializationDeserialization:
    """Tests de serialización y deserialización para Employee schemas."""

    def test_employee_to_dict(self, valid_employee_data):
        """Test serialización de Employee a diccionario."""
        employee = Employee(**valid_employee_data)
        employee_dict = employee.model_dump(mode='json')
        
        assert isinstance(employee_dict, dict)
        assert employee_dict["id"] == valid_employee_data["id"]
        assert employee_dict["first_name"] == valid_employee_data["first_name"]
        assert employee_dict["last_name"] == valid_employee_data["last_name"]
        assert employee_dict["employee_code"] == valid_employee_data["employee_code"]
        assert employee_dict["email"] == valid_employee_data["email"]
        assert employee_dict["status"] == valid_employee_data["status"]

    def test_employee_from_dict(self, valid_employee_data):
        """Test deserialización de Employee desde diccionario."""
        employee = Employee(**valid_employee_data)
        
        assert employee.id == valid_employee_data["id"]
        assert employee.first_name == valid_employee_data["first_name"]
        assert employee.last_name == valid_employee_data["last_name"]
        assert employee.employee_code == valid_employee_data["employee_code"]
        assert employee.email == valid_employee_data["email"]
        assert employee.status.value == valid_employee_data["status"]
        assert isinstance(employee.created_at, datetime)
        assert isinstance(employee.updated_at, datetime)

    def test_employee_to_json(self, valid_employee_data):
        """Test serialización de Employee a JSON."""
        employee = Employee(**valid_employee_data)
        employee_json = employee.model_dump_json()
        
        assert isinstance(employee_json, str)
        import json
        parsed = json.loads(employee_json)
        assert parsed["id"] == valid_employee_data["id"]
        assert parsed["first_name"] == valid_employee_data["first_name"]
        assert parsed["email"] == valid_employee_data["email"]

    def test_employee_from_json(self, valid_employee_data):
        """Test deserialización de Employee desde JSON."""
        employee = Employee(**valid_employee_data)
        employee_json = employee.model_dump_json()
        
        # Recrear desde JSON
        import json
        employee_dict = json.loads(employee_json)
        recreated_employee = Employee(**employee_dict)
        
        assert recreated_employee.id == employee.id
        assert recreated_employee.first_name == employee.first_name
        assert recreated_employee.email == employee.email

    def test_employee_with_none_values_serialization(self, valid_employee_data):
        """Test serialización de Employee con valores None."""
        employee_data = valid_employee_data.copy()
        employee_data.update({
            "phone": None,
            "position": None,
            "department": None
        })
        
        employee = Employee(**employee_data)
        employee_dict = employee.model_dump(mode='json')
        
        assert employee_dict["phone"] is None
        assert employee_dict["position"] is None
        assert employee_dict["department"] is None

    def test_employee_exclude_none_serialization(self, valid_employee_data):
        """Test serialización de Employee excluyendo valores None."""
        employee_data = valid_employee_data.copy()
        employee_data.update({
            "phone": None,
            "position": None,
            "department": None
        })
        
        employee = Employee(**employee_data)
        employee_dict = employee.model_dump(exclude_none=True, mode='json')
        
        assert "phone" not in employee_dict
        assert "position" not in employee_dict
        assert "department" not in employee_dict
        assert "first_name" in employee_dict
        assert "email" in employee_dict

    def test_employee_round_trip_serialization(self, valid_employee_data):
        """Test serialización y deserialización completa (round-trip)."""
        original_employee = Employee(**valid_employee_data)
        
        # Serializar a dict
        employee_dict = original_employee.model_dump()
        
        # Deserializar desde dict
        recreated_employee = Employee(**employee_dict)
        
        # Verificar que son equivalentes
        assert recreated_employee.id == original_employee.id
        assert recreated_employee.first_name == original_employee.first_name
        assert recreated_employee.last_name == original_employee.last_name
        assert recreated_employee.employee_code == original_employee.employee_code
        assert recreated_employee.email == original_employee.email
        assert recreated_employee.status == original_employee.status
        assert recreated_employee.phone == original_employee.phone
        assert recreated_employee.position == original_employee.position
        assert recreated_employee.department == original_employee.department
        assert recreated_employee.created_at == original_employee.created_at
        assert recreated_employee.updated_at == original_employee.updated_at