# -*- coding: utf-8 -*-
"""
Employee Domain Service - Main Implementation

Servicio principal del dominio Employee que actúa como fachada unificada
para todas las operaciones relacionadas con empleados.
"""

from typing import Dict, Any, List, Optional
import pendulum
from loguru import logger

from planificador.models.employee import Employee
from planificador.repositories.employee.employee_repository_facade import EmployeeRepositoryFacade
from planificador.schemas.employee.employee import EmployeeCreate, EmployeeUpdate

from .interfaces.employee_domain_interface import IEmployeeDomainService
from .modules.crud_operations import CrudOperations
from .modules.query_operations import QueryOperations
from .modules.advanced_query_operations import AdvancedQueryOperations
from .modules.date_operations import DateOperations
from .modules.relationship_operations import RelationshipOperations
from .modules.statistics_operations import StatisticsOperations
from .modules.validation_operations import ValidationOperations
from .modules.health_operations import HealthOperations


class EmployeeDomainService(IEmployeeDomainService):
    """
    Servicio principal del dominio Employee.
    
    Actúa como fachada unificada que coordina todas las operaciones
    del dominio de empleados, delegando a módulos especializados.
    """

    def __init__(self, repository_facade: EmployeeRepositoryFacade):
        """
        Inicializa el servicio de dominio Employee.
        
        Args:
            repository_facade: Fachada del repositorio de empleados
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="employee_domain_service")
        
        # Inicializar módulos especializados
        self._crud_ops = CrudOperations(repository_facade)
        self._query_ops = QueryOperations(repository_facade)
        self._advanced_query_ops = AdvancedQueryOperations(repository_facade)
        self._date_ops = DateOperations(repository_facade)
        self._relationship_ops = RelationshipOperations(repository_facade)
        self._statistics_ops = StatisticsOperations(repository_facade)
        self._validation_ops = ValidationOperations(repository_facade)
        self._health_ops = HealthOperations(repository_facade)
        
        self._logger.info("Employee Domain Service inicializado exitosamente")

    # ==================== CRUD Operations ====================

    async def create_employee(self, employee_data: EmployeeCreate) -> Employee:
        """Crea un nuevo empleado con validaciones de negocio."""
        self._logger.info("Iniciando creación de empleado")
        return await self._crud_ops.create_employee(employee_data)

    async def create_employee_with_validation(
        self,
        employee_data: Dict[str, Any],
        validate_business_rules: bool = True
    ) -> Employee:
        """Crea un nuevo empleado con validaciones completas de negocio."""
        self._logger.info(f"Iniciando creación de empleado con validación completa: {employee_data.get('email', 'N/A')}")
        return await self._crud_ops.create_employee_with_validation(employee_data, validate_business_rules)

    async def bulk_create_employees(self, employees_data: List[EmployeeCreate]) -> List[Employee]:
        """Crea múltiples empleados en una operación batch."""
        self._logger.info(f"Iniciando creación masiva de {len(employees_data)} empleados")
        return await self._crud_ops.bulk_create_employees(employees_data)

    async def soft_delete_employee(self, employee_id: int) -> bool:
        """Realiza eliminación lógica de un empleado."""
        self._logger.info(f"Iniciando eliminación lógica de empleado ID: {employee_id}")
        return await self._crud_ops.soft_delete_employee(employee_id)

    async def restore_employee(self, employee_id: int) -> bool:
        """Restaura un empleado previamente eliminado."""
        self._logger.info(f"Iniciando restauración de empleado ID: {employee_id}")
        return await self._crud_ops.restore_employee(employee_id)

    # ==================== Search Operations ====================

    async def search_employees_by_criteria(self, criteria: Dict[str, Any]) -> List[Employee]:
        """Busca empleados usando criterios avanzados."""
        self._logger.info("Iniciando búsqueda avanzada de empleados")
        return await self._advanced_query_ops.search_employees_by_criteria(criteria)

    async def get_employees_with_skills(self, skills: List[str]) -> List[Employee]:
        """Obtiene empleados que poseen habilidades específicas."""
        self._logger.info(f"Buscando empleados con habilidades: {skills}")
        return await self._advanced_query_ops.get_employees_with_skills(skills)

    async def get_employees_by_salary_range(
        self,
        min_salary: float,
        max_salary: float
    ) -> List[Employee]:
        """Obtiene empleados dentro de un rango salarial."""
        self._logger.info(f"Buscando empleados con salario entre {min_salary} y {max_salary}")
        return await self._advanced_query_ops.get_employees_by_salary_range(min_salary, max_salary)

    # ==================== Statistics Operations ====================

    async def get_employee_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de empleados."""
        self._logger.info("Obteniendo estadísticas de empleados")
        return await self._statistics_ops.get_employee_summary_report()

    async def get_employees_count_by_department(self) -> Dict[str, int]:
        """Obtiene el conteo de empleados por departamento."""
        self._logger.info("Obteniendo conteo de empleados por departamento")
        return await self._statistics_ops.get_employees_count_by_department()

    # ==================== Business Validation ====================

    async def validate_business_rules(self, employee_data: Dict[str, Any]) -> List[str]:
        """Valida reglas de negocio para datos de empleado."""
        self._logger.info("Validando reglas de negocio")
        return await self._validation_ops.validate_employee_data(employee_data)

    async def validate_manager_assignment(
        self,
        employee_id: int,
        manager_id: int
    ) -> List[str]:
        """Valida la asignación de un manager a un empleado."""
        self._logger.info(f"Validando asignación de manager {manager_id} a empleado {employee_id}")
        return await self._validation_ops.validate_manager_assignment(employee_id, manager_id)

    # ==================== Health Check ====================

    async def check_service_health(self) -> Dict[str, Any]:
        """Verifica el estado de salud del servicio."""
        self._logger.info("Verificando estado de salud del servicio")
        return await self._health_ops.check_service_health()

    async def get_service_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del servicio."""
        self._logger.info("Obteniendo métricas del servicio")
        return await self._health_ops.get_service_metrics()

    # ==================== Convenience Methods ====================

    async def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """Obtiene un empleado por su ID."""
        self._logger.info(f"Obteniendo empleado por ID: {employee_id}")
        return await self._repository.get_by_id(employee_id)

    async def update_employee(
        self,
        employee_id: int,
        employee_data: EmployeeUpdate
    ) -> Optional[Employee]:
        """Actualiza un empleado existente."""
        self._logger.info(f"Actualizando empleado ID: {employee_id}")
        
        # Validar datos antes de actualizar
        validation_errors = await self.validate_business_rules(employee_data.dict())
        if validation_errors:
            self._logger.warning(f"Errores de validación: {validation_errors}")
            # TODO: Lanzar excepción de validación personalizada
            return None
        
        return await self._repository.update(employee_id, employee_data.dict())

    async def get_active_employees(self) -> List[Employee]:
        """Obtiene todos los empleados activos."""
        self._logger.info("Obteniendo empleados activos")
        return await self._query_ops.get_active_employees()

    async def get_employees_hired_this_month(self) -> List[Employee]:
        """Obtiene empleados contratados en el mes actual."""
        self._logger.info("Obteniendo empleados contratados este mes")
        return await self._date_ops.get_employees_hired_current_month()

    async def assign_manager_to_employee(
        self,
        employee_id: int,
        manager_id: int
    ) -> bool:
        """Asigna un manager a un empleado con validaciones."""
        self._logger.info(f"Asignando manager {manager_id} a empleado {employee_id}")
        
        # Validar asignación antes de proceder
        validation_errors = await self.validate_manager_assignment(employee_id, manager_id)
        if validation_errors:
            self._logger.warning(f"Errores en asignación de manager: {validation_errors}")
            return False
        
        return await self._relationship_ops.assign_manager_to_employee(employee_id, manager_id)