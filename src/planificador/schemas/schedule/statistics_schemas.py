# src/planificador/schemas/schedule/statistics_schemas.py

from typing import List, Optional, Dict, Any
from pydantic import Field
from datetime import date, datetime
from decimal import Decimal

from ..base.base import BaseSchema


class EmployeeHoursSummarySchema(BaseSchema):
    """Esquema para resumen de horas trabajadas por empleado."""
    
    employee_id: int
    employee_name: str
    start_date: date
    end_date: date
    total_scheduled_hours: Decimal
    total_worked_hours: Decimal
    regular_hours: Decimal
    overtime_hours: Decimal = Decimal('0.00')
    utilization_rate: Decimal  # Porcentaje de utilización
    efficiency_score: Decimal  # Puntuación de eficiencia (0-100)
    projects_worked: List[Dict[str, Any]] = []
    daily_breakdown: List[Dict[str, Any]] = []


class ProjectHoursSummarySchema(BaseSchema):
    """Esquema para resumen de horas por proyecto."""
    
    project_id: int
    project_name: str
    start_date: date
    end_date: date
    total_scheduled_hours: Decimal
    total_worked_hours: Decimal
    team_members_count: int
    average_hours_per_member: Decimal
    project_progress_percentage: Decimal
    estimated_completion_hours: Optional[Decimal] = None
    employees_breakdown: List[Dict[str, Any]] = []
    timeline_analysis: Dict[str, Any] = {}


class TeamHoursSummarySchema(BaseSchema):
    """Esquema para resumen de horas por equipo."""
    
    team_id: int
    team_name: str
    start_date: date
    end_date: date
    total_team_hours: Decimal
    average_hours_per_member: Decimal
    team_utilization_rate: Decimal
    most_productive_member: Optional[Dict[str, Any]] = None
    least_productive_member: Optional[Dict[str, Any]] = None
    team_projects: List[Dict[str, Any]] = []
    collaboration_metrics: Dict[str, Any] = {}


class OvertimeAnalysisSchema(BaseSchema):
    """Esquema para análisis de horas extras."""
    
    # Período de análisis
    start_date: date
    end_date: date
    
    # Identificadores opcionales
    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    team_id: Optional[int] = None
    
    # Métricas de horas extras
    total_overtime_hours: Decimal
    average_overtime_per_day: Decimal
    overtime_frequency: int  # Días con horas extras
    overtime_percentage: Decimal  # Porcentaje del total de horas
    
    # Análisis de patrones
    peak_overtime_days: List[str] = []  # Días de la semana con más horas extras
    overtime_distribution: Dict[str, Any] = {}  # Distribución por franjas horarias
    
    # Análisis por entidad
    employees_with_overtime: List[Dict[str, Any]] = []
    projects_causing_overtime: List[Dict[str, Any]] = []
    
    # Métricas de impacto
    burnout_risk_indicators: List[Dict[str, Any]] = []
    productivity_impact: Dict[str, Any] = {}
    
    # Comparativas
    period_comparison: Dict[str, Any] = {}  # Comparación con período anterior
    team_comparison: Dict[str, Any] = {}   # Comparación con promedio del equipo
    
    # Recomendaciones
    recommendations: List[str] = []
    workload_adjustments: List[Dict[str, Any]] = []


class ScheduleStatisticsSummarySchema(BaseSchema):
    """Esquema para resumen general de estadísticas de horarios."""
    
    # Período de análisis
    start_date: date
    end_date: date
    
    # Métricas generales
    total_schedules: int
    total_employees_involved: int
    total_projects_involved: int
    total_teams_involved: int
    
    # Métricas de tiempo
    total_scheduled_hours: Decimal
    total_worked_hours: Decimal
    average_daily_hours: Decimal
    peak_activity_day: Optional[str] = None
    
    # Métricas de eficiencia
    overall_utilization_rate: Decimal
    schedule_compliance_rate: Decimal  # Porcentaje de horarios cumplidos
    confirmation_rate: Decimal  # Porcentaje de horarios confirmados
    
    # Distribución
    hours_by_project: List[Dict[str, Any]] = []
    hours_by_employee: List[Dict[str, Any]] = []
    hours_by_team: List[Dict[str, Any]] = []
    
    # Tendencias
    weekly_trends: List[Dict[str, Any]] = []
    monthly_trends: List[Dict[str, Any]] = []
    
    # Alertas y recomendaciones
    performance_alerts: List[Dict[str, Any]] = []
    optimization_opportunities: List[str] = []


class ProductivityTrendsSchema(BaseSchema):
    """Esquema para análisis de tendencias de productividad."""
    
    # Período de análisis
    start_date: date
    end_date: date
    analysis_granularity: str = "weekly"  # "daily", "weekly", "monthly"
    
    # Identificadores opcionales
    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    team_id: Optional[int] = None
    
    # Datos de tendencia
    trend_data_points: List[Dict[str, Any]] = []
    trend_direction: str = "stable"  # "increasing", "decreasing", "stable", "volatile"
    trend_strength: Decimal = Decimal('0.00')  # Fuerza de la tendencia (0-1)
    
    # Análisis estadístico
    correlation_factors: Dict[str, Any] = {}
    seasonal_patterns: List[Dict[str, Any]] = []
    anomalies_detected: List[Dict[str, Any]] = []
    
    # Predicciones
    forecast_next_period: Dict[str, Any] = {}
    confidence_interval: Dict[str, Any] = {}
    
    # Factores influyentes
    external_factors: List[Dict[str, Any]] = []
    internal_factors: List[Dict[str, Any]] = []
    
    # Recomendaciones estratégicas
    strategic_recommendations: List[str] = []
    action_items: List[Dict[str, Any]] = []