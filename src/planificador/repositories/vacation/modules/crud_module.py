# src/planificador/repositories/vacation/modules/crud_module.py

"""
Módulo CRUD para operaciones básicas del repositorio Vacation.

Este módulo implementa las operaciones de creación, actualización y eliminación
de registros de vacaciones, delegando en BaseRepository para operaciones estándar.

Principios de Diseño:
    - Single Responsibility: Solo operaciones CRUD básicas
    - Delegation Pattern: Delega en BaseRepository para operaciones estándar
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    crud_module = VacationCrudModule(session)
    vacation = await crud_module.create_vacation(vacation_data)
    updated_vacation = await crud_module.update_vacation(vacation_id, update_data)
    success = await crud_module.delete_vacation(vacation_id)
    ```
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.vacation import Vacation
from planificador.repositories.base_repository import BaseRepository
from planificador.repositories.vacation.interfaces.crud_interface import IVacationCrudOperations
from planificador.exceptions.repository import VacationRepositoryError


class VacationCrudModule(BaseRepository[Vacation], IVacationCrudOperations):
    """
    Módulo para operaciones CRUD del repositorio Vacation.
    
    Implementa las operaciones de creación, actualización y eliminación
    de registros de vacaciones en la base de datos, delegando en BaseRepository
    para operaciones estándar y agregando lógica específica de vacaciones.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Vacation
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo CRUD para vacaciones.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Vacation)
        self._logger = self._logger.bind(component="VacationCrudModule")
        self._logger.debug("VacationCrudModule inicializado")

    async def create_vacation(self, vacation_data: Dict[str, Any]) -> Vacation:
        """
        Crea una nueva vacación delegando en el repositorio base.
        
        Args:
            vacation_data: Diccionario con datos de la vacación
                - employee_id: ID del empleado (requerido)
                - start_date: Fecha de inicio (requerido)
                - end_date: Fecha de fin (requerido)
                - vacation_type: Tipo de vacación (requerido)
                - status: Estado de la vacación (opcional, default PENDING)
                - description: Descripción (opcional)
                - days_requested: Días solicitados (opcional, se calcula automáticamente)
        
        Returns:
            Vacation: La vacación creada con todos sus datos
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la creación
        """
        self._logger.debug(
            f"Creando vacación para empleado ID: {vacation_data.get('employee_id')} "
            f"del {vacation_data.get('start_date')} al {vacation_data.get('end_date')}"
        )
        
        # Asegurar que status tenga un valor por defecto
        vacation_data_copy = vacation_data.copy()
        if 'status' not in vacation_data_copy:
            vacation_data_copy['status'] = 'PENDING'
        
        created_vacation = await self.create(vacation_data_copy)
        
        self._logger.info(
            f"Vacación creada exitosamente: ID {created_vacation.id}, "
            f"Empleado: {created_vacation.employee_id}, "
            f"Período: {created_vacation.start_date} - {created_vacation.end_date}"
        )
        
        return created_vacation

    async def update_vacation(
        self, 
        vacation_id: int, 
        update_data: Dict[str, Any]
    ) -> Vacation:
        """
        Actualiza una vacación existente delegando en el repositorio base.
        
        Args:
            vacation_id: ID de la vacación a actualizar
            update_data: Diccionario con datos a actualizar
                - start_date: Nueva fecha de inicio (opcional)
                - end_date: Nueva fecha de fin (opcional)
                - vacation_type: Nuevo tipo de vacación (opcional)
                - status: Nuevo estado (opcional)
                - description: Nueva descripción (opcional)
                - days_requested: Nuevos días solicitados (opcional)
        
        Returns:
            Vacation: La vacación actualizada
        
        Raises:
            VacationRepositoryError: Si la vacación no existe o hay error en actualización
        """
        self._logger.debug(
            f"Actualizando vacación ID: {vacation_id} "
            f"con datos: {list(update_data.keys())}"
        )
        
        updated_vacation = await self.update(vacation_id, update_data)
        
        self._logger.info(
            f"Vacación actualizada exitosamente: ID {vacation_id}, "
            f"Campos actualizados: {list(update_data.keys())}"
        )
        
        return updated_vacation

    async def delete_vacation(self, vacation_id: int) -> bool:
        """
        Elimina una vacación existente delegando en el repositorio base.
        
        Args:
            vacation_id: ID de la vacación a eliminar
        
        Returns:
            bool: True si la eliminación fue exitosa
        
        Raises:
            VacationRepositoryError: Si la vacación no existe o hay error en eliminación
        """
        self._logger.debug(f"Eliminando vacación ID: {vacation_id}")
        
        success = await self.delete(vacation_id)
        
        if success:
            self._logger.info(f"Vacación eliminada exitosamente: ID {vacation_id}")
        else:
            self._logger.warning(f"No se pudo eliminar la vacación ID: {vacation_id}")
        
        return success

    async def get_vacation_by_id(self, vacation_id: int) -> Optional[Vacation]:
        """
        Obtiene una vacación por su ID delegando en el repositorio base.
        
        Args:
            vacation_id: ID de la vacación
        
        Returns:
            Optional[Vacation]: La vacación si existe, None en caso contrario
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo vacación por ID: {vacation_id}")
        
        vacation = await self.get_by_id(vacation_id)
        
        if vacation:
            self._logger.debug(f"Vacación encontrada: ID {vacation_id}")
        else:
            self._logger.debug(f"Vacación no encontrada: ID {vacation_id}")
        
        return vacation

    async def get_by_unique_field(
        self, 
        field_name: str, 
        value: Any
    ) -> Optional[Vacation]:
        """
        Obtiene una vacación por un campo único delegando en el repositorio base.
        
        Args:
            field_name: Nombre del campo único
            value: Valor a buscar
        
        Returns:
            Optional[Vacation]: La vacación si existe, None en caso contrario
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo vacación por {field_name}: {value}")
        
        return await self.get_by_field(field_name, value)