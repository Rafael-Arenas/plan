# src/planificador/services/domain/team/modules/membership_operations.py

"""
Módulo de Operaciones de Membresía del Dominio Team.

Este módulo implementa las operaciones relacionadas con la gestión de membresías
de equipos, proporcionando funcionalidad para agregar, remover y gestionar
miembros de equipos con validaciones de negocio apropiadas.

Características:
    - Gestión completa de membresías de equipos
    - Validaciones de roles y liderazgo
    - Control de fechas de inicio y fin
    - Prevención de conflictos de membresía
    - Logging detallado de operaciones

Principios de Diseño:
    - Single Responsibility: Solo operaciones de membresía
    - Business Logic: Validaciones específicas del dominio
    - Error Handling: Manejo robusto de errores
    - Data Integrity: Garantía de integridad de datos

Uso:
    ```python
    membership_ops = TeamDomainMembershipOperations(team_repo, membership_repo)
    await membership_ops.add_team_member(team_id, employee_id, "Developer")
    members = await membership_ops.get_team_members(team_id)
    ```
"""

from typing import List, Optional, Dict, Any
from datetime import date
from loguru import logger

from planificador.schemas.team.team import (
    TeamMembershipCreate, TeamMembershipUpdate
)
from planificador.schemas.team.team_advanced_schemas import TeamMembershipSchema
from planificador.repositories.team import TeamRepositoryFacade
from planificador.repositories.team_membership import TeamMembershipRepositoryFacade
from planificador.services.domain.team.interfaces.membership_operations_interface import (
    ITeamDomainMembershipOperations
)
from planificador.exceptions.domain import (
    TeamDomainError, ValidationError, NotFoundError, ConflictError
)
from planificador.exceptions.repository import (
    TeamRepositoryError, TeamMembershipRepositoryError
)


class TeamDomainMembershipOperations(ITeamDomainMembershipOperations):
    """
    Implementación de operaciones de membresía del dominio Team.
    
    Proporciona la lógica de negocio para la gestión de membresías de equipos,
    incluyendo validaciones de roles, control de liderazgo y prevención
    de conflictos.
    
    Attributes:
        _team_repo: Repositorio de equipos
        _membership_repo: Repositorio de membresías
        _logger: Logger para registro de eventos
    """

    def __init__(
        self,
        team_repo: TeamRepositoryFacade,
        membership_repo: TeamMembershipRepositoryFacade
    ):
        """
        Inicializa las operaciones de membresía del dominio Team.
        
        Args:
            team_repo: Repositorio de equipos
            membership_repo: Repositorio de membresías
        """
        self._team_repo = team_repo
        self._membership_repo = membership_repo
        self._logger = logger.bind(module="TeamDomainMembershipOperations")
        
        self._logger.debug("TeamDomainMembershipOperations inicializado")

    async def add_team_member(
        self,
        team_id: int,
        employee_id: int,
        role: MembershipRole,
        start_date: Optional[date] = None
    ) -> TeamMembershipSchema:
        """
        Agrega un miembro a un equipo con validaciones de negocio.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            role: Rol del miembro en el equipo
            start_date: Fecha de inicio (opcional, por defecto hoy)
            
        Returns:
            TeamMembershipSchema: Datos de la membresía creada
            
        Raises:
            TeamNotFoundError: Si el equipo no existe
            EmployeeNotFoundError: Si el empleado no existe
            TeamMembershipAlreadyExistsError: Si el empleado ya es miembro del equipo
            TeamCapacityExceededError: Si el equipo ha alcanzado su capacidad máxima
            TeamDomainError: Para otros errores de dominio
        """
        try:
            self._logger.info(
                f"Agregando miembro: empleado {employee_id} al equipo {team_id} "
                f"como {role}{'(líder)' if is_leader else ''}"
            )
            
            # Validar parámetros
            await self._validate_membership_params(team_id, employee_id, role)
            
            # Verificar que el equipo existe y está activo
            team = await self._team_repo.get_team_by_id(team_id)
            if not team:
                raise NotFoundError(f"Equipo con ID {team_id} no encontrado")
            if not team.is_active:
                raise ConflictError(f"No se puede agregar miembros a un equipo inactivo")
            
            # Verificar que no existe membresía activa
            existing_membership = await self._membership_repo.get_by_team_and_employee(
                team_id, employee_id, active_only=True
            )
            if existing_membership:
                raise ConflictError(
                    f"El empleado {employee_id} ya es miembro activo del equipo {team_id}"
                )
            
            # Validar liderazgo si es necesario
            if is_leader:
                await self._validate_leadership_assignment(team_id, employee_id)
            
            # Crear datos de membresía
            membership_data = TeamMembershipCreate(
                team_id=team_id,
                employee_id=employee_id,
                role=role,
                start_date=start_date or date.today(),
                is_active=True
            )
            
            # Crear membresía en repositorio
            created_membership = await self._membership_repo.create_membership(
                membership_data
            )
            
            # Convertir a schema de salida
            membership_schema = TeamMembershipSchema.model_validate(created_membership)
            
            logger.info(
                f"Miembro {employee_id} agregado exitosamente al equipo {team_id} "
                f"con rol {role.value}"
            )
            
            return membership_schema
            
        except (TeamRepositoryError, TeamMembershipRepositoryError) as e:
            self._logger.error(f"Error de repositorio al agregar miembro: {e}")
            raise TeamDomainError(
                f"Error al agregar miembro: {e.message}",
                operation="add_team_member",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}",
                original_error=e
            )
        except (ValidationError, NotFoundError, ConflictError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al agregar miembro: {e}")
            raise TeamDomainError(
                f"Error inesperado al agregar miembro: {str(e)}",
                operation="add_team_member",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}",
                original_error=e
            )

    async def remove_team_member(
        self,
        team_id: int,
        employee_id: int
    ) -> bool:
        """
        Remueve un miembro de un equipo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            
        Returns:
            bool: True si se removió exitosamente
            
        Raises:
            TeamNotFoundError: Si el equipo no existe
            EmployeeNotFoundError: Si el empleado no existe
            TeamMembershipNotFoundError: Si la membresía no existe
            TeamDomainError: Para otros errores de dominio
        """
        try:
            logger.info(
                f"Removiendo miembro: empleado {employee_id} del equipo {team_id}"
            )
            
            # Buscar la membresía activa
            membership = await self.membership_repository.get_by_team_and_employee(
                team_id, employee_id, active_only=True
            )
            
            if not membership:
                raise NotFoundError(
                    f"No se encontró membresía activa para empleado {employee_id} en equipo {team_id}"
                )
            
            # Desactivar la membresía
            await self.membership_repository.deactivate(membership.id)
            
            logger.info(f"Miembro {employee_id} removido exitosamente del equipo {team_id}")
            return True
            
        except (TeamRepositoryError, TeamMembershipRepositoryError) as e:
            self._logger.error(f"Error de repositorio al remover miembro: {e}")
            raise TeamDomainError(
                f"Error al remover miembro: {e.message}",
                operation="remove_team_member",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}",
                original_error=e
            )
        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al remover miembro: {e}")
            raise TeamDomainError(
                f"Error inesperado al remover miembro: {str(e)}",
                operation="remove_team_member",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}",
                original_error=e
            )

    async def update_member_role(
        self,
        team_id: int,
        employee_id: int,
        new_role: MembershipRole
    ) -> TeamMembershipSchema:
        """
        Actualiza el rol de un miembro del equipo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            new_role: Nuevo rol del miembro
            
        Returns:
            TeamMembershipSchema: Datos actualizados de la membresía
            
        Raises:
            TeamNotFoundError: Si el equipo no existe
            EmployeeNotFoundError: Si el empleado no existe
            TeamMembershipNotFoundError: Si la membresía no existe
            TeamDomainError: Para otros errores de dominio
        """
        try:
            logger.info(
                f"Actualizando rol: empleado {employee_id} en equipo {team_id} "
                f"a {new_role.value}"
            )
            
            # Buscar la membresía activa
            membership = await self.membership_repository.get_by_team_and_employee(
                team_id, employee_id, active_only=True
            )
            
            if not membership:
                raise NotFoundError(
                    f"No se encontró membresía activa para empleado {employee_id} en equipo {team_id}"
                )
            
            # Actualizar el rol
            update_data = TeamMembershipUpdate(role=new_role)
            updated_membership = await self.membership_repository.update(
                membership.id, update_data
            )
            
            # Convertir a schema de salida
            membership_schema = TeamMembershipSchema(
                id=updated_membership.id,
                team_id=updated_membership.team_id,
                employee_id=updated_membership.employee_id,
                role=updated_membership.role,
                start_date=updated_membership.start_date,
                end_date=updated_membership.end_date,
                is_active=updated_membership.is_active,
                created_at=updated_membership.created_at,
                updated_at=updated_membership.updated_at
            )
            
            logger.info(f"Rol actualizado exitosamente para empleado {employee_id} en equipo {team_id}")
            return membership_schema
            
        except (TeamRepositoryError, TeamMembershipRepositoryError) as e:
            self._logger.error(f"Error de repositorio al actualizar rol: {e}")
            raise TeamDomainError(
                f"Error al actualizar rol: {e.message}",
                operation="update_member_role",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}",
                original_error=e
            )
        except (ValidationError, NotFoundError, ConflictError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al actualizar rol: {e}")
            raise TeamDomainError(
                f"Error inesperado al actualizar rol: {str(e)}",
                operation="update_member_role",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}_employee_{employee_id}",
                original_error=e
            )

    async def get_team_members(
        self,
        team_id: int,
        active_only: bool = True
    ) -> List[TeamMembershipSchema]:
        """
        Obtiene los miembros de un equipo.
        
        Args:
            team_id: ID del equipo
            active_only: Si solo incluir miembros activos
            
        Returns:
            List[TeamMembershipSchema]: Lista de membresías del equipo
            
        Raises:
            ValidationError: Si el ID del equipo no es válido
            NotFoundError: Si el equipo no existe
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            logger.debug(
                f"Obteniendo miembros del equipo {team_id} "
                f"({'activos' if active_only else 'todos'})"
            )
            
            # Obtener membresías del repositorio
            memberships = await self.membership_repository.get_by_team_id(
                team_id, active_only=active_only
            )
            
            # Convertir a schemas de salida
            membership_schemas = [
                TeamMembershipSchema(
                    id=membership.id,
                    team_id=membership.team_id,
                    employee_id=membership.employee_id,
                    role=membership.role,
                    start_date=membership.start_date,
                    end_date=membership.end_date,
                    is_active=membership.is_active,
                    created_at=membership.created_at,
                    updated_at=membership.updated_at
                )
                for membership in memberships
            ]
            
            logger.debug(
                f"Miembros obtenidos: {len(membership_schemas)} para equipo {team_id}"
            )
            
            return membership_schemas
            
        except (TeamRepositoryError, TeamMembershipRepositoryError) as e:
            self._logger.error(f"Error de repositorio al obtener miembros: {e}")
            raise TeamDomainError(
                f"Error al obtener miembros: {e.message}",
                operation="get_team_members",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}",
                original_error=e
            )
        except (ValidationError, NotFoundError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener miembros: {e}")
            raise TeamDomainError(
                f"Error inesperado al obtener miembros: {str(e)}",
                operation="get_team_members",
                entity_type="TeamMembership",
                entity_id=f"team_{team_id}",
                original_error=e
            )

    async def _validate_membership_params(
        self,
        team_id: int,
        employee_id: int,
        role: str
    ) -> None:
        """
        Valida los parámetros básicos de membresía.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            role: Rol del miembro
            
        Raises:
            ValidationError: Si algún parámetro no es válido
        """
        if team_id <= 0:
            raise ValidationError("El ID del equipo debe ser positivo")
        
        if employee_id <= 0:
            raise ValidationError("El ID del empleado debe ser positivo")
        
        if not role or not isinstance(role, str):
            raise ValidationError("El rol es obligatorio y debe ser texto")
        
        if len(role.strip()) < 2:
            raise ValidationError("El rol debe tener al menos 2 caracteres")
        
        if len(role) > 50:
            raise ValidationError("El rol no puede exceder 50 caracteres")

    async def _validate_leadership_assignment(
        self,
        team_id: int,
        employee_id: int
    ) -> None:
        """
        Valida la asignación de liderazgo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            
        Raises:
            ConflictError: Si ya existe un líder en el equipo
        """
        # Verificar si ya existe un líder en el equipo
        current_leaders = await self._membership_repo.get_team_leaders(team_id)
        
        if current_leaders:
            # Verificar que no sea el mismo empleado
            for leader in current_leaders:
                if leader.employee_id != employee_id:
                    raise ConflictError(
                        f"El equipo {team_id} ya tiene un líder "
                        f"(empleado {leader.employee_id})"
                    )

    async def _validate_leadership_removal(
        self,
        team_id: int,
        employee_id: int
    ) -> None:
        """
        Valida la remoción de liderazgo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            
        Raises:
            ConflictError: Si es el único líder del equipo
        """
        # Obtener todos los líderes del equipo
        current_leaders = await self._membership_repo.get_team_leaders(team_id)
        
        # Verificar que no sea el único líder
        if len(current_leaders) == 1 and current_leaders[0].employee_id == employee_id:
            # Verificar si hay otros miembros activos que puedan ser líderes
            all_members = await self._membership_repo.get_by_team_id(
                team_id, active_only=True
            )
            
            if len(all_members) > 1:
                raise ConflictError(
                    f"No se puede remover el liderazgo: el empleado {employee_id} "
                    f"es el único líder del equipo {team_id}. "
                    "Asigne otro líder antes de remover este."
                )