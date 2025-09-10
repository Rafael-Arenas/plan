# src/planificador/tests/unit/test_schemas/fixtures/base.py
"""
Fixtures para testing de schemas base.

Este módulo proporciona fixtures reutilizables para testing
del schema base y schemas derivados del mismo.
"""

import pytest
from datetime import datetime, date
from typing import List, Dict, Optional
from planificador.schemas.base.base import BaseSchema


@pytest.fixture
def simple_derived_schema_class():
    """Clase de schema derivado simple para testing."""
    class SimpleDerivedSchema(BaseSchema):
        name: str
        value: int = 42
    
    return SimpleDerivedSchema


@pytest.fixture
def complex_derived_schema_class():
    """Clase de schema derivado complejo para testing."""
    class ComplexDerivedSchema(BaseSchema):
        required_string: str
        optional_string: Optional[str] = None
        integer_value: int
        float_value: float = 3.14
        boolean_value: bool = True
        datetime_value: Optional[datetime] = None
        date_value: Optional[date] = None
        string_list: List[str] = []
        string_dict: Dict[str, str] = {}
    
    return ComplexDerivedSchema


@pytest.fixture
def nested_schema_classes():
    """Clases de schemas anidados para testing."""
    class NestedSchema(BaseSchema):
        nested_field: str
        nested_value: int
    
    class ParentSchema(BaseSchema):
        parent_field: str
        nested: NestedSchema
        nested_list: List[NestedSchema] = []
    
    return {
        "nested": NestedSchema,
        "parent": ParentSchema
    }


@pytest.fixture
def valid_simple_data():
    """Datos válidos para schema derivado simple."""
    return {
        "name": "Test Schema",
        "value": 100
    }


@pytest.fixture
def valid_complex_data():
    """Datos válidos para schema derivado complejo."""
    return {
        "required_string": "Required Value",
        "optional_string": "Optional Value",
        "integer_value": 123,
        "float_value": 456.789,
        "boolean_value": False,
        "datetime_value": "2024-01-01T12:00:00",
        "date_value": "2024-01-01",
        "string_list": ["item1", "item2", "item3"],
        "string_dict": {"key1": "value1", "key2": "value2"}
    }


@pytest.fixture
def valid_nested_data():
    """Datos válidos para schemas anidados."""
    return {
        "parent_field": "Parent Value",
        "nested": {
            "nested_field": "Nested Value",
            "nested_value": 42
        },
        "nested_list": [
            {
                "nested_field": "First Nested",
                "nested_value": 1
            },
            {
                "nested_field": "Second Nested",
                "nested_value": 2
            }
        ]
    }


@pytest.fixture
def invalid_data_missing_required():
    """Datos inválidos con campos requeridos faltantes."""
    return {
        "optional_string": "Only optional field",
        "integer_value": 123
        # Falta required_string
    }


@pytest.fixture
def invalid_data_wrong_types():
    """Datos inválidos con tipos incorrectos."""
    return {
        "required_string": "Valid String",
        "integer_value": "not_an_integer",  # Tipo incorrecto
        "float_value": "not_a_float",      # Tipo incorrecto
        "boolean_value": "not_a_boolean",  # Tipo incorrecto
        "datetime_value": "invalid_datetime",  # Formato incorrecto
        "date_value": "invalid_date",      # Formato incorrecto
        "string_list": "not_a_list",       # Tipo incorrecto
        "string_dict": "not_a_dict"        # Tipo incorrecto
    }


@pytest.fixture
def mock_orm_object():
    """Objeto ORM simulado para testing de from_attributes."""
    class MockORMObject:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    return MockORMObject


@pytest.fixture
def valid_orm_data():
    """Datos válidos para crear objeto ORM simulado."""
    return {
        "id": 1,
        "name": "ORM Object",
        "description": "Test ORM object",
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
        "is_active": True
    }


@pytest.fixture
def schema_with_orm_config():
    """Schema derivado configurado para trabajar con ORM."""
    class ORMCompatibleSchema(BaseSchema):
        id: int
        name: str
        description: Optional[str] = None
        created_at: datetime
        is_active: bool = True
    
    return ORMCompatibleSchema


@pytest.fixture
def edge_case_data():
    """Datos para casos edge de testing."""
    return {
        "empty_strings": {
            "required_string": "",
            "integer_value": 0
        },
        "boundary_values": {
            "required_string": "a" * 1000,  # String muy largo
            "integer_value": 2**31 - 1,     # Valor máximo int32
            "float_value": 1.7976931348623157e+308,  # Valor máximo float
            "string_list": ["item"] * 1000,  # Lista muy larga
            "string_dict": {f"key{i}": f"value{i}" for i in range(100)}  # Dict grande
        },
        "special_characters": {
            "required_string": "Special chars: áéíóú ñ ¿¡ @#$%^&*()_+-=[]{}|;':,.<>?",
            "integer_value": 42
        },
        "unicode_data": {
            "required_string": "Unicode: 你好 🌟 Ω α β γ δ ε",
            "integer_value": 42
        }
    }


@pytest.fixture
def serialization_test_data():
    """Datos para testing de serialización/deserialización."""
    return {
        "json_string": '{"required_string": "JSON Value", "integer_value": 999}',
        "dict_data": {"required_string": "Dict Value", "integer_value": 888},
        "expected_json_keys": ["required_string", "integer_value"],
        "expected_serialized_types": {
            "required_string": str,
            "integer_value": int
        }
    }


@pytest.fixture
def validation_error_cases():
    """Casos que deben generar ValidationError."""
    return [
        {
            "name": "missing_required_field",
            "data": {"integer_value": 123},  # Falta required_string
            "expected_error_field": "required_string",
            "expected_error_type": "missing"
        },
        {
            "name": "wrong_type_integer",
            "data": {"required_string": "Valid", "integer_value": "not_int"},
            "expected_error_field": "integer_value",
            "expected_error_type": "int_parsing"
        },
        {
            "name": "wrong_type_boolean",
            "data": {"required_string": "Valid", "integer_value": 123, "boolean_value": "not_bool"},
            "expected_error_field": "boolean_value",
            "expected_error_type": "bool_parsing"
        },
        {
            "name": "invalid_datetime",
            "data": {"required_string": "Valid", "integer_value": 123, "datetime_value": "invalid"},
            "expected_error_field": "datetime_value",
            "expected_error_type": "datetime_parsing"
        }
    ]


@pytest.fixture
def performance_test_data():
    """Datos para testing de performance."""
    return {
        "large_dataset": [
            {
                "required_string": f"Item {i}",
                "integer_value": i,
                "string_list": [f"subitem_{i}_{j}" for j in range(10)]
            }
            for i in range(1000)
        ],
        "nested_large_dataset": {
            "parent_field": "Large Parent",
            "nested_list": [
                {
                    "nested_field": f"Nested {i}",
                    "nested_value": i
                }
                for i in range(500)
            ]
        }
    }


@pytest.fixture
def schema_comparison_data():
    """Datos para testing de comparación entre schemas."""
    return {
        "identical_data_1": {"required_string": "Same", "integer_value": 42},
        "identical_data_2": {"required_string": "Same", "integer_value": 42},
        "different_data": {"required_string": "Different", "integer_value": 99},
        "partial_different_data": {"required_string": "Same", "integer_value": 99}
    }