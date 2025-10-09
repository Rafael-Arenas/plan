"""
Servicio de Dominio Principal para Equipos (Team).

Este módulo implementa el patrón Facade proporcionando un punto de acceso
unificado a todas las operaciones del dominio de equipos.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import date
import pendulum
from loguru import logger

from ....repositories.team.team_repository_facade import TeamRepositoryFacade
from ....repositories.team_membership.team_membership_repository_facade import TeamMembershipRepositoryFacade
from .interfaces import ITeamDomainService
from .modules import (
    TeamDomainCrudOperations,
    TeamDomainMembershipOperations,
    TeamDomainSearchOperations,
    TeamDomainStatisticsOperations,
    TeamDomainProductivityOperations,
    TeamDomainValidationOperations,
    TeamDomainRelationshipOperations,
    TeamDomainDiagnosticOperations
)
from planificador.exceptions import RepositoryError, ValidationError, NotFoundError
from planificador.models.team import Team
from planificador.schemas.team import (
    Team,
    TeamCreate,
    TeamUpdate,
    TeamMembership,
    TeamMembershipCreate,
    TeamWithMembers,
    TeamWithSchedules,
    TeamWithDetails,
    MembershipRole
)
from planificador.schemas.team.enums import TeamStatus
from planificador.schemas.team.team_advanced_schemas import (
    TeamCreateSchema,
    TeamUpdateSchema,
    TeamSchema,
    TeamMembershipSchema,
    PaginatedResponse,
    TeamPerformanceMetrics,
    ProductivityAnalysis,
    CollaborationMetrics,
    TeamsSummaryReport,
    ValidationResult,
    BusinessRuleValidationResult,
    TeamSearchCriteria,
    DateRange,
    BusinessContext,
    TeamCreationTrend
)


class TeamDomainService(ITeamDomainService):
    """
    Servicio de Dominio Principal para Equipos (Team).
    
    Implementa el patrón Facade proporcionando una interfaz unificada
    para todas las operaciones del dominio de equipos.
    
    Organización modular según funcionalidades disponibles:
    1. Operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
    2. Operaciones de Membresía (Gestión de miembros del equipo)
    3. Operaciones de Búsqueda (Filtrado y búsqueda avanzada)
    4. Operaciones de Estadísticas (Métricas y reportes estadísticos)
    5. Operaciones de Productividad (Análisis de rendimiento y productividad)
    6. Operaciones de Validación (Reglas de negocio y validaciones)
    7. Operaciones de Relaciones (Consultas por relaciones específicas)
    8. Operaciones de Diagnóstico (Salud del sistema y diagnósticos)
    
    Características principales:
    - Punto de acceso único para todas las operaciones
    - Encapsulación de la complejidad interna
    - Coordinación entre múltiples módulos especializados
    - Manejo centralizado de transacciones y errores
    - Logging estructurado y trazabilidad completa
    """
    
    def __init__(
        self, 
        team_repository_facade: TeamRepositoryFacade,
        membership_repository_facade: TeamMembershipRepositoryFacade
    ):
        """
        Inicializa el servicio de dominio con todos sus módulos.
        
        Args:
            team_repository_facade: Fachada del repositorio de equipos
            membership_repository_facade: Fachada del repositorio de membresías
        """
        self._team_repository = team_repository_facade
        self._membership_repository = membership_repository_facade
        self._logger = logger.bind(service="team_domain")
        
        # Inicializar todos los módulos especializados
        self._crud_ops = TeamDomainCrudOperations(
            team_repository_facade, 
            membership_repository_facade
        )
        self._membership_ops = TeamDomainMembershipOperations(
            team_repository_facade, 
            membership_repository_facade
        )
        self._search_ops = TeamDomainSearchOperations(team_repository_facade)
        self._statistics_ops = TeamDomainStatisticsOperations(
            team_repository_facade, 
            membership_repository_facade
        )
        self._productivity_ops = TeamDomainProductivityOperations(
            team_repository_facade, 
            membership_repository_facade
        )
        self._validation_ops = TeamDomainValidationOperations(
            team_repository_facade, 
            membership_repository_facade
        )
        self._relationship_ops = TeamDomainRelationshipOperations(
            team_repository_facade, 
            membership_repository_facade
        )
        self._diagnostic_ops = TeamDomainDiagnosticOperations(
            team_repository_facade, 
            membership_repository_facade
        )
        
        self._logger.info(
            "TeamDomainService inicializado correctamente",
            modules_count=8,
            timestamp=pendulum.now().isoformat()
        )

    async def initialize_service(self) -> None:
        """
        Inicializa el servicio y todos sus módulos.
        
        Realiza verificaciones de salud y configuraciones iniciales
        necesarias para el correcto funcionamiento del servicio.
        """
        try:
            self._logger.info("Inicializando TeamDomainService...")
            
            # Verificar salud del servicio
            health_status = await self.check_service_health()
            
            if not health_status.get("healthy", False):
                raise RepositoryError("El servicio no pasó las verificaciones de salud")
            
            self._logger.info("TeamDomainService inicializado exitosamente")
            
        except Exception as e:
            self._logger.error(f"Error inicializando TeamDomainService: {str(e)}")
            raise

    def get_service_info(self) -> Dict[str, Any]:
        """
        Obtiene información detallada del servicio.
        
        Returns:
            Dict con información del servicio y sus módulos
        """
        return {
            "service_name": "TeamDomainService",
            "version": "1.0.0",
            "description": "Servicio de dominio principal para gestión de equipos",
            "modules": {
                "crud_operations": "Operaciones CRUD básicas",
                "membership_operations": "Gestión de membresías de equipo",
                "search_operations": "Búsqueda y filtrado avanzado",
                "statistics_operations": "Métricas y estadísticas",
                "productivity_operations": "Análisis de productividad",
                "validation_operations": "Validaciones y reglas de negocio",
                "relationship_operations": "Consultas por relaciones",
                "diagnostic_operations": "Diagnósticos y salud del sistema"
            },
            "capabilities": [
                "CRUD completo de equipos",
                "Gestión de membresías",
                "Búsqueda avanzada",
                "Análisis de productividad",
                "Validaciones de negocio",
                "Diagnósticos de sistema"
            ],
            "initialized_at": pendulum.now().isoformat()
        }

    # ========================================================================
    # OPERACIONES CRUD (Create, Read, Update, Delete)
    # ========================================================================

    async def create_team(
        self, 
        team_data: TeamCreateSchema, 
        validate_business_rules: bool = True
    ) -> TeamSchema:
        """Crea un nuevo equipo con validación completa de datos de negocio."""
        return await self._crud_ops.create_team(team_data, validate_business_rules)

    async def get_team_by_id(
        self, 
        team_id: int, 
        include_members: bool = False
    ) -> Optional[TeamSchema]:
        """Obtiene un equipo específico por su identificador único."""
        return await self._crud_ops.get_team_by_id(team_id, include_members)

    async def get_all_teams(
        self, 
        page: int = 1, 
        page_size: int = 50, 
        include_inactive: bool = False
    ) -> PaginatedResponse[TeamSchema]:
        """Obtiene todos los equipos del sistema con paginación y filtros."""
        return await self._crud_ops.get_all_teams(page, page_size, include_inactive)

    async def update_team(
        self, 
        team_id: int, 
        update_data: TeamUpdateSchema, 
        validate_changes: bool = True
    ) -> TeamSchema:
        """Actualiza la información de un equipo existente."""
        return await self._crud_ops.update_team(team_id, update_data, validate_changes)

    async def delete_team(
        self, 
        team_id: int, 
        force_delete: bool = False
    ) -> bool:
        """Elimina un equipo del sistema después de validar dependencias."""
        return await self._crud_ops.delete_team(team_id, force_delete)

    async def bulk_create_teams(
        self, 
        teams_data: List[TeamCreateSchema], 
        validate_all: bool = True
    ) -> List[TeamSchema]:
        """Crea múltiples equipos en una operación transaccional."""
        return await self._crud_ops.bulk_create_teams(teams_data, validate_all)

    # ========================================================================
    # OPERACIONES DE MEMBRESÍA
    # ========================================================================

    async def add_team_member(
        self, 
        team_id: int, 
        employee_id: int, 
        role: MembershipRole, 
        validate_capacity: bool = True
    ) -> TeamMembershipSchema:
        """Agrega un nuevo miembro a un equipo con validación de roles."""
        return await self._membership_ops.add_team_member(
            team_id, employee_id, role, validate_capacity
        )

    async def remove_team_member(
        self, 
        team_id: int, 
        employee_id: int, 
        transfer_responsibilities: bool = True
    ) -> bool:
        """Remueve un miembro de un equipo con validación de dependencias."""
        return await self._membership_ops.remove_team_member(
            team_id, employee_id, transfer_responsibilities
        )

    async def update_member_role(
        self, 
        team_id: int, 
        employee_id: int, 
        new_role: MembershipRole, 
        validate_permissions: bool = True
    ) -> TeamMembershipSchema:
        """Actualiza el rol de un miembro dentro del equipo."""
        return await self._membership_ops.update_member_role(
            team_id, employee_id, new_role, validate_permissions
        )

    async def get_team_members(
        self, 
        team_id: int, 
        active_only: bool = True, 
        include_employee_details: bool = False
    ) -> List[TeamMembershipSchema]:
        """Obtiene todos los miembros de un equipo con sus roles."""
        return await self._membership_ops.get_team_members(
            team_id, active_only, include_employee_details
        )

    # ========================================================================
    # OPERACIONES DE BÚSQUEDA
    # ========================================================================

    async def find_teams_by_name(
        self, 
        name_pattern: str, 
        exact_match: bool = False
    ) -> List[TeamSchema]:
        """Busca equipos por nombre con coincidencia parcial o exacta."""
        return await self._search_ops.find_teams_by_name(name_pattern, exact_match)

    async def get_teams_by_status(
        self, 
        status: TeamStatus, 
        include_details: bool = False
    ) -> List[TeamSchema]:
        """Obtiene equipos filtrados por su estado actual."""
        return await self._search_ops.get_teams_by_status(status, include_details)

    async def get_teams_by_department(
        self, 
        department_id: int, 
        include_members: bool = False
    ) -> List[TeamSchema]:
        """Obtiene equipos asociados a un departamento específico."""
        return await self._search_ops.get_teams_by_department(department_id, include_members)

    async def search_teams_advanced(
        self, 
        search_criteria: TeamSearchCriteria, 
        sort_by: str = "name", 
        sort_order: str = "asc"
    ) -> List[TeamSchema]:
        """Búsqueda avanzada con múltiples criterios complejos."""
        return await self._search_ops.search_teams_advanced(
            search_criteria, sort_by, sort_order
        )

    # ========================================================================
    # OPERACIONES DE ESTADÍSTICAS
    # ========================================================================

    async def get_team_member_count(
        self, 
        team_id: int, 
        active_only: bool = True
    ) -> int:
        """Obtiene el número total de miembros de un equipo."""
        return await self._statistics_ops.get_team_member_count(team_id, active_only)

    async def get_teams_count_by_status(
        self, 
        include_details: bool = False
    ) -> Dict[TeamStatus, int]:
        """Obtiene el conteo de equipos agrupados por estado."""
        return await self._statistics_ops.get_teams_count_by_status(include_details)

    async def get_average_team_size(
        self, 
        active_teams_only: bool = True, 
        exclude_empty: bool = True
    ) -> float:
        """Calcula el tamaño promedio de los equipos en el sistema."""
        return await self._statistics_ops.get_average_team_size(
            active_teams_only, exclude_empty
        )

    async def get_team_creation_trends(
        self, 
        period: str = "month", 
        months_back: int = 12
    ) -> List[TeamCreationTrend]:
        """Obtiene tendencias de creación de equipos por período."""
        return await self._statistics_ops.get_team_creation_trends(period, months_back)

    # ========================================================================
    # OPERACIONES DE PRODUCTIVIDAD
    # ========================================================================

    async def get_team_performance_metrics(
        self, 
        team_id: int, 
        metric_types: List[str], 
        date_range: Optional[DateRange] = None
    ) -> TeamPerformanceMetrics:
        """Calcula métricas avanzadas de rendimiento de un equipo específico."""
        return await self._productivity_ops.get_team_performance_metrics(
            team_id, metric_types, date_range
        )

    async def get_teams_productivity_analysis(
        self, 
        analysis_period: str = "quarter", 
        include_comparisons: bool = True
    ) -> ProductivityAnalysis:
        """Analiza la productividad de todos los equipos con comparaciones."""
        return await self._productivity_ops.get_teams_productivity_analysis(
            analysis_period, include_comparisons
        )

    async def get_team_collaboration_metrics(
        self, 
        team_ids: Optional[List[int]] = None, 
        collaboration_types: List[str] = None
    ) -> CollaborationMetrics:
        """Obtiene métricas de colaboración entre equipos."""
        return await self._productivity_ops.get_team_collaboration_metrics(
            team_ids, collaboration_types or []
        )

    async def generate_teams_summary_report(
        self, 
        report_format: str = "detailed", 
        include_charts: bool = False, 
        export_format: str = "json"
    ) -> TeamsSummaryReport:
        """Genera un reporte resumen completo de todos los equipos."""
        return await self._productivity_ops.generate_teams_summary_report(
            report_format, include_charts, export_format
        )

    # ========================================================================
    # OPERACIONES DE VALIDACIÓN
    # ========================================================================

    async def validate_team_data(
        self, 
        team_data: TeamSchema, 
        validation_rules: List[str]
    ) -> ValidationResult:
        """Valida la integridad y consistencia de los datos de un equipo."""
        return await self._validation_ops.validate_team_data(team_data, validation_rules)

    async def validate_team_business_rules(
        self, 
        team_id: int, 
        business_context: BusinessContext
    ) -> BusinessRuleValidationResult:
        """Valida que un equipo cumple con las reglas de negocio específicas."""
        return await self._validation_ops.validate_team_business_rules(
            team_id, business_context
        )

    # ========================================================================
    # OPERACIONES DE RELACIONES
    # ========================================================================

    async def find_teams_by_leader(
        self, 
        leader_id: int, 
        include_team_details: bool = True
    ) -> List[TeamSchema]:
        """Encuentra equipos liderados por un empleado específico."""
        return await self._relationship_ops.find_teams_by_leader(
            leader_id, include_team_details
        )

    async def find_teams_by_project(
        self, 
        project_id: int, 
        active_only: bool = True
    ) -> List[TeamSchema]:
        """Encuentra equipos asignados a un proyecto específico."""
        return await self._relationship_ops.find_teams_by_project(project_id, active_only)

    async def find_teams_by_skill_set(
        self, 
        required_skills: List[str], 
        match_all: bool = False
    ) -> List[TeamSchema]:
        """Encuentra equipos que poseen un conjunto específico de habilidades."""
        return await self._relationship_ops.find_teams_by_skill_set(
            required_skills, match_all
        )

    async def find_teams_by_date_range(
        self, 
        start_date: pendulum.DateTime, 
        end_date: pendulum.DateTime, 
        include_inactive: bool = False
    ) -> List[TeamSchema]:
        """Encuentra equipos creados en un rango de fechas específico."""
        return await self._relationship_ops.find_teams_by_date_range(
            start_date, end_date, include_inactive
        )

    # ========================================================================
    # OPERACIONES DE DIAGNÓSTICO
    # ========================================================================

    async def get_teams_by_creation_date(
        self, 
        creation_date: pendulum.DateTime, 
        date_tolerance: int = 0
    ) -> List[TeamSchema]:
        """Obtiene equipos filtrados por fecha de creación con tolerancia."""
        return await self._diagnostic_ops.get_teams_by_creation_date(
            creation_date, date_tolerance
        )

    async def check_service_health(self) -> Dict[str, Any]:
        """Verifica el estado de salud del servicio de equipos."""
        return await self._diagnostic_ops.check_service_health()