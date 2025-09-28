# src/planificador/services/domain/interfaces/client_domain_service_interface.py

"""
Interfaz para el servicio de dominio de clientes.

Este módulo define el contrato que debe cumplir el servicio de dominio de clientes,
especificando todas las operaciones de lógica de negocio disponibles para la gestión
integral de clientes en el sistema.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ....models.client import Client
from ....schemas.client import ClientCreate, ClientUpdate


class IClientDomainService(ABC):
    """
    Interfaz para el servicio de dominio de clientes.
    
    Define el contrato para todas las operaciones de lógica de negocio
    relacionadas con la gestión de clientes, incluyendo operaciones complejas
    que coordinan múltiples repositorios y aplican reglas de negocio específicas.
    """

    # ============================================================================
    # OPERACIONES DE GESTIÓN DE CLIENTES
    # ============================================================================

    @abstractmethod
    async def create_client_with_validation(
        self, 
        client_data: ClientCreate,
        validate_business_rules: bool = True
    ) -> Client:
        """
        Crea un nuevo cliente aplicando validaciones completas y reglas de negocio.
        
        Args:
            client_data: Datos del cliente a crear
            validate_business_rules: Si aplicar validaciones de reglas de negocio
            
        Returns:
            Cliente creado con todas las validaciones aplicadas
            
        Raises:
            ClientDomainError: Si falla la creación por reglas de negocio
            ValidationError: Si los datos no son válidos
        """
        pass

    @abstractmethod
    async def update_client_with_validation(
        self, 
        client_id: int, 
        client_data: ClientUpdate,
        validate_business_rules: bool = True
    ) -> Client:
        """
        Actualiza un cliente existente aplicando validaciones y reglas de negocio.
        
        Args:
            client_id: ID del cliente a actualizar
            client_data: Datos de actualización
            validate_business_rules: Si aplicar validaciones de reglas de negocio
            
        Returns:
            Cliente actualizado
            
        Raises:
            ClientDomainError: Si falla la actualización por reglas de negocio
            ClientNotFoundError: Si el cliente no existe
        """
        pass

    @abstractmethod
    async def delete_client_with_dependencies(
        self, 
        client_id: int,
        force_delete: bool = False
    ) -> bool:
        """
        Elimina un cliente verificando dependencias y aplicando reglas de negocio.
        
        Args:
            client_id: ID del cliente a eliminar
            force_delete: Si forzar eliminación ignorando dependencias
            
        Returns:
            True si se eliminó correctamente
            
        Raises:
            ClientDomainError: Si no se puede eliminar por dependencias
            ClientNotFoundError: Si el cliente no existe
        """
        pass

    # ============================================================================
    # OPERACIONES DE BÚSQUEDA Y CONSULTA AVANZADA
    # ============================================================================

    @abstractmethod
    async def search_clients_advanced(
        self,
        search_criteria: Dict[str, Any],
        include_relationships: bool = False,
        apply_business_filters: bool = True
    ) -> List[Client]:
        """
        Búsqueda avanzada de clientes con criterios complejos y filtros de negocio.
        
        Args:
            search_criteria: Criterios de búsqueda complejos
            include_relationships: Si incluir relaciones cargadas
            apply_business_filters: Si aplicar filtros de lógica de negocio
            
        Returns:
            Lista de clientes que cumplen los criterios
        """
        pass

    @abstractmethod
    async def get_client_with_full_context(
        self, 
        client_id: int
    ) -> Dict[str, Any]:
        """
        Obtiene un cliente con todo su contexto de negocio (proyectos, estadísticas, etc.).
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con cliente y contexto completo
            
        Raises:
            ClientNotFoundError: Si el cliente no existe
        """
        pass

    # ============================================================================
    # OPERACIONES DE GESTIÓN DE PROYECTOS
    # ============================================================================

    @abstractmethod
    async def transfer_client_projects(
        self,
        from_client_id: int,
        to_client_id: int,
        project_ids: Optional[List[int]] = None,
        validate_transfer_rules: bool = True
    ) -> Dict[str, Any]:
        """
        Transfiere proyectos entre clientes aplicando reglas de negocio.
        
        Args:
            from_client_id: ID del cliente origen
            to_client_id: ID del cliente destino
            project_ids: IDs específicos de proyectos (None = todos)
            validate_transfer_rules: Si validar reglas de transferencia
            
        Returns:
            Resultado de la transferencia con estadísticas
            
        Raises:
            ClientDomainError: Si la transferencia viola reglas de negocio
        """
        pass

    @abstractmethod
    async def analyze_client_project_portfolio(
        self, 
        client_id: int
    ) -> Dict[str, Any]:
        """
        Analiza el portafolio de proyectos de un cliente con métricas de negocio.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Análisis completo del portafolio de proyectos
            
        Raises:
            ClientNotFoundError: Si el cliente no existe
        """
        pass

    # ============================================================================
    # OPERACIONES DE ANÁLISIS Y ESTADÍSTICAS
    # ============================================================================

    @abstractmethod
    async def generate_client_business_report(
        self, 
        client_id: int,
        include_trends: bool = True,
        include_comparisons: bool = True
    ) -> Dict[str, Any]:
        """
        Genera un reporte completo de negocio para un cliente específico.
        
        Args:
            client_id: ID del cliente
            include_trends: Si incluir análisis de tendencias
            include_comparisons: Si incluir comparaciones con otros clientes
            
        Returns:
            Reporte completo de negocio del cliente
        """
        pass

    @abstractmethod
    async def analyze_client_performance_metrics(
        self,
        client_ids: Optional[List[int]] = None,
        date_range: Optional[Dict[str, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Analiza métricas de rendimiento de clientes con lógica de negocio.
        
        Args:
            client_ids: IDs de clientes específicos (None = todos)
            date_range: Rango de fechas para el análisis
            
        Returns:
            Análisis de métricas de rendimiento
        """
        pass

    @abstractmethod
    async def get_client_dashboard_metrics(
        self, 
        client_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene métricas consolidadas para dashboard de clientes.
        
        Args:
            client_id: ID de cliente específico (None = métricas generales)
            
        Returns:
            Métricas consolidadas para dashboard
        """
        pass

    # ============================================================================
    # OPERACIONES DE VALIDACIÓN Y REGLAS DE NEGOCIO
    # ============================================================================

    @abstractmethod
    async def validate_client_business_rules(
        self,
        client_data: Dict[str, Any],
        operation_type: str,
        client_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Valida reglas de negocio específicas para operaciones de clientes.
        
        Args:
            client_data: Datos del cliente a validar
            operation_type: Tipo de operación ('create', 'update', 'delete')
            client_id: ID del cliente (para actualizaciones)
            
        Returns:
            Resultado de validación con detalles
            
        Raises:
            ClientDomainError: Si se violan reglas de negocio
        """
        pass

    @abstractmethod
    async def check_client_dependencies(
        self, 
        client_id: int
    ) -> Dict[str, Any]:
        """
        Verifica todas las dependencias de un cliente en el sistema.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Información detallada de dependencias
            
        Raises:
            ClientNotFoundError: Si el cliente no existe
        """
        pass

    # ============================================================================
    # OPERACIONES DE COORDINACIÓN ENTRE DOMINIOS
    # ============================================================================

    @abstractmethod
    async def coordinate_client_lifecycle_event(
        self,
        client_id: int,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordina eventos del ciclo de vida del cliente con otros dominios.
        
        Args:
            client_id: ID del cliente
            event_type: Tipo de evento ('created', 'updated', 'deleted', etc.)
            event_data: Datos del evento
            
        Returns:
            Resultado de la coordinación del evento
        """
        pass

    @abstractmethod
    async def synchronize_client_data_across_domains(
        self, 
        client_id: int
    ) -> Dict[str, Any]:
        """
        Sincroniza datos del cliente a través de múltiples dominios.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Resultado de la sincronización
            
        Raises:
            ClientDomainError: Si falla la sincronización
        """
        pass