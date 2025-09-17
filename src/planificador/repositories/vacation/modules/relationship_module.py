# src/planificador/repositories/vacation/modules/relationship_module.py

"""
Módulo de relaciones para operaciones de entidades relacionadas del repositorio Vacation.

Este módulo implementa las operaciones de gestión de relaciones entre vacaciones
y empleados, validación de existencia de entidades y gestión de conflictos.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de relaciones y validaciones de entidades
    - Business Logic: Validaciones específicas del dominio de vacaciones
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    relationship_module = VacationRelationshipModule(session)
    vacation_details = await relationship_module.get_vacation_with_employee_details(vacation_id)
    conflicts = await relationship_module.check_vacation_conflicts(employee_id, start_date, end_date)
    overlaps = await relationship_module.get_overlapping_vacations(employee_id, start_date, end_date)
    ```
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.vacation import Vacation
from planificador.models.employee import Employee
from planificador.repositories.vacation.interfaces.relationship_interface import IVacationRelationshipOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    VacationRepositoryError,
    convert_sqlalchemy_error
)
import pendulum


class VacationRelationshipModule(BaseRepository[Vacation], IVacationRelationshipOperations):
    """
    Módulo para operaciones de relaciones del repositorio Vacation.
    
    Implementa las operaciones de gestión de relaciones entre vacaciones
    y empleados, validación de existencia de entidades y gestión de conflictos
    con manejo de fechas usando Pendulum.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Vacation
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de relaciones para vacaciones.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Vacation)
        self._logger = self._logger.bind(component="VacationRelationshipModule")
        self._logger.debug("VacationRelationshipModule inicializado")

    async def get_vacation_with_employee_details(self, vacation_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene una vacación con detalles completos del empleado.
        
        Args:
            vacation_id: ID de la vacación
        
        Returns:
            Optional[Dict[str, Any]]: Vacación con detalles del empleado o None si no existe
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Obteniendo vacación {vacation_id} con detalles del empleado")
            
            stmt = select(self.model_class).options(
                joinedload(self.model_class.employee)
            ).where(self.model_class.id == vacation_id)
            
            result = await self.session.execute(stmt)
            vacation = result.scalar_one_or_none()
            
            if not vacation:
                self._logger.debug(f"Vacación {vacation_id} no encontrada")
                return None
            
            # Construir diccionario con detalles completos
            vacation_details = {
                'vacation': {
                    'id': vacation.id,
                    'employee_id': vacation.employee_id,
                    'vacation_type': vacation.vacation_type,
                    'start_date': vacation.start_date.isoformat() if vacation.start_date else None,
                    'end_date': vacation.end_date.isoformat() if vacation.end_date else None,
                    'days_requested': vacation.days_requested,
                    'status': vacation.status,
                    'reason': vacation.reason,
                    'created_at': vacation.created_at.isoformat() if vacation.created_at else None,
                    'updated_at': vacation.updated_at.isoformat() if vacation.updated_at else None
                },
                'employee': {
                    'id': vacation.employee.id,
                    'name': vacation.employee.name,
                    'email': vacation.employee.email,
                    'department': vacation.employee.department,
                    'position': vacation.employee.position,
                    'hire_date': vacation.employee.hire_date.isoformat() if vacation.employee.hire_date else None
                } if vacation.employee else None
            }
            
            self._logger.debug(f"Vacación {vacation_id} obtenida con detalles del empleado")
            
            return vacation_details
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo vacación con detalles: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_vacation_with_employee_details",
                entity_type=self.model_class.__name__,
                entity_id=vacation_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo detalles: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado obteniendo detalles: {e}",
                operation="get_vacation_with_employee_details",
                entity_type=self.model_class.__name__,
                entity_id=vacation_id,
                original_error=e
            )

    async def validate_employee_exists(self, employee_id: int) -> bool:
        """
        Valida que un empleado existe en el sistema.
        
        Args:
            employee_id: ID del empleado a validar
        
        Returns:
            bool: True si el empleado existe, False en caso contrario
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la validación
        """
        try:
            self._logger.debug(f"Validando existencia del empleado {employee_id}")
            
            stmt = select(func.count(Employee.id)).where(Employee.id == employee_id)
            result = await self.session.execute(stmt)
            count = result.scalar()
            
            exists = count > 0
            self._logger.debug(f"Empleado {employee_id} {'existe' if exists else 'no existe'}")
            
            return exists
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error validando empleado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_employee_exists",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado validando empleado: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado validando empleado: {e}",
                operation="validate_employee_exists",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )

    async def check_vacation_conflicts(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date,
        exclude_vacation_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Verifica conflictos de vacaciones para un empleado en un rango de fechas.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio de la vacación
            end_date: Fecha de fin de la vacación
            exclude_vacation_id: ID de vacación a excluir de la verificación
        
        Returns:
            List[Dict[str, Any]]: Lista de vacaciones en conflicto
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la verificación
        """
        try:
            self._logger.debug(
                f"Verificando conflictos para empleado {employee_id} "
                f"del {start_date} al {end_date}"
            )
            
            # Condiciones base para conflictos
            conditions = [
                self.model_class.employee_id == employee_id,
                self.model_class.status.in_(['APPROVED', 'PENDING']),
                # Verificar solapamiento de fechas
                or_(
                    # La nueva vacación empieza durante una existente
                    and_(
                        self.model_class.start_date <= start_date,
                        self.model_class.end_date >= start_date
                    ),
                    # La nueva vacación termina durante una existente
                    and_(
                        self.model_class.start_date <= end_date,
                        self.model_class.end_date >= end_date
                    ),
                    # La nueva vacación engloba una existente
                    and_(
                        self.model_class.start_date >= start_date,
                        self.model_class.end_date <= end_date
                    )
                )
            ]
            
            # Excluir vacación específica si se proporciona
            if exclude_vacation_id:
                conditions.append(self.model_class.id != exclude_vacation_id)
            
            stmt = select(self.model_class).where(and_(*conditions))
            
            result = await self.session.execute(stmt)
            conflicting_vacations = result.scalars().all()
            
            # Convertir a diccionarios con información relevante
            conflicts = []
            for vacation in conflicting_vacations:
                conflicts.append({
                    'id': vacation.id,
                    'vacation_type': vacation.vacation_type,
                    'start_date': vacation.start_date.isoformat(),
                    'end_date': vacation.end_date.isoformat(),
                    'days_requested': vacation.days_requested,
                    'status': vacation.status,
                    'reason': vacation.reason
                })
            
            self._logger.debug(f"Encontrados {len(conflicts)} conflictos")
            
            return conflicts
            
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

    async def get_overlapping_vacations(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todas las vacaciones que se solapan con un rango de fechas.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
        
        Returns:
            List[Dict[str, Any]]: Lista de vacaciones que se solapan
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(
                f"Obteniendo solapamientos para empleado {employee_id} "
                f"del {start_date} al {end_date}"
            )
            
            # Condiciones para solapamiento (incluye todos los estados)
            conditions = [
                self.model_class.employee_id == employee_id,
                or_(
                    # Solapamiento parcial o total
                    and_(
                        self.model_class.start_date <= end_date,
                        self.model_class.end_date >= start_date
                    )
                )
            ]
            
            stmt = select(self.model_class).where(and_(*conditions)).order_by(
                self.model_class.start_date
            )
            
            result = await self.session.execute(stmt)
            overlapping_vacations = result.scalars().all()
            
            # Convertir a diccionarios con información de solapamiento
            overlaps = []
            for vacation in overlapping_vacations:
                # Calcular días de solapamiento
                overlap_start = max(vacation.start_date, start_date)
                overlap_end = min(vacation.end_date, end_date)
                overlap_days = (overlap_end - overlap_start).days + 1
                
                overlaps.append({
                    'id': vacation.id,
                    'vacation_type': vacation.vacation_type,
                    'start_date': vacation.start_date.isoformat(),
                    'end_date': vacation.end_date.isoformat(),
                    'days_requested': vacation.days_requested,
                    'status': vacation.status,
                    'overlap_start': overlap_start.isoformat(),
                    'overlap_end': overlap_end.isoformat(),
                    'overlap_days': overlap_days,
                    'reason': vacation.reason
                })
            
            self._logger.debug(f"Encontrados {len(overlaps)} solapamientos")
            
            return overlaps
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo solapamientos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_overlapping_vacations",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo solapamientos: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado obteniendo solapamientos: {e}",
                operation="get_overlapping_vacations",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )

    async def get_vacations_with_relationships(
        self, 
        include_employee: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene vacaciones con sus relaciones cargadas.
        
        Args:
            include_employee: Si incluir detalles del empleado
            filters: Filtros opcionales para la consulta
        
        Returns:
            List[Dict[str, Any]]: Lista de vacaciones con relaciones
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo vacaciones con relaciones")
            
            # Construir consulta base
            stmt = select(self.model_class)
            
            # Agregar carga de relaciones si se solicita
            if include_employee:
                stmt = stmt.options(joinedload(self.model_class.employee))
            
            # Aplicar filtros si se proporcionan
            if filters:
                conditions = []
                
                if 'employee_id' in filters:
                    conditions.append(self.model_class.employee_id == filters['employee_id'])
                
                if 'status' in filters:
                    if isinstance(filters['status'], list):
                        conditions.append(self.model_class.status.in_(filters['status']))
                    else:
                        conditions.append(self.model_class.status == filters['status'])
                
                if 'vacation_type' in filters:
                    conditions.append(self.model_class.vacation_type == filters['vacation_type'])
                
                if 'start_date_from' in filters:
                    conditions.append(self.model_class.start_date >= filters['start_date_from'])
                
                if 'start_date_to' in filters:
                    conditions.append(self.model_class.start_date <= filters['start_date_to'])
                
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            
            # Ordenar por fecha de inicio
            stmt = stmt.order_by(self.model_class.start_date.desc())
            
            result = await self.session.execute(stmt)
            vacations = result.scalars().all()
            
            # Convertir a diccionarios con relaciones
            vacation_list = []
            for vacation in vacations:
                vacation_dict = {
                    'id': vacation.id,
                    'employee_id': vacation.employee_id,
                    'vacation_type': vacation.vacation_type,
                    'start_date': vacation.start_date.isoformat() if vacation.start_date else None,
                    'end_date': vacation.end_date.isoformat() if vacation.end_date else None,
                    'days_requested': vacation.days_requested,
                    'status': vacation.status,
                    'reason': vacation.reason,
                    'created_at': vacation.created_at.isoformat() if vacation.created_at else None,
                    'updated_at': vacation.updated_at.isoformat() if vacation.updated_at else None
                }
                
                # Agregar detalles del empleado si se cargó la relación
                if include_employee and vacation.employee:
                    vacation_dict['employee'] = {
                        'id': vacation.employee.id,
                        'name': vacation.employee.name,
                        'email': vacation.employee.email,
                        'department': vacation.employee.department,
                        'position': vacation.employee.position,
                        'hire_date': vacation.employee.hire_date.isoformat() if vacation.employee.hire_date else None
                    }
                
                vacation_list.append(vacation_dict)
            
            self._logger.debug(f"Obtenidas {len(vacation_list)} vacaciones con relaciones")
            
            return vacation_list
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo vacaciones con relaciones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_vacations_with_relationships",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo relaciones: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado obteniendo relaciones: {e}",
                operation="get_vacations_with_relationships",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_employee_vacation_summary(self, employee_id: int) -> Dict[str, Any]:
        """
        Obtiene un resumen completo de vacaciones para un empleado.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            Dict[str, Any]: Resumen de vacaciones del empleado
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Obteniendo resumen de vacaciones para empleado {employee_id}")
            
            # Verificar que el empleado existe
            employee_exists = await self.validate_employee_exists(employee_id)
            if not employee_exists:
                return {
                    'employee_id': employee_id,
                    'exists': False,
                    'message': 'Empleado no encontrado'
                }
            
            # Obtener estadísticas generales
            current_year = pendulum.now().year
            
            stats_stmt = select(
                func.count(self.model_class.id).label('total_vacations'),
                func.count(case((self.model_class.status == 'APPROVED', 1))).label('approved_count'),
                func.count(case((self.model_class.status == 'PENDING', 1))).label('pending_count'),
                func.count(case((self.model_class.status == 'REJECTED', 1))).label('rejected_count'),
                func.sum(case((self.model_class.status == 'APPROVED', self.model_class.days_requested))).label('total_approved_days')
            ).where(self.model_class.employee_id == employee_id)
            
            stats_result = await self.session.execute(stats_stmt)
            stats = stats_result.first()
            
            # Obtener vacaciones recientes (últimas 5)
            recent_stmt = select(self.model_class).where(
                self.model_class.employee_id == employee_id
            ).order_by(self.model_class.created_at.desc()).limit(5)
            
            recent_result = await self.session.execute(recent_stmt)
            recent_vacations = recent_result.scalars().all()
            
            # Obtener vacaciones del año actual
            current_year_stmt = select(
                func.sum(case((
                    and_(
                        self.model_class.status == 'APPROVED',
                        self.model_class.vacation_type == 'ANNUAL'
                    ), 
                    self.model_class.days_requested
                ))).label('annual_days_used'),
                func.sum(case((
                    self.model_class.status == 'PENDING',
                    self.model_class.days_requested
                ))).label('pending_days')
            ).where(
                and_(
                    self.model_class.employee_id == employee_id,
                    func.extract('year', self.model_class.start_date) == current_year
                )
            )
            
            current_year_result = await self.session.execute(current_year_stmt)
            current_year_stats = current_year_result.first()
            
            # Compilar resumen
            summary = {
                'employee_id': employee_id,
                'exists': True,
                'statistics': {
                    'total_vacations': stats.total_vacations if stats else 0,
                    'approved_vacations': stats.approved_count if stats else 0,
                    'pending_vacations': stats.pending_count if stats else 0,
                    'rejected_vacations': stats.rejected_count if stats else 0,
                    'total_approved_days': stats.total_approved_days if stats else 0
                },
                'current_year': {
                    'year': current_year,
                    'annual_days_used': current_year_stats.annual_days_used if current_year_stats else 0,
                    'pending_days': current_year_stats.pending_days if current_year_stats else 0,
                    'annual_allowance': 25,  # Asumiendo 25 días anuales
                    'remaining_days': 25 - (current_year_stats.annual_days_used or 0)
                },
                'recent_vacations': [
                    {
                        'id': vacation.id,
                        'vacation_type': vacation.vacation_type,
                        'start_date': vacation.start_date.isoformat() if vacation.start_date else None,
                        'end_date': vacation.end_date.isoformat() if vacation.end_date else None,
                        'days_requested': vacation.days_requested,
                        'status': vacation.status,
                        'created_at': vacation.created_at.isoformat() if vacation.created_at else None
                    }
                    for vacation in recent_vacations
                ]
            }
            
            self._logger.debug(f"Resumen generado para empleado {employee_id}")
            
            return summary
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo resumen: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_vacation_summary",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo resumen: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado obteniendo resumen: {e}",
                operation="get_employee_vacation_summary",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )