# src/planificador/services/domain/project_assignment/interfaces/validation_operations_interface.py

"""
Interfaz para Operaciones de Validación y Reglas de Negocio

Define el contrato para validaciones complejas, verificación de reglas
de negocio y análisis de integridad de asignaciones de proyecto.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import date

from planificador.schemas import ProjectAssignmentCreate, ProjectAssignmentUpdate


class IValidationOperations(ABC):
    """
    Interfaz para operaciones de validación y reglas de negocio.
    
    Proporciona métodos para validar asignaciones, verificar reglas
    de negocio y mantener la integridad de los datos.
    """
    
    # ============================================================================
    # OPERACIONES DE VALIDACIÓN Y REGLAS DE NEGOCIO (5 métodos)
    # ============================================================================
    
    @abstractmethod
    async def validate_assignment_business_rules(
        self, 
        assignment_data: ProjectAssignmentCreate
    ) -> Dict[str, Any]:
        """
        Valida reglas de negocio complejas para una nueva asignación.
        
        Args:
            assignment_data: Datos de la asignación a validar
            
        Returns:
            Dict con resultado de validación:
            - is_valid: Booleano indicando si la asignación es válida
            - validation_score: Puntuación de validación (0.0-1.0)
            - passed_rules: Lista de reglas que pasaron la validación
            - failed_rules: Lista de reglas que fallaron
            - warnings: Lista de advertencias no críticas
            - errors: Lista de errores críticos
            - business_rule_violations: Violaciones específicas de reglas de negocio
            - recommendations: Recomendaciones para corregir problemas
            - validation_details: Detalles específicos de cada validación
            
        Raises:
            ValidationError: Si los datos de entrada no son válidos
        """
        pass
    
    @abstractmethod
    async def check_workload_constraints(
        self, 
        employee_id: int, 
        new_assignment: ProjectAssignmentCreate
    ) -> Dict[str, Any]:
        """
        Verifica restricciones de carga de trabajo para un empleado.
        
        Args:
            employee_id: ID del empleado
            new_assignment: Nueva asignación propuesta
            
        Returns:
            Dict con análisis de restricciones:
            - employee_id: ID del empleado analizado
            - current_workload: Carga de trabajo actual
            - proposed_additional_load: Carga adicional propuesta
            - total_projected_load: Carga total proyectada
            - workload_limit_exceeded: Booleano si se excede el límite
            - available_capacity: Capacidad disponible
            - workload_percentage: Porcentaje de carga de trabajo
            - constraint_violations: Violaciones de restricciones específicas
            - workload_recommendations: Recomendaciones de carga
            - alternative_allocations: Asignaciones alternativas sugeridas
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def validate_date_consistency(
        self, 
        assignment_data: ProjectAssignmentCreate
    ) -> Dict[str, Any]:
        """
        Valida consistencia temporal y lógica de fechas de asignación.
        
        Args:
            assignment_data: Datos de asignación con fechas a validar
            
        Returns:
            Dict con validación de fechas:
            - dates_are_valid: Booleano de validez general
            - start_date_validation: Validación de fecha de inicio
            - end_date_validation: Validación de fecha de fin
            - date_range_validation: Validación del rango de fechas
            - project_date_alignment: Alineación con fechas del proyecto
            - business_day_validation: Validación de días laborables
            - holiday_conflicts: Conflictos con días festivos
            - weekend_assignments: Asignaciones en fines de semana
            - date_logic_errors: Errores de lógica temporal
            - recommended_date_adjustments: Ajustes recomendados
            
        Raises:
            ValidationError: Si los datos de fecha no son válidos
        """
        pass
    
    @abstractmethod
    async def check_assignment_conflicts(
        self, 
        assignment_data: ProjectAssignmentCreate, 
        exclude_assignment_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Detecta y analiza conflictos potenciales con asignaciones existentes.
        
        Args:
            assignment_data: Datos de la nueva asignación
            exclude_assignment_id: ID de asignación a excluir del análisis
            
        Returns:
            Dict con análisis de conflictos:
            - has_conflicts: Booleano indicando presencia de conflictos
            - conflict_severity: Severidad de conflictos ("low", "medium", "high", "critical")
            - temporal_conflicts: Conflictos de superposición temporal
            - resource_conflicts: Conflictos de recursos/capacidad
            - role_conflicts: Conflictos de roles en el mismo proyecto
            - workload_conflicts: Conflictos de sobrecarga de trabajo
            - project_conflicts: Conflictos entre proyectos
            - conflicting_assignments: Lista de asignaciones en conflicto
            - conflict_resolution_suggestions: Sugerencias de resolución
            - impact_assessment: Evaluación del impacto de los conflictos
            
        Raises:
            ValidationError: Si los datos no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def validate_assignment_update_integrity(
        self, 
        assignment_id: int, 
        update_data: ProjectAssignmentUpdate
    ) -> Dict[str, Any]:
        """
        Valida integridad y consistencia de actualizaciones de asignación.
        
        Args:
            assignment_id: ID de la asignación a actualizar
            update_data: Datos de actualización
            
        Returns:
            Dict con validación de integridad:
            - update_is_valid: Booleano de validez de la actualización
            - integrity_score: Puntuación de integridad (0.0-1.0)
            - field_validations: Validaciones por campo específico
            - consistency_checks: Verificaciones de consistencia
            - business_rule_compliance: Cumplimiento de reglas de negocio
            - impact_analysis: Análisis de impacto de los cambios
            - dependency_validations: Validaciones de dependencias
            - rollback_safety: Seguridad para rollback si es necesario
            - update_recommendations: Recomendaciones para la actualización
            - validation_warnings: Advertencias de validación
            
        Raises:
            ValidationError: Si los datos de actualización no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        pass