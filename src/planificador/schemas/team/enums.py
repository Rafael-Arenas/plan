"""
Enumeraciones para el dominio Team.

Este módulo contiene todas las enumeraciones utilizadas en el dominio de equipos
para evitar importaciones circulares entre esquemas e interfaces.
"""

from enum import Enum


class TeamStatus(str, Enum):
    """Estados posibles de un equipo."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"