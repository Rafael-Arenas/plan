"""Tests para el modelo Employee.

Este módulo contiene tests comprehensivos para el modelo Employee,
incluyendo validaciones, constraints, enums, relaciones y métodos personalizados.
"""

import pytest
import pytest_asyncio
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.employee import Employee, EmployeeStatus


class TestEmployeeStatus:
    """Tests para el enum EmployeeStatus."""

    def test_employee_status_values(self):
        """Test que el enum tiene todos los valores esperados."""
        expected_values = {
            "ACTIVE": "active",
            "INACTIVE": "inactive",
            "ON_LEAVE": "on_leave",
            "ON_VACATION": "on_vacation",
            "TERMINATED": "terminated"
        }
        
        for attr_name, expected_value in expected_values.items():
            status = getattr(EmployeeStatus, attr_name)
            assert status.value == expected_value

    def test_employee_status_enum_membership(self):
        """Test que todos los estados son miembros válidos del enum."""
        assert EmployeeStatus.ACTIVE in EmployeeStatus
        assert EmployeeStatus.INACTIVE in EmployeeStatus
        assert EmployeeStatus.ON_LEAVE in EmployeeStatus
        assert EmployeeStatus.ON_VACATION in EmployeeStatus
        assert EmployeeStatus.TERMINATED in EmployeeStatus


class TestEmployeeModel:
    """Tests para el modelo Employee."""

    @pytest_asyncio.fixture
    async def sample_employee_data(self):
        """Datos de ejemplo para crear un empleado."""
        return {
            "first_name": "Juan",
            "last_name": "Pérez",
            "employee_code": "EMP001",
            "email": "juan.perez@empresa.com",
            "phone": "+56912345678",
            "hire_date": date(2023, 1, 15),
            "position": "Desarrollador Senior",
            "department": "Tecnología",
            "qualification_level": "Senior",
            "qualification_type": "Ingeniero",
            "status": EmployeeStatus.ACTIVE,
            "skills": ["Python", "JavaScript", "SQL"],
            "certifications": ["AWS Certified", "Scrum Master"],
            "special_training": ["Machine Learning", "DevOps"],
            "weekly_hours": 40,
            "hourly_rate": Decimal("25000.00"),
            "is_available": True,
            "notes": "Empleado destacado en desarrollo backend"
        }

    @pytest_asyncio.fixture
    async def employee_instance(self, test_session: AsyncSession):
        """Fixture que crea un empleado en la base de datos."""
        import uuid
        from decimal import Decimal
        from datetime import date
        unique_id = str(uuid.uuid4())[:8]
        employee_data = {
            "first_name": "Juan",
            "last_name": "Pérez",
            "full_name": f"Juan Pérez {unique_id}",
            "employee_code": f"EMP{unique_id}",
            "email": f"juan.perez{unique_id}@empresa.com",
            "phone": "+56912345678",
            "hire_date": date(2023, 1, 15),
            "position": "Desarrollador Senior",
            "department": "Tecnología",
            "qualification_level": "Senior",
            "qualification_type": "Ingeniero",
            "status": EmployeeStatus.ACTIVE,
            "skills": ["Python", "JavaScript", "SQL"],
            "certifications": ["AWS Certified", "Scrum Master"],
            "special_training": ["Machine Learning", "DevOps"],
            "weekly_hours": 40,
            "hourly_rate": Decimal("25000.00"),
            "is_available": True,
            "notes": "Empleado destacado en desarrollo backend"
        }
        employee = Employee(**employee_data)
        test_session.add(employee)
        await test_session.flush()  # Flush para obtener ID sin commit
        return employee

    # Tests de creación de instancias
    async def test_employee_creation_with_all_fields(self, sample_employee_data):
        """Test creación de empleado con todos los campos."""
        employee = Employee(**sample_employee_data)
        
        assert employee.first_name == "Juan"
        assert employee.last_name == "Pérez"
        assert employee.full_name == "Juan Pérez"  # Auto-generado
        assert employee.employee_code == "EMP001"
        assert employee.email == "juan.perez@empresa.com"
        assert employee.phone == "+56912345678"
        assert employee.hire_date == date(2023, 1, 15)
        assert employee.position == "Desarrollador Senior"
        assert employee.department == "Tecnología"
        assert employee.qualification_level == "Senior"
        assert employee.qualification_type == "Ingeniero"
        assert employee.status == EmployeeStatus.ACTIVE
        assert employee.skills == ["Python", "JavaScript", "SQL"]
        assert employee.certifications == ["AWS Certified", "Scrum Master"]
        assert employee.special_training == ["Machine Learning", "DevOps"]
        assert employee.weekly_hours == 40
        assert employee.hourly_rate == Decimal("25000.00")
        assert employee.is_available is True
        assert employee.notes == "Empleado destacado en desarrollo backend"

    async def test_employee_creation_minimal_fields(self, test_session: AsyncSession):
        """Test creación de empleado solo con campos obligatorios."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        employee = Employee(
            first_name="Ana",
            last_name="García",
            full_name=f"Ana García {unique_id}",
            employee_code=f"EMP-MIN-{unique_id}",
            email=f"ana.garcia{unique_id}@empresa.com"
        )
        
        test_session.add(employee)
        await test_session.flush()
        await test_session.refresh(employee)
        
        assert employee.first_name == "Ana"
        assert employee.last_name == "García"
        assert employee.full_name == f"Ana García {unique_id}"
        assert employee.phone is None
        assert employee.hire_date is None
        assert employee.position is None
        assert employee.department is None
        assert employee.qualification_level is None
        assert employee.qualification_type is None
        assert employee.status == EmployeeStatus.ACTIVE  # Valor por defecto
        assert employee.skills is None
        assert employee.certifications is None
        assert employee.special_training is None
        assert employee.weekly_hours == 40  # Valor por defecto
        assert employee.hourly_rate is None
        assert employee.is_available is True  # Valor por defecto
        assert employee.notes is None

    async def test_employee_full_name_auto_generation(self):
        """Test que full_name se genera automáticamente si no se proporciona."""
        employee = Employee(
            first_name="Carlos",
            last_name="Rodríguez"
        )
        assert employee.full_name == "Carlos Rodríguez"

    async def test_employee_full_name_explicit(self):
        """Test que se puede proporcionar full_name explícitamente."""
        employee = Employee(
            first_name="María",
            last_name="González",
            full_name="María González Pérez"
        )
        assert employee.full_name == "María González Pérez"

    async def test_employee_creation_with_defaults(self, test_session: AsyncSession):
        """Test que los valores por defecto se aplican correctamente."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        employee = Employee(
            first_name="Pedro",
            last_name="López",
            full_name=f"Pedro López {unique_id}",
            employee_code=f"EMP-DEF-{unique_id}",
            email=f"pedro.lopez{unique_id}@empresa.com"
        )
        
        test_session.add(employee)
        await test_session.flush()
        await test_session.refresh(employee)
        
        assert employee.status == EmployeeStatus.ACTIVE
        assert employee.weekly_hours == 40
        assert employee.is_available is True

    # Tests de validaciones y constraints
    async def test_employee_first_name_required(self, test_session: AsyncSession):
        """Test que first_name es obligatorio."""
        employee = Employee(last_name="Apellido")
        test_session.add(employee)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_employee_last_name_required(self, test_session: AsyncSession):
        """Test que last_name es obligatorio."""
        employee = Employee(first_name="Nombre")
        test_session.add(employee)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_employee_full_name_required(self, test_session: AsyncSession):
        """Test que full_name es obligatorio."""
        # Crear empleado sin first_name ni last_name, y sin full_name
        employee = Employee()
        # Forzar full_name a None para probar constraint
        employee.full_name = None
        test_session.add(employee)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_employee_full_name_unique_constraint(self, test_session: AsyncSession, employee_instance):
        """Test que full_name debe ser único."""
        # Intentar crear otro empleado con el mismo full_name
        duplicate_employee = Employee(
            first_name="Otro",
            last_name="Nombre",
            full_name=employee_instance.full_name
        )
        test_session.add(duplicate_employee)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_employee_code_unique_constraint(self, test_session: AsyncSession, employee_instance):
        """Test que employee_code debe ser único cuando se proporciona."""
        # Intentar crear otro empleado con el mismo código
        duplicate_employee = Employee(
            first_name="Otro",
            last_name="Empleado",
            employee_code=employee_instance.employee_code
        )
        test_session.add(duplicate_employee)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_employee_email_unique_constraint(self, test_session: AsyncSession, employee_instance):
        """Test que email debe ser único cuando se proporciona."""
        # Intentar crear otro empleado con el mismo email
        duplicate_employee = Employee(
            first_name="Otro",
            last_name="Empleado",
            email=employee_instance.email
        )
        test_session.add(duplicate_employee)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_employee_nullable_fields_can_be_null(self, test_session: AsyncSession):
        """Test que campos opcionales pueden ser nulos y múltiples empleados pueden tener valores nulos."""
        employee1 = Employee(
            first_name="Empleado1",
            last_name="Sin Código"
        )
        employee2 = Employee(
            first_name="Empleado2",
            last_name="Sin Email"
        )
        
        test_session.add_all([employee1, employee2])
        await test_session.flush()
        
        assert employee1.employee_code is None
        assert employee1.email is None
        assert employee2.employee_code is None
        assert employee2.email is None
        assert employee1.id != employee2.id

    # Tests de enum status
    async def test_employee_status_enum_values(self, test_session: AsyncSession):
        """Test que se pueden asignar todos los valores del enum status."""
        for status in EmployeeStatus:
            employee = Employee(
                first_name="Test",
                last_name=f"Status{status.value}",
                status=status
            )
            test_session.add(employee)
            await test_session.flush()
            await test_session.refresh(employee)
            
            assert employee.status == status
            await test_session.delete(employee)
            await test_session.flush()

    async def test_employee_status_default_value(self, test_session: AsyncSession):
        """Test que verifica que el status tiene valor por defecto ACTIVE."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        employee = Employee(
            first_name="Test",
            last_name="Default",
            full_name=f"Test Default {unique_id}",
            employee_code=f"EMP-DEF-{unique_id}",
            email=f"test.default{unique_id}@empresa.com"
        )
        test_session.add(employee)
        await test_session.flush()
        await test_session.refresh(employee)
        assert employee.status == EmployeeStatus.ACTIVE

    # Tests de campos JSON
    async def test_employee_json_fields(self, test_session: AsyncSession):
        """Test que los campos JSON se manejan correctamente."""
        skills = ["Python", "JavaScript", "Docker"]
        certifications = ["AWS", "Azure", "GCP"]
        training = ["Kubernetes", "Machine Learning"]
        
        employee = Employee(
            first_name="JSON",
            last_name="Test",
            skills=skills,
            certifications=certifications,
            special_training=training
        )
        
        test_session.add(employee)
        await test_session.flush()
        await test_session.refresh(employee)
        
        assert employee.skills == skills
        assert employee.certifications == certifications
        assert employee.special_training == training

    async def test_employee_json_fields_empty_lists(self, test_session: AsyncSession):
        """Test que los campos JSON pueden ser listas vacías."""
        employee = Employee(
            first_name="Empty",
            last_name="Lists",
            skills=[],
            certifications=[],
            special_training=[]
        )
        
        test_session.add(employee)
        await test_session.flush()
        await test_session.refresh(employee)
        
        assert employee.skills == []
        assert employee.certifications == []
        assert employee.special_training == []

    # Tests de métodos personalizados
    async def test_display_name_property(self, employee_instance):
        """Test del método display_name."""
        expected = f"{employee_instance.first_name} {employee_instance.last_name}"
        assert employee_instance.display_name == expected

    async def test_display_name_with_different_names(self):
        """Test display_name con diferentes combinaciones de nombres."""
        employee = Employee(
            first_name="María José",
            last_name="González Pérez"
        )
        assert employee.display_name == "María José González Pérez"

    async def test_initials_property(self, employee_instance):
        """Test del método initials."""
        expected = f"{employee_instance.first_name[0].upper()}{employee_instance.last_name[0].upper()}"
        assert employee_instance.initials == expected

    async def test_initials_with_different_names(self):
        """Test initials con diferentes nombres."""
        employee = Employee(
            first_name="ana",
            last_name="garcía"
        )
        assert employee.initials == "AG"

    async def test_initials_with_empty_names(self):
        """Test initials con nombres vacíos."""
        employee = Employee(
            first_name="",
            last_name="García"
        )
        assert employee.initials == "G"
        
        employee2 = Employee(
            first_name="Ana",
            last_name=""
        )
        assert employee2.initials == "A"

    async def test_is_active_status_property(self, employee_instance):
        """Test del método is_active_status."""
        assert employee_instance.is_active_status is True
        
        # Cambiar a estado inactivo
        employee_instance.status = EmployeeStatus.INACTIVE
        assert employee_instance.is_active_status is False
        
        # Probar otros estados
        employee_instance.status = EmployeeStatus.ON_LEAVE
        assert employee_instance.is_active_status is False
        
        employee_instance.status = EmployeeStatus.ON_VACATION
        assert employee_instance.is_active_status is False
        
        employee_instance.status = EmployeeStatus.TERMINATED
        assert employee_instance.is_active_status is False

    async def test_contact_info_property(self, employee_instance):
        """Test del método contact_info."""
        expected = {
            "email": employee_instance.email,
            "phone": employee_instance.phone,
            "full_name": employee_instance.display_name
        }
        assert employee_instance.contact_info == expected

    async def test_contact_info_with_partial_data(self):
        """Test contact_info con datos parciales."""
        employee = Employee(
            first_name="Test",
            last_name="Partial",
            email="test@test.com"
        )
        expected = {
            "email": "test@test.com",
            "phone": None,
            "full_name": "Test Partial"
        }
        assert employee.contact_info == expected

    async def test_update_full_name_method(self, test_session: AsyncSession, employee_instance):
        """Test del método update_full_name."""
        # Cambiar nombres
        employee_instance.first_name = "Nuevo"
        employee_instance.last_name = "Nombre"
        
        # Llamar al método
        employee_instance.update_full_name()
        
        assert employee_instance.full_name == "Nuevo Nombre"

    # Tests de representación
    async def test_employee_repr(self, employee_instance):
        """Test de la representación string del empleado."""
        expected = f"<Employee(id={employee_instance.id}, full_name='{employee_instance.full_name}')>"
        assert repr(employee_instance) == expected

    # Tests de persistencia
    async def test_employee_persistence(self, test_session: AsyncSession, sample_employee_data):
        """Test que el empleado se persiste correctamente en la base de datos."""
        employee = Employee(**sample_employee_data)
        test_session.add(employee)
        await test_session.flush()
        await test_session.refresh(employee)
        
        # Verificar que se asignó un ID
        assert employee.id is not None
        assert isinstance(employee.id, int)
        
        # Verificar que se asignaron timestamps
        assert employee.created_at is not None
        assert employee.updated_at is not None
        
        # Verificar que los datos se guardaron correctamente
        assert employee.first_name == sample_employee_data["first_name"]
        assert employee.last_name == sample_employee_data["last_name"]
        assert employee.email == sample_employee_data["email"]
        assert employee.status == sample_employee_data["status"]

    async def test_employee_update_timestamps(self, test_session: AsyncSession, employee_instance):
        """Test que updated_at se puede actualizar al modificar el empleado."""
        original_updated_at = employee_instance.updated_at
        
        # Actualizar el empleado
        employee_instance.position = "Desarrollador Lead"
        await test_session.flush()
        await test_session.refresh(employee_instance)
        
        # Verificar que el campo se actualizó y que updated_at existe
        assert employee_instance.position == "Desarrollador Lead"
        assert employee_instance.updated_at is not None
        assert isinstance(employee_instance.updated_at, type(original_updated_at))

    # Tests de relaciones (preparación para tests de relaciones más complejos)
    def test_employee_relationships_defined(self):
        """Test que las relaciones están definidas en el modelo."""
        # Crear una instancia simple sin persistir
        employee = Employee(first_name="Test", last_name="User")
        
        # Verificar que las relaciones están definidas como atributos
        assert hasattr(employee, 'team_memberships')
        assert hasattr(employee, 'project_assignments')
        assert hasattr(employee, 'schedules')
        assert hasattr(employee, 'vacations')
        assert hasattr(employee, 'workloads')

    # Tests de casos edge
    async def test_employee_with_special_characters(self, test_session: AsyncSession):
        """Test empleado con caracteres especiales en los campos."""
        employee = Employee(
            first_name="José María",
            last_name="González-Pérez",
            email="jose.maria@empresa.com"
        )
        test_session.add(employee)
        await test_session.flush()
        
        assert employee.first_name == "José María"
        assert employee.last_name == "González-Pérez"
        assert employee.full_name == "José María González-Pérez"

    async def test_employee_numeric_fields_precision(self, test_session: AsyncSession):
        """Test precisión de campos numéricos."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        employee = Employee(
            first_name="Test",
            last_name="Employee",
            full_name=f"Test Employee {unique_id}",
            employee_code=f"EMP-NUM-{unique_id}",
            email=f"test.employee{unique_id}@empresa.com",
            weekly_hours=37,
            hourly_rate=Decimal("15750.50")
        )
        test_session.add(employee)
        await test_session.flush()
        
        assert employee.weekly_hours == 37
        assert employee.hourly_rate == Decimal("15750.50")
        assert isinstance(employee.hourly_rate, Decimal)

    async def test_employee_date_fields(self, test_session: AsyncSession):
        """Test manejo de campos de fecha."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        hire_date = date(2020, 12, 25)
        employee = Employee(
            first_name="Test",
            last_name="Employee",
            full_name=f"Test Employee {unique_id}",
            employee_code=f"EMP-DATE-{unique_id}",
            email=f"test.employee{unique_id}@empresa.com",
            hire_date=hire_date
        )
        test_session.add(employee)
        await test_session.flush()
        
        assert employee.hire_date == hire_date
        assert isinstance(employee.hire_date, date)

    async def test_employee_boolean_field_variations(self, test_session: AsyncSession):
        """Test diferentes formas de asignar campos booleanos."""
        import uuid
        
        # Empleado disponible explícito
        unique_id_1 = str(uuid.uuid4())[:8]
        employee_available = Employee(
            first_name="Available",
            last_name="Employee",
            full_name=f"Available Employee {unique_id_1}",
            employee_code=f"EMP-BOOL-{unique_id_1}",
            email=f"available.employee{unique_id_1}@empresa.com",
            is_available=True
        )
        
        # Empleado no disponible explícito
        unique_id_2 = str(uuid.uuid4())[:8]
        employee_unavailable = Employee(
            first_name="Unavailable",
            last_name="Employee",
            full_name=f"Unavailable Employee {unique_id_2}",
            employee_code=f"EMP-BOOL-{unique_id_2}",
            email=f"unavailable.employee{unique_id_2}@empresa.com",
            is_available=False
        )
        
        # Empleado con valor por defecto
        unique_id_3 = str(uuid.uuid4())[:8]
        employee_default = Employee(
            first_name="Default",
            last_name="Employee",
            full_name=f"Default Employee {unique_id_3}",
            employee_code=f"EMP-BOOL-{unique_id_3}",
            email=f"default.employee{unique_id_3}@empresa.com"
        )
        
        test_session.add_all([employee_available, employee_unavailable, employee_default])
        await test_session.flush()
        
        assert employee_available.is_available is True
        assert employee_unavailable.is_available is False
        assert employee_default.is_available is True  # Valor por defecto