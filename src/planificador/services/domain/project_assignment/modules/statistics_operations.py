# src/planificador/services/domain/project_assignment/modules/statistics_operations.py

"""
Módulo de Operaciones Estadísticas para Asignaciones de Proyecto

Implementa análisis estadísticos según la documentación oficial:
- 4 métodos de estadísticas básicas
- 4 métodos de estadísticas avanzadas
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
    Implementación de operaciones estadísticas según documentación oficial.
    
    Proporciona 8 métodos documentados:
    - 4 estadísticas básicas
    - 4 estadísticas avanzadas
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """
        Inicializa el módulo de operaciones estadísticas.
        
        Args:
            repository_facade: Facade del repositorio de asignaciones
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="project_assignment_statistics")
    
    # ==========================================
    # ESTADÍSTICAS BÁSICAS (4 métodos)
    # ==========================================
    
    async def get_total_assignments_count(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> int:
        """
        Obtiene el conteo total de asignaciones en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango (opcional)
            end_date: Fecha de fin del rango (opcional)
            
        Returns:
            int: Número total de asignaciones
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Fechas inválidas
        """
        try:
            self._logger.info(
                "Obteniendo conteo total de asignaciones",
                extra={"start_date": start_date, "end_date": end_date}
            )
            
            # Validar fechas si se proporcionan
            if start_date and end_date and start_date > end_date:
                raise ValidationError(
                    message="La fecha de inicio no puede ser posterior a la fecha de fin",
                    field="date_range"
                )
            
            # Obtener todas las asignaciones en el rango
            assignments = await self._repository.get_assignments_by_date_range(
                start_date=start_date,
                end_date=end_date
            )
            
            total_count = len(assignments)
            
            self._logger.info(
                f"Conteo total de asignaciones obtenido: {total_count}",
                extra={"total_count": total_count}
            )
            
            return total_count
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error obteniendo conteo total de asignaciones: {e}")
            raise RepositoryError(
                message=f"Error obteniendo conteo total de asignaciones: {e}",
                operation="get_total_assignments_count",
                original_error=e
            )
    
    async def get_active_assignments_count(
        self, 
        reference_date: Optional[date] = None
    ) -> int:
        """
        Obtiene el conteo de asignaciones activas en una fecha específica.
        
        Args:
            reference_date: Fecha de referencia (por defecto hoy)
            
        Returns:
            int: Número de asignaciones activas
            
        Raises:
            RepositoryError: Error al acceder a los datos
        """
        try:
            if reference_date is None:
                reference_date = date.today()
                
            self._logger.info(
                "Obteniendo conteo de asignaciones activas",
                extra={"reference_date": reference_date}
            )
            
            # Obtener asignaciones activas en la fecha de referencia
            assignments = await self._repository.get_active_assignments_at_date(
                reference_date=reference_date
            )
            
            active_count = len(assignments)
            
            self._logger.info(
                f"Conteo de asignaciones activas obtenido: {active_count}",
                extra={"active_count": active_count, "reference_date": reference_date}
            )
            
            return active_count
            
        except Exception as e:
            self._logger.error(f"Error obteniendo conteo de asignaciones activas: {e}")
            raise RepositoryError(
                message=f"Error obteniendo conteo de asignaciones activas: {e}",
                operation="get_active_assignments_count",
                original_error=e
            )
    
    async def get_assignments_by_status_count(self) -> Dict[str, int]:
        """
        Obtiene el conteo de asignaciones agrupadas por estado.
        
        Returns:
            Dict[str, int]: Diccionario con estado como clave y conteo como valor
            
        Raises:
            RepositoryError: Error al acceder a los datos
        """
        try:
            self._logger.info("Obteniendo conteo de asignaciones por estado")
            
            # Obtener todas las asignaciones
            assignments = await self._repository.get_all_assignments()
            
            # Contar por estado
            status_counts = Counter(assignment.status for assignment in assignments)
            
            # Convertir a diccionario regular
            result = dict(status_counts)
            
            self._logger.info(
                f"Conteo por estado obtenido: {result}",
                extra={"status_counts": result}
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error obteniendo conteo por estado: {e}")
            raise RepositoryError(
                message=f"Error obteniendo conteo por estado: {e}",
                operation="get_assignments_by_status_count",
                original_error=e
            )
    
    async def get_assignments_by_allocation_category_count(self) -> Dict[str, int]:
        """
        Obtiene el conteo de asignaciones agrupadas por categoría de asignación.
        
        Returns:
            Dict[str, int]: Diccionario con categoría y conteo
            
        Raises:
            RepositoryError: Error al acceder a los datos
        """
        try:
            self._logger.info("Obteniendo conteo de asignaciones por categoría de asignación")
            
            # Obtener todas las asignaciones
            assignments = await self._repository.get_all_assignments()
            
            # Categorizar por porcentaje de asignación
            categories = {
                "Tiempo Completo (80-100%)": 0,
                "Tiempo Parcial Alto (50-79%)": 0,
                "Tiempo Parcial Medio (25-49%)": 0,
                "Tiempo Parcial Bajo (1-24%)": 0,
                "Sin Asignación (0%)": 0
            }
            
            for assignment in assignments:
                percentage = assignment.percentage_allocation
                
                if percentage >= 80:
                    categories["Tiempo Completo (80-100%)"] += 1
                elif percentage >= 50:
                    categories["Tiempo Parcial Alto (50-79%)"] += 1
                elif percentage >= 25:
                    categories["Tiempo Parcial Medio (25-49%)"] += 1
                elif percentage > 0:
                    categories["Tiempo Parcial Bajo (1-24%)"] += 1
                else:
                    categories["Sin Asignación (0%)"] += 1
            
            self._logger.info(
                f"Conteo por categoría de asignación obtenido: {categories}",
                extra={"allocation_categories": categories}
            )
            
            return categories
            
        except Exception as e:
            self._logger.error(f"Error obteniendo conteo por categoría de asignación: {e}")
            raise RepositoryError(
                message=f"Error obteniendo conteo por categoría de asignación: {e}",
                operation="get_assignments_by_allocation_category_count",
                original_error=e
            )
    
    # ==========================================
    # ESTADÍSTICAS AVANZADAS (4 métodos)
    # ==========================================
    
    async def get_assignment_duration_analytics(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Obtiene análisis avanzados de duración de asignaciones.
        
        Args:
            start_date: Fecha de inicio del análisis (opcional)
            end_date: Fecha de fin del análisis (opcional)
            
        Returns:
            Dict[str, Any]: Análisis de duración con métricas estadísticas
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Fechas inválidas
        """
        try:
            self._logger.info(
                "Obteniendo análisis de duración de asignaciones",
                extra={"start_date": start_date, "end_date": end_date}
            )
            
            # Validar fechas
            if start_date and end_date and start_date > end_date:
                raise ValidationError(
                    message="La fecha de inicio no puede ser posterior a la fecha de fin",
                    field="date_range"
                )
            
            # Obtener asignaciones en el rango
            assignments = await self._repository.get_assignments_by_date_range(
                start_date=start_date,
                end_date=end_date
            )
            
            if not assignments:
                return {
                    "total_assignments": 0,
                    "duration_stats": {},
                    "distribution": {},
                    "trends": {}
                }
            
            # Calcular duraciones en días
            durations = []
            for assignment in assignments:
                if assignment.end_date and assignment.start_date:
                    duration = (assignment.end_date - assignment.start_date).days
                    durations.append(duration)
            
            if not durations:
                return {
                    "total_assignments": len(assignments),
                    "duration_stats": {},
                    "distribution": {},
                    "trends": {}
                }
            
            # Estadísticas básicas
            duration_stats = {
                "mean": statistics.mean(durations),
                "median": statistics.median(durations),
                "mode": statistics.mode(durations) if durations else 0,
                "min": min(durations),
                "max": max(durations),
                "std_dev": statistics.stdev(durations) if len(durations) > 1 else 0
            }
            
            # Distribución por rangos
            distribution = {
                "Corto Plazo (1-30 días)": sum(1 for d in durations if 1 <= d <= 30),
                "Medio Plazo (31-90 días)": sum(1 for d in durations if 31 <= d <= 90),
                "Largo Plazo (91-365 días)": sum(1 for d in durations if 91 <= d <= 365),
                "Muy Largo Plazo (>365 días)": sum(1 for d in durations if d > 365)
            }
            
            result = {
                "total_assignments": len(assignments),
                "duration_stats": duration_stats,
                "distribution": distribution,
                "analysis_period": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
            self._logger.info(
                "Análisis de duración completado",
                extra={"result_summary": result}
            )
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error en análisis de duración: {e}")
            raise RepositoryError(
                message=f"Error en análisis de duración: {e}",
                operation="get_assignment_duration_analytics",
                original_error=e
            )
    
    async def get_workload_distribution_analytics(self) -> Dict[str, Any]:
        """
        Obtiene análisis avanzados de distribución de carga de trabajo.
        
        Returns:
            Dict[str, Any]: Análisis de distribución de carga de trabajo
            
        Raises:
            RepositoryError: Error al acceder a los datos
        """
        try:
            self._logger.info("Obteniendo análisis de distribución de carga de trabajo")
            
            # Obtener asignaciones activas
            assignments = await self._repository.get_active_assignments()
            
            if not assignments:
                return {
                    "total_active_assignments": 0,
                    "workload_distribution": {},
                    "employee_analysis": {},
                    "project_analysis": {}
                }
            
            # Análisis por empleado
            employee_workload = defaultdict(list)
            for assignment in assignments:
                employee_workload[assignment.employee_id].append(assignment.percentage_allocation)
            
            employee_analysis = {}
            for employee_id, allocations in employee_workload.items():
                total_allocation = sum(allocations)
                employee_analysis[employee_id] = {
                    "total_allocation": total_allocation,
                    "assignment_count": len(allocations),
                    "average_allocation": total_allocation / len(allocations),
                    "status": self._categorize_workload(total_allocation)
                }
            
            # Análisis por proyecto
            project_workload = defaultdict(list)
            for assignment in assignments:
                project_workload[assignment.project_id].append(assignment.percentage_allocation)
            
            project_analysis = {}
            for project_id, allocations in project_workload.items():
                total_allocation = sum(allocations)
                project_analysis[project_id] = {
                    "total_allocation": total_allocation,
                    "team_size": len(allocations),
                    "average_allocation": total_allocation / len(allocations)
                }
            
            # Distribución general
            all_allocations = [a.percentage_allocation for a in assignments]
            workload_distribution = {
                "total_assignments": len(assignments),
                "allocation_stats": {
                    "mean": statistics.mean(all_allocations),
                    "median": statistics.median(all_allocations),
                    "min": min(all_allocations),
                    "max": max(all_allocations),
                    "std_dev": statistics.stdev(all_allocations) if len(all_allocations) > 1 else 0
                },
                "distribution_by_range": {
                    "Alto (80-100%)": sum(1 for a in all_allocations if a >= 80),
                    "Medio (50-79%)": sum(1 for a in all_allocations if 50 <= a < 80),
                    "Bajo (25-49%)": sum(1 for a in all_allocations if 25 <= a < 50),
                    "Mínimo (1-24%)": sum(1 for a in all_allocations if 1 <= a < 25),
                    "Sin asignación (0%)": sum(1 for a in all_allocations if a == 0)
                }
            }
            
            result = {
                "total_active_assignments": len(assignments),
                "workload_distribution": workload_distribution,
                "employee_analysis": employee_analysis,
                "project_analysis": project_analysis
            }
            
            self._logger.info(
                "Análisis de distribución de carga completado",
                extra={"total_employees": len(employee_analysis), "total_projects": len(project_analysis)}
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error en análisis de distribución de carga: {e}")
            raise RepositoryError(
                message=f"Error en análisis de distribución de carga: {e}",
                operation="get_workload_distribution_analytics",
                original_error=e
            )
    
    async def get_assignment_trends(
        self, 
        months_back: int = 12
    ) -> Dict[str, Any]:
        """
        Obtiene análisis de tendencias de asignaciones en el tiempo.
        
        Args:
            months_back: Número de meses hacia atrás para el análisis
            
        Returns:
            Dict[str, Any]: Análisis de tendencias temporales
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Parámetros inválidos
        """
        try:
            if months_back <= 0:
                raise ValidationError(
                    message="El número de meses debe ser positivo",
                    field="months_back"
                )
            
            self._logger.info(
                f"Obteniendo análisis de tendencias para {months_back} meses",
                extra={"months_back": months_back}
            )
            
            # Calcular rango de fechas
            end_date = date.today()
            start_date = end_date - timedelta(days=months_back * 30)
            
            # Obtener asignaciones en el período
            assignments = await self._repository.get_assignments_by_date_range(
                start_date=start_date,
                end_date=end_date
            )
            
            if not assignments:
                return {
                    "period": {"start_date": start_date, "end_date": end_date},
                    "trends": {},
                    "monthly_analysis": {},
                    "growth_metrics": {}
                }
            
            # Agrupar por mes
            monthly_data = defaultdict(lambda: {
                "new_assignments": 0,
                "completed_assignments": 0,
                "active_assignments": 0,
                "total_allocation": 0
            })
            
            for assignment in assignments:
                month_key = assignment.start_date.strftime("%Y-%m")
                monthly_data[month_key]["new_assignments"] += 1
                monthly_data[month_key]["total_allocation"] += assignment.percentage_allocation
                
                if assignment.end_date and assignment.end_date <= end_date:
                    end_month_key = assignment.end_date.strftime("%Y-%m")
                    monthly_data[end_month_key]["completed_assignments"] += 1
            
            # Calcular métricas de crecimiento
            months = sorted(monthly_data.keys())
            if len(months) >= 2:
                first_month = monthly_data[months[0]]
                last_month = monthly_data[months[-1]]
                
                growth_metrics = {
                    "new_assignments_growth": self._calculate_growth_rate(
                        first_month["new_assignments"], 
                        last_month["new_assignments"]
                    ),
                    "allocation_growth": self._calculate_growth_rate(
                        first_month["total_allocation"], 
                        last_month["total_allocation"]
                    )
                }
            else:
                growth_metrics = {}
            
            result = {
                "period": {"start_date": start_date, "end_date": end_date},
                "monthly_analysis": dict(monthly_data),
                "growth_metrics": growth_metrics,
                "total_assignments_analyzed": len(assignments)
            }
            
            self._logger.info(
                "Análisis de tendencias completado",
                extra={"months_analyzed": len(months), "total_assignments": len(assignments)}
            )
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error en análisis de tendencias: {e}")
            raise RepositoryError(
                message=f"Error en análisis de tendencias: {e}",
                operation="get_assignment_trends",
                original_error=e
            )
    
    async def get_comprehensive_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas completas para dashboard ejecutivo.
        
        Returns:
            Dict[str, Any]: Métricas completas del dashboard
            
        Raises:
            RepositoryError: Error al acceder a los datos
        """
        try:
            self._logger.info("Obteniendo métricas completas para dashboard")
            
            # Obtener datos base
            all_assignments = await self._repository.get_all_assignments()
            active_assignments = await self._repository.get_active_assignments()
            
            # Métricas básicas
            basic_metrics = {
                "total_assignments": len(all_assignments),
                "active_assignments": len(active_assignments),
                "completion_rate": self._calculate_completion_rate(all_assignments),
                "average_allocation": statistics.mean([a.percentage_allocation for a in active_assignments]) if active_assignments else 0
            }
            
            # Distribución por estado
            status_distribution = Counter(assignment.status for assignment in all_assignments)
            
            # Análisis de empleados únicos
            unique_employees = set(assignment.employee_id for assignment in all_assignments)
            unique_projects = set(assignment.project_id for assignment in all_assignments)
            
            # Métricas de eficiencia
            efficiency_metrics = {
                "employees_with_assignments": len(unique_employees),
                "projects_with_assignments": len(unique_projects),
                "average_assignments_per_employee": len(all_assignments) / len(unique_employees) if unique_employees else 0,
                "average_assignments_per_project": len(all_assignments) / len(unique_projects) if unique_projects else 0
            }
            
            # Análisis de carga de trabajo
            workload_analysis = await self._analyze_current_workload(active_assignments)
            
            # Alertas y recomendaciones
            alerts = await self._generate_dashboard_alerts(active_assignments)
            
            result = {
                "basic_metrics": basic_metrics,
                "status_distribution": dict(status_distribution),
                "efficiency_metrics": efficiency_metrics,
                "workload_analysis": workload_analysis,
                "alerts": alerts,
                "last_updated": date.today().isoformat()
            }
            
            self._logger.info(
                "Métricas de dashboard completadas",
                extra={"total_metrics": len(result)}
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error obteniendo métricas de dashboard: {e}")
            raise RepositoryError(
                message=f"Error obteniendo métricas de dashboard: {e}",
                operation="get_comprehensive_dashboard_metrics",
                original_error=e
            )
    
    # ==========================================
    # MÉTODOS AUXILIARES PRIVADOS
    # ==========================================
    
    def _categorize_workload(self, total_allocation: float) -> str:
        """Categoriza la carga de trabajo de un empleado."""
        if total_allocation > 100:
            return "Sobrecargado"
        elif total_allocation >= 80:
            return "Completo"
        elif total_allocation >= 50:
            return "Parcial Alto"
        elif total_allocation >= 25:
            return "Parcial Medio"
        elif total_allocation > 0:
            return "Parcial Bajo"
        else:
            return "Sin Asignación"
    
    def _calculate_growth_rate(self, initial: float, final: float) -> float:
        """Calcula la tasa de crecimiento entre dos valores."""
        if initial == 0:
            return 100.0 if final > 0 else 0.0
        return ((final - initial) / initial) * 100
    
    def _calculate_completion_rate(self, assignments: List[ProjectAssignment]) -> float:
        """Calcula la tasa de finalización de asignaciones."""
        if not assignments:
            return 0.0
        
        completed = sum(1 for a in assignments if a.status == "completed")
        return (completed / len(assignments)) * 100
    
    async def _analyze_current_workload(self, active_assignments: List[ProjectAssignment]) -> Dict[str, Any]:
        """Analiza la carga de trabajo actual."""
        if not active_assignments:
            return {"status": "No hay asignaciones activas"}
        
        # Agrupar por empleado
        employee_workload = defaultdict(float)
        for assignment in active_assignments:
            employee_workload[assignment.employee_id] += assignment.percentage_allocation
        
        # Categorizar empleados
        categories = {
            "sobrecargados": sum(1 for w in employee_workload.values() if w > 100),
            "completos": sum(1 for w in employee_workload.values() if 80 <= w <= 100),
            "parciales": sum(1 for w in employee_workload.values() if 25 <= w < 80),
            "subutilizados": sum(1 for w in employee_workload.values() if 0 < w < 25)
        }
        
        return {
            "total_employees": len(employee_workload),
            "categories": categories,
            "average_workload": statistics.mean(employee_workload.values()) if employee_workload else 0
        }
    
    async def _generate_dashboard_alerts(self, active_assignments: List[ProjectAssignment]) -> List[Dict[str, str]]:
        """Genera alertas para el dashboard."""
        alerts = []
        
        if not active_assignments:
            alerts.append({
                "type": "warning",
                "message": "No hay asignaciones activas en el sistema"
            })
            return alerts
        
        # Verificar sobrecarga
        employee_workload = defaultdict(float)
        for assignment in active_assignments:
            employee_workload[assignment.employee_id] += assignment.percentage_allocation
        
        overloaded = [emp for emp, workload in employee_workload.items() if workload > 100]
        if overloaded:
            alerts.append({
                "type": "error",
                "message": f"{len(overloaded)} empleado(s) sobrecargado(s) detectado(s)"
            })
        
        # Verificar subutilización
        underutilized = [emp for emp, workload in employee_workload.items() if workload < 50]
        if len(underutilized) > len(employee_workload) * 0.3:  # Más del 30% subutilizado
            alerts.append({
                "type": "warning",
                "message": f"Alto porcentaje de empleados subutilizados: {len(underutilized)}"
            })
        
        return alerts