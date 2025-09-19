# src/planificador/repositories/workload/modules/validation_module.py

"""
Módulo de validación para operaciones del repositorio Workload.

Este módulo implementa las validaciones específicas del dominio para cargas de trabajo,
incluyendo validaciones de integridad, reglas de negocio y consistencia de datos.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de validación
    - Domain Validation: Validaciones específicas del dominio de cargas de trabajo
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    validation_module = WorkloadValidationModule(session)
    await validation_module.validate_workload_data(workload_data)
    is_valid = await validation_module.validate_workload_hours(hours)
    await validation_module.validate_workload_date_range(start_date, end_date)
    ```
"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.workload import Workload
from planificador.repositories.workload.interfaces.validation_interface import IWorkloadValidationOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    WorkloadRepositoryError,
    convert_sqlalchemy_error
)
from planificador.exceptions.validation import ValidationError


class WorkloadValidationModule(BaseRepository[Workload], IWorkloadValidationOperations):
    """
    Módulo para operaciones de validación del repositorio Workload.
    
    Implementa las validaciones específicas del dominio para cargas de trabajo,
    incluyendo validaciones de integridad referencial, reglas de negocio
    y consistencia de datos.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Workload
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de validación para cargas de trabajo.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Workload)
        self._logger = self._logger.bind(component="WorkloadValidationModule")
        self._logger.debug("WorkloadValidationModule inicializado")

    async def validate_workload_data(self, workload_data: Dict[str, Any]) -> bool:
        """
        Valida los datos completos de una carga de trabajo.
        
        Args:
            workload_data: Diccionario con los datos de la carga de trabajo
        
        Returns:
            bool: True si los datos son válidos
        
        Raises:
            ValidationError: Si los datos no son válidos
            WorkloadRepositoryError: Si ocurre un error durante la validación
        """
        self._logger.debug("Validando datos completos de carga de trabajo")
        
        try:
            # Validar campos requeridos
            required_fields = ['employee_id', 'project_id', 'workload_date', 'hours']
            for field in required_fields:
                if field not in workload_data or workload_data[field] is None:
                    raise ValidationError(
                        message=f"Campo requerido faltante: {field}",
                        field=field,
                        value=workload_data.get(field)
                    )
            
            # Validar tipos de datos
            if not isinstance(workload_data['employee_id'], int) or workload_data['employee_id'] <= 0:
                raise ValidationError(
                    message="employee_id debe ser un entero positivo",
                    field="employee_id",
                    value=workload_data['employee_id']
                )
            
            if not isinstance(workload_data['project_id'], int) or workload_data['project_id'] <= 0:
                raise ValidationError(
                    message="project_id debe ser un entero positivo",
                    field="project_id",
                    value=workload_data['project_id']
                )
            
            # Validar fecha
            workload_date = workload_data['workload_date']
            if isinstance(workload_date, str):
                try:
                    workload_date = datetime.strptime(workload_date, '%Y-%m-%d').date()
                except ValueError:
                    raise ValidationError(
                        message="Formato de fecha inválido. Use YYYY-MM-DD",
                        field="workload_date",
                        value=workload_date
                    )
            elif not isinstance(workload_date, date):
                raise ValidationError(
                    message="workload_date debe ser una fecha válida",
                    field="workload_date",
                    value=workload_date
                )
            
            # Validar horas
            await self.validate_workload_hours(workload_data['hours'])
            
            # Validar estado si está presente
            if 'status' in workload_data and workload_data['status'] is not None:
                await self.validate_workload_status(workload_data['status'])
            
            # Validar descripción si está presente
            if 'description' in workload_data and workload_data['description'] is not None:
                await self.validate_workload_description(workload_data['description'])
            
            # Validar duplicados
            await self.validate_no_duplicate_workload(
                workload_data['employee_id'],
                workload_data['project_id'],
                workload_date,
                workload_data.get('id')
            )
            
            self._logger.debug("Validación de datos completa exitosa")
            return True
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy durante validación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_workload_data",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado durante validación: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado durante validación: {e}",
                operation="validate_workload_data",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def validate_workload_hours(self, hours: Any) -> bool:
        """
        Valida las horas de una carga de trabajo.
        
        Args:
            hours: Horas a validar
        
        Returns:
            bool: True si las horas son válidas
        
        Raises:
            ValidationError: Si las horas no son válidas
        """
        self._logger.debug(f"Validando horas de carga de trabajo: {hours}")
        
        # Validar tipo
        if not isinstance(hours, (int, float, Decimal)):
            raise ValidationError(
                message="Las horas deben ser un número",
                field="hours",
                value=hours
            )
        
        # Convertir a Decimal para validación precisa
        try:
            hours_decimal = Decimal(str(hours))
        except (ValueError, TypeError):
            raise ValidationError(
                message="Las horas deben ser un número válido",
                field="hours",
                value=hours
            )
        
        # Validar rango
        if hours_decimal <= 0:
            raise ValidationError(
                message="Las horas deben ser mayor que cero",
                field="hours",
                value=hours
            )
        
        if hours_decimal > 24:
            raise ValidationError(
                message="Las horas no pueden exceder 24 horas por día",
                field="hours",
                value=hours
            )
        
        # Validar precisión (máximo 2 decimales)
        if hours_decimal.as_tuple().exponent < -2:
            raise ValidationError(
                message="Las horas no pueden tener más de 2 decimales",
                field="hours",
                value=hours
            )
        
        self._logger.debug("Validación de horas exitosa")
        return True

    async def validate_workload_status(self, status: str) -> bool:
        """
        Valida el estado de una carga de trabajo.
        
        Args:
            status: Estado a validar
        
        Returns:
            bool: True si el estado es válido
        
        Raises:
            ValidationError: Si el estado no es válido
        """
        self._logger.debug(f"Validando estado de carga de trabajo: {status}")
        
        if not isinstance(status, str):
            raise ValidationError(
                message="El estado debe ser una cadena de texto",
                field="status",
                value=status
            )
        
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'on_hold']
        
        if status.lower() not in valid_statuses:
            raise ValidationError(
                message=f"Estado inválido. Estados válidos: {', '.join(valid_statuses)}",
                field="status",
                value=status
            )
        
        self._logger.debug("Validación de estado exitosa")
        return True

    async def validate_workload_description(self, description: str) -> bool:
        """
        Valida la descripción de una carga de trabajo.
        
        Args:
            description: Descripción a validar
        
        Returns:
            bool: True si la descripción es válida
        
        Raises:
            ValidationError: Si la descripción no es válida
        """
        self._logger.debug("Validando descripción de carga de trabajo")
        
        if not isinstance(description, str):
            raise ValidationError(
                message="La descripción debe ser una cadena de texto",
                field="description",
                value=description
            )
        
        # Validar longitud
        if len(description.strip()) == 0:
            raise ValidationError(
                message="La descripción no puede estar vacía",
                field="description",
                value=description
            )
        
        if len(description) > 1000:
            raise ValidationError(
                message="La descripción no puede exceder 1000 caracteres",
                field="description",
                value=description
            )
        
        self._logger.debug("Validación de descripción exitosa")
        return True

    async def validate_workload_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> bool:
        """
        Valida un rango de fechas para cargas de trabajo.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Returns:
            bool: True si el rango es válido
        
        Raises:
            ValidationError: Si el rango no es válido
        """
        self._logger.debug(f"Validando rango de fechas: {start_date} - {end_date}")
        
        if not isinstance(start_date, date):
            raise ValidationError(
                message="La fecha de inicio debe ser una fecha válida",
                field="start_date",
                value=start_date
            )
        
        if not isinstance(end_date, date):
            raise ValidationError(
                message="La fecha de fin debe ser una fecha válida",
                field="end_date",
                value=end_date
            )
        
        if start_date > end_date:
            raise ValidationError(
                message="La fecha de inicio no puede ser posterior a la fecha de fin",
                field="date_range",
                value=f"{start_date} - {end_date}"
            )
        
        # Validar que el rango no sea excesivamente largo (más de 1 año)
        days_diff = (end_date - start_date).days
        if days_diff > 365:
            raise ValidationError(
                message="El rango de fechas no puede exceder 1 año",
                field="date_range",
                value=f"{start_date} - {end_date}"
            )
        
        self._logger.debug("Validación de rango de fechas exitosa")
        return True

    async def validate_no_duplicate_workload(
        self,
        employee_id: int,
        project_id: int,
        workload_date: date,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Valida que no exista una carga de trabajo duplicada.
        
        Args:
            employee_id: ID del empleado
            project_id: ID del proyecto
            workload_date: Fecha de la carga de trabajo
            exclude_id: ID a excluir de la validación (para actualizaciones)
        
        Returns:
            bool: True si no hay duplicados
        
        Raises:
            ValidationError: Si existe un duplicado
            WorkloadRepositoryError: Si ocurre un error durante la validación
        """
        self._logger.debug(
            f"Validando duplicados para empleado {employee_id}, "
            f"proyecto {project_id}, fecha {workload_date}"
        )
        
        try:
            stmt = select(self.model_class).where(
                and_(
                    self.model_class.employee_id == employee_id,
                    self.model_class.project_id == project_id,
                    self.model_class.workload_date == workload_date
                )
            )
            
            # Excluir ID específico si se proporciona (para actualizaciones)
            if exclude_id is not None:
                stmt = stmt.where(self.model_class.id != exclude_id)
            
            result = await self.session.execute(stmt)
            existing_workload = result.scalar_one_or_none()
            
            if existing_workload is not None:
                raise ValidationError(
                    message=f"Ya existe una carga de trabajo para el empleado {employee_id} "
                           f"en el proyecto {project_id} para la fecha {workload_date}",
                    field="duplicate_workload",
                    value=f"employee_id={employee_id}, project_id={project_id}, date={workload_date}"
                )
            
            self._logger.debug("Validación de duplicados exitosa")
            return True
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al validar duplicados: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_no_duplicate_workload",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar duplicados: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al validar duplicados: {e}",
                operation="validate_no_duplicate_workload",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def validate_employee_daily_hours(
        self,
        employee_id: int,
        workload_date: date,
        additional_hours: float,
        exclude_workload_id: Optional[int] = None
    ) -> bool:
        """
        Valida que las horas diarias totales de un empleado no excedan el límite.
        
        Args:
            employee_id: ID del empleado
            workload_date: Fecha de la carga de trabajo
            additional_hours: Horas adicionales a agregar
            exclude_workload_id: ID de carga a excluir del cálculo
        
        Returns:
            bool: True si las horas son válidas
        
        Raises:
            ValidationError: Si las horas exceden el límite
            WorkloadRepositoryError: Si ocurre un error durante la validación
        """
        self._logger.debug(
            f"Validando horas diarias para empleado {employee_id} "
            f"en fecha {workload_date}, horas adicionales: {additional_hours}"
        )
        
        try:
            # Obtener horas existentes para el empleado en la fecha
            stmt = select(func.sum(self.model_class.hours)).where(
                and_(
                    self.model_class.employee_id == employee_id,
                    self.model_class.workload_date == workload_date
                )
            )
            
            # Excluir carga específica si se proporciona
            if exclude_workload_id is not None:
                stmt = stmt.where(self.model_class.id != exclude_workload_id)
            
            result = await self.session.execute(stmt)
            existing_hours = result.scalar() or 0
            
            total_hours = float(existing_hours) + additional_hours
            
            # Validar límite diario (8 horas estándar, máximo 12 horas)
            if total_hours > 12:
                raise ValidationError(
                    message=f"Las horas diarias totales ({total_hours}) exceden el límite máximo de 12 horas",
                    field="daily_hours",
                    value=total_hours
                )
            
            # Advertencia si excede horas estándar
            if total_hours > 8:
                self._logger.warning(
                    f"Empleado {employee_id} excederá horas estándar: {total_hours} horas"
                )
            
            self._logger.debug("Validación de horas diarias exitosa")
            return True
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al validar horas diarias: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_employee_daily_hours",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar horas diarias: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al validar horas diarias: {e}",
                operation="validate_employee_daily_hours",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )

    async def validate_workload_consistency(
        self, 
        workload_data: Dict[str, Any]
    ) -> List[str]:
        """
        Valida la consistencia general de los datos de carga de trabajo.
        
        Args:
            workload_data: Datos de la carga de trabajo a validar
        
        Returns:
            List[str]: Lista de advertencias de consistencia (vacía si todo está bien)
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la validación
        """
        self._logger.debug("Validando consistencia de datos de carga de trabajo")
        
        warnings = []
        
        try:
            # Validar fecha no futura
            if 'workload_date' in workload_data:
                workload_date = workload_data['workload_date']
                if isinstance(workload_date, str):
                    workload_date = datetime.strptime(workload_date, '%Y-%m-%d').date()
                
                if workload_date > date.today():
                    warnings.append("La fecha de carga de trabajo es futura")
            
            # Validar horas vs estado
            if 'hours' in workload_data and 'status' in workload_data:
                hours = float(workload_data['hours'])
                status = workload_data['status'].lower()
                
                if status == 'completed' and hours < 1:
                    warnings.append("Carga marcada como completada con menos de 1 hora")
                
                if status == 'pending' and hours > 8:
                    warnings.append("Carga pendiente con más de 8 horas asignadas")
            
            # Validar descripción vs horas
            if 'description' in workload_data and 'hours' in workload_data:
                description = workload_data['description'] or ""
                hours = float(workload_data['hours'])
                
                if hours > 4 and len(description.strip()) < 10:
                    warnings.append("Carga de más de 4 horas con descripción muy breve")
            
            self._logger.debug(f"Validación de consistencia completada con {len(warnings)} advertencias")
            return warnings
            
        except Exception as e:
            self._logger.error(f"Error inesperado al validar consistencia: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al validar consistencia: {e}",
                operation="validate_workload_consistency",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    # Métodos alias para compatibilidad con la interfaz
    async def is_valid_workload_data(self, workload_data: Dict[str, Any]) -> bool:
        """Alias para validate_workload_data."""
        return await self.validate_workload_data(workload_data)

    async def is_valid_workload_hours(self, hours: Any) -> bool:
        """Alias para validate_workload_hours."""
        return await self.validate_workload_hours(hours)

    async def is_valid_workload_status(self, status: str) -> bool:
        """Alias para validate_workload_status."""
        return await self.validate_workload_status(status)

    async def is_valid_date_range(self, start_date: date, end_date: date) -> bool:
        """Alias para validate_workload_date_range."""
        return await self.validate_workload_date_range(start_date, end_date)

    # Implementación de funciones faltantes según la interfaz

    async def validate_create_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos para crear una nueva carga de trabajo.
        
        Args:
            data: Diccionario con los datos de la carga de trabajo
        
        Raises:
            ValidationError: Si los datos no son válidos
            WorkloadRepositoryError: Si ocurre un error durante la validación
        """
        self._logger.debug("Validando datos para creación de carga de trabajo")
        
        try:
            # Usar la validación completa existente
            await self.validate_workload_data(data)
            
            # Validaciones adicionales específicas para creación
            if 'id' in data:
                raise ValidationError(
                    message="No se debe especificar ID al crear una nueva carga de trabajo",
                    field="id",
                    value=data['id']
                )
            
            # Validar que las horas diarias no excedan el límite
            if all(field in data for field in ['employee_id', 'workload_date', 'hours']):
                await self.validate_employee_daily_hours(
                    employee_id=data['employee_id'],
                    workload_date=data['workload_date'],
                    additional_hours=float(data['hours'])
                )
            
            self._logger.debug("Validación de datos para creación exitosa")
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al validar datos para creación: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al validar datos para creación: {e}",
                operation="validate_create_data",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def validate_update_data(self, data: Dict[str, Any], workload_id: Optional[int] = None) -> None:
        """
        Valida los datos para actualizar una carga de trabajo.
        
        Args:
            data: Diccionario con los datos a actualizar
            workload_id: ID de la carga de trabajo (opcional)
        
        Raises:
            ValidationError: Si los datos no son válidos
            WorkloadRepositoryError: Si ocurre un error durante la validación
        """
        self._logger.debug(f"Validando datos para actualización de carga de trabajo ID: {workload_id}")
        
        try:
            # Validar que hay datos para actualizar
            if not data or len(data) == 0:
                raise ValidationError(
                    message="No se proporcionaron datos para actualizar",
                    field="data",
                    value=data
                )
            
            # Validar campos individuales si están presentes
            if 'hours' in data:
                await self.validate_workload_hours(data['hours'])
            
            if 'status' in data:
                await self.validate_workload_status(data['status'])
            
            if 'description' in data:
                await self.validate_workload_description(data['description'])
            
            # Validar duplicados si se están actualizando campos clave
            if all(field in data for field in ['employee_id', 'project_id', 'workload_date']):
                await self.validate_no_duplicate_workload(
                    employee_id=data['employee_id'],
                    project_id=data['project_id'],
                    workload_date=data['workload_date'],
                    exclude_id=workload_id
                )
            
            # Validar horas diarias si se están actualizando horas
            if 'hours' in data and all(field in data for field in ['employee_id', 'workload_date']):
                await self.validate_employee_daily_hours(
                    employee_id=data['employee_id'],
                    workload_date=data['workload_date'],
                    additional_hours=float(data['hours']),
                    exclude_workload_id=workload_id
                )
            
            self._logger.debug("Validación de datos para actualización exitosa")
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al validar datos para actualización: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al validar datos para actualización: {e}",
                operation="validate_update_data",
                entity_type=self.model_class.__name__,
                entity_id=workload_id,
                original_error=e
            )

    async def validate_date_range(self, start_date: date, end_date: date) -> None:
        """
        Valida un rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Raises:
            ValidationError: Si el rango de fechas no es válido
        """
        self._logger.debug(f"Validando rango de fechas: {start_date} - {end_date}")
        
        # Usar la validación existente que ya retorna bool
        await self.validate_workload_date_range(start_date, end_date)
        
        self._logger.debug("Validación de rango de fechas exitosa")

    async def validate_threshold_hours(self, threshold_hours: float) -> None:
        """
        Valida un umbral de horas.
        
        Args:
            threshold_hours: Umbral de horas a validar
        
        Raises:
            ValidationError: Si el umbral no es válido
        """
        self._logger.debug(f"Validando umbral de horas: {threshold_hours}")
        
        if not isinstance(threshold_hours, (int, float)):
            raise ValidationError(
                message="El umbral de horas debe ser un número",
                field="threshold_hours",
                value=threshold_hours
            )
        
        if threshold_hours <= 0:
            raise ValidationError(
                message="El umbral de horas debe ser mayor que cero",
                field="threshold_hours",
                value=threshold_hours
            )
        
        if threshold_hours > 24:
            raise ValidationError(
                message="El umbral de horas no puede exceder 24 horas",
                field="threshold_hours",
                value=threshold_hours
            )
        
        self._logger.debug("Validación de umbral de horas exitosa")

    async def validate_team_id(self, team_id: int) -> None:
        """
        Valida el ID del equipo.
        
        Args:
            team_id: ID del equipo a validar
        
        Raises:
            ValidationError: Si el ID del equipo no es válido
            WorkloadRepositoryError: Si el equipo no existe
        """
        self._logger.debug(f"Validando ID de equipo: {team_id}")
        
        if not isinstance(team_id, int):
            raise ValidationError(
                message="El ID del equipo debe ser un entero",
                field="team_id",
                value=team_id
            )
        
        if team_id <= 0:
            raise ValidationError(
                message="El ID del equipo debe ser mayor que cero",
                field="team_id",
                value=team_id
            )
        
        # Nota: En un sistema real, aquí se validaría que el equipo existe en la base de datos
        # Por ahora, solo validamos el formato del ID
        
        self._logger.debug("Validación de ID de equipo exitosa")

    async def validate_workload_id(self, workload_id: int) -> None:
        """
        Valida el ID de la carga de trabajo.
        
        Args:
            workload_id: ID de la carga de trabajo a validar
        
        Raises:
            ValidationError: Si el ID no es válido
            WorkloadRepositoryError: Si la carga de trabajo no existe
        """
        self._logger.debug(f"Validando ID de carga de trabajo: {workload_id}")
        
        if not isinstance(workload_id, int):
            raise ValidationError(
                message="El ID de la carga de trabajo debe ser un entero",
                field="workload_id",
                value=workload_id
            )
        
        if workload_id <= 0:
            raise ValidationError(
                message="El ID de la carga de trabajo debe ser mayor que cero",
                field="workload_id",
                value=workload_id
            )
        
        try:
            # Verificar que la carga de trabajo existe
            stmt = select(self.model_class).where(self.model_class.id == workload_id)
            result = await self.session.execute(stmt)
            workload = result.scalar_one_or_none()
            
            if workload is None:
                raise ValidationError(
                    message=f"No existe una carga de trabajo con ID {workload_id}",
                    field="workload_id",
                    value=workload_id
                )
            
            self._logger.debug("Validación de ID de carga de trabajo exitosa")
            
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al validar ID de carga de trabajo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_workload_id",
                entity_type=self.model_class.__name__,
                entity_id=workload_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar ID de carga de trabajo: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al validar ID de carga de trabajo: {e}",
                operation="validate_workload_id",
                entity_type=self.model_class.__name__,
                entity_id=workload_id,
                original_error=e
            )

    async def check_employee_project_consistency(self, workload_id: int, employee_id: int, project_id: int) -> bool:
        """
        Verifica consistencia entre empleado y proyecto asignados.
        
        Args:
            workload_id: ID de la carga de trabajo
            employee_id: ID del empleado
            project_id: ID del proyecto
        
        Returns:
            bool: True si la consistencia es válida
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la verificación
        """
        self._logger.debug(
            f"Verificando consistencia empleado-proyecto para carga {workload_id}: "
            f"empleado {employee_id}, proyecto {project_id}"
        )
        
        try:
            # Obtener la carga de trabajo
            stmt = select(self.model_class).where(self.model_class.id == workload_id)
            result = await self.session.execute(stmt)
            workload = result.scalar_one_or_none()
            
            if workload is None:
                raise WorkloadRepositoryError(
                    message=f"No se encontró la carga de trabajo con ID {workload_id}",
                    operation="check_employee_project_consistency",
                    entity_type=self.model_class.__name__,
                    entity_id=workload_id
                )
            
            # Verificar consistencia
            is_consistent = (
                workload.employee_id == employee_id and 
                workload.project_id == project_id
            )
            
            if not is_consistent:
                self._logger.warning(
                    f"Inconsistencia detectada en carga {workload_id}: "
                    f"esperado empleado {employee_id}, proyecto {project_id}; "
                    f"actual empleado {workload.employee_id}, proyecto {workload.project_id}"
                )
            
            self._logger.debug(f"Verificación de consistencia completada: {is_consistent}")
            return is_consistent
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al verificar consistencia: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="check_employee_project_consistency",
                entity_type=self.model_class.__name__,
                entity_id=workload_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al verificar consistencia: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al verificar consistencia: {e}",
                operation="check_employee_project_consistency",
                entity_type=self.model_class.__name__,
                entity_id=workload_id,
                original_error=e
            )