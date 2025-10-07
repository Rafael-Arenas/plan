# -*- coding: utf-8 -*-
"""
Módulo de Operaciones de Planificación de Fechas para Proyectos

Implementa funcionalidades avanzadas de planificación temporal,
cálculo de fechas, gestión de calendarios y análisis de cronogramas.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import pendulum
from pendulum import DateTime, Duration

from planificador.models.project import Project, ProjectStatus
from planificador.schemas.project.project import (
    ProjectDurationSchema,
    ProjectDatesUpdateSchema,
    ValidationResultSchema,
    ProjectTimelineSchema,
    ProjectAdvancedFilters
)
from planificador.repositories.project.project_repository_facade import ProjectRepositoryFacade
from planificador.exceptions.domain.project_domain_exceptions import (
    ProjectDateValidationError,
    ProjectPlanningError,
    ProjectTimelineConflictError,
    create_project_business_rule_error
)
from planificador.config.config import settings


class ProjectDatePlanningOperations:
    """
    Operaciones de planificación de fechas para proyectos.
    
    Maneja cálculos temporales, validaciones de fechas, planificación
    de cronogramas y análisis de disponibilidad temporal.
    """

    def __init__(self, repository_facade: ProjectRepositoryFacade):
        """
        Inicializa las operaciones de planificación de fechas.
        
        Args:
            repository_facade: Fachada del repositorio de proyectos
        """
        self._repository_facade = repository_facade
        self._logger = logger.bind(module="date_planning_operations")
        
        # Configuración de días laborables (Lunes=0, Domingo=6)
        self.business_days = [0, 1, 2, 3, 4]  # Lunes a Viernes
        self.timezone = settings.TIMEZONE if hasattr(settings, 'TIMEZONE') else 'America/Santiago'

    async def calculate_project_duration(
        self,
        start_date: DateTime,
        end_date: DateTime,
        include_weekends: bool = False
    ) -> ProjectDurationSchema:
        """
        Calcula la duración de un proyecto considerando días laborables.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            include_weekends: Incluir fines de semana en el cálculo
            
        Returns:
            Dict[str, Any]: Información detallada de duración
        """
        self._logger.debug(f"Calculando duración del proyecto: {start_date} - {end_date}")
        
        try:
            # Validar fechas
            await self._validate_date_range(start_date, end_date)
            
            # Convertir a objetos Pendulum para cálculos avanzados
            start_dt = pendulum.parse(start_date.isoformat(), tz=self.timezone)
            end_dt = pendulum.parse(end_date.isoformat(), tz=self.timezone)
            
            # Calcular duración total
            total_duration = end_dt - start_dt
            total_days = total_duration.days + 1  # Incluir el día de inicio
            
            # Calcular días laborables
            business_days_count = 0
            weekend_days_count = 0
            current_date = start_dt
            
            while current_date <= end_dt:
                if current_date.weekday() in self.business_days:
                    business_days_count += 1
                else:
                    weekend_days_count += 1
                current_date = current_date.add(days=1)
            
            # Calcular semanas y meses
            weeks = total_days / 7
            months = total_duration.total_seconds() / (30 * 24 * 3600)  # Aproximado
            
            duration_info = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_days": total_days,
                "business_days": business_days_count,
                "weekend_days": weekend_days_count,
                "weeks": round(weeks, 2),
                "months": round(months, 2),
                "duration_breakdown": {
                    "years": total_duration.years,
                    "months": total_duration.months,
                    "days": total_duration.days,
                    "total_seconds": total_duration.total_seconds()
                },
                "working_duration": {
                    "business_days_only": business_days_count,
                    "estimated_hours": business_days_count * 8,  # 8 horas por día laboral
                    "estimated_weeks": round(business_days_count / 5, 2)  # 5 días laborables por semana
                }
            }
            
            self._logger.debug(f"Duración calculada: {total_days} días totales, {business_days_count} días laborables")
            return duration_info
            
        except Exception as e:
            self._logger.error(f"Error calculando duración del proyecto: {e}")
            raise ProjectPlanningError(
                message=f"Error calculando duración del proyecto: {e}",
                operation="calculate_project_duration",
                details={"start_date": start_date, "end_date": end_date},
                original_error=e
            )

    async def suggest_optimal_start_date(
        self,
        desired_end_date: date,
        estimated_duration_days: int,
        avoid_weekends: bool = True,
        buffer_days: int = 0
    ) -> ProjectDatesUpdateSchema:
        """
        Sugiere una fecha de inicio óptima basada en la fecha de fin deseada.
        
        Args:
            desired_end_date: Fecha de fin deseada
            estimated_duration_days: Duración estimada en días
            avoid_weekends: Evitar iniciar en fines de semana
            buffer_days: Días de buffer adicionales
            
        Returns:
            Dict[str, Any]: Sugerencia de fecha de inicio con alternativas
        """
        self._logger.debug(f"Sugiriendo fecha de inicio óptima para terminar el {desired_end_date}")
        
        try:
            end_dt = pendulum.parse(desired_end_date.isoformat(), tz=self.timezone)
            
            # Calcular fecha de inicio base
            if avoid_weekends:
                # Calcular considerando solo días laborables
                business_days_needed = estimated_duration_days + buffer_days
                current_date = end_dt
                days_counted = 0
                
                while days_counted < business_days_needed:
                    current_date = current_date.subtract(days=1)
                    if current_date.weekday() in self.business_days:
                        days_counted += 1
                
                suggested_start = current_date
            else:
                # Calcular incluyendo fines de semana
                total_days_needed = estimated_duration_days + buffer_days
                suggested_start = end_dt.subtract(days=total_days_needed - 1)
            
            # Ajustar si cae en fin de semana
            if avoid_weekends and suggested_start.weekday() not in self.business_days:
                # Mover al viernes anterior
                while suggested_start.weekday() not in self.business_days:
                    suggested_start = suggested_start.subtract(days=1)
            
            # Generar alternativas
            alternatives = []
            for i in range(1, 4):  # 3 alternativas
                alt_start = suggested_start.subtract(days=i)
                if avoid_weekends and alt_start.weekday() not in self.business_days:
                    # Ajustar al día laborable anterior
                    while alt_start.weekday() not in self.business_days:
                        alt_start = alt_start.subtract(days=1)
                
                alternatives.append({
                    "start_date": alt_start.date().isoformat(),
                    "buffer_days": buffer_days + i,
                    "is_business_day": alt_start.weekday() in self.business_days
                })
            
            # Verificar conflictos con proyectos existentes
            conflicts = await self._check_date_conflicts(
                suggested_start.date(), 
                desired_end_date
            )
            
            suggestion = {
                "desired_end_date": desired_end_date.isoformat(),
                "estimated_duration_days": estimated_duration_days,
                "buffer_days": buffer_days,
                "suggested_start_date": suggested_start.date().isoformat(),
                "is_business_day": suggested_start.weekday() in self.business_days,
                "day_of_week": suggested_start.format('dddd'),
                "alternatives": alternatives,
                "duration_analysis": await self.calculate_project_duration(
                    suggested_start.date(), 
                    desired_end_date, 
                    not avoid_weekends
                ),
                "potential_conflicts": conflicts,
                "recommendations": await self._generate_start_date_recommendations(
                    suggested_start.date(), 
                    desired_end_date,
                    conflicts
                )
            }
            
            self._logger.debug(f"Fecha de inicio sugerida: {suggested_start.date()}")
            return suggestion
            
        except Exception as e:
            self._logger.error(f"Error sugiriendo fecha de inicio óptima: {e}")
            raise ProjectPlanningError(
                message=f"Error sugiriendo fecha de inicio óptima: {e}",
                operation="suggest_optimal_start_date",
                details={
                    "desired_end_date": desired_end_date,
                    "estimated_duration_days": estimated_duration_days
                },
                original_error=e
            )

    async def suggest_optimal_end_date(
        self,
        start_date: date,
        estimated_duration_days: int,
        avoid_weekends: bool = True,
        buffer_days: int = 0
    ) -> ProjectDatesUpdateSchema:
        """
        Sugiere una fecha de fin óptima basada en la fecha de inicio.
        
        Args:
            start_date: Fecha de inicio
            estimated_duration_days: Duración estimada en días
            avoid_weekends: Evitar terminar en fines de semana
            buffer_days: Días de buffer adicionales
            
        Returns:
            Dict[str, Any]: Sugerencia de fecha de fin con alternativas
        """
        self._logger.debug(f"Sugiriendo fecha de fin óptima desde {start_date}")
        
        try:
            start_dt = pendulum.parse(start_date.isoformat(), tz=self.timezone)
            
            # Calcular fecha de fin base
            if avoid_weekends:
                # Calcular considerando solo días laborables
                business_days_needed = estimated_duration_days + buffer_days
                current_date = start_dt
                days_counted = 0
                
                while days_counted < business_days_needed:
                    if current_date.weekday() in self.business_days:
                        days_counted += 1
                    if days_counted < business_days_needed:
                        current_date = current_date.add(days=1)
                
                suggested_end = current_date
            else:
                # Calcular incluyendo fines de semana
                total_days_needed = estimated_duration_days + buffer_days
                suggested_end = start_dt.add(days=total_days_needed - 1)
            
            # Ajustar si cae en fin de semana
            if avoid_weekends and suggested_end.weekday() not in self.business_days:
                # Mover al viernes anterior
                while suggested_end.weekday() not in self.business_days:
                    suggested_end = suggested_end.subtract(days=1)
            
            # Generar alternativas
            alternatives = []
            for i in range(1, 4):  # 3 alternativas
                alt_end = suggested_end.add(days=i)
                if avoid_weekends and alt_end.weekday() not in self.business_days:
                    # Ajustar al siguiente día laborable
                    while alt_end.weekday() not in self.business_days:
                        alt_end = alt_end.add(days=1)
                
                alternatives.append({
                    "end_date": alt_end.date().isoformat(),
                    "additional_days": i,
                    "is_business_day": alt_end.weekday() in self.business_days
                })
            
            # Verificar conflictos con proyectos existentes
            conflicts = await self._check_date_conflicts(start_date, suggested_end.date())
            
            suggestion = {
                "start_date": start_date.isoformat(),
                "estimated_duration_days": estimated_duration_days,
                "buffer_days": buffer_days,
                "suggested_end_date": suggested_end.date().isoformat(),
                "is_business_day": suggested_end.weekday() in self.business_days,
                "day_of_week": suggested_end.format('dddd'),
                "alternatives": alternatives,
                "duration_analysis": await self.calculate_project_duration(
                    start_date, 
                    suggested_end.date(), 
                    not avoid_weekends
                ),
                "potential_conflicts": conflicts,
                "recommendations": await self._generate_end_date_recommendations(
                    start_date, 
                    suggested_end.date(),
                    conflicts
                )
            }
            
            self._logger.debug(f"Fecha de fin sugerida: {suggested_end.date()}")
            return suggestion
            
        except Exception as e:
            self._logger.error(f"Error sugiriendo fecha de fin óptima: {e}")
            raise ProjectPlanningError(
                message=f"Error sugiriendo fecha de fin óptima: {e}",
                operation="suggest_optimal_end_date",
                details={
                    "start_date": start_date,
                    "estimated_duration_days": estimated_duration_days
                },
                original_error=e
            )

    async def analyze_timeline_feasibility(
        self,
        start_date: date,
        end_date: date,
        required_resources: Optional[List[int]] = None,
        client_id: Optional[int] = None
    ) -> ValidationResultSchema:
        """
        Analiza la viabilidad de un cronograma propuesto.
        
        Args:
            start_date: Fecha de inicio propuesta
            end_date: Fecha de fin propuesta
            required_resources: Lista de IDs de recursos requeridos
            client_id: ID del cliente (para verificar otros proyectos)
            
        Returns:
            Dict[str, Any]: Análisis de viabilidad del cronograma
        """
        self._logger.debug(f"Analizando viabilidad del cronograma: {start_date} - {end_date}")
        
        try:
            # Validar fechas básicas
            await self._validate_date_range(start_date, end_date)
            
            # Calcular duración del proyecto
            duration_info = await self.calculate_project_duration(start_date, end_date)
            
            # Verificar conflictos con proyectos existentes
            conflicts = await self._check_date_conflicts(start_date, end_date, client_id)
            
            # Analizar disponibilidad de recursos (si se proporcionan)
            resource_availability = {}
            if required_resources:
                resource_availability = await self._analyze_resource_availability(
                    start_date, end_date, required_resources
                )
            
            # Verificar días festivos y períodos especiales
            holidays_impact = await self._analyze_holidays_impact(start_date, end_date)
            
            # Calcular score de viabilidad
            feasibility_score = await self._calculate_feasibility_score(
                duration_info, conflicts, resource_availability, holidays_impact
            )
            
            # Generar recomendaciones
            recommendations = await self._generate_feasibility_recommendations(
                start_date, end_date, conflicts, resource_availability, holidays_impact
            )
            
            analysis = {
                "timeline": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "is_valid": len(conflicts) == 0,
                    "duration_info": duration_info
                },
                "feasibility_score": feasibility_score,
                "conflicts": conflicts,
                "resource_availability": resource_availability,
                "holidays_impact": holidays_impact,
                "recommendations": recommendations,
                "risk_factors": await self._identify_risk_factors(
                    start_date, end_date, conflicts, resource_availability
                ),
                "alternative_timelines": await self._suggest_alternative_timelines(
                    start_date, end_date, conflicts
                )
            }
            
            self._logger.debug(f"Análisis de viabilidad completado. Score: {feasibility_score}")
            return analysis
            
        except Exception as e:
            self._logger.error(f"Error analizando viabilidad del cronograma: {e}")
            raise ProjectPlanningError(
                message=f"Error analizando viabilidad del cronograma: {e}",
                operation="analyze_timeline_feasibility",
                details={"start_date": start_date, "end_date": end_date},
                original_error=e
            )

    async def get_optimal_project_schedule(
        self,
        projects_data: List[Dict[str, Any]],
        optimization_criteria: str = "minimize_conflicts"
    ) -> ProjectTimelineSchema:
        """
        Calcula un cronograma óptimo para múltiples proyectos.
        
        Args:
            projects_data: Lista de datos de proyectos a programar
            optimization_criteria: Criterio de optimización
            
        Returns:
            Dict[str, Any]: Cronograma optimizado
        """
        self._logger.debug(f"Calculando cronograma óptimo para {len(projects_data)} proyectos")
        
        try:
            optimized_schedule = {
                "projects": [],
                "optimization_criteria": optimization_criteria,
                "total_conflicts": 0,
                "timeline_span": {},
                "resource_utilization": {},
                "recommendations": []
            }
            
            # Ordenar proyectos por prioridad y fechas deseadas
            sorted_projects = await self._sort_projects_for_optimization(
                projects_data, optimization_criteria
            )
            
            scheduled_projects = []
            
            for project_data in sorted_projects:
                # Calcular fechas óptimas para este proyecto
                optimal_dates = await self._calculate_optimal_dates_for_project(
                    project_data, scheduled_projects
                )
                
                # Verificar y resolver conflictos
                resolved_dates = await self._resolve_scheduling_conflicts(
                    optimal_dates, scheduled_projects
                )
                
                # Agregar proyecto al cronograma
                scheduled_project = {
                    "project_id": project_data.get("id"),
                    "project_name": project_data.get("name"),
                    "original_start": project_data.get("desired_start_date"),
                    "original_end": project_data.get("desired_end_date"),
                    "optimized_start": resolved_dates["start_date"],
                    "optimized_end": resolved_dates["end_date"],
                    "duration_days": resolved_dates["duration_days"],
                    "adjustments_made": resolved_dates["adjustments"],
                    "conflicts_resolved": resolved_dates["conflicts_resolved"]
                }
                
                scheduled_projects.append(scheduled_project)
                optimized_schedule["projects"].append(scheduled_project)
            
            # Calcular métricas del cronograma optimizado
            optimized_schedule.update(
                await self._calculate_schedule_metrics(scheduled_projects)
            )
            
            # Generar recomendaciones finales
            optimized_schedule["recommendations"] = await self._generate_schedule_recommendations(
                scheduled_projects, optimization_criteria
            )
            
            self._logger.debug("Cronograma óptimo calculado exitosamente")
            return optimized_schedule
            
        except Exception as e:
            self._logger.error(f"Error calculando cronograma óptimo: {e}")
            raise ProjectPlanningError(
                message=f"Error calculando cronograma óptimo: {e}",
                operation="get_optimal_project_schedule",
                original_error=e
            )

    async def validate_project_dates(
        self,
        project_data: Dict[str, Any],
        operation: str = "create"
    ) -> ValidationResultSchema:
        """
        Valida las fechas de un proyecto según reglas de negocio.
        
        Args:
            project_data: Datos del proyecto a validar
            operation: Tipo de operación (create, update)
            
        Returns:
            Dict[str, Any]: Resultado de la validación
        """
        self._logger.debug(f"Validando fechas del proyecto para operación: {operation}")
        
        try:
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "suggestions": []
            }
            
            start_date = project_data.get("start_date")
            end_date = project_data.get("end_date")
            
            # Validaciones básicas
            if start_date and end_date:
                try:
                    await self._validate_date_range(start_date, end_date)
                except ProjectDateValidationError as e:
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(str(e))
            
            # Validar fecha de inicio no sea en el pasado (para nuevos proyectos)
            if operation == "create" and start_date:
                today = pendulum.now(self.timezone).date()
                if start_date < today:
                    validation_result["warnings"].append(
                        f"La fecha de inicio ({start_date}) es anterior a hoy ({today})"
                    )
            
            # Validar duración mínima y máxima
            if start_date and end_date:
                duration_info = await self.calculate_project_duration(start_date, end_date)
                
                if duration_info["total_days"] < 1:
                    validation_result["is_valid"] = False
                    validation_result["errors"].append("La duración del proyecto debe ser al menos 1 día")
                
                if duration_info["total_days"] > 365 * 2:  # 2 años máximo
                    validation_result["warnings"].append(
                        f"El proyecto tiene una duración muy larga: {duration_info['total_days']} días"
                    )
                
                # Sugerir ajustes si termina en fin de semana
                end_dt = pendulum.parse(end_date.isoformat(), tz=self.timezone)
                if end_dt.weekday() not in self.business_days:
                    validation_result["suggestions"].append(
                        f"Considere mover la fecha de fin al viernes anterior para evitar terminar en {end_dt.format('dddd')}"
                    )
            
            # Verificar conflictos con otros proyectos
            if start_date and end_date:
                conflicts = await self._check_date_conflicts(
                    start_date, end_date, project_data.get("client_id")
                )
                
                if conflicts:
                    validation_result["warnings"].extend([
                        f"Conflicto potencial con proyecto: {conflict['project_name']}"
                        for conflict in conflicts
                    ])
            
            # Validaciones específicas por operación
            if operation == "update":
                # Validar que los cambios no afecten proyectos dependientes
                project_id = project_data.get("id")
                if project_id:
                    dependency_impact = await self._validate_date_change_impact(
                        project_id, start_date, end_date
                    )
                    
                    if dependency_impact["has_impact"]:
                        validation_result["warnings"].extend(
                            dependency_impact["warnings"]
                        )
            
            self._logger.debug(f"Validación de fechas completada. Válido: {validation_result['is_valid']}")
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error validando fechas del proyecto: {e}")
            raise ProjectDateValidationError(
                message=f"Error validando fechas del proyecto: {e}",
                operation="validate_project_dates",
                original_error=e
            )

    # ============================================================================
    # MÉTODOS PRIVADOS DE UTILIDAD
    # ============================================================================

    async def _validate_date_range(self, start_date: date, end_date: date) -> None:
        """Valida que el rango de fechas sea válido."""
        if start_date > end_date:
            raise ProjectDateValidationError(
                message="La fecha de inicio no puede ser posterior a la fecha de fin",
                operation="validate_date_range",
                details={"start_date": start_date, "end_date": end_date}
            )

    async def _check_date_conflicts(
        self, 
        start_date: date, 
        end_date: date,
        client_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Verifica conflictos de fechas con proyectos existentes."""
        try:
            # Obtener proyectos en el rango de fechas
            overlapping_projects = await self.repository.get_by_date_range(start_date, end_date)
            
            # Filtrar por cliente si se especifica
            if client_id:
                overlapping_projects = [
                    p for p in overlapping_projects 
                    if p.client_id == client_id
                ]
            
            conflicts = []
            for project in overlapping_projects:
                if project.status == ProjectStatus.ACTIVE:
                    conflicts.append({
                        "project_id": project.id,
                        "project_name": project.name,
                        "project_reference": project.reference,
                        "conflict_start": max(start_date, project.start_date) if project.start_date else start_date,
                        "conflict_end": min(end_date, project.end_date) if project.end_date else end_date,
                        "conflict_type": "date_overlap"
                    })
            
            return conflicts
            
        except Exception as e:
            self._logger.warning(f"Error verificando conflictos de fechas: {e}")
            return []

    async def _analyze_resource_availability(
        self,
        start_date: date,
        end_date: date,
        resource_ids: List[int]
    ) -> Dict[str, Any]:
        """Analiza la disponibilidad de recursos en el período especificado."""
        # Implementación simplificada - en un sistema real consultaría
        # la disponibilidad de empleados/recursos
        return {
            "total_resources_required": len(resource_ids),
            "available_resources": len(resource_ids),  # Simplificado
            "availability_percentage": 100.0,  # Simplificado
            "resource_conflicts": [],
            "recommendations": []
        }

    async def _analyze_holidays_impact(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Analiza el impacto de días festivos en el cronograma."""
        try:
            # Lista básica de días festivos chilenos (simplificada)
            holidays_2024 = [
                date(2024, 1, 1),   # Año Nuevo
                date(2024, 4, 19),  # Viernes Santo
                date(2024, 4, 20),  # Sábado Santo
                date(2024, 5, 1),   # Día del Trabajador
                date(2024, 5, 21),  # Día de las Glorias Navales
                date(2024, 6, 29),  # San Pedro y San Pablo
                date(2024, 7, 16),  # Día de la Virgen del Carmen
                date(2024, 8, 15),  # Asunción de la Virgen
                date(2024, 9, 18),  # Independencia Nacional
                date(2024, 9, 19),  # Día de las Glorias del Ejército
                date(2024, 10, 12), # Día de la Raza
                date(2024, 11, 1),  # Día de Todos los Santos
                date(2024, 12, 8),  # Inmaculada Concepción
                date(2024, 12, 25), # Navidad
            ]
            
            # Encontrar días festivos en el rango
            holidays_in_range = [
                holiday for holiday in holidays_2024
                if start_date <= holiday <= end_date
            ]
            
            # Calcular impacto
            business_days_lost = len([
                holiday for holiday in holidays_in_range
                if pendulum.parse(holiday.isoformat()).weekday() in self.business_days
            ])
            
            return {
                "holidays_in_range": [h.isoformat() for h in holidays_in_range],
                "total_holidays": len(holidays_in_range),
                "business_days_lost": business_days_lost,
                "impact_percentage": (business_days_lost / ((end_date - start_date).days + 1)) * 100,
                "recommendations": [
                    f"Considere agregar {business_days_lost} días adicionales por días festivos"
                ] if business_days_lost > 0 else []
            }
            
        except Exception as e:
            self._logger.warning(f"Error analizando impacto de días festivos: {e}")
            return {
                "holidays_in_range": [],
                "total_holidays": 0,
                "business_days_lost": 0,
                "impact_percentage": 0,
                "recommendations": []
            }

    async def _calculate_feasibility_score(
        self,
        duration_info: Dict[str, Any],
        conflicts: List[Dict[str, Any]],
        resource_availability: Dict[str, Any],
        holidays_impact: Dict[str, Any]
    ) -> float:
        """Calcula un score de viabilidad del cronograma."""
        try:
            base_score = 100.0
            
            # Penalizar por conflictos
            conflict_penalty = len(conflicts) * 15
            base_score -= conflict_penalty
            
            # Penalizar por baja disponibilidad de recursos
            resource_penalty = (100 - resource_availability.get("availability_percentage", 100)) * 0.5
            base_score -= resource_penalty
            
            # Penalizar por alto impacto de días festivos
            holiday_penalty = holidays_impact.get("impact_percentage", 0) * 0.3
            base_score -= holiday_penalty
            
            # Bonificar por duración razonable
            duration_days = duration_info.get("total_days", 0)
            if 7 <= duration_days <= 180:  # Entre 1 semana y 6 meses
                base_score += 5
            
            # Asegurar que el score esté entre 0 y 100
            return max(0.0, min(100.0, base_score))
            
        except Exception as e:
            self._logger.warning(f"Error calculando score de viabilidad: {e}")
            return 50.0  # Score neutro en caso de error

    async def _generate_start_date_recommendations(
        self,
        suggested_start: date,
        desired_end: date,
        conflicts: List[Dict[str, Any]]
    ) -> List[str]:
        """Genera recomendaciones para la fecha de inicio."""
        recommendations = []
        
        # Recomendación por día de la semana
        start_dt = pendulum.parse(suggested_start.isoformat())
        if start_dt.weekday() == 0:  # Lunes
            recommendations.append("Excelente: Iniciar en lunes permite una semana completa de trabajo")
        elif start_dt.weekday() in [5, 6]:  # Fin de semana
            recommendations.append("Considere mover al lunes siguiente para mejor productividad")
        
        # Recomendaciones por conflictos
        if conflicts:
            recommendations.append(f"Se detectaron {len(conflicts)} conflictos potenciales")
            recommendations.append("Considere coordinar con los equipos de proyectos superpuestos")
        
        # Recomendación por buffer
        duration_days = (desired_end - suggested_start).days + 1
        if duration_days < 14:
            recommendations.append("Proyecto corto: considere agregar días de buffer")
        
        return recommendations

    async def _generate_end_date_recommendations(
        self,
        start_date: date,
        suggested_end: date,
        conflicts: List[Dict[str, Any]]
    ) -> List[str]:
        """Genera recomendaciones para la fecha de fin."""
        recommendations = []
        
        # Recomendación por día de la semana
        end_dt = pendulum.parse(suggested_end.isoformat())
        if end_dt.weekday() == 4:  # Viernes
            recommendations.append("Excelente: Terminar en viernes permite cierre semanal")
        elif end_dt.weekday() in [5, 6]:  # Fin de semana
            recommendations.append("Considere mover al viernes anterior para mejor cierre")
        
        # Recomendaciones por conflictos
        if conflicts:
            recommendations.append("Verifique que los recursos estén disponibles hasta la fecha de fin")
        
        return recommendations

    async def _generate_feasibility_recommendations(
        self,
        start_date: date,
        end_date: date,
        conflicts: List[Dict[str, Any]],
        resource_availability: Dict[str, Any],
        holidays_impact: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones de viabilidad."""
        recommendations = []
        
        if conflicts:
            recommendations.append(f"Resolver {len(conflicts)} conflictos de cronograma identificados")
        
        if resource_availability.get("availability_percentage", 100) < 80:
            recommendations.append("Asegurar disponibilidad de recursos críticos")
        
        if holidays_impact.get("business_days_lost", 0) > 0:
            recommendations.append("Considerar días festivos en la planificación")
        
        duration_days = (end_date - start_date).days + 1
        if duration_days > 180:
            recommendations.append("Considerar dividir el proyecto en fases más pequeñas")
        
        return recommendations

    async def _identify_risk_factors(
        self,
        start_date: date,
        end_date: date,
        conflicts: List[Dict[str, Any]],
        resource_availability: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identifica factores de riesgo en el cronograma."""
        risk_factors = []
        
        # Riesgo por conflictos
        if conflicts:
            risk_factors.append({
                "type": "schedule_conflicts",
                "severity": "high" if len(conflicts) > 2 else "medium",
                "description": f"{len(conflicts)} conflictos de cronograma detectados",
                "mitigation": "Coordinar con equipos de proyectos superpuestos"
            })
        
        # Riesgo por duración
        duration_days = (end_date - start_date).days + 1
        if duration_days > 365:
            risk_factors.append({
                "type": "long_duration",
                "severity": "medium",
                "description": f"Proyecto muy largo: {duration_days} días",
                "mitigation": "Dividir en fases o hitos intermedios"
            })
        
        # Riesgo por disponibilidad de recursos
        if resource_availability.get("availability_percentage", 100) < 70:
            risk_factors.append({
                "type": "resource_availability",
                "severity": "high",
                "description": "Baja disponibilidad de recursos",
                "mitigation": "Asegurar recursos antes de iniciar"
            })
        
        return risk_factors

    async def _suggest_alternative_timelines(
        self,
        original_start: date,
        original_end: date,
        conflicts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Sugiere cronogramas alternativos."""
        alternatives = []
        
        if conflicts:
            # Alternativa 1: Mover después del último conflicto
            latest_conflict_end = max(
                pendulum.parse(conflict.get("conflict_end", original_end.isoformat())).date()
                for conflict in conflicts
            )
            
            duration_days = (original_end - original_start).days + 1
            alt1_start = latest_conflict_end + timedelta(days=1)
            alt1_end = alt1_start + timedelta(days=duration_days - 1)
            
            alternatives.append({
                "option": "after_conflicts",
                "start_date": alt1_start.isoformat(),
                "end_date": alt1_end.isoformat(),
                "description": "Iniciar después de resolver todos los conflictos",
                "pros": ["Sin conflictos de cronograma"],
                "cons": ["Retraso en el inicio del proyecto"]
            })
            
            # Alternativa 2: Acortar duración
            if duration_days > 14:
                alt2_duration = max(7, duration_days - 7)  # Reducir una semana
                alt2_end = original_start + timedelta(days=alt2_duration - 1)
                
                alternatives.append({
                    "option": "reduced_duration",
                    "start_date": original_start.isoformat(),
                    "end_date": alt2_end.isoformat(),
                    "description": f"Reducir duración a {alt2_duration} días",
                    "pros": ["Mantiene fecha de inicio", "Reduce conflictos"],
                    "cons": ["Cronograma más ajustado", "Mayor presión de tiempo"]
                })
        
        return alternatives

    async def _sort_projects_for_optimization(
        self,
        projects_data: List[Dict[str, Any]],
        criteria: str
    ) -> List[Dict[str, Any]]:
        """Ordena proyectos para optimización del cronograma."""
        if criteria == "minimize_conflicts":
            # Ordenar por fecha de inicio deseada
            return sorted(
                projects_data,
                key=lambda p: p.get("desired_start_date", date.max)
            )
        elif criteria == "priority":
            # Ordenar por prioridad y luego por fecha
            return sorted(
                projects_data,
                key=lambda p: (
                    p.get("priority", "MEDIUM"),
                    p.get("desired_start_date", date.max)
                )
            )
        else:
            return projects_data

    async def _calculate_optimal_dates_for_project(
        self,
        project_data: Dict[str, Any],
        scheduled_projects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calcula fechas óptimas para un proyecto considerando los ya programados."""
        # Implementación simplificada
        desired_start = project_data.get("desired_start_date")
        desired_end = project_data.get("desired_end_date")
        
        if desired_start and desired_end:
            duration_days = (desired_end - desired_start).days + 1
        else:
            duration_days = project_data.get("estimated_duration_days", 30)
        
        # Si no hay fecha de inicio deseada, usar la fecha actual
        if not desired_start:
            desired_start = pendulum.now().date()
        
        # Si no hay fecha de fin deseada, calcularla
        if not desired_end:
            desired_end = desired_start + timedelta(days=duration_days - 1)
        
        return {
            "start_date": desired_start.isoformat(),
            "end_date": desired_end.isoformat(),
            "duration_days": duration_days,
            "adjustments": [],
            "conflicts_resolved": []
        }

    async def _resolve_scheduling_conflicts(
        self,
        optimal_dates: Dict[str, Any],
        scheduled_projects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Resuelve conflictos de programación."""
        # Implementación simplificada - en un sistema real haría
        # análisis más sofisticado de conflictos y resolución
        return optimal_dates

    async def _calculate_schedule_metrics(
        self,
        scheduled_projects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calcula métricas del cronograma optimizado."""
        if not scheduled_projects:
            return {}
        
        # Calcular span temporal total
        all_starts = [
            pendulum.parse(p["optimized_start"]).date()
            for p in scheduled_projects
        ]
        all_ends = [
            pendulum.parse(p["optimized_end"]).date()
            for p in scheduled_projects
        ]
        
        timeline_start = min(all_starts)
        timeline_end = max(all_ends)
        
        return {
            "timeline_span": {
                "start_date": timeline_start.isoformat(),
                "end_date": timeline_end.isoformat(),
                "total_days": (timeline_end - timeline_start).days + 1
            },
            "total_conflicts": sum(
                len(p.get("conflicts_resolved", []))
                for p in scheduled_projects
            ),
            "projects_adjusted": len([
                p for p in scheduled_projects
                if p.get("adjustments_made")
            ])
        }

    async def _generate_schedule_recommendations(
        self,
        scheduled_projects: List[Dict[str, Any]],
        criteria: str
    ) -> List[str]:
        """Genera recomendaciones para el cronograma optimizado."""
        recommendations = []
        
        projects_with_adjustments = [
            p for p in scheduled_projects
            if p.get("adjustments_made")
        ]
        
        if projects_with_adjustments:
            recommendations.append(
                f"{len(projects_with_adjustments)} proyectos requirieron ajustes de fechas"
            )
        
        total_conflicts = sum(
            len(p.get("conflicts_resolved", []))
            for p in scheduled_projects
        )
        
        if total_conflicts > 0:
            recommendations.append(
                f"Se resolvieron {total_conflicts} conflictos de cronograma"
            )
        
        recommendations.append("Revisar regularmente el cronograma para ajustes")
        
        return recommendations

    async def _validate_date_change_impact(
        self,
        project_id: int,
        new_start_date: Optional[date],
        new_end_date: Optional[date]
    ) -> Dict[str, Any]:
        """Valida el impacto de cambios de fecha en proyectos dependientes."""
        # Implementación simplificada
        return {
            "has_impact": False,
            "warnings": [],
            "affected_projects": []
        }