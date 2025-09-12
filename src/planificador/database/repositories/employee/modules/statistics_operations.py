"""Módulo de operaciones estadísticas para empleados.

Este módulo implementa la interfaz IEmployeeStatisticsOperations proporcionando
funcionalidad completa para generar estadísticas y métricas de empleados.
"""

from typing import Dict, List, Any, Optional
from datetime import date, timedelta
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from .....models.employee import Employee, EmployeeStatus
from .....models.team_membership import TeamMembership
from .....models.project_assignment import ProjectAssignment
from .....models.vacation import Vacation, VacationStatus
from .....utils.date_utils import get_current_time
from .....exceptions.repository import convert_sqlalchemy_error
from .....exceptions.repository.employee_repository_exceptions import create_employee_statistics_error
from ..interfaces.statistics_interface import IEmployeeStatisticsOperations


class StatisticsOperations(IEmployeeStatisticsOperations):
    """Implementación de operaciones estadísticas para empleados.
    
    Esta clase proporciona métodos para generar estadísticas y métricas
    detalladas sobre empleados, incluyendo distribuciones por estado,
    departamento, posición, estadísticas salariales, participación en
    equipos y proyectos, vacaciones, habilidades y carga de trabajo.
    """
    
    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones estadísticas.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self.session = session
        self._logger = logger.bind(component="StatisticsOperations")
    
    # ============================================================================
    # ESTADÍSTICAS POR CATEGORÍAS
    # ============================================================================
    
    async def get_employee_count_by_status(self) -> Dict[str, int]:
        """Obtiene el conteo de empleados por estado.
        
        Returns:
            Diccionario con conteos por estado
        """
        try:
            query = (
                select(
                    Employee.status,
                    func.count(Employee.id).label('count')
                )
                .group_by(Employee.status)
            )
            
            result = await self.session.execute(query)
            rows = result.all()
            
            # Inicializar con todos los estados posibles
            counts = {status.value: 0 for status in EmployeeStatus}
            
            # Actualizar con los conteos reales
            for row in rows:
                counts[row.status.value] = row.count
            
            self._logger.debug(f"Conteos por estado obtenidos: {counts}")
            return counts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo conteos por estado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_count_by_status",
                entity_type="Employee"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo conteos por estado: {e}")
            raise create_employee_statistics_error(
                message=f"Error inesperado obteniendo conteos por estado: {e}",
                operation="get_employee_count_by_status",
                original_error=e
            )
    
    async def get_employee_count_by_department(self) -> Dict[str, int]:
        """Obtiene el conteo de empleados por departamento.
        
        Returns:
            Diccionario con conteos por departamento
        """
        try:
            query = (
                select(
                    Employee.department,
                    func.count(Employee.id).label('count')
                )
                .where(Employee.status == EmployeeStatus.ACTIVE)
                .group_by(Employee.department)
                .order_by(func.count(Employee.id).desc())
            )
            
            result = await self.session.execute(query)
            rows = result.all()
            
            counts = {}
            for row in rows:
                department = row.department or 'Sin Departamento'
                counts[department] = row.count
            
            self._logger.debug(f"Conteos por departamento obtenidos: {len(counts)} departamentos")
            return counts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo conteos por departamento: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_count_by_department",
                entity_type="Employee"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo conteos por departamento: {e}")
            raise create_employee_statistics_error(
                message=f"Error inesperado obteniendo conteos por departamento: {e}",
                operation="get_employee_count_by_department",
                original_error=e
            )
    
    async def get_employee_count_by_position(self) -> Dict[str, int]:
        """Obtiene el conteo de empleados por posición.
        
        Returns:
            Diccionario con conteos por posición
        """
        try:
            query = (
                select(
                    Employee.position,
                    func.count(Employee.id).label('count')
                )
                .where(Employee.status == EmployeeStatus.ACTIVE)
                .group_by(Employee.position)
                .order_by(func.count(Employee.id).desc())
            )
            
            result = await self.session.execute(query)
            rows = result.all()
            
            counts = {}
            for row in rows:
                position = row.position or 'Sin Posición'
                counts[position] = row.count
            
            self._logger.debug(f"Conteos por posición obtenidos: {len(counts)} posiciones")
            return counts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo conteos por posición: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_count_by_position",
                entity_type="Employee"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo conteos por posición: {e}")
            raise create_employee_statistics_error(
                message=f"Error inesperado obteniendo conteos por posición: {e}",
                operation="get_employee_count_by_position",
                original_error=e
            )
    
    # ============================================================================
    # ESTADÍSTICAS FINANCIERAS
    # ============================================================================
    
    async def get_salary_statistics(self) -> Dict[str, float]:
        """Obtiene estadísticas salariales de empleados activos.
        
        Returns:
            Diccionario con estadísticas salariales
        """
        try:
            query = (
                select(
                    func.count(Employee.id).label('count'),
                    func.avg(Employee.salary).label('average'),
                    func.min(Employee.salary).label('minimum'),
                    func.max(Employee.salary).label('maximum'),
                    func.sum(Employee.salary).label('total')
                )
                .where(
                    and_(
                        Employee.status == EmployeeStatus.ACTIVE,
                        Employee.salary.is_not(None)
                    )
                )
            )
            
            result = await self.session.execute(query)
            row = result.first()
            
            if row and row.count > 0:
                stats = {
                    'count': int(row.count),
                    'average': float(row.average or 0),
                    'minimum': float(row.minimum or 0),
                    'maximum': float(row.maximum or 0),
                    'total': float(row.total or 0)
                }
            else:
                stats = {
                    'count': 0,
                    'average': 0.0,
                    'minimum': 0.0,
                    'maximum': 0.0,
                    'total': 0.0
                }
            
            self._logger.debug(f"Estadísticas salariales obtenidas: {stats}")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo estadísticas salariales: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_salary_statistics",
                entity_type="Employee"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo estadísticas salariales: {e}")
            raise create_employee_statistics_error(
                message=f"Error inesperado obteniendo estadísticas salariales: {e}",
                operation="get_salary_statistics",
                original_error=e
            )
    
    # ============================================================================
    # ESTADÍSTICAS TEMPORALES
    # ============================================================================
    
    async def get_hire_date_distribution(self, years: int = 5) -> Dict[str, int]:
        """Obtiene la distribución de fechas de contratación.
        
        Args:
            years: Número de años hacia atrás a considerar
            
        Returns:
            Diccionario con conteos por año
        """
        try:
            current_date = get_current_time().date()
            start_date = date(current_date.year - years + 1, 1, 1)
            
            query = (
                select(
                    func.extract('year', Employee.hire_date).label('year'),
                    func.count(Employee.id).label('count')
                )
                .where(
                    and_(
                        Employee.hire_date >= start_date,
                        Employee.hire_date <= current_date
                    )
                )
                .group_by(func.extract('year', Employee.hire_date))
                .order_by(func.extract('year', Employee.hire_date))
            )
            
            result = await self.session.execute(query)
            rows = result.all()
            
            distribution = {}
            for row in rows:
                year = str(int(row.year))
                distribution[year] = row.count
            
            self._logger.debug(f"Distribución de fechas de contratación obtenida: {len(distribution)} años")
            return distribution
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo distribución de fechas de contratación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_hire_date_distribution",
                entity_type="Employee"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo distribución de fechas de contratación: {e}")
            raise create_employee_statistics_error(
                message=f"Error inesperado obteniendo distribución de fechas de contratación: {e}",
                operation="get_hire_date_distribution",
                original_error=e
            )
    
    # ============================================================================
    # ESTADÍSTICAS DE PARTICIPACIÓN
    # ============================================================================
    
    async def get_team_participation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de participación en equipos.
        
        Returns:
            Diccionario con estadísticas de equipos
        """
        try:
            # Empleados por número de equipos
            teams_per_employee_query = (
                select(
                    func.count(TeamMembership.team_id).label('team_count'),
                    func.count(TeamMembership.employee_id).label('employee_count')
                )
                .join(Employee)
                .where(Employee.status == EmployeeStatus.ACTIVE)
                .group_by(TeamMembership.employee_id)
            )
            
            result = await self.session.execute(teams_per_employee_query)
            team_counts = result.all()
            
            # Distribución de empleados por número de equipos
            distribution = {}
            for row in team_counts:
                team_count = row.team_count
                if team_count not in distribution:
                    distribution[team_count] = 0
                distribution[team_count] += 1
            
            # Empleados sin equipos
            no_team_query = (
                select(func.count(Employee.id))
                .outerjoin(TeamMembership)
                .where(
                    and_(
                        Employee.status == EmployeeStatus.ACTIVE,
                        TeamMembership.employee_id.is_(None)
                    )
                )
            )
            
            no_team_result = await self.session.execute(no_team_query)
            no_team_count = no_team_result.scalar()
            
            if no_team_count > 0:
                distribution[0] = no_team_count
            
            stats = {
                'distribution': distribution,
                'total_employees_with_teams': sum(count for teams, count in distribution.items() if teams > 0),
                'employees_without_teams': distribution.get(0, 0)
            }
            
            self._logger.debug(f"Estadísticas de equipos obtenidas: {stats}")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo estadísticas de equipos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_participation_stats",
                entity_type="Employee"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo estadísticas de equipos: {e}")
            raise create_employee_statistics_error(
                message=f"Error inesperado obteniendo estadísticas de equipos: {e}",
                operation="get_team_participation_stats",
                original_error=e
            )
    
    async def get_project_participation_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de participación en proyectos.
        
        Returns:
            Diccionario con estadísticas de proyectos
        """
        try:
            # Empleados por número de proyectos
            projects_per_employee_query = (
                select(
                    func.count(ProjectAssignment.project_id).label('project_count'),
                    func.count(ProjectAssignment.employee_id).label('employee_count')
                )
                .join(Employee)
                .where(Employee.status == EmployeeStatus.ACTIVE)
                .group_by(ProjectAssignment.employee_id)
            )
            
            result = await self.session.execute(projects_per_employee_query)
            project_counts = result.all()
            
            # Distribución de empleados por número de proyectos
            distribution = {}
            for row in project_counts:
                project_count = row.project_count
                if project_count not in distribution:
                    distribution[project_count] = 0
                distribution[project_count] += 1
            
            # Empleados sin proyectos
            no_project_query = (
                select(func.count(Employee.id))
                .outerjoin(ProjectAssignment)
                .where(
                    and_(
                        Employee.status == EmployeeStatus.ACTIVE,
                        ProjectAssignment.employee_id.is_(None)
                    )
                )
            )
            
            no_project_result = await self.session.execute(no_project_query)
            no_project_count = no_project_result.scalar()
            
            if no_project_count > 0:
                distribution[0] = no_project_count
            
            stats = {
                'distribution': distribution,
                'total_employees_with_projects': sum(count for projects, count in distribution.items() if projects > 0),
                'employees_without_projects': distribution.get(0, 0)
            }
            
            self._logger.debug(f"Estadísticas de proyectos obtenidas: {stats}")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo estadísticas de proyectos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_participation_stats",
                entity_type="Employee"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo estadísticas de proyectos: {e}")
            raise create_employee_statistics_error(
                message=f"Error inesperado obteniendo estadísticas de proyectos: {e}",
                operation="get_project_participation_stats",
                original_error=e
            )
    
    # ============================================================================
    # ESTADÍSTICAS DE VACACIONES
    # ============================================================================
    
    async def get_vacation_statistics(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Obtiene estadísticas de vacaciones.
        
        Args:
            year: Año específico para las estadísticas (actual si es None)
            
        Returns:
            Diccionario con estadísticas de vacaciones
        """
        try:
            if year is None:
                year = get_current_time().year
            
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            
            # Estadísticas generales de vacaciones
            vacation_query = (
                select(
                    func.count(Vacation.id).label('total_requests'),
                    func.sum(
                        case(
                            (Vacation.status == VacationStatus.APPROVED, 1),
                            else_=0
                        )
                    ).label('approved_requests'),
                    func.sum(
                        case(
                            (Vacation.status == VacationStatus.PENDING, 1),
                            else_=0
                        )
                    ).label('pending_requests'),
                    func.sum(
                        case(
                            (Vacation.status == VacationStatus.REJECTED, 1),
                            else_=0
                        )
                    ).label('rejected_requests')
                )
                .join(Employee)
                .where(
                    and_(
                        Employee.status == EmployeeStatus.ACTIVE,
                        or_(
                            and_(Vacation.start_date >= start_date, Vacation.start_date <= end_date),
                            and_(Vacation.end_date >= start_date, Vacation.end_date <= end_date),
                            and_(Vacation.start_date <= start_date, Vacation.end_date >= end_date)
                        )
                    )
                )
            )
            
            result = await self.session.execute(vacation_query)
            row = result.first()
            
            stats = {
                'year': year,
                'total_requests': row.total_requests or 0,
                'approved_requests': row.approved_requests or 0,
                'pending_requests': row.pending_requests or 0,
                'rejected_requests': row.rejected_requests or 0
            }
            
            # Calcular porcentajes
            if stats['total_requests'] > 0:
                stats['approval_rate'] = (stats['approved_requests'] / stats['total_requests']) * 100
                stats['rejection_rate'] = (stats['rejected_requests'] / stats['total_requests']) * 100
            else:
                stats['approval_rate'] = 0.0
                stats['rejection_rate'] = 0.0
            
            self._logger.debug(f"Estadísticas de vacaciones {year} obtenidas: {stats}")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo estadísticas de vacaciones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_vacation_statistics",
                entity_type="Vacation"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo estadísticas de vacaciones: {e}")
            raise create_employee_statistics_error(
                message=f"Error inesperado obteniendo estadísticas de vacaciones: {e}",
                operation="get_vacation_statistics",
                original_error=e
            )
    
    # ============================================================================
    # ESTADÍSTICAS DE HABILIDADES
    # ============================================================================
    
    async def get_skills_distribution(self, limit: int = 20) -> Dict[str, int]:
        """Obtiene la distribución de habilidades más comunes.
        
        Args:
            limit: Número máximo de habilidades a retornar
            
        Returns:
            Diccionario con conteos de habilidades
        """
        try:
            # Obtener todos los empleados activos con habilidades
            query = (
                select(Employee.skills)
                .where(
                    and_(
                        Employee.status == EmployeeStatus.ACTIVE,
                        Employee.skills.is_not(None),
                        Employee.skills != '[]',
                        Employee.skills != ''
                    )
                )
            )
            
            result = await self.session.execute(query)
            skills_data = result.scalars().all()
            
            # Contar habilidades
            skill_counts = {}
            for skills_json in skills_data:
                try:
                    import json
                    skills = json.loads(skills_json)
                    if isinstance(skills, list):
                        for skill in skills:
                            if isinstance(skill, str) and skill.strip():
                                skill_clean = skill.strip()
                                skill_counts[skill_clean] = skill_counts.get(skill_clean, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    continue
            
            # Ordenar por frecuencia y limitar
            sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
            top_skills = dict(sorted_skills[:limit])
            
            self._logger.debug(f"Distribución de habilidades obtenida: {len(top_skills)} habilidades")
            return top_skills
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo distribución de habilidades: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_skills_distribution",
                entity_type="Employee"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo distribución de habilidades: {e}")
            raise create_employee_statistics_error(
                message=f"Error inesperado obteniendo distribución de habilidades: {e}",
                operation="get_skills_distribution",
                original_error=e
            )
    
    # ============================================================================
    # ESTADÍSTICAS ESPECÍFICAS DE EMPLEADO
    # ============================================================================
    
    async def get_employee_workload_stats(self, employee_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Obtiene estadísticas de carga de trabajo de un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Diccionario con estadísticas de carga de trabajo
        """
        try:
            from .....models.workload import Workload
            
            # Verificar que el empleado existe
            employee_query = select(Employee).where(Employee.id == employee_id)
            employee_result = await self.session.execute(employee_query)
            employee = employee_result.scalar_one_or_none()
            
            if not employee:
                return {
                    'employee_id': employee_id,
                    'period': {'start_date': start_date.isoformat(), 'end_date': end_date.isoformat()},
                    'error': 'Employee not found'
                }
            
            # Calcular días del período
            period_days = (end_date - start_date).days + 1
            
            # Consultar datos de Workload para el empleado en el período
            workload_query = select(Workload).where(
                Workload.employee_id == employee_id,
                Workload.date >= start_date,
                Workload.date <= end_date
            )
            
            result = await self.session.execute(workload_query)
            workloads = result.scalars().all()
            
            # Calcular estadísticas reales basadas en los datos de Workload
            total_planned_hours = float(sum(w.planned_hours or 0 for w in workloads))
            total_actual_hours = float(sum(w.actual_hours or 0 for w in workloads))
            total_records = len(workloads)
            
            # Calcular utilización promedio
            utilizations = [w.utilization_percentage for w in workloads if w.utilization_percentage is not None]
            average_utilization = float(sum(utilizations) / len(utilizations)) if utilizations else 0.0
            
            # Calcular tasa de eficiencia (actual/planned * 100)
            efficiency_rate = (total_actual_hours / total_planned_hours * 100) if total_planned_hours > 0 else 0.0
            
            # Obtener proyectos únicos
            active_projects = len(set(w.project_id for w in workloads if w.project_id is not None))
            
            # Contar vacaciones en el período
            vacation_query = (
                select(func.count(Vacation.id))
                .where(
                    and_(
                        Vacation.employee_id == employee_id,
                        Vacation.start_date <= end_date,
                        Vacation.end_date >= start_date,
                        Vacation.status == VacationStatus.APPROVED
                    )
                )
            )
            
            vacation_result = await self.session.execute(vacation_query)
            vacation_days = vacation_result.scalar() or 0
            
            stats = {
                'employee_id': employee_id,
                'employee_name': employee.full_name,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'total_days': period_days
                },
                'workload': {
                    'active_projects': active_projects,
                    'vacation_days': vacation_days,
                    'available_days': max(0, period_days - vacation_days)
                },
                # Campos calculados basados en datos reales de Workload
                'total_planned_hours': total_planned_hours,
                'total_actual_hours': total_actual_hours,
                'total_records': total_records,
                'average_utilization': average_utilization,
                'efficiency_rate': efficiency_rate
            }
            
            self._logger.debug(f"Estadísticas de carga de trabajo generadas para empleado {employee_id}")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos generando estadísticas de carga de trabajo para empleado {employee_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_workload_stats",
                entity_type="Employee",
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado generando estadísticas de carga de trabajo para empleado {employee_id}: {e}")
            raise create_employee_statistics_error(
                message=f"Error inesperado generando estadísticas de carga de trabajo para empleado {employee_id}: {e}",
                operation="get_employee_workload_stats",
                original_error=e
            )
    
    # ============================================================================
    # RESUMEN COMPLETO
    # ============================================================================
    
    async def get_comprehensive_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen completo de estadísticas de empleados.
        
        Returns:
            Diccionario con resumen completo
        """
        try:
            summary = {
                'status_distribution': await self.get_employee_count_by_status(),
                'department_distribution': await self.get_employee_count_by_department(),
                'position_distribution': await self.get_employee_count_by_position(),
                'salary_statistics': await self.get_salary_statistics(),
                'team_participation': await self.get_team_participation_stats(),
                'project_participation': await self.get_project_participation_stats(),
                'vacation_statistics': await self.get_vacation_statistics(),
                'top_skills': await self.get_skills_distribution(10),
                'hire_trends': await self.get_hire_date_distribution()
            }
            
            # Agregar timestamp
            summary['generated_at'] = get_current_time().isoformat()
            
            self._logger.debug("Resumen completo de estadísticas generado")
            return summary
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos generando resumen completo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_comprehensive_summary",
                entity_type="Employee"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado generando resumen completo: {e}")
            raise create_employee_statistics_error(
                message=f"Error inesperado generando resumen completo: {e}",
                operation="get_comprehensive_summary",
                original_error=e
            )