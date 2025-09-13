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
from planificador.repositories.base_repository import BaseRepository
from planificador.models import (
    Employee, Project, ProjectAssignment, Team, TeamMembership, Vacation
)
from planificador.exceptions.repository import (
    EmployeeRepositoryError,
    RepositoryValidationError,
)
from planificador.exceptions import NotFoundError
from planificador.exceptions import (
    convert_sqlalchemy_error,
)
from planificador.repositories.employee.interfaces.relationship_interface import (
    IEmployeeRelationshipOperations,
)
from planificador.exceptions.validation import ValidationError


class RelationshipOperations(BaseRepository[Employee], IEmployeeRelationshipOperations):
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
        
        super().__init__(session, Employee)
        self._logger = logger.bind(component="RelationshipOperations")Inicializa las operaciones de relaciones.
        
        Args:
            session: Sesión de base de datos SQLAlchemy
        """
        super().__init__(session, Employee)
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
            employee = await self.find_by_criteria(
                criteria={"id": employee_id},
                options=[selectinload(self.model_class.teams)]
            )
            if not employee:
                raise NotFoundError(
                    message=f"Empleado con id {employee_id} no fue encontrado",
                    operation="get_employee_teams",
                    entity_type=self.model_class.__name__,
                    entity_id=employee_id
                )
            return employee.teams
        except SQLAlchemyError as e:
            self.logger.error(f"Error al obtener equipos del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e, 
                operation="get_employee_teams", 
                entity_type=self.model_class.__name__, 
                context={"employee_id": employee_id}
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
            employee = await self.find_by_criteria(
                criteria={"id": employee_id},
                options=[selectinload(self.model_class.projects)]
            )
            if not employee:
                raise NotFoundError(
                    message=f"Empleado con id {employee_id} no fue encontrado",
                    operation="get_employee_projects",
                    entity_type=self.model_class.__name__,
                    entity_id=employee_id
                )
            return employee.projects
        except SQLAlchemyError as e:
            self.logger.error(f"Error al obtener proyectos del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_projects",
                entity_type=self.model_class.__name__,
                context={"employee_id": employee_id}
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
            employee = await self.find_by_criteria(
                criteria={"id": employee_id},
                options=[selectinload(self.model_class.vacations)]
            )
            if not employee:
                raise NotFoundError(
                    message=f"Empleado con id {employee_id} no fue encontrado",
                    operation="get_employee_vacations",
                    entity_type=self.model_class.__name__,
                    entity_id=employee_id
                )
            return employee.vacations
        except SQLAlchemyError as e:
            self.logger.error(f"Error al obtener vacaciones del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_vacations",
                entity_type=self.model_class.__name__,
                context={"employee_id": employee_id}
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
            employee = await self.find_by_criteria(
                criteria={"id": employee_id},
                options=[selectinload(self.model_class.team_memberships)]
            )
            if not employee:
                raise NotFoundError(
                    message=f"Empleado con id {employee_id} no fue encontrado",
                    operation="get_team_memberships",
                    entity_type=self.model_class.__name__,
                    entity_id=employee_id
                )
            return employee.team_memberships
        except SQLAlchemyError as e:
            self.logger.error(f"Error al obtener membresías de equipo del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_memberships",
                entity_type=self.model_class.__name__,
                context={"employee_id": employee_id}
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
            employee = await self.find_by_criteria(
                criteria={"id": employee_id},
                options=[selectinload(self.model_class.project_assignments)]
            )
            if not employee:
                raise NotFoundError(
                    message=f"Empleado con id {employee_id} no fue encontrado",
                    operation="get_project_assignments",
                    entity_type=self.model_class.__name__,
                    entity_id=employee_id
                )
            return employee.project_assignments
        except SQLAlchemyError as e:
            self.logger.error(f"Error al obtener asignaciones de proyecto del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_assignments",
                entity_type=self.model_class.__name__,
                context={"employee_id": employee_id}
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
            membership = result.scalars().first()
            is_member = membership is not None
            self.logger.info(f"Verificación de membresía: Empleado {employee_id} en equipo {team_id} -> {is_member}")
            return is_member
        except SQLAlchemyError as e:
            self.logger.error(f"Error al verificar la membresía del empleado {employee_id} en el equipo {team_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e, 
                operation="check_team_membership", 
                entity_type=self.model_class.__name__, 
                context={"employee_id": employee_id, "team_id": team_id}
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
            assignment = result.scalars().first()
            is_assigned = assignment is not None
            self.logger.info(f"Verificación de asignación: Empleado {employee_id} en proyecto {project_id} -> {is_assigned}")
            return is_assigned
        except SQLAlchemyError as e:
            self.logger.error(f"Error al verificar la asignación del empleado {employee_id} al proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="check_project_assignment",
                entity_type=self.model_class.__name__,
                context={"employee_id": employee_id, "project_id": project_id}
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
            return await self.find_all_by_criteria(
                criteria={"teams.id": team_id},
                options=[joinedload(self.model_class.teams)]
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error al obtener empleados del equipo {team_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_by_team",
                entity_type=self.model_class.__name__,
                context={"team_id": team_id}
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
            return await self.find_all_by_criteria(
                criteria={"projects.id": project_id},
                options=[joinedload(self.model_class.projects)]
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error al obtener empleados del proyecto {project_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_by_project",
                entity_type=self.model_class.__name__,
                context={"project_id": project_id}
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
            employee = await self.find_by_id(employee_id)
            if not employee:
                raise NotFoundError(
                    message=f"Empleado con id {employee_id} no fue encontrado",
                    operation="validate_employee_exists",
                    entity_type=self.model_class.__name__,
                    entity_id=employee_id
                )
            return employee
        except SQLAlchemyError as e:
            self.logger.error(f"Error al validar la existencia del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e, 
                operation="validate_employee_exists", 
                entity_type=self.model_class.__name__, 
                context={"employee_id": employee_id}
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
            return await self.find_by_criteria(
                criteria={"id": employee_id},
                options=[
                    selectinload(self.model_class.teams),
                    selectinload(self.model_class.projects),
                    selectinload(self.model_class.vacations),
                    selectinload(self.model_class.team_memberships),
                    selectinload(self.model_class.project_assignments),
                ]
            )
        except SQLAlchemyError as e:
            self.logger.error(f"Error al obtener el empleado con todas las relaciones para el id {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e, 
                operation="get_employee_with_all_relations", 
                entity_type=self.model_class.__name__, 
                context={"employee_id": employee_id}
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
            employee = await self.find_one_by_criteria(
                criteria={"id": employee_id},
                options=[
                    selectinload(self.model_class.teams),
                    selectinload(self.model_class.projects),
                    selectinload(self.model_class.vacations),
                ]
            )

            if not employee:
                counts = {"teams": 0, "projects": 0, "vacations": 0, "total": 0}
                self.logger.info(f"No se encontró empleado {employee_id}, no hay relaciones que contar.")
                return counts

            team_count = len(employee.teams)
            project_count = len(employee.projects)
            vacation_count = len(employee.vacations)

            counts = {
                "teams": team_count,
                "projects": project_count,
                "vacations": vacation_count,
                "total": team_count + project_count + vacation_count
            }
            
            self.logger.info(f"Conteos de relaciones para empleado {employee_id}: {counts}")
            return counts
        except SQLAlchemyError as e:
            self.logger.error(f"Error al contar las relaciones del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e, 
                operation="count_employee_relationships", 
                entity_type=self.model_class.__name__, 
                context={"employee_id": employee_id}
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
            has_dependencies = counts["total"] > 0
            self.logger.info(f"El empleado {employee_id} {'tiene' if has_dependencies else 'no tiene'} dependencias.")
            return has_dependencies
        except SQLAlchemyError as e:
            self.logger.error(f"Error al verificar las dependencias del empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e, 
                operation="has_dependencies", 
                entity_type=self.model_class.__name__, 
                context={"employee_id": employee_id}
            )

    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Employee]:
        """
        Obtiene un empleado por un campo único.

        Args:
            field_name: Nombre del campo único.
            value: Valor del campo único.

        Returns:
            El empleado si se encuentra, de lo contrario None.
        """
        try:
            return await self.find_by_criteria(criteria={field_name: value})
        except SQLAlchemyError as e:
            self.logger.error(
                f'Error al buscar empleado por campo único ' 
                f'{field_name}={value}: {e}'
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type=self.model_class.__name__,
                context={"field_name": field_name, "value": value},
            )
            raise convert_sqlalchemy_error(
                error=e, 
                operation="has_dependencies", 
                entity_type=self.model_class.__name__, 
                context={"employee_id": employee_id}
            )