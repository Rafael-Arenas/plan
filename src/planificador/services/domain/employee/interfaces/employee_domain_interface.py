# -*- coding: utf-8 -*-
"""
Interfaz del Servicio de Dominio Employee

Define el contrato principal para el servicio de dominio de empleados,
especificando todas las operaciones disponibles para la gestión de empleados.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import date

from planificador.models.employee import Employee, EmployeeStatus


class IEmployeeDomainService(ABC):
    """
    Interfaz para el servicio de dominio de empleados.
    
    Define el contrato para todas las operaciones de negocio relacionadas
    con la gestión de empleados, incluyendo CRUD, consultas, validaciones,
    estadísticas y operaciones de salud del servicio.
    """

    # ========== Operaciones CRUD ==========
    
    @abstractmethod
    async def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        """Crea un nuevo empleado con validaciones de negocio."""
        pass

    @abstractmethod
    async def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """Obtiene un empleado por su ID."""
        pass

    @abstractmethod
    async def update_employee(self, employee_id: int, employee_data: Dict[str, Any]) -> Optional[Employee]:
        """Actualiza un empleado existente con validaciones."""
        pass

    @abstractmethod
    async def delete_employee(self, employee_id: int) -> bool:
        """Elimina un empleado verificando dependencias."""
        pass

    # ========== Operaciones de Consulta ==========
    
    @abstractmethod
    async def search_employees(self, filters: Dict[str, Any]) -> List[Employee]:
        """Busca empleados con filtros avanzados."""
        pass

    # ========== Operaciones de Estadísticas ==========
    
    @abstractmethod
    async def get_employee_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas de empleados."""
        pass

    # ========== Operaciones de Validación ==========
    
    @abstractmethod
    async def validate_employee_business_rules(self, employee_data: Dict[str, Any]) -> bool:
        """Valida reglas de negocio para empleados."""
        pass

    # ========== Health Check ==========
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verifica el estado de salud del servicio."""
        pass