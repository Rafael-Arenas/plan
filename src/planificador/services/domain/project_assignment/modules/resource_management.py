# src/planificador/services/domain/project_assignment/modules/resource_management.py

"""
Módulo de Gestión de Recursos para Asignaciones de Proyecto

Implementa funcionalidades avanzadas de gestión de recursos,
optimización de asignaciones y balanceo de carga de trabajo
entre equipos y proyectos.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, timedelta
from loguru import logger

from planificador.schemas import ProjectAssignment
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.exceptions import RepositoryError, ValidationError, BusinessLogicError
from ..interfaces import IResourceManagement


class ResourceManagement(IResourceManagement):
    """
    Implementación de gestión de recursos y capacidad.
    
    Proporciona métodos especializados para optimizar la asignación
    de recursos, calcular capacidades de equipo y balancear cargas
    de trabajo de manera eficiente.
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """
        Inicializa el módulo de gestión de recursos.
        
        Args:
            repository_facade: Facade del repositorio de asignaciones
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="project_assignment_resource_management")
    
    async def optimize_resource_allocation(
        self, 
        project_id: int, 
        optimization_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimiza la asignación de recursos para un proyecto específico.
        
        Args:
            project_id: ID del proyecto a optimizar
            optimization_criteria: Criterios de optimización
            
        Returns:
            Dict[str, Any]: Plan de optimización con recomendaciones
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            BusinessLogicError: Si hay conflictos de reglas de negocio
            RepositoryError: Si hay errores en el cálculo
        """
        try:
            self._logger.info(
                f"Iniciando optimización de recursos para proyecto {project_id}"
            )
            
            # Validar parámetros
            if project_id <= 0:
                raise ValidationError(
                    message="El ID del proyecto debe ser un número positivo",
                    field="project_id",
                    value=project_id
                )
            
            validated_criteria = await self._validate_optimization_criteria(optimization_criteria)
            
            # Obtener asignaciones actuales del proyecto
            current_assignments = await self._repository.queries.get_assignments_by_project(
                project_id=project_id,
                include_inactive=False
            )
            
            if not current_assignments:
                return {
                    "project_id": project_id,
                    "optimization_status": "no_assignments",
                    "message": "No hay asignaciones activas para optimizar",
                    "recommendations": [],
                    "potential_savings": 0
                }
            
            # Analizar estado actual
            current_analysis = await self._analyze_current_resource_state(current_assignments)
            
            # Generar plan de optimización
            optimization_plan = await self._generate_optimization_plan(
                current_assignments, current_analysis, validated_criteria
            )
            
            # Calcular impacto de la optimización
            impact_analysis = await self._calculate_optimization_impact(
                current_analysis, optimization_plan
            )
            
            result = {
                "project_id": project_id,
                "optimization_status": "completed",
                "current_state": current_analysis,
                "optimization_plan": optimization_plan,
                "impact_analysis": impact_analysis,
                "implementation_priority": self._calculate_implementation_priority(impact_analysis)
            }
            
            self._logger.info(
                f"Optimización completada para proyecto {project_id}: "
                f"{len(optimization_plan['recommendations'])} recomendaciones generadas"
            )
            
            return result
            
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(
                f"Error en optimización de recursos para proyecto {project_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error en optimización de recursos: {e}",
                operation="optimize_resource_allocation",
                entity_type="ProjectAssignment",
                entity_id=project_id,
                original_error=e
            )
    
    async def calculate_team_capacity(
        self, 
        team_member_ids: List[int], 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """
        Calcula la capacidad total del equipo durante un período específico.
        
        Args:
            team_member_ids: Lista de IDs de miembros del equipo
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict[str, Any]: Análisis detallado de capacidad del equipo
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay errores en el cálculo
        """
        try:
            self._logger.info(
                f"Calculando capacidad de equipo para {len(team_member_ids)} miembros "
                f"del {start_date} al {end_date}"
            )
            
            # Validar parámetros
            if not team_member_ids:
                raise ValidationError(
                    message="La lista de miembros del equipo no puede estar vacía",
                    field="team_member_ids",
                    value=team_member_ids
                )
            
            if start_date > end_date:
                raise ValidationError(
                    message="La fecha de inicio debe ser anterior a la fecha de fin",
                    field="date_range",
                    value=f"{start_date} - {end_date}"
                )
            
            # Validar IDs de empleados
            for employee_id in team_member_ids:
                if employee_id <= 0:
                    raise ValidationError(
                        message=f"ID de empleado inválido: {employee_id}",
                        field="team_member_ids",
                        value=employee_id
                    )
            
            # Obtener asignaciones de todos los miembros del equipo en el período
            team_assignments = await self._get_team_assignments_in_period(
                team_member_ids, start_date, end_date
            )
            
            # Calcular capacidad por miembro
            member_capacities = await self._calculate_individual_capacities(
                team_member_ids, team_assignments, start_date, end_date
            )
            
            # Calcular métricas agregadas del equipo
            team_metrics = await self._calculate_team_aggregate_metrics(
                member_capacities, start_date, end_date
            )
            
            # Identificar cuellos de botella y oportunidades
            capacity_analysis = await self._analyze_capacity_constraints(
                member_capacities, team_metrics
            )
            
            result = {
                "team_member_ids": team_member_ids,
                "analysis_period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_days": (end_date - start_date).days
                },
                "member_capacities": member_capacities,
                "team_metrics": team_metrics,
                "capacity_analysis": capacity_analysis,
                "recommendations": await self._generate_capacity_recommendations(
                    member_capacities, team_metrics, capacity_analysis
                )
            }
            
            self._logger.info(
                f"Cálculo de capacidad completado: "
                f"{team_metrics['total_available_capacity']}% capacidad total disponible"
            )
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al calcular capacidad del equipo: {e}")
            raise RepositoryError(
                message=f"Error al calcular capacidad del equipo: {e}",
                operation="calculate_team_capacity",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def balance_workload_across_team(
        self, 
        project_id: int, 
        balancing_strategy: str = "equal_distribution"
    ) -> Dict[str, Any]:
        """
        Balancea la carga de trabajo dentro de un equipo de proyecto.
        
        Args:
            project_id: ID del proyecto
            balancing_strategy: Estrategia de balanceo
            
        Returns:
            Dict[str, Any]: Plan de balanceo de carga con recomendaciones
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            BusinessLogicError: Si hay conflictos de reglas de negocio
            RepositoryError: Si hay errores en el cálculo
        """
        try:
            self._logger.info(
                f"Iniciando balanceo de carga para proyecto {project_id} "
                f"con estrategia '{balancing_strategy}'"
            )
            
            # Validar parámetros
            if project_id <= 0:
                raise ValidationError(
                    message="El ID del proyecto debe ser un número positivo",
                    field="project_id",
                    value=project_id
                )
            
            valid_strategies = ["equal_distribution", "skill_based", "capacity_based", "priority_based"]
            if balancing_strategy not in valid_strategies:
                raise ValidationError(
                    message=f"Estrategia de balanceo inválida. Debe ser una de: {valid_strategies}",
                    field="balancing_strategy",
                    value=balancing_strategy
                )
            
            # Obtener asignaciones actuales del proyecto
            project_assignments = await self._repository.queries.get_assignments_by_project(
                project_id=project_id,
                include_inactive=False
            )
            
            if not project_assignments:
                return {
                    "project_id": project_id,
                    "balancing_status": "no_assignments",
                    "message": "No hay asignaciones activas para balancear",
                    "recommendations": []
                }
            
            # Analizar distribución actual de carga
            current_distribution = await self._analyze_workload_distribution(project_assignments)
            
            # Detectar desequilibrios
            imbalance_analysis = await self._detect_workload_imbalances(current_distribution)
            
            if not imbalance_analysis["has_imbalances"]:
                return {
                    "project_id": project_id,
                    "balancing_status": "already_balanced",
                    "message": "La carga de trabajo ya está bien balanceada",
                    "current_distribution": current_distribution,
                    "imbalance_score": imbalance_analysis["imbalance_score"]
                }
            
            # Generar plan de balanceo
            balancing_plan = await self._generate_balancing_plan(
                project_assignments, current_distribution, balancing_strategy
            )
            
            # Simular impacto del balanceo
            impact_simulation = await self._simulate_balancing_impact(
                current_distribution, balancing_plan
            )
            
            result = {
                "project_id": project_id,
                "balancing_status": "plan_generated",
                "balancing_strategy": balancing_strategy,
                "current_distribution": current_distribution,
                "imbalance_analysis": imbalance_analysis,
                "balancing_plan": balancing_plan,
                "impact_simulation": impact_simulation,
                "implementation_steps": await self._generate_implementation_steps(balancing_plan)
            }
            
            self._logger.info(
                f"Plan de balanceo generado para proyecto {project_id}: "
                f"mejora esperada del {impact_simulation['improvement_percentage']}%"
            )
            
            return result
            
        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(
                f"Error en balanceo de carga para proyecto {project_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error en balanceo de carga: {e}",
                operation="balance_workload_across_team",
                entity_type="ProjectAssignment",
                entity_id=project_id,
                original_error=e
            )
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE OPTIMIZACIÓN
    # ============================================================================
    
    async def _validate_optimization_criteria(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Valida y normaliza los criterios de optimización."""
        if not isinstance(criteria, dict):
            raise ValidationError(
                message="Los criterios de optimización deben ser un diccionario",
                field="optimization_criteria",
                value=type(criteria).__name__
            )
        
        validated_criteria = {}
        
        # Criterios válidos con sus validaciones
        valid_criteria = {
            "minimize_overallocation": lambda x: isinstance(x, bool),
            "maximize_utilization": lambda x: isinstance(x, bool),
            "balance_workload": lambda x: isinstance(x, bool),
            "reduce_conflicts": lambda x: isinstance(x, bool),
            "target_utilization_percentage": lambda x: isinstance(x, (int, float)) and 0 <= x <= 100,
            "max_allocation_per_employee": lambda x: isinstance(x, (int, float)) and 0 <= x <= 100,
            "priority_roles": lambda x: isinstance(x, list) and all(isinstance(role, str) for role in x)
        }
        
        for criterion, value in criteria.items():
            if criterion not in valid_criteria:
                self._logger.warning(f"Criterio de optimización desconocido ignorado: {criterion}")
                continue
            
            if not valid_criteria[criterion](value):
                raise ValidationError(
                    message=f"Valor inválido para criterio '{criterion}'",
                    field=criterion,
                    value=value
                )
            
            validated_criteria[criterion] = value
        
        # Establecer valores por defecto
        default_criteria = {
            "minimize_overallocation": True,
            "maximize_utilization": True,
            "balance_workload": True,
            "reduce_conflicts": True,
            "target_utilization_percentage": 80,
            "max_allocation_per_employee": 100
        }
        
        for key, default_value in default_criteria.items():
            if key not in validated_criteria:
                validated_criteria[key] = default_value
        
        return validated_criteria
    
    async def _analyze_current_resource_state(
        self, 
        assignments: List[ProjectAssignment]
    ) -> Dict[str, Any]:
        """Analiza el estado actual de los recursos."""
        # Agrupar por empleado
        employee_allocations = {}
        for assignment in assignments:
            employee_id = assignment.employee_id
            if employee_id not in employee_allocations:
                employee_allocations[employee_id] = {
                    "employee_id": employee_id,
                    "assignments": [],
                    "total_percentage": 0,
                    "total_hours": 0
                }
            
            employee_allocations[employee_id]["assignments"].append(assignment)
            employee_allocations[employee_id]["total_percentage"] += assignment.percentage_allocation
            employee_allocations[employee_id]["total_hours"] += assignment.allocated_hours_per_day
        
        # Calcular métricas
        total_employees = len(employee_allocations)
        overallocated_employees = sum(
            1 for emp in employee_allocations.values() 
            if emp["total_percentage"] > 100
        )
        underutilized_employees = sum(
            1 for emp in employee_allocations.values() 
            if emp["total_percentage"] < 50
        )
        
        total_allocation = sum(emp["total_percentage"] for emp in employee_allocations.values())
        average_allocation = total_allocation / total_employees if total_employees > 0 else 0
        
        # Calcular varianza de asignación
        if total_employees > 1:
            variance = sum(
                (emp["total_percentage"] - average_allocation) ** 2 
                for emp in employee_allocations.values()
            ) / total_employees
            allocation_balance_score = max(0, 100 - (variance / 10))  # Normalizar a 0-100
        else:
            allocation_balance_score = 100
        
        return {
            "total_assignments": len(assignments),
            "total_employees": total_employees,
            "employee_allocations": list(employee_allocations.values()),
            "overallocated_employees": overallocated_employees,
            "underutilized_employees": underutilized_employees,
            "total_allocation_percentage": total_allocation,
            "average_allocation_percentage": round(average_allocation, 2),
            "allocation_balance_score": round(allocation_balance_score, 2),
            "utilization_efficiency": min(100, average_allocation)
        }
    
    async def _generate_optimization_plan(
        self, 
        assignments: List[ProjectAssignment], 
        current_analysis: Dict[str, Any], 
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera un plan de optimización basado en los criterios."""
        recommendations = []
        
        # Recomendaciones para sobreasignación
        if criteria["minimize_overallocation"] and current_analysis["overallocated_employees"] > 0:
            for emp_data in current_analysis["employee_allocations"]:
                if emp_data["total_percentage"] > 100:
                    excess = emp_data["total_percentage"] - criteria["max_allocation_per_employee"]
                    recommendations.append({
                        "type": "reduce_overallocation",
                        "employee_id": emp_data["employee_id"],
                        "current_allocation": emp_data["total_percentage"],
                        "target_allocation": criteria["max_allocation_per_employee"],
                        "reduction_needed": excess,
                        "priority": "high",
                        "affected_assignments": len(emp_data["assignments"])
                    })
        
        # Recomendaciones para maximizar utilización
        if criteria["maximize_utilization"] and current_analysis["underutilized_employees"] > 0:
            target_utilization = criteria["target_utilization_percentage"]
            for emp_data in current_analysis["employee_allocations"]:
                if emp_data["total_percentage"] < target_utilization:
                    increase_potential = target_utilization - emp_data["total_percentage"]
                    recommendations.append({
                        "type": "increase_utilization",
                        "employee_id": emp_data["employee_id"],
                        "current_allocation": emp_data["total_percentage"],
                        "target_allocation": target_utilization,
                        "increase_potential": increase_potential,
                        "priority": "medium",
                        "affected_assignments": len(emp_data["assignments"])
                    })
        
        # Recomendaciones para balanceo de carga
        if criteria["balance_workload"] and current_analysis["allocation_balance_score"] < 80:
            recommendations.append({
                "type": "balance_workload",
                "current_balance_score": current_analysis["allocation_balance_score"],
                "target_balance_score": 90,
                "priority": "medium",
                "description": "Redistribuir asignaciones para mejorar el balance de carga"
            })
        
        return {
            "optimization_criteria": criteria,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "high_priority_count": sum(1 for r in recommendations if r.get("priority") == "high"),
            "estimated_effort": self._estimate_implementation_effort(recommendations)
        }
    
    async def _calculate_optimization_impact(
        self, 
        current_analysis: Dict[str, Any], 
        optimization_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcula el impacto esperado de la optimización."""
        recommendations = optimization_plan["recommendations"]
        
        # Calcular mejoras potenciales
        overallocation_reduction = sum(
            r.get("reduction_needed", 0) for r in recommendations 
            if r["type"] == "reduce_overallocation"
        )
        
        utilization_increase = sum(
            r.get("increase_potential", 0) for r in recommendations 
            if r["type"] == "increase_utilization"
        )
        
        # Estimar nueva puntuación de balance
        current_balance = current_analysis["allocation_balance_score"]
        balance_improvements = [
            r for r in recommendations if r["type"] == "balance_workload"
        ]
        estimated_new_balance = current_balance + (10 * len(balance_improvements))
        estimated_new_balance = min(100, estimated_new_balance)
        
        # Calcular ahorro potencial en horas
        potential_hour_savings = overallocation_reduction * 8 / 100  # Asumiendo 8 horas por día
        
        return {
            "overallocation_reduction_percentage": round(overallocation_reduction, 2),
            "utilization_increase_percentage": round(utilization_increase, 2),
            "balance_score_improvement": round(estimated_new_balance - current_balance, 2),
            "potential_hour_savings_per_day": round(potential_hour_savings, 2),
            "estimated_efficiency_gain": round(
                (overallocation_reduction + utilization_increase) / 2, 2
            ),
            "roi_score": self._calculate_optimization_roi(
                overallocation_reduction, utilization_increase, len(recommendations)
            )
        }
    
    def _calculate_implementation_priority(self, impact_analysis: Dict[str, Any]) -> str:
        """Calcula la prioridad de implementación basada en el impacto."""
        roi_score = impact_analysis["roi_score"]
        efficiency_gain = impact_analysis["estimated_efficiency_gain"]
        
        if roi_score > 80 and efficiency_gain > 20:
            return "critical"
        elif roi_score > 60 and efficiency_gain > 15:
            return "high"
        elif roi_score > 40 and efficiency_gain > 10:
            return "medium"
        else:
            return "low"
    
    def _calculate_optimization_roi(
        self, 
        overallocation_reduction: float, 
        utilization_increase: float, 
        recommendation_count: int
    ) -> float:
        """Calcula el ROI de la optimización."""
        benefits = overallocation_reduction + utilization_increase
        costs = recommendation_count * 5  # Factor de costo por recomendación
        
        if costs == 0:
            return 0
        
        roi = (benefits / costs) * 100
        return min(100, max(0, roi))
    
    def _estimate_implementation_effort(self, recommendations: List[Dict[str, Any]]) -> str:
        """Estima el esfuerzo de implementación."""
        total_recommendations = len(recommendations)
        high_priority_count = sum(1 for r in recommendations if r.get("priority") == "high")
        
        if total_recommendations == 0:
            return "none"
        elif total_recommendations <= 3 and high_priority_count <= 1:
            return "low"
        elif total_recommendations <= 6 and high_priority_count <= 2:
            return "medium"
        else:
            return "high"
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE CAPACIDAD
    # ============================================================================
    
    async def _get_team_assignments_in_period(
        self, 
        team_member_ids: List[int], 
        start_date: date, 
        end_date: date
    ) -> List[ProjectAssignment]:
        """Obtiene todas las asignaciones del equipo en el período especificado."""
        all_assignments = []
        
        for employee_id in team_member_ids:
            employee_assignments = await self._repository.queries.get_assignments_by_employee(
                employee_id=employee_id,
                include_inactive=False
            )
            
            # Filtrar por período
            period_assignments = [
                assignment for assignment in employee_assignments
                if (assignment.start_date <= end_date and assignment.end_date >= start_date)
            ]
            
            all_assignments.extend(period_assignments)
        
        return all_assignments
    
    async def _calculate_individual_capacities(
        self, 
        team_member_ids: List[int], 
        team_assignments: List[ProjectAssignment], 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Calcula la capacidad individual de cada miembro del equipo."""
        member_capacities = []
        
        for employee_id in team_member_ids:
            # Obtener asignaciones del empleado
            employee_assignments = [
                assignment for assignment in team_assignments
                if assignment.employee_id == employee_id
            ]
            
            # Calcular métricas de capacidad
            total_percentage = sum(
                assignment.percentage_allocation for assignment in employee_assignments
            )
            total_hours = sum(
                assignment.allocated_hours_per_day for assignment in employee_assignments
            )
            
            # Calcular disponibilidad por período
            availability_analysis = self._analyze_employee_availability(
                employee_assignments, start_date, end_date
            )
            
            member_capacity = {
                "employee_id": employee_id,
                "total_assignments": len(employee_assignments),
                "total_percentage_allocation": total_percentage,
                "total_hours_per_day": total_hours,
                "available_capacity_percentage": max(0, 100 - total_percentage),
                "available_hours_per_day": max(0, 8 - total_hours),  # Asumiendo 8 horas por día
                "utilization_status": self._classify_utilization_status(total_percentage),
                "availability_analysis": availability_analysis,
                "capacity_score": self._calculate_capacity_score(total_percentage, len(employee_assignments))
            }
            
            member_capacities.append(member_capacity)
        
        return member_capacities
    
    def _analyze_employee_availability(
        self, 
        assignments: List[ProjectAssignment], 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Analiza la disponibilidad del empleado durante el período."""
        if not assignments:
            return {
                "fully_available_days": (end_date - start_date).days,
                "partially_available_days": 0,
                "unavailable_days": 0,
                "availability_percentage": 100
            }
        
        # Simplificación: calcular días con diferentes niveles de disponibilidad
        total_days = (end_date - start_date).days
        
        # Calcular promedio de asignación
        avg_allocation = sum(a.percentage_allocation for a in assignments) / len(assignments)
        
        if avg_allocation == 0:
            fully_available = total_days
            partially_available = 0
            unavailable = 0
        elif avg_allocation < 50:
            fully_available = int(total_days * 0.7)
            partially_available = int(total_days * 0.3)
            unavailable = 0
        elif avg_allocation < 100:
            fully_available = 0
            partially_available = total_days
            unavailable = 0
        else:
            fully_available = 0
            partially_available = 0
            unavailable = total_days
        
        availability_percentage = ((fully_available + partially_available * 0.5) / total_days * 100) if total_days > 0 else 0
        
        return {
            "fully_available_days": fully_available,
            "partially_available_days": partially_available,
            "unavailable_days": unavailable,
            "availability_percentage": round(availability_percentage, 2)
        }
    
    def _classify_utilization_status(self, percentage: float) -> str:
        """Clasifica el estado de utilización del empleado."""
        if percentage == 0:
            return "available"
        elif percentage < 50:
            return "underutilized"
        elif percentage < 80:
            return "well_utilized"
        elif percentage <= 100:
            return "fully_utilized"
        else:
            return "overallocated"
    
    def _calculate_capacity_score(self, percentage: float, assignment_count: int) -> float:
        """Calcula una puntuación de capacidad (0-100)."""
        # Penalizar sobreasignación y subutilización
        if percentage > 100:
            utilization_score = max(0, 100 - (percentage - 100))
        elif percentage < 50:
            utilization_score = percentage * 2
        else:
            utilization_score = 100
        
        # Bonificar diversidad de asignaciones (hasta cierto punto)
        diversity_bonus = min(20, assignment_count * 5)
        
        capacity_score = min(100, utilization_score + diversity_bonus)
        return round(capacity_score, 2)
    
    async def _calculate_team_aggregate_metrics(
        self, 
        member_capacities: List[Dict[str, Any]], 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Calcula métricas agregadas del equipo."""
        if not member_capacities:
            return {
                "total_team_members": 0,
                "total_available_capacity": 0,
                "average_utilization": 0,
                "team_capacity_score": 0
            }
        
        total_members = len(member_capacities)
        total_allocated = sum(member["total_percentage_allocation"] for member in member_capacities)
        total_available = sum(member["available_capacity_percentage"] for member in member_capacities)
        
        average_utilization = total_allocated / total_members if total_members > 0 else 0
        team_capacity_score = sum(member["capacity_score"] for member in member_capacities) / total_members
        
        # Clasificar miembros por estado
        utilization_distribution = {}
        for member in member_capacities:
            status = member["utilization_status"]
            if status not in utilization_distribution:
                utilization_distribution[status] = 0
            utilization_distribution[status] += 1
        
        return {
            "total_team_members": total_members,
            "total_allocated_capacity": round(total_allocated, 2),
            "total_available_capacity": round(total_available, 2),
            "average_utilization": round(average_utilization, 2),
            "team_capacity_score": round(team_capacity_score, 2),
            "utilization_distribution": utilization_distribution,
            "capacity_efficiency": min(100, average_utilization),
            "team_balance_score": self._calculate_team_balance_score(member_capacities)
        }
    
    def _calculate_team_balance_score(self, member_capacities: List[Dict[str, Any]]) -> float:
        """Calcula una puntuación de balance del equipo."""
        if len(member_capacities) <= 1:
            return 100
        
        utilizations = [member["total_percentage_allocation"] for member in member_capacities]
        avg_utilization = sum(utilizations) / len(utilizations)
        
        # Calcular varianza
        variance = sum((util - avg_utilization) ** 2 for util in utilizations) / len(utilizations)
        
        # Convertir a puntuación (menor varianza = mejor balance)
        balance_score = max(0, 100 - (variance / 10))
        return round(balance_score, 2)
    
    async def _analyze_capacity_constraints(
        self, 
        member_capacities: List[Dict[str, Any]], 
        team_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analiza las limitaciones de capacidad del equipo."""
        constraints = []
        opportunities = []
        
        # Identificar cuellos de botella
        overallocated_members = [
            member for member in member_capacities 
            if member["utilization_status"] == "overallocated"
        ]
        
        underutilized_members = [
            member for member in member_capacities 
            if member["utilization_status"] in ["available", "underutilized"]
        ]
        
        if overallocated_members:
            constraints.append({
                "type": "overallocation",
                "affected_members": len(overallocated_members),
                "severity": "high" if len(overallocated_members) > len(member_capacities) * 0.3 else "medium",
                "description": f"{len(overallocated_members)} miembros están sobreasignados"
            })
        
        if underutilized_members:
            opportunities.append({
                "type": "underutilization",
                "affected_members": len(underutilized_members),
                "potential_capacity": sum(
                    member["available_capacity_percentage"] for member in underutilized_members
                ),
                "description": f"{len(underutilized_members)} miembros tienen capacidad disponible"
            })
        
        # Analizar balance del equipo
        if team_metrics["team_balance_score"] < 70:
            constraints.append({
                "type": "imbalanced_workload",
                "severity": "medium",
                "current_score": team_metrics["team_balance_score"],
                "description": "La carga de trabajo no está bien distribuida en el equipo"
            })
        
        return {
            "constraints": constraints,
            "opportunities": opportunities,
            "constraint_count": len(constraints),
            "opportunity_count": len(opportunities),
            "overall_capacity_health": self._assess_overall_capacity_health(
                constraints, opportunities, team_metrics
            )
        }
    
    def _assess_overall_capacity_health(
        self, 
        constraints: List[Dict[str, Any]], 
        opportunities: List[Dict[str, Any]], 
        team_metrics: Dict[str, Any]
    ) -> str:
        """Evalúa la salud general de la capacidad del equipo."""
        high_severity_constraints = sum(
            1 for constraint in constraints if constraint.get("severity") == "high"
        )
        
        team_score = team_metrics["team_capacity_score"]
        
        if high_severity_constraints > 0 or team_score < 50:
            return "poor"
        elif len(constraints) > len(opportunities) or team_score < 70:
            return "fair"
        elif team_score > 85 and len(opportunities) > 0:
            return "excellent"
        else:
            return "good"
    
    async def _generate_capacity_recommendations(
        self, 
        member_capacities: List[Dict[str, Any]], 
        team_metrics: Dict[str, Any], 
        capacity_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera recomendaciones para mejorar la capacidad del equipo."""
        recommendations = []
        
        # Recomendaciones basadas en limitaciones
        for constraint in capacity_analysis["constraints"]:
            if constraint["type"] == "overallocation":
                recommendations.append({
                    "type": "reduce_overallocation",
                    "priority": constraint["severity"],
                    "description": "Redistribuir o reducir asignaciones de miembros sobreasignados",
                    "affected_members": constraint["affected_members"],
                    "expected_impact": "high"
                })
            
            elif constraint["type"] == "imbalanced_workload":
                recommendations.append({
                    "type": "rebalance_workload",
                    "priority": "medium",
                    "description": "Redistribuir tareas para mejorar el balance del equipo",
                    "current_score": constraint["current_score"],
                    "target_score": 85,
                    "expected_impact": "medium"
                })
        
        # Recomendaciones basadas en oportunidades
        for opportunity in capacity_analysis["opportunities"]:
            if opportunity["type"] == "underutilization":
                recommendations.append({
                    "type": "increase_utilization",
                    "priority": "low",
                    "description": "Asignar más trabajo a miembros subutilizados",
                    "affected_members": opportunity["affected_members"],
                    "potential_capacity": opportunity["potential_capacity"],
                    "expected_impact": "medium"
                })
        
        # Recomendación general si el equipo está bien
        if not recommendations and team_metrics["team_capacity_score"] > 80:
            recommendations.append({
                "type": "maintain_current_state",
                "priority": "low",
                "description": "El equipo tiene una buena distribución de capacidad, mantener estado actual",
                "expected_impact": "low"
            })
        
        return recommendations
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE BALANCEO
    # ============================================================================
    
    async def _analyze_workload_distribution(
        self, 
        assignments: List[ProjectAssignment]
    ) -> Dict[str, Any]:
        """Analiza la distribución actual de carga de trabajo."""
        # Agrupar por empleado
        employee_workloads = {}
        for assignment in assignments:
            employee_id = assignment.employee_id
            if employee_id not in employee_workloads:
                employee_workloads[employee_id] = {
                    "employee_id": employee_id,
                    "assignments": [],
                    "total_percentage": 0,
                    "total_hours": 0,
                    "roles": set()
                }
            
            employee_workloads[employee_id]["assignments"].append(assignment)
            employee_workloads[employee_id]["total_percentage"] += assignment.percentage_allocation
            employee_workloads[employee_id]["total_hours"] += assignment.allocated_hours_per_day
            employee_workloads[employee_id]["roles"].add(assignment.role_in_project)
        
        # Convertir sets a listas para serialización
        for workload in employee_workloads.values():
            workload["roles"] = list(workload["roles"])
            workload["role_count"] = len(workload["roles"])
        
        # Calcular estadísticas de distribución
        workloads = list(employee_workloads.values())
        percentages = [w["total_percentage"] for w in workloads]
        
        if percentages:
            avg_percentage = sum(percentages) / len(percentages)
            min_percentage = min(percentages)
            max_percentage = max(percentages)
            
            # Calcular desviación estándar
            variance = sum((p - avg_percentage) ** 2 for p in percentages) / len(percentages)
            std_deviation = variance ** 0.5
        else:
            avg_percentage = min_percentage = max_percentage = std_deviation = 0
        
        return {
            "employee_workloads": workloads,
            "total_employees": len(workloads),
            "distribution_stats": {
                "average_percentage": round(avg_percentage, 2),
                "min_percentage": min_percentage,
                "max_percentage": max_percentage,
                "standard_deviation": round(std_deviation, 2),
                "range": max_percentage - min_percentage if percentages else 0
            },
            "workload_categories": self._categorize_workloads(workloads)
        }
    
    def _categorize_workloads(self, workloads: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categoriza las cargas de trabajo por nivel."""
        categories = {
            "underutilized": 0,  # < 50%
            "well_balanced": 0,  # 50-80%
            "highly_utilized": 0,  # 80-100%
            "overallocated": 0   # > 100%
        }
        
        for workload in workloads:
            percentage = workload["total_percentage"]
            if percentage < 50:
                categories["underutilized"] += 1
            elif percentage <= 80:
                categories["well_balanced"] += 1
            elif percentage <= 100:
                categories["highly_utilized"] += 1
            else:
                categories["overallocated"] += 1
        
        return categories
    
    async def _detect_workload_imbalances(
        self, 
        distribution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detecta desequilibrios en la carga de trabajo."""
        stats = distribution["distribution_stats"]
        categories = distribution["workload_categories"]
        
        # Calcular puntuación de desequilibrio
        std_dev = stats["standard_deviation"]
        range_spread = stats["range"]
        
        # Factores de desequilibrio
        high_std_dev = std_dev > 20  # Desviación estándar alta
        wide_range = range_spread > 50  # Rango amplio
        has_overallocation = categories["overallocated"] > 0
        has_underutilization = categories["underutilized"] > 0
        
        # Calcular puntuación de desequilibrio (0-100, donde 0 es perfectamente balanceado)
        imbalance_score = min(100, std_dev + (range_spread / 2))
        
        has_imbalances = (
            high_std_dev or wide_range or 
            has_overallocation or 
            (has_underutilization and categories["underutilized"] > 1)
        )
        
        # Identificar tipos específicos de desequilibrio
        imbalance_types = []
        if has_overallocation:
            imbalance_types.append("overallocation")
        if has_underutilization and categories["underutilized"] > 1:
            imbalance_types.append("underutilization")
        if high_std_dev:
            imbalance_types.append("high_variance")
        if wide_range:
            imbalance_types.append("wide_distribution")
        
        return {
            "has_imbalances": has_imbalances,
            "imbalance_score": round(imbalance_score, 2),
            "imbalance_types": imbalance_types,
            "severity": self._classify_imbalance_severity(imbalance_score),
            "primary_issues": {
                "overallocation_count": categories["overallocated"],
                "underutilization_count": categories["underutilized"],
                "standard_deviation": std_dev,
                "range_spread": range_spread
            }
        }
    
    def _classify_imbalance_severity(self, imbalance_score: float) -> str:
        """Clasifica la severidad del desequilibrio."""
        if imbalance_score < 10:
            return "minimal"
        elif imbalance_score < 25:
            return "low"
        elif imbalance_score < 50:
            return "medium"
        elif imbalance_score < 75:
            return "high"
        else:
            return "critical"
    
    async def _generate_balancing_plan(
        self, 
        assignments: List[ProjectAssignment], 
        distribution: Dict[str, Any], 
        strategy: str
    ) -> Dict[str, Any]:
        """Genera un plan de balanceo basado en la estrategia seleccionada."""
        workloads = distribution["employee_workloads"]
        
        if strategy == "equal_distribution":
            return await self._generate_equal_distribution_plan(workloads)
        elif strategy == "capacity_based":
            return await self._generate_capacity_based_plan(workloads)
        elif strategy == "skill_based":
            return await self._generate_skill_based_plan(workloads)
        elif strategy == "priority_based":
            return await self._generate_priority_based_plan(workloads)
        else:
            # Fallback a distribución igual
            return await self._generate_equal_distribution_plan(workloads)
    
    async def _generate_equal_distribution_plan(
        self, 
        workloads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Genera un plan de distribución igual."""
        if not workloads:
            return {"strategy": "equal_distribution", "actions": []}
        
        # Calcular objetivo de distribución igual
        total_percentage = sum(w["total_percentage"] for w in workloads)
        target_percentage = total_percentage / len(workloads)
        
        actions = []
        for workload in workloads:
            current = workload["total_percentage"]
            difference = current - target_percentage
            
            if abs(difference) > 5:  # Solo actuar si la diferencia es significativa
                if difference > 0:
                    # Reducir carga
                    actions.append({
                        "type": "reduce_allocation",
                        "employee_id": workload["employee_id"],
                        "current_percentage": current,
                        "target_percentage": target_percentage,
                        "reduction_amount": difference,
                        "affected_assignments": len(workload["assignments"])
                    })
                else:
                    # Aumentar carga
                    actions.append({
                        "type": "increase_allocation",
                        "employee_id": workload["employee_id"],
                        "current_percentage": current,
                        "target_percentage": target_percentage,
                        "increase_amount": abs(difference),
                        "capacity_available": True
                    })
        
        return {
            "strategy": "equal_distribution",
            "target_percentage_per_employee": round(target_percentage, 2),
            "actions": actions,
            "total_actions": len(actions),
            "estimated_balance_improvement": self._estimate_balance_improvement(actions)
        }
    
    async def _generate_capacity_based_plan(
        self, 
        workloads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Genera un plan basado en capacidad individual."""
        # Simplificación: asumir capacidad estándar de 100% por empleado
        actions = []
        
        for workload in workloads:
            current = workload["total_percentage"]
            capacity = 100  # Capacidad estándar
            
            if current > capacity:
                # Reducir sobreasignación
                actions.append({
                    "type": "reduce_overallocation",
                    "employee_id": workload["employee_id"],
                    "current_percentage": current,
                    "capacity_limit": capacity,
                    "excess_allocation": current - capacity,
                    "priority": "high"
                })
            elif current < capacity * 0.7:  # Menos del 70% de capacidad
                # Aumentar utilización
                actions.append({
                    "type": "increase_utilization",
                    "employee_id": workload["employee_id"],
                    "current_percentage": current,
                    "capacity_limit": capacity,
                    "available_capacity": capacity - current,
                    "priority": "medium"
                })
        
        return {
            "strategy": "capacity_based",
            "actions": actions,
            "total_actions": len(actions),
            "capacity_optimization_score": self._calculate_capacity_optimization_score(actions)
        }
    
    async def _generate_skill_based_plan(
        self, 
        workloads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Genera un plan basado en habilidades (simplificado)."""
        # Simplificación: usar diversidad de roles como proxy de habilidades
        actions = []
        
        # Identificar empleados con muchos roles (especialistas) vs pocos roles
        specialists = [w for w in workloads if w["role_count"] >= 3]
        generalists = [w for w in workloads if w["role_count"] <= 1]
        
        # Balancear entre especialistas y generalistas
        for specialist in specialists:
            if specialist["total_percentage"] > 90:
                actions.append({
                    "type": "reduce_specialist_load",
                    "employee_id": specialist["employee_id"],
                    "current_percentage": specialist["total_percentage"],
                    "role_count": specialist["role_count"],
                    "recommendation": "Redistribuir algunos roles a generalistas"
                })
        
        for generalist in generalists:
            if generalist["total_percentage"] < 60:
                actions.append({
                    "type": "increase_generalist_load",
                    "employee_id": generalist["employee_id"],
                    "current_percentage": generalist["total_percentage"],
                    "role_count": generalist["role_count"],
                    "recommendation": "Asignar roles adicionales desde especialistas sobrecargados"
                })
        
        return {
            "strategy": "skill_based",
            "actions": actions,
            "specialists_count": len(specialists),
            "generalists_count": len(generalists),
            "skill_distribution_score": self._calculate_skill_distribution_score(workloads)
        }
    
    async def _generate_priority_based_plan(
        self, 
        workloads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Genera un plan basado en prioridades (simplificado)."""
        # Simplificación: priorizar empleados con menos asignaciones
        actions = []
        
        # Ordenar por número de asignaciones (menos asignaciones = mayor prioridad para más trabajo)
        sorted_workloads = sorted(workloads, key=lambda x: len(x["assignments"]))
        
        # Identificar candidatos para redistribución
        low_assignment_employees = sorted_workloads[:len(sorted_workloads)//2]
        high_assignment_employees = sorted_workloads[len(sorted_workloads)//2:]
        
        for emp in high_assignment_employees:
            if emp["total_percentage"] > 85 and len(emp["assignments"]) > 2:
                actions.append({
                    "type": "redistribute_from_busy",
                    "employee_id": emp["employee_id"],
                    "current_percentage": emp["total_percentage"],
                    "assignment_count": len(emp["assignments"]),
                    "priority": "high"
                })
        
        for emp in low_assignment_employees:
            if emp["total_percentage"] < 70:
                actions.append({
                    "type": "assign_to_available",
                    "employee_id": emp["employee_id"],
                    "current_percentage": emp["total_percentage"],
                    "assignment_count": len(emp["assignments"]),
                    "priority": "medium"
                })
        
        return {
            "strategy": "priority_based",
            "actions": actions,
            "redistribution_opportunities": len([a for a in actions if a["type"] == "redistribute_from_busy"]),
            "assignment_opportunities": len([a for a in actions if a["type"] == "assign_to_available"])
        }
    
    def _estimate_balance_improvement(self, actions: List[Dict[str, Any]]) -> float:
        """Estima la mejora en el balance después de aplicar las acciones."""
        if not actions:
            return 0
        
        # Simplificación: cada acción contribuye a la mejora
        total_adjustments = sum(
            abs(action.get("reduction_amount", 0)) + abs(action.get("increase_amount", 0))
            for action in actions
        )
        
        # Convertir a porcentaje de mejora (máximo 50%)
        improvement = min(50, total_adjustments / 10)
        return round(improvement, 2)
    
    def _calculate_capacity_optimization_score(self, actions: List[Dict[str, Any]]) -> float:
        """Calcula una puntuación de optimización de capacidad."""
        if not actions:
            return 100  # Ya está optimizado
        
        high_priority_actions = sum(1 for a in actions if a.get("priority") == "high")
        total_actions = len(actions)
        
        # Puntuación basada en la proporción de acciones de alta prioridad
        if total_actions == 0:
            return 100
        
        optimization_needed = (high_priority_actions / total_actions) * 100
        current_score = 100 - optimization_needed
        
        return max(0, round(current_score, 2))
    
    def _calculate_skill_distribution_score(self, workloads: List[Dict[str, Any]]) -> float:
        """Calcula una puntuación de distribución de habilidades."""
        if not workloads:
            return 100
        
        role_counts = [w["role_count"] for w in workloads]
        avg_roles = sum(role_counts) / len(role_counts)
        
        # Calcular varianza en la distribución de roles
        variance = sum((count - avg_roles) ** 2 for count in role_counts) / len(role_counts)
        
        # Convertir a puntuación (menor varianza = mejor distribución)
        distribution_score = max(0, 100 - (variance * 10))
        return round(distribution_score, 2)
    
    async def _simulate_balancing_impact(
        self, 
        current_distribution: Dict[str, Any], 
        balancing_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simula el impacto del plan de balanceo."""
        actions = balancing_plan["actions"]
        current_stats = current_distribution["distribution_stats"]
        
        # Simular nueva distribución después de aplicar acciones
        simulated_std_dev = max(0, current_stats["standard_deviation"] - len(actions) * 2)
        simulated_range = max(0, current_stats["range"] - len(actions) * 5)
        
        # Calcular mejoras
        std_dev_improvement = current_stats["standard_deviation"] - simulated_std_dev
        range_improvement = current_stats["range"] - simulated_range
        
        # Calcular porcentaje de mejora general
        improvement_percentage = min(50, (std_dev_improvement + range_improvement) / 2)
        
        return {
            "current_standard_deviation": current_stats["standard_deviation"],
            "projected_standard_deviation": round(simulated_std_dev, 2),
            "standard_deviation_improvement": round(std_dev_improvement, 2),
            "current_range": current_stats["range"],
            "projected_range": round(simulated_range, 2),
            "range_improvement": round(range_improvement, 2),
            "improvement_percentage": round(improvement_percentage, 2),
            "balance_score_improvement": round(improvement_percentage * 1.5, 2),
            "implementation_complexity": self._assess_implementation_complexity(actions)
        }
    
    def _assess_implementation_complexity(self, actions: List[Dict[str, Any]]) -> str:
        """Evalúa la complejidad de implementación del plan."""
        if not actions:
            return "none"
        
        total_actions = len(actions)
        high_priority_actions = sum(1 for a in actions if a.get("priority") == "high")
        
        if total_actions <= 2:
            return "low"
        elif total_actions <= 5 and high_priority_actions <= 1:
            return "medium"
        elif total_actions <= 8 and high_priority_actions <= 2:
            return "high"
        else:
            return "very_high"
    
    async def _generate_implementation_steps(
        self, 
        balancing_plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera pasos de implementación para el plan de balanceo."""
        actions = balancing_plan["actions"]
        
        if not actions:
            return []
        
        # Agrupar acciones por prioridad
        high_priority = [a for a in actions if a.get("priority") == "high"]
        medium_priority = [a for a in actions if a.get("priority") == "medium"]
        low_priority = [a for a in actions if a.get("priority") == "low"]
        
        steps = []
        step_number = 1
        
        # Paso 1: Acciones de alta prioridad
        if high_priority:
            steps.append({
                "step_number": step_number,
                "phase": "critical_adjustments",
                "description": "Resolver sobreasignaciones críticas y conflictos de alta prioridad",
                "actions": high_priority,
                "estimated_duration": "1-2 días",
                "dependencies": []
            })
            step_number += 1
        
        # Paso 2: Acciones de prioridad media
        if medium_priority:
            dependencies = ["critical_adjustments"] if high_priority else []
            steps.append({
                "step_number": step_number,
                "phase": "optimization_adjustments",
                "description": "Optimizar distribución y mejorar utilización",
                "actions": medium_priority,
                "estimated_duration": "2-3 días",
                "dependencies": dependencies
            })
            step_number += 1
        
        # Paso 3: Acciones de baja prioridad
        if low_priority:
            dependencies = []
            if high_priority:
                dependencies.append("critical_adjustments")
            if medium_priority:
                dependencies.append("optimization_adjustments")
            
            steps.append({
                "step_number": step_number,
                "phase": "fine_tuning",
                "description": "Ajustes finales y optimizaciones menores",
                "actions": low_priority,
                "estimated_duration": "1 día",
                "dependencies": dependencies
            })
        
        # Paso final: Validación
        steps.append({
            "step_number": len(steps) + 1,
            "phase": "validation",
            "description": "Validar resultados y monitorear impacto",
            "actions": [],
            "estimated_duration": "1 día",
            "dependencies": [step["phase"] for step in steps]
        })
        
        return steps