# -*- coding: utf-8 -*-
"""
Esquemas avanzados para el dominio de equipos.

Este módulo contiene esquemas Pydantic especializados para operaciones avanzadas
del servicio de dominio de equipos, incluyendo búsquedas complejas, análisis de
productividad, métricas de colaboración y validaciones de reglas de negocio.
"""

from typing import List, Optional, Dict, Any, Union, Generic, TypeVar
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import pendulum
from pydantic import Field, field_validator, model_validator

from ..base.base import BaseSchema
from ..common_schemas import DateRangeSchema, PaginationSchema
from ...models.team_membership import MembershipRole
from .enums import TeamStatus

# Definir TypeVar para el tipo genérico
T = TypeVar('T')


# ==========================================
# ENUMS Y TIPOS AUXILIARES
# ==========================================

class MetricType(str, Enum):
    """Tipos de métricas de rendimiento."""
    EFFICIENCY = "efficiency"
    PRODUCTIVITY = "productivity"
    COLLABORATION = "collaboration"
    QUALITY = "quality"
    DELIVERY = "delivery"
    INNOVATION = "innovation"


class CollaborationType(str, Enum):
    """Tipos de colaboración entre equipos."""
    CROSS_FUNCTIONAL = "cross_functional"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    RESOURCE_SHARING = "resource_sharing"
    PROJECT_COLLABORATION = "project_collaboration"
    MENTORING = "mentoring"


class ValidationRuleType(str, Enum):
    """Tipos de reglas de validación."""
    DATA_INTEGRITY = "data_integrity"
    BUSINESS_RULES = "business_rules"
    CAPACITY_LIMITS = "capacity_limits"
    ROLE_PERMISSIONS = "role_permissions"
    COMPLIANCE = "compliance"


class ReportFormat(str, Enum):
    """Formatos de reporte disponibles."""
    SUMMARY = "summary"
    DETAILED = "detailed"
    EXECUTIVE = "executive"
    TECHNICAL = "technical"


class ExportFormat(str, Enum):
    """Formatos de exportación disponibles."""
    JSON = "json"
    EXCEL = "excel"
    PDF = "pdf"
    CSV = "csv"


# ==========================================
# ESQUEMAS DE BÚSQUEDA Y FILTROS
# ==========================================

class TeamSearchCriteria(BaseSchema):
    """Criterios avanzados para búsqueda de equipos."""
    
    name_pattern: Optional[str] = Field(None, description="Patrón de nombre a buscar")
    status: Optional[TeamStatus] = Field(None, description="Estado del equipo")
    department_id: Optional[int] = Field(None, description="ID del departamento")
    leader_id: Optional[int] = Field(None, description="ID del líder del equipo")
    project_id: Optional[int] = Field(None, description="ID del proyecto asignado")
    min_members: Optional[int] = Field(None, ge=0, description="Número mínimo de miembros")
    max_members: Optional[int] = Field(None, ge=1, description="Número máximo de miembros")
    required_skills: Optional[List[str]] = Field(None, description="Habilidades requeridas")
    creation_date_range: Optional[DateRangeSchema] = Field(None, description="Rango de fechas de creación")
    is_active: Optional[bool] = Field(None, description="Estado activo/inactivo")
    has_projects: Optional[bool] = Field(None, description="Tiene proyectos asignados")
    
    @field_validator('max_members')
    @classmethod
    def validate_max_members(cls, v: Optional[int], info) -> Optional[int]:
        """Valida que max_members sea mayor que min_members."""
        if v is not None and hasattr(info.data, 'min_members') and info.data.get('min_members') is not None:
            if v < info.data['min_members']:
                raise ValueError("max_members debe ser mayor o igual que min_members")
        return v


class DateRange(BaseSchema):
    """Rango de fechas con validaciones específicas."""
    
    start_date: pendulum.DateTime = Field(..., description="Fecha de inicio")
    end_date: pendulum.DateTime = Field(..., description="Fecha de fin")
    
    @model_validator(mode='after')
    def validate_date_range(self) -> 'DateRange':
        """Valida que el rango de fechas sea coherente."""
        if self.end_date <= self.start_date:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio")
        
        # Validar que el rango no sea excesivamente largo (más de 5 años)
        if (self.end_date - self.start_date).days > 1825:  # 5 años
            raise ValueError("El rango de fechas no puede ser mayor a 5 años")
        
        return self


# ==========================================
# ESQUEMAS DE RESPUESTA PAGINADA
# ==========================================

class PaginatedResponse(BaseSchema, Generic[T]):
    """Respuesta paginada genérica."""
    
    items: List[T] = Field(default_factory=list, description="Elementos de la página actual")
    total: int = Field(..., ge=0, description="Total de elementos")
    page: int = Field(..., ge=1, description="Página actual")
    page_size: int = Field(..., ge=1, le=1000, description="Elementos por página")
    pages: int = Field(..., ge=0, description="Total de páginas")
    has_next: bool = Field(..., description="Tiene página siguiente")
    has_prev: bool = Field(..., description="Tiene página anterior")
    
    @model_validator(mode='after')
    def validate_pagination(self) -> 'PaginatedResponse':
        """Valida la consistencia de los datos de paginación."""
        # Calcular páginas totales
        calculated_pages = (self.total + self.page_size - 1) // self.page_size if self.total > 0 else 0
        
        if self.pages != calculated_pages:
            self.pages = calculated_pages
        
        # Validar has_next y has_prev
        self.has_next = self.page < self.pages
        self.has_prev = self.page > 1
        
        # Validar que la página actual no exceda el total
        if self.page > self.pages and self.pages > 0:
            raise ValueError(f"La página {self.page} excede el total de páginas {self.pages}")
        
        return self


# ==========================================
# ESQUEMAS DE MÉTRICAS Y ANÁLISIS
# ==========================================

class TeamPerformanceMetrics(BaseSchema):
    """Métricas de rendimiento de un equipo."""
    
    team_id: int = Field(..., description="ID del equipo")
    team_name: str = Field(..., description="Nombre del equipo")
    period_start: pendulum.DateTime = Field(..., description="Inicio del período de análisis")
    period_end: pendulum.DateTime = Field(..., description="Fin del período de análisis")
    
    # Métricas de eficiencia
    efficiency_score: Decimal = Field(..., ge=0, le=100, description="Puntuación de eficiencia (0-100)")
    productivity_index: Decimal = Field(..., ge=0, description="Índice de productividad")
    quality_score: Decimal = Field(..., ge=0, le=100, description="Puntuación de calidad (0-100)")
    
    # Métricas de colaboración
    collaboration_score: Decimal = Field(..., ge=0, le=100, description="Puntuación de colaboración (0-100)")
    communication_frequency: int = Field(..., ge=0, description="Frecuencia de comunicación")
    knowledge_sharing_index: Decimal = Field(..., ge=0, description="Índice de intercambio de conocimiento")
    
    # Métricas de entrega
    delivery_performance: Decimal = Field(..., ge=0, le=100, description="Rendimiento de entrega (0-100)")
    on_time_delivery_rate: Decimal = Field(..., ge=0, le=100, description="Tasa de entrega a tiempo (%)")
    project_completion_rate: Decimal = Field(..., ge=0, le=100, description="Tasa de finalización de proyectos (%)")
    
    # Métricas de innovación
    innovation_score: Decimal = Field(..., ge=0, le=100, description="Puntuación de innovación (0-100)")
    improvement_suggestions: int = Field(..., ge=0, description="Número de sugerencias de mejora")
    
    # Datos adicionales
    total_projects: int = Field(..., ge=0, description="Total de proyectos en el período")
    active_members: int = Field(..., ge=0, description="Miembros activos en el período")
    utilization_rate: Decimal = Field(..., ge=0, le=100, description="Tasa de utilización (%)")


class ProductivityAnalysis(BaseSchema):
    """Análisis de productividad de equipos."""
    
    analysis_period: str = Field(..., description="Período de análisis")
    total_teams_analyzed: int = Field(..., ge=0, description="Total de equipos analizados")
    analysis_date: pendulum.DateTime = Field(default_factory=pendulum.now, description="Fecha del análisis")
    
    # Métricas globales
    average_productivity: Decimal = Field(..., ge=0, description="Productividad promedio")
    productivity_variance: Decimal = Field(..., ge=0, description="Varianza de productividad")
    top_performing_teams: List[Dict[str, Any]] = Field(default_factory=list, description="Equipos de mejor rendimiento")
    underperforming_teams: List[Dict[str, Any]] = Field(default_factory=list, description="Equipos con bajo rendimiento")
    
    # Comparaciones
    period_over_period_change: Optional[Decimal] = Field(None, description="Cambio período sobre período (%)")
    benchmark_comparison: Optional[Dict[str, Decimal]] = Field(None, description="Comparación con benchmarks")
    
    # Recomendaciones
    improvement_recommendations: List[str] = Field(default_factory=list, description="Recomendaciones de mejora")
    action_items: List[Dict[str, Any]] = Field(default_factory=list, description="Elementos de acción")
    
    # Tendencias
    productivity_trends: List[Dict[str, Any]] = Field(default_factory=list, description="Tendencias de productividad")
    seasonal_patterns: Optional[Dict[str, Any]] = Field(None, description="Patrones estacionales")


class CollaborationMetrics(BaseSchema):
    """Métricas de colaboración entre equipos."""
    
    analysis_date: pendulum.DateTime = Field(default_factory=pendulum.now, description="Fecha del análisis")
    teams_analyzed: List[int] = Field(..., description="IDs de equipos analizados")
    collaboration_types: List[CollaborationType] = Field(..., description="Tipos de colaboración analizados")
    
    # Métricas de colaboración
    overall_collaboration_score: Decimal = Field(..., ge=0, le=100, description="Puntuación general de colaboración")
    cross_team_interactions: int = Field(..., ge=0, description="Interacciones entre equipos")
    knowledge_transfer_events: int = Field(..., ge=0, description="Eventos de transferencia de conocimiento")
    resource_sharing_instances: int = Field(..., ge=0, description="Instancias de compartir recursos")
    
    # Análisis por tipo de colaboración
    collaboration_breakdown: Dict[CollaborationType, Decimal] = Field(
        default_factory=dict, 
        description="Desglose por tipo de colaboración"
    )
    
    # Redes de colaboración
    collaboration_network: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Red de colaboración entre equipos"
    )
    
    # Métricas de efectividad
    collaboration_effectiveness: Decimal = Field(..., ge=0, le=100, description="Efectividad de la colaboración")
    synergy_index: Decimal = Field(..., ge=0, description="Índice de sinergia")
    
    # Recomendaciones
    collaboration_opportunities: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Oportunidades de colaboración"
    )


class TeamCreationTrend(BaseSchema):
    """Tendencia de creación de equipos."""
    
    period: str = Field(..., description="Período (mes, trimestre, año)")
    period_start: pendulum.DateTime = Field(..., description="Inicio del período")
    period_end: pendulum.DateTime = Field(..., description="Fin del período")
    teams_created: int = Field(..., ge=0, description="Equipos creados en el período")
    teams_dissolved: int = Field(..., ge=0, description="Equipos disueltos en el período")
    net_change: int = Field(..., description="Cambio neto de equipos")
    growth_rate: Decimal = Field(..., description="Tasa de crecimiento (%)")
    
    # Análisis adicional
    average_team_size: Decimal = Field(..., ge=0, description="Tamaño promedio de equipos creados")
    most_common_department: Optional[str] = Field(None, description="Departamento más común")
    creation_reasons: List[str] = Field(default_factory=list, description="Razones de creación")


class TeamsSummaryReport(BaseSchema):
    """Reporte resumen de equipos."""
    
    report_date: pendulum.DateTime = Field(default_factory=pendulum.now, description="Fecha del reporte")
    report_format: ReportFormat = Field(..., description="Formato del reporte")
    period_covered: DateRange = Field(..., description="Período cubierto por el reporte")
    
    # Estadísticas generales
    total_teams: int = Field(..., ge=0, description="Total de equipos")
    active_teams: int = Field(..., ge=0, description="Equipos activos")
    total_members: int = Field(..., ge=0, description="Total de miembros")
    average_team_size: Decimal = Field(..., ge=0, description="Tamaño promedio de equipo")
    
    # Distribución por estado
    teams_by_status: Dict[TeamStatus, int] = Field(default_factory=dict, description="Equipos por estado")
    
    # Métricas de rendimiento
    overall_performance: TeamPerformanceMetrics = Field(..., description="Rendimiento general")
    top_performing_teams: List[Dict[str, Any]] = Field(default_factory=list, description="Mejores equipos")
    
    # Análisis de productividad
    productivity_summary: ProductivityAnalysis = Field(..., description="Resumen de productividad")
    
    # Colaboración
    collaboration_summary: CollaborationMetrics = Field(..., description="Resumen de colaboración")
    
    # Tendencias
    creation_trends: List[TeamCreationTrend] = Field(default_factory=list, description="Tendencias de creación")
    
    # Recomendaciones ejecutivas
    executive_summary: str = Field(..., description="Resumen ejecutivo")
    key_insights: List[str] = Field(default_factory=list, description="Insights clave")
    strategic_recommendations: List[str] = Field(default_factory=list, description="Recomendaciones estratégicas")
    
    # Datos para gráficos (opcional)
    charts_data: Optional[Dict[str, Any]] = Field(None, description="Datos para visualizaciones")


# ==========================================
# ESQUEMAS DE VALIDACIÓN
# ==========================================

class ValidationResult(BaseSchema):
    """Resultado de validación de datos de equipo."""
    
    is_valid: bool = Field(..., description="Indica si la validación fue exitosa")
    validation_date: pendulum.DateTime = Field(default_factory=pendulum.now, description="Fecha de validación")
    rules_applied: List[ValidationRuleType] = Field(..., description="Reglas aplicadas")
    
    # Errores y advertencias
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Errores encontrados")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="Advertencias")
    
    # Detalles de validación
    validation_details: Dict[str, Any] = Field(default_factory=dict, description="Detalles de la validación")
    
    # Recomendaciones de corrección
    correction_suggestions: List[str] = Field(default_factory=list, description="Sugerencias de corrección")
    
    @property
    def has_errors(self) -> bool:
        """Indica si hay errores."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Indica si hay advertencias."""
        return len(self.warnings) > 0


class BusinessContext(BaseSchema):
    """Contexto de negocio para validación de reglas."""
    
    organization_id: int = Field(..., description="ID de la organización")
    department_id: Optional[int] = Field(None, description="ID del departamento")
    business_unit: Optional[str] = Field(None, description="Unidad de negocio")
    
    # Políticas aplicables
    applicable_policies: List[str] = Field(default_factory=list, description="Políticas aplicables")
    compliance_requirements: List[str] = Field(default_factory=list, description="Requisitos de cumplimiento")
    
    # Límites organizacionales
    max_team_size: Optional[int] = Field(None, ge=1, description="Tamaño máximo de equipo")
    min_team_size: Optional[int] = Field(None, ge=1, description="Tamaño mínimo de equipo")
    max_teams_per_employee: Optional[int] = Field(None, ge=1, description="Máximo equipos por empleado")
    
    # Configuraciones específicas
    allow_cross_department_teams: bool = Field(default=True, description="Permitir equipos interdepartamentales")
    require_team_leader: bool = Field(default=True, description="Requerir líder de equipo")
    auto_assign_projects: bool = Field(default=False, description="Asignación automática de proyectos")
    
    # Fechas de vigencia
    effective_date: pendulum.DateTime = Field(default_factory=pendulum.now, description="Fecha de vigencia")
    expiration_date: Optional[pendulum.DateTime] = Field(None, description="Fecha de expiración")


class BusinessRuleValidationResult(BaseSchema):
    """Resultado de validación de reglas de negocio."""
    
    team_id: int = Field(..., description="ID del equipo validado")
    business_context: BusinessContext = Field(..., description="Contexto de negocio aplicado")
    validation_date: pendulum.DateTime = Field(default_factory=pendulum.now, description="Fecha de validación")
    
    # Resultado general
    is_compliant: bool = Field(..., description="Cumple con las reglas de negocio")
    compliance_score: Decimal = Field(..., ge=0, le=100, description="Puntuación de cumplimiento (0-100)")
    
    # Validaciones específicas
    rule_validations: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Resultados por regla específica"
    )
    
    # Violaciones encontradas
    violations: List[Dict[str, Any]] = Field(default_factory=list, description="Violaciones encontradas")
    
    # Recomendaciones de cumplimiento
    compliance_recommendations: List[str] = Field(
        default_factory=list, 
        description="Recomendaciones para mejorar cumplimiento"
    )
    
    # Acciones requeridas
    required_actions: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Acciones requeridas para cumplimiento"
    )
    
    # Riesgo de incumplimiento
    risk_level: str = Field(default="LOW", description="Nivel de riesgo: LOW, MEDIUM, HIGH, CRITICAL")
    risk_factors: List[str] = Field(default_factory=list, description="Factores de riesgo identificados")


# ==========================================
# ESQUEMAS PARA CREAR/ACTUALIZAR
# ==========================================

class TeamCreateSchema(BaseSchema):
    """Schema para crear un equipo con validaciones completas."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del equipo")
    code: Optional[str] = Field(None, max_length=20, description="Código del equipo")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del equipo")
    color_hex: str = Field(default="#3498db", pattern=r"^#[0-9A-Fa-f]{6}$", description="Color en hexadecimal")
    max_members: int = Field(default=10, ge=1, le=100, description="Número máximo de miembros")
    department_id: Optional[int] = Field(None, description="ID del departamento")
    leader_id: Optional[int] = Field(None, description="ID del líder inicial")
    is_active: bool = Field(default=True, description="Estado activo")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas adicionales")
    
    # Configuraciones avanzadas
    allow_external_members: bool = Field(default=False, description="Permitir miembros externos")
    auto_assign_projects: bool = Field(default=False, description="Asignación automática de proyectos")
    notification_settings: Optional[Dict[str, bool]] = Field(None, description="Configuraciones de notificación")


class TeamUpdateSchema(BaseSchema):
    """Schema para actualizar un equipo."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del equipo")
    code: Optional[str] = Field(None, max_length=20, description="Código del equipo")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del equipo")
    color_hex: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Color en hexadecimal")
    max_members: Optional[int] = Field(None, ge=1, le=100, description="Número máximo de miembros")
    department_id: Optional[int] = Field(None, description="ID del departamento")
    is_active: Optional[bool] = Field(None, description="Estado activo")
    notes: Optional[str] = Field(None, max_length=1000, description="Notas adicionales")
    
    # Configuraciones avanzadas
    allow_external_members: Optional[bool] = Field(None, description="Permitir miembros externos")
    auto_assign_projects: Optional[bool] = Field(None, description="Asignación automática de proyectos")
    notification_settings: Optional[Dict[str, bool]] = Field(None, description="Configuraciones de notificación")


class TeamMembershipSchema(BaseSchema):
    """Schema completo para membresía de equipo."""
    
    id: int = Field(..., description="ID de la membresía")
    team_id: int = Field(..., description="ID del equipo")
    employee_id: int = Field(..., description="ID del empleado")
    role: MembershipRole = Field(..., description="Rol en el equipo")
    start_date: date = Field(..., description="Fecha de inicio")
    end_date: Optional[date] = Field(None, description="Fecha de fin")
    is_active: bool = Field(..., description="Estado activo")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")
    
    # Información adicional del empleado (opcional)
    employee_name: Optional[str] = Field(None, description="Nombre del empleado")
    employee_email: Optional[str] = Field(None, description="Email del empleado")
    
    # Información adicional del equipo (opcional)
    team_name: Optional[str] = Field(None, description="Nombre del equipo")


# ==========================================
# ESQUEMAS DE RESPUESTA ESPECÍFICOS
# ==========================================

class TeamSchema(BaseSchema):
    """Schema completo de respuesta para equipo."""
    
    id: int = Field(..., description="ID del equipo")
    name: str = Field(..., description="Nombre del equipo")
    code: Optional[str] = Field(None, description="Código del equipo")
    description: Optional[str] = Field(None, description="Descripción del equipo")
    color_hex: str = Field(..., description="Color en hexadecimal")
    max_members: int = Field(..., description="Número máximo de miembros")
    is_active: bool = Field(..., description="Estado activo")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")
    
    # Información adicional (opcional)
    current_members_count: Optional[int] = Field(None, description="Número actual de miembros")
    active_projects_count: Optional[int] = Field(None, description="Número de proyectos activos")
    department_name: Optional[str] = Field(None, description="Nombre del departamento")
    leader_name: Optional[str] = Field(None, description="Nombre del líder")
    
    # Membresías (opcional)
    memberships: Optional[List[TeamMembershipSchema]] = Field(None, description="Membresías del equipo")


# Crear alias para compatibilidad con respuestas paginadas
PaginatedTeamResponse = PaginatedResponse