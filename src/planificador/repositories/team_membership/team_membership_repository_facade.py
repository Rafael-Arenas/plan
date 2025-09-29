# src/planificador/repositories/team_membership/team_membership_repository_facade.py

"""
Facade del Repositorio TeamMembership.

Este módulo implementa el patrón Facade para proporcionar una interfaz
unificada para todas las operaciones de membresías de equipos, integrando
los módulos especializados de CRUD, consultas, relaciones, estadísticas
y validaciones.

Principios de Diseño:
    - Facade Pattern: Interfaz simplificada para operaciones complejas
    - Composition: Integra múltiples módulos especializados
    - Single Responsibility: Cada módulo maneja un aspecto específico
    - Dependency Injection: Recibe sesión de base de datos por constructor
    - Error Handling: Manejo centralizado de errores y logging

Uso:
    ```python
    facade = TeamMembershipRepositoryFacade(session)
    
    # Operaciones CRUD
    membership = await facade.create_membership(data)
    await facade.update_membership(membership_id, updates)
    
    # Consultas
    memberships = await facade.get_by_employee_id(employee_id)
    active_memberships = await facade.get_active_memberships()
    
    # Estadísticas
    stats = await facade.get_membership_statistics()
    
    # Validaciones
    is_valid, errors = await facade.validate_membership_data(data)
    ```
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.database.database import db_manager
from planificador.models.employee import Employee
from planificador.models.team import Team
from planificador.models.team_membership import ( 
    TeamMembership, MembershipRole
)
from planificador.schemas.team_membership import (
    MembershipStatus
)
from planificador.repositories.team_membership.interfaces.crud_interface import ITeamMembershipCrudOperations
from planificador.repositories.team_membership.interfaces.query_interface import ITeamMembershipQueryOperations
from planificador.repositories.team_membership.interfaces.relationship_interface import ITeamMembershipRelationshipOperations
from planificador.repositories.team_membership.interfaces.statistics_interface import (
    ITeamMembershipStatisticsOperations, StatisticsPeriod
)
from planificador.repositories.team_membership.interfaces.validation_interface import ITeamMembershipValidationOperations
from planificador.repositories.team_membership.modules.crud_module import TeamMembershipCrudModule
from planificador.repositories.team_membership.modules.query_module import TeamMembershipQueryModule
from planificador.repositories.team_membership.modules.relationship_module import TeamMembershipRelationshipModule
from planificador.repositories.team_membership.modules.statistics_module import TeamMembershipStatisticsModule
from planificador.repositories.team_membership.modules.validation_module import TeamMembershipValidationModule
from planificador.exceptions.repository import TeamMembershipRepositoryError


class TeamMembershipRepositoryFacade(
    ITeamMembershipCrudOperations,
    ITeamMembershipQueryOperations,
    ITeamMembershipRelationshipOperations,
    ITeamMembershipStatisticsOperations,
    ITeamMembershipValidationOperations
):
    """
    Facade para el repositorio de membresías de equipos.
    
    Proporciona una interfaz unificada para todas las operaciones
    relacionadas con membresías de equipos, delegando a módulos
    especializados para cada tipo de operación.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        _logger: Logger para registro de eventos
        _crud_module: Módulo para operaciones CRUD
        _query_module: Módulo para operaciones de consulta
        _relationship_module: Módulo para operaciones de relaciones
        _statistics_module: Módulo para operaciones estadísticas
        _validation_module: Módulo para operaciones de validación
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el facade del repositorio TeamMembership.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        self.session = session
        self._logger = logger.bind(module="TeamMembershipRepositoryFacade")
        
        # Inicializar módulos especializados
        self._crud_module = TeamMembershipCrudModule(session)
        self._query_module = TeamMembershipQueryModule(session)
        self._relationship_module = TeamMembershipRelationshipModule(session)
        self._statistics_module = TeamMembershipStatisticsModule(session)
        self._validation_module = TeamMembershipValidationModule(session)
        
        self._logger.debug("TeamMembershipRepositoryFacade inicializado")
    
    # ==================== OPERACIONES CRUD ====================
    
    async def create_membership(self, membership_data: Dict[str, Any]) -> TeamMembership:
        """Crea una nueva membresía de equipo."""
        return await self._crud_module.create_membership(membership_data)

    async def update_membership(
        self,
        membership_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[TeamMembership]:
        """Actualiza una membresía existente."""
        return await self._crud_module.update_membership(membership_id, update_data)

    async def delete_membership(self, membership_id: int) -> bool:
        """Elimina una membresía."""
        return await self._crud_module.delete_membership(membership_id)

    async def activate_membership(self, membership_id: int) -> bool:
        """Activa una membresía."""
        return await self._crud_module.activate_membership(membership_id)

    async def deactivate_membership(
        self,
        membership_id: int,
        end_date: Optional[date] = None
    ) -> bool:
        """Desactiva una membresía."""
        return await self._crud_module.deactivate_membership(membership_id, end_date)
    
    async def update_membership_role(
        self,
        membership_id: int,
        new_role: MembershipRole
    ) -> Optional[TeamMembership]:
        """Actualiza el rol de una membresía."""
        return await self._crud_module.update_membership_role(membership_id, new_role)
    
    async def end_membership(
        self,
        membership_id: int,
        end_date: Optional[date] = None
    ) -> Optional[TeamMembership]:
        """Finaliza una membresía."""
        return await self._crud_module.end_membership(membership_id, end_date)
    
    async def get_by_unique_field(
        self,
        field_name: str,
        field_value: Any
    ) -> Optional[TeamMembership]:
        """Obtiene una membresía por campo único."""
        return await self._crud_module.get_by_unique_field(field_name, field_value)
    
    # ==================== OPERACIONES DE CONSULTA ====================
    
    async def get_membership_by_id(self, membership_id: int) -> Optional[TeamMembership]:
        return await self._query_module.get_membership_by_id(membership_id)

    async def get_memberships_by_employee(
        self, 
        employee_id: int,
        active_only: bool = True
    ) -> List[TeamMembership]:
        return await self._query_module.get_memberships_by_employee(employee_id, active_only)

    async def get_memberships_by_team(
        self, 
        team_id: int,
        active_only: bool = True
    ) -> List[TeamMembership]:
        return await self._query_module.get_memberships_by_team(team_id, active_only)

    async def get_membership_by_employee_and_team(
        self,
        employee_id: int,
        team_id: int,
        active_only: bool = True
    ) -> Optional[TeamMembership]:
        return await self._query_module.get_membership_by_employee_and_team(
            employee_id, team_id, active_only
        )

    async def get_memberships_by_role(
        self, 
        role: MembershipRole,
        active_only: bool = True
    ) -> List[TeamMembership]:
        return await self._query_module.get_memberships_by_role(role, active_only)

    async def get_active_memberships(self) -> List[TeamMembership]:
        return await self._query_module.get_active_memberships()

    async def get_memberships_by_date_range(
        self,
        start_date: date,
        end_date: date,
        include_overlapping: bool = True
    ) -> List[TeamMembership]:
        return await self._query_module.get_memberships_by_date_range(
            start_date, end_date, include_overlapping
        )

    async def get_current_memberships(self, as_of_date: Optional[date] = None) -> List[TeamMembership]:
        return await self._query_module.get_current_memberships(as_of_date)

    async def get_future_memberships(self, from_date: Optional[date] = None) -> List[TeamMembership]:
        return await self._query_module.get_future_memberships(from_date)

    async def get_past_memberships(self, until_date: Optional[date] = None) -> List[TeamMembership]:
        return await self._query_module.get_past_memberships(until_date)

    async def search_memberships(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TeamMembership]:
        return await self._query_module.search_memberships(filters, limit, offset)

    async def count_memberships(self, filters: Optional[Dict[str, Any]] = None) -> int:
        return await self._query_module.count_memberships(filters)

    async def get_all_memberships(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TeamMembership]:
        return await self._query_module.get_all_memberships(limit, offset)
    
    # ==================== OPERACIONES DE RELACIONES ====================

    async def get_membership_with_employee(self, membership_id: int) -> Optional[TeamMembership]:
        return await self._relationship_module.get_membership_with_employee(membership_id)

    async def get_membership_with_team(self, membership_id: int) -> Optional[TeamMembership]:
        return await self._relationship_module.get_membership_with_team(membership_id)

    async def get_membership_with_all_relations(self, membership_id: int) -> Optional[TeamMembership]:
        return await self._relationship_module.get_membership_with_all_relations(membership_id)

    async def get_employee_teams_with_details(
        self, 
        employee_id: int,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        return await self._relationship_module.get_employee_teams_with_details(employee_id, active_only)

    async def get_team_members_with_details(
        self, 
        team_id: int,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        return await self._relationship_module.get_team_members_with_details(team_id, active_only)

    async def transfer_employee_between_teams(
        self,
        employee_id: int,
        from_team_id: int,
        to_team_id: int,
        transfer_date: date,
        new_role: Optional[MembershipRole] = None
    ) -> Tuple[TeamMembership, TeamMembership]:
        return await self._relationship_module.transfer_employee_between_teams(
            employee_id, from_team_id, to_team_id, transfer_date, new_role
        )

    async def get_overlapping_memberships(
        self,
        employee_id: int,
        start_date: date,
        end_date: Optional[date] = None
    ) -> List[TeamMembership]:
        return await self._relationship_module.get_overlapping_memberships(
            employee_id, start_date, end_date
        )

    async def get_membership_conflicts(
        self,
        employee_id: int,
        team_id: int,
        start_date: date,
        end_date: Optional[date] = None
    ) -> List[TeamMembership]:
        return await self._relationship_module.get_membership_conflicts(
            employee_id, team_id, start_date, end_date
        )

    async def get_employee_membership_history(
        self, 
        employee_id: int,
        include_future: bool = False
    ) -> List[TeamMembership]:
        return await self._relationship_module.get_employee_membership_history(employee_id, include_future)

    async def get_team_membership_timeline(
        self, 
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        return await self._relationship_module.get_team_membership_timeline(
            team_id, start_date, end_date
        )

    async def get_concurrent_memberships(
        self,
        employee_id: int,
        reference_date: Optional[date] = None
    ) -> List[TeamMembership]:
        return await self._relationship_module.get_concurrent_memberships(employee_id, reference_date)

    async def get_leadership_transitions(
        self,
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        return await self._relationship_module.get_leadership_transitions(
            team_id, start_date, end_date
        )

    async def get_role_changes_history(
        self,
        employee_id: Optional[int] = None,
        team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene historial de cambios de roles.
        
        Args:
            employee_id: ID del empleado (opcional)
            team_id: ID del equipo (opcional)
        
        Returns:
            List[Dict[str, Any]]: Historial de cambios de roles
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        return await self._relationship_module.get_role_changes_history(
            employee_id=employee_id,
            team_id=team_id
        )

    async def get_employee_for_membership(self, membership_id: int) -> Optional[Employee]:
        """Obtiene el empleado asociado a una membresía."""
        membership = await self._relationship_module.get_membership_with_employee(membership_id)
        return membership.employee if membership else None

    async def get_team_for_membership(self, membership_id: int) -> Optional[Team]:
        """Obtiene el equipo asociado a una membresía."""
        membership = await self._relationship_module.get_membership_with_team(membership_id)
        return membership.team if membership else None

    # ==================== OPERACIONES DE ESTADÍSTICAS ====================

    async def count_total_memberships(
        self,
        active_only: bool = False,
        as_of_date: Optional[date] = None
    ) -> int:
        """
        Cuenta el total de membresías, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.count_total_memberships(
            active_only=active_only,
            as_of_date=as_of_date
        )

    async def count_memberships_by_status(
        self,
        as_of_date: Optional[date] = None
    ) -> Dict[MembershipStatus, int]:
        """
        Cuenta membresías por estado, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.count_memberships_by_status(
            as_of_date=as_of_date
        )

    async def count_memberships_by_role(
        self,
        active_only: bool = True,
        as_of_date: Optional[date] = None
    ) -> Dict[MembershipRole, int]:
        """
        Cuenta membresías por rol, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.count_memberships_by_role(
            active_only=active_only,
            as_of_date=as_of_date
        )

    async def get_membership_duration_statistics(
        self,
        completed_only: bool = True
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de duración, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_membership_duration_statistics(
            completed_only=completed_only
        )

    async def get_team_size_distribution(
        self,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene distribución de tamaños de equipos, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_team_size_distribution(
            as_of_date=as_of_date
        )

    async def get_employee_participation_stats(
        self,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de participación de empleados, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_employee_participation_stats(
            employee_id=employee_id
        )

    async def get_membership_trends(
        self,
        period: StatisticsPeriod,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Obtiene tendencias de membresías, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_membership_trends(
            period=period,
            start_date=start_date,
            end_date=end_date
        )

    async def get_turnover_rate(
        self,
        team_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calcula la tasa de rotación, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_turnover_rate(
            team_id=team_id,
            start_date=start_date,
            end_date=end_date
        )

    async def get_retention_rate(
        self,
        team_id: Optional[int] = None,
        months_threshold: int = 12
    ) -> Dict[str, Any]:
        """
        Calcula la tasa de retención, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_retention_rate(
            team_id=team_id,
            months_threshold=months_threshold
        )

    async def get_role_transition_matrix(
        self,
        team_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene matriz de transiciones de roles, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_role_transition_matrix(
            team_id=team_id
        )

    async def get_membership_overlap_statistics(
        self,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de solapamiento, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_membership_overlap_statistics(
            employee_id=employee_id
        )

    async def get_team_stability_metrics(
        self,
        team_id: int,
        analysis_period_months: int = 12
    ) -> Dict[str, Any]:
        """
        Calcula métricas de estabilidad de equipo, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_team_stability_metrics(
            team_id=team_id,
            analysis_period_months=analysis_period_months
        )

    async def get_leadership_statistics(
        self,
        team_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de liderazgo, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_leadership_statistics(
            team_id=team_id
        )

    async def get_membership_summary_report(
        self,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte resumen, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_membership_summary_report(
            as_of_date=as_of_date
        )

    async def get_team_composition_analysis(
        self,
        team_id: int,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Analiza la composición de un equipo, delegando al módulo de estadísticas.
        """
        return await self._statistics_module.get_team_composition_analysis(
            team_id=team_id,
            as_of_date=as_of_date
        )

    async def get_cross_team_participation(
        self,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analiza la participación cruzada, delegando al módulo de estadísticas."""
        return await self._statistics_module.get_cross_team_participation(
            employee_id=employee_id
        )

    async def get_membership_count(self) -> int:
        """Obtiene el número total de membresías."""
        return await self.count_total_memberships()

    async def get_active_membership_count(self) -> int:
        """Obtiene el número de membresías activas."""
        return await self.count_total_memberships(active_only=True)

    async def get_membership_count_by_role(self, role: MembershipRole) -> int:
        """Obtiene el número de membresías para un rol específico."""
        counts = await self.count_memberships_by_role()
        return counts.get(role, 0)

    async def get_average_membership_duration(self) -> float:
        """Obtiene la duración promedio de las membresías."""
        stats = await self.get_membership_duration_statistics()
        return stats.get("average_duration", 0.0)

    async def get_memberships_per_team(self) -> Dict[int, int]:
        """Obtiene el número de membresías por equipo."""
        return await self._statistics_module.get_memberships_per_team()

    async def get_memberships_per_employee(self) -> Dict[int, int]:
        """Obtiene el número de membresías por empleado."""
        return await self._statistics_module.get_memberships_per_employee()

    async def get_role_distribution(self) -> Dict[str, int]:
        """Obtiene la distribución de roles."""
        return await self._statistics_module.get_role_distribution()

    async def get_average_duration_by_role(self) -> Dict[str, float]:
        """Obtiene la duración promedio por rol."""
        return await self._statistics_module.get_average_duration_by_role()

    # --------------------------------------------------------------------------
    # Validation Operations
    # --------------------------------------------------------------------------

    async def validate_membership_dates(self, start_date: date, end_date: Optional[date]) -> None:
        """Valida las fechas de una membresía."""
        await self._validation_module.validate_dates(start_date, end_date)

    async def check_employee_active_membership(self, employee_id: int) -> bool:
        """Verifica si un empleado ya tiene una membresía activa."""
        return await self._validation_module.has_active_membership(employee_id)

    async def validate_role_for_update(self, membership_id: int, new_role: MembershipRole) -> bool:
        """Valida si el nuevo rol es válido para la actualización."""
        return await self._validation_module.is_valid_role_for_update(membership_id, new_role)

    async def validate_membership_data(
        self, data: Dict[str, Any], is_update: bool = False
    ) -> bool:
        return await self._validation_module.validate_membership_data(data)

    async def validate_membership_id(self, membership_id: int) -> bool:
        return await self._validation_module.validate_membership_id(membership_id)

    async def validate_employee_id(self, employee_id: int) -> bool:
        return await self._validation_module.validate_employee_id(employee_id)

    async def validate_team_id(self, team_id: int) -> bool:
        return await self._validation_module.validate_team_id(team_id)

    async def validate_membership_role(self, role: MembershipRole) -> bool:
        return await self._validation_module.validate_membership_role(role)

    async def validate_membership_status(self, status: MembershipStatus) -> bool:
        return await self._validation_module.validate_membership_status(status)

    async def validate_date_range(
        self, 
        start_date: date, 
        end_date: Optional[date] = None
    ) -> bool:
        return await self._validation_module.validate_date_range(start_date, end_date)

    async def validate_membership_overlap(
        self,
        employee_id: int,
        team_id: int,
        start_date: date,
        end_date: Optional[date] = None,
        exclude_membership_id: Optional[int] = None
    ) -> bool:
        return await self._validation_module.validate_membership_overlap(
            employee_id, team_id, start_date, end_date, exclude_membership_id
        )

    async def validate_leadership_assignment(
        self,
        employee_id: int,
        team_id: int,
        role: MembershipRole,
        start_date: date,
        end_date: Optional[date] = None
    ) -> bool:
        return await self._validation_module.validate_leadership_assignment(
            employee_id, team_id, role, start_date, end_date
        )

    async def validate_team_capacity(
        self,
        team_id: int,
        as_of_date: Optional[date] = None
    ) -> bool:
        return await self._validation_module.validate_team_capacity(team_id, as_of_date)

    async def validate_role_permissions(
        self,
        employee_id: int,
        role: MembershipRole,
        team_id: int
    ) -> bool:
        return await self._validation_module.validate_role_permissions(
            employee_id, role, team_id
        )

    async def validate_membership_transition(
        self,
        membership_id: int,
        new_status: MembershipStatus,
        transition_date: Optional[date] = None
    ) -> bool:
        return await self._validation_module.validate_membership_transition(
            membership_id, new_status, transition_date
        )

    async def validate_membership_end_date(
        self,
        membership_id: int,
        end_date: date
    ) -> bool:
        return await self._validation_module.validate_membership_end_date(
            membership_id, end_date
        )

    async def validate_business_rules(
        self,
        employee_id: int,
        team_id: int,
        role: MembershipRole,
        start_date: date,
        end_date: Optional[date] = None
    ) -> Tuple[bool, List[str]]:
        return await self._validation_module.validate_business_rules(
            employee_id, team_id, role, start_date, end_date
        )

    async def validate_data_consistency(
        self,
        membership_id: Optional[int] = None
    ) -> Tuple[bool, List[str]]:
        return await self._validation_module.validate_data_consistency(membership_id)

    async def validate_search_criteria(self, criteria: Dict[str, Any]) -> bool:
        return await self._validation_module.validate_search_criteria(criteria)

    async def validate_bulk_operation_data(
        self, 
        operations_data: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        return await self._validation_module.validate_bulk_operation_data(operations_data)

    async def validate_concurrent_membership_limit(
        self,
        employee_id: int,
        as_of_date: Optional[date] = None
    ) -> bool:
        return await self._validation_module.validate_concurrent_membership_limit(
            employee_id, as_of_date
        )
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    async def close(self):
        """
        Cierra la sesión de base de datos.
        
        Nota: Este método debe ser llamado cuando se termine de usar el facade
        para liberar recursos de base de datos.
        """
        try:
            if self.session:
                await self.session.close()
                self._logger.debug("Sesión de base de datos cerrada")
        except Exception as e:
            self._logger.error(f"Error al cerrar sesión: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error al cerrar sesión: {e}",
                operation="close",
                entity_type="TeamMembership",
                original_error=e
            )
    
    def __repr__(self) -> str:
        """Representación string del facade."""
        return f"TeamMembershipRepositoryFacade(session={self.session})"