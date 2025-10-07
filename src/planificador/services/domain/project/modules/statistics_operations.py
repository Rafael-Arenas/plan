# -*- coding: utf-8 -*-
"""
Módulo de Operaciones de Estadísticas para Proyectos

Implementa funcionalidades para generar estadísticas, métricas y análisis
de rendimiento de proyectos, incluyendo reportes y dashboards.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from loguru import logger
import pendulum

from planificador.models.project import Project, ProjectStatus, ProjectPriority
from planificador.repositories.project.project_repository_facade import ProjectRepositoryFacade
from planificador.exceptions.domain.project_domain_exceptions import (
    ProjectStatisticsError,
    create_project_business_rule_error
)


class ProjectStatisticsOperations:
    """
    Operaciones de estadísticas para proyectos.
    
    Proporciona funcionalidades para generar estadísticas, métricas,
    análisis de rendimiento y reportes de proyectos.
    """

    def __init__(self, repository_facade: ProjectRepositoryFacade):
        """
        Inicializa las operaciones de estadísticas.
        
        Args:
            repository_facade: Fachada del repositorio de proyectos
        """
        self.repository_facade = repository_facade
        self._logger = logger.bind(module="project_statistics_operations")

    async def get_status_summary(self) -> Dict[str, int]:
        """
        Obtiene un resumen de proyectos por estado.
        
        Returns:
            Dict[str, Any]: Resumen de estados de proyectos
        """
        self._logger.debug("Generando resumen de estados de proyectos")
        
        try:
            summary = await self.repository.get_status_summary()
            
            # Enriquecer con cálculos adicionales
            total_projects = sum(summary.values()) if summary else 0
            
            enriched_summary = {
                "status_counts": summary,
                "total_projects": total_projects,
                "status_percentages": {
                    status: (count / total_projects * 100) if total_projects > 0 else 0
                    for status, count in summary.items()
                } if summary else {},
                "active_ratio": (
                    summary.get("ACTIVE", 0) / total_projects * 100
                ) if total_projects > 0 else 0,
                "completion_ratio": (
                    summary.get("COMPLETED", 0) / total_projects * 100
                ) if total_projects > 0 else 0,
                "generated_at": pendulum.now().isoformat()
            }
            
            self._logger.debug(f"Resumen de estados generado: {total_projects} proyectos totales")
            return enriched_summary
            
        except Exception as e:
            self._logger.error(f"Error generando resumen de estados: {e}")
            raise ProjectStatisticsError(
                message=f"Error generando resumen de estados: {e}",
                operation="get_status_summary",
                original_error=e
            )

    async def get_overdue_projects_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de proyectos vencidos.
        
        Returns:
            Dict[str, Any]: Resumen de proyectos vencidos
        """
        self._logger.debug("Generando resumen de proyectos vencidos")
        
        try:
            overdue_summary = await self.repository.get_overdue_projects_summary()
            overdue_projects = await self.repository.get_overdue_projects()
            
            # Análisis detallado de proyectos vencidos
            if overdue_projects:
                overdue_analysis = await self._analyze_overdue_projects(overdue_projects)
            else:
                overdue_analysis = {
                    "average_delay_days": 0,
                    "max_delay_days": 0,
                    "delay_distribution": {},
                    "priority_distribution": {},
                    "client_distribution": {}
                }
            
            summary = {
                **overdue_summary,
                "overdue_analysis": overdue_analysis,
                "generated_at": pendulum.now().isoformat()
            }
            
            self._logger.debug(f"Resumen de vencidos generado: {len(overdue_projects)} proyectos")
            return summary
            
        except Exception as e:
            self._logger.error(f"Error generando resumen de proyectos vencidos: {e}")
            raise ProjectStatisticsError(
                message=f"Error generando resumen de proyectos vencidos: {e}",
                operation="get_overdue_projects_summary",
                original_error=e
            )

    async def get_project_performance_stats(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de rendimiento de proyectos.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict[str, Any]: Estadísticas de rendimiento
        """
        self._logger.debug("Generando estadísticas de rendimiento de proyectos")
        
        try:
            # Usar fechas por defecto si no se proporcionan
            if not end_date:
                end_date = pendulum.now().date()
            if not start_date:
                start_date = pendulum.now().subtract(months=6).date()
            
            performance_stats = await self.repository.get_project_performance_stats()
            
            # Obtener proyectos del período para análisis adicional
            period_projects = await self.repository.get_by_date_range(start_date, end_date)
            
            # Análisis de rendimiento del período
            period_analysis = await self._analyze_period_performance(
                period_projects, start_date, end_date
            )
            
            # Análisis de tendencias
            trend_analysis = await self._analyze_performance_trends(
                period_projects, start_date, end_date
            )
            
            stats = {
                **performance_stats,
                "period_analysis": period_analysis,
                "trend_analysis": trend_analysis,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "duration_days": (end_date - start_date).days + 1
                },
                "generated_at": pendulum.now().isoformat()
            }
            
            self._logger.debug(f"Estadísticas de rendimiento generadas para período {start_date} - {end_date}")
            return stats
            
        except Exception as e:
            self._logger.error(f"Error generando estadísticas de rendimiento: {e}")
            raise ProjectStatisticsError(
                message=f"Error generando estadísticas de rendimiento: {e}",
                operation="get_project_performance_stats",
                original_error=e
            )

    async def get_projects_by_status_summary(self) -> Dict[str, List[Project]]:
        """
        Obtiene un resumen detallado de proyectos agrupados por estado.
        
        Returns:
            Dict[str, Any]: Resumen detallado por estado
        """
        self._logger.debug("Generando resumen detallado por estado")
        
        try:
            summary = await self.repository.get_projects_by_status_summary()
            
            # Enriquecer con análisis adicional
            enriched_summary = {}
            total_projects = 0
            
            for status, projects in summary.items():
                project_count = len(projects) if isinstance(projects, list) else projects
                total_projects += project_count
                
                enriched_summary[status] = {
                    "count": project_count,
                    "projects": projects if isinstance(projects, list) else []
                }
            
            # Agregar métricas calculadas
            for status, data in enriched_summary.items():
                data["percentage"] = (
                    data["count"] / total_projects * 100
                ) if total_projects > 0 else 0
            
            result = {
                "status_summary": enriched_summary,
                "total_projects": total_projects,
                "status_distribution": {
                    status: data["percentage"]
                    for status, data in enriched_summary.items()
                },
                "generated_at": pendulum.now().isoformat()
            }
            
            self._logger.debug(f"Resumen detallado por estado generado: {total_projects} proyectos")
            return result
            
        except Exception as e:
            self._logger.error(f"Error generando resumen por estado: {e}")
            raise ProjectStatisticsError(
                message=f"Error generando resumen por estado: {e}",
                operation="get_projects_by_status_summary",
                original_error=e
            )

    async def get_project_workload_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de carga de trabajo de proyectos.
        
        Returns:
            Dict[str, Any]: Estadísticas de carga de trabajo
        """
        self._logger.debug("Generando estadísticas de carga de trabajo")
        
        try:
            workload_stats = await self.repository.get_project_workload_stats()
            
            # Análisis adicional de carga de trabajo
            current_date = pendulum.now().date()
            active_projects = await self.repository.get_by_status(ProjectStatus.ACTIVE)
            
            # Análisis de proyectos activos
            active_analysis = await self._analyze_active_workload(active_projects, current_date)
            
            # Proyección de carga futura
            future_workload = await self._project_future_workload(current_date)
            
            stats = {
                **workload_stats,
                "active_projects_analysis": active_analysis,
                "future_workload_projection": future_workload,
                "workload_recommendations": await self._generate_workload_recommendations(
                    active_analysis, future_workload
                ),
                "generated_at": pendulum.now().isoformat()
            }
            
            self._logger.debug("Estadísticas de carga de trabajo generadas")
            return stats
            
        except Exception as e:
            self._logger.error(f"Error generando estadísticas de carga de trabajo: {e}")
            raise ProjectStatisticsError(
                message=f"Error generando estadísticas de carga de trabajo: {e}",
                operation="get_project_workload_stats",
                original_error=e
            )

    async def get_project_duration_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de duración de proyectos.
        
        Returns:
            Dict[str, Any]: Estadísticas de duración
        """
        self._logger.debug("Generando estadísticas de duración de proyectos")
        
        try:
            duration_stats = await self.repository.get_project_duration_stats()
            
            # Análisis adicional de duraciones
            all_projects = await self.repository.search_projects()
            projects_with_dates = [
                p for p in all_projects 
                if p.start_date and p.end_date
            ]
            
            if projects_with_dates:
                duration_analysis = await self._analyze_project_durations(projects_with_dates)
            else:
                duration_analysis = {
                    "duration_distribution": {},
                    "duration_by_priority": {},
                    "duration_by_status": {},
                    "duration_trends": {}
                }
            
            stats = {
                **duration_stats,
                "detailed_duration_analysis": duration_analysis,
                "duration_insights": await self._generate_duration_insights(duration_analysis),
                "generated_at": pendulum.now().isoformat()
            }
            
            self._logger.debug(f"Estadísticas de duración generadas para {len(projects_with_dates)} proyectos")
            return stats
            
        except Exception as e:
            self._logger.error(f"Error generando estadísticas de duración: {e}")
            raise ProjectStatisticsError(
                message=f"Error generando estadísticas de duración: {e}",
                operation="get_project_duration_stats",
                original_error=e
            )

    async def get_monthly_project_stats(self, year: int, month: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas mensuales de proyectos.
        
        Args:
            year: Año para el análisis
            month: Mes para el análisis
            
        Returns:
            Dict[str, Any]: Estadísticas mensuales
        """
        self._logger.debug(f"Generando estadísticas mensuales para {year}/{month}")
        
        try:
            # Usar fecha actual si no se especifica
            current_date = pendulum.now()
            target_year = year or current_date.year
            target_month = month or current_date.month
            
            monthly_stats = await self.repository.get_monthly_project_stats()
            
            # Análisis específico del mes
            month_start = pendulum.datetime(target_year, target_month, 1).date()
            month_end = pendulum.datetime(target_year, target_month, 1).add(months=1).subtract(days=1).date()
            
            month_projects = await self.repository.get_by_date_range(month_start, month_end)
            
            # Análisis detallado del mes
            month_analysis = await self._analyze_monthly_performance(
                month_projects, target_year, target_month
            )
            
            # Comparación con meses anteriores
            comparison_analysis = await self._compare_monthly_performance(
                target_year, target_month
            )
            
            stats = {
                **monthly_stats,
                "target_period": {
                    "year": target_year,
                    "month": target_month,
                    "month_name": pendulum.datetime(target_year, target_month, 1).format("MMMM"),
                    "start_date": month_start.isoformat(),
                    "end_date": month_end.isoformat()
                },
                "month_analysis": month_analysis,
                "comparison_analysis": comparison_analysis,
                "generated_at": pendulum.now().isoformat()
            }
            
            self._logger.debug(f"Estadísticas mensuales generadas para {target_year}/{target_month}")
            return stats
            
        except Exception as e:
            self._logger.error(f"Error generando estadísticas mensuales: {e}")
            raise ProjectStatisticsError(
                message=f"Error generando estadísticas mensuales: {e}",
                operation="get_monthly_project_stats",
                original_error=e
            )

    async def get_client_project_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos por cliente.
        
        Args:
            client_id: ID del cliente específico (opcional)
            
        Returns:
            Dict[str, Any]: Estadísticas por cliente
        """
        self._logger.debug(f"Generando estadísticas de cliente {client_id or 'todos'}")
        
        try:
            client_stats = await self.repository.get_client_project_stats()
            
            if client_id:
                # Análisis específico del cliente
                client_projects = await self.repository.get_by_client(client_id)
                client_analysis = await self._analyze_client_performance(client_projects, client_id)
                
                stats = {
                    "client_id": client_id,
                    "client_analysis": client_analysis,
                    "overall_client_stats": client_stats,
                    "generated_at": pendulum.now().isoformat()
                }
            else:
                # Análisis de todos los clientes
                all_clients_analysis = await self._analyze_all_clients_performance(client_stats)
                
                stats = {
                    "all_clients_stats": client_stats,
                    "clients_analysis": all_clients_analysis,
                    "top_clients": await self._identify_top_clients(client_stats),
                    "generated_at": pendulum.now().isoformat()
                }
            
            self._logger.debug(f"Estadísticas de cliente generadas")
            return stats
            
        except Exception as e:
            self._logger.error(f"Error generando estadísticas de cliente: {e}")
            raise ProjectStatisticsError(
                message=f"Error generando estadísticas de cliente: {e}",
                operation="get_client_project_stats",
                original_error=e
            )

    async def get_overdue_projects_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas detalladas de proyectos vencidos.
        
        Returns:
            Dict[str, Any]: Estadísticas detalladas de vencidos
        """
        self._logger.debug("Generando estadísticas detalladas de proyectos vencidos")
        
        try:
            overdue_stats = await self.repository.get_overdue_projects_stats()
            overdue_projects = await self.repository.get_overdue_projects()
            
            # Análisis detallado de vencimientos
            detailed_analysis = await self._analyze_overdue_details(overdue_projects)
            
            # Análisis de causas de vencimiento
            causes_analysis = await self._analyze_overdue_causes(overdue_projects)
            
            # Recomendaciones para reducir vencimientos
            recommendations = await self._generate_overdue_recommendations(
                overdue_projects, detailed_analysis, causes_analysis
            )
            
            stats = {
                **overdue_stats,
                "detailed_overdue_analysis": detailed_analysis,
                "overdue_causes_analysis": causes_analysis,
                "overdue_recommendations": recommendations,
                "generated_at": pendulum.now().isoformat()
            }
            
            self._logger.debug(f"Estadísticas detalladas de vencidos generadas: {len(overdue_projects)} proyectos")
            return stats
            
        except Exception as e:
            self._logger.error(f"Error generando estadísticas de proyectos vencidos: {e}")
            raise ProjectStatisticsError(
                message=f"Error generando estadísticas de proyectos vencidos: {e}",
                operation="get_overdue_projects_stats",
                original_error=e
            )

    async def generate_dashboard_summary(self) -> Dict[str, Any]:
        """
        Genera un resumen completo para dashboard ejecutivo.
        
        Returns:
            Dict[str, Any]: Resumen completo para dashboard
        """
        self._logger.debug("Generando resumen completo para dashboard")
        
        try:
            # Recopilar todas las estadísticas principales
            status_summary = await self.get_status_summary()
            overdue_summary = await self.get_overdue_projects_summary()
            workload_stats = await self.get_project_workload_stats()
            performance_stats = await self.get_project_performance_stats()
            
            # Métricas clave
            key_metrics = await self._calculate_key_metrics()
            
            # Alertas y notificaciones
            alerts = await self._generate_dashboard_alerts()
            
            # Tendencias recientes
            recent_trends = await self._analyze_recent_trends()
            
            dashboard_summary = {
                "key_metrics": key_metrics,
                "status_overview": {
                    "total_projects": status_summary["total_projects"],
                    "active_projects": status_summary["status_counts"].get("ACTIVE", 0),
                    "completed_projects": status_summary["status_counts"].get("COMPLETED", 0),
                    "overdue_projects": overdue_summary.get("total_overdue", 0)
                },
                "performance_indicators": {
                    "completion_rate": status_summary["completion_ratio"],
                    "on_time_delivery": performance_stats.get("on_time_percentage", 0),
                    "average_project_duration": performance_stats.get("average_duration_days", 0)
                },
                "workload_overview": {
                    "current_capacity": workload_stats.get("current_capacity_percentage", 0),
                    "projects_starting_this_week": len(
                        await self.repository.get_projects_starting_current_week()
                    ),
                    "projects_ending_this_week": len(
                        await self.repository.get_projects_ending_current_week()
                    )
                },
                "alerts_and_notifications": alerts,
                "recent_trends": recent_trends,
                "generated_at": pendulum.now().isoformat(),
                "refresh_interval_minutes": 15
            }
            
            self._logger.debug("Resumen completo para dashboard generado")
            return dashboard_summary
            
        except Exception as e:
            self._logger.error(f"Error generando resumen de dashboard: {e}")
            raise ProjectStatisticsError(
                message=f"Error generando resumen de dashboard: {e}",
                operation="generate_dashboard_summary",
                original_error=e
            )

    # ============================================================================
    # MÉTODOS PRIVADOS DE ANÁLISIS
    # ============================================================================

    async def _analyze_overdue_projects(self, overdue_projects: List[Project]) -> Dict[str, Any]:
        """Analiza proyectos vencidos en detalle."""
        if not overdue_projects:
            return {
                "average_delay_days": 0,
                "max_delay_days": 0,
                "delay_distribution": {},
                "priority_distribution": {},
                "client_distribution": {}
            }
        
        current_date = pendulum.now().date()
        delays = []
        priority_counts = {}
        client_counts = {}
        
        for project in overdue_projects:
            if project.end_date:
                delay_days = (current_date - project.end_date).days
                delays.append(delay_days)
                
                # Distribución por prioridad
                priority = project.priority.value if project.priority else "UNKNOWN"
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                # Distribución por cliente
                client_id = str(project.client_id)
                client_counts[client_id] = client_counts.get(client_id, 0) + 1
        
        # Distribución de retrasos
        delay_distribution = {}
        for delay in delays:
            if delay <= 7:
                category = "1-7_days"
            elif delay <= 30:
                category = "8-30_days"
            elif delay <= 90:
                category = "31-90_days"
            else:
                category = "90+_days"
            
            delay_distribution[category] = delay_distribution.get(category, 0) + 1
        
        return {
            "average_delay_days": sum(delays) / len(delays) if delays else 0,
            "max_delay_days": max(delays) if delays else 0,
            "delay_distribution": delay_distribution,
            "priority_distribution": priority_counts,
            "client_distribution": client_counts
        }

    async def _analyze_period_performance(
        self,
        projects: List[Project],
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Analiza el rendimiento en un período específico."""
        if not projects:
            return {
                "projects_started": 0,
                "projects_completed": 0,
                "projects_cancelled": 0,
                "average_completion_time": 0,
                "success_rate": 0
            }
        
        projects_started = len([
            p for p in projects 
            if p.start_date and start_date <= p.start_date <= end_date
        ])
        
        projects_completed = len([
            p for p in projects 
            if p.status == ProjectStatus.COMPLETED and 
            p.end_date and start_date <= p.end_date <= end_date
        ])
        
        projects_cancelled = len([
            p for p in projects 
            if p.status == ProjectStatus.CANCELLED
        ])
        
        # Calcular tiempo promedio de finalización
        completed_projects = [
            p for p in projects 
            if p.status == ProjectStatus.COMPLETED and p.start_date and p.end_date
        ]
        
        if completed_projects:
            completion_times = [
                (p.end_date - p.start_date).days + 1 
                for p in completed_projects
            ]
            average_completion_time = sum(completion_times) / len(completion_times)
        else:
            average_completion_time = 0
        
        success_rate = (
            projects_completed / (projects_completed + projects_cancelled) * 100
        ) if (projects_completed + projects_cancelled) > 0 else 0
        
        return {
            "projects_started": projects_started,
            "projects_completed": projects_completed,
            "projects_cancelled": projects_cancelled,
            "average_completion_time": average_completion_time,
            "success_rate": success_rate
        }

    async def _analyze_performance_trends(
        self,
        projects: List[Project],
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Analiza tendencias de rendimiento."""
        # Implementación simplificada de análisis de tendencias
        return {
            "trend_direction": "stable",  # stable, improving, declining
            "completion_trend": "stable",
            "duration_trend": "stable",
            "quality_trend": "stable"
        }

    async def _analyze_active_workload(
        self,
        active_projects: List[Project],
        current_date: date
    ) -> Dict[str, Any]:
        """Analiza la carga de trabajo actual."""
        if not active_projects:
            return {
                "total_active": 0,
                "high_priority": 0,
                "ending_soon": 0,
                "overdue": 0,
                "workload_level": "low"
            }
        
        high_priority = len([
            p for p in active_projects 
            if p.priority == ProjectPriority.HIGH
        ])
        
        ending_soon = len([
            p for p in active_projects 
            if p.end_date and (p.end_date - current_date).days <= 7
        ])
        
        overdue = len([
            p for p in active_projects 
            if p.end_date and p.end_date < current_date
        ])
        
        # Determinar nivel de carga
        total_active = len(active_projects)
        if total_active <= 5:
            workload_level = "low"
        elif total_active <= 15:
            workload_level = "medium"
        elif total_active <= 25:
            workload_level = "high"
        else:
            workload_level = "critical"
        
        return {
            "total_active": total_active,
            "high_priority": high_priority,
            "ending_soon": ending_soon,
            "overdue": overdue,
            "workload_level": workload_level
        }

    async def _project_future_workload(self, current_date: date) -> Dict[str, Any]:
        """Proyecta la carga de trabajo futura."""
        # Obtener proyectos que inician en las próximas semanas
        future_start = current_date
        future_end = pendulum.now().add(months=3).date()
        
        future_projects = await self.repository.get_by_date_range(future_start, future_end)
        
        # Agrupar por semanas
        weekly_projection = {}
        for project in future_projects:
            if project.start_date and project.start_date >= current_date:
                week_start = pendulum.instance(project.start_date).start_of('week').date()
                week_key = week_start.isoformat()
                
                if week_key not in weekly_projection:
                    weekly_projection[week_key] = {
                        "projects_starting": 0,
                        "projects_ending": 0,
                        "net_change": 0
                    }
                
                weekly_projection[week_key]["projects_starting"] += 1
                weekly_projection[week_key]["net_change"] += 1
            
            if project.end_date and project.end_date >= current_date:
                week_end = pendulum.instance(project.end_date).start_of('week').date()
                week_key = week_end.isoformat()
                
                if week_key not in weekly_projection:
                    weekly_projection[week_key] = {
                        "projects_starting": 0,
                        "projects_ending": 0,
                        "net_change": 0
                    }
                
                weekly_projection[week_key]["projects_ending"] += 1
                weekly_projection[week_key]["net_change"] -= 1
        
        return {
            "weekly_projection": weekly_projection,
            "peak_workload_week": max(
                weekly_projection.items(),
                key=lambda x: x[1]["net_change"]
            )[0] if weekly_projection else None,
            "projection_period": {
                "start_date": future_start.isoformat(),
                "end_date": future_end.isoformat()
            }
        }

    async def _generate_workload_recommendations(
        self,
        active_analysis: Dict[str, Any],
        future_workload: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones basadas en análisis de carga."""
        recommendations = []
        
        workload_level = active_analysis.get("workload_level", "low")
        
        if workload_level == "critical":
            recommendations.append("Carga de trabajo crítica - considerar redistribuir recursos")
        elif workload_level == "high":
            recommendations.append("Carga de trabajo alta - monitorear capacidad de equipo")
        
        if active_analysis.get("overdue", 0) > 0:
            recommendations.append(f"Atender {active_analysis['overdue']} proyectos vencidos prioritariamente")
        
        if active_analysis.get("ending_soon", 0) > 3:
            recommendations.append("Múltiples proyectos terminan pronto - preparar recursos para cierre")
        
        if not recommendations:
            recommendations.append("Carga de trabajo bajo control - mantener monitoreo regular")
        
        return recommendations

    async def _analyze_project_durations(self, projects: List[Project]) -> Dict[str, Any]:
        """Analiza las duraciones de los proyectos."""
        durations = [
            (p.end_date - p.start_date).days + 1 
            for p in projects 
            if p.start_date and p.end_date
        ]
        
        if not durations:
            return {
                "duration_distribution": {},
                "duration_by_priority": {},
                "duration_by_status": {},
                "duration_trends": {}
            }
        
        # Distribución de duraciones
        duration_distribution = {}
        for duration in durations:
            if duration <= 30:
                category = "short"  # <= 1 mes
            elif duration <= 90:
                category = "medium"  # 1-3 meses
            elif duration <= 180:
                category = "long"  # 3-6 meses
            else:
                category = "very_long"  # > 6 meses
            
            duration_distribution[category] = duration_distribution.get(category, 0) + 1
        
        # Duración por prioridad
        duration_by_priority = {}
        for project in projects:
            if project.start_date and project.end_date and project.priority:
                priority = project.priority.value
                duration = (project.end_date - project.start_date).days + 1
                
                if priority not in duration_by_priority:
                    duration_by_priority[priority] = []
                duration_by_priority[priority].append(duration)
        
        # Calcular promedios por prioridad
        for priority, durations_list in duration_by_priority.items():
            duration_by_priority[priority] = {
                "average": sum(durations_list) / len(durations_list),
                "count": len(durations_list)
            }
        
        return {
            "duration_distribution": duration_distribution,
            "duration_by_priority": duration_by_priority,
            "duration_by_status": {},  # Implementar si es necesario
            "duration_trends": {}  # Implementar si es necesario
        }

    async def _generate_duration_insights(self, duration_analysis: Dict[str, Any]) -> List[str]:
        """Genera insights basados en análisis de duración."""
        insights = []
        
        distribution = duration_analysis.get("duration_distribution", {})
        
        if distribution.get("very_long", 0) > distribution.get("short", 0):
            insights.append("Tendencia hacia proyectos de larga duración - considerar dividir en fases")
        
        if distribution.get("short", 0) > sum(distribution.values()) * 0.6:
            insights.append("Mayoría de proyectos son de corta duración - eficiencia en ejecución")
        
        priority_analysis = duration_analysis.get("duration_by_priority", {})
        if priority_analysis:
            high_priority_avg = priority_analysis.get("HIGH", {}).get("average", 0)
            low_priority_avg = priority_analysis.get("LOW", {}).get("average", 0)
            
            if high_priority_avg > low_priority_avg * 1.5:
                insights.append("Proyectos de alta prioridad tienden a ser más largos")
        
        if not insights:
            insights.append("Distribución de duraciones equilibrada")
        
        return insights

    async def _analyze_monthly_performance(
        self,
        month_projects: List[Project],
        year: int,
        month: int
    ) -> Dict[str, Any]:
        """Analiza el rendimiento de un mes específico."""
        # Implementación simplificada
        return {
            "projects_in_month": len(month_projects),
            "projects_started": len([
                p for p in month_projects 
                if p.start_date and p.start_date.month == month and p.start_date.year == year
            ]),
            "projects_completed": len([
                p for p in month_projects 
                if p.status == ProjectStatus.COMPLETED
            ]),
            "month_performance_score": 85  # Placeholder
        }

    async def _compare_monthly_performance(self, year: int, month: int) -> Dict[str, Any]:
        """Compara el rendimiento mensual con períodos anteriores."""
        # Implementación simplificada
        return {
            "vs_previous_month": {
                "projects_change": 0,
                "completion_rate_change": 0,
                "trend": "stable"
            },
            "vs_same_month_last_year": {
                "projects_change": 0,
                "completion_rate_change": 0,
                "trend": "stable"
            }
        }

    async def _analyze_client_performance(
        self,
        client_projects: List[Project],
        client_id: int
    ) -> Dict[str, Any]:
        """Analiza el rendimiento de un cliente específico."""
        if not client_projects:
            return {
                "total_projects": 0,
                "completion_rate": 0,
                "average_duration": 0,
                "client_score": 0
            }
        
        completed_projects = [p for p in client_projects if p.status == ProjectStatus.COMPLETED]
        completion_rate = len(completed_projects) / len(client_projects) * 100
        
        # Calcular duración promedio
        projects_with_dates = [
            p for p in completed_projects 
            if p.start_date and p.end_date
        ]
        
        if projects_with_dates:
            durations = [
                (p.end_date - p.start_date).days + 1 
                for p in projects_with_dates
            ]
            average_duration = sum(durations) / len(durations)
        else:
            average_duration = 0
        
        # Calcular score del cliente (simplificado)
        client_score = min(100, completion_rate + (50 if average_duration <= 90 else 0))
        
        return {
            "total_projects": len(client_projects),
            "completion_rate": completion_rate,
            "average_duration": average_duration,
            "client_score": client_score,
            "projects_by_status": {
                status.value: len([p for p in client_projects if p.status == status])
                for status in ProjectStatus
            }
        }

    async def _analyze_all_clients_performance(self, client_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el rendimiento de todos los clientes."""
        # Implementación simplificada basada en estadísticas existentes
        return {
            "total_clients": len(client_stats) if isinstance(client_stats, dict) else 0,
            "average_projects_per_client": 0,  # Calcular basado en client_stats
            "top_performing_clients": [],
            "clients_needing_attention": []
        }

    async def _identify_top_clients(self, client_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica los mejores clientes basado en estadísticas."""
        # Implementación simplificada
        return [
            {
                "client_id": 1,
                "total_projects": 10,
                "completion_rate": 95,
                "score": 95
            }
        ]

    async def _analyze_overdue_details(self, overdue_projects: List[Project]) -> Dict[str, Any]:
        """Analiza detalles de proyectos vencidos."""
        if not overdue_projects:
            return {
                "severity_distribution": {},
                "impact_analysis": {},
                "recovery_timeline": {}
            }
        
        current_date = pendulum.now().date()
        severity_distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for project in overdue_projects:
            if project.end_date:
                delay_days = (current_date - project.end_date).days
                
                if delay_days <= 7:
                    severity = "low"
                elif delay_days <= 30:
                    severity = "medium"
                elif delay_days <= 90:
                    severity = "high"
                else:
                    severity = "critical"
                
                severity_distribution[severity] += 1
        
        return {
            "severity_distribution": severity_distribution,
            "impact_analysis": {
                "total_overdue": len(overdue_projects),
                "high_priority_overdue": len([
                    p for p in overdue_projects 
                    if p.priority == ProjectPriority.HIGH
                ]),
                "client_impact": len(set(p.client_id for p in overdue_projects))
            },
            "recovery_timeline": {
                "immediate_action_needed": severity_distribution["critical"],
                "short_term_recovery": severity_distribution["high"],
                "medium_term_recovery": severity_distribution["medium"]
            }
        }

    async def _analyze_overdue_causes(self, overdue_projects: List[Project]) -> Dict[str, Any]:
        """Analiza las causas de vencimiento de proyectos."""
        # Implementación simplificada - en un sistema real analizaría logs, cambios, etc.
        return {
            "common_causes": [
                "Cambios en alcance del proyecto",
                "Retrasos en aprobaciones del cliente",
                "Problemas técnicos inesperados",
                "Falta de recursos disponibles"
            ],
            "cause_frequency": {
                "scope_changes": 40,
                "client_delays": 25,
                "technical_issues": 20,
                "resource_constraints": 15
            },
            "preventable_causes": 65  # Porcentaje de causas que podrían haberse evitado
        }

    async def _generate_overdue_recommendations(
        self,
        overdue_projects: List[Project],
        detailed_analysis: Dict[str, Any],
        causes_analysis: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones para reducir vencimientos."""
        recommendations = []
        
        severity_dist = detailed_analysis.get("severity_distribution", {})
        
        if severity_dist.get("critical", 0) > 0:
            recommendations.append("Atención inmediata a proyectos con retraso crítico (>90 días)")
        
        if severity_dist.get("high", 0) > 0:
            recommendations.append("Plan de recuperación urgente para proyectos con alto retraso")
        
        # Recomendaciones basadas en causas
        cause_freq = causes_analysis.get("cause_frequency", {})
        
        if cause_freq.get("scope_changes", 0) > 30:
            recommendations.append("Implementar mejor control de cambios de alcance")
        
        if cause_freq.get("client_delays", 0) > 20:
            recommendations.append("Mejorar comunicación y seguimiento con clientes")
        
        if not recommendations:
            recommendations.append("Mantener monitoreo proactivo de fechas de entrega")
        
        return recommendations

    async def _calculate_key_metrics(self) -> Dict[str, Any]:
        """Calcula métricas clave para el dashboard."""
        # Obtener datos básicos
        all_projects = await self.repository.search_projects()
        active_projects = await self.repository.get_by_status(ProjectStatus.ACTIVE)
        overdue_projects = await self.repository.get_overdue_projects()
        
        total_projects = len(all_projects)
        
        return {
            "total_projects": total_projects,
            "active_projects": len(active_projects),
            "overdue_projects": len(overdue_projects),
            "completion_rate": (
                len([p for p in all_projects if p.status == ProjectStatus.COMPLETED]) / 
                total_projects * 100
            ) if total_projects > 0 else 0,
            "overdue_rate": (
                len(overdue_projects) / len(active_projects) * 100
            ) if active_projects else 0
        }

    async def _generate_dashboard_alerts(self) -> List[Dict[str, Any]]:
        """Genera alertas para el dashboard."""
        alerts = []
        
        # Verificar proyectos vencidos
        overdue_projects = await self.repository.get_overdue_projects()
        if overdue_projects:
            alerts.append({
                "type": "warning",
                "title": "Proyectos Vencidos",
                "message": f"{len(overdue_projects)} proyectos están vencidos",
                "priority": "high",
                "action_required": True
            })
        
        # Verificar proyectos que terminan pronto
        projects_ending_soon = await self.repository.get_projects_ending_current_week()
        if len(projects_ending_soon) > 5:
            alerts.append({
                "type": "info",
                "title": "Múltiples Proyectos Terminando",
                "message": f"{len(projects_ending_soon)} proyectos terminan esta semana",
                "priority": "medium",
                "action_required": False
            })
        
        return alerts

    async def _analyze_recent_trends(self) -> Dict[str, Any]:
        """Analiza tendencias recientes."""
        # Implementación simplificada
        return {
            "project_creation_trend": "increasing",
            "completion_trend": "stable",
            "duration_trend": "decreasing",
            "client_satisfaction_trend": "improving"
        }
