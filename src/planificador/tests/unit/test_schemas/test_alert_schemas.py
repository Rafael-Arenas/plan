# src/planificador/tests/unit/test_schemas/test_alert_schemas.py

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
import pendulum

from planificador.schemas.alert.alert import (
    AlertBase,
    AlertCreate,
    AlertUpdate,
    Alert,
    AlertSearchFilter
)
from planificador.models.alert import AlertType, AlertStatus


class TestAlertBase:
    """Tests para AlertBase schema."""

    def test_alert_base_creation_valid(self, valid_alert_data):
        """Test creación válida de AlertBase."""
        alert = AlertBase(**valid_alert_data)
        assert alert.user_id == valid_alert_data["user_id"]
        assert alert.alert_type == valid_alert_data["alert_type"]
        assert alert.status == valid_alert_data["status"]
        assert alert.title == valid_alert_data["title"]
        assert alert.message == valid_alert_data["message"]
        assert alert.is_read is False
        assert alert.read_at is None

    def test_alert_base_defaults(self, minimal_alert_data):
        """Test valores por defecto de AlertBase."""
        alert = AlertBase(**minimal_alert_data)
        assert alert.status == AlertStatus.NEW
        assert alert.is_read is False
        assert alert.read_at is None
        assert alert.related_entity_type is None
        assert alert.related_entity_id is None

    def test_alert_base_title_validation(self, valid_alert_data):
        """Test validación de título."""
        # Título vacío
        invalid_data = valid_alert_data.copy()
        invalid_data["title"] = ""
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            AlertBase(**invalid_data)

        # Título muy largo
        invalid_data["title"] = "x" * 201
        with pytest.raises(ValueError, match="String should have at most 200 characters"):
            AlertBase(**invalid_data)

    def test_alert_base_message_validation(self, valid_alert_data):
        """Test validación de mensaje."""
        invalid_data = valid_alert_data.copy()
        invalid_data["message"] = ""
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            AlertBase(**invalid_data)

    def test_alert_base_read_at_future_validation(self, valid_alert_data):
        """Test validación de read_at no puede ser futuro."""
        invalid_data = valid_alert_data.copy()
        invalid_data["read_at"] = pendulum.now().add(days=1)
        with pytest.raises(ValueError, match="La fecha de lectura no puede ser futura"):
            AlertBase(**invalid_data)

    def test_alert_base_read_consistency_validation(self, valid_alert_data):
        """Test validación de coherencia entre is_read y read_at."""
        # is_read=True pero read_at=None
        invalid_data = valid_alert_data.copy()
        invalid_data["is_read"] = True
        invalid_data["read_at"] = None
        with pytest.raises(ValueError, match="Si la alerta está marcada como leída, debe tener fecha de lectura"):
            AlertBase(**invalid_data)

        # is_read=False pero read_at tiene valor
        invalid_data = valid_alert_data.copy()
        invalid_data["is_read"] = False
        invalid_data["read_at"] = pendulum.now()
        with pytest.raises(ValueError, match="Si la alerta no está leída, no debe tener fecha de lectura"):
            AlertBase(**invalid_data)

    def test_alert_base_valid_read_state(self, valid_alert_data):
        """Test estado de lectura válido."""
        # Alerta leída con fecha
        read_data = valid_alert_data.copy()
        read_data["is_read"] = True
        read_data["read_at"] = pendulum.now().subtract(hours=1)
        alert = AlertBase(**read_data)
        assert alert.is_read is True
        assert alert.read_at is not None

        # Alerta no leída sin fecha
        unread_data = valid_alert_data.copy()
        unread_data["is_read"] = False
        unread_data["read_at"] = None
        alert = AlertBase(**unread_data)
        assert alert.is_read is False
        assert alert.read_at is None

    def test_alert_base_related_entity_validation(self, valid_alert_data):
        """Test validación de entidad relacionada."""
        # related_entity_type muy largo
        invalid_data = valid_alert_data.copy()
        invalid_data["related_entity_type"] = "x" * 51
        with pytest.raises(ValueError, match="String should have at most 50 characters"):
            AlertBase(**invalid_data)

    def test_alert_base_serialization(self, valid_alert_data):
        """Test serialización de AlertBase."""
        alert = AlertBase(**valid_alert_data)
        data = alert.model_dump()
        assert isinstance(data, dict)
        assert data["user_id"] == valid_alert_data["user_id"]
        assert data["alert_type"] == valid_alert_data["alert_type"]
        assert data["status"] == valid_alert_data["status"]


class TestAlertCreate:
    """Tests para AlertCreate schema."""

    def test_alert_create_inherits_from_base(self):
        """Test que AlertCreate hereda de AlertBase."""
        assert issubclass(AlertCreate, AlertBase)

    def test_alert_create_creation(self, valid_alert_data):
        """Test creación de AlertCreate."""
        alert = AlertCreate(**valid_alert_data)
        assert isinstance(alert, AlertBase)
        assert alert.user_id == valid_alert_data["user_id"]
        assert alert.alert_type == valid_alert_data["alert_type"]

    def test_alert_create_validation(self, invalid_alert_data):
        """Test validación en AlertCreate."""
        with pytest.raises(ValueError):
            AlertCreate(**invalid_alert_data)


class TestAlertUpdate:
    """Tests para AlertUpdate schema."""

    def test_alert_update_inherits_from_base(self):
        """Test que AlertUpdate hereda de AlertBase."""
        assert issubclass(AlertUpdate, AlertBase)

    def test_alert_update_all_optional(self):
        """Test que todos los campos son opcionales en AlertUpdate."""
        alert = AlertUpdate()
        assert alert.user_id is None
        assert alert.alert_type is None
        assert alert.status is None
        assert alert.title is None
        assert alert.message is None

    def test_alert_update_partial_data(self, valid_alert_data):
        """Test actualización parcial con AlertUpdate."""
        partial_data = {
            "title": "Título actualizado",
            "status": AlertStatus.READ
        }
        alert = AlertUpdate(**partial_data)
        assert alert.title == "Título actualizado"
        assert alert.status == AlertStatus.READ
        assert alert.user_id is None
        assert alert.message is None

    def test_alert_update_validation_when_provided(self):
        """Test que las validaciones aplican cuando se proporcionan valores."""
        # Título vacío
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            AlertUpdate(title="")

        # Mensaje vacío
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            AlertUpdate(message="")


class TestAlert:
    """Tests para Alert schema (respuesta)."""

    def test_alert_inherits_from_base(self):
        """Test que Alert hereda de AlertBase."""
        assert issubclass(Alert, AlertBase)

    def test_alert_creation(self, complete_alert_data):
        """Test creación de Alert con datos completos."""
        alert = Alert(**complete_alert_data)
        assert alert.id == complete_alert_data["id"]
        assert alert.created_at == complete_alert_data["created_at"]
        assert alert.updated_at == complete_alert_data["updated_at"]
        assert alert.user_id == complete_alert_data["user_id"]
        assert alert.title == complete_alert_data["title"]

    def test_alert_serialization(self, complete_alert_data):
        """Test serialización de Alert."""
        alert = Alert(**complete_alert_data)
        data = alert.model_dump()
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["id"] == complete_alert_data["id"]


class TestAlertSearchFilter:
    """Tests para AlertSearchFilter schema."""

    def test_alert_search_filter_inherits_from_base(self):
        """Test que AlertSearchFilter hereda de BaseSchema."""
        from planificador.schemas.base.base import BaseSchema
        assert issubclass(AlertSearchFilter, BaseSchema)

    def test_alert_search_filter_all_optional(self):
        """Test que todos los campos son opcionales."""
        filter_obj = AlertSearchFilter()
        assert filter_obj.user_id is None
        assert filter_obj.alert_type is None
        assert filter_obj.status is None
        assert filter_obj.is_read is None
        assert filter_obj.related_entity_type is None
        assert filter_obj.related_entity_id is None

    def test_alert_search_filter_partial_data(self):
        """Test filtro con datos parciales."""
        filter_data = {
            "user_id": 1,
            "alert_type": AlertType.CONFLICT,
            "is_read": False
        }
        filter_obj = AlertSearchFilter(**filter_data)
        assert filter_obj.user_id == 1
        assert filter_obj.alert_type == AlertType.CONFLICT
        assert filter_obj.is_read is False
        assert filter_obj.status is None

    def test_alert_search_filter_serialization(self):
        """Test serialización de AlertSearchFilter."""
        filter_data = {
            "user_id": 1,
            "alert_type": AlertType.DEADLINE_WARNING,
            "status": AlertStatus.NEW
        }
        filter_obj = AlertSearchFilter(**filter_data)
        data = filter_obj.model_dump(exclude_none=True)
        assert data["user_id"] == 1
        assert data["alert_type"] == AlertType.DEADLINE_WARNING
        assert data["status"] == AlertStatus.NEW
        assert "related_entity_type" not in data


class TestAlertSchemasEdgeCases:
    """Tests para casos extremos de Alert schemas."""

    def test_alert_with_all_alert_types(self, valid_alert_data):
        """Test creación de alertas con todos los tipos disponibles."""
        for alert_type in AlertType:
            data = valid_alert_data.copy()
            data["alert_type"] = alert_type
            alert = AlertBase(**data)
            assert alert.alert_type == alert_type

    def test_alert_with_all_statuses(self, valid_alert_data):
        """Test creación de alertas con todos los estados disponibles."""
        for status in AlertStatus:
            data = valid_alert_data.copy()
            data["status"] = status
            alert = AlertBase(**data)
            assert alert.status == status

    def test_alert_boundary_values(self, valid_alert_data):
        """Test valores límite para campos de texto."""
        # Título de 1 carácter
        data = valid_alert_data.copy()
        data["title"] = "A"
        alert = AlertBase(**data)
        assert alert.title == "A"

        # Título de 200 caracteres
        data["title"] = "A" * 200
        alert = AlertBase(**data)
        assert len(alert.title) == 200

        # Mensaje de 1 carácter
        data["message"] = "M"
        alert = AlertBase(**data)
        assert alert.message == "M"

        # related_entity_type de 50 caracteres
        data["related_entity_type"] = "E" * 50
        alert = AlertBase(**data)
        assert len(alert.related_entity_type) == 50

    def test_alert_with_related_entity(self, valid_alert_data):
        """Test alerta con entidad relacionada."""
        data = valid_alert_data.copy()
        data["related_entity_type"] = "project"
        data["related_entity_id"] = 123
        alert = AlertBase(**data)
        assert alert.related_entity_type == "project"
        assert alert.related_entity_id == 123

    def test_alert_read_at_edge_cases(self, valid_alert_data):
        """Test casos extremos para read_at."""
        # read_at exactamente ahora
        now = pendulum.now()
        data = valid_alert_data.copy()
        data["read_at"] = now
        data["is_read"] = True
        alert = AlertBase(**data)
        assert alert.read_at == now

        # read_at en el pasado
        past = pendulum.now().subtract(days=30)
        data["read_at"] = past
        alert = AlertBase(**data)
        assert alert.read_at == past

    def test_alert_complex_scenarios(self, valid_alert_data):
        """Test escenarios complejos de alertas."""
        # Alerta de conflicto con entidad relacionada
        conflict_data = valid_alert_data.copy()
        conflict_data.update({
            "alert_type": AlertType.CONFLICT,
            "status": AlertStatus.NEW,
            "title": "Conflicto de horario detectado",
            "message": "Se ha detectado un conflicto en la programación",
            "related_entity_type": "schedule",
            "related_entity_id": 456,
            "is_read": False,
            "read_at": None
        })
        alert = AlertBase(**conflict_data)
        assert alert.alert_type == AlertType.CONFLICT
        assert alert.related_entity_type == "schedule"
        assert alert.is_read is False

        # Alerta resuelta y leída
        resolved_data = valid_alert_data.copy()
        read_time = pendulum.now().subtract(hours=2)
        resolved_data.update({
            "alert_type": AlertType.DEADLINE_WARNING,
            "status": AlertStatus.RESOLVED,
            "is_read": True,
            "read_at": read_time
        })
        alert = AlertBase(**resolved_data)
        assert alert.status == AlertStatus.RESOLVED
        assert alert.is_read is True
        assert alert.read_at == read_time

    def test_alert_update_consistency_validation(self):
        """Test validación de coherencia en AlertUpdate."""
        # Debe fallar si se proporciona is_read=True sin read_at
        with pytest.raises(ValueError, match="Si la alerta está marcada como leída, debe tener fecha de lectura"):
            AlertUpdate(is_read=True, read_at=None)

        # Debe fallar si se proporciona read_at sin is_read=True
        with pytest.raises(ValueError, match="Si la alerta no está leída, no debe tener fecha de lectura"):
            AlertUpdate(is_read=False, read_at=pendulum.now())

    def test_alert_filter_with_enum_values(self):
        """Test filtro con valores de enum."""
        filter_obj = AlertSearchFilter(
            alert_type=AlertType.SYSTEM_ERROR,
            status=AlertStatus.IGNORED
        )
        assert filter_obj.alert_type == AlertType.SYSTEM_ERROR
        assert filter_obj.status == AlertStatus.IGNORED

    def test_alert_inheritance_chain(self):
        """Test cadena de herencia de schemas."""
        from planificador.schemas.base.base import BaseSchema
        
        # Verificar herencia
        assert issubclass(AlertBase, BaseSchema)
        assert issubclass(AlertCreate, AlertBase)
        assert issubclass(AlertUpdate, AlertBase)
        assert issubclass(Alert, AlertBase)
        assert issubclass(AlertSearchFilter, BaseSchema)

        # Verificar MRO (Method Resolution Order)
        assert AlertCreate.__mro__[1] == AlertBase
        assert AlertUpdate.__mro__[1] == AlertBase
        assert Alert.__mro__[1] == AlertBase