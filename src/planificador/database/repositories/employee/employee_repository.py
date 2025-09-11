# src/planificador/database/repositories/employee/employee_repository.py

from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import pendulum
from pendulum import DateTime, Date
from loguru import logger

from ..base_repository import BaseRepository
from ..date_mixin import DateMixin
from ....models.employee import Employee, EmployeeStatus
from ....utils.date_utils import (
    get_current_time,
    format_datetime,
    is_business_day,
    add_business_days,
    get_business_days
)
from ....exceptions.repository import (
    convert_sqlalchemy_error,
    EmployeeRepositoryError,
    EmployeeQueryError,
    EmployeeStatisticsError,
    EmployeeValidationRepositoryError,
    EmployeeRelationshipError,
    EmployeeBulkOperationError,
    EmployeeDateRangeError,
    EmployeeSkillsError,
    EmployeeAvailabilityError,
    create_employee_query_error,
    create_employee_statistics_error,
    create_employee_validation_repository_error,
    create_employee_relationship_error,
    create_employee_bulk_operation_error,
    create_employee_date_range_error,
    create_employee_skills_error,
    create_employee_availability_error
)
from .employee_query_builder import EmployeeQueryBuilder
from .employee_validator import EmployeeValidator
from .employee_relationship_manager import EmployeeRelationshipManager
from .employee_statistics import EmployeeStatistics


class EmployeeRepository(BaseRepository[Employee], DateMixin):
    """
    Repositorio específico para la gestión de empleados.
    
    Proporciona métodos especializados para operaciones relacionadas con empleados,
    incluyendo búsquedas por nombre, código, estado, disponibilidad y gestión de asignaciones.
    Implementa una arquitectura modular con componentes especializados.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Employee, session)
        
        # Inicializar componentes modulares
        self.query_builder = EmployeeQueryBuilder(session)
        self.validator = EmployeeValidator()
        self.relationship_manager = EmployeeRelationshipManager(session, self.query_builder)
        self.statistics = EmployeeStatistics(session)
    
    # ============================================================================
    # OPERACIONES CRUD BÁSICAS
    # ============================================================================
    
    async def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        """
        Crea un nuevo empleado con validaciones.
        
        Args:
            employee_data: Datos del empleado
            
        Returns:
            Empleado creado
            
        Raises:
            ValueError: Si algún campo único ya existe
        """
        try:
            # Validar datos de creación
            await self.validator.validate_create_data(employee_data)
            
            # Crear empleado
            employee = await self.create(employee_data)
            self.logger.info(f"Empleado creado exitosamente: {employee.full_name} (ID: {employee.id})")
            return employee
            
        except ValueError as e:
            await self.session.rollback()
            raise create_employee_validation_repository_error(
                field="employee_data",
                value=str(employee_data),
                reason=f"Error de validación: {str(e)}",
                operation="create_employee"
            )
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_employee",
                entity_type="Employee"
            )
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error inesperado creando empleado: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado creando empleado: {e}",
                operation="create_employee",
                entity_type="Employee",
                original_error=e
            )
    
    async def update_employee(self, employee_id: int, update_data: Dict[str, Any]) -> Optional[Employee]:
        """
        Actualiza un empleado con validaciones.
        
        Args:
            employee_id: ID del empleado
            update_data: Datos a actualizar
            
        Returns:
            Empleado actualizado o None si no existe
            
        Raises:
            ValueError: Si algún campo único ya existe
        """
        try:
            # Validar datos de actualización
            await self.validator.validate_update_data(update_data, employee_id)
            
            # Actualizar empleado
            employee = await self.update(employee_id, update_data)
            if employee:
                self.logger.info(f"Empleado actualizado exitosamente: {employee.full_name} (ID: {employee.id})")
            return employee
            
        except ValueError as e:
            await self.session.rollback()
            raise create_employee_validation_repository_error(
                field="update_data",
                value=str(update_data),
                reason=f"Error de validación: {str(e)}",
                operation="update_employee"
            )
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_employee",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Error inesperado actualizando empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado actualizando empleado: {e}",
                operation="update_employee",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )
    
    # get_by_id está heredado de BaseRepository
    
    # ============================================================================
    # CONSULTAS POR IDENTIFICADORES ÚNICOS
    # ============================================================================
    
    async def get_by_full_name(self, full_name: str) -> Optional[Employee]:
        """
        Busca un empleado por su nombre completo.
        
        Args:
            full_name: Nombre completo del empleado
            
        Returns:
            Empleado encontrado o None
            
        Raises:
            EmployeeQueryError: Si la consulta falla
            EmployeeValidationRepositoryError: Si el nombre no es válido
        """
        try:
            # Validar parámetros de entrada
            if not full_name or not full_name.strip():
                raise create_employee_validation_repository_error(
                    field="full_name",
                    value=full_name,
                    reason="El nombre completo no puede estar vacío",
                    operation="get_by_full_name"
                )
            
            if len(full_name.strip()) < 2:
                raise create_employee_validation_repository_error(
                    field="full_name",
                    value=full_name,
                    reason="El nombre completo debe tener al menos 2 caracteres",
                    operation="get_by_full_name"
                )
            
            # Ejecutar consulta
            employee = await self.query_builder.get_by_full_name(full_name.strip())
            
            if employee:
                self.logger.debug(f"Empleado encontrado por nombre completo: {full_name}")
            else:
                self.logger.debug(f"No se encontró empleado con nombre completo: {full_name}")
            
            return employee
            
        except (EmployeeValidationRepositoryError, EmployeeQueryError):
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado buscando empleado por nombre completo '{full_name}': {e}")
            raise create_employee_query_error(
                query_type="get_by_full_name",
                parameters={"full_name": full_name},
                reason=f"Error inesperado: {str(e)}",
                original_error=e
            )
    
    async def get_by_employee_code(self, employee_code: str) -> Optional[Employee]:
        """
        Busca un empleado por su código único.
        
        Args:
            employee_code: Código único del empleado
            
        Returns:
            Empleado encontrado o None
        """
        return await self.query_builder.get_by_employee_code(employee_code)
    
    async def get_by_email(self, email: str) -> Optional[Employee]:
        """
        Busca un empleado por su email.
        
        Args:
            email: Email del empleado
            
        Returns:
            Empleado encontrado o None
        """
        return await self.query_builder.get_by_email(email)
    
    # ============================================================================
    # CONSULTAS POR ATRIBUTOS
    # ============================================================================
    
    async def search_by_name(self, search_term: str) -> List[Employee]:
        """
        Busca empleados por patrón de nombre.
        
        Args:
            search_term: Término de búsqueda
            
        Returns:
            Lista de empleados que coinciden
        """
        return await self.query_builder.search_by_name(search_term)
    
    async def get_by_status(self, status: EmployeeStatus) -> List[Employee]:
        """
        Obtiene empleados por estado.
        
        Args:
            status: Estado del empleado
            
        Returns:
            Lista de empleados con el estado especificado
        """
        return await self.query_builder.get_by_status(status)
    
    async def get_active_employees(self) -> List[Employee]:
        """
        Obtiene todos los empleados activos.
        
        Returns:
            Lista de empleados activos
        """
        return await self.query_builder.get_active_employees()
    
    async def get_available_employees(self, target_date: Optional[date] = None) -> List[Employee]:
        """
        Obtiene empleados disponibles en una fecha específica.
        
        Args:
            target_date: Fecha objetivo (por defecto hoy)
            
        Returns:
            Lista de empleados disponibles
        """
        try:
            return await self.query_builder.get_available_employees(target_date)
        except Exception as e:
            raise create_employee_availability_error(
                date=target_date or date.today(),
                reason=f"Error obteniendo empleados disponibles: {str(e)}",
                original_error=e
            )
    
    async def get_by_department(self, department: str) -> List[Employee]:
        """
        Obtiene empleados por departamento.
        
        Args:
            department: Nombre del departamento
            
        Returns:
            Lista de empleados del departamento
        """
        return await self.query_builder.get_by_department(department)
    
    async def get_by_position(self, position: str) -> List[Employee]:
        """
        Obtiene empleados por posición.
        
        Args:
            position: Nombre de la posición
            
        Returns:
            Lista de empleados con la posición especificada
        """
        return await self.query_builder.get_by_position(position)
    
    # ============================================================================
    # CONSULTAS POR HABILIDADES
    # ============================================================================
    
    async def get_by_skills(self, skills: List[str]) -> List[Employee]:
        """
        Obtiene empleados que tienen habilidades específicas.
        
        Args:
            skills: Lista de habilidades requeridas
            
        Returns:
            Lista de empleados con las habilidades
            
        Raises:
            EmployeeSkillsError: Si hay error en la consulta de habilidades
        """
        try:
            # Validar entrada
            if not skills:
                raise create_employee_skills_error(
                    skills=[],
                    reason="La lista de habilidades no puede estar vacía",
                    operation="get_by_skills"
                )
            
            # Limpiar y validar habilidades
            clean_skills = [skill.strip() for skill in skills if skill and skill.strip()]
            if not clean_skills:
                raise create_employee_skills_error(
                    skills=skills,
                    reason="No se proporcionaron habilidades válidas",
                    operation="get_by_skills"
                )
            
            # Ejecutar consulta
            employees = await self.query_builder.get_by_skills(clean_skills)
            
            self.logger.debug(f"Encontrados {len(employees)} empleados con habilidades: {clean_skills}")
            return employees
            
        except EmployeeSkillsError:
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado buscando empleados por habilidades {skills}: {e}")
            raise create_employee_skills_error(
                skills=skills,
                reason=f"Error inesperado en consulta: {str(e)}",
                operation="get_by_skills",
                original_error=e
            )
    
    # ============================================================================
    # CONSULTAS CON RELACIONES
    # ============================================================================
    
    async def get_with_teams(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado con información de equipos.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado con equipos cargados o None
        """
        return await self.relationship_manager.get_with_teams(employee_id)
    
    async def get_with_projects(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado con sus proyectos asignados.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado con proyectos cargados o None
        """
        return await self.relationship_manager.get_with_projects(employee_id)
    
    async def get_employee_teams(self, employee_id: int) -> List[Any]:
        """
        Obtiene los equipos de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de equipos del empleado
        """
        return await self.relationship_manager.get_employee_teams(employee_id)
    
    async def get_employee_projects(self, employee_id: int) -> List[Any]:
        """
        Obtiene los proyectos de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de proyectos del empleado
        """
        return await self.relationship_manager.get_employee_projects(employee_id)
    
    async def get_employee_vacations(self, employee_id: int) -> List[Any]:
        """
        Obtiene las vacaciones de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de vacaciones del empleado
        """
        return await self.relationship_manager.get_employee_vacations(employee_id)
    
    async def get_employee_time_records(self, employee_id: int) -> List[Any]:
        """
        Obtiene los registros de tiempo de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de registros de tiempo del empleado
        """
        return await self.relationship_manager.get_employee_time_records(employee_id)
    
    # ============================================================================
    # VALIDACIONES DE DEPENDENCIAS
    # ============================================================================
    
    async def has_team_memberships(self, employee_id: int) -> bool:
        """
        Verifica si el empleado tiene membresías en equipos.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            True si tiene membresías en equipos
        """
        return await self.relationship_manager.has_team_memberships(employee_id)
    
    async def has_project_assignments(self, employee_id: int) -> bool:
        """
        Verifica si el empleado tiene asignaciones de proyecto.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            True si tiene asignaciones de proyecto
        """
        return await self.relationship_manager.has_project_assignments(employee_id)
    
    async def has_vacations(self, employee_id: int) -> bool:
        """
        Verifica si el empleado tiene vacaciones registradas.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            True si tiene vacaciones registradas
        """
        return await self.relationship_manager.has_vacations(employee_id)
    
    async def has_time_records(self, employee_id: int) -> bool:
        """
        Verifica si el empleado tiene registros de tiempo.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            True si tiene registros de tiempo
        """
        return await self.relationship_manager.has_time_records(employee_id)
    
    async def count_dependencies(self, employee_id: int) -> Dict[str, int]:
        """
        Cuenta todas las dependencias del empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Diccionario con conteos de dependencias
        """
        return await self.relationship_manager.count_dependencies(employee_id)
    
    # ============================================================================
    # VALIDACIONES DE UNICIDAD
    # ============================================================================
    
    async def full_name_exists(self, full_name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un nombre completo.
        
        Args:
            full_name: Nombre completo a verificar
            exclude_id: ID a excluir de la verificación
            
        Returns:
            True si el nombre ya existe
        """
        return await self.query_builder.full_name_exists(full_name, exclude_id)
    
    async def employee_code_exists(self, employee_code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un código de empleado.
        
        Args:
            employee_code: Código a verificar
            exclude_id: ID a excluir de la verificación
            
        Returns:
            True si el código ya existe
        """
        return await self.query_builder.employee_code_exists(employee_code, exclude_id)
    
    async def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si existe un email.
        
        Args:
            email: Email a verificar
            exclude_id: ID a excluir de la verificación
            
        Returns:
            True si el email ya existe
        """
        return await self.query_builder.email_exists(email, exclude_id)
    
    # ============================================================================
    # ESTADÍSTICAS BÁSICAS
    # ============================================================================
    
    async def get_employee_workload_stats(self, employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Obtiene estadísticas de carga de trabajo.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Estadísticas de carga de trabajo
        """
        return await self.statistics.get_employee_workload_stats(employee_id, start_date, end_date)
    
    async def get_count_by_status(self) -> Dict[str, int]:
        """
        Obtiene conteo de empleados por estado.
        
        Returns:
            Diccionario con conteos por estado
        """
        return await self.statistics.get_employee_count_by_status()
    
    async def get_count_by_department(self) -> Dict[str, int]:
        """
        Obtiene conteo de empleados por departamento.
        
        Returns:
            Diccionario con conteos por departamento
        """
        return await self.statistics.get_employee_count_by_department()
    
    async def get_count_by_position(self) -> Dict[str, int]:
        """
        Obtiene conteo de empleados por posición.
        
        Returns:
            Diccionario con conteos por posición
        """
        return await self.statistics.get_employee_count_by_position()
    
    async def get_salary_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas salariales.
        
        Returns:
            Estadísticas salariales
        """
        return await self.statistics.get_salary_statistics()
    
    async def get_hire_date_distribution(self) -> Dict[str, Any]:
        """
        Obtiene distribución de fechas de contratación.
        
        Returns:
            Distribución de fechas de contratación
        """
        return await self.statistics.get_hire_date_distribution()
    
    async def get_team_participation_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de participación en equipos.
        
        Returns:
            Estadísticas de participación en equipos
        """
        return await self.statistics.get_team_participation_stats()
    
    async def get_project_participation_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de participación en proyectos.
        
        Returns:
            Estadísticas de participación en proyectos
        """
        return await self.statistics.get_project_participation_stats()
    
    async def get_vacation_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de vacaciones.
        
        Returns:
            Estadísticas de vacaciones
        """
        return await self.statistics.get_vacation_statistics()
    
    async def get_skills_distribution(self) -> Dict[str, Any]:
        """
        Obtiene distribución de habilidades.
        
        Returns:
            Distribución de habilidades
        """
        return await self.statistics.get_skills_distribution()
    
    # ============================================================================
    # ESTADÍSTICAS AVANZADAS
    # ============================================================================
    
    async def get_comprehensive_summary(self) -> Dict[str, Any]:
        """
        Obtiene resumen estadístico completo.
        
        Returns:
            Resumen estadístico completo
        """
        return await self.statistics.get_comprehensive_summary()
    
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
            employees = await self.query_builder.get_employees_by_hire_date_range(start_date, end_date)
            
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
            # Obtener empleados según estado
            if status:
                employees = await self.get_by_status(status)
            else:
                employees = await self.get_active_employees()
            
            current_date = get_current_time().date()
            result = []
            
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
                        result.append({
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
            result.sort(key=lambda x: x["tenure_years"], reverse=True)
            
            return result
            
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
    
    async def create_employee_with_pendulum_validation(
        self,
        employee_data: Dict[str, Any],
        validate_hire_date_business_day: bool = False
    ) -> Employee:
        """
        Crea empleado con validaciones de fecha usando Pendulum.
        
        Args:
            employee_data: Datos del empleado
            validate_hire_date_business_day: Si validar que la fecha de contratación sea día laborable
            
        Returns:
            Empleado creado
        """
        try:
            # Validar fecha de contratación con Pendulum si se especifica
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
                        operation="create_employee_with_pendulum_validation"
                    )
            
            # Crear empleado usando el método estándar
            return await self.create_employee(employee_data)
            
        except Exception as e:
            if isinstance(e, (EmployeeValidationRepositoryError, EmployeeRepositoryError)):
                raise
            
            raise create_employee_validation_repository_error(
                field="employee_data",
                value=str(employee_data),
                reason=f"Error en validación con Pendulum: {str(e)}",
                operation="create_employee_with_pendulum_validation",
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