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
from ....repositories.team.team_membership_repository_facade import TeamMembershipRepositoryFacade
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
    TeamResponseSchema,
    TeamListResponse,
    TeamSearchResponse,
    TeamMemberResponseSchema,
    TeamMembershipResponseSchema,
    BulkTeamCreationResultSchema,
    TeamCreationTrend,
    TeamPerformanceMetrics,
    ProductivityAnalysis,
    CollaborationMetrics,
    TeamsSummaryReport,
    ValidationResult,
    BusinessRuleValidationResult
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
        
        self._logger.info("TeamDomainService inicializado correctamente")
    
    async def initialize_service(self) -> None:
        """
        Inicializa el servicio y sus dependencias.
        
        Raises:
            RepositoryError: Si hay problemas con la inicialización del repositorio
        """
        try:
            self._logger.info("Inicializando TeamDomainService...")
            # Aquí se pueden agregar inicializaciones específicas si es necesario
            self._logger.info("TeamDomainService inicializado exitosamente")
        except Exception as e:
            self._logger.error(f"Error inicializando TeamDomainService: {e}")
            raise RepositoryError(f"Error en inicialización del servicio: {e}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Obtiene información del servicio y sus capacidades.
        
        Returns:
            Dict con información del servicio, módulos disponibles y estadísticas
        """
        return {
            "service_name": "TeamDomainService",
            "version": "1.0.0",
            "description": "Servicio de dominio para gestión integral de equipos",
            "modules": {
                "crud_operations": "Operaciones CRUD básicas para equipos",
                "membership_operations": "Gestión de membresías y roles",
                "search_operations": "Búsqueda y filtrado avanzado",
                "statistics_operations": "Métricas y estadísticas de equipos",
                "productivity_operations": "Análisis de productividad y rendimiento",
                "validation_operations": "Validaciones de reglas de negocio",
                "relationship_operations": "Consultas por relaciones específicas",
                "diagnostic_operations": "Diagnósticos y salud del sistema"
            },
            "capabilities": [
                "Gestión completa del ciclo de vida de equipos",
                "Administración de membresías y roles",
                "Análisis de productividad y colaboración",
                "Validación de reglas de negocio",
                "Reportes estadísticos avanzados",
                "Diagnósticos de salud del sistema"
            ],
            "initialized_at": pendulum.now().isoformat()
        }
    
    # ==========================================
    # OPERACIONES CRUD
    # ==========================================
    
    async def create_team(self, team_data: Dict[str, Any]) -> Team:
        """Delega la creación de equipo al módulo CRUD."""
        return await self._crud_ops.create_team(team_data)
    
    async def get_team_by_id(self, team_id: int) -> Optional[Team]:
        """Delega la obtención de equipo por ID al módulo CRUD."""
        return await self._crud_ops.get_team_by_id(team_id)
    
    async def update_team(self, team_id: int, team_data: Dict[str, Any]) -> Team:
        """Delega la actualización de equipo al módulo CRUD."""
        return await self._crud_ops.update_team(team_id, team_data)
    
    async def delete_team(self, team_id: int) -> bool:
        """Delega la eliminación de equipo al módulo CRUD."""
        return await self._crud_ops.delete_team(team_id)
    
    async def bulk_create_teams(
        self, 
        teams_data: List[Dict[str, Any]]
    ) -> BulkTeamCreationResultSchema:
        """Delega la creación masiva de equipos al módulo CRUD."""
        return await self._crud_ops.bulk_create_teams(teams_data)
    
    # ==========================================
    # OPERACIONES DE MEMBRESÍA
    # ==========================================
    
    async def add_team_member(
        self, 
        team_id: int, 
        employee_id: int, 
        role: str = "member"
    ) -> TeamMembershipResponseSchema:
        """Delega la adición de miembro al módulo de membresía."""
        return await self._membership_ops.add_team_member(team_id, employee_id, role)
    
    async def remove_team_member(
        self, 
        team_id: int, 
        employee_id: int
    ) -> bool:
        """Delega la remoción de miembro al módulo de membresía."""
        return await self._membership_ops.remove_team_member(team_id, employee_id)
    
    async def update_member_role(
        self, 
        team_id: int, 
        employee_id: int, 
        new_role: str
    ) -> TeamMembershipResponseSchema:
        """Delega la actualización de rol al módulo de membresía."""
        return await self._membership_ops.update_member_role(team_id, employee_id, new_role)
    
    async def get_team_members(self, team_id: int) -> List[TeamMemberResponseSchema]:
        """Delega la obtención de miembros al módulo de membresía."""
        return await self._membership_ops.get_team_members(team_id)
    
    # ==========================================
    # OPERACIONES DE BÚSQUEDA
    # ==========================================
    
    async def find_teams_by_name(
        self, 
        name_pattern: str, 
        exact_match: bool = False
    ) -> List[Team]:
        """Delega la búsqueda por nombre al módulo de búsqueda."""
        return await self._search_ops.find_teams_by_name(name_pattern, exact_match)
    
    async def find_teams_by_status(self, status: str) -> List[Team]:
        """Delega la búsqueda por estado al módulo de búsqueda."""
        return await self._search_ops.find_teams_by_status(status)
    
    async def find_teams_by_department(self, department: str) -> List[Team]:
        """Delega la búsqueda por departamento al módulo de búsqueda."""
        return await self._search_ops.find_teams_by_department(department)
    
    async def advanced_team_search(
        self, 
        search_criteria: Dict[str, Any]
    ) -> TeamSearchResponse:
        """Delega la búsqueda avanzada al módulo de búsqueda."""
        return await self._search_ops.advanced_team_search(search_criteria)
    
    # ==========================================
    # OPERACIONES DE ESTADÍSTICAS
    # ==========================================
    
    async def get_team_member_count(self, team_id: int) -> int:
        """Delega el conteo de miembros al módulo de estadísticas."""
        return await self._statistics_ops.get_team_member_count(team_id)
    
    async def get_teams_count_by_status(self, status: Optional[str] = None) -> Dict[str, int]:
        """Delega el conteo por estado al módulo de estadísticas."""
        return await self._statistics_ops.get_teams_count_by_status(status)
    
    async def get_average_team_size(self) -> float:
        """Delega el cálculo de tamaño promedio al módulo de estadísticas."""
        return await self._statistics_ops.get_average_team_size()
    
    async def get_team_creation_trends(
        self, 
        start_date: date, 
        end_date: date, 
        group_by: str = "month"
    ) -> List[TeamCreationTrend]:
        """Delega las tendencias de creación al módulo de estadísticas."""
        return await self._statistics_ops.get_team_creation_trends(
            start_date, end_date, group_by
        )
    
    # ==========================================
    # OPERACIONES DE PRODUCTIVIDAD
    # ==========================================
    
    async def calculate_team_performance_metrics(
        self, 
        team_id: int, 
        start_date: date, 
        end_date: date
    ) -> TeamPerformanceMetrics:
        """Delega el cálculo de métricas al módulo de productividad."""
        return await self._productivity_ops.calculate_team_performance_metrics(
            team_id, start_date, end_date
        )
    
    async def analyze_team_productivity(
        self, 
        team_id: int, 
        analysis_period_start: date, 
        analysis_period_end: date
    ) -> ProductivityAnalysis:
        """Delega el análisis de productividad al módulo de productividad."""
        return await self._productivity_ops.analyze_team_productivity(
            team_id, analysis_period_start, analysis_period_end
        )
    
    async def get_collaboration_metrics(
        self, 
        team_id: int, 
        metric_period_start: date, 
        metric_period_end: date
    ) -> CollaborationMetrics:
        """Delega las métricas de colaboración al módulo de productividad."""
        return await self._productivity_ops.get_collaboration_metrics(
            team_id, metric_period_start, metric_period_end
        )
    
    async def generate_teams_summary_report(
        self, 
        report_start_date: date, 
        report_end_date: date, 
        include_inactive: bool = False
    ) -> TeamsSummaryReport:
        """Delega el reporte resumen al módulo de productividad."""
        return await self._productivity_ops.generate_teams_summary_report(
            report_start_date, report_end_date, include_inactive
        )
    
    # ==========================================
    # OPERACIONES DE VALIDACIÓN
    # ==========================================
    
    async def validate_team_data_integrity(
        self, 
        team_data: Dict[str, Any]
    ) -> ValidationResult:
        """Delega la validación de integridad al módulo de validación."""
        return await self._validation_ops.validate_team_data_integrity(team_data)
    
    async def validate_business_rules(
        self, 
        operation_type: str, 
        operation_data: Dict[str, Any], 
        business_context: Optional[Dict[str, Any]] = None
    ) -> BusinessRuleValidationResult:
        """Delega la validación de reglas al módulo de validación."""
        return await self._validation_ops.validate_business_rules(
            operation_type, operation_data, business_context
        )
    
    # ==========================================
    # OPERACIONES DE RELACIONES
    # ==========================================
    
    async def find_teams_by_leader(self, leader_id: int) -> List[Team]:
        """Delega la búsqueda por líder al módulo de relaciones."""
        return await self._relationship_ops.find_teams_by_leader(leader_id)
    
    async def find_teams_by_project(self, project_id: int) -> List[Team]:
        """Delega la búsqueda por proyecto al módulo de relaciones."""
        return await self._relationship_ops.find_teams_by_project(project_id)
    
    async def find_teams_by_skill_set(self, required_skills: List[str]) -> List[Team]:
        """Delega la búsqueda por habilidades al módulo de relaciones."""
        return await self._relationship_ops.find_teams_by_skill_set(required_skills)
    
    async def find_teams_by_date_range(
        self, 
        start_date: date, 
        end_date: date, 
        date_field: str = "created_at"
    ) -> List[Team]:
        """Delega la búsqueda por rango de fechas al módulo de relaciones."""
        return await self._relationship_ops.find_teams_by_date_range(
            start_date, end_date, date_field
        )
    
    # ==========================================
    # OPERACIONES DE DIAGNÓSTICO
    # ==========================================
    
    async def get_teams_by_creation_date_with_tolerance(
        self, 
        target_date: date, 
        tolerance_days: int = 1
    ) -> List[Team]:
        """Delega la búsqueda con tolerancia al módulo de diagnóstico."""
        return await self._diagnostic_ops.get_teams_by_creation_date_with_tolerance(
            target_date, tolerance_days
        )
    
    async def check_service_health(self) -> Dict[str, Any]:
        """Delega la verificación de salud al módulo de diagnóstico."""
        return await self._diagnostic_ops.check_service_health()