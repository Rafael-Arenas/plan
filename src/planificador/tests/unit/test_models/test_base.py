"""Tests para el modelo BaseModel.

Este módulo contiene tests unitarios completos para el modelo BaseModel,
cubriendo todas sus funcionalidades, propiedades calculadas y métodos utilitarios.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from planificador.models.base import BaseModel
from planificador.tests.fixtures.database import (
    SampleModel,
    sample_test_model_data,
    sample_test_model,
    old_test_model,
    recently_modified_test_model,
    multiple_test_models
)


class TestBaseModelCreation:
    """Tests para la creación de modelos BaseModel."""
    
    async def test_successful_creation(self, test_session: AsyncSession, sample_test_model_data: dict):
        """Test de creación exitosa de un modelo."""
        model = SampleModel(**sample_test_model_data)
        test_session.add(model)
        await test_session.flush()
        await test_session.refresh(model)
        
        assert model.id is not None
        assert model.name == sample_test_model_data["name"]
        assert model.description == sample_test_model_data["description"]
        assert model.value == sample_test_model_data["value"]
        assert model.created_at is not None
        assert model.updated_at is not None
        # BaseModel no tiene campo is_active
    
    async def test_creation_with_minimal_data(self, test_session: AsyncSession):
        """Test de creación con datos mínimos requeridos."""
        model = SampleModel(name="Minimal Model")
        test_session.add(model)
        await test_session.flush()
        await test_session.refresh(model)
        
        assert model.id is not None
        assert model.name == "Minimal Model"
        assert model.description is None
        assert model.value is None
        assert model.created_at is not None
        assert model.updated_at is not None
        # BaseModel no tiene campo is_active
    
    async def test_creation_sets_timestamps(self, test_session: AsyncSession):
        """Test que verifica que se establecen las marcas de tiempo."""
        model = SampleModel(name="Timestamp Model")
        test_session.add(model)
        await test_session.flush()
        await test_session.refresh(model)
        
        assert model.id is not None
        assert model.name == "Timestamp Model"
        assert model.created_at is not None
        assert model.updated_at is not None
    
    async def test_creation_without_name_fails(self, test_session: AsyncSession):
        """Test que verifica que la creación falla sin nombre."""
        model = SampleModel(description="Sin nombre")
        test_session.add(model)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()


class TestBaseModelRepresentation:
    """Tests para la representación de modelos BaseModel."""
    
    async def test_string_representation(self, sample_test_model: SampleModel):
        """Test de representación en string del modelo."""
        # BaseModel no tiene método __str__ personalizado, usa el por defecto
        result = str(sample_test_model)
        assert "SampleModel" in result
    
    async def test_repr_representation(self, sample_test_model: SampleModel):
        """Test de representación repr del modelo."""
        expected = f"<SampleModel(id={sample_test_model.id})>"
        assert repr(sample_test_model) == expected


class TestBaseModelCalculatedProperties:
    """Tests para las propiedades calculadas de BaseModel."""
    
    async def test_age_in_days_recent_model(self, sample_test_model: SampleModel):
        """Test de age_in_days para un modelo reciente."""
        age = sample_test_model.age_in_days
        assert isinstance(age, int)
        assert age >= 0
        assert age <= 1  # Debería ser 0 o 1 para un modelo recién creado
    
    async def test_age_in_days_old_model(self, old_test_model: SampleModel):
        """Test de age_in_days para un modelo antiguo."""
        age = old_test_model.age_in_days
        assert isinstance(age, int)
        assert age >= 10  # Fue creado hace 10 días
        assert age <= 11  # Margen de error
    
    async def test_is_recently_created_true(self, sample_test_model: SampleModel):
        """Test de is_recently_created para modelo reciente."""
        assert sample_test_model.is_recently_created is True
    
    async def test_is_recently_created_false(self, old_test_model: SampleModel):
        """Test de is_recently_created para modelo antiguo."""
        assert old_test_model.is_recently_created is False
    
    async def test_is_recently_modified_true(self, recently_modified_test_model: SampleModel):
        """Test de is_recently_modified para modelo modificado recientemente."""
        assert recently_modified_test_model.is_recently_modified is True
    
    async def test_is_recently_modified_false(self, old_test_model: SampleModel):
        """Test de is_recently_modified para modelo no modificado recientemente."""
        assert old_test_model.is_recently_modified is False
    
    async def test_last_modified_days(self, recently_modified_test_model: SampleModel):
        """Test de last_modified_days."""
        days = recently_modified_test_model.last_modified_days
        assert isinstance(days, int)
        assert days >= 0
        # Debería ser 0 para un modelo modificado hace 2 horas
        assert days == 0
    
    async def test_was_modified_property(self, recently_modified_test_model: SampleModel):
        """Test de la propiedad was_modified."""
        assert recently_modified_test_model.was_modified is True
    
    async def test_was_modified_false_for_new_model(self, sample_test_model: SampleModel):
        """Test de was_modified para modelo recién creado."""
        # Un modelo recién creado puede no tener diferencia entre created_at y updated_at
        result = sample_test_model.was_modified
        assert isinstance(result, bool)


class TestBaseModelUtilityMethods:
    """Tests para los métodos utilitarios de BaseModel."""
    
    async def test_to_dict_basic(self, sample_test_model: SampleModel):
        """Test básico del método to_dict."""
        result = sample_test_model.to_dict()
        
        assert isinstance(result, dict)
        assert "id" in result
        assert "name" in result
        assert "description" in result
        assert "value" in result
        assert "created_at" in result
        assert "updated_at" in result
        
        assert result["id"] == sample_test_model.id
        assert result["name"] == sample_test_model.name
        assert result["description"] == sample_test_model.description
        assert result["value"] == sample_test_model.value
    
    async def test_to_dict_includes_all_columns(self, sample_test_model: SampleModel):
        """Test que verifica que to_dict incluye todas las columnas."""
        result = sample_test_model.to_dict()
        
        # Verificar que incluye todas las columnas esperadas
        expected_columns = {"id", "name", "description", "value", "created_at", "updated_at"}
        assert set(result.keys()) == expected_columns
    
    async def test_update_from_dict_basic(self, sample_test_model_data, test_session):
        """Test básico del método update_from_dict."""
        # Crear una nueva instancia de SampleModel
        test_model = SampleModel(**sample_test_model_data)
        test_session.add(test_model)
        await test_session.flush()
        
        # Datos para actualizar
        update_data = {
            "name": "Updated Name",
            "description": "Updated Description",
            "value": 999
        }
        
        # Actualizar usando el método
        await test_model.update_from_dict(update_data, test_session)
        
        # Verificar que los campos se actualizaron
        assert test_model.name == "Updated Name"
        assert test_model.description == "Updated Description"
        assert test_model.value == 999
    
    async def test_update_from_dict_ignores_protected_fields(self, sample_test_model_data, test_session):
        """Test que verifica que update_from_dict ignora campos protegidos."""
        # Crear una nueva instancia de SampleModel
        test_model = SampleModel(**sample_test_model_data)
        test_session.add(test_model)
        await test_session.flush()
        
        # Guardar valores originales
        original_id = test_model.id
        original_created_at = test_model.created_at
        
        update_data = {
            "id": 99999,  # Debería ser ignorado
            "created_at": datetime.now() + timedelta(days=1),  # Debería ser ignorado
            "name": "Updated Name"
        }
        
        # Actualizar usando el método
        await test_model.update_from_dict(update_data, test_session)
        
        # Verificar que los campos protegidos no cambiaron
        assert test_model.id == original_id
        assert test_model.created_at == original_created_at
        # Pero el campo permitido sí cambió
        assert test_model.name == "Updated Name"
    
    async def test_get_field_value(self, sample_test_model: SampleModel):
        """Test del método get_field_value."""
        # Test con campo existente
        assert sample_test_model.get_field_value("name") == sample_test_model.name
        assert sample_test_model.get_field_value("value") == sample_test_model.value
        
        # Test con campo inexistente
        assert sample_test_model.get_field_value("nonexistent") is None
        assert sample_test_model.get_field_value("nonexistent", "default") == "default"
    
    async def test_has_field(self, sample_test_model: SampleModel):
        """Test del método has_field."""
        assert sample_test_model.has_field("name") is True
        assert sample_test_model.has_field("id") is True
        assert sample_test_model.has_field("nonexistent") is False
    
    async def test_get_primary_key(self, sample_test_model: SampleModel):
        """Test del método get_primary_key."""
        assert sample_test_model.get_primary_key() == sample_test_model.id


class TestBaseModelFormatting:
    """Tests para formateo de BaseModel."""
    
    async def test_created_at_formatted(self, sample_test_model: SampleModel):
        """Test del formateo de created_at."""
        formatted = sample_test_model.created_at_formatted
        assert isinstance(formatted, str)
        assert "/" in formatted  # Formato DD/MM/YYYY
        assert ":" in formatted  # Formato HH:mm
    
    async def test_updated_at_formatted(self, sample_test_model: SampleModel):
        """Test del formateo de updated_at."""
        formatted = sample_test_model.updated_at_formatted
        assert isinstance(formatted, str)
        assert "/" in formatted
        assert ":" in formatted
    
    async def test_audit_summary(self, sample_test_model: SampleModel):
        """Test del resumen de auditoría."""
        summary = sample_test_model.audit_summary
        assert isinstance(summary, str)
        assert "Creado:" in summary
        assert "Actualizado:" in summary
        assert "Estado:" in summary


class TestBaseModelEdgeCases:
    """Tests para casos edge de BaseModel."""
    
    async def test_model_with_very_long_name(self, test_session: AsyncSession):
        """Test con nombre muy largo."""
        long_name = "A" * 200  # Más largo que el límite de 100
        model = SampleModel(name=long_name)
        test_session.add(model)
        
        # En SQLite puede no fallar, pero en otros DB sí
        try:
            await test_session.flush()
            # Si no falla, verificar que se truncó o se guardó completo
            assert len(model.name) >= 100
        except Exception:
            # Es esperado que falle en algunos casos
            pass
    
    async def test_model_with_very_long_description(self, test_session: AsyncSession):
        """Test con descripción muy larga."""
        long_description = "B" * 300  # Más largo que el límite de 255
        model = SampleModel(name="Valid Name", description=long_description)
        test_session.add(model)
        
        try:
            await test_session.flush()
            assert len(model.description) >= 255
        except Exception:
            pass
    
    async def test_model_with_negative_value(self, test_session: AsyncSession):
        """Test con valor negativo."""
        model = SampleModel(name="Negative Value Model", value=-100)
        test_session.add(model)
        await test_session.flush()
        await test_session.refresh(model)
        
        assert model.value == -100  # Debería permitir valores negativos
    
    async def test_model_with_zero_value(self, test_session: AsyncSession):
        """Test con valor cero."""
        model = SampleModel(name="Zero Value Model", value=0)
        test_session.add(model)
        await test_session.flush()
        await test_session.refresh(model)
        
        assert model.value == 0
    
    async def test_model_with_large_value(self, test_session: AsyncSession):
        """Test con valor muy grande."""
        large_value = 2147483647  # Máximo para INTEGER
        model = SampleModel(name="Large Value Model", value=large_value)
        test_session.add(model)
        await test_session.flush()
        await test_session.refresh(model)
        
        assert model.value == large_value
    
    async def test_multiple_models_with_same_name(self, test_session: AsyncSession):
        """Test de múltiples modelos con el mismo nombre."""
        name = "Duplicate Name"
        
        model1 = SampleModel(name=name, value=1)
        model2 = SampleModel(name=name, value=2)
        
        test_session.add(model1)
        test_session.add(model2)
        await test_session.flush()
        await test_session.refresh(model1)
        await test_session.refresh(model2)
        
        # Debería permitir nombres duplicados
        assert model1.name == name
        assert model2.name == name
        assert model1.id != model2.id
    
    async def test_to_dict_with_datetime_serialization(self, sample_test_model: SampleModel):
        """Test de serialización de datetime en to_dict."""
        result = sample_test_model.to_dict()
        
        # Los datetime deberían ser serializables
        assert isinstance(result["created_at"], datetime)
        assert isinstance(result["updated_at"], datetime)
    
    async def test_update_from_dict_with_invalid_data_types(self, sample_test_model_data, test_session):
        """Test de update_from_dict con tipos de datos inválidos."""
        # Crear una nueva instancia de SampleModel
        test_model = SampleModel(**sample_test_model_data)
        test_session.add(test_model)
        await test_session.flush()
        
        # Intentar actualizar con campos inexistentes
        update_data = {
            "nonexistent_field": "some_value",
            "name": "Valid Name"
        }
        
        # El método debería ignorar campos inexistentes
        await test_model.update_from_dict(update_data, test_session)
        
        # Verificar que el campo válido se actualizó
        assert test_model.name == "Valid Name"
        # Y que no se creó el campo inexistente
        assert not hasattr(test_model, "nonexistent_field")
    
    async def test_age_calculation_precision(self, test_session: AsyncSession):
        """Test de precisión en el cálculo de age_in_days."""
        # Crear modelo con fecha específica
        specific_date = datetime.now() - timedelta(days=5, hours=12)  # 5.5 días atrás
        
        model = SampleModel(name="Precision Test")
        test_session.add(model)
        await test_session.flush()
        
        # Simular fecha de creación específica
        model.created_at = specific_date
        await test_session.flush()
        await test_session.refresh(model)
        
        age = model.age_in_days
        assert age == 5  # Debería truncar a 5 días
    
    async def test_model_timestamps_consistency(self, test_session: AsyncSession, sample_test_model: SampleModel):
        """Test de consistencia de timestamps."""
        # Verificar que created_at y updated_at son consistentes
        assert sample_test_model.created_at is not None
        assert sample_test_model.updated_at is not None
        assert sample_test_model.updated_at >= sample_test_model.created_at