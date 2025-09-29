# src/planificador/repositories/team_membership/validation_module.py

"""
Módulo de validación para el repositorio TeamMembership.

Este módulo implementa las operaciones de validación de datos,
reglas de negocio y consistencia para membresías de equipos,
siguiendo los patrones establecidos del proyecto.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de validación
    - Dependency Injection: Recibe dependencias por constructor
    - Error Handling: Manejo robusto de excepciones con logging estructurado
    - Async/Await: Operaciones asíncronas para mejor performance

Uso:
    ```python
    validation_module = TeamMembershipValidationModule(session, logger)
    is_valid = await validation_module.validate_membership_data(data)
    ```
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date

from loguru import logger
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.team_membership import MembershipRole as TeamRole
from planificador.schemas.team_membership import MembershipStatus
from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.repositories.base_repository import BaseRepository
from planificador.repositories.team_membership.interfaces.validation_interface import ITeamMembershipValidationOperations
from planificador.exceptions.repository import TeamMembershipRepositoryError, convert_sqlalchemy_error
from planificador.exceptions.validation import ValidationError


class TeamMembershipValidationModule(BaseRepository[TeamMembership], ITeamMembershipValidationOperations):
    """
    Módulo para operaciones de validación de membresías de equipos.
    
    Hereda de BaseRepository para operaciones estándar y implementa
    la interfaz ITeamMembershipValidationOperations para validaciones.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        _logger: Logger para registro de eventos
        model_class: Clase del modelo TeamMembership
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de validación de TeamMembership.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, TeamMembership)
        self._logger = logger.bind(module="TeamMembershipValidationModule")

    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[TeamMembership]:
        """
        Método abstracto para obtener una entidad por un campo único.
        
        Este método es requerido por BaseRepository, pero no es relevante
        para la lógica de validación. Se implementa para cumplir con la
        interfaz, pero no se espera que sea utilizado directamente.
        """
        self._logger.warning(
            f"Llamada a 'get_by_unique_field' en {self.__class__.__name__}, "
            f"que no debería ser usado para operaciones de validación."
        )
        return None
    
    
    async def validate_membership_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida los datos de una membresía.
        
        Args:
            data: Diccionario con datos de la membresía
        
        Returns:
            Tuple[bool, List[str]]: (es_válido, lista_de_errores)
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        try:
            self._logger.debug(f"Validando datos de membresía: {data}")
            
            errors = []
            
            # Validar campos requeridos
            required_fields = ['employee_id', 'team_id', 'role', 'start_date']
            for field in required_fields:
                if field not in data or data[field] is None:
                    errors.append(f"Campo requerido faltante: {field}")
            
            # Validar tipos de datos
            if 'employee_id' in data and not isinstance(data['employee_id'], int):
                errors.append("employee_id debe ser un entero")
            
            if 'team_id' in data and not isinstance(data['team_id'], int):
                errors.append("team_id debe ser un entero")
            
            if 'role' in data and not isinstance(data['role'], MembershipRole):
                errors.append("role debe ser un MembershipRole válido")
            
            if 'start_date' in data and not isinstance(data['start_date'], date):
                errors.append("start_date debe ser una fecha válida")
            
            if 'end_date' in data and data['end_date'] is not None and not isinstance(data['end_date'], date):
                errors.append("end_date debe ser una fecha válida o None")
            
            if 'is_active' in data and not isinstance(data['is_active'], bool):
                errors.append("is_active debe ser un booleano")
            
            # Validar lógica de fechas
            if ('start_date' in data and 'end_date' in data and 
                data['start_date'] and data['end_date'] and 
                data['start_date'] > data['end_date']):
                errors.append("La fecha de inicio no puede ser posterior a la fecha de fin")
            
            # Validar fechas futuras
            if 'start_date' in data and data['start_date'] and data['start_date'] > date.today():
                # Permitir fechas futuras pero advertir
                self._logger.warning(f"Fecha de inicio en el futuro: {data['start_date']}")
            
            is_valid = len(errors) == 0
            self._logger.debug(f"Validación completada: válido={is_valid}, errores={len(errors)}")
            
            return is_valid, errors
            
        except Exception as e:
            self._logger.error(f"Error inesperado al validar datos de membresía: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_membership_data",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def validate_membership_id(self, membership_id: int) -> bool:
        """
        Valida que un ID de membresía exista.
        
        Args:
            membership_id: ID de la membresía
        
        Returns:
            bool: True si existe, False si no
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        try:
            self._logger.debug(f"Validando ID de membresía: {membership_id}")
            
            if not isinstance(membership_id, int) or membership_id <= 0:
                return False
            
            membership = await self.get_by_id(membership_id)
            exists = membership is not None
            
            self._logger.debug(f"ID de membresía {membership_id} existe: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al validar ID de membresía: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_membership_id",
                entity_type="TeamMembership",
                entity_id=membership_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar ID de membresía: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_membership_id",
                entity_type="TeamMembership",
                entity_id=membership_id,
                original_error=e
            )
    
    async def validate_employee_id(self, employee_id: int) -> bool:
        """
        Valida que un ID de empleado exista.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            bool: True si existe, False si no
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        try:
            self._logger.debug(f"Validando ID de empleado: {employee_id}")
            
            if not isinstance(employee_id, int) or employee_id <= 0:
                return False
            
            # Verificar si el empleado tiene al menos una membresía
            # (asumiendo que si tiene membresías, el empleado existe)
            query = select(func.count(TeamMembership.id)).where(
                TeamMembership.employee_id == employee_id
            )
            
            result = await self.session.execute(query)
            count = result.scalar()
            
            exists = count > 0
            self._logger.debug(f"ID de empleado {employee_id} existe: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al validar ID de empleado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_employee_id",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar ID de empleado: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_employee_id",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def validate_team_id(self, team_id: int) -> bool:
        """
        Valida que un ID de equipo exista.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            bool: True si existe, False si no
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        try:
            self._logger.debug(f"Validando ID de equipo: {team_id}")
            
            if not isinstance(team_id, int) or team_id <= 0:
                return False
            
            # Verificar si el equipo tiene al menos una membresía
            # (asumiendo que si tiene membresías, el equipo existe)
            query = select(func.count(TeamMembership.id)).where(
                TeamMembership.team_id == team_id
            )
            
            result = await self.session.execute(query)
            count = result.scalar()
            
            exists = count > 0
            self._logger.debug(f"ID de equipo {team_id} existe: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al validar ID de equipo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_team_id",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar ID de equipo: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_team_id",
                entity_type="TeamMembership",
                original_error=e
            )

    async def validate_membership_role(self, role: MembershipRole) -> Tuple[bool, List[str]]:
        """
        Valida el rol de la membresía.

        Args:
            role: Rol a validar.

        Returns:
            Tuple[bool, List[str]]: (es_valido, errores).
        """
        try:
            self._logger.debug(f"Validando rol de membresía: {role}")
            
            errors = []
            if not isinstance(role, MembershipRole):
                errors.append(f"El rol debe ser una instancia de MembershipRole, no {type(role).__name__}")
            
            is_valid = len(errors) == 0
            self._logger.debug(f"Validación de rol: válido={is_valid}")
            return is_valid, errors
            
        except Exception as e:
            self._logger.error(f"Error inesperado al validar rol: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_membership_role",
                entity_type="MembershipRole",
                original_error=e
            )

    async def validate_membership_status(self, status: MembershipStatus) -> Tuple[bool, List[str]]:
        """
        Valida el estado de la membresía.

        Args:
            status: Estado a validar.

        Returns:
            Tuple[bool, List[str]]: (es_valido, errores).
        """
        self._logger.warning("`validate_membership_status` no implementado, retornando True por defecto.")
        return True, []

    async def validate_date_range(
        self,
        start_date: date,
        end_date: Optional[date] = None
    ) -> Tuple[bool, List[str]]:
        """
        Valida un rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin (opcional)
        
        Returns:
            Tuple[bool, List[str]]: (es_válido, lista_de_errores)
        """
        try:
            self._logger.debug(f"Validando rango de fechas: {start_date} - {end_date}")
            
            errors = []
            
            # Validar tipos
            if not isinstance(start_date, date):
                errors.append("start_date debe ser una fecha válida")
            
            if end_date is not None and not isinstance(end_date, date):
                errors.append("end_date debe ser una fecha válida o None")
            
            # Validar lógica
            if (isinstance(start_date, date) and isinstance(end_date, date) and 
                start_date > end_date):
                errors.append("La fecha de inicio no puede ser posterior a la fecha de fin")
            
            # Validar fechas muy antiguas (más de 50 años)
            if isinstance(start_date, date):
                min_date = date.today().replace(year=date.today().year - 50)
                if start_date < min_date:
                    errors.append(f"La fecha de inicio es muy antigua (anterior a {min_date})")
            
            is_valid = len(errors) == 0
            self._logger.debug(f"Validación de rango completada: válido={is_valid}")
            
            return is_valid, errors
            
        except Exception as e:
            self._logger.error(f"Error al validar rango de fechas: {e}")
            return False, [f"Error inesperado: {e}"]
    
    async def validate_membership_overlap(
        self,
        employee_id: int,
        start_date: date,
        end_date: Optional[date] = None,
        exclude_membership_id: Optional[int] = None
    ) -> Tuple[bool, List[TeamMembership]]:
        """
        Valida si hay solapamiento de membresías para un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio de la nueva membresía
            end_date: Fecha de fin de la nueva membresía (opcional)
            exclude_membership_id: ID de membresía a excluir (opcional)
        
        Returns:
            Tuple[bool, List[TeamMembership]]: (sin_solapamiento, membresías_solapadas)
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        try:
            self._logger.debug(f"Validando solapamiento para empleado {employee_id}")
            
            end_ref = end_date or date.today()
            
            query = select(TeamMembership).where(
                and_(
                    TeamMembership.employee_id == employee_id,
                    TeamMembership.start_date <= end_ref,
                    or_(
                        TeamMembership.end_date.is_(None),
                        TeamMembership.end_date >= start_date
                    )
                )
            )
            
            if exclude_membership_id:
                query = query.where(TeamMembership.id != exclude_membership_id)
            
            result = await self.session.execute(query)
            overlapping = result.scalars().all()
            
            has_overlap = len(overlapping) > 0
            self._logger.debug(f"Solapamiento detectado: {has_overlap}, membresías: {len(overlapping)}")
            
            return not has_overlap, list(overlapping)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al validar solapamiento: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_membership_overlap",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar solapamiento: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_membership_overlap",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def validate_leadership_assignment(
        self,
        team_id: int,
        role: MembershipRole,
        exclude_membership_id: Optional[int] = None
    ) -> Tuple[bool, List[str]]:
        """
        Valida asignaciones de liderazgo en un equipo.
        
        Args:
            team_id: ID del equipo
            role: Rol a asignar
            exclude_membership_id: ID de membresía a excluir (opcional)
        
        Returns:
            Tuple[bool, List[str]]: (es_válido, lista_de_errores)
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        try:
            self._logger.debug(f"Validando asignación de liderazgo en equipo {team_id}, rol {role}")
            
            errors = []
            
            # Solo validar para roles de liderazgo
            leadership_roles = [MembershipRole.LEAD, MembershipRole.SUPERVISOR, MembershipRole.COORDINATOR]
            
            if role not in leadership_roles:
                return True, []  # No hay restricciones para roles regulares
            
            # Contar líderes actuales del mismo tipo
            query = select(func.count(TeamMembership.id)).where(
                and_(
                    TeamMembership.team_id == team_id,
                    TeamMembership.role == role,
                    TeamMembership.is_active == True
                )
            )
            
            if exclude_membership_id:
                query = query.where(TeamMembership.id != exclude_membership_id)
            
            result = await self.session.execute(query)
            current_count = result.scalar() or 0
            
            # Reglas de negocio para liderazgo
            max_limits = {
                MembershipRole.LEAD: 1,  # Solo un líder por equipo
                MembershipRole.SUPERVISOR: 2,  # Máximo 2 supervisores
                MembershipRole.COORDINATOR: 3  # Máximo 3 coordinadores
            }
            
            max_allowed = max_limits.get(role, 1)
            
            if current_count >= max_allowed:
                errors.append(f"El equipo ya tiene el máximo de {role.value}s permitidos ({max_allowed})")
            
            is_valid = len(errors) == 0
            self._logger.debug(f"Validación de liderazgo: válido={is_valid}, líderes actuales={current_count}")
            
            return is_valid, errors
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al validar liderazgo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_leadership_assignment",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar liderazgo: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado en validación: {e}",
                operation="validate_leadership_assignment",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def validate_team_capacity(
        self,
        team_id: int,
        as_of_date: Optional[date] = None
    ) -> Tuple[bool, List[str]]:
        """Valida que un equipo no excede su capacidad máxima."""
        self._logger.warning("La validación de capacidad del equipo no está completamente implementada.")
        return True, []

    async def validate_role_permissions(
        self,
        employee_id: int,
        role: MembershipRole,
        team_id: int
    ) -> bool:
        """Valida que un empleado tiene permisos para un rol."""
        self._logger.warning("La validación de permisos de rol no está completamente implementada.")
        return True

    async def validate_business_rules(
        self,
        employee_id: int,
        role: MembershipRole,
        team_id: int
    ) -> Tuple[bool, List[str]]:
        """
        Valida reglas de negocio específicas.
        
        Args:
            employee_id: ID del empleado
            role: Rol de la membresía
            team_id: ID del equipo
        
        Returns:
            Tuple[bool, List[str]]: (cumple_reglas, lista_de_violaciones)
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        self._logger.warning("La validación de reglas de negocio no está completamente implementada.")
        return True, []

    async def validate_membership_transition(
        self,
        old_status: "MembershipStatus",
        new_status: "MembershipStatus"
    ) -> Tuple[bool, List[str]]:
        """Valida la transición entre estados de membresía."""
        self._logger.warning("La validación de transición de membresía no está implementada.")
        return True, []

    async def validate_membership_end_date(
        self,
        membership: "TeamMembership",
        end_date: date
    ) -> Tuple[bool, List[str]]:
        """Valida la fecha de finalización de una membresía."""
        self._logger.warning("La validación de fecha de fin de membresía no está implementada.")
        return True, []

    async def validate_data_consistency(
        self,
        membership: "TeamMembership"
    ) -> Tuple[bool, List[str]]:
        """Valida la consistencia de los datos de una membresía."""
        self._logger.warning("La validación de consistencia de datos no está implementada.")
        return True, []

    async def validate_search_criteria(
        self,
        criteria: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Valida los criterios de búsqueda para membresías."""
        self._logger.warning("La validación de criterios de búsqueda no está implementada.")
        return True, []

    async def validate_bulk_operation_data(
        self,
        data_list: List[Dict[str, Any]]
    ) -> Tuple[bool, Dict[int, List[str]]]:
        """Valida los datos para operaciones masivas."""
        self._logger.warning("La validación de datos para operaciones masivas no está implementada.")
        return True, {}

    async def validate_concurrent_membership_limit(
        self,
        employee_id: int,
        as_of_date: Optional[date] = None
    ) -> Tuple[bool, List[str]]:
        """Valida el límite de membresías concurrentes para un empleado."""
        self._logger.warning("La validación de límite de membresías concurrentes no está implementada.")
        return True, []