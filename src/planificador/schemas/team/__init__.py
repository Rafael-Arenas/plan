"""Módulo de esquemas para Team.

Este módulo contiene todos los esquemas relacionados con equipos (Team)
y membresías de equipos (TeamMembership).

Clases exportadas:
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
    - MembershipRole: Enum para roles de membresía

Autor: Sistema de Planificación
Fecha: 2024-12-21
"""

from .team import (
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
)
from ...models.team_membership import MembershipRole

__all__ = [
    "TeamBase",
    "TeamCreate",
    "TeamUpdate",
    "Team",
    "TeamMembershipBase",
    "TeamMembershipCreate",
    "TeamMembership",
    "TeamWithMembers",
    "TeamWithSchedules",
    "TeamWithDetails",
    "MembershipRole",
]