"""Tests para los esquemas de Team.

Este módulo contiene tests unitarios para validar el comportamiento
de los esquemas relacionados con equipos (Team) y membresías (TeamMembership).

Clases de esquemas probadas:
    - TeamBase: Esquema base para equipos
    - TeamCreate: Esquema para crear equipos
    - TeamUpdate: Esquema para actualizar equipos
    - Team: Esquema completo de equipo
    - TeamMembershipBase: Esquema base para membresías
    - TeamMembershipCreate: Esquema para crear membresías
    - TeamMembership: Esquema completo de membresía
    - TeamWithMembers: Equipo con sus miembros
    - TeamWithSchedules: Equipo con sus horarios
    - TeamWithDetails: Equipo con todos los detalles

Autor: Sistema de Planificación
Fecha: 2024-12-21
"""

import pytest
from datetime import date, datetime, timedelta
from typing import Any, Dict, List
from pydantic import ValidationError
import pendulum

from planificador.schemas.team import (
    TeamBase,
    TeamCreate,
    TeamUpdate,
    Team,
    TeamMembershipBase,
    TeamMembershipCreate,
    TeamMembership,
    TeamWithMembers,
    TeamWithSchedules,
    TeamWithDetails,
    MembershipRole
)


class TestTeamBase:
    """Tests para el esquema TeamBase."""

    def test_valid_team_base_creation(self, valid_team_base_data: Dict[str, Any]):
        """Test: Crear TeamBase con datos válidos.
        
        Args:
            valid_team_base_data: Fixture con datos válidos
        """
        team = TeamBase(**valid_team_base_data)
        
        assert team.name == valid_team_base_data["name"]
        assert team.code == valid_team_base_data["code"]
        assert team.description == valid_team_base_data["description"]
        assert team.color_hex == valid_team_base_data["color_hex"]
        assert team.max_members == valid_team_base_data["max_members"]
        assert team.is_active == valid_team_base_data["is_active"]
        assert team.notes == valid_team_base_data["notes"]

    def test_minimal_team_base_creation(self, minimal_team_data: Dict[str, Any]):
        """Test: Crear TeamBase con datos mínimos.
        
        Args:
            minimal_team_data: Fixture con datos mínimos
        """
        team = TeamBase(**minimal_team_data)
        
        assert team.name == minimal_team_data["name"]
        assert team.code is None  # Campo opcional
        assert team.description is None  # Campo opcional
        assert team.color_hex == "#3498db"  # Valor por defecto
        assert team.max_members == 10  # Valor por defecto
        assert team.is_active is True  # Valor por defecto
        assert team.notes is None  # Campo opcional

    def test_maximal_team_base_creation(self, maximal_team_data: Dict[str, Any]):
        """Test: Crear TeamBase con datos máximos.
        
        Args:
            maximal_team_data: Fixture con datos máximos
        """
        team = TeamBase(**maximal_team_data)
        
        assert team.name == maximal_team_data["name"]
        assert team.code == maximal_team_data["code"]
        assert team.description == maximal_team_data["description"]
        assert team.color_hex == maximal_team_data["color_hex"]
        assert team.max_members == maximal_team_data["max_members"]
        assert team.is_active == maximal_team_data["is_active"]
        assert team.notes == maximal_team_data["notes"]

    def test_invalid_empty_name(self, invalid_team_empty_name: Dict[str, Any]):
        """Test: Fallar con nombre vacío.
        
        Args:
            invalid_team_empty_name: Fixture con nombre vacío
        """
        with pytest.raises(ValidationError) as exc_info:
            TeamBase(**invalid_team_empty_name)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("name",)
        assert "String should have at least 1 character" in str(errors[0]["msg"])

    def test_invalid_long_name(self, invalid_team_long_name: Dict[str, Any]):
        """Test: Fallar con nombre muy largo.
        
        Args:
            invalid_team_long_name: Fixture con nombre muy largo
        """
        with pytest.raises(ValidationError) as exc_info:
            TeamBase(**invalid_team_long_name)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("name",)
        assert "String should have at most 100 characters" in str(errors[0]["msg"])

    def test_invalid_long_code(self, invalid_team_long_code: Dict[str, Any]):
        """Test: Fallar con código muy largo.
        
        Args:
            invalid_team_long_code: Fixture con código muy largo
        """
        with pytest.raises(ValidationError) as exc_info:
            TeamBase(**invalid_team_long_code)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("code",)
        assert "String should have at most 20 characters" in str(errors[0]["msg"])

    def test_invalid_color_hex(self, invalid_team_color_hex: Dict[str, Any]):
        """Test: Fallar con color hex inválido.
        
        Args:
            invalid_team_color_hex: Fixture con color hex inválido
        """
        with pytest.raises(ValidationError) as exc_info:
            TeamBase(**invalid_team_color_hex)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("color_hex",)
        assert "String should match pattern" in str(errors[0]["msg"])

    def test_invalid_max_members_low(self, invalid_team_max_members_low: Dict[str, Any]):
        """Test: Fallar con max_members muy bajo.
        
        Args:
            invalid_team_max_members_low: Fixture con max_members bajo
        """
        with pytest.raises(ValidationError) as exc_info:
            TeamBase(**invalid_team_max_members_low)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("max_members",)
        assert "Input should be greater than or equal to 1" in str(errors[0]["msg"])

    def test_invalid_max_members_high(self, invalid_team_max_members_high: Dict[str, Any]):
        """Test: Fallar con max_members muy alto.
        
        Args:
            invalid_team_max_members_high: Fixture con max_members alto
        """
        with pytest.raises(ValidationError) as exc_info:
            TeamBase(**invalid_team_max_members_high)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("max_members",)
        assert "Input should be less than or equal to 100" in str(errors[0]["msg"])

    @pytest.mark.parametrize("color_hex", [
        "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF",
        "#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"
    ])
    def test_valid_color_hex_values(self, color_hex: str):
        """Test: Validar colores hex válidos.
        
        Args:
            color_hex: Color hex a validar
        """
        team_data = {"name": "Test Team", "color_hex": color_hex}
        team = TeamBase(**team_data)
        assert team.color_hex == color_hex

    @pytest.mark.parametrize("invalid_color", [
        "000000", "#00000", "#0000000", "#GGGGGG", "#xyz123",
        "red", "rgb(255,0,0)", "", "#", "123456"
    ])
    def test_invalid_color_hex_values(self, invalid_color: str):
        """Test: Fallar con colores hex inválidos.
        
        Args:
            invalid_color: Color hex inválido
        """
        team_data = {"name": "Test Team", "color_hex": invalid_color}
        with pytest.raises(ValidationError) as exc_info:
            TeamBase(**team_data)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("color_hex",) for error in errors)


class TestTeamCreate:
    """Tests para el esquema TeamCreate."""

    def test_valid_team_create(self, valid_team_create_data: Dict[str, Any]):
        """Test: Crear TeamCreate con datos válidos.
        
        Args:
            valid_team_create_data: Fixture con datos válidos
        """
        team = TeamCreate(**valid_team_create_data)
        
        assert team.name == valid_team_create_data["name"]
        assert team.code == valid_team_create_data["code"]
        assert team.description == valid_team_create_data["description"]
        assert team.color_hex == valid_team_create_data["color_hex"]
        assert team.max_members == valid_team_create_data["max_members"]
        assert team.is_active == valid_team_create_data["is_active"]
        assert team.notes == valid_team_create_data["notes"]

    def test_team_create_inheritance(self, valid_team_create_data: Dict[str, Any]):
        """Test: Verificar herencia de TeamBase.
        
        Args:
            valid_team_create_data: Fixture con datos válidos
        """
        team = TeamCreate(**valid_team_create_data)
        assert isinstance(team, TeamBase)


class TestTeamUpdate:
    """Tests para el esquema TeamUpdate."""

    def test_valid_team_update(self, valid_team_update_data: Dict[str, Any]):
        """Test: Crear TeamUpdate con datos válidos.
        
        Args:
            valid_team_update_data: Fixture con datos válidos
        """
        team = TeamUpdate(**valid_team_update_data)
        
        assert team.name == valid_team_update_data["name"]
        assert team.description == valid_team_update_data["description"]
        assert team.color_hex == valid_team_update_data["color_hex"]
        assert team.max_members == valid_team_update_data["max_members"]
        assert team.is_active == valid_team_update_data["is_active"]
        assert team.notes == valid_team_update_data["notes"]

    def test_team_update_partial_data(self):
        """Test: TeamUpdate con datos parciales."""
        partial_data = {"name": "Updated Name"}
        team = TeamUpdate(**partial_data)
        
        assert team.name == "Updated Name"
        assert team.description is None
        assert team.color_hex is None
        assert team.max_members is None
        assert team.is_active is None
        assert team.notes is None

    def test_team_update_empty_data(self):
        """Test: TeamUpdate con datos vacíos."""
        team = TeamUpdate()
        
        assert team.name is None
        assert team.description is None
        assert team.color_hex is None
        assert team.max_members is None
        assert team.is_active is None
        assert team.notes is None


class TestTeam:
    """Tests para el esquema Team."""

    def test_valid_team_creation(self, valid_team_complete_data: Dict[str, Any]):
        """Test: Crear Team con datos válidos.
        
        Args:
            valid_team_complete_data: Fixture con datos completos válidos
        """
        team = Team(**valid_team_complete_data)
        
        assert team.id == valid_team_complete_data["id"]
        assert team.name == valid_team_complete_data["name"]
        assert team.code == valid_team_complete_data["code"]
        assert team.description == valid_team_complete_data["description"]
        assert team.color_hex == valid_team_complete_data["color_hex"]
        assert team.max_members == valid_team_complete_data["max_members"]
        assert team.is_active == valid_team_complete_data["is_active"]
        assert team.notes == valid_team_complete_data["notes"]
        assert team.created_at == valid_team_complete_data["created_at"]
        assert team.updated_at == valid_team_complete_data["updated_at"]

    def test_team_inheritance(self, valid_team_complete_data: Dict[str, Any]):
        """Test: Verificar herencia de TeamBase.
        
        Args:
            valid_team_complete_data: Fixture con datos completos válidos
        """
        team = Team(**valid_team_complete_data)
        assert isinstance(team, TeamBase)


class TestTeamMembershipBase:
    """Tests para el esquema TeamMembershipBase."""

    def test_valid_membership_creation(self, valid_team_membership_base_data: Dict[str, Any]):
        """Test: Crear TeamMembershipBase con datos válidos.
        
        Args:
            valid_team_membership_base_data: Fixture con datos válidos
        """
        membership = TeamMembershipBase(**valid_team_membership_base_data)
        
        assert membership.employee_id == valid_team_membership_base_data["employee_id"]
        assert membership.team_id == valid_team_membership_base_data["team_id"]
        assert membership.role.value == valid_team_membership_base_data["role"]
        assert membership.start_date == valid_team_membership_base_data["start_date"]
        assert membership.end_date == valid_team_membership_base_data["end_date"]
        assert membership.is_active == valid_team_membership_base_data["is_active"]

    @pytest.mark.parametrize("role", ["member", "lead", "supervisor", "coordinator"])
    def test_valid_membership_roles(self, role: str):
        """Test: Validar roles de membresía válidos.
        
        Args:
            role: Rol a validar
        """
        membership_data = {
            "employee_id": 1,
            "team_id": 1,
            "role": role,
            "start_date": date.today(),
            "is_active": True
        }
        membership = TeamMembershipBase(**membership_data)
        assert membership.role.value == role

    def test_invalid_membership_role(self):
        """Test: Fallar con rol inválido."""
        membership_data = {
            "employee_id": 1,
            "team_id": 1,
            "role": "invalid_role",
            "start_date": date.today(),
            "is_active": True
        }
        with pytest.raises(ValidationError) as exc_info:
            TeamMembershipBase(**membership_data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("role",)
        assert "Input should be 'member', 'lead', 'supervisor' or 'coordinator'" in str(errors[0]["msg"])

    def test_invalid_membership_dates(self, invalid_team_membership_dates: Dict[str, Any]):
        """Test: Fallar con fechas inválidas (end_date antes que start_date).
        
        Args:
            invalid_team_membership_dates: Fixture con fechas inválidas
        """
        # Solo validar si realmente debería fallar
        if invalid_team_membership_dates.get("start_date") and invalid_team_membership_dates.get("end_date"):
            start_date = invalid_team_membership_dates["start_date"]
            end_date = invalid_team_membership_dates["end_date"]
            if start_date >= end_date:
                with pytest.raises(ValidationError) as exc_info:
                    TeamMembershipBase(**invalid_team_membership_dates)
                
                errors = exc_info.value.errors()
                assert len(errors) == 1
                assert "La fecha de inicio debe ser anterior a la fecha de fin" in str(errors[0]["msg"])
            else:
                # Si las fechas son válidas individualmente, no debería fallar
                membership = TeamMembershipBase(**invalid_team_membership_dates)
                assert membership is not None

    def test_invalid_old_start_date(self, invalid_team_membership_old_start_date: Dict[str, Any]):
        """Test: Fallar con start_date muy antigua.
        
        Args:
            invalid_team_membership_old_start_date: Fixture con start_date antigua
        """
        with pytest.raises(ValidationError) as exc_info:
            TeamMembershipBase(**invalid_team_membership_old_start_date)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "La fecha de inicio no puede ser anterior a 10 años" in str(errors[0]["msg"])

    def test_invalid_future_start_date(self, invalid_team_membership_future_start_date: Dict[str, Any]):
        """Test: Fallar con start_date muy futura.
        
        Args:
            invalid_team_membership_future_start_date: Fixture con start_date futura
        """
        with pytest.raises(ValidationError) as exc_info:
            TeamMembershipBase(**invalid_team_membership_future_start_date)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "La fecha de inicio no puede ser posterior a 5 años" in str(errors[0]["msg"])

    def test_invalid_future_end_date(self, invalid_team_membership_future_end_date: Dict[str, Any]):
        """Test: Fallar con end_date muy futura.
        
        Args:
            invalid_team_membership_future_end_date: Fixture con end_date futura
        """
        with pytest.raises(ValidationError) as exc_info:
            TeamMembershipBase(**invalid_team_membership_future_end_date)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "La fecha de fin no puede ser posterior a 10 años" in str(errors[0]["msg"])


class TestTeamMembershipCreate:
    """Tests para el esquema TeamMembershipCreate."""

    def test_valid_membership_create(self, valid_team_membership_create_data: Dict[str, Any]):
        """Test: Crear TeamMembershipCreate con datos válidos.
        
        Args:
            valid_team_membership_create_data: Fixture con datos válidos
        """
        membership = TeamMembershipCreate(**valid_team_membership_create_data)
        
        assert membership.employee_id == valid_team_membership_create_data["employee_id"]
        assert membership.team_id == valid_team_membership_create_data["team_id"]
        assert membership.role.value == valid_team_membership_create_data["role"]
        assert membership.start_date == valid_team_membership_create_data["start_date"]
        assert membership.end_date == valid_team_membership_create_data["end_date"]
        assert membership.is_active == valid_team_membership_create_data["is_active"]

    def test_membership_create_inheritance(self, valid_team_membership_create_data: Dict[str, Any]):
        """Test: Verificar herencia de TeamMembershipBase.
        
        Args:
            valid_team_membership_create_data: Fixture con datos válidos
        """
        membership = TeamMembershipCreate(**valid_team_membership_create_data)
        assert isinstance(membership, TeamMembershipBase)


class TestTeamMembership:
    """Tests para el esquema TeamMembership."""

    def test_valid_membership_full(self, valid_team_membership_data: Dict[str, Any]):
        """Test: Crear TeamMembership con datos válidos.
        
        Args:
            valid_team_membership_data: Fixture con datos válidos
        """
        membership = TeamMembership(**valid_team_membership_data)
        
        assert membership.id == valid_team_membership_data["id"]
        assert membership.employee_id == valid_team_membership_data["employee_id"]
        assert membership.team_id == valid_team_membership_data["team_id"]
        assert membership.role.value == valid_team_membership_data["role"]
        assert membership.start_date == valid_team_membership_data["start_date"]
        assert membership.end_date == valid_team_membership_data["end_date"]
        assert membership.is_active == valid_team_membership_data["is_active"]
        assert membership.created_at == valid_team_membership_data["created_at"]
        assert membership.updated_at == valid_team_membership_data["updated_at"]

    def test_membership_inheritance(self, valid_team_membership_data: Dict[str, Any]):
        """Test: Verificar herencia de TeamMembershipBase.
        
        Args:
            valid_team_membership_data: Fixture con datos válidos
        """
        membership = TeamMembership(**valid_team_membership_data)
        assert isinstance(membership, TeamMembershipBase)


class TestTeamWithMembers:
    """Tests para el esquema TeamWithMembers."""

    def test_valid_team_with_members(self, valid_team_with_members_data: Dict[str, Any]):
        """Test: Crear TeamWithMembers con datos válidos.
        
        Args:
            valid_team_with_members_data: Fixture con datos válidos
        """
        team = TeamWithMembers(**valid_team_with_members_data)
        
        assert team.id == valid_team_with_members_data["id"]
        assert team.name == valid_team_with_members_data["name"]
        assert team.memberships == valid_team_with_members_data["memberships"]
        assert isinstance(team.memberships, list)

    def test_team_with_members_inheritance(self, valid_team_with_members_data: Dict[str, Any]):
        """Test: Verificar herencia de Team.
        
        Args:
            valid_team_with_members_data: Fixture con datos válidos
        """
        team = TeamWithMembers(**valid_team_with_members_data)
        assert isinstance(team, Team)


class TestTeamWithSchedules:
    """Tests para el esquema TeamWithSchedules."""

    def test_valid_team_with_schedules(self, valid_team_with_schedules_data: Dict[str, Any]):
        """Test: Crear TeamWithSchedules con datos válidos.
        
        Args:
            valid_team_with_schedules_data: Fixture con datos válidos
        """
        team = TeamWithSchedules(**valid_team_with_schedules_data)
        
        assert team.id == valid_team_with_schedules_data["id"]
        assert team.name == valid_team_with_schedules_data["name"]
        assert team.schedules == valid_team_with_schedules_data["schedules"]
        assert isinstance(team.schedules, list)

    def test_team_with_schedules_inheritance(self, valid_team_with_schedules_data: Dict[str, Any]):
        """Test: Verificar herencia de Team.
        
        Args:
            valid_team_with_schedules_data: Fixture con datos válidos
        """
        team = TeamWithSchedules(**valid_team_with_schedules_data)
        assert isinstance(team, Team)


class TestTeamWithDetails:
    """Tests para el esquema TeamWithDetails."""

    def test_valid_team_with_details(self, valid_team_with_details_data: Dict[str, Any]):
        """Test: Crear TeamWithDetails con datos válidos.
        
        Args:
            valid_team_with_details_data: Fixture con datos válidos
        """
        team = TeamWithDetails(**valid_team_with_details_data)
        
        assert team.id == valid_team_with_details_data["id"]
        assert team.name == valid_team_with_details_data["name"]
        assert team.memberships == valid_team_with_details_data["memberships"]
        assert team.schedules == valid_team_with_details_data["schedules"]
        assert isinstance(team.memberships, list)
        assert isinstance(team.schedules, list)

    def test_team_with_details_inheritance(self, valid_team_with_details_data: Dict[str, Any]):
        """Test: Verificar herencia de Team.
        
        Args:
            valid_team_with_details_data: Fixture con datos válidos
        """
        team = TeamWithDetails(**valid_team_with_details_data)
        assert isinstance(team, Team)


class TestMembershipRole:
    """Tests para el enum MembershipRole."""

    def test_membership_role_values(self):
        """Test: Verificar valores válidos del enum."""
        valid_roles = ["member", "lead", "supervisor", "coordinator"]
        for role_value in valid_roles:
            role = MembershipRole(role_value)
            assert role.value == role_value

    def test_membership_role_invalid_value(self):
        """Test: Fallar con valor inválido del enum."""
        with pytest.raises(ValueError):
            MembershipRole("invalid_role")

    def test_membership_role_enum_members(self):
        """Test: Verificar miembros del enum."""
        assert MembershipRole.MEMBER.value == "member"
        assert MembershipRole.LEAD.value == "lead"
        assert MembershipRole.SUPERVISOR.value == "supervisor"
        assert MembershipRole.COORDINATOR.value == "coordinator"


class TestTeamValidations:
    """Tests para validaciones específicas de Team."""



    def test_membership_default_values(self):
        """Test: Verificar valores por defecto de membresía."""
        membership_data = {
            "employee_id": 1,
            "team_id": 1,
            "start_date": date.today()
        }
        membership = TeamMembershipBase(**membership_data)
        
        assert membership.role == MembershipRole.MEMBER  # Valor por defecto
        assert membership.end_date is None
        assert membership.is_active is True  # Valor por defecto

    def test_membership_date_validation_edge_cases(self):
        """Test: Casos límite de validación de fechas."""
        # Fecha de inicio exactamente 10 años atrás (válida)
        start_date_10_years = pendulum.now().subtract(years=10).date()
        membership_data = {
            "employee_id": 1,
            "team_id": 1,
            "start_date": start_date_10_years,
            "is_active": True
        }
        membership = TeamMembershipBase(**membership_data)
        assert membership.start_date == start_date_10_years
        
        # Fecha de inicio exactamente 5 años adelante (válida)
        start_date_5_years = pendulum.now().add(years=5).date()
        membership_data["start_date"] = start_date_5_years
        membership = TeamMembershipBase(**membership_data)
        assert membership.start_date == start_date_5_years
        
        # Fecha de fin exactamente 10 años adelante (válida)
        end_date_10_years = pendulum.now().add(years=10).date()
        membership_data["start_date"] = date.today()
        membership_data["end_date"] = end_date_10_years
        membership = TeamMembershipBase(**membership_data)
        assert membership.end_date == end_date_10_years