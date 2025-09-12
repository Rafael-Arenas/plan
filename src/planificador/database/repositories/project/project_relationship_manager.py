# src/planificador/database/repositories/project/project_relationship_manager.py

from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from ....models.project import Project
from ....models.client import Client
from ....models.project_assignment import ProjectAssignment
from ....models.employee import Employee
from ....models.workload import Workload
from ....exceptions.domain import ProjectNotFoundError
from ....exceptions.repository import (
    RepositoryError,
    convert_sqlalchemy_error,
)
from .project_query_builder import ProjectQueryBuilder


class ProjectRelationshipManager:
    """
    Gestor de relaciones para proyectos.
    
    Maneja la carga y gestión de relaciones entre proyectos y otras entidades,
    optimizando las consultas y evitando el problema N+1.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.query_builder = ProjectQueryBuilder(session)
        self._logger = logging.getLogger(__name__)
    
    # ==========================================
    # CONSULTAS INDIVIDUALES CON RELACIONES
    # ==========================================
    
    async def get_with_client(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto con su cliente cargado.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Proyecto con cliente o None si no existe
        """
        try:
            query = self.query_builder.build_with_client_query(project_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener el proyecto {project_id} con cliente: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_client",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener el proyecto {project_id} con cliente: {e}")
            raise RepositoryError(
                message=f"Error inesperado al obtener el proyecto {project_id} con cliente",
                operation="get_with_client",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    async def get_with_assignments(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto con sus asignaciones cargadas.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Proyecto con asignaciones o None si no existe
        """
        try:
            query = self.query_builder.build_with_assignments_query(project_id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener el proyecto {project_id} con asignaciones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_assignments",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener el proyecto {project_id} con asignaciones: {e}")
            raise RepositoryError(
                message=f"Error inesperado al obtener el proyecto {project_id} con asignaciones",
                operation="get_with_assignments",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    async def get_with_full_details(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto con todas sus relaciones cargadas.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Proyecto con todas las relaciones o None si no existe
        """
        try:
            query = select(Project).options(
                selectinload(Project.client),
                selectinload(Project.assignments).selectinload(ProjectAssignment.employee),
                selectinload(Project.workloads).selectinload(Workload.employee)
            ).where(Project.id == project_id)
            
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener los detalles completos del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_full_details",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener los detalles completos del proyecto {project_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al obtener los detalles completos del proyecto {project_id}",
                operation="get_with_full_details",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    # ==========================================
    # CONSULTAS MÚLTIPLES CON RELACIONES
    # ==========================================
    
    async def get_projects_with_clients(self, project_ids: List[int]) -> List[Project]:
        """
        Obtiene múltiples proyectos con sus clientes cargados.
        
        Args:
            project_ids: Lista de IDs de proyectos
            
        Returns:
            Lista de proyectos con clientes
        """
        if not project_ids:
            return []
        
        try:
            query = select(Project).options(
                selectinload(Project.client)
            ).where(Project.id.in_(project_ids))
            
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener proyectos con clientes: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_projects_with_clients",
                entity_type="Project"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener proyectos con clientes: {e}")
            raise RepositoryError(
                message="Error inesperado al obtener proyectos con clientes",
                operation="get_projects_with_clients",
                entity_type="Project",
                original_error=e
            )
    
    async def get_projects_with_assignments(self, project_ids: List[int]) -> List[Project]:
        """
        Obtiene múltiples proyectos con sus asignaciones cargadas.
        
        Args:
            project_ids: Lista de IDs de proyectos
            
        Returns:
            Lista de proyectos con asignaciones
        """
        if not project_ids:
            return []
        
        try:
            query = select(Project).options(
                selectinload(Project.assignments).selectinload(ProjectAssignment.employee)
            ).where(Project.id.in_(project_ids))
            
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener proyectos con asignaciones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_projects_with_assignments",
                entity_type="Project"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener proyectos con asignaciones: {e}")
            raise RepositoryError(
                message="Error inesperado al obtener proyectos con asignaciones",
                operation="get_projects_with_assignments",
                entity_type="Project",
                original_error=e
            )
    
    async def get_client_projects_with_details(self, client_id: int) -> List[Project]:
        """
        Obtiene todos los proyectos de un cliente con detalles completos.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Lista de proyectos del cliente con detalles
        """
        try:
            query = select(Project).options(
                selectinload(Project.client),
                selectinload(Project.assignments).selectinload(ProjectAssignment.employee)
            ).where(Project.client_id == client_id).order_by(
                Project.start_date.desc(), Project.name
            )
            
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener los proyectos del cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_projects_with_details",
                entity_type="Project",
                filters={"client_id": client_id}
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener los proyectos del cliente {client_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al obtener los proyectos del cliente {client_id}",
                operation="get_client_projects_with_details",
                entity_type="Project",
                filters={"client_id": client_id},
                original_error=e
            )
    
    # ==========================================
    # CONSULTAS POR EMPLEADO Y EQUIPO
    # ==========================================
    
    async def get_employee_projects(self, employee_id: int) -> List[Project]:
        """
        Obtiene todos los proyectos asignados a un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de proyectos del empleado
        """
        try:
            query = select(Project).join(
                ProjectAssignment, Project.id == ProjectAssignment.project_id
            ).options(
                selectinload(Project.client)
            ).where(
                and_(
                    ProjectAssignment.employee_id == employee_id,
                    ProjectAssignment.is_active == True
                )
            ).order_by(Project.start_date.desc())
            
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener los proyectos del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_projects",
                entity_type="Project",
                filters={"employee_id": employee_id}
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener los proyectos del empleado {employee_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al obtener los proyectos del empleado {employee_id}",
                operation="get_employee_projects",
                entity_type="Project",
                filters={"employee_id": employee_id},
                original_error=e
            )
    
    async def get_project_team_members(self, project_id: int) -> List[Employee]:
        """
        Obtiene todos los miembros del equipo de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de empleados asignados al proyecto
        """
        try:
            query = select(Employee).join(
                ProjectAssignment, Employee.id == ProjectAssignment.employee_id
            ).where(
                and_(
                    ProjectAssignment.project_id == project_id,
                    ProjectAssignment.is_active == True
                )
            ).order_by(Employee.first_name, Employee.last_name)
            
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener los miembros del equipo del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_team_members",
                entity_type="Employee",
                filters={"project_id": project_id}
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener los miembros del equipo del proyecto {project_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al obtener los miembros del equipo del proyecto {project_id}",
                operation="get_project_team_members",
                entity_type="Employee",
                filters={"project_id": project_id},
                original_error=e
            )

    async def get_project_workload_summary(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene un resumen de la carga de trabajo del proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con resumen de carga de trabajo
        """
        from sqlalchemy import func
        
        try:
            # Consulta para obtener estadísticas de workload
            workload_query = select(
                func.count(Workload.id).label('total_records'),
                func.sum(Workload.planned_hours).label('total_planned_hours'),
                func.sum(Workload.actual_hours).label('total_actual_hours'),
                func.avg(Workload.planned_hours).label('avg_planned_hours'),
                func.avg(Workload.actual_hours).label('avg_actual_hours')
            ).where(Workload.project_id == project_id)
            
            result = await self.session.execute(workload_query)
            workload_stats = result.first()
            
            # Consulta para obtener estadísticas de asignaciones
            assignment_query = select(
                func.count(ProjectAssignment.id).label('total_assignments'),
                func.count(
                    ProjectAssignment.id.filter(ProjectAssignment.is_active == True)
                ).label('active_assignments'),
                func.sum(ProjectAssignment.allocated_hours_per_day).label('total_allocated_hours')
            ).where(ProjectAssignment.project_id == project_id)
            
            result = await self.session.execute(assignment_query)
            assignment_stats = result.first()
            
            return {
                'workload': {
                    'total_records': workload_stats.total_records or 0,
                    'total_planned_hours': float(workload_stats.total_planned_hours or 0),
                    'total_actual_hours': float(workload_stats.total_actual_hours or 0),
                    'avg_planned_hours': float(workload_stats.avg_planned_hours or 0),
                    'avg_actual_hours': float(workload_stats.avg_actual_hours or 0)
                },
                'assignments': {
                    'total_assignments': assignment_stats.total_assignments or 0,
                    'active_assignments': assignment_stats.active_assignments or 0,
                    'total_allocated_hours': float(assignment_stats.total_allocated_hours or 0)
                }
            }
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener el resumen de carga de trabajo del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_workload_summary",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener el resumen de carga de trabajo del proyecto {project_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al obtener el resumen de carga de trabajo del proyecto {project_id}",
                operation="get_project_workload_summary",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    # ==========================================
    # CONSULTAS DE ASIGNACIONES
    # ==========================================
    
    async def get_project_assignments_details(self, project_id: int) -> List[ProjectAssignment]:
        """
        Obtiene las asignaciones de un proyecto con detalles del empleado.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de asignaciones con detalles del empleado
        """
        try:
            query = select(ProjectAssignment).options(
                selectinload(ProjectAssignment.employee),
                selectinload(ProjectAssignment.project)
            ).where(ProjectAssignment.project_id == project_id).order_by(
                ProjectAssignment.start_date.desc()
            )
            
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener los detalles de asignaciones del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_assignments_details",
                entity_type="ProjectAssignment",
                filters={"project_id": project_id}
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener los detalles de asignaciones del proyecto {project_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al obtener los detalles de asignaciones del proyecto {project_id}",
                operation="get_project_assignments_details",
                entity_type="ProjectAssignment",
                filters={"project_id": project_id},
                original_error=e
            )
    
    async def get_active_project_assignments(self, project_id: int) -> List[ProjectAssignment]:
        """
        Obtiene las asignaciones activas de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de asignaciones activas
        """
        try:
            query = select(ProjectAssignment).options(
                selectinload(ProjectAssignment.employee)
            ).where(
                and_(
                    ProjectAssignment.project_id == project_id,
                    ProjectAssignment.is_active == True
                )
            ).order_by(ProjectAssignment.start_date.desc())
            
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al obtener las asignaciones activas del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_active_project_assignments",
                entity_type="ProjectAssignment",
                filters={"project_id": project_id, "is_active": True}
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener las asignaciones activas del proyecto {project_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al obtener las asignaciones activas del proyecto {project_id}",
                operation="get_active_project_assignments",
                entity_type="ProjectAssignment",
                filters={"project_id": project_id, "is_active": True},
                original_error=e
            )
    

    # ==========================================
    # GESTIÓN DE RELACIONES
    # ==========================================
    
    async def load_project_relationships(self, project: Project, relationships: List[str]) -> Project:
        """
        Carga relaciones específicas para un proyecto existente.
        
        Args:
            project: Proyecto base
            relationships: Lista de relaciones a cargar ('client', 'assignments', 'workloads')
            
        Returns:
            Proyecto con relaciones cargadas
        """
        try:
            if not relationships:
                return project
            
            # Construir opciones de carga basadas en las relaciones solicitadas
            load_options = []
            
            if 'client' in relationships:
                load_options.append(selectinload(Project.client))
            
            if 'assignments' in relationships:
                load_options.append(
                    selectinload(Project.assignments).selectinload(ProjectAssignment.employee)
                )
            
            if 'workloads' in relationships:
                load_options.append(
                    selectinload(Project.workloads).selectinload(Workload.employee)
                )
            
            if not load_options:
                return project
            
            # Recargar el proyecto con las relaciones especificadas
            query = select(Project).options(*load_options).where(Project.id == project.id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none() or project
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al cargar relaciones para el proyecto {project.id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="load_project_relationships",
                entity_type="Project",
                entity_id=project.id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al cargar relaciones para el proyecto {project.id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al cargar relaciones para el proyecto {project.id}",
                operation="load_project_relationships",
                entity_type="Project",
                entity_id=project.id,
                original_error=e
            )
    
    async def preload_projects_relationships(
        self,
        projects: List[Project],
        relationships: List[str]
    ) -> List[Project]:
        """
        Precarga relaciones para una lista de proyectos.
        
        Args:
            projects: Lista de proyectos
            relationships: Lista de relaciones a cargar
            
        Returns:
            Lista de proyectos con relaciones cargadas
        """
        try:
            if not projects or not relationships:
                return projects
            
            project_ids = [p.id for p in projects]
            
            # Construir opciones de carga
            load_options = []
            
            if 'client' in relationships:
                load_options.append(selectinload(Project.client))
            
            if 'assignments' in relationships:
                load_options.append(
                    selectinload(Project.assignments).selectinload(ProjectAssignment.employee)
                )
            
            if 'workloads' in relationships:
                load_options.append(
                    selectinload(Project.workloads).selectinload(Workload.employee)
                )
            
            if not load_options:
                return projects
            
            # Cargar proyectos con relaciones
            query = select(Project).options(*load_options).where(
                Project.id.in_(project_ids)
            )
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al precargar relaciones de proyectos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="preload_projects_relationships",
                entity_type="Project"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al precargar relaciones de proyectos: {e}")
            raise RepositoryError(
                message="Error inesperado al precargar relaciones de proyectos",
                operation="preload_projects_relationships",
                entity_type="Project",
                original_error=e
            )