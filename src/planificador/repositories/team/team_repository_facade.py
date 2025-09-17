# src/planificador/repositories/team/team_repository_facade.py

"""
Fachada del Repositorio Team.

Este módulo implementa el patrón Facade para el repositorio de equipos,
proporcionando una interfaz unificada y simplificada para todas las
operaciones relacionadas con la gestión de equipos y membresías.

Arquitectura:
    - Implementa múltiples interfaces especializadas
    - Delega operaciones a módulos específicos
    - Maneja la sesión de base de datos de forma centralizada
    - Proporciona logging y manejo de errores consistente

Principios de Diseño:
    - Single Responsibility: Cada módulo tiene una responsabilidad específica
    - Dependency Injection: Los módulos se inyectan como dependencias
    - Interface Segregation: Interfaces pequeñas y específicas
    - Open/Closed: Extensible sin modificar código existente

Uso:
    ```python
    async with get_async_session() as session:
        facade = TeamRepositoryFacade(session)
        team = await facade.create_team(team_data)
        teams = await facade.get_teams_by_department(department)
        await facade.add_team_member(team_id, employee_id, role)
    ```
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from planificador.models.team import Team
from planificador.models.team_membership import TeamMembership
from planificador.repositories.team.interfaces import (
    ITeamCrudOperations,
    ITeamQueryOperations,
    ITeamValidationOperations,
    ITeamRelationshipOperations,
    ITeamStatisticsOperations
)
from planificador.repositories.team.modules import (
    TeamCrudModule,
    TeamQueryModule,
    TeamValidationModule,
    TeamRelationshipModule,
    TeamStatisticsModule
)
from planificador.exceptions.repository import TeamRepositoryError


class TeamRepositoryFacade(
    ITeamCrudOperations,
    ITeamQueryOperations,
    ITeamValidationOperations,
    ITeamRelationshipOperations,
    ITeamStatisticsOperations
):
    """
    Fachada del repositorio Team que unifica todas las operaciones.
    
    Implementa las interfaces de CRUD, consultas, validación, relaciones y estadísticas,
    delegando las operaciones a los módulos especializados correspondientes.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        crud_module: Módulo para operaciones CRUD
        query_module: Módulo para operaciones de consulta
        validation_module: Módulo para operaciones de validación
        relationship_module: Módulo para operaciones de relaciones
        statistics_module: Módulo para operaciones de estadísticas
    """

    def __init__(self, session: AsyncSession):
        """Inicializa la fachada con sesión de BD y módulos especializados."""
        self.session = session
        self._logger = logger.bind(module="team_repository_facade")
        
        # Inicializar módulos especializados
        self.crud_module = TeamCrudModule(session)
        self.query_module = TeamQueryModule(session)
        self.validation_module = TeamValidationModule(session)
        self.relationship_module = TeamRelationshipModule(session)
        self.statistics_module = TeamStatisticsModule(session)
        
        self._logger.debug("TeamRepositoryFacade inicializada")

    # =============================================================================
    # OPERACIONES CRUD
    # =============================================================================

    async def create_team(self, team_data: Dict[str, Any]) -> Team:
        """Crea un nuevo equipo."""
        return await self.crud_module.create_team(team_data)

    async def update_team(
        self,
        team_id: int,
        team_data: Dict[str, Any]
    ) -> Team:
        """Actualiza un equipo existente."""
        return await self.crud_module.update_team(team_id, team_data)

    async def delete_team(self, team_id: int) -> bool:
        """Elimina un equipo."""
        return await self.crud_module.delete_team(team_id)

    # =============================================================================
    # OPERACIONES DE CONSULTA
    # =============================================================================

    async def get_team_by_id(self, team_id: int) -> Optional[Team]:
        """Obtiene un equipo por su ID."""
        return await self.query_module.get_team_by_id(team_id)

    async def get_team_by_name(self, name: str) -> Optional[Team]:
        """Obtiene un equipo por su nombre."""
        return await self.query_module.get_team_by_name(name)

    async def get_teams_by_department(
        self,
        department: str,
        active_only: bool = True
    ) -> List[Team]:
        """Obtiene equipos por departamento."""
        return await self.query_module.get_teams_by_department(department, active_only)

    async def get_active_teams(self) -> List[Team]:
        """Obtiene todos los equipos activos."""
        return await self.query_module.get_active_teams()

    async def get_inactive_teams(self) -> List[Team]:
        """Obtiene todos los equipos inactivos."""
        return await self.query_module.get_inactive_teams()

    async def search_teams_by_criteria(
        self,
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Team]:
        """Busca equipos por criterios específicos."""
        return await self.query_module.search_teams_by_criteria(criteria, limit, offset)

    async def get_teams_with_pagination(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Team], int]:
        """Obtiene equipos con paginación."""
        return await self.query_module.get_teams_with_pagination(page, page_size, filters)

    async def count_teams(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Cuenta el número total de equipos."""
        return await self.query_module.count_teams(filters)

    # =============================================================================
    # OPERACIONES DE RELACIONES
    # =============================================================================

    async def add_team_member(
        self,
        team_id: int,
        employee_id: int,
        role: str,
        is_leader: bool = False,
        start_date: Optional[date] = None
    ) -> TeamMembership:
        """Agrega un miembro al equipo."""
        return await self.relationship_module.add_team_member(
            team_id, employee_id, role, is_leader, start_date
        )

    async def remove_team_member(
        self,
        team_id: int,
        employee_id: int,
        end_date: Optional[date] = None
    ) -> bool:
        """Remueve un miembro del equipo."""
        return await self.relationship_module.remove_team_member(
            team_id, employee_id, end_date
        )

    async def assign_team_leader(
        self,
        team_id: int,
        employee_id: int
    ) -> TeamMembership:
        """Asigna un líder al equipo."""
        return await self.relationship_module.assign_team_leader(team_id, employee_id)

    async def get_team_members(
        self,
        team_id: int,
        active_only: bool = True,
        include_details: bool = False
    ) -> List[TeamMembership]:
        """Obtiene los miembros de un equipo."""
        return await self.relationship_module.get_team_members(
            team_id, active_only, include_details
        )

    async def get_team_leader(self, team_id: int) -> Optional[TeamMembership]:
        """Obtiene el líder de un equipo."""
        return await self.relationship_module.get_team_leader(team_id)

    async def get_employee_teams(
        self,
        employee_id: int,
        active_only: bool = True,
        include_details: bool = False
    ) -> List[TeamMembership]:
        """Obtiene los equipos de un empleado."""
        return await self.relationship_module.get_employee_teams(
            employee_id, active_only, include_details
        )

    async def get_teams_with_members_details(
        self,
        team_ids: Optional[List[int]] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Obtiene equipos con detalles de sus miembros."""
        return await self.relationship_module.get_teams_with_members_details(
            team_ids, active_only
        )

    async def update_member_role(
        self,
        team_id: int,
        employee_id: int,
        new_role: str
    ) -> TeamMembership:
        """Actualiza el rol de un miembro del equipo."""
        return await self.relationship_module.update_member_role(
            team_id, employee_id, new_role
        )

    # =============================================================================
    # OPERACIONES DE ESTADÍSTICAS
    # =============================================================================

    async def count_total_teams(self, active_only: bool = True) -> int:
        """Cuenta el total de equipos."""
        return await self.statistics_module.count_total_teams(active_only)

    async def get_team_size_distribution(self) -> Dict[str, int]:
        """Obtiene la distribución de tamaños de equipos."""
        return await self.statistics_module.get_team_size_distribution()

    async def get_membership_trends(
        self,
        start_date: date,
        end_date: date,
        granularity: str = "monthly"
    ) -> List[Dict[str, Any]]:
        """Obtiene tendencias de membresías."""
        return await self.statistics_module.get_membership_trends(
            start_date, end_date, granularity
        )

    async def get_leadership_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de liderazgo."""
        return await self.statistics_module.get_leadership_statistics()

    async def get_department_team_distribution(self) -> Dict[str, int]:
        """Obtiene la distribución de equipos por departamento."""
        return await self.statistics_module.get_department_team_distribution()

    async def get_average_team_size(self, department: Optional[str] = None) -> float:
        """Obtiene el tamaño promedio de equipos."""
        return await self.statistics_module.get_average_team_size(department)

    async def get_teams_without_leader(self) -> List[Team]:
        """Obtiene equipos sin líder."""
        return await self.statistics_module.get_teams_without_leader()

    async def get_most_active_employees_in_teams(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obtiene los empleados más activos en equipos."""
        return await self.statistics_module.get_most_active_employees_in_teams(limit)

    async def get_team_creation_trends(
        self,
        start_date: date,
        end_date: date,
        granularity: str = "monthly"
    ) -> List[Dict[str, Any]]:
        """Obtiene tendencias de creación de equipos."""
        return await self.statistics_module.get_team_creation_trends(
            start_date, end_date, granularity
        )

    async def generate_teams_summary_report(
        self,
        include_inactive: bool = False
    ) -> Dict[str, Any]:
        """Genera un reporte resumen de equipos."""
        return await self.statistics_module.generate_teams_summary_report(include_inactive)

    # =============================================================================
    # OPERACIONES DE VALIDACIÓN
    # =============================================================================

    async def validate_team_data(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida los datos de un equipo."""
        return await self.validation_module.validate_team_data(team_data)

    async def validate_membership_data(
        self, 
        membership_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida los datos de una membresía."""
        return await self.validation_module.validate_membership_data(membership_data)

    async def check_membership_conflicts(
        self, 
        employee_id: int, 
        team_id: int
    ) -> Dict[str, Any]:
        """Verifica conflictos de membresía para un empleado."""
        return await self.validation_module.check_membership_conflicts(employee_id, team_id)

    async def validate_business_rules(
        self, 
        operation: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida reglas de negocio específicas."""
        return await self.validation_module.validate_business_rules(operation, data)

    async def validate_data_consistency(self) -> Dict[str, Any]:
        """Valida la consistencia general de los datos."""
        return await self.validation_module.validate_data_consistency()

    # =============================================================================
    # MÉTODOS COMPUESTOS Y DE ALTO NIVEL
    # =============================================================================

    async def get_complete_team_info(self, team_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información completa de un equipo incluyendo miembros y estadísticas.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            Dict[str, Any]: Información completa del equipo o None si no existe
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Obteniendo información completa del equipo {team_id}")
            
            # Obtener datos básicos del equipo
            team = await self.get_team_by_id(team_id)
            if not team:
                return None
            
            # Obtener miembros con detalles
            members = await self.get_team_members(team_id, active_only=False, include_details=True)
            
            # Obtener líder
            leader = await self.get_team_leader(team_id)
            
            # Obtener estadísticas básicas
            active_members_count = len([m for m in members if m.is_active])
            inactive_members_count = len([m for m in members if not m.is_active])
            
            team_info = {
                'team': {
                    'id': team.id,
                    'name': team.name,
                    'description': team.description,
                    'department': team.department,
                    'is_active': team.is_active,
                    'created_at': team.created_at.isoformat() if team.created_at else None
                },
                'members': [
                    {
                        'employee_id': member.employee_id,
                        'role': member.role,
                        'is_leader': member.is_leader,
                        'is_active': member.is_active,
                        'start_date': member.start_date.isoformat() if member.start_date else None,
                        'end_date': member.end_date.isoformat() if member.end_date else None
                    }
                    for member in members
                ],
                'leader': {
                    'employee_id': leader.employee_id,
                    'role': leader.role,
                    'start_date': leader.start_date.isoformat() if leader.start_date else None
                } if leader else None,
                'statistics': {
                    'total_members': len(members),
                    'active_members': active_members_count,
                    'inactive_members': inactive_members_count,
                    'has_leader': leader is not None
                }
            }
            
            self._logger.debug(
                f"Información completa obtenida para equipo {team_id}: "
                f"{active_members_count} miembros activos, {'con' if leader else 'sin'} líder"
            )
            
            return team_info
            
        except Exception as e:
            self._logger.error(f"Error al obtener información completa del equipo {team_id}: {e}")
            raise TeamRepositoryError(
                message=f"Error al obtener información completa: {e}",
                operation="get_complete_team_info",
                entity_type="Team",
                entity_id=team_id,
                original_error=e
            )

    async def create_team_with_validation(
        self,
        team_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea un equipo con validación completa.
        
        Args:
            team_data: Datos del equipo a crear
        
        Returns:
            Dict[str, Any]: Resultado de la creación con validaciones
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la creación
        """
        try:
            self._logger.debug(f"Creando equipo con validación: {team_data.get('name', 'Sin nombre')}")
            
            # Validar datos del equipo
            validation_result = await self.validate_team_data(team_data)
            
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'team': None,
                    'validation_errors': validation_result['errors'],
                    'validation_warnings': validation_result['warnings']
                }
            
            # Validar reglas de negocio
            business_validation = await self.validate_business_rules('create_team', team_data)
            
            if not business_validation['is_valid']:
                return {
                    'success': False,
                    'team': None,
                    'validation_errors': business_validation['errors'],
                    'business_rule_violations': business_validation['errors']
                }
            
            # Crear el equipo
            team = await self.create_team(team_data)
            
            result = {
                'success': True,
                'team': {
                    'id': team.id,
                    'name': team.name,
                    'description': team.description,
                    'department': team.department,
                    'is_active': team.is_active,
                    'created_at': team.created_at.isoformat() if team.created_at else None
                },
                'validation_warnings': validation_result.get('warnings', [])
            }
            
            self._logger.info(f"Equipo creado exitosamente: {team.name} (ID: {team.id})")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al crear equipo con validación: {e}")
            raise TeamRepositoryError(
                message=f"Error al crear equipo: {e}",
                operation="create_team_with_validation",
                entity_type="Team",
                original_error=e
            )

    async def add_team_member_with_validation(
        self,
        team_id: int,
        employee_id: int,
        role: str,
        is_leader: bool = False,
        start_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Agrega un miembro al equipo con validación completa.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            role: Rol del empleado en el equipo
            is_leader: Si el empleado será líder
            start_date: Fecha de inicio de la membresía
        
        Returns:
            Dict[str, Any]: Resultado de la operación con validaciones
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la operación
        """
        try:
            self._logger.debug(
                f"Agregando miembro con validación: empleado {employee_id} al equipo {team_id}"
            )
            
            membership_data = {
                'team_id': team_id,
                'employee_id': employee_id,
                'role': role,
                'is_leader': is_leader,
                'start_date': start_date
            }
            
            # Validar datos de membresía
            validation_result = await self.validate_membership_data(membership_data)
            
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'membership': None,
                    'validation_errors': validation_result['errors'],
                    'validation_warnings': validation_result['warnings']
                }
            
            # Verificar conflictos
            conflicts = await self.check_membership_conflicts(employee_id, team_id)
            
            if conflicts['has_conflicts']:
                return {
                    'success': False,
                    'membership': None,
                    'conflicts': conflicts['conflicts'],
                    'existing_memberships': conflicts['existing_memberships']
                }
            
            # Validar reglas de negocio
            business_validation = await self.validate_business_rules('add_member', membership_data)
            
            if not business_validation['is_valid']:
                return {
                    'success': False,
                    'membership': None,
                    'business_rule_violations': business_validation['errors']
                }
            
            # Agregar el miembro
            membership = await self.add_team_member(
                team_id, employee_id, role, is_leader, start_date
            )
            
            result = {
                'success': True,
                'membership': {
                    'id': membership.id,
                    'team_id': membership.team_id,
                    'employee_id': membership.employee_id,
                    'role': membership.role,
                    'is_leader': membership.is_leader,
                    'is_active': membership.is_active,
                    'start_date': membership.start_date.isoformat() if membership.start_date else None
                },
                'validation_warnings': validation_result.get('warnings', [])
            }
            
            self._logger.info(
                f"Miembro agregado exitosamente: empleado {employee_id} al equipo {team_id} "
                f"como {role}{'(líder)' if is_leader else ''}"
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al agregar miembro con validación: {e}")
            raise TeamRepositoryError(
                message=f"Error al agregar miembro: {e}",
                operation="add_team_member_with_validation",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}",
                original_error=e
            )

    async def get_team_dashboard_data(
        self,
        team_id: Optional[int] = None,
        department: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene datos para dashboard de equipos.
        
        Args:
            team_id: ID de equipo específico (opcional)
            department: Departamento específico (opcional)
        
        Returns:
            Dict[str, Any]: Datos del dashboard
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(
                f"Obteniendo datos de dashboard: equipo {team_id}, departamento {department}"
            )
            
            dashboard_data = {
                'summary': {},
                'teams': [],
                'statistics': {},
                'alerts': []
            }
            
            # Estadísticas generales
            total_teams = await self.count_total_teams(active_only=False)
            active_teams = await self.count_total_teams(active_only=True)
            
            dashboard_data['summary'] = {
                'total_teams': total_teams,
                'active_teams': active_teams,
                'inactive_teams': total_teams - active_teams
            }
            
            # Obtener equipos según filtros
            if team_id:
                team_info = await self.get_complete_team_info(team_id)
                if team_info:
                    dashboard_data['teams'] = [team_info]
            elif department:
                teams = await self.get_teams_by_department(department, active_only=True)
                dashboard_data['teams'] = [
                    await self.get_complete_team_info(team.id) for team in teams
                ]
                dashboard_data['teams'] = [t for t in dashboard_data['teams'] if t is not None]
            else:
                # Obtener equipos más relevantes (con más miembros)
                teams = await self.get_active_teams()
                team_infos = []
                for team in teams[:10]:  # Limitar a 10 equipos
                    team_info = await self.get_complete_team_info(team.id)
                    if team_info:
                        team_infos.append(team_info)
                dashboard_data['teams'] = sorted(
                    team_infos,
                    key=lambda x: x['statistics']['active_members'],
                    reverse=True
                )
            
            # Estadísticas adicionales
            size_distribution = await self.get_team_size_distribution()
            department_distribution = await self.get_department_team_distribution()
            teams_without_leader = await self.get_teams_without_leader()
            
            dashboard_data['statistics'] = {
                'size_distribution': size_distribution,
                'department_distribution': department_distribution,
                'teams_without_leader_count': len(teams_without_leader),
                'average_team_size': await self.get_average_team_size()
            }
            
            # Alertas
            if teams_without_leader:
                dashboard_data['alerts'].append({
                    'type': 'warning',
                    'message': f'{len(teams_without_leader)} equipos sin líder asignado',
                    'teams': [{'id': t.id, 'name': t.name} for t in teams_without_leader]
                })
            
            # Verificar consistencia de datos
            consistency_report = await self.validate_data_consistency()
            if not consistency_report['is_consistent']:
                error_issues = [i for i in consistency_report['issues'] if i['severity'] == 'error']
                if error_issues:
                    dashboard_data['alerts'].append({
                        'type': 'error',
                        'message': f'{len(error_issues)} problemas de consistencia de datos',
                        'issues': error_issues
                    })
            
            self._logger.debug(
                f"Datos de dashboard obtenidos: {len(dashboard_data['teams'])} equipos, "
                f"{len(dashboard_data['alerts'])} alertas"
            )
            
            return dashboard_data
            
        except Exception as e:
            self._logger.error(f"Error al obtener datos de dashboard: {e}")
            raise TeamRepositoryError(
                message=f"Error al obtener datos de dashboard: {e}",
                operation="get_team_dashboard_data",
                entity_type="Team",
                original_error=e
            )

    async def bulk_team_operation(
        self,
        operation: str,
        team_data_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Realiza operaciones en lote sobre equipos.
        
        Args:
            operation: Tipo de operación (create, update, delete)
            team_data_list: Lista de datos de equipos
        
        Returns:
            List[Dict[str, Any]]: Resultados de las operaciones
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante las operaciones
        """
        try:
            self._logger.debug(f"Ejecutando operación en lote: {operation} sobre {len(team_data_list)} equipos")
            
            results = []
            
            for i, team_data in enumerate(team_data_list):
                try:
                    if operation == 'create':
                        result = await self.create_team_with_validation(team_data)
                    elif operation == 'update':
                        team_id = team_data.get('id')
                        if not team_id:
                            results.append({
                                'index': i,
                                'success': False,
                                'error': 'ID de equipo requerido para actualización'
                            })
                            continue
                        team = await self.update_team(team_id, team_data)
                        result = {
                            'success': True,
                            'team': {
                                'id': team.id,
                                'name': team.name,
                                'description': team.description,
                                'department': team.department,
                                'is_active': team.is_active
                            }
                        }
                    elif operation == 'delete':
                        team_id = team_data.get('id')
                        if not team_id:
                            results.append({
                                'index': i,
                                'success': False,
                                'error': 'ID de equipo requerido para eliminación'
                            })
                            continue
                        
                        # Validar reglas de negocio para eliminación
                        business_validation = await self.validate_business_rules(
                            'delete_team', {'team_id': team_id}
                        )
                        
                        if not business_validation['is_valid']:
                            results.append({
                                'index': i,
                                'success': False,
                                'business_rule_violations': business_validation['errors']
                            })
                            continue
                        
                        deleted = await self.delete_team(team_id)
                        result = {
                            'success': deleted,
                            'team_id': team_id
                        }
                    else:
                        results.append({
                            'index': i,
                            'success': False,
                            'error': f'Operación no soportada: {operation}'
                        })
                        continue
                    
                    result['index'] = i
                    results.append(result)
                    
                except Exception as e:
                    results.append({
                        'index': i,
                        'success': False,
                        'error': str(e)
                    })
            
            successful_operations = len([r for r in results if r.get('success', False)])
            
            self._logger.info(
                f"Operación en lote completada: {successful_operations}/{len(team_data_list)} exitosas"
            )
            
            return results
            
        except Exception as e:
            self._logger.error(f"Error en operación en lote: {e}")
            raise TeamRepositoryError(
                message=f"Error en operación en lote: {e}",
                operation="bulk_team_operation",
                entity_type="Team",
                original_error=e
            )