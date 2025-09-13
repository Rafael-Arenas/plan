from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from loguru import logger

from ..interfaces.relationship_interface import IEmployeeRelationshipOperations
from planificador.models.employee import Employee
from planificador.models.team import Team
from planificador.models.project import Project
from planificador.models.vacation import Vacation
from planificador.models.team_membership import TeamMembership
from planificador.models.project_assignment import ProjectAssignment
from planificador.exceptions.repository import (
    convert_sqlalchemy_error,
    EmployeeRepositoryError,
    create_employee_validation_repository_error
)
from planificador.exceptions.validation import ValidationError


class RelationshipOperations(IEmployeeRelationshipOperations):
    """
    Implementación de operaciones de relaciones para empleados.
    
    Esta clase maneja todas las operaciones relacionadas con las relaciones
    de empleados con equipos, proyectos, vacaciones y otros elementos relacionados.
    
    Attributes:
        session: Sesión de base de datos SQLAlchemy
        logger: Logger para registro de operaciones
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa las operaciones de relaciones.
        
        Args:
            session: Sesión de base de datos SQLAlchemy
        """
        self.session = session
        self.logger = logger.bind(component="EmployeeRelationshipOperations")
    
    async def get_employee_teams(self, employee_id: int) -> List[Team]:
        """
        Obtiene todos los equipos a los que pertenece un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de equipos del empleado
        """
        try:
            stmt = (
                select(Team)
                .join(TeamMembership)
                .where(TeamMembership.employee_id == employee_id)
            )
            result = await self.session.execute(stmt)
            teams = result.scalars().all()
            
            self.logger.info(f"Obtenidos {len(teams)} equipos para empleado {employee_id}")
            return list(teams)
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_teams",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado obteniendo equipos del empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado obteniendo equipos del empleado: {e}",
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
            stmt = (
                select(Project)
                .join(ProjectAssignment)
                .where(ProjectAssignment.employee_id == employee_id)
            )
            result = await self.session.execute(stmt)
            projects = result.scalars().all()
            
            self.logger.info(f"Obtenidos {len(projects)} proyectos para empleado {employee_id}")
            return list(projects)
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_projects",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado obteniendo proyectos del empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado obteniendo proyectos del empleado: {e}",
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
            stmt = select(Vacation).where(Vacation.employee_id == employee_id)
            result = await self.session.execute(stmt)
            vacations = result.scalars().all()
            
            self.logger.info(f"Obtenidas {len(vacations)} vacaciones para empleado {employee_id}")
            return list(vacations)
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_vacations",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado obteniendo vacaciones del empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado obteniendo vacaciones del empleado: {e}",
                operation="get_employee_vacations",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_team_memberships(self, employee_id: int) -> List[TeamMembership]:
        """
        Obtiene todas las membresías de equipo de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de membresías de equipo
        """
        try:
            stmt = select(TeamMembership).where(TeamMembership.employee_id == employee_id)
            result = await self.session.execute(stmt)
            memberships = result.scalars().all()
            
            self.logger.info(f"Obtenidas {len(memberships)} membresías para empleado {employee_id}")
            return list(memberships)
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_memberships",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado obteniendo membresías del empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado obteniendo membresías del empleado: {e}",
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
            stmt = select(ProjectAssignment).where(ProjectAssignment.employee_id == employee_id)
            result = await self.session.execute(stmt)
            assignments = result.scalars().all()
            
            self.logger.info(f"Obtenidas {len(assignments)} asignaciones para empleado {employee_id}")
            return list(assignments)
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_assignments",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado obteniendo asignaciones del empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado obteniendo asignaciones del empleado: {e}",
                operation="get_project_assignments",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    async def check_team_membership(self, employee_id: int, team_id: int) -> bool:
        """
        Verifica si un empleado pertenece a un equipo específico.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo
            
        Returns:
            True si pertenece al equipo, False en caso contrario
        """
        try:
            stmt = select(TeamMembership).where(
                TeamMembership.employee_id == employee_id,
                TeamMembership.team_id == team_id
            )
            result = await self.session.execute(stmt)
            membership = result.scalar_one_or_none()
            
            exists = membership is not None
            self.logger.debug(f"Empleado {employee_id} {'pertenece' if exists else 'no pertenece'} al equipo {team_id}")
            return exists
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="check_team_membership",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado verificando membresía del empleado {employee_id} en equipo {team_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado verificando membresía: {e}",
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
            True si está asignado al proyecto, False en caso contrario
        """
        try:
            stmt = select(ProjectAssignment).where(
                ProjectAssignment.employee_id == employee_id,
                ProjectAssignment.project_id == project_id
            )
            result = await self.session.execute(stmt)
            assignment = result.scalar_one_or_none()
            
            exists = assignment is not None
            self.logger.debug(f"Empleado {employee_id} {'está asignado' if exists else 'no está asignado'} al proyecto {project_id}")
            return exists
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="check_project_assignment",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado verificando asignación del empleado {employee_id} al proyecto {project_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado verificando asignación: {e}",
                operation="check_project_assignment",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_employees_by_team(self, team_id: int) -> List[Employee]:
        """
        Obtiene todos los empleados de un equipo específico.
        
        Args:
            team_id: ID del equipo
            
        Returns:
            Lista de empleados del equipo
        """
        try:
            stmt = (
                select(Employee)
                .join(TeamMembership)
                .where(TeamMembership.team_id == team_id)
            )
            result = await self.session.execute(stmt)
            employees = result.scalars().all()
            
            self.logger.info(f"Obtenidos {len(employees)} empleados para equipo {team_id}")
            return list(employees)
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_by_team",
                entity_type="Team",
                entity_id=team_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado obteniendo empleados del equipo {team_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado obteniendo empleados del equipo: {e}",
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
            stmt = (
                select(Employee)
                .join(ProjectAssignment)
                .where(ProjectAssignment.project_id == project_id)
            )
            result = await self.session.execute(stmt)
            employees = result.scalars().all()
            
            self.logger.info(f"Obtenidos {len(employees)} empleados para proyecto {project_id}")
            return list(employees)
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_by_project",
                entity_type="Project",
                entity_id=project_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado obteniendo empleados del proyecto {project_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado obteniendo empleados del proyecto: {e}",
                operation="get_employees_by_project",
                entity_type="Project",
                entity_id=project_id,
                original_error=e
            )
    
    async def validate_employee_exists(self, employee_id: int) -> Employee:
        """
        Valida que un empleado existe y lo retorna.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado encontrado
            
        Raises:
            ValidationError: Si el empleado no existe
        """
        try:
            stmt = select(Employee).where(Employee.id == employee_id)
            result = await self.session.execute(stmt)
            employee = result.scalar_one_or_none()
            
            if employee is None:
                raise ValidationError(
                    message=f"Empleado con ID {employee_id} no existe",
                    field="employee_id",
                    value=employee_id
                )
            
            self.logger.debug(f"Empleado {employee_id} validado exitosamente")
            return employee
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_employee_exists",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado validando empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado validando empleado: {e}",
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
            stmt = (
                select(Employee)
                .options(
                    selectinload(Employee.team_memberships),
                    selectinload(Employee.project_assignments),
                    selectinload(Employee.vacations)
                )
                .where(Employee.id == employee_id)
            )
            result = await self.session.execute(stmt)
            employee = result.scalar_one_or_none()
            
            if employee:
                self.logger.info(f"Empleado {employee_id} obtenido con todas las relaciones")
            else:
                self.logger.warning(f"Empleado {employee_id} no encontrado")
            
            return employee
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_with_all_relations",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado obteniendo empleado {employee_id} con relaciones: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado obteniendo empleado con relaciones: {e}",
                operation="get_employee_with_all_relations",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    async def count_employee_relationships(self, employee_id: int) -> Dict[str, int]:
        """
        Cuenta las relaciones de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Diccionario con conteos de relaciones
        """
        try:
            # Contar membresías de equipo
            team_stmt = select(TeamMembership).where(TeamMembership.employee_id == employee_id)
            team_result = await self.session.execute(team_stmt)
            team_count = len(team_result.scalars().all())
            
            # Contar asignaciones de proyecto
            project_stmt = select(ProjectAssignment).where(ProjectAssignment.employee_id == employee_id)
            project_result = await self.session.execute(project_stmt)
            project_count = len(project_result.scalars().all())
            
            # Contar vacaciones
            vacation_stmt = select(Vacation).where(Vacation.employee_id == employee_id)
            vacation_result = await self.session.execute(vacation_stmt)
            vacation_count = len(vacation_result.scalars().all())
            
            counts = {
                "teams": team_count,
                "projects": project_count,
                "vacations": vacation_count,
                "total": team_count + project_count + vacation_count
            }
            
            self.logger.info(f"Conteos de relaciones para empleado {employee_id}: {counts}")
            return counts
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_employee_relationships",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self.logger.error(f"Error inesperado contando relaciones del empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado contando relaciones del empleado: {e}",
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
            True si tiene dependencias, False en caso contrario
        """
        try:
            counts = await self.count_employee_relationships(employee_id)
            has_deps = counts["total"] > 0
            
            self.logger.debug(f"Empleado {employee_id} {'tiene' if has_deps else 'no tiene'} dependencias")
            return has_deps
            
        except Exception as e:
            self.logger.error(f"Error verificando dependencias del empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error verificando dependencias del empleado: {e}",
                operation="has_dependencies",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )