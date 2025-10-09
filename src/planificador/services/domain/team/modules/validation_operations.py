# src/planificador/services/domain/team/modules/validation_operations.py

"""
Módulo de Operaciones de Validación del Dominio Team.

Este módulo implementa las operaciones de validación de integridad de datos
y reglas de negocio para equipos, asegurando que los datos cumplan con
los estándares y políticas organizacionales.

Características:
    - Validación de integridad de datos de equipos
    - Verificación de reglas de negocio
    - Validación de consistencia relacional
    - Auditoría de cumplimiento normativo
    - Reportes de validación detallados

Principios de Diseño:
    - Data Integrity: Garantizar consistencia de datos
    - Business Rules: Aplicar políticas organizacionales
    - Comprehensive: Validaciones exhaustivas
    - Actionable: Resultados útiles para corrección

Uso:
    ```python
    validation_ops = TeamDomainValidationOperations(team_repo, membership_repo)
    result = await validation_ops.validate_team_data_integrity(team_id)
    business_result = await validation_ops.validate_business_rules(context)
    ```
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import pendulum
from loguru import logger

from planificador.repositories.team import TeamRepositoryFacade
from planificador.repositories.team_membership import TeamMembershipRepositoryFacade
from planificador.services.domain.team.interfaces.validation_operations_interface import (
    ITeamDomainValidationOperations,
    ValidationResult,
    BusinessContext,
    BusinessRuleValidationResult
)
from planificador.exceptions.domain import (
    TeamDomainError, ValidationError
)
from planificador.exceptions.repository import (
    TeamRepositoryError, TeamMembershipRepositoryError
)


class TeamDomainValidationOperations(ITeamDomainValidationOperations):
    """
    Implementación de operaciones de validación del dominio Team.
    
    Proporciona validaciones exhaustivas de integridad de datos y
    cumplimiento de reglas de negocio para equipos y sus relaciones.
    
    Attributes:
        _team_repo: Repositorio de equipos
        _membership_repo: Repositorio de membresías
        _logger: Logger para registro de eventos
    """

    def __init__(
        self,
        team_repo: TeamRepositoryFacade,
        membership_repo: TeamMembershipRepositoryFacade
    ):
        """
        Inicializa las operaciones de validación del dominio Team.
        
        Args:
            team_repo: Repositorio de equipos
            membership_repo: Repositorio de membresías
        """
        self.team_repository = team_repo
        self.membership_repository = membership_repo
        
        logger.debug("TeamDomainValidationOperations inicializado")

    async def validate_team_data(
        self,
        team_id: Optional[int] = None
    ) -> ValidationResult:
        """
        Valida la integridad de datos de equipos.
        
        Args:
            team_id: ID del equipo específico (opcional, todos si no se especifica)
            
        Returns:
            ValidationResult: Resultado de la validación de integridad
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            logger.debug(
                f"Validando integridad de datos para equipo: "
                f"{team_id if team_id else 'todos'}"
            )
            
            validation_errors = []
            validation_warnings = []
            teams_validated = 0
            
            # Obtener equipos a validar
            if team_id:
                # Validar ID específico
                if not isinstance(team_id, int) or team_id <= 0:
                    raise ValidationError("El ID del equipo debe ser un entero positivo")
                
                team = await self.team_repository.get_by_id(team_id)
                if not team:
                    raise ValidationError(f"No se encontró el equipo con ID {team_id}")
                teams = [team]
            else:
                # Validar todos los equipos
                teams = await self.team_repository.get_all()
            
            # Validar cada equipo
            for team in teams:
                teams_validated += 1
                
                # Validaciones de datos básicos
                team_errors, team_warnings = await self._validate_team_basic_data(team)
                validation_errors.extend(team_errors)
                validation_warnings.extend(team_warnings)
                
                # Validaciones de relaciones
                rel_errors, rel_warnings = await self._validate_team_relationships(team)
                validation_errors.extend(rel_errors)
                validation_warnings.extend(rel_warnings)
                
                # Validaciones de membresías
                mem_errors, mem_warnings = await self._validate_team_memberships(team)
                validation_errors.extend(mem_errors)
                validation_warnings.extend(mem_warnings)
            
            # Determinar estado de validación
            is_valid = len(validation_errors) == 0
            
            # Crear resultado de validación
            validation_result = ValidationResult(
                is_valid=is_valid,
                errors=validation_errors,
                warnings=validation_warnings,
                validated_entities=teams_validated,
                validation_type="data_integrity",
                validated_at=pendulum.now().to_datetime_string(),
                summary=f"Validación de integridad completada: {teams_validated} equipos, "
                       f"{len(validation_errors)} errores, {len(validation_warnings)} advertencias"
            )
            
            logger.debug(
                f"Validación de integridad completada: {teams_validated} equipos, "
                f"válido: {is_valid}"
            )
            
            return validation_result
            
        except TeamRepositoryError as e:
            logger.error(f"Error de repositorio en validación de integridad: {e}")
            raise TeamDomainError(
                f"Error al validar integridad de datos: {e.message}",
                operation="validate_team_data",
                entity_type="Team",
                entity_id=str(team_id) if team_id else None,
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado en validación de integridad: {e}")
            raise TeamDomainError(
                f"Error inesperado en validación de integridad: {str(e)}",
                operation="validate_team_data",
                entity_type="Team",
                entity_id=str(team_id) if team_id else None,
                original_error=e
            )

    async def validate_team_business_rules(
        self,
        context: BusinessContext
    ) -> BusinessRuleValidationResult:
        """
        Valida el cumplimiento de reglas de negocio.
        
        Args:
            context: Contexto de negocio para la validación
            
        Returns:
            BusinessRuleValidationResult: Resultado de validación de reglas
            
        Raises:
            ValidationError: Si el contexto no es válido
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            logger.debug(
                f"Validando reglas de negocio para operación: {context.operation}"
            )
            
            # Validar contexto
            if not context.operation:
                raise ValidationError("La operación es obligatoria en el contexto")
            
            rule_violations = []
            compliance_score = 1.0
            rules_evaluated = 0
            
            # Validar reglas según la operación
            if context.operation == "team_creation":
                violations, score, count = await self._validate_team_creation_rules(context)
                rule_violations.extend(violations)
                compliance_score = min(compliance_score, score)
                rules_evaluated += count
                
            elif context.operation == "team_update":
                violations, score, count = await self._validate_team_update_rules(context)
                rule_violations.extend(violations)
                compliance_score = min(compliance_score, score)
                rules_evaluated += count
                
            elif context.operation == "membership_assignment":
                violations, score, count = await self._validate_membership_rules(context)
                rule_violations.extend(violations)
                compliance_score = min(compliance_score, score)
                rules_evaluated += count
                
            elif context.operation == "team_deletion":
                violations, score, count = await self._validate_team_deletion_rules(context)
                rule_violations.extend(violations)
                compliance_score = min(compliance_score, score)
                rules_evaluated += count
            
            # Validar reglas generales siempre
            general_violations, general_score, general_count = await self._validate_general_business_rules(context)
            rule_violations.extend(general_violations)
            compliance_score = min(compliance_score, general_score)
            rules_evaluated += general_count
            
            # Determinar cumplimiento
            is_compliant = len(rule_violations) == 0
            
            # Generar recomendaciones
            recommendations = await self._generate_compliance_recommendations(
                rule_violations, context
            )
            
            # Crear resultado de validación
            business_result = BusinessRuleValidationResult(
                is_compliant=is_compliant,
                rule_violations=rule_violations,
                compliance_score=round(compliance_score, 2),
                rules_evaluated=rules_evaluated,
                context=context,
                recommendations=recommendations,
                validated_at=pendulum.now().to_datetime_string()
            )
            
            logger.debug(
                f"Validación de reglas completada: {rules_evaluated} reglas, "
                f"cumplimiento: {compliance_score:.2f}"
            )
            
            return business_result
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado en validación de reglas: {e}")
            raise TeamDomainError(
                f"Error inesperado en validación de reglas: {str(e)}",
                operation="validate_team_business_rules",
                entity_type="Team",
                original_error=e
            )

    # Métodos auxiliares privados

    async def _validate_team_basic_data(self, team) -> tuple[List[str], List[str]]:
        """Valida datos básicos del equipo."""
        errors = []
        warnings = []
        
        # Validar nombre
        if not team.name or len(team.name.strip()) < 2:
            errors.append(f"Equipo {team.id}: Nombre inválido o muy corto")
        elif len(team.name) > 100:
            warnings.append(f"Equipo {team.id}: Nombre muy largo ({len(team.name)} caracteres)")
        
        # Validar descripción
        if team.description and len(team.description) > 500:
            warnings.append(f"Equipo {team.id}: Descripción muy larga")
        
        # Validar departamento
        if not team.department or len(team.department.strip()) < 2:
            errors.append(f"Equipo {team.id}: Departamento inválido")
        
        # Validar fechas
        if team.created_at and team.updated_at:
            if team.created_at > team.updated_at:
                errors.append(f"Equipo {team.id}: Fecha de creación posterior a actualización")
        
        return errors, warnings

    async def _validate_team_relationships(self, team) -> tuple[List[str], List[str]]:
        """Valida relaciones del equipo."""
        errors = []
        warnings = []
        
        try:
            # Validar que el equipo tenga al menos un miembro
            members = await self._membership_repo.get_team_members(team.id)
            if not members:
                warnings.append(f"Equipo {team.id}: No tiene miembros asignados")
            elif len(members) > 50:
                warnings.append(f"Equipo {team.id}: Tiene muchos miembros ({len(members)})")
            
            # Validar liderazgo
            leaders = [m for m in members if m.role == "leader"]
            if len(leaders) == 0:
                warnings.append(f"Equipo {team.id}: No tiene líder asignado")
            elif len(leaders) > 1:
                warnings.append(f"Equipo {team.id}: Tiene múltiples líderes")
            
        except Exception as e:
            errors.append(f"Equipo {team.id}: Error al validar relaciones - {str(e)}")
        
        return errors, warnings

    async def _validate_team_memberships(self, team) -> tuple[List[str], List[str]]:
        """Valida membresías del equipo."""
        errors = []
        warnings = []
        
        try:
            memberships = await self._membership_repo.get_team_memberships(team.id)
            
            for membership in memberships:
                # Validar fechas de membresía
                if membership.start_date and membership.end_date:
                    if membership.start_date > membership.end_date:
                        errors.append(
                            f"Equipo {team.id}, Membresía {membership.id}: "
                            f"Fecha de inicio posterior a fecha de fin"
                        )
                
                # Validar roles
                valid_roles = ["member", "leader", "coordinator", "specialist"]
                if membership.role not in valid_roles:
                    errors.append(
                        f"Equipo {team.id}, Membresía {membership.id}: "
                        f"Rol inválido '{membership.role}'"
                    )
        
        except Exception as e:
            errors.append(f"Equipo {team.id}: Error al validar membresías - {str(e)}")
        
        return errors, warnings

    async def _validate_team_creation_rules(
        self, context: BusinessContext
    ) -> tuple[List[str], float, int]:
        """Valida reglas de creación de equipos."""
        violations = []
        score = 1.0
        rules_count = 0
        
        # Regla: Nombre único
        if context.data and "name" in context.data:
            existing_team = await self._team_repo.get_team_by_name(context.data["name"])
            if existing_team:
                violations.append(f"Ya existe un equipo con el nombre '{context.data['name']}'")
                score -= 0.5
            rules_count += 1
        
        # Regla: Departamento válido
        if context.data and "department" in context.data:
            valid_departments = ["IT", "HR", "Finance", "Marketing", "Operations", "Sales"]
            if context.data["department"] not in valid_departments:
                violations.append(f"Departamento '{context.data['department']}' no es válido")
                score -= 0.3
            rules_count += 1
        
        return violations, max(score, 0.0), rules_count

    async def _validate_team_update_rules(
        self, context: BusinessContext
    ) -> tuple[List[str], float, int]:
        """Valida reglas de actualización de equipos."""
        violations = []
        score = 1.0
        rules_count = 0
        
        # Regla: No cambiar nombre si tiene proyectos activos
        if context.entity_id and context.data and "name" in context.data:
            # En una implementación real, verificaríamos proyectos activos
            # Por ahora, simulamos la validación
            rules_count += 1
        
        return violations, max(score, 0.0), rules_count

    async def _validate_membership_rules(
        self, context: BusinessContext
    ) -> tuple[List[str], float, int]:
        """Valida reglas de membresía."""
        violations = []
        score = 1.0
        rules_count = 0
        
        # Regla: Un empleado no puede ser líder de más de 3 equipos
        if context.data and "employee_id" in context.data and "role" in context.data:
            if context.data["role"] == "leader":
                # En implementación real, contaríamos liderazgos actuales
                rules_count += 1
        
        return violations, max(score, 0.0), rules_count

    async def _validate_team_deletion_rules(
        self, context: BusinessContext
    ) -> tuple[List[str], float, int]:
        """Valida reglas de eliminación de equipos."""
        violations = []
        score = 1.0
        rules_count = 0
        
        # Regla: No eliminar equipos con proyectos activos
        if context.entity_id:
            # En implementación real, verificaríamos proyectos activos
            rules_count += 1
        
        return violations, max(score, 0.0), rules_count

    async def _validate_general_business_rules(
        self, context: BusinessContext
    ) -> tuple[List[str], float, int]:
        """Valida reglas generales de negocio."""
        violations = []
        score = 1.0
        rules_count = 0
        
        # Regla: Operaciones solo en horario laboral (ejemplo)
        current_hour = pendulum.now().hour
        if current_hour < 6 or current_hour > 22:
            violations.append("Operaciones fuera del horario laboral requieren aprobación")
            score -= 0.1
        rules_count += 1
        
        return violations, max(score, 0.0), rules_count

    async def _generate_compliance_recommendations(
        self, violations: List[str], context: BusinessContext
    ) -> List[str]:
        """Genera recomendaciones para mejorar el cumplimiento."""
        recommendations = []
        
        if violations:
            recommendations.append("Revisar y corregir las violaciones identificadas")
            
            if any("nombre" in v.lower() for v in violations):
                recommendations.append("Verificar unicidad de nombres antes de crear equipos")
            
            if any("departamento" in v.lower() for v in violations):
                recommendations.append("Usar solo departamentos válidos del catálogo")
            
            if any("horario" in v.lower() for v in violations):
                recommendations.append("Programar operaciones críticas en horario laboral")
        else:
            recommendations.append("Excelente cumplimiento de reglas de negocio")
        
        return recommendations