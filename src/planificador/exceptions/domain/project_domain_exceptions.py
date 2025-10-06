# src/planificador/exceptions/domain/project_domain_exceptions.py

"""
Excepciones específicas para el dominio de proyectos.

Este módulo define excepciones especializadas para operaciones del servicio de dominio
de proyectos, incluyendo errores de lógica de negocio, validaciones de fechas,
códigos duplicados, asignaciones y coordinación entre dominios específicas del
dominio de proyectos.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
import pendulum

from ..base import BusinessLogicError, ValidationError, NotFoundError, ConflictError


# ============================================================================
# EXCEPCIONES BASE DEL DOMINIO DE PROYECTOS
# ============================================================================

class ProjectDomainError(BusinessLogicError):
    """
    Excepción base para errores del dominio de proyectos.
    
    Se utiliza para errores de lógica de negocio específicos del dominio
    de proyectos que no encajan en categorías más específicas.
    """
    
    def __init__(
        self, 
        message: str,
        project_id: Optional[Union[int, str]] = None,
        project_code: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message, 
            rule="project_domain_rule",
            **kwargs
        )
        
        # Agregar contexto específico del dominio de proyectos
        if project_id is not None:
            self.add_detail('project_id', str(project_id))
        if project_code:
            self.add_detail('project_code', project_code)
        if operation:
            self.add_detail('domain_operation', operation)
            
        self.project_id = project_id
        self.project_code = project_code
        self.operation = operation


# ============================================================================
# EXCEPCIONES DE VALIDACIÓN DE PROYECTOS
# ============================================================================

class ProjectValidationError(ProjectDomainError):
    """
    Excepción para errores de validación específicos de proyectos.
    
    Se lanza cuando los datos del proyecto no cumplen con las reglas
    de validación del dominio.
    """
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        validation_rule: Optional[str] = None,
        project_id: Optional[Union[int, str]] = None,
        project_code: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            project_id=project_id,
            project_code=project_code,
            operation="project_validation",
            **kwargs
        )
        
        # Agregar detalles específicos de validación
        if field_name:
            self.add_detail('field_name', field_name)
        if field_value is not None:
            self.add_detail('field_value', str(field_value))
        if validation_rule:
            self.add_detail('validation_rule', validation_rule)
            
        self.field_name = field_name
        self.field_value = field_value
        self.validation_rule = validation_rule


class ProjectDateValidationError(ProjectValidationError):
    """
    Excepción para errores de validación de fechas en proyectos.
    
    Se lanza cuando las fechas del proyecto no cumplen con las reglas
    de negocio (fechas de inicio/fin, duraciones, etc.).
    """
    
    def __init__(
        self,
        message: str,
        start_date: Optional[Union[datetime, date, pendulum.DateTime]] = None,
        end_date: Optional[Union[datetime, date, pendulum.DateTime]] = None,
        duration_days: Optional[int] = None,
        max_duration_days: Optional[int] = None,
        project_id: Optional[Union[int, str]] = None,
        project_code: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            field_name="project_dates",
            validation_rule="date_validation",
            project_id=project_id,
            project_code=project_code,
            **kwargs
        )
        
        # Agregar detalles específicos de fechas
        if start_date:
            self.add_detail('start_date', str(start_date))
        if end_date:
            self.add_detail('end_date', str(end_date))
        if duration_days is not None:
            self.add_detail('duration_days', duration_days)
        if max_duration_days is not None:
            self.add_detail('max_duration_days', max_duration_days)
            
        self.start_date = start_date
        self.end_date = end_date
        self.duration_days = duration_days
        self.max_duration_days = max_duration_days


class ProjectCodeDuplicateError(ConflictError):
    """
    Excepción para códigos de proyecto duplicados.
    
    Se lanza cuando se intenta crear o actualizar un proyecto con un
    código que ya existe en el sistema.
    """
    
    def __init__(
        self,
        project_code: str,
        existing_project_id: Optional[Union[int, str]] = None,
        client_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        message = f"El código de proyecto '{project_code}' ya existe"
        if client_id:
            message += f" para el cliente {client_id}"
            
        super().__init__(
            message,
            resource_type="project_code",
            resource_id=project_code,
            **kwargs
        )
        
        # Agregar detalles específicos del código duplicado
        self.add_detail('project_code', project_code)
        if existing_project_id:
            self.add_detail('existing_project_id', str(existing_project_id))
        if client_id:
            self.add_detail('client_id', str(client_id))
            
        self.project_code = project_code
        self.existing_project_id = existing_project_id
        self.client_id = client_id


class ProjectTrigramDuplicateError(ConflictError):
    """
    Excepción para trigramas de proyecto duplicados.
    
    Se lanza cuando se intenta crear o actualizar un proyecto con un
    trigrama que ya existe en el sistema.
    """
    
    def __init__(
        self,
        trigram: str,
        existing_project_id: Optional[Union[int, str]] = None,
        project_code: Optional[str] = None,
        **kwargs
    ):
        message = f"El trigrama '{trigram}' ya existe"
        if project_code:
            message += f" (código: {project_code})"
            
        super().__init__(
            message,
            resource_type="project_trigram",
            resource_id=trigram,
            **kwargs
        )
        
        # Agregar detalles específicos del trigrama duplicado
        self.add_detail('trigram', trigram)
        if existing_project_id:
            self.add_detail('existing_project_id', str(existing_project_id))
        if project_code:
            self.add_detail('project_code', project_code)
            
        self.trigram = trigram
        self.existing_project_id = existing_project_id
        self.project_code = project_code


# ============================================================================
# EXCEPCIONES DE LÓGICA DE NEGOCIO
# ============================================================================

class ProjectBusinessRuleViolationError(ProjectDomainError):
    """
    Excepción para violaciones de reglas de negocio específicas de proyectos.
    
    Se lanza cuando una operación viola reglas de negocio complejas
    del dominio de proyectos.
    """
    
    def __init__(
        self,
        rule_name: str,
        rule_description: str,
        project_id: Optional[Union[int, str]] = None,
        project_code: Optional[str] = None,
        violated_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Violación de regla de negocio '{rule_name}': {rule_description}"
        
        super().__init__(
            message,
            project_id=project_id,
            project_code=project_code,
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


class ProjectStatusTransitionError(ProjectDomainError):
    """
    Excepción para transiciones de estado inválidas en proyectos.
    
    Se lanza cuando se intenta cambiar el estado de un proyecto
    a un estado no permitido según las reglas de negocio.
    """
    
    def __init__(
        self,
        current_status: str,
        target_status: str,
        project_id: Optional[Union[int, str]] = None,
        project_code: Optional[str] = None,
        allowed_transitions: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Transición de estado inválida de '{current_status}' a '{target_status}'"
        if allowed_transitions:
            message += f". Transiciones permitidas: {', '.join(allowed_transitions)}"
            
        super().__init__(
            message,
            project_id=project_id,
            project_code=project_code,
            operation="status_transition",
            **kwargs
        )
        
        # Agregar detalles específicos de la transición
        self.add_detail('current_status', current_status)
        self.add_detail('target_status', target_status)
        if allowed_transitions:
            self.add_detail('allowed_transitions', allowed_transitions)
            
        self.current_status = current_status
        self.target_status = target_status
        self.allowed_transitions = allowed_transitions


# ============================================================================
# EXCEPCIONES DE ASIGNACIONES Y RELACIONES
# ============================================================================

class ProjectAssignmentError(ProjectDomainError):
    """
    Excepción para errores en asignaciones de empleados a proyectos.
    
    Se lanza cuando hay problemas con la asignación, desasignación
    o gestión de empleados en proyectos.
    """
    
    def __init__(
        self,
        message: str,
        project_id: Optional[Union[int, str]] = None,
        project_code: Optional[str] = None,
        employee_id: Optional[Union[int, str]] = None,
        employee_name: Optional[str] = None,
        assignment_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            project_id=project_id,
            project_code=project_code,
            operation="project_assignment",
            **kwargs
        )
        
        # Agregar detalles específicos de la asignación
        if employee_id:
            self.add_detail('employee_id', str(employee_id))
        if employee_name:
            self.add_detail('employee_name', employee_name)
        if assignment_type:
            self.add_detail('assignment_type', assignment_type)
            
        self.employee_id = employee_id
        self.employee_name = employee_name
        self.assignment_type = assignment_type


class ProjectCapacityExceededError(ProjectAssignmentError):
    """
    Excepción para cuando se excede la capacidad de un proyecto.
    
    Se lanza cuando se intenta asignar más empleados de los permitidos
    o cuando la carga de trabajo excede los límites establecidos.
    """
    
    def __init__(
        self,
        project_id: Union[int, str],
        project_code: Optional[str] = None,
        current_capacity: Optional[int] = None,
        max_capacity: Optional[int] = None,
        attempted_assignment: Optional[str] = None,
        **kwargs
    ):
        message = f"Capacidad del proyecto excedida"
        if current_capacity is not None and max_capacity is not None:
            message += f" ({current_capacity}/{max_capacity})"
            
        super().__init__(
            message,
            project_id=project_id,
            project_code=project_code,
            assignment_type="capacity_check",
            **kwargs
        )
        
        # Agregar detalles específicos de capacidad
        if current_capacity is not None:
            self.add_detail('current_capacity', current_capacity)
        if max_capacity is not None:
            self.add_detail('max_capacity', max_capacity)
        if attempted_assignment:
            self.add_detail('attempted_assignment', attempted_assignment)
            
        self.current_capacity = current_capacity
        self.max_capacity = max_capacity
        self.attempted_assignment = attempted_assignment


class ProjectClientRelationshipError(ProjectDomainError):
    """
    Excepción para errores relacionados con la relación proyecto-cliente.
    
    Se lanza cuando hay problemas con la asignación de proyectos a clientes
    o cuando se violan reglas de negocio relacionadas con esta relación.
    """
    
    def __init__(
        self,
        message: str,
        project_id: Optional[Union[int, str]] = None,
        project_code: Optional[str] = None,
        client_id: Optional[Union[int, str]] = None,
        client_name: Optional[str] = None,
        relationship_issue: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            project_id=project_id,
            project_code=project_code,
            operation="client_relationship",
            **kwargs
        )
        
        # Agregar detalles específicos de la relación cliente
        if client_id:
            self.add_detail('client_id', str(client_id))
        if client_name:
            self.add_detail('client_name', client_name)
        if relationship_issue:
            self.add_detail('relationship_issue', relationship_issue)
            
        self.client_id = client_id
        self.client_name = client_name
        self.relationship_issue = relationship_issue


# ============================================================================
# EXCEPCIONES DE OPERACIONES MASIVAS
# ============================================================================

class ProjectBulkOperationError(ProjectDomainError):
    """
    Excepción para errores en operaciones masivas de proyectos.
    
    Se lanza cuando fallan operaciones que afectan múltiples proyectos
    como actualizaciones masivas, clonaciones o archivado.
    """
    
    def __init__(
        self,
        operation_type: str,
        failed_projects: List[Union[int, str]],
        successful_projects: Optional[List[Union[int, str]]] = None,
        error_details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        total_failed = len(failed_projects)
        total_successful = len(successful_projects) if successful_projects else 0
        
        message = f"Operación masiva '{operation_type}' falló para {total_failed} proyecto(s)"
        if total_successful > 0:
            message += f" ({total_successful} exitosos)"
            
        super().__init__(
            message,
            operation=f"bulk_{operation_type}",
            **kwargs
        )
        
        # Agregar detalles específicos de la operación masiva
        self.add_detail('operation_type', operation_type)
        self.add_detail('failed_projects', [str(p) for p in failed_projects])
        if successful_projects:
            self.add_detail('successful_projects', [str(p) for p in successful_projects])
        if error_details:
            self.add_detail('error_details', error_details)
            
        self.operation_type = operation_type
        self.failed_projects = failed_projects
        self.successful_projects = successful_projects
        self.error_details = error_details


class ProjectCloneError(ProjectDomainError):
    """
    Excepción para errores en la clonación de proyectos.
    
    Se lanza cuando falla la clonación de un proyecto debido a
    restricciones de negocio o problemas técnicos.
    """
    
    def __init__(
        self,
        source_project_id: Union[int, str],
        source_project_code: Optional[str] = None,
        target_project_code: Optional[str] = None,
        clone_reason: str = "Error en clonación de proyecto",
        clone_options: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Error clonando proyecto {source_project_id}"
        if source_project_code:
            message += f" ({source_project_code})"
        if target_project_code:
            message += f" hacia {target_project_code}"
        message += f": {clone_reason}"
        
        super().__init__(
            message,
            project_id=source_project_id,
            project_code=source_project_code,
            operation="project_clone",
            **kwargs
        )
        
        # Agregar detalles específicos de la clonación
        self.add_detail('source_project_id', str(source_project_id))
        if source_project_code:
            self.add_detail('source_project_code', source_project_code)
        if target_project_code:
            self.add_detail('target_project_code', target_project_code)
        if clone_options:
            self.add_detail('clone_options', clone_options)
            
        self.source_project_id = source_project_id
        self.source_project_code = source_project_code
        self.target_project_code = target_project_code
        self.clone_reason = clone_reason
        self.clone_options = clone_options


# ============================================================================
# EXCEPCIONES DE ESTADÍSTICAS Y ANÁLISIS
# ============================================================================

class ProjectStatisticsError(ProjectDomainError):
    """
    Excepción para errores en cálculos de estadísticas de proyectos.
    
    Se lanza cuando fallan los cálculos de métricas, estadísticas
    o análisis de proyectos.
    """
    
    def __init__(
        self,
        statistic_type: str,
        calculation_error: str,
        project_ids: Optional[List[Union[int, str]]] = None,
        date_range: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Error calculando estadística '{statistic_type}': {calculation_error}"
        
        super().__init__(
            message,
            operation=f"calculate_{statistic_type}",
            **kwargs
        )
        
        # Agregar detalles específicos de estadísticas
        self.add_detail('statistic_type', statistic_type)
        self.add_detail('calculation_error', calculation_error)
        if project_ids:
            self.add_detail('project_ids', [str(p) for p in project_ids])
        if date_range:
            self.add_detail('date_range', date_range)
            
        self.statistic_type = statistic_type
        self.calculation_error = calculation_error
        self.project_ids = project_ids
        self.date_range = date_range


# ============================================================================
# EXCEPCIONES DE PLANIFICACIÓN Y CRONOGRAMAS
# ============================================================================

class ProjectPlanningError(ProjectDomainError):
    """
    Excepción para errores en planificación y cronogramas de proyectos.
    
    Se lanza cuando hay problemas con la planificación temporal,
    cálculos de duración o análisis de cronogramas.
    """
    
    def __init__(
        self,
        planning_issue: str,
        project_id: Optional[Union[int, str]] = None,
        project_code: Optional[str] = None,
        timeline_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Error en planificación de proyecto: {planning_issue}"
        
        super().__init__(
            message,
            project_id=project_id,
            project_code=project_code,
            operation="project_planning",
            **kwargs
        )
        
        # Agregar detalles específicos de planificación
        self.add_detail('planning_issue', planning_issue)
        if timeline_data:
            self.add_detail('timeline_data', timeline_data)
            
        self.planning_issue = planning_issue
        self.timeline_data = timeline_data


class ProjectTimelineConflictError(ProjectPlanningError):
    """
    Excepción para conflictos en cronogramas de proyectos.
    
    Se lanza cuando hay solapamientos o conflictos en las fechas
    de proyectos que no pueden resolverse automáticamente.
    """
    
    def __init__(
        self,
        conflicting_projects: List[Dict[str, Any]],
        conflict_type: str = "timeline_overlap",
        resolution_suggestions: Optional[List[str]] = None,
        **kwargs
    ):
        project_codes = [p.get('code', p.get('id', 'N/A')) for p in conflicting_projects]
        message = f"Conflicto de cronograma entre proyectos: {', '.join(map(str, project_codes))}"
        
        super().__init__(
            planning_issue=f"Conflicto de tipo '{conflict_type}'",
            **kwargs
        )
        
        # Agregar detalles específicos del conflicto
        self.add_detail('conflict_type', conflict_type)
        self.add_detail('conflicting_projects', conflicting_projects)
        if resolution_suggestions:
            self.add_detail('resolution_suggestions', resolution_suggestions)
            
        self.conflicting_projects = conflicting_projects
        self.conflict_type = conflict_type
        self.resolution_suggestions = resolution_suggestions


# ============================================================================
# FUNCIONES DE UTILIDAD PARA CREACIÓN DE EXCEPCIONES
# ============================================================================

def create_project_not_found_error(
    project_id: Union[int, str],
    search_criteria: Optional[Dict[str, Any]] = None
) -> NotFoundError:
    """
    Crea una excepción NotFoundError específica para proyectos.
    
    Args:
        project_id: ID del proyecto no encontrado
        search_criteria: Criterios de búsqueda utilizados
        
    Returns:
        NotFoundError: Excepción configurada para proyecto no encontrado
    """
    message = f"Proyecto {project_id} no encontrado"
    
    error = NotFoundError(
        message=message,
        resource_type="Project",
        resource_id=str(project_id)
    )
    
    if search_criteria:
        error.add_detail('search_criteria', search_criteria)
    
    return error


def create_project_validation_error(
    field_name: str,
    field_value: Any,
    validation_message: str,
    project_id: Optional[Union[int, str]] = None,
    project_code: Optional[str] = None
) -> ProjectValidationError:
    """
    Crea una excepción de validación específica para proyectos.
    
    Args:
        field_name: Nombre del campo que falló la validación
        field_value: Valor que causó el error
        validation_message: Mensaje descriptivo del error
        project_id: ID del proyecto (opcional)
        project_code: Código del proyecto (opcional)
        
    Returns:
        ProjectValidationError: Excepción de validación configurada
    """
    return ProjectValidationError(
        message=validation_message,
        field_name=field_name,
        field_value=field_value,
        project_id=project_id,
        project_code=project_code
    )


def create_project_business_rule_error(
    rule_name: str,
    rule_description: str,
    project_id: Optional[Union[int, str]] = None,
    project_code: Optional[str] = None,
    violated_data: Optional[Dict[str, Any]] = None
) -> ProjectBusinessRuleViolationError:
    """
    Crea una excepción de violación de regla de negocio para proyectos.
    
    Args:
        rule_name: Nombre de la regla violada
        rule_description: Descripción de la regla
        project_id: ID del proyecto (opcional)
        project_code: Código del proyecto (opcional)
        violated_data: Datos que violaron la regla (opcional)
        
    Returns:
        ProjectBusinessRuleViolationError: Excepción de regla de negocio configurada
    """
    return ProjectBusinessRuleViolationError(
        rule_name=rule_name,
        rule_description=rule_description,
        project_id=project_id,
        project_code=project_code,
        violated_data=violated_data
    )