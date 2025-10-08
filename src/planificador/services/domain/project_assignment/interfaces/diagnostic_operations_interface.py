# src/planificador/services/domain/project_assignment/interfaces/diagnostic_operations_interface.py

"""
Interfaz para Operaciones de Diagnóstico del Sistema

Define el contrato para operaciones de diagnóstico, monitoreo
de salud y análisis de integridad del sistema de asignaciones.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IDiagnosticOperations(ABC):
    """
    Interfaz para operaciones de diagnóstico del sistema de asignaciones.
    
    Proporciona métodos para monitorear la salud del sistema,
    diagnosticar problemas y verificar la integridad de los datos.
    """
    
    # ============================================================================
    # OPERACIONES DE DIAGNÓSTICO (2 métodos)
    # ============================================================================
    
    @abstractmethod
    async def get_system_health_status(self) -> Dict[str, Any]:
        """
        Diagnóstico completo de salud del sistema de asignaciones.
        
        Returns:
            Dict con estado de salud del sistema:
            - overall_health_score: Puntuación general de salud (0.0-1.0)
            - system_status: Estado general ("healthy", "warning", "critical", "error")
            - component_health: Salud de componentes individuales
            - data_integrity_score: Puntuación de integridad de datos
            - performance_metrics: Métricas de rendimiento del sistema
            - active_assignments_health: Salud de asignaciones activas
            - repository_connectivity: Estado de conectividad con repositorios
            - validation_system_status: Estado del sistema de validación
            - error_rates: Tasas de error por componente
            - system_load_indicators: Indicadores de carga del sistema
            - health_trends: Tendencias de salud a lo largo del tiempo
            - critical_issues: Problemas críticos identificados
            - warnings: Advertencias del sistema
            - recommendations: Recomendaciones de mantenimiento
            
        Raises:
            RepositoryError: Si hay errores críticos en el diagnóstico
        """
        pass
    
    @abstractmethod
    async def run_data_integrity_audit(self) -> Dict[str, Any]:
        """
        Auditoría completa de integridad de datos de asignaciones.
        
        Returns:
            Dict con resultado de auditoría:
            - audit_timestamp: Timestamp de la auditoría
            - overall_integrity_score: Puntuación general de integridad (0.0-1.0)
            - audit_status: Estado de la auditoría ("passed", "warning", "failed")
            - total_assignments_audited: Total de asignaciones auditadas
            - integrity_checks_performed: Verificaciones realizadas
            - data_consistency_results: Resultados de consistencia de datos
            - referential_integrity_status: Estado de integridad referencial
            - business_rule_compliance: Cumplimiento de reglas de negocio
            - orphaned_records: Registros huérfanos detectados
            - duplicate_assignments: Asignaciones duplicadas encontradas
            - invalid_date_ranges: Rangos de fechas inválidos
            - constraint_violations: Violaciones de restricciones
            - data_quality_metrics: Métricas de calidad de datos
            - corruption_indicators: Indicadores de corrupción de datos
            - repair_recommendations: Recomendaciones de reparación
            - cleanup_suggestions: Sugerencias de limpieza
            - audit_details: Detalles específicos de la auditoría
            
        Raises:
            RepositoryError: Si hay errores durante la auditoría
        """
        pass