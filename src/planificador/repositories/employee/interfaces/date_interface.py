from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union, Optional
from datetime import date

from planificador.models.employee import Employee, EmployeeStatus


class IEmployeeDateOperations(ABC):
    """
    Interfaz para operaciones relacionadas con fechas en empleados.
    
    Define métodos para consultas basadas en fechas de contratación,
    cálculos de antigüedad y operaciones con días laborables.
    """
    
    @abstractmethod
    async def get_employees_hired_current_week(self, **kwargs) -> List[Employee]:
        """
        Obtiene empleados contratados en la semana actual.
        
        Args:
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados contratados esta semana
        """
        pass
    
    @abstractmethod
    async def get_employees_hired_current_month(self, **kwargs) -> List[Employee]:
        """
        Obtiene empleados contratados en el mes actual.
        
        Args:
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados contratados este mes
        """
        pass
    
    @abstractmethod
    async def get_employees_hired_business_days_only(
        self, 
        start_date: Union[date, str, None] = None,
        end_date: Union[date, str, None] = None,
        **kwargs
    ) -> List[Employee]:
        """
        Obtiene empleados contratados solo en días laborables.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados contratados en días laborables
        """
        pass
    
    @abstractmethod
    async def get_by_hire_date_range(self, start_date: date, end_date: date, **kwargs) -> List[Employee]:
        """
        Obtiene empleados por rango de fecha de contratación.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados contratados en el rango de fechas
        """
        pass
    
    @abstractmethod
    async def get_employee_tenure_stats(self, employee_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de antigüedad de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Diccionario con estadísticas de antigüedad
        """
        pass
    
    @abstractmethod
    async def get_employees_by_tenure_range(
        self,
        min_years: float = 0.0,
        max_years: Optional[float] = None,
        status: Optional[EmployeeStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene empleados por rango de antigüedad.
        
        Args:
            min_years: Años mínimos de antigüedad
            max_years: Años máximos de antigüedad (opcional)
            status: Estado del empleado (opcional)
            
        Returns:
            Lista de empleados con información de antigüedad
        """
        pass
    
    @abstractmethod
    async def create_employee_with_date_validation(
        self,
        employee_data: Dict[str, Any],
        validate_hire_date_business_day: bool = False
    ) -> Employee:
        """
        Crea un empleado con validación avanzada de fechas.
        
        Args:
            employee_data: Datos del empleado
            validate_hire_date_business_day: Si validar que la fecha de contratación sea día laborable
            
        Returns:
            Empleado creado
            
        Raises:
            EmployeeDateRangeError: Si las fechas no son válidas
        """
        pass
    
    @abstractmethod
    def format_employee_hire_date(self, employee: Employee, format_type: str = 'default') -> Optional[str]:
        """
        Formatea la fecha de contratación de un empleado.
        
        Args:
            employee: Empleado cuya fecha formatear
            format_type: Tipo de formato ('default', 'short', 'long', etc.)
            
        Returns:
            Fecha formateada como string o None si no tiene fecha
        """
        pass