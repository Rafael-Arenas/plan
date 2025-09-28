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

from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.repositories.team_membership.interfaces.crud_interface import ITeamMembershipCrudOperations
from planificador.repositories.team_membership.interfaces.query_interface import ITeamMembershipQueryOperations
from planificador.repositories.team_membership.interfaces.relationship_interface import ITeamMembershipRelationshipOperations
from planificador.repositories.team_membership.interfaces.statistics_interface import ITeamMembershipStatisticsOperations
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
    
    async def create_membership(self, data: Dict[str, Any]) -> TeamMembership:
        """Crea una nueva membresía de equipo."""
        return await self._crud_module.create_membership(data)
    
    async def update_membership(
        self,
        membership_id: int,
        updates: Dict[str, Any]
    ) -> Optional[TeamMembership]:
        """Actualiza una membresía existente."""
        return await self._crud_module.update_membership(membership_id, updates)
    
    async def delete_membership(self, membership_id: int) -> bool:
        """Elimina una membresía."""
        return await self._crud_module.delete_membership(membership_id)
    
    async def activate_membership(self, membership_id: int) -> Optional[TeamMembership]:
        """Activa una membresía."""
        return await self._crud_module.activate_membership(membership_id)
    
    async def deactivate_membership(self, membership_id: int) -> Optional[TeamMembership]:
        """Desactiva una membresía."""
        return await self._crud_module.deactivate_membership(membership_id)
    
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
    
    async def get_by_id(self, membership_id: int) -> Optional[TeamMembership]:
        """Obtiene una membresía por ID."""
        return await self._query_module.get_by_id(membership_id)
    
    async def get_by_employee_id(self, employee_id: int) -> List[TeamMembership]:
        """Obtiene todas las membresías de un empleado."""
        return await self._query_module.get_by_employee_id(employee_id)
    
    async def get_by_team_id(self, team_id: int) -> List[TeamMembership]:
        """Obtiene todas las membresías de un equipo."""
        return await self._query_module.get_by_team_id(team_id)
    
    async def get_by_role(self, role: MembershipRole) -> List[TeamMembership]:
        """Obtiene membresías por rol."""
        return await self._query_module.get_by_role(role)
    
    async def get_active_memberships(self) -> List[TeamMembership]:
        """Obtiene todas las membresías activas."""
        return await self._query_module.get_active_memberships()
    
    async def get_by_date_range(
        self,
        start_date: date,
        end_date: Optional[date] = None
    ) -> List[TeamMembership]:
        """Obtiene membresías en un rango de fechas."""
        return await self._query_module.get_by_date_range(start_date, end_date)
    
    async def search_memberships(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TeamMembership]:
        """Busca membresías con filtros."""
        return await self._query_module.search_memberships(filters, limit, offset)
    
    async def count_memberships(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Cuenta membresías con filtros opcionales."""
        return await self._query_module.count_memberships(filters)
    
    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TeamMembership]:
        """Obtiene todas las membresías."""
        return await self._query_module.get_all(limit, offset)
    
    # ==================== OPERACIONES DE RELACIONES ====================
    
    async def get_membership_with_relations(
        self,
        membership_id: int,
        load_employee: bool = True,
        load_team: bool = True
    ) -> Optional[TeamMembership]:
        """Obtiene una membresía con relaciones cargadas."""
        return await self._relationship_module.get_membership_with_relations(
            membership_id, load_employee, load_team
        )
    
    async def get_employee_memberships_with_teams(
        self,
        employee_id: int,
        active_only: bool = False
    ) -> List[TeamMembership]:
        """Obtiene membresías de un empleado con equipos cargados."""
        return await self._relationship_module.get_employee_memberships_with_teams(
            employee_id, active_only
        )
    
    async def get_team_memberships_with_employees(
        self,
        team_id: int,
        active_only: bool = False
    ) -> List[TeamMembership]:
        """Obtiene membresías de un equipo con empleados cargados."""
        return await self._relationship_module.get_team_memberships_with_employees(
            team_id, active_only
        )
    
    async def transfer_employee_to_team(
        self,
        employee_id: int,
        from_team_id: int,
        to_team_id: int,
        new_role: Optional[MembershipRole] = None,
        transfer_date: Optional[date] = None
    ) -> Tuple[Optional[TeamMembership], Optional[TeamMembership]]:
        """Transfiere un empleado entre equipos."""
        return await self._relationship_module.transfer_employee_to_team(
            employee_id, from_team_id, to_team_id, new_role, transfer_date
        )
    
    async def get_overlapping_memberships(
        self,
        employee_id: int,
        start_date: date,
        end_date: Optional[date] = None
    ) -> List[TeamMembership]:
        """Obtiene membresías que se solapan."""
        return await self._relationship_module.get_overlapping_memberships(
            employee_id, start_date, end_date
        )
    
    async def get_membership_conflicts(
        self,
        employee_id: int
    ) -> List[Tuple[TeamMembership, TeamMembership]]:
        """Obtiene conflictos de membresías."""
        return await self._relationship_module.get_membership_conflicts(employee_id)
    
    async def get_membership_history(
        self,
        employee_id: int,
        include_inactive: bool = True
    ) -> List[TeamMembership]:
        """Obtiene el historial de membresías."""
        return await self._relationship_module.get_membership_history(
            employee_id, include_inactive
        )
    
    async def get_role_change_history(
        self,
        employee_id: int,
        team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene el historial de cambios de rol."""
        return await self._relationship_module.get_role_change_history(
            employee_id, team_id
        )
    
    # ==================== OPERACIONES ESTADÍSTICAS ====================
    
    async def count_by_status(self, is_active: bool) -> int:
        """Cuenta membresías por estado."""
        return await self._statistics_module.count_by_status(is_active)
    
    async def count_by_role(self, role: MembershipRole) -> int:
        """Cuenta membresías por rol."""
        return await self._statistics_module.count_by_role(role)
    
    async def get_membership_duration_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de duración de membresías."""
        return await self._statistics_module.get_membership_duration_stats()
    
    async def get_team_size_distribution(self) -> Dict[str, Any]:
        """Obtiene distribución de tamaños de equipos."""
        return await self._statistics_module.get_team_size_distribution()
    
    async def get_employee_participation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de participación de empleados."""
        return await self._statistics_module.get_employee_participation_stats()
    
    async def get_membership_trends(
        self,
        start_date: date,
        end_date: date,
        granularity: str = 'month'
    ) -> List[Dict[str, Any]]:
        """Obtiene tendencias de membresías."""
        return await self._statistics_module.get_membership_trends(
            start_date, end_date, granularity
        )
    
    async def get_turnover_rate(
        self,
        team_id: Optional[int] = None,
        period_months: int = 12
    ) -> Dict[str, Any]:
        """Obtiene tasa de rotación."""
        return await self._statistics_module.get_turnover_rate(team_id, period_months)
    
    async def get_retention_rate(
        self,
        team_id: Optional[int] = None,
        period_months: int = 12
    ) -> Dict[str, Any]:
        """Obtiene tasa de retención."""
        return await self._statistics_module.get_retention_rate(team_id, period_months)
    
    async def get_role_transition_matrix(
        self,
        team_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obtiene matriz de transición de roles."""
        return await self._statistics_module.get_role_transition_matrix(team_id)
    
    async def get_membership_overlap_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de solapamiento de membresías."""
        return await self._statistics_module.get_membership_overlap_stats()
    
    async def get_team_stability_metrics(self, team_id: int) -> Dict[str, Any]:
        """Obtiene métricas de estabilidad del equipo."""
        return await self._statistics_module.get_team_stability_metrics(team_id)
    
    async def get_leadership_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de liderazgo."""
        return await self._statistics_module.get_leadership_statistics()
    
    async def get_membership_summary_report(
        self,
        team_id: Optional[int] = None,
        employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obtiene reporte resumen de membresías."""
        return await self._statistics_module.get_membership_summary_report(
            team_id, employee_id
        )
    
    async def get_team_composition_analysis(self, team_id: int) -> Dict[str, Any]:
        """Obtiene análisis de composición del equipo."""
        return await self._statistics_module.get_team_composition_analysis(team_id)
    
    async def get_cross_team_participation(self, employee_id: int) -> Dict[str, Any]:
        """Obtiene participación cruzada en equipos."""
        return await self._statistics_module.get_cross_team_participation(employee_id)
    
    # ==================== OPERACIONES DE VALIDACIÓN ====================
    
    async def validate_membership_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Valida datos de membresía."""
        return await self._validation_module.validate_membership_data(data)
    
    async def validate_membership_id(self, membership_id: int) -> bool:
        """Valida ID de membresía."""
        return await self._validation_module.validate_membership_id(membership_id)
    
    async def validate_employee_id(self, employee_id: int) -> bool:
        """Valida ID de empleado."""
        return await self._validation_module.validate_employee_id(employee_id)
    
    async def validate_team_id(self, team_id: int) -> bool:
        """Valida ID de equipo."""
        return await self._validation_module.validate_team_id(team_id)
    
    async def validate_role(self, role: MembershipRole) -> bool:
        """Valida rol."""
        return await self._validation_module.validate_role(role)
    
    async def validate_date_range(
        self,
        start_date: date,
        end_date: Optional[date] = None
    ) -> Tuple[bool, List[str]]:
        """Valida rango de fechas."""
        return await self._validation_module.validate_date_range(start_date, end_date)
    
    async def validate_membership_overlap(
        self,
        employee_id: int,
        start_date: date,
        end_date: Optional[date] = None,
        exclude_membership_id: Optional[int] = None
    ) -> Tuple[bool, List[TeamMembership]]:
        """Valida solapamiento de membresías."""
        return await self._validation_module.validate_membership_overlap(
            employee_id, start_date, end_date, exclude_membership_id
        )
    
    async def validate_leadership_assignment(
        self,
        team_id: int,
        role: MembershipRole,
        exclude_membership_id: Optional[int] = None
    ) -> Tuple[bool, List[str]]:
        """Valida asignación de liderazgo."""
        return await self._validation_module.validate_leadership_assignment(
            team_id, role, exclude_membership_id
        )
    
    async def validate_team_capacity(
        self,
        team_id: int,
        max_capacity: Optional[int] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Valida capacidad del equipo."""
        return await self._validation_module.validate_team_capacity(team_id, max_capacity)
    
    async def validate_business_rules(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Valida reglas de negocio."""
        return await self._validation_module.validate_business_rules(data)
    
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