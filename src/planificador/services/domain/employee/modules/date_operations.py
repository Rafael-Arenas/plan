# -*- coding: utf-8 -*-
"""
Date Operations Implementation for Employee Domain Service

Implementación concreta de las operaciones relacionadas con fechas para empleados.
"""

from typing import List, Dict, Any
from datetime import date
from loguru import logger
import pendulum

from planificador.models.employee import Employee
from planificador.repositories.employee_repository_facade import EmployeeRepositoryFacade
from ..interfaces.date_interface import IDateOperations


class DateOperations(IDateOperations):
    """
    Implementación de operaciones de fechas para el dominio Employee.
    
    Proporciona funcionalidades para gestionar operaciones relacionadas con fechas
    de contratación, antigüedad y períodos temporales usando Pendulum.
    """

    def __init__(self, repository_facade: EmployeeRepositoryFacade):
        """
        Inicializa las operaciones de fechas.
        
        Args:
            repository_facade: Fachada del repositorio de empleados
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="employee_date_operations")

    async def get_employees_hired_in_period(
        self,
        start_date: date,
        end_date: date
    ) -> List[Employee]:
        """
        Obtiene empleados contratados en un período específico.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            List[Employee]: Lista de empleados contratados en el período
        """
        self._logger.info(f"Consultando empleados contratados entre {start_date} y {end_date}")
        
        try:
            # Convertir a objetos Pendulum para mejor manejo
            start_pendulum = pendulum.instance(start_date) if not isinstance(start_date, pendulum.Date) else start_date
            end_pendulum = pendulum.instance(end_date) if not isinstance(end_date, pendulum.Date) else end_date
            
            employees = await self._repository.get_hired_in_period(start_pendulum, end_pendulum)
            self._logger.info(f"Encontrados {len(employees)} empleados contratados en el período")
            return employees
            
        except Exception as e:
            self._logger.error(f"Error consultando empleados por período de contratación: {e}")
            raise

    async def get_employees_by_tenure_range(
        self,
        min_years: float,
        max_years: float
    ) -> List[Employee]:
        """
        Obtiene empleados por rango de antigüedad.
        
        Args:
            min_years: Antigüedad mínima en años
            max_years: Antigüedad máxima en años
            
        Returns:
            List[Employee]: Lista de empleados en el rango de antigüedad
        """
        self._logger.info(f"Consultando empleados con antigüedad entre {min_years} y {max_years} años")
        
        try:
            # TODO: Implementar cálculo de antigüedad usando Pendulum
            # TODO: Convertir años a fechas para la consulta
            
            employees = await self._repository.get_by_tenure_range(min_years, max_years)
            self._logger.info(f"Encontrados {len(employees)} empleados en rango de antigüedad")
            return employees
            
        except Exception as e:
            self._logger.error(f"Error consultando empleados por rango de antigüedad: {e}")
            raise

    async def calculate_employee_tenure(self, employee_id: int) -> Dict[str, Any]:
        """
        Calcula la antigüedad detallada de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Dict[str, Any]: Información detallada de antigüedad
                          (años, meses, días, etc.)
        """
        self._logger.info(f"Calculando antigüedad para empleado ID: {employee_id}")
        
        try:
            employee = await self._repository.get_by_id(employee_id)
            if not employee or not employee.hire_date:
                return {}
            
            # Usar Pendulum para cálculos precisos de antigüedad
            hire_date = pendulum.instance(employee.hire_date)
            now = pendulum.now()
            
            # Calcular diferencia detallada
            period = now - hire_date
            
            tenure_info = {
                "employee_id": employee_id,
                "hire_date": hire_date.to_date_string(),
                "current_date": now.to_date_string(),
                "total_days": period.days,
                "years": period.years,
                "months": period.months,
                "days": period.remaining_days,
                "total_years_decimal": round(period.total_days() / 365.25, 2),
                "formatted_tenure": f"{period.years} años, {period.months} meses, {period.remaining_days} días"
            }
            
            self._logger.info(f"Antigüedad calculada para empleado {employee_id}: {tenure_info['formatted_tenure']}")
            return tenure_info
            
        except Exception as e:
            self._logger.error(f"Error calculando antigüedad para empleado {employee_id}: {e}")
            raise

    async def get_employees_hired_current_month(self) -> List[Employee]:
        """
        Obtiene empleados contratados en el mes actual.
        
        Returns:
            List[Employee]: Lista de empleados contratados este mes
        """
        self._logger.info("Consultando empleados contratados en el mes actual")
        
        try:
            # Usar Pendulum para obtener el rango del mes actual
            now = pendulum.now()
            start_of_month = now.start_of('month')
            end_of_month = now.end_of('month')
            
            employees = await self.get_employees_hired_in_period(
                start_of_month.date(),
                end_of_month.date()
            )
            
            self._logger.info(f"Encontrados {len(employees)} empleados contratados este mes")
            return employees
            
        except Exception as e:
            self._logger.error(f"Error consultando empleados contratados este mes: {e}")
            raise