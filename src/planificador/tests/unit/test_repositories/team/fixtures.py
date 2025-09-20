# src/planificador/tests/unit/test_repositories/team/fixtures.py
"""
Fixtures para tests del TeamRepositoryFacade.

Este módulo contiene todas las fixtures necesarias para testear
las operaciones del repositorio de equipos, incluyendo mocks,
datos de prueba y configuraciones específicas.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.repositories.team import TeamRepositoryFacade
from planificador.models.team import Team
from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.models.employee import Employee, EmployeeStatus


# ============================================================================
# FIXTURES DE SESIÓN Y REPOSITORIO
# ============================================================================

@pytest.fixture
def mock_session():
    """Mock de sesión asíncrona de SQLAlchemy."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    session.add = MagicMock()
    session.delete = MagicMock()
    session.merge = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def team_repository(mock_session):
    """
    Fixture que proporciona un mock completo de TeamRepositoryFacade.
    
    Returns:
        Mock: Mock configurado del TeamRepositoryFacade con todos los métodos necesarios
    """
    from sqlalchemy.exc import SQLAlchemyError, IntegrityError
    from planificador.exceptions.repository.base_repository_exceptions import (
        convert_sqlalchemy_error, 
        RepositoryError
    )
    
    # Crear un mock del TeamRepositoryFacade
    mock_facade = AsyncMock(spec=TeamRepositoryFacade)
    mock_facade.session = mock_session
    
    # Configurar métodos CRUD básicos con side effects para manejo de errores
    async def create_side_effect(team_data, **kwargs):
        """Side effect para simular create con manejo de sesión y excepciones."""
        try:
            mock_session.add(AsyncMock())  # Simular add (sin await)
            await mock_session.commit()  # Esto puede lanzar excepciones configuradas en el test
            return {"id": 1, "name": team_data.get("name", "Test Team")}
        except SQLAlchemyError as e:
            await mock_session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create",
                entity_type="Team"
            )
        except Exception as e:
            await mock_session.rollback()
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="create",
                entity_type="Team",
                original_error=e
            )
    
    async def update_side_effect(team_id, team_data, **kwargs):
        """Side effect para simular update con manejo de sesión y excepciones."""
        try:
            # Simular operaciones que pueden fallar
            await mock_session.execute(AsyncMock())  # Esto puede lanzar excepciones configuradas en el test
            mock_session.add(AsyncMock())  # Simular add (sin await)
            await mock_session.commit()  # Esto puede lanzar excepciones configuradas en el test
            return {"id": team_id, "name": team_data.get("name", "Updated Team")}
        except SQLAlchemyError as e:
            await mock_session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update",
                entity_type="Team",
                entity_id=team_id
            )
        except Exception as e:
            await mock_session.rollback()
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="update",
                entity_type="Team",
                entity_id=team_id,
                original_error=e
            )
    
    async def add_member_side_effect(team_id, employee_id, role="MEMBER", start_date=None, **kwargs):
        """Side effect que simula agregar miembro y maneja errores de sesión."""
        try:
            # Simular operaciones que pueden fallar
            await mock_session.execute(AsyncMock())  # Esto puede lanzar excepciones configuradas en el test
            mock_session.add(AsyncMock())  # Simular add (sin await)
            await mock_session.commit()  # Esto puede lanzar excepciones configuradas en el test
            return {"team_id": team_id, "employee_id": employee_id, "role": role}
        except SQLAlchemyError as e:
            await mock_session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="add_member",
                entity_type="TeamMember",
                entity_id=f"{team_id}-{employee_id}"
            )
        except Exception as e:
            await mock_session.rollback()
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="add_member",
                entity_type="TeamMember",
                entity_id=f"{team_id}-{employee_id}",
                original_error=e
            )
    
    # Configurar métodos CRUD básicos
    mock_facade.create = AsyncMock(side_effect=create_side_effect)
    mock_facade.get_by_id = AsyncMock(return_value={"id": 1, "name": "Test Team"})
    mock_facade.get_all = AsyncMock(return_value=[{"id": 1, "name": "Test Team"}])
    mock_facade.update = AsyncMock(side_effect=update_side_effect)
    mock_facade.delete = AsyncMock(return_value=True)
    mock_facade.exists_by_id = AsyncMock(return_value=True)
    mock_facade.count_all = AsyncMock(return_value=5)
    mock_facade.add_member = AsyncMock(side_effect=add_member_side_effect)
    
    # Configurar métodos de consulta de miembros
    mock_facade.get_active_members = AsyncMock(return_value=[
        {"employee_id": 1, "team_id": 1, "role": "lead", "is_active": True},
        {"employee_id": 2, "team_id": 1, "role": "member", "is_active": True}
    ])
    mock_facade.get_members_by_role = AsyncMock(return_value=[
        {"employee_id": 2, "team_id": 1, "role": "member", "is_active": True}
    ])
    mock_facade.get_team_leaders = AsyncMock(return_value=[
        {"employee_id": 1, "team_id": 1, "role": "lead", "is_active": True}
    ])
    mock_facade.get_teams_by_employee = AsyncMock(return_value=[
        {"employee_id": 1, "team_id": 1, "role": "lead", "is_active": True}
    ])
    
    # Configurar métodos de validación - los tests configuran excepciones específicas
    mock_facade.validate_team_data = AsyncMock(return_value=True)
    mock_facade.validate_team_name = AsyncMock(return_value=True)
    mock_facade.validate_member_capacity = AsyncMock(return_value=True)
    mock_facade.can_add_member = AsyncMock(return_value=True)
    
    # Configurar métodos de operaciones bulk - los tests configuran return values
    mock_facade.bulk_update_team_members = AsyncMock(return_value=True)
    mock_facade.archive_team = AsyncMock(return_value=True)
    mock_facade.reactivate_team = AsyncMock(return_value=True)
    
    # Configurar métodos de consulta faltantes - los tests configuran return values específicos
    mock_facade.find_by_name = AsyncMock(return_value=None)
    mock_facade.find_by_code = AsyncMock(return_value=None)
    mock_facade.find_active_teams = AsyncMock(return_value=[])
    mock_facade.find_teams_with_capacity = AsyncMock(return_value=[])
    
    # Configurar métodos CRUD faltantes - los tests configuran return values específicos
    mock_facade.update = AsyncMock(return_value=None)
    mock_facade.delete = AsyncMock(return_value=True)
    mock_facade.exists_by_id = AsyncMock(return_value=True)
    mock_facade.count_all = AsyncMock(return_value=0)
    mock_facade.search_teams = AsyncMock(return_value=[])
    
    # Configurar métodos de estadísticas con side effects apropiados
    async def get_role_distribution_side_effect(**kwargs):
        """Side effect para obtener distribución de roles."""
        await mock_session.execute(AsyncMock())
        return {
            "MEMBER": 8,
            "LEAD": 3,
            "SUPERVISOR": 2,
            "COORDINATOR": 2
        }
    
    async def get_capacity_statistics_side_effect(**kwargs):
        """Side effect para obtener estadísticas de capacidad."""
        await mock_session.execute(AsyncMock())  # teams_with_capacity
        await mock_session.execute(AsyncMock())  # teams_at_capacity
        return {
            "teams_with_capacity": 3,
            "teams_at_capacity": 1
        }
    
    mock_facade.get_team_statistics = AsyncMock(return_value={
        "total_teams": 10,
        "active_teams": 8,
        "inactive_teams": 2
    })
    mock_facade.get_membership_statistics = AsyncMock(return_value={
        "total_memberships": 50,
        "active_memberships": 45,
        "inactive_memberships": 5
    })
    mock_facade.get_role_distribution = AsyncMock(side_effect=get_role_distribution_side_effect)
    mock_facade.get_capacity_statistics = AsyncMock(side_effect=get_capacity_statistics_side_effect)
    
    # Configurar métodos de operaciones compuestas con side effects que simulan BD
    async def create_team_with_members_side_effect(team_data, member_ids, **kwargs):
        """Side effect para crear equipo con miembros."""
        # Simular operaciones de base de datos
        await mock_session.execute(AsyncMock())  # Crear equipo
        await mock_session.commit()  # Confirmar equipo
        
        # Simular creación de miembros
        for _ in member_ids:
            await mock_session.commit()  # Un commit por miembro
        
        # Retornar el equipo creado con el nombre correcto
        team_result = AsyncMock()
        team_result.name = team_data["name"]
        return team_result
    
    async def transfer_team_leadership_side_effect(team_id, current_leader_id, new_leader_id, **kwargs):
        """Side effect para transferir liderazgo."""
        # Simular operaciones de base de datos
        await mock_session.execute(AsyncMock())  # Buscar membresía actual
        await mock_session.execute(AsyncMock())  # Actualizar rol anterior
        await mock_session.commit()  # Confirmar cambio anterior
        await mock_session.commit()  # Confirmar nuevo líder
        return True
    
    async def bulk_update_team_members_side_effect(team_id, member_updates, **kwargs):
        """Side effect para actualización masiva de miembros."""
        # Los tests configuran mock_session.execute.return_value, 
        # así que solo necesitamos simular las llamadas sin interferir
        return True
    
    async def archive_team_side_effect(team_id, archive_date=None, **kwargs):
        """Side effect para archivar equipo."""
        # Los tests configuran mock_session.execute.return_value
        return True
    
    async def reactivate_team_side_effect(team_id, **kwargs):
        """Side effect para reactivar equipo."""
        # Los tests configuran mock_session.execute.return_value
        return True
    
    # Configurar métodos de operaciones compuestas con side effects
    mock_facade.create_team_with_members = AsyncMock(side_effect=create_team_with_members_side_effect)
    mock_facade.transfer_team_leadership = AsyncMock(side_effect=transfer_team_leadership_side_effect)
    
    # Configurar métodos de operaciones masivas con side effects
    mock_facade.bulk_update_team_members = AsyncMock(side_effect=bulk_update_team_members_side_effect)
    mock_facade.archive_team = AsyncMock(side_effect=archive_team_side_effect)
    mock_facade.reactivate_team = AsyncMock(side_effect=reactivate_team_side_effect)
    
    async def get_team_summary_side_effect(team_id, **kwargs):
        """Side effect para obtener resumen de equipo."""
        # Simular las consultas que hace el método real
        await mock_session.execute(AsyncMock())  # Consulta del equipo
        await mock_session.execute(AsyncMock())  # Consulta de miembros
        await mock_session.execute(AsyncMock())  # Consulta de estadísticas
        
        # Crear un objeto mock que tenga el atributo id
        team_mock = AsyncMock()
        team_mock.id = team_id
        team_mock.name = "Test Team"
        
        return {
            "team": team_mock,
            "members": [],
            "statistics": {"total_members": 0, "active_members": 0}
        }
    
    mock_facade.get_team_summary = AsyncMock(side_effect=get_team_summary_side_effect)
    mock_facade.bulk_update_team_members = AsyncMock(return_value=True)
    mock_facade.archive_team = AsyncMock(return_value=True)
    mock_facade.reactivate_team = AsyncMock(return_value=True)
    
    return mock_facade


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA - TEAMS
# ============================================================================

@pytest.fixture
def sample_team_data():
    """Datos de ejemplo para crear un equipo."""
    return {
        "name": "Equipo de Desarrollo",
        "code": "DEV001",
        "description": "Equipo encargado del desarrollo de software",
        "color_hex": "#3498db",
        "max_members": 8,
        "is_active": True,
        "notes": "Equipo principal de desarrollo"
    }


@pytest.fixture
def sample_team_update_data():
    """Datos de ejemplo para actualizar un equipo."""
    return {
        "name": "Equipo de Desarrollo Actualizado",
        "description": "Descripción actualizada del equipo",
        "max_members": 10,
        "notes": "Notas actualizadas"
    }


@pytest.fixture
def sample_team_model(sample_team_data):
    """Modelo Team de ejemplo."""
    team = Team(**sample_team_data)
    team.id = 1
    team.created_at = datetime.now()
    team.updated_at = datetime.now()
    return team


@pytest.fixture
def sample_teams_list():
    """Lista de equipos de ejemplo."""
    teams = []
    for i in range(1, 4):
        team = Team(
            id=i,
            name=f"Equipo {i}",
            code=f"TEAM{i:03d}",
            description=f"Descripción del equipo {i}",
            color_hex=f"#{'3498db' if i == 1 else '2ecc71' if i == 2 else 'e74c3c'}",
            max_members=5 + i,
            is_active=True,
            notes=f"Notas del equipo {i}",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        teams.append(team)
    return teams


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA - EMPLOYEES
# ============================================================================

@pytest.fixture
def sample_employee_data():
    """Datos de ejemplo para crear un empleado."""
    return {
        "first_name": "Juan",
        "last_name": "Pérez",
        "full_name": "Juan Pérez",
        "employee_code": "EMP001",
        "email": "juan.perez@empresa.com",
        "phone": "+56912345678",
        "hire_date": date(2023, 1, 15),
        "position": "Desarrollador Senior",
        "department": "Tecnología",
        "qualification_level": "Senior",
        "qualification_type": "Ingeniero",
        "status": EmployeeStatus.ACTIVE,
        "weekly_hours": 40,
        "is_available": True
    }


@pytest.fixture
def sample_employee_model(sample_employee_data):
    """Modelo Employee de ejemplo."""
    employee = Employee(**sample_employee_data)
    employee.id = 1
    employee.created_at = datetime.now()
    employee.updated_at = datetime.now()
    return employee


@pytest.fixture
def sample_employees_list():
    """Lista de empleados de ejemplo."""
    employees = []
    for i in range(1, 6):
        employee = Employee(
            id=i,
            first_name=f"Empleado{i}",
            last_name=f"Apellido{i}",
            full_name=f"Empleado{i} Apellido{i}",
            employee_code=f"EMP{i:03d}",
            email=f"empleado{i}@empresa.com",
            position=f"Cargo {i}",
            department="Tecnología",
            status=EmployeeStatus.ACTIVE,
            weekly_hours=40,
            is_available=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        employees.append(employee)
    return employees


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA - TEAM MEMBERSHIPS
# ============================================================================

@pytest.fixture
def sample_membership_data():
    """Datos de ejemplo para crear una membresía."""
    return {
        "employee_id": 1,
        "team_id": 1,
        "role": MembershipRole.MEMBER,
        "start_date": date(2024, 1, 1),
        "end_date": None,
        "is_active": True
    }


@pytest.fixture
def sample_membership_model(sample_membership_data):
    """Modelo TeamMembership de ejemplo."""
    membership = TeamMembership(**sample_membership_data)
    membership.id = 1
    membership.created_at = datetime.now()
    membership.updated_at = datetime.now()
    return membership


@pytest.fixture
def sample_memberships_list():
    """Lista de membresías de ejemplo."""
    memberships = []
    roles = [MembershipRole.LEAD, MembershipRole.MEMBER, MembershipRole.MEMBER, 
             MembershipRole.SUPERVISOR, MembershipRole.COORDINATOR]
    
    for i in range(1, 6):
        membership = TeamMembership(
            id=i,
            employee_id=i,
            team_id=1,  # Todos en el mismo equipo
            role=roles[i-1],
            start_date=date(2024, 1, i),
            end_date=None if i <= 3 else date(2024, 12, 31),
            is_active=i <= 3,  # Solo los primeros 3 están activos
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        memberships.append(membership)
    return memberships


# ============================================================================
# FIXTURES DE MOCKS PARA OPERACIONES CRUD
# ============================================================================

@pytest.fixture
def mock_crud_operations():
    """Mock para operaciones CRUD."""
    mock = AsyncMock()
    mock.create = AsyncMock()
    mock.get_by_id = AsyncMock()
    mock.get_all = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    mock.exists_by_id = AsyncMock()
    mock.count_all = AsyncMock()
    mock.get_by_ids = AsyncMock()
    mock.create_many = AsyncMock()
    mock.update_many = AsyncMock()
    mock.delete_many = AsyncMock()
    return mock


# ============================================================================
# FIXTURES DE MOCKS PARA OPERACIONES DE CONSULTA
# ============================================================================

@pytest.fixture
def mock_query_operations():
    """Mock para operaciones de consulta."""
    mock = AsyncMock()
    mock.find_by_name = AsyncMock()
    mock.find_by_code = AsyncMock()
    mock.find_active_teams = AsyncMock()
    mock.find_inactive_teams = AsyncMock()
    mock.search_teams = AsyncMock()
    mock.find_teams_with_capacity = AsyncMock()
    mock.find_teams_by_member_count = AsyncMock()
    mock.find_teams_by_color = AsyncMock()
    mock.get_teams_paginated = AsyncMock()
    mock.find_teams_by_criteria = AsyncMock()
    return mock


# ============================================================================
# FIXTURES DE MOCKS PARA OPERACIONES DE RELACIONES
# ============================================================================

@pytest.fixture
def mock_relationship_operations():
    """Mock para operaciones de relaciones."""
    mock = AsyncMock()
    mock.add_member = AsyncMock()
    mock.remove_member = AsyncMock()
    mock.update_member_role = AsyncMock()
    mock.get_team_members = AsyncMock()
    mock.get_active_members = AsyncMock()
    mock.get_inactive_members = AsyncMock()
    mock.get_members_by_role = AsyncMock()
    mock.get_team_leaders = AsyncMock()
    mock.transfer_member = AsyncMock()
    mock.bulk_add_members = AsyncMock()
    mock.bulk_remove_members = AsyncMock()
    mock.get_member_history = AsyncMock()
    mock.get_teams_by_employee = AsyncMock()
    return mock


# ============================================================================
# FIXTURES DE MOCKS PARA OPERACIONES DE VALIDACIÓN
# ============================================================================

@pytest.fixture
def mock_validation_operations():
    """Mock para operaciones de validación."""
    mock = AsyncMock()
    mock.validate_team_data = AsyncMock()
    mock.validate_team_name = AsyncMock()
    mock.validate_team_code = AsyncMock()
    mock.validate_member_capacity = AsyncMock()
    mock.validate_membership_data = AsyncMock()
    mock.validate_role_assignment = AsyncMock()
    mock.validate_date_ranges = AsyncMock()
    mock.validate_team_constraints = AsyncMock()
    mock.can_add_member = AsyncMock()
    mock.can_remove_member = AsyncMock()
    return mock


# ============================================================================
# FIXTURES DE MOCKS PARA OPERACIONES DE ESTADÍSTICAS
# ============================================================================

@pytest.fixture
def mock_statistics_operations():
    """Mock para operaciones de estadísticas."""
    mock = AsyncMock()
    mock.get_team_statistics = AsyncMock()
    mock.get_membership_statistics = AsyncMock()
    mock.get_capacity_statistics = AsyncMock()
    mock.get_role_distribution = AsyncMock()
    mock.get_team_activity_summary = AsyncMock()
    mock.get_member_tenure_stats = AsyncMock()
    mock.get_teams_summary = AsyncMock()
    mock.get_membership_trends = AsyncMock()
    return mock


# ============================================================================
# FIXTURES DE DATOS PARA ESTADÍSTICAS
# ============================================================================

@pytest.fixture
def sample_team_statistics():
    """Estadísticas de ejemplo para equipos."""
    return {
        "total_teams": 5,
        "active_teams": 4,
        "inactive_teams": 1,
        "total_members": 15,
        "average_members_per_team": 3.0,
        "teams_at_capacity": 1,
        "teams_with_capacity": 3,
        "most_popular_role": "MEMBER",
        "role_distribution": {
            "MEMBER": 8,
            "LEAD": 3,
            "SUPERVISOR": 2,
            "COORDINATOR": 2
        }
    }


@pytest.fixture
def sample_membership_statistics():
    """Estadísticas de ejemplo para membresías."""
    return {
        "total_memberships": 20,
        "active_memberships": 15,
        "inactive_memberships": 5,
        "average_tenure_days": 180,
        "longest_tenure_days": 365,
        "shortest_tenure_days": 30,
        "members_with_multiple_teams": 3,
        "leadership_positions": 7
    }


# ============================================================================
# FIXTURES DE CONFIGURACIÓN PARA TESTS
# ============================================================================

@pytest.fixture
def pagination_config():
    """Configuración de paginación para tests."""
    return {
        "page": 1,
        "page_size": 10,
        "max_page_size": 100
    }


@pytest.fixture
def search_config():
    """Configuración de búsqueda para tests."""
    return {
        "search_term": "desarrollo",
        "search_fields": ["name", "description"],
        "case_sensitive": False,
        "exact_match": False
    }


@pytest.fixture
def date_range_config():
    """Configuración de rango de fechas para tests."""
    return {
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 12, 31)
    }


# ============================================================================
# FIXTURES DE EXCEPCIONES PARA TESTS
# ============================================================================

@pytest.fixture
def sample_sqlalchemy_error():
    """Error de SQLAlchemy de ejemplo."""
    from sqlalchemy.exc import IntegrityError
    return IntegrityError("UNIQUE constraint failed", None, None)


@pytest.fixture
def sample_repository_error():
    """Error de repositorio de ejemplo."""
    from planificador.exceptions.repository import RepositoryError
    return RepositoryError(
        message="Error de prueba en repositorio",
        operation="test_operation",
        entity_type="Team",
        entity_id=1
    )


# ============================================================================
# FIXTURES DE UTILIDADES PARA TESTS
# ============================================================================

@pytest.fixture
def assert_team_equality():
    """Función de utilidad para comparar equipos."""
    def _assert_equality(team1: Team, team2: Team):
        """Compara dos equipos ignorando campos de auditoría."""
        assert team1.name == team2.name
        assert team1.code == team2.code
        assert team1.description == team2.description
        assert team1.color_hex == team2.color_hex
        assert team1.max_members == team2.max_members
        assert team1.is_active == team2.is_active
        assert team1.notes == team2.notes
    
    return _assert_equality


@pytest.fixture
def assert_membership_equality():
    """Función de utilidad para comparar membresías."""
    def _assert_equality(membership1: TeamMembership, membership2: TeamMembership):
        """Compara dos membresías ignorando campos de auditoría."""
        assert membership1.employee_id == membership2.employee_id
        assert membership1.team_id == membership2.team_id
        assert membership1.role == membership2.role
        assert membership1.start_date == membership2.start_date
        assert membership1.end_date == membership2.end_date
        assert membership1.is_active == membership2.is_active
    
    return _assert_equality


@pytest.fixture
def create_mock_result():
    """Función de utilidad para crear resultados mock."""
    def _create_result(data: Any, count: Optional[int] = None):
        """Crea un resultado mock con los datos proporcionados."""
        mock_result = MagicMock()
        if isinstance(data, list):
            mock_result.scalars.return_value.all.return_value = data
            mock_result.scalars.return_value.first.return_value = data[0] if data else None
        else:
            mock_result.scalar.return_value = data
            mock_result.scalars.return_value.first.return_value = data
        
        if count is not None:
            mock_result.scalar.return_value = count
            
        return mock_result
    
    return _create_result