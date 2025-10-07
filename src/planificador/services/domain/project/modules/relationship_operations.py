# -*- coding: utf-8 -*-
"""
Módulo de Operaciones de Relaciones para Proyectos

Implementa funcionalidades para gestionar relaciones entre proyectos,
clientes, empleados y equipos, incluyendo asignaciones y dependencias.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from loguru import logger

from planificador.repositories.project.project_repository_facade import ProjectRepositoryFacade
from planificador.schemas.project.project import (
    Project,
    ProjectWithDetails,
    ProjectWithAssignments,
    ClientProjectStatsSchema,
    ClientProjectsSummarySchema,
    ValidationResultSchema
)
from planificador.schemas.common_schemas import PaginationSchema
from planificador.exceptions.domain.project_domain_exceptions import (
    ProjectClientRelationshipError,
    ProjectAssignmentError,
    create_project_not_found_error,
    create_project_business_rule_error
)


class ProjectRelationshipOperations:
    """
    Operaciones de relaciones para proyectos.
    
    Maneja las relaciones entre proyectos y otras entidades del sistema,
    incluyendo clientes, empleados, equipos y dependencias entre proyectos.
    """

    def __init__(self, repository_facade: ProjectRepositoryFacade):
        """
        Inicializa las operaciones de relaciones.
        
        Args:
            repository_facade: Fachada del repositorio de proyectos
        """
        self._repository_facade = repository_facade
        self._logger = logger.bind(module="relationship_operations")

    async def get_project_with_client(self, project_id: UUID) -> Optional[ProjectWithDetails]:
        """
        Obtiene un proyecto con información completa del cliente.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            ProjectWithDetails: Proyecto con datos del cliente
        """
        self._logger.debug(f"Obteniendo proyecto {project_id} con información del cliente")
        
        try:
            project = await self.repository.get_with_client(project_id)
            
            if not project:
                raise create_project_not_found_error(project_id)
            
            return ProjectWithDetails.model_validate(project)
            
        except Exception as e:
            self._logger.error(f"Error obteniendo proyecto con cliente: {e}")
            if isinstance(e, (ProjectClientRelationshipError, ValueError)):
                raise
            raise ProjectClientRelationshipError(
                message=f"Error obteniendo proyecto con cliente: {e}",
                operation="get_project_with_client",
                project_id=project_id,
                original_error=e
            )

    async def get_project_with_assignments(self, project_id: UUID) -> Optional[ProjectWithDetails]:
        """
        Obtiene un proyecto con todas sus asignaciones de empleados.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            ProjectWithAssignments: Proyecto con asignaciones
        """
        self._logger.debug(f"Obteniendo proyecto {project_id} con asignaciones")
        
        try:
            project = await self.repository.get_with_assignments(project_id)
            
            if not project:
                raise create_project_not_found_error(project_id)
            
            return ProjectWithAssignments.model_validate(project)
            
        except Exception as e:
            self._logger.error(f"Error obteniendo proyecto con asignaciones: {e}")
            if isinstance(e, (ProjectAssignmentError, ValueError)):
                raise
            raise ProjectAssignmentError(
                message=f"Error obteniendo proyecto con asignaciones: {e}",
                operation="get_project_with_assignments",
                project_id=project_id,
                original_error=e
            )

    async def get_project_with_full_details(self, project_id: UUID) -> Optional[ProjectWithDetails]:
        """
        Obtiene un proyecto con todos los detalles relacionados.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            ProjectFullDetailsSchema: Proyecto con detalles completos
        """
        self._logger.debug(f"Obteniendo proyecto {project_id} con detalles completos")
        
        try:
            project = await self.repository.get_with_full_details(project_id)
            
            if not project:
                raise create_project_not_found_error(project_id)
            
            return ProjectFullDetailsSchema.model_validate(project)
            
        except Exception as e:
            self._logger.error(f"Error obteniendo proyecto con detalles completos: {e}")
            if isinstance(e, (ProjectClientRelationshipError, ProjectAssignmentError, ValueError)):
                raise
            raise ProjectClientRelationshipError(
                message=f"Error obteniendo proyecto con detalles completos: {e}",
                operation="get_project_with_full_details",
                project_id=project_id,
                original_error=e
            )

    async def get_projects_by_client_detailed(
        self,
        client_id: UUID,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[ProjectWithDetails], int]:
        """
        Obtiene todos los proyectos de un cliente específico.
        
        Args:
            client_id: ID del cliente
            include_inactive: Incluir proyectos inactivos
            
        Returns:
            List[Project]: Lista de proyectos del cliente
        """
        self._logger.debug(f"Obteniendo proyectos del cliente {client_id}")
        
        try:
            projects = await self.repository.get_by_client(client_id)
            
            # Filtrar proyectos inactivos si es necesario
            if not include_inactive:
                projects = [
                    p for p in projects 
                    if p.status.value not in ['CANCELLED', 'ARCHIVED']
                ]
            
            return [Project.model_validate(project) for project in projects]
            
        except Exception as e:
            self._logger.error(f"Error obteniendo proyectos del cliente: {e}")
            raise ProjectClientRelationshipError(
                message=f"Error obteniendo proyectos del cliente: {e}",
                operation="get_projects_by_client",
                client_id=client_id,
                original_error=e
            )

    async def get_client_project_summary(self, client_id: UUID) -> ClientProjectStatsSchema:
        """
        Obtiene un resumen de proyectos para un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Dict[str, Any]: Resumen de proyectos del cliente
        """
        self._logger.debug(f"Obteniendo resumen de proyectos del cliente {client_id}")
        
        try:
            projects = await self.repository.get_by_client(client_id)
            
            # Calcular estadísticas
            total_projects = len(projects)
            active_projects = len([p for p in projects if p.status.value == 'ACTIVE'])
            completed_projects = len([p for p in projects if p.status.value == 'COMPLETED'])
            cancelled_projects = len([p for p in projects if p.status.value == 'CANCELLED'])
            
            # Calcular estadísticas de fechas
            projects_with_dates = [p for p in projects if p.start_date and p.end_date]
            
            summary = {
                "client_id": client_id,
                "total_projects": total_projects,
                "projects_by_status": {
                    "active": active_projects,
                    "completed": completed_projects,
                    "cancelled": cancelled_projects,
                    "other": total_projects - active_projects - completed_projects - cancelled_projects
                },
                "date_statistics": {
                    "projects_with_dates": len(projects_with_dates),
                    "earliest_start": min([p.start_date for p in projects_with_dates]) if projects_with_dates else None,
                    "latest_end": max([p.end_date for p in projects_with_dates]) if projects_with_dates else None
                },
                "recent_projects": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "reference": p.reference,
                        "status": p.status.value,
                        "start_date": p.start_date.isoformat() if p.start_date else None,
                        "end_date": p.end_date.isoformat() if p.end_date else None
                    }
                    for p in sorted(projects, key=lambda x: x.created_at, reverse=True)[:5]
                ]
            }
            
            self._logger.debug(f"Resumen generado para cliente {client_id}: {total_projects} proyectos")
            return summary
            
        except Exception as e:
            self._logger.error(f"Error generando resumen de proyectos del cliente: {e}")
            raise ProjectClientRelationshipError(
                message=f"Error generando resumen de proyectos del cliente: {e}",
                operation="get_client_project_summary",
                client_id=client_id,
                original_error=e
            )

    async def analyze_client_project_relationships(self) -> ClientProjectsSummarySchema:
        """
        Analiza las relaciones y patrones de proyectos de un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Dict[str, Any]: Análisis de relaciones de proyectos
        """
        self._logger.debug(f"Analizando relaciones de proyectos del cliente {client_id}")
        
        try:
            projects = await self.repository.get_by_client(client_id)
            
            if not projects:
                return {
                    "client_id": client_id,
                    "has_projects": False,
                    "analysis": "No hay proyectos para analizar"
                }
            
            # Análisis temporal
            projects_with_dates = [p for p in projects if p.start_date and p.end_date]
            
            temporal_analysis = {}
            if projects_with_dates:
                durations = [
                    (p.end_date - p.start_date).days + 1 
                    for p in projects_with_dates
                ]
                
                temporal_analysis = {
                    "average_duration_days": sum(durations) / len(durations),
                    "min_duration_days": min(durations),
                    "max_duration_days": max(durations),
                    "total_project_days": sum(durations)
                }
            
            # Análisis de patrones de estado
            status_patterns = {}
            for project in projects:
                status = project.status.value
                status_patterns[status] = status_patterns.get(status, 0) + 1
            
            # Análisis de frecuencia de proyectos
            project_frequency = await self._analyze_project_frequency(projects)
            
            # Análisis de complejidad (basado en duración y estado)
            complexity_analysis = await self._analyze_project_complexity(projects)
            
            analysis = {
                "client_id": client_id,
                "has_projects": True,
                "total_projects": len(projects),
                "temporal_analysis": temporal_analysis,
                "status_patterns": status_patterns,
                "project_frequency": project_frequency,
                "complexity_analysis": complexity_analysis,
                "recommendations": await self._generate_client_recommendations(
                    projects, temporal_analysis, status_patterns
                )
            }
            
            self._logger.debug(f"Análisis completado para cliente {client_id}")
            return analysis
            
        except Exception as e:
            self._logger.error(f"Error analizando relaciones de proyectos del cliente: {e}")
            raise ProjectClientRelationshipError(
                message=f"Error analizando relaciones de proyectos del cliente: {e}",
                operation="analyze_client_project_relationships",
                client_id=client_id,
                original_error=e
            )

    async def get_project_assignments_summary(self, project_id: UUID) -> Dict[str, Any]:
        """
        Obtiene un resumen de las asignaciones de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict[str, Any]: Resumen de asignaciones del proyecto
        """
        self._logger.debug(f"Obteniendo resumen de asignaciones del proyecto {project_id}")
        
        try:
            project = await self.repository.get_with_assignments(project_id)
            
            if not project:
                raise create_project_not_found_error(project_id)
            
            # Analizar asignaciones (implementación simplificada)
            # En un sistema real, esto consultaría la tabla de asignaciones
            assignments_summary = {
                "project_id": project_id,
                "project_name": project.name,
                "total_assignments": 0,  # Placeholder
                "active_assignments": 0,  # Placeholder
                "assignment_roles": {},  # Placeholder
                "workload_distribution": {},  # Placeholder
                "assignment_timeline": [],  # Placeholder
                "capacity_analysis": {
                    "total_capacity": 0,
                    "used_capacity": 0,
                    "available_capacity": 0,
                    "capacity_percentage": 0
                }
            }
            
            self._logger.debug(f"Resumen de asignaciones generado para proyecto {project_id}")
            return assignments_summary
            
        except Exception as e:
            self._logger.error(f"Error obteniendo resumen de asignaciones: {e}")
            if isinstance(e, ValueError):
                raise
            raise ProjectAssignmentError(
                message=f"Error obteniendo resumen de asignaciones: {e}",
                operation="get_project_assignments_summary",
                project_id=project_id,
                original_error=e
            )

    async def validate_client_relationship(
        self, 
        project_id: UUID, 
        client_id: UUID
    ) -> ValidationResultSchema:
        """
        Valida la relación entre un proyecto y un cliente.
        
        Args:
            project_id: ID del proyecto
            client_id: ID del cliente
            
        Returns:
            Dict[str, Any]: Resultado de la validación
        """
        self._logger.debug(f"Validando relación proyecto {project_id} - cliente {client_id}")
        
        try:
            project = await self.repository.get_by_id(project_id)
            
            if not project:
                raise create_project_not_found_error(project_id)
            
            validation_result = {
                "is_valid": project.client_id == client_id,
                "project_id": project_id,
                "expected_client_id": client_id,
                "actual_client_id": project.client_id,
                "validation_errors": []
            }
            
            if not validation_result["is_valid"]:
                validation_result["validation_errors"].append(
                    f"El proyecto {project_id} pertenece al cliente {project.client_id}, "
                    f"no al cliente {client_id}"
                )
            
            self._logger.debug(f"Validación completada. Válida: {validation_result['is_valid']}")
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error validando relación cliente-proyecto: {e}")
            if isinstance(e, ValueError):
                raise
            raise ProjectClientRelationshipError(
                message=f"Error validando relación cliente-proyecto: {e}",
                operation="validate_client_relationship",
                project_id=project_id,
                client_id=client_id,
                original_error=e
            )

    async def get_related_projects(self, project_id: UUID) -> List[ProjectWithDetails]:
        """
        Obtiene proyectos relacionados según el tipo de relación especificado.
        
        Args:
            project_id: ID del proyecto base
            relationship_type: Tipo de relación ("client", "timeline", "resources")
            
        Returns:
            List[Project]: Lista de proyectos relacionados
        """
        self._logger.debug(f"Obteniendo proyectos relacionados con {project_id} por {relationship_type}")
        
        try:
            base_project = await self.repository.get_by_id(project_id)
            
            if not base_project:
                raise create_project_not_found_error(project_id)
            
            related_projects = []
            
            if relationship_type == "client":
                # Proyectos del mismo cliente
                client_projects = await self.repository.get_by_client(base_project.client_id)
                related_projects = [p for p in client_projects if p.id != project_id]
                
            elif relationship_type == "timeline":
                # Proyectos con fechas superpuestas
                if base_project.start_date and base_project.end_date:
                    overlapping_projects = await self.repository.get_by_date_range(
                        base_project.start_date, 
                        base_project.end_date
                    )
                    related_projects = [p for p in overlapping_projects if p.id != project_id]
                
            elif relationship_type == "resources":
                # Proyectos que comparten recursos (implementación simplificada)
                # En un sistema real, esto consultaría las asignaciones de empleados
                related_projects = []
            
            return [Project.model_validate(project) for project in related_projects]
            
        except Exception as e:
            self._logger.error(f"Error obteniendo proyectos relacionados: {e}")
            if isinstance(e, ValueError):
                raise
            raise ProjectClientRelationshipError(
                message=f"Error obteniendo proyectos relacionados: {e}",
                operation="get_related_projects",
                project_id=project_id,
                original_error=e
            )

    async def analyze_project_dependencies(self, project_id: UUID) -> Dict[str, Any]:
        """
        Analiza las dependencias de un proyecto con otros proyectos.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict[str, Any]: Análisis de dependencias
        """
        self._logger.debug(f"Analizando dependencias del proyecto {project_id}")
        
        try:
            project = await self.repository.get_by_id(project_id)
            
            if not project:
                raise create_project_not_found_error(project_id)
            
            # Obtener proyectos relacionados por diferentes criterios
            client_projects = await self.get_related_projects(project_id, "client")
            timeline_projects = await self.get_related_projects(project_id, "timeline")
            
            # Analizar dependencias temporales
            temporal_dependencies = []
            if project.start_date and project.end_date:
                for related_project in timeline_projects:
                    if (related_project.start_date and related_project.end_date and
                        related_project.start_date <= project.end_date and
                        related_project.end_date >= project.start_date):
                        
                        temporal_dependencies.append({
                            "project_id": related_project.id,
                            "project_name": related_project.name,
                            "dependency_type": "temporal_overlap",
                            "overlap_start": max(project.start_date, related_project.start_date).isoformat(),
                            "overlap_end": min(project.end_date, related_project.end_date).isoformat()
                        })
            
            # Analizar dependencias de cliente
            client_dependencies = [
                {
                    "project_id": p.id,
                    "project_name": p.name,
                    "dependency_type": "same_client",
                    "client_id": p.client_id
                }
                for p in client_projects
            ]
            
            dependencies_analysis = {
                "project_id": project_id,
                "project_name": project.name,
                "temporal_dependencies": temporal_dependencies,
                "client_dependencies": client_dependencies,
                "total_dependencies": len(temporal_dependencies) + len(client_dependencies),
                "dependency_summary": {
                    "has_temporal_conflicts": len(temporal_dependencies) > 0,
                    "shares_client_resources": len(client_dependencies) > 0,
                    "risk_level": await self._calculate_dependency_risk_level(
                        temporal_dependencies, client_dependencies
                    )
                },
                "recommendations": await self._generate_dependency_recommendations(
                    project, temporal_dependencies, client_dependencies
                )
            }
            
            self._logger.debug(f"Análisis de dependencias completado para proyecto {project_id}")
            return dependencies_analysis
            
        except Exception as e:
            self._logger.error(f"Error analizando dependencias del proyecto: {e}")
            if isinstance(e, ValueError):
                raise
            raise ProjectClientRelationshipError(
                message=f"Error analizando dependencias del proyecto: {e}",
                operation="analyze_project_dependencies",
                project_id=project_id,
                original_error=e
            )

    # ============================================================================
    # MÉTODOS PRIVADOS DE UTILIDAD
    # ============================================================================

    async def _analyze_project_frequency(self, projects: List[Project]) -> Dict[str, Any]:
        """Analiza la frecuencia de proyectos del cliente."""
        if not projects:
            return {"frequency": "no_data", "pattern": "none"}
        
        # Ordenar proyectos por fecha de creación
        sorted_projects = sorted(projects, key=lambda p: p.created_at)
        
        if len(sorted_projects) < 2:
            return {"frequency": "single_project", "pattern": "insufficient_data"}
        
        # Calcular intervalos entre proyectos
        intervals = []
        for i in range(1, len(sorted_projects)):
            interval = (sorted_projects[i].created_at - sorted_projects[i-1].created_at).days
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        # Clasificar frecuencia
        if avg_interval <= 30:
            frequency = "high"  # Más de un proyecto por mes
        elif avg_interval <= 90:
            frequency = "medium"  # Un proyecto cada 1-3 meses
        elif avg_interval <= 180:
            frequency = "low"  # Un proyecto cada 3-6 meses
        else:
            frequency = "very_low"  # Menos de un proyecto cada 6 meses
        
        return {
            "frequency": frequency,
            "average_interval_days": avg_interval,
            "total_projects": len(projects),
            "pattern": "regular" if len(set(intervals)) <= 2 else "irregular"
        }

    async def _analyze_project_complexity(self, projects: List[Project]) -> Dict[str, Any]:
        """Analiza la complejidad de los proyectos del cliente."""
        if not projects:
            return {"complexity": "no_data"}
        
        projects_with_dates = [p for p in projects if p.start_date and p.end_date]
        
        if not projects_with_dates:
            return {"complexity": "insufficient_data"}
        
        # Calcular duración promedio
        durations = [(p.end_date - p.start_date).days + 1 for p in projects_with_dates]
        avg_duration = sum(durations) / len(durations)
        
        # Clasificar complejidad basada en duración
        if avg_duration <= 30:
            complexity = "low"  # Proyectos cortos
        elif avg_duration <= 90:
            complexity = "medium"  # Proyectos medianos
        elif avg_duration <= 180:
            complexity = "high"  # Proyectos largos
        else:
            complexity = "very_high"  # Proyectos muy largos
        
        # Analizar variabilidad
        if len(durations) > 1:
            variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
            std_dev = variance ** 0.5
            variability = "high" if std_dev > avg_duration * 0.5 else "low"
        else:
            variability = "no_data"
        
        return {
            "complexity": complexity,
            "average_duration_days": avg_duration,
            "duration_variability": variability,
            "project_count": len(projects_with_dates)
        }

    async def _generate_client_recommendations(
        self,
        projects: List[Project],
        temporal_analysis: Dict[str, Any],
        status_patterns: Dict[str, int]
    ) -> List[str]:
        """Genera recomendaciones basadas en el análisis del cliente."""
        recommendations = []
        
        # Recomendaciones basadas en patrones de estado
        total_projects = len(projects)
        completed_ratio = status_patterns.get("COMPLETED", 0) / total_projects if total_projects > 0 else 0
        cancelled_ratio = status_patterns.get("CANCELLED", 0) / total_projects if total_projects > 0 else 0
        
        if completed_ratio > 0.8:
            recommendations.append("Excelente historial de finalización de proyectos")
        elif completed_ratio < 0.5:
            recommendations.append("Considerar mejorar el seguimiento de proyectos para aumentar la tasa de finalización")
        
        if cancelled_ratio > 0.2:
            recommendations.append("Alta tasa de cancelación - revisar proceso de planificación inicial")
        
        # Recomendaciones basadas en duración
        if temporal_analysis and temporal_analysis.get("average_duration_days", 0) > 180:
            recommendations.append("Los proyectos tienden a ser largos - considerar dividir en fases")
        
        # Recomendación general
        if not recommendations:
            recommendations.append("Mantener el buen desempeño en la gestión de proyectos")
        
        return recommendations

    async def _calculate_dependency_risk_level(
        self,
        temporal_dependencies: List[Dict[str, Any]],
        client_dependencies: List[Dict[str, Any]]
    ) -> str:
        """Calcula el nivel de riesgo basado en dependencias."""
        risk_score = 0
        
        # Riesgo por dependencias temporales
        risk_score += len(temporal_dependencies) * 2
        
        # Riesgo por dependencias de cliente
        risk_score += len(client_dependencies) * 1
        
        if risk_score == 0:
            return "low"
        elif risk_score <= 3:
            return "medium"
        else:
            return "high"

    async def _generate_dependency_recommendations(
        self,
        project: Project,
        temporal_dependencies: List[Dict[str, Any]],
        client_dependencies: List[Dict[str, Any]]
    ) -> List[str]:
        """Genera recomendaciones basadas en dependencias."""
        recommendations = []
        
        if temporal_dependencies:
            recommendations.append(
                f"Coordinar con {len(temporal_dependencies)} proyectos con fechas superpuestas"
            )
            recommendations.append("Verificar disponibilidad de recursos compartidos")
        
        if client_dependencies:
            recommendations.append(
                f"Considerar la carga de trabajo del cliente con {len(client_dependencies)} proyectos adicionales"
            )
        
        if not temporal_dependencies and not client_dependencies:
            recommendations.append("Proyecto independiente - sin dependencias críticas detectadas")
        
        return recommendations