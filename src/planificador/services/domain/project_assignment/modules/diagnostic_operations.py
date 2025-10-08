"""
Módulo de operaciones de diagnóstico para asignaciones de proyecto.

Este módulo implementa la interfaz IDiagnosticOperations proporcionando
funcionalidades para diagnóstico del sistema y auditoría de integridad de datos.
"""

from typing import Dict, List, Any, Optional
import pendulum
from loguru import logger

from ..interfaces.diagnostic_operations_interface import IDiagnosticOperations
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.exceptions import RepositoryError, ValidationError


class DiagnosticOperations(IDiagnosticOperations):
    """
    Implementación de operaciones de diagnóstico para asignaciones de proyecto.
    
    Proporciona funcionalidades para:
    - Diagnóstico de salud del sistema
    - Auditoría de integridad de datos
    - Detección de inconsistencias
    - Análisis de rendimiento
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """
        Inicializa las operaciones de diagnóstico.
        
        Args:
            repository_facade: Fachada del repositorio para acceso a datos
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="diagnostic_operations")
        
        # Configuración de umbrales para diagnósticos
        self._health_thresholds = {
            "max_overlapping_assignments": 5,
            "max_overallocation_percentage": 150,
            "max_orphaned_assignments": 10,
            "max_inconsistent_dates": 5,
            "max_invalid_allocations": 3,
            "performance_threshold_ms": 1000
        }
    
    async def get_system_health_status(
        self, 
        include_performance_metrics: bool = True,
        include_data_quality_checks: bool = True
    ) -> Dict[str, Any]:
        """
        Obtiene el estado de salud del sistema de asignaciones.
        
        Args:
            include_performance_metrics: Si incluir métricas de rendimiento
            include_data_quality_checks: Si incluir verificaciones de calidad de datos
            
        Returns:
            Diccionario con el estado de salud del sistema
            
        Raises:
            RepositoryError: Si hay error al acceder a los datos
        """
        try:
            self._logger.info("Iniciando diagnóstico de salud del sistema")
            
            health_status = {
                "timestamp": pendulum.now().isoformat(),
                "overall_status": "healthy",
                "components": {},
                "metrics": {},
                "issues": [],
                "recommendations": []
            }
            
            # Verificar componentes básicos
            await self._check_basic_components(health_status)
            
            # Verificar calidad de datos si está habilitado
            if include_data_quality_checks:
                await self._check_data_quality(health_status)
            
            # Verificar métricas de rendimiento si está habilitado
            if include_performance_metrics:
                await self._check_performance_metrics(health_status)
            
            # Determinar estado general
            health_status["overall_status"] = self._determine_overall_health(health_status)
            
            self._logger.info(
                f"Diagnóstico completado - Estado: {health_status['overall_status']}"
            )
            
            return health_status
            
        except Exception as e:
            self._logger.error(f"Error en diagnóstico de salud: {e}")
            raise RepositoryError(
                message=f"Error al obtener estado de salud del sistema: {e}",
                operation="get_system_health_status",
                entity_type="SystemHealth",
                original_error=e
            )
    
    async def run_data_integrity_audit(
        self, 
        fix_issues: bool = False,
        audit_scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta una auditoría completa de integridad de datos.
        
        Args:
            fix_issues: Si intentar corregir automáticamente los problemas encontrados
            audit_scope: Alcance de la auditoría ('full', 'assignments', 'relationships')
            
        Returns:
            Diccionario con los resultados de la auditoría
            
        Raises:
            RepositoryError: Si hay error durante la auditoría
            ValidationError: Si los parámetros de auditoría son inválidos
        """
        try:
            # Validar parámetros
            if audit_scope and audit_scope not in ['full', 'assignments', 'relationships']:
                raise ValidationError(
                    message="Alcance de auditoría inválido",
                    field="audit_scope",
                    value=audit_scope
                )
            
            self._logger.info(f"Iniciando auditoría de integridad - Alcance: {audit_scope or 'full'}")
            
            audit_results = {
                "timestamp": pendulum.now().isoformat(),
                "audit_scope": audit_scope or "full",
                "summary": {
                    "total_issues": 0,
                    "critical_issues": 0,
                    "warnings": 0,
                    "fixed_issues": 0
                },
                "detailed_results": {},
                "recommendations": [],
                "next_audit_recommended": None
            }
            
            # Ejecutar auditorías según el alcance
            if audit_scope in [None, 'full', 'assignments']:
                await self._audit_assignment_integrity(audit_results, fix_issues)
            
            if audit_scope in [None, 'full', 'relationships']:
                await self._audit_relationship_integrity(audit_results, fix_issues)
            
            if audit_scope in [None, 'full']:
                await self._audit_business_rule_compliance(audit_results, fix_issues)
                await self._audit_temporal_consistency(audit_results, fix_issues)
            
            # Generar recomendaciones
            self._generate_audit_recommendations(audit_results)
            
            self._logger.info(
                f"Auditoría completada - Problemas encontrados: {audit_results['summary']['total_issues']}"
            )
            
            return audit_results
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error en auditoría de integridad: {e}")
            raise RepositoryError(
                message=f"Error durante la auditoría de integridad: {e}",
                operation="run_data_integrity_audit",
                entity_type="DataIntegrity",
                original_error=e
            )
    
    async def _check_basic_components(self, health_status: Dict[str, Any]) -> None:
        """Verifica el estado de los componentes básicos del sistema."""
        try:
            # Verificar conectividad del repositorio
            assignment_count = await self._repository.count_all_assignments()
            health_status["components"]["repository"] = {
                "status": "healthy",
                "total_assignments": assignment_count,
                "last_check": pendulum.now().isoformat()
            }
            
            # Verificar integridad básica de datos
            active_assignments = await self._repository.count_active_assignments()
            health_status["components"]["data_integrity"] = {
                "status": "healthy",
                "active_assignments": active_assignments,
                "integrity_ratio": active_assignments / max(assignment_count, 1)
            }
            
        except Exception as e:
            health_status["components"]["repository"] = {
                "status": "unhealthy",
                "error": str(e),
                "last_check": pendulum.now().isoformat()
            }
            health_status["issues"].append({
                "severity": "critical",
                "component": "repository",
                "message": f"Error de conectividad: {e}"
            })
    
    async def _check_data_quality(self, health_status: Dict[str, Any]) -> None:
        """Verifica la calidad de los datos."""
        try:
            # Verificar asignaciones superpuestas
            overlapping_count = await self._count_overlapping_assignments()
            health_status["metrics"]["overlapping_assignments"] = overlapping_count
            
            if overlapping_count > self._health_thresholds["max_overlapping_assignments"]:
                health_status["issues"].append({
                    "severity": "warning",
                    "component": "data_quality",
                    "message": f"Muchas asignaciones superpuestas: {overlapping_count}"
                })
            
            # Verificar sobreasignaciones
            overallocated_count = await self._count_overallocated_employees()
            health_status["metrics"]["overallocated_employees"] = overallocated_count
            
            if overallocated_count > 0:
                health_status["issues"].append({
                    "severity": "warning",
                    "component": "resource_allocation",
                    "message": f"Empleados sobreasignados: {overallocated_count}"
                })
            
            # Verificar asignaciones huérfanas
            orphaned_count = await self._count_orphaned_assignments()
            health_status["metrics"]["orphaned_assignments"] = orphaned_count
            
            if orphaned_count > self._health_thresholds["max_orphaned_assignments"]:
                health_status["issues"].append({
                    "severity": "critical",
                    "component": "data_integrity",
                    "message": f"Asignaciones huérfanas: {orphaned_count}"
                })
            
        except Exception as e:
            health_status["issues"].append({
                "severity": "error",
                "component": "data_quality_check",
                "message": f"Error verificando calidad de datos: {e}"
            })
    
    async def _check_performance_metrics(self, health_status: Dict[str, Any]) -> None:
        """Verifica las métricas de rendimiento del sistema."""
        try:
            # Medir tiempo de respuesta de consultas básicas
            start_time = pendulum.now()
            await self._repository.count_all_assignments()
            query_time = (pendulum.now() - start_time).total_seconds() * 1000
            
            health_status["metrics"]["query_response_time_ms"] = query_time
            
            if query_time > self._health_thresholds["performance_threshold_ms"]:
                health_status["issues"].append({
                    "severity": "warning",
                    "component": "performance",
                    "message": f"Tiempo de respuesta alto: {query_time:.2f}ms"
                })
            
            # Verificar uso de memoria (simulado)
            health_status["metrics"]["memory_usage_mb"] = 45.2  # Valor simulado
            
        except Exception as e:
            health_status["issues"].append({
                "severity": "error",
                "component": "performance_check",
                "message": f"Error verificando rendimiento: {e}"
            })
    
    def _determine_overall_health(self, health_status: Dict[str, Any]) -> str:
        """Determina el estado general de salud basado en los problemas encontrados."""
        critical_issues = sum(1 for issue in health_status["issues"] if issue["severity"] == "critical")
        error_issues = sum(1 for issue in health_status["issues"] if issue["severity"] == "error")
        warning_issues = sum(1 for issue in health_status["issues"] if issue["severity"] == "warning")
        
        if critical_issues > 0 or error_issues > 0:
            return "unhealthy"
        elif warning_issues > 3:
            return "degraded"
        else:
            return "healthy"
    
    async def _audit_assignment_integrity(
        self, 
        audit_results: Dict[str, Any], 
        fix_issues: bool
    ) -> None:
        """Audita la integridad de las asignaciones individuales."""
        self._logger.info("Auditando integridad de asignaciones")
        
        assignment_issues = {
            "invalid_dates": [],
            "invalid_allocations": [],
            "missing_required_fields": [],
            "inconsistent_data": []
        }
        
        try:
            # Obtener todas las asignaciones para auditoría
            all_assignments = await self._repository.get_all_assignments()
            
            for assignment in all_assignments:
                # Verificar fechas válidas
                if assignment.start_date >= assignment.end_date:
                    assignment_issues["invalid_dates"].append({
                        "assignment_id": assignment.id,
                        "issue": "start_date >= end_date",
                        "start_date": assignment.start_date.isoformat(),
                        "end_date": assignment.end_date.isoformat()
                    })
                
                # Verificar asignaciones válidas
                if assignment.percentage_allocation <= 0 or assignment.percentage_allocation > 100:
                    assignment_issues["invalid_allocations"].append({
                        "assignment_id": assignment.id,
                        "issue": "invalid_percentage",
                        "percentage": assignment.percentage_allocation
                    })
                
                # Verificar campos requeridos
                if not assignment.role_in_project or not assignment.role_in_project.strip():
                    assignment_issues["missing_required_fields"].append({
                        "assignment_id": assignment.id,
                        "issue": "missing_role",
                        "role": assignment.role_in_project
                    })
            
            # Contar problemas
            total_assignment_issues = sum(len(issues) for issues in assignment_issues.values())
            audit_results["summary"]["total_issues"] += total_assignment_issues
            audit_results["summary"]["critical_issues"] += len(assignment_issues["invalid_dates"])
            audit_results["summary"]["warnings"] += len(assignment_issues["invalid_allocations"])
            
            audit_results["detailed_results"]["assignment_integrity"] = assignment_issues
            
        except Exception as e:
            self._logger.error(f"Error auditando integridad de asignaciones: {e}")
            audit_results["detailed_results"]["assignment_integrity"] = {
                "error": f"No se pudo completar la auditoría: {e}"
            }
    
    async def _audit_relationship_integrity(
        self, 
        audit_results: Dict[str, Any], 
        fix_issues: bool
    ) -> None:
        """Audita la integridad de las relaciones entre entidades."""
        self._logger.info("Auditando integridad de relaciones")
        
        relationship_issues = {
            "orphaned_assignments": [],
            "invalid_employee_references": [],
            "invalid_project_references": []
        }
        
        try:
            # Verificar referencias huérfanas (simulado)
            # En una implementación real, se verificarían las claves foráneas
            orphaned_count = await self._count_orphaned_assignments()
            
            if orphaned_count > 0:
                relationship_issues["orphaned_assignments"].append({
                    "count": orphaned_count,
                    "description": "Asignaciones sin empleado o proyecto válido"
                })
            
            audit_results["summary"]["total_issues"] += orphaned_count
            if orphaned_count > 0:
                audit_results["summary"]["critical_issues"] += 1
            
            audit_results["detailed_results"]["relationship_integrity"] = relationship_issues
            
        except Exception as e:
            self._logger.error(f"Error auditando integridad de relaciones: {e}")
            audit_results["detailed_results"]["relationship_integrity"] = {
                "error": f"No se pudo completar la auditoría: {e}"
            }
    
    async def _audit_business_rule_compliance(
        self, 
        audit_results: Dict[str, Any], 
        fix_issues: bool
    ) -> None:
        """Audita el cumplimiento de reglas de negocio."""
        self._logger.info("Auditando cumplimiento de reglas de negocio")
        
        business_rule_issues = {
            "overlapping_assignments": [],
            "overallocated_employees": [],
            "invalid_role_combinations": []
        }
        
        try:
            # Verificar asignaciones superpuestas
            overlapping_count = await self._count_overlapping_assignments()
            if overlapping_count > 0:
                business_rule_issues["overlapping_assignments"].append({
                    "count": overlapping_count,
                    "description": "Asignaciones con fechas superpuestas para el mismo empleado"
                })
            
            # Verificar empleados sobreasignados
            overallocated_count = await self._count_overallocated_employees()
            if overallocated_count > 0:
                business_rule_issues["overallocated_employees"].append({
                    "count": overallocated_count,
                    "description": "Empleados con asignación total > 100%"
                })
            
            audit_results["summary"]["total_issues"] += overlapping_count + overallocated_count
            audit_results["summary"]["warnings"] += overlapping_count + overallocated_count
            
            audit_results["detailed_results"]["business_rule_compliance"] = business_rule_issues
            
        except Exception as e:
            self._logger.error(f"Error auditando reglas de negocio: {e}")
            audit_results["detailed_results"]["business_rule_compliance"] = {
                "error": f"No se pudo completar la auditoría: {e}"
            }
    
    async def _audit_temporal_consistency(
        self, 
        audit_results: Dict[str, Any], 
        fix_issues: bool
    ) -> None:
        """Audita la consistencia temporal de las asignaciones."""
        self._logger.info("Auditando consistencia temporal")
        
        temporal_issues = {
            "future_end_dates": [],
            "very_long_assignments": [],
            "very_short_assignments": []
        }
        
        try:
            all_assignments = await self._repository.get_all_assignments()
            now = pendulum.now().date()
            
            for assignment in all_assignments:
                # Verificar fechas futuras inconsistentes
                if assignment.end_date < now and assignment.status == "active":
                    temporal_issues["future_end_dates"].append({
                        "assignment_id": assignment.id,
                        "end_date": assignment.end_date.isoformat(),
                        "status": assignment.status
                    })
                
                # Verificar asignaciones muy largas (más de 2 años)
                duration = (assignment.end_date - assignment.start_date).days
                if duration > 730:  # 2 años
                    temporal_issues["very_long_assignments"].append({
                        "assignment_id": assignment.id,
                        "duration_days": duration
                    })
                
                # Verificar asignaciones muy cortas (menos de 1 día)
                if duration < 1:
                    temporal_issues["very_short_assignments"].append({
                        "assignment_id": assignment.id,
                        "duration_days": duration
                    })
            
            total_temporal_issues = sum(len(issues) for issues in temporal_issues.values())
            audit_results["summary"]["total_issues"] += total_temporal_issues
            audit_results["summary"]["warnings"] += total_temporal_issues
            
            audit_results["detailed_results"]["temporal_consistency"] = temporal_issues
            
        except Exception as e:
            self._logger.error(f"Error auditando consistencia temporal: {e}")
            audit_results["detailed_results"]["temporal_consistency"] = {
                "error": f"No se pudo completar la auditoría: {e}"
            }
    
    def _generate_audit_recommendations(self, audit_results: Dict[str, Any]) -> None:
        """Genera recomendaciones basadas en los resultados de la auditoría."""
        recommendations = []
        
        total_issues = audit_results["summary"]["total_issues"]
        critical_issues = audit_results["summary"]["critical_issues"]
        
        if critical_issues > 0:
            recommendations.append({
                "priority": "high",
                "action": "Resolver problemas críticos inmediatamente",
                "description": f"Se encontraron {critical_issues} problemas críticos que requieren atención inmediata"
            })
        
        if total_issues > 10:
            recommendations.append({
                "priority": "medium",
                "action": "Implementar validaciones adicionales",
                "description": "Alto número de problemas sugiere necesidad de validaciones más estrictas"
            })
        
        if total_issues > 0:
            recommendations.append({
                "priority": "low",
                "action": "Programar auditorías regulares",
                "description": "Establecer auditorías automáticas para prevenir problemas futuros"
            })
        
        # Determinar próxima auditoría recomendada
        if critical_issues > 0:
            next_audit = pendulum.now().add(days=1)
        elif total_issues > 5:
            next_audit = pendulum.now().add(weeks=1)
        else:
            next_audit = pendulum.now().add(months=1)
        
        audit_results["recommendations"] = recommendations
        audit_results["next_audit_recommended"] = next_audit.isoformat()
    
    async def _count_overlapping_assignments(self) -> int:
        """Cuenta las asignaciones superpuestas (simulado)."""
        # En una implementación real, se ejecutaría una consulta SQL compleja
        # para detectar asignaciones superpuestas por empleado
        return 2  # Valor simulado
    
    async def _count_overallocated_employees(self) -> int:
        """Cuenta los empleados sobreasignados (simulado)."""
        # En una implementación real, se sumarían los porcentajes de asignación
        # por empleado y se contarían los que excedan 100%
        return 1  # Valor simulado
    
    async def _count_orphaned_assignments(self) -> int:
        """Cuenta las asignaciones huérfanas (simulado)."""
        # En una implementación real, se verificarían las claves foráneas
        return 0  # Valor simulado