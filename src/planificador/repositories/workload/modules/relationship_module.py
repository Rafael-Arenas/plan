# src/planificador/repositories/workload/modules/relationship_module.py

"""
Módulo de relaciones para operaciones de asociación del repositorio Workload.

Este módulo implementa las operaciones de gestión de relaciones y asociaciones
entre cargas de trabajo, empleados, proyectos y equipos.

Principios de Diseño:
    - Relationship Management: Gestión centralizada de asociaciones
    - Data Integrity: Validación de integridad referencial
    - Dependency Analysis: Análisis de dependencias entre entidades

Uso:
    ```python
    rel_module = WorkloadRelationshipModule(session)
    employee_workloads = await rel_module.get_employee_workloads(employee_id)
    project_workloads = await rel_module.get_project_workloads(project_id)
    dependencies = await rel_module.analyze_workload_dependencies(workload_id)
    ```
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import date, datetime
from sqlalchemy import select, func, and_, or_, exists, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.workload import Workload
from planificador.repositories.workload.interfaces.relationship_interface import IWorkloadRelationshipOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    WorkloadRepositoryError,
    convert_sqlalchemy_error
)


class WorkloadRelationshipModule(BaseRepository[Workload], IWorkloadRelationshipOperations):
    """
    Módulo para operaciones de relaciones del repositorio Workload.
    
    Implementa las operaciones de gestión de relaciones y asociaciones
    entre cargas de trabajo y otras entidades del sistema, incluyendo
    análisis de dependencias y validación de integridad referencial.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Workload
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de relaciones para cargas de trabajo.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Workload)
        self._logger = self._logger.bind(component="WorkloadRelationshipModule")
        self._logger.debug("WorkloadRelationshipModule inicializado")

    async def get_employee_workloads(
        self, 
        employee_id: int,
        include_completed: bool = True,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Workload]:
        """
        Obtiene todas las cargas de trabajo asociadas a un empleado.
        
        Args:
            employee_id: ID del empleado
            include_completed: Si incluir cargas completadas
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
        
        Returns:
            List[Workload]: Lista de cargas de trabajo del empleado
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo cargas de trabajo para empleado {employee_id}")
        
        try:
            conditions = [self.model_class.employee_id == employee_id]
            
            if not include_completed:
                conditions.append(self.model_class.status != 'completed')
            
            if start_date:
                conditions.append(self.model_class.workload_date >= start_date)
            if end_date:
                conditions.append(self.model_class.workload_date <= end_date)
            
            stmt = select(self.model_class).where(and_(*conditions)).order_by(
                self.model_class.workload_date.desc(),
                self.model_class.created_at.desc()
            )
            
            result = await self.session.execute(stmt)
            workloads = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(workloads)} cargas para empleado {employee_id}")
            return list(workloads)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener cargas de empleado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_employee_workloads",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener cargas de empleado: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener cargas de empleado: {e}",
                operation="get_employee_workloads",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )

    async def get_project_workloads(
        self, 
        project_id: int,
        include_completed: bool = True,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Workload]:
        """
        Obtiene todas las cargas de trabajo asociadas a un proyecto.
        
        Args:
            project_id: ID del proyecto
            include_completed: Si incluir cargas completadas
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
        
        Returns:
            List[Workload]: Lista de cargas de trabajo del proyecto
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo cargas de trabajo para proyecto {project_id}")
        
        try:
            conditions = [self.model_class.project_id == project_id]
            
            if not include_completed:
                conditions.append(self.model_class.status != 'completed')
            
            if start_date:
                conditions.append(self.model_class.workload_date >= start_date)
            if end_date:
                conditions.append(self.model_class.workload_date <= end_date)
            
            stmt = select(self.model_class).where(and_(*conditions)).order_by(
                self.model_class.workload_date.desc(),
                self.model_class.employee_id,
                self.model_class.created_at.desc()
            )
            
            result = await self.session.execute(stmt)
            workloads = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(workloads)} cargas para proyecto {project_id}")
            return list(workloads)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener cargas de proyecto: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_project_workloads",
                entity_type=self.model_class.__name__,
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener cargas de proyecto: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener cargas de proyecto: {e}",
                operation="get_project_workloads",
                entity_type=self.model_class.__name__,
                entity_id=project_id,
                original_error=e
            )

    async def get_team_workloads(
        self, 
        team_id: int,
        include_completed: bool = True,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Workload]:
        """
        Obtiene todas las cargas de trabajo asociadas a un equipo.
        
        Args:
            team_id: ID del equipo
            include_completed: Si incluir cargas completadas
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
        
        Returns:
            List[Workload]: Lista de cargas de trabajo del equipo
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo cargas de trabajo para equipo {team_id}")
        
        try:
            # Nota: Esta implementación asume que existe una relación empleado-equipo
            # En una implementación real, se haría JOIN con la tabla de empleados/equipos
            
            conditions = []
            
            if not include_completed:
                conditions.append(self.model_class.status != 'completed')
            
            if start_date:
                conditions.append(self.model_class.workload_date >= start_date)
            if end_date:
                conditions.append(self.model_class.workload_date <= end_date)
            
            # Por ahora, devolvemos una lista vacía con un mensaje informativo
            # En una implementación real, se haría:
            # JOIN workload w ON employee e ON team_member tm WHERE tm.team_id = team_id
            
            self._logger.warning(f"get_team_workloads requiere implementación de relación empleado-equipo")
            
            # Implementación básica - devolver workloads sin filtro de equipo
            base_condition = and_(*conditions) if conditions else True
            
            stmt = select(self.model_class).where(base_condition).limit(0)  # Limitar a 0 por ahora
            
            result = await self.session.execute(stmt)
            workloads = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(workloads)} cargas para equipo {team_id} (implementación básica)")
            return list(workloads)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener cargas de equipo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_team_workloads",
                entity_type=self.model_class.__name__,
                entity_id=team_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener cargas de equipo: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener cargas de equipo: {e}",
                operation="get_team_workloads",
                entity_type=self.model_class.__name__,
                entity_id=team_id,
                original_error=e
            )

    async def validate_employee_project_association(
        self, 
        employee_id: int, 
        project_id: int
    ) -> bool:
        """
        Valida si un empleado puede ser asociado a un proyecto específico.
        
        Args:
            employee_id: ID del empleado
            project_id: ID del proyecto
        
        Returns:
            bool: True si la asociación es válida
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la validación
        """
        self._logger.debug(f"Validando asociación empleado {employee_id} - proyecto {project_id}")
        
        try:
            # Verificar si ya existe una asociación activa
            existing_stmt = select(self.model_class).where(
                and_(
                    self.model_class.employee_id == employee_id,
                    self.model_class.project_id == project_id,
                    self.model_class.status.in_(['pending', 'in_progress'])
                )
            ).limit(1)
            
            result = await self.session.execute(existing_stmt)
            existing_workload = result.scalar_one_or_none()
            
            # Por ahora, permitimos múltiples asociaciones activas
            # En una implementación real, podrían existir reglas de negocio específicas
            
            is_valid = True  # Siempre válido por defecto
            
            if existing_workload:
                self._logger.debug(f"Asociación existente encontrada: {existing_workload.id}")
            
            self._logger.debug(f"Asociación empleado-proyecto válida: {is_valid}")
            return is_valid
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al validar asociación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_employee_project_association",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar asociación: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al validar asociación: {e}",
                operation="validate_employee_project_association",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def validate_team_project_association(
        self, 
        team_id: int, 
        project_id: int
    ) -> bool:
        """
        Valida si un equipo puede ser asociado a un proyecto específico.
        
        Args:
            team_id: ID del equipo
            project_id: ID del proyecto
        
        Returns:
            bool: True si la asociación es válida
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la validación
        """
        self._logger.debug(f"Validando asociación equipo {team_id} - proyecto {project_id}")
        
        try:
            # En una implementación real, se verificarían reglas de negocio específicas
            # como capacidad del equipo, disponibilidad, etc.
            
            # Por ahora, siempre devolvemos True
            is_valid = True
            
            self._logger.debug(f"Asociación equipo-proyecto válida: {is_valid}")
            return is_valid
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al validar asociación equipo-proyecto: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_team_project_association",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al validar asociación equipo-proyecto: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al validar asociación equipo-proyecto: {e}",
                operation="validate_team_project_association",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def analyze_workload_dependencies(
        self, 
        workload_id: int
    ) -> Dict[str, Any]:
        """
        Analiza las dependencias de una carga de trabajo específica.
        
        Args:
            workload_id: ID de la carga de trabajo
        
        Returns:
            Dict[str, Any]: Análisis de dependencias
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        self._logger.debug(f"Analizando dependencias de carga {workload_id}")
        
        try:
            # Obtener la carga de trabajo principal
            main_workload = await self.get_by_id(workload_id)
            if not main_workload:
                raise WorkloadRepositoryError(
                    message=f"Carga de trabajo {workload_id} no encontrada",
                    operation="analyze_workload_dependencies",
                    entity_type=self.model_class.__name__,
                    entity_id=workload_id
                )
            
            # Analizar cargas relacionadas por empleado
            employee_workloads_stmt = select(self.model_class).where(
                and_(
                    self.model_class.employee_id == main_workload.employee_id,
                    self.model_class.id != workload_id,
                    self.model_class.workload_date.between(
                        main_workload.workload_date - timedelta(days=7),
                        main_workload.workload_date + timedelta(days=7)
                    )
                )
            ).order_by(self.model_class.workload_date)
            
            employee_result = await self.session.execute(employee_workloads_stmt)
            related_by_employee = list(employee_result.scalars().all())
            
            # Analizar cargas relacionadas por proyecto
            project_workloads_stmt = select(self.model_class).where(
                and_(
                    self.model_class.project_id == main_workload.project_id,
                    self.model_class.id != workload_id,
                    self.model_class.workload_date.between(
                        main_workload.workload_date - timedelta(days=14),
                        main_workload.workload_date + timedelta(days=14)
                    )
                )
            ).order_by(self.model_class.workload_date)
            
            project_result = await self.session.execute(project_workloads_stmt)
            related_by_project = list(project_result.scalars().all())
            
            # Analizar conflictos potenciales (mismo empleado, mismo día)
            conflicts_stmt = select(self.model_class).where(
                and_(
                    self.model_class.employee_id == main_workload.employee_id,
                    self.model_class.workload_date == main_workload.workload_date,
                    self.model_class.id != workload_id
                )
            )
            
            conflicts_result = await self.session.execute(conflicts_stmt)
            potential_conflicts = list(conflicts_result.scalars().all())
            
            # Calcular métricas de dependencia
            total_hours_same_day = sum(w.hours for w in potential_conflicts) + main_workload.hours
            
            analysis = {
                'workload_id': workload_id,
                'main_workload': {
                    'employee_id': main_workload.employee_id,
                    'project_id': main_workload.project_id,
                    'workload_date': main_workload.workload_date.isoformat(),
                    'hours': float(main_workload.hours),
                    'status': main_workload.status
                },
                'dependencies': {
                    'related_by_employee': [
                        {
                            'id': w.id,
                            'project_id': w.project_id,
                            'workload_date': w.workload_date.isoformat(),
                            'hours': float(w.hours),
                            'status': w.status
                        } for w in related_by_employee
                    ],
                    'related_by_project': [
                        {
                            'id': w.id,
                            'employee_id': w.employee_id,
                            'workload_date': w.workload_date.isoformat(),
                            'hours': float(w.hours),
                            'status': w.status
                        } for w in related_by_project
                    ],
                    'potential_conflicts': [
                        {
                            'id': w.id,
                            'project_id': w.project_id,
                            'hours': float(w.hours),
                            'status': w.status
                        } for w in potential_conflicts
                    ]
                },
                'metrics': {
                    'related_workloads_count': len(related_by_employee) + len(related_by_project),
                    'potential_conflicts_count': len(potential_conflicts),
                    'total_hours_same_day': float(total_hours_same_day),
                    'has_overallocation': total_hours_same_day > 8,
                    'dependency_score': min(100, (len(related_by_employee) * 10) + (len(related_by_project) * 5))
                }
            }
            
            self._logger.debug(f"Análisis de dependencias completado para carga {workload_id}")
            return analysis
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al analizar dependencias: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="analyze_workload_dependencies",
                entity_type=self.model_class.__name__,
                entity_id=workload_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al analizar dependencias: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al analizar dependencias: {e}",
                operation="analyze_workload_dependencies",
                entity_type=self.model_class.__name__,
                entity_id=workload_id,
                original_error=e
            )

    async def get_cross_project_workloads(
        self, 
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, List[Workload]]:
        """
        Obtiene cargas de trabajo de un empleado agrupadas por proyecto.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
        
        Returns:
            Dict[str, List[Workload]]: Cargas agrupadas por proyecto
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo cargas cross-project para empleado {employee_id}")
        
        try:
            conditions = [self.model_class.employee_id == employee_id]
            
            if start_date:
                conditions.append(self.model_class.workload_date >= start_date)
            if end_date:
                conditions.append(self.model_class.workload_date <= end_date)
            
            stmt = select(self.model_class).where(and_(*conditions)).order_by(
                self.model_class.project_id,
                self.model_class.workload_date.desc()
            )
            
            result = await self.session.execute(stmt)
            workloads = result.scalars().all()
            
            # Agrupar por proyecto
            grouped_workloads = {}
            for workload in workloads:
                project_key = f"project_{workload.project_id}"
                if project_key not in grouped_workloads:
                    grouped_workloads[project_key] = []
                grouped_workloads[project_key].append(workload)
            
            self._logger.debug(f"Cargas agrupadas en {len(grouped_workloads)} proyectos")
            return grouped_workloads
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener cargas cross-project: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_cross_project_workloads",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener cargas cross-project: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener cargas cross-project: {e}",
                operation="get_cross_project_workloads",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )

    async def find_workload_conflicts(
        self,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Encuentra conflictos potenciales en las cargas de trabajo.
        
        Args:
            employee_id: ID del empleado (opcional)
            project_id: ID del proyecto (opcional)
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
        
        Returns:
            List[Dict[str, Any]]: Lista de conflictos encontrados
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la búsqueda
        """
        self._logger.debug("Buscando conflictos en cargas de trabajo")
        
        try:
            conditions = []
            
            if employee_id:
                conditions.append(self.model_class.employee_id == employee_id)
            if project_id:
                conditions.append(self.model_class.project_id == project_id)
            if start_date:
                conditions.append(self.model_class.workload_date >= start_date)
            if end_date:
                conditions.append(self.model_class.workload_date <= end_date)
            
            base_condition = and_(*conditions) if conditions else True
            
            # Buscar días con más de 8 horas por empleado
            overallocation_stmt = select(
                self.model_class.employee_id,
                self.model_class.workload_date,
                func.sum(self.model_class.hours).label('total_hours'),
                func.count(self.model_class.id).label('workload_count')
            ).where(base_condition).group_by(
                self.model_class.employee_id,
                self.model_class.workload_date
            ).having(func.sum(self.model_class.hours) > 8)
            
            overallocation_result = await self.session.execute(overallocation_stmt)
            conflicts = []
            
            for row in overallocation_result:
                # Obtener las cargas específicas del conflicto
                conflict_workloads_stmt = select(self.model_class).where(
                    and_(
                        self.model_class.employee_id == row.employee_id,
                        self.model_class.workload_date == row.workload_date,
                        base_condition
                    )
                )
                
                conflict_result = await self.session.execute(conflict_workloads_stmt)
                conflict_workloads = list(conflict_result.scalars().all())
                
                conflict = {
                    'type': 'overallocation',
                    'employee_id': row.employee_id,
                    'date': row.workload_date.isoformat(),
                    'total_hours': float(row.total_hours),
                    'workload_count': row.workload_count,
                    'excess_hours': float(row.total_hours - 8),
                    'workloads': [
                        {
                            'id': w.id,
                            'project_id': w.project_id,
                            'hours': float(w.hours),
                            'status': w.status,
                            'description': w.description
                        } for w in conflict_workloads
                    ]
                }
                conflicts.append(conflict)
            
            self._logger.debug(f"Encontrados {len(conflicts)} conflictos")
            return conflicts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al buscar conflictos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_workload_conflicts",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar conflictos: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al buscar conflictos: {e}",
                operation="find_workload_conflicts",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    # Métodos alias para compatibilidad con la interfaz
    async def get_workloads_by_employee(
        self, 
        employee_id: int,
        include_completed: bool = True,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Workload]:
        """Alias para get_employee_workloads."""
        return await self.get_employee_workloads(employee_id, include_completed, start_date, end_date)

    async def get_workloads_by_project(
        self, 
        project_id: int,
        include_completed: bool = True,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Workload]:
        """Alias para get_project_workloads."""
        return await self.get_project_workloads(project_id, include_completed, start_date, end_date)

    async def get_workloads_by_team(
        self, 
        team_id: int,
        include_completed: bool = True,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Workload]:
        """Alias para get_team_workloads."""
        return await self.get_team_workloads(team_id, include_completed, start_date, end_date)