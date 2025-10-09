# src/planificador/services/domain/team/modules/crud_operations.py

"""
Módulo de Operaciones CRUD del Dominio Team.

Este módulo implementa las operaciones básicas de creación, lectura, actualización
y eliminación para equipos, proporcionando una capa de lógica de negocio sobre
el repositorio de equipos.

Características:
    - Validaciones de negocio antes de operaciones
    - Transformación de datos entre capas
    - Manejo de errores específico del dominio
    - Logging detallado de operaciones
    - Integración con múltiples repositorios

Principios de Diseño:
    - Single Responsibility: Solo operaciones CRUD
    - Dependency Injection: Repositorios inyectados
    - Error Handling: Conversión de errores de repositorio a dominio
    - Business Logic: Validaciones y reglas de negocio centralizadas

Uso:
    ```python
    crud_ops = TeamDomainCrudOperations(team_repo, membership_repo)
    team = await crud_ops.create_team(team_data)
    teams = await crud_ops.get_all_teams(page=1, page_size=20)
    ```
"""

from typing import List, Optional, Dict, Any, Tuple
from loguru import logger

from planificador.schemas.team.team_advanced_schemas import (
    TeamCreateSchema,
    TeamUpdateSchema,
    TeamSchema,
    PaginatedResponse
)
from planificador.repositories.team import TeamRepositoryFacade
from planificador.repositories.team_membership import TeamMembershipRepositoryFacade
from planificador.services.domain.team.interfaces.crud_operations_interface import (
    ITeamDomainCrudOperations
)
from planificador.exceptions.domain import (
    TeamDomainError
)
from planificador.exceptions.base import (
    ValidationError, NotFoundError, ConflictError
)
from planificador.exceptions.repository import (
    TeamRepositoryError, TeamMembershipRepositoryError
)


class TeamDomainCrudOperations(ITeamDomainCrudOperations):
    """
    Implementación de operaciones CRUD del dominio Team.
    
    Proporciona la lógica de negocio para operaciones básicas de equipos,
    incluyendo validaciones, transformaciones de datos y coordinación
    entre múltiples repositorios.
    
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
        Inicializa las operaciones CRUD del dominio Team.
        
        Args:
            team_repo: Repositorio de equipos
            membership_repo: Repositorio de membresías
        """
        self._team_repo = team_repo
        self._membership_repo = membership_repo
        self._logger = logger.bind(module="TeamDomainCrudOperations")
        
        self._logger.debug("TeamDomainCrudOperations inicializado")

    async def create_team(
        self, 
        team_data: TeamCreateSchema, 
        validate_business_rules: bool = True
    ) -> TeamSchema:
        """
        Crea un nuevo equipo con validación completa de datos de negocio y verificación de capacidad organizacional.
        
        Args:
            team_data: Datos del equipo a crear
            validate_business_rules: Si se deben validar las reglas de negocio
            
        Returns:
            TeamSchema: Equipo creado con información completa
            
        Raises:
            ValidationError: Si los datos no son válidos
            ConflictError: Si ya existe un equipo con el mismo nombre
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.info(f"Iniciando creación de equipo: {team_data.name}")
            
            # Validar datos de entrada
            if validate_business_rules:
                await self._validate_team_data(team_data.model_dump())
            
            # Verificar que no exista equipo con el mismo nombre en el departamento
            existing_team = await self._team_repo.get_team_by_name(team_data.name)
            if existing_team and existing_team.department == team_data.department:
                raise ConflictError(
                    f"Ya existe un equipo con el nombre '{team_data.name}' "
                    f"en el departamento '{team_data.department}'"
                )
            
            # Crear equipo en el repositorio
            team_dict = team_data.model_dump()
            created_team = await self._team_repo.create_team(team_dict)
            
            # Convertir a schema de salida
            team_output = TeamSchema.model_validate(created_team)
            
            self._logger.info(
                f"Equipo creado exitosamente: ID {created_team.id}, "
                f"Nombre: {created_team.name}"
            )
            
            return team_output
            
        except (TeamRepositoryError, TeamMembershipRepositoryError) as e:
            self._logger.error(f"Error de repositorio al crear equipo: {e}")
            raise TeamDomainError(
                f"Error al crear equipo: {e.message}",
                operation="create_team",
                entity_type="Team",
                original_error=e
            )
        except (ValidationError, ConflictError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al crear equipo: {e}")
            raise TeamDomainError(
                f"Error inesperado al crear equipo: {str(e)}",
                operation="create_team",
                entity_type="Team",
                original_error=e
            )

    async def get_team_by_id(
        self, 
        team_id: int, 
        include_members: bool = False
    ) -> Optional[TeamSchema]:
        """
        Obtiene un equipo específico por su identificador único con opción de incluir información detallada de miembros.
        
        Args:
            team_id: ID del equipo a buscar
            include_members: Si se debe incluir información de miembros
            
        Returns:
            Optional[TeamSchema]: Equipo encontrado o None si no existe
            
        Raises:
            ValidationError: Si el ID no es válido
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(f"Buscando equipo por ID: {team_id}")
            
            # Validar ID
            if team_id <= 0:
                raise ValidationError("El ID del equipo debe ser un número positivo")
            
            # Buscar en repositorio
            team = await self._team_repo.get_team_by_id(team_id)
            
            if team is None:
                self._logger.debug(f"Equipo no encontrado: ID {team_id}")
                return None
            
            # Si se requieren miembros, obtenerlos
            if include_members:
                members = await self._membership_repo.get_by_team_id(team_id)
                # Agregar miembros al objeto team si es necesario
                team_dict = team.__dict__.copy()
                team_dict['members'] = members
                team_output = TeamSchema.model_validate(team_dict)
            else:
                # Convertir a schema de salida
                team_output = TeamSchema.model_validate(team)
            
            self._logger.debug(f"Equipo encontrado: {team.name}")
            return team_output
            
        except (TeamRepositoryError, TeamMembershipRepositoryError) as e:
            self._logger.error(f"Error de repositorio al buscar equipo: {e}")
            raise TeamDomainError(
                f"Error al buscar equipo: {e.message}",
                operation="get_team_by_id",
                entity_type="Team",
                entity_id=team_id,
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar equipo: {e}")
            raise TeamDomainError(
                f"Error inesperado al buscar equipo: {str(e)}",
                operation="get_team_by_id",
                entity_type="Team",
                entity_id=team_id,
                original_error=e
            )

    async def get_teams(
        self,
        page: int = 1,
        page_size: int = 50,
        include_inactive: bool = False
    ) -> PaginatedResponse[TeamSchema]:
        """
        Obtiene todos los equipos del sistema con paginación y filtros de estado.
        
        Args:
            page: Número de página (base 1)
            page_size: Tamaño de página
            include_inactive: Si se deben incluir equipos inactivos
            
        Returns:
            PaginatedResponse[TeamSchema]: Respuesta paginada con equipos
            
        Raises:
            ValidationError: Si los parámetros de paginación no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(
                f"Obteniendo equipos: página {page}, tamaño {page_size}"
            )
            
            # Validar parámetros de paginación
            if page <= 0:
                raise ValidationError("El número de página debe ser positivo")
            if page_size <= 0 or page_size > 100:
                raise ValidationError(
                    "El tamaño de página debe estar entre 1 y 100"
                )
            
            # Configurar filtros basados en include_inactive
            filters = {}
            if not include_inactive:
                filters['is_active'] = True
            
            # Obtener equipos del repositorio
            teams, total = await self._team_repo.get_teams_with_pagination(
                page=page,
                page_size=page_size,
                filters=filters
            )
            
            # Convertir a schemas de salida
            team_schemas = [TeamSchema.model_validate(team) for team in teams]
            
            # Crear respuesta paginada
            paginated_response = PaginatedResponse[TeamSchema](
                items=team_schemas,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )
            
            self._logger.debug(
                f"Equipos obtenidos: {len(team_schemas)} de {total} total"
            )
            
            return paginated_response
            
        except (TeamRepositoryError, TeamMembershipRepositoryError) as e:
            self._logger.error(f"Error de repositorio al obtener equipos: {e}")
            raise TeamDomainError(
                f"Error al obtener equipos: {e.message}",
                operation="get_all_teams",
                entity_type="Team",
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener equipos: {e}")
            raise TeamDomainError(
                f"Error inesperado al obtener equipos: {str(e)}",
                operation="get_all_teams",
                entity_type="Team",
                original_error=e
            )

    async def update_team(
        self,
        team_id: int,
        update_data: TeamUpdateSchema,
        validate_changes: bool = True
    ) -> TeamSchema:
        """
        Actualiza la información de un equipo existente con validación de cambios y verificación de impacto.
        
        Args:
            team_id: ID del equipo a actualizar
            update_data: Datos de actualización del equipo
            validate_changes: Si se deben validar los cambios
            
        Returns:
            TeamSchema: Equipo actualizado
            
        Raises:
            ValidationError: Si los datos no son válidos
            NotFoundError: Si el equipo no existe
            ConflictError: Si hay conflicto con otro equipo
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.info(f"Actualizando equipo ID: {team_id}")
            
            # Validar ID
            if team_id <= 0:
                raise ValidationError("El ID del equipo debe ser un número positivo")
            
            # Verificar que el equipo existe
            existing_team = await self._team_repo.get_team_by_id(team_id)
            if not existing_team:
                raise NotFoundError(f"Equipo con ID {team_id} no encontrado")
            
            # Validar datos de actualización
            update_dict = update_data.model_dump(exclude_unset=True)
            if update_dict and validate_changes:
                await self._validate_team_data(update_dict, is_update=True)
            
            # Verificar conflictos de nombre si se está actualizando
            if 'name' in update_dict and update_dict['name'] != existing_team.name:
                conflicting_team = await self._team_repo.get_team_by_name(
                    update_dict['name']
                )
                if (conflicting_team and 
                    conflicting_team.id != team_id and
                    conflicting_team.department == update_dict.get('department', existing_team.department)):
                    raise ConflictError(
                        f"Ya existe un equipo con el nombre '{update_dict['name']}' "
                        f"en el departamento"
                    )
            
            # Actualizar en repositorio
            updated_team = await self._team_repo.update_team(team_id, update_dict)
            
            # Convertir a schema de salida
            team_output = TeamSchema.model_validate(updated_team)
            
            self._logger.info(f"Equipo actualizado exitosamente: ID {team_id}")
            
            return team_output
            
        except (TeamRepositoryError, TeamMembershipRepositoryError) as e:
            self._logger.error(f"Error de repositorio al actualizar equipo: {e}")
            raise TeamDomainError(
                f"Error al actualizar equipo: {e.message}",
                operation="update_team",
                entity_type="Team",
                entity_id=team_id,
                original_error=e
            )
        except (ValidationError, NotFoundError, ConflictError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al actualizar equipo: {e}")
            raise TeamDomainError(
                f"Error inesperado al actualizar equipo: {str(e)}",
                operation="update_team",
                entity_type="Team",
                entity_id=team_id,
                original_error=e
            )

    async def delete_team(
        self,
        team_id: int,
        force_delete: bool = False
    ) -> bool:
        """
        Elimina un equipo del sistema con verificación de dependencias y opción de eliminación forzada.
        
        Args:
            team_id: ID del equipo a eliminar
            force_delete: Si se debe forzar la eliminación
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Raises:
            NotFoundError: Si el equipo no existe
            ConflictError: Si el equipo tiene dependencias activas
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.info(f"Eliminando equipo ID: {team_id}")
            
            # Validar ID
            if team_id <= 0:
                raise ValidationError("El ID del equipo debe ser un número positivo")
            
            # Verificar que el equipo existe
            existing_team = await self._team_repo.get_team_by_id(team_id)
            if not existing_team:
                raise NotFoundError(f"Equipo con ID {team_id} no encontrado")
            
            # Verificar dependencias activas si no es eliminación forzada
            if not force_delete:
                # Verificar membresías activas
                active_memberships = await self._team_membership_repo.get_active_memberships_by_team(
                    team_id
                )
                if active_memberships:
                    raise ConflictError(
                        f"No se puede eliminar el equipo: tiene {len(active_memberships)} "
                        "membresías activas"
                    )
                
                # Verificar proyectos asignados (si existe repositorio de proyectos)
                # Esta verificación se puede expandir según las dependencias del dominio
            
            # Eliminar del repositorio
            success = await self._team_repo.delete_team(team_id)
            
            if success:
                self._logger.info(f"Equipo eliminado exitosamente: ID {team_id}")
            else:
                self._logger.warning(f"No se pudo eliminar el equipo: ID {team_id}")
            
            return success
            
        except (TeamRepositoryError, TeamMembershipRepositoryError) as e:
            self._logger.error(f"Error de repositorio al eliminar equipo: {e}")
            raise TeamDomainError(
                f"Error al eliminar equipo: {e.message}",
                operation="delete_team",
                entity_type="Team",
                entity_id=team_id,
                original_error=e
            )
        except (ValidationError, NotFoundError, ConflictError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al eliminar equipo: {e}")
            raise TeamDomainError(
                f"Error inesperado al eliminar equipo: {str(e)}",
                operation="delete_team",
                entity_type="Team",
                entity_id=team_id,
                original_error=e
            )

    async def bulk_create_teams(
        self,
        teams_data: List[TeamCreateSchema],
        validate_all: bool = True
    ) -> List[TeamSchema]:
        """
        Crea múltiples equipos en una sola operación con validación en lote y manejo de errores.
        
        Args:
            teams_data: Lista de datos para crear equipos
            validate_business_rules: Si se deben validar las reglas de negocio
            continue_on_error: Si continuar con otros equipos en caso de error
            
        Returns:
            List[TeamSchema]: Lista de equipos creados exitosamente
            
        Raises:
            ValidationError: Si los datos no son válidos
            ConflictError: Si hay conflictos entre equipos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.info(f"Creación masiva de {len(teams_data)} equipos")
            
            if not teams_data:
                raise ValidationError("La lista de equipos no puede estar vacía")
            
            created_teams = []
            errors = []
            
            # Procesar cada equipo
            for i, team_data in enumerate(teams_data):
                try:
                    # Validar datos individuales
                    team_dict = team_data.model_dump()
                    if validate_business_rules:
                        await self._validate_team_data(team_dict)
                    
                    # Verificar conflictos con equipos existentes
                    existing_team = await self._team_repo.get_team_by_name(team_data.name)
                    if existing_team and existing_team.department == team_data.department:
                        raise ConflictError(
                            f"Ya existe un equipo con el nombre '{team_data.name}' "
                            f"en el departamento '{team_data.department}'"
                        )
                    
                    # Crear equipo individual
                    created_team = await self._team_repo.create_team(team_dict)
                    team_schema = TeamSchema.model_validate(created_team)
                    created_teams.append(team_schema)
                    
                except Exception as e:
                    error_msg = f"Error en equipo {i + 1} ({team_data.name}): {str(e)}"
                    errors.append(error_msg)
                    
                    if not continue_on_error:
                        raise ValidationError(error_msg)
            
            # Si hay errores y continue_on_error es True, registrar advertencias
            if errors and continue_on_error:
                for error in errors:
                    self._logger.warning(error)
            
            self._logger.info(
                f"Creación masiva completada: {len(created_teams)} equipos creados, "
                f"{len(errors)} errores"
            )
            
            return created_teams
            
        except (TeamRepositoryError, TeamMembershipRepositoryError) as e:
            self._logger.error(f"Error de repositorio en creación masiva: {e}")
            raise TeamDomainError(
                f"Error en creación masiva: {e.message}",
                operation="bulk_create_teams",
                entity_type="Team",
                original_error=e
            )
        except (ValidationError, ConflictError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en creación masiva: {e}")
            raise TeamDomainError(
                f"Error inesperado en creación masiva: {str(e)}",
                operation="bulk_create_teams",
                entity_type="Team",
                original_error=e
            )

    async def _validate_team_data(
        self,
        team_data: Dict[str, Any],
        is_update: bool = False
    ) -> None:
        """
        Valida los datos de un equipo.
        
        Args:
            team_data: Datos del equipo a validar
            is_update: Si es una actualización (permite campos opcionales)
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validaciones básicas
        if not is_update:
            required_fields = ['name', 'department']
            for field in required_fields:
                if field not in team_data or not team_data[field]:
                    raise ValidationError(f"El campo '{field}' es obligatorio")
        
        # Validar nombre
        if 'name' in team_data:
            name = team_data['name']
            if not isinstance(name, str) or len(name.strip()) < 2:
                raise ValidationError(
                    "El nombre del equipo debe tener al menos 2 caracteres"
                )
            if len(name) > 100:
                raise ValidationError(
                    "El nombre del equipo no puede exceder 100 caracteres"
                )
        
        # Validar departamento
        if 'department' in team_data:
            department = team_data['department']
            if not isinstance(department, str) or len(department.strip()) < 2:
                raise ValidationError(
                    "El departamento debe tener al menos 2 caracteres"
                )
            if len(department) > 50:
                raise ValidationError(
                    "El departamento no puede exceder 50 caracteres"
                )
        
        # Validar descripción si está presente
        if 'description' in team_data and team_data['description']:
            description = team_data['description']
            if len(description) > 500:
                raise ValidationError(
                    "La descripción no puede exceder 500 caracteres"
                )
        
        # Validar is_active si está presente
        if 'is_active' in team_data:
            if not isinstance(team_data['is_active'], bool):
                raise ValidationError("El campo 'is_active' debe ser booleano")