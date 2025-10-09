# src/planificador/services/domain/team/modules/productivity_operations.py

"""
Módulo de Operaciones de Productividad del Dominio Team.

Este módulo implementa las operaciones de análisis de productividad y rendimiento
de equipos, proporcionando métricas avanzadas para evaluar la eficiencia,
colaboración y desempeño general de los equipos.

Características:
    - Métricas de rendimiento por equipo
    - Análisis de productividad general
    - Métricas de colaboración entre equipos
    - Reportes de resumen ejecutivo
    - Indicadores clave de rendimiento (KPIs)

Principios de Diseño:
    - Data-Driven: Análisis basado en datos objetivos
    - Actionable Insights: Métricas útiles para toma de decisiones
    - Comprehensive: Análisis holístico del rendimiento
    - Performance: Cálculos optimizados para grandes volúmenes

Uso:
    ```python
    productivity_ops = TeamDomainProductivityOperations(team_repo, membership_repo)
    performance = await productivity_ops.calculate_team_performance_metrics(team_id)
    analysis = await productivity_ops.analyze_team_productivity(date_range)
    ```
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import pendulum
from loguru import logger

from planificador.repositories.team import TeamRepositoryFacade
from planificador.repositories.team_membership import TeamMembershipRepositoryFacade
from planificador.services.domain.team.interfaces.productivity_operations_interface import (
    ITeamDomainProductivityOperations,
    DateRange,
    TeamPerformanceMetrics,
    ProductivityAnalysis,
    CollaborationMetrics,
    TeamsSummaryReport
)
from planificador.exceptions.domain import (
    TeamDomainError
)
from planificador.exceptions.base import (
    ValidationError
)
from planificador.exceptions.repository import (
    TeamRepositoryError, TeamMembershipRepositoryError
)


class TeamDomainProductivityOperations(ITeamDomainProductivityOperations):
    """
    Implementación de operaciones de productividad del dominio Team.
    
    Proporciona análisis avanzados de productividad, rendimiento y colaboración
    de equipos con métricas detalladas y reportes ejecutivos.
    
    Attributes:
        _team_repo: Repositorio de equipos
        _membership_repo: Repositorio de membresías
        _logger: Logger para registro de eventos
    """

    def __init__(
        self,
        team_repo: TeamRepositoryFacade,
        membership_repo: TeamMembershipRepositoryFacade
    ):
        """
        Inicializa las operaciones de productividad del dominio Team.
        
        Args:
            team_repo: Repositorio de equipos
            membership_repo: Repositorio de membresías
        """
        self._team_repo = team_repo
        self._membership_repo = membership_repo
        
        logger.debug("TeamDomainProductivityOperations inicializado")

    async def get_team_performance_metrics(
        self,
        team_id: int,
        metric_types: List[str],
        date_range: Optional[DateRange] = None
    ) -> TeamPerformanceMetrics:
        """
        Calcula métricas de rendimiento para un equipo específico.
        
        Args:
            team_id: ID del equipo
            date_range: Rango de fechas para el análisis (opcional)
            
        Returns:
            TeamPerformanceMetrics: Métricas de rendimiento del equipo
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            logger.debug(
                f"Calculando métricas de rendimiento para equipo {team_id}"
            )
            
            # Validar que el equipo existe
            team = await self._team_repo.get_by_id(team_id)
            if not team:
                raise ValidationError(f"No se encontró el equipo con ID {team_id}")
            
            # Establecer rango de fechas por defecto si no se proporciona
            if date_range is None:
                end_date = pendulum.now()
                start_date = end_date.subtract(months=3)  # Últimos 3 meses
                date_range = DateRange(
                    start_date=start_date.to_datetime_string(),
                    end_date=end_date.to_datetime_string()
                )
            
            # Validar rango de fechas
            await self._validate_date_range(date_range)
            
            # Obtener miembros del equipo
            members = await self._membership_repo.get_by_team_id(team_id)
            member_count = len(members)
            
            # Calcular métricas básicas
            # Nota: En una implementación real, estas métricas se calcularían
            # basándose en datos reales de tareas, proyectos, etc.
            
            # Métricas simuladas para demostración
            efficiency_score = await self._calculate_efficiency_score(
                team_id, date_range
            )
            collaboration_index = await self._calculate_collaboration_index(
                team_id, date_range
            )
            task_completion_rate = await self._calculate_task_completion_rate(
                team_id, date_range
            )
            average_response_time = await self._calculate_average_response_time(
                team_id, date_range
            )
            quality_score = await self._calculate_quality_score(
                team_id, date_range
            )
            
            # Crear métricas de rendimiento
            performance_metrics = TeamPerformanceMetrics(
                team_id=team_id,
                team_name=team.name,
                date_range=date_range,
                member_count=member_count,
                efficiency_score=efficiency_score,
                collaboration_index=collaboration_index,
                task_completion_rate=task_completion_rate,
                average_response_time_hours=average_response_time,
                quality_score=quality_score,
                calculated_at=pendulum.now().to_datetime_string()
            )
            
            logger.debug(
                f"Métricas de rendimiento calculadas para equipo {team_id}: "
                f"eficiencia={efficiency_score}, colaboración={collaboration_index}"
            )
            
            return performance_metrics
            
        except TeamRepositoryError as e:
            logger.error(f"Error de repositorio en métricas de rendimiento: {e}")
            raise TeamDomainError(
                f"Error al calcular métricas de rendimiento: {e.message}",
                operation="get_team_performance_metrics",
                entity_type="Team",
                entity_id=str(team_id),
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado en métricas de rendimiento: {e}")
            raise TeamDomainError(
                f"Error inesperado al calcular métricas: {str(e)}",
                operation="get_team_performance_metrics",
                entity_type="Team",
                entity_id=str(team_id),
                original_error=e
            )

    async def get_teams_productivity_analysis(
        self,
        analysis_period: str = "quarter",
        include_comparisons: bool = True
    ) -> ProductivityAnalysis:
        """
        Analiza la productividad general de equipos en un período.
        
        Args:
            date_range: Rango de fechas para el análisis
            team_ids: IDs de equipos específicos (opcional, todos si no se especifica)
            
        Returns:
            ProductivityAnalysis: Análisis de productividad
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            logger.debug(
                f"Analizando productividad para período: {date_range.start_date} "
                f"a {date_range.end_date}"
            )
            
            # Validar rango de fechas
            await self._validate_date_range(date_range)
            
            # Obtener equipos a analizar
            if team_ids:
                teams = []
                for team_id in team_ids:
                    team = await self._team_repo.get_by_id(team_id)
                    if team:
                        teams.append(team)
            else:
                teams = await self._team_repo.get_all()
                teams = [team for team in teams if team.is_active]
            
            if not teams:
                raise ValidationError("No se encontraron equipos para analizar")
            
            # Calcular métricas agregadas
            total_teams = len(teams)
            total_members = 0
            efficiency_scores = []
            collaboration_indices = []
            completion_rates = []
            
            team_metrics = []
            for team in teams:
                try:
                    # Obtener métricas del equipo
                    metrics = await self.get_team_performance_metrics(
                        team.id, date_range
                    )
                    team_metrics.append(metrics)
                    
                    # Agregar a totales
                    total_members += metrics.member_count
                    efficiency_scores.append(metrics.efficiency_score)
                    collaboration_indices.append(metrics.collaboration_index)
                    completion_rates.append(metrics.task_completion_rate)
                    
                except Exception as e:
                    logger.warning(
                        f"Error al calcular métricas para equipo {team.id}: {e}"
                    )
                    continue
            
            # Calcular promedios
            avg_efficiency = sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0.0
            avg_collaboration = sum(collaboration_indices) / len(collaboration_indices) if collaboration_indices else 0.0
            avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0.0
            avg_team_size = total_members / total_teams if total_teams > 0 else 0.0
            
            # Identificar equipos top y bottom
            top_performers = sorted(
                team_metrics,
                key=lambda x: x.efficiency_score,
                reverse=True
            )[:3]
            
            bottom_performers = sorted(
                team_metrics,
                key=lambda x: x.efficiency_score
            )[:3]
            
            # Crear análisis de productividad
            productivity_analysis = ProductivityAnalysis(
                date_range=date_range,
                total_teams_analyzed=total_teams,
                total_members=total_members,
                average_team_size=round(avg_team_size, 1),
                overall_efficiency_score=round(avg_efficiency, 2),
                overall_collaboration_index=round(avg_collaboration, 2),
                overall_completion_rate=round(avg_completion_rate, 2),
                top_performing_teams=[tm.team_name for tm in top_performers],
                underperforming_teams=[tm.team_name for tm in bottom_performers],
                recommendations=await self._generate_productivity_recommendations(
                    avg_efficiency, avg_collaboration, avg_completion_rate
                ),
                analyzed_at=pendulum.now().to_datetime_string()
            )
            
            logger.debug(
                f"Análisis de productividad completado: {total_teams} equipos, "
                f"eficiencia promedio: {avg_efficiency:.2f}"
            )
            
            return productivity_analysis
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado en análisis de productividad: {e}")
            raise TeamDomainError(
                f"Error inesperado en análisis de productividad: {str(e)}",
                operation="get_teams_productivity_analysis",
                entity_type="Team",
                original_error=e
            )

    async def get_team_collaboration_metrics(
        self,
        team_ids: Optional[List[int]] = None,
        collaboration_types: List[str] = None
    ) -> CollaborationMetrics:
        """
        Obtiene métricas de colaboración entre equipos.
        
        Args:
            date_range: Rango de fechas para el análisis
            team_ids: IDs de equipos específicos (opcional)
            
        Returns:
            CollaborationMetrics: Métricas de colaboración
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            logger.debug(
                f"Obteniendo métricas de colaboración para período: "
                f"{date_range.start_date} a {date_range.end_date}"
            )
            
            # Validar rango de fechas
            await self._validate_date_range(date_range)
            
            # Obtener equipos
            teams = await self._team_repo.get_all()
            teams = [team for team in teams if team.is_active]
            
            if not teams:
                raise ValidationError("No se encontraron equipos para analizar")
            
            # Calcular métricas de colaboración
            # Nota: En una implementación real, estas métricas se basarían
            # en datos reales de interacciones, proyectos compartidos, etc.
            
            total_teams = len(teams)
            cross_team_projects = await self._count_cross_team_projects(
                team_ids or [t.id for t in teams], date_range
            )
            shared_resources = await self._count_shared_resources(
                team_ids or [t.id for t in teams], date_range
            )
            communication_frequency = await self._calculate_communication_frequency(
                team_ids or [t.id for t in teams], date_range
            )
            knowledge_sharing_score = await self._calculate_knowledge_sharing_score(
                team_ids or [t.id for t in teams], date_range
            )
            
            # Crear métricas de colaboración
            collaboration_metrics = CollaborationMetrics(
                date_range=date_range,
                teams_analyzed=total_teams,
                cross_team_projects=cross_team_projects,
                shared_resources=shared_resources,
                communication_frequency=communication_frequency,
                knowledge_sharing_score=knowledge_sharing_score,
                collaboration_effectiveness=await self._calculate_collaboration_effectiveness(
                    cross_team_projects, shared_resources, communication_frequency
                ),
                calculated_at=pendulum.now().to_datetime_string()
            )
            
            logger.debug(
                f"Métricas de colaboración calculadas: {total_teams} equipos, "
                f"proyectos cruzados: {cross_team_projects}"
            )
            
            return collaboration_metrics
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado en métricas de colaboración: {e}")
            raise TeamDomainError(
                f"Error inesperado en métricas de colaboración: {str(e)}",
                operation="get_team_collaboration_metrics",
                entity_type="Team",
                original_error=e
            )

    async def generate_teams_summary_report(
        self,
        report_format: str = "detailed",
        include_charts: bool = False,
        export_format: str = "json"
    ) -> TeamsSummaryReport:
        """
        Genera un reporte de resumen ejecutivo de equipos.
        
        Args:
            report_format: Formato del reporte (detailed, summary, executive)
            include_charts: Si incluir gráficos en el reporte
            export_format: Formato de exportación (json, pdf, excel)
            
        Returns:
            TeamsSummaryReport: Reporte de resumen
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            logger.debug(
                f"Generando reporte de resumen con formato: {report_format}, "
                f"gráficos: {include_charts}, exportación: {export_format}"
            )
            
            # Establecer rango de fechas por defecto (últimos 3 meses)
            end_date = pendulum.now()
            start_date = end_date.subtract(months=3)
            date_range = DateRange(
                start_date=start_date.to_datetime_string(),
                end_date=end_date.to_datetime_string()
            )
            
            # Validar rango de fechas
            await self._validate_date_range(date_range)
            
            # Obtener equipos (solo activos por defecto)
            teams = await self._team_repo.get_all()
            teams = [team for team in teams if team.is_active]
            
            # Obtener análisis de productividad
            productivity_analysis = await self.get_teams_productivity_analysis(
                date_range, [t.id for t in teams]
            )
            
            # Obtener métricas de colaboración
            collaboration_metrics = await self.get_team_collaboration_metrics(
                date_range, [t.id for t in teams]
            )
            
            # Calcular estadísticas adicionales
            active_teams = len([t for t in teams if t.is_active])
            inactive_teams = len([t for t in teams if not t.is_active])
            
            # Generar reporte de resumen
            summary_report = TeamsSummaryReport(
                date_range=date_range,
                total_teams=len(teams),
                active_teams=active_teams,
                inactive_teams=inactive_teams,
                productivity_analysis=productivity_analysis,
                collaboration_metrics=collaboration_metrics,
                key_insights=await self._generate_key_insights(
                    productivity_analysis, collaboration_metrics
                ),
                action_items=await self._generate_action_items(
                    productivity_analysis, collaboration_metrics
                ),
                generated_at=pendulum.now().to_datetime_string()
            )
            
            logger.debug(
                f"Reporte de resumen generado: {len(teams)} equipos analizados"
            )
            
            return summary_report
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error inesperado en reporte de resumen: {e}")
            raise TeamDomainError(
                f"Error inesperado en reporte de resumen: {str(e)}",
                operation="generate_teams_summary_report",
                entity_type="Team",
                original_error=e
            )

    # Métodos auxiliares privados

    async def _validate_date_range(self, date_range: DateRange) -> None:
        """Valida que el rango de fechas sea válido."""
        start = pendulum.parse(date_range.start_date)
        end = pendulum.parse(date_range.end_date)
        
        if start >= end:
            raise ValidationError(
                "La fecha de inicio debe ser anterior a la fecha de fin"
            )
        
        # Validar que el rango no sea demasiado amplio (máximo 2 años)
        if end.diff(start).in_days() > 730:
            raise ValidationError(
                "El rango de fechas no puede ser mayor a 2 años"
            )

    async def _calculate_efficiency_score(
        self, team_id: int, date_range: DateRange
    ) -> float:
        """Calcula el puntaje de eficiencia del equipo."""
        # Implementación simulada - en producción usaría datos reales
        import random
        return round(random.uniform(0.6, 0.95), 2)

    async def _calculate_collaboration_index(
        self, team_id: int, date_range: DateRange
    ) -> float:
        """Calcula el índice de colaboración del equipo."""
        # Implementación simulada
        import random
        return round(random.uniform(0.5, 0.9), 2)

    async def _calculate_task_completion_rate(
        self, team_id: int, date_range: DateRange
    ) -> float:
        """Calcula la tasa de completación de tareas."""
        # Implementación simulada
        import random
        return round(random.uniform(0.7, 0.98), 2)

    async def _calculate_average_response_time(
        self, team_id: int, date_range: DateRange
    ) -> float:
        """Calcula el tiempo promedio de respuesta en horas."""
        # Implementación simulada
        import random
        return round(random.uniform(2.0, 24.0), 1)

    async def _calculate_quality_score(
        self, team_id: int, date_range: DateRange
    ) -> float:
        """Calcula el puntaje de calidad del trabajo."""
        # Implementación simulada
        import random
        return round(random.uniform(0.6, 0.95), 2)

    async def _count_cross_team_projects(
        self, team_ids: List[int], date_range: DateRange
    ) -> int:
        """Cuenta proyectos que involucran múltiples equipos."""
        # Implementación simulada
        import random
        return random.randint(1, 10)

    async def _count_shared_resources(
        self, team_ids: List[int], date_range: DateRange
    ) -> int:
        """Cuenta recursos compartidos entre equipos."""
        # Implementación simulada
        import random
        return random.randint(5, 25)

    async def _calculate_communication_frequency(
        self, team_ids: List[int], date_range: DateRange
    ) -> float:
        """Calcula la frecuencia de comunicación entre equipos."""
        # Implementación simulada
        import random
        return round(random.uniform(0.3, 0.8), 2)

    async def _calculate_knowledge_sharing_score(
        self, team_ids: List[int], date_range: DateRange
    ) -> float:
        """Calcula el puntaje de intercambio de conocimiento."""
        # Implementación simulada
        import random
        return round(random.uniform(0.4, 0.85), 2)

    async def _calculate_collaboration_effectiveness(
        self, cross_projects: int, shared_resources: int, comm_freq: float
    ) -> float:
        """Calcula la efectividad de colaboración."""
        # Fórmula simple para demostración
        base_score = (cross_projects * 0.3 + shared_resources * 0.1 + comm_freq * 0.6)
        return round(min(base_score / 10, 1.0), 2)

    async def _generate_productivity_recommendations(
        self, efficiency: float, collaboration: float, completion: float
    ) -> List[str]:
        """Genera recomendaciones basadas en métricas de productividad."""
        recommendations = []
        
        if efficiency < 0.7:
            recommendations.append(
                "Considerar capacitación en herramientas de productividad"
            )
        if collaboration < 0.6:
            recommendations.append(
                "Implementar más actividades de trabajo en equipo"
            )
        if completion < 0.8:
            recommendations.append(
                "Revisar procesos de gestión de tareas y plazos"
            )
        
        if not recommendations:
            recommendations.append("Mantener el excelente desempeño actual")
        
        return recommendations

    async def _generate_key_insights(
        self, productivity: ProductivityAnalysis, collaboration: CollaborationMetrics
    ) -> List[str]:
        """Genera insights clave del análisis."""
        insights = []
        
        if productivity.overall_efficiency_score > 0.8:
            insights.append("Los equipos muestran alta eficiencia general")
        
        if collaboration.cross_team_projects > 5:
            insights.append("Excelente colaboración inter-equipos")
        
        if productivity.overall_completion_rate > 0.9:
            insights.append("Tasa de completación de tareas excepcional")
        
        return insights

    async def _generate_action_items(
        self, productivity: ProductivityAnalysis, collaboration: CollaborationMetrics
    ) -> List[str]:
        """Genera elementos de acción basados en el análisis."""
        actions = []
        
        if productivity.underperforming_teams:
            actions.append(
                f"Brindar apoyo adicional a equipos: "
                f"{', '.join(productivity.underperforming_teams)}"
            )
        
        if collaboration.knowledge_sharing_score < 0.6:
            actions.append("Implementar programa de intercambio de conocimiento")
        
        return actions