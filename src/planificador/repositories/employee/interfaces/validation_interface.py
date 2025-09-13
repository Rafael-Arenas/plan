from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class IEmployeeValidationOperations(ABC):
    """
    Interfaz para operaciones de validación de empleados.
    
    Define métodos para validar datos de empleados tanto para creación
    como para actualización, incluyendo validaciones de formato y reglas de negocio.
    """
    
    @abstractmethod
    def validate_create_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos para crear un nuevo empleado.
        
        Args:
            data: Diccionario con los datos del empleado
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        pass
    
    @abstractmethod
    def validate_update_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos para actualizar un empleado existente.
        
        Args:
            data: Diccionario con los datos a actualizar
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        pass
    
    @abstractmethod
    def validate_skills_json(self, skills_json: Optional[str]) -> Optional[List[str]]:
        """
        Valida y convierte un JSON de habilidades a lista.
        
        Args:
            skills_json: JSON string con las habilidades
            
        Returns:
            Lista de habilidades validadas o None
            
        Raises:
            ValidationError: Si el JSON no es válido
        """
        pass
    
    @abstractmethod
    def validate_search_term(self, search_term: str) -> str:
        """
        Valida y limpia un término de búsqueda.
        
        Args:
            search_term: Término de búsqueda a validar
            
        Returns:
            Término de búsqueda validado y limpio
            
        Raises:
            ValidationError: Si el término no es válido
        """
        pass
    
    @abstractmethod
    def validate_employee_id(self, employee_id: int) -> None:
        """
        Valida que un ID de empleado sea válido.
        
        Args:
            employee_id: ID del empleado a validar
            
        Raises:
            ValidationError: Si el ID no es válido
        """
        pass