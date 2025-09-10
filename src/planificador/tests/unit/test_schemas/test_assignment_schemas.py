# src/planificador/tests/unit/test_schemas/test_assignment_schemas.py
"""
Tests unitarios para schemas de Assignment.

Este módulo contiene tests para validar:
- ProjectAssignmentBase: Schema base con validaciones
- ProjectAssignmentCreate: Schema para creación
- ProjectAssignmentUpdate: Schema para actualización
- ProjectAssignment: Schema completo con ID
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from pydantic import ValidationError

from planificador.schemas.assignment.assignment import (
    ProjectAssignmentBase,
    ProjectAssignmentCreate,
    ProjectAssignmentUpdate,
    ProjectAssignment
)


class TestProjectAssignmentBase:
    """Tests para ProjectAssignmentBase schema."""

    def test_valid_creation(self, valid_assignment_base_data):
        """Test creación válida de ProjectAssignmentBase."""
        assignment = ProjectAssignmentBase(**valid_assignment_base_data)
        
        assert assignment.employee_id == valid_assignment_base_data["employee_id"]
        assert assignment.project_id == valid_assignment_base_data["project_id"]
        assert assignment.start_date == valid_assignment_base_data["start_date"]
        assert assignment.end_date == valid_assignment_base_data["end_date"]
        assert assignment.allocated_hours_per_day == valid_assignment_base_data["allocated_hours_per_day"]
        assert assignment.percentage_allocation == valid_assignment_base_data["percentage_allocation"]
        assert assignment.role_in_project == valid_assignment_base_data["role_in_project"]
        assert assignment.is_active == valid_assignment_base_data["is_active"]
        assert assignment.notes == valid_assignment_base_data["notes"]

    def test_required_fields(self):
        """Test campos obligatorios."""
        # Test sin employee_id
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentBase(
                project_id=1,
                start_date=date(2025, 1, 1)
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("employee_id",) for error in errors)
        
        # Test sin project_id
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentBase(
                employee_id=1,
                start_date=date(2025, 1, 1)
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("project_id",) for error in errors)
        
        # Test sin start_date
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentBase(
                employee_id=1,
                project_id=1
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("start_date",) for error in errors)

    def test_optional_fields_defaults(self):
        """Test valores por defecto de campos opcionales."""
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1)
        )
        
        assert assignment.end_date is None
        assert assignment.allocated_hours_per_day is None
        assert assignment.percentage_allocation is None
        assert assignment.role_in_project is None
        assert assignment.is_active is True  # Valor por defecto
        assert assignment.notes is None

    def test_allocated_hours_validation(self):
        """Test validación de horas asignadas por día."""
        # Test horas negativas
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentBase(
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 1),
                allocated_hours_per_day=Decimal("-1")
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("allocated_hours_per_day",) for error in errors)
        
        # Test horas excesivas
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentBase(
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 1),
                allocated_hours_per_day=Decimal("25")
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("allocated_hours_per_day",) for error in errors)
        
        # Test horas válidas
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            allocated_hours_per_day=Decimal("8")
        )
        assert assignment.allocated_hours_per_day == Decimal("8")

    def test_percentage_allocation_validation(self):
        """Test validación de porcentaje de asignación."""
        # Test porcentaje negativo
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentBase(
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 1),
                percentage_allocation=Decimal("-10")
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("percentage_allocation",) for error in errors)
        
        # Test porcentaje excesivo
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentBase(
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 1),
                percentage_allocation=Decimal("150")
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("percentage_allocation",) for error in errors)
        
        # Test porcentaje válido
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            percentage_allocation=Decimal("50")
        )
        assert assignment.percentage_allocation == Decimal("50")

    def test_role_in_project_length(self):
        """Test validación de longitud del rol en proyecto."""
        # Test rol muy largo
        long_role = "x" * 101
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentBase(
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 1),
                role_in_project=long_role
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("role_in_project",) for error in errors)
        
        # Test rol válido
        valid_role = "x" * 100
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            role_in_project=valid_role
        )
        assert assignment.role_in_project == valid_role

    def test_date_range_validation(self):
        """Test validación de rango de fechas."""
        # Test end_date anterior a start_date
        with pytest.raises(ValueError, match="La fecha de fin debe ser posterior a la fecha de inicio"):
            ProjectAssignmentBase(
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 10),
                end_date=date(2025, 1, 5)
            )
        
        # Test end_date igual a start_date
        with pytest.raises(ValueError, match="La fecha de fin debe ser posterior a la fecha de inicio"):
            ProjectAssignmentBase(
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 10),
                end_date=date(2025, 1, 10)
            )
        
        # Test fechas válidas
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        assert assignment.start_date == date(2025, 1, 1)
        assert assignment.end_date == date(2025, 1, 31)

    def test_allocation_consistency_validation(self):
        """Test validación de consistencia entre horas y porcentaje."""
        # Test inconsistencia (8 horas debería ser 100%)
        with pytest.raises(ValueError, match="Las horas asignadas por día y el porcentaje de asignación no son consistentes"):
            ProjectAssignmentBase(
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 1),
                allocated_hours_per_day=Decimal("8"),
                percentage_allocation=Decimal("50")  # Inconsistente
            )
        
        # Test consistencia válida (4 horas = 50%)
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            allocated_hours_per_day=Decimal("4"),
            percentage_allocation=Decimal("50")
        )
        assert assignment.allocated_hours_per_day == Decimal("4")
        assert assignment.percentage_allocation == Decimal("50")
        
        # Test solo uno de los campos (válido)
        assignment_only_hours = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            allocated_hours_per_day=Decimal("6")
        )
        assert assignment_only_hours.allocated_hours_per_day == Decimal("6")
        assert assignment_only_hours.percentage_allocation is None

    def test_serialization(self, valid_assignment_base_data):
        """Test serialización del schema."""
        assignment = ProjectAssignmentBase(**valid_assignment_base_data)
        data = assignment.model_dump()
        
        assert data["employee_id"] == valid_assignment_base_data["employee_id"]
        assert data["project_id"] == valid_assignment_base_data["project_id"]
        assert data["start_date"] == valid_assignment_base_data["start_date"]
        assert data["end_date"] == valid_assignment_base_data["end_date"]
        assert data["allocated_hours_per_day"] == valid_assignment_base_data["allocated_hours_per_day"]
        assert data["percentage_allocation"] == valid_assignment_base_data["percentage_allocation"]
        assert data["role_in_project"] == valid_assignment_base_data["role_in_project"]
        assert data["is_active"] == valid_assignment_base_data["is_active"]
        assert data["notes"] == valid_assignment_base_data["notes"]

    def test_inheritance_from_base_schema(self):
        """Test herencia de BaseSchema."""
        from planificador.schemas.base.base import BaseSchema
        
        assert issubclass(ProjectAssignmentBase, BaseSchema)
        
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1)
        )
        assert isinstance(assignment, BaseSchema)


class TestProjectAssignmentCreate:
    """Tests para ProjectAssignmentCreate schema."""

    def test_valid_creation(self, valid_assignment_create_data):
        """Test creación válida de ProjectAssignmentCreate."""
        assignment = ProjectAssignmentCreate(**valid_assignment_create_data)
        
        assert assignment.employee_id == valid_assignment_create_data["employee_id"]
        assert assignment.project_id == valid_assignment_create_data["project_id"]
        assert assignment.start_date == valid_assignment_create_data["start_date"]

    def test_inheritance_from_base(self):
        """Test herencia de ProjectAssignmentBase."""
        assert issubclass(ProjectAssignmentCreate, ProjectAssignmentBase)
        
        assignment = ProjectAssignmentCreate(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1)
        )
        assert isinstance(assignment, ProjectAssignmentBase)

    def test_all_validations_inherited(self):
        """Test que todas las validaciones se heredan correctamente."""
        # Test validación de fechas
        with pytest.raises(ValueError, match="La fecha de fin debe ser posterior a la fecha de inicio"):
            ProjectAssignmentCreate(
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 10),
                end_date=date(2025, 1, 5)
            )
        
        # Test validación de consistencia
        with pytest.raises(ValueError, match="Las horas asignadas por día y el porcentaje de asignación no son consistentes"):
            ProjectAssignmentCreate(
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 1),
                allocated_hours_per_day=Decimal("8"),
                percentage_allocation=Decimal("25")
            )


class TestProjectAssignmentUpdate:
    """Tests para ProjectAssignmentUpdate schema."""

    def test_all_fields_optional(self):
        """Test que todos los campos son opcionales."""
        assignment = ProjectAssignmentUpdate()
        
        assert assignment.employee_id is None
        assert assignment.project_id is None
        assert assignment.start_date is None
        assert assignment.end_date is None
        assert assignment.allocated_hours_per_day is None
        assert assignment.percentage_allocation is None
        assert assignment.role_in_project is None
        assert assignment.is_active is None
        assert assignment.notes is None

    def test_partial_update(self, valid_assignment_update_data):
        """Test actualización parcial."""
        assignment = ProjectAssignmentUpdate(**valid_assignment_update_data)
        
        assert assignment.role_in_project == valid_assignment_update_data["role_in_project"]
        assert assignment.is_active == valid_assignment_update_data["is_active"]
        assert assignment.notes == valid_assignment_update_data["notes"]
        # Otros campos no especificados deben ser None
        assert assignment.employee_id is None
        assert assignment.project_id is None

    def test_field_validations(self):
        """Test validaciones de campos individuales."""
        # Test horas inválidas
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentUpdate(allocated_hours_per_day=Decimal("-1"))
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("allocated_hours_per_day",) for error in errors)
        
        # Test porcentaje inválido
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentUpdate(percentage_allocation=Decimal("150"))
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("percentage_allocation",) for error in errors)
        
        # Test rol muy largo
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignmentUpdate(role_in_project="x" * 101)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("role_in_project",) for error in errors)

    def test_inheritance_from_base_schema(self):
        """Test herencia de BaseSchema."""
        from planificador.schemas.base.base import BaseSchema
        
        assert issubclass(ProjectAssignmentUpdate, BaseSchema)
        
        assignment = ProjectAssignmentUpdate()
        assert isinstance(assignment, BaseSchema)

    def test_serialization(self, valid_assignment_update_data):
        """Test serialización del schema."""
        assignment = ProjectAssignmentUpdate(**valid_assignment_update_data)
        data = assignment.model_dump()
        
        assert data["role_in_project"] == valid_assignment_update_data["role_in_project"]
        assert data["is_active"] == valid_assignment_update_data["is_active"]
        assert data["notes"] == valid_assignment_update_data["notes"]


class TestProjectAssignment:
    """Tests para ProjectAssignment schema."""

    def test_valid_creation(self, valid_assignment_data):
        """Test creación válida de ProjectAssignment."""
        assignment = ProjectAssignment(**valid_assignment_data)
        
        assert assignment.id == valid_assignment_data["id"]
        assert assignment.employee_id == valid_assignment_data["employee_id"]
        assert assignment.project_id == valid_assignment_data["project_id"]
        assert assignment.start_date == valid_assignment_data["start_date"]
        assert assignment.created_at == valid_assignment_data["created_at"]
        assert assignment.updated_at == valid_assignment_data["updated_at"]

    def test_inheritance_from_base(self):
        """Test herencia de ProjectAssignmentBase."""
        assert issubclass(ProjectAssignment, ProjectAssignmentBase)
        
        assignment = ProjectAssignment(
            id=1,
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            created_at=datetime(2025, 1, 1, 10, 0, 0),
            updated_at=datetime(2025, 1, 1, 10, 0, 0)
        )
        assert isinstance(assignment, ProjectAssignmentBase)

    def test_required_additional_fields(self):
        """Test campos adicionales obligatorios."""
        # Test sin id
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignment(
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 1),
                created_at=datetime(2025, 1, 1, 10, 0, 0),
                updated_at=datetime(2025, 1, 1, 10, 0, 0)
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)
        
        # Test sin created_at
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignment(
                id=1,
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 1),
                updated_at=datetime(2025, 1, 1, 10, 0, 0)
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("created_at",) for error in errors)
        
        # Test sin updated_at
        with pytest.raises(ValidationError) as exc_info:
            ProjectAssignment(
                id=1,
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 1),
                created_at=datetime(2025, 1, 1, 10, 0, 0)
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("updated_at",) for error in errors)

    def test_all_validations_inherited(self):
        """Test que todas las validaciones se heredan correctamente."""
        # Test validación de fechas
        with pytest.raises(ValueError, match="La fecha de fin debe ser posterior a la fecha de inicio"):
            ProjectAssignment(
                id=1,
                employee_id=1,
                project_id=1,
                start_date=date(2025, 1, 10),
                end_date=date(2025, 1, 5),
                created_at=datetime(2025, 1, 1, 10, 0, 0),
                updated_at=datetime(2025, 1, 1, 10, 0, 0)
            )

    def test_serialization(self, valid_assignment_data):
        """Test serialización del schema."""
        assignment = ProjectAssignment(**valid_assignment_data)
        data = assignment.model_dump()
        
        assert data["id"] == valid_assignment_data["id"]
        assert data["employee_id"] == valid_assignment_data["employee_id"]
        assert data["project_id"] == valid_assignment_data["project_id"]
        assert data["start_date"] == valid_assignment_data["start_date"]
        assert data["created_at"] == valid_assignment_data["created_at"]
        assert data["updated_at"] == valid_assignment_data["updated_at"]


class TestAssignmentSchemasEdgeCases:
    """Tests de casos edge para schemas de Assignment."""

    def test_boundary_values_hours(self):
        """Test valores límite para horas."""
        # Test 0 horas (mínimo)
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            allocated_hours_per_day=Decimal("0")
        )
        assert assignment.allocated_hours_per_day == Decimal("0")
        
        # Test 24 horas (máximo)
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            allocated_hours_per_day=Decimal("24")
        )
        assert assignment.allocated_hours_per_day == Decimal("24")

    def test_boundary_values_percentage(self):
        """Test valores límite para porcentaje."""
        # Test 0% (mínimo)
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            percentage_allocation=Decimal("0")
        )
        assert assignment.percentage_allocation == Decimal("0")
        
        # Test 100% (máximo)
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            percentage_allocation=Decimal("100")
        )
        assert assignment.percentage_allocation == Decimal("100")

    def test_allocation_consistency_tolerance(self):
        """Test tolerancia en validación de consistencia."""
        # Test dentro de tolerancia (5%)
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            allocated_hours_per_day=Decimal("8"),
            percentage_allocation=Decimal("97")  # 3% de diferencia, dentro de tolerancia
        )
        assert assignment.allocated_hours_per_day == Decimal("8")
        assert assignment.percentage_allocation == Decimal("97")

    def test_decimal_precision(self):
        """Test precisión de decimales."""
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            allocated_hours_per_day=Decimal("7.5"),
            percentage_allocation=Decimal("93.75")
        )
        assert assignment.allocated_hours_per_day == Decimal("7.5")
        assert assignment.percentage_allocation == Decimal("93.75")

    def test_empty_strings_vs_none(self):
        """Test diferencia entre strings vacíos y None."""
        # String vacío para role_in_project
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            role_in_project=""
        )
        assert assignment.role_in_project == ""
        
        # String vacío para notes
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            notes=""
        )
        assert assignment.notes == ""

    def test_complex_scenarios(self):
        """Test escenarios complejos de asignación."""
        # Asignación a tiempo parcial con fechas específicas
        assignment = ProjectAssignmentBase(
            employee_id=1,
            project_id=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            allocated_hours_per_day=Decimal("4"),
            percentage_allocation=Decimal("50"),
            role_in_project="Senior Developer",
            is_active=True,
            notes="Asignación temporal para proyecto crítico"
        )
        
        assert assignment.employee_id == 1
        assert assignment.project_id == 1
        assert assignment.start_date == date(2025, 1, 1)
        assert assignment.end_date == date(2025, 6, 30)
        assert assignment.allocated_hours_per_day == Decimal("4")
        assert assignment.percentage_allocation == Decimal("50")
        assert assignment.role_in_project == "Senior Developer"
        assert assignment.is_active is True
        assert assignment.notes == "Asignación temporal para proyecto crítico"