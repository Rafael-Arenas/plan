# src/planificador/database/repositories/project_repository.py

from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..base_repository import BaseRepository
from ..date_mixin import DateMixin
from .project_query_builder import ProjectQueryBuilder
from .project_validator import ProjectValidator
from .project_relationship_manager import ProjectRelationshipManager
from .project_statistics import ProjectStatistics
from ....models.project import Project, ProjectStatus, ProjectPriority
from ....exceptions.domain import (
    ProjectNotFoundError,
    ProjectValidationError,
    ProjectConflictError
)
from ....exceptions.repository import (
    create_project_query_error,
    create_project_statistics_error,
    create_project_validation_repository_error,
    create_project_relationship_error,
    create_project_bulk_operation_error,
    create_project_date_range_error,
    create_project_reference_error,
    create_project_trigram_error,
    create_project_workload_error,
    convert_sqlalchemy_error,
    ProjectRepositoryError
)
from ....utils.date_utils import get_current_time


class ProjectRepository(BaseRepository[Project], DateMixin):
    """
    Repositorio refactorizado para la gestión de proyectos.
    
    Implementa una arquitectura modular que separa responsabilidades:
    - ProjectQueryBuilder: Construcción de consultas SQL
    - ProjectValidator: Validación de datos y reglas de negocio
    - ProjectRelationshipManager: Gestión de relaciones con otras entidades
    - ProjectStatistics: Cálculo de estadísticas y métricas
    
    Esta arquitectura mejora la mantenibilidad, testabilidad y escalabilidad
    del código siguiendo principios SOLID.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)
        
        # Inicializar componentes modulares
        self.query_builder = ProjectQueryBuilder(session)
        self.validator = ProjectValidator(session)
        self.relationship_manager = ProjectRelationshipManager(session)
        self.statistics = ProjectStatistics(session)
        
        self._logger = logging.getLogger(__name__)
    
    # ==========================================
    # OPERACIONES CRUD BÁSICAS
    # ==========================================
    
    async def create_project(self, project_data: Dict[str, Any]) -> Project:
        """
        Crea un nuevo proyecto con validación completa.
        
        Args:
            project_data: Datos del proyecto
            
        Returns:
            Proyecto creado
            
        Raises:
            ProjectValidationError: Si los datos no son válidos
        """
        try:
            # Validar datos antes de crear
            await self.validator.validate_project_data(project_data)
            
            # Validar formatos específicos
            if 'reference' in project_data:
                self.validator.validate_reference_format(project_data['reference'])
            if 'trigram' in project_data:
                self.validator.validate_trigram_format(project_data['trigram'])
            
            # Crear el proyecto
            project = Project(**project_data)
            self.session.add(project)
            await self.session.flush()
            
            self._logger.info(f"Proyecto creado: {project.reference}")
            return project
            
        except ProjectValidationError:
            # Re-lanzar errores de validación directamente
            await self.session.rollback()
            raise
        except ValueError as e:
            # Convertir ValueError a ProjectValidationRepositoryError
            self._logger.error(f"Error de validación creando proyecto: {e}")
            await self.session.rollback()
            raise create_project_validation_repository_error(
                field="project_data",
                value=project_data,
                reason=f"create_project validation failed: {str(e)}",
                operation="create_project"
            ) from e
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos creando proyecto: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_project",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado creando proyecto: {e}")
            await self.session.rollback()
            raise ProjectRepositoryError(
                message=f"Error inesperado creando proyecto: {e}",
                operation="create_project",
                entity_type="Project",
                original_error=e
            )
    
    async def update_project(self, project_id: int, update_data: Dict[str, Any]) -> Optional[Project]:
        """
        Actualiza un proyecto existente con validación.
        
        Args:
            project_id: ID del proyecto a actualizar
            update_data: Datos a actualizar
            
        Returns:
            Proyecto actualizado o None si no existe
            
        Raises:
            ProjectValidationError: Si los datos no son válidos
        """
        try:
            # Obtener el proyecto existente
            project = await self.get_by_id(project_id)
            if not project:
                raise ProjectNotFoundError(project_id=project_id)
            
            # Validar datos de actualización
            await self.validator.validate_project_data(update_data, project_id)
            
            # Validar formatos específicos si están presentes
            if 'reference' in update_data:
                self.validator.validate_reference_format(update_data['reference'])
            if 'trigram' in update_data:
                self.validator.validate_trigram_format(update_data['trigram'])
            
            # Aplicar actualizaciones
            for key, value in update_data.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            await self.session.flush()
            
            self._logger.info(f"Proyecto actualizado: {project.reference}")
            return project
            
        except ProjectNotFoundError:
            await self.session.rollback()
            raise
        except ProjectValidationError:
            await self.session.rollback()
            raise
        except ValueError as e:
            self._logger.error(f"Error de validación actualizando proyecto {project_id}: {e}")
            await self.session.rollback()
            raise create_project_validation_repository_error(
                field="update_data",
                value=update_data,
                reason=f"update_project validation failed: {str(e)}",
                operation="update_project"
            ) from e
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos actualizando proyecto {project_id}: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_project",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado actualizando proyecto {project_id}: {e}")
            await self.session.rollback()
            raise ProjectRepositoryError(
                message=f"Error inesperado actualizando proyecto {project_id}: {e}",
                operation="update_project",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    # get_by_id está heredado de BaseRepository
    
    async def delete_project(self, project_id: int) -> bool:
        """
        Elimina un proyecto después de validar que puede ser eliminado.
        
        Args:
            project_id: ID del proyecto a eliminar
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            ProjectNotFoundError: Si el proyecto no existe
            ProjectValidationError: Si el proyecto no puede ser eliminado
        """
        try:
            # Obtener el proyecto
            project = await self.get_by_id(project_id)
            if not project:
                raise ProjectNotFoundError(project_id=project_id)
            
            # Validar que puede ser eliminado
            await self.validator.validate_project_deletion(project_id)
            
            # Eliminar el proyecto
            await self.session.delete(project)
            await self.session.flush()
            
            self._logger.info(f"Proyecto eliminado: {project.reference}")
            return True
            
        except (ProjectNotFoundError, ProjectValidationError):
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos eliminando proyecto {project_id}: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="delete_project",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado eliminando proyecto {project_id}: {e}")
            await self.session.rollback()
            raise ProjectRepositoryError(
                message=f"Error inesperado eliminando proyecto {project_id}: {e}",
                operation="delete_project",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    async def archive_project(self, project_id: int) -> Optional[Project]:
        """
        Archiva un proyecto después de validar que puede ser archivado.
        
        Args:
            project_id: ID del proyecto a archivar
            
        Returns:
            Proyecto archivado o None si no existe
            
        Raises:
            ProjectValidationError: Si el proyecto no puede ser archivado
        """
        try:
            # Obtener el proyecto
            project = await self.get_by_id(project_id)
            if not project:
                raise ProjectNotFoundError(project_id=project_id)
            
            # Validar que puede ser archivado
            await self.validator.validate_project_archival(project_id)
            
            # Archivar el proyecto
            project.is_archived = True
            project.archived_at = get_current_time()
            
            await self.session.flush()
            
            self._logger.info(f"Proyecto archivado: {project.reference}")
            return project
            
        except (ProjectNotFoundError, ProjectValidationError):
            await self.session.rollback()
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos archivando proyecto {project_id}: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="archive_project",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado archivando proyecto {project_id}: {e}")
            await self.session.rollback()
            raise ProjectRepositoryError(
                message=f"Error inesperado archivando proyecto {project_id}: {e}",
                operation="archive_project",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    def format_project_dates(self, project: Project) -> Dict[str, Optional[str]]:
        """
        Formatea las fechas de un proyecto para presentación.
        
        Args:
            project: Proyecto a formatear
            
        Returns:
            Diccionario con fechas formateadas
        """
        return self.format_dates(project)
    
    # ==========================================
    # CONSULTAS POR IDENTIFICADORES ÚNICOS
    # ==========================================
    
    async def get_by_reference(self, reference: str) -> Optional[Project]:
        """
        Busca un proyecto por su referencia única.
        
        Args:
            reference: Referencia del proyecto
            
        Returns:
            Proyecto encontrado o None
            
        Raises:
            ProjectReferenceError: Si hay errores en la consulta por referencia
        """
        try:
            query = self.query_builder.build_by_reference_query(reference)
            result = await self.session.execute(query)
            project = result.scalar_one_or_none()
            
            if project:
                self._logger.debug(f"Proyecto encontrado por referencia: {reference}")
            else:
                self._logger.debug(f"Proyecto no encontrado por referencia: {reference}")
            
            return project
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos buscando proyecto por referencia '{reference}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_reference",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado buscando proyecto por referencia '{reference}': {e}")
            raise create_project_reference_error(
                reference=reference,
                reason=str(e),
                operation="get_by_reference"
            )
    
    async def get_by_trigram(self, trigram: str) -> Optional[Project]:
        """
        Busca un proyecto por su trigrama.
        
        Args:
            trigram: Trigrama del proyecto
            
        Returns:
            Proyecto encontrado o None
            
        Raises:
            ProjectTrigramError: Si hay errores en la consulta por trigrama
        """
        try:
            query = self.query_builder.build_by_trigram_query(trigram)
            result = await self.session.execute(query)
            project = result.scalar_one_or_none()
            
            if project:
                self._logger.debug(f"Proyecto encontrado por trigrama: {trigram}")
            else:
                self._logger.debug(f"Proyecto no encontrado por trigrama: {trigram}")
            
            return project
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos buscando proyecto por trigrama '{trigram}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_trigram",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado buscando proyecto por trigrama '{trigram}': {e}")
            raise create_project_trigram_error(
                trigram=trigram,
                reason=str(e),
                operation="get_by_trigram"
            )
    
    async def search_by_name(self, search_term: str) -> List[Project]:
        """
        Busca proyectos cuyo nombre contenga el término de búsqueda.
        
        Args:
            search_term: Término a buscar en el nombre
            
        Returns:
            Lista de proyectos que coinciden
            
        Raises:
            ProjectQueryError: Si hay errores en la consulta de búsqueda
        """
        try:
            query = self.query_builder.build_search_by_name_query(search_term)
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            self._logger.debug(f"Encontrados {len(projects)} proyectos con término: {search_term}")
            return list(projects)
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos buscando proyectos con término '{search_term}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_by_name",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado buscando proyectos con término '{search_term}': {e}")
            raise create_project_query_error(
                query_type="search_by_name",
                parameters={"search_term": search_term},
                reason=str(e)
            )
    
    # ==========================================
    # CONSULTAS POR ATRIBUTOS
    # ==========================================
    
    async def get_by_client(self, client_id: int) -> List[Project]:
        """
        Obtiene todos los proyectos de un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Lista de proyectos del cliente
        """
        try:
            query = self.query_builder.build_by_client_query(client_id)
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(projects)} proyectos del cliente: {client_id}")
            return list(projects)
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyectos del cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_client",
                entity_type="Project",
                entity_id=client_id
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyectos del cliente {client_id}: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado obteniendo proyectos del cliente {client_id}: {e}",
                operation="get_by_client",
                entity_type="Project",
                entity_id=client_id,
                original_error=e
            )
    
    async def get_by_status(self, status: ProjectStatus) -> List[Project]:
        """
        Obtiene proyectos por su estado.
        
        Args:
            status: Estado del proyecto
            
        Returns:
            Lista de proyectos con el estado especificado
        """
        try:
            query = self.query_builder.build_by_status_query(status)
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(projects)} proyectos con estado: {status.value}")
            return list(projects)
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyectos por estado '{status.value}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_status",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyectos por estado '{status.value}': {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado obteniendo proyectos por estado '{status.value}': {e}",
                operation="get_by_status",
                entity_type="Project",
                original_error=e
            )
    
    async def get_active_projects(self) -> List[Project]:
        """
        Obtiene todos los proyectos activos (planificados o en progreso y no archivados).
        
        Returns:
            Lista de proyectos activos
        """
        try:
            query = self.query_builder.build_active_projects_query()
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(projects)} proyectos activos")
            return list(projects)
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyectos activos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_active_projects",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyectos activos: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado obteniendo proyectos activos: {e}",
                operation="get_active_projects",
                entity_type="Project",
                original_error=e
            )
    
    async def get_by_priority(self, priority: ProjectPriority) -> List[Project]:
        """
        Obtiene proyectos por su prioridad.
        
        Args:
            priority: Prioridad del proyecto
            
        Returns:
            Lista de proyectos con la prioridad especificada
        """
        try:
            query = self.query_builder.build_by_priority_query(priority)
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(projects)} proyectos con prioridad: {priority.value}")
            return list(projects)
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyectos por prioridad '{priority.value}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_priority",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyectos por prioridad '{priority.value}': {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado obteniendo proyectos por prioridad '{priority.value}': {e}",
                operation="get_by_priority",
                entity_type="Project",
                original_error=e
            )

    # ==========================================
    # CONSULTAS TEMPORALES
    # ==========================================

    async def get_by_date_range(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Project]:
        """
        Obtiene proyectos en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            Lista de proyectos en el rango especificado
            
        Raises:
            ProjectDateRangeError: Si ocurre un error al procesar el rango de fechas
        """
        try:
            query = self.query_builder.build_by_date_range_query(start_date, end_date)
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            self.logger.debug(f"Obtenidos {len(projects)} proyectos en rango de fechas")
            return list(projects)
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyectos por rango de fechas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_date_range",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyectos por rango de fechas: {e}")
            raise create_project_date_range_error(
                start_date=start_date,
                end_date=end_date,
                operation="get_by_date_range",
                reason=str(e)
            ) from e
    
    async def get_overdue_projects(self, reference_date: Optional[date] = None) -> List[Project]:
        """
        Obtiene proyectos atrasados.
        
        Args:
            reference_date: Fecha de referencia (por defecto fecha actual)
            
        Returns:
            Lista de proyectos atrasados
        """
        try:
            query = self.query_builder.build_overdue_projects_query(reference_date)
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(projects)} proyectos atrasados")
            return list(projects)
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyectos atrasados: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_overdue_projects",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyectos atrasados: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado obteniendo proyectos atrasados: {e}",
                operation="get_overdue_projects",
                entity_type="Project",
                original_error=e
            )

    async def get_projects_starting_current_week(self, **kwargs) -> List[Project]:
        """
        Obtiene proyectos que inician en la semana actual.
        
        Returns:
            Lista de proyectos que inician esta semana
        """
        try:
            query = self.query_builder.build_current_week_query('start_date', **kwargs)
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(projects)} proyectos que inician esta semana")
            return list(projects)
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyectos de la semana actual: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_projects_starting_current_week",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyectos de la semana actual: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado obteniendo proyectos de la semana actual: {e}",
                operation="get_projects_starting_current_week",
                entity_type="Project",
                original_error=e
            )
    
    async def get_projects_ending_current_week(self, **kwargs) -> List[Project]:
        """
        Obtiene proyectos que terminan en la semana actual.
        
        Returns:
            Lista de proyectos que terminan esta semana
        """
        try:
            query = self.query_builder.build_current_week_query('end_date', **kwargs)
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(projects)} proyectos que terminan esta semana")
            return list(projects)
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyectos que terminan esta semana: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_projects_ending_current_week",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyectos que terminan esta semana: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado obteniendo proyectos que terminan esta semana: {e}",
                operation="get_projects_ending_current_week",
                entity_type="Project",
                original_error=e
            )
    
    async def get_projects_starting_current_month(self, **kwargs) -> List[Project]:
        """
        Obtiene proyectos que inician en el mes actual.
        
        Returns:
            Lista de proyectos que inician este mes
        """
        try:
            query = self.query_builder.build_current_month_query('start_date', **kwargs)
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(projects)} proyectos que inician este mes")
            return list(projects)
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyectos del mes actual: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_projects_starting_current_month",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyectos del mes actual: {e}")
            raise ProjectRepositoryError(
                message=f"Error inesperado obteniendo proyectos del mes actual: {e}",
                operation="get_projects_starting_current_month",
                entity_type="Project",
                original_error=e
            )
    
    async def get_projects_starting_business_days_only(
        self, 
        start_date: Union[date, str, None] = None,
        end_date: Union[date, str, None] = None,
        **kwargs
    ) -> List[Project]:
        """
        Obtiene proyectos que inician en días hábiles dentro de un rango.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            
        Returns:
            Lista de proyectos que inician en días hábiles
            
        Raises:
            ProjectDateRangeError: Si ocurre un error al procesar días hábiles
        """
        try:
            # Convertir fechas si son strings
            if isinstance(start_date, str):
                start_date = date.fromisoformat(start_date)
            if isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)
            
            query = self.query_builder.build_business_days_query(
                'start_date', start_date, end_date, **kwargs
            )
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            # Filtrar por días hábiles en memoria (más eficiente para rangos pequeños)
            from ...utils.date_utils import is_business_day
            business_day_projects = [
                p for p in projects if is_business_day(p.start_date)
            ]
            
            self.logger.debug(
                f"Obtenidos {len(business_day_projects)} proyectos que inician en días hábiles"
            )
            return business_day_projects
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyectos en días hábiles: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_projects_starting_business_days_only",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyectos en días hábiles: {e}")
            raise create_project_date_range_error(
                start_date=start_date or date.today(),
                end_date=end_date or date.today(),
                operation="get_projects_starting_business_days_only",
                reason=str(e)
            ) from e
    
    # ==========================================
    # CONSULTAS CON RELACIONES
    # ==========================================
    
    async def get_with_client(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto con su cliente cargado.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Proyecto con cliente o None si no existe
            
        Raises:
            ProjectRelationshipError: Si ocurre un error al cargar las relaciones
        """
        try:
            return await self.relationship_manager.get_with_client(project_id)
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyecto {project_id} con cliente: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_client",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyecto {project_id} con cliente: {e}")
            raise create_project_relationship_error(
                relationship_type="client",
                project_id=project_id,
                related_entity_type="Client",
                reason=str(e)
            ) from e
    
    async def get_with_assignments(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto con sus asignaciones cargadas.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Proyecto con asignaciones o None si no existe
            
        Raises:
            ProjectRelationshipError: Si ocurre un error al cargar las relaciones
        """
        try:
            return await self.relationship_manager.get_with_assignments(project_id)
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyecto {project_id} con asignaciones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_assignments",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyecto {project_id} con asignaciones: {e}")
            raise create_project_relationship_error(
                relationship_type="assignments",
                project_id=project_id,
                related_entity_type="Assignment",
                reason=str(e)
            ) from e
    
    async def get_with_full_details(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto con todas sus relaciones cargadas.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Proyecto con todas las relaciones o None si no existe
            
        Raises:
            ProjectRelationshipError: Si ocurre un error al cargar las relaciones
        """
        try:
            return await self.relationship_manager.get_with_full_details(project_id)
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo proyecto {project_id} con detalles completos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_full_details",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo proyecto {project_id} con detalles completos: {e}")
            raise create_project_relationship_error(
                relationship_type="full_details",
                project_id=project_id,
                related_entity_type="All",
                reason=str(e)
            ) from e
    
    # ==========================================
    # VALIDACIONES
    # ==========================================
    
    async def reference_exists(self, reference: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un proyecto con la referencia especificada.
        
        Args:
            reference: Referencia a verificar
            exclude_id: ID de proyecto a excluir de la verificación
            
        Returns:
            True si la referencia existe, False en caso contrario
        """
        try:
            query = self.query_builder.build_reference_exists_query(reference, exclude_id)
            result = await self.session.execute(query)
            count = result.scalar()
            
            exists = count > 0
            self._logger.debug(f"Referencia '{reference}' existe: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos verificando existencia de referencia '{reference}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="reference_exists",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado verificando existencia de referencia '{reference}': {e}")
            raise create_project_reference_error(
                reference=reference,
                operation="reference_exists",
                reason=str(e)
            ) from e
    
    async def trigram_exists(self, trigram: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un proyecto con el trigrama especificado.
        
        Args:
            trigram: Trigrama a verificar
            exclude_id: ID de proyecto a excluir de la verificación
            
        Returns:
            True si el trigrama existe, False en caso contrario
        """
        try:
            query = self.query_builder.build_trigram_exists_query(trigram, exclude_id)
            result = await self.session.execute(query)
            count = result.scalar()
            
            exists = count > 0
            self._logger.debug(f"Trigrama '{trigram}' existe: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos verificando existencia de trigrama '{trigram}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="trigram_exists",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado verificando existencia de trigrama '{trigram}': {e}")
            raise create_project_trigram_error(
                trigram=trigram,
                operation="trigram_exists",
                reason=str(e)
            ) from e
    
    # ==========================================
    # ESTADÍSTICAS
    # ==========================================
    
    async def get_project_performance_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de rendimiento para un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con estadísticas del proyecto
            
        Raises:
            ProjectStatisticsError: Si ocurre un error al calcular las estadísticas
            ProjectNotFoundError: Si el proyecto no existe
        """
        try:
            return await self.statistics.get_project_performance_stats(project_id)
        except ProjectNotFoundError:
            # Re-lanzar errores de proyecto no encontrado directamente
            raise
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo estadísticas de rendimiento del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_performance_stats",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo estadísticas de rendimiento del proyecto {project_id}: {e}")
            raise create_project_statistics_error(
                statistic_type="performance",
                parameters={"project_id": project_id, "operation": "get_project_performance_stats"},
                reason=f"get_project_performance_stats failed: {str(e)}"
            ) from e
    
    async def get_projects_by_status_summary(self) -> Dict[str, int]:
        """
        Obtiene un resumen de proyectos agrupados por estado.
        
        Returns:
            Diccionario con conteo de proyectos por estado
            
        Raises:
            ProjectStatisticsError: Si ocurre un error al calcular las estadísticas
        """
        try:
            summary_stats = await self.statistics.get_project_summary_stats()
            return summary_stats.get('by_status', {})
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo resumen por estado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_projects_by_status_summary",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo resumen por estado: {e}")
            raise create_project_statistics_error(
                statistic_type="summary",
                parameters={"operation": "get_projects_by_status_summary"},
                reason=f"get_projects_by_status_summary failed: {str(e)}"
            ) from e
    
    async def get_project_workload_stats(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de carga de trabajo para un proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
            
        Returns:
            Diccionario con estadísticas de carga de trabajo
            
        Raises:
            ProjectWorkloadError: Si ocurre un error al calcular la carga de trabajo
        """
        try:
            return await self.statistics.get_project_workload_stats(
                project_id, start_date, end_date
            )
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo estadísticas de carga de trabajo del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_workload_stats",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo estadísticas de carga de trabajo del proyecto {project_id}: {e}")
            raise create_project_workload_error(
                workload_data={"start_date": start_date, "end_date": end_date},
                operation="get_project_workload_stats",
                reason=str(e),
                project_id=project_id
            ) from e
  
    async def get_project_duration_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de duración de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con estadísticas de duración
        """
        return await self.statistics.get_project_timeline_stats(project_id)
    
    async def get_monthly_project_stats(self, year: int, month: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos para un mes específico.
        
        Args:
            year: Año
            month: Mes
            
        Returns:
            Diccionario con estadísticas mensuales
            
        Raises:
            ProjectStatisticsError: Si ocurre un error al calcular las estadísticas
        """
        try:
            return await self.statistics.get_monthly_project_stats(year, month)
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo estadísticas mensuales para {year}-{month}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_monthly_project_stats",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo estadísticas mensuales para {year}-{month}: {e}")
            raise create_project_statistics_error(
                statistic_type="monthly",
                parameters={"year": year, "month": month},
                reason=f"get_monthly_project_stats: {str(e)}"
            ) from e
    
    async def get_client_project_stats(self, client_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos para un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con estadísticas del cliente
            
        Raises:
            ProjectStatisticsError: Si ocurre un error al calcular las estadísticas
        """
        try:
            return await self.statistics.get_client_project_stats(client_id)
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo estadísticas del cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_project_stats",
                entity_type="Project",
                entity_id=client_id
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo estadísticas del cliente {client_id}: {e}")
            raise create_project_statistics_error(
                statistic_type="client",
                parameters={"client_id": client_id},
                reason=f"get_client_project_stats: {str(e)}"
            ) from e
    
    async def get_overdue_projects_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos atrasados.
        
        Returns:
            Diccionario con estadísticas de proyectos atrasados
            
        Raises:
            ProjectStatisticsError: Si ocurre un error al calcular las estadísticas
        """
        try:
            return await self.statistics.get_overdue_projects_stats()
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo estadísticas de proyectos atrasados: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_overdue_projects_stats",
                entity_type="Project"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo estadísticas de proyectos atrasados: {e}")
            raise create_project_statistics_error(
                statistic_type="overdue",
                parameters={},
                reason=f"get_overdue_projects_stats: {str(e)}"
            ) from e
