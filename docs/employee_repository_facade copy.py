# src/planificador/database/repositories/employee/employee_repository_facade.py

from typing import List, Dict, Any, Optional, Union
from datetime import date
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ....models.employee import Employee, EmployeeStatus
from ....exceptions.repository_exceptions import RepositoryError
from .interfaces import (
    IEmployeeCrudOperations,
    IEmployeeQueryOperations,
    IEmployeeValidationOperations,
    IEmployeeStatisticsOperations,
    IEmployeeRelationshipOperations,
    IEmployeeDateOperations
)


class EmployeeRepositoryFacade:
    """
    Facade principal para el repositorio Employee.
    
    Proporciona una interfaz unificada para todas las operaciones del repositorio
    Employee, delegando a los módulos especializados correspondientes.
    Mantiene compatibilidad hacia atrás con la interfaz original.
    """
    
    def __init__(
        self,
        session: AsyncSession,
        crud_operations: IEmployeeCrudOperations,
        query_operations: IEmployeeQueryOperations,
        validation_operations: IEmployeeValidationOperations,
        statistics_operations: IEmployeeStatisticsOperations,
        relationship_operations: IEmployeeRelationshipOperations,
        date_operations: IEmployeeDateOperations
    ):
        """
        Inicializa el facade con todas las operaciones especializadas.
        
        Args:
            session: Sesión de base de datos SQLAlchemy
            crud_operations: Operaciones CRUD
            query_operations: Operaciones de consulta
            validation_operations: Operaciones de validación
            statistics_operations: Operaciones estadísticas
            relationship_operations: Operaciones de relaciones
            date_operations: Operaciones de fechas
        """
        self.session = session
        self._crud = crud_operations
        self._query = query_operations
        self._validation = validation_operations
        self._statistics = statistics_operations
        self._relationships = relationship_operations
        self._dates = date_operations
        self._logger = logger
    
    # ==========================================
    # OPERACIONES CRUD - Delegación a _crud
    # ==========================================
    
    async def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        """Crea un nuevo empleado."""
        return await self._crud.create_employee(employee_data)
    
    async def update_employee(self, employee_id: int, update_data: Dict[str, Any]) -> Optional[Employee]:
        """Actualiza un empleado."""
        return await self._crud.update_employee(employee_id, update_data)
    
    async def delete_employee(self, employee_id: int) -> bool:
        """Elimina un empleado."""
        return await self._crud.delete_employee(employee_id)
    
    
    # ==========================================
    # OPERACIONES DE CONSULTA - Delegación a _query
    # ==========================================
    
    async def search_by_name(self, name: str, **kwargs) -> List[Employee]:
        """Busca empleados por nombre."""
        return await self._query.search_by_name(name, **kwargs)
    
    async def get_by_email(self, email: str) -> Optional[Employee]:
        """Obtiene empleado por email."""
        return await self._query.get_by_email(email)
    
    async def get_by_status(self, status: EmployeeStatus, **kwargs) -> List[Employee]:
        """Obtiene empleados por estado."""
        return await self._query.get_by_status(status, **kwargs)
    
    async def get_available_employees(self, **kwargs) -> List[Employee]:
        """Obtiene empleados disponibles."""
        return await self._query.get_available_employees(**kwargs)
    
    async def search_by_skills(self, skills: List[str], **kwargs) -> List[Employee]:
        """Busca empleados por habilidades."""
        return await self._query.search_by_skills(skills, **kwargs)
    
    async def get_by_department(self, department: str, **kwargs) -> List[Employee]:
        """Obtiene empleados por departamento."""
        return await self._query.get_by_department(department, **kwargs)
    
    async def get_by_position(self, position: str, **kwargs) -> List[Employee]:
        """Obtiene empleados por posición."""
        return await self._query.get_by_position(position, **kwargs)
    
    async def get_by_salary_range(self, min_salary: float, max_salary: float, **kwargs) -> List[Employee]:
        """Obtiene empleados por rango salarial."""
        return await self._query.get_by_salary_range(min_salary, max_salary, **kwargs)
    
    async def get_by_hire_date_range(self, start_date: date, end_date: date, **kwargs) -> List[Employee]:
        """Obtiene empleados por rango de fecha de contratación."""
        return await self._query.get_by_hire_date_range(start_date, end_date, **kwargs)
    
    async def advanced_search(self, filters: Dict[str, Any], **kwargs) -> List[Employee]:
        """Búsqueda avanzada con múltiples filtros."""
        return await self._query.advanced_search(filters, **kwargs)
    
    # ==========================================
    # OPERACIONES DE VALIDACIÓN - Delegación a _validation
    # ==========================================
    
    async def validate_create_data(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida datos para crear empleado."""
        return await self._validation.validate_create_data(employee_data)
    
    async def validate_update_data(self, employee_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida datos para actualizar empleado."""
        return await self._validation.validate_update_data(employee_id, update_data)
    
    async def validate_email_unique(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Valida que el email sea único."""
        return await self._validation.validate_email_unique(email, exclude_id)
    
    def validate_skills_json(self, skills_data: Any) -> List[str]:
        """Valida formato JSON de habilidades."""
        return self._validation.validate_skills_json(skills_data)
    
    def validate_employee_id(self, employee_id: Any) -> int:
        """Valida ID de empleado."""
        return self._validation.validate_employee_id(employee_id)
    
    def validate_salary_range(self, min_salary: Any, max_salary: Any) -> tuple[float, float]:
        """Valida rango salarial."""
        return self._validation.validate_salary_range(min_salary, max_salary)
    
    def validate_date_range(self, start_date: Any, end_date: Any) -> tuple[date, date]:
        """Valida rango de fechas."""
        return self._validation.validate_date_range(start_date, end_date)
    
    # ==========================================
    # OPERACIONES ESTADÍSTICAS - Delegación a _statistics
    # ==========================================
    
    async def count_by_status(self, status: Optional[EmployeeStatus] = None) -> Dict[str, int]:
        """Cuenta empleados por estado."""
        return await self._statistics.count_by_status(status)
    
    async def get_salary_statistics(self, **kwargs) -> Dict[str, float]:
        """Obtiene estadísticas salariales."""
        return await self._statistics.get_salary_statistics(**kwargs)
    
    async def get_department_distribution(self) -> Dict[str, int]:
        """Obtiene distribución por departamento."""
        return await self._statistics.get_department_distribution()
    
    async def get_position_distribution(self) -> Dict[str, int]:
        """Obtiene distribución por posición."""
        return await self._statistics.get_position_distribution()
    
    async def get_skills_distribution(self) -> Dict[str, int]:
        """Obtiene distribución de habilidades."""
        return await self._statistics.get_skills_distribution()
    
    async def get_hire_date_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de fechas de contratación."""
        return await self._statistics.get_hire_date_statistics()
    
    async def get_employee_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas generales de empleados."""
        return await self._statistics.get_employee_metrics()
    
    # ==========================================
    # OPERACIONES DE RELACIONES - Delegación a _relationships
    # ==========================================
    
    async def get_employee_teams(self, employee_id: int):
        """Obtiene equipos del empleado."""
        return await self._relationships.get_employee_teams(employee_id)
    
    async def get_employee_projects(self, employee_id: int):
        """Obtiene proyectos del empleado."""
        return await self._relationships.get_employee_projects(employee_id)
    
    async def get_employee_vacations(self, employee_id: int):
        """Obtiene vacaciones del empleado."""
        return await self._relationships.get_employee_vacations(employee_id)
    
    async def get_team_memberships(self, employee_id: int):
        """Obtiene membresías de equipo del empleado."""
        return await self._relationships.get_team_memberships(employee_id)
    
    async def get_project_assignments(self, employee_id: int):
        """Obtiene asignaciones de proyecto del empleado."""
        return await self._relationships.get_project_assignments(employee_id)
    
    async def check_team_membership(self, employee_id: int, team_id: int) -> bool:
        """Verifica si un empleado pertenece a un equipo específico."""
        return await self._relationships.check_team_membership(employee_id, team_id)
    
    async def check_project_assignment(self, employee_id: int, project_id: int) -> bool:
        """Verifica si un empleado está asignado a un proyecto específico."""
        return await self._relationships.check_project_assignment(employee_id, project_id)
    
    async def get_employees_by_team(self, team_id: int):
        """Obtiene empleados de un equipo específico."""
        return await self._relationships.get_employees_by_team(team_id)
    
    async def get_employees_by_project(self, project_id: int):
        """Obtiene empleados de un proyecto específico."""
        return await self._relationships.get_employees_by_project(project_id)
    
    async def validate_employee_exists(self, employee_id: int):
        """Valida que un empleado existe y lo retorna."""
        return await self._relationships.validate_employee_exists(employee_id)
    
    async def get_employee_with_all_relations(self, employee_id: int):
        """Obtiene un empleado con todas sus relaciones cargadas."""
        return await self._relationships.get_employee_with_all_relations(employee_id)
    
    async def count_employee_relationships(self, employee_id: int):
        """Cuenta las relaciones de un empleado."""
        return await self._relationships.count_employee_relationships(employee_id)
    
    async def has_dependencies(self, employee_id: int) -> bool:
        """Verifica si un empleado tiene dependencias que impidan su eliminación."""
        return await self._relationships.has_dependencies(employee_id)
    
    # ==========================================
    # OPERACIONES DE FECHAS - Delegación a _dates
    # ==========================================
    
    async def get_employees_hired_current_week(self, **kwargs) -> List[Employee]:
        """Obtiene empleados contratados esta semana."""
        return await self._dates.get_employees_hired_current_week(**kwargs)
    
    async def get_employees_hired_current_month(self, **kwargs) -> List[Employee]:
        """Obtiene empleados contratados este mes."""
        return await self._dates.get_employees_hired_current_month(**kwargs)
    
    async def get_employees_hired_business_days_only(
        self, 
        start_date: Union[date, str, None] = None,
        end_date: Union[date, str, None] = None,
        **kwargs
    ) -> List[Employee]:
        """Obtiene empleados contratados en días laborables."""
        return await self._dates.get_employees_hired_business_days_only(start_date, end_date, **kwargs)
    
    async def get_employee_tenure_stats(self, employee_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas de antigüedad del empleado."""
        return await self._dates.get_employee_tenure_stats(employee_id)
    
    async def get_employees_by_tenure_range(
        self,
        min_years: float = 0.0,
        max_years: Optional[float] = None,
        status: Optional[EmployeeStatus] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene empleados por rango de antigüedad."""
        return await self._dates.get_employees_by_tenure_range(min_years, max_years, status)
    
    async def create_employee_with_pendulum_validation(
        self,
        employee_data: Dict[str, Any],
        validate_hire_date_business_day: bool = False
    ) -> Employee:
        """Crea empleado con validación avanzada de fechas."""
        return await self._dates.create_employee_with_pendulum_validation(
            employee_data, validate_hire_date_business_day
        )
    
    def format_employee_hire_date(self, employee: Employee, format_type: str = 'default') -> Optional[str]:
        """Formatea fecha de contratación del empleado."""
        return self._dates.format_employee_hire_date(employee, format_type)
    
    # ==========================================
    # MÉTODOS CRUD BÁSICOS - Delegación a _crud
    # ==========================================
    
    async def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """Obtiene un empleado por ID."""
        return await self._query.get_by_id(employee_id)
    
    async def get_all(self, **kwargs) -> List[Employee]:
        """Obtiene todos los empleados."""
        return await self._query.get_all(**kwargs)
    
    async def exists(self, employee_id: int) -> bool:
        """Verifica si un empleado existe."""
        return await self._query.exists(employee_id)
    
    # ==========================================
    # MÉTODOS DE COMPATIBILIDAD HACIA ATRÁS
    # ==========================================
    
    async def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """Alias para compatibilidad hacia atrás."""
        return await self.get_by_id(employee_id)
    
    async def get_all_employees(self, **kwargs) -> List[Employee]:
        """Alias para compatibilidad hacia atrás."""
        return await self.get_all(**kwargs)
    
    async def update_employee_data(self, employee_id: int, update_data: Dict[str, Any]) -> Optional[Employee]:
        """Alias para compatibilidad hacia atrás."""
        return await self.update_employee(employee_id, update_data)
    
    async def employee_exists(self, employee_id: int) -> bool:
        """Alias para compatibilidad hacia atrás."""
        return await self.exists(employee_id)