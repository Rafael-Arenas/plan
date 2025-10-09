# src/planificador/services/domain/team/modules/diagnostic_operations.py

"""
Módulo de Operaciones de Diagnóstico del Dominio Team.

Este módulo implementa las operaciones de diagnóstico y monitoreo para
el servicio de dominio de equipos, proporcionando herramientas para
verificar el estado del sistema y realizar consultas de diagnóstico.

Características:
    - Consultas de equipos por fecha con tolerancia
    - Verificación de salud del servicio
    - Diagnósticos de rendimiento
    - Monitoreo de integridad del sistema
    - Métricas de operación

Principios de Diseño:
    - Health Monitoring: Supervisión continua del estado
    - Diagnostic Queries: Consultas especializadas para diagnóstico
    - Performance Tracking: Seguimiento de métricas de rendimiento
    - System Integrity: Verificación de integridad del sistema

Uso:
    ```python
    diagnostic_ops = TeamDomainDiagnosticOperations(team_repo, membership_repo)
    teams = await diagnostic_ops.get_teams_by_creation_date_with_tolerance(date, tolerance)
    health = await diagnostic_ops.check_service_health()
    ```
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pendulum
from loguru import logger

from planificador.repositories.team import TeamRepositoryFacade
from planificador.repositories.team_membership import TeamMembershipRepositoryFacade
from planificador.services.domain.team.interfaces.diagnostic_operations_interface import (
    ITeamDomainDiagnosticOperations
)
from planificador.schemas.team import Team
from planificador.exceptions.domain import (
    TeamDomainError
)
from planificador.exceptions.base import (
    ValidationError
)
from planificador.exceptions.repository import (
    TeamRepositoryError, TeamMembershipRepositoryError
)


class TeamDomainDiagnosticOperations(ITeamDomainDiagnosticOperations):
    """
    Implementación de operaciones de diagnóstico del dominio Team.
    
    Proporciona funcionalidades especializadas para diagnóstico,
    monitoreo y verificación de salud del servicio de equipos.
    
    Attributes:
        _team_repo: Repositorio de equipos
        _membership_repo: Repositorio de membresías
        _logger: Logger para registro de eventos
        _service_start_time: Tiempo de inicio del servicio
    """

    def __init__(
        self,
        team_repo: TeamRepositoryFacade,
        membership_repo: TeamMembershipRepositoryFacade
    ):
        """
        Inicializa las operaciones de diagnóstico del dominio Team.
        
        Args:
            team_repo: Repositorio de equipos
            membership_repo: Repositorio de membresías
        """
        self._team_repo = team_repo
        self._membership_repo = membership_repo
        self._logger = logger
        self._service_start_time = pendulum.now()
        
        self._logger.debug("TeamDomainDiagnosticOperations inicializado")

    async def get_teams_by_creation_date(
        self,
        creation_date: pendulum.DateTime,
        date_tolerance: int = 0
    ) -> List[Team]:
        """
        Obtiene equipos creados cerca de una fecha específica con tolerancia.
        
        Args:
            target_date: Fecha objetivo de creación
            tolerance_hours: Tolerancia en horas (por defecto 24)
            
        Returns:
            List[Team]: Lista de equipos creados dentro del rango
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        self._logger.debug(f"Buscando equipos creados en fecha: {creation_date}")
        
        try:
            # Validar parámetros de entrada
            if date_tolerance < 0:
                raise ValidationError("La tolerancia de fecha no puede ser negativa")
            
            # Calcular rango de fechas basado en la tolerancia en días
            start_date = creation_date.subtract(days=date_tolerance)
            end_date = creation_date.add(days=date_tolerance)
            
            self._logger.debug(f"Rango de búsqueda: {start_date} - {end_date}")
            
            # Buscar equipos en el rango de fechas
            teams = await self._team_repo.get_teams_by_creation_date_range(
                start_date=start_date,
                end_date=end_date
            )
            
            # Convertir a DTOs de salida
            team_outputs = []
            for team in teams:
                team_output = Team(
                    id=team.id,
                    name=team.name,
                    description=team.description,
                    department=team.department,
                    status=team.status,
                    created_at=team.created_at,
                    updated_at=team.updated_at
                )
                team_outputs.append(team_output)
            
            self._logger.debug(f"Encontrados {len(team_outputs)} equipos")
            return team_outputs
            
        except ValidationError:
            self._logger.error(f"Error de validación en get_teams_by_creation_date: {creation_date}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en get_teams_by_creation_date: {str(e)}")
            raise DiagnosticError(
                message=f"Error al obtener equipos por fecha de creación: {str(e)}",
                operation="get_teams_by_creation_date",
                context={"creation_date": str(creation_date), "date_tolerance": date_tolerance}
            )

    async def check_service_health(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud del servicio de dominio de equipos.
        
        Returns:
            Dict[str, Any]: Información detallada del estado de salud
            
        Raises:
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug("Verificando estado de salud del servicio")
            
            health_status = {
                "service": "TeamDomainService",
                "status": "healthy",
                "timestamp": pendulum.now().to_iso8601_string(),
                "uptime_seconds": int((pendulum.now() - self._service_start_time).total_seconds()),
                "checks": {},
                "metrics": {},
                "warnings": [],
                "errors": []
            }
            
            # Verificar conectividad de repositorios
            repo_health = await self._check_repository_health()
            health_status["checks"]["repositories"] = repo_health
            
            # Verificar integridad de datos básica
            data_health = await self._check_data_integrity()
            health_status["checks"]["data_integrity"] = data_health
            
            # Obtener métricas del sistema
            system_metrics = await self._get_system_metrics()
            health_status["metrics"] = system_metrics
            
            # Verificar rendimiento
            performance_check = await self._check_performance()
            health_status["checks"]["performance"] = performance_check
            
            # Determinar estado general
            all_checks_healthy = all(
                check.get("status") == "healthy" 
                for check in health_status["checks"].values()
            )
            
            if not all_checks_healthy:
                health_status["status"] = "degraded"
                health_status["warnings"].append("Algunos componentes presentan problemas")
            
            # Verificar métricas críticas
            if system_metrics.get("total_teams", 0) == 0:
                health_status["warnings"].append("No hay equipos en el sistema")
            
            if system_metrics.get("avg_response_time_ms", 0) > 1000:
                health_status["warnings"].append("Tiempo de respuesta elevado")
            
            # Si hay errores críticos, marcar como no saludable
            if health_status["errors"]:
                health_status["status"] = "unhealthy"
            
            self._logger.debug(f"Verificación de salud completada: {health_status['status']}")
            
            return health_status
            
        except Exception as e:
            self._logger.error(f"Error inesperado en verificación de salud: {e}")
            
            # Retornar estado de error
            return {
                "service": "TeamDomainService",
                "status": "unhealthy",
                "timestamp": pendulum.now().to_iso8601_string(),
                "uptime_seconds": int((pendulum.now() - self._service_start_time).total_seconds()),
                "checks": {},
                "metrics": {},
                "warnings": [],
                "errors": [f"Error crítico en verificación de salud: {str(e)}"]
            }

    # Métodos auxiliares privados para verificaciones de salud

    async def _check_repository_health(self) -> Dict[str, Any]:
        """Verifica la salud de los repositorios."""
        try:
            start_time = pendulum.now()
            
            # Intentar operación básica en repositorio de equipos
            try:
                teams_count = len(await self._team_repo.get_all())
                team_repo_status = "healthy"
                team_repo_error = None
            except Exception as e:
                teams_count = 0
                team_repo_status = "unhealthy"
                team_repo_error = str(e)
            
            # Intentar operación básica en repositorio de membresías
            try:
                # Simulamos una consulta básica
                membership_repo_status = "healthy"
                membership_repo_error = None
            except Exception as e:
                membership_repo_status = "unhealthy"
                membership_repo_error = str(e)
            
            response_time = (pendulum.now() - start_time).total_seconds() * 1000
            
            overall_status = "healthy" if (
                team_repo_status == "healthy" and membership_repo_status == "healthy"
            ) else "unhealthy"
            
            return {
                "status": overall_status,
                "response_time_ms": round(response_time, 2),
                "team_repository": {
                    "status": team_repo_status,
                    "teams_accessible": teams_count,
                    "error": team_repo_error
                },
                "membership_repository": {
                    "status": membership_repo_status,
                    "error": membership_repo_error
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Error en verificación de repositorios: {str(e)}"
            }

    async def _check_data_integrity(self) -> Dict[str, Any]:
        """Verifica la integridad básica de los datos."""
        try:
            start_time = pendulum.now()
            
            # Obtener muestra de equipos para verificación
            teams = await self._team_repo.get_all()
            
            integrity_issues = []
            teams_checked = 0
            
            # Verificar una muestra (máximo 10 equipos para no impactar rendimiento)
            sample_teams = teams[:10] if len(teams) > 10 else teams
            
            for team in sample_teams:
                teams_checked += 1
                
                # Verificar datos básicos
                if not team.name or len(team.name.strip()) < 2:
                    integrity_issues.append(f"Equipo {team.id}: nombre inválido")
                
                if not team.department:
                    integrity_issues.append(f"Equipo {team.id}: departamento faltante")
                
                # Verificar fechas
                if team.created_at and team.updated_at:
                    if team.created_at > team.updated_at:
                        integrity_issues.append(f"Equipo {team.id}: fechas inconsistentes")
            
            response_time = (pendulum.now() - start_time).total_seconds() * 1000
            
            status = "healthy" if len(integrity_issues) == 0 else "degraded"
            
            return {
                "status": status,
                "response_time_ms": round(response_time, 2),
                "teams_checked": teams_checked,
                "integrity_issues": integrity_issues,
                "issues_count": len(integrity_issues)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Error en verificación de integridad: {str(e)}"
            }

    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas del sistema."""
        try:
            start_time = pendulum.now()
            
            # Obtener métricas básicas
            teams = await self._team_repo.get_all()
            total_teams = len(teams)
            
            # Calcular métricas de distribución
            departments = {}
            for team in teams:
                dept = team.department or "Unknown"
                departments[dept] = departments.get(dept, 0) + 1
            
            # Simular tiempo de respuesta promedio
            response_time = (pendulum.now() - start_time).total_seconds() * 1000
            
            return {
                "total_teams": total_teams,
                "departments_count": len(departments),
                "department_distribution": departments,
                "avg_response_time_ms": round(response_time, 2),
                "service_uptime_seconds": int(
                    (pendulum.now() - self._service_start_time).total_seconds()
                ),
                "last_updated": pendulum.now().to_iso8601_string()
            }
            
        except Exception as e:
            return {
                "error": f"Error al obtener métricas: {str(e)}"
            }

    async def _check_performance(self) -> Dict[str, Any]:
        """Verifica el rendimiento del servicio."""
        try:
            # Realizar operaciones de prueba y medir tiempos
            performance_tests = []
            
            # Test 1: Obtener todos los equipos
            start_time = pendulum.now()
            teams = await self._team_repo.get_all()
            get_all_time = (pendulum.now() - start_time).total_seconds() * 1000
            
            performance_tests.append({
                "test": "get_all_teams",
                "response_time_ms": round(get_all_time, 2),
                "records_processed": len(teams),
                "status": "good" if get_all_time < 500 else "slow"
            })
            
            # Test 2: Búsqueda por nombre (si hay equipos)
            if teams:
                start_time = pendulum.now()
                await self._team_repo.get_team_by_name(teams[0].name)
                search_time = (pendulum.now() - start_time).total_seconds() * 1000
                
                performance_tests.append({
                    "test": "search_by_name",
                    "response_time_ms": round(search_time, 2),
                    "status": "good" if search_time < 200 else "slow"
                })
            
            # Determinar estado general de rendimiento
            slow_tests = [t for t in performance_tests if t["status"] == "slow"]
            overall_status = "good" if len(slow_tests) == 0 else "degraded"
            
            return {
                "status": overall_status,
                "tests": performance_tests,
                "slow_operations": len(slow_tests),
                "avg_response_time_ms": round(
                    sum(t["response_time_ms"] for t in performance_tests) / len(performance_tests), 2
                ) if performance_tests else 0
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Error en verificación de rendimiento: {str(e)}"
            }