# src/planificador/repositories/team/interfaces/crud_interface.py

"""
Interfaz para operaciones CRUD del repositorio Team.

Este módulo define la interfaz abstracta para las operaciones básicas
de creación, lectura, actualización y eliminación de equipos.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para operaciones CRUD
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones CRUD básicas

Uso:
    ```python
    class TeamCrudModule(ITeamCrudOperations):
        async def create_team(self, team_data: Dict[str, Any]) -> Team:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from planificador.models.team import Team
from planificador.exceptions.repository import TeamRepositoryError


class ITeamCrudOperations(ABC):
    """
    Interfaz abstracta para operaciones CRUD de equipos.
    
    Define los métodos básicos que debe implementar cualquier módulo
    que maneje operaciones de creación, lectura, actualización y
    eliminación de equipos.
    
    Métodos:
        create_team: Crea un nuevo equipo
        update_team: Actualiza un equipo existente
        delete_team: Elimina un equipo
    """
    
    @abstractmethod
    async def create_team(self, team_data: Dict[str, Any]) -> Team:
        """
        Crea un nuevo equipo con validaciones.
        
        Args:
            team_data: Diccionario con los datos del equipo
                - name (str): Nombre del equipo (requerido)
                - code (str): Código único del equipo (requerido)
                - description (str, opcional): Descripción del equipo
                - department (str, opcional): Departamento al que pertenece
                - leader_id (int, opcional): ID del líder del equipo
                - is_active (bool, opcional): Estado activo del equipo
        
        Returns:
            Team: Instancia del equipo creado
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la creación
            ValidationError: Si los datos no son válidos
        """
        pass
    
    @abstractmethod
    async def update_team(
        self,
        team_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[Team]:
        """
        Actualiza un equipo existente con validaciones.
        
        Args:
            team_id: ID del equipo a actualizar
            update_data: Diccionario con los datos a actualizar
                - name (str, opcional): Nuevo nombre del equipo
                - code (str, opcional): Nuevo código del equipo
                - description (str, opcional): Nueva descripción
                - department (str, opcional): Nuevo departamento
                - leader_id (int, opcional): Nuevo ID del líder
                - is_active (bool, opcional): Nuevo estado activo
        
        Returns:
            Optional[Team]: Equipo actualizado o None si no existe
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la actualización
            ValidationError: Si los datos no son válidos
            NotFoundError: Si el equipo no existe
        """
        pass
    
    @abstractmethod
    async def delete_team(self, team_id: int) -> bool:
        """
        Elimina un equipo del sistema.
        
        Args:
            team_id: ID del equipo a eliminar
        
        Returns:
            bool: True si se eliminó exitosamente, False en caso contrario
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la eliminación
            NotFoundError: Si el equipo no existe
            ValidationError: Si el equipo no puede ser eliminado (tiene dependencias)
        """
        pass