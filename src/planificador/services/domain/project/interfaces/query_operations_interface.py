"""
Interfaz para las operaciones de consulta de proyectos.

Esta interfaz define el contrato para todas las operaciones de búsqueda,
filtrado y consulta de proyectos con diferentes criterios.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from datetime import date

from planificador.models.project import Project, ProjectStatus, ProjectPriority
from planificador.schemas.project.project import ProjectSearchFilter


class IProjectQueryOperations(ABC):
    """
    Interfaz abstracta para las operaciones de consulta de proyectos.
    
    Define el contrato para todas las operaciones de búsqueda, filtrado
    y consulta de proyectos con diferentes criterios y parámetros.
    """

    # ==========================================
    # BÚSQUEDAS BÁSICAS
    # ==========================================

    @abstractmethod
    async def search_projects(self, filters: ProjectSearchFilter) -> List[Project]:
        """
        Busca proyectos aplicando filtros específicos.
        
        Args:
            filters (ProjectSearchFilter): Filtros de búsqueda
            
        Returns:
            List[Project]: Lista de proyectos que coinciden con los filtros
            
        Raises:
            ValidationError: Si los filtros no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def search_projects_by_text(
        self, 
        search_text: str,
        search_fields: Optional[List[str]] = None
    ) -> List[Project]:
        """
        Busca proyectos por texto en campos específicos.
        
        Args:
            search_text (str): Texto a buscar
            search_fields (List[str], optional): Campos donde buscar
            
        Returns:
            List[Project]: Proyectos que contienen el texto
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # CONSULTAS POR ESTADO
    # ==========================================

    @abstractmethod
    async def get_projects_by_status(self, status: ProjectStatus) -> List[Project]:
        """
        Obtiene proyectos filtrados por estado.
        
        Args:
            status (ProjectStatus): Estado de los proyectos a buscar
            
        Returns:
            List[Project]: Proyectos con el estado especificado
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_active_projects(self) -> List[Project]:
        """
        Obtiene todos los proyectos activos (en progreso).
        
        Returns:
            List[Project]: Lista de proyectos activos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_completed_projects(self) -> List[Project]:
        """
        Obtiene todos los proyectos completados.
        
        Returns:
            List[Project]: Lista de proyectos completados
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_pending_projects(self) -> List[Project]:
        """
        Obtiene todos los proyectos pendientes de iniciar.
        
        Returns:
            List[Project]: Lista de proyectos pendientes
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # CONSULTAS POR CLIENTE
    # ==========================================

    @abstractmethod
    async def get_projects_by_client(self, client_id: int) -> List[Project]:
        """
        Obtiene proyectos de un cliente específico.
        
        Args:
            client_id (int): ID del cliente
            
        Returns:
            List[Project]: Proyectos del cliente especificado
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_projects_by_multiple_clients(
        self, 
        client_ids: List[int]
    ) -> List[Project]:
        """
        Obtiene proyectos de múltiples clientes.
        
        Args:
            client_ids (List[int]): Lista de IDs de clientes
            
        Returns:
            List[Project]: Proyectos de los clientes especificados
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # CONSULTAS POR PRIORIDAD
    # ==========================================

    @abstractmethod
    async def get_projects_by_priority(self, priority: ProjectPriority) -> List[Project]:
        """
        Obtiene proyectos filtrados por prioridad.
        
        Args:
            priority (ProjectPriority): Prioridad de los proyectos
            
        Returns:
            List[Project]: Proyectos con la prioridad especificada
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_high_priority_projects(self) -> List[Project]:
        """
        Obtiene todos los proyectos de alta prioridad.
        
        Returns:
            List[Project]: Lista de proyectos de alta prioridad
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # CONSULTAS POR FECHAS
    # ==========================================

    @abstractmethod
    async def get_projects_by_date_range(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[Project]:
        """
        Obtiene proyectos dentro de un rango de fechas.
        
        Args:
            start_date (date, optional): Fecha de inicio del rango
            end_date (date, optional): Fecha de fin del rango
            
        Returns:
            List[Project]: Proyectos dentro del rango de fechas
            
        Raises:
            ValidationError: Si el rango de fechas no es válido
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_overdue_projects(self) -> List[Project]:
        """
        Obtiene proyectos que han superado su fecha de finalización.
        
        Returns:
            List[Project]: Lista de proyectos vencidos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_projects_ending_soon(self, days_ahead: int = 30) -> List[Project]:
        """
        Obtiene proyectos que finalizan próximamente.
        
        Args:
            days_ahead (int): Número de días hacia adelante a considerar
            
        Returns:
            List[Project]: Proyectos que finalizan pronto
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_projects_starting_soon(self, days_ahead: int = 7) -> List[Project]:
        """
        Obtiene proyectos que inician próximamente.
        
        Args:
            days_ahead (int): Número de días hacia adelante a considerar
            
        Returns:
            List[Project]: Proyectos que inician pronto
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # CONSULTAS CON PAGINACIÓN
    # ==========================================

    @abstractmethod
    async def get_projects_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[ProjectSearchFilter] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Tuple[List[Project], int, Dict[str, Any]]:
        """
        Obtiene proyectos con paginación y ordenamiento.
        
        Args:
            page (int): Número de página (base 1)
            page_size (int): Tamaño de página
            filters (ProjectSearchFilter, optional): Filtros a aplicar
            sort_by (str, optional): Campo por el cual ordenar
            sort_order (str): Orden de clasificación ('asc' o 'desc')
            
        Returns:
            Tuple[List[Project], int, Dict[str, Any]]: 
                - Lista de proyectos
                - Total de registros
                - Metadatos de paginación
                
        Raises:
            ValidationError: Si los parámetros de paginación no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # CONSULTAS DE CONTEO
    # ==========================================

    @abstractmethod
    async def count_projects_by_status(self) -> Dict[ProjectStatus, int]:
        """
        Cuenta proyectos agrupados por estado.
        
        Returns:
            Dict[ProjectStatus, int]: Conteo de proyectos por estado
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def count_projects_by_client(self, client_id: int) -> int:
        """
        Cuenta proyectos de un cliente específico.
        
        Args:
            client_id (int): ID del cliente
            
        Returns:
            int: Número de proyectos del cliente
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def count_total_projects(self, include_archived: bool = False) -> int:
        """
        Cuenta el total de proyectos en el sistema.
        
        Args:
            include_archived (bool): Si incluir proyectos archivados
            
        Returns:
            int: Número total de proyectos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # CONSULTAS ESPECIALIZADAS
    # ==========================================

    @abstractmethod
    async def get_projects_without_assignments(self) -> List[Project]:
        """
        Obtiene proyectos que no tienen asignaciones de empleados.
        
        Returns:
            List[Project]: Proyectos sin asignaciones
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_projects_by_duration_range(
        self,
        min_days: Optional[int] = None,
        max_days: Optional[int] = None
    ) -> List[Project]:
        """
        Obtiene proyectos filtrados por duración estimada.
        
        Args:
            min_days (int, optional): Duración mínima en días
            max_days (int, optional): Duración máxima en días
            
        Returns:
            List[Project]: Proyectos dentro del rango de duración
            
        Raises:
            ValidationError: Si el rango de duración no es válido
            RepositoryError: Si hay errores en la base de datos
        """
        pass