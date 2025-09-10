# src/planificador/tests/unit/test_models/test_project.py

import pytest
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from planificador.models.project import Project, ProjectStatus, ProjectPriority
from planificador.models.client import Client


class TestProjectModel:
    """Tests para el modelo Project."""

    async def test_project_creation_minimal_fields(self, test_session: Session):
        """Test creación de proyecto con campos mínimos requeridos."""
        # Crear cliente requerido
        client = Client(
            name="Cliente Test",
            email="test@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        # Crear proyecto con campos mínimos
        project = Project(
            reference="PROJ-001",
            trigram="P01",
            name="Proyecto Test",
            client_id=client.id
        )
        test_session.add(project)
        await test_session.flush()

        assert project.id is not None
        assert project.reference == "PROJ-001"
        assert project.trigram == "P01"
        assert project.name == "Proyecto Test"
        assert project.client_id == client.id
        assert project.status == ProjectStatus.PLANNED  # Default
        assert project.priority == ProjectPriority.MEDIUM  # Default
        assert project.revision_number == 1  # Default
        assert project.is_archived is False  # Default
        assert project.created_at is not None
        assert project.updated_at is not None

    async def test_project_creation_with_all_fields(self, test_session: Session):
        """Test creación de proyecto con todos los campos."""
        # Crear cliente requerido
        client = Client(
            name="Cliente Completo",
            email="completo@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        # Crear proyecto con todos los campos
        start_date = date.today()
        end_date = start_date + timedelta(days=30)
        
        project = Project(
            reference="PROJ-FULL-001",
            trigram="PF1",
            name="Proyecto Completo",
            job_code="JOB-001",
            client_id=client.id,
            start_date=start_date,
            end_date=end_date,
            shutdown_dates="2024-12-25,2024-01-01",
            duration_days=30,
            required_personnel="2 desarrolladores, 1 PM",
            special_training="Capacitación en tecnología X",
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.HIGH,
            responsible_person="Juan Pérez",
            last_updated_by="Admin",
            details="Detalles del proyecto",
            comments="Comentarios importantes",
            notes="Notas adicionales",
            validation_status="Validado",
            approval_status="Aprobado",
            revision_number=2,
            is_archived=False
        )
        test_session.add(project)
        await test_session.flush()

        assert project.id is not None
        assert project.reference == "PROJ-FULL-001"
        assert project.trigram == "PF1"
        assert project.name == "Proyecto Completo"
        assert project.job_code == "JOB-001"
        assert project.client_id == client.id
        assert project.start_date == start_date
        assert project.end_date == end_date
        assert project.shutdown_dates == "2024-12-25,2024-01-01"
        assert project.duration_days == 30
        assert project.required_personnel == "2 desarrolladores, 1 PM"
        assert project.special_training == "Capacitación en tecnología X"
        assert project.status == ProjectStatus.IN_PROGRESS
        assert project.priority == ProjectPriority.HIGH
        assert project.responsible_person == "Juan Pérez"
        assert project.last_updated_by == "Admin"
        assert project.details == "Detalles del proyecto"
        assert project.comments == "Comentarios importantes"
        assert project.notes == "Notas adicionales"
        assert project.validation_status == "Validado"
        assert project.approval_status == "Aprobado"
        assert project.revision_number == 2
        assert project.is_archived is False

    async def test_project_required_fields_validation(self, test_session: Session):
        """Test que campos requeridos son validados correctamente."""
        # Crear cliente válido
        client = Client(
            name="Cliente Test",
            email="test@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        # Test proyecto válido con todos los campos requeridos
        project = Project(
            reference="PROJ-VALID",
            trigram="PV1",
            name="Proyecto Válido",
            client_id=client.id
        )
        test_session.add(project)
        await test_session.flush()
        
        # Verificar que el proyecto se creó correctamente
        assert project.reference == "PROJ-VALID"
        assert project.trigram == "PV1"
        assert project.name == "Proyecto Válido"
        assert project.client_id == client.id
        assert project.id is not None

    async def test_project_unique_constraints(self, test_session: Session):
        """Test que valores únicos son aceptados correctamente."""
        # Crear cliente
        client = Client(
            name="Cliente Test",
            email="test@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        # Crear primer proyecto con valores únicos
        project1 = Project(
            reference="PROJ-UNIQUE-1",
            trigram="PU1",
            name="Proyecto Único 1",
            client_id=client.id
        )
        test_session.add(project1)
        await test_session.flush()
        
        assert project1.reference == "PROJ-UNIQUE-1"
        assert project1.trigram == "PU1"

        # Crear segundo proyecto con valores únicos diferentes
        project2 = Project(
            reference="PROJ-UNIQUE-2",
            trigram="PU2",
            name="Proyecto Único 2",
            client_id=client.id
        )
        test_session.add(project2)
        await test_session.flush()
        
        assert project2.reference == "PROJ-UNIQUE-2"
        assert project2.trigram == "PU2"
        
        # Verificar que ambos proyectos existen
        assert project1.id != project2.id

    async def test_project_status_enum_values(self, test_session: Session):
        """Test valores del enum ProjectStatus."""
        # Crear cliente
        client = Client(
            name="Cliente Test",
            email="test@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        # Test todos los valores del enum
        statuses = [
            ProjectStatus.PLANNED,
            ProjectStatus.IN_PROGRESS,
            ProjectStatus.ON_HOLD,
            ProjectStatus.COMPLETED,
            ProjectStatus.CANCELLED
        ]

        for i, status in enumerate(statuses):
            project = Project(
                reference=f"PROJ-STATUS-{i}",
                trigram=f"PS{i}",
                name=f"Proyecto Status {i}",
                client_id=client.id,
                status=status
            )
            test_session.add(project)
            await test_session.flush()
            assert project.status == status

    async def test_project_priority_enum_values(self, test_session: Session):
        """Test valores del enum ProjectPriority."""
        # Crear cliente
        client = Client(
            name="Cliente Test",
            email="test@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        # Test todos los valores del enum
        priorities = [
            ProjectPriority.LOW,
            ProjectPriority.MEDIUM,
            ProjectPriority.HIGH,
            ProjectPriority.CRITICAL
        ]

        for i, priority in enumerate(priorities):
            project = Project(
                reference=f"PROJ-PRIORITY-{i}",
                trigram=f"PP{i}",
                name=f"Proyecto Priority {i}",
                client_id=client.id,
                priority=priority
            )
            test_session.add(project)
            await test_session.flush()
            assert project.priority == priority

    async def test_project_string_length_constraints(self, test_session: Session):
        """Test que strings dentro de límites válidos son aceptados."""
        # Crear cliente
        client = Client(
            name="Cliente Test",
            email="test@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        # Test reference válido (50 caracteres máximo)
        project1 = Project(
            reference="A" * 50,  # 50 caracteres exactos
            trigram="P01",
            name="Proyecto Test",
            client_id=client.id
        )
        test_session.add(project1)
        await test_session.flush()
        assert len(project1.reference) == 50

        # Test trigram válido (3 caracteres máximo)
        project2 = Project(
            reference="PROJ-002",
            trigram="ABC",  # 3 caracteres exactos
            name="Proyecto Test 2",
            client_id=client.id
        )
        test_session.add(project2)
        await test_session.flush()
        assert len(project2.trigram) == 3

        # Test name válido (200 caracteres máximo)
        project3 = Project(
            reference="PROJ-003",
            trigram="P03",
            name="A" * 200,  # 200 caracteres exactos
            client_id=client.id
        )
        test_session.add(project3)
        await test_session.flush()
        assert len(project3.name) == 200

    async def test_project_duration_days_calculated_property(self, test_session: Session):
        """Test propiedad calculada duration_days_calculated."""
        # Crear cliente
        client = Client(
            name="Cliente Test",
            email="test@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        # Test con fechas válidas
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 10)
        
        project = Project(
            reference="PROJ-DURATION",
            trigram="PD1",
            name="Proyecto Duración",
            client_id=client.id,
            start_date=start_date,
            end_date=end_date
        )
        test_session.add(project)
        await test_session.flush()

        # 10 días (1 al 10 inclusive)
        assert project.duration_days_calculated == 10

        # Test sin fechas
        project_no_dates = Project(
            reference="PROJ-NO-DATES",
            trigram="PND",
            name="Proyecto Sin Fechas",
            client_id=client.id
        )
        test_session.add(project_no_dates)
        await test_session.flush()

        assert project_no_dates.duration_days_calculated is None

        # Test con solo start_date
        project_start_only = Project(
            reference="PROJ-START-ONLY",
            trigram="PSO",
            name="Proyecto Solo Inicio",
            client_id=client.id,
            start_date=start_date
        )
        test_session.add(project_start_only)
        await test_session.flush()

        assert project_start_only.duration_days_calculated is None

    async def test_project_status_properties(self, test_session: Session):
        """Test propiedades de estado del proyecto."""
        # Crear cliente
        client = Client(
            name="Cliente Test",
            email="test@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        # Test is_active (no archivado y en progreso)
        project_active = Project(
            reference="PROJ-ACTIVE",
            trigram="PA1",
            name="Proyecto Activo",
            client_id=client.id,
            status=ProjectStatus.IN_PROGRESS,
            is_archived=False
        )
        test_session.add(project_active)
        await test_session.flush()

        assert project_active.is_active is True
        assert project_active.is_completed is False
        assert project_active.is_planned is False
        assert project_active.is_on_hold is False
        assert project_active.is_cancelled is False

        # Test is_completed
        project_completed = Project(
            reference="PROJ-COMPLETED",
            trigram="PC1",
            name="Proyecto Completado",
            client_id=client.id,
            status=ProjectStatus.COMPLETED
        )
        test_session.add(project_completed)
        await test_session.flush()

        assert project_completed.is_active is False
        assert project_completed.is_completed is True
        assert project_completed.is_planned is False
        assert project_completed.is_on_hold is False
        assert project_completed.is_cancelled is False

        # Test is_planned
        project_planned = Project(
            reference="PROJ-PLANNED",
            trigram="PP1",
            name="Proyecto Planificado",
            client_id=client.id,
            status=ProjectStatus.PLANNED
        )
        test_session.add(project_planned)
        await test_session.flush()

        assert project_planned.is_active is False
        assert project_planned.is_completed is False
        assert project_planned.is_planned is True
        assert project_planned.is_on_hold is False
        assert project_planned.is_cancelled is False

        # Test is_on_hold
        project_on_hold = Project(
            reference="PROJ-ON-HOLD",
            trigram="POH",
            name="Proyecto En Pausa",
            client_id=client.id,
            status=ProjectStatus.ON_HOLD
        )
        test_session.add(project_on_hold)
        await test_session.flush()

        assert project_on_hold.is_active is False
        assert project_on_hold.is_completed is False
        assert project_on_hold.is_planned is False
        assert project_on_hold.is_on_hold is True
        assert project_on_hold.is_cancelled is False

        # Test is_cancelled
        project_cancelled = Project(
            reference="PROJ-CANCELLED",
            trigram="PCN",
            name="Proyecto Cancelado",
            client_id=client.id,
            status=ProjectStatus.CANCELLED
        )
        test_session.add(project_cancelled)
        await test_session.flush()

        assert project_cancelled.is_active is False
        assert project_cancelled.is_completed is False
        assert project_cancelled.is_planned is False
        assert project_cancelled.is_on_hold is False
        assert project_cancelled.is_cancelled is True

        # Test proyecto archivado (no activo aunque esté en progreso)
        project_archived = Project(
            reference="PROJ-ARCHIVED",
            trigram="PAR",
            name="Proyecto Archivado",
            client_id=client.id,
            status=ProjectStatus.IN_PROGRESS,
            is_archived=True
        )
        test_session.add(project_archived)
        await test_session.flush()

        assert project_archived.is_active is False  # Archivado

    async def test_project_display_properties(self, test_session: Session):
        """Test propiedades de visualización."""
        # Crear cliente
        client = Client(
            name="Cliente Test",
            email="test@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        # Test status_display
        project = Project(
            reference="PROJ-DISPLAY",
            trigram="PD1",
            name="Proyecto Display",
            client_id=client.id,
            status=ProjectStatus.IN_PROGRESS,
            priority=ProjectPriority.HIGH
        )
        test_session.add(project)
        await test_session.flush()

        assert project.status_display == "En Progreso"
        assert project.priority_display == "Alta"
        assert project.display_name == "[PROJ-DISPLAY] Proyecto Display"

        # Test diferentes estados
        project.status = ProjectStatus.PLANNED
        assert project.status_display == "Planificado"

        project.status = ProjectStatus.ON_HOLD
        assert project.status_display == "En Pausa"

        project.status = ProjectStatus.COMPLETED
        assert project.status_display == "Completado"

        project.status = ProjectStatus.CANCELLED
        assert project.status_display == "Cancelado"

        # Test diferentes prioridades
        project.priority = ProjectPriority.LOW
        assert project.priority_display == "Baja"

        project.priority = ProjectPriority.MEDIUM
        assert project.priority_display == "Media"

        project.priority = ProjectPriority.CRITICAL
        assert project.priority_display == "Crítica"

    async def test_project_repr(self, test_session: Session):
        """Test representación string del modelo."""
        # Crear cliente
        client = Client(
            name="Cliente Test",
            email="test@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        project = Project(
            reference="PROJ-REPR",
            trigram="PR1",
            name="Proyecto Repr",
            client_id=client.id
        )
        test_session.add(project)
        await test_session.flush()

        expected_repr = f"<Project(id={project.id}, reference='PROJ-REPR', name='Proyecto Repr')>"
        assert repr(project) == expected_repr

    async def test_project_client_relationship(self, test_session: Session):
        """Test relación con Client."""
        # Crear cliente
        client = Client(
            name="Cliente Relación",
            email="relacion@example.com"
        )
        test_session.add(client)
        await test_session.flush()

        # Crear proyecto
        project = Project(
            reference="PROJ-REL",
            trigram="PR1",
            name="Proyecto Relación",
            client_id=client.id
        )
        test_session.add(project)
        await test_session.flush()

        # Test relación directa (usando eager loading)
        await test_session.refresh(project, ['client'])
        assert project.client is not None
        assert project.client.id == client.id
        assert project.client.name == "Cliente Relación"

        # Test relación inversa (usando eager loading)
        await test_session.refresh(client, ['projects'])
        assert len(client.projects) > 0
        assert project in client.projects