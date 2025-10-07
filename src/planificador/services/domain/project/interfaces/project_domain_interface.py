# -*- coding: utf-8 -*-
"""
Interfaz principal para el servicio de dominio de proyectos.

Esta interfaz define el contrato completo para todas las operaciones
relacionadas con la gestión de proyectos en el sistema.
Hereda de todas las interfaces específicas para mantener compatibilidad
y proporcionar una interfaz unificada.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from datetime import date

from planificador.models.project import Project
from planificador.schemas.project.create import ProjectCreateSchema
from planificador.schemas.project.update import ProjectUpdateSchema
from planificador.schemas.project.response import (
    ProjectResponseSchema,
    ProjectDetailResponseSchema,
    ProjectListResponseSchema
)
from planificador.schemas.project.query import (
    ProjectQuerySchema,
    ProjectSearchFilters,
    ProjectSortOptions,
    PaginationParams
)
from planificador.schemas.project.statistics import (
    ProjectStatisticsSchema,
    ProjectPerformanceMetrics,
    ProjectWorkloadStats,
    ProjectDurationStats
)
from planificador.schemas.project.validation import (
    ProjectValidationResult,
    ValidationRuleResult,
    BusinessRuleValidation
)
from planificador.schemas.project.diagnostic import (
    ProjectHealthReport,
    ProjectAnomalyReport,
    ProjectPerformanceAnalysis,
    ProjectStatusReport
)
from planificador.schemas.project.date_planning import (
    ProjectDatePlanningSchema,
    DateCalculationResult,
    TimelineFeasibilityReport,
    CalendarAnalysisResult
)
from planificador.schemas.project.relationship import (
    ProjectRelationshipSchema,
    ClientProjectAnalysis,
    EmployeeWorkloadAnalysis,
    TeamProjectDistribution
)
from planificador.schemas.project.advanced_query import (
    AdvancedSearchCriteria,
    ProjectDashboardData,
    ProjectTrendAnalysis,
    WorkloadDistributionAnalysis
)
from planificador.schemas.common.enums import ProjectStatus, ProjectPriority

# Importar todas las interfaces específicas
from .crud_operations_interface import IProjectCrudOperations
from .query_operations_interface import IProjectQueryOperations
from .validation_operations_interface import IProjectValidationOperations
from .advanced_query_operations_interface import IProjectAdvancedQueryOperations
from .relationship_operations_interface import IProjectRelationshipOperations
from .statistics_operations_interface import IProjectStatisticsOperations
from .date_planning_operations_interface import IProjectDatePlanningOperations
from .diagnostic_operations_interface import IProjectDiagnosticOperations


class IProjectDomainService(
    IProjectCrudOperations,
    IProjectQueryOperations,
    IProjectValidationOperations,
    IProjectAdvancedQueryOperations,
    IProjectRelationshipOperations,
    IProjectStatisticsOperations,
    IProjectDatePlanningOperations,
    IProjectDiagnosticOperations,
    ABC
):
    """
    Interfaz principal para el servicio de dominio de proyectos.
    
    Esta interfaz hereda de todas las interfaces específicas de operaciones
    para proporcionar un contrato unificado y completo para la gestión
    avanzada de proyectos. Mantiene compatibilidad con implementaciones
    existentes mientras mejora la modularización del código.
    
    Las operaciones están organizadas en las siguientes categorías:
    - CRUD Operations: Operaciones básicas de creación, lectura, actualización y eliminación
    - Query Operations: Consultas y búsquedas de proyectos
    - Validation Operations: Validaciones de datos y reglas de negocio
    - Advanced Query Operations: Consultas complejas y análisis avanzados
    - Relationship Operations: Gestión de relaciones entre entidades
    - Statistics Operations: Estadísticas y métricas de proyectos
    - Date Planning Operations: Planificación temporal y gestión de fechas
    - Diagnostic Operations: Diagnósticos de salud y detección de anomalías
    """

    # ============================================================================
    # MÉTODOS ADICIONALES DE SERVICIO
    # ============================================================================

    @abstractmethod
    async def service_health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud del servicio de dominio de proyectos.
        
        Realiza una verificación completa del estado del servicio,
        incluyendo conectividad a base de datos, integridad de datos
        y disponibilidad de componentes críticos.
        
        Returns:
            Dict[str, Any]: Reporte de estado del servicio con métricas
            
        Raises:
            ServiceHealthError: Si hay problemas críticos en el servicio
        """
        pass
