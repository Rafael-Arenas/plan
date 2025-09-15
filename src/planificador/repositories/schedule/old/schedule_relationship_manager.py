# src/planificador/database/repositories/schedule/schedule_relationship_manager.py

from typing import List, Optional, Dict, Any, Tuple
from datetime import date
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import pendulum
from pendulum import DateTime, Date
from sqlalchemy.exc import SQLAlchemyError

from ....models.schedule import Schedule
from ....models.employee import Employee
from ....models.project import Project
from ....models.team import Team
from ....models.status_code import StatusCode
from ....exceptions.repository import (
    convert_sqlalchemy_error,
    create_schedule_relationship_error,
)
from ....utils.date_utils import (
    get_current_time,
    format_datetime,
    get_week_range,
    get_month_range
)


class ScheduleRelationshipManager:
    """
    Gestor de relaciones para Schedule.
    
    Maneja las operaciones relacionadas con las asociaciones
    entre horarios y otras entidades como empleados, proyectos,
    equipos y códigos de estado.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger = logger.bind(component="ScheduleRelationshipManager")
    
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
        # Construir opciones de carga
        load_options = [selectinload(Schedule.employee)]
        
        if include_projects:
            load_options.append(selectinload(Schedule.project))
        if include_teams:
            load_options.append(selectinload(Schedule.team))
        if include_status_codes:
            load_options.append(selectinload(Schedule.status_code))
        
        stmt = (
            select(Schedule)
            .options(*load_options)
            .where(Schedule.employee_id == employee_id)
            .order_by(Schedule.date.desc(), Schedule.start_time.asc())
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                error=exc,
                operation="get_employee_schedules_with_details",
                entity_type="Schedule",
            )
            logger.error(
                "Error de base de datos al obtener horarios del empleado",
                employee_id=employee_id,
                include_projects=include_projects,
                include_teams=include_teams,
                include_status_codes=include_status_codes,
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al obtener horarios del empleado con detalles",
                details={
                    "employee_id": employee_id,
                    "include_projects": include_projects,
                    "include_teams": include_teams,
                    "include_status_codes": include_status_codes,
                    "db_error": str(db_error),
                },
            ) from db_error
        except Exception as e:
            logger.error(f"Error inesperado en get_employee_schedules_with_details: {e}")
            raise create_schedule_relationship_error(
                f"Error inesperado al obtener horarios del empleado: {e}",
                details={"original_error": str(e)}
            ) from e
        return list(result.scalars().all())
    
    async def get_employees_with_schedules_in_period(
        self,
        start_date: date,
        end_date: date
    ) -> List[Tuple[Employee, List[Schedule]]]:
        """
        Obtiene empleados con sus horarios en un período específico.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista de tuplas (empleado, lista_de_horarios)
        """
        # Obtener empleados que tienen horarios en el período
        stmt = (
            select(Employee)
            .join(Schedule)
            .where(
                and_(
                    Schedule.date >= start_date,
                    Schedule.date <= end_date
                )
            )
            .distinct()
            .order_by(Employee.name)
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                error=exc,
                operation="get_employees_with_schedules_in_period",
                entity_type="Schedule",
            )
            logger.error(
                "Error de base de datos al obtener empleados con horarios en período",
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al obtener empleados con horarios en el período",
                details={
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        except Exception as e:
            logger.error(f"Error inesperado en get_employees_with_schedules_in_period: {e}")
            raise create_schedule_relationship_error(
                f"Error inesperado al obtener empleados con horarios en el período: {e}",
                details={"original_error": str(e)}
            ) from e
        employees = result.scalars().all()
        
        # Para cada empleado, obtener sus horarios del período
        employee_schedules = []
        for employee in employees:
            schedules = await self.get_employee_schedules_in_period(
                employee.id, start_date, end_date
            )
            employee_schedules.append((employee, schedules))
        
        return employee_schedules
    
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
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista de horarios del empleado en el período
        """
        stmt = (
            select(Schedule)
            .options(
                selectinload(Schedule.project),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
            .where(
                and_(
                    Schedule.employee_id == employee_id,
                    Schedule.date >= start_date,
                    Schedule.date <= end_date
                )
            )
            .order_by(Schedule.date.asc(), Schedule.start_time.asc())
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                error=exc,
                operation="get_employee_schedules_in_period",
                entity_type="Schedule",
            )
            logger.error(
                "Error de base de datos al obtener horarios del empleado en período",
                employee_id=employee_id,
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al obtener horarios del empleado en el período",
                details={
                    "employee_id": employee_id,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        except Exception as e:
            logger.error(f"Error inesperado en get_employee_schedules_in_period: {e}")
            raise create_schedule_relationship_error(
                f"Error inesperado al obtener horarios del empleado en período: {e}",
                details={"original_error": str(e)}
            ) from e
        return list(result.scalars().all())
    
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
        # Construir opciones de carga
        load_options = [selectinload(Schedule.project)]
        
        if include_employees:
            load_options.append(selectinload(Schedule.employee))
        if include_teams:
            load_options.append(selectinload(Schedule.team))
        if include_status_codes:
            load_options.append(selectinload(Schedule.status_code))
        
        stmt = (
            select(Schedule)
            .options(*load_options)
            .where(Schedule.project_id == project_id)
            .order_by(Schedule.date.desc(), Schedule.start_time.asc())
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                error=exc,
                operation="get_project_schedules_with_details",
                entity_type="Schedule",
            )
            logger.error(
                "Error de base de datos al obtener horarios del proyecto",
                project_id=project_id,
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al obtener horarios del proyecto con detalles",
                details={
                    "project_id": project_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        except Exception as e:
            logger.error(f"Error inesperado en get_project_schedules_with_details: {e}")
            raise create_schedule_relationship_error(
                f"Error inesperado al obtener horarios del proyecto: {e}",
                details={"original_error": str(e)}
            ) from e
            
        return list(result.scalars().all())
    
    async def get_projects_with_schedules_in_period(
        self,
        start_date: date,
        end_date: date
    ) -> List[Tuple[Project, List[Schedule]]]:
        """
        Obtiene proyectos con sus horarios en un período específico.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista de tuplas (proyecto, lista_de_horarios)
        """
        # Obtener proyectos que tienen horarios en el período
        stmt = (
            select(Project)
            .join(Schedule)
            .where(
                and_(
                    Schedule.date >= start_date,
                    Schedule.date <= end_date
                )
            )
            .distinct()
            .order_by(Project.name)
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                error=exc,
                operation="get_projects_with_schedules_in_period",
                entity_type="Schedule",
            )
            logger.error(
                "Error de BD al obtener proyectos con horarios en período",
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al obtener proyectos con horarios en el período",
                details={
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        except Exception as e:
            logger.error(f"Error inesperado en get_projects_with_schedules_in_period: {e}")
            raise create_schedule_relationship_error(
                f"Error inesperado al obtener proyectos con horarios en el período: {e}",
                details={"original_error": str(e)}
            ) from e
            
        projects = result.scalars().all()
        
        # Para cada proyecto, obtener sus horarios del período
        project_schedules = []
        for project in projects:
            schedules = await self.get_project_schedules_in_period(
                project.id, start_date, end_date
            )
            project_schedules.append((project, schedules))
        
        return project_schedules
    
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
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista de horarios del proyecto en el período
        """
        stmt = (
            select(Schedule)
            .options(
                selectinload(Schedule.employee),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
            .where(
                and_(
                    Schedule.project_id == project_id,
                    Schedule.date >= start_date,
                    Schedule.date <= end_date
                )
            )
            .order_by(Schedule.date.asc(), Schedule.start_time.asc())
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                error=exc,
                operation="get_project_schedules_in_period",
                entity_type="Schedule",
            )
            logger.error(
                "Error de BD al obtener horarios del proyecto en período",
                project_id=project_id,
                start_date=str(start_date),
                end_date=str(end_date),
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al obtener horarios del proyecto en el período",
                details={
                    "project_id": project_id,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "db_error": str(db_error),
                },
            ) from db_error
        except Exception as e:
            logger.error(f"Error inesperado en get_project_schedules_in_period: {e}")
            raise create_schedule_relationship_error(
                f"Error inesperado al obtener horarios del proyecto en período: {e}",
                details={"original_error": str(e)}
            ) from e
            
        return list(result.scalars().all())

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
        # Construir opciones de carga
        load_options = [selectinload(Schedule.team)]
        
        if include_employees:
            load_options.append(selectinload(Schedule.employee))
        if include_projects:
            load_options.append(selectinload(Schedule.project))
        if include_status_codes:
            load_options.append(selectinload(Schedule.status_code))
        
        stmt = (
            select(Schedule)
            .options(*load_options)
            .where(Schedule.team_id == team_id)
            .order_by(Schedule.date.desc(), Schedule.start_time.asc())
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                error=exc,
                operation="get_team_schedules_with_details",
                entity_type="Schedule",
            )
            logger.error(
                "Error de base de datos al obtener horarios del equipo",
                team_id=team_id,
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al obtener horarios del equipo con detalles",
                details={
                    "team_id": team_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        except Exception as e:
            logger.error(f"Error inesperado en get_team_schedules_with_details: {e}")
            raise create_schedule_relationship_error(
                f"Error inesperado al obtener horarios del equipo: {e}",
                details={"original_error": str(e)}
            ) from e
            
        return list(result.scalars().all())

    # ==========================================
    # ASIGNACIÓN Y REMOCIÓN
    # ==========================================
    
    async def assign_schedule_to_project(self, schedule_id: int, project_id: int) -> Schedule:
        """
        Asigna un horario a un proyecto.
        
        Args:
            schedule_id: ID del horario
            project_id: ID del proyecto
            
        Returns:
            Horario actualizado
            
        Raises:
            ScheduleRelationshipError: Si el horario o el proyecto no existen o no son válidos
        """
        # Verificar que el horario existe
        schedule = await self.get_schedule_by_id(schedule_id)
        if not schedule:
            raise create_schedule_relationship_error(
                f"Horario con ID {schedule_id} no encontrado",
                details={"schedule_id": schedule_id, "operation": "assign_schedule_to_project"},
            )
        
        # Verificar que el proyecto existe
        project = await self.get_project_by_id(project_id)
        if not project:
            raise create_schedule_relationship_error(
                f"Proyecto con ID {project_id} no encontrado",
                details={"project_id": project_id, "operation": "assign_schedule_to_project"},
            )
        
        if not project.is_active:
            raise create_schedule_relationship_error(
                f"El proyecto {project.name} no está activo",
                details={"project_id": project_id, "operation": "assign_schedule_to_project"},
            )
        
        # Asignar proyecto
        schedule.project_id = project_id
        try:
            await self.session.commit()
            await self.session.refresh(schedule)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="assign_schedule_to_project"
            )
            logger.error(
                "Error de base de datos al asignar horario a proyecto",
                schedule_id=schedule_id,
                project_id=project_id,
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al asignar el horario al proyecto",
                details={
                    "schedule_id": schedule_id,
                    "project_id": project_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        
        return schedule
    
    async def assign_schedule_to_team(self, schedule_id: int, team_id: int) -> Schedule:
        """
        Asigna un horario a un equipo.
        
        Args:
            schedule_id: ID del horario
            team_id: ID del equipo
            
        Returns:
            Horario actualizado
            
        Raises:
            ScheduleRelationshipError: Si el horario o el equipo no existen o no son válidos
        """
        # Verificar que el horario existe
        schedule = await self.get_schedule_by_id(schedule_id)
        if not schedule:
            raise create_schedule_relationship_error(
                f"Horario con ID {schedule_id} no encontrado",
                details={"schedule_id": schedule_id, "operation": "assign_schedule_to_team"},
            )
        
        # Verificar que el equipo existe
        team = await self.get_team_by_id(team_id)
        if not team:
            raise create_schedule_relationship_error(
                f"Equipo con ID {team_id} no encontrado",
                details={"team_id": team_id, "operation": "assign_schedule_to_team"},
            )
        
        if not team.is_active:
            raise create_schedule_relationship_error(
                f"El equipo {team.name} no está activo",
                details={"team_id": team_id, "operation": "assign_schedule_to_team"},
            )
        
        # Asignar equipo
        schedule.team_id = team_id
        try:
            await self.session.commit()
            await self.session.refresh(schedule)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="assign_schedule_to_team"
            )
            logger.error(
                "Error de base de datos al asignar horario a equipo",
                schedule_id=schedule_id,
                team_id=team_id,
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al asignar el horario al equipo",
                details={
                    "schedule_id": schedule_id,
                    "team_id": team_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        
        return schedule
    
    async def remove_schedule_from_project(self, schedule_id: int) -> Schedule:
        """
        Remueve un horario de su proyecto asignado.
        
        Args:
            schedule_id: ID del horario
            
        Returns:
            Horario actualizado
            
        Raises:
            ScheduleRelationshipError: Si el horario no existe
        """
        schedule = await self.get_schedule_by_id(schedule_id)
        if not schedule:
            raise create_schedule_relationship_error(
                f"Horario con ID {schedule_id} no encontrado",
                details={"schedule_id": schedule_id, "operation": "remove_schedule_from_project"},
            )
        
        schedule.project_id = None
        try:
            await self.session.commit()
            await self.session.refresh(schedule)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="remove_schedule_from_project"
            )
            logger.error(
                "Error de base de datos al remover proyecto del horario",
                schedule_id=schedule_id,
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al remover el proyecto del horario",
                details={
                    "schedule_id": schedule_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        
        return schedule
    
    async def remove_schedule_from_team(self, schedule_id: int) -> Schedule:
        """
        Remueve un horario de su equipo asignado.
        
        Args:
            schedule_id: ID del horario
            
        Returns:
            Horario actualizado
            
        Raises:
            ScheduleRelationshipError: Si el horario no existe
        """
        schedule = await self.get_schedule_by_id(schedule_id)
        if not schedule:
            raise create_schedule_relationship_error(
                f"Horario con ID {schedule_id} no encontrado",
                details={"schedule_id": schedule_id, "operation": "remove_schedule_from_team"},
            )
        
        schedule.team_id = None
        try:
            await self.session.commit()
            await self.session.refresh(schedule)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(
                exc, context="remove_schedule_from_team"
            )
            logger.error(
                "Error de base de datos al remover equipo del horario",
                schedule_id=schedule_id,
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al remover el equipo del horario",
                details={
                    "schedule_id": schedule_id,
                    "db_error": str(db_error),
                },
            ) from db_error
        
        return schedule
    
    # ==========================================
    # CONSULTAS DE ENTIDADES
    # ==========================================
    
    async def get_schedule_by_id(self, schedule_id: int) -> Optional[Schedule]:
        """
        Obtiene un horario por su ID.
        
        Args:
            schedule_id: ID del horario
            
        Returns:
            Horario encontrado o None
        """
        stmt = (
            select(Schedule)
            .options(
                selectinload(Schedule.employee),
                selectinload(Schedule.project),
                selectinload(Schedule.team),
                selectinload(Schedule.status_code)
            )
            .where(Schedule.id == schedule_id)
        )
        
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(exc, context="get_schedule_by_id")
            logger.error(
                "Error de base de datos al obtener horario por ID",
                schedule_id=schedule_id,
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al obtener el horario",
                details={"schedule_id": schedule_id, "db_error": str(db_error)},
            ) from db_error
        return result.scalar_one_or_none()
    
    async def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto por su ID.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Proyecto encontrado o None
        """
        stmt = select(Project).where(Project.id == project_id)
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(exc, context="get_project_by_id")
            logger.error(
                "Error de base de datos al obtener proyecto por ID",
                project_id=project_id,
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al obtener el proyecto",
                details={"project_id": project_id, "db_error": str(db_error)},
            ) from db_error
        return result.scalar_one_or_none()
    
    async def get_team_by_id(self, team_id: int) -> Optional[Team]:
        """
        Obtiene un equipo por su ID.
        
        Args:
            team_id: ID del equipo
            
        Returns:
            Equipo encontrado o None
        """
        stmt = select(Team).where(Team.id == team_id)
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError as exc:
            db_error = convert_sqlalchemy_error(exc, context="get_team_by_id")
            logger.error(
                "Error de base de datos al obtener equipo por ID",
                team_id=team_id,
                error=str(db_error),
            )
            raise create_schedule_relationship_error(
                "Error al obtener el equipo",
                details={"team_id": team_id, "db_error": str(db_error)},
            ) from db_error
        return result.scalar_one_or_none()
    
    # ==========================================
    # RESUMEN DE RELACIONES
    # ==========================================
    
    async def get_schedule_relationships_summary(
        self,
        schedule_id: int
    ) -> Dict[str, Any]:
        """
        Obtiene un resumen completo de las relaciones de un horario.
        
        Args:
            schedule_id: ID del horario
            
        Returns:
            Diccionario con información de relaciones
            
        Raises:
            ScheduleRelationshipError: Si el horario no existe
        """
        schedule = await self.get_schedule_by_id(schedule_id)
        if not schedule:
            raise create_schedule_relationship_error(
                f"Horario con ID {schedule_id} no encontrado",
                details={"schedule_id": schedule_id, "operation": "get_schedule_relationships_summary"},
            )
        
        return {
            'schedule_id': schedule_id,
            'employee': {
                'id': schedule.employee.id if schedule.employee else None,
                'name': schedule.employee.name if schedule.employee else None,
                'is_active': schedule.employee.is_active if schedule.employee else None
            },
            'project': {
                'id': schedule.project.id if schedule.project else None,
                'name': schedule.project.name if schedule.project else None,
                'is_active': schedule.project.is_active if schedule.project else None
            },
            'team': {
                'id': schedule.team.id if schedule.team else None,
                'name': schedule.team.name if schedule.team else None,
                'is_active': schedule.team.is_active if schedule.team else None
            },
            'status_code': {
                'id': schedule.status_code.id if schedule.status_code else None,
                'code': schedule.status_code.code if schedule.status_code else None,
                'description': schedule.status_code.description if schedule.status_code else None
            }
        }