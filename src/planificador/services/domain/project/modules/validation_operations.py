# -*- coding: utf-8 -*-
"""
Módulo de Operaciones de Validación para Proyectos

Implementa funcionalidades para validar datos, reglas de negocio,
integridad referencial y consistencia de proyectos.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from uuid import UUID
from loguru import logger
import pendulum
import re
from pendulum import DateTime

from planificador.models.project import Project, ProjectStatus, ProjectPriority
from planificador.schemas.project.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectDatesUpdateSchema,
    ValidationResultSchema
)
from planificador.repositories.project.project_repository_facade import ProjectRepositoryFacade
from planificador.exceptions.domain.project_domain_exceptions import (
    ProjectValidationError,
    ProjectDateValidationError,
    ProjectCodeDuplicateError,
    ProjectTrigramDuplicateError,
    ProjectBusinessRuleViolationError,
    ProjectStatusTransitionError,
    create_project_validation_error,
    create_project_business_rule_error
)


class ProjectValidationOperations:
    """
    Operaciones de validación para proyectos.
    
    Proporciona funcionalidades para validar datos, reglas de negocio,
    integridad referencial y consistencia de proyectos.
    """

    def __init__(self, repository_facade: ProjectRepositoryFacade):
        """
        Inicializa las operaciones de validación.
        
        Args:
            repository_facade: Fachada del repositorio de proyectos
        """
        self.repository = repository_facade
        self._logger = logger.bind(module="project_validation_operations")

    async def validate_project_creation(self, project_data: ProjectCreate) -> ValidationResultSchema:
        """
        Valida los datos para la creación de un proyecto.
        
        Args:
            project_data: Datos del proyecto a crear
            
        Returns:
            Dict[str, Any]: Resultado de la validación
            
        Raises:
            ProjectValidationError: Si la validación falla
        """
        self._logger.debug(f"Validando creación de proyecto: {project_data.name}")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Validaciones básicas de datos
            await self._validate_basic_data(project_data, validation_result)
            
            # Validaciones de unicidad
            await self._validate_uniqueness_for_creation(project_data, validation_result)
            
            # Validaciones de fechas
            await self._validate_dates_for_creation(project_data, validation_result)
            
            # Validaciones de relaciones
            await self._validate_relationships_for_creation(project_data, validation_result)
            
            # Validaciones de reglas de negocio
            await self._validate_business_rules_for_creation(project_data, validation_result)
            
            # Determinar si es válido
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            self._logger.debug(
                f"Validación de creación completada: "
                f"válido={validation_result['is_valid']}, "
                f"errores={len(validation_result['errors'])}"
            )
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error en validación de creación: {e}")
            raise create_project_validation_error(
                field="general",
                value=str(project_data),
                message=f"Error en validación de creación: {e}",
                original_error=e
            )

    async def validate_project_update(
        self,
        project_id: UUID,
        update_data: ProjectUpdate
    ) -> ValidationResultSchema:
        """
        Valida los datos para la actualización de un proyecto.
        
        Args:
            project_id: ID del proyecto a actualizar
            update_data: Datos de actualización
            
        Returns:
            Dict[str, Any]: Resultado de la validación
            
        Raises:
            ProjectValidationError: Si la validación falla
        """
        self._logger.debug(f"Validando actualización de proyecto ID: {project_id}")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Obtener proyecto actual
            current_project = await self.repository.get_by_id(project_id)
            if not current_project:
                validation_result["errors"].append({
                    "field": "project_id",
                    "message": f"Proyecto con ID {project_id} no encontrado",
                    "code": "PROJECT_NOT_FOUND"
                })
                validation_result["is_valid"] = False
                return validation_result
            
            # Validaciones básicas de datos actualizados
            await self._validate_basic_data_for_update(update_data, validation_result)
            
            # Validaciones de unicidad (solo si se cambian campos únicos)
            await self._validate_uniqueness_for_update(
                project_id, current_project, update_data, validation_result
            )
            
            # Validaciones de fechas
            await self._validate_dates_for_update(
                current_project, update_data, validation_result
            )
            
            # Validaciones de relaciones
            await self._validate_relationships_for_update(
                current_project, update_data, validation_result
            )
            
            # Validaciones de reglas de negocio
            await self._validate_business_rules_for_update(
                current_project, update_data, validation_result
            )
            
            # Validaciones de impacto de cambios
            await self._validate_change_impact(
                current_project, update_data, validation_result
            )
            
            # Determinar si es válido
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            self._logger.debug(
                f"Validación de actualización completada: "
                f"válido={validation_result['is_valid']}, "
                f"errores={len(validation_result['errors'])}"
            )
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error en validación de actualización: {e}")
            raise create_project_validation_error(
                field="general",
                value=str(update_data),
                message=f"Error en validación de actualización: {e}",
                original_error=e
            )

    async def validate_status_transition(
        self,
        project_id: UUID,
        new_status: str,
        reason: Optional[str] = None
    ) -> ValidationResultSchema:
        """
        Valida una transición de estado de proyecto.
        
        Args:
            project_id: ID del proyecto
            new_status: Nuevo estado
            reason: Razón del cambio (opcional)
            
        Returns:
            Dict[str, Any]: Resultado de la validación
            
        Raises:
            ProjectStatusTransitionError: Si la transición no es válida
        """
        self._logger.debug(f"Validando transición de estado para proyecto ID: {project_id}")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "transition_allowed": False,
            "required_actions": []
        }
        
        try:
            # Obtener proyecto actual
            current_project = await self.repository.get_by_id(project_id)
            if not current_project:
                validation_result["errors"].append({
                    "field": "project_id",
                    "message": f"Proyecto con ID {project_id} no encontrado",
                    "code": "PROJECT_NOT_FOUND"
                })
                validation_result["is_valid"] = False
                return validation_result
            
            current_status = current_project.status
            
            # Verificar si la transición es permitida
            transition_allowed = await self._is_status_transition_allowed(
                current_status, new_status
            )
            
            validation_result["transition_allowed"] = transition_allowed
            
            if not transition_allowed:
                validation_result["errors"].append({
                    "field": "status",
                    "message": f"Transición de {current_status.value} a {new_status.value} no permitida",
                    "code": "INVALID_STATUS_TRANSITION"
                })
            
            # Validaciones específicas por tipo de transición
            await self._validate_specific_status_transition(
                current_project, current_status, new_status, validation_result
            )
            
            # Generar acciones requeridas
            await self._generate_transition_required_actions(
                current_project, current_status, new_status, validation_result
            )
            
            # Determinar si es válido
            validation_result["is_valid"] = (
                len(validation_result["errors"]) == 0 and 
                validation_result["transition_allowed"]
            )
            
            self._logger.debug(
                f"Validación de transición completada: "
                f"de {current_status.value} a {new_status.value}, "
                f"válido={validation_result['is_valid']}"
            )
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error en validación de transición de estado: {e}")
            raise ProjectStatusTransitionError(
                message=f"Error validando transición de estado: {e}",
                current_status=current_status.value if 'current_status' in locals() else "UNKNOWN",
                target_status=new_status.value,
                project_id=project_id,
                original_error=e
            )

    async def validate_project_dates(
        self,
        start_date: DateTime,
        end_date: DateTime,
        project_id: Optional[UUID] = None
    ) -> ValidationResultSchema:
        """
        Valida las fechas de un proyecto.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            project_id: ID del proyecto (para validaciones de conflictos)
            
        Returns:
            Dict[str, Any]: Resultado de la validación
            
        Raises:
            ProjectDateValidationError: Si las fechas no son válidas
        """
        self._logger.debug(f"Validando fechas de proyecto: {start_date} - {end_date}")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Validaciones básicas de fechas
            await self._validate_basic_dates(start_date, end_date, validation_result)
            
            # Validaciones de lógica de fechas
            await self._validate_date_logic(start_date, end_date, validation_result)
            
            # Validaciones de reglas de negocio para fechas
            await self._validate_date_business_rules(start_date, end_date, validation_result)
            
            # Validaciones de conflictos (si se proporciona project_id)
            if project_id:
                await self._validate_date_conflicts(
                    start_date, end_date, project_id, validation_result
                )
            
            # Generar sugerencias de optimización
            await self._generate_date_suggestions(start_date, end_date, validation_result)
            
            # Determinar si es válido
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            self._logger.debug(
                f"Validación de fechas completada: "
                f"válido={validation_result['is_valid']}, "
                f"errores={len(validation_result['errors'])}"
            )
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error en validación de fechas: {e}")
            raise ProjectDateValidationError(
                message=f"Error validando fechas de proyecto: {e}",
                start_date=start_date.isoformat() if start_date else None,
                end_date=end_date.isoformat() if end_date else None,
                original_error=e
            )

    async def validate_project_code(self, code: str, project_id: Optional[UUID] = None) -> ValidationResultSchema:
        """
        Valida el código de un proyecto.
        
        Args:
            code: Código del proyecto
            project_id: ID del proyecto (para actualizaciones)
            
        Returns:
            Dict[str, Any]: Resultado de la validación
            
        Raises:
            ProjectCodeDuplicateError: Si el código ya existe
        """
        self._logger.debug(f"Validando código de proyecto: {code}")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Validaciones de formato
            await self._validate_code_format(code, validation_result)
            
            # Validaciones de unicidad
            await self._validate_code_uniqueness(code, project_id, validation_result)
            
            # Validaciones de reglas de negocio para códigos
            await self._validate_code_business_rules(code, validation_result)
            
            # Determinar si es válido
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            self._logger.debug(
                f"Validación de código completada: "
                f"código={code}, válido={validation_result['is_valid']}"
            )
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error en validación de código: {e}")
            raise create_project_validation_error(
                field="code",
                value=code,
                message=f"Error validando código de proyecto: {e}",
                original_error=e
            )

    async def validate_project_trigram(
        self,
        trigram: str,
        project_id: Optional[UUID] = None
    ) -> ValidationResultSchema:
        """
        Valida el trigrama de un proyecto.
        
        Args:
            trigram: Trigrama del proyecto
            project_id: ID del proyecto (para actualizaciones)
            
        Returns:
            Dict[str, Any]: Resultado de la validación
            
        Raises:
            ProjectTrigramDuplicateError: Si el trigrama ya existe
        """
        self._logger.debug(f"Validando trigrama de proyecto: {trigram}")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Validaciones de formato
            await self._validate_trigram_format(trigram, validation_result)
            
            # Validaciones de unicidad
            await self._validate_trigram_uniqueness(trigram, project_id, validation_result)
            
            # Validaciones de reglas de negocio para trigramas
            await self._validate_trigram_business_rules(trigram, validation_result)
            
            # Determinar si es válido
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            self._logger.debug(
                f"Validación de trigrama completada: "
                f"trigrama={trigram}, válido={validation_result['is_valid']}"
            )
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error en validación de trigrama: {e}")
            raise create_project_validation_error(
                field="trigram",
                value=trigram,
                message=f"Error validando trigrama de proyecto: {e}",
                original_error=e
            )

    async def validate_business_rules(self, project_data: ProjectCreate) -> ValidationResultSchema:
        """
        Valida las reglas de negocio generales para proyectos.
        
        Args:
            project_data: Datos del proyecto a validar
            
        Returns:
            Dict[str, Any]: Resultado de la validación
            
        Raises:
            ProjectBusinessRuleViolationError: Si se violan reglas de negocio
        """
        self._logger.debug("Validando reglas de negocio generales")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "rules_checked": []
        }
        
        try:
            # Regla: Proyectos de alta prioridad deben tener fechas definidas
            await self._validate_high_priority_dates_rule(project_data, validation_result)
            
            # Regla: Duración mínima y máxima de proyectos
            await self._validate_duration_limits_rule(project_data, validation_result)
            
            # Regla: Proyectos no pueden empezar en fines de semana
            await self._validate_weekend_start_rule(project_data, validation_result)
            
            # Regla: Límite de proyectos activos por cliente
            await self._validate_client_active_projects_limit_rule(project_data, validation_result)
            
            # Regla: Validación de presupuesto vs duración
            await self._validate_budget_duration_rule(project_data, validation_result)
            
            # Determinar si es válido
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            self._logger.debug(
                f"Validación de reglas de negocio completada: "
                f"válido={validation_result['is_valid']}, "
                f"reglas verificadas={len(validation_result['rules_checked'])}"
            )
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error en validación de reglas de negocio: {e}")
            raise create_project_business_rule_error(
                rule="general_business_rules",
                message=f"Error validando reglas de negocio: {e}",
                original_error=e
            )

    async def validate_project_dates_detailed(
        self,
        start_date: DateTime,
        end_date: DateTime,
        project_id: Optional[UUID] = None
    ) -> ValidationResultSchema:
        """
        Valida fechas del proyecto detalladamente.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            project_id: ID del proyecto (opcional)
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            ProjectDateValidationError: Si las fechas no son válidas
        """
        self._logger.debug("Validando fechas del proyecto detalladamente")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Validaciones básicas de fechas
            await self._validate_basic_dates(start_date, end_date, validation_result)
            
            # Validaciones de lógica de fechas
            await self._validate_date_logic(start_date, end_date, validation_result)
            
            # Validaciones de reglas de negocio
            await self._validate_date_business_rules(start_date, end_date, validation_result)
            
            # Validaciones de conflictos si se proporciona project_id
            if project_id:
                await self._validate_date_conflicts(start_date, end_date, project_id, validation_result)
            
            # Generar sugerencias
            await self._generate_date_suggestions(start_date, end_date, validation_result)
            
            # Determinar si es válido
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            self._logger.debug(
                f"Validación detallada de fechas completada: "
                f"válido={validation_result['is_valid']}, "
                f"errores={len(validation_result['errors'])}"
            )
            
            return ValidationResultSchema(**validation_result)
            
        except Exception as e:
            self._logger.error(f"Error en validación detallada de fechas: {e}")
            raise ProjectDateValidationError(
                message=f"Error validando fechas detalladamente: {e}",
                start_date=start_date,
                end_date=end_date,
                original_error=e
            )

    async def validate_data_integrity(self, project_id: UUID) -> ValidationResultSchema:
        """
        Valida la integridad de datos de un proyecto existente.
        
        Args:
            project_id: ID del proyecto a validar
            
        Returns:
            Dict[str, Any]: Resultado de la validación de integridad
        """
        self._logger.debug(f"Validando integridad de datos para proyecto ID: {project_id}")
        
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "integrity_checks": []
        }
        
        try:
            # Obtener proyecto
            project = await self.repository.get_by_id(project_id)
            if not project:
                validation_result["errors"].append({
                    "field": "project_id",
                    "message": f"Proyecto con ID {project_id} no encontrado",
                    "code": "PROJECT_NOT_FOUND"
                })
                validation_result["is_valid"] = False
                return validation_result
            
            # Verificar integridad referencial
            await self._validate_referential_integrity(project, validation_result)
            
            # Verificar consistencia de datos
            await self._validate_data_consistency(project, validation_result)
            
            # Verificar reglas de negocio actuales
            await self._validate_current_business_rules(project, validation_result)
            
            # Verificar estado vs datos
            await self._validate_status_data_consistency(project, validation_result)
            
            # Determinar si es válido
            validation_result["is_valid"] = len(validation_result["errors"]) == 0
            
            self._logger.debug(
                f"Validación de integridad completada: "
                f"válido={validation_result['is_valid']}, "
                f"verificaciones={len(validation_result['integrity_checks'])}"
            )
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error en validación de integridad: {e}")
            raise create_project_validation_error(
                field="integrity",
                value=str(project_id),
                message=f"Error validando integridad de datos: {e}",
                original_error=e
            )

    # ============================================================================
    # MÉTODOS PRIVADOS DE VALIDACIÓN
    # ============================================================================

    async def _validate_basic_data(
        self,
        project_data: ProjectCreate,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida datos básicos del proyecto."""
        # Validar nombre
        if not project_data.name or len(project_data.name.strip()) < 3:
            validation_result["errors"].append({
                "field": "name",
                "message": "El nombre del proyecto debe tener al menos 3 caracteres",
                "code": "INVALID_NAME_LENGTH"
            })
        
        # Validar descripción
        if project_data.description and len(project_data.description) > 1000:
            validation_result["warnings"].append({
                "field": "description",
                "message": "La descripción es muy larga (>1000 caracteres)",
                "code": "LONG_DESCRIPTION"
            })
        
        # Validar prioridad
        if project_data.priority and project_data.priority not in ProjectPriority:
            validation_result["errors"].append({
                "field": "priority",
                "message": f"Prioridad inválida: {project_data.priority}",
                "code": "INVALID_PRIORITY"
            })

    async def _validate_basic_data_for_update(
        self,
        update_data: ProjectUpdate,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida datos básicos para actualización."""
        # Validar nombre si se proporciona
        if hasattr(update_data, 'name') and update_data.name is not None:
            if len(update_data.name.strip()) < 3:
                validation_result["errors"].append({
                    "field": "name",
                    "message": "El nombre del proyecto debe tener al menos 3 caracteres",
                    "code": "INVALID_NAME_LENGTH"
                })
        
        # Validar descripción si se proporciona
        if hasattr(update_data, 'description') and update_data.description is not None:
            if len(update_data.description) > 1000:
                validation_result["warnings"].append({
                    "field": "description",
                    "message": "La descripción es muy larga (>1000 caracteres)",
                    "code": "LONG_DESCRIPTION"
                })

    async def _validate_uniqueness_for_creation(
        self,
        project_data: ProjectCreate,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida unicidad para creación."""
        # Validar código único
        if project_data.code:
            existing_code = await self.repository.get_by_code(project_data.code)
            if existing_code:
                validation_result["errors"].append({
                    "field": "code",
                    "message": f"El código '{project_data.code}' ya existe",
                    "code": "DUPLICATE_CODE"
                })
        
        # Validar trigrama único
        if project_data.trigram:
            existing_trigram = await self.repository.get_by_trigram(project_data.trigram)
            if existing_trigram:
                validation_result["errors"].append({
                    "field": "trigram",
                    "message": f"El trigrama '{project_data.trigram}' ya existe",
                    "code": "DUPLICATE_TRIGRAM"
                })

    async def _validate_uniqueness_for_update(
        self,
        project_id: int,
        current_project: Project,
        update_data: ProjectUpdate,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida unicidad para actualización."""
        # Validar código único si se cambia
        if hasattr(update_data, 'code') and update_data.code is not None:
            if update_data.code != current_project.code:
                existing_code = await self.repository.get_by_code(update_data.code)
                if existing_code and existing_code.id != project_id:
                    validation_result["errors"].append({
                        "field": "code",
                        "message": f"El código '{update_data.code}' ya existe",
                        "code": "DUPLICATE_CODE"
                    })
        
        # Validar trigrama único si se cambia
        if hasattr(update_data, 'trigram') and update_data.trigram is not None:
            if update_data.trigram != current_project.trigram:
                existing_trigram = await self.repository.get_by_trigram(update_data.trigram)
                if existing_trigram and existing_trigram.id != project_id:
                    validation_result["errors"].append({
                        "field": "trigram",
                        "message": f"El trigrama '{update_data.trigram}' ya existe",
                        "code": "DUPLICATE_TRIGRAM"
                    })

    async def _validate_dates_for_creation(
        self,
        project_data: ProjectCreate,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida fechas para creación."""
        if project_data.start_date and project_data.end_date:
            if project_data.start_date >= project_data.end_date:
                validation_result["errors"].append({
                    "field": "dates",
                    "message": "La fecha de inicio debe ser anterior a la fecha de fin",
                    "code": "INVALID_DATE_RANGE"
                })
            
            # Validar que no sean fechas muy pasadas
            current_date = pendulum.now().date()
            if project_data.start_date < current_date.subtract(years=1):
                validation_result["warnings"].append({
                    "field": "start_date",
                    "message": "La fecha de inicio es muy antigua",
                    "code": "OLD_START_DATE"
                })

    async def _validate_dates_for_update(
        self,
        current_project: Project,
        update_data: ProjectUpdate,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida fechas para actualización."""
        start_date = getattr(update_data, 'start_date', current_project.start_date)
        end_date = getattr(update_data, 'end_date', current_project.end_date)
        
        if start_date and end_date:
            if start_date >= end_date:
                validation_result["errors"].append({
                    "field": "dates",
                    "message": "La fecha de inicio debe ser anterior a la fecha de fin",
                    "code": "INVALID_DATE_RANGE"
                })

    async def _validate_relationships_for_creation(
        self,
        project_data: ProjectCreate,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida relaciones para creación."""
        # Validar que el cliente existe (implementación simplificada)
        if project_data.client_id:
            # En un sistema real, verificaríamos que el cliente existe
            pass

    async def _validate_relationships_for_update(
        self,
        current_project: Project,
        update_data: ProjectUpdate,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida relaciones para actualización."""
        # Validar cambio de cliente si se proporciona
        if hasattr(update_data, 'client_id') and update_data.client_id is not None:
            if update_data.client_id != current_project.client_id:
                # Verificar que el nuevo cliente existe
                pass

    async def _validate_business_rules_for_creation(
        self,
        project_data: ProjectCreate,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida reglas de negocio para creación."""
        # Regla: Proyectos de alta prioridad deben tener fechas
        if project_data.priority == ProjectPriority.HIGH:
            if not project_data.start_date or not project_data.end_date:
                validation_result["errors"].append({
                    "field": "priority",
                    "message": "Proyectos de alta prioridad deben tener fechas definidas",
                    "code": "HIGH_PRIORITY_REQUIRES_DATES"
                })

    async def _validate_business_rules_for_update(
        self,
        current_project: Project,
        update_data: ProjectUpdate,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida reglas de negocio para actualización."""
        # Regla: No se puede cambiar a alta prioridad sin fechas
        if hasattr(update_data, 'priority') and update_data.priority == ProjectPriority.HIGH:
            start_date = getattr(update_data, 'start_date', current_project.start_date)
            end_date = getattr(update_data, 'end_date', current_project.end_date)
            
            if not start_date or not end_date:
                validation_result["errors"].append({
                    "field": "priority",
                    "message": "Proyectos de alta prioridad deben tener fechas definidas",
                    "code": "HIGH_PRIORITY_REQUIRES_DATES"
                })

    async def _validate_change_impact(
        self,
        current_project: Project,
        update_data: ProjectUpdate,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida el impacto de los cambios."""
        # Verificar cambios críticos
        critical_changes = []
        
        if hasattr(update_data, 'client_id') and update_data.client_id != current_project.client_id:
            critical_changes.append("client_change")
        
        if hasattr(update_data, 'end_date') and update_data.end_date != current_project.end_date:
            critical_changes.append("end_date_change")
        
        if critical_changes:
            validation_result["warnings"].append({
                "field": "changes",
                "message": f"Cambios críticos detectados: {', '.join(critical_changes)}",
                "code": "CRITICAL_CHANGES"
            })

    async def _is_status_transition_allowed(
        self,
        current_status: ProjectStatus,
        new_status: ProjectStatus
    ) -> bool:
        """Verifica si una transición de estado es permitida."""
        # Definir transiciones permitidas
        allowed_transitions = {
            ProjectStatus.DRAFT: [ProjectStatus.ACTIVE, ProjectStatus.CANCELLED],
            ProjectStatus.ACTIVE: [ProjectStatus.ON_HOLD, ProjectStatus.COMPLETED, ProjectStatus.CANCELLED],
            ProjectStatus.ON_HOLD: [ProjectStatus.ACTIVE, ProjectStatus.CANCELLED],
            ProjectStatus.COMPLETED: [],  # Los proyectos completados no pueden cambiar
            ProjectStatus.CANCELLED: [ProjectStatus.DRAFT]  # Solo se puede reactivar como borrador
        }
        
        return new_status in allowed_transitions.get(current_status, [])

    async def _validate_specific_status_transition(
        self,
        project: Project,
        current_status: ProjectStatus,
        new_status: ProjectStatus,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida transiciones específicas de estado."""
        # Validar transición a COMPLETED
        if new_status == ProjectStatus.COMPLETED:
            if not project.start_date or not project.end_date:
                validation_result["errors"].append({
                    "field": "status",
                    "message": "No se puede completar un proyecto sin fechas definidas",
                    "code": "COMPLETION_REQUIRES_DATES"
                })
        
        # Validar transición a ACTIVE
        if new_status == ProjectStatus.ACTIVE:
            if not project.start_date:
                validation_result["warnings"].append({
                    "field": "status",
                    "message": "Se recomienda definir fecha de inicio antes de activar",
                    "code": "ACTIVE_SHOULD_HAVE_START_DATE"
                })

    async def _generate_transition_required_actions(
        self,
        project: Project,
        current_status: ProjectStatus,
        new_status: ProjectStatus,
        validation_result: Dict[str, Any]
    ) -> None:
        """Genera acciones requeridas para la transición."""
        required_actions = []
        
        if new_status == ProjectStatus.COMPLETED:
            required_actions.append("Verificar que todas las tareas estén completadas")
            required_actions.append("Documentar resultados del proyecto")
        
        if new_status == ProjectStatus.CANCELLED:
            required_actions.append("Documentar razón de cancelación")
            required_actions.append("Notificar a stakeholders")
        
        validation_result["required_actions"] = required_actions

    async def _validate_basic_dates(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida fechas básicas."""
        current_date = pendulum.now().date()
        
        # Validar que las fechas no sean nulas si ambas se proporcionan
        if start_date and end_date:
            if start_date >= end_date:
                validation_result["errors"].append({
                    "field": "dates",
                    "message": "La fecha de inicio debe ser anterior a la fecha de fin",
                    "code": "INVALID_DATE_RANGE"
                })
        
        # Validar fechas muy pasadas
        if start_date and start_date < current_date.subtract(years=2):
            validation_result["warnings"].append({
                "field": "start_date",
                "message": "La fecha de inicio es muy antigua",
                "code": "OLD_START_DATE"
            })

    async def _validate_date_logic(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida lógica de fechas."""
        if start_date and end_date:
            duration = (end_date - start_date).days + 1
            
            # Validar duración mínima
            if duration < 1:
                validation_result["errors"].append({
                    "field": "dates",
                    "message": "La duración del proyecto debe ser al menos 1 día",
                    "code": "INVALID_DURATION"
                })
            
            # Validar duración máxima
            if duration > 730:  # 2 años
                validation_result["warnings"].append({
                    "field": "dates",
                    "message": "El proyecto tiene una duración muy larga (>2 años)",
                    "code": "LONG_DURATION"
                })

    async def _validate_date_business_rules(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida reglas de negocio para fechas."""
        # Regla: No iniciar en fines de semana
        if start_date:
            start_pendulum = pendulum.instance(start_date)
            if start_pendulum.day_of_week in [6, 7]:  # Sábado o Domingo
                validation_result["warnings"].append({
                    "field": "start_date",
                    "message": "Se recomienda no iniciar proyectos en fines de semana",
                    "code": "WEEKEND_START"
                })

    async def _validate_date_conflicts(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        project_id: int,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida conflictos de fechas con otros proyectos."""
        # Implementación simplificada - en un sistema real verificaría conflictos reales
        pass

    async def _generate_date_suggestions(
        self,
        start_date: Optional[date],
        end_date: Optional[date],
        validation_result: Dict[str, Any]
    ) -> None:
        """Genera sugerencias para optimizar fechas."""
        if start_date and end_date:
            duration = (end_date - start_date).days + 1
            
            if duration > 90:
                validation_result["suggestions"].append({
                    "field": "dates",
                    "message": "Considere dividir el proyecto en fases más pequeñas",
                    "code": "CONSIDER_PHASES"
                })

    async def _validate_code_format(self, code: str, validation_result: Dict[str, Any]) -> None:
        """Valida el formato del código."""
        # Reglas de formato para códigos
        if not re.match(r'^[A-Z0-9-_]{3,20}$', code):
            validation_result["errors"].append({
                "field": "code",
                "message": "El código debe tener 3-20 caracteres alfanuméricos, guiones o guiones bajos",
                "code": "INVALID_CODE_FORMAT"
            })

    async def _validate_code_uniqueness(
        self,
        code: str,
        project_id: Optional[int],
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida unicidad del código."""
        existing_project = await self.repository.get_by_code(code)
        if existing_project and (not project_id or existing_project.id != project_id):
            validation_result["errors"].append({
                "field": "code",
                "message": f"El código '{code}' ya existe",
                "code": "DUPLICATE_CODE"
            })

    async def _validate_code_business_rules(
        self,
        code: str,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida reglas de negocio para códigos."""
        # Regla: Los códigos no deben contener palabras reservadas
        reserved_words = ['TEST', 'TEMP', 'DELETE', 'ADMIN']
        if any(word in code.upper() for word in reserved_words):
            validation_result["warnings"].append({
                "field": "code",
                "message": "El código contiene palabras reservadas",
                "code": "RESERVED_WORD_IN_CODE"
            })

    async def _validate_trigram_format(self, trigram: str, validation_result: Dict[str, Any]) -> None:
        """Valida el formato del trigrama."""
        if not re.match(r'^[A-Z]{3}$', trigram):
            validation_result["errors"].append({
                "field": "trigram",
                "message": "El trigrama debe tener exactamente 3 letras mayúsculas",
                "code": "INVALID_TRIGRAM_FORMAT"
            })

    async def _validate_trigram_uniqueness(
        self,
        trigram: str,
        project_id: Optional[int],
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida unicidad del trigrama."""
        existing_project = await self.repository.get_by_trigram(trigram)
        if existing_project and (not project_id or existing_project.id != project_id):
            validation_result["errors"].append({
                "field": "trigram",
                "message": f"El trigrama '{trigram}' ya existe",
                "code": "DUPLICATE_TRIGRAM"
            })

    async def _validate_trigram_business_rules(
        self,
        trigram: str,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida reglas de negocio para trigramas."""
        # Regla: Evitar trigramas ofensivos o confusos
        forbidden_trigrams = ['SEX', 'BAD', 'DIE', 'WAR']
        if trigram.upper() in forbidden_trigrams:
            validation_result["errors"].append({
                "field": "trigram",
                "message": "El trigrama no es apropiado",
                "code": "INAPPROPRIATE_TRIGRAM"
            })

    async def _validate_high_priority_dates_rule(
        self,
        project_data: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida regla de fechas para proyectos de alta prioridad."""
        validation_result["rules_checked"].append("high_priority_dates")
        
        priority = project_data.get('priority')
        if priority == ProjectPriority.HIGH:
            start_date = project_data.get('start_date')
            end_date = project_data.get('end_date')
            
            if not start_date or not end_date:
                validation_result["errors"].append({
                    "field": "priority",
                    "message": "Proyectos de alta prioridad deben tener fechas definidas",
                    "code": "HIGH_PRIORITY_REQUIRES_DATES"
                })

    async def _validate_duration_limits_rule(
        self,
        project_data: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida regla de límites de duración."""
        validation_result["rules_checked"].append("duration_limits")
        
        start_date = project_data.get('start_date')
        end_date = project_data.get('end_date')
        
        if start_date and end_date:
            duration = (end_date - start_date).days + 1
            
            if duration < 1:
                validation_result["errors"].append({
                    "field": "dates",
                    "message": "La duración mínima de un proyecto es 1 día",
                    "code": "DURATION_TOO_SHORT"
                })
            
            if duration > 365:
                validation_result["warnings"].append({
                    "field": "dates",
                    "message": "Proyectos de más de 1 año requieren aprobación especial",
                    "code": "LONG_DURATION_APPROVAL"
                })

    async def _validate_weekend_start_rule(
        self,
        project_data: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida regla de no inicio en fines de semana."""
        validation_result["rules_checked"].append("weekend_start")
        
        start_date = project_data.get('start_date')
        if start_date:
            start_pendulum = pendulum.instance(start_date)
            if start_pendulum.day_of_week in [6, 7]:
                validation_result["warnings"].append({
                    "field": "start_date",
                    "message": "Se recomienda no iniciar proyectos en fines de semana",
                    "code": "WEEKEND_START"
                })

    async def _validate_client_active_projects_limit_rule(
        self,
        project_data: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida regla de límite de proyectos activos por cliente."""
        validation_result["rules_checked"].append("client_active_projects_limit")
        
        client_id = project_data.get('client_id')
        if client_id:
            # Obtener proyectos activos del cliente
            active_projects = await self.repository.get_by_client(client_id)
            active_count = len([p for p in active_projects if p.status == ProjectStatus.ACTIVE])
            
            if active_count >= 10:  # Límite de ejemplo
                validation_result["warnings"].append({
                    "field": "client_id",
                    "message": f"El cliente ya tiene {active_count} proyectos activos",
                    "code": "CLIENT_MANY_ACTIVE_PROJECTS"
                })

    async def _validate_budget_duration_rule(
        self,
        project_data: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida regla de presupuesto vs duración."""
        validation_result["rules_checked"].append("budget_duration")
        
        # Implementación simplificada - en un sistema real validaría presupuesto real
        pass

    async def _validate_referential_integrity(
        self,
        project: Project,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida integridad referencial."""
        validation_result["integrity_checks"].append("referential_integrity")
        
        # Verificar que el cliente existe (simplificado)
        if project.client_id:
            # En un sistema real, verificaríamos que el cliente existe
            pass

    async def _validate_data_consistency(
        self,
        project: Project,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida consistencia de datos."""
        validation_result["integrity_checks"].append("data_consistency")
        
        # Verificar consistencia de fechas
        if project.start_date and project.end_date:
            if project.start_date >= project.end_date:
                validation_result["errors"].append({
                    "field": "dates",
                    "message": "Inconsistencia: fecha de inicio >= fecha de fin",
                    "code": "INCONSISTENT_DATES"
                })

    async def _validate_current_business_rules(
        self,
        project: Project,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida reglas de negocio actuales."""
        validation_result["integrity_checks"].append("current_business_rules")
        
        # Verificar reglas actuales
        if project.priority == ProjectPriority.HIGH:
            if not project.start_date or not project.end_date:
                validation_result["errors"].append({
                    "field": "priority",
                    "message": "Proyecto de alta prioridad sin fechas definidas",
                    "code": "HIGH_PRIORITY_NO_DATES"
                })

    async def _validate_status_data_consistency(
        self,
        project: Project,
        validation_result: Dict[str, Any]
    ) -> None:
        """Valida consistencia entre estado y datos."""
        validation_result["integrity_checks"].append("status_data_consistency")
        
        # Verificar consistencia de estado
        if project.status == ProjectStatus.COMPLETED:
            if not project.end_date:
                validation_result["errors"].append({
                    "field": "status",
                    "message": "Proyecto completado sin fecha de fin",
                    "code": "COMPLETED_NO_END_DATE"
                })
        
        if project.status == ProjectStatus.ACTIVE:
            if not project.start_date:
                validation_result["warnings"].append({
                    "field": "status",
                    "message": "Proyecto activo sin fecha de inicio",
                    "code": "ACTIVE_NO_START_DATE"
                })
