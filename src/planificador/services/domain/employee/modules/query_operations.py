# -*- coding: utf-8 -*-
"""
Query Operations Implementation for Employee Domain Service

Implementación concreta de las operaciones de consulta básicas para empleados.
"""

from typing import List
from loguru import logger

from planificador.models.employee import Employee, EmployeeStatus
from planificador.repositories.employee_repository_facade import EmployeeRepositoryFacade
from planificador.schemas.employee import EmployeeSearchFilter
from ..interfaces.query_interface import IQueryOperations


class QueryOperations(IQueryOperations):
    """
    Implementación de operaciones de consulta para el dominio Employee.
    
    Proporciona funcionalidades para realizar consultas básicas sobre empleados
    con lógica de negocio aplicada.
    """

    def __init__(self, repository_facade: EmployeeRepositoryFacade):
        """
        Inicializa las operaciones de consulta.
        
        Args:
            repository_facade: Fachada del repositorio de empleados
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="employee_query_operations")

    async def get_employees_by_status(self, status: EmployeeStatus) -> List[Employee]:
        """
        Obtiene empleados filtrados por estado.
        
        Args:
            status: Estado del empleado a filtrar
            
        Returns:
            List[Employee]: Lista de empleados con el estado especificado
        """
        self._logger.info(f"Consultando empleados por estado: {status}")
        
        try:
            employees = await self._repository.get_by_status(status)
            self._logger.info(f"Encontrados {len(employees)} empleados con estado {status}")
            return employees
            
        except Exception as e:
            self._logger.error(f"Error consultando empleados por estado {status}: {e}")
            raise

    async def get_employees_by_department(self, department: str) -> List[Employee]:
        """
        Obtiene empleados de un departamento específico.
        
        Args:
            department: Nombre del departamento
            
        Returns:
            List[Employee]: Lista de empleados del departamento
        """
        self._logger.info(f"Consultando empleados por departamento: {department}")
        
        try:
            employees = await self._repository.get_by_department(department)
            self._logger.info(f"Encontrados {len(employees)} empleados en departamento {department}")
            return employees
            
        except Exception as e:
            self._logger.error(f"Error consultando empleados por departamento {department}: {e}")
            raise

    async def search_employees_by_name(self, name: str) -> List[Employee]:
        """
        Busca empleados por nombre (búsqueda parcial).
        
        Args:
            name: Término de búsqueda para el nombre
            
        Returns:
            List[Employee]: Lista de empleados que coinciden
        """
        self._logger.info(f"Buscando empleados por nombre: {name}")
        
        try:
            employees = await self._repository.search_by_name(name)
            self._logger.info(f"Encontrados {len(employees)} empleados con nombre similar a '{name}'")
            return employees
            
        except Exception as e:
            self._logger.error(f"Error buscando empleados por nombre '{name}': {e}")
            raise

    async def get_active_employees(self) -> List[Employee]:
        """
        Obtiene todos los empleados activos.
        
        Returns:
            List[Employee]: Lista de empleados activos
        """
        self._logger.info("Consultando empleados activos")
        
        try:
            employees = await self._repository.get_active()
            self._logger.info(f"Encontrados {len(employees)} empleados activos")
            return employees
            
        except Exception as e:
            self._logger.error(f"Error consultando empleados activos: {e}")
            raise

    async def get_employees_paginated(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """
        Obtiene empleados con paginación.
        
        Args:
            skip: Número de registros a omitir
            limit: Número máximo de registros a retornar
            
        Returns:
            List[Employee]: Lista paginada de empleados
        """
        self._logger.info(f"Consultando empleados paginados: skip={skip}, limit={limit}")
        
        try:
            employees = await self._repository.get_paginated(skip=skip, limit=limit)
            self._logger.info(f"Obtenidos {len(employees)} empleados (página: skip={skip}, limit={limit})")
            return employees
            
        except Exception as e:
            self._logger.error(f"Error consultando empleados paginados: {e}")
            raise

    async def search_employees(self, filters: EmployeeSearchFilter) -> List[Employee]:
        """
        Busca empleados usando filtros estructurados.
        
        Args:
            filters: Filtros de búsqueda estructurados para empleados
            
        Returns:
            List[Employee]: Lista de empleados que cumplen los criterios
        """
        self._logger.info(f"Buscando empleados con filtros estructurados: {filters}")
        
        try:
            # Convertir EmployeeSearchFilter a diccionario para usar con advanced_search
            filter_dict = {}
            
            if filters.name is not None:
                filter_dict["name"] = filters.name
            if filters.code is not None:
                filter_dict["code"] = filters.code
            if filters.email is not None:
                filter_dict["email"] = filters.email
            if filters.status is not None:
                filter_dict["status"] = filters.status
            if filters.department is not None:
                filter_dict["department"] = filters.department
            if filters.position is not None:
                filter_dict["position"] = filters.position
            if filters.team_id is not None:
                filter_dict["team_id"] = filters.team_id
            if filters.project_id is not None:
                filter_dict["project_id"] = filters.project_id
            
            employees = await self._repository.advanced_search(filter_dict)
            self._logger.info(f"Encontrados {len(employees)} empleados con los filtros aplicados")
            return employees
            
        except Exception as e:
            self._logger.error(f"Error buscando empleados con filtros: {e}")
            raise