# -*- coding: utf-8 -*-
"""
Relationship Operations Interface for Client Domain Service

Define las operaciones de gestión de relaciones para la entidad Client
con otras entidades del sistema.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from planificador.schemas.client import Client


class IRelationshipOperations(ABC):
    """
    Interfaz para operaciones de relaciones del dominio Client.
    
    Define métodos para gestionar las relaciones entre clientes
    y otras entidades del sistema con lógica de negocio aplicada.
    """

    @abstractmethod
    async def get_clients_with_projects(
        self,
        include_inactive_projects: bool = False,
        include_inactive_clients: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes que tienen proyectos asociados.
        
        Args:
            include_inactive_projects: Si incluir proyectos inactivos
            include_inactive_clients: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes con proyectos
        """
        pass

    @abstractmethod
    async def get_clients_without_projects(
        self,
        include_inactive_clients: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes que no tienen proyectos asociados.
        
        Args:
            include_inactive_clients: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes sin proyectos
        """
        pass

    @abstractmethod
    async def get_client_projects_count(
        self,
        client_id: UUID,
        include_inactive: bool = False
    ) -> int:
        """
        Obtiene el número de proyectos asociados a un cliente.
        
        Args:
            client_id: ID del cliente
            include_inactive: Si incluir proyectos inactivos
            
        Returns:
            int: Número de proyectos del cliente
        """
        pass

    @abstractmethod
    async def get_clients_with_teams(
        self,
        include_inactive_teams: bool = False,
        include_inactive_clients: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes que tienen equipos asociados.
        
        Args:
            include_inactive_teams: Si incluir equipos inactivos
            include_inactive_clients: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes con equipos
        """
        pass

    @abstractmethod
    async def get_client_teams_count(
        self,
        client_id: UUID,
        include_inactive: bool = False
    ) -> int:
        """
        Obtiene el número de equipos asociados a un cliente.
        
        Args:
            client_id: ID del cliente
            include_inactive: Si incluir equipos inactivos
            
        Returns:
            int: Número de equipos del cliente
        """
        pass

    @abstractmethod
    async def get_clients_by_project_count_range(
        self,
        min_projects: int,
        max_projects: Optional[int] = None,
        include_inactive: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes por rango de número de proyectos.
        
        Args:
            min_projects: Número mínimo de proyectos
            max_projects: Número máximo de proyectos (None = sin límite)
            include_inactive: Si incluir clientes/proyectos inactivos
            
        Returns:
            List[Client]: Lista de clientes en el rango especificado
        """
        pass

    @abstractmethod
    async def get_clients_relationship_summary(
        self,
        client_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Obtiene un resumen de las relaciones de un cliente o todos los clientes.
        
        Args:
            client_id: ID específico del cliente (None para todos)
            
        Returns:
            Dict[str, Any]: Resumen detallado de relaciones
        """
        pass

    @abstractmethod
    async def validate_client_relationships(
        self,
        client_id: UUID
    ) -> Dict[str, Any]:
        """
        Valida la integridad de las relaciones de un cliente.
        
        Args:
            client_id: ID del cliente a validar
            
        Returns:
            Dict[str, Any]: Resultado de la validación con detalles
        """
        pass

    @abstractmethod
    async def get_clients_with_active_assignments(
        self,
        assignment_type: Optional[str] = None
    ) -> List[Client]:
        """
        Obtiene clientes que tienen asignaciones activas.
        
        Args:
            assignment_type: Tipo específico de asignación (None para todos)
            
        Returns:
            List[Client]: Lista de clientes con asignaciones activas
        """
        pass

    @abstractmethod
    async def get_client_dependency_tree(
        self,
        client_id: UUID,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Obtiene el árbol de dependencias de un cliente.
        
        Args:
            client_id: ID del cliente
            max_depth: Profundidad máxima del árbol
            
        Returns:
            Dict[str, Any]: Árbol de dependencias estructurado
        """
        pass
