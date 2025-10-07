"""
Interfaz para las operaciones de relaciones de proyectos.

Esta interfaz define el contrato para la gestión de relaciones entre proyectos,
clientes, empleados, equipos y otras entidades del sistema.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import date

from planificador.models.project import Project
from planificador.schemas.project.project import ProjectWithAssignments


class IProjectRelationshipOperations(ABC):
    """
    Interfaz abstracta para las operaciones de relaciones de proyectos.
    
    Define el contrato para la gestión de todas las relaciones entre proyectos
    y otras entidades del sistema como clientes, empleados, equipos y dependencias.
    """

    # ==========================================
    # RELACIONES CON CLIENTES
    # ==========================================

    @abstractmethod
    async def get_project_with_client_details(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene un proyecto con información detallada del cliente.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Proyecto con detalles del cliente
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_client_project_portfolio(self, client_id: int) -> Dict[str, Any]:
        """
        Obtiene el portafolio completo de proyectos de un cliente.
        
        Args:
            client_id (int): ID del cliente
            
        Returns:
            Dict[str, Any]: Portafolio de proyectos del cliente
            
        Raises:
            NotFoundError: Si el cliente no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_client_project_relationship(
        self, 
        client_id: int
    ) -> Dict[str, Any]:
        """
        Analiza la relación y patrones de proyectos de un cliente.
        
        Args:
            client_id (int): ID del cliente
            
        Returns:
            Dict[str, Any]: Análisis de la relación cliente-proyectos
            
        Raises:
            NotFoundError: Si el cliente no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_client_project_history(
        self, 
        client_id: int,
        include_archived: bool = False
    ) -> List[Project]:
        """
        Obtiene el historial completo de proyectos de un cliente.
        
        Args:
            client_id (int): ID del cliente
            include_archived (bool): Incluir proyectos archivados
            
        Returns:
            List[Project]: Historial de proyectos del cliente
            
        Raises:
            NotFoundError: Si el cliente no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_client_project_relationship(
        self,
        client_id: int,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valida la relación entre un cliente y un proyecto.
        
        Args:
            client_id (int): ID del cliente
            project_data (Dict[str, Any]): Datos del proyecto
            
        Returns:
            Dict[str, Any]: Resultado de la validación
            
        Raises:
            NotFoundError: Si el cliente no existe
            ValidationError: Si la relación no es válida
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # RELACIONES CON EMPLEADOS Y ASIGNACIONES
    # ==========================================

    @abstractmethod
    async def get_project_with_assignments(self, project_id: int) -> ProjectWithAssignments:
        """
        Obtiene un proyecto con todas sus asignaciones de empleados.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            ProjectWithAssignments: Proyecto con asignaciones
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_employee_project_assignments(
        self, 
        employee_id: int,
        active_only: bool = True
    ) -> List[ProjectWithAssignments]:
        """
        Obtiene todos los proyectos asignados a un empleado.
        
        Args:
            employee_id (int): ID del empleado
            active_only (bool): Solo proyectos activos
            
        Returns:
            List[ProjectWithAssignments]: Proyectos asignados al empleado
            
        Raises:
            NotFoundError: Si el empleado no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_employee_project_workload(
        self, 
        employee_id: int,
        date_range: Optional[tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Analiza la carga de trabajo de un empleado en proyectos.
        
        Args:
            employee_id (int): ID del empleado
            date_range (tuple[date, date], optional): Rango de fechas para análisis
            
        Returns:
            Dict[str, Any]: Análisis de carga de trabajo
            
        Raises:
            NotFoundError: Si el empleado no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_project_team_composition(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene la composición del equipo de un proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Composición del equipo del proyecto
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_employee_project_assignment(
        self,
        employee_id: int,
        project_id: int,
        assignment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valida la asignación de un empleado a un proyecto.
        
        Args:
            employee_id (int): ID del empleado
            project_id (int): ID del proyecto
            assignment_data (Dict[str, Any]): Datos de la asignación
            
        Returns:
            Dict[str, Any]: Resultado de la validación
            
        Raises:
            NotFoundError: Si el empleado o proyecto no existe
            ValidationError: Si la asignación no es válida
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # DEPENDENCIAS ENTRE PROYECTOS
    # ==========================================

    @abstractmethod
    async def get_project_dependencies(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las dependencias de un proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            List[Dict[str, Any]]: Lista de dependencias del proyecto
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_dependent_projects(self, project_id: int) -> List[Project]:
        """
        Obtiene proyectos que dependen del proyecto especificado.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            List[Project]: Proyectos dependientes
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_related_projects(self, project_id: int) -> List[Project]:
        """
        Obtiene proyectos relacionados (dependencias bidireccionales).
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            List[Project]: Proyectos relacionados
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_project_dependency_chain(self, project_id: int) -> Dict[str, Any]:
        """
        Analiza la cadena completa de dependencias de un proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Análisis de la cadena de dependencias
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_project_dependency(
        self,
        project_id: int,
        dependency_id: int
    ) -> Dict[str, Any]:
        """
        Valida una dependencia entre proyectos.
        
        Args:
            project_id (int): ID del proyecto principal
            dependency_id (int): ID del proyecto dependencia
            
        Returns:
            Dict[str, Any]: Resultado de la validación
            
        Raises:
            NotFoundError: Si algún proyecto no existe
            ValidationError: Si la dependencia crea ciclos o es inválida
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # RELACIONES CON EQUIPOS
    # ==========================================

    @abstractmethod
    async def get_team_projects(self, team_id: int) -> List[ProjectWithAssignments]:
        """
        Obtiene todos los proyectos asignados a un equipo.
        
        Args:
            team_id (int): ID del equipo
            
        Returns:
            List[ProjectWithAssignments]: Proyectos del equipo
            
        Raises:
            NotFoundError: Si el equipo no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_team_project_distribution(self, team_id: int) -> Dict[str, Any]:
        """
        Analiza la distribución de proyectos dentro de un equipo.
        
        Args:
            team_id (int): ID del equipo
            
        Returns:
            Dict[str, Any]: Análisis de distribución de proyectos
            
        Raises:
            NotFoundError: Si el equipo no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # RECURSOS COMPARTIDOS ENTRE PROYECTOS
    # ==========================================

    @abstractmethod
    async def get_cross_project_resources(self) -> Dict[str, Any]:
        """
        Obtiene análisis de recursos compartidos entre proyectos.
        
        Returns:
            Dict[str, Any]: Análisis de recursos compartidos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_resource_conflicts(
        self,
        date_range: Optional[tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Analiza conflictos de recursos entre proyectos.
        
        Args:
            date_range (tuple[date, date], optional): Rango de fechas para análisis
            
        Returns:
            Dict[str, Any]: Análisis de conflictos de recursos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_shared_resource_utilization(self) -> Dict[str, Any]:
        """
        Obtiene utilización de recursos compartidos entre proyectos.
        
        Returns:
            Dict[str, Any]: Utilización de recursos compartidos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ANÁLISIS DE RELACIONES COMPLEJAS
    # ==========================================

    @abstractmethod
    async def get_project_relationship_matrix(self) -> Dict[str, Any]:
        """
        Obtiene matriz de relaciones entre todos los proyectos.
        
        Returns:
            Dict[str, Any]: Matriz de relaciones de proyectos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_project_network_effects(self, project_id: int) -> Dict[str, Any]:
        """
        Analiza efectos de red de un proyecto en el sistema.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Análisis de efectos de red
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass