# src/planificador/repositories/team/modules/crud_module.py

"""
Módulo CRUD para operaciones básicas del repositorio Team.

Este módulo implementa las operaciones de creación, actualización y eliminación
de registros de equipos, delegando en BaseRepository para operaciones estándar.

Principios de Diseño:
    - Single Responsibility: Solo operaciones CRUD básicas
    - Delegation Pattern: Delega en BaseRepository para operaciones estándar
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    crud_module = TeamCrudModule(session)
    team = await crud_module.create_team(team_data)
    updated_team = await crud_module.update_team(team_id, update_data)
    success = await crud_module.delete_team(team_id)
    ```
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.team import Team
from planificador.repositories.base_repository import BaseRepository
from planificador.repositories.team.interfaces.crud_interface import ITeamCrudOperations
from planificador.exceptions.repository import TeamRepositoryError


class TeamCrudModule(BaseRepository[Team], ITeamCrudOperations):
    """
    Módulo para operaciones CRUD del repositorio Team.
    
    Implementa las operaciones de creación, actualización y eliminación
    de registros de equipos en la base de datos, delegando en BaseRepository
    para operaciones estándar y agregando lógica específica de equipos.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Team
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo CRUD para equipos.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Team)
        self._logger = self._logger.bind(component="TeamCrudModule")
        self._logger.debug("TeamCrudModule inicializado")

    async def create_team(self, team_data: Dict[str, Any]) -> Team:
        """
        Crea un nuevo equipo delegando en el repositorio base.
        
        Args:
            team_data: Diccionario con datos del equipo
                - name: Nombre del equipo (requerido)
                - description: Descripción del equipo (opcional)
                - department: Departamento al que pertenece (requerido)
                - is_active: Estado activo (opcional, default True)
                - created_at: Fecha de creación (opcional, se asigna automáticamente)
        
        Returns:
            Team: El equipo creado con todos sus datos
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la creación
        """
        self._logger.debug(
            f"Creando equipo: {team_data.get('name', 'Sin nombre')} "
            f"en departamento: {team_data.get('department', 'Sin departamento')}"
        )
        
        # Asegurar que is_active tenga un valor por defecto
        team_data_copy = team_data.copy()
        if 'is_active' not in team_data_copy:
            team_data_copy['is_active'] = True
        
        created_team = await self.create(team_data_copy)
        
        self._logger.info(
            f"Equipo creado exitosamente: ID {created_team.id}, "
            f"Nombre: {created_team.name}"
        )
        
        return created_team

    async def update_team(
        self, 
        team_id: int, 
        update_data: Dict[str, Any]
    ) -> Team:
        """
        Actualiza un equipo existente delegando en el repositorio base.
        
        Args:
            team_id: ID del equipo a actualizar
            update_data: Diccionario con datos a actualizar
                - name: Nuevo nombre (opcional)
                - description: Nueva descripción (opcional)
                - department: Nuevo departamento (opcional)
                - is_active: Nuevo estado activo (opcional)
        
        Returns:
            Team: El equipo actualizado con los nuevos datos
        
        Raises:
            TeamRepositoryError: Si el equipo no existe o ocurre un error
        """
        self._logger.debug(
            f"Actualizando equipo con ID {team_id} con datos: {update_data}"
        )
        
        updated_team = await self.update(team_id, update_data)
        if not updated_team:
            raise TeamRepositoryError(
                message=f"Equipo con ID {team_id} no encontrado para actualización",
                operation="update_team",
                entity_type="Team",
                entity_id=team_id
            )
        
        self._logger.info(
            f"Equipo actualizado exitosamente: ID {team_id}, "
            f"Nombre: {updated_team.name}"
        )
        
        return updated_team

    async def delete_team(self, team_id: int) -> bool:
        """
        Elimina un equipo delegando en el repositorio base.
        
        Args:
            team_id: ID del equipo a eliminar
        
        Returns:
            bool: True si el equipo fue eliminado exitosamente
        
        Raises:
            TeamRepositoryError: Si el equipo no existe o no puede ser eliminado
        """
        self._logger.debug(f"Eliminando equipo con ID {team_id}")
        
        # Verificar que el equipo existe antes de intentar eliminarlo
        existing_team = await self.get_by_id(team_id)
        if not existing_team:
            raise TeamRepositoryError(
                message=f"Equipo con ID {team_id} no encontrado para eliminación",
                operation="delete_team",
                entity_type="Team",
                entity_id=team_id
            )
        
        success = await self.delete(team_id)
        
        if success:
            self._logger.info(
                f"Equipo eliminado exitosamente: ID {team_id}, "
                f"Nombre: {existing_team.name}"
            )
        else:
            self._logger.warning(
                f"No se pudo eliminar el equipo con ID {team_id}"
            )
        
        return success

    async def get_by_unique_field(
        self, 
        field_name: str, 
        value: Any
    ) -> Optional[Team]:
        """
        Obtiene un equipo por un campo único específico.
        
        Método de compatibilidad que delega en BaseRepository para
        mantener consistencia con otros módulos del sistema.
        
        Args:
            field_name: Nombre del campo único (ej: 'name', 'id')
            value: Valor a buscar en el campo
        
        Returns:
            Optional[Team]: El equipo encontrado o None si no existe
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(
            f"Buscando equipo por campo único {field_name} = {value}"
        )
        
        return await self.get_by_field(field_name, value)