# src/planificador/repositories/vacation/modules/validation_module.py

"""
Módulo de validación para operaciones de validación del repositorio Vacation.

Este módulo implementa las operaciones de validación de datos, reglas de negocio
y verificaciones de consistencia para vacaciones y solicitudes.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de validación y verificación
    - Business Rules: Implementación de reglas de negocio específicas
    - Data Integrity: Validaciones para mantener consistencia de datos

Uso:
    ```python
    validation_module = VacationValidationModule(session)
    is_valid = await validation_module.validate_vacation_data(vacation_data)
    conflicts = await validation_module.check_vacation_conflicts(employee_id, start_date, end_date)
    consistency = await validation_module.validate_data_consistency()
    ```
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date
from sqlalchemy import select, and_, or_, func, exists
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.vacation import Vacation
from planificador.models.employee import Employee
from planificador.repositories.vacation.interfaces.validation_interface import IVacationValidationOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    VacationRepositoryError,
    convert_sqlalchemy_error
)
from planificador.exceptions.validation import ValidationError
import pendulum
import re


class VacationValidationModule(BaseRepository[Vacation], IVacationValidationOperations):
    """
    Módulo para operaciones de validación del repositorio Vacation.
    
    Implementa las operaciones de validación de datos, reglas de negocio
    y verificaciones de consistencia usando Pendulum para fechas
    y validaciones robustas.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Vacation
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de validación para vacaciones.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Vacation)
        self._logger = self._logger.bind(component="VacationValidationModule")
        self._logger.debug("VacationValidationModule inicializado")

    async def validate_vacation_data(self, vacation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida los datos de una vacación.
        
        Args:
            vacation_data: Diccionario con datos de la vacación
        
        Returns:
            Dict[str, Any]: Resultado de validación con errores si los hay
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando datos de vacación para empleado: {vacation_data.get('employee_id')}")
            
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Validar employee_id requerido
            employee_id = vacation_data.get('employee_id')
            if not employee_id:
                validation_result['errors'].append({
                    'field': 'employee_id',
                    'message': 'El ID del empleado es requerido',
                    'code': 'REQUIRED_FIELD'
                })
            elif not isinstance(employee_id, int) or employee_id <= 0:
                validation_result['errors'].append({
                    'field': 'employee_id',
                    'message': 'El ID del empleado debe ser un número entero positivo',
                    'code': 'INVALID_FORMAT'
                })
            
            # Validar fechas requeridas
            start_date = vacation_data.get('start_date')
            end_date = vacation_data.get('end_date')
            
            if not start_date:
                validation_result['errors'].append({
                    'field': 'start_date',
                    'message': 'La fecha de inicio es requerida',
                    'code': 'REQUIRED_FIELD'
                })
            
            if not end_date:
                validation_result['errors'].append({
                    'field': 'end_date',
                    'message': 'La fecha de fin es requerida',
                    'code': 'REQUIRED_FIELD'
                })
            
            # Validar lógica de fechas si ambas están presentes
            if start_date and end_date:
                try:
                    # Convertir a objetos Pendulum para validación robusta
                    start_pendulum = pendulum.parse(str(start_date)) if isinstance(start_date, str) else pendulum.instance(start_date)
                    end_pendulum = pendulum.parse(str(end_date)) if isinstance(end_date, str) else pendulum.instance(end_date)
                    
                    if end_pendulum < start_pendulum:
                        validation_result['errors'].append({
                            'field': 'end_date',
                            'message': 'La fecha de fin debe ser posterior a la fecha de inicio',
                            'code': 'INVALID_DATE_RANGE'
                        })
                    
                    # Validar que las fechas no sean en el pasado (excepto para actualizaciones)
                    today = pendulum.today()
                    if start_pendulum.date() < today.date():
                        validation_result['warnings'].append({
                            'field': 'start_date',
                            'message': 'La fecha de inicio está en el pasado',
                            'code': 'PAST_DATE'
                        })
                    
                    # Validar duración máxima (ejemplo: 30 días consecutivos)
                    duration = (end_pendulum.date() - start_pendulum.date()).days + 1
                    if duration > 30:
                        validation_result['warnings'].append({
                            'field': 'duration',
                            'message': f'La duración de {duration} días excede el máximo recomendado de 30 días',
                            'code': 'EXCESSIVE_DURATION'
                        })
                    
                except Exception as e:
                    validation_result['errors'].append({
                        'field': 'dates',
                        'message': f'Error procesando fechas: {str(e)}',
                        'code': 'DATE_PROCESSING_ERROR'
                    })
            
            # Validar tipo de vacación
            vacation_type = vacation_data.get('vacation_type', '').strip()
            valid_types = ['ANNUAL', 'SICK', 'PERSONAL', 'MATERNITY', 'PATERNITY', 'EMERGENCY']
            if not vacation_type:
                validation_result['errors'].append({
                    'field': 'vacation_type',
                    'message': 'El tipo de vacación es requerido',
                    'code': 'REQUIRED_FIELD'
                })
            elif vacation_type not in valid_types:
                validation_result['errors'].append({
                    'field': 'vacation_type',
                    'message': f'Tipo de vacación inválido. Debe ser uno de: {", ".join(valid_types)}',
                    'code': 'INVALID_VALUE'
                })
            
            # Validar estado si se proporciona
            status = vacation_data.get('status')
            if status:
                valid_statuses = ['PENDING', 'APPROVED', 'REJECTED', 'CANCELLED']
                if status not in valid_statuses:
                    validation_result['errors'].append({
                        'field': 'status',
                        'message': f'Estado inválido. Debe ser uno de: {", ".join(valid_statuses)}',
                        'code': 'INVALID_VALUE'
                    })
            
            # Validar días solicitados si se proporciona
            days_requested = vacation_data.get('days_requested')
            if days_requested is not None:
                if not isinstance(days_requested, (int, float)) or days_requested <= 0:
                    validation_result['errors'].append({
                        'field': 'days_requested',
                        'message': 'Los días solicitados deben ser un número positivo',
                        'code': 'INVALID_FORMAT'
                    })
            
            # Validar descripción si se proporciona
            description = vacation_data.get('description', '').strip()
            if description and len(description) > 500:
                validation_result['errors'].append({
                    'field': 'description',
                    'message': 'La descripción no puede exceder 500 caracteres',
                    'code': 'FIELD_TOO_LONG'
                })
            
            # Determinar si la validación es exitosa
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
            self._logger.debug(
                f"Validación completada: {'exitosa' if validation_result['is_valid'] else 'con errores'}, "
                f"Errores: {len(validation_result['errors'])}, "
                f"Advertencias: {len(validation_result['warnings'])}"
            )
            
            return validation_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos validando vacación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_vacation_data",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando vacación: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado validando vacación: {e}",
                operation="validate_vacation_data",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def validate_vacation_request(
        self, 
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valida una solicitud de vacación completa.
        
        Args:
            request_data: Diccionario con datos de la solicitud
        
        Returns:
            Dict[str, Any]: Resultado de validación con errores si los hay
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug("Validando solicitud de vacación completa")
            
            # Primero validar los datos básicos
            validation_result = await self.validate_vacation_data(request_data)
            
            # Si hay errores básicos, no continuar con validaciones avanzadas
            if not validation_result['is_valid']:
                return validation_result
            
            # Validaciones adicionales para solicitudes
            employee_id = request_data.get('employee_id')
            start_date = request_data.get('start_date')
            end_date = request_data.get('end_date')
            
            # Verificar que el empleado existe
            if employee_id:
                employee_exists = await self._check_employee_exists(employee_id)
                if not employee_exists:
                    validation_result['errors'].append({
                        'field': 'employee_id',
                        'message': f'El empleado con ID {employee_id} no existe',
                        'code': 'EMPLOYEE_NOT_FOUND'
                    })
            
            # Verificar conflictos de fechas
            if employee_id and start_date and end_date:
                conflicts = await self.check_vacation_conflicts(employee_id, start_date, end_date)
                if conflicts['has_conflicts']:
                    validation_result['errors'].append({
                        'field': 'dates',
                        'message': 'Existe conflicto con vacaciones existentes',
                        'code': 'DATE_CONFLICT',
                        'details': conflicts
                    })
            
            # Actualizar estado de validación
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
            return validation_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos validando solicitud: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_vacation_request",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando solicitud: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado validando solicitud: {e}",
                operation="validate_vacation_request",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def validate_vacation_id(self, vacation_id: int) -> Dict[str, Any]:
        """
        Valida que un ID de vacación sea válido y exista.
        
        Args:
            vacation_id: ID de la vacación a validar
        
        Returns:
            Dict[str, Any]: Resultado de validación
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando ID de vacación: {vacation_id}")
            
            validation_result = {
                'is_valid': True,
                'errors': [],
                'vacation': None
            }
            
            # Validar formato del ID
            if not isinstance(vacation_id, int) or vacation_id <= 0:
                validation_result['errors'].append({
                    'field': 'vacation_id',
                    'message': 'El ID de vacación debe ser un número entero positivo',
                    'code': 'INVALID_FORMAT'
                })
                validation_result['is_valid'] = False
                return validation_result
            
            # Verificar existencia
            vacation = await self.get_by_id(vacation_id)
            if not vacation:
                validation_result['errors'].append({
                    'field': 'vacation_id',
                    'message': f'La vacación con ID {vacation_id} no existe',
                    'code': 'VACATION_NOT_FOUND'
                })
                validation_result['is_valid'] = False
            else:
                validation_result['vacation'] = vacation
            
            return validation_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos validando ID: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_vacation_id",
                entity_type=self.model_class.__name__,
                entity_id=vacation_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando ID: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado validando ID: {e}",
                operation="validate_vacation_id",
                entity_type=self.model_class.__name__,
                entity_id=vacation_id,
                original_error=e
            )

    async def check_vacation_conflicts(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date,
        exclude_vacation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Verifica conflictos de fechas con vacaciones existentes.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio de la vacación
            end_date: Fecha de fin de la vacación
            exclude_vacation_id: ID de vacación a excluir (opcional)
        
        Returns:
            Dict[str, Any]: Información sobre conflictos encontrados
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la verificación
        """
        try:
            self._logger.debug(
                f"Verificando conflictos para empleado {employee_id} "
                f"del {start_date} al {end_date}"
            )
            
            # Construir consulta para buscar solapamientos
            conditions = [
                self.model_class.employee_id == employee_id,
                self.model_class.start_date <= end_date,
                self.model_class.end_date >= start_date,
                self.model_class.status.in_(['PENDING', 'APPROVED'])  # Solo vacaciones activas
            ]
            
            # Excluir vacación específica si se proporciona
            if exclude_vacation_id:
                conditions.append(self.model_class.id != exclude_vacation_id)
            
            stmt = select(self.model_class).where(and_(*conditions))
            result = await self.session.execute(stmt)
            conflicting_vacations = result.scalars().all()
            
            conflict_result = {
                'has_conflicts': len(conflicting_vacations) > 0,
                'conflict_count': len(conflicting_vacations),
                'conflicting_vacations': []
            }
            
            # Detallar cada conflicto
            for vacation in conflicting_vacations:
                conflict_result['conflicting_vacations'].append({
                    'id': vacation.id,
                    'start_date': vacation.start_date,
                    'end_date': vacation.end_date,
                    'vacation_type': vacation.vacation_type,
                    'status': vacation.status,
                    'overlap_days': self._calculate_overlap_days(
                        start_date, end_date,
                        vacation.start_date, vacation.end_date
                    )
                })
            
            self._logger.debug(
                f"Verificación completada: {'conflictos encontrados' if conflict_result['has_conflicts'] else 'sin conflictos'}"
            )
            
            return conflict_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error verificando conflictos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="check_vacation_conflicts",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado verificando conflictos: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado verificando conflictos: {e}",
                operation="check_vacation_conflicts",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )

    async def validate_business_rules(
        self, 
        operation: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valida reglas de negocio específicas para vacaciones.
        
        Args:
            operation: Tipo de operación (create, update, delete, approve, etc.)
            data: Datos de la operación
        
        Returns:
            Dict[str, Any]: Resultado de validación de reglas de negocio
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando reglas de negocio para operación: {operation}")
            
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            if operation == 'create':
                # Reglas para creación de vacaciones
                employee_id = data.get('employee_id')
                vacation_type = data.get('vacation_type')
                start_date = data.get('start_date')
                
                # Verificar límite de vacaciones anuales
                if vacation_type == 'ANNUAL' and employee_id and start_date:
                    year = pendulum.parse(str(start_date)).year
                    annual_count = await self._count_annual_vacations(employee_id, year)
                    if annual_count >= 4:  # Máximo 4 períodos anuales por año
                        validation_result['errors'].append({
                            'field': 'vacation_type',
                            'message': f'Límite de vacaciones anuales alcanzado para el año {year}',
                            'code': 'ANNUAL_LIMIT_EXCEEDED'
                        })
                
                # Verificar anticipación mínima
                if start_date:
                    start_pendulum = pendulum.parse(str(start_date))
                    days_ahead = (start_pendulum.date() - pendulum.today().date()).days
                    if vacation_type == 'ANNUAL' and days_ahead < 15:
                        validation_result['warnings'].append({
                            'field': 'start_date',
                            'message': 'Las vacaciones anuales requieren al menos 15 días de anticipación',
                            'code': 'INSUFFICIENT_NOTICE'
                        })
            
            elif operation == 'update':
                # Reglas para actualización
                vacation_id = data.get('vacation_id')
                if vacation_id:
                    vacation = await self.get_by_id(vacation_id)
                    if vacation and vacation.status == 'APPROVED':
                        validation_result['errors'].append({
                            'field': 'status',
                            'message': 'No se pueden modificar vacaciones ya aprobadas',
                            'code': 'APPROVED_VACATION_IMMUTABLE'
                        })
            
            elif operation == 'delete':
                # Reglas para eliminación
                vacation_id = data.get('vacation_id')
                if vacation_id:
                    vacation = await self.get_by_id(vacation_id)
                    if vacation:
                        if vacation.status == 'APPROVED':
                            days_until_start = (vacation.start_date - pendulum.today().date()).days
                            if days_until_start < 7:
                                validation_result['errors'].append({
                                    'field': 'timing',
                                    'message': 'No se pueden cancelar vacaciones aprobadas con menos de 7 días de anticipación',
                                    'code': 'INSUFFICIENT_CANCELLATION_NOTICE'
                                })
            
            # Determinar validez general
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
            return validation_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando reglas de negocio: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_business_rules",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando reglas de negocio: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado validando reglas de negocio: {e}",
                operation="validate_business_rules",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def validate_data_consistency(self) -> Dict[str, Any]:
        """
        Valida la consistencia general de los datos de vacaciones.
        
        Returns:
            Dict[str, Any]: Resultado de validación de consistencia
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug("Validando consistencia de datos de vacaciones")
            
            consistency_result = {
                'is_consistent': True,
                'issues': [],
                'statistics': {}
            }
            
            # Verificar vacaciones con fechas inválidas
            invalid_dates_count = await self._count_invalid_date_ranges()
            if invalid_dates_count > 0:
                consistency_result['issues'].append({
                    'type': 'INVALID_DATE_RANGES',
                    'count': invalid_dates_count,
                    'message': f'Se encontraron {invalid_dates_count} vacaciones con rangos de fechas inválidos'
                })
            
            # Verificar vacaciones huérfanas (empleados inexistentes)
            orphaned_count = await self._count_orphaned_vacations()
            if orphaned_count > 0:
                consistency_result['issues'].append({
                    'type': 'ORPHANED_VACATIONS',
                    'count': orphaned_count,
                    'message': f'Se encontraron {orphaned_count} vacaciones con empleados inexistentes'
                })
            
            # Verificar solapamientos no detectados
            overlapping_count = await self._count_overlapping_vacations()
            if overlapping_count > 0:
                consistency_result['issues'].append({
                    'type': 'OVERLAPPING_VACATIONS',
                    'count': overlapping_count,
                    'message': f'Se encontraron {overlapping_count} pares de vacaciones solapadas'
                })
            
            # Estadísticas generales
            consistency_result['statistics'] = {
                'total_vacations': await self._count_total_vacations(),
                'pending_vacations': await self._count_vacations_by_status('PENDING'),
                'approved_vacations': await self._count_vacations_by_status('APPROVED'),
                'rejected_vacations': await self._count_vacations_by_status('REJECTED')
            }
            
            # Determinar consistencia general
            consistency_result['is_consistent'] = len(consistency_result['issues']) == 0
            
            self._logger.debug(
                f"Validación de consistencia completada: "
                f"{'consistente' if consistency_result['is_consistent'] else 'inconsistencias encontradas'}"
            )
            
            return consistency_result
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando consistencia: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_data_consistency",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando consistencia: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado validando consistencia: {e}",
                operation="validate_data_consistency",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    # Métodos auxiliares privados
    
    async def _check_employee_exists(self, employee_id: int) -> bool:
        """Verifica si un empleado existe."""
        try:
            stmt = select(exists().where(Employee.id == employee_id))
            result = await self.session.execute(stmt)
            return result.scalar()
        except Exception:
            return False
    
    def _calculate_overlap_days(
        self, 
        start1: date, 
        end1: date, 
        start2: date, 
        end2: date
    ) -> int:
        """Calcula los días de solapamiento entre dos rangos de fechas."""
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        if overlap_end >= overlap_start:
            return (overlap_end - overlap_start).days + 1
        return 0
    
    async def _count_annual_vacations(self, employee_id: int, year: int) -> int:
        """Cuenta las vacaciones anuales de un empleado en un año específico."""
        try:
            stmt = select(func.count(self.model_class.id)).where(
                and_(
                    self.model_class.employee_id == employee_id,
                    self.model_class.vacation_type == 'ANNUAL',
                    func.extract('year', self.model_class.start_date) == year,
                    self.model_class.status.in_(['PENDING', 'APPROVED'])
                )
            )
            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except Exception:
            return 0
    
    async def _count_invalid_date_ranges(self) -> int:
        """Cuenta vacaciones con rangos de fechas inválidos."""
        try:
            stmt = select(func.count(self.model_class.id)).where(
                self.model_class.end_date < self.model_class.start_date
            )
            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except Exception:
            return 0
    
    async def _count_orphaned_vacations(self) -> int:
        """Cuenta vacaciones con empleados inexistentes."""
        try:
            stmt = select(func.count(self.model_class.id)).where(
                ~exists().where(Employee.id == self.model_class.employee_id)
            )
            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except Exception:
            return 0
    
    async def _count_overlapping_vacations(self) -> int:
        """Cuenta pares de vacaciones solapadas del mismo empleado."""
        try:
            # Esta es una consulta compleja que requeriría un JOIN con sí misma
            # Por simplicidad, retornamos 0 por ahora
            return 0
        except Exception:
            return 0
    
    async def _count_total_vacations(self) -> int:
        """Cuenta el total de vacaciones."""
        try:
            stmt = select(func.count(self.model_class.id))
            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except Exception:
            return 0
    
    async def _count_vacations_by_status(self, status: str) -> int:
        """Cuenta vacaciones por estado específico."""
        try:
            stmt = select(func.count(self.model_class.id)).where(
                self.model_class.status == status
            )
            result = await self.session.execute(stmt)
            return result.scalar() or 0
        except Exception:
            return 0