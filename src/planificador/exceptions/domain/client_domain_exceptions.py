# src/planificador/exceptions/domain/client_domain_exceptions.py

"""
Excepciones específicas para el dominio de clientes.

Este módulo define excepciones especializadas para operaciones del servicio de dominio
de clientes, incluyendo errores de lógica de negocio, coordinación entre dominios
y validaciones complejas específicas del dominio de clientes.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ..base import BusinessLogicError, ValidationError, NotFoundError, ConflictError


# ============================================================================
# EXCEPCIONES BASE DEL DOMINIO DE CLIENTES
# ============================================================================

class ClientDomainError(BusinessLogicError):
    """
    Excepción base para errores del dominio de clientes.
    
    Se utiliza para errores de lógica de negocio específicos del dominio
    de clientes que no encajan en categorías más específicas.
    """
    
    def __init__(
        self, 
        message: str,
        client_id: Optional[Union[int, str]] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message, 
            rule="client_domain_rule",
            **kwargs
        )
        
        # Agregar contexto específico del dominio de clientes
        if client_id is not None:
            self.add_detail('client_id', str(client_id))
        if operation:
            self.add_detail('domain_operation', operation)
            
        self.client_id = client_id
        self.operation = operation


# ============================================================================
# EXCEPCIONES DE LÓGICA DE NEGOCIO
# ============================================================================

class ClientBusinessRuleViolationError(ClientDomainError):
    """
    Excepción para violaciones de reglas de negocio específicas de clientes.
    
    Se lanza cuando una operación viola reglas de negocio complejas
    del dominio de clientes.
    """
    
    def __init__(
        self,
        rule_name: str,
        rule_description: str,
        client_id: Optional[Union[int, str]] = None,
        violated_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Violación de regla de negocio '{rule_name}': {rule_description}"
        
        super().__init__(
            message,
            client_id=client_id,
            operation="business_rule_validation",
            **kwargs
        )
        
        # Agregar detalles específicos de la regla violada
        self.add_detail('rule_name', rule_name)
        self.add_detail('rule_description', rule_description)
        if violated_data:
            self.add_detail('violated_data', violated_data)
            
        self.rule_name = rule_name
        self.rule_description = rule_description
        self.violated_data = violated_data


class ClientDependencyError(ClientDomainError):
    """
    Excepción para errores relacionados con dependencias de clientes.
    
    Se lanza cuando una operación no puede completarse debido a
    dependencias existentes o faltantes.
    """
    
    def __init__(
        self,
        dependency_type: str,
        dependency_details: Dict[str, Any],
        client_id: Optional[Union[int, str]] = None,
        operation: str = "dependency_check",
        **kwargs
    ):
        message = f"Error de dependencia '{dependency_type}' para cliente"
        if client_id:
            message += f" {client_id}"
            
        super().__init__(
            message,
            client_id=client_id,
            operation=operation,
            **kwargs
        )
        
        # Agregar detalles específicos de la dependencia
        self.add_detail('dependency_type', dependency_type)
        self.add_detail('dependency_details', dependency_details)
        
        self.dependency_type = dependency_type
        self.dependency_details = dependency_details


class ClientProjectTransferError(ClientDomainError):
    """
    Excepción para errores en transferencias de proyectos entre clientes.
    
    Se lanza cuando falla la transferencia de proyectos debido a
    reglas de negocio o restricciones del dominio.
    """
    
    def __init__(
        self,
        from_client_id: Union[int, str],
        to_client_id: Union[int, str],
        project_ids: Optional[List[int]] = None,
        reason: str = "Error en transferencia de proyectos",
        **kwargs
    ):
        message = f"Error transfiriendo proyectos del cliente {from_client_id} al cliente {to_client_id}: {reason}"
        
        super().__init__(
            message,
            operation="project_transfer",
            **kwargs
        )
        
        # Agregar detalles específicos de la transferencia
        self.add_detail('from_client_id', str(from_client_id))
        self.add_detail('to_client_id', str(to_client_id))
        self.add_detail('transfer_reason', reason)
        if project_ids:
            self.add_detail('project_ids', project_ids)
            
        self.from_client_id = from_client_id
        self.to_client_id = to_client_id
        self.project_ids = project_ids
        self.reason = reason


# ============================================================================
# EXCEPCIONES DE COORDINACIÓN ENTRE DOMINIOS
# ============================================================================

class ClientDomainCoordinationError(ClientDomainError):
    """
    Excepción para errores de coordinación entre dominios.
    
    Se lanza cuando falla la coordinación de operaciones entre
    el dominio de clientes y otros dominios del sistema.
    """
    
    def __init__(
        self,
        coordination_type: str,
        target_domain: str,
        client_id: Optional[Union[int, str]] = None,
        coordination_data: Optional[Dict[str, Any]] = None,
        reason: str = "Error en coordinación entre dominios",
        **kwargs
    ):
        message = f"Error de coordinación '{coordination_type}' con dominio '{target_domain}': {reason}"
        
        super().__init__(
            message,
            client_id=client_id,
            operation="domain_coordination",
            **kwargs
        )
        
        # Agregar detalles específicos de la coordinación
        self.add_detail('coordination_type', coordination_type)
        self.add_detail('target_domain', target_domain)
        self.add_detail('coordination_reason', reason)
        if coordination_data:
            self.add_detail('coordination_data', coordination_data)
            
        self.coordination_type = coordination_type
        self.target_domain = target_domain
        self.coordination_data = coordination_data


class ClientDataSynchronizationError(ClientDomainError):
    """
    Excepción para errores de sincronización de datos de clientes.
    
    Se lanza cuando falla la sincronización de datos del cliente
    a través de múltiples dominios o sistemas.
    """
    
    def __init__(
        self,
        synchronization_target: str,
        client_id: Union[int, str],
        sync_data: Optional[Dict[str, Any]] = None,
        reason: str = "Error en sincronización de datos",
        **kwargs
    ):
        message = f"Error sincronizando datos del cliente {client_id} con '{synchronization_target}': {reason}"
        
        super().__init__(
            message,
            client_id=client_id,
            operation="data_synchronization",
            **kwargs
        )
        
        # Agregar detalles específicos de la sincronización
        self.add_detail('synchronization_target', synchronization_target)
        self.add_detail('sync_reason', reason)
        if sync_data:
            self.add_detail('sync_data', sync_data)
            
        self.synchronization_target = synchronization_target
        self.sync_data = sync_data


# ============================================================================
# EXCEPCIONES DE ANÁLISIS Y REPORTES
# ============================================================================

class ClientAnalysisError(ClientDomainError):
    """
    Excepción para errores en análisis de datos de clientes.
    
    Se lanza cuando fallan operaciones de análisis, generación de reportes
    o cálculo de métricas complejas de clientes.
    """
    
    def __init__(
        self,
        analysis_type: str,
        client_id: Optional[Union[int, str]] = None,
        analysis_parameters: Optional[Dict[str, Any]] = None,
        reason: str = "Error en análisis de cliente",
        **kwargs
    ):
        message = f"Error en análisis '{analysis_type}'"
        if client_id:
            message += f" para cliente {client_id}"
        message += f": {reason}"
        
        super().__init__(
            message,
            client_id=client_id,
            operation="client_analysis",
            **kwargs
        )
        
        # Agregar detalles específicos del análisis
        self.add_detail('analysis_type', analysis_type)
        self.add_detail('analysis_reason', reason)
        if analysis_parameters:
            self.add_detail('analysis_parameters', analysis_parameters)
            
        self.analysis_type = analysis_type
        self.analysis_parameters = analysis_parameters


class ClientReportGenerationError(ClientDomainError):
    """
    Excepción para errores en generación de reportes de clientes.
    
    Se lanza cuando falla la generación de reportes de negocio
    o documentos analíticos de clientes.
    """
    
    def __init__(
        self,
        report_type: str,
        client_id: Optional[Union[int, str]] = None,
        report_parameters: Optional[Dict[str, Any]] = None,
        reason: str = "Error en generación de reporte",
        **kwargs
    ):
        message = f"Error generando reporte '{report_type}'"
        if client_id:
            message += f" para cliente {client_id}"
        message += f": {reason}"
        
        super().__init__(
            message,
            client_id=client_id,
            operation="report_generation",
            **kwargs
        )
        
        # Agregar detalles específicos del reporte
        self.add_detail('report_type', report_type)
        self.add_detail('report_reason', reason)
        if report_parameters:
            self.add_detail('report_parameters', report_parameters)
            
        self.report_type = report_type
        self.report_parameters = report_parameters


# ============================================================================
# FUNCIONES HELPER PARA CREAR EXCEPCIONES
# ============================================================================

def create_client_business_rule_violation(
    rule_name: str,
    rule_description: str,
    client_id: Optional[Union[int, str]] = None,
    violated_data: Optional[Dict[str, Any]] = None
) -> ClientBusinessRuleViolationError:
    """
    Crea una excepción de violación de regla de negocio de cliente.
    
    Args:
        rule_name: Nombre de la regla violada
        rule_description: Descripción de la regla
        client_id: ID del cliente afectado
        violated_data: Datos que violaron la regla
        
    Returns:
        Instancia de ClientBusinessRuleViolationError
    """
    return ClientBusinessRuleViolationError(
        rule_name=rule_name,
        rule_description=rule_description,
        client_id=client_id,
        violated_data=violated_data
    )


def create_client_dependency_error(
    dependency_type: str,
    dependency_details: Dict[str, Any],
    client_id: Optional[Union[int, str]] = None,
    operation: str = "dependency_check"
) -> ClientDependencyError:
    """
    Crea una excepción de error de dependencia de cliente.
    
    Args:
        dependency_type: Tipo de dependencia
        dependency_details: Detalles de la dependencia
        client_id: ID del cliente afectado
        operation: Operación que causó el error
        
    Returns:
        Instancia de ClientDependencyError
    """
    return ClientDependencyError(
        dependency_type=dependency_type,
        dependency_details=dependency_details,
        client_id=client_id,
        operation=operation
    )


def create_client_project_transfer_error(
    from_client_id: Union[int, str],
    to_client_id: Union[int, str],
    project_ids: Optional[List[int]] = None,
    reason: str = "Error en transferencia de proyectos"
) -> ClientProjectTransferError:
    """
    Crea una excepción de error de transferencia de proyectos.
    
    Args:
        from_client_id: ID del cliente origen
        to_client_id: ID del cliente destino
        project_ids: IDs de proyectos a transferir
        reason: Razón del error
        
    Returns:
        Instancia de ClientProjectTransferError
    """
    return ClientProjectTransferError(
        from_client_id=from_client_id,
        to_client_id=to_client_id,
        project_ids=project_ids,
        reason=reason
    )


def create_client_analysis_error(
    analysis_type: str,
    client_id: Optional[Union[int, str]] = None,
    analysis_parameters: Optional[Dict[str, Any]] = None,
    reason: str = "Error en análisis de cliente"
) -> ClientAnalysisError:
    """
    Crea una excepción de error de análisis de cliente.
    
    Args:
        analysis_type: Tipo de análisis
        client_id: ID del cliente
        analysis_parameters: Parámetros del análisis
        reason: Razón del error
        
    Returns:
        Instancia de ClientAnalysisError
    """
    return ClientAnalysisError(
        analysis_type=analysis_type,
        client_id=client_id,
        analysis_parameters=analysis_parameters,
        reason=reason
    )