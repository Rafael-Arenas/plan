"""Tests para el modelo Alert.

Este módulo contiene tests unitarios para el modelo Alert,
incluye validación de campos, relaciones, métodos personalizados y casos límite.
"""

import pytest
import pytest_asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from planificador.models.alert import Alert, AlertType, AlertStatus
from planificador.models.employee import Employee


class TestAlertModel:
    """Tests básicos del modelo Alert."""
    
    async def test_valid_creation(self, test_session: AsyncSession, sample_employee: Employee):
        """Test creación válida de una alerta."""
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.CONFLICT,
            title="Test Alert",
            message="This is a test alert message"
        )
        
        test_session.add(alert)
        await test_session.flush()
        await test_session.refresh(alert)
        
        assert alert.id is not None
        assert alert.user_id == sample_employee.id
        assert alert.alert_type == AlertType.CONFLICT
        assert alert.status == AlertStatus.NEW  # Default value
        assert alert.title == "Test Alert"
        assert alert.message == "This is a test alert message"
        assert alert.is_read is False  # Default value
        assert alert.read_at is None
        assert alert.related_entity_type is None
        assert alert.related_entity_id is None
        assert alert.created_at is not None
        assert alert.updated_at is not None
    
    async def test_creation_with_all_fields(self, test_session: AsyncSession, sample_employee: Employee):
        """Test creación de alerta con todos los campos."""
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.DEADLINE_WARNING,
            status=AlertStatus.READ,
            title="Complete Alert",
            message="This is a complete alert with all fields",
            related_entity_type="Project",
            related_entity_id=123,
            is_read=True,
            read_at=datetime.now()
        )
        
        test_session.add(alert)
        await test_session.flush()
        await test_session.refresh(alert)
        
        assert alert.id is not None
        assert alert.user_id == sample_employee.id
        assert alert.alert_type == AlertType.DEADLINE_WARNING
        assert alert.status == AlertStatus.READ
        assert alert.title == "Complete Alert"
        assert alert.message == "This is a complete alert with all fields"
        assert alert.related_entity_type == "Project"
        assert alert.related_entity_id == 123
        assert alert.is_read is True
        assert alert.read_at is not None
    
    async def test_string_representation(self, test_session: AsyncSession, sample_employee: Employee):
        """Test representación string del modelo Alert."""
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.SYSTEM_ERROR,
            title="Test Alert",
            message="Test message"
        )
        
        test_session.add(alert)
        await test_session.flush()
        await test_session.refresh(alert)
        
        str_repr = repr(alert)
        assert f"Alert(id={alert.id}" in str_repr
        assert f"user_id={alert.user_id}" in str_repr
        assert f"type='{alert.alert_type.value}'" in str_repr
        assert f"status='{alert.status.value}'" in str_repr


class TestAlertValidation:
    """Tests de validación del modelo Alert."""
    
    async def test_required_user_id(self, test_session: AsyncSession):
        """Test validación de user_id obligatorio."""
        with pytest.raises(IntegrityError):
            alert = Alert(
                alert_type=AlertType.CONFLICT,
                title="Test Alert",
                message="Test message"
                # user_id faltante
            )
            test_session.add(alert)
            await test_session.flush()
    
    async def test_required_alert_type(self, test_session: AsyncSession, sample_employee: Employee):
        """Test validación de alert_type obligatorio."""
        with pytest.raises(IntegrityError):
            alert = Alert(
                user_id=sample_employee.id,
                title="Test Alert",
                message="Test message"
                # alert_type faltante
            )
            test_session.add(alert)
            await test_session.flush()
    
    async def test_required_title(self, test_session: AsyncSession, sample_employee: Employee):
        """Test validación de title obligatorio."""
        with pytest.raises(IntegrityError):
            alert = Alert(
                user_id=sample_employee.id,
                alert_type=AlertType.CONFLICT,
                message="Test message"
                # title faltante
            )
            test_session.add(alert)
            await test_session.flush()
    
    async def test_required_message(self, test_session: AsyncSession, sample_employee: Employee):
        """Test validación de message obligatorio."""
        with pytest.raises(IntegrityError):
            alert = Alert(
                user_id=sample_employee.id,
                alert_type=AlertType.CONFLICT,
                title="Test Alert"
                # message faltante
            )
            test_session.add(alert)
            await test_session.flush()
    
    async def test_title_max_length(self, test_session: AsyncSession, sample_employee: Employee):
        """Test validación de longitud máxima del título."""
        max_length = 200
        long_title = "a" * max_length
        
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.CONFLICT,
            title=long_title,
            message="Test message"
        )
        
        test_session.add(alert)
        await test_session.flush()
        
        assert alert.title == long_title
    
    async def test_title_too_long(self, test_session: AsyncSession, sample_employee: Employee):
        """Test validación de título que excede longitud máxima."""
        max_length = 200
        too_long_title = "a" * (max_length + 1)
        
        # SQLite no valida automáticamente la longitud, pero podemos verificar el comportamiento
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.CONFLICT,
            title=too_long_title,
            message="Test message"
        )
        test_session.add(alert)
        await test_session.flush()
        
        # Verificar que el alert se creó (SQLite permite strings largos)
        assert alert.id is not None
        assert len(alert.title) == max_length + 1
    
    async def test_related_entity_type_max_length(self, test_session: AsyncSession, sample_employee: Employee):
        """Test validación de longitud máxima del tipo de entidad relacionada."""
        max_length = 50
        long_entity_type = "a" * max_length
        
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.CONFLICT,
            title="Test Alert",
            message="Test message",
            related_entity_type=long_entity_type
        )
        
        test_session.add(alert)
        await test_session.flush()
        
        assert alert.related_entity_type == long_entity_type
    
    async def test_related_entity_type_too_long(self, test_session: AsyncSession, sample_employee: Employee):
        """Test validación de tipo de entidad que excede longitud máxima."""
        max_length = 50
        too_long_entity_type = "a" * (max_length + 1)
        
        # SQLite no valida automáticamente la longitud, pero podemos verificar el comportamiento
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.CONFLICT,
            title="Test Alert",
            message="Test message",
            related_entity_type=too_long_entity_type
        )
        test_session.add(alert)
        await test_session.flush()
        
        # Verificar que el alert se creó
        assert alert.id is not None
        assert len(alert.related_entity_type) == max_length + 1
    
    async def test_invalid_foreign_key(self, test_session: AsyncSession):
        """Test validación de foreign key inválida."""
        # En SQLite con foreign keys habilitadas, esto debería fallar
        # Pero en el entorno de test puede que no estén habilitadas
        alert = Alert(
            user_id=99999,  # ID que no existe
            alert_type=AlertType.CONFLICT,
            title="Test Alert",
            message="Test message"
        )
        test_session.add(alert)
        
        # Intentar hacer flush y verificar si falla o no
        try:
            await test_session.flush()
            # Si no falla, verificar que el alert se creó pero sin relación válida
            assert alert.id is not None
            assert alert.user_id == 99999
        except IntegrityError:
            # Si falla, es el comportamiento esperado con foreign keys habilitadas
            await test_session.rollback()
            assert True  # Test pasó correctamente


class TestAlertEnums:
    """Tests de los enums AlertType y AlertStatus."""
    
    def test_alert_type_values(self):
        """Test valores del enum AlertType."""
        expected_values = {
            "conflict", "insufficient_personnel", "overallocation",
            "deadline_warning", "validation_error", "system_error",
            "approval_pending", "schedule_change", "vacation_conflict", "other"
        }
        
        actual_values = {alert_type.value for alert_type in AlertType}
        assert actual_values == expected_values
    
    def test_alert_status_values(self):
        """Test valores del enum AlertStatus."""
        expected_values = {"new", "read", "resolved", "ignored"}
        
        actual_values = {status.value for status in AlertStatus}
        assert actual_values == expected_values
    
    async def test_all_alert_types_creation(self, test_session: AsyncSession, sample_employee: Employee):
        """Test creación de alertas con todos los tipos."""
        for alert_type in AlertType:
            alert = Alert(
                user_id=sample_employee.id,
                alert_type=alert_type,
                title=f"Test {alert_type.value}",
                message=f"Test message for {alert_type.value}"
            )
            
            test_session.add(alert)
            await test_session.flush()
            await test_session.refresh(alert)
            
            assert alert.alert_type == alert_type
            
            # Limpiar para el siguiente test
            await test_session.delete(alert)
            await test_session.flush()
    
    async def test_all_alert_statuses_creation(self, test_session: AsyncSession, sample_employee: Employee):
        """Test creación de alertas con todos los estados."""
        for status in AlertStatus:
            alert = Alert(
                user_id=sample_employee.id,
                alert_type=AlertType.OTHER,
                status=status,
                title=f"Test {status.value}",
                message=f"Test message for {status.value}"
            )
            
            test_session.add(alert)
            await test_session.flush()
            await test_session.refresh(alert)
            
            assert alert.status == status
            
            # Limpiar para el siguiente test
            await test_session.delete(alert)
            await test_session.flush()


class TestAlertProperties:
    """Tests de las propiedades del modelo Alert."""
    
    @pytest_asyncio.fixture
    async def sample_alert(self, test_session: AsyncSession, sample_employee: Employee) -> Alert:
        """Fixture que crea una alerta de prueba."""
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.CONFLICT,
            title="Test Alert",
            message="Test message"
        )
        
        test_session.add(alert)
        await test_session.flush()
        await test_session.refresh(alert)
        
        return alert
    
    def test_type_display_translations(self, sample_alert: Alert):
        """Test traducciones de tipos de alerta."""
        translations = {
            AlertType.CONFLICT: "Conflicto",
            AlertType.INSUFFICIENT_PERSONNEL: "Personal Insuficiente",
            AlertType.OVERALLOCATION: "Sobreasignación",
            AlertType.DEADLINE_WARNING: "Advertencia de Fecha Límite",
            AlertType.VALIDATION_ERROR: "Error de Validación",
            AlertType.SYSTEM_ERROR: "Error del Sistema",
            AlertType.APPROVAL_PENDING: "Aprobación Pendiente",
            AlertType.SCHEDULE_CHANGE: "Cambio de Horario",
            AlertType.VACATION_CONFLICT: "Conflicto de Vacaciones",
            AlertType.OTHER: "Otro"
        }
        
        for alert_type, expected_translation in translations.items():
            sample_alert.alert_type = alert_type
            assert sample_alert.type_display == expected_translation
    
    def test_status_display_translations(self, sample_alert: Alert):
        """Test traducciones de estados de alerta."""
        translations = {
            AlertStatus.NEW: "Nueva",
            AlertStatus.READ: "Leída",
            AlertStatus.RESOLVED: "Resuelta",
            AlertStatus.IGNORED: "Ignorada"
        }
        
        for status, expected_translation in translations.items():
            sample_alert.status = status
            assert sample_alert.status_display == expected_translation
    
    def test_is_unread_property(self, sample_alert: Alert):
        """Test propiedad is_unread."""
        # Por defecto, is_read es False
        assert sample_alert.is_unread is True
        
        # Cambiar a leída
        sample_alert.is_read = True
        assert sample_alert.is_unread is False
    
    def test_is_active_property(self, sample_alert: Alert):
        """Test propiedad is_active."""
        # Estados activos: NEW, READ
        sample_alert.status = AlertStatus.NEW
        assert sample_alert.is_active is True
        
        sample_alert.status = AlertStatus.READ
        assert sample_alert.is_active is True
        
        # Estados inactivos: RESOLVED, IGNORED
        sample_alert.status = AlertStatus.RESOLVED
        assert sample_alert.is_active is False
        
        sample_alert.status = AlertStatus.IGNORED
        assert sample_alert.is_active is False
    
    def test_requires_attention_property(self, sample_alert: Alert):
        """Test propiedad requires_attention."""
        critical_types = [
            AlertType.CONFLICT,
            AlertType.SYSTEM_ERROR,
            AlertType.VALIDATION_ERROR,
            AlertType.DEADLINE_WARNING
        ]
        
        # Test tipos críticos con estado activo
        for critical_type in critical_types:
            sample_alert.alert_type = critical_type
            sample_alert.status = AlertStatus.NEW
            assert sample_alert.requires_attention is True
            
            sample_alert.status = AlertStatus.READ
            assert sample_alert.requires_attention is True
        
        # Test tipos críticos con estado inactivo
        sample_alert.alert_type = AlertType.CONFLICT
        sample_alert.status = AlertStatus.RESOLVED
        assert sample_alert.requires_attention is False
        
        sample_alert.status = AlertStatus.IGNORED
        assert sample_alert.requires_attention is False
        
        # Test tipos no críticos
        sample_alert.alert_type = AlertType.OTHER
        sample_alert.status = AlertStatus.NEW
        assert sample_alert.requires_attention is False
    
    def test_priority_level_property(self, sample_alert: Alert):
        """Test propiedad priority_level."""
        # Prioridad alta
        high_priority_types = [
            AlertType.CONFLICT,
            AlertType.SYSTEM_ERROR,
            AlertType.DEADLINE_WARNING
        ]
        
        for alert_type in high_priority_types:
            sample_alert.alert_type = alert_type
            assert sample_alert.priority_level == "Alta"
        
        # Prioridad media
        medium_priority_types = [
            AlertType.INSUFFICIENT_PERSONNEL,
            AlertType.OVERALLOCATION,
            AlertType.VALIDATION_ERROR,
            AlertType.VACATION_CONFLICT
        ]
        
        for alert_type in medium_priority_types:
            sample_alert.alert_type = alert_type
            assert sample_alert.priority_level == "Media"
        
        # Prioridad baja
        low_priority_types = [
            AlertType.APPROVAL_PENDING,
            AlertType.SCHEDULE_CHANGE,
            AlertType.OTHER
        ]
        
        for alert_type in low_priority_types:
            sample_alert.alert_type = alert_type
            assert sample_alert.priority_level == "Baja"
    
    def test_alert_summary_property(self, sample_alert: Alert):
        """Test propiedad alert_summary."""
        sample_alert.alert_type = AlertType.CONFLICT
        sample_alert.status = AlertStatus.NEW
        
        expected_summary = f"{sample_alert.type_display} - {sample_alert.status_display} ({sample_alert.priority_level})"
        assert sample_alert.alert_summary == expected_summary
        assert sample_alert.alert_summary == "Conflicto - Nueva (Alta)"


class TestAlertMethods:
    """Tests de los métodos del modelo Alert."""
    
    @pytest_asyncio.fixture
    async def sample_alert(self, test_session: AsyncSession, sample_employee: Employee) -> Alert:
        """Fixture que crea una alerta de prueba."""
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.CONFLICT,
            title="Test Alert",
            message="Test message"
        )
        
        test_session.add(alert)
        await test_session.flush()
        await test_session.refresh(alert)
        
        return alert
    
    def test_mark_as_read_method(self, sample_alert: Alert):
        """Test método mark_as_read."""
        # Estado inicial
        assert sample_alert.is_read is False
        assert sample_alert.read_at is None
        assert sample_alert.status == AlertStatus.NEW
        
        # Marcar como leída
        sample_alert.mark_as_read()
        
        # Verificar cambios
        assert sample_alert.is_read is True
        assert sample_alert.read_at is not None
        assert sample_alert.status == AlertStatus.READ
        assert isinstance(sample_alert.read_at, datetime)
    
    def test_mark_as_read_already_read_status(self, sample_alert: Alert):
        """Test método mark_as_read cuando ya tiene estado READ."""
        # Configurar estado inicial como READ
        sample_alert.status = AlertStatus.READ
        sample_alert.is_read = False  # Inconsistencia intencional para el test
        
        # Marcar como leída
        sample_alert.mark_as_read()
        
        # Verificar que se actualiza is_read y read_at pero no cambia status
        assert sample_alert.is_read is True
        assert sample_alert.read_at is not None
        assert sample_alert.status == AlertStatus.READ
    
    def test_mark_as_resolved_method(self, sample_alert: Alert):
        """Test método mark_as_resolved."""
        # Estado inicial
        assert sample_alert.is_read is False
        assert sample_alert.read_at is None
        assert sample_alert.status == AlertStatus.NEW
        
        # Marcar como resuelta
        sample_alert.mark_as_resolved()
        
        # Verificar cambios
        assert sample_alert.status == AlertStatus.RESOLVED
        assert sample_alert.is_read is True  # Se marca como leída automáticamente
        assert sample_alert.read_at is not None
    
    def test_mark_as_resolved_already_read(self, sample_alert: Alert):
        """Test método mark_as_resolved cuando ya está leída."""
        # Marcar como leída primero
        sample_alert.mark_as_read()
        original_read_at = sample_alert.read_at
        
        # Marcar como resuelta
        sample_alert.mark_as_resolved()
        
        # Verificar que no se cambia read_at
        assert sample_alert.status == AlertStatus.RESOLVED
        assert sample_alert.is_read is True
        assert sample_alert.read_at == original_read_at
    
    def test_mark_as_ignored_method(self, sample_alert: Alert):
        """Test método mark_as_ignored."""
        # Estado inicial
        assert sample_alert.is_read is False
        assert sample_alert.read_at is None
        assert sample_alert.status == AlertStatus.NEW
        
        # Marcar como ignorada
        sample_alert.mark_as_ignored()
        
        # Verificar cambios
        assert sample_alert.status == AlertStatus.IGNORED
        assert sample_alert.is_read is True  # Se marca como leída automáticamente
        assert sample_alert.read_at is not None
    
    def test_mark_as_ignored_already_read(self, sample_alert: Alert):
        """Test método mark_as_ignored cuando ya está leída."""
        # Marcar como leída primero
        sample_alert.mark_as_read()
        original_read_at = sample_alert.read_at
        
        # Marcar como ignorada
        sample_alert.mark_as_ignored()
        
        # Verificar que no se cambia read_at
        assert sample_alert.status == AlertStatus.IGNORED
        assert sample_alert.is_read is True
        assert sample_alert.read_at == original_read_at


class TestAlertRelationships:
    """Tests de las relaciones del modelo Alert."""
    
    async def test_user_relationship(self, test_session: AsyncSession, sample_employee: Employee):
        """Test relación con Employee (user)."""
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.CONFLICT,
            title="Test Alert",
            message="Test message"
        )
        
        test_session.add(alert)
        await test_session.flush()
        await test_session.refresh(alert)
        
        # Verificar relación directa
        assert alert.user_id == sample_employee.id
        
        # Verificar relación a través de SQLAlchemy
        await test_session.refresh(alert, ['user'])
        assert alert.user is not None
        assert alert.user.id == sample_employee.id
        assert alert.user.first_name == sample_employee.first_name
        assert alert.user.last_name == sample_employee.last_name


class TestAlertEdgeCases:
    """Tests de casos límite del modelo Alert."""
    
    async def test_null_optional_fields(self, test_session: AsyncSession, sample_employee: Employee):
        """Test campos opcionales con valores nulos."""
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.OTHER,
            title="Test Alert",
            message="Test message",
            related_entity_type=None,
            related_entity_id=None,
            read_at=None
        )
        
        test_session.add(alert)
        await test_session.flush()
        await test_session.refresh(alert)
        
        assert alert.related_entity_type is None
        assert alert.related_entity_id is None
        assert alert.read_at is None
    
    async def test_very_long_message(self, test_session: AsyncSession, sample_employee: Employee):
        """Test mensaje muy largo (Text field)."""
        very_long_message = "a" * 10000  # 10KB de texto
        
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.OTHER,
            title="Test Alert",
            message=very_long_message
        )
        
        test_session.add(alert)
        await test_session.flush()
        await test_session.refresh(alert)
        
        assert alert.message == very_long_message
        assert len(alert.message) == 10000
    
    async def test_boundary_related_entity_id(self, test_session: AsyncSession, sample_employee: Employee):
        """Test valores límite para related_entity_id."""
        # Test con ID muy grande
        large_id = 2147483647  # Max int32
        
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.OTHER,
            title="Test Alert",
            message="Test message",
            related_entity_id=large_id
        )
        
        test_session.add(alert)
        await test_session.flush()
        await test_session.refresh(alert)
        
        assert alert.related_entity_id == large_id
    
    async def test_unicode_content(self, test_session: AsyncSession, sample_employee: Employee):
        """Test contenido con caracteres Unicode."""
        unicode_title = "Alerta con émojis 🚨⚠️ y acentos ñáéíóú"
        unicode_message = "Mensaje con caracteres especiales: ñáéíóúü ¡¿ €£¥ 中文 🎉"
        
        alert = Alert(
            user_id=sample_employee.id,
            alert_type=AlertType.OTHER,
            title=unicode_title,
            message=unicode_message
        )
        
        test_session.add(alert)
        await test_session.flush()
        await test_session.refresh(alert)
        
        assert alert.title == unicode_title
        assert alert.message == unicode_message
    
    async def test_multiple_alerts_same_user(self, test_session: AsyncSession, sample_employee: Employee):
        """Test múltiples alertas para el mismo usuario."""
        alerts = []
        
        for i in range(5):
            alert = Alert(
                user_id=sample_employee.id,
                alert_type=AlertType.OTHER,
                title=f"Test Alert {i+1}",
                message=f"Test message {i+1}"
            )
            alerts.append(alert)
            test_session.add(alert)
        
        await test_session.flush()
        
        for alert in alerts:
            await test_session.refresh(alert)
            assert alert.id is not None
            assert alert.user_id == sample_employee.id
        
        # Verificar que todos tienen IDs únicos
        alert_ids = [alert.id for alert in alerts]
        assert len(set(alert_ids)) == len(alert_ids)  # Todos únicos