"""Tests para el modelo Vacation.

Este módulo contiene tests comprehensivos para el modelo Vacation,
incluyendo validaciones, constraints, enums, relaciones y métodos personalizados.
"""

import pytest
import pytest_asyncio
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from planificador.models.vacation import Vacation, VacationType, VacationStatus
from planificador.models.employee import Employee, EmployeeStatus


class TestVacationEnums:
    """Tests para los enums del modelo Vacation."""

    def test_vacation_type_enum_values(self):
        """Test que verifica los valores del enum VacationType."""
        assert VacationType.ANNUAL.value == "annual"
        assert VacationType.SICK.value == "sick"
        assert VacationType.PERSONAL.value == "personal"
        assert VacationType.MATERNITY.value == "maternity"
        assert VacationType.PATERNITY.value == "paternity"
        assert VacationType.TRAINING.value == "training"
        assert VacationType.OTHER.value == "other"

    def test_vacation_type_enum_membership(self):
        """Test que verifica la membresía del enum VacationType."""
        assert VacationType.ANNUAL in VacationType
        assert VacationType.SICK in VacationType
        assert VacationType.PERSONAL in VacationType
        assert VacationType.MATERNITY in VacationType
        assert VacationType.PATERNITY in VacationType
        assert VacationType.TRAINING in VacationType
        assert VacationType.OTHER in VacationType

    def test_vacation_status_enum_values(self):
        """Test que verifica los valores del enum VacationStatus."""
        assert VacationStatus.PENDING.value == "pending"
        assert VacationStatus.APPROVED.value == "approved"
        assert VacationStatus.REJECTED.value == "rejected"
        assert VacationStatus.CANCELLED.value == "cancelled"

    def test_vacation_status_enum_membership(self):
        """Test que verifica la membresía del enum VacationStatus."""
        assert VacationStatus.PENDING in VacationStatus
        assert VacationStatus.APPROVED in VacationStatus
        assert VacationStatus.REJECTED in VacationStatus
        assert VacationStatus.CANCELLED in VacationStatus


class TestVacationModel:
    """Tests para el modelo Vacation."""

    @pytest_asyncio.fixture
    async def sample_vacation_data(self, sample_employee: Employee):
        """Datos de ejemplo para crear una vacación."""
        return {
            "employee_id": sample_employee.id,
            "start_date": date(2024, 7, 1),
            "end_date": date(2024, 7, 15),
            "vacation_type": VacationType.ANNUAL,
            "status": VacationStatus.PENDING,
            "requested_date": date(2024, 6, 1),
            "reason": "Vacaciones de verano",
            "notes": "Vacaciones planificadas con anticipación",
            "total_days": 15,
            "business_days": 11
        }

    @pytest_asyncio.fixture
    async def vacation_instance(self, test_session: AsyncSession, sample_employee: Employee):
        """Fixture que crea una vacación en la base de datos."""
        vacation_data = {
            "employee_id": sample_employee.id,
            "start_date": date(2024, 7, 1),
            "end_date": date(2024, 7, 15),
            "vacation_type": VacationType.ANNUAL,
            "status": VacationStatus.PENDING,
            "requested_date": date(2024, 6, 1),
            "reason": "Vacaciones de verano",
            "notes": "Vacaciones planificadas con anticipación",
            "total_days": 15,
            "business_days": 11
        }
        vacation = Vacation(**vacation_data)
        test_session.add(vacation)
        await test_session.flush()
        await test_session.refresh(vacation)
        return vacation

    # Tests de creación de instancias
    async def test_vacation_creation_with_all_fields(self, sample_vacation_data):
        """Test creación de vacación con todos los campos."""
        vacation = Vacation(**sample_vacation_data)
        
        assert vacation.employee_id == sample_vacation_data["employee_id"]
        assert vacation.start_date == date(2024, 7, 1)
        assert vacation.end_date == date(2024, 7, 15)
        assert vacation.vacation_type == VacationType.ANNUAL
        assert vacation.status == VacationStatus.PENDING
        assert vacation.requested_date == date(2024, 6, 1)
        assert vacation.reason == "Vacaciones de verano"
        assert vacation.notes == "Vacaciones planificadas con anticipación"
        assert vacation.total_days == 15
        assert vacation.business_days == 11

    async def test_vacation_creation_minimal_fields(self, test_session: AsyncSession, sample_employee: Employee):
        """Test creación de vacación solo con campos obligatorios."""
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            vacation_type=VacationType.PERSONAL,
            requested_date=date(2024, 7, 15),
            total_days=5,
            business_days=5
        )
        
        test_session.add(vacation)
        await test_session.flush()
        await test_session.refresh(vacation)
        
        assert vacation.employee_id == sample_employee.id
        assert vacation.start_date == date(2024, 8, 1)
        assert vacation.end_date == date(2024, 8, 5)
        assert vacation.vacation_type == VacationType.PERSONAL
        assert vacation.status == VacationStatus.PENDING  # Valor por defecto
        assert vacation.requested_date == date(2024, 7, 15)
        assert vacation.reason is None
        assert vacation.notes is None
        assert vacation.approved_date is None
        assert vacation.approved_by is None
        assert vacation.total_days == 5
        assert vacation.business_days == 5

    # Tests de validaciones y constraints
    async def test_vacation_requires_employee_id(self, test_session: AsyncSession):
        """Test que employee_id es obligatorio."""
        vacation = Vacation(
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            vacation_type=VacationType.PERSONAL,
            requested_date=date(2024, 7, 15),
            total_days=5,
            business_days=5
        )
        
        test_session.add(vacation)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_vacation_requires_start_date(self, test_session: AsyncSession, sample_employee: Employee):
        """Test que start_date es obligatorio."""
        vacation = Vacation(
            employee_id=sample_employee.id,
            end_date=date(2024, 8, 5),
            vacation_type=VacationType.PERSONAL,
            requested_date=date(2024, 7, 15),
            total_days=5,
            business_days=5
        )
        
        test_session.add(vacation)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_vacation_requires_end_date(self, test_session: AsyncSession, sample_employee: Employee):
        """Test que end_date es obligatorio."""
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            vacation_type=VacationType.PERSONAL,
            requested_date=date(2024, 7, 15),
            total_days=5,
            business_days=5
        )
        
        test_session.add(vacation)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_vacation_requires_vacation_type(self, test_session: AsyncSession, sample_employee: Employee):
        """Test que vacation_type es obligatorio."""
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            requested_date=date(2024, 7, 15),
            total_days=5,
            business_days=5
        )
        
        test_session.add(vacation)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_vacation_requires_requested_date(self, test_session: AsyncSession, sample_employee: Employee):
        """Test que requested_date es obligatorio."""
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            vacation_type=VacationType.PERSONAL,
            total_days=5,
            business_days=5
        )
        
        test_session.add(vacation)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_vacation_requires_total_days(self, test_session: AsyncSession, sample_employee: Employee):
        """Test que total_days es obligatorio."""
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            vacation_type=VacationType.PERSONAL,
            requested_date=date(2024, 7, 15),
            business_days=5
        )
        
        test_session.add(vacation)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_vacation_requires_business_days(self, test_session: AsyncSession, sample_employee: Employee):
        """Test que business_days es obligatorio."""
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            vacation_type=VacationType.PERSONAL,
            requested_date=date(2024, 7, 15),
            total_days=5
        )
        
        test_session.add(vacation)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    # Tests de propiedades híbridas y calculadas
    async def test_duration_days_property(self, vacation_instance: Vacation):
        """Test de la propiedad duration_days."""
        # Vacación del 1 al 15 de julio = 15 días
        assert vacation_instance.duration_days == 15

    async def test_duration_days_single_day(self, test_session: AsyncSession, sample_employee: Employee):
        """Test duration_days para vacación de un solo día."""
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 1),
            vacation_type=VacationType.SICK,
            requested_date=date(2024, 7, 30),
            total_days=1,
            business_days=1
        )
        
        test_session.add(vacation)
        await test_session.flush()
        await test_session.refresh(vacation)
        
        assert vacation.duration_days == 1

    async def test_duration_formatted_property(self, vacation_instance: Vacation):
        """Test de la propiedad duration_formatted."""
        assert vacation_instance.duration_formatted == "15 días"

    async def test_duration_formatted_single_day(self, test_session: AsyncSession, sample_employee: Employee):
        """Test duration_formatted para vacación de un solo día."""
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 1),
            vacation_type=VacationType.SICK,
            requested_date=date(2024, 7, 30),
            total_days=1,
            business_days=1
        )
        
        test_session.add(vacation)
        await test_session.flush()
        await test_session.refresh(vacation)
        
        assert vacation.duration_formatted == "1 día"

    # Tests de propiedades de estado
    async def test_is_approved_property(self, test_session: AsyncSession, sample_employee: Employee):
        """Test de la propiedad is_approved."""
        # Vacación aprobada
        approved_vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            vacation_type=VacationType.ANNUAL,
            status=VacationStatus.APPROVED,
            requested_date=date(2024, 7, 15),
            total_days=5,
            business_days=5
        )
        
        # Vacación pendiente
        pending_vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 9, 1),
            end_date=date(2024, 9, 5),
            vacation_type=VacationType.PERSONAL,
            status=VacationStatus.PENDING,
            requested_date=date(2024, 8, 15),
            total_days=5,
            business_days=5
        )
        
        assert approved_vacation.is_approved is True
        assert pending_vacation.is_approved is False

    async def test_is_pending_property(self, test_session: AsyncSession, sample_employee: Employee):
        """Test de la propiedad is_pending."""
        # Vacación pendiente
        pending_vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            vacation_type=VacationType.ANNUAL,
            status=VacationStatus.PENDING,
            requested_date=date(2024, 7, 15),
            total_days=5,
            business_days=5
        )
        
        # Vacación aprobada
        approved_vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 9, 1),
            end_date=date(2024, 9, 5),
            vacation_type=VacationType.PERSONAL,
            status=VacationStatus.APPROVED,
            requested_date=date(2024, 8, 15),
            total_days=5,
            business_days=5
        )
        
        assert pending_vacation.is_pending is True
        assert approved_vacation.is_pending is False

    async def test_is_active_property(self, test_session: AsyncSession, sample_employee: Employee):
        """Test de la propiedad is_active."""
        today = date.today()
        
        # Vacación activa (en curso)
        active_vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=today - timedelta(days=2),
            end_date=today + timedelta(days=3),
            vacation_type=VacationType.ANNUAL,
            status=VacationStatus.APPROVED,
            requested_date=today - timedelta(days=30),
            total_days=6,
            business_days=4
        )
        
        # Vacación futura
        future_vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=15),
            vacation_type=VacationType.PERSONAL,
            status=VacationStatus.APPROVED,
            requested_date=today - timedelta(days=15),
            total_days=6,
            business_days=4
        )
        
        # Vacación pasada
        past_vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=today - timedelta(days=20),
            end_date=today - timedelta(days=15),
            vacation_type=VacationType.SICK,
            status=VacationStatus.APPROVED,
            requested_date=today - timedelta(days=25),
            total_days=6,
            business_days=4
        )
        
        assert active_vacation.is_active is True
        assert future_vacation.is_active is False
        assert past_vacation.is_active is False

    async def test_is_upcoming_property(self, test_session: AsyncSession, sample_employee: Employee):
        """Test de la propiedad is_upcoming."""
        today = date.today()
        
        # Vacación futura
        future_vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=15),
            vacation_type=VacationType.ANNUAL,
            status=VacationStatus.APPROVED,
            requested_date=today - timedelta(days=15),
            total_days=6,
            business_days=4
        )
        
        # Vacación activa
        active_vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=today - timedelta(days=2),
            end_date=today + timedelta(days=3),
            vacation_type=VacationType.PERSONAL,
            status=VacationStatus.APPROVED,
            requested_date=today - timedelta(days=30),
            total_days=6,
            business_days=4
        )
        
        assert future_vacation.is_upcoming is True
        assert active_vacation.is_upcoming is False

    async def test_days_until_start_property(self, test_session: AsyncSession, sample_employee: Employee):
        """Test de la propiedad days_until_start."""
        today = date.today()
        
        # Vacación futura
        future_vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=15),
            vacation_type=VacationType.ANNUAL,
            status=VacationStatus.APPROVED,
            requested_date=today - timedelta(days=15),
            total_days=6,
            business_days=4
        )
        
        # Vacación que ya comenzó
        started_vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=today - timedelta(days=2),
            end_date=today + timedelta(days=3),
            vacation_type=VacationType.PERSONAL,
            status=VacationStatus.APPROVED,
            requested_date=today - timedelta(days=30),
            total_days=6,
            business_days=4
        )
        
        assert future_vacation.days_until_start == 10
        assert started_vacation.days_until_start == 0

    # Tests de propiedades de display
    async def test_vacation_type_display_property(self, test_session: AsyncSession, sample_employee: Employee):
        """Test de la propiedad vacation_type_display."""
        vacation_types_and_displays = [
            (VacationType.ANNUAL, "Vacaciones Anuales"),
            (VacationType.SICK, "Licencia Médica"),
            (VacationType.PERSONAL, "Asuntos Personales"),
            (VacationType.MATERNITY, "Licencia Maternal"),
            (VacationType.PATERNITY, "Licencia Paternal"),
            (VacationType.TRAINING, "Capacitación"),
            (VacationType.OTHER, "Otros")
        ]
        
        for vacation_type, expected_display in vacation_types_and_displays:
            vacation = Vacation(
                employee_id=sample_employee.id,
                start_date=date(2024, 8, 1),
                end_date=date(2024, 8, 5),
                vacation_type=vacation_type,
                requested_date=date(2024, 7, 15),
                total_days=5,
                business_days=5
            )
            
            assert vacation.vacation_type_display == expected_display

    async def test_status_display_property(self, test_session: AsyncSession, sample_employee: Employee):
        """Test de la propiedad status_display."""
        status_and_displays = [
            (VacationStatus.PENDING, "Pendiente"),
            (VacationStatus.APPROVED, "Aprobado"),
            (VacationStatus.REJECTED, "Rechazado"),
            (VacationStatus.CANCELLED, "Cancelado")
        ]
        
        for status, expected_display in status_and_displays:
            vacation = Vacation(
                employee_id=sample_employee.id,
                start_date=date(2024, 8, 1),
                end_date=date(2024, 8, 5),
                vacation_type=VacationType.ANNUAL,
                status=status,
                requested_date=date(2024, 7, 15),
                total_days=5,
                business_days=5
            )
            
            assert vacation.status_display == expected_display

    # Tests de métodos personalizados
    async def test_overlaps_with_method(self, test_session: AsyncSession, sample_employee: Employee):
        """Test del método overlaps_with."""
        # Vacación base
        vacation1 = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
            vacation_type=VacationType.ANNUAL,
            requested_date=date(2024, 6, 1),
            total_days=15,
            business_days=11
        )
        
        # Vacación que se superpone
        vacation2_overlap = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 7, 10),
            end_date=date(2024, 7, 20),
            vacation_type=VacationType.PERSONAL,
            requested_date=date(2024, 6, 15),
            total_days=11,
            business_days=8
        )
        
        # Vacación que no se superpone
        vacation3_no_overlap = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 10),
            vacation_type=VacationType.SICK,
            requested_date=date(2024, 7, 20),
            total_days=10,
            business_days=7
        )
        
        # Vacación adyacente (no se superpone)
        vacation4_adjacent = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 7, 16),
            end_date=date(2024, 7, 20),
            vacation_type=VacationType.TRAINING,
            requested_date=date(2024, 6, 20),
            total_days=5,
            business_days=4
        )
        
        assert vacation1.overlaps_with(vacation2_overlap) is True
        assert vacation1.overlaps_with(vacation3_no_overlap) is False
        assert vacation1.overlaps_with(vacation4_adjacent) is False
        
        # Test simétrico
        assert vacation2_overlap.overlaps_with(vacation1) is True

    # Tests de persistencia
    async def test_vacation_persistence(self, test_session: AsyncSession, sample_vacation_data):
        """Test que la vacación se persiste correctamente en la base de datos."""
        vacation = Vacation(**sample_vacation_data)
        test_session.add(vacation)
        await test_session.flush()
        await test_session.refresh(vacation)
        
        # Verificar que se asignó un ID
        assert vacation.id is not None
        assert isinstance(vacation.id, int)
        
        # Verificar que se asignaron timestamps
        assert vacation.created_at is not None
        assert vacation.updated_at is not None
        
        # Verificar que los datos se guardaron correctamente
        assert vacation.employee_id == sample_vacation_data["employee_id"]
        assert vacation.start_date == sample_vacation_data["start_date"]
        assert vacation.end_date == sample_vacation_data["end_date"]
        assert vacation.vacation_type == sample_vacation_data["vacation_type"]
        assert vacation.status == sample_vacation_data["status"]
        assert vacation.requested_date == sample_vacation_data["requested_date"]
        assert vacation.reason == sample_vacation_data["reason"]
        assert vacation.notes == sample_vacation_data["notes"]
        assert vacation.total_days == sample_vacation_data["total_days"]
        assert vacation.business_days == sample_vacation_data["business_days"]

    # Tests de relaciones
    async def test_employee_relationship(self, test_session: AsyncSession, vacation_instance: Vacation):
        """Test relación con Employee."""
        await test_session.refresh(vacation_instance, ["employee"])
        
        assert vacation_instance.employee is not None
        assert vacation_instance.employee.id == vacation_instance.employee_id
        assert isinstance(vacation_instance.employee, Employee)

    def test_vacation_relationships_defined(self):
        """Test que las relaciones están definidas en el modelo."""
        # Crear una instancia simple sin persistir
        vacation = Vacation(
            employee_id=1,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            vacation_type=VacationType.ANNUAL,
            requested_date=date(2024, 7, 15),
            total_days=5,
            business_days=5
        )
        
        # Verificar que las relaciones están definidas como atributos
        assert hasattr(vacation, 'employee')

    # Tests de representación
    async def test_vacation_repr(self, vacation_instance: Vacation):
        """Test de la representación string del modelo."""
        repr_str = repr(vacation_instance)
        
        assert "Vacation" in repr_str
        assert f"employee_id={vacation_instance.employee_id}" in repr_str
        assert f"start_date={vacation_instance.start_date}" in repr_str
        assert f"end_date={vacation_instance.end_date}" in repr_str
        assert f"status='{vacation_instance.status.value}'" in repr_str


class TestVacationConstraints:
    """Tests para constraints específicos del modelo Vacation."""

    async def test_vacation_employee_relationship_exists(self, test_session: AsyncSession, sample_employee: Employee):
        """Test que la relación con Employee funciona correctamente."""
        # Crear vacación con employee_id válido
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            vacation_type=VacationType.ANNUAL,
            requested_date=date(2024, 7, 15),
            total_days=5,
            business_days=5
        )
        
        test_session.add(vacation)
        await test_session.flush()
        await test_session.refresh(vacation)
        
        # Verificar que la vacación se creó correctamente
        assert vacation.id is not None
        assert vacation.employee_id == sample_employee.id
        
        # Verificar que la relación funciona
        await test_session.refresh(vacation, ["employee"])
        assert vacation.employee is not None
        assert vacation.employee.id == sample_employee.id


class TestVacationBusinessLogic:
    """Tests para lógica de negocio específica del modelo Vacation."""

    async def test_vacation_approval_workflow(self, test_session: AsyncSession, sample_employee: Employee):
        """Test del flujo de aprobación de vacaciones."""
        # Crear vacación pendiente
        vacation = Vacation(
            employee_id=sample_employee.id,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            vacation_type=VacationType.ANNUAL,
            status=VacationStatus.PENDING,
            requested_date=date(2024, 7, 15),
            total_days=5,
            business_days=5
        )
        
        test_session.add(vacation)
        await test_session.flush()
        await test_session.refresh(vacation)
        
        # Verificar estado inicial
        assert vacation.is_pending is True
        assert vacation.is_approved is False
        assert vacation.approved_date is None
        assert vacation.approved_by is None
        
        # Aprobar vacación
        vacation.status = VacationStatus.APPROVED
        vacation.approved_date = date.today()
        vacation.approved_by = "Manager Test"
        
        await test_session.flush()
        await test_session.refresh(vacation)
        
        # Verificar estado después de aprobación
        assert vacation.is_pending is False
        assert vacation.is_approved is True
        assert vacation.approved_date is not None
        assert vacation.approved_by == "Manager Test"

    async def test_multiple_vacations_same_employee(self, test_session: AsyncSession, sample_employee: Employee):
        """Test que un empleado puede tener múltiples vacaciones."""
        vacations = [
            Vacation(
                employee_id=sample_employee.id,
                start_date=date(2024, 7, 1),
                end_date=date(2024, 7, 15),
                vacation_type=VacationType.ANNUAL,
                requested_date=date(2024, 6, 1),
                total_days=15,
                business_days=11
            ),
            Vacation(
                employee_id=sample_employee.id,
                start_date=date(2024, 12, 20),
                end_date=date(2024, 12, 31),
                vacation_type=VacationType.ANNUAL,
                requested_date=date(2024, 11, 15),
                total_days=12,
                business_days=8
            ),
            Vacation(
                employee_id=sample_employee.id,
                start_date=date(2024, 9, 5),
                end_date=date(2024, 9, 5),
                vacation_type=VacationType.SICK,
                requested_date=date(2024, 9, 5),
                total_days=1,
                business_days=1
            )
        ]
        
        for vacation in vacations:
            test_session.add(vacation)
        
        await test_session.flush()
        
        # Verificar que todas las vacaciones se crearon
        result = await test_session.execute(
            select(Vacation).where(Vacation.employee_id == sample_employee.id)
        )
        employee_vacations = result.scalars().all()
        
        assert len(employee_vacations) == 3
        
        # Verificar que no hay superposiciones entre las vacaciones anuales
        annual_vacations = [v for v in employee_vacations if v.vacation_type == VacationType.ANNUAL]
        assert len(annual_vacations) == 2
        assert not annual_vacations[0].overlaps_with(annual_vacations[1])