from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import date


class IEmployeeStatisticsOperations(ABC):
    """
    Interfaz para operaciones de estadísticas de empleados.
    
    Define métodos para generar métricas, análisis estadísticos y resúmenes
    sobre empleados, incluyendo distribuciones y tendencias.
    """
    
    @abstractmethod
    async def get_employee_count_by_status(self) -> Dict[str, int]:
        """
        Obtiene el conteo de empleados por estado.
        
        Returns:
            Diccionario con conteos por estado
        """
        pass
    
    @abstractmethod
    async def get_employee_count_by_department(self) -> Dict[str, int]:
        """
        Obtiene el conteo de empleados por departamento.
        
        Returns:
            Diccionario con conteos por departamento
        """
        pass
    
    @abstractmethod
    async def get_employee_count_by_position(self) -> Dict[str, int]:
        """
        Obtiene el conteo de empleados por posición.
        
        Returns:
            Diccionario con conteos por posición
        """
        pass
    
    @abstractmethod
    async def get_salary_statistics(self) -> Dict[str, float]:
        """
        Obtiene estadísticas de salarios.
        
        Returns:
            Diccionario con estadísticas salariales (promedio, mediana, min, max)
        """
        pass
    
    @abstractmethod
    async def get_hire_date_distribution(self, years: int = 5) -> Dict[str, int]:
        """
        Obtiene la distribución de fechas de contratación.
        
        Args:
            years: Número de años hacia atrás a considerar
            
        Returns:
            Diccionario con distribución por año/mes
        """
        pass
    
    @abstractmethod
    async def get_team_participation_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de participación en equipos.
        
        Returns:
            Diccionario con estadísticas de equipos
        """
        pass
    
    @abstractmethod
    async def get_project_participation_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de participación en proyectos.
        
        Returns:
            Diccionario con estadísticas de proyectos
        """
        pass
    
    @abstractmethod
    async def get_vacation_statistics(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene estadísticas sobre las solicitudes de vacaciones."""
        pass

    @abstractmethod
    async def get_skills_distribution(self, limit: int = 20) -> Dict[str, int]:
        """Obtiene la distribución de habilidades más comunes."""
        pass

    @abstractmethod
    async def get_employee_workload_stats(self, employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Obtiene estadísticas de carga de trabajo de un empleado."""
        pass

    @abstractmethod
    async def get_comprehensive_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen completo de estadísticas de empleados."""
        pass

    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Any]:
        """
        Obtiene una entidad por un campo único.

        Args:
            field_name: Nombre del campo único.
            value: Valor del campo único.

        Returns:
            La entidad si se encuentra, de lo contrario None.
        """
        pass