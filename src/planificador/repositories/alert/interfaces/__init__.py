# src/planificador/repositories/alert/interfaces/__init__.py

"""
Módulo de interfaces para el repositorio de alertas.

Este módulo contiene las interfaces que definen los contratos
para las operaciones del repositorio de alertas.
"""

from .alert_repository_interface import IAlertRepository

__all__ = [
    "IAlertRepository",
]

__version__ = "1.0.0"
__author__ = "Planificador Team"