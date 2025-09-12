# src/planificador/database/repositories/employee/modules/date_operations.py

from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import pendulum
from pendulum import DateTime, Date
from loguru import logger

from ..base_repository import BaseRepository
from .....models.employee import Employee, EmployeeStatus
from .....utils.date_utils import (
    get_current_time,
    format_datetime,
    is_business_day,
    add_business_days,
    get_business_days
)
from .....exceptions.repository import (
    convert_sqlalchemy_error,
    EmployeeRepositoryError,
    EmployeeQueryError,
    EmployeeValidationRepositoryError,
    EmployeeDateRangeError,
    create_employee_query_error,
    create_employee_validation_repository_error,
    create_employee_date_range_error
)
from ..interfaces.date_interface import IEmployeeDateOperations


class DateOperations(BaseRepository[Employee], IEmployeeDateOperations):
    """
    Operaciones de fecha para empleados.
    
    Esta clase maneja todas las operaciones relacionadas con fechas
    en el contexto de empleados, incluyendo consultas temporales,
    análisis de antigüedad y validaciones de fechas.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Employee)
        self._logger = logger.bind(component="DateOperations")
    
    # ============================================================================
    # CONSULTAS TEMPORALES
    # ============================================================================
    
    async def get_employees_hired_current_week(self, **kwargs) -> List[Employee]:
        """
        Obtiene empleados contratados en la semana actual.
        
        Returns:
            Lista de empleados contratados esta semana
        """
        try:
            current_time = get_current_time()
            start_of_week = current_time.start_of('week')
            end_of_week = current_time.end_of('week')
            
            return await self.get_employees_hired_business_days_only(
                start_date=start_of_week.date(),
                end_date=end_of_week.date(),
                **kwargs
            )
        except Exception as e:
            raise create_employee_date_range_error(
                start_date=None,
                end_date=None,
                reason=f"Error obteniendo empleados contratados esta semana: {str(e)}",
                original_error=e
            )
    
    async def get_employees_hired_current_month(self, **kwargs) -> List[Employee]:
        """
        Obtiene empleados contratados en el mes actual.
        
        Returns:
            Lista de empleados contratados este mes
        """
        try:
            current_time = get_current_time()
            start_of_month = current_time.start_of('month')
            end_of_month = current_time.end_of('month')
            
            return await self.get_employees_hired_business_days_only(
                start_date=start_of_month.date(),
                end_date=end_of_month.date(),
                **kwargs
            )
        except Exception as e:
            raise create_employee_date_range_error(
                start_date=None,
                end_date=None,
                reason=f"Error obteniendo empleados contratados este mes: {str(e)}",
                original_error=e
            )
    
    async def get_employees_hired_business_days_only(
        self, 
        start_date: Union[date, str, None] = None,
        end_date: Union[date, str, None] = None,
        **kwargs
    ) -> List[Employee]:
        """
        Obtiene empleados contratados en días laborables.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista de empleados contratados en días laborables
        """
        try:
            # Convertir fechas si son strings
            if isinstance(start_date, str):
                start_date = pendulum.parse(start_date).date()
            if isinstance(end_date, str):
                end_date = pendulum.parse(end_date).date()
            
            # Usar fechas por defecto si no se proporcionan
            if start_date is None:
                start_date = get_current_time().subtract(months=1).date()
            if end_date is None:
                end_date = get_current_time().date()
            
            # Obtener empleados en el rango de fechas
            # Nota: Necesitamos acceso al query_builder desde el repository principal
            # Por ahora, implementamos la consulta directamente
            from sqlalchemy import select, and_
            
            query = select(Employee).where(
                and_(
                    Employee.hire_date >= start_date,
                    Employee.hire_date <= end_date
                )
            ).order_by(Employee.hire_date.desc())
            
            result = await self.session.execute(query)
            employees = result.scalars().all()
            
            # Filtrar solo los contratados en días laborables
            business_day_employees = [
                emp for emp in employees 
                if emp.hire_date and is_business_day(emp.hire_date)
            ]
            
            return business_day_employees
            
        except Exception as e:
            raise create_employee_date_range_error(
                start_date=start_date,
                end_date=end_date,
                reason=f"Error obteniendo empleados contratados en días laborables: {str(e)}",
                original_error=e
            )
    
    async def get_by_hire_date_range(self, start_date: date, end_date: date, **kwargs) -> List[Employee]:
        """
        Obtiene empleados por rango de fecha de contratación.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados contratados en el rango de fechas
        """
        try:
            from sqlalchemy import select, and_
            
            query = select(Employee).where(
                and_(
                    Employee.hire_date >= start_date,
                    Employee.hire_date <= end_date
                )
            ).order_by(Employee.hire_date.desc())
            
            result = await self.session.execute(query)
            employees = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(employees)} empleados contratados entre {start_date} y {end_date}")
            return list(employees)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo empleados por rango de fechas {start_date}-{end_date}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_hire_date_range",
                entity_type="Employee"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo empleados por rango de fechas {start_date}-{end_date}: {e}")
            raise create_employee_query_error(
                query_type="get_by_hire_date_range",
                parameters={"start_date": str(start_date), "end_date": str(end_date)},
                reason=f"Error inesperado: {str(e)}"
            )
    
    # ============================================================================
    # ANÁLISIS DE ANTIGÜEDAD
    # ============================================================================
    
    async def get_employee_tenure_stats(self, employee_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de antigüedad de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Estadísticas de antigüedad
        """
        try:
            employee = await self.get_by_id(employee_id)
            if not employee:
                raise create_employee_query_error(
                    query_type="get_employee_tenure_stats",
                    parameters={"employee_id": employee_id},
                    reason="Empleado no encontrado"
                )
            
            if not employee.hire_date:
                return {
                    "employee_id": employee_id,
                    "full_name": employee.full_name,
                    "hire_date": None,
                    "tenure_years": 0,
                    "tenure_months": 0,
                    "tenure_days": 0,
                    "is_new_employee": True,
                    "tenure_category": "Sin fecha de contratación"
                }
            
            current_date = get_current_time().date()
            hire_pendulum = pendulum.instance(employee.hire_date)
            current_pendulum = pendulum.instance(current_date)
            
            # Calcular diferencia
            diff = current_pendulum - hire_pendulum
            
            # Calcular años, meses y días
            years = diff.years
            months = diff.months
            days = diff.remaining_days
            
            # Determinar categoría de antigüedad
            if years < 1:
                category = "Nuevo (< 1 año)"
            elif years < 3:
                category = "Junior (1-3 años)"
            elif years < 7:
                category = "Intermedio (3-7 años)"
            elif years < 15:
                category = "Senior (7-15 años)"
            else:
                category = "Veterano (15+ años)"
            
            return {
                "employee_id": employee_id,
                "full_name": employee.full_name,
                "hire_date": employee.hire_date.isoformat(),
                "tenure_years": years,
                "tenure_months": months,
                "tenure_days": days,
                "total_days": diff.total_days(),
                "is_new_employee": years < 1,
                "tenure_category": category
            }
            
        except Exception as e:
            raise create_employee_query_error(
                query_type="get_employee_tenure_stats",
                parameters={"employee_id": employee_id},
                reason=f"Error calculando estadísticas de antigüedad: {str(e)}",
                original_error=e
            )
    
    async def get_employees_by_tenure_range(
        self,
        min_years: float = 0.0,
        max_years: Optional[float] = None,
        status: Optional[EmployeeStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene empleados por rango de antigüedad.
        
        Args:
            min_years: Años mínimos de antigüedad
            max_years: Años máximos de antigüedad (opcional)
            status: Estado del empleado (opcional)
            
        Returns:
            Lista de empleados con información de antigüedad
        """
        try:
            from sqlalchemy import select
            
            # Obtener empleados según estado
            if status:
                query = select(Employee).where(Employee.status == status)
            else:
                query = select(Employee).where(Employee.status == EmployeeStatus.ACTIVE)
            
            result = await self.session.execute(query)
            employees = result.scalars().all()
            
            current_date = get_current_time().date()
            result_list = []
            
            for employee in employees:
                if not employee.hire_date:
                    continue
                
                # Calcular antigüedad en años
                hire_pendulum = pendulum.instance(employee.hire_date)
                current_pendulum = pendulum.instance(current_date)
                tenure_years = (current_pendulum - hire_pendulum).total_days() / 365.25
                
                # Verificar si está en el rango
                if tenure_years >= min_years:
                    if max_years is None or tenure_years <= max_years:
                        result_list.append({
                            "employee_id": employee.id,
                            "full_name": employee.full_name,
                            "employee_code": employee.employee_code,
                            "department": employee.department,
                            "position": employee.position,
                            "hire_date": employee.hire_date.isoformat(),
                            "tenure_years": round(tenure_years, 2),
                            "status": employee.status.value if employee.status else None
                        })
            
            # Ordenar por antigüedad (más antiguos primero)
            result_list.sort(key=lambda x: x["tenure_years"], reverse=True)
            
            return result_list
            
        except Exception as e:
            raise create_employee_query_error(
                query_type="get_employees_by_tenure_range",
                parameters={
                    "min_years": min_years,
                    "max_years": max_years,
                    "status": status.value if status else None
                },
                reason=f"Error obteniendo empleados por rango de antigüedad: {str(e)}",
                original_error=e
            )
    
    # ============================================================================
    # VALIDACIONES AVANZADAS
    # ============================================================================
    
    async def create_employee_with_date_validation(
        self,
        employee_data: Dict[str, Any],
        validate_hire_date_business_day: bool = False
    ) -> Employee:
        """
        Crea empleado con validaciones de fecha.
        
        Args:
            employee_data: Datos del empleado
            validate_hire_date_business_day: Si validar que la fecha de contratación sea día laborable
            
        Returns:
            Empleado creado
        """
        try:
            # Validar fecha de contratación si se especifica
            if validate_hire_date_business_day and 'hire_date' in employee_data:
                hire_date = employee_data['hire_date']
                if isinstance(hire_date, str):
                    hire_date = pendulum.parse(hire_date).date()
                elif isinstance(hire_date, datetime):
                    hire_date = hire_date.date()
                
                if not is_business_day(hire_date):
                    raise create_employee_validation_repository_error(
                        field="hire_date",
                        value=hire_date,
                        reason="La fecha de contratación debe ser un día laborable",
                        operation="create_employee_with_date_validation"
                    )
            
            # Crear empleado usando el método estándar del BaseRepository
            return await self.create(employee_data)
            
        except Exception as e:
            if isinstance(e, (EmployeeValidationRepositoryError, EmployeeRepositoryError)):
                raise
            
            raise create_employee_validation_repository_error(
                field="employee_data",
                value=str(employee_data),
                reason=f"Error en validación de fecha: {str(e)}",
                operation="create_employee_with_date_validation",
                original_error=e
            )
    
    # ============================================================================
    # FORMATEO DE FECHAS
    # ============================================================================
    
    def format_employee_hire_date(self, employee: Employee, format_type: str = 'default') -> Optional[str]:
        """
        Formatea la fecha de contratación para presentación.
        
        Args:
            employee: Empleado
            format_type: Tipo de formato
            
        Returns:
            Fecha formateada o None
        """
        return self.format_entity_date(employee, 'hire_date', format_type)
    
    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================
    
    def format_entity_date(self, entity: Employee, date_field: str, format_type: str = 'default') -> Optional[str]:
        """
        Formatea una fecha de una entidad para presentación.
        
        Args:
            entity: Entidad con el campo de fecha
            date_field: Nombre del campo de fecha
            format_type: Tipo de formato
            
        Returns:
            Fecha formateada o None
        """
        try:
            date_value = getattr(entity, date_field, None)
            if not date_value:
                return None
            
            # Convertir a objeto Pendulum si es necesario
            if isinstance(date_value, date) and not isinstance(date_value, DateTime):
                pendulum_date = pendulum.instance(date_value)
            else:
                pendulum_date = date_value
            
            # Aplicar formato según el tipo
            if format_type == 'short':
                return pendulum_date.format('DD/MM/YYYY')
            elif format_type == 'long':
                return pendulum_date.format('dddd, DD [de] MMMM [de] YYYY', locale='es')
            elif format_type == 'iso':
                return pendulum_date.format('YYYY-MM-DD')
            else:  # default
                return pendulum_date.format('DD/MM/YYYY')
                
        except Exception as e:
            self._logger.error(f"Error formateando fecha {date_field} de {entity.__class__.__name__}: {e}")
            return None