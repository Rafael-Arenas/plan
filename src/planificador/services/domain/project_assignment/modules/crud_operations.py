# src/planificador/services/domain/project_assignment/modules/crud_operations.py

"""
Módulo de Operaciones CRUD para Asignaciones de Proyecto

Implementa las operaciones CRUD principales y especializadas para
el dominio de asignaciones de proyecto, incluyendo validaciones
y manejo de errores robusto.
"""

from typing import List, Optional, Dict, Any
from loguru import logger

from planificador.schemas import (
    ProjectAssignment,
    ProjectAssignmentCreate,
    ProjectAssignmentUpdate
)
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.exceptions import (
    ValidationError,
    RepositoryError,
    BusinessLogicError
)
from ..interfaces import ICrudOperations


class CrudOperations(ICrudOperations):
    """
    Implementación de operaciones CRUD para asignaciones de proyecto.
    
    Maneja las operaciones básicas y especializadas de creación, lectura,
    actualización y eliminación de asignaciones, con validaciones
    de reglas de negocio integradas.
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """
        Inicializa el módulo de operaciones CRUD.
        
        Args:
            repository_facade: Facade del repositorio de asignaciones
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="project_assignment_crud")
    
    # ============================================================================
    # OPERACIONES CRUD PRINCIPALES (4 métodos)
    # ============================================================================
    
    async def create_assignment(self, assignment_data: ProjectAssignmentCreate) -> ProjectAssignment:
        """
        Crea una nueva asignación de proyecto con validaciones completas.
        
        Args:
            assignment_data: Datos de la nueva asignación
            
        Returns:
            ProjectAssignment: Asignación creada
            
        Raises:
            ValidationError: Si los datos no son válidos
            BusinessLogicError: Si viola reglas de negocio
            RepositoryError: Si hay errores en la persistencia
        """
        try:
            self._logger.info(
                f"Creando nueva asignación para empleado {assignment_data.employee_id} "
                f"en proyecto {assignment_data.project_id}"
            )
            
            # Validar datos básicos
            await self._validate_assignment_data(assignment_data)
            
            # Verificar reglas de negocio
            await self._validate_business_rules(assignment_data)
            
            # Crear la asignación
            created_assignment = await self._repository.crud.create(assignment_data)
            
            self._logger.info(f"Asignación creada exitosamente con ID: {created_assignment.id}")
            return created_assignment
            
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al crear asignación: {e}")
            raise RepositoryError(
                message=f"Error inesperado al crear asignación: {e}",
                operation="create_assignment",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def update_assignment(
        self, 
        assignment_id: int, 
        update_data: ProjectAssignmentUpdate
    ) -> ProjectAssignment:
        """
        Actualiza una asignación existente con validaciones de integridad.
        
        Args:
            assignment_id: ID de la asignación a actualizar
            update_data: Datos de actualización
            
        Returns:
            ProjectAssignment: Asignación actualizada
            
        Raises:
            ValidationError: Si los datos de actualización no son válidos
            BusinessLogicError: Si viola reglas de negocio
            RepositoryError: Si hay errores en la persistencia
        """
        try:
            self._logger.info(f"Actualizando asignación ID: {assignment_id}")
            
            # Verificar que la asignación existe
            existing_assignment = await self._repository.crud.get_by_id(assignment_id)
            if not existing_assignment:
                raise ValidationError(
                    message=f"Asignación con ID {assignment_id} no encontrada",
                    field="assignment_id",
                    value=assignment_id
                )
            
            # Validar datos de actualización
            await self._validate_update_data(assignment_id, update_data)
            
            # Actualizar la asignación
            updated_assignment = await self._repository.crud.update(assignment_id, update_data)
            
            self._logger.info(f"Asignación ID: {assignment_id} actualizada exitosamente")
            return updated_assignment
            
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al actualizar asignación {assignment_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al actualizar asignación: {e}",
                operation="update_assignment",
                entity_type="ProjectAssignment",
                entity_id=assignment_id,
                original_error=e
            )
    
    async def delete_assignment(self, assignment_id: int) -> bool:
        """
        Elimina una asignación con verificaciones de integridad.
        
        Args:
            assignment_id: ID de la asignación a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Raises:
            ValidationError: Si la asignación no existe
            BusinessLogicError: Si no se puede eliminar por reglas de negocio
            RepositoryError: Si hay errores en la eliminación
        """
        try:
            self._logger.info(f"Eliminando asignación ID: {assignment_id}")
            
            # Verificar que la asignación existe
            existing_assignment = await self._repository.crud.get_by_id(assignment_id)
            if not existing_assignment:
                raise ValidationError(
                    message=f"Asignación con ID {assignment_id} no encontrada",
                    field="assignment_id",
                    value=assignment_id
                )
            
            # Verificar si se puede eliminar
            await self._validate_deletion_rules(assignment_id)
            
            # Eliminar la asignación
            success = await self._repository.crud.delete(assignment_id)
            
            if success:
                self._logger.info(f"Asignación ID: {assignment_id} eliminada exitosamente")
            else:
                self._logger.warning(f"No se pudo eliminar la asignación ID: {assignment_id}")
            
            return success
            
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al eliminar asignación {assignment_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al eliminar asignación: {e}",
                operation="delete_assignment",
                entity_type="ProjectAssignment",
                entity_id=assignment_id,
                original_error=e
            )
    
    async def get_assignment_by_id(self, assignment_id: int) -> Optional[ProjectAssignment]:
        """
        Obtiene una asignación por su ID.
        
        Args:
            assignment_id: ID de la asignación
            
        Returns:
            Optional[ProjectAssignment]: Asignación encontrada o None
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        try:
            self._logger.debug(f"Obteniendo asignación ID: {assignment_id}")
            
            assignment = await self._repository.crud.get_by_id(assignment_id)
            
            if assignment:
                self._logger.debug(f"Asignación ID: {assignment_id} encontrada")
            else:
                self._logger.debug(f"Asignación ID: {assignment_id} no encontrada")
            
            return assignment
            
        except Exception as e:
            self._logger.error(f"Error al obtener asignación {assignment_id}: {e}")
            raise RepositoryError(
                message=f"Error al obtener asignación: {e}",
                operation="get_assignment_by_id",
                entity_type="ProjectAssignment",
                entity_id=assignment_id,
                original_error=e
            )
    
    # ============================================================================
    # OPERACIONES CRUD ESPECIALIZADAS (3 métodos)
    # ============================================================================
    
    async def bulk_create_assignments(
        self, 
        assignments_data: List[ProjectAssignmentCreate]
    ) -> List[ProjectAssignment]:
        """
        Crea múltiples asignaciones en una operación transaccional.
        
        Args:
            assignments_data: Lista de datos de asignaciones a crear
            
        Returns:
            List[ProjectAssignment]: Lista de asignaciones creadas
            
        Raises:
            ValidationError: Si alguna asignación no es válida
            BusinessLogicError: Si viola reglas de negocio
            RepositoryError: Si hay errores en la persistencia
        """
        try:
            self._logger.info(f"Creando {len(assignments_data)} asignaciones en lote")
            
            # Validar todas las asignaciones antes de crear
            for i, assignment_data in enumerate(assignments_data):
                try:
                    await self._validate_assignment_data(assignment_data)
                    await self._validate_business_rules(assignment_data)
                except Exception as e:
                    raise ValidationError(
                        message=f"Error en asignación {i + 1}: {e}",
                        field=f"assignments[{i}]",
                        value=assignment_data
                    )
            
            # Crear todas las asignaciones
            created_assignments = await self._repository.crud.bulk_create(assignments_data)
            
            self._logger.info(f"{len(created_assignments)} asignaciones creadas exitosamente")
            return created_assignments
            
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en creación en lote: {e}")
            raise RepositoryError(
                message=f"Error inesperado en creación en lote: {e}",
                operation="bulk_create_assignments",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def duplicate_assignment(
        self, 
        source_assignment_id: int, 
        modifications: Optional[Dict[str, Any]] = None
    ) -> ProjectAssignment:
        """
        Duplica una asignación existente con modificaciones opcionales.
        
        Args:
            source_assignment_id: ID de la asignación a duplicar
            modifications: Modificaciones opcionales para la nueva asignación
            
        Returns:
            ProjectAssignment: Nueva asignación duplicada
            
        Raises:
            ValidationError: Si la asignación fuente no existe o las modificaciones no son válidas
            BusinessLogicError: Si la duplicación viola reglas de negocio
            RepositoryError: Si hay errores en la operación
        """
        try:
            self._logger.info(f"Duplicando asignación ID: {source_assignment_id}")
            
            # Obtener asignación fuente
            source_assignment = await self._repository.crud.get_by_id(source_assignment_id)
            if not source_assignment:
                raise ValidationError(
                    message=f"Asignación fuente con ID {source_assignment_id} no encontrada",
                    field="source_assignment_id",
                    value=source_assignment_id
                )
            
            # Crear datos para la nueva asignación
            new_assignment_data = ProjectAssignmentCreate(
                employee_id=source_assignment.employee_id,
                project_id=source_assignment.project_id,
                start_date=source_assignment.start_date,
                end_date=source_assignment.end_date,
                allocated_hours_per_day=source_assignment.allocated_hours_per_day,
                percentage_allocation=source_assignment.percentage_allocation,
                role_in_project=source_assignment.role_in_project,
                is_active=source_assignment.is_active,
                notes=f"Duplicado de asignación #{source_assignment_id}"
            )
            
            # Aplicar modificaciones si se proporcionan
            if modifications:
                for field, value in modifications.items():
                    if hasattr(new_assignment_data, field):
                        setattr(new_assignment_data, field, value)
            
            # Crear la nueva asignación
            duplicated_assignment = await self.create_assignment(new_assignment_data)
            
            self._logger.info(
                f"Asignación duplicada exitosamente. Original: {source_assignment_id}, "
                f"Nueva: {duplicated_assignment.id}"
            )
            return duplicated_assignment
            
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al duplicar asignación {source_assignment_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al duplicar asignación: {e}",
                operation="duplicate_assignment",
                entity_type="ProjectAssignment",
                entity_id=source_assignment_id,
                original_error=e
            )
    
    async def archive_assignment(self, assignment_id: int) -> ProjectAssignment:
        """
        Archiva una asignación (marca como inactiva) en lugar de eliminarla.
        
        Args:
            assignment_id: ID de la asignación a archivar
            
        Returns:
            ProjectAssignment: Asignación archivada
            
        Raises:
            ValidationError: Si la asignación no existe
            RepositoryError: Si hay errores en la operación
        """
        try:
            self._logger.info(f"Archivando asignación ID: {assignment_id}")
            
            # Verificar que la asignación existe
            existing_assignment = await self._repository.crud.get_by_id(assignment_id)
            if not existing_assignment:
                raise ValidationError(
                    message=f"Asignación con ID {assignment_id} no encontrada",
                    field="assignment_id",
                    value=assignment_id
                )
            
            # Archivar (marcar como inactiva)
            update_data = ProjectAssignmentUpdate(is_active=False)
            archived_assignment = await self._repository.crud.update(assignment_id, update_data)
            
            self._logger.info(f"Asignación ID: {assignment_id} archivada exitosamente")
            return archived_assignment
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al archivar asignación {assignment_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al archivar asignación: {e}",
                operation="archive_assignment",
                entity_type="ProjectAssignment",
                entity_id=assignment_id,
                original_error=e
            )
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE VALIDACIÓN
    # ============================================================================
    
    async def _validate_assignment_data(self, assignment_data: ProjectAssignmentCreate) -> None:
        """Valida los datos básicos de una asignación."""
        # Validar fechas
        if assignment_data.start_date >= assignment_data.end_date:
            raise ValidationError(
                message="La fecha de inicio debe ser anterior a la fecha de fin",
                field="date_range",
                value=f"{assignment_data.start_date} - {assignment_data.end_date}"
            )
        
        # Validar porcentaje de asignación
        if not (0 < assignment_data.percentage_allocation <= 100):
            raise ValidationError(
                message="El porcentaje de asignación debe estar entre 1 y 100",
                field="percentage_allocation",
                value=assignment_data.percentage_allocation
            )
        
        # Validar horas por día
        if assignment_data.allocated_hours_per_day <= 0:
            raise ValidationError(
                message="Las horas asignadas por día deben ser mayor a 0",
                field="allocated_hours_per_day",
                value=assignment_data.allocated_hours_per_day
            )
    
    async def _validate_business_rules(self, assignment_data: ProjectAssignmentCreate) -> None:
        """Valida reglas de negocio específicas."""
        # Verificar que no haya superposición de asignaciones
        overlapping = await self._repository.queries.get_overlapping_assignments(
            employee_id=assignment_data.employee_id,
            start_date=assignment_data.start_date,
            end_date=assignment_data.end_date
        )
        
        if overlapping:
            raise BusinessLogicError(
                message=f"El empleado {assignment_data.employee_id} ya tiene asignaciones "
                f"superpuestas en el período especificado",
                rule="no_overlapping_assignments",
                context={
                    "employee_id": assignment_data.employee_id,
                    "conflicting_assignments": len(overlapping)
                }
            )
    
    async def _validate_update_data(
        self, 
        assignment_id: int, 
        update_data: ProjectAssignmentUpdate
    ) -> None:
        """Valida los datos de actualización."""
        # Si se actualizan fechas, validar el rango
        if update_data.start_date and update_data.end_date:
            if update_data.start_date >= update_data.end_date:
                raise ValidationError(
                    message="La fecha de inicio debe ser anterior a la fecha de fin",
                    field="date_range",
                    value=f"{update_data.start_date} - {update_data.end_date}"
                )
        
        # Validar porcentaje si se proporciona
        if update_data.percentage_allocation is not None:
            if not (0 < update_data.percentage_allocation <= 100):
                raise ValidationError(
                    message="El porcentaje de asignación debe estar entre 1 y 100",
                    field="percentage_allocation",
                    value=update_data.percentage_allocation
                )
    
    async def _validate_deletion_rules(self, assignment_id: int) -> None:
        """Valida si una asignación puede ser eliminada."""
        # Aquí se pueden agregar validaciones específicas para eliminación
        # Por ejemplo, verificar si la asignación está vinculada a otros registros
        pass