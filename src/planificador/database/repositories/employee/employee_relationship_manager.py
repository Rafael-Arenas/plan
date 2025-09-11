# src/planificador/database/repositories/employee/employee_relationship_manager.py

from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from ....models.employee import Employee
from ....models.team_membership import TeamMembership
from ....models.team import Team
from ....models.project_assignment import ProjectAssignment
from ....models.project import Project
from ....models.vacation import Vacation
# from ....models.time_entry import TimeEntry  # TODO: TimeEntry model not found
from ....exceptions import ValidationError
from ....exceptions.repository.base_repository_exceptions import (
    convert_sqlalchemy_error,
    RepositoryError
)

class EmployeeRelationshipManager:
    """
    Gestor de relaciones de empleados.
    Maneja las consultas relacionadas con equipos, proyectos, vacaciones y registros de tiempo.
    """
    
    def __init__(self, session: AsyncSession, query_builder=None):
        self.session = session
        self._logger = logger
        self.query_builder = query_builder
    
    # ============================================================================
    # CONSULTAS DE RELACIONES BÁSICAS
    # ============================================================================
    
    async def get_employee_teams(self, employee_id: int) -> List[Team]:
        """
        Obtiene todos los equipos a los que pertenece un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de equipos del empleado
        """
        try:
            query = (
                select(Team)
                .join(TeamMembership)
                .where(TeamMembership.employee_id == employee_id)
                .order_by(Team.name)
            )
            
            result = await self.session.execute(query)
            teams = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(teams)} equipos para empleado {employee_id}")
            return list(teams)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo equipos del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_teams",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo equipos del empleado {employee_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo equipos del empleado {employee_id}: {e}",
                operation="get_employee_teams",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_employee_projects(self, employee_id: int) -> List[Project]:
        """
        Obtiene todos los proyectos asignados a un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de proyectos del empleado
        """
        try:
            query = (
                select(Project)
                .join(ProjectAssignment)
                .where(ProjectAssignment.employee_id == employee_id)
                .order_by(Project.name)
            )
            
            result = await self.session.execute(query)
            projects = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(projects)} proyectos para empleado {employee_id}")
            return list(projects)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo proyectos del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_projects",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo proyectos del empleado {employee_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo proyectos del empleado {employee_id}: {e}",
                operation="get_employee_projects",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_employee_vacations(self, employee_id: int) -> List[Vacation]:
        """
        Obtiene todas las vacaciones de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de vacaciones del empleado
        """
        try:
            query = (
                select(Vacation)
                .where(Vacation.employee_id == employee_id)
                .order_by(Vacation.start_date.desc())
            )
            
            result = await self.session.execute(query)
            vacations = result.scalars().all()
            
            self._logger.debug(f"Obtenidas {len(vacations)} vacaciones para empleado {employee_id}")
            return list(vacations)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo vacaciones del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_vacations",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo vacaciones del empleado {employee_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo vacaciones del empleado {employee_id}: {e}",
                operation="get_employee_vacations",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    # ============================================================================
    # CONSULTAS DE MEMBRESÍAS Y ASIGNACIONES
    # ============================================================================
    
    async def get_team_memberships(self, employee_id: int) -> List[TeamMembership]:
        """
        Obtiene todas las membresías de equipo de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de membresías de equipo
        """
        try:
            query = (
                select(TeamMembership)
                .options(selectinload(TeamMembership.team))
                .where(TeamMembership.employee_id == employee_id)
                .order_by(TeamMembership.joined_date.desc())
            )
            
            result = await self.session.execute(query)
            memberships = result.scalars().all()
            
            self._logger.debug(f"Obtenidas {len(memberships)} membresías para empleado {employee_id}")
            return list(memberships)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo membresías del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_memberships",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo membresías del empleado {employee_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo membresías del empleado {employee_id}: {e}",
                operation="get_team_memberships",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )

    async def get_project_assignments(self, employee_id: int) -> List[ProjectAssignment]:
        """
        Obtiene todas las asignaciones de proyecto de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de asignaciones de proyecto
        """
        try:
            query = (
                select(ProjectAssignment)
                .options(selectinload(ProjectAssignment.project))
                .where(ProjectAssignment.employee_id == employee_id)
                .order_by(ProjectAssignment.assigned_date.desc())
            )
            
            result = await self.session.execute(query)
            assignments = result.scalars().all()
            
            self._logger.debug(f"Obtenidas {len(assignments)} asignaciones para empleado {employee_id}")
            return list(assignments)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo asignaciones del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_assignments",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo asignaciones del empleado {employee_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo asignaciones del empleado {employee_id}: {e}",
                operation="get_project_assignments",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    # ============================================================================
    # CONSULTAS CON CARGA DE RELACIONES
    # ============================================================================
    
    async def get_with_teams(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado con sus equipos cargados.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado con equipos cargados o None
        """
        return await self.query_builder.get_with_teams(employee_id)
    
    async def get_with_projects(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado con sus proyectos asignados cargados.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado con proyectos cargados o None
        """
        return await self.query_builder.get_with_projects(employee_id)
    
    # ============================================================================
    # VALIDACIONES DE MEMBRESÍA
    # ============================================================================
    
    async def check_team_membership(self, employee_id: int, team_id: int) -> bool:
        """
        Verifica si un empleado pertenece a un equipo específico.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo
            
        Returns:
            True si el empleado pertenece al equipo
        """
        try:
            query = select(TeamMembership).where(
                and_(
                    TeamMembership.employee_id == employee_id,
                    TeamMembership.team_id == team_id
                )
            )
            
            result = await self.session.execute(query)
            membership = result.scalar_one_or_none()
            
            is_member = membership is not None
            self._logger.debug(
                f"Empleado {employee_id} {'pertenece' if is_member else 'no pertenece'} al equipo {team_id}"
            )
            return is_member
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos verificando membresía de equipo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="check_team_membership",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado verificando membresía de equipo: {e}")
            raise RepositoryError(
                message=f"Error inesperado verificando membresía de equipo: {e}",
                operation="check_team_membership",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    async def check_project_assignment(self, employee_id: int, project_id: int) -> bool:
        """
        Verifica si un empleado está asignado a un proyecto específico.
        
        Args:
            employee_id: ID del empleado
            project_id: ID del proyecto
            
        Returns:
            True si el empleado está asignado al proyecto
        """
        try:
            query = select(ProjectAssignment).where(
                and_(
                    ProjectAssignment.employee_id == employee_id,
                    ProjectAssignment.project_id == project_id
                )
            )
            
            result = await self.session.execute(query)
            assignment = result.scalar_one_or_none()
            
            is_assigned = assignment is not None
            self._logger.debug(
                f"Empleado {employee_id} {'está asignado' if is_assigned else 'no está asignado'} al proyecto {project_id}"
            )
            return is_assigned
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos verificando asignación de proyecto: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="check_project_assignment",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado verificando asignación de proyecto: {e}")
            raise RepositoryError(
                message=f"Error inesperado verificando asignación de proyecto: {e}",
                operation="check_project_assignment",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    # ============================================================================
    # CONSULTAS INVERSAS
    # ============================================================================
    
    async def get_employees_by_team(self, team_id: int) -> List[Employee]:
        """
        Obtiene todos los empleados que pertenecen a un equipo específico.
        
        Args:
            team_id: ID del equipo
            
        Returns:
            Lista de empleados del equipo
        """
        try:
            query = (
                select(Employee)
                .join(TeamMembership)
                .where(TeamMembership.team_id == team_id)
                .order_by(Employee.full_name)
            )
            
            result = await self.session.execute(query)
            employees = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(employees)} empleados del equipo {team_id}")
            return list(employees)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo empleados del equipo {team_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_by_team",
                entity_type="Team",
                entity_id=team_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo empleados del equipo {team_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo empleados del equipo {team_id}: {e}",
                operation="get_employees_by_team",
                entity_type="Team",
                entity_id=team_id,
                original_error=e
            )
    
    async def get_employees_by_project(self, project_id: int) -> List[Employee]:
        """
        Obtiene todos los empleados asignados a un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de empleados del proyecto
        """
        try:
            query = (
                select(Employee)
                .join(ProjectAssignment)
                .where(ProjectAssignment.project_id == project_id)
                .order_by(Employee.full_name)
            )
            
            result = await self.session.execute(query)
            employees = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(employees)} empleados del proyecto {project_id}")
            return list(employees)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo empleados del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_by_project",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo empleados del proyecto {project_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo empleados del proyecto {project_id}: {e}",
                operation="get_employees_by_project",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    # ============================================================================
    # VALIDACIONES Y UTILIDADES
    # ============================================================================
    
    async def validate_employee_exists(self, employee_id: int) -> Employee:
        """
        Valida que un empleado existe y lo retorna.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            El empleado encontrado
            
        Raises:
            ValidationError: Si el empleado no existe
        """
        try:
            query = select(Employee).where(Employee.id == employee_id)
            result = await self.session.execute(query)
            employee = result.scalar_one_or_none()
            
            if not employee:
                raise ValidationError(f"Empleado con ID {employee_id} no encontrado")
            
            self._logger.debug(f"Empleado {employee_id} validado exitosamente")
            return employee
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos validando empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_employee_exists",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando empleado {employee_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado validando empleado {employee_id}: {e}",
                operation="validate_employee_exists",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_employee_with_all_relations(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado con todas sus relaciones cargadas.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado con todas las relaciones cargadas o None
        """
        try:
            query = (
                select(Employee)
                .options(
                    selectinload(Employee.team_memberships).selectinload(TeamMembership.team),
                    selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project),
                    selectinload(Employee.vacations),
                    selectinload(Employee.time_entries)
                )
                .where(Employee.id == employee_id)
            )
            
            result = await self.session.execute(query)
            employee = result.scalar_one_or_none()
            
            if employee:
                self._logger.debug(f"Empleado {employee_id} con todas las relaciones cargado")
            else:
                self._logger.debug(f"Empleado {employee_id} no encontrado")
            
            return employee
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo empleado con relaciones {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_with_all_relations",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo empleado con relaciones {employee_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo empleado con relaciones {employee_id}: {e}",
                operation="get_employee_with_all_relations",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    async def count_employee_relationships(self, employee_id: int) -> dict:
        """
        Cuenta las relaciones de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Diccionario con conteos de relaciones
        """
        try:
            # Contar equipos
            teams_query = select(TeamMembership).where(TeamMembership.employee_id == employee_id)
            teams_result = await self.session.execute(teams_query)
            teams_count = len(teams_result.scalars().all())
            
            # Contar proyectos
            projects_query = select(ProjectAssignment).where(ProjectAssignment.employee_id == employee_id)
            projects_result = await self.session.execute(projects_query)
            projects_count = len(projects_result.scalars().all())
            
            # Contar vacaciones
            vacations_query = select(Vacation).where(Vacation.employee_id == employee_id)
            vacations_result = await self.session.execute(vacations_query)
            vacations_count = len(vacations_result.scalars().all())
            
            # Contar registros de tiempo
            time_entries_query = select(TimeEntry).where(TimeEntry.employee_id == employee_id)
            time_entries_result = await self.session.execute(time_entries_query)
            time_entries_count = len(time_entries_result.scalars().all())
            
            counts = {
                'teams': teams_count,
                'projects': projects_count,
                'vacations': vacations_count,
                'time_entries': time_entries_count
            }
            
            self._logger.debug(f"Conteos de relaciones para empleado {employee_id}: {counts}")
            return counts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos contando relaciones del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_employee_relationships",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado contando relaciones del empleado {employee_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado contando relaciones del empleado {employee_id}: {e}",
                operation="count_employee_relationships",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    async def has_dependencies(self, employee_id: int) -> bool:
        """
        Verifica si un empleado tiene dependencias que impidan su eliminación.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            True si tiene dependencias
        """
        try:
            counts = await self.count_employee_relationships(employee_id)
            
            # Un empleado tiene dependencias si tiene cualquier relación
            has_deps = any(count > 0 for count in counts.values())
            
            self._logger.debug(
                f"Empleado {employee_id} {'tiene' if has_deps else 'no tiene'} dependencias"
            )
            return has_deps
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos verificando dependencias del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="has_dependencies",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado verificando dependencias del empleado {employee_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado verificando dependencias del empleado {employee_id}: {e}",
                operation="has_dependencies",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )