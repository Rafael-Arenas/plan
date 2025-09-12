# src/planificador/database/repositories/project/project_validator.py

from typing import Optional, Dict, Any, List
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from ....models.project import Project, ProjectStatus, ProjectPriority
from ....models.client import Client
from ....exceptions.domain import (
    ProjectValidationError,
    ProjectConflictError,
    ProjectDateError,
    ProjectNotFoundError
)
from ....exceptions.repository import (
    convert_sqlalchemy_error,
    create_project_validation_repository_error
)
from ....utils.date_utils import get_current_time
from .project_query_builder import ProjectQueryBuilder


class ProjectValidator:
    """
    Validador especializado para proyectos.
    
    Centraliza toda la lógica de validación de datos de proyectos,
    incluyendo validaciones de negocio, integridad referencial y reglas específicas.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.query_builder = ProjectQueryBuilder(session)
        self._logger = logging.getLogger(__name__)
    
    # ============================================================================
    # VALIDACIONES PRINCIPALES
    # ============================================================================
    
    async def validate_project_data(self, project_data: Dict[str, Any], project_id: Optional[int] = None) -> None:
        """
        Valida los datos completos de un proyecto.
        
        Args:
            project_data: Diccionario con los datos del proyecto
            project_id: ID del proyecto (para actualizaciones)
            
        Raises:
            ProjectValidationError: Si los datos no son válidos
        """
        await self._validate_required_fields(project_data)
        await self._validate_reference_uniqueness(project_data.get('reference'), project_id)
        await self._validate_trigram_uniqueness(project_data.get('trigram'), project_id)
        await self._validate_dates(project_data)
        await self._validate_client_exists(project_data.get('client_id'))
        await self._validate_business_rules(project_data)
    
    async def validate_project_deletion(self, project: Project) -> None:
        """
        Valida si un proyecto puede ser eliminado.
        
        Args:
            project: Proyecto a validar
            
        Raises:
            ProjectValidationError: Si el proyecto no puede ser eliminado
        """
        # No permitir eliminar proyectos en progreso
        if project.status == ProjectStatus.IN_PROGRESS:
            raise ProjectValidationError(
                "No se puede eliminar un proyecto que está en progreso"
            )
        
        # Verificar si tiene asignaciones activas
        from sqlalchemy import select, func
        from ....models.project_assignment import ProjectAssignment
        
        query = select(func.count(ProjectAssignment.id)).where(
            ProjectAssignment.project_id == project.id,
            ProjectAssignment.is_active == True
        )
        result = await self.session.execute(query)
        active_assignments = result.scalar()
        
        if active_assignments > 0:
            raise ProjectValidationError(
                "No se puede eliminar un proyecto con asignaciones activas"
            )
    
    # ============================================================================
    # VALIDACIONES DE ESTADO
    # ============================================================================
    
    async def validate_project_archival(self, project: Project) -> None:
        """
        Valida si un proyecto puede ser archivado.
        
        Args:
            project: Proyecto a validar
            
        Raises:
            ProjectValidationError: Si el proyecto no puede ser archivado
        """
        # Solo permitir archivar proyectos completados o cancelados
        allowed_statuses = [ProjectStatus.COMPLETED, ProjectStatus.CANCELLED]
        
        if project.status not in allowed_statuses:
            raise ProjectValidationError(
                "Solo se pueden archivar proyectos completados o cancelados"
            )
    
    # ============================================================================
    # VALIDACIONES DE FORMATO
    # ============================================================================
    
    def validate_reference_format(self, reference: str) -> None:
        """
        Valida el formato de la referencia del proyecto.
        
        Args:
            reference: Referencia a validar
            
        Raises:
            ProjectValidationError: Si el formato no es válido
        """
        if not reference:
            raise ProjectValidationError(
                field="reference",
                value=reference,
                reason="La referencia es requerida"
            )
        
        # Validar longitud
        if len(reference) < 3 or len(reference) > 20:
            raise ProjectValidationError(
                field="reference",
                value=reference,
                reason="La referencia debe tener entre 3 y 20 caracteres"
            )
        
        # Validar caracteres permitidos (alfanuméricos, guiones y guiones bajos)
        import re
        if not re.match(r'^[A-Za-z0-9_-]+$', reference):
            raise ProjectValidationError(
                field="reference",
                value=reference,
                reason="La referencia solo puede contener letras, números, guiones y guiones bajos"
            )
    
    def validate_trigram_format(self, trigram: str) -> None:
        """
        Valida el formato del trigrama del proyecto.
        
        Args:
            trigram: Trigrama a validar
            
        Raises:
            ProjectValidationError: Si el formato no es válido
        """
        if not trigram:
            raise ProjectValidationError(
                field="trigram",
                value=trigram,
                reason="El trigrama es requerido"
            )
        
        # Validar longitud exacta
        if len(trigram) != 3:
            raise ProjectValidationError(
                field="trigram",
                value=trigram,
                reason="El trigrama debe tener exactamente 3 caracteres"
            )
        
        # Validar que sean solo letras mayúsculas
        if not trigram.isupper() or not trigram.isalpha():
            raise ProjectValidationError(
                field="trigram",
                value=trigram,
                reason="El trigrama debe contener solo letras mayúsculas"
            )
    
    # ============================================================================
    # VALIDACIONES INTERNAS - CAMPOS REQUERIDOS
    # ============================================================================
    
    async def _validate_required_fields(self, project_data: Dict[str, Any]) -> None:
        """Valida que los campos requeridos estén presentes."""
        required_fields = ['name', 'reference', 'trigram', 'client_id', 'start_date', 'end_date']
        missing_fields = []
        
        for field in required_fields:
            if field not in project_data or project_data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ProjectValidationError(
                f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            )
    
    # ============================================================================
    # VALIDACIONES INTERNAS - UNICIDAD
    # ============================================================================
    
    async def _validate_reference_uniqueness(self, reference: str, exclude_id: Optional[int] = None) -> None:
        """Valida que la referencia sea única."""
        if not reference:
            return
        
        try:
            query = self.query_builder.build_reference_exists_query(reference, exclude_id)
            result = await self.session.execute(query)
            count = result.scalar()
            
            if count > 0:
                raise ProjectConflictError(
                    'reference', reference
                )
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD validando unicidad de referencia de proyecto: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_reference_uniqueness",
                entity_type="Project",
                entity_id=exclude_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando unicidad de referencia de proyecto: {e}")
            raise create_project_validation_repository_error(
                message=f"Error inesperado validando referencia: {e}",
                details={"reference": reference, "exclude_id": exclude_id, "original_error": str(e)}
            )
    
    async def _validate_trigram_uniqueness(self, trigram: str, exclude_id: Optional[int] = None) -> None:
        """Valida que el trigrama sea único."""
        if not trigram:
            return
        
        try:
            query = self.query_builder.build_trigram_exists_query(trigram, exclude_id)
            result = await self.session.execute(query)
            count = result.scalar()
            
            if count > 0:
                raise ProjectConflictError(
                    'trigram', trigram
                )
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD validando unicidad de trigrama de proyecto: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_trigram_uniqueness",
                entity_type="Project",
                entity_id=exclude_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando unicidad de trigrama de proyecto: {e}")
            raise create_project_validation_repository_error(
                message=f"Error inesperado validando trigrama: {e}",
                details={"trigram": trigram, "exclude_id": exclude_id, "original_error": str(e)}
            )
    
    # ============================================================================
    # VALIDACIONES INTERNAS - FECHAS Y RELACIONES
    # ============================================================================
    
    async def _validate_dates(self, project_data: Dict[str, Any]) -> None:
        """Valida la coherencia de las fechas del proyecto."""
        start_date = project_data.get('start_date')
        end_date = project_data.get('end_date')
        
        if not start_date or not end_date:
            return
        
        # Validar que la fecha de fin sea posterior a la de inicio
        if end_date <= start_date:
            raise ProjectDateError(
                start_date, end_date
            )
        
        # Validar que las fechas no sean muy antiguas (más de 10 años)
        current_date = get_current_time().date()
        ten_years_ago = current_date.replace(year=current_date.year - 10)
        
        if start_date < ten_years_ago:
            raise ProjectValidationError(
                'start_date', start_date, "La fecha de inicio no puede ser anterior a 10 años"
            )
        
        # Validar que las fechas no sean muy futuras (más de 5 años)
        five_years_future = current_date.replace(year=current_date.year + 5)
        
        if end_date > five_years_future:
            raise ProjectValidationError(
                'end_date', end_date, "La fecha de fin no puede ser posterior a 5 años en el futuro"
            )
    
    async def _validate_client_exists(self, client_id: int) -> None:
        """Valida que el cliente exista."""
        if not client_id:
            return
        
        try:
            from sqlalchemy import select
            query = select(Client).where(Client.id == client_id)
            result = await self.session.execute(query)
            client = result.scalar_one_or_none()
            
            if not client:
                raise ProjectNotFoundError(
                    f"No se encontró el cliente con ID {client_id}"
                )
                
        except SQLAlchemyError as e:
            self._logger.error(f"Error de BD validando existencia de cliente: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_client_exists",
                entity_type="Client",
                entity_id=client_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando existencia de cliente: {e}")
            raise create_project_validation_repository_error(
                message=f"Error inesperado validando cliente: {e}",
                details={"client_id": client_id, "original_error": str(e)}
            )
    
    # ============================================================================
    # VALIDACIONES INTERNAS - REGLAS DE NEGOCIO
    # ============================================================================
    
    async def _validate_business_rules(self, project_data: Dict[str, Any]) -> None:
        """Valida reglas de negocio específicas."""
        await self._validate_status_transitions(project_data)
        await self._validate_priority_consistency(project_data)
        await self._validate_budget_consistency(project_data)
    
    async def _validate_status_transitions(self, project_data: Dict[str, Any]) -> None:
        """Valida transiciones válidas de estado."""
        status = project_data.get('status')
        if not status:
            return
        
        # Validar que el estado sea válido
        if status not in ProjectStatus:
            raise ProjectValidationError(
                f"Estado de proyecto inválido: {status}"
            )
        
        # Validar coherencia entre estado y fechas
        start_date = project_data.get('start_date')
        end_date = project_data.get('end_date')
        current_date = get_current_time().date()
        
        if status == ProjectStatus.COMPLETED and end_date and end_date > current_date:
            raise ProjectValidationError(
                "Un proyecto no puede estar completado si su fecha de fin es futura"
            )
        
        if status == ProjectStatus.IN_PROGRESS:
            if start_date and start_date > current_date:
                raise ProjectValidationError(
                    "Un proyecto no puede estar en progreso si su fecha de inicio es futura"
                )
    
    async def _validate_priority_consistency(self, project_data: Dict[str, Any]) -> None:
        """Valida la consistencia de la prioridad."""
        priority = project_data.get('priority')
        if not priority:
            return
        
        # Validar que la prioridad sea válida
        if priority not in ProjectPriority:
            raise ProjectValidationError(
                f"Prioridad de proyecto inválida: {priority}"
            )
    
    async def _validate_budget_consistency(self, project_data: Dict[str, Any]) -> None:
        """Valida la consistencia del presupuesto."""
        budget = project_data.get('budget')
        if budget is None:
            return
        
        if budget < 0:
            raise ProjectValidationError(
                "El presupuesto no puede ser negativo"
            )
        
        # Validar límites razonables de presupuesto
        if budget > 10_000_000:  # 10 millones
            raise ProjectValidationError(
                "El presupuesto excede el límite máximo permitido"
            )