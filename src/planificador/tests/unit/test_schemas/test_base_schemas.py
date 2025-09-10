# src/planificador/tests/unit/test_schemas/test_base_schemas.py
"""
Tests para schemas base del sistema de planificación.

Este módulo contiene tests unitarios para validar el comportamiento
del schema base que sirve como fundamento para todos los demás schemas
del sistema.
"""

import pytest
from pydantic import BaseModel, ValidationError
from planificador.schemas.base.base import BaseSchema


class TestBaseSchema:
    """Tests para el schema base del sistema."""

    def test_base_schema_inheritance(self):
        """Test que BaseSchema hereda correctamente de BaseModel."""
        assert issubclass(BaseSchema, BaseModel)
        assert BaseSchema.__bases__ == (BaseModel,)

    def test_base_schema_config(self):
        """Test configuración del schema base."""
        # Verificar que tiene la configuración correcta
        assert hasattr(BaseSchema, 'model_config')
        config = BaseSchema.model_config
        
        # Verificar que from_attributes está habilitado
        assert config.get('from_attributes') is True

    def test_base_schema_instantiation(self):
        """Test que BaseSchema puede ser instanciado directamente."""
        # BaseSchema debería poder instanciarse sin campos
        schema_instance = BaseSchema()
        assert isinstance(schema_instance, BaseSchema)
        assert isinstance(schema_instance, BaseModel)

    def test_base_schema_with_orm_object(self):
        """Test que BaseSchema puede trabajar con objetos ORM simulados."""
        # Crear una clase que simula un objeto ORM
        class MockORMObject:
            def __init__(self):
                self.id = 1
                self.name = "Test Object"
        
        # Crear un schema derivado para testing
        class TestDerivedSchema(BaseSchema):
            id: int
            name: str
        
        # Crear objeto ORM simulado
        orm_obj = MockORMObject()
        
        # Verificar que puede crear schema desde objeto ORM
        schema_instance = TestDerivedSchema.model_validate(orm_obj)
        assert schema_instance.id == 1
        assert schema_instance.name == "Test Object"

    def test_base_schema_serialization(self):
        """Test serialización del schema base."""
        # Crear un schema derivado simple para testing
        class TestSerializationSchema(BaseSchema):
            test_field: str = "default_value"
        
        schema_instance = TestSerializationSchema()
        
        # Test model_dump
        data_dict = schema_instance.model_dump()
        assert isinstance(data_dict, dict)
        assert data_dict["test_field"] == "default_value"
        
        # Test model_dump_json
        json_str = schema_instance.model_dump_json()
        assert isinstance(json_str, str)
        assert '"test_field"' in json_str
        assert '"default_value"' in json_str

    def test_base_schema_deserialization(self):
        """Test deserialización del schema base."""
        # Crear un schema derivado para testing
        class TestDeserializationSchema(BaseSchema):
            test_field: str
            optional_field: str = "default"
        
        # Test model_validate con dict
        data_dict = {"test_field": "test_value"}
        schema_instance = TestDeserializationSchema.model_validate(data_dict)
        assert schema_instance.test_field == "test_value"
        assert schema_instance.optional_field == "default"
        
        # Test model_validate_json
        json_str = '{"test_field": "json_value", "optional_field": "json_optional"}'
        schema_instance = TestDeserializationSchema.model_validate_json(json_str)
        assert schema_instance.test_field == "json_value"
        assert schema_instance.optional_field == "json_optional"

    def test_base_schema_validation_error(self):
        """Test que BaseSchema maneja errores de validación correctamente."""
        # Crear un schema derivado con validación estricta
        class TestValidationSchema(BaseSchema):
            required_field: str
            numeric_field: int
        
        # Test campo requerido faltante
        with pytest.raises(ValidationError) as exc_info:
            TestValidationSchema(numeric_field=123)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("required_field",) for error in errors)
        assert any(error["type"] == "missing" for error in errors)
        
        # Test tipo incorrecto
        with pytest.raises(ValidationError) as exc_info:
            TestValidationSchema(required_field="test", numeric_field="not_a_number")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("numeric_field",) for error in errors)

    def test_base_schema_field_access(self):
        """Test acceso a campos del schema base."""
        # Crear un schema derivado para testing
        class TestFieldAccessSchema(BaseSchema):
            field1: str
            field2: int = 42
        
        schema_instance = TestFieldAccessSchema(field1="test_value")
        
        # Test acceso directo a campos
        assert schema_instance.field1 == "test_value"
        assert schema_instance.field2 == 42
        
        # Test modificación de campos
        schema_instance.field1 = "modified_value"
        assert schema_instance.field1 == "modified_value"

    def test_base_schema_equality(self):
        """Test comparación de igualdad entre instancias del schema base."""
        # Crear un schema derivado para testing
        class TestEqualitySchema(BaseSchema):
            field1: str
            field2: int
        
        # Crear dos instancias idénticas
        schema1 = TestEqualitySchema(field1="test", field2=123)
        schema2 = TestEqualitySchema(field1="test", field2=123)
        
        # Test igualdad
        assert schema1 == schema2
        
        # Crear instancia diferente
        schema3 = TestEqualitySchema(field1="different", field2=123)
        
        # Test desigualdad
        assert schema1 != schema3

    def test_base_schema_repr(self):
        """Test representación string del schema base."""
        # Crear un schema derivado para testing
        class TestReprSchema(BaseSchema):
            field1: str
            field2: int
        
        schema_instance = TestReprSchema(field1="test", field2=123)
        
        # Test __repr__
        repr_str = repr(schema_instance)
        assert "TestReprSchema" in repr_str
        assert "field1='test'" in repr_str
        assert "field2=123" in repr_str

    def test_base_schema_copy(self):
        """Test copia de instancias del schema base."""
        # Crear un schema derivado para testing
        class TestCopySchema(BaseSchema):
            field1: str
            field2: int
        
        original = TestCopySchema(field1="original", field2=123)
        
        # Test copia sin modificaciones
        copy_instance = original.model_copy()
        assert copy_instance == original
        assert copy_instance is not original  # Diferentes objetos
        
        # Test copia con modificaciones
        modified_copy = original.model_copy(update={"field1": "modified"})
        assert modified_copy.field1 == "modified"
        assert modified_copy.field2 == 123
        assert modified_copy != original

    def test_base_schema_fields_info(self):
        """Test información de campos del schema base."""
        # Crear un schema derivado para testing
        class TestFieldsInfoSchema(BaseSchema):
            required_field: str
            optional_field: str = "default"
            numeric_field: int
        
        # Test model_fields
        fields = TestFieldsInfoSchema.model_fields
        assert "required_field" in fields
        assert "optional_field" in fields
        assert "numeric_field" in fields
        
        # Verificar información de campo opcional
        optional_field_info = fields["optional_field"]
        assert optional_field_info.default == "default"
        
        # Test model_json_schema
        json_schema = TestFieldsInfoSchema.model_json_schema()
        assert "properties" in json_schema
        assert "required_field" in json_schema["properties"]
        assert "optional_field" in json_schema["properties"]
        assert "numeric_field" in json_schema["properties"]


class TestBaseSchemaEdgeCases:
    """Tests de casos edge para el schema base."""

    def test_empty_schema_derivation(self):
        """Test derivación de schema vacío."""
        class EmptyDerivedSchema(BaseSchema):
            pass
        
        # Debería poder instanciarse sin problemas
        empty_schema = EmptyDerivedSchema()
        assert isinstance(empty_schema, BaseSchema)
        assert isinstance(empty_schema, BaseModel)

    def test_multiple_inheritance_compatibility(self):
        """Test compatibilidad con herencia múltiple."""
        class Mixin:
            def custom_method(self):
                return "mixin_method"
        
        class MultipleInheritanceSchema(BaseSchema, Mixin):
            field: str
        
        schema_instance = MultipleInheritanceSchema(field="test")
        assert schema_instance.field == "test"
        assert schema_instance.custom_method() == "mixin_method"

    def test_nested_schema_with_base(self):
        """Test schemas anidados usando BaseSchema."""
        class NestedSchema(BaseSchema):
            nested_field: str
        
        class ParentSchema(BaseSchema):
            parent_field: str
            nested: NestedSchema
        
        nested_data = {"nested_field": "nested_value"}
        parent_data = {
            "parent_field": "parent_value",
            "nested": nested_data
        }
        
        parent_instance = ParentSchema.model_validate(parent_data)
        assert parent_instance.parent_field == "parent_value"
        assert parent_instance.nested.nested_field == "nested_value"
        assert isinstance(parent_instance.nested, NestedSchema)

    def test_schema_with_complex_types(self):
        """Test schema con tipos complejos usando BaseSchema."""
        from typing import List, Dict, Optional
        from datetime import datetime
        
        class ComplexTypeSchema(BaseSchema):
            string_list: List[str]
            string_dict: Dict[str, str]
            optional_datetime: Optional[datetime] = None
        
        complex_data = {
            "string_list": ["item1", "item2", "item3"],
            "string_dict": {"key1": "value1", "key2": "value2"},
            "optional_datetime": "2024-01-01T12:00:00"
        }
        
        schema_instance = ComplexTypeSchema.model_validate(complex_data)
        assert schema_instance.string_list == ["item1", "item2", "item3"]
        assert schema_instance.string_dict == {"key1": "value1", "key2": "value2"}
        assert isinstance(schema_instance.optional_datetime, datetime)

    def test_schema_config_inheritance(self):
        """Test que la configuración se hereda correctamente."""
        class DerivedSchema(BaseSchema):
            field: str
        
        # Verificar que la configuración se hereda
        assert hasattr(DerivedSchema, 'model_config')
        config = DerivedSchema.model_config
        assert config.get('from_attributes') is True
        
        # Verificar que funciona con objetos ORM simulados
        class MockORM:
            def __init__(self):
                self.field = "orm_value"
        
        orm_obj = MockORM()
        schema_instance = DerivedSchema.model_validate(orm_obj)
        assert schema_instance.field == "orm_value"