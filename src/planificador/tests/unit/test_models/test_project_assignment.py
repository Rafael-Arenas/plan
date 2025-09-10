# src/planificador/tests/models/test_project_assignment.py

import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from planificador.models.project_assignment import ProjectAssignment
from planificador.models.employee import Employee
from planificador.models.project import Project


class TestProjectAssignmentModel:
    """Tests unitarios para el modelo ProjectAssignment."""

    async def test_create_project_assignment_success(
        self,
        test_session: AsyncSession,
        sample_project_assignment_data: dict
    ):
        """Test: Crear una asignación de proyecto exitosamente."""
        # Arrange & Act
        assignment = ProjectAssignment(**sample_project_assignment_data)
        test_session.add(assignment)
        await test_session.flush()
        await test_session.refresh(assignment)

        # Assert
        assert assignment.id is not None
        assert assignment.employee_id == sample_project_assignment_data["employee_id"]
        assert assignment.project_id == sample_project_assignment_data["project_id"]
        assert assignment.start_date == sample_project_assignment_data["start_date"]
        assert assignment.end_date == sample_project_assignment_data["end_date"]
        assert assignment.allocated_hours_per_day == sample_project_assignment_data["allocated_hours_per_day"]
        assert assignment.percentage_allocation == sample_project_assignment_data["percentage_allocation"]
        assert assignment.role_in_project == sample_project_assignment_data["role_in_project"]
        assert assignment.is_active == sample_project_assignment_data["is_active"]
        assert assignment.notes == sample_project_assignment_data["notes"]

    async def test_create_project_assignment_minimal_data(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test: Crear asignación con datos mínimos requeridos."""
        # Arrange & Act
        assignment = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 1, 1)
        )
        test_session.add(assignment)
        await test_session.flush()
        await test_session.refresh(assignment)

        # Assert
        assert assignment.id is not None
        assert assignment.employee_id == sample_employee.id
        assert assignment.project_id == sample_project.id
        assert assignment.start_date == date(2024, 1, 1)
        assert assignment.end_date is None
        assert assignment.allocated_hours_per_day is None
        assert assignment.percentage_allocation is None
        assert assignment.role_in_project is None
        assert assignment.is_active is True  # Valor por defecto
        assert assignment.notes is None

    async def test_create_project_assignment_missing_employee_id(
        self,
        test_session: AsyncSession,
        sample_project: Project
    ):
        """Test: Error al crear asignación sin employee_id."""
        # Arrange & Act & Assert
        with pytest.raises(IntegrityError):
            assignment = ProjectAssignment(
                project_id=sample_project.id,
                start_date=date(2024, 1, 1)
            )
            test_session.add(assignment)
            await test_session.flush()

    async def test_create_project_assignment_missing_project_id(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test: Error al crear asignación sin project_id."""
        # Arrange & Act & Assert
        with pytest.raises(IntegrityError):
            assignment = ProjectAssignment(
                employee_id=sample_employee.id,
                start_date=date(2024, 1, 1)
            )
            test_session.add(assignment)
            await test_session.flush()

    async def test_create_project_assignment_missing_start_date(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test: Error al crear asignación sin start_date."""
        # Arrange & Act & Assert
        with pytest.raises(IntegrityError):
            assignment = ProjectAssignment(
                employee_id=sample_employee.id,
                project_id=sample_project.id
            )
            test_session.add(assignment)
            await test_session.flush()

    def test_project_assignment_repr(
        self,
        sample_project_assignment: ProjectAssignment
    ):
        """Test: Representación string del modelo."""
        # Act
        repr_str = repr(sample_project_assignment)

        # Assert
        expected = f"<ProjectAssignment(employee_id={sample_project_assignment.employee_id}, project_id={sample_project_assignment.project_id})>"
        assert repr_str == expected

    async def test_project_assignment_relationships(
        self,
        sample_project_assignment: ProjectAssignment
    ):
        """Test: Relaciones del modelo con Employee y Project."""
        # Assert
        assert sample_project_assignment.employee is not None
        assert sample_project_assignment.project is not None
        assert sample_project_assignment.employee.id == sample_project_assignment.employee_id
        assert sample_project_assignment.project.id == sample_project_assignment.project_id


class TestProjectAssignmentProperties:
    """Tests para propiedades calculadas del modelo ProjectAssignment."""

    def test_duration_days_with_end_date(
        self,
        sample_project_assignment: ProjectAssignment
    ):
        """Test: Cálculo de duración en días con fecha de fin."""
        # Arrange
        assignment = sample_project_assignment
        assignment.start_date = date(2024, 1, 1)
        assignment.end_date = date(2024, 1, 10)

        # Act
        duration = assignment.duration_days

        # Assert
        assert duration == 10  # 10 días inclusive

    def test_duration_days_without_end_date(
        self,
        sample_project_assignment: ProjectAssignment
    ):
        """Test: Duración es None sin fecha de fin."""
        # Arrange
        assignment = sample_project_assignment
        assignment.start_date = date(2024, 1, 1)
        assignment.end_date = None

        # Act
        duration = assignment.duration_days

        # Assert
        assert duration is None

    def test_is_current_active_assignment(self):
        """Test: Asignación activa en fecha actual."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=10),
            is_active=True
        )

        # Act & Assert
        assert assignment.is_current is True

    def test_is_current_inactive_assignment(self):
        """Test: Asignación inactiva no es current."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=10),
            is_active=False
        )

        # Act & Assert
        assert assignment.is_current is False

    def test_is_current_future_assignment(self):
        """Test: Asignación futura no es current."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=20),
            is_active=True
        )

        # Act & Assert
        assert assignment.is_current is False

    def test_is_current_past_assignment(self):
        """Test: Asignación pasada no es current."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=20),
            end_date=today - timedelta(days=10),
            is_active=True
        )

        # Act & Assert
        assert assignment.is_current is False

    def test_is_future_assignment(self):
        """Test: Identificar asignación futura."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=20)
        )

        # Act & Assert
        assert assignment.is_future is True

    def test_is_not_future_assignment(self):
        """Test: Asignación actual no es futura."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=10)
        )

        # Act & Assert
        assert assignment.is_future is False

    def test_is_past_assignment(self):
        """Test: Identificar asignación pasada."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=20),
            end_date=today - timedelta(days=10)
        )

        # Act & Assert
        assert assignment.is_past is True

    def test_is_not_past_assignment_without_end_date(self):
        """Test: Asignación sin fecha de fin no es pasada."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=10),
            end_date=None
        )

        # Act & Assert
        assert assignment.is_past is False

    def test_is_indefinite_assignment(self):
        """Test: Identificar asignación indefinida."""
        # Arrange
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=date(2024, 1, 1),
            end_date=None
        )

        # Act & Assert
        assert assignment.is_indefinite is True

    def test_is_not_indefinite_assignment(self):
        """Test: Asignación con fecha de fin no es indefinida."""
        # Arrange
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )

        # Act & Assert
        assert assignment.is_indefinite is False

    @pytest.mark.parametrize("percentage,expected_category", [
        (Decimal('100.0'), "Tiempo Completo"),
        (Decimal('90.0'), "Tiempo Completo"),
        (Decimal('80.0'), "Alta Dedicación"),
        (Decimal('70.0'), "Alta Dedicación"),
        (Decimal('60.0'), "Media Dedicación"),
        (Decimal('50.0'), "Media Dedicación"),
        (Decimal('40.0'), "Baja Dedicación"),
        (Decimal('25.0'), "Baja Dedicación"),
        (Decimal('20.0'), "Mínima Dedicación"),
        (Decimal('10.0'), "Mínima Dedicación"),
        (None, "Sin Definir")
    ])
    def test_allocation_category(
        self,
        percentage: Decimal | None,
        expected_category: str
    ):
        """Test: Categorización del porcentaje de asignación."""
        # Arrange
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=date(2024, 1, 1),
            percentage_allocation=percentage
        )

        # Act & Assert
        assert assignment.allocation_category == expected_category

    @pytest.mark.parametrize("hours,expected_category", [
        (Decimal('8.0'), "Jornada Completa"),
        (Decimal('8.5'), "Jornada Completa"),
        (Decimal('7.0'), "Jornada Alta"),
        (Decimal('6.0'), "Jornada Alta"),
        (Decimal('5.0'), "Media Jornada"),
        (Decimal('4.0'), "Media Jornada"),
        (Decimal('3.0'), "Jornada Baja"),
        (Decimal('2.0'), "Jornada Baja"),
        (Decimal('1.0'), "Jornada Mínima"),
        (Decimal('0.5'), "Jornada Mínima"),
        (None, "Sin Definir")
    ])
    def test_workload_category(
        self,
        hours: Decimal | None,
        expected_category: str
    ):
        """Test: Categorización de las horas asignadas por día."""
        # Arrange
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=date(2024, 1, 1),
            allocated_hours_per_day=hours
        )

        # Act & Assert
        assert assignment.workload_category == expected_category

    @pytest.mark.parametrize("is_active,start_offset,end_offset,expected_status", [
        (False, -10, 10, "Inactiva"),
        (True, 10, 20, "Futura"),
        (True, -10, 10, "Activa"),
        (True, -20, -10, "Finalizada")
    ])
    def test_status_display(
        self,
        is_active: bool,
        start_offset: int,
        end_offset: int,
        expected_status: str
    ):
        """Test: Display del estado de la asignación."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today + timedelta(days=start_offset),
            end_date=today + timedelta(days=end_offset),
            is_active=is_active
        )

        # Act & Assert
        assert assignment.status_display == expected_status

    def test_assignment_summary_complete(
        self,
        sample_project_assignment: ProjectAssignment
    ):
        """Test: Resumen completo de asignación."""
        # Arrange
        assignment = sample_project_assignment
        assignment.role_in_project = "Desarrollador Senior"
        assignment.percentage_allocation = Decimal('100.0')
        assignment.allocated_hours_per_day = Decimal('8.0')

        # Act
        summary = assignment.assignment_summary

        # Assert
        assert "Rol: Desarrollador Senior" in summary
        assert "Dedicación: Tiempo Completo" in summary
        assert "Carga: Jornada Completa" in summary
        assert "Estado:" in summary
        assert "|" in summary  # Separador

    def test_assignment_summary_minimal(self):
        """Test: Resumen mínimo de asignación."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=10),
            is_active=True
        )

        # Act
        summary = assignment.assignment_summary

        # Assert
        assert "Estado: Activa" in summary
        assert "Rol:" not in summary
        assert "Dedicación:" not in summary
        assert "Carga:" not in summary


class TestProjectAssignmentMethods:
    """Tests para métodos de utilidad del modelo ProjectAssignment."""

    def test_days_until_start_future_assignment(self):
        """Test: Días hasta el inicio de asignación futura."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today + timedelta(days=10)
        )

        # Act
        days_until = assignment.days_until_start()

        # Assert
        assert days_until == 10

    def test_days_until_start_current_assignment(self):
        """Test: Días hasta el inicio de asignación actual (0)."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=5)
        )

        # Act
        days_until = assignment.days_until_start()

        # Assert
        assert days_until == 0

    def test_days_until_end_future_end(self):
        """Test: Días hasta el fin de asignación."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=15)
        )

        # Act
        days_until = assignment.days_until_end()

        # Assert
        assert days_until == 15

    def test_days_until_end_no_end_date(self):
        """Test: Días hasta el fin sin fecha de fin (None)."""
        # Arrange
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=date(2024, 1, 1),
            end_date=None
        )

        # Act
        days_until = assignment.days_until_end()

        # Assert
        assert days_until is None

    def test_days_until_end_past_end(self):
        """Test: Días hasta el fin de asignación pasada (0)."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=20),
            end_date=today - timedelta(days=5)
        )

        # Act
        days_until = assignment.days_until_end()

        # Assert
        assert days_until == 0

    def test_progress_percentage_no_end_date(self):
        """Test: Progreso sin fecha de fin (None)."""
        # Arrange
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=date(2024, 1, 1),
            end_date=None
        )

        # Act
        progress = assignment.progress_percentage()

        # Assert
        assert progress is None

    def test_progress_percentage_before_start(self):
        """Test: Progreso antes del inicio (0%)."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=20)
        )

        # Act
        progress = assignment.progress_percentage()

        # Assert
        assert progress == 0.0

    def test_progress_percentage_after_end(self):
        """Test: Progreso después del fin (100%)."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=20),
            end_date=today - timedelta(days=10)
        )

        # Act
        progress = assignment.progress_percentage()

        # Assert
        assert progress == 100.0

    def test_progress_percentage_mid_assignment(self):
        """Test: Progreso en medio de asignación (50%)."""
        # Arrange
        today = date.today()
        assignment = ProjectAssignment(
            employee_id=1,
            project_id=1,
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=10)
        )

        # Act
        progress = assignment.progress_percentage()

        # Assert
        assert progress == 50.0

    def test_overlaps_with_overlapping_assignments(
        self,
        overlapping_assignments: list[ProjectAssignment]
    ):
        """Test: Detectar superposición entre asignaciones."""
        # Arrange
        assignment1, assignment2 = overlapping_assignments

        # Act & Assert
        assert assignment1.overlaps_with(assignment2) is True
        assert assignment2.overlaps_with(assignment1) is True

    def test_overlaps_with_non_overlapping_assignments(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test: No detectar superposición en asignaciones separadas."""
        # Arrange
        assignment1 = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            is_active=True
        )
        
        assignment2 = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 4, 1),
            end_date=date(2024, 6, 30),
            is_active=True
        )

        # Act & Assert
        assert assignment1.overlaps_with(assignment2) is False
        assert assignment2.overlaps_with(assignment1) is False

    def test_overlaps_with_inactive_assignment(
        self,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test: No hay superposición con asignaciones inactivas."""
        # Arrange
        assignment1 = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_active=True
        )
        
        assignment2 = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 3, 1),
            end_date=date(2024, 9, 30),
            is_active=False  # Inactiva
        )

        # Act & Assert
        assert assignment1.overlaps_with(assignment2) is False
        assert assignment2.overlaps_with(assignment1) is False

    def test_overlaps_with_indefinite_assignments(
        self,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test: Superposición con asignaciones indefinidas."""
        # Arrange
        assignment1 = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 1, 1),
            end_date=None,  # Indefinida
            is_active=True
        )
        
        assignment2 = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 6, 1),
            end_date=date(2024, 12, 31),
            is_active=True
        )

        # Act & Assert
        assert assignment1.overlaps_with(assignment2) is True
        assert assignment2.overlaps_with(assignment1) is True


class TestProjectAssignmentEdgeCases:
    """Tests para casos edge y validaciones especiales."""

    async def test_assignment_with_zero_allocation(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test: Asignación con 0% de dedicación."""
        # Arrange & Act
        assignment = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 1, 1),
            percentage_allocation=Decimal('0.0'),
            allocated_hours_per_day=Decimal('0.0')
        )
        test_session.add(assignment)
        await test_session.flush()
        await test_session.refresh(assignment)

        # Assert
        assert assignment.allocation_category == "Mínima Dedicación"
        assert assignment.workload_category == "Jornada Mínima"

    async def test_assignment_with_over_100_percent(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test: Asignación con más de 100% de dedicación."""
        # Arrange & Act
        assignment = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 1, 1),
            percentage_allocation=Decimal('150.0'),
            allocated_hours_per_day=Decimal('12.0')
        )
        test_session.add(assignment)
        await test_session.flush()
        await test_session.refresh(assignment)

        # Assert
        assert assignment.allocation_category == "Tiempo Completo"
        assert assignment.workload_category == "Jornada Completa"

    async def test_assignment_same_start_end_date(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test: Asignación de un solo día."""
        # Arrange & Act
        same_date = date(2024, 1, 15)
        assignment = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=same_date,
            end_date=same_date
        )
        test_session.add(assignment)
        await test_session.flush()
        await test_session.refresh(assignment)

        # Assert
        assert assignment.duration_days == 1

    async def test_assignment_end_before_start(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test: Asignación con fecha de fin antes del inicio."""
        # Arrange & Act
        assignment = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 10)  # Antes del inicio
        )
        test_session.add(assignment)
        await test_session.flush()
        await test_session.refresh(assignment)

        # Assert
        # El modelo permite esto, pero duration_days será negativo
        assert assignment.duration_days == -4  # (10 - 15) + 1

    async def test_assignment_with_very_long_role(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test: Asignación con rol muy largo."""
        # Arrange
        long_role = "A" * 100  # Máximo permitido por el campo String(100)
        
        # Act
        assignment = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 1, 1),
            role_in_project=long_role
        )
        test_session.add(assignment)
        await test_session.flush()
        await test_session.refresh(assignment)

        # Assert
        assert assignment.role_in_project == long_role
        assert len(assignment.role_in_project) == 100

    async def test_assignment_with_very_long_notes(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test: Asignación con notas muy largas."""
        # Arrange
        long_notes = "Esta es una nota muy larga. " * 100  # Campo Text permite mucho texto
        
        # Act
        assignment = ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 1, 1),
            notes=long_notes
        )
        test_session.add(assignment)
        await test_session.flush()
        await test_session.refresh(assignment)

        # Assert
        assert assignment.notes == long_notes
        assert len(assignment.notes) > 1000