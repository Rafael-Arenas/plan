"""Tests para relaciones entre modelos.

Este módulo contiene tests específicos para validar las relaciones
entre diferentes modelos del sistema, incluyendo foreign keys,
backrefs y propiedades de navegación.
"""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from planificador.models.client import Client
from planificador.models.employee import Employee, EmployeeStatus
from planificador.models.team import Team
from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.models.project import Project, ProjectStatus, ProjectPriority
from planificador.models.workload import Workload
from planificador.models.schedule import Schedule


class TestClientProjectRelationship:
    """Tests para la relación Client-Project."""
    
    @pytest.mark.asyncio
    async def test_client_projects_relationship(
        self,
        test_session: AsyncSession,
        sample_client: Client
    ):
        """Test que valida la relación uno-a-muchos entre Client y Project."""
        # Crear proyectos asociados al cliente
        project1 = Project(
            name="Project 1",
            details="Primer proyecto del cliente",
            reference="REF-001",
            trigram="PR1",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.HIGH,
            client_id=sample_client.id
        )
        
        project2 = Project(
            name="Project 2",
            details="Segundo proyecto del cliente",
            reference="REF-002",
            trigram="PR2",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 8, 31),
            status=ProjectStatus.PLANNED,
            priority=ProjectPriority.MEDIUM,
            client_id=sample_client.id
        )
        
        test_session.add_all([project1, project2])
        await test_session.flush()
        
        # Verificar que los proyectos se guardaron correctamente
        projects_result = await test_session.execute(
            select(Project).where(Project.client_id == sample_client.id)
        )
        saved_projects = projects_result.scalars().all()
        assert len(saved_projects) == 2
        
        # Verificar directamente la relación usando join
        client_projects_result = await test_session.execute(
            select(Client, Project)
            .join(Project, Client.id == Project.client_id)
            .where(Client.id == sample_client.id)
        )
        client_project_pairs = client_projects_result.all()
        
        # Verificar que el cliente tiene los proyectos asociados
        assert len(client_project_pairs) == 2
        project_names = [pair.Project.name for pair in client_project_pairs]
        assert "Project 1" in project_names
        assert "Project 2" in project_names
        
        # Verificar que los proyectos tienen el cliente correcto
        for pair in client_project_pairs:
            assert pair.Project.client_id == sample_client.id
            assert pair.Client.id == sample_client.id
    
    @pytest.mark.asyncio
    async def test_project_without_client_fails(
        self,
        test_session: AsyncSession
    ):
        """Test que valida que un proyecto no puede existir sin cliente."""
        project = Project(
            name="Orphan Project",
            details="Proyecto sin cliente",
            reference="REF-ORPHAN",
            trigram="ORP",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.HIGH,
            client_id=None  # Sin cliente
        )
        
        test_session.add(project)
        
        # Debe fallar por constraint de foreign key
        with pytest.raises(IntegrityError):
            await test_session.flush()


class TestTeamMembershipRelationship:
    """Tests para las relaciones Team-Employee a través de TeamMembership."""
    
    @pytest.mark.asyncio
    async def test_team_employee_membership(
        self,
        test_session: AsyncSession,
        sample_team: Team,
        multiple_employees: list[Employee]
    ):
        """Test que valida la relación muchos-a-muchos Team-Employee."""
        # Crear membresías para los empleados
        memberships = []
        roles = [MembershipRole.LEAD, MembershipRole.MEMBER, MembershipRole.COORDINATOR]
        
        for i, employee in enumerate(multiple_employees):
            membership = TeamMembership(
                team_id=sample_team.id,
                employee_id=employee.id,
                role=roles[i % len(roles)],
                start_date=date.today(),
                is_active=True
            )
            memberships.append(membership)
            test_session.add(membership)
        
        await test_session.flush()
        
        # Recargar equipo con membresías
        result = await test_session.execute(
            select(Team).options(selectinload(Team.memberships)).where(Team.id == sample_team.id)
        )
        team_with_memberships = result.scalar_one()
        
        # Verificar que el equipo tiene las membresías
        assert len(team_with_memberships.memberships) == len(multiple_employees)
        
        # Verificar que cada empleado está en el equipo
        employee_ids_in_team = [m.employee_id for m in team_with_memberships.memberships]
        for employee in multiple_employees:
            assert employee.id in employee_ids_in_team
        
        # Verificar roles asignados
        membership_roles = [m.role for m in team_with_memberships.memberships]
        assert MembershipRole.LEAD in membership_roles
        assert MembershipRole.MEMBER in membership_roles
        assert MembershipRole.COORDINATOR in membership_roles
    
    @pytest.mark.asyncio
    async def test_employee_team_memberships(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test que valida que un empleado puede estar en múltiples equipos."""
        # Crear múltiples equipos
        team1 = Team(
            name="Development Team",
            description="Equipo de desarrollo",
            is_active=True
        )
        
        team2 = Team(
            name="QA Team",
            description="Equipo de QA",
            is_active=True
        )
        
        test_session.add_all([team1, team2])
        await test_session.flush()
        
        # Crear membresías en ambos equipos
        membership1 = TeamMembership(
            team_id=team1.id,
            employee_id=sample_employee.id,
            role=MembershipRole.MEMBER,
            start_date=date.today(),
            is_active=True
        )
        
        membership2 = TeamMembership(
            team_id=team2.id,
            employee_id=sample_employee.id,
            role=MembershipRole.LEAD,
            start_date=date.today(),
            is_active=True
        )
        
        test_session.add_all([membership1, membership2])
        await test_session.flush()
        
        # Recargar empleado con membresías
        result = await test_session.execute(
            select(Employee).options(selectinload(Employee.team_memberships)).where(Employee.id == sample_employee.id)
        )
        employee_with_memberships = result.scalar_one()
        
        # Verificar que el empleado está en ambos equipos
        assert len(employee_with_memberships.team_memberships) == 2
        
        team_ids = [m.team_id for m in employee_with_memberships.team_memberships]
        assert team1.id in team_ids
        assert team2.id in team_ids
        
        # Verificar roles diferentes
        roles = [m.role for m in employee_with_memberships.team_memberships]
        assert MembershipRole.MEMBER in roles
        assert MembershipRole.LEAD in roles


class TestProjectWorkloadRelationship:
    """Tests para la relación Project-Workload."""
    
    @pytest.mark.asyncio
    async def test_project_workloads_relationship(
        self,
        test_session: AsyncSession,
        sample_client: Client,
        sample_employee: Employee
    ):
        """Test que valida la relación uno-a-muchos Project-Workload."""
        # Crear proyecto
        project = Project(
            name="Test Project",
            details="Proyecto para testing de workloads",
            reference="REF-WL",
            trigram="TWL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.HIGH,
            client_id=sample_client.id
        )
        
        test_session.add(project)
        await test_session.flush()
        
        # Crear workloads para el proyecto
        workload1 = Workload(
            project_id=project.id,
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=8.0,
            actual_hours=8.0,
            is_billable=True,
            notes="Desarrollo de funcionalidad A"
        )
        
        workload2 = Workload(
            project_id=project.id,
            employee_id=sample_employee.id,
            date=date(2024, 1, 16),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=6.5,
            actual_hours=6.5,
            is_billable=True,
            notes="Testing de funcionalidad A"
        )
        
        test_session.add_all([workload1, workload2])
        await test_session.flush()
        
        # Recargar proyecto con workloads
        result = await test_session.execute(
            select(Project).options(selectinload(Project.workloads)).where(Project.id == project.id)
        )
        project_with_workloads = result.scalar_one()
        
        # Verificar que el proyecto tiene los workloads
        assert len(project_with_workloads.workloads) == 2
        
        total_hours = sum(float(w.actual_hours or 0) for w in project_with_workloads.workloads)
        assert total_hours == 14.5
        
        # Verificar que los workloads tienen el proyecto correcto
        for workload in project_with_workloads.workloads:
            assert workload.project_id == project.id
            assert workload.project == project_with_workloads


class TestEmployeeWorkloadRelationship:
    """Tests para la relación Employee-Workload."""
    
    @pytest.mark.asyncio
    async def test_employee_workloads_relationship(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_client: Client
    ):
        """Test que valida la relación uno-a-muchos Employee-Workload."""
        # Crear proyectos
        project1 = Project(
            name="Project A",
            details="Primer proyecto",
            reference="REF-A",
            trigram="PRA",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.HIGH,
            client_id=sample_client.id
        )
        
        project2 = Project(
            name="Project B",
            details="Segundo proyecto",
            reference="REF-B",
            trigram="PRB",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 8, 31),
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.MEDIUM,
            client_id=sample_client.id
        )
        
        test_session.add_all([project1, project2])
        await test_session.flush()
        
        # Crear workloads en diferentes proyectos
        workload1 = Workload(
            project_id=project1.id,
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=8.0,
            actual_hours=8.0,
            is_billable=True,
            notes="Trabajo en proyecto A"
        )
        
        workload2 = Workload(
            project_id=project2.id,
            employee_id=sample_employee.id,
            date=date(2024, 2, 15),
            week_number=7,
            month=2,
            year=2024,
            planned_hours=6.0,
            actual_hours=6.0,
            is_billable=True,
            notes="Trabajo en proyecto B"
        )
        
        test_session.add_all([workload1, workload2])
        await test_session.flush()
        
        # Recargar empleado con workloads
        result = await test_session.execute(
            select(Employee).options(selectinload(Employee.workloads)).where(Employee.id == sample_employee.id)
        )
        employee_with_workloads = result.scalar_one()
        
        # Verificar que el empleado tiene workloads en ambos proyectos
        assert len(employee_with_workloads.workloads) == 2
        
        project_ids = [w.project_id for w in employee_with_workloads.workloads]
        assert project1.id in project_ids
        assert project2.id in project_ids
        
        total_hours = sum(float(w.actual_hours or 0) for w in employee_with_workloads.workloads)
        assert total_hours == 14.0


class TestEmployeeScheduleRelationship:
    """Tests para la relación Employee-Schedule."""
    
    @pytest.mark.asyncio
    async def test_employee_schedules_relationship(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test que valida la relación uno-a-muchos Employee-Schedule."""
        from datetime import time
        
        # Crear horarios para el empleado
        schedule1 = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            start_time=time(9, 0),
            end_time=time(17, 0),
            description="Horario regular de trabajo",
            is_confirmed=True
        )
        
        schedule2 = Schedule(
            employee_id=sample_employee.id,
            date=date(2024, 1, 16),
            start_time=time(10, 0),
            end_time=time(18, 0),
            description="Horario flexible",
            is_confirmed=True
        )
        
        test_session.add_all([schedule1, schedule2])
        await test_session.flush()
        
        # Recargar empleado con schedules
        result = await test_session.execute(
            select(Employee).options(selectinload(Employee.schedules)).where(Employee.id == sample_employee.id)
        )
        employee_with_schedules = result.scalar_one()
        
        # Verificar que el empleado tiene los horarios
        assert len(employee_with_schedules.schedules) == 2
        
        # Verificar que los horarios tienen el empleado correcto
        for schedule in employee_with_schedules.schedules:
            assert schedule.employee_id == sample_employee.id
            assert schedule.employee == employee_with_schedules
        
        # Verificar propiedades de los horarios
        dates = [s.date for s in employee_with_schedules.schedules]
        assert date(2024, 1, 15) in dates
        assert date(2024, 1, 16) in dates


class TestCascadeDeletes:
    """Tests para validar comportamiento de eliminación en cascada."""
    
    @pytest.mark.asyncio
    async def test_client_deletion_affects_projects(
        self,
        test_session: AsyncSession
    ):
        """Test que valida el comportamiento al eliminar un cliente."""
        # Crear cliente y proyecto
        client = Client(
            name="Test Client",
            email="test@client.com",
            phone="+1234567890",
            contact_person="John Doe",
            is_active=True
        )
        
        test_session.add(client)
        await test_session.flush()
        
        project = Project(
            name="Test Project",
            details="Proyecto de prueba",
            reference="REF-TEST",
            trigram="TST",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.HIGH,
            client_id=client.id
        )
        
        test_session.add(project)
        await test_session.flush()
        
        # Verificar que el proyecto existe
        result = await test_session.execute(
            select(Project).where(Project.id == project.id)
        )
        assert result.scalar_one_or_none() is not None
        
        # Eliminar cliente
        await test_session.delete(client)
        await test_session.flush()
        
        # Verificar que el proyecto ya no puede existir sin cliente
        # (esto depende de la configuración de foreign key constraints)
        result = await test_session.execute(
            select(Project).where(Project.id == project.id)
        )
        # El proyecto debería seguir existiendo pero con client_id=None
        # o fallar según la configuración de constraints
        project_after_delete = result.scalar_one_or_none()
        if project_after_delete:
            assert project_after_delete.client_id is None
    
    @pytest.mark.asyncio
    async def test_team_deletion_affects_memberships(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test que valida el comportamiento al eliminar un equipo."""
        # Crear equipo
        team = Team(
            name="Test Team",
            description="Equipo de prueba",
            is_active=True
        )
        
        test_session.add(team)
        await test_session.flush()
        
        # Crear membresía
        membership = TeamMembership(
            team_id=team.id,
            employee_id=sample_employee.id,
            role=MembershipRole.MEMBER,
            start_date=date.today(),
            is_active=True
        )
        
        test_session.add(membership)
        await test_session.flush()
        
        # Verificar que la membresía existe
        result = await test_session.execute(
            select(TeamMembership).where(TeamMembership.id == membership.id)
        )
        assert result.scalar_one_or_none() is not None
        
        # Eliminar equipo
        await test_session.delete(team)
        await test_session.flush()
        
        # Verificar que la membresía se eliminó en cascada
        result = await test_session.execute(
            select(TeamMembership).where(TeamMembership.id == membership.id)
        )
        assert result.scalar_one_or_none() is None