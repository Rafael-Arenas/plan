"""Fixtures específicas para base de datos y modelos."""

import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
import uuid

from planificador.models.client import Client
from planificador.models.employee import Employee, EmployeeStatus
from planificador.models.project import Project, ProjectStatus, ProjectPriority
from planificador.models.team import Team
from planificador.models.schedule import Schedule
from planificador.models.workload import Workload
from planificador.models.status_code import StatusCode
from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.models.project_assignment import ProjectAssignment
from planificador.models.alert import Alert, AlertType, AlertStatus
from planificador.models.base import BaseModel
from sqlalchemy import Column, String, Integer


def generate_unique_code(prefix: str = "TEST") -> str:
    """Genera un código único para testing."""
    return f"{prefix}-{str(uuid.uuid4())[:8].upper()}"


@pytest.fixture
async def sample_client(test_session: AsyncSession) -> Client:
    """Fixture que crea un cliente de prueba.
    
    Args:
        test_session: Sesión de base de datos de testing
        
    Returns:
        Client: Cliente creado para testing
    """
    unique_id = str(uuid.uuid4())[:8].upper()
    client = Client(
        name=f"Test Client {unique_id}",
        code=generate_unique_code("TC"),
        contact_person="John Doe",
        email=f"contact-{unique_id.lower()}@testclient.com",
        phone="+1234567890",
        is_active=True,
        notes="Cliente de prueba para testing"
    )
    
    test_session.add(client)
    await test_session.flush()
    await test_session.refresh(client)
    
    return client


@pytest.fixture
async def sample_employee(test_session: AsyncSession) -> Employee:
    """Fixture que crea un empleado de prueba.
    
    Args:
        test_session: Sesión de base de datos de testing
        
    Returns:
        Employee: Empleado creado para testing
    """
    unique_id = str(uuid.uuid4())[:8].upper()
    employee = Employee(
        first_name="John",
        last_name=f"Doe-{unique_id}",
        email=f"john.doe-{unique_id.lower()}@company.com",
        phone="+1234567890",
        hire_date=date(2024, 1, 15),
        status=EmployeeStatus.ACTIVE,
        hourly_rate=25.50,
        notes="Empleado de prueba para testing"
    )
    
    test_session.add(employee)
    await test_session.flush()
    await test_session.refresh(employee)
    
    return employee


@pytest.fixture
async def sample_team(test_session: AsyncSession) -> Team:
    """Fixture que crea un equipo de prueba.
    
    Args:
        test_session: Sesión de base de datos de testing
        
    Returns:
        Team: Equipo creado para testing
    """
    team = Team(
        name="Development Team",
        description="Equipo de desarrollo para testing",
        is_active=True
    )
    
    test_session.add(team)
    await test_session.flush()
    await test_session.refresh(team)
    
    return team


@pytest.fixture
async def sample_project(
    test_session: AsyncSession,
    sample_client: Client
) -> Project:
    """Fixture que crea un proyecto de prueba.
    
    Args:
        test_session: Sesión de base de datos de testing
        sample_client: Cliente de prueba
        
    Returns:
        Project: Proyecto creado para testing
    """
    unique_id = str(uuid.uuid4())[:8].upper()
    project = Project(
        reference=generate_unique_code("PROJ"),
        trigram=f"TRG{unique_id[:5]}",
        name="Test Project",
        details="Proyecto de prueba para testing",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        status=ProjectStatus.IN_PROGRESS,
        priority=ProjectPriority.MEDIUM,
        client_id=sample_client.id
    )
    
    test_session.add(project)
    await test_session.flush()
    await test_session.refresh(project)
    
    return project


@pytest.fixture
async def sample_schedule(
    test_session: AsyncSession,
    sample_employee: Employee,
    sample_project: Project
) -> Schedule:
    """Fixture que crea un horario de prueba.
    
    Args:
        test_session: Sesión de base de datos de testing
        sample_employee: Empleado de prueba
        sample_project: Proyecto de prueba
        
    Returns:
        Schedule: Horario creado para testing
    """
    from datetime import time
    
    schedule = Schedule(
        employee_id=sample_employee.id,
        project_id=sample_project.id,
        date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(17, 0),
        description="Horario de prueba para testing",
        is_confirmed=True
    )
    
    test_session.add(schedule)
    await test_session.commit()
    await test_session.refresh(schedule)
    
    return schedule


@pytest.fixture
async def multiple_employees(test_session: AsyncSession) -> list[Employee]:
    """Fixture que crea múltiples empleados de prueba.
    
    Args:
        test_session: Sesión de base de datos de testing
        
    Returns:
        list[Employee]: Lista de empleados creados para testing
    """
    unique_id = str(uuid.uuid4())[:8].upper()
    employees = [
        Employee(
            first_name=f"Employee{i}",
            last_name=f"Test{i}-{unique_id}",
            email=f"employee{i}-{unique_id.lower()}@company.com",
            phone=f"+123456789{i}",
            hire_date=date(2024, 1, i),
            status=EmployeeStatus.ACTIVE,
            hourly_rate=20.00 + i * 5.0,
            notes=f"Empleado {i} de prueba para testing"
        )
        for i in range(1, 4)
    ]
    
    for employee in employees:
        test_session.add(employee)
    
    await test_session.flush()
    
    for employee in employees:
        await test_session.refresh(employee)
    
    return employees


@pytest.fixture
async def project_with_different_statuses(
    test_session: AsyncSession,
    sample_client: Client
) -> list[Project]:
    """Fixture que crea proyectos con diferentes estados.
    
    Args:
        test_session: Sesión de base de datos de testing
        sample_client: Cliente de prueba
        
    Returns:
        list[Project]: Lista de proyectos con diferentes estados
    """
    unique_id = str(uuid.uuid4())[:8].upper()
    projects = [
        Project(
            name="Active Project",
            details="Proyecto activo para testing",
            reference=f"REF-001-{unique_id}",
            trigram=f"AC{unique_id[:1]}",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.HIGH,
            client_id=sample_client.id,

        ),
        Project(
            name="Completed Project",
            details="Proyecto completado para testing",
            reference=f"REF-002-{unique_id}",
            trigram=f"CM{unique_id[:1]}",
            start_date=date(2023, 6, 1),
            end_date=date(2023, 12, 31),
            status=ProjectStatus.COMPLETED,
            priority=ProjectPriority.MEDIUM,
            client_id=sample_client.id,

        ),
        Project(
            name="Planned Project",
            details="Proyecto planificado para testing",
            reference=f"REF-003-{unique_id}",
            trigram=f"PL{unique_id[:1]}",
            start_date=date(2024, 7, 1),
            end_date=date(2024, 12, 31),
            status=ProjectStatus.PLANNED,
            priority=ProjectPriority.LOW,
            client_id=sample_client.id,

        ),
        Project(
            name="On Hold Project",
            details="Proyecto en pausa para testing",
            reference=f"REF-004-{unique_id}",
            trigram=f"HL{unique_id[:1]}",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 8, 31),
            status=ProjectStatus.ON_HOLD,
            priority=ProjectPriority.MEDIUM,
            client_id=sample_client.id,

        ),
        Project(
            name="Cancelled Project",
            details="Proyecto cancelado para testing",
            reference=f"REF-005-{unique_id}",
            trigram=f"CA{unique_id[:1]}",
            start_date=date(2024, 3, 1),
            end_date=date(2024, 9, 30),
            status=ProjectStatus.CANCELLED,
            priority=ProjectPriority.LOW,
            client_id=sample_client.id,

        )
    ]
    
    for project in projects:
        test_session.add(project)
    
    await test_session.flush()
    
    for project in projects:
        await test_session.refresh(project)
    
    return projects


@pytest.fixture
async def project_with_different_priorities(
    test_session: AsyncSession,
    sample_client: Client
) -> list[Project]:
    """Fixture que crea proyectos con diferentes prioridades.
    
    Args:
        test_session: Sesión de base de datos de testing
        sample_client: Cliente de prueba
        
    Returns:
        list[Project]: Lista de proyectos con diferentes prioridades
    """
    projects = [
        Project(
            name="High Priority Project",
            details="Proyecto de alta prioridad",
            reference="PRI-001",
            trigram="HIG",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31),
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.HIGH,
            client_id=sample_client.id,

        ),
        Project(
            name="Medium Priority Project",
            details="Proyecto de prioridad media",
            reference="PRI-002",
            trigram="MED",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 5, 31),
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.MEDIUM,
            client_id=sample_client.id,

        ),
        Project(
            name="Low Priority Project",
            details="Proyecto de baja prioridad",
            reference="PRI-003",
            trigram="LOW",
            start_date=date(2024, 3, 1),
            end_date=date(2024, 8, 31),
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.LOW,
            client_id=sample_client.id,

        )
    ]
    
    for project in projects:
        test_session.add(project)
    
    await test_session.flush()
    
    for project in projects:
        await test_session.refresh(project)
    
    return projects


@pytest.fixture
async def team_with_members(
    test_session: AsyncSession,
    multiple_employees: list[Employee]
) -> Team:
    """Fixture que crea un equipo con miembros.
    
    Args:
        test_session: Sesión de base de datos de testing
        multiple_employees: Lista de empleados de prueba
        
    Returns:
        Team: Equipo con miembros para testing
    """
    from planificador.models.team_membership import TeamMembership
    
    team = Team(
        name="Full Development Team",
        description="Equipo completo de desarrollo con miembros",
        is_active=True
    )
    
    test_session.add(team)
    await test_session.flush()  # Para obtener el ID del equipo
    
    # Agregar miembros al equipo
    from planificador.models.team_membership import MembershipRole
    from datetime import date
    
    for i, employee in enumerate(multiple_employees):
        # Asignar roles diferentes según el índice
        roles = [MembershipRole.LEAD, MembershipRole.MEMBER, MembershipRole.COORDINATOR]
        role = roles[i % len(roles)]
        
        membership = TeamMembership(
            team_id=team.id,
            employee_id=employee.id,
            role=role,
            start_date=date.today(),
            is_active=True
        )
        test_session.add(membership)
    
    await test_session.flush()
    await test_session.refresh(team)
    
    return team


@pytest.fixture
async def multiple_teams(test_session: AsyncSession) -> list[Team]:
    """Fixture que crea múltiples equipos de prueba.
    
    Args:
        test_session: Sesión de base de datos de testing
        
    Returns:
        list[Team]: Lista de equipos creados para testing
    """
    teams = [
        Team(
            name="Frontend Team",
            description="Equipo especializado en desarrollo frontend",
            is_active=True
        ),
        Team(
            name="Backend Team",
            description="Equipo especializado en desarrollo backend",
            is_active=True
        ),
        Team(
            name="QA Team",
            description="Equipo de aseguramiento de calidad",
            is_active=True
        ),
        Team(
            name="Inactive Team",
            description="Equipo inactivo para testing",
            is_active=False
        )
    ]
    
    for team in teams:
        test_session.add(team)
    
    await test_session.flush()
    
    for team in teams:
        await test_session.refresh(team)
    
    return teams


@pytest.fixture
async def project_with_long_duration(
    test_session: AsyncSession,
    sample_client: Client
) -> Project:
    """Fixture que crea un proyecto con duración larga para testing de propiedades calculadas.
    
    Args:
        test_session: Sesión de base de datos de testing
        sample_client: Cliente de prueba
        
    Returns:
        Project: Proyecto con duración larga
    """
    project = Project(
        name="Long Duration Project",
        details="Proyecto de larga duración para testing",
        reference="LONG-001",
        trigram="LNG",
        start_date=date(2024, 1, 1),
        end_date=date(2025, 12, 31),  # 2 años de duración
        duration_days=730,  # 2 años aproximadamente
        status=ProjectStatus.IN_PROGRESS,
        priority=ProjectPriority.HIGH,
        client_id=sample_client.id,

    )
    
    test_session.add(project)
    await test_session.flush()
    await test_session.refresh(project)
    
    return project


@pytest.fixture
async def sample_workload(
    test_session: AsyncSession,
    sample_employee: Employee,
    sample_project: Project
) -> Workload:
    """Fixture que crea una carga de trabajo de prueba.
    
    Args:
        test_session: Sesión de base de datos de testing
        sample_employee: Empleado de prueba
        sample_project: Proyecto de prueba
        
    Returns:
        Workload: Carga de trabajo creada para testing
    """
    from decimal import Decimal
    
    workload = Workload(
        employee_id=sample_employee.id,
        project_id=sample_project.id,
        date=date(2024, 1, 15),
        week_number=3,
        month=1,
        year=2024,
        planned_hours=Decimal('8.0'),
        actual_hours=Decimal('7.5'),
        utilization_percentage=Decimal('93.75'),
        efficiency_score=Decimal('95.0'),
        productivity_index=Decimal('88.5'),
        is_billable=True,
        notes="Trabajo completado según planificación"
    )
    
    test_session.add(workload)
    await test_session.flush()
    await test_session.refresh(workload)
    
    return workload


@pytest.fixture
async def clean_database(test_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Fixture que proporciona una base de datos limpia.
    
    Útil para tests que necesitan empezar con una base de datos vacía.
    
    Args:
        test_session: Sesión de base de datos de testing
        
    Yields:
        AsyncSession: Sesión de base de datos limpia
    """
    # La sesión ya está limpia por el rollback automático en conftest.py
    yield test_session


# Fixtures para StatusCode
@pytest.fixture
async def sample_status_code_data():
    """Datos de ejemplo para crear un código de estado.
    
    Returns:
        dict: Diccionario con datos de ejemplo para StatusCode
    """
    return {
        "code": "DEV",
        "name": "Desarrollo",
        "description": "Tiempo dedicado al desarrollo de software",
        "color": "#007bff",
        "icon": "code",
        "is_billable": True,
        "is_productive": True,
        "requires_approval": False,
        "is_active": True,
        "sort_order": 10
    }


@pytest.fixture
async def status_code_instance(test_session: AsyncSession) -> StatusCode:
    """Fixture que crea un código de estado en la base de datos.
    
    Args:
        test_session: Sesión de base de datos de testing
        
    Returns:
        StatusCode: Código de estado creado para testing
    """
    unique_id = str(uuid.uuid4())[:8]
    status_code = StatusCode(
        code=f"TST{unique_id[:5].upper()}",
        name=f"Test Status {unique_id}",
        description="Código de estado de prueba",
        color="#28a745",
        icon="test",
        is_billable=True,
        is_productive=True,
        requires_approval=False,
        is_active=True,
        sort_order=5
    )
    test_session.add(status_code)
    await test_session.flush()
    await test_session.refresh(status_code)
    return status_code


# Fixtures para TeamMembership
@pytest.fixture
async def sample_membership_data(sample_employee: Employee, sample_team: Team):
    """Datos de ejemplo para crear una membresía.
    
    Args:
        sample_employee: Empleado de ejemplo
        sample_team: Equipo de ejemplo
        
    Returns:
        dict: Diccionario con datos de ejemplo para TeamMembership
    """
    return {
        "employee_id": sample_employee.id,
        "team_id": sample_team.id,
        "role": MembershipRole.MEMBER,
        "start_date": date(2024, 1, 15),
        "end_date": date(2024, 12, 31),
        "is_active": True
    }


@pytest.fixture
async def membership_instance(
    test_session: AsyncSession,
    sample_employee: Employee,
    sample_team: Team
) -> TeamMembership:
    """Fixture que crea una membresía en la base de datos.
    
    Args:
        test_session: Sesión de base de datos de testing
        sample_employee: Empleado de ejemplo
        sample_team: Equipo de ejemplo
        
    Returns:
        TeamMembership: Membresía creada para testing
    """
    membership = TeamMembership(
        employee_id=sample_employee.id,
        team_id=sample_team.id,
        role=MembershipRole.MEMBER,
        start_date=date(2024, 1, 15),
        is_active=True
    )
    test_session.add(membership)
    await test_session.flush()
    await test_session.refresh(membership)
    return membership


# Fixtures para ProjectAssignment
@pytest.fixture
async def sample_project_assignment_data(
    sample_employee: Employee,
    sample_project: Project
):
    """Datos de ejemplo para crear una asignación de proyecto.
    
    Args:
        sample_employee: Empleado de ejemplo
        sample_project: Proyecto de ejemplo
        
    Returns:
        dict: Diccionario con datos de ejemplo para ProjectAssignment
    """
    from decimal import Decimal
    
    return {
        "employee_id": sample_employee.id,
        "project_id": sample_project.id,
        "start_date": date(2024, 1, 15),
        "end_date": date(2024, 6, 30),
        "allocated_hours_per_day": Decimal('8.0'),
        "percentage_allocation": Decimal('100.0'),
        "role_in_project": "Desarrollador Senior",
        "is_active": True,
        "notes": "Asignación principal del proyecto"
    }


@pytest.fixture
async def sample_project_assignment(
    test_session: AsyncSession,
    sample_employee: Employee,
    sample_project: Project
) -> ProjectAssignment:
    """Fixture que crea una asignación de proyecto en la base de datos.
    
    Args:
        test_session: Sesión de base de datos de testing
        sample_employee: Empleado de ejemplo
        sample_project: Proyecto de ejemplo
        
    Returns:
        ProjectAssignment: Asignación de proyecto creada para testing
    """
    from decimal import Decimal
    
    assignment = ProjectAssignment(
        employee_id=sample_employee.id,
        project_id=sample_project.id,
        start_date=date(2024, 1, 15),
        end_date=date(2024, 6, 30),
        allocated_hours_per_day=Decimal('8.0'),
        percentage_allocation=Decimal('100.0'),
        role_in_project="Desarrollador Senior",
        is_active=True,
        notes="Asignación principal del proyecto"
    )
    
    test_session.add(assignment)
    await test_session.flush()
    await test_session.refresh(assignment)
    return assignment


@pytest.fixture
async def multiple_project_assignments(
    test_session: AsyncSession,
    multiple_employees: list[Employee],
    sample_project: Project
) -> list[ProjectAssignment]:
    """Fixture que crea múltiples asignaciones de proyecto.
    
    Args:
        test_session: Sesión de base de datos de testing
        multiple_employees: Lista de empleados de ejemplo
        sample_project: Proyecto de ejemplo
        
    Returns:
        list[ProjectAssignment]: Lista de asignaciones creadas para testing
    """
    from decimal import Decimal
    
    assignments = []
    roles = ["Desarrollador Senior", "Desarrollador Junior", "Analista"]
    allocations = [Decimal('100.0'), Decimal('75.0'), Decimal('50.0')]
    hours = [Decimal('8.0'), Decimal('6.0'), Decimal('4.0')]
    
    for i, employee in enumerate(multiple_employees):
        assignment = ProjectAssignment(
            employee_id=employee.id,
            project_id=sample_project.id,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 6, 30),
            allocated_hours_per_day=hours[i % len(hours)],
            percentage_allocation=allocations[i % len(allocations)],
            role_in_project=roles[i % len(roles)],
            is_active=True,
            notes=f"Asignación {i+1} del proyecto"
        )
        assignments.append(assignment)
        test_session.add(assignment)
    
    await test_session.flush()
    
    for assignment in assignments:
        await test_session.refresh(assignment)
    
    return assignments


@pytest.fixture
async def sample_alert(test_session: AsyncSession, sample_employee: Employee) -> Alert:
    """Fixture que crea una alerta de prueba."""
    alert = Alert(
        user_id=sample_employee.id,
        alert_type=AlertType.TASK_OVERDUE,
        status=AlertStatus.ACTIVE,
        title="Tarea Vencida",
        message="La tarea 'Desarrollo de módulo' ha vencido y requiere atención inmediata.",
        related_entity_type="Task",
        related_entity_id=str(uuid.uuid4()),
        is_read=False
    )
    
    test_session.add(alert)
    await test_session.flush()
    await test_session.refresh(alert)
    
    return alert


# ============================================================================
# FIXTURES PARA BASEMODEL
# ============================================================================

# Modelo concreto para testing de BaseModel
class SampleModel(BaseModel):
    """Modelo concreto para testing de BaseModel."""
    __tablename__ = 'sample_models'
    
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    value = Column(Integer, nullable=True)


@pytest.fixture
async def sample_test_model_data() -> dict:
    """Datos de ejemplo para crear un SampleModel.
    
    Returns:
        dict: Diccionario con datos de prueba
    """
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "name": f"Test Model {unique_id}",
        "description": f"Descripción de prueba {unique_id}",
        "value": 42
    }


@pytest.fixture
async def sample_test_model(test_session: AsyncSession, sample_test_model_data: dict) -> SampleModel:
    """Fixture que crea un SampleModel de prueba.
    
    Args:
        test_session: Sesión de base de datos de testing
        sample_test_model_data: Datos de prueba
        
    Returns:
        SampleModel: Modelo creado para testing
    """
    model = SampleModel(**sample_test_model_data)
    
    test_session.add(model)
    await test_session.flush()
    await test_session.refresh(model)
    
    return model


@pytest.fixture
async def old_test_model(test_session: AsyncSession) -> SampleModel:
    """Fixture que crea un SampleModel antiguo (creado hace más de 7 días).
    
    Args:
        test_session: Sesión de base de datos de testing
        
    Returns:
        SampleModel: Modelo antiguo para testing
    """
    from datetime import timedelta
    
    unique_id = str(uuid.uuid4())[:8].upper()
    old_date = datetime.now() - timedelta(days=10)
    
    model = SampleModel(
        name=f"Old Test Model {unique_id}",
        description="Modelo antiguo para testing",
        value=100
    )
    
    test_session.add(model)
    await test_session.flush()
    
    # Simular fecha de creación antigua
    model.created_at = old_date
    model.updated_at = old_date
    
    await test_session.flush()
    await test_session.refresh(model)
    
    return model


@pytest.fixture
async def recently_modified_test_model(test_session: AsyncSession) -> SampleModel:
    """Fixture que crea un SampleModel recientemente modificado.
    
    Args:
        test_session: Sesión de base de datos de testing
        
    Returns:
        SampleModel: Modelo recientemente modificado para testing
    """
    from datetime import timedelta
    
    unique_id = str(uuid.uuid4())[:8].upper()
    old_date = datetime.now() - timedelta(days=5)
    recent_date = datetime.now() - timedelta(hours=2)
    
    model = SampleModel(
        name=f"Modified Test Model {unique_id}",
        description="Modelo modificado recientemente",
        value=200
    )
    
    test_session.add(model)
    await test_session.flush()
    
    # Simular fechas de creación y modificación
    model.created_at = old_date
    model.updated_at = recent_date
    
    await test_session.flush()
    await test_session.refresh(model)
    
    return model


@pytest.fixture
async def multiple_test_models(test_session: AsyncSession) -> list[SampleModel]:
    """Fixture que crea múltiples SampleModels para testing.
    
    Args:
        test_session: Sesión de base de datos de testing
        
    Returns:
        list[SampleModel]: Lista de modelos para testing
    """
    from datetime import timedelta
    
    models = []
    base_date = datetime.now()
    
    for i in range(3):
        unique_id = str(uuid.uuid4())[:8].upper()
        creation_date = base_date - timedelta(days=i)
        
        model = SampleModel(
            name=f"Test Model {i+1} {unique_id}",
            description=f"Descripción del modelo {i+1}",
            value=(i+1) * 10
        )
        
        test_session.add(model)
        await test_session.flush()
        
        # Simular diferentes fechas de creación
        model.created_at = creation_date
        model.updated_at = creation_date
        
        models.append(model)
    
    await test_session.flush()
    
    for model in models:
        await test_session.refresh(model)
    
    return models


@pytest.fixture
async def assignment_with_different_statuses(
    test_session: AsyncSession,
    sample_employee: Employee,
    project_with_different_statuses: list[Project]
) -> list[ProjectAssignment]:
    """Fixture que crea asignaciones con diferentes estados temporales.
    
    Args:
        test_session: Sesión de base de datos de testing
        sample_employee: Empleado de ejemplo
        project_with_different_statuses: Lista de proyectos con diferentes estados
        
    Returns:
        list[ProjectAssignment]: Lista de asignaciones con diferentes estados
    """
    from decimal import Decimal
    
    assignments = [
        # Asignación pasada
        ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=project_with_different_statuses[0].id,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            allocated_hours_per_day=Decimal('8.0'),
            percentage_allocation=Decimal('100.0'),
            role_in_project="Desarrollador",
            is_active=True,
            notes="Asignación pasada"
        ),
        # Asignación actual
        ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=project_with_different_statuses[1].id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            allocated_hours_per_day=Decimal('6.0'),
            percentage_allocation=Decimal('75.0'),
            role_in_project="Analista",
            is_active=True,
            notes="Asignación actual"
        ),
        # Asignación futura
        ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=project_with_different_statuses[2].id,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            allocated_hours_per_day=Decimal('4.0'),
            percentage_allocation=Decimal('50.0'),
            role_in_project="Consultor",
            is_active=True,
            notes="Asignación futura"
        ),
        # Asignación indefinida (sin fecha de fin)
        ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=project_with_different_statuses[3].id,
            start_date=date(2024, 6, 1),
            end_date=None,
            allocated_hours_per_day=Decimal('2.0'),
            percentage_allocation=Decimal('25.0'),
            role_in_project="Soporte",
            is_active=True,
            notes="Asignación indefinida"
        ),
        # Asignación inactiva
        ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=project_with_different_statuses[4].id,
            start_date=date(2024, 3, 1),
            end_date=date(2024, 9, 30),
            allocated_hours_per_day=Decimal('8.0'),
            percentage_allocation=Decimal('100.0'),
            role_in_project="Desarrollador",
            is_active=False,
            notes="Asignación inactiva"
        )
    ]
    
    for assignment in assignments:
        test_session.add(assignment)
    
    await test_session.flush()
    
    for assignment in assignments:
        await test_session.refresh(assignment)
    
    return assignments


@pytest.fixture
async def overlapping_assignments(
    test_session: AsyncSession,
    sample_employee: Employee,
    multiple_teams: list[Team]
) -> list[ProjectAssignment]:
    """Fixture que crea asignaciones que se superponen en el tiempo.
    
    Args:
        test_session: Sesión de base de datos de testing
        sample_employee: Empleado de ejemplo
        multiple_teams: Lista de equipos para crear proyectos
        
    Returns:
        list[ProjectAssignment]: Lista de asignaciones superpuestas
    """
    from decimal import Decimal
    
    # Crear proyectos temporales para las asignaciones superpuestas
    projects = []
    for i, team in enumerate(multiple_teams[:2]):
        project = Project(
            name=f"Overlap Project {i+1}",
            details=f"Proyecto {i+1} para testing de superposición",
            reference=f"OVL-{i+1:03d}",
            trigram=f"OV{i+1}",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.MEDIUM,
            client_id=1  # Asumiendo que existe un cliente con ID 1
        )
        projects.append(project)
        test_session.add(project)
    
    await test_session.flush()
    
    assignments = [
        # Primera asignación: Enero - Junio
        ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=projects[0].id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            allocated_hours_per_day=Decimal('4.0'),
            percentage_allocation=Decimal('50.0'),
            role_in_project="Desarrollador",
            is_active=True,
            notes="Primera asignación superpuesta"
        ),
        # Segunda asignación: Abril - Septiembre (se superpone con la primera)
        ProjectAssignment(
            employee_id=sample_employee.id,
            project_id=projects[1].id,
            start_date=date(2024, 4, 1),
            end_date=date(2024, 9, 30),
            allocated_hours_per_day=Decimal('4.0'),
            percentage_allocation=Decimal('50.0'),
            role_in_project="Analista",
            is_active=True,
            notes="Segunda asignación superpuesta"
        )
    ]
    
    for assignment in assignments:
        test_session.add(assignment)
    
    await test_session.flush()
    
    for assignment in assignments:
        await test_session.refresh(assignment)
    
    return assignments