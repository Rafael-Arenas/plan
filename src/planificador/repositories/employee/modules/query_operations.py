from typing import List, Optional, Dict, Any
from datetime import date

from loguru import logger

from planificador.repositories.base_repository import BaseRepository
from planificador.models.employee import Employee, EmployeeStatus
from ..interfaces.query_interface import IEmployeeQueryOperations


class QueryOperations(BaseRepository[Employee], IEmployeeQueryOperations):
    """
    Implementación de operaciones de consulta para empleados.
    
    Proporciona métodos para construir consultas complejas de empleados
    con diferentes criterios de búsqueda y filtrado.
    """
    
    def __init__(self, session: Any):
        super().__init__(session, Employee)
        self._logger = logger.bind(component="EmployeeQueryOperations")
    
    # ============================================================================
    # MÉTODOS DE CONSULTA PRINCIPALES
    # ============================================================================
    
    async def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado por su ID.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado encontrado o None
        """
        try:
            query = select(self.model_class).where(self.model_class.id == employee_id)
            result = await self.session.execute(query)
            employee = result.scalar_one_or_none()
            
            if employee:
                self._logger.debug(f"Empleado encontrado por ID: {employee_id}")
            else:
                self._logger.warning(f"Empleado no encontrado por ID: {employee_id}")
                
            return employee
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo empleado por ID {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_id",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo empleado por ID {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado al obtener el empleado con ID {employee_id}",
                operation="get_by_id",
                entity_type=self.model_class.__name__,
            )

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """
        Obtiene una lista paginada de todos los empleados.
        
        Args:
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de empleados
        """
        try:
            query = select(self.model_class).offset(skip).limit(limit).order_by(self.model_class.full_name)
            result = await self.session.execute(query)
            employees = result.scalars().all()
            
            self._logger.debug(f"Obtenidos {len(employees)} empleados (skip={skip}, limit={limit})")
            return list(employees)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo todos los empleados: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_all",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo todos los empleados: {e}")
            raise EmployeeRepositoryError(
                message="Error inesperado al obtener todos los empleados",
                operation="get_all",
                entity_type=self.model_class.__name__,
            )

    async def employee_exists(self, employee_id: int) -> bool:
        """
        Verifica si existe un empleado por ID.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            bool: True si el empleado existe, False en caso contrario
            
        Raises:
            EmployeeRepositoryError: Si ocurre un error durante la verificación
        """
        try:
            # Usar el método heredado de BaseRepository
            return await self.exists(employee_id)
            
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="employee_exists",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado verificando existencia de empleado {employee_id}: {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado al verificar la existencia del empleado con ID {employee_id}",
                operation="employee_exists",
                entity_type=self.model_class.__name__,
            )
    
    async def count(self) -> int:
        """
        Cuenta el número total de empleados.
        
        Returns:
            Número total de empleados
        """
        try:
            query = select(func.count(self.model_class.id))
            result = await self.session.execute(query)
            total_employees = result.scalar()
            
            self._logger.debug(f"Total de empleados contados: {total_employees}")
            return total_employees
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos contando empleados: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado contando empleados: {e}")
            raise EmployeeRepositoryError(
                message="Error inesperado al contar los empleados",
                operation="count",
                entity_type=self.model_class.__name__,
            )

    async def search_by_name(self, name: str, **kwargs) -> List[Employee]:
        """
        Busca empleados cuyo nombre contenga el término de búsqueda.
        
        Args:
            name: Término a buscar en el nombre
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados que coinciden
        """
        try:
            # Validar que el término de búsqueda no esté vacío
            if not name or not name.strip():
                self._logger.debug("Término de búsqueda vacío, retornando lista vacía")
                return []
            
            query = select(Employee).where(
                or_(
                    Employee.full_name.ilike(f"%{name}%"),
                    Employee.first_name.ilike(f"%{name}%"),
                    Employee.last_name.ilike(f"%{name}%")
                )
            ).order_by(Employee.full_name)
            
            result = await self.session.execute(query)
            employees = result.scalars().all()
            
            self._logger.debug(f"Encontrados {len(employees)} empleados con término: {name}")
            return list(employees)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos buscando empleados con término '{name}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_by_name",
                entity_type="Employee"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando empleados con término '{name}': {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado al buscar empleados con el término '{name}'",
                operation="search_by_name",
                entity_type=self.model_class.__name__,
            )
    
    async def get_by_email(self, email: str) -> Optional[Employee]:
        """
        Busca un empleado por su email (insensible a mayúsculas/minúsculas).
        
        Args:
            email: Email del empleado
            
        Returns:
            Empleado encontrado o None
        """
        try:
            return await self.find_by_criteria(
                {"func.lower(email)": func.lower(email)}
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_email",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al obtener el empleado con email {email}",
                operation="get_by_email",
                entity_type=self.model_class.__name__,
            )

    async def get_by_status(
        self, status: EmployeeStatus, **kwargs
    ) -> List[Employee]:
        """
        Obtiene empleados por su estado.
        
        Args:
            status: Estado del empleado
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados con el estado especificado
        """
        try:
            return await self.find_all_by_criteria(
                {"status": status}, order_by="full_name"
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_status",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al obtener empleados con estado {status}",
                operation="get_by_status",
                entity_type=self.model_class.__name__,
            )
    
    async def get_available_employees(self, **kwargs) -> List[Employee]:
        """
        Obtiene los empleados que están disponibles en una fecha determinada.
        Un empleado está disponible si:
        - Está activo.
        - No está de vacaciones en esa fecha.

        Args:
            **kwargs: Parámetros adicionales, incluyendo 'target_date'

        Returns:
            Una lista de empleados disponibles.
        """
        try:
            target_date = kwargs.get('target_date')
            if target_date is None:
                target_date = get_current_time().date()

            return await self.find_all_by_criteria(
                {
                    "status": EmployeeStatus.ACTIVE,
                    "id": {
                        "operator": "not_in",
                        "value": select(Vacation.employee_id).where(
                            and_(
                                Vacation.start_date <= target_date,
                                Vacation.end_date >= target_date,
                                Vacation.status == VacationStatus.APPROVED
                            )
                        )
                    }
                },
                order_by="full_name"
            )
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo empleados disponibles: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_available_employees",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo empleados disponibles: {e}")
            raise EmployeeRepositoryError(
                message="Error inesperado al obtener empleados disponibles",
                operation="get_available_employees",
                entity_type=self.model_class.__name__,
            )
    
    async def search_by_skills(self, skills: List[str], **kwargs) -> List[Employee]:
        """
        Obtiene empleados que tienen al menos una de las habilidades especificadas.
        Busca coincidencias parciales de palabras completas dentro del JSON de skills.
        
        Args:
            skills: Lista de habilidades a buscar
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados que tienen al menos una de las habilidades
        """
        try:
            if not skills:
                return []

            conditions = {
                "operator": "or",
                "conditions": [
                    {"skills": {"operator": "ilike", "value": f'%{skill}%'}}
                    for skill in skills
                ]
            }
            
            return await self.find_all_by_criteria(conditions, order_by="full_name")
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_by_skills",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al buscar empleados por habilidades",
                operation="search_by_skills",
                entity_type=self.model_class.__name__,
            )
    
    async def get_by_department(self, department: str, **kwargs) -> List[Employee]:
        """
        Obtiene empleados por departamento.
        
        Args:
            department: Nombre del departamento
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados del departamento
        """
        try:
            return await self.find_all_by_criteria(
                {"department": department}, order_by="full_name"
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_department",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al obtener empleados del departamento {department}",
                operation="get_by_department",
                entity_type=self.model_class.__name__,
            )
    
    async def get_by_position(self, position: str, **kwargs) -> List[Employee]:
        """
        Obtiene empleados por posición.
        
        Args:
            position: Posición del empleado
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados con la posición especificada
        """
        try:
            return await self.find_all_by_criteria(
                {"position": position}, order_by="full_name"
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_position",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al obtener empleados con la posición {position}",
                operation="get_by_position",
                entity_type=self.model_class.__name__,
            )
    
    async def get_by_salary_range(self, min_salary: float, max_salary: float, **kwargs) -> List[Employee]:
        """
        Obtiene empleados por rango salarial.
        
        Args:
            min_salary: Salario mínimo
            max_salary: Salario máximo
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados en el rango salarial
        """
        try:
            return await self.find_all_by_criteria(
                {"salary": {"operator": "between", "value": (min_salary, max_salary)}},
                order_by="salary_desc"
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_salary_range",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al obtener empleados por rango salarial",
                operation="get_by_salary_range",
                entity_type=self.model_class.__name__,
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
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al obtener empleados por rango de fecha de contratación",
                operation="get_by_hire_date_range",
                entity_type=self.model_class.__name__,
            )
    
    async def advanced_search(self, filters: Dict[str, Any], **kwargs) -> List[Employee]:
        """
        Búsqueda avanzada con múltiples filtros.
        
        Args:
            filters: Diccionario con filtros a aplicar
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de empleados que cumplen los filtros
        """
        order_by = kwargs.get('order_by') or filters.pop('order_by', 'full_name')
        
        try:
            return await self.find_all_by_criteria(filters, order_by=order_by)
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en búsqueda avanzada: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="advanced_search",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en búsqueda avanzada: {e}")
            raise EmployeeRepositoryError(
                message="Error inesperado durante la búsqueda avanzada de empleados",
                operation="advanced_search",
                entity_type=self.model_class.__name__,
            )
    
    # ============================================================================
    # MÉTODOS ADICIONALES DEL QUERY BUILDER ORIGINAL
    # ============================================================================
    
    async def get_by_full_name(self, full_name: str) -> Optional[Employee]:
        """
        Busca un empleado por su nombre completo.
        
        Args:
            full_name: Nombre completo del empleado
            
        Returns:
            Empleado encontrado o None
        """
        try:
            return await self.find_all_by_criteria(
                {"full_name": {"operator": "ilike", "value": f"%{full_name}%"}},
                order_by="full_name"
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_full_name",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al buscar empleados por nombre completo",
                operation="get_by_full_name",
                entity_type=self.model_class.__name__,
            )
    
    async def get_by_employee_code(self, employee_code: str) -> Optional[Employee]:
        """
        Busca un empleado por su código de empleado.
        
        Args:
            employee_code: Código del empleado
            
        Returns:
            Empleado encontrado o None
        """
        try:
            return await self.find_by_criteria({"employee_code": employee_code})
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_employee_code",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al buscar empleado por código",
                operation="get_by_employee_code",
                entity_type=self.model_class.__name__,
            )
    
    async def get_active_employees(self) -> List[Employee]:
        """
        Obtiene todos los empleados activos.
        
        Returns:
            Lista de empleados activos
        """
        try:
            return await self.find_all_by_criteria(
                {"status": EmployeeStatus.ACTIVE}, order_by="full_name"
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_active_employees",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al obtener empleados activos",
                operation="get_active_employees",
                entity_type=self.model_class.__name__,
            )
    
    async def get_with_teams(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado con sus equipos cargados.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado con equipos cargados o None
        """
        try:
            return await self.find_by_criteria(
                {"id": employee_id},
                options=[selectinload(Employee.team_memberships).selectinload(TeamMembership.team)]
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_teams",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al obtener empleado con equipos",
                operation="get_with_teams",
                entity_type=self.model_class.__name__,
            )
    
    async def get_with_projects(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado con sus proyectos asignados cargados.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado con proyectos cargados o None
        """
        try:
            return await self.find_by_criteria(
                {"id": employee_id},
                options=[selectinload(Employee.project_assignments).selectinload(ProjectAssignment.project)]
            )
        except SQLAlchemyError as e:
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_projects",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al obtener empleado con proyectos",
                operation="get_with_projects",
                entity_type=self.model_class.__name__,
            )
    
    # ============================================================================
    # VALIDACIONES DE EXISTENCIA
    # ============================================================================
    
    async def full_name_exists(self, full_name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si ya existe un empleado con el nombre completo especificado.
        
        Args:
            full_name: Nombre completo a verificar
            exclude_id: ID a excluir de la verificación
            
        Returns:
            True si el nombre ya existe
        """
        try:
            query = select(func.count(self.model_class.id)).where(
                func.lower(self.model_class.full_name) == func.lower(full_name)
            )
            
            if exclude_id:
                query = query.where(self.model_class.id != exclude_id)
            
            result = await self.session.execute(query)
            count = result.scalar()
            
            exists = count > 0
            self._logger.debug(f"Verificación de nombre '{full_name}': {'existe' if exists else 'no existe'}")
            return exists
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos verificando nombre '{full_name}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="full_name_exists",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            raise EmployeeRepositoryError(
                message=f"Error inesperado al verificar la existencia del nombre completo",
                operation="full_name_exists",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            self._logger.error(f"Error inesperado verificando nombre '{full_name}': {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado al verificar la existencia del nombre completo",
                operation="full_name_exists",
                entity_type=self.model_class.__name__,
            )
    
    async def employee_code_exists(self, employee_code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si ya existe un empleado con el código especificado.
        
        Args:
            employee_code: Código a verificar
            exclude_id: ID a excluir de la verificación
            
        Returns:
            True si el código ya existe
        """
        try:
            query = select(func.count(self.model_class.id)).where(
                self.model_class.employee_code == employee_code
            )
            
            if exclude_id:
                query = query.where(self.model_class.id != exclude_id)
            
            result = await self.session.execute(query)
            count = result.scalar()
            
            exists = count > 0
            self._logger.debug(f"Verificación de código '{employee_code}': {'existe' if exists else 'no existe'}")
            return exists
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos verificando código '{employee_code}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="employee_code_exists",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            self._logger.error(f"Error inesperado verificando código '{employee_code}': {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado al verificar la existencia del código de empleado",
                operation="employee_code_exists",
                entity_type=self.model_class.__name__,
            )
    
    async def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si ya existe un empleado con el email especificado.
        
        Args:
            email: Email a verificar
            exclude_id: ID a excluir de la verificación
            
        Returns:
            True si el email ya existe
        """
        try:
            query = select(func.count(self.model_class.id)).where(
                func.lower(self.model_class.email) == func.lower(email)
            )
            
            if exclude_id:
                query = query.where(self.model_class.id != exclude_id)
            
            result = await self.session.execute(query)
            count = result.scalar()
            
            exists = count > 0
            self._logger.debug(f"Verificación de email '{email}': {'existe' if exists else 'no existe'}")
            return exists
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos verificando email '{email}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="email_exists",
                entity_type=self.model_class.__name__,
            )
        except Exception as e:
            self._logger.error(f"Error inesperado verificando email '{email}': {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado al verificar la existencia del email",
                operation="email_exists",
                entity_type=self.model_class.__name__,
            )

    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Employee]:
        """
        Obtiene una entidad por un campo único.
        
        Args:
            field_name: Nombre del campo.
            value: Valor del campo.
            
        Returns:
            La entidad encontrada o None.
        """
        try:
            return await self.find_by_criteria({field_name: value})
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo por campo único '{field_name}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo por campo único '{field_name}': {e}")
            raise EmployeeRepositoryError(
                message=f"Error inesperado al obtener por campo único '{field_name}'",
                operation="get_by_unique_field",
                entity_type=self.model_class.__name__,
            )