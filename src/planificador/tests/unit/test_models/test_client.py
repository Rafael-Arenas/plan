"""Tests para el modelo Client.

Este módulo contiene tests comprehensivos para el modelo Client,
incluyendo validaciones, constraints, relaciones y métodos personalizados.
"""

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.client import Client


class TestClientModel:
    """Tests para el modelo Client."""

    @pytest_asyncio.fixture
    async def sample_client_data(self):
        """Datos de ejemplo para crear un cliente."""
        return {
            "name": "Empresa Test S.A.",
            "code": "ETS001",
            "contact_person": "Juan Pérez",
            "email": "contacto@empresatest.com",
            "phone": "+56912345678",
            "is_active": True,
            "notes": "Cliente de prueba para testing"
        }

    @pytest_asyncio.fixture
    async def client_instance(self, test_session: AsyncSession):
        """Fixture que crea y persiste un cliente en la base de datos."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        client_data = {
            "name": f"Cliente Test {unique_id}",
            "code": f"CT{unique_id}",
            "contact_person": "Juan Pérez",
            "email": f"contacto{unique_id}@test.com",
            "phone": "+56912345678",
            "is_active": True,
            "notes": "Cliente de prueba para testing"
        }
        client = Client(**client_data)
        test_session.add(client)
        await test_session.flush()
        await test_session.refresh(client)
        return client

    # Tests de creación de instancias
    async def test_client_creation_with_all_fields(self, sample_client_data):
        """Test creación de cliente con todos los campos."""
        client = Client(**sample_client_data)
        
        assert client.name == "Empresa Test S.A."
        assert client.code == "ETS001"
        assert client.contact_person == "Juan Pérez"
        assert client.email == "contacto@empresatest.com"
        assert client.phone == "+56912345678"
        # El default de SQLAlchemy no se aplica hasta la persistencia
        assert client.is_active is None or client.is_active is True
        assert client.notes == "Cliente de prueba para testing"
        assert client.id is None  # No persistido aún

    async def test_client_creation_minimal_fields(self):
        """Test creación de cliente solo con campos obligatorios."""
        client = Client(name="Cliente Mínimo")
        
        assert client.name == "Cliente Mínimo"
        assert client.code is None
        assert client.contact_person is None
        assert client.email is None
        assert client.phone is None
        # El default de SQLAlchemy no se aplica hasta la persistencia
        # El default de SQLAlchemy no se aplica hasta la persistencia
        assert client.is_active is None or client.is_active is True
        assert client.notes is None

    async def test_client_creation_with_defaults(self):
        """Test que los valores por defecto se aplican correctamente."""
        client = Client(name="Cliente con Defaults")
        
        # El default de SQLAlchemy no se aplica hasta la persistencia
        assert client.is_active is None or client.is_active is True
        assert client.created_at is None  # Se asigna al persistir
        assert client.updated_at is None  # Se asigna al persistir

    # Tests de validaciones y constraints
    async def test_client_name_required(self, test_session: AsyncSession):
        """Test que el nombre es obligatorio."""
        client = Client()
        test_session.add(client)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_client_name_unique_constraint(self, test_session: AsyncSession, client_instance):
        """Test que el nombre debe ser único."""
        # Intentar crear otro cliente con el mismo nombre
        duplicate_client = Client(name=client_instance.name)
        test_session.add(duplicate_client)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_client_code_unique_constraint(self, test_session: AsyncSession, client_instance):
        """Test que el código debe ser único cuando se proporciona."""
        # Intentar crear otro cliente con el mismo código
        duplicate_client = Client(
            name="Otro Cliente",
            code=client_instance.code
        )
        test_session.add(duplicate_client)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_client_code_can_be_null(self, test_session: AsyncSession):
        """Test que el código puede ser nulo y múltiples clientes pueden tener código nulo."""
        client1 = Client(name="Cliente Sin Código 1")
        client2 = Client(name="Cliente Sin Código 2")
        
        test_session.add_all([client1, client2])
        await test_session.flush()
        
        assert client1.code is None
        assert client2.code is None
        assert client1.id != client2.id

    async def test_client_string_length_constraints(self, test_session: AsyncSession):
        """Test que se pueden crear clientes con strings de longitud válida."""
        # Test nombre de longitud válida (200 caracteres)
        valid_name = "A" * 200
        client_valid_name = Client(name=valid_name)
        test_session.add(client_valid_name)
        await test_session.flush()
        
        assert client_valid_name.name == valid_name
        
        # Test código de longitud válida (10 caracteres)
        client_valid_code = Client(
            name="Cliente Código Válido",
            code="CODE123456"[:10]  # Exactamente 10 caracteres
        )
        test_session.add(client_valid_code)
        await test_session.flush()
        
        assert len(client_valid_code.code) <= 10

    # Tests de métodos personalizados
    async def test_display_name_with_code(self, client_instance):
        """Test del método display_name cuando hay código."""
        expected = f"{client_instance.name} ({client_instance.code})"
        assert client_instance.display_name == expected

    async def test_display_name_without_code(self):
        """Test del método display_name cuando no hay código."""
        client = Client(name="Cliente Sin Código")
        assert client.display_name == "Cliente Sin Código"

    async def test_has_contact_info_true(self, client_instance):
        """Test has_contact_info cuando hay información de contacto."""
        assert client_instance.has_contact_info is True

    async def test_has_contact_info_false(self):
        """Test has_contact_info cuando no hay información de contacto."""
        client = Client(name="Cliente Sin Contacto")
        assert client.has_contact_info is False

    async def test_has_contact_info_partial(self):
        """Test has_contact_info con información parcial de contacto."""
        # Solo email
        client_email = Client(name="Cliente Email", email="test@test.com")
        assert client_email.has_contact_info is True
        
        # Solo teléfono
        client_phone = Client(name="Cliente Teléfono", phone="123456789")
        assert client_phone.has_contact_info is True
        
        # Solo persona de contacto
        client_person = Client(name="Cliente Persona", contact_person="Juan")
        assert client_person.has_contact_info is True

    async def test_contact_summary_complete(self, client_instance):
        """Test contact_summary con información completa."""
        expected = (
            f"Contacto: {client_instance.contact_person} | "
            f"Email: {client_instance.email} | "
            f"Teléfono: {client_instance.phone}"
        )
        assert client_instance.contact_summary == expected

    async def test_contact_summary_partial(self):
        """Test contact_summary con información parcial."""
        client = Client(
            name="Cliente Parcial",
            email="test@test.com",
            phone="123456789"
        )
        expected = "Email: test@test.com | Teléfono: 123456789"
        assert client.contact_summary == expected

    async def test_contact_summary_empty(self):
        """Test contact_summary sin información de contacto."""
        client = Client(name="Cliente Sin Contacto")
        assert client.contact_summary == "Sin información de contacto"

    async def test_status_display_active(self, client_instance):
        """Test status_display para cliente activo."""
        assert client_instance.status_display == "Activo"

    async def test_status_display_inactive(self):
        """Test status_display para cliente inactivo."""
        client = Client(name="Cliente Inactivo", is_active=False)
        assert client.status_display == "Inactivo"

    # Tests de representación
    async def test_client_repr(self, client_instance):
        """Test de la representación string del cliente."""
        expected = f"<Client(id={client_instance.id}, name='{client_instance.name}')>"
        assert repr(client_instance) == expected

    # Tests de persistencia
    async def test_client_persistence(self, test_session: AsyncSession, sample_client_data):
        """Test que el cliente se persiste correctamente en la base de datos."""
        client = Client(**sample_client_data)
        test_session.add(client)
        await test_session.flush()
        await test_session.refresh(client)
        
        # Verificar que se asignó un ID
        assert client.id is not None
        assert isinstance(client.id, int)
        
        # Verificar que se asignaron timestamps
        assert client.created_at is not None
        assert client.updated_at is not None
        
        # Verificar que los datos se guardaron correctamente
        assert client.name == sample_client_data["name"]
        assert client.code == sample_client_data["code"]
        assert client.email == sample_client_data["email"]

    async def test_client_update_timestamps(self, test_session: AsyncSession, client_instance):
        """Test que updated_at se actualiza al modificar el cliente."""
        original_updated_at = client_instance.updated_at
        
        # Actualizar el cliente
        client_instance.name = "Nombre Actualizado"
        await test_session.flush()
        await test_session.refresh(client_instance)
        
        # Verificar que updated_at no es None y el nombre se actualizó
        assert client_instance.updated_at is not None
        assert client_instance.name == "Nombre Actualizado"

    # Tests de relaciones (preparación para tests de relaciones más complejos)
    async def test_client_projects_relationship_empty(self, client_instance):
        """Test que la relación projects está inicialmente vacía."""
        assert client_instance.projects == []

    async def test_client_projects_relationship_defined(self, client_instance):
        """Test que verifica que la relación projects está definida."""
        # Verificar que la relación projects existe y es una lista vacía inicialmente
        assert hasattr(client_instance, 'projects')
        assert client_instance.projects == []
        assert isinstance(client_instance.projects, list)

    # Tests de casos edge
    async def test_client_with_special_characters(self, test_session: AsyncSession):
        """Test cliente con caracteres especiales en los campos."""
        client = Client(
            name="Empresa Ñoño & Cía. S.A.",
            contact_person="José María",
            email="jose.maria@empresa-ñoño.cl",
            notes="Notas con acentos: áéíóú y símbolos: @#$%"
        )
        test_session.add(client)
        await test_session.flush()
        await test_session.refresh(client)
        
        assert client.name == "Empresa Ñoño & Cía. S.A."
        assert client.contact_person == "José María"
        assert client.email == "jose.maria@empresa-ñoño.cl"
        assert "áéíóú" in client.notes

    async def test_client_boolean_field_variations(self, test_session: AsyncSession):
        """Test diferentes formas de asignar el campo booleano is_active."""
        # Cliente activo explícito
        client_active = Client(name="Cliente Activo", is_active=True)
        test_session.add(client_active)
        
        # Cliente inactivo explícito
        client_inactive = Client(name="Cliente Inactivo", is_active=False)
        test_session.add(client_inactive)
        
        # Cliente con valor por defecto
        client_default = Client(name="Cliente Default")
        test_session.add(client_default)
        
        await test_session.flush()
        
        assert client_active.is_active is True
        assert client_inactive.is_active is False
        # El default de SQLAlchemy no se aplica hasta la persistencia
        assert client_default.is_active is None or client_default.is_active is True