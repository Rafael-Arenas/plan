# src/planificador/services/domain/team/interfaces/validation_operations.py

"""
Interfaz para operaciones de validación del servicio de dominio de Team.

Define los métodos para verificación de integridad de datos,
cumplimiento de reglas de negocio y validaciones contextuales.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from .....schemas.team.team_advanced_schemas import TeamSchema


class ValidationResult(BaseModel):
    """Modelo para resultados de validación."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    validation_details: Dict[str, Any]


class BusinessContext(BaseModel):
    """Modelo para contexto de negocio."""
    organization_id: int
    department_constraints: Dict[str, Any]
    compliance_requirements: List[str]
    business_rules: Dict[str, Any]


class BusinessRuleValidationResult(BaseModel):
    """Modelo para resultados de validación de reglas de negocio."""
    is_compliant: bool
    violated_rules: List[str]
    compliance_score: float
    recommendations: List[str]
    context_analysis: Dict[str, Any]


class ITeamDomainValidationOperations(ABC):
    """
    Interfaz para operaciones de validación del servicio de dominio de Team.
    
    Define los métodos para verificar integridad de datos y cumplimiento
    de reglas de negocio específicas del contexto organizacional.
    """

    @abstractmethod
    async def validate_team_data(
        self,
        team_data: TeamSchema
    ) -> ValidationResult:
        """
        Valida la integridad y consistencia de los datos de un equipo.
        
        Args:
            team_data: Datos del equipo a validar
            
        Returns:
            ValidationResult: Resultado detallado de la validación
            
        Raises:
            ValidationError: Si los datos del equipo son inválidos
            RepositoryError: Si hay error en la validación
        """
        pass

    @abstractmethod
    async def validate_team_business_rules(
        self,
        team_id: Optional[int],
        context: BusinessContext
    ) -> BusinessRuleValidationResult:
        """
        Valida que un equipo cumple con las reglas de negocio específicas.
        
        Args:
            team_id: Identificador único del equipo (opcional para validaciones generales)
            context: Contexto organizacional para la validación
            
        Returns:
            BusinessRuleValidationResult: Resultado de validación de reglas
            
        Raises:
            NotFoundError: Si el equipo no existe (cuando team_id es proporcionado)
            ValidationError: Si el contexto de negocio es inválido
            RepositoryError: Si hay error en la validación
        """
        pass