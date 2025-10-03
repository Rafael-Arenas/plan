# -*- coding: utf-8 -*-
"""
Query Operations Interface for Employee Domain Service

Define las operaciones de consulta básicas para empleados a nivel de dominio.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from planificador.models.employee import Employee, EmployeeStatus
from planificador.schemas.employee import EmployeeSearchFilter


class IQueryOperations(ABC):
    """
    Interfaz para operaciones de consulta del dominio Employee.
    
    Define métodos para realizar consultas básicas sobre empleados
    con lógica de negocio aplicada.
    """

    @abstractmethod
    async def get_employees_by_status(self, status: EmployeeStatus) -> List[Employee]:
        """
        Obtiene empleados filtrados por estado.
        
        Args:
            status: Estado del empleado a filtrar
            
        Returns:
            List[Employee]: Lista de empleados con el estado especificado
        """
        pass

    @abstractmethod
    async def get_employees_by_department(self, department: str) -> List[Employee]:
        """
        Obtiene empleados de un departamento específico.
        
        Args:
            department: Nombre del departamento
            
        Returns:
            List[Employee]: Lista de empleados del departamento
        """
        pass

    @abstractmethod
    async def search_employees_by_name(self, name: str) -> List[Employee]:
        """
        Busca empleados por nombre (búsqueda parcial).
        
        Args:
            name: Término de búsqueda para el nombre
            
        Returns:
            List[Employee]: Lista de empleados que coinciden
        """
        pass

    @abstractmethod
    async def get_active_employees(self) -> List[Employee]:
        """
        Obtiene todos los empleados activos.
        
        Returns:
            List[Employee]: Lista de empleados activos
        """
        pass

    @abstractmethod
    async def get_employees_paginated(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """
        Obtiene empleados con paginación.
        
        Args:
            skip: Número de registros a omitir
            limit: Número máximo de registros a retornar
            
        Returns:
            List[Employee]: Lista paginada de empleados
        """
        pass

    @abstractmethod
    async def search_employees(self, filters: EmployeeSearchFilter) -> List[Employee]:
        """
        Busca empleados usando filtros estructurados.
        
        Args:
            filters: Filtros de búsqueda estructurados para empleados
            
        Returns:
            List[Employee]: Lista de empleados que cumplen los criterios
        """
        pass