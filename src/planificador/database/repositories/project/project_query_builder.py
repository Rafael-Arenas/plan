# src/planificador/database/repositories/project/project_query_builder.py

from typing import List, Optional, Dict, Any, Union
from datetime import date
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ....models.project import Project, ProjectStatus, ProjectPriority
from ....models.client import Client
from ....models.project_assignment import ProjectAssignment
from ....models.vacation import Vacation, VacationStatus
from ....utils.date_utils import get_current_time


class ProjectQueryBuilder:
    """
    Constructor de consultas especializadas para proyectos.
    
    Centraliza toda la lógica de construcción de consultas SQL complejas
    para el repositorio de proyectos, siguiendo el patrón Builder.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger = logging.getLogger(__name__)
    
    # ==========================================
    # CONSULTAS BASE
    # ==========================================
    
    def build_base_query(self) -> select:
        """Construye la consulta base para proyectos."""
        return select(Project)
    
    def build_by_reference_query(self, reference: str) -> select:
        """Construye consulta para buscar por referencia."""
        return self.build_base_query().where(Project.reference == reference)
    
    def build_by_trigram_query(self, trigram: str) -> select:
        """Construye consulta para buscar por trigrama."""
        return self.build_base_query().where(Project.trigram == trigram)
    
    # ==========================================
    # CONSULTAS POR ATRIBUTOS
    # ==========================================
    
    def build_search_by_name_query(self, search_term: str) -> select:
        """Construye consulta para búsqueda por nombre/referencia/trigrama."""
        return self.build_base_query().where(
            or_(
                Project.name.ilike(f"%{search_term}%"),
                Project.reference.ilike(f"%{search_term}%"),
                Project.trigram.ilike(f"%{search_term}%")
            )
        ).order_by(Project.name)
    
    def build_by_client_query(self, client_id: int) -> select:
        """Construye consulta para proyectos de un cliente."""
        return self.build_base_query().where(
            Project.client_id == client_id
        ).order_by(Project.start_date.desc(), Project.name)
    
    def build_by_status_query(self, status: ProjectStatus) -> select:
        """Construye consulta para proyectos por estado."""
        return self.build_base_query().where(
            Project.status == status
        ).order_by(Project.start_date.desc(), Project.name)
    
    def build_active_projects_query(self) -> select:
        """Construye consulta para proyectos activos."""
        return self.build_base_query().where(
            and_(
                Project.status.in_([ProjectStatus.PLANNED, ProjectStatus.IN_PROGRESS]),
                Project.is_archived == False
            )
        ).order_by(Project.start_date.desc(), Project.name)
    
    def build_by_priority_query(self, priority: ProjectPriority) -> select:
        """Construye consulta para proyectos por prioridad."""
        return self.build_base_query().where(
            Project.priority == priority
        ).order_by(Project.start_date.desc(), Project.name)

    # ==========================================
    # CONSULTAS TEMPORALES
    # ==========================================
    
    def build_current_week_query(self, date_field: str, **kwargs) -> select:
        """Construye consulta para proyectos de la semana actual."""
        from ....utils.date_utils import get_current_time
        
        current_time = get_current_time()
        week_start = current_time.start_of('week')
        week_end = current_time.end_of('week')
        
        query = self.build_base_query().where(
            and_(
                getattr(Project, date_field) >= week_start.date(),
                getattr(Project, date_field) <= week_end.date()
            )
        )
        
        # Aplicar filtros adicionales
        for key, value in kwargs.items():
            if hasattr(Project, key):
                if isinstance(value, list):
                    query = query.where(getattr(Project, key).in_(value))
                else:
                    query = query.where(getattr(Project, key) == value)
        
        return query.order_by(getattr(Project, date_field))
    
    def build_current_month_query(self, date_field: str, **kwargs) -> select:
        """Construye consulta para proyectos del mes actual."""
        from ....utils.date_utils import get_current_time
        
        current_time = get_current_time()
        month_start = current_time.start_of('month')
        month_end = current_time.end_of('month')
        
        query = self.build_base_query().where(
            and_(
                getattr(Project, date_field) >= month_start.date(),
                getattr(Project, date_field) <= month_end.date()
            )
        )
        
        # Aplicar filtros adicionales
        for key, value in kwargs.items():
            if hasattr(Project, key):
                if isinstance(value, list):
                    query = query.where(getattr(Project, key).in_(value))
                else:
                    query = query.where(getattr(Project, key) == value)
        
        return query.order_by(getattr(Project, date_field))
    
    def build_business_days_query(
        self,
        date_field: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs
    ) -> select:
        """Construye consulta para proyectos en días hábiles."""
        from ....utils.date_utils import get_current_time, is_business_day
        
        if start_date is None:
            start_date = get_current_time().date()
        if end_date is None:
            end_date = get_current_time().date()
        
        query = self.build_base_query().where(
            and_(
                getattr(Project, date_field) >= start_date,
                getattr(Project, date_field) <= end_date
            )
        )
        
        # Aplicar filtros adicionales
        for key, value in kwargs.items():
            if hasattr(Project, key):
                if isinstance(value, list):
                    query = query.where(getattr(Project, key).in_(value))
                else:
                    query = query.where(getattr(Project, key) == value)
        
        return query.order_by(getattr(Project, date_field))

    def build_by_date_range_query(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> select:
        """Construye consulta para proyectos en rango de fechas."""
        query = self.build_base_query()
        conditions = []
        
        if start_date:
            conditions.append(Project.end_date >= start_date)
        if end_date:
            conditions.append(Project.start_date <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        return query.order_by(Project.start_date.desc())
    
    def build_overdue_projects_query(self, reference_date: Optional[date] = None) -> select:
        """Construye consulta para proyectos atrasados."""
        if reference_date is None:
            reference_date = get_current_time().date()
        
        return self.build_base_query().where(
            and_(
                Project.end_date < reference_date,
                Project.status.in_([
                    ProjectStatus.PLANNED,
                    ProjectStatus.IN_PROGRESS,
                    ProjectStatus.ON_HOLD
                ])
            )
        ).order_by(Project.end_date.asc())
    
    # ==========================================
    # CONSULTAS CON RELACIONES
    # ==========================================
    
    def build_with_client_query(self, project_id: int) -> select:
        """Construye consulta para proyecto con cliente cargado."""
        return self.build_base_query().options(
            selectinload(Project.client)
        ).where(Project.id == project_id)
    
    def build_with_assignments_query(self, project_id: int) -> select:
        """Construye consulta para proyecto con asignaciones cargadas."""
        return self.build_base_query().options(
            selectinload(Project.assignments).selectinload(ProjectAssignment.employee)
        ).where(Project.id == project_id)
    
    # ==========================================
    # CONSULTAS DE VALIDACIÓN
    # ==========================================
    
    def build_reference_exists_query(self, reference: str, exclude_id: Optional[int] = None) -> select:
        """Construye consulta para verificar existencia de referencia."""
        query = select(func.count(Project.id)).where(Project.reference == reference)
        
        if exclude_id:
            query = query.where(Project.id != exclude_id)
        
        return query
    
    def build_trigram_exists_query(self, trigram: str, exclude_id: Optional[int] = None) -> select:
        """Construye consulta para verificar existencia de trigrama."""
        query = select(func.count(Project.id)).where(Project.trigram == trigram)
        
        if exclude_id:
            query = query.where(Project.id != exclude_id)
        
        return query
    
    # ==========================================
    # CONSULTAS DE ESTADÍSTICAS
    # ==========================================
    
    def build_project_stats_query(self, project_id: int) -> Dict[str, select]:
        """Construye consultas para estadísticas de proyecto."""
        return {
            'active_assignments': select(func.count(ProjectAssignment.id)).where(
                and_(
                    ProjectAssignment.project_id == project_id,
                    ProjectAssignment.is_active == True
                )
            ),
            'total_assignments': select(func.count(ProjectAssignment.id)).where(
                ProjectAssignment.project_id == project_id
            ),
            'planned_hours': select(
                func.sum(ProjectAssignment.allocated_hours_per_day)
            ).where(
                and_(
                    ProjectAssignment.project_id == project_id,
                    ProjectAssignment.is_active == True
                )
            )
        }
    
    def build_projects_by_status_summary_query(self) -> select:
        """Construye consulta para resumen de proyectos por estado."""
        return select(
            Project.status,
            func.count(Project.id).label('count')
        ).group_by(Project.status)
    
