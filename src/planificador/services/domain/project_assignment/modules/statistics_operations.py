# src/planificador/services/domain/project_assignment/modules/statistics_operations.py

"""
Módulo de Operaciones Estadísticas para Asignaciones de Proyecto

Implementa análisis estadísticos avanzados, métricas de rendimiento,
tendencias temporales y análisis predictivos para asignaciones
de proyecto y recursos.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, timedelta
from collections import defaultdict, Counter
import statistics
from loguru import logger

from planificador.schemas import ProjectAssignment
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.exceptions import RepositoryError, ValidationError
from ..interfaces import IStatisticsOperations


class StatisticsOperations(IStatisticsOperations):
    """
    Implementación de operaciones estadísticas avanzadas.
    
    Proporciona análisis estadísticos completos, métricas de rendimiento,
    análisis de tendencias temporales y capacidades predictivas para
    la gestión de asignaciones de proyecto.
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """
        Inicializa el módulo de operaciones estadísticas.
        
        Args:
            repository_facade: Facade del repositorio de asignaciones
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="project_assignment_statistics")
    
    async def get_assignment_count_by_status(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> Dict[str, int]:
        """
        Obtiene el conteo de asignaciones agrupadas por estado.
        
        Args:
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
            
        Returns:
            Dict[str, int]: Conteo de asignaciones por estado
            
        Raises:
            ValidationError: Si las fechas no son válidas
            RepositoryError: Si hay errores en la consulta
        """
        try:
            self._logger.info(
                f"Obteniendo conteo de asignaciones por estado "
                f"desde {start_date} hasta {end_date}"
            )
            
            # Validar fechas si se proporcionan
            if start_date and end_date and start_date > end_date:
                raise ValidationError(
                    message="La fecha de inicio debe ser anterior a la fecha de fin",
                    field="date_range",
                    value=f"{start_date} - {end_date}"
                )
            
            # Obtener todas las asignaciones
            all_assignments = await self._repository.queries.get_all_assignments()
            
            # Filtrar por fechas si se especifican
            filtered_assignments = self._filter_assignments_by_date_range(
                all_assignments, start_date, end_date
            )
            
            # Contar por estado
            status_counts = Counter()
            for assignment in filtered_assignments:
                # Determinar estado basado en fechas
                status = self._determine_assignment_status(assignment)
                status_counts[status] += 1
            
            # Asegurar que todos los estados estén representados
            all_statuses = ["active", "completed", "upcoming", "cancelled"]
            result = {status: status_counts.get(status, 0) for status in all_statuses}
            
            self._logger.info(
                f"Conteo completado: {sum(result.values())} asignaciones totales"
            )
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener conteo por estado: {e}")
            raise RepositoryError(
                message=f"Error al obtener conteo por estado: {e}",
                operation="get_assignment_count_by_status",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def get_assignment_distribution_by_role(
        self, 
        project_id: Optional[int] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene la distribución de asignaciones por rol.
        
        Args:
            project_id: ID del proyecto específico (opcional)
            
        Returns:
            Dict[str, Dict[str, Any]]: Distribución detallada por rol
            
        Raises:
            ValidationError: Si el project_id no es válido
            RepositoryError: Si hay errores en la consulta
        """
        try:
            self._logger.info(
                f"Obteniendo distribución por rol "
                f"{'para proyecto ' + str(project_id) if project_id else 'global'}"
            )
            
            # Validar project_id si se proporciona
            if project_id is not None and project_id <= 0:
                raise ValidationError(
                    message="El ID del proyecto debe ser un número positivo",
                    field="project_id",
                    value=project_id
                )
            
            # Obtener asignaciones
            if project_id:
                assignments = await self._repository.queries.get_assignments_by_project(
                    project_id=project_id,
                    include_inactive=True
                )
            else:
                assignments = await self._repository.queries.get_all_assignments()
            
            # Agrupar por rol
            role_data = defaultdict(lambda: {
                "count": 0,
                "total_percentage": 0,
                "total_hours": 0,
                "employees": set(),
                "projects": set(),
                "assignments": []
            })
            
            for assignment in assignments:
                role = assignment.role_in_project
                role_data[role]["count"] += 1
                role_data[role]["total_percentage"] += assignment.percentage_allocation
                role_data[role]["total_hours"] += assignment.allocated_hours_per_day
                role_data[role]["employees"].add(assignment.employee_id)
                role_data[role]["projects"].add(assignment.project_id)
                role_data[role]["assignments"].append(assignment)
            
            # Calcular estadísticas por rol
            result = {}
            total_assignments = len(assignments)
            
            for role, data in role_data.items():
                assignments_for_role = data["assignments"]
                percentages = [a.percentage_allocation for a in assignments_for_role]
                hours = [a.allocated_hours_per_day for a in assignments_for_role]
                
                result[role] = {
                    "assignment_count": data["count"],
                    "percentage_of_total": round(
                        (data["count"] / total_assignments * 100) if total_assignments > 0 else 0, 2
                    ),
                    "unique_employees": len(data["employees"]),
                    "unique_projects": len(data["projects"]),
                    "allocation_stats": {
                        "total_percentage": data["total_percentage"],
                        "average_percentage": round(
                            statistics.mean(percentages) if percentages else 0, 2
                        ),
                        "median_percentage": round(
                            statistics.median(percentages) if percentages else 0, 2
                        ),
                        "min_percentage": min(percentages) if percentages else 0,
                        "max_percentage": max(percentages) if percentages else 0
                    },
                    "hours_stats": {
                        "total_hours": data["total_hours"],
                        "average_hours": round(
                            statistics.mean(hours) if hours else 0, 2
                        ),
                        "median_hours": round(
                            statistics.median(hours) if hours else 0, 2
                        ),
                        "min_hours": min(hours) if hours else 0,
                        "max_hours": max(hours) if hours else 0
                    },
                    "utilization_efficiency": self._calculate_role_efficiency(assignments_for_role)
                }
            
            self._logger.info(
                f"Distribución por rol completada: {len(result)} roles analizados"
            )
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener distribución por rol: {e}")
            raise RepositoryError(
                message=f"Error al obtener distribución por rol: {e}",
                operation="get_assignment_distribution_by_role",
                entity_type="ProjectAssignment",
                entity_id=project_id,
                original_error=e
            )
    
    async def get_average_allocation_metrics(
        self, 
        group_by: str = "employee"
    ) -> Dict[str, Any]:
        """
        Calcula métricas promedio de asignación.
        
        Args:
            group_by: Criterio de agrupación ("employee", "project", "role")
            
        Returns:
            Dict[str, Any]: Métricas promedio detalladas
            
        Raises:
            ValidationError: Si el criterio de agrupación no es válido
            RepositoryError: Si hay errores en el cálculo
        """
        try:
            self._logger.info(f"Calculando métricas promedio agrupadas por {group_by}")
            
            # Validar criterio de agrupación
            valid_group_by = ["employee", "project", "role"]
            if group_by not in valid_group_by:
                raise ValidationError(
                    message=f"Criterio de agrupación inválido. Debe ser uno de: {valid_group_by}",
                    field="group_by",
                    value=group_by
                )
            
            # Obtener todas las asignaciones activas
            assignments = await self._repository.queries.get_all_assignments()
            active_assignments = [
                a for a in assignments 
                if self._determine_assignment_status(a) == "active"
            ]
            
            if not active_assignments:
                return {
                    "group_by": group_by,
                    "total_groups": 0,
                    "total_assignments": 0,
                    "overall_metrics": {},
                    "group_metrics": {}
                }
            
            # Agrupar según criterio
            groups = self._group_assignments(active_assignments, group_by)
            
            # Calcular métricas por grupo
            group_metrics = {}
            all_percentages = []
            all_hours = []
            
            for group_key, group_assignments in groups.items():
                percentages = [a.percentage_allocation for a in group_assignments]
                hours = [a.allocated_hours_per_day for a in group_assignments]
                
                all_percentages.extend(percentages)
                all_hours.extend(hours)
                
                group_metrics[str(group_key)] = {
                    "assignment_count": len(group_assignments),
                    "percentage_allocation": {
                        "mean": round(statistics.mean(percentages), 2),
                        "median": round(statistics.median(percentages), 2),
                        "std_dev": round(statistics.stdev(percentages) if len(percentages) > 1 else 0, 2),
                        "min": min(percentages),
                        "max": max(percentages),
                        "total": sum(percentages)
                    },
                    "hours_allocation": {
                        "mean": round(statistics.mean(hours), 2),
                        "median": round(statistics.median(hours), 2),
                        "std_dev": round(statistics.stdev(hours) if len(hours) > 1 else 0, 2),
                        "min": min(hours),
                        "max": max(hours),
                        "total": sum(hours)
                    },
                    "efficiency_score": self._calculate_group_efficiency(group_assignments)
                }
            
            # Calcular métricas generales
            overall_metrics = {
                "percentage_allocation": {
                    "mean": round(statistics.mean(all_percentages), 2),
                    "median": round(statistics.median(all_percentages), 2),
                    "std_dev": round(statistics.stdev(all_percentages) if len(all_percentages) > 1 else 0, 2),
                    "min": min(all_percentages),
                    "max": max(all_percentages),
                    "total": sum(all_percentages)
                },
                "hours_allocation": {
                    "mean": round(statistics.mean(all_hours), 2),
                    "median": round(statistics.median(all_hours), 2),
                    "std_dev": round(statistics.stdev(all_hours) if len(all_hours) > 1 else 0, 2),
                    "min": min(all_hours),
                    "max": max(all_hours),
                    "total": sum(all_hours)
                },
                "distribution_analysis": self._analyze_allocation_distribution(all_percentages),
                "utilization_categories": self._categorize_utilization(all_percentages)
            }
            
            result = {
                "group_by": group_by,
                "total_groups": len(groups),
                "total_assignments": len(active_assignments),
                "overall_metrics": overall_metrics,
                "group_metrics": group_metrics,
                "top_performers": self._identify_top_performers(group_metrics, group_by),
                "improvement_opportunities": self._identify_improvement_opportunities(group_metrics)
            }
            
            self._logger.info(
                f"Métricas promedio calculadas: {len(groups)} grupos analizados"
            )
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al calcular métricas promedio: {e}")
            raise RepositoryError(
                message=f"Error al calcular métricas promedio: {e}",
                operation="get_average_allocation_metrics",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def get_assignment_duration_statistics(
        self, 
        include_projected: bool = True
    ) -> Dict[str, Any]:
        """
        Calcula estadísticas de duración de asignaciones.
        
        Args:
            include_projected: Si incluir asignaciones futuras en el análisis
            
        Returns:
            Dict[str, Any]: Estadísticas detalladas de duración
            
        Raises:
            RepositoryError: Si hay errores en el cálculo
        """
        try:
            self._logger.info(
                f"Calculando estadísticas de duración "
                f"{'incluyendo proyecciones' if include_projected else 'solo históricas'}"
            )
            
            # Obtener todas las asignaciones
            assignments = await self._repository.queries.get_all_assignments()
            
            # Filtrar según criterio
            if not include_projected:
                today = date.today()
                assignments = [a for a in assignments if a.end_date <= today]
            
            if not assignments:
                return {
                    "total_assignments": 0,
                    "duration_statistics": {},
                    "duration_categories": {},
                    "temporal_analysis": {}
                }
            
            # Calcular duraciones en días
            durations = []
            duration_by_role = defaultdict(list)
            duration_by_project = defaultdict(list)
            duration_by_month = defaultdict(list)
            
            for assignment in assignments:
                duration_days = (assignment.end_date - assignment.start_date).days + 1
                durations.append(duration_days)
                
                duration_by_role[assignment.role_in_project].append(duration_days)
                duration_by_project[assignment.project_id].append(duration_days)
                
                # Agrupar por mes de inicio
                month_key = assignment.start_date.strftime("%Y-%m")
                duration_by_month[month_key].append(duration_days)
            
            # Estadísticas generales de duración
            duration_stats = {
                "mean_days": round(statistics.mean(durations), 2),
                "median_days": round(statistics.median(durations), 2),
                "std_dev_days": round(statistics.stdev(durations) if len(durations) > 1 else 0, 2),
                "min_days": min(durations),
                "max_days": max(durations),
                "total_person_days": sum(durations),
                "percentiles": {
                    "p25": round(statistics.quantiles(durations, n=4)[0], 2) if len(durations) >= 4 else 0,
                    "p75": round(statistics.quantiles(durations, n=4)[2], 2) if len(durations) >= 4 else 0,
                    "p90": round(statistics.quantiles(durations, n=10)[8], 2) if len(durations) >= 10 else 0
                }
            }
            
            # Categorizar duraciones
            duration_categories = self._categorize_durations(durations)
            
            # Análisis por rol
            role_analysis = {}
            for role, role_durations in duration_by_role.items():
                if role_durations:
                    role_analysis[role] = {
                        "count": len(role_durations),
                        "mean_days": round(statistics.mean(role_durations), 2),
                        "median_days": round(statistics.median(role_durations), 2),
                        "min_days": min(role_durations),
                        "max_days": max(role_durations)
                    }
            
            # Análisis temporal
            temporal_analysis = self._analyze_duration_trends(duration_by_month)
            
            # Análisis de eficiencia
            efficiency_analysis = self._analyze_duration_efficiency(assignments, durations)
            
            result = {
                "total_assignments": len(assignments),
                "analysis_period": {
                    "include_projected": include_projected,
                    "earliest_start": min(a.start_date for a in assignments),
                    "latest_end": max(a.end_date for a in assignments)
                },
                "duration_statistics": duration_stats,
                "duration_categories": duration_categories,
                "role_analysis": role_analysis,
                "temporal_analysis": temporal_analysis,
                "efficiency_analysis": efficiency_analysis,
                "insights": self._generate_duration_insights(duration_stats, duration_categories, role_analysis)
            }
            
            self._logger.info(
                f"Estadísticas de duración calculadas: "
                f"promedio {duration_stats['mean_days']} días"
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al calcular estadísticas de duración: {e}")
            raise RepositoryError(
                message=f"Error al calcular estadísticas de duración: {e}",
                operation="get_assignment_duration_statistics",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def analyze_assignment_trends(
        self, 
        period_months: int = 12
    ) -> Dict[str, Any]:
        """
        Analiza tendencias temporales de asignaciones.
        
        Args:
            period_months: Número de meses hacia atrás para el análisis
            
        Returns:
            Dict[str, Any]: Análisis completo de tendencias
            
        Raises:
            ValidationError: Si el período no es válido
            RepositoryError: Si hay errores en el análisis
        """
        try:
            self._logger.info(f"Analizando tendencias de los últimos {period_months} meses")
            
            # Validar período
            if period_months <= 0 or period_months > 60:
                raise ValidationError(
                    message="El período debe estar entre 1 y 60 meses",
                    field="period_months",
                    value=period_months
                )
            
            # Calcular rango de fechas
            end_date = date.today()
            start_date = end_date.replace(day=1) - timedelta(days=period_months * 30)
            
            # Obtener asignaciones del período
            assignments = await self._repository.queries.get_all_assignments()
            period_assignments = [
                a for a in assignments
                if a.start_date >= start_date or a.end_date >= start_date
            ]
            
            if not period_assignments:
                return {
                    "analysis_period": {"start_date": start_date, "end_date": end_date},
                    "total_assignments": 0,
                    "trends": {}
                }
            
            # Análisis de tendencias por mes
            monthly_trends = self._analyze_monthly_trends(period_assignments, start_date, end_date)
            
            # Análisis de tendencias por rol
            role_trends = self._analyze_role_trends(period_assignments, start_date, end_date)
            
            # Análisis de carga de trabajo
            workload_trends = self._analyze_workload_trends(period_assignments, start_date, end_date)
            
            # Análisis de proyectos
            project_trends = self._analyze_project_trends(period_assignments, start_date, end_date)
            
            # Detección de patrones estacionales
            seasonal_patterns = self._detect_seasonal_patterns(monthly_trends)
            
            # Predicciones básicas
            predictions = self._generate_trend_predictions(monthly_trends, role_trends)
            
            result = {
                "analysis_period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "period_months": period_months
                },
                "total_assignments": len(period_assignments),
                "monthly_trends": monthly_trends,
                "role_trends": role_trends,
                "workload_trends": workload_trends,
                "project_trends": project_trends,
                "seasonal_patterns": seasonal_patterns,
                "predictions": predictions,
                "trend_summary": self._summarize_trends(monthly_trends, role_trends, workload_trends)
            }
            
            self._logger.info(
                f"Análisis de tendencias completado: "
                f"{len(monthly_trends)} meses analizados"
            )
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al analizar tendencias: {e}")
            raise RepositoryError(
                message=f"Error al analizar tendencias: {e}",
                operation="analyze_assignment_trends",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def calculate_resource_utilization_metrics(
        self, 
        analysis_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calcula métricas de utilización de recursos.
        
        Args:
            analysis_date: Fecha específica para el análisis (por defecto hoy)
            
        Returns:
            Dict[str, Any]: Métricas detalladas de utilización
            
        Raises:
            RepositoryError: Si hay errores en el cálculo
        """
        try:
            if analysis_date is None:
                analysis_date = date.today()
            
            self._logger.info(f"Calculando métricas de utilización para {analysis_date}")
            
            # Obtener asignaciones activas en la fecha
            assignments = await self._repository.queries.get_all_assignments()
            active_assignments = [
                a for a in assignments
                if a.start_date <= analysis_date <= a.end_date
            ]
            
            if not active_assignments:
                return {
                    "analysis_date": analysis_date,
                    "total_active_assignments": 0,
                    "utilization_metrics": {}
                }
            
            # Calcular utilización por empleado
            employee_utilization = self._calculate_employee_utilization(active_assignments)
            
            # Calcular utilización por proyecto
            project_utilization = self._calculate_project_utilization(active_assignments)
            
            # Calcular utilización por rol
            role_utilization = self._calculate_role_utilization(active_assignments)
            
            # Métricas agregadas
            aggregate_metrics = self._calculate_aggregate_utilization_metrics(
                employee_utilization, project_utilization, role_utilization
            )
            
            # Análisis de capacidad
            capacity_analysis = self._analyze_capacity_utilization(employee_utilization)
            
            # Identificar cuellos de botella
            bottlenecks = self._identify_resource_bottlenecks(
                employee_utilization, project_utilization, role_utilization
            )
            
            # Oportunidades de optimización
            optimization_opportunities = self._identify_utilization_opportunities(
                employee_utilization, capacity_analysis
            )
            
            result = {
                "analysis_date": analysis_date,
                "total_active_assignments": len(active_assignments),
                "employee_utilization": employee_utilization,
                "project_utilization": project_utilization,
                "role_utilization": role_utilization,
                "aggregate_metrics": aggregate_metrics,
                "capacity_analysis": capacity_analysis,
                "bottlenecks": bottlenecks,
                "optimization_opportunities": optimization_opportunities,
                "utilization_score": self._calculate_overall_utilization_score(aggregate_metrics)
            }
            
            self._logger.info(
                f"Métricas de utilización calculadas: "
                f"puntuación general {result['utilization_score']}"
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al calcular métricas de utilización: {e}")
            raise RepositoryError(
                message=f"Error al calcular métricas de utilización: {e}",
                operation="calculate_resource_utilization_metrics",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def get_project_performance_metrics(
        self, 
        project_id: int
    ) -> Dict[str, Any]:
        """
        Calcula métricas de rendimiento para un proyecto específico.
        
        Args:
            project_id: ID del proyecto a analizar
            
        Returns:
            Dict[str, Any]: Métricas completas de rendimiento del proyecto
            
        Raises:
            ValidationError: Si el project_id no es válido
            RepositoryError: Si hay errores en el cálculo
        """
        try:
            self._logger.info(f"Calculando métricas de rendimiento para proyecto {project_id}")
            
            # Validar project_id
            if project_id <= 0:
                raise ValidationError(
                    message="El ID del proyecto debe ser un número positivo",
                    field="project_id",
                    value=project_id
                )
            
            # Obtener asignaciones del proyecto
            project_assignments = await self._repository.queries.get_assignments_by_project(
                project_id=project_id,
                include_inactive=True
            )
            
            if not project_assignments:
                return {
                    "project_id": project_id,
                    "total_assignments": 0,
                    "performance_metrics": {},
                    "message": "No se encontraron asignaciones para este proyecto"
                }
            
            # Métricas básicas del proyecto
            basic_metrics = self._calculate_basic_project_metrics(project_assignments)
            
            # Métricas de equipo
            team_metrics = self._calculate_team_performance_metrics(project_assignments)
            
            # Métricas de tiempo
            time_metrics = self._calculate_time_performance_metrics(project_assignments)
            
            # Métricas de recursos
            resource_metrics = self._calculate_resource_performance_metrics(project_assignments)
            
            # Análisis de eficiencia
            efficiency_analysis = self._analyze_project_efficiency(project_assignments)
            
            # Análisis de riesgos
            risk_analysis = self._analyze_project_risks(project_assignments)
            
            # Comparación con benchmarks
            benchmark_comparison = await self._compare_with_benchmarks(
                project_id, basic_metrics, team_metrics, time_metrics
            )
            
            # Puntuación general de rendimiento
            performance_score = self._calculate_project_performance_score(
                basic_metrics, team_metrics, time_metrics, resource_metrics, efficiency_analysis
            )
            
            result = {
                "project_id": project_id,
                "total_assignments": len(project_assignments),
                "analysis_date": date.today(),
                "basic_metrics": basic_metrics,
                "team_metrics": team_metrics,
                "time_metrics": time_metrics,
                "resource_metrics": resource_metrics,
                "efficiency_analysis": efficiency_analysis,
                "risk_analysis": risk_analysis,
                "benchmark_comparison": benchmark_comparison,
                "performance_score": performance_score,
                "recommendations": self._generate_performance_recommendations(
                    performance_score, efficiency_analysis, risk_analysis
                )
            }
            
            self._logger.info(
                f"Métricas de rendimiento calculadas para proyecto {project_id}: "
                f"puntuación {performance_score['overall_score']}"
            )
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(
                f"Error al calcular métricas de rendimiento para proyecto {project_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error al calcular métricas de rendimiento: {e}",
                operation="get_project_performance_metrics",
                entity_type="ProjectAssignment",
                entity_id=project_id,
                original_error=e
            )
    
    async def generate_predictive_insights(
        self, 
        prediction_horizon_days: int = 90
    ) -> Dict[str, Any]:
        """
        Genera insights predictivos basados en datos históricos.
        
        Args:
            prediction_horizon_days: Días hacia el futuro para predicciones
            
        Returns:
            Dict[str, Any]: Insights y predicciones detalladas
            
        Raises:
            ValidationError: Si el horizonte de predicción no es válido
            RepositoryError: Si hay errores en el análisis predictivo
        """
        try:
            self._logger.info(
                f"Generando insights predictivos para los próximos {prediction_horizon_days} días"
            )
            
            # Validar horizonte de predicción
            if prediction_horizon_days <= 0 or prediction_horizon_days > 365:
                raise ValidationError(
                    message="El horizonte de predicción debe estar entre 1 y 365 días",
                    field="prediction_horizon_days",
                    value=prediction_horizon_days
                )
            
            # Obtener datos históricos
            assignments = await self._repository.queries.get_all_assignments()
            
            if len(assignments) < 10:  # Mínimo de datos para predicciones
                return {
                    "prediction_horizon_days": prediction_horizon_days,
                    "data_sufficiency": "insufficient",
                    "message": "Datos insuficientes para generar predicciones confiables",
                    "minimum_required": 10,
                    "current_count": len(assignments)
                }
            
            # Análisis de patrones históricos
            historical_patterns = self._analyze_historical_patterns(assignments)
            
            # Predicciones de carga de trabajo
            workload_predictions = self._predict_workload_trends(
                assignments, prediction_horizon_days
            )
            
            # Predicciones de demanda por rol
            role_demand_predictions = self._predict_role_demand(
                assignments, prediction_horizon_days
            )
            
            # Predicciones de capacidad
            capacity_predictions = self._predict_capacity_needs(
                assignments, prediction_horizon_days
            )
            
            # Identificación de riesgos futuros
            risk_predictions = self._predict_future_risks(
                assignments, prediction_horizon_days
            )
            
            # Oportunidades de optimización
            optimization_opportunities = self._identify_future_opportunities(
                workload_predictions, role_demand_predictions, capacity_predictions
            )
            
            # Recomendaciones estratégicas
            strategic_recommendations = self._generate_strategic_recommendations(
                historical_patterns, workload_predictions, risk_predictions
            )
            
            # Métricas de confianza
            confidence_metrics = self._calculate_prediction_confidence(
                assignments, historical_patterns
            )
            
            result = {
                "prediction_horizon_days": prediction_horizon_days,
                "analysis_date": date.today(),
                "prediction_period": {
                    "start_date": date.today(),
                    "end_date": date.today() + timedelta(days=prediction_horizon_days)
                },
                "data_sufficiency": "sufficient",
                "historical_data_points": len(assignments),
                "historical_patterns": historical_patterns,
                "workload_predictions": workload_predictions,
                "role_demand_predictions": role_demand_predictions,
                "capacity_predictions": capacity_predictions,
                "risk_predictions": risk_predictions,
                "optimization_opportunities": optimization_opportunities,
                "strategic_recommendations": strategic_recommendations,
                "confidence_metrics": confidence_metrics,
                "prediction_accuracy_disclaimer": "Las predicciones se basan en patrones históricos y pueden variar según factores externos"
            }
            
            self._logger.info(
                f"Insights predictivos generados con confianza del "
                f"{confidence_metrics['overall_confidence']}%"
            )
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al generar insights predictivos: {e}")
            raise RepositoryError(
                message=f"Error al generar insights predictivos: {e}",
                operation="generate_predictive_insights",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE UTILIDAD
    # ============================================================================
    
    def _filter_assignments_by_date_range(
        self, 
        assignments: List[ProjectAssignment], 
        start_date: Optional[date], 
        end_date: Optional[date]
    ) -> List[ProjectAssignment]:
        """Filtra asignaciones por rango de fechas."""
        if not start_date and not end_date:
            return assignments
        
        filtered = []
        for assignment in assignments:
            # Verificar si la asignación se superpone con el rango
            if start_date and assignment.end_date < start_date:
                continue
            if end_date and assignment.start_date > end_date:
                continue
            filtered.append(assignment)
        
        return filtered
    
    def _determine_assignment_status(self, assignment: ProjectAssignment) -> str:
        """Determina el estado de una asignación basado en fechas."""
        today = date.today()
        
        if assignment.start_date > today:
            return "upcoming"
        elif assignment.end_date < today:
            return "completed"
        else:
            return "active"
    
    def _calculate_role_efficiency(self, assignments: List[ProjectAssignment]) -> float:
        """Calcula la eficiencia de un rol basada en sus asignaciones."""
        if not assignments:
            return 0
        
        # Simplificación: eficiencia basada en utilización promedio
        avg_percentage = statistics.mean(a.percentage_allocation for a in assignments)
        
        # Penalizar sobreasignación y subutilización
        if avg_percentage > 100:
            efficiency = max(0, 100 - (avg_percentage - 100))
        elif avg_percentage < 50:
            efficiency = avg_percentage * 1.5  # Bonificar utilización parcial
        else:
            efficiency = 100
        
        return round(min(100, efficiency), 2)
    
    def _group_assignments(
        self, 
        assignments: List[ProjectAssignment], 
        group_by: str
    ) -> Dict[Any, List[ProjectAssignment]]:
        """Agrupa asignaciones según el criterio especificado."""
        groups = defaultdict(list)
        
        for assignment in assignments:
            if group_by == "employee":
                key = assignment.employee_id
            elif group_by == "project":
                key = assignment.project_id
            elif group_by == "role":
                key = assignment.role_in_project
            else:
                key = "unknown"
            
            groups[key].append(assignment)
        
        return dict(groups)
    
    def _calculate_group_efficiency(self, assignments: List[ProjectAssignment]) -> float:
        """Calcula la eficiencia de un grupo de asignaciones."""
        if not assignments:
            return 0
        
        percentages = [a.percentage_allocation for a in assignments]
        total_percentage = sum(percentages)
        
        # Eficiencia basada en utilización y balance
        if len(assignments) == 1:
            # Un solo assignment
            if total_percentage <= 100:
                return min(100, total_percentage)
            else:
                return max(0, 100 - (total_percentage - 100))
        else:
            # Múltiples assignments
            avg_percentage = total_percentage / len(assignments)
            std_dev = statistics.stdev(percentages) if len(percentages) > 1 else 0
            
            # Penalizar alta varianza
            balance_penalty = min(20, std_dev / 5)
            base_efficiency = min(100, avg_percentage)
            
            return round(max(0, base_efficiency - balance_penalty), 2)
    
    def _analyze_allocation_distribution(self, percentages: List[float]) -> Dict[str, Any]:
        """Analiza la distribución de asignaciones de porcentaje."""
        if not percentages:
            return {}
        
        # Crear histograma de distribución
        bins = [0, 25, 50, 75, 100, float('inf')]
        bin_labels = ["0-25%", "26-50%", "51-75%", "76-100%", "100%+"]
        distribution = {label: 0 for label in bin_labels}
        
        for percentage in percentages:
            for i, bin_max in enumerate(bins[1:]):
                if percentage <= bin_max:
                    distribution[bin_labels[i]] += 1
                    break
        
        # Calcular métricas de distribución
        total = len(percentages)
        distribution_percentages = {
            label: round((count / total * 100), 2) if total > 0 else 0
            for label, count in distribution.items()
        }
        
        return {
            "distribution_counts": distribution,
            "distribution_percentages": distribution_percentages,
            "skewness": self._calculate_skewness(percentages),
            "kurtosis": self._calculate_kurtosis(percentages)
        }
    
    def _categorize_utilization(self, percentages: List[float]) -> Dict[str, int]:
        """Categoriza los niveles de utilización."""
        categories = {
            "underutilized": 0,    # < 50%
            "optimal": 0,          # 50-80%
            "high": 0,             # 80-100%
            "overallocated": 0     # > 100%
        }
        
        for percentage in percentages:
            if percentage < 50:
                categories["underutilized"] += 1
            elif percentage <= 80:
                categories["optimal"] += 1
            elif percentage <= 100:
                categories["high"] += 1
            else:
                categories["overallocated"] += 1
        
        return categories
    
    def _identify_top_performers(
        self, 
        group_metrics: Dict[str, Dict[str, Any]], 
        group_by: str
    ) -> List[Dict[str, Any]]:
        """Identifica los grupos con mejor rendimiento."""
        performers = []
        
        for group_key, metrics in group_metrics.items():
            efficiency = metrics.get("efficiency_score", 0)
            assignment_count = metrics.get("assignment_count", 0)
            
            performers.append({
                f"{group_by}_id": group_key,
                "efficiency_score": efficiency,
                "assignment_count": assignment_count,
                "performance_rating": self._rate_performance(efficiency, assignment_count)
            })
        
        # Ordenar por eficiencia y luego por número de asignaciones
        performers.sort(key=lambda x: (x["efficiency_score"], x["assignment_count"]), reverse=True)
        
        return performers[:5]  # Top 5
    
    def _identify_improvement_opportunities(
        self, 
        group_metrics: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identifica oportunidades de mejora."""
        opportunities = []
        
        for group_key, metrics in group_metrics.items():
            efficiency = metrics.get("efficiency_score", 0)
            percentage_stats = metrics.get("percentage_allocation", {})
            
            if efficiency < 70:
                opportunity_type = "low_efficiency"
                description = f"Eficiencia baja ({efficiency}%), revisar distribución de carga"
            elif percentage_stats.get("std_dev", 0) > 25:
                opportunity_type = "high_variance"
                description = f"Alta varianza en asignaciones ({percentage_stats.get('std_dev', 0)}%)"
            elif percentage_stats.get("total", 0) > 150:
                opportunity_type = "overallocation"
                description = f"Posible sobreasignación ({percentage_stats.get('total', 0)}%)"
            else:
                continue
            
            opportunities.append({
                "group_id": group_key,
                "opportunity_type": opportunity_type,
                "description": description,
                "priority": "high" if efficiency < 50 else "medium",
                "current_efficiency": efficiency
            })
        
        return opportunities
    
    def _rate_performance(self, efficiency: float, assignment_count: int) -> str:
        """Califica el rendimiento basado en eficiencia y carga."""
        if efficiency >= 90 and assignment_count >= 2:
            return "excellent"
        elif efficiency >= 80 and assignment_count >= 1:
            return "good"
        elif efficiency >= 60:
            return "fair"
        else:
            return "needs_improvement"
    
    def _calculate_skewness(self, values: List[float]) -> float:
        """Calcula la asimetría de una distribución."""
        if len(values) < 3:
            return 0
        
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        if std_dev == 0:
            return 0
        
        n = len(values)
        skewness = (n / ((n - 1) * (n - 2))) * sum(
            ((x - mean_val) / std_dev) ** 3 for x in values
        )
        
        return round(skewness, 3)
    
    def _calculate_kurtosis(self, values: List[float]) -> float:
        """Calcula la curtosis de una distribución."""
        if len(values) < 4:
            return 0
        
        mean_val = statistics.mean(values)
        std_dev = statistics.stdev(values)
        
        if std_dev == 0:
            return 0
        
        n = len(values)
        kurtosis = (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * sum(
            ((x - mean_val) / std_dev) ** 4 for x in values
        ) - (3 * (n - 1) ** 2 / ((n - 2) * (n - 3)))
        
        return round(kurtosis, 3)
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE DURACIÓN
    # ============================================================================
    
    def _categorize_durations(self, durations: List[int]) -> Dict[str, Dict[str, Any]]:
        """Categoriza las duraciones en grupos."""
        categories = {
            "short_term": {"range": "1-30 días", "count": 0, "durations": []},
            "medium_term": {"range": "31-90 días", "count": 0, "durations": []},
            "long_term": {"range": "91-365 días", "count": 0, "durations": []},
            "extended": {"range": "365+ días", "count": 0, "durations": []}
        }
        
        for duration in durations:
            if duration <= 30:
                categories["short_term"]["count"] += 1
                categories["short_term"]["durations"].append(duration)
            elif duration <= 90:
                categories["medium_term"]["count"] += 1
                categories["medium_term"]["durations"].append(duration)
            elif duration <= 365:
                categories["long_term"]["count"] += 1
                categories["long_term"]["durations"].append(duration)
            else:
                categories["extended"]["count"] += 1
                categories["extended"]["durations"].append(duration)
        
        # Calcular estadísticas por categoría
        for category_data in categories.values():
            if category_data["durations"]:
                category_data["mean"] = round(statistics.mean(category_data["durations"]), 2)
                category_data["median"] = round(statistics.median(category_data["durations"]), 2)
            else:
                category_data["mean"] = 0
                category_data["median"] = 0
            
            # Remover la lista de duraciones para el resultado final
            del category_data["durations"]
        
        return categories
    
    def _analyze_duration_trends(self, duration_by_month: Dict[str, List[int]]) -> Dict[str, Any]:
        """Analiza tendencias de duración por mes."""
        if not duration_by_month:
            return {}
        
        monthly_averages = {}
        for month, durations in duration_by_month.items():
            if durations:
                monthly_averages[month] = round(statistics.mean(durations), 2)
        
        if len(monthly_averages) < 2:
            return {"monthly_averages": monthly_averages, "trend": "insufficient_data"}
        
        # Calcular tendencia simple
        months = sorted(monthly_averages.keys())
        values = [monthly_averages[month] for month in months]
        
        # Tendencia lineal simple
        if len(values) >= 2:
            trend_direction = "increasing" if values[-1] > values[0] else "decreasing"
            trend_strength = abs(values[-1] - values[0]) / values[0] * 100 if values[0] != 0 else 0
        else:
            trend_direction = "stable"
            trend_strength = 0
        
        return {
            "monthly_averages": monthly_averages,
            "trend_direction": trend_direction,
            "trend_strength_percentage": round(trend_strength, 2),
            "most_recent_average": values[-1] if values else 0,
            "historical_average": round(statistics.mean(values), 2) if values else 0
        }
    
    def _analyze_duration_efficiency(
        self, 
        assignments: List[ProjectAssignment], 
        durations: List[int]
    ) -> Dict[str, Any]:
        """Analiza la eficiencia de duración de asignaciones."""
        if not assignments or not durations:
            return {}
        
        # Calcular eficiencia por rol
        role_efficiency = {}
        role_durations = defaultdict(list)
        
        for assignment, duration in zip(assignments, durations):
            role_durations[assignment.role_in_project].append(duration)
        
        for role, role_dur_list in role_durations.items():
            avg_duration = statistics.mean(role_dur_list)
            # Eficiencia inversa: duraciones más cortas = mayor eficiencia
            efficiency = max(0, 100 - (avg_duration / 10))  # Normalizar
            role_efficiency[role] = {
                "average_duration": round(avg_duration, 2),
                "efficiency_score": round(min(100, efficiency), 2),
                "assignment_count": len(role_dur_list)
            }
        
        # Identificar roles más y menos eficientes
        sorted_roles = sorted(
            role_efficiency.items(), 
            key=lambda x: x[1]["efficiency_score"], 
            reverse=True
        )
        
        return {
            "role_efficiency": role_efficiency,
            "most_efficient_role": sorted_roles[0] if sorted_roles else None,
            "least_efficient_role": sorted_roles[-1] if sorted_roles else None,
            "overall_efficiency_score": round(
                statistics.mean([r["efficiency_score"] for r in role_efficiency.values()]), 2
            ) if role_efficiency else 0
        }
    
    def _generate_duration_insights(
        self, 
        duration_stats: Dict[str, Any], 
        duration_categories: Dict[str, Dict[str, Any]], 
        role_analysis: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Genera insights sobre las duraciones."""
        insights = []
        
        # Insight sobre duración promedio
        mean_days = duration_stats.get("mean_days", 0)
        if mean_days > 180:
            insights.append(f"Las asignaciones tienden a ser de larga duración (promedio: {mean_days} días)")
        elif mean_days < 30:
            insights.append(f"Las asignaciones tienden a ser de corta duración (promedio: {mean_days} días)")
        else:
            insights.append(f"Las asignaciones tienen duración moderada (promedio: {mean_days} días)")
        
        # Insight sobre variabilidad
        std_dev = duration_stats.get("std_dev_days", 0)
        if std_dev > mean_days * 0.5:
            insights.append("Hay alta variabilidad en las duraciones de asignaciones")
        
        # Insight sobre categorías dominantes
        max_category = max(
            duration_categories.items(), 
            key=lambda x: x[1]["count"]
        ) if duration_categories else None
        
        if max_category:
            category_name, category_data = max_category
            insights.append(
                f"La mayoría de asignaciones son de {category_name.replace('_', ' ')} "
                f"({category_data['count']} asignaciones)"
            )
        
        # Insight sobre roles
        if role_analysis:
            longest_role = max(
                role_analysis.items(), 
                key=lambda x: x[1]["mean_days"]
            )
            shortest_role = min(
                role_analysis.items(), 
                key=lambda x: x[1]["mean_days"]
            )
            
            insights.append(
                f"El rol '{longest_role[0]}' tiene las asignaciones más largas "
                f"(promedio: {longest_role[1]['mean_days']} días)"
            )
            insights.append(
                f"El rol '{shortest_role[0]}' tiene las asignaciones más cortas "
                f"(promedio: {shortest_role[1]['mean_days']} días)"
            )
        
        return insights
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE TENDENCIAS (Continuación en siguiente mensaje...)
    # ============================================================================