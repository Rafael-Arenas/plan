"""Módulo de operaciones de consulta para asignaciones de proyectos.

Este módulo implementa la interfaz IQueryOperations y proporciona
funcionalidades especializadas para consultas básicas de asignaciones de proyectos,
optimizadas mediante la herencia de BaseRepository.

Versión: 1.0.0
"""

from typing import Any
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_

from planificador.models.project_assignment import ProjectAssignment
from planificador.repositories.base_repository import BaseRepository
from ..interfaces.query_interface import IQueryOperations


class QueryOperations(BaseRepository[ProjectAssignment], IQueryOperations):
    """Implementación de operaciones de consulta para asignaciones de proyectos.

    Hereda de BaseRepository para reutilizar la lógica de acceso a datos
    y se especializa en consultas comunes sobre la entidad ProjectAssignment.
    """

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones de consulta.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
        """
        super().__init__(session, ProjectAssignment)
        self._logger = self._logger.bind(component="ProjectAssignmentQueryOperations")
        self._logger.debug("QueryOperations para ProjectAssignment inicializado")

    async def get_all_assignments(
        self, limit: int | None = None, offset: int = 0
    ) -> list[ProjectAssignment]:
        """Obtiene todas las asignaciones con paginación opcional.
        
        Args:
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            
        Returns:
            Lista de asignaciones
        """
        self._logger.debug(f"Obteniendo todas las asignaciones (limit={limit}, offset={offset})")
        return await self.get_all(limit=limit, offset=offset)

    async def get_assignments_by_employee(self, employee_id: int) -> list[ProjectAssignment]:
        """Obtiene todas las asignaciones de un empleado específico.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de asignaciones del empleado
        """
        self._logger.debug(f"Obteniendo asignaciones del empleado ID: {employee_id}")
        return await self.find_by_criteria({"employee_id": employee_id})

    async def get_assignments_by_project(self, project_id: int) -> list[ProjectAssignment]:
        """Obtiene todas las asignaciones de un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de asignaciones del proyecto
        """
        self._logger.debug(f"Obteniendo asignaciones del proyecto ID: {project_id}")
        return await self.find_by_criteria({"project_id": project_id})

    async def get_active_assignments(self) -> list[ProjectAssignment]:
        """Obtiene todas las asignaciones activas.
        
        Returns:
            Lista de asignaciones activas
        """
        self._logger.debug("Obteniendo asignaciones activas")
        return await self.find_by_criteria({"is_active": True})

    async def get_assignments_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[ProjectAssignment]:
        """Obtiene asignaciones que se superponen con un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            
        Returns:
            Lista de asignaciones en el rango
        """
        self._logger.debug(f"Obteniendo asignaciones entre {start_date} y {end_date}")
        # Buscar asignaciones que se superponen con el rango
        criteria = {
            "start_date": {"operator": "<=", "value": end_date},
            "end_date": {"operator": ">=", "value": start_date}
        }
        return await self.find_by_criteria(criteria)

    async def get_assignments_by_role(self, role: str) -> list[ProjectAssignment]:
        """Obtiene asignaciones por rol específico.
        
        Args:
            role: Rol a buscar
            
        Returns:
            Lista de asignaciones con el rol especificado
        """
        self._logger.debug(f"Obteniendo asignaciones con rol: {role}")
        return await self.find_by_criteria({"role": role})

    async def get_assignments_with_filters(
        self,
        employee_id: int | None = None,
        project_id: int | None = None,
        role: str | None = None,
        is_active: bool | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[ProjectAssignment]:
        """Obtiene asignaciones aplicando múltiples filtros.
        
        Args:
            employee_id: ID del empleado (opcional)
            project_id: ID del proyecto (opcional)
            role: Rol (opcional)
            is_active: Estado activo (opcional)
            start_date: Fecha de inicio mínima (opcional)
            end_date: Fecha de fin máxima (opcional)
            
        Returns:
            Lista de asignaciones que cumplen los filtros
        """
        criteria = {}
        
        if employee_id is not None:
            criteria["employee_id"] = employee_id
        if project_id is not None:
            criteria["project_id"] = project_id
        if role is not None:
            criteria["role"] = role
        if is_active is not None:
            criteria["is_active"] = is_active
        if start_date is not None:
            criteria["start_date"] = {"operator": ">=", "value": start_date}
        if end_date is not None:
            criteria["end_date"] = {"operator": "<=", "value": end_date}
        
        self._logger.debug(f"Obteniendo asignaciones con filtros: {criteria}")
        return await self.find_by_criteria(criteria)

    async def get_overlapping_assignments(
        self, employee_id: int, start_date: date, end_date: date, exclude_id: int | None = None
    ) -> list[ProjectAssignment]:
        """Obtiene asignaciones que se superponen para un empleado en un período.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            exclude_id: ID de asignación a excluir (opcional)
            
        Returns:
            Lista de asignaciones superpuestas
        """
        criteria = {
            "employee_id": employee_id,
            "start_date": {"operator": "<=", "value": end_date},
            "end_date": {"operator": ">=", "value": start_date}
        }
        
        if exclude_id is not None:
            criteria["id"] = {"operator": "!=", "value": exclude_id}
        
        self._logger.debug(
            f"Obteniendo asignaciones superpuestas para empleado {employee_id} "
            f"entre {start_date} y {end_date}"
        )
        return await self.find_by_criteria(criteria)

    async def get_by_unique_field(self, field_name: str, value: Any) -> ProjectAssignment | None:
        """Obtiene una asignación por un campo único delegando en el repositorio base.
        
        Args:
            field_name: Nombre del campo único
            value: Valor del campo
            
        Returns:
            Asignación encontrada o None si no existe
        """
        self._logger.debug(f"Obteniendo asignación por {field_name}: {value}")
        return await self.get_by_field(field_name, value)

    async def search_assignments_by_filters(
        self, filters: dict[str, Any], limit: int = 50, offset: int = 0
    ) -> list[ProjectAssignment]:
        """Busca asignaciones usando múltiples filtros.
        
        Args:
            filters: Diccionario de filtros a aplicar
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            
        Returns:
            Lista de asignaciones que coinciden con los filtros
        """
        self._logger.debug(f"Buscando asignaciones con filtros: {filters}")
        return await self.find_by_criteria(filters, limit=limit, offset=offset)