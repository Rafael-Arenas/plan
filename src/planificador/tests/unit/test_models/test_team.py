# src/planificador/tests/unit/test_models/test_team.py

import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from planificador.models.team import Team
from planificador.models.team_membership import TeamMembership
from planificador.models.employee import Employee


class TestTeamModel:
    """Tests para el modelo Team."""

    async def test_team_creation_minimal_fields(self, test_session: Session):
        """Test creación de equipo con campos mínimos requeridos."""
        team = Team(
            name="Equipo Test"
        )
        test_session.add(team)
        await test_session.flush()

        assert team.id is not None
        assert team.name == "Equipo Test"
        assert team.code is None  # Opcional
        assert team.description is None  # Opcional
        assert team.color_hex == '#3498db'  # Default
        assert team.max_members == 10  # Default
        assert team.is_active is True  # Default
        assert team.notes is None  # Opcional
        assert team.created_at is not None
        assert team.updated_at is not None

    async def test_team_creation_with_all_fields(self, test_session: Session):
        """Test creación de equipo con todos los campos."""
        team = Team(
            name="Equipo Completo",
            code="EC01",
            description="Descripción del equipo completo",
            color_hex="#ff5733",
            max_members=15,
            is_active=True,
            notes="Notas importantes del equipo"
        )
        test_session.add(team)
        await test_session.flush()

        assert team.id is not None
        assert team.name == "Equipo Completo"
        assert team.code == "EC01"
        assert team.description == "Descripción del equipo completo"
        assert team.color_hex == "#ff5733"
        assert team.max_members == 15
        assert team.is_active is True
        assert team.notes == "Notas importantes del equipo"

    async def test_team_creation_with_defaults(self, test_session: Session):
        """Test creación de equipo verificando valores por defecto."""
        team = Team(
            name="Equipo Defaults"
        )
        test_session.add(team)
        await test_session.flush()  # Flush para aplicar defaults de BD
        await test_session.refresh(team)  # Refrescar para obtener valores de BD

        # Verificar defaults específicos
        assert team.color_hex == '#3498db'
        assert team.max_members == 10
        assert team.is_active is True
        assert team.created_at is not None
        assert team.updated_at is not None

    async def test_team_required_fields_validation(self, test_session: Session):
        """Test validación de campos requeridos."""
        # Test sin name (requerido)
        with pytest.raises(IntegrityError):
            team = Team(
                code="T01",
                description="Equipo sin nombre"
            )
            test_session.add(team)
            await test_session.flush()

    async def test_team_unique_name_constraint(self, test_session: Session):
        """Test restricción de unicidad en name."""
        # Crear primer equipo
        team1 = Team(
            name="Equipo Único",
            code="EU1"
        )
        test_session.add(team1)
        await test_session.flush()

        # Intentar crear equipo con nombre duplicado
        team2 = Team(
            name="Equipo Único",  # Nombre duplicado
            code="EU2"
        )
        test_session.add(team2)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()
    
    async def test_team_unique_code_constraint(self, test_session: Session):
        """Test restricción de unicidad en code."""
        # Crear primer equipo
        team1 = Team(
            name="Equipo Diferente 1",
            code="EU_CODE"
        )
        test_session.add(team1)
        await test_session.flush()

        # Intentar crear equipo con código duplicado
        team2 = Team(
            name="Equipo Diferente 2",
            code="EU_CODE"  # Código duplicado
        )
        test_session.add(team2)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_team_string_length_constraints(self, test_session: Session):
        """Test que los campos string aceptan valores dentro de los límites esperados."""
        # Test name con longitud máxima válida (100 caracteres)
        team_max_name = Team(
            name="A" * 100  # 100 caracteres exactos
        )
        test_session.add(team_max_name)
        await test_session.flush()
        assert len(team_max_name.name) == 100

        # Test code con longitud máxima válida (20 caracteres)
        team_max_code = Team(
            name="Equipo Test Code",
            code="A" * 20  # 20 caracteres exactos
        )
        test_session.add(team_max_code)
        await test_session.flush()
        assert len(team_max_code.code) == 20

        # Test color_hex con longitud máxima válida (7 caracteres)
        team_max_color = Team(
            name="Equipo Test Color",
            color_hex="#123456"  # 7 caracteres exactos
        )
        test_session.add(team_max_color)
        await test_session.flush()
        assert len(team_max_color.color_hex) == 7

    async def test_team_display_name_property(self, test_session: Session):
        """Test propiedad display_name."""
        # Test con código
        team_with_code = Team(
            name="Equipo Con Código",
            code="ECC"
        )
        test_session.add(team_with_code)
        await test_session.flush()

        assert team_with_code.display_name == "Equipo Con Código (ECC)"

        # Test sin código
        team_without_code = Team(
            name="Equipo Sin Código"
        )
        test_session.add(team_without_code)
        await test_session.flush()

        assert team_without_code.display_name == "Equipo Sin Código"

    async def test_team_capacity_properties_empty_team(self, test_session: Session):
        """Test propiedades de capacidad con equipo vacío."""
        team = Team(
            name="Equipo Vacío",
            max_members=5
        )
        test_session.add(team)
        await test_session.flush()
        await test_session.refresh(team, ['memberships'])

        # Sin miembros
        assert team.current_members_count == 0
        assert team.is_at_capacity is False
        assert team.available_spots == 5
        assert team.capacity_percentage == 0.0

    async def test_team_capacity_properties_with_members(self, test_session: Session):
        """Test propiedades de capacidad con miembros."""
        # Crear equipo
        team = Team(
            name="Equipo Con Miembros",
            max_members=3
        )
        test_session.add(team)
        await test_session.flush()

        # Crear empleados
        employee1 = Employee(
            first_name="Juan",
            last_name="Pérez",
            email="juan@example.com"
        )
        employee2 = Employee(
            first_name="María",
            last_name="García",
            email="maria@example.com"
        )
        employee3 = Employee(
            first_name="Carlos",
            last_name="López",
            email="carlos@example.com"
        )
        test_session.add_all([employee1, employee2, employee3])
        await test_session.flush()

        # Crear membresías activas
        membership1 = TeamMembership(
            team_id=team.id,
            employee_id=employee1.id,
            start_date=date.today(),
            is_active=True
        )
        membership2 = TeamMembership(
            team_id=team.id,
            employee_id=employee2.id,
            start_date=date.today(),
            is_active=True
        )
        # Membresía inactiva (no debe contar)
        membership3 = TeamMembership(
            team_id=team.id,
            employee_id=employee3.id,
            start_date=date.today(),
            is_active=False
        )
        test_session.add_all([membership1, membership2, membership3])
        await test_session.flush()

        # Flush para persistir y refrescar para cargar relaciones
        await test_session.flush()
        await test_session.refresh(team)
        
        # Cargar explícitamente las relaciones
        stmt = select(Team).options(selectinload(Team.memberships)).where(Team.id == team.id)
        result = await test_session.execute(stmt)
        team = result.scalar_one()

        # Solo 2 miembros activos
        assert team.current_members_count == 2
        assert team.is_at_capacity is False
        assert team.available_spots == 1
        assert team.capacity_percentage == (2/3) * 100  # 66.67%

    async def test_team_at_capacity(self, test_session: Session):
        """Test equipo a capacidad máxima."""
        # Crear equipo pequeño
        team = Team(
            name="Equipo Pequeño",
            max_members=2
        )
        test_session.add(team)
        await test_session.flush()

        # Crear empleados
        employee1 = Employee(
            first_name="Ana",
            last_name="Martín",
            email="ana@example.com"
        )
        employee2 = Employee(
            first_name="Luis",
            last_name="Rodríguez",
            email="luis@example.com"
        )
        test_session.add_all([employee1, employee2])
        await test_session.flush()

        # Llenar a capacidad
        membership1 = TeamMembership(
            team_id=team.id,
            employee_id=employee1.id,
            start_date=date.today(),
            is_active=True
        )
        membership2 = TeamMembership(
            team_id=team.id,
            employee_id=employee2.id,
            start_date=date.today(),
            is_active=True
        )
        test_session.add_all([membership1, membership2])
        await test_session.flush()

        # Flush para persistir y refrescar para cargar relaciones
        await test_session.flush()
        await test_session.refresh(team)
        
        # Cargar explícitamente las relaciones
        stmt = select(Team).options(selectinload(Team.memberships)).where(Team.id == team.id)
        result = await test_session.execute(stmt)
        team = result.scalar_one()

        assert team.current_members_count == 2
        assert team.is_at_capacity is True
        assert team.available_spots == 0
        assert team.capacity_percentage == 100.0

    async def test_team_capacity_with_zero_max_members(self, test_session: Session):
        """Test capacidad con max_members = 0."""
        team = Team(
            name="Equipo Sin Capacidad",
            max_members=0
        )
        test_session.add(team)
        await test_session.flush()
        await test_session.refresh(team, ['memberships'])

        assert team.current_members_count == 0
        assert team.is_at_capacity is True  # 0 >= 0
        assert team.available_spots == 0
        assert team.capacity_percentage == 0.0  # Caso especial

    async def test_team_status_display_property(self, test_session: Session):
        """Test propiedad status_display."""
        # Equipo activo
        team_active = Team(
            name="Equipo Activo",
            is_active=True
        )
        test_session.add(team_active)
        await test_session.flush()

        assert team_active.status_display == "Activo"

        # Equipo inactivo
        team_inactive = Team(
            name="Equipo Inactivo",
            is_active=False
        )
        test_session.add(team_inactive)
        await test_session.flush()

        assert team_inactive.status_display == "Inactivo"

    async def test_team_repr(self, test_session: Session):
        """Test representación string del modelo."""
        team = Team(
            name="Equipo Repr",
            code="REP"
        )
        test_session.add(team)
        await test_session.flush()

        expected_repr = f"<Team(id={team.id}, name='Equipo Repr', code='REP')>"
        assert repr(team) == expected_repr

        # Test sin código
        team_no_code = Team(
            name="Equipo Sin Código"
        )
        test_session.add(team_no_code)
        await test_session.flush()

        expected_repr_no_code = f"<Team(id={team_no_code.id}, name='Equipo Sin Código', code='None')>"
        assert repr(team_no_code) == expected_repr_no_code

    async def test_team_memberships_relationship(self, test_session: Session):
        """Test relación con TeamMembership."""
        # Crear equipo
        team = Team(
            name="Equipo Relaciones"
        )
        test_session.add(team)
        await test_session.flush()

        # Crear empleado
        employee = Employee(
            first_name="Pedro",
            last_name="Sánchez",
            email="pedro@example.com"
        )
        test_session.add(employee)
        await test_session.flush()

        # Crear membresía
        membership = TeamMembership(
            team_id=team.id,
            employee_id=employee.id,
            start_date=date.today(),
            is_active=True
        )
        test_session.add(membership)
        await test_session.flush()

        # Flush para persistir y refrescar para cargar relaciones
        await test_session.flush()
        await test_session.refresh(team)
        
        # Cargar explícitamente las relaciones
        stmt = select(Team).options(selectinload(Team.memberships)).where(Team.id == team.id)
        result = await test_session.execute(stmt)
        team = result.scalar_one()

        # Test relación
        assert len(team.memberships) == 1
        assert team.memberships[0].employee_id == employee.id
        assert team.memberships[0].is_active is True

    async def test_team_boolean_field_variations(self, test_session: Session):
        """Test variaciones del campo booleano is_active."""
        # Equipo activo explícito
        team_active = Team(
            name="Equipo Activo Explícito",
            is_active=True
        )
        test_session.add(team_active)
        await test_session.flush()
        assert team_active.is_active is True

        # Equipo inactivo explícito
        team_inactive = Team(
            name="Equipo Inactivo Explícito",
            is_active=False
        )
        test_session.add(team_inactive)
        await test_session.flush()
        assert team_inactive.is_active is False

        # Equipo con default (debe ser True)
        team_default = Team(
            name="Equipo Default"
        )
        test_session.add(team_default)
        await test_session.flush()  # Flush para aplicar defaults de BD
        await test_session.refresh(team_default)  # Refrescar para obtener valores de BD
        assert team_default.is_active is True

    async def test_team_color_hex_validation(self, test_session: Session):
        """Test validación del campo color_hex."""
        # Color válido
        team_valid_color = Team(
            name="Equipo Color Válido",
            color_hex="#ff0000"
        )
        test_session.add(team_valid_color)
        await test_session.flush()
        assert team_valid_color.color_hex == "#ff0000"

        # Color por defecto
        team_default = Team(
            name="Equipo Color Default"
        )
        test_session.add(team_default)
        await test_session.flush()  # Flush para aplicar defaults de BD
        await test_session.refresh(team_default)  # Refrescar para obtener valores de BD
        assert team_default.color_hex == "#3498db"

    async def test_team_max_members_edge_cases(self, test_session: Session):
        """Test casos límite para max_members."""
        # max_members = 1
        team_one = Team(
            name="Equipo Uno",
            max_members=1
        )
        test_session.add(team_one)
        await test_session.flush()
        await test_session.refresh(team_one, ['memberships'])
        assert team_one.max_members == 1
        assert team_one.available_spots == 1

        # max_members muy grande
        team_large = Team(
            name="Equipo Grande",
            max_members=1000
        )
        test_session.add(team_large)
        await test_session.flush()
        await test_session.refresh(team_large, ['memberships'])
        assert team_large.max_members == 1000
        assert team_large.available_spots == 1000

    async def test_team_cascade_delete_memberships(self, test_session: Session):
        """Test eliminación en cascada de membresías."""
        # Crear equipo
        team = Team(
            name="Equipo Para Eliminar"
        )
        test_session.add(team)
        await test_session.flush()

        # Crear empleado
        employee = Employee(
            first_name="Temporal",
            last_name="Usuario",
            email="temporal@example.com"
        )
        test_session.add(employee)
        await test_session.flush()

        # Crear membresía
        membership = TeamMembership(
            team_id=team.id,
            employee_id=employee.id,
            start_date=date.today(),
            is_active=True
        )
        test_session.add(membership)
        await test_session.flush()

        membership_id = membership.id

        # Eliminar equipo (debe eliminar membresías en cascada)
        await test_session.delete(team)
        await test_session.flush()

        # Verificar que las membresías fueron eliminadas
        stmt = select(TeamMembership).where(TeamMembership.id == membership_id)
        result = await test_session.execute(stmt)
        deleted_membership = result.scalar_one_or_none()
        assert deleted_membership is None

        # El empleado debe seguir existiendo
        existing_employee = await test_session.get(Employee, employee.id)
        assert existing_employee is not None