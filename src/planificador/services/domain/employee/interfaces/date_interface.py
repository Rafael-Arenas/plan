# -*- coding: utf-8 -*-
"""
Date Operations Interface for Employee Domain Service

Define las operaciones relacionadas con fechas y tiempo para empleados.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date

from planificador.models.employee import Employee


class IDateOperations(ABC):
    """
    Interfaz para operaciones de fechas del dominio Employee.
    
    Define métodos para gestionar operaciones relacionadas con fechas
    de contratación, antigüedad y períodos temporales.
    """

    @abstractmethod
    async def get_employees_hired_in_period(
        self,
        start_date: date,
        end_date: date
    ) -> List[Employee]:
        """
        Obtiene empleados contratados en un período específico.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            List[Employee]: Lista de empleados contratados en el período
        """
        pass

    @abstractmethod
    async def get_employees_by_tenure_range(
        self,
        min_years: float,
        max_years: float
    ) -> List[Employee]:
        """
        Obtiene empleados por rango de antigüedad.
        
        Args:
            min_years: Antigüedad mínima en años
            max_years: Antigüedad máxima en años
            
        Returns:
            List[Employee]: Lista de empleados en el rango de antigüedad
        """
        pass

    @abstractmethod
    async def calculate_employee_tenure(self, employee_id: int) -> Dict[str, Any]:
        """
        Calcula la antigüedad detallada de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Dict[str, Any]: Información detallada de antigüedad
                          (años, meses, días, etc.)
        """
        pass

    @abstractmethod
    async def get_employees_hired_current_month(self) -> List[Employee]:
        """
        Obtiene empleados contratados en el mes actual.
        
        Returns:
            List[Employee]: Lista de empleados contratados este mes
        """
        pass