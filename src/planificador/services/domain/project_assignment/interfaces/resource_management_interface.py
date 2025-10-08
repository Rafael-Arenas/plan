# src/planificador/services/domain/project_assignment/interfaces/resource_management_interface.py

"""
Interfaz para Gestión de Recursos de Asignaciones de Proyecto

Define el contrato para operaciones de gestión de recursos,
incluyendo capacidades, optimización y balanceado de cargas.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date

from planificador.schemas import ProjectAssignment


class IResourceManagement(ABC):
    """
    Interfaz para gestión de recursos en asignaciones de proyecto.
    
    Proporciona métodos para optimizar la distribución de recursos,
    gestionar capacidades y balancear cargas de trabajo.
    """
    
    # ============================================================================
    # OPERACIONES DE GESTIÓN DE RECURSOS (3 métodos)
    # ============================================================================
    
    @abstractmethod
    async def optimize_resource_allocation(
        self, 
        project_id: int, 
        optimization_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimiza la asignación de recursos para un proyecto específico.
        
        Args:
            project_id: ID del proyecto a optimizar
            optimization_criteria: Criterios de optimización que pueden incluir:
                - target_utilization: Utilización objetivo (0.0-1.0)
                - balance_workload: Balancear carga entre empleados
                - minimize_conflicts: Minimizar conflictos de horarios
                - prioritize_skills: Priorizar asignación por habilidades
                - max_allocation_per_employee: Máxima asignación por empleado
                - preferred_team_size: Tamaño preferido del equipo
                
        Returns:
            Dict con recomendaciones de optimización:
            - project_id: ID del proyecto
            - current_allocation: Asignación actual de recursos
            - optimized_allocation: Asignación optimizada propuesta
            - optimization_score: Puntuación de mejora (0.0-1.0)
            - recommendations: Lista de recomendaciones específicas
            - resource_adjustments: Ajustes sugeridos por empleado
            - expected_benefits: Beneficios esperados de la optimización
            - implementation_complexity: Complejidad de implementación
            
        Raises:
            ValidationError: Si los criterios de optimización no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def calculate_team_capacity(
        self, 
        employee_ids: List[int], 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """
        Calcula la capacidad disponible de un equipo en un período.
        
        Args:
            employee_ids: Lista de IDs de empleados del equipo
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict con análisis de capacidad:
            - team_size: Número de miembros del equipo
            - period_days: Días en el período analizado
            - total_theoretical_capacity: Capacidad teórica total (horas)
            - current_allocation: Asignación actual total (horas)
            - available_capacity: Capacidad disponible (horas)
            - utilization_rate: Tasa de utilización actual (0.0-1.0)
            - capacity_by_employee: Capacidad detallada por empleado
            - peak_utilization_periods: Períodos de mayor utilización
            - underutilized_periods: Períodos de baja utilización
            - capacity_recommendations: Recomendaciones de capacidad
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def balance_workload_across_team(
        self, 
        project_id: int, 
        target_balance_score: float = 0.8
    ) -> Dict[str, Any]:
        """
        Analiza y propone balanceado de carga de trabajo en el equipo.
        
        Args:
            project_id: ID del proyecto a balancear
            target_balance_score: Puntuación objetivo de balance (0.0-1.0)
            
        Returns:
            Dict con análisis de balanceado:
            - project_id: ID del proyecto
            - current_balance_score: Puntuación actual de balance (0.0-1.0)
            - target_balance_score: Puntuación objetivo
            - workload_distribution: Distribución actual de carga por empleado
            - imbalance_indicators: Indicadores de desbalance
            - rebalancing_suggestions: Sugerencias de rebalanceado
            - workload_adjustments: Ajustes específicos por empleado
            - expected_balance_improvement: Mejora esperada en balance
            - implementation_steps: Pasos para implementar el balanceado
            - risk_assessment: Evaluación de riesgos del rebalanceado
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en la consulta
        """
        pass