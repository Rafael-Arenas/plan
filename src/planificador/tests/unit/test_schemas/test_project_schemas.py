"""Tests para schemas de Project.

Este módulo contiene tests unitarios para validar los schemas
relacionados con proyectos: ProjectBase, ProjectCreate, ProjectUpdate, Project y ProjectWithAssignments.

Author: Assistant
Date: 2024-01-21
"""

import pytest
from datetime import datetime, date
from typing import Dict, Any
from pydantic import ValidationError

from planificador.schemas.project.project import (
    ProjectBase,
    ProjectCreate,
    ProjectUpdate,
    Project,
    ProjectWithAssignments
)
from planificador.models.project import ProjectStatus, ProjectPriority


class TestProjectBase:
    """Tests para el schema ProjectBase."""

    def test_valid_project_base(self, valid_project_data: Dict[str, Any]):
        """Test: ProjectBase con datos válidos.
        
        Args:
            valid_project_data: Fixture con datos válidos
        """
        project = ProjectBase(**valid_project_data)
        
        assert project.name == valid_project_data["name"]
        assert project.reference == valid_project_data["reference"]
        assert project.trigram == valid_project_data["trigram"]
        assert project.details == valid_project_data["details"]
        assert project.status == ProjectStatus.PLANNED
        assert project.priority == ProjectPriority.MEDIUM
        assert project.start_date == date(2024, 2, 1)
        assert project.end_date == date(2024, 12, 31)
        assert project.client_id == valid_project_data["client_id"]

    def test_project_base_with_minimal_data(self):
        """Test: ProjectBase con datos mínimos requeridos."""
        minimal_data = {
            "name": "Proyecto Mínimo",
            "reference": "PM-001",
            "trigram": "PMN",
            "client_id": 1
        }
        
        project = ProjectBase(**minimal_data)
        
        assert project.name == "Proyecto Mínimo"
        assert project.reference == "PM-001"
        assert project.trigram == "PMN"
        assert project.client_id == 1
        # Verificar valores por defecto
        assert project.details is None
        assert project.status == ProjectStatus.PLANNED
        assert project.priority == ProjectPriority.MEDIUM
        assert project.start_date is None
        assert project.end_date is None

    def test_project_base_invalid_status_fails(self):
        """Test: ProjectBase falla con status inválido."""
        invalid_data = {
            "name": "Proyecto Test",
            "reference": "PT-001",
            "trigram": "PTT",
            "client_id": 1,
            "status": "invalid_status"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ProjectBase(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("status",)
        assert "Input should be" in errors[0]["msg"]

    def test_project_base_invalid_priority_fails(self):
        """Test: ProjectBase falla con prioridad inválida."""
        invalid_data = {
            "name": "Proyecto Test",
            "reference": "PT-001",
            "trigram": "PTT",
            "client_id": 1,
            "priority": "invalid_priority"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ProjectBase(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("priority",)
        assert "Input should be" in errors[0]["msg"]

    def test_project_base_date_validation_fails(self):
        """Test: ProjectBase falla con fechas inválidas."""
        # Test fecha de inicio muy antigua
        invalid_data = {
            "name": "Proyecto Test",
            "reference": "PT-001",
            "trigram": "PTT",
            "client_id": 1,
            "start_date": date(2010, 1, 1)  # Más de 5 años atrás
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ProjectBase(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) >= 1
        assert any("fecha de inicio" in str(error["ctx"]["error"]) for error in errors if "ctx" in error)

    def test_project_base_future_date_validation_fails(self):
        """Test: ProjectBase falla con fechas muy futuras."""
        # Test fecha de fin muy futura
        invalid_data = {
            "name": "Proyecto Test",
            "reference": "PT-001",
            "trigram": "PTT",
            "client_id": 1,
            "end_date": date(2050, 1, 1)  # Más de 15 años en el futuro
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ProjectBase(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) >= 1
        assert any("fecha de fin" in str(error["ctx"]["error"]) for error in errors if "ctx" in error)


class TestProjectCreate:
    """Tests para el schema ProjectCreate."""

    def test_valid_project_create(self, valid_project_create_data: Dict[str, Any]):
        """Test: ProjectCreate con datos válidos.
        
        Args:
            valid_project_create_data: Fixture con datos válidos
        """
        project = ProjectCreate(**valid_project_create_data)
        
        assert project.name == valid_project_create_data["name"]
        assert project.reference == valid_project_create_data["reference"]
        assert project.trigram == valid_project_create_data["trigram"]
        assert project.client_id == valid_project_create_data["client_id"]

    def test_project_create_inheritance(self, valid_project_create_data: Dict[str, Any]):
        """Test: ProjectCreate hereda correctamente de ProjectBase.
        
        Args:
            valid_project_create_data: Fixture con datos válidos
        """
        project = ProjectCreate(**valid_project_create_data)
        
        # Verificar que es instancia de ProjectBase
        assert isinstance(project, ProjectBase)
        
        # Verificar que tiene todos los campos de ProjectBase
        assert hasattr(project, 'name')
        assert hasattr(project, 'reference')
        assert hasattr(project, 'trigram')
        assert hasattr(project, 'details')
        assert hasattr(project, 'status')
        assert hasattr(project, 'priority')
        assert hasattr(project, 'start_date')
        assert hasattr(project, 'end_date')
        assert hasattr(project, 'client_id')


class TestProjectUpdate:
    """Tests para el schema ProjectUpdate."""

    def test_valid_project_update(self, valid_project_update_data: Dict[str, Any]):
        """Test: ProjectUpdate con datos válidos.
        
        Args:
            valid_project_update_data: Fixture con datos válidos
        """
        project = ProjectUpdate(**valid_project_update_data)
        
        assert project.name == valid_project_update_data["name"]
        assert project.details == valid_project_update_data["details"]
        assert project.status == ProjectStatus.IN_PROGRESS
        assert project.priority == ProjectPriority.HIGH

    def test_project_update_all_optional(self):
        """Test: ProjectUpdate con todos los campos opcionales."""
        # Crear ProjectUpdate sin ningún campo
        project = ProjectUpdate()
        
        # Verificar que todos los campos son None
        assert project.name is None
        assert project.reference is None
        assert project.trigram is None
        assert project.details is None
        assert project.status is None
        assert project.priority is None
        assert project.start_date is None
        assert project.end_date is None
        assert project.client_id is None

    def test_project_update_partial_data(self):
        """Test: ProjectUpdate con datos parciales."""
        partial_data = {
            "name": "Proyecto Actualizado",
            "status": "completed"
        }
        
        project = ProjectUpdate(**partial_data)
        
        assert project.name == "Proyecto Actualizado"
        assert project.status == ProjectStatus.COMPLETED
        # Verificar que otros campos son None
        assert project.reference is None
        assert project.details is None
        assert project.priority is None


class TestProject:
    """Tests para el schema Project."""

    def test_valid_project(self, valid_project_data: Dict[str, Any]):
        """Test: Project con datos válidos.
        
        Args:
            valid_project_data: Fixture con datos válidos
        """
        # Agregar campos requeridos para Project
        project_data = valid_project_data.copy()
        project_data["id"] = 1
        project_data["created_at"] = datetime(2024, 1, 15, 10, 0, 0)
        project_data["updated_at"] = datetime(2024, 1, 15, 11, 0, 0)
        project_data["client"] = {
            "id": 1,
            "name": "Cliente Test",
            "code": "CT-001",
            "contact_person": "Juan Pérez",
            "email": "juan@cliente.com",
            "is_active": True,
            "created_at": datetime(2024, 1, 10, 9, 0, 0),
            "updated_at": datetime(2024, 1, 10, 9, 0, 0)
        }
        
        project = Project(**project_data)
        
        assert project.id == 1
        assert project.name == valid_project_data["name"]
        assert project.created_at == datetime(2024, 1, 15, 10, 0, 0)
        assert project.updated_at == datetime(2024, 1, 15, 11, 0, 0)
        assert project.client is not None
        assert project.client.name == "Cliente Test"

    def test_project_inheritance(self, valid_project_data: Dict[str, Any]):
        """Test: Project hereda correctamente de ProjectBase.
        
        Args:
            valid_project_data: Fixture con datos válidos
        """
        project_data = valid_project_data.copy()
        project_data["id"] = 1
        project_data["created_at"] = datetime(2024, 1, 15, 10, 0, 0)
        project_data["updated_at"] = datetime(2024, 1, 15, 11, 0, 0)
        project_data["client"] = {
            "id": 1,
            "name": "Cliente Test",
            "code": "CT-001",
            "contact_person": "Juan Pérez",
            "email": "juan@cliente.com",
            "is_active": True,
            "created_at": datetime(2024, 1, 10, 9, 0, 0),
            "updated_at": datetime(2024, 1, 10, 9, 0, 0)
        }
        
        project = Project(**project_data)
        
        # Verificar que es instancia de ProjectBase
        assert isinstance(project, ProjectBase)
        
        # Verificar que tiene campos adicionales de Project
        assert hasattr(project, 'id')
        assert hasattr(project, 'created_at')
        assert hasattr(project, 'updated_at')
        assert hasattr(project, 'client')


class TestProjectWithAssignments:
    """Tests para el schema ProjectWithAssignments."""

    def test_valid_project_with_empty_assignments(self, valid_project_with_assignments_data: Dict[str, Any]):
        """Test: ProjectWithAssignments con lista vacía de asignaciones.
        
        Args:
            valid_project_with_assignments_data: Fixture con datos válidos y asignaciones vacías
        """
        project = ProjectWithAssignments(**valid_project_with_assignments_data)
        
        assert project.name == valid_project_with_assignments_data["name"]
        assert project.id == valid_project_with_assignments_data["id"]
        
        # Verificar relaciones
        assert project.assignments == []
        assert isinstance(project.assignments, list)
        assert project.client is not None
        assert project.client.name == "Cliente Test"

    def test_project_with_assignments_inheritance(self, valid_project_with_assignments_data: Dict[str, Any]):
        """Test: ProjectWithAssignments hereda correctamente de Project.
        
        Args:
            valid_project_with_assignments_data: Fixture con datos válidos
        """
        project = ProjectWithAssignments(**valid_project_with_assignments_data)
        
        # Verificar que es instancia de Project
        assert isinstance(project, Project)
        
        # Verificar que tiene campos adicionales
        assert hasattr(project, 'assignments')
        assert hasattr(project, 'client')

    def test_project_with_assignments_default_empty_list(self, valid_project_data: Dict[str, Any]):
        """Test: ProjectWithAssignments con lista por defecto vacía.
        
        Args:
            valid_project_data: Fixture con datos válidos sin campo assignments
        """
        # Agregar campos requeridos pero no incluir 'assignments'
        project_data = valid_project_data.copy()
        project_data["id"] = 1
        project_data["created_at"] = datetime(2024, 1, 15, 10, 0, 0)
        project_data["updated_at"] = datetime(2024, 1, 15, 11, 0, 0)
        project_data["client"] = {
            "id": 1,
            "name": "Cliente Test",
            "code": "CT-001",
            "contact_person": "Juan Pérez",
            "email": "juan@cliente.com",
            "is_active": True,
            "created_at": datetime(2024, 1, 10, 9, 0, 0),
            "updated_at": datetime(2024, 1, 10, 9, 0, 0)
        }
        
        project = ProjectWithAssignments(**project_data)
        
        # Verificar que assignments es una lista vacía por defecto
        assert project.assignments == []
        assert isinstance(project.assignments, list)


class TestProjectStatusValidation:
    """Tests para validación del enum ProjectStatus."""

    def test_valid_status_values(self):
        """Test: Valores válidos de ProjectStatus."""
        valid_statuses = ["planned", "in_progress", "on_hold", "completed", "cancelled"]
        
        for status in valid_statuses:
            project_data = {
                "name": "Test Project",
                "reference": "TP-001",
                "trigram": "TPS",
                "status": status,
                "client_id": 1
            }
            
            project = ProjectBase(**project_data)
            assert project.status.value == status

    def test_invalid_status_values(self):
        """Test: Valores inválidos de ProjectStatus."""
        invalid_statuses = ["invalid", "unknown", "pending", "active"]
        
        for status in invalid_statuses:
            project_data = {
                "name": "Test Project",
                "reference": "TP-001",
                "trigram": "TPS",
                "status": status,
                "client_id": 1
            }
            
            with pytest.raises(ValidationError) as exc_info:
                ProjectBase(**project_data)
            
            errors = exc_info.value.errors()
            assert len(errors) == 1
            assert errors[0]["loc"] == ("status",)

    def test_status_enum_attributes(self):
        """Test: Atributos correctos del enum ProjectStatus."""
        assert ProjectStatus.PLANNED.value == "planned"
        assert ProjectStatus.IN_PROGRESS.value == "in_progress"
        assert ProjectStatus.ON_HOLD.value == "on_hold"
        assert ProjectStatus.COMPLETED.value == "completed"
        assert ProjectStatus.CANCELLED.value == "cancelled"

    def test_status_enum_membership(self):
        """Test: Todos los estados son miembros válidos del enum."""
        expected_statuses = {"planned", "in_progress", "on_hold", "completed", "cancelled"}
        actual_statuses = {status.value for status in ProjectStatus}
        assert actual_statuses == expected_statuses

    def test_status_case_sensitivity(self):
        """Test: ProjectStatus es sensible a mayúsculas/minúsculas."""
        project_data = {
            "name": "Test Project",
            "reference": "TP-001",
            "trigram": "TPS",
            "status": "PLANNED",  # Mayúsculas - inválido
            "client_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ProjectBase(**project_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("status",)


class TestProjectPriorityValidation:
    """Tests para validación del enum ProjectPriority."""

    def test_valid_priority_values(self):
        """Test: Valores válidos de ProjectPriority."""
        valid_priorities = ["low", "medium", "high", "critical"]
        
        for priority in valid_priorities:
            project_data = {
                "name": "Test Project",
                "reference": "TP-001",
                "trigram": "TPS",
                "priority": priority,
                "client_id": 1
            }
            
            project = ProjectBase(**project_data)
            assert project.priority.value == priority

    def test_invalid_priority_values(self):
        """Test: Valores inválidos de ProjectPriority."""
        invalid_priorities = ["urgent", "super_high", "normal", ""]
        
        for priority in invalid_priorities:
            project_data = {
                "name": "Test Project",
                "reference": "TP-001",
                "trigram": "TPS",
                "priority": priority,
                "client_id": 1
            }
            
            with pytest.raises(ValidationError) as exc_info:
                ProjectBase(**project_data)
            
            errors = exc_info.value.errors()
            assert len(errors) >= 1
            priority_error = next((error for error in errors if error["loc"] == ("priority",)), None)
            assert priority_error is not None
            assert "Input should be" in priority_error["msg"]

    def test_priority_enum_attributes(self):
        """Test: Atributos correctos del enum ProjectPriority."""
        assert ProjectPriority.LOW.value == "low"
        assert ProjectPriority.MEDIUM.value == "medium"
        assert ProjectPriority.HIGH.value == "high"
        assert ProjectPriority.CRITICAL.value == "critical"

    def test_priority_enum_membership(self):
        """Test: Todas las prioridades son miembros válidos del enum."""
        expected_priorities = {"low", "medium", "high", "critical"}
        actual_priorities = {priority.value for priority in ProjectPriority}
        assert actual_priorities == expected_priorities

    def test_priority_case_sensitivity(self):
        """Test: ProjectPriority es sensible a mayúsculas/minúsculas."""
        project_data = {
            "name": "Test Project",
            "reference": "TP-001",
            "trigram": "TPS",
            "priority": "HIGH",  # Mayúsculas - inválido
            "client_id": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ProjectBase(**project_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("priority",)


class TestProjectSpecificFieldValidation:
    """Tests para validación de campos específicos de Project."""

    def test_reference_format_validation(self):
        """Test: Validación del formato de reference."""
        valid_references = ["PRJ-001", "SGT-2024-001", "ABC-123", "X-1"]
        
        for reference in valid_references:
            project_data = {
                "name": "Test Project",
                "reference": reference,
                "trigram": "TPS",
                "client_id": 1
            }
            
            project = ProjectBase(**project_data)
            assert project.reference == reference

    def test_date_order_validation(self):
        """Test: Validación del orden de fechas."""
        # Test fecha de fin anterior a fecha de inicio
        invalid_data = {
            "name": "Proyecto Test",
            "reference": "PT-001",
            "trigram": "PTT",
            "client_id": 1,
            "start_date": date(2024, 12, 31),
            "end_date": date(2024, 1, 1)  # Anterior a start_date
        }
        
        project = ProjectBase(**invalid_data)
        
        # La validación de fechas se hace en validate_project_dates
        with pytest.raises(ValueError) as exc_info:
            project.validate_project_dates()
        
        assert "fecha de inicio debe ser anterior" in str(exc_info.value)

    def test_project_duration_validation(self):
        """Test: Validación de duración máxima del proyecto."""
        # Test duración mayor a 5 años
        invalid_data = {
            "name": "Proyecto Test",
            "reference": "PT-001",
            "trigram": "PTT",
            "client_id": 1,
            "start_date": date(2024, 1, 1),
            "end_date": date(2030, 1, 1)  # Más de 5 años
        }
        
        project = ProjectBase(**invalid_data)
        
        # La validación de duración se hace en validate_project_dates
        with pytest.raises(ValueError) as exc_info:
            project.validate_project_dates()
        
        assert "duración del proyecto no puede exceder" in str(exc_info.value)

    def test_date_validation(self):
        """Test: Validación de fechas."""
        # Fechas válidas
        project_data = {
            "name": "Test Project",
            "reference": "TP-001",
            "trigram": "TPS",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "client_id": 1
        }
        
        project = ProjectBase(**project_data)
        assert project.start_date == date(2024, 1, 1)
        assert project.end_date == date(2024, 12, 31)
        
        # Formato de fecha inválido
        project_data["start_date"] = "invalid-date"
        
        with pytest.raises(ValidationError) as exc_info:
            ProjectBase(**project_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("start_date",)

    def test_optional_fields_defaults(self):
        """Test: Campos opcionales tienen valores por defecto correctos."""
        minimal_data = {
            "name": "Proyecto Mínimo",
            "reference": "PM-001",
            "trigram": "PMI",
            "client_id": 1
        }
        
        project = ProjectBase(**minimal_data)
        
        # Verificar valores por defecto
        assert project.details is None
        assert project.status == ProjectStatus.PLANNED
        assert project.priority == ProjectPriority.MEDIUM
        assert project.start_date is None
        assert project.end_date is None

    def test_reference_uniqueness_assumption(self):
        """Test: Asunción de unicidad de reference (manejada por BD)."""
        # El schema acepta references duplicadas
        # La unicidad se maneja a nivel de base de datos
        project_data_1 = {
            "name": "Project 1",
            "reference": "DUPLICATE-REF",
            "trigram": "PR1",
            "client_id": 1
        }
        
        project_data_2 = {
            "name": "Project 2",
            "reference": "DUPLICATE-REF",  # Mismo reference
            "trigram": "PR2",
            "client_id": 2
        }
        
        # Ambos proyectos se crean sin error en el schema
        project_1 = ProjectBase(**project_data_1)
        project_2 = ProjectBase(**project_data_2)
        
        assert project_1.reference == project_2.reference
        assert project_1.name != project_2.name