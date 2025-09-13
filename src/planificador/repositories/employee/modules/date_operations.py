from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import pendulum
from pendulum import DateTime, Date
from loguru import logger

from planificador.repositories.base_repository import BaseRepository
from planificador.models.employee import Employee, EmployeeStatus
from planificador.utils.date_utils import (
    get_current_time,
    format_datetime,
    add_business_days
)
from planificador.utils.date_utils import get_business_days, is_business_day
from planificador.exceptions.repository import (
    EmployeeQueryError,
    EmployeeRepositoryError,
    EmployeeValidationRepositoryError,
    EmployeeDateRangeError,
    convert_sqlalchemy_error,
    create_employee_validation_repository_error,
    create_employee_date_range_error
)
from planificador.repositories.employee.interfaces.date_interface import IEmployeeDateOperations


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
    
    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Employee]:
        return await super().get_by_unique_field(field_name, value)

    async def get_employees_hired_on_date(self, date: date, **kwargs) -> List[Employee]:
        """
        Obtiene empleados contratados en una fecha específica.

        Args:
            date: Fecha de contratación

        Returns:
            Lista de empleados contratados en esa fecha
        """
        try:
            return await self.find_all_by_criteria(
                {"hire_date": date},
                order_by="full_name_asc",
                **kwargs
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_hired_on_date",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            raise EmployeeQueryError(
                message=f"Error inesperado al obtener empleados por fecha de contratación: {e}",
                operation="get_employees_hired_on_date",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
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

            return await self.find_all_by_criteria(
                {"hire_date": {"operator": "between", "value": (start_of_week.date(), end_of_week.date())}},
                order_by="hire_date_desc",
                **kwargs
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_hired_current_week",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            start_date = locals().get('start_of_week')
            end_date = locals().get('end_of_week')
            raise EmployeeQueryError(
                message=f"Error obteniendo empleados contratados esta semana: {str(e)}",
                operation="get_employees_hired_current_week",
                entity_type=self.model_class.__name__,
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
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_hired_current_month",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            raise EmployeeQueryError(
                message=f"Error inesperado al obtener empleados contratados en el mes actual: {e}",
                operation="get_employees_hired_current_month",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_employees_hired_last_n_days(self, days: int, **kwargs) -> List[Employee]:
        """
        Obtiene empleados contratados en los últimos N días.
        
        Args:
            days: Número de días a revisar hacia atrás.
        
        Returns:
            Lista de empleados contratados en los últimos N días.
        """
        try:
            end_date = get_current_time().date()
            start_date = end_date.subtract(days=days)
            
            return await self.find_all_by_criteria(
                {"hire_date": {"operator": "between", "value": (start_date, end_date)}},
                order_by="hire_date_desc",
                **kwargs
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_hired_last_n_days",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            raise EmployeeQueryError(
                message=f"Error inesperado al obtener empleados contratados en los últimos {days} días: {e}",
                operation="get_employees_hired_last_n_days",
                entity_type=self.model_class.__name__,
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
            
            # Obtener solo los días laborables en el rango
            business_days_in_range = get_business_days(start_date, end_date)

            if not business_days_in_range:
                return []

            # Filtrar por días laborables usando el repositorio
            return await self.find_all_by_criteria(
                {"hire_date": {"operator": "in", "value": business_days_in_range}},
                order_by="hire_date_asc",
                **kwargs
            )
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_hired_business_days_only",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            raise EmployeeQueryError(
                message=f"Error inesperado al obtener empleados contratados en días laborables: {e}",
                operation="get_employees_hired_business_days_only",
                entity_type=self.model_class.__name__,
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
            return await self.find_all_by_criteria(
                {"hire_date": {"operator": "between", "value": (start_date, end_date)}},
                order_by="hire_date_desc"
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_hire_date_range",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            raise EmployeeQueryError(
                message=f"Error inesperado al obtener empleados por rango de fecha: {e}",
                operation="get_by_hire_date_range",
                entity_type=self.model_class.__name__,
                original_error=e
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
                raise EmployeeRepositoryError(
                    message="Empleado no encontrado",
                    operation="get_employee_tenure_stats",
                    entity_type=self.model_class.__name__,
                    entity_id=employee_id
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
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_tenure_stats",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except EmployeeRepositoryError as e:
            raise EmployeeQueryError(
                message=f"Error al buscar empleado: {e.message}",
                operation="get_employee_tenure_stats",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )
        except Exception as e:
            raise EmployeeQueryError(
                message=f"Error inesperado al calcular estadísticas de antigüedad: {e}",
                operation="get_employee_tenure_stats",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
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
                query = select(self.model_class).where(self.model_class.status == status)
            else:
                query = select(self.model_class).where(self.model_class.status == EmployeeStatus.ACTIVE)
            
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
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_by_tenure_range",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            raise EmployeeQueryError(
                message=f"Error inesperado al obtener empleados por rango de antigüedad: {e}",
                operation="get_employees_by_tenure_range",
                entity_type=self.model_class.__name__,
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
                    raise RepositoryValidationError(
                        message="La fecha de contratación debe ser un día laborable",
                        operation="create_employee_with_date_validation",
                        entity_type=self.model_class.__name__,
                        field="hire_date",
                        invalid_value=str(hire_date)
                    )
            
            # Crear empleado usando el método estándar del BaseRepository
            return await self.create(employee_data)
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_employee_with_date_validation",
                entity_type=self.model_class.__name__
            )
        except EmployeeValidationRepositoryError as e:
            # Re-raise validation errors to be handled by the caller
            raise e
        except Exception as e:
            raise EmployeeQueryError(
                message=f"Error inesperado al crear empleado con validación de fecha: {e}",
                operation="create_employee_with_date_validation",
                entity_type=self.model_class.__name__,
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