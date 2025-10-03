# -*- coding: utf-8 -*-
"""
Advanced Query Operations Interface for Employee Domain Service

Define las operaciones de consulta avanzadas y complejas para empleados.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from planificador.models.employee import Employee


class IAdvancedQueryOperations(ABC):
    """
    Interfaz para operaciones de consulta avanzadas del dominio Employee.
    
    Define métodos para realizar consultas complejas con múltiples filtros
    y criterios de búsqueda sofisticados.
    """

    @abstractmethod
    async def advanced_employee_search(self, filters: Dict[str, Any]) -> List[Employee]:
        """
        Realiza búsqueda avanzada de empleados con múltiples filtros.
        
        Args:
            filters: Diccionario con criterios de búsqueda
                    Puede incluir: department, position, status, skills, etc.
            
        Returns:
            List[Employee]: Lista de empleados que cumplen los criterios
        """
        pass

    @abstractmethod
    async def get_employees_with_skills(self, skills: List[str]) -> List[Employee]:
        """
        Obtiene empleados que poseen habilidades específicas.
        
        Args:
            skills: Lista de habilidades requeridas
            
        Returns:
            List[Employee]: Lista de empleados con las habilidades
        """
        pass

    @abstractmethod
    async def get_employees_by_salary_range(
        self,
        min_salary: float,
        max_salary: float
    ) -> List[Employee]:
        """
        Obtiene empleados dentro de un rango salarial.
        
        Args:
            min_salary: Salario mínimo
            max_salary: Salario máximo
            
        Returns:
            List[Employee]: Lista de empleados en el rango salarial
        """
        pass