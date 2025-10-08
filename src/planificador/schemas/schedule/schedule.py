# src/planificador/schemas/schedule/schedule.py

from typing import Optional, List, Dict, Any
from pydantic import Field, model_validator
from datetime import datetime, date, time
from decimal import Decimal

from ..base.base import BaseSchema


class ScheduleBase(BaseSchema):
    """Schema base para Schedule."""

    employee_id: int
    project_id: Optional[int] = None
    team_id: Optional[int] = None
    status_code_id: Optional[int] = None
    date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    is_confirmed: bool = False
    notes: Optional[str] = None

    @model_validator(mode='after')
    def validate_time_range(self):
        """Validar que end_time sea posterior a start_time."""
        if (self.start_time is not None and 
            self.end_time is not None and 
            self.end_time <= self.start_time):
            raise ValueError('La hora de fin debe ser posterior a la hora de inicio')
        return self

    @model_validator(mode='after')
    def validate_project_or_team(self):
        """Validar que se especifique al menos un proyecto o equipo."""
        if not self.project_id and not self.team_id:
            raise ValueError('Debe especificarse al menos un proyecto o equipo para el horario')
        return self

    @model_validator(mode='after')
    def validate_time_consistency(self):
        """Validar que si se especifica una hora, se especifiquen ambas."""
        if (self.start_time is None) != (self.end_time is None):
            raise ValueError('Debe especificarse tanto la hora de inicio como la de fin, o ninguna')
        return self


class ScheduleCreate(ScheduleBase):
    """Schema para crear un Schedule."""

    pass


class ScheduleUpdate(BaseSchema):
    """Schema para actualizar un Schedule."""

    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    team_id: Optional[int] = None
    status_code_id: Optional[int] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    is_confirmed: Optional[bool] = None
    notes: Optional[str] = None


class Schedule(ScheduleBase):
    """Schema de salida para Schedule."""

    id: int
    created_at: datetime
    updated_at: datetime


class ScheduleSearchFilter(BaseSchema):
    """Filtros para búsqueda de horarios."""

    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    team_id: Optional[int] = None
    status_code_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_confirmed: Optional[bool] = None


# ============================================================================
# ESQUEMAS PARA ANÁLISIS DE PRODUCTIVIDAD
# ============================================================================

class ProductivityMetricsSchema(BaseSchema):
    """Esquema para métricas avanzadas de productividad y eficiencia."""
    
    # Período de análisis
    start_date: date
    end_date: date
    
    # Identificadores opcionales
    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    
    # Métricas de tiempo
    total_hours_worked: Decimal
    total_scheduled_hours: Decimal
    utilization_rate: Decimal  # Porcentaje de utilización
    
    # Métricas de eficiencia
    efficiency_score: Decimal  # Puntuación de eficiencia (0-100)
    productivity_index: Decimal  # Índice de productividad
    
    # Análisis de distribución
    peak_hours: List[int]  # Horas del día con mayor productividad
    low_productivity_periods: List[Dict[str, Any]]
    
    # Comparativas
    period_comparison: Dict[str, Any]  # Comparación con período anterior
    benchmark_comparison: Dict[str, Any]  # Comparación con benchmarks
    
    # Recomendaciones
    improvement_suggestions: List[str]
    optimization_opportunities: List[Dict[str, Any]]


class UtilizationReportSchema(BaseSchema):
    """Esquema para reporte de utilización de recursos humanos."""
    
    # Identificación
    entity_id: int  # ID del empleado, equipo o proyecto
    entity_name: str
    entity_type: str  # "employee", "team", "project"
    
    # Período de análisis
    start_date: date
    end_date: date
    
    # Métricas de utilización
    total_available_hours: Decimal
    total_scheduled_hours: Decimal
    total_worked_hours: Decimal
    utilization_percentage: Decimal
    
    # Distribución temporal
    daily_utilization: List[Dict[str, Any]]
    weekly_averages: List[Dict[str, Any]]
    
    # Análisis de capacidad
    capacity_status: str  # "underutilized", "optimal", "overutilized"
    capacity_variance: Decimal  # Diferencia vs capacidad óptima
    
    # Detalles por proyecto/actividad
    activity_breakdown: List[Dict[str, Any]]
    
    # Tendencias
    utilization_trend: str  # "increasing", "decreasing", "stable"
    trend_analysis: Dict[str, Any]


class ScheduleDistributionSchema(BaseSchema):
    """Esquema para análisis de patrones de distribución temporal de horarios."""
    
    # Período de análisis
    start_date: date
    end_date: date
    distribution_type: str  # "daily", "weekly", "monthly"
    
    # Distribución temporal
    time_distribution: Dict[str, Any]  # Distribución por franjas horarias
    day_distribution: Dict[str, Any]  # Distribución por días de la semana
    
    # Patrones identificados
    peak_periods: List[Dict[str, Any]]  # Períodos de mayor actividad
    low_activity_periods: List[Dict[str, Any]]  # Períodos de menor actividad
    
    # Análisis de carga
    workload_balance: Dict[str, Any]  # Balance de carga de trabajo
    resource_conflicts: List[Dict[str, Any]]  # Conflictos de recursos
    
    # Métricas de distribución
    distribution_evenness: Decimal  # Uniformidad de la distribución (0-1)
    concentration_index: Decimal  # Índice de concentración
    
    # Análisis por entidad
    employee_distribution: List[Dict[str, Any]]
    project_distribution: List[Dict[str, Any]]
    team_distribution: List[Dict[str, Any]]
    
    # Recomendaciones de optimización
    optimization_suggestions: List[str]
    redistribution_opportunities: List[Dict[str, Any]]


# ============================================================================
# ESQUEMAS PARA VALIDACIONES Y REGLAS DE NEGOCIO
# ============================================================================

class ValidationResultSchema(BaseSchema):
    """Esquema para resultado de validación de reglas de negocio de horarios."""
    
    is_valid: bool
    validation_errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    business_rules_checked: List[str]
    validation_summary: Dict[str, Any]
    
    # Detalles específicos de horarios
    schedule_data_validated: Dict[str, Any]
    time_constraints_status: Dict[str, Any]
    employee_constraints_status: Dict[str, Any]
    project_constraints_status: Dict[str, Any]
    
    # Recomendaciones
    recommendations: List[str]
    corrective_actions: List[Dict[str, Any]]


class ConflictValidationSchema(BaseSchema):
    """Esquema para validación y detección de conflictos de horarios."""
    
    # Información del horario evaluado
    employee_id: int
    schedule_date: date
    start_time: time
    end_time: time
    
    # Resultado de la validación
    has_conflicts: bool
    conflict_count: int
    
    # Detalles de conflictos encontrados
    conflicts_detected: List[Dict[str, Any]]
    overlapping_schedules: List[Dict[str, Any]]
    
    # Análisis de impacto
    conflict_severity: str  # "low", "medium", "high", "critical"
    impact_analysis: Dict[str, Any]
    
    # Sugerencias de resolución
    resolution_suggestions: List[Dict[str, Any]]
    alternative_time_slots: List[Dict[str, Any]]
    
    # Metadatos
    validation_timestamp: datetime
    excluded_schedule_id: Optional[int] = None


class TeamCoordinationValidationSchema(BaseSchema):
    """Esquema para validación de coordinación de horarios de equipo."""
    
    # Identificación del equipo
    team_id: int
    team_name: str
    target_date: date
    
    # Estado de coordinación
    is_coordinated: bool
    coordination_score: Decimal  # Puntuación de coordinación (0-100)
    
    # Análisis de miembros del equipo
    team_members_analysis: List[Dict[str, Any]]
    availability_matrix: Dict[str, Any]
    
    # Conflictos de coordinación
    coordination_conflicts: List[Dict[str, Any]]
    scheduling_gaps: List[Dict[str, Any]]
    
    # Métricas de colaboración
    overlap_hours: Decimal  # Horas de solapamiento del equipo
    coverage_percentage: Decimal  # Porcentaje de cobertura temporal
    
    # Proyectos colaborativos
    collaborative_projects: List[Dict[str, Any]]
    project_coordination_status: Dict[str, Any]
    
    # Recomendaciones
    coordination_recommendations: List[str]
    optimal_meeting_windows: List[Dict[str, Any]]


class WorkloadValidationSchema(BaseSchema):
    """Esquema para validación de distribución equilibrada de carga de trabajo."""
    
    # Identificación del empleado
    employee_id: int
    employee_name: str
    
    # Período de análisis
    start_date: date
    end_date: date
    
    # Estado de la carga de trabajo
    is_balanced: bool
    workload_status: str  # "underloaded", "balanced", "overloaded", "critical"
    
    # Métricas de carga
    total_scheduled_hours: Decimal
    average_daily_hours: Decimal
    peak_daily_hours: Decimal
    workload_variance: Decimal
    
    # Análisis de sostenibilidad
    sustainability_score: Decimal  # Puntuación de sostenibilidad (0-100)
    burnout_risk_level: str  # "low", "medium", "high", "critical"
    
    # Distribución temporal
    daily_workload_distribution: List[Dict[str, Any]]
    weekly_patterns: Dict[str, Any]
    
    # Comparativas
    team_average_comparison: Dict[str, Any]
    historical_comparison: Dict[str, Any]
    
    # Factores de riesgo
    risk_factors: List[Dict[str, Any]]
    warning_indicators: List[str]
    
    # Recomendaciones de equilibrio
    balancing_recommendations: List[str]
    workload_adjustments: List[Dict[str, Any]]
    rest_period_suggestions: List[Dict[str, Any]]