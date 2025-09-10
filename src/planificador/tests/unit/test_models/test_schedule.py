"""Tests para el modelo Schedule.

Este módulo contiene tests comprehensivos para el modelo Schedule,
incluyendo validaciones, constraints, relaciones, métodos personalizados
y propiedades híbridas.
"""

import pytest
import pytest_asyncio
from datetime import date, time, datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from planificador.models.schedule import Schedule
from planificador.models.employee import Employee, EmployeeStatus
from planificador.models.project import Project, ProjectStatus, ProjectPriority
from planificador.models.team import Team
from planificador.models.client import Client
from planificador.models.status_code import StatusCode


class TestScheduleModel:
    """Tests para el modelo Schedule."""

    @pytest_asyncio.fixture
    async def sample_schedule_data(self):
        """Datos de ejemplo para crear un horario."""
        return {
            "date": date(2024, 1, 15),
            "start_time": time(9, 0),
            "end_time": time(17, 0),
            "description": "Desarrollo de funcionalidad principal",
            "location": "Oficina Central",
            "is_confirmed": True,
            "notes": "Reunión de seguimiento a las 14:00"
        }

    async def test_schedule_creation_minimal_fields(
        self, 
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test creación de horario con campos mínimos requeridos."""
        schedule = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15)
        )
        test_session.add(schedule)
        await test_session.flush()
        await test_session.refresh(schedule)

        assert schedule.id is not None
        assert schedule.employee_id == sample_employee.id
        assert schedule.date == date(2024, 1, 15)
        assert schedule.project_id is None
        assert schedule.team_id is None
        assert schedule.status_code_id is None
        assert schedule.start_time is None
        assert schedule.end_time is None
        assert schedule.description is None
        assert schedule.location is None
        assert schedule.is_confirmed is False  # Default
        assert schedule.notes is None
        assert schedule.created_at is not None
        assert schedule.updated_at is not None

    async def test_schedule_creation_with_all_fields(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project,
        sample_team: Team,
        sample_schedule_data: dict
    ):
        """Test creación de horario con todos los campos."""
        # Crear status_code para el test
        status_code = StatusCode(
            code="WORK",
            name="Trabajo Regular",
            description="Horario de trabajo regular",
            is_active=True
        )
        test_session.add(status_code)
        await test_session.flush()

        schedule = Schedule(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            team_id=sample_team.id,
            status_code_id=status_code.id,
            **sample_schedule_data
        )
        test_session.add(schedule)
        await test_session.flush()
        await test_session.refresh(schedule)

        assert schedule.id is not None
        assert schedule.employee_id == sample_employee.id
        assert schedule.project_id == sample_project.id
        assert schedule.team_id == sample_team.id
        assert schedule.status_code_id == status_code.id
        assert schedule.date == sample_schedule_data["date"]
        assert schedule.start_time == sample_schedule_data["start_time"]
        assert schedule.end_time == sample_schedule_data["end_time"]
        assert schedule.description == sample_schedule_data["description"]
        assert schedule.location == sample_schedule_data["location"]
        assert schedule.is_confirmed == sample_schedule_data["is_confirmed"]
        assert schedule.notes == sample_schedule_data["notes"]

    async def test_schedule_required_fields_validation(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test que campos requeridos son validados correctamente."""
        # Test horario válido con campos requeridos
        schedule = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15)
        )
        test_session.add(schedule)
        await test_session.flush()
        
        assert schedule.employee_id == sample_employee.id
        assert schedule.date == date(2024, 1, 15)
        assert schedule.id is not None

    async def test_schedule_foreign_key_constraints(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project,
        sample_team: Team
    ):
        """Test que las foreign keys funcionan correctamente."""
        schedule = Schedule(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            team_id=sample_team.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        test_session.add(schedule)
        await test_session.flush()
        await test_session.refresh(schedule)

        assert schedule.employee_id == sample_employee.id
        assert schedule.project_id == sample_project.id
        assert schedule.team_id == sample_team.id

    async def test_schedule_boolean_field_default(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test valores por defecto de campos booleanos."""
        schedule = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15)
        )
        test_session.add(schedule)
        await test_session.flush()
        await test_session.refresh(schedule)

        # is_confirmed debe tener valor por defecto False
        assert schedule.is_confirmed is False

    async def test_schedule_boolean_field_variations(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test diferentes formas de asignar campos booleanos."""
        # Horario confirmado explícito
        schedule_confirmed = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            is_confirmed=True
        )
        
        # Horario no confirmado explícito
        schedule_unconfirmed = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 16),
            is_confirmed=False
        )
        
        # Horario con valor por defecto
        schedule_default = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 17)
        )
        
        test_session.add_all([schedule_confirmed, schedule_unconfirmed, schedule_default])
        await test_session.flush()
        
        await test_session.refresh(schedule_confirmed)
        await test_session.refresh(schedule_unconfirmed)
        await test_session.refresh(schedule_default)
        
        assert schedule_confirmed.is_confirmed is True
        assert schedule_unconfirmed.is_confirmed is False
        assert schedule_default.is_confirmed is False


class TestScheduleHybridProperties:
    """Tests para las propiedades híbridas del modelo Schedule."""

    async def test_hours_worked_calculation(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test cálculo de horas trabajadas."""
        # Horario de 8 horas (9:00 - 17:00)
        schedule_8h = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        # Horario de 4.5 horas (9:00 - 13:30)
        schedule_4h30m = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 16),
            start_time=time(9, 0),
            end_time=time(13, 30)
        )
        
        # Horario sin horas definidas
        schedule_no_hours = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 17)
        )
        
        test_session.add_all([schedule_8h, schedule_4h30m, schedule_no_hours])
        await test_session.flush()
        
        assert schedule_8h.hours_worked == 8.0
        assert schedule_4h30m.hours_worked == 4.5
        assert schedule_no_hours.hours_worked == 0.0

    async def test_hours_worked_night_shift(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test cálculo de horas trabajadas para turno nocturno."""
        # Turno nocturno (22:00 - 06:00)
        schedule_night = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(22, 0),
            end_time=time(6, 0)
        )
        
        test_session.add(schedule_night)
        await test_session.flush()
        
        assert schedule_night.hours_worked == 8.0

    async def test_hours_worked_partial_hours(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test cálculo de horas trabajadas con minutos."""
        # Horario con minutos (9:15 - 17:45)
        schedule_with_minutes = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(9, 15),
            end_time=time(17, 45)
        )
        
        test_session.add(schedule_with_minutes)
        await test_session.flush()
        
        # 8 horas y 30 minutos = 8.5 horas
        assert schedule_with_minutes.hours_worked == 8.5


class TestScheduleProperties:
    """Tests para las propiedades del modelo Schedule."""

    async def test_duration_formatted_property(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test del formato de duración."""
        # 8 horas exactas
        schedule_8h = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        # 4 horas y 30 minutos
        schedule_4h30m = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 16),
            start_time=time(9, 0),
            end_time=time(13, 30)
        )
        
        # Sin horario
        schedule_no_time = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 17)
        )
        
        test_session.add_all([schedule_8h, schedule_4h30m, schedule_no_time])
        await test_session.flush()
        
        assert schedule_8h.duration_formatted == "8h"
        assert schedule_4h30m.duration_formatted == "4h 30m"
        assert schedule_no_time.duration_formatted == "0h"

    async def test_time_range_formatted_property(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test del formato de rango de tiempo."""
        # Con horarios definidos
        schedule_with_time = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(9, 30),
            end_time=time(17, 45)
        )
        
        # Sin horarios definidos
        schedule_no_time = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 16)
        )
        
        test_session.add_all([schedule_with_time, schedule_no_time])
        await test_session.flush()
        
        assert schedule_with_time.time_range_formatted == "09:30 - 17:45"
        assert schedule_no_time.time_range_formatted == "Sin horario definido"

    async def test_is_full_day_property(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test de la propiedad is_full_day."""
        # Evento de día completo (sin horarios)
        schedule_full_day = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            description="Evento de día completo"
        )
        
        # Evento con horarios específicos
        schedule_with_time = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 16),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        test_session.add_all([schedule_full_day, schedule_with_time])
        await test_session.flush()
        
        assert schedule_full_day.is_full_day is True
        assert schedule_with_time.is_full_day is False

    async def test_assignment_type_property(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project,
        sample_team: Team
    ):
        """Test de la propiedad assignment_type."""
        # Asignación a proyecto
        schedule_project = Schedule(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15)
        )
        
        # Asignación a equipo
        schedule_team = Schedule(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            date=date(2024, 1, 16)
        )
        
        # Asignación general
        schedule_general = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 17)
        )
        
        test_session.add_all([schedule_project, schedule_team, schedule_general])
        await test_session.flush()
        
        assert schedule_project.assignment_type == "Proyecto"
        assert schedule_team.assignment_type == "Equipo"
        assert schedule_general.assignment_type == "General"


class TestScheduleMethods:
    """Tests para los métodos del modelo Schedule."""

    async def test_is_overlapping_with_same_date(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test de superposición de horarios en la misma fecha."""
        # Horario 1: 9:00 - 13:00
        schedule1 = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(13, 0)
        )
        
        # Horario 2: 12:00 - 16:00 (se superpone)
        schedule2 = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(12, 0),
            end_time=time(16, 0)
        )
        
        # Horario 3: 14:00 - 18:00 (no se superpone)
        schedule3 = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(14, 0),
            end_time=time(18, 0)
        )
        
        test_session.add_all([schedule1, schedule2, schedule3])
        await test_session.flush()
        
        assert schedule1.is_overlapping_with(schedule2) is True
        assert schedule1.is_overlapping_with(schedule3) is False
        assert schedule2.is_overlapping_with(schedule3) is True

    async def test_is_overlapping_with_different_dates(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test de superposición de horarios en fechas diferentes."""
        schedule1 = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        schedule2 = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 16),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        test_session.add_all([schedule1, schedule2])
        await test_session.flush()
        
        # Fechas diferentes nunca se superponen
        assert schedule1.is_overlapping_with(schedule2) is False

    async def test_is_overlapping_with_full_day_events(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test de superposición con eventos de día completo."""
        # Evento de día completo
        schedule_full_day = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            description="Evento de día completo"
        )
        
        # Evento con horario específico
        schedule_with_time = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        test_session.add_all([schedule_full_day, schedule_with_time])
        await test_session.flush()
        
        # Eventos de día completo siempre se superponen si es la misma fecha
        assert schedule_full_day.is_overlapping_with(schedule_with_time) is True
        assert schedule_with_time.is_overlapping_with(schedule_full_day) is True

    async def test_is_overlapping_with_missing_times(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test de superposición con horarios incompletos."""
        # Horario con solo start_time
        schedule_start_only = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0)
        )
        
        # Horario completo
        schedule_complete = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(10, 0),
            end_time=time(16, 0)
        )
        
        test_session.add_all([schedule_start_only, schedule_complete])
        await test_session.flush()
        
        # Sin horarios completos no se puede determinar superposición
        assert schedule_start_only.is_overlapping_with(schedule_complete) is False


class TestScheduleRelationships:
    """Tests para las relaciones del modelo Schedule."""

    async def test_schedule_employee_relationship(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test de la relación Schedule-Employee."""
        schedule = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        test_session.add(schedule)
        await test_session.flush()
        
        # Cargar schedule con relación employee
        result = await test_session.execute(
            select(Schedule).options(selectinload(Schedule.employee)).where(Schedule.id == schedule.id)
        )
        schedule_with_employee = result.scalar_one()
        
        assert schedule_with_employee.employee is not None
        assert schedule_with_employee.employee.id == sample_employee.id
        assert schedule_with_employee.employee_id == sample_employee.id

    async def test_schedule_project_relationship(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test de la relación Schedule-Project."""
        schedule = Schedule(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        test_session.add(schedule)
        await test_session.flush()
        
        # Cargar schedule con relación project
        result = await test_session.execute(
            select(Schedule).options(selectinload(Schedule.project)).where(Schedule.id == schedule.id)
        )
        schedule_with_project = result.scalar_one()
        
        assert schedule_with_project.project is not None
        assert schedule_with_project.project.id == sample_project.id
        assert schedule_with_project.project_id == sample_project.id

    async def test_schedule_team_relationship(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test de la relación Schedule-Team."""
        schedule = Schedule(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        
        test_session.add(schedule)
        await test_session.flush()
        
        # Cargar schedule con relación team
        result = await test_session.execute(
            select(Schedule).options(selectinload(Schedule.team)).where(Schedule.id == schedule.id)
        )
        schedule_with_team = result.scalar_one()
        
        assert schedule_with_team.team is not None
        assert schedule_with_team.team.id == sample_team.id
        assert schedule_with_team.team_id == sample_team.id

    # Test de relación Employee.schedules eliminado - ahora centralizado en test_model_relationships.py
    # Ver TestEmployeeScheduleRelationship en test_model_relationships.py


class TestScheduleStringRepresentation:
    """Tests para la representación string del modelo Schedule."""

    async def test_schedule_repr(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test de la representación __repr__ del Schedule."""
        schedule = Schedule(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15)
        )
        
        test_session.add(schedule)
        await test_session.flush()
        
        expected_repr = f"<Schedule(employee_id={sample_employee.id}, date={date(2024, 1, 15)}, project_id={sample_project.id})>"
        assert repr(schedule) == expected_repr

    async def test_schedule_repr_without_project(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test de la representación __repr__ del Schedule sin proyecto."""
        schedule = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15)
        )
        
        test_session.add(schedule)
        await test_session.flush()
        
        expected_repr = f"<Schedule(employee_id={sample_employee.id}, date={date(2024, 1, 15)}, project_id=None)>"
        assert repr(schedule) == expected_repr


class TestScheduleEdgeCases:
    """Tests para casos edge del modelo Schedule."""

    async def test_schedule_with_same_start_end_time(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test horario con misma hora de inicio y fin."""
        schedule = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(9, 0)
        )
        
        test_session.add(schedule)
        await test_session.flush()
        
        assert schedule.hours_worked == 0.0
        assert schedule.duration_formatted == "0h"
        assert schedule.time_range_formatted == "09:00 - 09:00"

    async def test_schedule_with_extreme_times(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test horario con horarios extremos."""
        # Horario de 23:59 a 00:01 (turno nocturno de 2 minutos)
        schedule = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(23, 59),
            end_time=time(0, 1)
        )
        
        test_session.add(schedule)
        await test_session.flush()
        
        # 2 minutos = 2/60 horas = 0.033... horas
        expected_hours = 2.0 / 60.0
        assert abs(schedule.hours_worked - expected_hours) < 0.001

    async def test_schedule_multiple_assignments(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project,
        sample_team: Team
    ):
        """Test horario con múltiples asignaciones (proyecto y equipo)."""
        schedule = Schedule(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            team_id=sample_team.id,
            date=date(2024, 1, 15)
        )
        
        test_session.add(schedule)
        await test_session.flush()
        
        # Cuando hay proyecto, assignment_type debe ser "Proyecto"
        assert schedule.assignment_type == "Proyecto"
        assert schedule.project_id == sample_project.id
        assert schedule.team_id == sample_team.id