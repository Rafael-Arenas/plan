# -*- coding: utf-8 -*-
"""
Módulo de Operaciones de Diagnóstico para Proyectos

Implementa funcionalidades para diagnóstico de problemas, análisis de salud,
detección de anomalías y generación de reportes de estado de proyectos.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from uuid import UUID
from loguru import logger
import pendulum
from enum import Enum

from planificador.models.project import Project, ProjectStatus, ProjectPriority
from planificador.repositories.project.project_repository_facade import ProjectRepositoryFacade
from planificador.schemas.project.project import (
    ProjectDurationSchema,
    ValidationResultSchema,
    ProjectPerformanceStatsSchema,
    HealthReportSchema
)
from planificador.exceptions.domain.project_domain_exceptions import (
    ProjectDomainError,
    create_project_business_rule_error
)


class DiagnosticSeverity(Enum):
    """Niveles de severidad para diagnósticos."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class DiagnosticCategory(Enum):
    """Categorías de diagnóstico."""
    DATES = "dates"
    STATUS = "status"
    PERFORMANCE = "performance"
    RELATIONSHIPS = "relationships"
    BUSINESS_RULES = "business_rules"
    DATA_INTEGRITY = "data_integrity"
    RESOURCE_ALLOCATION = "resource_allocation"
    TIMELINE = "timeline"


class ProjectDiagnosticOperations:
    """
    Operaciones de diagnóstico para proyectos.
    
    Proporciona funcionalidades para diagnóstico de problemas, análisis de salud,
    detección de anomalías y generación de reportes de estado.
    """

    def __init__(self, repository_facade: ProjectRepositoryFacade):
        """
        Inicializa las operaciones de diagnóstico.
        
        Args:
            repository_facade: Fachada del repositorio de proyectos
        """
        self.repository = repository_facade
        self._logger = logger.bind(module="project_diagnostic_operations")

    async def diagnose_project_health(self, project_id: UUID) -> ProjectDurationSchema:
        """
        Realiza un diagnóstico completo de salud de un proyecto.
        
        Args:
            project_id: ID del proyecto a diagnosticar
            
        Returns:
            Dict[str, Any]: Reporte completo de diagnóstico
            
        Raises:
            ProjectDomainError: Si ocurre un error en el diagnóstico
        """
        self._logger.debug(f"Iniciando diagnóstico de salud para proyecto ID: {project_id}")
        
        try:
            # Obtener proyecto
            project = await self.repository.get_by_id(project_id)
            if not project:
                raise create_project_business_rule_error(
                    category="project_not_found",
                    message=f"Proyecto con ID {project_id} no encontrado",
                    project_id=project_id
                )
            
            # Inicializar reporte de diagnóstico
            diagnostic_report = {
                "project_id": project_id,
                "project_name": project.name,
                "diagnosis_timestamp": pendulum.now().isoformat(),
                "overall_health_score": 0,
                "health_status": "unknown",
                "issues": [],
                "recommendations": [],
                "categories": {},
                "summary": {}
            }
            
            # Realizar diagnósticos por categoría
            await self._diagnose_dates_health(project, diagnostic_report)
            await self._diagnose_status_health(project, diagnostic_report)
            await self._diagnose_performance_health(project, diagnostic_report)
            await self._diagnose_relationships_health(project, diagnostic_report)
            await self._diagnose_business_rules_health(project, diagnostic_report)
            await self._diagnose_data_integrity_health(project, diagnostic_report)
            await self._diagnose_timeline_health(project, diagnostic_report)
            
            # Calcular puntuación general de salud
            await self._calculate_overall_health_score(diagnostic_report)
            
            # Generar resumen y recomendaciones
            await self._generate_health_summary(diagnostic_report)
            await self._generate_health_recommendations(diagnostic_report)
            
            self._logger.debug(
                f"Diagnóstico completado para proyecto {project_id}: "
                f"salud={diagnostic_report['health_status']}, "
                f"puntuación={diagnostic_report['overall_health_score']}"
            )
            
            return diagnostic_report
            
        except Exception as e:
            self._logger.error(f"Error en diagnóstico de salud: {e}")
            raise create_project_business_rule_error(
                category="health_diagnosis_error",
                message=f"Error diagnosticando salud del proyecto: {e}",
                project_id=project_id,
                original_error=e
            )

    async def detect_project_anomalies(self, project_id: UUID) -> ValidationResultSchema:
        """
        Detecta anomalías en un proyecto específico.
        
        Args:
            project_id: ID del proyecto a analizar
            
        Returns:
            Dict[str, Any]: Reporte de anomalías detectadas
            
        Raises:
            ProjectDomainError: Si ocurre un error en la detección
        """
        self._logger.debug(f"Detectando anomalías para proyecto ID: {project_id}")
        
        try:
            # Obtener proyecto
            project = await self.repository.get_by_id(project_id)
            if not project:
                raise create_project_business_rule_error(
                    category="project_not_found",
                    message=f"Proyecto con ID {project_id} no encontrado",
                    project_id=project_id
                )
            
            anomaly_report = {
                "project_id": project_id,
                "project_name": project.name,
                "detection_timestamp": pendulum.now().isoformat(),
                "anomalies_detected": 0,
                "anomalies": [],
                "risk_level": "low",
                "categories_affected": [],
                "recommendations": []
            }
            
            # Detectar diferentes tipos de anomalías
            await self._detect_date_anomalies(project, anomaly_report)
            await self._detect_status_anomalies(project, anomaly_report)
            await self._detect_performance_anomalies(project, anomaly_report)
            await self._detect_pattern_anomalies(project, anomaly_report)
            await self._detect_business_rule_anomalies(project, anomaly_report)
            
            # Calcular nivel de riesgo
            await self._calculate_anomaly_risk_level(anomaly_report)
            
            # Generar recomendaciones para anomalías
            await self._generate_anomaly_recommendations(anomaly_report)
            
            self._logger.debug(
                f"Detección de anomalías completada: "
                f"anomalías={anomaly_report['anomalies_detected']}, "
                f"riesgo={anomaly_report['risk_level']}"
            )
            
            return anomaly_report
            
        except Exception as e:
            self._logger.error(f"Error en detección de anomalías: {e}")
            raise create_project_business_rule_error(
                category="anomaly_detection_error",
                message=f"Error detectando anomalías: {e}",
                project_id=project_id,
                original_error=e
            )

    async def analyze_project_performance(self, project_id: UUID) -> ProjectPerformanceStatsSchema:
        """
        Analiza el rendimiento de un proyecto.
        
        Args:
            project_id: ID del proyecto a analizar
            
        Returns:
            Dict[str, Any]: Análisis de rendimiento
            
        Raises:
            ProjectDomainError: Si ocurre un error en el análisis
        """
        self._logger.debug(f"Analizando rendimiento para proyecto ID: {project_id}")
        
        try:
            # Obtener proyecto
            project = await self.repository.get_by_id(project_id)
            if not project:
                raise create_project_business_rule_error(
                    category="project_not_found",
                    message=f"Proyecto con ID {project_id} no encontrado",
                    project_id=project_id
                )
            
            performance_report = {
                "project_id": project_id,
                "project_name": project.name,
                "analysis_timestamp": pendulum.now().isoformat(),
                "performance_score": 0,
                "performance_level": "unknown",
                "metrics": {},
                "trends": {},
                "bottlenecks": [],
                "opportunities": [],
                "recommendations": []
            }
            
            # Analizar diferentes métricas de rendimiento
            await self._analyze_timeline_performance(project, performance_report)
            await self._analyze_resource_performance(project, performance_report)
            await self._analyze_quality_performance(project, performance_report)
            await self._analyze_efficiency_performance(project, performance_report)
            
            # Identificar tendencias
            await self._identify_performance_trends(project, performance_report)
            
            # Detectar cuellos de botella
            await self._detect_performance_bottlenecks(project, performance_report)
            
            # Identificar oportunidades de mejora
            await self._identify_improvement_opportunities(project, performance_report)
            
            # Calcular puntuación general de rendimiento
            await self._calculate_performance_score(performance_report)
            
            # Generar recomendaciones de rendimiento
            await self._generate_performance_recommendations(performance_report)
            
            self._logger.debug(
                f"Análisis de rendimiento completado: "
                f"puntuación={performance_report['performance_score']}, "
                f"nivel={performance_report['performance_level']}"
            )
            
            return performance_report
            
        except Exception as e:
            self._logger.error(f"Error en análisis de rendimiento: {e}")
            raise create_project_business_rule_error(
                category="performance_analysis_error",
                message=f"Error analizando rendimiento: {e}",
                project_id=project_id,
                original_error=e
            )

    async def generate_project_status_report(self, project_id: UUID) -> HealthReportSchema:
        """
        Genera un reporte completo del estado de un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict[str, Any]: Reporte completo de estado
            
        Raises:
            ProjectDomainError: Si ocurre un error generando el reporte
        """
        self._logger.debug(f"Generando reporte de estado para proyecto ID: {project_id}")
        
        try:
            # Obtener proyecto
            project = await self.repository.get_by_id(project_id)
            if not project:
                raise create_project_business_rule_error(
                    category="project_not_found",
                    message=f"Proyecto con ID {project_id} no encontrado",
                    project_id=project_id
                )
            
            status_report = {
                "project_id": project_id,
                "project_name": project.name,
                "report_timestamp": pendulum.now().isoformat(),
                "current_status": project.status.value,
                "basic_info": {},
                "timeline_status": {},
                "health_indicators": {},
                "risk_assessment": {},
                "progress_metrics": {},
                "alerts": [],
                "next_actions": [],
                "stakeholder_summary": {}
            }
            
            # Recopilar información básica
            await self._collect_basic_project_info(project, status_report)
            
            # Analizar estado de cronograma
            await self._analyze_timeline_status(project, status_report)
            
            # Evaluar indicadores de salud
            await self._evaluate_health_indicators(project, status_report)
            
            # Realizar evaluación de riesgos
            await self._assess_project_risks(project, status_report)
            
            # Calcular métricas de progreso
            await self._calculate_progress_metrics(project, status_report)
            
            # Generar alertas
            await self._generate_status_alerts(project, status_report)
            
            # Determinar próximas acciones
            await self._determine_next_actions(project, status_report)
            
            # Crear resumen para stakeholders
            await self._create_stakeholder_summary(project, status_report)
            
            self._logger.debug(
                f"Reporte de estado generado: "
                f"estado={project.status.value}, "
                f"alertas={len(status_report['alerts'])}"
            )
            
            return status_report
            
        except Exception as e:
            self._logger.error(f"Error generando reporte de estado: {e}")
            raise create_project_business_rule_error(
                category="status_report_error",
                message=f"Error generando reporte de estado: {e}",
                project_id=project_id,
                original_error=e
            )

    async def diagnose_multiple_projects(self, project_ids: List[UUID]) -> HealthReportSchema:
        """
        Realiza diagnóstico de múltiples proyectos.
        
        Args:
            project_ids: Lista de IDs de proyectos
            
        Returns:
            Dict[str, Any]: Diagnóstico consolidado
            
        Raises:
            ProjectDomainError: Si ocurre un error en el diagnóstico
        """
        self._logger.debug(f"Diagnosticando múltiples proyectos: {len(project_ids)} proyectos")
        
        try:
            consolidated_report = {
                "diagnosis_timestamp": pendulum.now().isoformat(),
                "projects_analyzed": len(project_ids),
                "projects_reports": {},
                "consolidated_metrics": {},
                "cross_project_issues": [],
                "portfolio_health": {},
                "recommendations": []
            }
            
            # Diagnosticar cada proyecto individualmente
            for project_id in project_ids:
                try:
                    project_diagnosis = await self.diagnose_project_health(project_id)
                    consolidated_report["projects_reports"][project_id] = project_diagnosis
                except Exception as e:
                    self._logger.warning(f"Error diagnosticando proyecto {project_id}: {e}")
                    consolidated_report["projects_reports"][project_id] = {
                        "error": str(e),
                        "diagnosis_failed": True
                    }
            
            # Analizar métricas consolidadas
            await self._calculate_consolidated_metrics(consolidated_report)
            
            # Detectar problemas entre proyectos
            await self._detect_cross_project_issues(consolidated_report)
            
            # Evaluar salud del portafolio
            await self._evaluate_portfolio_health(consolidated_report)
            
            # Generar recomendaciones consolidadas
            await self._generate_consolidated_recommendations(consolidated_report)
            
            self._logger.debug(
                f"Diagnóstico múltiple completado: "
                f"proyectos analizados={consolidated_report['projects_analyzed']}"
            )
            
            return consolidated_report
            
        except Exception as e:
            self._logger.error(f"Error en diagnóstico múltiple: {e}")
            raise create_project_business_rule_error(
                category="multiple_diagnosis_error",
                message=f"Error diagnosticando múltiples proyectos: {e}",
                original_error=e
            )

    async def get_diagnostic_summary(self) -> HealthReportSchema:
        """
        Obtiene un resumen rápido de diagnóstico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict[str, Any]: Resumen de diagnóstico
        """
        self._logger.debug(f"Generando resumen de diagnóstico para proyecto ID: {project_id}")
        
        try:
            # Obtener proyecto
            project = await self.repository.get_by_id(project_id)
            if not project:
                return {
                    "project_id": project_id,
                    "error": "Proyecto no encontrado",
                    "summary_available": False
                }
            
            summary = {
                "project_id": project_id,
                "project_name": project.name,
                "current_status": project.status.value,
                "summary_timestamp": pendulum.now().isoformat(),
                "quick_health_check": {},
                "critical_issues": [],
                "key_metrics": {},
                "action_required": False,
                "summary_available": True
            }
            
            # Verificación rápida de salud
            await self._quick_health_check(project, summary)
            
            # Identificar problemas críticos
            await self._identify_critical_issues(project, summary)
            
            # Calcular métricas clave
            await self._calculate_key_metrics(project, summary)
            
            # Determinar si se requiere acción
            summary["action_required"] = len(summary["critical_issues"]) > 0
            
            return summary
            
        except Exception as e:
            self._logger.error(f"Error generando resumen de diagnóstico: {e}")
            return {
                "project_id": project_id,
                "error": f"Error generando resumen: {e}",
                "summary_available": False
            }

    # ============================================================================
    # MÉTODOS PRIVADOS DE DIAGNÓSTICO
    # ============================================================================

    async def _diagnose_dates_health(self, project: Project, report: Dict[str, Any]) -> None:
        """Diagnostica la salud de las fechas del proyecto."""
        dates_diagnosis = {
            "score": 100,
            "issues": [],
            "status": "healthy"
        }
        
        current_date = pendulum.now().date()
        
        # Verificar fechas faltantes
        if not project.start_date:
            dates_diagnosis["issues"].append({
                "severity": DiagnosticSeverity.MEDIUM.value,
                "message": "Fecha de inicio no definida",
                "category": DiagnosticCategory.DATES.value
            })
            dates_diagnosis["score"] -= 20
        
        if not project.end_date:
            dates_diagnosis["issues"].append({
                "severity": DiagnosticSeverity.MEDIUM.value,
                "message": "Fecha de fin no definida",
                "category": DiagnosticCategory.DATES.value
            })
            dates_diagnosis["score"] -= 20
        
        # Verificar fechas lógicas
        if project.start_date and project.end_date:
            if project.start_date >= project.end_date:
                dates_diagnosis["issues"].append({
                    "severity": DiagnosticSeverity.CRITICAL.value,
                    "message": "Fecha de inicio posterior o igual a fecha de fin",
                    "category": DiagnosticCategory.DATES.value
                })
                dates_diagnosis["score"] -= 50
        
        # Verificar proyectos vencidos
        if project.end_date and project.end_date < current_date and project.status != ProjectStatus.COMPLETED:
            dates_diagnosis["issues"].append({
                "severity": DiagnosticSeverity.HIGH.value,
                "message": "Proyecto vencido",
                "category": DiagnosticCategory.DATES.value
            })
            dates_diagnosis["score"] -= 30
        
        # Determinar estado general
        if dates_diagnosis["score"] >= 80:
            dates_diagnosis["status"] = "healthy"
        elif dates_diagnosis["score"] >= 60:
            dates_diagnosis["status"] = "warning"
        else:
            dates_diagnosis["status"] = "critical"
        
        report["categories"]["dates"] = dates_diagnosis
        report["issues"].extend(dates_diagnosis["issues"])

    async def _diagnose_status_health(self, project: Project, report: Dict[str, Any]) -> None:
        """Diagnostica la salud del estado del proyecto."""
        status_diagnosis = {
            "score": 100,
            "issues": [],
            "status": "healthy"
        }
        
        current_date = pendulum.now().date()
        
        # Verificar consistencia de estado con fechas
        if project.status == ProjectStatus.ACTIVE:
            if project.start_date and project.start_date > current_date:
                status_diagnosis["issues"].append({
                    "severity": DiagnosticSeverity.MEDIUM.value,
                    "message": "Proyecto marcado como activo pero aún no ha comenzado",
                    "category": DiagnosticCategory.STATUS.value
                })
                status_diagnosis["score"] -= 15
        
        if project.status == ProjectStatus.COMPLETED:
            if not project.end_date:
                status_diagnosis["issues"].append({
                    "severity": DiagnosticSeverity.HIGH.value,
                    "message": "Proyecto completado sin fecha de fin",
                    "category": DiagnosticCategory.STATUS.value
                })
                status_diagnosis["score"] -= 25
        
        # Verificar proyectos en borrador por mucho tiempo
        if project.status == ProjectStatus.DRAFT:
            if project.created_at:
                days_in_draft = (pendulum.now() - project.created_at).days
                if days_in_draft > 30:
                    status_diagnosis["issues"].append({
                        "severity": DiagnosticSeverity.LOW.value,
                        "message": f"Proyecto en borrador por {days_in_draft} días",
                        "category": DiagnosticCategory.STATUS.value
                    })
                    status_diagnosis["score"] -= 10
        
        # Determinar estado general
        if status_diagnosis["score"] >= 80:
            status_diagnosis["status"] = "healthy"
        elif status_diagnosis["score"] >= 60:
            status_diagnosis["status"] = "warning"
        else:
            status_diagnosis["status"] = "critical"
        
        report["categories"]["status"] = status_diagnosis
        report["issues"].extend(status_diagnosis["issues"])

    async def _diagnose_performance_health(self, project: Project, report: Dict[str, Any]) -> None:
        """Diagnostica la salud del rendimiento del proyecto."""
        performance_diagnosis = {
            "score": 100,
            "issues": [],
            "status": "healthy"
        }
        
        # Análisis de duración del proyecto
        if project.start_date and project.end_date:
            duration = (project.end_date - project.start_date).days + 1
            
            if duration > 365:  # Más de 1 año
                performance_diagnosis["issues"].append({
                    "severity": DiagnosticSeverity.MEDIUM.value,
                    "message": f"Proyecto de larga duración ({duration} días)",
                    "category": DiagnosticCategory.PERFORMANCE.value
                })
                performance_diagnosis["score"] -= 15
            
            if duration < 7:  # Menos de 1 semana
                performance_diagnosis["issues"].append({
                    "severity": DiagnosticSeverity.LOW.value,
                    "message": f"Proyecto de muy corta duración ({duration} días)",
                    "category": DiagnosticCategory.PERFORMANCE.value
                })
                performance_diagnosis["score"] -= 5
        
        # Determinar estado general
        if performance_diagnosis["score"] >= 80:
            performance_diagnosis["status"] = "healthy"
        elif performance_diagnosis["score"] >= 60:
            performance_diagnosis["status"] = "warning"
        else:
            performance_diagnosis["status"] = "critical"
        
        report["categories"]["performance"] = performance_diagnosis
        report["issues"].extend(performance_diagnosis["issues"])

    async def _diagnose_relationships_health(self, project: Project, report: Dict[str, Any]) -> None:
        """Diagnostica la salud de las relaciones del proyecto."""
        relationships_diagnosis = {
            "score": 100,
            "issues": [],
            "status": "healthy"
        }
        
        # Verificar relación con cliente
        if not project.client_id:
            relationships_diagnosis["issues"].append({
                "severity": DiagnosticSeverity.HIGH.value,
                "message": "Proyecto sin cliente asignado",
                "category": DiagnosticCategory.RELATIONSHIPS.value
            })
            relationships_diagnosis["score"] -= 30
        
        # Determinar estado general
        if relationships_diagnosis["score"] >= 80:
            relationships_diagnosis["status"] = "healthy"
        elif relationships_diagnosis["score"] >= 60:
            relationships_diagnosis["status"] = "warning"
        else:
            relationships_diagnosis["status"] = "critical"
        
        report["categories"]["relationships"] = relationships_diagnosis
        report["issues"].extend(relationships_diagnosis["issues"])

    async def _diagnose_business_rules_health(self, project: Project, report: Dict[str, Any]) -> None:
        """Diagnostica el cumplimiento de reglas de negocio."""
        business_rules_diagnosis = {
            "score": 100,
            "issues": [],
            "status": "healthy"
        }
        
        # Regla: Proyectos de alta prioridad deben tener fechas
        if project.priority == ProjectPriority.HIGH:
            if not project.start_date or not project.end_date:
                business_rules_diagnosis["issues"].append({
                    "severity": DiagnosticSeverity.HIGH.value,
                    "message": "Proyecto de alta prioridad sin fechas definidas",
                    "category": DiagnosticCategory.BUSINESS_RULES.value
                })
                business_rules_diagnosis["score"] -= 25
        
        # Determinar estado general
        if business_rules_diagnosis["score"] >= 80:
            business_rules_diagnosis["status"] = "healthy"
        elif business_rules_diagnosis["score"] >= 60:
            business_rules_diagnosis["status"] = "warning"
        else:
            business_rules_diagnosis["status"] = "critical"
        
        report["categories"]["business_rules"] = business_rules_diagnosis
        report["issues"].extend(business_rules_diagnosis["issues"])

    async def _diagnose_data_integrity_health(self, project: Project, report: Dict[str, Any]) -> None:
        """Diagnostica la integridad de los datos."""
        data_integrity_diagnosis = {
            "score": 100,
            "issues": [],
            "status": "healthy"
        }
        
        # Verificar campos obligatorios
        if not project.name or len(project.name.strip()) == 0:
            data_integrity_diagnosis["issues"].append({
                "severity": DiagnosticSeverity.CRITICAL.value,
                "message": "Nombre del proyecto vacío",
                "category": DiagnosticCategory.DATA_INTEGRITY.value
            })
            data_integrity_diagnosis["score"] -= 50
        
        # Verificar formato de código si existe
        if project.code and len(project.code) < 3:
            data_integrity_diagnosis["issues"].append({
                "severity": DiagnosticSeverity.MEDIUM.value,
                "message": "Código del proyecto muy corto",
                "category": DiagnosticCategory.DATA_INTEGRITY.value
            })
            data_integrity_diagnosis["score"] -= 15
        
        # Determinar estado general
        if data_integrity_diagnosis["score"] >= 80:
            data_integrity_diagnosis["status"] = "healthy"
        elif data_integrity_diagnosis["score"] >= 60:
            data_integrity_diagnosis["status"] = "warning"
        else:
            data_integrity_diagnosis["status"] = "critical"
        
        report["categories"]["data_integrity"] = data_integrity_diagnosis
        report["issues"].extend(data_integrity_diagnosis["issues"])

    async def _diagnose_timeline_health(self, project: Project, report: Dict[str, Any]) -> None:
        """Diagnostica la salud del cronograma."""
        timeline_diagnosis = {
            "score": 100,
            "issues": [],
            "status": "healthy"
        }
        
        current_date = pendulum.now().date()
        
        # Verificar proyectos que deberían haber comenzado
        if project.start_date and project.start_date < current_date and project.status == ProjectStatus.DRAFT:
            timeline_diagnosis["issues"].append({
                "severity": DiagnosticSeverity.HIGH.value,
                "message": "Proyecto debería haber comenzado pero sigue en borrador",
                "category": DiagnosticCategory.TIMELINE.value
            })
            timeline_diagnosis["score"] -= 30
        
        # Verificar proyectos próximos a vencer
        if project.end_date and project.status == ProjectStatus.ACTIVE:
            days_to_end = (project.end_date - current_date).days
            if days_to_end <= 7 and days_to_end > 0:
                timeline_diagnosis["issues"].append({
                    "severity": DiagnosticSeverity.MEDIUM.value,
                    "message": f"Proyecto termina en {days_to_end} días",
                    "category": DiagnosticCategory.TIMELINE.value
                })
                timeline_diagnosis["score"] -= 15
        
        # Determinar estado general
        if timeline_diagnosis["score"] >= 80:
            timeline_diagnosis["status"] = "healthy"
        elif timeline_diagnosis["score"] >= 60:
            timeline_diagnosis["status"] = "warning"
        else:
            timeline_diagnosis["status"] = "critical"
        
        report["categories"]["timeline"] = timeline_diagnosis
        report["issues"].extend(timeline_diagnosis["issues"])

    async def _calculate_overall_health_score(self, report: Dict[str, Any]) -> None:
        """Calcula la puntuación general de salud."""
        categories = report["categories"]
        if not categories:
            report["overall_health_score"] = 0
            report["health_status"] = "unknown"
            return
        
        total_score = sum(cat["score"] for cat in categories.values())
        average_score = total_score / len(categories)
        
        report["overall_health_score"] = round(average_score, 2)
        
        # Determinar estado de salud general
        if average_score >= 80:
            report["health_status"] = "healthy"
        elif average_score >= 60:
            report["health_status"] = "warning"
        elif average_score >= 40:
            report["health_status"] = "poor"
        else:
            report["health_status"] = "critical"

    async def _generate_health_summary(self, report: Dict[str, Any]) -> None:
        """Genera resumen de salud."""
        categories = report["categories"]
        critical_issues = [issue for issue in report["issues"] 
                          if issue["severity"] == DiagnosticSeverity.CRITICAL.value]
        high_issues = [issue for issue in report["issues"] 
                      if issue["severity"] == DiagnosticSeverity.HIGH.value]
        
        report["summary"] = {
            "total_categories_analyzed": len(categories),
            "healthy_categories": len([cat for cat in categories.values() if cat["status"] == "healthy"]),
            "warning_categories": len([cat for cat in categories.values() if cat["status"] == "warning"]),
            "critical_categories": len([cat for cat in categories.values() if cat["status"] == "critical"]),
            "total_issues": len(report["issues"]),
            "critical_issues": len(critical_issues),
            "high_priority_issues": len(high_issues),
            "requires_immediate_attention": len(critical_issues) > 0
        }

    async def _generate_health_recommendations(self, report: Dict[str, Any]) -> None:
        """Genera recomendaciones de salud."""
        recommendations = []
        
        # Recomendaciones basadas en problemas críticos
        critical_issues = [issue for issue in report["issues"] 
                          if issue["severity"] == DiagnosticSeverity.CRITICAL.value]
        
        if critical_issues:
            recommendations.append({
                "priority": "critical",
                "message": f"Resolver {len(critical_issues)} problemas críticos inmediatamente",
                "actions": ["Revisar problemas críticos", "Implementar correcciones", "Verificar resolución"]
            })
        
        # Recomendaciones basadas en estado general
        if report["health_status"] == "poor":
            recommendations.append({
                "priority": "high",
                "message": "El proyecto requiere atención urgente para mejorar su salud general",
                "actions": ["Revisar todas las categorías", "Priorizar correcciones", "Monitorear progreso"]
            })
        
        report["recommendations"] = recommendations

    async def _detect_date_anomalies(self, project: Project, report: Dict[str, Any]) -> None:
        """Detecta anomalías en fechas."""
        if project.start_date and project.end_date:
            duration = (project.end_date - project.start_date).days + 1
            
            # Duración anómala
            if duration > 1000:  # Más de ~3 años
                report["anomalies"].append({
                    "type": "extreme_duration",
                    "severity": DiagnosticSeverity.HIGH.value,
                    "message": f"Duración extremadamente larga: {duration} días",
                    "category": DiagnosticCategory.DATES.value
                })
                report["anomalies_detected"] += 1
            
            if duration < 1:
                report["anomalies"].append({
                    "type": "invalid_duration",
                    "severity": DiagnosticSeverity.CRITICAL.value,
                    "message": "Duración inválida o negativa",
                    "category": DiagnosticCategory.DATES.value
                })
                report["anomalies_detected"] += 1

    async def _detect_status_anomalies(self, project: Project, report: Dict[str, Any]) -> None:
        """Detecta anomalías en estado."""
        current_date = pendulum.now().date()
        
        # Proyecto completado en el futuro
        if project.status == ProjectStatus.COMPLETED and project.end_date and project.end_date > current_date:
            report["anomalies"].append({
                "type": "future_completion",
                "severity": DiagnosticSeverity.HIGH.value,
                "message": "Proyecto marcado como completado con fecha futura",
                "category": DiagnosticCategory.STATUS.value
            })
            report["anomalies_detected"] += 1

    async def _detect_performance_anomalies(self, project: Project, report: Dict[str, Any]) -> None:
        """Detecta anomalías de rendimiento."""
        # Implementación simplificada
        pass

    async def _detect_pattern_anomalies(self, project: Project, report: Dict[str, Any]) -> None:
        """Detecta anomalías de patrones."""
        # Implementación simplificada
        pass

    async def _detect_business_rule_anomalies(self, project: Project, report: Dict[str, Any]) -> None:
        """Detecta anomalías en reglas de negocio."""
        # Proyecto de alta prioridad sin fechas
        if project.priority == ProjectPriority.HIGH and (not project.start_date or not project.end_date):
            report["anomalies"].append({
                "type": "high_priority_no_dates",
                "severity": DiagnosticSeverity.HIGH.value,
                "message": "Proyecto de alta prioridad sin fechas definidas",
                "category": DiagnosticCategory.BUSINESS_RULES.value
            })
            report["anomalies_detected"] += 1

    async def _calculate_anomaly_risk_level(self, report: Dict[str, Any]) -> None:
        """Calcula el nivel de riesgo basado en anomalías."""
        critical_anomalies = len([a for a in report["anomalies"] 
                                if a["severity"] == DiagnosticSeverity.CRITICAL.value])
        high_anomalies = len([a for a in report["anomalies"] 
                            if a["severity"] == DiagnosticSeverity.HIGH.value])
        
        if critical_anomalies > 0:
            report["risk_level"] = "critical"
        elif high_anomalies > 2:
            report["risk_level"] = "high"
        elif high_anomalies > 0 or report["anomalies_detected"] > 3:
            report["risk_level"] = "medium"
        else:
            report["risk_level"] = "low"

    async def _generate_anomaly_recommendations(self, report: Dict[str, Any]) -> None:
        """Genera recomendaciones para anomalías."""
        recommendations = []
        
        if report["risk_level"] == "critical":
            recommendations.append({
                "priority": "critical",
                "message": "Anomalías críticas detectadas - requiere acción inmediata",
                "actions": ["Revisar anomalías críticas", "Corregir datos", "Validar cambios"]
            })
        
        if report["anomalies_detected"] > 5:
            recommendations.append({
                "priority": "high",
                "message": "Múltiples anomalías detectadas - revisar integridad de datos",
                "actions": ["Auditoría completa de datos", "Validación sistemática", "Corrección por lotes"]
            })
        
        report["recommendations"] = recommendations

    async def _analyze_timeline_performance(self, project: Project, report: Dict[str, Any]) -> None:
        """Analiza rendimiento de cronograma."""
        timeline_metrics = {
            "on_schedule": True,
            "days_variance": 0,
            "completion_percentage": 0
        }
        
        current_date = pendulum.now().date()
        
        if project.start_date and project.end_date:
            total_duration = (project.end_date - project.start_date).days + 1
            
            if project.start_date <= current_date <= project.end_date:
                elapsed_days = (current_date - project.start_date).days + 1
                timeline_metrics["completion_percentage"] = (elapsed_days / total_duration) * 100
            elif current_date > project.end_date:
                timeline_metrics["days_variance"] = (current_date - project.end_date).days
                timeline_metrics["on_schedule"] = False
                timeline_metrics["completion_percentage"] = 100
        
        report["metrics"]["timeline"] = timeline_metrics

    async def _analyze_resource_performance(self, project: Project, report: Dict[str, Any]) -> None:
        """Analiza rendimiento de recursos."""
        # Implementación simplificada
        report["metrics"]["resources"] = {
            "utilization_rate": 75,  # Ejemplo
            "allocation_efficiency": 80  # Ejemplo
        }

    async def _analyze_quality_performance(self, project: Project, report: Dict[str, Any]) -> None:
        """Analiza rendimiento de calidad."""
        # Implementación simplificada
        report["metrics"]["quality"] = {
            "quality_score": 85,  # Ejemplo
            "defect_rate": 5  # Ejemplo
        }

    async def _analyze_efficiency_performance(self, project: Project, report: Dict[str, Any]) -> None:
        """Analiza eficiencia del proyecto."""
        # Implementación simplificada
        report["metrics"]["efficiency"] = {
            "efficiency_score": 78,  # Ejemplo
            "productivity_index": 82  # Ejemplo
        }

    async def _identify_performance_trends(self, project: Project, report: Dict[str, Any]) -> None:
        """Identifica tendencias de rendimiento."""
        # Implementación simplificada
        report["trends"] = {
            "timeline_trend": "stable",
            "quality_trend": "improving",
            "efficiency_trend": "declining"
        }

    async def _detect_performance_bottlenecks(self, project: Project, report: Dict[str, Any]) -> None:
        """Detecta cuellos de botella."""
        # Implementación simplificada
        report["bottlenecks"] = [
            {
                "area": "resource_allocation",
                "severity": "medium",
                "description": "Asignación de recursos subóptima"
            }
        ]

    async def _identify_improvement_opportunities(self, project: Project, report: Dict[str, Any]) -> None:
        """Identifica oportunidades de mejora."""
        # Implementación simplificada
        report["opportunities"] = [
            {
                "area": "timeline_optimization",
                "potential_impact": "high",
                "description": "Optimización de cronograma puede reducir duración en 15%"
            }
        ]

    async def _calculate_performance_score(self, report: Dict[str, Any]) -> None:
        """Calcula puntuación de rendimiento."""
        metrics = report["metrics"]
        
        # Calcular puntuación promedio de todas las métricas
        all_scores = []
        
        if "timeline" in metrics and "completion_percentage" in metrics["timeline"]:
            timeline_score = min(100, metrics["timeline"]["completion_percentage"])
            if not metrics["timeline"]["on_schedule"]:
                timeline_score *= 0.8  # Penalizar retrasos
            all_scores.append(timeline_score)
        
        if "resources" in metrics:
            all_scores.append(metrics["resources"].get("utilization_rate", 0))
            all_scores.append(metrics["resources"].get("allocation_efficiency", 0))
        
        if "quality" in metrics:
            all_scores.append(metrics["quality"].get("quality_score", 0))
        
        if "efficiency" in metrics:
            all_scores.append(metrics["efficiency"].get("efficiency_score", 0))
        
        if all_scores:
            report["performance_score"] = round(sum(all_scores) / len(all_scores), 2)
        else:
            report["performance_score"] = 0
        
        # Determinar nivel de rendimiento
        score = report["performance_score"]
        if score >= 85:
            report["performance_level"] = "excellent"
        elif score >= 70:
            report["performance_level"] = "good"
        elif score >= 55:
            report["performance_level"] = "fair"
        else:
            report["performance_level"] = "poor"

    async def _generate_performance_recommendations(self, report: Dict[str, Any]) -> None:
        """Genera recomendaciones de rendimiento."""
        recommendations = []
        
        if report["performance_level"] == "poor":
            recommendations.append({
                "priority": "high",
                "message": "Rendimiento deficiente - requiere intervención inmediata",
                "actions": ["Revisar procesos", "Optimizar recursos", "Replantear cronograma"]
            })
        
        if len(report["bottlenecks"]) > 0:
            recommendations.append({
                "priority": "medium",
                "message": "Cuellos de botella identificados",
                "actions": ["Analizar cuellos de botella", "Implementar soluciones", "Monitorear mejoras"]
            })
        
        report["recommendations"] = recommendations

    # Métodos adicionales para reporte de estado y diagnóstico múltiple
    async def _collect_basic_project_info(self, project: Project, report: Dict[str, Any]) -> None:
        """Recopila información básica del proyecto."""
        report["basic_info"] = {
            "name": project.name,
            "code": project.code,
            "trigram": project.trigram,
            "status": project.status.value,
            "priority": project.priority.value if project.priority else None,
            "client_id": project.client_id,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "end_date": project.end_date.isoformat() if project.end_date else None,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None
        }

    async def _analyze_timeline_status(self, project: Project, report: Dict[str, Any]) -> None:
        """Analiza estado del cronograma."""
        current_date = pendulum.now().date()
        
        timeline_status = {
            "current_phase": "unknown",
            "progress_percentage": 0,
            "days_elapsed": 0,
            "days_remaining": 0,
            "is_overdue": False,
            "schedule_variance": 0
        }
        
        if project.start_date and project.end_date:
            total_duration = (project.end_date - project.start_date).days + 1
            
            if current_date < project.start_date:
                timeline_status["current_phase"] = "not_started"
                timeline_status["days_remaining"] = (project.start_date - current_date).days
            elif current_date > project.end_date:
                timeline_status["current_phase"] = "overdue"
                timeline_status["is_overdue"] = True
                timeline_status["schedule_variance"] = (current_date - project.end_date).days
                timeline_status["progress_percentage"] = 100
            else:
                timeline_status["current_phase"] = "in_progress"
                elapsed = (current_date - project.start_date).days + 1
                timeline_status["days_elapsed"] = elapsed
                timeline_status["days_remaining"] = (project.end_date - current_date).days
                timeline_status["progress_percentage"] = (elapsed / total_duration) * 100
        
        report["timeline_status"] = timeline_status

    async def _evaluate_health_indicators(self, project: Project, report: Dict[str, Any]) -> None:
        """Evalúa indicadores de salud."""
        # Realizar diagnóstico rápido de salud
        health_diagnosis = await self.diagnose_project_health(project.id)
        
        report["health_indicators"] = {
            "overall_health_score": health_diagnosis["overall_health_score"],
            "health_status": health_diagnosis["health_status"],
            "critical_issues_count": len([i for i in health_diagnosis["issues"] 
                                        if i["severity"] == DiagnosticSeverity.CRITICAL.value]),
            "total_issues_count": len(health_diagnosis["issues"]),
            "categories_status": {cat: data["status"] for cat, data in health_diagnosis["categories"].items()}
        }

    async def _assess_project_risks(self, project: Project, report: Dict[str, Any]) -> None:
        """Evalúa riesgos del proyecto."""
        risk_factors = []
        risk_score = 0
        
        current_date = pendulum.now().date()
        
        # Riesgo de cronograma
        if project.end_date and project.end_date < current_date and project.status != ProjectStatus.COMPLETED:
            risk_factors.append({
                "type": "schedule",
                "level": "high",
                "description": "Proyecto vencido"
            })
            risk_score += 30
        
        # Riesgo de datos incompletos
        if not project.start_date or not project.end_date:
            risk_factors.append({
                "type": "data",
                "level": "medium",
                "description": "Fechas incompletas"
            })
            risk_score += 15
        
        # Riesgo de cliente
        if not project.client_id:
            risk_factors.append({
                "type": "relationship",
                "level": "high",
                "description": "Sin cliente asignado"
            })
            risk_score += 25
        
        # Determinar nivel de riesgo general
        if risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 25:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        report["risk_assessment"] = {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "mitigation_required": risk_score >= 25
        }

    async def _calculate_progress_metrics(self, project: Project, report: Dict[str, Any]) -> None:
        """Calcula métricas de progreso."""
        # Implementación simplificada
        report["progress_metrics"] = {
            "completion_percentage": 0,
            "milestones_completed": 0,
            "milestones_total": 0,
            "tasks_completed": 0,
            "tasks_total": 0,
            "deliverables_completed": 0,
            "deliverables_total": 0
        }

    async def _generate_status_alerts(self, project: Project, report: Dict[str, Any]) -> None:
        """Genera alertas de estado."""
        alerts = []
        current_date = pendulum.now().date()
        
        # Alerta de proyecto vencido
        if project.end_date and project.end_date < current_date and project.status != ProjectStatus.COMPLETED:
            days_overdue = (current_date - project.end_date).days
            alerts.append({
                "type": "overdue",
                "severity": "critical",
                "message": f"Proyecto vencido por {days_overdue} días",
                "action_required": True
            })
        
        # Alerta de proyecto próximo a vencer
        elif project.end_date and project.status == ProjectStatus.ACTIVE:
            days_to_end = (project.end_date - current_date).days
            if 0 < days_to_end <= 7:
                alerts.append({
                    "type": "due_soon",
                    "severity": "warning",
                    "message": f"Proyecto termina en {days_to_end} días",
                    "action_required": True
                })
        
        # Alerta de datos incompletos
        if not project.start_date or not project.end_date:
            alerts.append({
                "type": "incomplete_data",
                "severity": "warning",
                "message": "Fechas del proyecto incompletas",
                "action_required": False
            })
        
        report["alerts"] = alerts

    async def _determine_next_actions(self, project: Project, report: Dict[str, Any]) -> None:
        """Determina próximas acciones."""
        next_actions = []
        
        # Acciones basadas en alertas críticas
        critical_alerts = [a for a in report["alerts"] if a["severity"] == "critical"]
        if critical_alerts:
            next_actions.append({
                "priority": "immediate",
                "action": "Resolver alertas críticas",
                "description": "Atender problemas críticos identificados"
            })
        
        # Acciones basadas en estado
        if project.status == ProjectStatus.DRAFT:
            next_actions.append({
                "priority": "high",
                "action": "Activar proyecto",
                "description": "Revisar y activar el proyecto si está listo"
            })
        
        # Acciones basadas en fechas
        if not project.start_date or not project.end_date:
            next_actions.append({
                "priority": "medium",
                "action": "Completar fechas",
                "description": "Definir fechas de inicio y fin del proyecto"
            })
        
        report["next_actions"] = next_actions

    async def _create_stakeholder_summary(self, project: Project, report: Dict[str, Any]) -> None:
        """Crea resumen para stakeholders."""
        report["stakeholder_summary"] = {
            "project_name": project.name,
            "current_status": project.status.value,
            "health_status": report["health_indicators"]["health_status"],
            "risk_level": report["risk_assessment"]["risk_level"],
            "critical_issues": len([a for a in report["alerts"] if a["severity"] == "critical"]),
            "action_items": len([a for a in report["next_actions"] if a["priority"] in ["immediate", "high"]]),
            "overall_assessment": self._get_overall_assessment(report),
            "key_recommendations": self._get_key_recommendations(report)
        }

    def _get_overall_assessment(self, report: Dict[str, Any]) -> str:
        """Obtiene evaluación general."""
        health_status = report["health_indicators"]["health_status"]
        risk_level = report["risk_assessment"]["risk_level"]
        
        if health_status == "critical" or risk_level == "high":
            return "Requiere atención inmediata"
        elif health_status == "warning" or risk_level == "medium":
            return "Requiere monitoreo cercano"
        else:
            return "En buen estado"

    def _get_key_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Obtiene recomendaciones clave."""
        recommendations = []
        
        if report["alerts"]:
            recommendations.append("Resolver alertas identificadas")
        
        if report["risk_assessment"]["risk_level"] == "high":
            recommendations.append("Implementar plan de mitigación de riesgos")
        
        if report["health_indicators"]["health_status"] in ["warning", "critical"]:
            recommendations.append("Mejorar salud general del proyecto")
        
        return recommendations[:3]  # Máximo 3 recomendaciones clave

    async def _calculate_consolidated_metrics(self, report: Dict[str, Any]) -> None:
        """Calcula métricas consolidadas."""
        projects_reports = report["projects_reports"]
        successful_reports = {k: v for k, v in projects_reports.items() 
                            if not v.get("diagnosis_failed", False)}
        
        if not successful_reports:
            report["consolidated_metrics"] = {"error": "No hay reportes válidos para consolidar"}
            return
        
        # Calcular métricas promedio
        health_scores = [r["overall_health_score"] for r in successful_reports.values()]
        
        report["consolidated_metrics"] = {
            "average_health_score": round(sum(health_scores) / len(health_scores), 2),
            "projects_healthy": len([r for r in successful_reports.values() 
                                   if r["health_status"] == "healthy"]),
            "projects_warning": len([r for r in successful_reports.values() 
                                   if r["health_status"] == "warning"]),
            "projects_critical": len([r for r in successful_reports.values() 
                                    if r["health_status"] == "critical"]),
            "total_issues": sum(len(r["issues"]) for r in successful_reports.values()),
            "critical_issues": sum(len([i for i in r["issues"] 
                                      if i["severity"] == DiagnosticSeverity.CRITICAL.value]) 
                                 for r in successful_reports.values())
        }

    async def _detect_cross_project_issues(self, report: Dict[str, Any]) -> None:
        """Detecta problemas entre proyectos."""
        # Implementación simplificada
        report["cross_project_issues"] = [
            {
                "type": "resource_conflict",
                "severity": "medium",
                "description": "Posibles conflictos de recursos entre proyectos",
                "affected_projects": []
            }
        ]

    async def _evaluate_portfolio_health(self, report: Dict[str, Any]) -> None:
        """Evalúa salud del portafolio."""
        metrics = report["consolidated_metrics"]
        
        if "error" in metrics:
            report["portfolio_health"] = {"status": "unknown", "error": metrics["error"]}
            return
        
        total_projects = report["projects_analyzed"]
        healthy_percentage = (metrics["projects_healthy"] / total_projects) * 100
        
        if healthy_percentage >= 80:
            portfolio_status = "excellent"
        elif healthy_percentage >= 60:
            portfolio_status = "good"
        elif healthy_percentage >= 40:
            portfolio_status = "fair"
        else:
            portfolio_status = "poor"
        
        report["portfolio_health"] = {
            "status": portfolio_status,
            "healthy_percentage": round(healthy_percentage, 2),
            "average_health_score": metrics["average_health_score"],
            "requires_attention": metrics["critical_issues"] > 0 or healthy_percentage < 60
        }

    async def _generate_consolidated_recommendations(self, report: Dict[str, Any]) -> None:
        """Genera recomendaciones consolidadas."""
        recommendations = []
        
        portfolio_health = report["portfolio_health"]
        if portfolio_health.get("requires_attention", False):
            recommendations.append({
                "priority": "high",
                "message": "El portafolio requiere atención inmediata",
                "actions": ["Revisar proyectos críticos", "Implementar plan de mejora", "Monitorear progreso"]
            })
        
        metrics = report["consolidated_metrics"]
        if not isinstance(metrics, dict) or "error" in metrics:
            recommendations.append({
                "priority": "medium",
                "message": "Revisar proyectos con errores de diagnóstico",
                "actions": ["Verificar datos de proyectos", "Corregir problemas", "Re-ejecutar diagnóstico"]
            })
        elif metrics.get("critical_issues", 0) > 0:
            recommendations.append({
                "priority": "critical",
                "message": f"{metrics['critical_issues']} problemas críticos en el portafolio",
                "actions": ["Priorizar problemas críticos", "Asignar recursos", "Seguimiento diario"]
            })
        
        report["recommendations"] = recommendations

    async def _quick_health_check(self, project: Project, summary: Dict[str, Any]) -> None:
        """Verificación rápida de salud."""
        health_check = {
            "dates_defined": bool(project.start_date and project.end_date),
            "client_assigned": bool(project.client_id),
            "status_appropriate": True,  # Simplificado
            "no_critical_issues": True   # Se determina después
        }
        
        # Verificar problemas críticos básicos
        current_date = pendulum.now().date()
        if project.end_date and project.end_date < current_date and project.status != ProjectStatus.COMPLETED:
            health_check["no_critical_issues"] = False
        
        if project.start_date and project.end_date and project.start_date >= project.end_date:
            health_check["no_critical_issues"] = False
        
        summary["quick_health_check"] = health_check

    async def _identify_critical_issues(self, project: Project, summary: Dict[str, Any]) -> None:
        """Identifica problemas críticos."""
        critical_issues = []
        current_date = pendulum.now().date()
        
        # Proyecto vencido
        if project.end_date and project.end_date < current_date and project.status != ProjectStatus.COMPLETED:
            days_overdue = (current_date - project.end_date).days
            critical_issues.append({
                "type": "overdue",
                "message": f"Proyecto vencido por {days_overdue} días",
                "severity": "critical"
            })
        
        # Fechas inválidas
        if project.start_date and project.end_date and project.start_date >= project.end_date:
            critical_issues.append({
                "type": "invalid_dates",
                "message": "Fechas de proyecto inválidas",
                "severity": "critical"
            })
        
        # Sin cliente
        if not project.client_id:
            critical_issues.append({
                "type": "no_client",
                "message": "Proyecto sin cliente asignado",
                "severity": "high"
            })
        
        summary["critical_issues"] = critical_issues

    async def _calculate_key_metrics(self, project: Project, summary: Dict[str, Any]) -> None:
        """Calcula métricas clave."""
        current_date = pendulum.now().date()
        
        key_metrics = {
            "days_since_creation": 0,
            "days_to_start": 0,
            "days_to_end": 0,
            "project_duration": 0,
            "completion_percentage": 0
        }
        
        if project.created_at:
            key_metrics["days_since_creation"] = (pendulum.now() - project.created_at).days
        
        if project.start_date:
            key_metrics["days_to_start"] = (project.start_date - current_date).days
        
        if project.end_date:
            key_metrics["days_to_end"] = (project.end_date - current_date).days
        
        if project.start_date and project.end_date:
            key_metrics["project_duration"] = (project.end_date - project.start_date).days + 1
            
            # Calcular porcentaje de completación basado en tiempo
            if current_date >= project.start_date:
                if current_date >= project.end_date:
                    key_metrics["completion_percentage"] = 100
                else:
                    elapsed_days = (current_date - project.start_date).days + 1
                    total_days = key_metrics["project_duration"]
                    key_metrics["completion_percentage"] = round((elapsed_days / total_days) * 100, 2)
        
        summary["key_metrics"] = key_metrics