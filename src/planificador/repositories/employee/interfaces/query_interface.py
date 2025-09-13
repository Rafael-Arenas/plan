from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import date

from planificador.models.employee import Employee, EmployeeStatus


class IEmployeeQueryOperations(ABC):
    """
    Interfaz para operaciones de consulta avanzadas de empleados.
    
    Define métodos para búsquedas complejas, filtrado por criterios específicos
    y consultas de disponibilidad.
    """
    @abstractmethod
    async def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado por su ID.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado encontrado o None
        """
        pass

    @abstractmethod
    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Employee]:
        """
        Obtiene un empleado por un campo único.

        Args:
            field_name: Nombre del campo único
            value: Valor del campo

        Returns:
            Empleado o None si no se encuentra
        """
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """
        Obtiene una lista paginada de todos los empleados.
        
        Args:
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de empleados
        """
        pass

    @abstractmethod
    async def employee_exists(self, employee_id: int) -> bool:
        """
        Verifica si un empleado existe por su ID.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            True si el empleado existe, False en caso contrario
        """
        pass

    @abstractmethod
    async def count(self) -> int:
        """
        Cuenta el número total de empleados.
        
        Returns:
            Número total de empleados
        """
        pass

    @abstractmethod
    async def search_by_name(self, name: str, **kwargs) -> List[Employee]:
        """
        Busca empleados por término de búsqueda en el nombre.
        
        Args:
            name: Término de búsqueda
            
        Returns:
            Lista de empleados que coinciden con la búsqueda
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Employee]:
        """
        Busca un empleado por su email.
        
        Args:
            email: Email del empleado
            
        Returns:
            Empleado encontrado o None
        """
        pass

    @abstractmethod
    async def get_by_status(self, status: EmployeeStatus, **kwargs) -> List[Employee]:
        """
        Obtiene empleados por estado.
        
        Args:
            status: Estado del empleado
            
        Returns:
            Lista de empleados con el estado especificado
        """
        pass

    @abstractmethod
    async def get_available_employees(self, **kwargs) -> List[Employee]:
        """
        Obtiene empleados disponibles.
        
        Returns:
            Lista de empleados disponibles
        """
        pass

    @abstractmethod
    async def search_by_skills(self, skills: Union[str, List[str]], **kwargs) -> List[Employee]:
        """
        Obtiene empleados que tienen las habilidades especificadas.
        
        Args:
            skills: Lista de habilidades requeridas
            
        Returns:
            Lista de empleados con las habilidades
        """
        pass

    @abstractmethod
    async def get_by_department(self, department: str, **kwargs) -> List[Employee]:
        """
        Obtiene empleados por departamento.
        
        Args:
            department: Nombre del departamento
            
        Returns:
            Lista de empleados del departamento
        """
        pass

    @abstractmethod
    async def get_by_position(self, position: str, **kwargs) -> List[Employee]:
        """
        Obtiene empleados por posición.
        
        Args:
            position: Nombre de la posición
            
        Returns:
            Lista de empleados con la posición especificada
        """
        pass

    @abstractmethod
    async def get_by_salary_range(self, min_salary: float, max_salary: float, **kwargs) -> List[Employee]:
        """
        Obtiene empleados por rango salarial.
        
        Args:
            min_salary: Salario mínimo
            max_salary: Salario máximo
            
        Returns:
            Lista de empleados en el rango salarial
        """
        pass

    @abstractmethod
    async def get_by_hire_date_range(self, start_date: date, end_date: date, **kwargs) -> List[Employee]:
        """
        Obtiene empleados por rango de fecha de contratación.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            
        Returns:
            Lista de empleados contratados en el rango de fechas
        """
        pass

    @abstractmethod
    async def advanced_search(self, filters: Dict[str, Any], **kwargs) -> List[Employee]:
        """
        Búsqueda avanzada con múltiples filtros.
        
        Args:
            filters: Diccionario con filtros a aplicar
            
        Returns:
            Lista de empleados que cumplen los filtros
        """
        pass

    @abstractmethod
    async def get_by_full_name(self, full_name: str) -> Optional[Employee]:
        """
        Busca un empleado por su nombre completo.
        
        Args:
            full_name: Nombre completo del empleado
            
        Returns:
            Empleado encontrado o None
        """
        pass

    @abstractmethod
    async def get_by_employee_code(self, employee_code: str) -> Optional[Employee]:
        """
        Busca un empleado por su código de empleado.
        
        Args:
            employee_code: Código del empleado
            
        Returns:
            Empleado encontrado o None
        """
        pass

    @abstractmethod
    async def get_active_employees(self) -> List[Employee]:
        """
        Obtiene todos los empleados activos.
        
        Returns:
            Lista de empleados activos
        """
        pass

    @abstractmethod
    async def get_with_teams(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado con sus equipos cargados.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado con equipos cargados o None
        """
        pass

    @abstractmethod
    async def get_with_projects(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado con sus proyectos cargados.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado con proyectos cargados o None
        """
        pass

    @abstractmethod
    async def full_name_exists(self, full_name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un empleado con el nombre completo especificado.
        
        Args:
            full_name: Nombre completo a verificar
            exclude_id: ID a excluir de la búsqueda (para actualizaciones)
            
        Returns:
            True si existe, False en caso contrario
        """
        pass

    @abstractmethod
    async def employee_code_exists(self, employee_code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un empleado con el código especificado.
        
        Args:
            employee_code: Código de empleado a verificar
            exclude_id: ID a excluir de la búsqueda (para actualizaciones)
            
        Returns:
            True si existe, False en caso contrario
        """
        pass

    @abstractmethod
    async def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un empleado con el email especificado.
        
        Args:
            email: Email a verificar
            exclude_id: ID a excluir de la búsqueda (para actualizaciones)
            
        Returns:
            True si existe, False en caso contrario
        """
        pass