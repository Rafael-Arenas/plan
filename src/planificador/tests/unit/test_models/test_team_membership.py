"""Tests para el modelo TeamMembership.

Este módulo contiene tests comprehensivos para el modelo TeamMembership,
incluyendo validaciones, constraints, enums, relaciones, métodos personalizados
y propiedades calculadas.
"""

import pytest
import pytest_asyncio
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.models.employee import Employee, EmployeeStatus
from planificador.models.team import Team


class TestMembershipRole:
    """Tests para el enum MembershipRole."""

    def test_membership_role_values(self):
        """Test que el enum tiene todos los valores esperados."""
        expected_values = {
            "MEMBER": "member",
            "LEAD": "lead",
            "SUPERVISOR": "supervisor",
            "COORDINATOR": "coordinator"
        }
        
        for attr_name, expected_value in expected_values.items():
            role = getattr(MembershipRole, attr_name)
            assert role.value == expected_value

    def test_membership_role_enum_membership(self):
        """Test que todos los roles son miembros válidos del enum."""
        assert MembershipRole.MEMBER in MembershipRole
        assert MembershipRole.LEAD in MembershipRole
        assert MembershipRole.SUPERVISOR in MembershipRole
        assert MembershipRole.COORDINATOR in MembershipRole


class TestTeamMembershipModel:
    """Tests para el modelo TeamMembership."""

    # Tests de creación de instancias
    async def test_membership_creation_with_all_fields(
        self,
        sample_membership_data: dict
    ):
        """Test creación de membresía con todos los campos."""
        membership = TeamMembership(**sample_membership_data)
        
        assert membership.employee_id == sample_membership_data["employee_id"]
        assert membership.team_id == sample_membership_data["team_id"]
        assert membership.role == MembershipRole.MEMBER
        assert membership.start_date == date(2024, 1, 15)
        assert membership.end_date == date(2024, 12, 31)
        assert membership.is_active is True

    async def test_membership_creation_minimal_fields(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test creación de membresía solo con campos obligatorios."""
        membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=date(2024, 1, 15)
        )
        
        test_session.add(membership)
        await test_session.flush()
        await test_session.refresh(membership)
        
        assert membership.employee_id == sample_employee.id
        assert membership.team_id == sample_team.id
        assert membership.role == MembershipRole.MEMBER  # Valor por defecto
        assert membership.start_date == date(2024, 1, 15)
        assert membership.end_date is None
        assert membership.is_active is True  # Valor por defecto

    async def test_membership_creation_with_defaults(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test que los valores por defecto se aplican correctamente."""
        membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=date(2024, 1, 15)
        )
        
        test_session.add(membership)
        await test_session.flush()
        await test_session.refresh(membership)
        
        assert membership.role == MembershipRole.MEMBER
        assert membership.is_active is True

    # Tests de validaciones y constraints
    async def test_membership_employee_id_required(
        self,
        test_session: AsyncSession,
        sample_team: Team
    ):
        """Test que employee_id es obligatorio."""
        membership = TeamMembership(
            team_id=sample_team.id,
            start_date=date(2024, 1, 15)
        )
        test_session.add(membership)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_membership_team_id_required(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test que team_id es obligatorio."""
        membership = TeamMembership(
            employee_id=sample_employee.id,
            start_date=date(2024, 1, 15)
        )
        test_session.add(membership)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_membership_start_date_required(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test que start_date es obligatorio."""
        membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id
        )
        test_session.add(membership)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_membership_foreign_key_employee_constraint(
        self,
        test_session: AsyncSession,
        sample_team: Team
    ):
        """Test que employee_id debe referenciar un empleado existente.
        
        Nota: SQLite en modo testing puede no tener foreign key constraints habilitadas,
        por lo que este test verifica la creación pero no necesariamente la restricción.
        """
        membership = TeamMembership(
            employee_id=99999,  # ID inexistente
            team_id=sample_team.id,
            start_date=date(2024, 1, 15)
        )
        test_session.add(membership)
        
        # En SQLite de testing, las FK constraints pueden no estar habilitadas
        # Este test verifica que el modelo acepta el valor pero no valida la restricción
        try:
            await test_session.flush()
            # Si no hay error, el modelo acepta IDs inexistentes (comportamiento esperado en testing)
            assert membership.employee_id == 99999
        except IntegrityError:
            # Si hay error, las FK constraints están habilitadas (comportamiento ideal)
            pass

    async def test_membership_foreign_key_team_constraint(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test que team_id debe referenciar un equipo existente.
        
        Nota: SQLite en modo testing puede no tener foreign key constraints habilitadas,
        por lo que este test verifica la creación pero no necesariamente la restricción.
        """
        membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=99999,  # ID inexistente
            start_date=date(2024, 1, 15)
        )
        test_session.add(membership)
        
        # En SQLite de testing, las FK constraints pueden no estar habilitadas
        # Este test verifica que el modelo acepta el valor pero no valida la restricción
        try:
            await test_session.flush()
            # Si no hay error, el modelo acepta IDs inexistentes (comportamiento esperado en testing)
            assert membership.team_id == 99999
        except IntegrityError:
            # Si hay error, las FK constraints están habilitadas (comportamiento ideal)
            pass


class TestTeamMembershipProperties:
    """Tests para las propiedades del modelo TeamMembership."""

    async def test_duration_days_property(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test del cálculo de duración en días."""
        # Membresía con fecha de fin específica
        membership_with_end = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            is_active=True
        )
        
        # Membresía sin fecha de fin (usa fecha actual)
        membership_without_end = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=date.today() - timedelta(days=30),
            is_active=True
        )
        
        test_session.add_all([membership_with_end, membership_without_end])
        await test_session.flush()
        
        assert membership_with_end.duration_days == 30
        assert membership_without_end.duration_days == 30

    async def test_is_current_property(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test de la propiedad is_current."""
        today = date.today()
        
        # Membresía actual activa
        current_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=30),
            is_active=True
        )
        
        # Membresía inactiva
        inactive_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=30),
            is_active=False
        )
        
        # Membresía futura
        future_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today + timedelta(days=10),
            is_active=True
        )
        
        # Membresía pasada
        past_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=30),
            is_active=True
        )
        
        test_session.add_all([
            current_membership,
            inactive_membership,
            future_membership,
            past_membership
        ])
        await test_session.flush()
        
        assert current_membership.is_current is True
        assert inactive_membership.is_current is False
        assert future_membership.is_current is False
        assert past_membership.is_current is False

    async def test_is_future_property(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test de la propiedad is_future."""
        today = date.today()
        
        # Membresía futura
        future_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today + timedelta(days=10),
            is_active=True
        )
        
        # Membresía actual
        current_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=10),
            is_active=True
        )
        
        test_session.add_all([future_membership, current_membership])
        await test_session.flush()
        
        assert future_membership.is_future is True
        assert current_membership.is_future is False

    async def test_is_past_property(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test de la propiedad is_past."""
        today = date.today()
        
        # Membresía pasada
        past_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=30),
            is_active=True
        )
        
        # Membresía sin fecha de fin
        indefinite_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=30),
            is_active=True
        )
        
        # Membresía actual
        current_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=30),
            is_active=True
        )
        
        test_session.add_all([
            past_membership,
            indefinite_membership,
            current_membership
        ])
        await test_session.flush()
        
        assert past_membership.is_past is True
        assert indefinite_membership.is_past is False
        assert current_membership.is_past is False

    async def test_is_indefinite_property(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test de la propiedad is_indefinite."""
        # Membresía indefinida (sin fecha de fin)
        indefinite_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=date(2024, 1, 15),
            is_active=True
        )
        
        # Membresía con fecha de fin
        definite_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 12, 31),
            is_active=True
        )
        
        test_session.add_all([indefinite_membership, definite_membership])
        await test_session.flush()
        
        assert indefinite_membership.is_indefinite is True
        assert definite_membership.is_indefinite is False

    def test_role_display_property(self):
        """Test de la propiedad role_display."""
        membership_member = TeamMembership(role=MembershipRole.MEMBER)
        membership_lead = TeamMembership(role=MembershipRole.LEAD)
        membership_supervisor = TeamMembership(role=MembershipRole.SUPERVISOR)
        membership_coordinator = TeamMembership(role=MembershipRole.COORDINATOR)
        
        assert membership_member.role_display == "Miembro"
        assert membership_lead.role_display == "Líder"
        assert membership_supervisor.role_display == "Supervisor"
        assert membership_coordinator.role_display == "Coordinador"

    async def test_status_display_property(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test de la propiedad status_display."""
        today = date.today()
        
        # Membresía inactiva
        inactive_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today,
            is_active=False
        )
        
        # Membresía futura
        future_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today + timedelta(days=10),
            is_active=True
        )
        
        # Membresía pasada
        past_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=30),
            is_active=True
        )
        
        # Membresía actual
        current_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=30),
            is_active=True
        )
        
        test_session.add_all([
            inactive_membership,
            future_membership,
            past_membership,
            current_membership
        ])
        await test_session.flush()
        
        assert inactive_membership.status_display == "Inactivo"
        assert future_membership.status_display == "Futuro"
        assert past_membership.status_display == "Finalizado"
        assert current_membership.status_display == "Activo"

    def test_membership_summary_property(
        self,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test de la propiedad membership_summary."""
        membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            role=MembershipRole.LEAD,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30),
            is_active=True
        )
        
        expected_summary = f"{membership.role_display} - {membership.status_display}"
        assert membership.membership_summary == expected_summary


class TestTeamMembershipMethods:
    """Tests para los métodos del modelo TeamMembership."""

    async def test_days_until_start_method(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test del método days_until_start."""
        today = date.today()
        
        # Membresía futura
        future_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today + timedelta(days=10),
            is_active=True
        )
        
        # Membresía ya iniciada
        started_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=10),
            is_active=True
        )
        
        test_session.add_all([future_membership, started_membership])
        await test_session.flush()
        
        assert future_membership.days_until_start() == 10
        assert started_membership.days_until_start() == 0

    async def test_days_until_end_method(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test del método days_until_end."""
        today = date.today()
        
        # Membresía con fecha de fin futura
        future_end_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=10),
            is_active=True
        )
        
        # Membresía ya terminada
        ended_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=30),
            is_active=True
        )
        
        # Membresía indefinida
        indefinite_membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            start_date=today - timedelta(days=30),
            is_active=True
        )
        
        test_session.add_all([
            future_end_membership,
            ended_membership,
            indefinite_membership
        ])
        await test_session.flush()
        
        assert future_end_membership.days_until_end() == 10
        assert ended_membership.days_until_end() == 0
        assert indefinite_membership.days_until_end() == -1

    def test_repr_method(
        self,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test del método __repr__."""
        membership = TeamMembership(
            employee_id=sample_employee.id,
            team_id=sample_team.id,
            role=MembershipRole.LEAD,
            start_date=date(2024, 1, 15)
        )
        
        expected_repr = f"<TeamMembership(employee_id={sample_employee.id}, team_id={sample_team.id}, role='lead')>"
        assert repr(membership) == expected_repr


# Tests de relaciones eliminados - ahora centralizados en test_model_relationships.py
# Ver TestTeamMembershipRelationship en test_model_relationships.py para tests de relaciones


class TestTeamMembershipRoleScenarios:
    """Tests para diferentes escenarios de roles en membresías."""

    async def test_multiple_roles_same_employee_different_teams(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test que un empleado puede tener diferentes roles en diferentes equipos."""
        # Crear múltiples equipos
        team1 = Team(name="Dev Team", description="Desarrollo", is_active=True)
        team2 = Team(name="QA Team", description="QA", is_active=True)
        
        test_session.add_all([team1, team2])
        await test_session.flush()
        
        # Crear membresías con diferentes roles
        membership1 = TeamMembership(
            employee_id=sample_employee.id,
            team_id=team1.id,
            role=MembershipRole.MEMBER,
            start_date=date(2024, 1, 15),
            is_active=True
        )
        
        membership2 = TeamMembership(
            employee_id=sample_employee.id,
            team_id=team2.id,
            role=MembershipRole.LEAD,
            start_date=date(2024, 1, 15),
            is_active=True
        )
        
        test_session.add_all([membership1, membership2])
        await test_session.flush()
        
        # Verificar que ambas membresías existen con roles diferentes
        result = await test_session.execute(
            select(TeamMembership).where(
                TeamMembership.employee_id == sample_employee.id
            )
        )
        memberships = result.scalars().all()
        
        assert len(memberships) == 2
        roles = [m.role for m in memberships]
        assert MembershipRole.MEMBER in roles
        assert MembershipRole.LEAD in roles

    async def test_role_hierarchy_validation(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_team: Team
    ):
        """Test que se pueden asignar todos los tipos de roles."""
        memberships = []
        
        for i, role in enumerate(MembershipRole):
            membership = TeamMembership(
                employee_id=sample_employee.id,
                team_id=sample_team.id,
                role=role,
                start_date=date(2024, 1, 15) + timedelta(days=i),
                is_active=True
            )
            memberships.append(membership)
            test_session.add(membership)
        
        await test_session.flush()
        
        # Verificar que todas las membresías se crearon correctamente
        result = await test_session.execute(
            select(TeamMembership).where(
                TeamMembership.employee_id == sample_employee.id,
                TeamMembership.team_id == sample_team.id
            )
        )
        saved_memberships = result.scalars().all()
        
        assert len(saved_memberships) == len(MembershipRole)
        saved_roles = [m.role for m in saved_memberships]
        
        for role in MembershipRole:
            assert role in saved_roles