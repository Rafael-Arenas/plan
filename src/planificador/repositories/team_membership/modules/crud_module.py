# src/planificador/repositories/team_membership/crud_module.py

"""
Módulo CRUD para operaciones básicas del repositorio TeamMembership.

Este módulo implementa las operaciones CRUD (Create, Read, Update, Delete)
para la entidad TeamMembership, siguiendo los patrones establecidos del proyecto.

Principios de Diseño:
    - Single Responsibility: Solo operaciones CRUD básicas
    - Dependency Injection: Recibe dependencias por constructor
    - Error Handling: Manejo robusto de excepciones con logging estructurado
    - Async/Await: Operaciones asíncronas para mejor performance

Uso:
    ```python
    crud_module = TeamMembershipCrudModule(session, logger)
    membership = await crud_module.create_membership(membership_data)
    ```
"""

from typing import Optional, Dict, Any
from datetime import date

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.repositories.base_repository import BaseRepository
from planificador.repositories.team_membership.interfaces.crud_interface import ITeamMembershipCrudOperations
from planificador.exceptions.repository import TeamMembershipRepositoryError, convert_sqlalchemy_error
from planificador.exceptions.validation import ValidationError


class TeamMembershipCrudModule(BaseRepository[TeamMembership], ITeamMembershipCrudOperations):
    """
    Módulo para operaciones CRUD de membresías de equipos.
    
    Hereda de BaseRepository para operaciones estándar y implementa
    la interfaz ITeamMembershipCrudOperations para operaciones específicas.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        _logger: Logger para registro de eventos
        model_class: Clase del modelo TeamMembership
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo CRUD de TeamMembership.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, TeamMembership)
        self._logger = logger.bind(module="TeamMembershipCrudModule")
    
    async def create_membership(self, membership_data: Dict[str, Any]) -> TeamMembership:
        """
        Crea una nueva membresía de equipo.
        
        Args:
            membership_data: Datos de la membresía a crear
        
        Returns:
            TeamMembership: Membresía creada
        
        Raises:
            ValidationError: Si los datos no son válidos
            TeamMembershipRepositoryError: Si ocurre un error en la creación
        """
        try:
            self._logger.info(f"Creando nueva membresía: {membership_data}")
            
            # Validar datos requeridos
            required_fields = ['employee_id', 'team_id', 'role', 'start_date']
            for field in required_fields:
                if field not in membership_data:
                    raise ValidationError(f"Campo requerido faltante: {field}")
            
            # Crear instancia de TeamMembership
            membership = TeamMembership(
                employee_id=membership_data['employee_id'],
                team_id=membership_data['team_id'],
                role=membership_data['role'],
                start_date=membership_data['start_date'],
                end_date=membership_data.get('end_date'),
                is_active=membership_data.get('is_active', True),
                notes=membership_data.get('notes')
            )
            
            # Usar el método create del BaseRepository
            created_membership = await self.create(membership)
            
            self._logger.info(f"Membresía creada exitosamente con ID: {created_membership.id}")
            return created_membership
            
        except ValidationError:
            # Re-lanzar errores de validación sin modificar
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al crear membresía: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_membership",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al crear membresía: {e}")
            await self.session.rollback()
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al crear membresía: {e}",
                operation="create_membership",
                entity_type="TeamMembership",
                original_error=e
            )
    
    async def update_membership(
        self, 
        membership_id: int, 
        update_data: Dict[str, Any]
    ) -> TeamMembership:
        """
        Actualiza una membresía existente.
        
        Args:
            membership_id: ID de la membresía a actualizar
            update_data: Datos a actualizar
        
        Returns:
            TeamMembership: Membresía actualizada
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la actualización
        """
        try:
            self._logger.info(f"Actualizando membresía ID {membership_id}: {update_data}")
            
            # Usar el método update del BaseRepository
            updated_membership = await self.update(membership_id, update_data)
            
            if not updated_membership:
                raise TeamMembershipRepositoryError(
                    message=f"Membresía con ID {membership_id} no encontrada",
                    operation="update_membership",
                    entity_type="TeamMembership",
                    entity_id=membership_id
                )
            
            self._logger.info(f"Membresía ID {membership_id} actualizada exitosamente")
            return updated_membership
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al actualizar membresía ID {membership_id}: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_membership",
                entity_type="TeamMembership",
                entity_id=membership_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al actualizar membresía ID {membership_id}: {e}")
            await self.session.rollback()
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al actualizar membresía: {e}",
                operation="update_membership",
                entity_type="TeamMembership",
                entity_id=membership_id,
                original_error=e
            )
    
    async def delete_membership(self, membership_id: int) -> bool:
        """
        Elimina una membresía (soft delete).
        
        Args:
            membership_id: ID de la membresía a eliminar
        
        Returns:
            bool: True si se eliminó exitosamente
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la eliminación
        """
        try:
            self._logger.info(f"Eliminando membresía ID {membership_id}")
            
            # Usar el método delete del BaseRepository
            deleted = await self.delete(membership_id)
            
            if deleted:
                self._logger.info(f"Membresía ID {membership_id} eliminada exitosamente")
            else:
                self._logger.warning(f"Membresía ID {membership_id} no encontrada para eliminar")
            
            return deleted
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al eliminar membresía ID {membership_id}: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="delete_membership",
                entity_type="TeamMembership",
                entity_id=membership_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al eliminar membresía ID {membership_id}: {e}")
            await self.session.rollback()
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al eliminar membresía: {e}",
                operation="delete_membership",
                entity_type="TeamMembership",
                entity_id=membership_id,
                original_error=e
            )
    
    async def activate_membership(self, membership_id: int) -> TeamMembership:
        """
        Activa una membresía estableciendo is_active como True.
        
        Args:
            membership_id: ID de la membresía a activar
        
        Returns:
            TeamMembership: Membresía activada
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la activación
        """
        try:
            self._logger.info(f"Activando membresía ID {membership_id}")
            
            update_data = {
                'is_active': True,
                'end_date': None  # Limpiar fecha de fin si existe
            }
            
            activated_membership = await self.update_membership(membership_id, update_data)
            
            self._logger.info(f"Membresía ID {membership_id} activada exitosamente")
            return activated_membership
            
        except Exception as e:
            # Los errores específicos ya son manejados por update_membership
            self._logger.error(f"Error al activar membresía ID {membership_id}: {e}")
            raise
    
    async def deactivate_membership(
        self, 
        membership_id: int, 
        end_date: Optional[date] = None
    ) -> TeamMembership:
        """
        Desactiva una membresía estableciendo is_active como False.
        
        Args:
            membership_id: ID de la membresía a desactivar
            end_date: Fecha de fin de la membresía (opcional)
        
        Returns:
            TeamMembership: Membresía desactivada
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la desactivación
        """
        try:
            self._logger.info(f"Desactivando membresía ID {membership_id}")
            
            update_data = {
                'is_active': False
            }
            
            if end_date:
                update_data['end_date'] = end_date
            
            deactivated_membership = await self.update_membership(membership_id, update_data)
            
            self._logger.info(f"Membresía ID {membership_id} desactivada exitosamente")
            return deactivated_membership
            
        except Exception as e:
            # Los errores específicos ya son manejados por update_membership
            self._logger.error(f"Error al desactivar membresía ID {membership_id}: {e}")
            raise
    
    async def update_membership_role(
        self, 
        membership_id: int, 
        new_role: MembershipRole
    ) -> TeamMembership:
        """
        Actualiza el rol de una membresía.
        
        Args:
            membership_id: ID de la membresía
            new_role: Nuevo rol a asignar
        
        Returns:
            TeamMembership: Membresía con rol actualizado
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la actualización
        """
        try:
            self._logger.info(f"Actualizando rol de membresía ID {membership_id} a {new_role}")
            
            update_data = {'role': new_role}
            updated_membership = await self.update_membership(membership_id, update_data)
            
            self._logger.info(f"Rol de membresía ID {membership_id} actualizado exitosamente")
            return updated_membership
            
        except Exception as e:
            # Los errores específicos ya son manejados por update_membership
            self._logger.error(f"Error al actualizar rol de membresía ID {membership_id}: {e}")
            raise
    
    async def end_membership(
        self, 
        membership_id: int, 
        end_date: date
    ) -> TeamMembership:
        """
        Finaliza una membresía estableciendo fecha de fin e is_active como False.
        
        Args:
            membership_id: ID de la membresía
            end_date: Fecha de finalización
        
        Returns:
            TeamMembership: Membresía finalizada
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la finalización
        """
        try:
            self._logger.info(f"Finalizando membresía ID {membership_id} en fecha {end_date}")
            
            update_data = {
                'end_date': end_date,
                'is_active': False
            }
            
            ended_membership = await self.update_membership(membership_id, update_data)
            
            self._logger.info(f"Membresía ID {membership_id} finalizada exitosamente")
            return ended_membership
            
        except Exception as e:
            # Los errores específicos ya son manejados por update_membership
            self._logger.error(f"Error al finalizar membresía ID {membership_id}: {e}")
            raise
    
    async def get_by_unique_field(
        self, 
        field_name: str, 
        field_value: Any
    ) -> Optional[TeamMembership]:
        """
        Obtiene una membresía por un campo único.
        
        Args:
            field_name: Nombre del campo
            field_value: Valor del campo
        
        Returns:
            Optional[TeamMembership]: Membresía encontrada o None
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        try:
            self._logger.debug(f"Buscando membresía por {field_name}={field_value}")
            
            # Usar el método get_by_field del BaseRepository
            membership = await self.get_by_field(field_name, field_value)
            
            if membership:
                self._logger.debug(f"Membresía encontrada: ID {membership.id}")
            else:
                self._logger.debug(f"No se encontró membresía con {field_name}={field_value}")
            
            return membership
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al buscar por {field_name}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type="TeamMembership"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar por {field_name}: {e}")
            raise TeamMembershipRepositoryError(
                message=f"Error inesperado al buscar membresía: {e}",
                operation="get_by_unique_field",
                entity_type="TeamMembership",
                original_error=e
            )