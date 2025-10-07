# -*- coding: utf-8 -*-
"""
Módulo de Operaciones CRUD para Proyectos

Implementa las operaciones básicas de creación, lectura, actualización y eliminación
de proyectos con validaciones de negocio y manejo robusto de errores.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from planificador.models.project import Project, ProjectStatus
from planificador.schemas.project.project import (
    ProjectCreate,
    ProjectUpdate,
    Project,
    ProjectCloneSchema
)
from planificador.repositories.project.project_repository_facade import ProjectRepositoryFacade
from planificador.exceptions.domain.project_domain_exceptions import (
    ProjectValidationError,
    ProjectCodeDuplicateError,
    ProjectTrigramDuplicateError,
    ProjectBusinessRuleViolationError,
    ProjectAssignmentError,
    create_project_not_found_error,
    create_project_validation_error,
    create_project_business_rule_error
)
from planificador.exceptions.base import NotFoundError
from planificador.config.config import settings


class ProjectCrudOperations:
    """
    Operaciones CRUD especializadas para proyectos.
    
    Maneja las operaciones básicas de creación, lectura, actualización y eliminación
    de proyectos con validaciones completas de negocio y transformación de datos.
    """

    def __init__(self, repository_facade: ProjectRepositoryFacade):
        """
        Inicializa las operaciones CRUD.
        
        Args:
            repository_facade: Facade del repositorio de proyectos
        """
        self.repository = repository_facade
        self._logger = logger.bind(module="project_crud_operations")

    async def create_project(self, project_data: ProjectCreate) -> Project:
        """
        Crea un nuevo proyecto con validaciones completas de negocio.
        
        Args:
            project_data: Datos del proyecto a crear
            
        Returns:
            Project: Proyecto creado con información completa
            
        Raises:
            ProjectValidationError: Si los datos no son válidos
            ProjectCodeDuplicateError: Si el código ya existe
            ProjectTrigramDuplicateError: Si el trigrama ya existe
            ProjectBusinessRuleViolationError: Si viola reglas de negocio
        """
        self._logger.info(f"Iniciando creación de proyecto: {project_data.name}")
        
        try:
            # Validar datos de entrada
            await self._validate_create_data(project_data)
            
            # Verificar duplicados
            await self._check_duplicates_for_create(project_data)
            
            # Validar reglas de negocio específicas
            await self._validate_business_rules_for_create(project_data)
            
            # Transformar datos para creación
            transformed_data = await self._transform_data_for_create(project_data)
            
            # Crear proyecto en repositorio
            created_project = await self.repository.create_project(transformed_data)
            
            if not created_project:
                raise ProjectBusinessRuleViolationError(
                    message="No se pudo crear el proyecto",
                    operation="create_project",
                    project_data=project_data.model_dump()
                )
            
            # Convertir a schema de respuesta
            response_schema = Project.model_validate(created_project)
            
            self._logger.info(f"Proyecto creado exitosamente: ID {created_project.id}")
            return response_schema
            
        except (ProjectValidationError, ProjectCodeDuplicateError, 
                ProjectTrigramDuplicateError, ProjectBusinessRuleViolationError) as e:
            self._logger.error(f"Error de validación al crear proyecto: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al crear proyecto: {e}")
            raise create_project_business_rule_error(
                message=f"Error inesperado al crear proyecto: {e}",
                operation="create_project",
                project_data=project_data.model_dump(),
                original_error=e
            )

    async def duplicate_project(
        self, 
        project_id: UUID, 
        new_project_data: ProjectCloneSchema
    ) -> Project:
        """
        Duplica un proyecto existente con nuevos datos.
        
        Args:
            project_id: ID del proyecto a duplicar
            new_project_data: Datos para el nuevo proyecto
            
        Returns:
            Project: El proyecto duplicado
            
        Raises:
            ProjectValidationError: Si el proyecto original no existe o los datos no son válidos
            ProjectCodeDuplicateError: Si la referencia ya existe
            ProjectTrigramDuplicateError: Si el trigrama ya existe
        """
        self._logger.info(f"Duplicando proyecto {project_id}")
        
        try:
            # Obtener el proyecto original
            original_project = await self.repository.get_by_id(project_id)
            if not original_project:
                raise create_project_not_found_error(
                    message=f"Proyecto con ID {project_id} no encontrado",
                    project_id=project_id,
                    operation="duplicate_project"
                )
            
            # Verificar duplicados para los nuevos datos
            await self._check_duplicates_for_duplicate(new_project_data)
            
            # Crear datos del nuevo proyecto basado en el original
            project_create_data = {
                "name": new_project_data.name,
                "reference": new_project_data.reference,
                "trigram": new_project_data.trigram,
                "description": original_project.description,
                "client_id": new_project_data.client_id or original_project.client_id,
                "status": ProjectStatus.PLANNING,  # Nuevo proyecto siempre inicia en PLANNING
                "priority": original_project.priority,
                "start_date": original_project.start_date,
                "end_date": original_project.end_date,
                "estimated_hours": original_project.estimated_hours,
                "actual_hours": 0.0,  # Resetear horas actuales
                "completion_percentage": 0.0,  # Resetear progreso
                "is_billable": original_project.is_billable,
                "notes": f"Duplicado de: {original_project.name} (Ref: {original_project.reference})"
            }
            
            # Crear el nuevo proyecto usando el método create_project existente
            project_create = ProjectCreate(**project_create_data)
            new_project = await self.create_project(project_create)
            
            self._logger.info(f"Proyecto duplicado exitosamente: {new_project.id}")
            return new_project
            
        except (ProjectValidationError, ProjectCodeDuplicateError, 
                ProjectTrigramDuplicateError, ProjectBusinessRuleViolationError) as e:
            self._logger.error(f"Error de validación al duplicar proyecto: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al duplicar proyecto: {e}")
            raise create_project_business_rule_error(
                message=f"Error inesperado al duplicar proyecto: {e}",
                operation="duplicate_project",
                project_id=project_id,
                original_error=e
            )

    async def get_project_by_id(self, project_id: UUID) -> Optional[Project]:
        """
        Obtiene un proyecto por su ID con información básica.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Optional[Project]: Proyecto encontrado o None
        """
        self._logger.debug(f"Obteniendo proyecto por ID: {project_id}")
        
        try:
            project = await self.repository.get_by_id(project_id)
            
            if not project:
                self._logger.warning(f"Proyecto no encontrado: ID {project_id}")
                return None
            
            response_schema = Project.model_validate(project)
            self._logger.debug(f"Proyecto obtenido exitosamente: ID {project_id}")
            return response_schema
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyecto {project_id}: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyecto: {e}",
                operation="get_project_by_id",
                project_id=project_id,
                original_error=e
            )

    async def update_project(
        self, 
        project_id: UUID, 
        project_data: ProjectUpdate
    ) -> Project:
        """
        Actualiza un proyecto existente con validaciones de negocio.
        
        Args:
            project_id: ID del proyecto a actualizar
            project_data: Datos de actualización
            
        Returns:
            Optional[Project]: Proyecto actualizado o None
            
        Raises:
            ProjectValidationError: Si los datos no son válidos
            ProjectStatusTransitionError: Si la transición de estado no es válida
        """
        self._logger.info(f"Iniciando actualización de proyecto: ID {project_id}")
        
        try:
            # Verificar que el proyecto existe
            existing_project = await self.repository.get_by_id(project_id)
            if not existing_project:
                self._logger.warning(f"Proyecto no encontrado para actualizar: ID {project_id}")
                return None
            
            # Validar datos de actualización
            await self._validate_update_data(project_id, project_data, existing_project)
            
            # Verificar duplicados si se cambian códigos
            await self._check_duplicates_for_update(project_id, project_data)
            
            # Validar transiciones de estado
            await self._validate_status_transition(existing_project, project_data)
            
            # Transformar datos para actualización
            transformed_data = await self._transform_data_for_update(project_data, existing_project)
            
            # Actualizar proyecto en repositorio
            updated_project = await self.repository.update_project(project_id, transformed_data)
            
            if not updated_project:
                raise ProjectBusinessRuleViolationError(
                    message="No se pudo actualizar el proyecto",
                    operation="update_project",
                    project_id=project_id,
                    project_data=project_data.model_dump()
                )
            
            # Convertir a schema de respuesta
            response_schema = Project.model_validate(updated_project)
            
            self._logger.info(f"Proyecto actualizado exitosamente: ID {project_id}")
            return response_schema
            
        except (ProjectValidationError, ProjectBusinessRuleViolationError) as e:
            self._logger.error(f"Error de validación al actualizar proyecto {project_id}: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al actualizar proyecto {project_id}: {e}")
            raise create_project_business_rule_error(
                message=f"Error inesperado al actualizar proyecto: {e}",
                operation="update_project",
                project_id=project_id,
                original_error=e
            )

    async def delete_project(self, project_id: UUID) -> bool:
        """
        Elimina un proyecto verificando dependencias y reglas de negocio.
        
        Args:
            project_id: ID del proyecto a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            ProjectAssignmentError: Si tiene asignaciones activas
            ProjectBusinessRuleViolationError: Si no se puede eliminar
        """
        self._logger.info(f"Iniciando eliminación de proyecto: ID {project_id}")
        
        try:
            # Verificar que el proyecto existe
            existing_project = await self.repository.get_by_id(project_id)
            if not existing_project:
                self._logger.warning(f"Proyecto no encontrado para eliminar: ID {project_id}")
                return False
            
            # Validar que se puede eliminar
            await self._validate_can_delete(existing_project)
            
            # Eliminar proyecto en repositorio
            deleted = await self.repository.delete_project(project_id)
            
            if deleted:
                self._logger.info(f"Proyecto eliminado exitosamente: ID {project_id}")
            else:
                self._logger.warning(f"No se pudo eliminar el proyecto: ID {project_id}")
            
            return deleted
            
        except (ProjectAssignmentError, ProjectBusinessRuleViolationError) as e:
            self._logger.error(f"Error de validación al eliminar proyecto {project_id}: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al eliminar proyecto {project_id}: {e}")
            raise create_project_business_rule_error(
                message=f"Error inesperado al eliminar proyecto: {e}",
                operation="delete_project",
                project_id=project_id,
                original_error=e
            )

    async def archive_project(self, project_id: UUID) -> Project:
        """
        Archiva un proyecto verificando que esté en estado válido.
        
        Args:
            project_id: ID del proyecto a archivar
            
        Returns:
            Optional[Project]: Proyecto archivado o None
        """
        self._logger.info(f"Iniciando archivado de proyecto: ID {project_id}")
        
        try:
            # Verificar que el proyecto existe
            existing_project = await self.repository.get_by_id(project_id)
            if not existing_project:
                self._logger.warning(f"Proyecto no encontrado para archivar: ID {project_id}")
                return None
            
            # Validar que se puede archivar
            await self._validate_can_archive(existing_project)
            
            # Archivar proyecto (cambiar estado a ARCHIVED)
            archive_data = {"status": ProjectStatus.ARCHIVED}
            archived_project = await self.repository.update_project(project_id, archive_data)
            
            if not archived_project:
                raise ProjectBusinessRuleViolationError(
                    message="No se pudo archivar el proyecto",
                    operation="archive_project",
                    project_id=project_id
                )
            
            # Convertir a schema de respuesta
            response_schema = Project.model_validate(archived_project)
            
            self._logger.info(f"Proyecto archivado exitosamente: ID {project_id}")
            return response_schema
            
        except ProjectBusinessRuleViolationError as e:
            self._logger.error(f"Error de validación al archivar proyecto {project_id}: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al archivar proyecto {project_id}: {e}")
            raise create_project_business_rule_error(
                message=f"Error inesperado al archivar proyecto: {e}",
                operation="archive_project",
                project_id=project_id,
                original_error=e
            )

    # ============================================================================
    # MÉTODOS PRIVADOS DE VALIDACIÓN
    # ============================================================================

    async def _validate_create_data(self, project_data: ProjectCreate) -> None:
        """Valida datos básicos para creación."""
        if not project_data.name or not project_data.name.strip():
            raise create_project_validation_error(
                message="El nombre del proyecto es obligatorio",
                field="name",
                value=project_data.name
            )
        
        if not project_data.reference or not project_data.reference.strip():
            raise create_project_validation_error(
                message="La referencia del proyecto es obligatoria",
                field="reference",
                value=project_data.reference
            )
        
        if not project_data.trigram or not project_data.trigram.strip():
            raise create_project_validation_error(
                message="El trigrama del proyecto es obligatorio",
                field="trigram",
                value=project_data.trigram
            )
        
        # Validar longitud del trigrama
        if len(project_data.trigram) != 3:
            raise create_project_validation_error(
                message="El trigrama debe tener exactamente 3 caracteres",
                field="trigram",
                value=project_data.trigram
            )

    async def _check_duplicates_for_create(self, project_data: ProjectCreate) -> None:
        """Verifica duplicados para creación."""
        # Verificar referencia duplicada
        if await self.repository.reference_exists(project_data.reference):
            raise ProjectCodeDuplicateError(
                message=f"Ya existe un proyecto con la referencia: {project_data.reference}",
                field="reference",
                value=project_data.reference,
                operation="create_project"
            )
        
        # Verificar trigrama duplicado
        if await self.repository.trigram_exists(project_data.trigram):
            raise ProjectTrigramDuplicateError(
                message=f"Ya existe un proyecto con el trigrama: {project_data.trigram}",
                field="trigram",
                value=project_data.trigram,
                operation="create_project"
            )

    async def _validate_business_rules_for_create(self, project_data: ProjectCreate) -> None:
        """Valida reglas de negocio específicas para creación."""
        # Validar fechas si están presentes
        if project_data.start_date and project_data.end_date:
            if project_data.start_date >= project_data.end_date:
                raise create_project_validation_error(
                    message="La fecha de inicio debe ser anterior a la fecha de fin",
                    field="dates",
                    value=f"start: {project_data.start_date}, end: {project_data.end_date}"
                )
        
        # Validar cliente si está presente
        if project_data.client_id:
            # Aquí se podría validar que el cliente existe
            # Por ahora solo validamos que sea un ID válido
            if project_data.client_id <= 0:
                raise create_project_validation_error(
                    message="El ID del cliente debe ser un número positivo",
                    field="client_id",
                    value=project_data.client_id
                )

    async def _validate_update_data(
        self, 
        project_id: UUID, 
        project_data: ProjectUpdate, 
        existing_project: Project
    ) -> None:
        """Valida datos para actualización."""
        # Validar que al menos un campo se está actualizando
        update_fields = {k: v for k, v in project_data.model_dump(exclude_unset=True).items() if v is not None}
        if not update_fields:
            raise create_project_validation_error(
                message="Debe proporcionar al menos un campo para actualizar",
                field="update_data",
                value=str(update_fields)
            )
        
        # Validar campos específicos si están presentes
        if project_data.name is not None and (not project_data.name or not project_data.name.strip()):
            raise create_project_validation_error(
                message="El nombre del proyecto no puede estar vacío",
                field="name",
                value=project_data.name
            )

    async def _check_duplicates_for_update(
        self, 
        project_id: UUID, 
        project_data: ProjectUpdate
    ) -> None:
        """Verifica duplicados para actualización."""
        # Verificar referencia duplicada si se está cambiando
        if project_data.reference is not None:
            existing_with_reference = await self.repository.get_by_reference(project_data.reference)
            if existing_with_reference and existing_with_reference.id != project_id:
                raise ProjectCodeDuplicateError(
                    message=f"Ya existe otro proyecto con la referencia: {project_data.reference}",
                    field="reference",
                    value=project_data.reference,
                    operation="update_project"
                )
        
        # Verificar trigrama duplicado si se está cambiando
        if project_data.trigram is not None:
            existing_with_trigram = await self.repository.get_by_trigram(project_data.trigram)
            if existing_with_trigram and existing_with_trigram.id != project_id:
                raise ProjectTrigramDuplicateError(
                    message=f"Ya existe otro proyecto con el trigrama: {project_data.trigram}",
                    field="trigram",
                    value=project_data.trigram,
                    operation="update_project"
                )

    async def _validate_status_transition(
        self, 
        existing_project: Project, 
        project_data: ProjectUpdate
    ) -> None:
        """Valida transiciones de estado válidas."""
        if project_data.status is None:
            return
        
        current_status = existing_project.status
        new_status = project_data.status
        
        # Definir transiciones válidas
        valid_transitions = {
            ProjectStatus.PLANNING: [ProjectStatus.ACTIVE, ProjectStatus.CANCELLED],
            ProjectStatus.ACTIVE: [ProjectStatus.ON_HOLD, ProjectStatus.COMPLETED, ProjectStatus.CANCELLED],
            ProjectStatus.ON_HOLD: [ProjectStatus.ACTIVE, ProjectStatus.CANCELLED],
            ProjectStatus.COMPLETED: [ProjectStatus.ARCHIVED],
            ProjectStatus.CANCELLED: [ProjectStatus.ARCHIVED],
            ProjectStatus.ARCHIVED: []  # No se puede cambiar desde archivado
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise ProjectBusinessRuleViolationError(
                message=f"Transición de estado no válida: {current_status} -> {new_status}",
                operation="update_project",
                project_id=existing_project.id,
                details={
                    "current_status": current_status,
                    "new_status": new_status,
                    "valid_transitions": valid_transitions.get(current_status, [])
                }
            )

    async def _validate_can_delete(self, project: Project) -> None:
        """Valida que un proyecto se puede eliminar."""
        # No se pueden eliminar proyectos activos
        if project.status == ProjectStatus.ACTIVE:
            raise ProjectBusinessRuleViolationError(
                message="No se puede eliminar un proyecto activo",
                operation="delete_project",
                project_id=project.id,
                details={"current_status": project.status}
            )
        
        # Verificar si tiene asignaciones activas (esto requeriría consultar asignaciones)
        # Por ahora solo validamos el estado

    async def _validate_can_archive(self, project: Project) -> None:
        """Valida que un proyecto se puede archivar."""
        # Solo se pueden archivar proyectos completados o cancelados
        valid_statuses = [ProjectStatus.COMPLETED, ProjectStatus.CANCELLED]
        if project.status not in valid_statuses:
            raise ProjectBusinessRuleViolationError(
                message=f"Solo se pueden archivar proyectos completados o cancelados. Estado actual: {project.status}",
                operation="archive_project",
                project_id=project.id,
                details={
                    "current_status": project.status,
                    "valid_statuses": valid_statuses
                }
            )

    # ============================================================================
    # MÉTODOS PRIVADOS DE TRANSFORMACIÓN
    # ============================================================================

    async def _transform_data_for_create(self, project_data: ProjectCreate) -> Dict[str, Any]:
        """Transforma datos para creación."""
        transformed = project_data.model_dump(exclude_unset=True)
        
        # Agregar campos calculados o por defecto
        if "status" not in transformed:
            transformed["status"] = ProjectStatus.PLANNING
        
        # Normalizar strings
        if "name" in transformed:
            transformed["name"] = transformed["name"].strip()
        if "reference" in transformed:
            transformed["reference"] = transformed["reference"].strip().upper()
        if "trigram" in transformed:
            transformed["trigram"] = transformed["trigram"].strip().upper()
        
        return transformed

    async def _check_duplicates_for_duplicate(self, new_project_data: ProjectCloneSchema) -> None:
        """Verifica duplicados para duplicación de proyecto."""
        # Verificar referencia duplicada
        if await self.repository.reference_exists(new_project_data.reference):
            raise ProjectCodeDuplicateError(
                message=f"Ya existe un proyecto con la referencia: {new_project_data.reference}",
                field="reference",
                value=new_project_data.reference,
                operation="duplicate_project"
            )
        
        # Verificar trigrama duplicado
        if await self.repository.trigram_exists(new_project_data.trigram):
            raise ProjectTrigramDuplicateError(
                message=f"Ya existe un proyecto con el trigrama: {new_project_data.trigram}",
                field="trigram",
                value=new_project_data.trigram,
                operation="duplicate_project"
            )

    async def create_project_with_validation(
        self,
        project_data: Dict[str, Any],
        validate_business_rules: bool = True
    ) -> Project:
        """Crea un proyecto con validación completa."""
        # Convertir dict a ProjectCreate
        project_create = ProjectCreate(**project_data)
        return await self.create_project(project_create)

    async def bulk_create_projects(self, projects_data: List[ProjectCreate]) -> List[Project]:
        """Crea múltiples proyectos en lote."""
        results = []
        for project_data in projects_data:
            project = await self.create_project(project_data)
            results.append(project)
        return results

    async def restore_project(self, project_id: UUID) -> bool:
        """Restaura un proyecto eliminado."""
        # Implementación básica - delegar al repositorio
        return await self.repository.restore_project(project_id)

    async def _transform_data_for_update(
        self, 
        project_data: ProjectUpdate, 
        existing_project: Project
    ) -> Dict[str, Any]:
        """Transforma datos para actualización."""
        transformed = project_data.model_dump(exclude_unset=True, exclude_none=True)
        
        # Normalizar strings si están presentes
        if "name" in transformed and transformed["name"]:
            transformed["name"] = transformed["name"].strip()
        if "reference" in transformed and transformed["reference"]:
            transformed["reference"] = transformed["reference"].strip().upper()
        if "trigram" in transformed and transformed["trigram"]:
            transformed["trigram"] = transformed["trigram"].strip().upper()
        
        return transformed