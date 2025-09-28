"""Módulo de operaciones de relaciones para asignaciones de proyectos.

Este módulo implementa la interfaz IRelationshipOperations y proporciona
funcionalidades para manejar las relaciones entre asignaciones, empleados y proyectos.

Versión: 1.0.0
"""

from typing import Any
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func

from planificador.models.project_assignment import ProjectAssignment
from planificador.models.employee import Employee
from planificador.models.project import Project
from planificador.repositories.base_repository import BaseRepository
from ..interfaces.relationship_interface import IRelationshipOperations


class RelationshipOperations(BaseRepository[ProjectAssignment], IRelationshipOperations):
    """Implementación de operaciones de relaciones para asignaciones de proyectos.

    Hereda de BaseRepository y se especializa en operaciones que involucran
    relaciones entre asignaciones, empleados y proyectos.
    """

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones de relaciones.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
        """
        super().__init__(session, ProjectAssignment)
        self._logger = self._logger.bind(component="ProjectAssignmentRelationshipOperations")
        self._logger.debug("RelationshipOperations para ProjectAssignment inicializado")

    async def get_assignments_with_employee(
        self, employee_id: int | None = None
    ) -> list[ProjectAssignment]:
        """Obtiene asignaciones con datos del empleado cargados.
        
        Args:
            employee_id: ID del empleado específico (opcional)
            
        Returns:
            Lista de asignaciones con datos del empleado
        """
        self._logger.debug(f"Obteniendo asignaciones con empleado (employee_id={employee_id})")
        
        query = select(ProjectAssignment).options(selectinload(ProjectAssignment.employee))
        
        if employee_id is not None:
            query = query.where(ProjectAssignment.employee_id == employee_id)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_assignments_with_project(
        self, project_id: int | None = None
    ) -> list[ProjectAssignment]:
        """Obtiene asignaciones con datos del proyecto cargados.
        
        Args:
            project_id: ID del proyecto específico (opcional)
            
        Returns:
            Lista de asignaciones con datos del proyecto
        """
        self._logger.debug(f"Obteniendo asignaciones con proyecto (project_id={project_id})")
        
        query = select(ProjectAssignment).options(selectinload(ProjectAssignment.project))
        
        if project_id is not None:
            query = query.where(ProjectAssignment.project_id == project_id)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_assignments_with_full_data(
        self, assignment_ids: list[int] | None = None
    ) -> list[ProjectAssignment]:
        """Obtiene asignaciones con todos los datos relacionados cargados.
        
        Args:
            assignment_ids: Lista de IDs de asignaciones específicas (opcional)
            
        Returns:
            Lista de asignaciones con datos completos
        """
        self._logger.debug(f"Obteniendo asignaciones con datos completos (ids={assignment_ids})")
        
        query = select(ProjectAssignment).options(
            selectinload(ProjectAssignment.employee),
            selectinload(ProjectAssignment.project)
        )
        
        if assignment_ids is not None:
            query = query.where(ProjectAssignment.id.in_(assignment_ids))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def transfer_employee_assignments(
        self, from_employee_id: int, to_employee_id: int, project_ids: list[int] | None = None
    ) -> int:
        """Transfiere asignaciones de un empleado a otro.
        
        Args:
            from_employee_id: ID del empleado origen
            to_employee_id: ID del empleado destino
            project_ids: Lista de IDs de proyectos específicos (opcional)
            
        Returns:
            Número de asignaciones transferidas
        """
        self._logger.debug(
            f"Transfiriendo asignaciones del empleado {from_employee_id} "
            f"al empleado {to_employee_id} (proyectos={project_ids})"
        )
        
        criteria = {"employee_id": from_employee_id}
        if project_ids is not None:
            criteria["project_id"] = {"operator": "in", "value": project_ids}
        
        assignments = await self.find_by_criteria(criteria)
        
        transferred_count = 0
        for assignment in assignments:
            await self.update(assignment.id, {"employee_id": to_employee_id})
            transferred_count += 1
        
        self._logger.info(f"Transferidas {transferred_count} asignaciones")
        return transferred_count

    async def reassign_project_assignments(
        self, from_project_id: int, to_project_id: int, employee_ids: list[int] | None = None
    ) -> int:
        """Reasigna asignaciones de un proyecto a otro.
        
        Args:
            from_project_id: ID del proyecto origen
            to_project_id: ID del proyecto destino
            employee_ids: Lista de IDs de empleados específicos (opcional)
            
        Returns:
            Número de asignaciones reasignadas
        """
        self._logger.debug(
            f"Reasignando asignaciones del proyecto {from_project_id} "
            f"al proyecto {to_project_id} (empleados={employee_ids})"
        )
        
        criteria = {"project_id": from_project_id}
        if employee_ids is not None:
            criteria["employee_id"] = {"operator": "in", "value": employee_ids}
        
        assignments = await self.find_by_criteria(criteria)
        
        reassigned_count = 0
        for assignment in assignments:
            await self.update(assignment.id, {"project_id": to_project_id})
            reassigned_count += 1
        
        self._logger.info(f"Reasignadas {reassigned_count} asignaciones")
        return reassigned_count

    async def get_employee_workload_summary(
        self, employee_id: int, start_date: date | None = None, end_date: date | None = None
    ) -> dict[str, Any]:
        """Obtiene un resumen de la carga de trabajo de un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
            
        Returns:
            Diccionario con resumen de carga de trabajo
        """
        self._logger.debug(
            f"Obteniendo resumen de carga de trabajo para empleado {employee_id} "
            f"(período: {start_date} - {end_date})"
        )
        
        criteria = {"employee_id": employee_id}
        if start_date is not None:
            criteria["start_date"] = {"operator": ">=", "value": start_date}
        if end_date is not None:
            criteria["end_date"] = {"operator": "<=", "value": end_date}
        
        assignments = await self.find_by_criteria(criteria)
        
        total_assignments = len(assignments)
        active_assignments = len([a for a in assignments if a.is_active])
        total_allocation = sum(a.allocation_percentage for a in assignments)
        
        projects = list(set(a.project_id for a in assignments))
        roles = list(set(a.role for a in assignments if a.role))
        
        return {
            "employee_id": employee_id,
            "total_assignments": total_assignments,
            "active_assignments": active_assignments,
            "total_allocation_percentage": total_allocation,
            "unique_projects": len(projects),
            "unique_roles": len(roles),
            "project_ids": projects,
            "roles": roles,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            }
        }

    async def get_project_team_summary(
        self, project_id: int, include_inactive: bool = False
    ) -> dict[str, Any]:
        """Obtiene un resumen del equipo de un proyecto.
        
        Args:
            project_id: ID del proyecto
            include_inactive: Si incluir asignaciones inactivas
            
        Returns:
            Diccionario con resumen del equipo
        """
        self._logger.debug(
            f"Obteniendo resumen del equipo para proyecto {project_id} "
            f"(incluir inactivos: {include_inactive})"
        )
        
        criteria = {"project_id": project_id}
        if not include_inactive:
            criteria["is_active"] = True
        
        assignments = await self.get_assignments_with_employee()
        assignments = [a for a in assignments if a.project_id == project_id]
        
        if not include_inactive:
            assignments = [a for a in assignments if a.is_active]
        
        total_assignments = len(assignments)
        employees = list(set(a.employee_id for a in assignments))
        roles = list(set(a.role for a in assignments if a.role))
        total_allocation = sum(a.allocation_percentage for a in assignments)
        
        return {
            "project_id": project_id,
            "total_assignments": total_assignments,
            "unique_employees": len(employees),
            "employee_ids": employees,
            "unique_roles": len(roles),
            "roles": roles,
            "total_allocation_percentage": total_allocation,
            "include_inactive": include_inactive
        }