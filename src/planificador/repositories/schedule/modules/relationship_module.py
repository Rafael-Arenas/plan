# src/planificador/repositories/schedule/modules/relationship_module.py

from typing import Dict, Any, List, Optional, Tuple
from datetime import date

from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from ....models.schedule import Schedule
from ....models.employee import Employee
from ....models.project import Project
from ....models.team import Team
from ...base_repository import BaseRepository
from ....exceptions.repository import RepositoryError
from ....exceptions.repository import convert_sqlalchemy_error
from ....exceptions.validation import ValidationError
from ..interfaces.relationship_interface import IScheduleRelationshipOperations


class ScheduleRelationshipModule(BaseRepository[Schedule], IScheduleRelationshipOperations):
    """
    Módulo para operaciones de relaciones del repositorio Schedule.
    
    Proporciona métodos para gestionar las relaciones entre horarios
    y otras entidades como empleados, proyectos y equipos.
    """
    
    def __init__(self, session: AsyncSession, model_class: type = Schedule):
        """
        Inicializa el módulo de relaciones.
        
        Args:
            session: Sesión de base de datos asíncrona
            model_class: Clase del modelo Schedule
        """
        super().__init__(session, model_class)
        self._logger = logger.bind(module="ScheduleRelationshipModule")
    
    # ==========================================
    # GESTIÓN DE RELACIONES CON EMPLEADOS
    # ==========================================
    
    async def get_employee_schedules_with_details(
        self,
        employee_id: int,
        include_projects: bool = True,
        include_teams: bool = True,
        include_status_codes: bool = True
    ) -> List[Schedule]:
        """
        Obtiene horarios de un empleado con detalles de relaciones.
        
        Args:
            employee_id: ID del empleado
            include_projects: Incluir detalles de proyectos
            include_teams: Incluir detalles de equipos
            include_status_codes: Incluir detalles de códigos de estado
            
        Returns:
            Lista de horarios con relaciones cargadas
        """
        try:
            # Construir opciones de carga según parámetros
            options = []
            if include_projects:
                options.append(selectinload(self.model_class.project))
            if include_teams:
                options.append(selectinload(self.model_class.team))
            if include_status_codes:
                options.append(selectinload(self.model_class.status_code))
            
            query = select(self.model_class).where(
                self.model_class.employee_id == employee_id
            ).options(*options).order_by(self.model_class.date.desc())
            
            result = await self.session.execute(query)
            schedules = result.scalars().all()
            
            self._logger.debug(
                f"Horarios empleado {employee_id} con detalles: {len(schedules)}"
            )
            return list(schedules)
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error BD obteniendo horarios empleado {employee_id}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_schedules_with_details",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo horarios empleado {employee_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_employee_schedules_with_details",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )
    
    async def get_employees_with_schedules_in_period(
        self,
        start_date: date,
        end_date: date
    ) -> List[Tuple[Employee, List[Schedule]]]:
        """
        Obtiene empleados con sus horarios en un período.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Lista de tuplas (empleado, lista de horarios)
        """
        try:
            # Obtener empleados únicos con horarios en el período
            employee_ids_query = select(
                func.distinct(self.model_class.employee_id)
            ).where(
                and_(
                    self.model_class.date >= start_date,
                    self.model_class.date <= end_date
                )
            )
            
            result = await self.session.execute(employee_ids_query)
            employee_ids = [row[0] for row in result.fetchall()]
            
            employees_with_schedules = []
            
            for employee_id in employee_ids:
                # Obtener empleado
                employee_query = select(Employee).where(Employee.id == employee_id)
                employee_result = await self.session.execute(employee_query)
                employee = employee_result.scalar_one_or_none()
                
                if employee:
                    # Obtener horarios del empleado en el período
                    schedules_query = select(self.model_class).where(
                        and_(
                            self.model_class.employee_id == employee_id,
                            self.model_class.date >= start_date,
                            self.model_class.date <= end_date
                        )
                    ).order_by(self.model_class.date)
                    
                    schedules_result = await self.session.execute(schedules_query)
                    schedules = list(schedules_result.scalars().all())
                    
                    employees_with_schedules.append((employee, schedules))
            
            self._logger.debug(
                f"Empleados con horarios en período: {len(employees_with_schedules)}"
            )
            return employees_with_schedules
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error BD obteniendo empleados con horarios: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employees_with_schedules_in_period",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo empleados con horarios: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_employees_with_schedules_in_period",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
    async def get_employee_schedules_in_period(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """
        Obtiene horarios de un empleado en un período específico.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Lista de horarios del empleado
        """
        try:
            query = select(self.model_class).where(
                and_(
                    self.model_class.employee_id == employee_id,
                    self.model_class.date >= start_date,
                    self.model_class.date <= end_date
                )
            ).order_by(self.model_class.date)
            
            result = await self.session.execute(query)
            schedules = result.scalars().all()
            
            self._logger.debug(
                f"Horarios empleado {employee_id} en período: {len(schedules)}"
            )
            return list(schedules)
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error BD obteniendo horarios empleado en período: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_schedules_in_period",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo horarios empleado en período: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_employee_schedules_in_period",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )
    
    # ==========================================
    # GESTIÓN DE RELACIONES CON PROYECTOS
    # ==========================================
    
    async def get_project_schedules_with_details(
        self,
        project_id: int,
        include_employees: bool = True,
        include_teams: bool = True,
        include_status_codes: bool = True
    ) -> List[Schedule]:
        """
        Obtiene horarios de un proyecto con detalles de relaciones.
        
        Args:
            project_id: ID del proyecto
            include_employees: Incluir detalles de empleados
            include_teams: Incluir detalles de equipos
            include_status_codes: Incluir detalles de códigos de estado
            
        Returns:
            Lista de horarios con relaciones cargadas
        """
        try:
            # Construir opciones de carga según parámetros
            options = []
            if include_employees:
                options.append(selectinload(self.model_class.employee))
            if include_teams:
                options.append(selectinload(self.model_class.team))
            if include_status_codes:
                options.append(selectinload(self.model_class.status_code))
            
            query = select(self.model_class).where(
                self.model_class.project_id == project_id
            ).options(*options).order_by(self.model_class.date.desc())
            
            result = await self.session.execute(query)
            schedules = result.scalars().all()
            
            self._logger.debug(
                f"Horarios proyecto {project_id} con detalles: {len(schedules)}"
            )
            return list(schedules)
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error BD obteniendo horarios proyecto {project_id}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_schedules_with_details",
                entity_type=self.model_class.__name__,
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo horarios proyecto {project_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_project_schedules_with_details",
                entity_type=self.model_class.__name__,
                entity_id=project_id,
                original_error=e
            )
    
    async def get_projects_with_schedules_in_period(
        self,
        start_date: date,
        end_date: date
    ) -> List[Tuple[Project, List[Schedule]]]:
        """
        Obtiene proyectos con sus horarios en un período.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Lista de tuplas (proyecto, lista de horarios)
        """
        try:
            # Obtener proyectos únicos con horarios en el período
            project_ids_query = select(
                func.distinct(self.model_class.project_id)
            ).where(
                and_(
                    self.model_class.date >= start_date,
                    self.model_class.date <= end_date,
                    self.model_class.project_id.isnot(None)
                )
            )
            
            result = await self.session.execute(project_ids_query)
            project_ids = [row[0] for row in result.fetchall()]
            
            projects_with_schedules = []
            
            for project_id in project_ids:
                # Obtener proyecto
                project_query = select(Project).where(Project.id == project_id)
                project_result = await self.session.execute(project_query)
                project = project_result.scalar_one_or_none()
                
                if project:
                    # Obtener horarios del proyecto en el período
                    schedules_query = select(self.model_class).where(
                        and_(
                            self.model_class.project_id == project_id,
                            self.model_class.date >= start_date,
                            self.model_class.date <= end_date
                        )
                    ).order_by(self.model_class.date)
                    
                    schedules_result = await self.session.execute(schedules_query)
                    schedules = list(schedules_result.scalars().all())
                    
                    projects_with_schedules.append((project, schedules))
            
            self._logger.debug(
                f"Proyectos con horarios en período: {len(projects_with_schedules)}"
            )
            return projects_with_schedules
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error BD obteniendo proyectos con horarios: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_projects_with_schedules_in_period",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo proyectos con horarios: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_projects_with_schedules_in_period",
                entity_type=self.model_class.__name__,
                original_error=e
            )
    
    async def get_project_schedules_in_period(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """
        Obtiene horarios de un proyecto en un período específico.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Lista de horarios del proyecto
        """
        try:
            query = select(self.model_class).where(
                and_(
                    self.model_class.project_id == project_id,
                    self.model_class.date >= start_date,
                    self.model_class.date <= end_date
                )
            ).order_by(self.model_class.date)
            
            result = await self.session.execute(query)
            schedules = result.scalars().all()
            
            self._logger.debug(
                f"Horarios proyecto {project_id} en período: {len(schedules)}"
            )
            return list(schedules)
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error BD obteniendo horarios proyecto en período: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_schedules_in_period",
                entity_type=self.model_class.__name__,
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo horarios proyecto en período: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_project_schedules_in_period",
                entity_type=self.model_class.__name__,
                entity_id=project_id,
                original_error=e
            )
    
    # ==========================================
    # GESTIÓN DE RELACIONES CON EQUIPOS
    # ==========================================
    
    async def get_team_schedules_with_details(
        self,
        team_id: int,
        include_employees: bool = True,
        include_projects: bool = True,
        include_status_codes: bool = True
    ) -> List[Schedule]:
        """
        Obtiene horarios de un equipo con detalles de relaciones.
        
        Args:
            team_id: ID del equipo
            include_employees: Incluir detalles de empleados
            include_projects: Incluir detalles de proyectos
            include_status_codes: Incluir detalles de códigos de estado
            
        Returns:
            Lista de horarios con relaciones cargadas
        """
        try:
            # Construir opciones de carga según parámetros
            options = []
            if include_employees:
                options.append(selectinload(self.model_class.employee))
            if include_projects:
                options.append(selectinload(self.model_class.project))
            if include_status_codes:
                options.append(selectinload(self.model_class.status_code))
            
            query = select(self.model_class).where(
                self.model_class.team_id == team_id
            ).options(*options).order_by(self.model_class.date.desc())
            
            result = await self.session.execute(query)
            schedules = result.scalars().all()
            
            self._logger.debug(
                f"Horarios equipo {team_id} con detalles: {len(schedules)}"
            )
            return list(schedules)
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error BD obteniendo horarios equipo {team_id}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_schedules_with_details",
                entity_type=self.model_class.__name__,
                entity_id=team_id
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo horarios equipo {team_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_team_schedules_with_details",
                entity_type=self.model_class.__name__,
                entity_id=team_id,
                original_error=e
            )
    
    # ==========================================
    # OPERACIONES DE ASIGNACIÓN
    # ==========================================
    
    async def assign_schedule_to_project(
        self,
        schedule_id: int,
        project_id: int
    ) -> Schedule:
        """
        Asigna un horario a un proyecto.
        
        Args:
            schedule_id: ID del horario
            project_id: ID del proyecto
            
        Returns:
            Horario actualizado
        """
        try:
            # Validar asignación
            is_valid = await self.validate_project_assignment(schedule_id, project_id)
            if not is_valid:
                raise ValidationError(
                    message=f"Asignación no válida: horario {schedule_id} a proyecto {project_id}",
                    field="project_assignment",
                    value={"schedule_id": schedule_id, "project_id": project_id}
                )
            
            # Usar BaseRepository para obtener y actualizar el horario
            schedule = await self.get_by_id(schedule_id)
            if not schedule:
                raise ValidationError(
                    message=f"Horario no encontrado: {schedule_id}",
                    field="schedule_id",
                    value=schedule_id
                )
            
            # Actualizar usando BaseRepository
            updated_schedule = await self.update(schedule_id, {"project_id": project_id})
            
            self._logger.info(
                f"Horario {schedule_id} asignado a proyecto {project_id}"
            )
            return updated_schedule
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error inesperado asignando horario a proyecto: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="assign_schedule_to_project",
                entity_type=self.model_class.__name__,
                entity_id=schedule_id,
                original_error=e
            )
    
    async def assign_schedule_to_team(
        self,
        schedule_id: int,
        team_id: int
    ) -> Schedule:
        """
        Asigna un horario a un equipo.
        
        Args:
            schedule_id: ID del horario
            team_id: ID del equipo
            
        Returns:
            Horario actualizado
        """
        try:
            # Validar asignación
            is_valid = await self.validate_team_assignment(schedule_id, team_id)
            if not is_valid:
                raise ValidationError(
                    message=f"Asignación no válida: horario {schedule_id} a equipo {team_id}",
                    field="team_assignment",
                    value={"schedule_id": schedule_id, "team_id": team_id}
                )
            
            # Usar BaseRepository para obtener y actualizar el horario
            schedule = await self.get_by_id(schedule_id)
            if not schedule:
                raise ValidationError(
                    message=f"Horario no encontrado: {schedule_id}",
                    field="schedule_id",
                    value=schedule_id
                )
            
            # Actualizar usando BaseRepository
            updated_schedule = await self.update(schedule_id, {"team_id": team_id})
            
            self._logger.info(
                f"Horario {schedule_id} asignado a equipo {team_id}"
            )
            return updated_schedule
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error inesperado asignando horario a equipo: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="assign_schedule_to_team",
                entity_type=self.model_class.__name__,
                entity_id=schedule_id,
                original_error=e
            )
    
    async def remove_schedule_from_project(
        self,
        schedule_id: int
    ) -> Schedule:
        """
        Remueve un horario de su proyecto asignado.
        
        Args:
            schedule_id: ID del horario
            
        Returns:
            Horario actualizado
        """
        try:
            # Usar BaseRepository para obtener el horario
            schedule = await self.get_by_id(schedule_id)
            if not schedule:
                raise ValidationError(
                    message=f"Horario no encontrado: {schedule_id}",
                    field="schedule_id",
                    value=schedule_id
                )
            
            # Remover proyecto usando BaseRepository
            old_project_id = schedule.project_id
            updated_schedule = await self.update(schedule_id, {"project_id": None})
            
            self._logger.info(
                f"Horario {schedule_id} removido de proyecto {old_project_id}"
            )
            return updated_schedule
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error inesperado removiendo horario de proyecto: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="remove_schedule_from_project",
                entity_type=self.model_class.__name__,
                entity_id=schedule_id,
                original_error=e
            )
    
    async def remove_schedule_from_team(
        self,
        schedule_id: int
    ) -> Schedule:
        """
        Remueve un horario de su equipo asignado.
        
        Args:
            schedule_id: ID del horario
            
        Returns:
            Horario actualizado
        """
        try:
            # Usar BaseRepository para obtener el horario
            schedule = await self.get_by_id(schedule_id)
            if not schedule:
                raise ValidationError(
                    message=f"Horario no encontrado: {schedule_id}",
                    field="schedule_id",
                    value=schedule_id
                )
            
            # Remover equipo usando BaseRepository
            old_team_id = schedule.team_id
            updated_schedule = await self.update(schedule_id, {"team_id": None})
            
            self._logger.info(
                f"Horario {schedule_id} removido de equipo {old_team_id}"
            )
            return updated_schedule
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error inesperado removiendo horario de equipo: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="remove_schedule_from_team",
                entity_type=self.model_class.__name__,
                entity_id=schedule_id,
                original_error=e
            )
    
    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Schedule]:
        """
        Obtiene un horario por un campo único específico.
        
        Args:
            field_name: Nombre del campo único
            value: Valor a buscar
            
        Returns:
            Schedule encontrado o None si no existe
            
        Raises:
            ScheduleRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo horario por campo {field_name}={value}")
        
        return await self.get_by_field(field_name, value)
    
    # ==========================================
    # OPERACIONES DE CONSULTA AUXILIARES
    # ==========================================
    
    async def get_schedule_relationships_summary(
        self,
        schedule_id: int
    ) -> Dict[str, Any]:
        """
        Obtiene resumen de relaciones de un horario.
        
        Args:
            schedule_id: ID del horario
            
        Returns:
            Dict con resumen de relaciones
        """
        try:
            # Usar BaseRepository para obtener el horario
            schedule = await self.get_by_id(schedule_id)
            
            if not schedule:
                raise ValidationError(
                    message=f"Horario no encontrado: {schedule_id}",
                    field="schedule_id",
                    value=schedule_id
                )
            
            # Cargar relaciones manualmente si es necesario
            query = select(self.model_class).where(
                self.model_class.id == schedule_id
            ).options(
                selectinload(self.model_class.employee),
                selectinload(self.model_class.project),
                selectinload(self.model_class.team),
                selectinload(self.model_class.status_code)
            )
            
            result = await self.session.execute(query)
            schedule_with_relations = result.scalar_one_or_none()
            
            summary = {
                'schedule_id': schedule_id,
                'date': schedule_with_relations.date.isoformat(),
                'hours_worked': float(schedule_with_relations.hours_worked),
                'employee': {
                    'id': schedule_with_relations.employee.id if schedule_with_relations.employee else None,
                    'name': schedule_with_relations.employee.name if schedule_with_relations.employee else None
                } if schedule_with_relations.employee else None,
                'project': {
                    'id': schedule_with_relations.project.id if schedule_with_relations.project else None,
                    'name': schedule_with_relations.project.name if schedule_with_relations.project else None
                } if schedule_with_relations.project else None,
                'team': {
                    'id': schedule_with_relations.team.id if schedule_with_relations.team else None,
                    'name': schedule_with_relations.team.name if schedule_with_relations.team else None
                } if schedule_with_relations.team else None,
                'status_code': {
                    'id': schedule_with_relations.status_code.id if schedule_with_relations.status_code else None,
                    'code': schedule_with_relations.status_code.code if schedule_with_relations.status_code else None,
                    'description': schedule_with_relations.status_code.description if schedule_with_relations.status_code else None
                } if schedule_with_relations.status_code else None
            }
            
            self._logger.debug(
                f"Resumen relaciones horario {schedule_id} generado"
            )
            return summary
            
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error BD obteniendo resumen relaciones horario {schedule_id}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_schedule_relationships_summary",
                entity_type=self.model_class.__name__,
                entity_id=schedule_id
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo resumen relaciones: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_schedule_relationships_summary",
                entity_type=self.model_class.__name__,
                entity_id=schedule_id,
                original_error=e
            )
    
    async def validate_project_assignment(
        self,
        schedule_id: int,
        project_id: int
    ) -> bool:
        """
        Valida si un horario puede ser asignado a un proyecto.
        
        Args:
            schedule_id: ID del horario
            project_id: ID del proyecto
            
        Returns:
            True si la asignación es válida
        """
        try:
            # Verificar que el horario existe
            schedule_query = select(self.model_class).where(
                self.model_class.id == schedule_id
            )
            schedule_result = await self.session.execute(schedule_query)
            schedule = schedule_result.scalar_one_or_none()
            
            if not schedule:
                return False
            
            # Verificar que el proyecto existe
            project_query = select(Project).where(Project.id == project_id)
            project_result = await self.session.execute(project_query)
            project = project_result.scalar_one_or_none()
            
            if not project:
                return False
            
            # Validaciones adicionales pueden agregarse aquí
            # Por ejemplo: verificar que el empleado esté asignado al proyecto
            
            return True
            
        except Exception as e:
            self._logger.error(
                f"Error validando asignación proyecto: {e}"
            )
            return False
    
    async def validate_team_assignment(
        self,
        schedule_id: int,
        team_id: int
    ) -> bool:
        """
        Valida si un horario puede ser asignado a un equipo.
        
        Args:
            schedule_id: ID del horario
            team_id: ID del equipo
            
        Returns:
            True si la asignación es válida
        """
        try:
            # Verificar que el horario existe
            schedule_query = select(self.model_class).where(
                self.model_class.id == schedule_id
            )
            schedule_result = await self.session.execute(schedule_query)
            schedule = schedule_result.scalar_one_or_none()
            
            if not schedule:
                return False
            
            # Verificar que el equipo existe
            team_query = select(Team).where(Team.id == team_id)
            team_result = await self.session.execute(team_query)
            team = team_result.scalar_one_or_none()
            
            if not team:
                return False
            
            # Validaciones adicionales pueden agregarse aquí
            # Por ejemplo: verificar que el empleado sea miembro del equipo
            
            return True
            
        except Exception as e:
            self._logger.error(
                f"Error validando asignación equipo: {e}"
            )
            return False