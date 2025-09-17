# src/planificador/repositories/team/interfaces/query_interface.py

"""
Interfaz para operaciones de consulta del repositorio Team.

Este módulo define la interfaz abstracta para las operaciones de
búsqueda y consulta de equipos en el sistema.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para consultas
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones de consulta

Uso:
    ```python
    class TeamQueryModule(ITeamQueryOperations):
        async def get_team_by_id(self, team_id: int) -> Optional[Team]:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.models.team import Team
from planificador.models.employee import Employee
from planificador.exceptions.repository import TeamRepositoryError


class ITeamQueryOperations(ABC):
    """
    Interfaz abstracta para operaciones de consulta de equipos.
    
    Define los métodos de búsqueda y consulta que debe implementar
    cualquier módulo que maneje la recuperación de datos de equipos.
    
    Métodos:
        - Consultas básicas por ID, nombre, código
        - Búsquedas por criterios específicos
        - Consultas por relaciones (departamento, líder)
        - Consultas con filtros avanzados
    """
    
    @abstractmethod
    async def get_team_by_id(self, team_id: int) -> Optional[Team]:
        """
        Obtiene un equipo por su ID.
        
        Args:
            team_id: ID del equipo a buscar
        
        Returns:
            Optional[Team]: Equipo encontrado o None si no existe
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """
        Obtiene un equipo por su nombre exacto.
        
        Args:
            name: Nombre exacto del equipo
        
        Returns:
            Optional[Team]: Equipo encontrado o None si no existe
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_team_by_code(self, code: str) -> Optional[Team]:
        """
        Obtiene un equipo por su código único.
        
        Args:
            code: Código único del equipo
        
        Returns:
            Optional[Team]: Equipo encontrado o None si no existe
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def search_teams_by_name(self, search_term: str) -> List[Team]:
        """
        Busca equipos por término en el nombre (búsqueda parcial).
        
        Args:
            search_term: Término a buscar en el nombre
        
        Returns:
            List[Team]: Lista de equipos que coinciden
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la búsqueda
        """
        pass
    
    @abstractmethod
    async def search_teams_by_code(self, search_term: str) -> List[Team]:
        """
        Busca equipos por término en el código (búsqueda parcial).
        
        Args:
            search_term: Término a buscar en el código
        
        Returns:
            List[Team]: Lista de equipos que coinciden
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la búsqueda
        """
        pass
    
    @abstractmethod
    async def search_teams_by_description(self, search_term: str) -> List[Team]:
        """
        Busca equipos por término en la descripción.
        
        Args:
            search_term: Término a buscar en la descripción
        
        Returns:
            List[Team]: Lista de equipos que coinciden
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la búsqueda
        """
        pass
    
    @abstractmethod
    async def get_active_teams(self) -> List[Team]:
        """
        Obtiene todos los equipos activos.
        
        Returns:
            List[Team]: Lista de equipos activos
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_teams_by_department(self, department: str) -> List[Team]:
        """
        Obtiene equipos por departamento.
        
        Args:
            department: Nombre del departamento
        
        Returns:
            List[Team]: Lista de equipos del departamento
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_teams_by_leader(self, leader_id: int) -> List[Team]:
        """
        Obtiene equipos liderados por un empleado específico.
        
        Args:
            leader_id: ID del empleado líder
        
        Returns:
            List[Team]: Lista de equipos liderados por el empleado
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_teams_by_size_range(
        self, 
        min_size: int, 
        max_size: int
    ) -> List[Team]:
        """
        Obtiene equipos cuyo número de miembros esté dentro del rango.
        
        Args:
            min_size: Tamaño mínimo del equipo
            max_size: Tamaño máximo del equipo
        
        Returns:
            List[Team]: Lista de equipos en el rango de tamaño
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_all_teams(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Team]:
        """
        Obtiene todos los equipos con paginación opcional.
        
        Args:
            limit: Número máximo de equipos a retornar
            offset: Número de equipos a omitir
        
        Returns:
            List[Team]: Lista de equipos
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def search_teams(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Team]:
        """
        Busca equipos usando filtros múltiples.
        
        Args:
            filters: Diccionario con criterios de búsqueda
                - name: Búsqueda parcial en nombre
                - code: Búsqueda parcial en código
                - department: Departamento exacto
                - is_active: Estado activo
                - has_leader: Si tiene líder asignado
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
        
        Returns:
            List[Team]: Lista de equipos que coinciden con los filtros
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la búsqueda
        """
        pass
    
    @abstractmethod
    async def count_teams(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número de equipos que coinciden con los filtros.
        
        Args:
            filters: Filtros opcionales para aplicar al conteo
        
        Returns:
            int: Número de equipos que coinciden
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el conteo
        """
        pass