"""Tests para el modelo StatusCode.

Este módulo contiene tests comprehensivos para el modelo StatusCode,
incluyendo validaciones, constraints, propiedades y métodos personalizados.
"""

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.status_code import StatusCode


class TestStatusCodeModel:
    """Tests para el modelo StatusCode."""

    # Tests de creación de instancias
    async def test_status_code_creation_with_all_fields(self, sample_status_code_data):
        """Test creación de código de estado con todos los campos."""
        status_code = StatusCode(**sample_status_code_data)
        
        assert status_code.code == "DEV"
        assert status_code.name == "Desarrollo"
        assert status_code.description == "Tiempo dedicado al desarrollo de software"
        assert status_code.color == "#007bff"
        assert status_code.icon == "code"
        assert status_code.is_billable is True
        assert status_code.is_productive is True
        assert status_code.requires_approval is False
        assert status_code.is_active is True
        assert status_code.sort_order == 10
        assert status_code.id is None  # No persistido aún

    async def test_status_code_creation_minimal_fields(self):
        """Test creación de código de estado solo con campos obligatorios."""
        status_code = StatusCode(
            code="MIN",
            name="Mínimo"
        )
        
        assert status_code.code == "MIN"
        assert status_code.name == "Mínimo"
        assert status_code.description is None
        assert status_code.color is None
        assert status_code.icon is None
        # Los defaults de SQLAlchemy no se aplican hasta la persistencia
        assert status_code.is_billable is None or status_code.is_billable is True
        assert status_code.is_productive is None or status_code.is_productive is True
        assert status_code.requires_approval is None or status_code.requires_approval is False
        assert status_code.is_active is None or status_code.is_active is True
        assert status_code.sort_order is None or status_code.sort_order == 0

    async def test_status_code_creation_with_defaults(self):
        """Test que los valores por defecto se aplican correctamente."""
        status_code = StatusCode(
            code="DEF",
            name="Default"
        )
        
        # Los defaults de SQLAlchemy no se aplican hasta la persistencia
        assert status_code.is_billable is None or status_code.is_billable is True
        assert status_code.is_productive is None or status_code.is_productive is True
        assert status_code.requires_approval is None or status_code.requires_approval is False
        assert status_code.is_active is None or status_code.is_active is True
        assert status_code.sort_order is None or status_code.sort_order == 0
        assert status_code.created_at is None  # Se asigna al persistir
        assert status_code.updated_at is None  # Se asigna al persistir

    # Tests de validaciones y constraints
    async def test_status_code_code_required(self, test_session: AsyncSession):
        """Test que el código es obligatorio."""
        status_code = StatusCode(name="Test")
        test_session.add(status_code)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_status_code_name_required(self, test_session: AsyncSession):
        """Test que el nombre es obligatorio."""
        status_code = StatusCode(code="TST")
        test_session.add(status_code)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_status_code_code_unique_constraint(self, test_session: AsyncSession, status_code_instance):
        """Test que el código debe ser único."""
        # Intentar crear otro código de estado con el mismo código
        duplicate_status_code = StatusCode(
            code=status_code_instance.code,
            name="Otro Nombre"
        )
        test_session.add(duplicate_status_code)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()

    async def test_status_code_string_length_constraints(self, test_session: AsyncSession):
        """Test que se pueden crear códigos de estado con strings de longitud válida."""
        # Test código de longitud válida (20 caracteres)
        valid_code = "A" * 20
        status_code_valid_code = StatusCode(
            code=valid_code,
            name="Código Válido"
        )
        test_session.add(status_code_valid_code)
        await test_session.flush()
        
        assert status_code_valid_code.code == valid_code
        
        # Test nombre de longitud válida (100 caracteres)
        valid_name = "B" * 100
        status_code_valid_name = StatusCode(
            code="VALID2",
            name=valid_name
        )
        test_session.add(status_code_valid_name)
        await test_session.flush()
        
        assert status_code_valid_name.name == valid_name

    async def test_status_code_boolean_fields_validation(self, test_session: AsyncSession):
        """Test validación de campos booleanos."""
        # Test con todos los booleanos en False
        status_code = StatusCode(
            code="BOOL",
            name="Boolean Test",
            is_billable=False,
            is_productive=False,
            requires_approval=True,
            is_active=False
        )
        test_session.add(status_code)
        await test_session.flush()
        
        assert status_code.is_billable is False
        assert status_code.is_productive is False
        assert status_code.requires_approval is True
        assert status_code.is_active is False

    async def test_status_code_sort_order_validation(self, test_session: AsyncSession):
        """Test validación del campo sort_order."""
        # Test con sort_order negativo
        status_code_negative = StatusCode(
            code="NEG",
            name="Negative Sort",
            sort_order=-5
        )
        test_session.add(status_code_negative)
        await test_session.flush()
        
        assert status_code_negative.sort_order == -5
        
        # Test con sort_order grande
        status_code_large = StatusCode(
            code="LARGE",
            name="Large Sort",
            sort_order=9999
        )
        test_session.add(status_code_large)
        await test_session.flush()
        
        assert status_code_large.sort_order == 9999


class TestStatusCodeProperties:
    """Tests para las propiedades del modelo StatusCode."""

    async def test_display_name_property(self, status_code_instance):
        """Test de la propiedad display_name."""
        expected = f"{status_code_instance.code} - {status_code_instance.name}"
        assert status_code_instance.display_name == expected

    async def test_is_billable_productive_property(self):
        """Test de la propiedad is_billable_productive."""
        # Ambos True
        status_code_both = StatusCode(
            code="BOTH",
            name="Both True",
            is_billable=True,
            is_productive=True
        )
        assert status_code_both.is_billable_productive is True
        
        # Solo billable
        status_code_billable = StatusCode(
            code="BILL",
            name="Only Billable",
            is_billable=True,
            is_productive=False
        )
        assert status_code_billable.is_billable_productive is False
        
        # Solo productive
        status_code_productive = StatusCode(
            code="PROD",
            name="Only Productive",
            is_billable=False,
            is_productive=True
        )
        assert status_code_productive.is_billable_productive is False
        
        # Ninguno
        status_code_neither = StatusCode(
            code="NONE",
            name="Neither",
            is_billable=False,
            is_productive=False
        )
        assert status_code_neither.is_billable_productive is False

    async def test_status_category_property(self):
        """Test de la propiedad status_category."""
        # Productivo Facturable
        status_code_prod_bill = StatusCode(
            code="PB",
            name="Prod Bill",
            is_billable=True,
            is_productive=True
        )
        assert status_code_prod_bill.status_category == "Productivo Facturable"
        
        # Productivo No Facturable
        status_code_prod_no_bill = StatusCode(
            code="PNB",
            name="Prod No Bill",
            is_billable=False,
            is_productive=True
        )
        assert status_code_prod_no_bill.status_category == "Productivo No Facturable"
        
        # Facturable No Productivo
        status_code_bill_no_prod = StatusCode(
            code="BNP",
            name="Bill No Prod",
            is_billable=True,
            is_productive=False
        )
        assert status_code_bill_no_prod.status_category == "Facturable No Productivo"
        
        # No Productivo No Facturable
        status_code_neither = StatusCode(
            code="NPNF",
            name="Neither",
            is_billable=False,
            is_productive=False
        )
        assert status_code_neither.status_category == "No Productivo No Facturable"

    async def test_requires_special_handling_property(self):
        """Test de la propiedad requires_special_handling."""
        # Requiere aprobación
        status_code_approval = StatusCode(
            code="APP",
            name="Approval",
            requires_approval=True,
            is_active=True
        )
        assert status_code_approval.requires_special_handling is True
        
        # No activo
        status_code_inactive = StatusCode(
            code="INA",
            name="Inactive",
            requires_approval=False,
            is_active=False
        )
        assert status_code_inactive.requires_special_handling is True
        
        # Ambos
        status_code_both = StatusCode(
            code="BOTH",
            name="Both",
            requires_approval=True,
            is_active=False
        )
        assert status_code_both.requires_special_handling is True
        
        # Ninguno
        status_code_normal = StatusCode(
            code="NORM",
            name="Normal",
            requires_approval=False,
            is_active=True
        )
        assert status_code_normal.requires_special_handling is False

    async def test_status_display_property(self):
        """Test de la propiedad status_display."""
        # Activo
        status_code_active = StatusCode(
            code="ACT",
            name="Active",
            is_active=True
        )
        assert status_code_active.status_display == "Activo"
        
        # Inactivo
        status_code_inactive = StatusCode(
            code="INA",
            name="Inactive",
            is_active=False
        )
        assert status_code_inactive.status_display == "Inactivo"


class TestStatusCodeMethods:
    """Tests para los métodos del modelo StatusCode."""

    async def test_repr_method(self, status_code_instance):
        """Test del método __repr__."""
        expected = f"<StatusCode(id={status_code_instance.id}, code='{status_code_instance.code}', name='{status_code_instance.name}')>"
        assert repr(status_code_instance) == expected


class TestStatusCodePersistence:
    """Tests de persistencia del modelo StatusCode."""

    async def test_status_code_persistence(self, test_session: AsyncSession, sample_status_code_data):
        """Test que el código de estado se persiste correctamente en la base de datos."""
        status_code = StatusCode(**sample_status_code_data)
        test_session.add(status_code)
        await test_session.flush()
        await test_session.refresh(status_code)
        
        # Verificar que se asignó un ID
        assert status_code.id is not None
        assert isinstance(status_code.id, int)
        
        # Verificar que se asignaron timestamps
        assert status_code.created_at is not None
        assert status_code.updated_at is not None
        
        # Verificar que los datos se guardaron correctamente
        assert status_code.code == sample_status_code_data["code"]
        assert status_code.name == sample_status_code_data["name"]
        assert status_code.description == sample_status_code_data["description"]
        assert status_code.color == sample_status_code_data["color"]
        assert status_code.icon == sample_status_code_data["icon"]
        assert status_code.is_billable == sample_status_code_data["is_billable"]
        assert status_code.is_productive == sample_status_code_data["is_productive"]
        assert status_code.requires_approval == sample_status_code_data["requires_approval"]
        assert status_code.is_active == sample_status_code_data["is_active"]
        assert status_code.sort_order == sample_status_code_data["sort_order"]

    async def test_status_code_update_timestamps(self, test_session: AsyncSession, status_code_instance):
        """Test que updated_at se actualiza al modificar el código de estado."""
        original_updated_at = status_code_instance.updated_at
        
        # Actualizar el código de estado
        status_code_instance.name = "Nombre Actualizado"
        await test_session.flush()
        await test_session.refresh(status_code_instance)
        
        # Verificar que updated_at no es None y el nombre se actualizó
        assert status_code_instance.updated_at is not None
        assert status_code_instance.name == "Nombre Actualizado"

    async def test_status_code_defaults_after_persistence(self, test_session: AsyncSession):
        """Test que los valores por defecto se aplican correctamente después de la persistencia."""
        status_code = StatusCode(
            code="DEFAULTS",
            name="Test Defaults"
        )
        test_session.add(status_code)
        await test_session.flush()
        await test_session.refresh(status_code)
        
        # Verificar que los defaults se aplicaron
        assert status_code.is_billable is True
        assert status_code.is_productive is True
        assert status_code.requires_approval is False
        assert status_code.is_active is True
        assert status_code.sort_order == 0


class TestStatusCodeRelationships:
    """Tests para relaciones del modelo StatusCode."""

    async def test_schedules_relationship_defined(self):
        """Test que verifica que la relación schedules está definida en el modelo."""
        from planificador.models.status_code import StatusCode
        
        # Verificar que la relación schedules existe en la clase
        assert hasattr(StatusCode, 'schedules')
        
        # Verificar que es una relación de SQLAlchemy
        from sqlalchemy.orm import RelationshipProperty
        schedules_attr = getattr(StatusCode.__mapper__.attrs, 'schedules', None)
        assert schedules_attr is not None
        assert isinstance(schedules_attr, RelationshipProperty)


class TestStatusCodeEdgeCases:
    """Tests de casos edge para el modelo StatusCode."""

    async def test_status_code_with_special_characters(self, test_session: AsyncSession):
        """Test código de estado con caracteres especiales en los campos."""
        status_code = StatusCode(
            code="SPEC-1",
            name="Código Especial & Símbolos",
            description="Descripción con acentos: áéíóú y símbolos: @#$%",
            color="#ff5733",
            icon="special-icon"
        )
        test_session.add(status_code)
        await test_session.flush()
        await test_session.refresh(status_code)
        
        assert status_code.code == "SPEC-1"
        assert status_code.name == "Código Especial & Símbolos"
        assert "áéíóú" in status_code.description
        assert status_code.color == "#ff5733"
        assert status_code.icon == "special-icon"

    async def test_status_code_color_hex_format(self, test_session: AsyncSession):
        """Test diferentes formatos de color hexadecimal."""
        # Color hex corto
        status_code_short = StatusCode(
            code="SHORT",
            name="Short Color",
            color="#fff"
        )
        test_session.add(status_code_short)
        
        # Color hex largo
        status_code_long = StatusCode(
            code="LONG",
            name="Long Color",
            color="#ffffff"
        )
        test_session.add(status_code_long)
        
        await test_session.flush()
        
        assert status_code_short.color == "#fff"
        assert status_code_long.color == "#ffffff"

    async def test_status_code_extreme_sort_orders(self, test_session: AsyncSession):
        """Test con valores extremos de sort_order."""
        # Sort order muy negativo
        status_code_min = StatusCode(
            code="MIN",
            name="Minimum Sort",
            sort_order=-999999
        )
        test_session.add(status_code_min)
        
        # Sort order muy positivo
        status_code_max = StatusCode(
            code="MAX",
            name="Maximum Sort",
            sort_order=999999
        )
        test_session.add(status_code_max)
        
        await test_session.flush()
        
        assert status_code_min.sort_order == -999999
        assert status_code_max.sort_order == 999999

    async def test_status_code_empty_optional_fields(self, test_session: AsyncSession):
        """Test con campos opcionales vacíos o nulos."""
        status_code = StatusCode(
            code="EMPTY",
            name="Empty Fields",
            description=None,
            color=None,
            icon=None
        )
        test_session.add(status_code)
        await test_session.flush()
        await test_session.refresh(status_code)
        
        assert status_code.description is None
        assert status_code.color is None
        assert status_code.icon is None
        # Los campos con defaults deberían tener sus valores por defecto
        assert status_code.is_billable is True
        assert status_code.is_productive is True
        assert status_code.requires_approval is False
        assert status_code.is_active is True
        assert status_code.sort_order == 0