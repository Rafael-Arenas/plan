# src/planificador/repositories/team/modules/validation_module.py

"""
Módulo de validación para operaciones de validación del repositorio Team.

Este módulo implementa las operaciones de validación de datos, reglas de negocio
y verificaciones de consistencia para equipos y membresías.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de validación y verificación
    - Business Rules: Implementación de reglas de negocio específicas
    - Data Integrity: Validaciones para mantener consistencia de datos

Uso:
    ```python
    validation_module = TeamValidationModule(session)
    is_valid = await validation_module.validate_team_data(team_data)
    conflicts = await validation_module.check_membership_conflicts(employee_id, team_id)
    consistency = await validation_module.validate_data_consistency()
    ```
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date
from sqlalchemy import select, and_, or_, func, exists
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.team import Team
from planificador.models.team_membership import TeamMembership
from planificador.repositories.team.interfaces.validation_interface import ITeamValidationOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    TeamRepositoryError,
    convert_sqlalchemy_error
)
from planificador.exceptions.validation import ValidationError
import pendulum
import re


class TeamValidationModule(BaseRepository[Team], ITeamValidationOperations):
    """
    Módulo para operaciones de validación del repositorio Team.
    
    Implementa las operaciones de validación de datos, reglas de negocio
    y verificaciones de consistencia usando Pendulum para fechas
    y validaciones robustas.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Team
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de validación para equipos.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Team)
        self._logger = self._logger.bind(component="TeamValidationModule")
        self._logger.debug("TeamValidationModule inicializado")

    async def validate_team_data(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida los datos de un equipo.
        
        Args:
            team_data: Diccionario con datos del equipo
        
        Returns:
            Dict[str, Any]: Resultado de validación con errores si los hay
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando datos del equipo: {team_data.get('name', 'Sin nombre')}")
            
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Validar nombre requerido
            name = team_data.get('name', '').strip()
            if not name:
                validation_result['errors'].append({
                    'field': 'name',
                    'message': 'El nombre del equipo es requerido',
                    'code': 'REQUIRED_FIELD'
                })
            elif len(name) < 2:
                validation_result['errors'].append({
                    'field': 'name',
                    'message': 'El nombre del equipo debe tener al menos 2 caracteres',
                    'code': 'MIN_LENGTH'
                })
            elif len(name) > 100:
                validation_result['errors'].append({
                    'field': 'name',
                    'message': 'El nombre del equipo no puede exceder 100 caracteres',
                    'code': 'MAX_LENGTH'
                })
            
            # Validar caracteres especiales en nombre
            if name and not re.match(r'^[a-zA-Z0-9\s\-_áéíóúÁÉÍÓÚñÑ]+$', name):
                validation_result['errors'].append({
                    'field': 'name',
                    'message': 'El nombre contiene caracteres no permitidos',
                    'code': 'INVALID_CHARACTERS'
                })
            
            # Validar descripción
            description = team_data.get('description', '')
            if description and len(description) > 500:
                validation_result['errors'].append({
                    'field': 'description',
                    'message': 'La descripción no puede exceder 500 caracteres',
                    'code': 'MAX_LENGTH'
                })
            
            # Validar departamento
            department = team_data.get('department', '').strip()
            if department and len(department) > 100:
                validation_result['errors'].append({
                    'field': 'department',
                    'message': 'El departamento no puede exceder 100 caracteres',
                    'code': 'MAX_LENGTH'
                })
            
            # Validar fechas
            created_at = team_data.get('created_at')
            if created_at:
                try:
                    if isinstance(created_at, str):
                        pendulum.parse(created_at)
                    elif isinstance(created_at, date):
                        # Validar que no sea fecha futura
                        if created_at > pendulum.now().date():
                            validation_result['warnings'].append({
                                'field': 'created_at',
                                'message': 'La fecha de creación es futura',
                                'code': 'FUTURE_DATE'
                            })
                except Exception:
                    validation_result['errors'].append({
                        'field': 'created_at',
                        'message': 'Formato de fecha inválido',
                        'code': 'INVALID_DATE_FORMAT'
                    })
            
            # Validar estado activo
            is_active = team_data.get('is_active')
            if is_active is not None and not isinstance(is_active, bool):
                validation_result['errors'].append({
                    'field': 'is_active',
                    'message': 'El estado activo debe ser verdadero o falso',
                    'code': 'INVALID_BOOLEAN'
                })
            
            # Verificar unicidad del nombre si se proporciona ID
            team_id = team_data.get('id')
            if name:
                name_exists = await self._check_name_uniqueness(name, team_id)
                if name_exists:
                    validation_result['errors'].append({
                        'field': 'name',
                        'message': 'Ya existe un equipo con este nombre',
                        'code': 'DUPLICATE_NAME'
                    })
            
            # Determinar si es válido
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
            self._logger.debug(
                f"Validación completada: {'válido' if validation_result['is_valid'] else 'inválido'}, "
                f"{len(validation_result['errors'])} errores, {len(validation_result['warnings'])} advertencias"
            )
            
            return validation_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al validar datos del equipo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_team_data",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar datos: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="validate_team_data",
                entity_type="Team",
                original_error=e
            )

    async def validate_membership_data(
        self, 
        membership_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valida los datos de una membresía.
        
        Args:
            membership_data: Diccionario con datos de la membresía
        
        Returns:
            Dict[str, Any]: Resultado de validación con errores si los hay
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(
                f"Validando datos de membresía: equipo {membership_data.get('team_id')}, "
                f"empleado {membership_data.get('employee_id')}"
            )
            
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Validar IDs requeridos
            team_id = membership_data.get('team_id')
            employee_id = membership_data.get('employee_id')
            
            if not team_id:
                validation_result['errors'].append({
                    'field': 'team_id',
                    'message': 'El ID del equipo es requerido',
                    'code': 'REQUIRED_FIELD'
                })
            
            if not employee_id:
                validation_result['errors'].append({
                    'field': 'employee_id',
                    'message': 'El ID del empleado es requerido',
                    'code': 'REQUIRED_FIELD'
                })
            
            # Validar rol
            role = membership_data.get('role', '').strip()
            if not role:
                validation_result['errors'].append({
                    'field': 'role',
                    'message': 'El rol es requerido',
                    'code': 'REQUIRED_FIELD'
                })
            elif len(role) > 50:
                validation_result['errors'].append({
                    'field': 'role',
                    'message': 'El rol no puede exceder 50 caracteres',
                    'code': 'MAX_LENGTH'
                })
            
            # Validar fechas
            start_date = membership_data.get('start_date')
            end_date = membership_data.get('end_date')
            
            if start_date:
                try:
                    if isinstance(start_date, str):
                        start_date = pendulum.parse(start_date).date()
                    
                    # Validar que no sea muy antigua
                    if start_date < pendulum.now().subtract(years=10).date():
                        validation_result['warnings'].append({
                            'field': 'start_date',
                            'message': 'La fecha de inicio es muy antigua',
                            'code': 'OLD_DATE'
                        })
                except Exception:
                    validation_result['errors'].append({
                        'field': 'start_date',
                        'message': 'Formato de fecha de inicio inválido',
                        'code': 'INVALID_DATE_FORMAT'
                    })
            
            if end_date:
                try:
                    if isinstance(end_date, str):
                        end_date = pendulum.parse(end_date).date()
                    
                    # Validar que end_date sea posterior a start_date
                    if start_date and end_date <= start_date:
                        validation_result['errors'].append({
                            'field': 'end_date',
                            'message': 'La fecha de fin debe ser posterior a la fecha de inicio',
                            'code': 'INVALID_DATE_RANGE'
                        })
                except Exception:
                    validation_result['errors'].append({
                        'field': 'end_date',
                        'message': 'Formato de fecha de fin inválido',
                        'code': 'INVALID_DATE_FORMAT'
                    })
            
            # Validar campos booleanos
            is_leader = membership_data.get('is_leader')
            if is_leader is not None and not isinstance(is_leader, bool):
                validation_result['errors'].append({
                    'field': 'is_leader',
                    'message': 'El campo líder debe ser verdadero o falso',
                    'code': 'INVALID_BOOLEAN'
                })
            
            is_active = membership_data.get('is_active')
            if is_active is not None and not isinstance(is_active, bool):
                validation_result['errors'].append({
                    'field': 'is_active',
                    'message': 'El estado activo debe ser verdadero o falso',
                    'code': 'INVALID_BOOLEAN'
                })
            
            # Verificar conflictos de membresía si los IDs son válidos
            if team_id and employee_id:
                conflicts = await self.check_membership_conflicts(employee_id, team_id)
                if conflicts['has_conflicts']:
                    validation_result['errors'].extend([
                        {
                            'field': 'membership',
                            'message': conflict,
                            'code': 'MEMBERSHIP_CONFLICT'
                        }
                        for conflict in conflicts['conflicts']
                    ])
            
            # Determinar si es válido
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
            self._logger.debug(
                f"Validación de membresía completada: {'válida' if validation_result['is_valid'] else 'inválida'}, "
                f"{len(validation_result['errors'])} errores"
            )
            
            return validation_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al validar datos de membresía: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_membership_data",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar membresía: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="validate_membership_data",
                entity_type="TeamMembership",
                original_error=e
            )

    async def check_membership_conflicts(
        self, 
        employee_id: int, 
        team_id: int
    ) -> Dict[str, Any]:
        """
        Verifica conflictos de membresía para un empleado.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo
        
        Returns:
            Dict[str, Any]: Información sobre conflictos encontrados
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la verificación
        """
        try:
            self._logger.debug(
                f"Verificando conflictos de membresía: empleado {employee_id}, equipo {team_id}"
            )
            
            conflicts_info = {
                'has_conflicts': False,
                'conflicts': [],
                'existing_memberships': []
            }
            
            # Verificar membresía activa existente en el mismo equipo
            existing_membership_stmt = (
                select(TeamMembership)
                .where(
                    and_(
                        TeamMembership.employee_id == employee_id,
                        TeamMembership.team_id == team_id,
                        TeamMembership.is_active == True
                    )
                )
            )
            
            result = await self.session.execute(existing_membership_stmt)
            existing_membership = result.scalar_one_or_none()
            
            if existing_membership:
                conflicts_info['has_conflicts'] = True
                conflicts_info['conflicts'].append(
                    f"El empleado {employee_id} ya es miembro activo del equipo {team_id}"
                )
                conflicts_info['existing_memberships'].append({
                    'team_id': team_id,
                    'role': existing_membership.role,
                    'is_leader': existing_membership.is_leader,
                    'start_date': existing_membership.start_date.isoformat() if existing_membership.start_date else None
                })
            
            # Verificar si ya es líder de otro equipo (regla de negocio)
            leader_in_other_team_stmt = (
                select(TeamMembership)
                .options(selectinload(TeamMembership.team))
                .where(
                    and_(
                        TeamMembership.employee_id == employee_id,
                        TeamMembership.team_id != team_id,
                        TeamMembership.is_leader == True,
                        TeamMembership.is_active == True
                    )
                )
            )
            
            result = await self.session.execute(leader_in_other_team_stmt)
            other_leadership = result.scalars().all()
            
            if other_leadership:
                for leadership in other_leadership:
                    conflicts_info['conflicts'].append(
                        f"El empleado {employee_id} ya es líder del equipo {leadership.team.name} (ID: {leadership.team_id})"
                    )
                    conflicts_info['existing_memberships'].append({
                        'team_id': leadership.team_id,
                        'team_name': leadership.team.name,
                        'role': leadership.role,
                        'is_leader': True,
                        'start_date': leadership.start_date.isoformat() if leadership.start_date else None
                    })
                
                # Solo marcar como conflicto si se intenta asignar como líder
                # (esto se validaría en el contexto de uso)
                conflicts_info['has_conflicts'] = True
            
            # Obtener todas las membresías activas del empleado para contexto
            all_memberships_stmt = (
                select(TeamMembership)
                .options(selectinload(TeamMembership.team))
                .where(
                    and_(
                        TeamMembership.employee_id == employee_id,
                        TeamMembership.is_active == True
                    )
                )
            )
            
            result = await self.session.execute(all_memberships_stmt)
            all_memberships = result.scalars().all()
            
            # Agregar información de contexto
            conflicts_info['total_active_memberships'] = len(all_memberships)
            conflicts_info['teams_count'] = len(set(m.team_id for m in all_memberships))
            
            self._logger.debug(
                f"Verificación completada: {'conflictos encontrados' if conflicts_info['has_conflicts'] else 'sin conflictos'}, "
                f"{len(conflicts_info['conflicts'])} conflictos, {conflicts_info['total_active_memberships']} membresías activas"
            )
            
            return conflicts_info
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al verificar conflictos de membresía: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="check_membership_conflicts",
                entity_type="TeamMembership",
                entity_id=f"employee_{employee_id}_team_{team_id}"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al verificar conflictos: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="check_membership_conflicts",
                entity_type="TeamMembership",
                entity_id=f"employee_{employee_id}_team_{team_id}",
                original_error=e
            )

    async def validate_business_rules(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida reglas de negocio específicas.
        
        Args:
            operation: Tipo de operación (create, update, delete)
            data: Datos a validar
        
        Returns:
            Dict[str, Any]: Resultado de validación de reglas de negocio
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando reglas de negocio para operación: {operation}")
            
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            if operation == 'create_team':
                # Regla: No más de 50 equipos activos por departamento
                department = data.get('department')
                if department:
                    dept_teams_count = await self._count_teams_by_department(department, active_only=True)
                    if dept_teams_count >= 50:
                        validation_result['errors'].append({
                            'rule': 'max_teams_per_department',
                            'message': f'El departamento {department} ya tiene el máximo de equipos permitidos (50)',
                            'code': 'BUSINESS_RULE_VIOLATION'
                        })
            
            elif operation == 'assign_leader':
                # Regla: Un empleado no puede ser líder de más de 3 equipos
                employee_id = data.get('employee_id')
                if employee_id:
                    leadership_count = await self._count_employee_leaderships(employee_id)
                    if leadership_count >= 3:
                        validation_result['errors'].append({
                            'rule': 'max_leaderships_per_employee',
                            'message': f'El empleado {employee_id} ya es líder del máximo de equipos permitidos (3)',
                            'code': 'BUSINESS_RULE_VIOLATION'
                        })
            
            elif operation == 'add_member':
                # Regla: Un equipo no puede tener más de 30 miembros activos
                team_id = data.get('team_id')
                if team_id:
                    members_count = await self._count_team_members(team_id, active_only=True)
                    if members_count >= 30:
                        validation_result['errors'].append({
                            'rule': 'max_members_per_team',
                            'message': f'El equipo {team_id} ya tiene el máximo de miembros permitidos (30)',
                            'code': 'BUSINESS_RULE_VIOLATION'
                        })
                
                # Regla: Un empleado no puede estar en más de 5 equipos activos
                employee_id = data.get('employee_id')
                if employee_id:
                    employee_teams_count = await self._count_employee_teams(employee_id, active_only=True)
                    if employee_teams_count >= 5:
                        validation_result['errors'].append({
                            'rule': 'max_teams_per_employee',
                            'message': f'El empleado {employee_id} ya está en el máximo de equipos permitidos (5)',
                            'code': 'BUSINESS_RULE_VIOLATION'
                        })
            
            elif operation == 'delete_team':
                # Regla: No se puede eliminar un equipo con miembros activos
                team_id = data.get('team_id')
                if team_id:
                    active_members = await self._count_team_members(team_id, active_only=True)
                    if active_members > 0:
                        validation_result['errors'].append({
                            'rule': 'no_delete_team_with_members',
                            'message': f'No se puede eliminar el equipo {team_id} porque tiene {active_members} miembros activos',
                            'code': 'BUSINESS_RULE_VIOLATION'
                        })
            
            # Determinar si es válido
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
            self._logger.debug(
                f"Validación de reglas de negocio completada: {'válida' if validation_result['is_valid'] else 'inválida'}, "
                f"{len(validation_result['errors'])} violaciones"
            )
            
            return validation_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al validar reglas de negocio: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_business_rules",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar reglas de negocio: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="validate_business_rules",
                entity_type="Team",
                original_error=e
            )

    async def validate_data_consistency(self) -> Dict[str, Any]:
        """
        Valida la consistencia general de los datos.
        
        Returns:
            Dict[str, Any]: Reporte de consistencia de datos
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug("Validando consistencia de datos")
            
            consistency_report = {
                'is_consistent': True,
                'issues': [],
                'statistics': {},
                'recommendations': []
            }
            
            # Verificar equipos sin miembros activos
            teams_without_members_stmt = (
                select(Team.id, Team.name)
                .outerjoin(
                    TeamMembership,
                    and_(
                        TeamMembership.team_id == Team.id,
                        TeamMembership.is_active == True
                    )
                )
                .where(
                    and_(
                        Team.is_active == True,
                        TeamMembership.id.is_(None)
                    )
                )
            )
            
            result = await self.session.execute(teams_without_members_stmt)
            teams_without_members = result.all()
            
            if teams_without_members:
                consistency_report['issues'].append({
                    'type': 'teams_without_members',
                    'count': len(teams_without_members),
                    'message': f'{len(teams_without_members)} equipos activos sin miembros',
                    'severity': 'warning',
                    'teams': [{'id': team_id, 'name': name} for team_id, name in teams_without_members]
                })
                consistency_report['recommendations'].append(
                    'Considerar agregar miembros o desactivar equipos sin miembros'
                )
            
            # Verificar equipos sin líder
            teams_without_leader_stmt = (
                select(Team.id, Team.name)
                .outerjoin(
                    TeamMembership,
                    and_(
                        TeamMembership.team_id == Team.id,
                        TeamMembership.is_leader == True,
                        TeamMembership.is_active == True
                    )
                )
                .where(
                    and_(
                        Team.is_active == True,
                        TeamMembership.id.is_(None)
                    )
                )
            )
            
            result = await self.session.execute(teams_without_leader_stmt)
            teams_without_leader = result.all()
            
            if teams_without_leader:
                consistency_report['issues'].append({
                    'type': 'teams_without_leader',
                    'count': len(teams_without_leader),
                    'message': f'{len(teams_without_leader)} equipos activos sin líder',
                    'severity': 'warning',
                    'teams': [{'id': team_id, 'name': name} for team_id, name in teams_without_leader]
                })
                consistency_report['recommendations'].append(
                    'Asignar líderes a los equipos que no tienen uno'
                )
            
            # Verificar membresías con fechas inconsistentes
            inconsistent_dates_stmt = (
                select(TeamMembership.id, TeamMembership.team_id, TeamMembership.employee_id)
                .where(
                    and_(
                        TeamMembership.start_date.is_not(None),
                        TeamMembership.end_date.is_not(None),
                        TeamMembership.end_date <= TeamMembership.start_date
                    )
                )
            )
            
            result = await self.session.execute(inconsistent_dates_stmt)
            inconsistent_dates = result.all()
            
            if inconsistent_dates:
                consistency_report['is_consistent'] = False
                consistency_report['issues'].append({
                    'type': 'inconsistent_membership_dates',
                    'count': len(inconsistent_dates),
                    'message': f'{len(inconsistent_dates)} membresías con fechas inconsistentes',
                    'severity': 'error',
                    'memberships': [
                        {'id': mem_id, 'team_id': team_id, 'employee_id': emp_id}
                        for mem_id, team_id, emp_id in inconsistent_dates
                    ]
                })
                consistency_report['recommendations'].append(
                    'Corregir las fechas de inicio y fin de las membresías inconsistentes'
                )
            
            # Verificar múltiples líderes activos en el mismo equipo
            multiple_leaders_stmt = (
                select(
                    TeamMembership.team_id,
                    func.count(TeamMembership.id).label('leader_count')
                )
                .where(
                    and_(
                        TeamMembership.is_leader == True,
                        TeamMembership.is_active == True
                    )
                )
                .group_by(TeamMembership.team_id)
                .having(func.count(TeamMembership.id) > 1)
            )
            
            result = await self.session.execute(multiple_leaders_stmt)
            multiple_leaders = result.all()
            
            if multiple_leaders:
                consistency_report['is_consistent'] = False
                consistency_report['issues'].append({
                    'type': 'multiple_leaders_per_team',
                    'count': len(multiple_leaders),
                    'message': f'{len(multiple_leaders)} equipos con múltiples líderes activos',
                    'severity': 'error',
                    'teams': [
                        {'team_id': team_id, 'leader_count': count}
                        for team_id, count in multiple_leaders
                    ]
                })
                consistency_report['recommendations'].append(
                    'Asegurar que cada equipo tenga solo un líder activo'
                )
            
            # Estadísticas generales
            total_teams = await self.count_total_teams(active_only=False)
            active_teams = await self.count_total_teams(active_only=True)
            
            consistency_report['statistics'] = {
                'total_teams': total_teams,
                'active_teams': active_teams,
                'inactive_teams': total_teams - active_teams,
                'teams_without_members': len(teams_without_members),
                'teams_without_leader': len(teams_without_leader),
                'data_issues_count': len([issue for issue in consistency_report['issues'] if issue['severity'] == 'error'])
            }
            
            self._logger.info(
                f"Validación de consistencia completada: {'consistente' if consistency_report['is_consistent'] else 'inconsistente'}, "
                f"{len(consistency_report['issues'])} problemas encontrados"
            )
            
            return consistency_report
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al validar consistencia de datos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_data_consistency",
                entity_type="Team"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar consistencia: {e}")
            raise TeamRepositoryError(
                message=f"Error inesperado: {e}",
                operation="validate_data_consistency",
                entity_type="Team",
                original_error=e
            )

    # Métodos auxiliares privados
    
    async def _check_name_uniqueness(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si un nombre de equipo ya existe."""
        stmt = select(exists().where(Team.name == name))
        if exclude_id:
            stmt = select(exists().where(and_(Team.name == name, Team.id != exclude_id)))
        
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def _count_teams_by_department(self, department: str, active_only: bool = True) -> int:
        """Cuenta equipos por departamento."""
        stmt = select(func.count(Team.id)).where(Team.department == department)
        if active_only:
            stmt = stmt.where(Team.is_active == True)
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def _count_employee_leaderships(self, employee_id: int) -> int:
        """Cuenta liderazgos activos de un empleado."""
        stmt = (
            select(func.count(TeamMembership.id))
            .where(
                and_(
                    TeamMembership.employee_id == employee_id,
                    TeamMembership.is_leader == True,
                    TeamMembership.is_active == True
                )
            )
        )
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def _count_team_members(self, team_id: int, active_only: bool = True) -> int:
        """Cuenta miembros de un equipo."""
        stmt = select(func.count(TeamMembership.id)).where(TeamMembership.team_id == team_id)
        if active_only:
            stmt = stmt.where(TeamMembership.is_active == True)
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0
    
    async def _count_employee_teams(self, employee_id: int, active_only: bool = True) -> int:
        """Cuenta equipos de un empleado."""
        stmt = select(func.count(TeamMembership.id)).where(TeamMembership.employee_id == employee_id)
        if active_only:
            stmt = stmt.where(TeamMembership.is_active == True)
        
        result = await self.session.execute(stmt)
        return result.scalar() or 0