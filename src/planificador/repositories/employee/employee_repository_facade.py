from typing import Any, Dict, List, Optional, Union
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from ...models.employee import Employee, EmployeeStatus
from .interfaces.crud_interface import IEmployeeCrudOperations
from .interfaces.date_interface import IEmployeeDateOperations
from .interfaces.query_interface import IEmployeeQueryOperations
from .interfaces.relationship_interface import IEmployeeRelationshipOperations
from .interfaces.statistics_interface import IEmployeeStatisticsOperations
from .interfaces.validation_interface import IEmployeeValidationOperations
from .modules.crud_operations import CrudOperations
from .modules.date_operations import DateOperations
from .modules.query_operations import QueryOperations
from .modules.relationship_operations import RelationshipOperations
from .modules.statistics_operations import StatisticsOperations
from .modules.validation_operations import ValidationOperations


class EmployeeRepositoryFacade(
    IEmployeeCrudOperations,
    IEmployeeDateOperations,
    IEmployeeQueryOperations,
    IEmployeeRelationshipOperations,
    IEmployeeStatisticsOperations,
    IEmployeeValidationOperations,
):
    """Facade que unifica las operaciones de CRUD, consultas y fechas para empleados."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._crud: IEmployeeCrudOperations = CrudOperations(session)
        self._queries: IEmployeeQueryOperations = QueryOperations(session)
        self._dates: IEmployeeDateOperations = DateOperations(session)
        self._relationships: IEmployeeRelationshipOperations = RelationshipOperations(
            session
        )
        self._statistics: IEmployeeStatisticsOperations = StatisticsOperations(session)
        self._validation: IEmployeeValidationOperations = ValidationOperations()

    # ============================================================================
    # OPERACIONES CRUD - Delegación a _crud
    # ============================================================================
    
    async def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        """Crea un nuevo empleado."""
        return await self._crud.create_employee(employee_data)
    
    async def update_employee(self, employee_id: int, update_data: Dict[str, Any]) -> Optional[Employee]:
        """Actualiza un empleado."""
        return await self._crud.update_employee(employee_id, update_data)
    
    async def delete_employee(self, employee_id: int) -> bool:
        """Elimina un empleado."""
        return await self._crud.delete_employee(employee_id)
    
    # ============================================================================
    # OPERACIONES DE FECHAS - Delegación a _dates
    # ============================================================================

    async def get_employees_hired_current_week(self, **kwargs) -> List[Employee]:
        """Obtiene empleados contratados en la semana actual."""
        return await self._dates.get_employees_hired_current_week(**kwargs)

    async def get_employees_hired_current_month(self, **kwargs) -> List[Employee]:
        """Obtiene empleados contratados en el mes actual."""
        return await self._dates.get_employees_hired_current_month(**kwargs)

    async def get_employees_hired_business_days_only(
        self,
        start_date: Union[date, str, None] = None,
        end_date: Union[date, str, None] = None,
        **kwargs,
    ) -> List[Employee]:
        """Obtiene empleados contratados solo en días laborables."""
        return await self._dates.get_employees_hired_business_days_only(
            start_date=start_date, end_date=end_date, **kwargs
        )

    async def get_by_hire_date_range(
        self, start_date: date, end_date: date, **kwargs
    ) -> List[Employee]:
        """Obtiene empleados por rango de fecha de contratación."""
        return await self._dates.get_by_hire_date_range(
            start_date=start_date, end_date=end_date, **kwargs
        )

    async def get_employee_tenure_stats(self, employee_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas de antigüedad de un empleado."""
        return await self._dates.get_employee_tenure_stats(employee_id)

    async def get_employees_by_tenure_range(
        self,
        min_years: float = 0.0,
        max_years: Optional[float] = None,
        status: Optional[EmployeeStatus] = None,
    ) -> List[Dict[str, Any]]:
        """Obtiene empleados por rango de antigüedad."""
        return await self._dates.get_employees_by_tenure_range(
            min_years=min_years, max_years=max_years, status=status
        )

    async def create_employee_with_date_validation(
        self,
        employee_data: Dict[str, Any],
        validate_hire_date_business_day: bool = False,
    ) -> Employee:
        """Crea un empleado con validación avanzada de fechas."""
        return await self._dates.create_employee_with_date_validation(
            employee_data=employee_data,
            validate_hire_date_business_day=validate_hire_date_business_day,
        )

    def format_employee_hire_date(
        self, employee: Employee, format_type: str = "default"
    ) -> Optional[str]:
        """Formatea la fecha de contratación de un empleado."""
        return self._dates.format_employee_hire_date(
            employee=employee, format_type=format_type
        )
    
    
    # ============================================================================
    # OPERACIONES DE CONSULTA
    # ============================================================================

    async def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """Obtiene un empleado por su ID."""
        return await self._queries.get_by_id(employee_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Obtiene todos los empleados con paginación."""
        return await self._queries.get_all(skip, limit)

    async def employee_exists(self, employee_id: int) -> bool:
        """Verifica si un empleado existe."""
        return await self._queries.employee_exists(employee_id)

    async def count(self) -> int:
        """Cuenta el número total de empleados."""
        return await self._queries.count()

    async def search_by_name(self, name: str, **kwargs) -> List[Employee]:
        """Busca empleados por nombre."""
        return await self._queries.search_by_name(name, **kwargs)

    async def get_by_email(self, email: str) -> Optional[Employee]:
        """Obtiene un empleado por su email."""
        return await self._queries.get_by_email(email)

    async def get_by_status(self, status: EmployeeStatus, **kwargs) -> List[Employee]:
        """Obtiene empleados por su estado."""
        return await self._queries.get_by_status(status, **kwargs)

    async def get_available_employees(self, **kwargs) -> List[Employee]:
        """Obtiene empleados disponibles."""
        return await self._queries.get_available_employees(**kwargs)

    async def search_by_skills(self, skills: Union[str, List[str]], **kwargs) -> List[Employee]:
        """Busca empleados por habilidades."""
        return await self._queries.search_by_skills(skills, **kwargs)

    async def get_by_department(self, department: str, **kwargs) -> List[Employee]:
        """Obtiene empleados por departamento."""
        return await self._queries.get_by_department(department, **kwargs)

    async def get_by_position(self, position: str, **kwargs) -> List[Employee]:
        """Obtiene empleados por posición."""
        return await self._queries.get_by_position(position, **kwargs)

    async def get_by_salary_range(self, min_salary: float, max_salary: float, **kwargs) -> List[Employee]:
        """Obtiene empleados por rango salarial."""
        return await self._queries.get_by_salary_range(min_salary, max_salary, **kwargs)

    async def get_by_hire_date_range(self, start_date: date, end_date: date, **kwargs) -> List[Employee]:
        """Obtiene empleados por rango de fecha de contratación."""
        return await self._queries.get_by_hire_date_range(start_date, end_date, **kwargs)

    async def advanced_search(self, filters: Dict[str, Any], **kwargs) -> List[Employee]:
        """Realiza una búsqueda avanzada de empleados."""
        return await self._queries.advanced_search(filters, **kwargs)

    async def get_by_full_name(self, full_name: str) -> Optional[Employee]:
        """Obtiene un empleado por su nombre completo."""
        return await self._queries.get_by_full_name(full_name)

    async def get_by_employee_code(self, employee_code: str) -> Optional[Employee]:
        """Obtiene un empleado por su código de empleado."""
        return await self._queries.get_by_employee_code(employee_code)

    async def get_active_employees(self) -> List[Employee]:
        """Obtiene todos los empleados activos."""
        return await self._queries.get_active_employees()

    async def get_with_teams(self, employee_id: int) -> Optional[Employee]:
        """Obtiene un empleado con sus equipos."""
        return await self._queries.get_with_teams(employee_id)

    async def get_with_projects(self, employee_id: int) -> Optional[Employee]:
        """Obtiene un empleado con sus proyectos."""
        return await self._queries.get_with_projects(employee_id)

    async def full_name_exists(self, full_name: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si un nombre completo de empleado ya existe."""
        return await self._queries.full_name_exists(full_name, exclude_id)

    async def employee_code_exists(self, employee_code: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si un código de empleado ya existe."""
        return await self._queries.employee_code_exists(employee_code, exclude_id)

    async def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si un email de empleado ya existe."""
        return await self._queries.email_exists(email, exclude_id)


    # ============================================================================
    # OPERACIONES DE RELACIONES - Delegación a _relationships
    # ============================================================================

    async def get_employee_teams(self, employee_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los equipos a los que pertenece un empleado."""
        return await self._relationships.get_employee_teams(employee_id)

    async def get_employee_projects(self, employee_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los proyectos asignados a un empleado."""
        return await self._relationships.get_employee_projects(employee_id)

    async def get_employee_vacations(self, employee_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las vacaciones de un empleado."""
        return await self._relationships.get_employee_vacations(employee_id)

    async def get_team_memberships(self, employee_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las membresías de equipo de un empleado."""
        return await self._relationships.get_team_memberships(employee_id)

    async def get_project_assignments(self, employee_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las asignaciones de proyecto de un empleado."""
        return await self._relationships.get_project_assignments(employee_id)

    async def check_team_membership(self, employee_id: int, team_id: int) -> bool:
        """Verifica si un empleado pertenece a un equipo específico."""
        return await self._relationships.check_team_membership(employee_id, team_id)

    async def check_project_assignment(self, employee_id: int, project_id: int) -> bool:
        """Verifica si un empleado está asignado a un proyecto específico."""
        return await self._relationships.check_project_assignment(employee_id, project_id)

    async def get_employees_by_team(self, team_id: int) -> List[Employee]:
        """Obtiene todos los empleados de un equipo específico."""
        return await self._relationships.get_employees_by_team(team_id)

    async def get_employees_by_project(self, project_id: int) -> List[Employee]:
        """Obtiene todos los empleados asignados a un proyecto específico."""
        return await self._relationships.get_employees_by_project(project_id)

    async def validate_employee_exists(self, employee_id: int) -> Employee:
        """Valida que un empleado existe y lo retorna."""
        return await self._relationships.validate_employee_exists(employee_id)

    async def get_employee_with_all_relations(self, employee_id: int) -> Optional[Employee]:
        """Obtiene un empleado con todas sus relaciones cargadas."""
        return await self._relationships.get_employee_with_all_relations(employee_id)

    async def count_employee_relationships(self, employee_id: int) -> Dict[str, int]:
        """Cuenta las relaciones de un empleado."""
        return await self._relationships.count_employee_relationships(employee_id)

    async def has_dependencies(self, employee_id: int) -> bool:
        """Verifica si un empleado tiene dependencias que impidan su eliminación."""
        return await self._relationships.has_dependencies(employee_id)


    # ============================================================================
    # OPERACIONES DE ESTADÍSTICAS - Delegación a _statistics
    # ============================================================================

    async def get_employee_count_by_status(self) -> Dict[str, int]:
        """Obtiene el conteo de empleados por estado."""
        return await self._statistics.get_employee_count_by_status()

    async def get_employee_count_by_department(self) -> Dict[str, int]:
        """Obtiene el conteo de empleados por departamento."""
        return await self._statistics.get_employee_count_by_department()

    async def get_employee_count_by_position(self) -> Dict[str, int]:
        """Obtiene el conteo de empleados por posición."""
        return await self._statistics.get_employee_count_by_position()

    async def get_salary_statistics(self) -> Dict[str, float]:
        """Obtiene estadísticas de salarios."""
        return await self._statistics.get_salary_statistics()

    async def get_hire_date_distribution(self, period: str = "monthly") -> Dict[str, int]:
        """Obtiene la distribución de fechas de contratación."""
        return await self._statistics.get_hire_date_distribution(period)

    async def get_team_participation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de participación en equipos."""
        return await self._statistics.get_team_participation_stats()

    async def get_project_participation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de participación en proyectos."""
        return await self._statistics.get_project_participation_stats()

    async def get_vacation_statistics(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene estadísticas sobre las solicitudes de vacaciones."""
        return await self._statistics.get_vacation_statistics(year)

    async def get_skills_distribution(self, limit: int = 20) -> Dict[str, int]:
        """Obtiene la distribución de habilidades más comunes."""
        return await self._statistics.get_skills_distribution(limit)

    async def get_employee_workload_stats(self, employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Obtiene estadísticas de carga de trabajo de un empleado."""
        return await self._statistics.get_employee_workload_stats(employee_id, start_date, end_date)

    async def get_comprehensive_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen completo de estadísticas de empleados."""
        return await self._statistics.get_comprehensive_summary()


    # ============================================================================
    # OPERACIONES DE VALIDACIÓN - Delegación a _validation
    # ============================================================================

    def validate_create_data(self, data: Dict[str, Any]) -> None:
        """Valida los datos para crear un nuevo empleado."""
        return self._validation.validate_create_data(data)

    def validate_update_data(self, data: Dict[str, Any]) -> None:
        """Valida los datos para actualizar un empleado existente."""
        return self._validation.validate_update_data(data)

    def validate_skills_json(
        self, skills_json: Optional[str]
    ) -> Optional[List[str]]:
        """Valida y convierte un JSON de habilidades a lista."""
        return self._validation.validate_skills_json(skills_json)

    def validate_search_term(self, search_term: str) -> str:
        """Valida y limpia un término de búsqueda."""
        return self._validation.validate_search_term(search_term)

    def validate_employee_id(self, employee_id: int) -> None:
        """Valida que un ID de empleado sea válido."""
        return self._validation.validate_employee_id(employee_id)
    
    