# src/planificador/services/domain/project_assignment/modules/validation_operations.py

"""
Módulo de Operaciones de Validación para Asignaciones de Proyecto

Implementa validaciones de reglas de negocio, verificaciones de integridad,
validaciones de restricciones de carga de trabajo y detección de conflictos
para asignaciones de proyecto.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, timedelta
from loguru import logger

from planificador.schemas import ProjectAssignment, ProjectAssignmentCreate, ProjectAssignmentUpdate
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.exceptions import ValidationError, RepositoryError
from ..interfaces import IValidationOperations


class ValidationOperations(IValidationOperations):
    """
    Implementación de operaciones de validación avanzadas.
    
    Proporciona validaciones completas de reglas de negocio,
    verificaciones de integridad de datos, validaciones de
    restricciones de carga de trabajo y detección de conflictos.
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """
        Inicializa el módulo de operaciones de validación.
        
        Args:
            repository_facade: Facade del repositorio de asignaciones
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="project_assignment_validation")
        
        # Configuración de reglas de negocio
        self._business_rules = {
            "max_allocation_percentage": 100,
            "max_daily_hours": 8,
            "min_assignment_duration_days": 1,
            "max_assignment_duration_days": 730,  # 2 años
            "max_concurrent_assignments": 5,
            "min_percentage_allocation": 1,
            "overlap_tolerance_days": 0
        }
    
    async def validate_assignment_business_rules(
        self, 
        assignment_data: ProjectAssignmentCreate
    ) -> Dict[str, Any]:
        """
        Valida que una asignación cumple con las reglas de negocio.
        
        Args:
            assignment_data: Datos de la asignación a validar
            
        Returns:
            Dict[str, Any]: Resultado de validación con detalles
            
        Raises:
            ValidationError: Si los datos de entrada no son válidos
            RepositoryError: Si hay errores en las consultas de validación
        """
        try:
            self._logger.info(
                f"Validando reglas de negocio para asignación "
                f"empleado {assignment_data.employee_id} - proyecto {assignment_data.project_id}"
            )
            
            validation_results = {
                "is_valid": True,
                "violations": [],
                "warnings": [],
                "validation_details": {}
            }
            
            # Validación 1: Datos básicos
            basic_validation = await self._validate_basic_data(assignment_data)
            validation_results["validation_details"]["basic_data"] = basic_validation
            if not basic_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["violations"].extend(basic_validation["violations"])
            
            # Validación 2: Fechas
            date_validation = await self._validate_dates(assignment_data)
            validation_results["validation_details"]["dates"] = date_validation
            if not date_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["violations"].extend(date_validation["violations"])
            
            # Validación 3: Porcentaje de asignación
            allocation_validation = await self._validate_allocation_percentage(assignment_data)
            validation_results["validation_details"]["allocation"] = allocation_validation
            if not allocation_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["violations"].extend(allocation_validation["violations"])
            
            # Validación 4: Horas diarias
            hours_validation = await self._validate_daily_hours(assignment_data)
            validation_results["validation_details"]["daily_hours"] = hours_validation
            if not hours_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["violations"].extend(hours_validation["violations"])
            
            # Validación 5: Duración de asignación
            duration_validation = await self._validate_assignment_duration(assignment_data)
            validation_results["validation_details"]["duration"] = duration_validation
            if not duration_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["violations"].extend(duration_validation["violations"])
            
            # Validación 6: Existencia de entidades relacionadas
            entity_validation = await self._validate_related_entities(assignment_data)
            validation_results["validation_details"]["related_entities"] = entity_validation
            if not entity_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["violations"].extend(entity_validation["violations"])
            
            # Validación 7: Reglas específicas del rol
            role_validation = await self._validate_role_specific_rules(assignment_data)
            validation_results["validation_details"]["role_rules"] = role_validation
            if not role_validation["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["violations"].extend(role_validation["violations"])
            
            # Agregar advertencias si las hay
            validation_results["warnings"].extend(basic_validation.get("warnings", []))
            validation_results["warnings"].extend(allocation_validation.get("warnings", []))
            validation_results["warnings"].extend(hours_validation.get("warnings", []))
            
            self._logger.info(
                f"Validación de reglas de negocio completada: "
                f"{'válida' if validation_results['is_valid'] else 'inválida'} "
                f"({len(validation_results['violations'])} violaciones, "
                f"{len(validation_results['warnings'])} advertencias)"
            )
            
            return validation_results
            
        except Exception as e:
            self._logger.error(f"Error al validar reglas de negocio: {e}")
            raise RepositoryError(
                message=f"Error al validar reglas de negocio: {e}",
                operation="validate_assignment_business_rules",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def check_workload_constraints(
        self, 
        employee_id: int, 
        new_assignment: ProjectAssignmentCreate,
        exclude_assignment_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Verifica las restricciones de carga de trabajo para un empleado.
        
        Args:
            employee_id: ID del empleado
            new_assignment: Nueva asignación a validar
            exclude_assignment_id: ID de asignación a excluir (para actualizaciones)
            
        Returns:
            Dict[str, Any]: Resultado de verificación de carga de trabajo
            
        Raises:
            ValidationError: Si el employee_id no es válido
            RepositoryError: Si hay errores en las consultas
        """
        try:
            self._logger.info(
                f"Verificando restricciones de carga de trabajo para empleado {employee_id}"
            )
            
            # Validar employee_id
            if employee_id <= 0:
                raise ValidationError(
                    message="El ID del empleado debe ser un número positivo",
                    field="employee_id",
                    value=employee_id
                )
            
            # Obtener asignaciones existentes del empleado
            existing_assignments = await self._repository.queries.get_assignments_by_employee(
                employee_id=employee_id,
                include_inactive=False
            )
            
            # Excluir asignación específica si se proporciona
            if exclude_assignment_id:
                existing_assignments = [
                    a for a in existing_assignments 
                    if a.id != exclude_assignment_id
                ]
            
            workload_check = {
                "is_valid": True,
                "violations": [],
                "warnings": [],
                "current_workload": {},
                "projected_workload": {},
                "recommendations": []
            }
            
            # Calcular carga de trabajo actual
            current_workload = self._calculate_current_workload(existing_assignments)
            workload_check["current_workload"] = current_workload
            
            # Calcular carga de trabajo proyectada con la nueva asignación
            projected_workload = self._calculate_projected_workload(
                existing_assignments, new_assignment
            )
            workload_check["projected_workload"] = projected_workload
            
            # Verificar restricciones de porcentaje total
            percentage_check = self._check_percentage_constraints(
                current_workload, projected_workload, new_assignment
            )
            if not percentage_check["is_valid"]:
                workload_check["is_valid"] = False
                workload_check["violations"].extend(percentage_check["violations"])
            workload_check["warnings"].extend(percentage_check.get("warnings", []))
            
            # Verificar restricciones de horas diarias
            hours_check = self._check_daily_hours_constraints(
                current_workload, projected_workload, new_assignment
            )
            if not hours_check["is_valid"]:
                workload_check["is_valid"] = False
                workload_check["violations"].extend(hours_check["violations"])
            workload_check["warnings"].extend(hours_check.get("warnings", []))
            
            # Verificar número máximo de asignaciones concurrentes
            concurrent_check = self._check_concurrent_assignments_limit(
                existing_assignments, new_assignment
            )
            if not concurrent_check["is_valid"]:
                workload_check["is_valid"] = False
                workload_check["violations"].extend(concurrent_check["violations"])
            
            # Verificar solapamientos problemáticos
            overlap_check = await self._check_problematic_overlaps(
                existing_assignments, new_assignment
            )
            if not overlap_check["is_valid"]:
                workload_check["is_valid"] = False
                workload_check["violations"].extend(overlap_check["violations"])
            workload_check["warnings"].extend(overlap_check.get("warnings", []))
            
            # Generar recomendaciones
            workload_check["recommendations"] = self._generate_workload_recommendations(
                current_workload, projected_workload, workload_check["violations"]
            )
            
            self._logger.info(
                f"Verificación de carga de trabajo completada: "
                f"{'válida' if workload_check['is_valid'] else 'inválida'} "
                f"({len(workload_check['violations'])} violaciones)"
            )
            
            return workload_check
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al verificar restricciones de carga de trabajo: {e}")
            raise RepositoryError(
                message=f"Error al verificar restricciones de carga de trabajo: {e}",
                operation="check_workload_constraints",
                entity_type="ProjectAssignment",
                entity_id=employee_id,
                original_error=e
            )
    
    async def validate_date_consistency(
        self, 
        assignment_data: ProjectAssignmentCreate
    ) -> Dict[str, Any]:
        """
        Valida la consistencia de fechas en una asignación.
        
        Args:
            assignment_data: Datos de la asignación a validar
            
        Returns:
            Dict[str, Any]: Resultado de validación de fechas
            
        Raises:
            ValidationError: Si los datos de fecha no son válidos
            RepositoryError: Si hay errores en las validaciones
        """
        try:
            self._logger.info("Validando consistencia de fechas")
            
            date_validation = {
                "is_valid": True,
                "violations": [],
                "warnings": [],
                "date_analysis": {}
            }
            
            start_date = assignment_data.start_date
            end_date = assignment_data.end_date
            
            # Validación 1: Fechas no nulas
            if not start_date or not end_date:
                date_validation["is_valid"] = False
                date_validation["violations"].append({
                    "rule": "required_dates",
                    "message": "Las fechas de inicio y fin son obligatorias",
                    "severity": "error"
                })
                return date_validation
            
            # Validación 2: Fecha de inicio anterior a fecha de fin
            if start_date >= end_date:
                date_validation["is_valid"] = False
                date_validation["violations"].append({
                    "rule": "date_order",
                    "message": "La fecha de inicio debe ser anterior a la fecha de fin",
                    "severity": "error",
                    "details": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                })
            
            # Validación 3: Fechas no en el pasado lejano
            min_date = date.today() - timedelta(days=365 * 2)  # 2 años atrás
            if start_date < min_date:
                date_validation["warnings"].append({
                    "rule": "historical_date",
                    "message": f"La fecha de inicio es muy antigua ({start_date})",
                    "severity": "warning"
                })
            
            # Validación 4: Fechas no muy lejanas en el futuro
            max_date = date.today() + timedelta(days=365 * 3)  # 3 años adelante
            if end_date > max_date:
                date_validation["warnings"].append({
                    "rule": "future_date",
                    "message": f"La fecha de fin está muy lejos en el futuro ({end_date})",
                    "severity": "warning"
                })
            
            # Validación 5: Duración razonable
            duration_days = (end_date - start_date).days + 1
            if duration_days < self._business_rules["min_assignment_duration_days"]:
                date_validation["is_valid"] = False
                date_validation["violations"].append({
                    "rule": "minimum_duration",
                    "message": f"La duración mínima es {self._business_rules['min_assignment_duration_days']} día(s)",
                    "severity": "error",
                    "details": {"current_duration": duration_days}
                })
            
            if duration_days > self._business_rules["max_assignment_duration_days"]:
                date_validation["is_valid"] = False
                date_validation["violations"].append({
                    "rule": "maximum_duration",
                    "message": f"La duración máxima es {self._business_rules['max_assignment_duration_days']} días",
                    "severity": "error",
                    "details": {"current_duration": duration_days}
                })
            
            # Validación 6: Fechas en días laborables (advertencia)
            if start_date.weekday() >= 5:  # Sábado o domingo
                date_validation["warnings"].append({
                    "rule": "weekend_start",
                    "message": "La fecha de inicio cae en fin de semana",
                    "severity": "info"
                })
            
            if end_date.weekday() >= 5:  # Sábado o domingo
                date_validation["warnings"].append({
                    "rule": "weekend_end",
                    "message": "La fecha de fin cae en fin de semana",
                    "severity": "info"
                })
            
            # Análisis de fechas
            date_validation["date_analysis"] = {
                "duration_days": duration_days,
                "duration_weeks": round(duration_days / 7, 1),
                "duration_months": round(duration_days / 30, 1),
                "start_weekday": start_date.strftime("%A"),
                "end_weekday": end_date.strftime("%A"),
                "crosses_year_boundary": start_date.year != end_date.year,
                "business_days": self._calculate_business_days(start_date, end_date)
            }
            
            self._logger.info(
                f"Validación de fechas completada: "
                f"duración {duration_days} días, "
                f"{'válida' if date_validation['is_valid'] else 'inválida'}"
            )
            
            return date_validation
            
        except Exception as e:
            self._logger.error(f"Error al validar consistencia de fechas: {e}")
            raise RepositoryError(
                message=f"Error al validar consistencia de fechas: {e}",
                operation="validate_date_consistency",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def check_assignment_conflicts(
        self, 
        assignment_data: ProjectAssignmentCreate,
        exclude_assignment_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Detecta conflictos con asignaciones existentes.
        
        Args:
            assignment_data: Datos de la nueva asignación
            exclude_assignment_id: ID de asignación a excluir (para actualizaciones)
            
        Returns:
            Dict[str, Any]: Resultado de detección de conflictos
            
        Raises:
            RepositoryError: Si hay errores en las consultas de conflictos
        """
        try:
            self._logger.info(
                f"Detectando conflictos para asignación "
                f"empleado {assignment_data.employee_id} - proyecto {assignment_data.project_id}"
            )
            
            conflict_check = {
                "has_conflicts": False,
                "conflicts": [],
                "potential_conflicts": [],
                "conflict_summary": {}
            }
            
            # Obtener asignaciones que podrían generar conflictos
            overlapping_assignments = await self._get_overlapping_assignments(
                assignment_data, exclude_assignment_id
            )
            
            if not overlapping_assignments:
                self._logger.info("No se encontraron asignaciones superpuestas")
                return conflict_check
            
            # Detectar conflictos de solapamiento temporal
            temporal_conflicts = self._detect_temporal_conflicts(
                assignment_data, overlapping_assignments
            )
            if temporal_conflicts:
                conflict_check["has_conflicts"] = True
                conflict_check["conflicts"].extend(temporal_conflicts)
            
            # Detectar conflictos de carga de trabajo
            workload_conflicts = self._detect_workload_conflicts(
                assignment_data, overlapping_assignments
            )
            if workload_conflicts:
                conflict_check["has_conflicts"] = True
                conflict_check["conflicts"].extend(workload_conflicts)
            
            # Detectar conflictos de rol
            role_conflicts = self._detect_role_conflicts(
                assignment_data, overlapping_assignments
            )
            if role_conflicts:
                conflict_check["potential_conflicts"].extend(role_conflicts)
            
            # Detectar conflictos de proyecto
            project_conflicts = self._detect_project_conflicts(
                assignment_data, overlapping_assignments
            )
            if project_conflicts:
                conflict_check["potential_conflicts"].extend(project_conflicts)
            
            # Generar resumen de conflictos
            conflict_check["conflict_summary"] = self._generate_conflict_summary(
                conflict_check["conflicts"], conflict_check["potential_conflicts"]
            )
            
            self._logger.info(
                f"Detección de conflictos completada: "
                f"{'conflictos encontrados' if conflict_check['has_conflicts'] else 'sin conflictos'} "
                f"({len(conflict_check['conflicts'])} críticos, "
                f"{len(conflict_check['potential_conflicts'])} potenciales)"
            )
            
            return conflict_check
            
        except Exception as e:
            self._logger.error(f"Error al detectar conflictos: {e}")
            raise RepositoryError(
                message=f"Error al detectar conflictos: {e}",
                operation="check_assignment_conflicts",
                entity_type="ProjectAssignment",
                original_error=e
            )
    
    async def validate_assignment_update_integrity(
        self, 
        assignment_id: int, 
        update_data: ProjectAssignmentUpdate
    ) -> Dict[str, Any]:
        """
        Valida la integridad de una actualización de asignación.
        
        Args:
            assignment_id: ID de la asignación a actualizar
            update_data: Datos de actualización
            
        Returns:
            Dict[str, Any]: Resultado de validación de integridad
            
        Raises:
            ValidationError: Si el assignment_id no es válido
            RepositoryError: Si hay errores en las validaciones
        """
        try:
            self._logger.info(f"Validando integridad de actualización para asignación {assignment_id}")
            
            # Validar assignment_id
            if assignment_id <= 0:
                raise ValidationError(
                    message="El ID de la asignación debe ser un número positivo",
                    field="assignment_id",
                    value=assignment_id
                )
            
            integrity_check = {
                "is_valid": True,
                "violations": [],
                "warnings": [],
                "update_analysis": {},
                "impact_assessment": {}
            }
            
            # Obtener asignación actual
            try:
                current_assignment = await self._repository.queries.get_assignment_by_id(assignment_id)
            except Exception:
                integrity_check["is_valid"] = False
                integrity_check["violations"].append({
                    "rule": "assignment_exists",
                    "message": f"No se encontró la asignación con ID {assignment_id}",
                    "severity": "error"
                })
                return integrity_check
            
            # Validar campos que se pueden actualizar
            updatable_fields = self._validate_updatable_fields(update_data)
            integrity_check["update_analysis"]["updatable_fields"] = updatable_fields
            if not updatable_fields["is_valid"]:
                integrity_check["is_valid"] = False
                integrity_check["violations"].extend(updatable_fields["violations"])
            
            # Validar cambios de fechas
            if update_data.start_date or update_data.end_date:
                date_changes = await self._validate_date_changes(
                    current_assignment, update_data
                )
                integrity_check["update_analysis"]["date_changes"] = date_changes
                if not date_changes["is_valid"]:
                    integrity_check["is_valid"] = False
                    integrity_check["violations"].extend(date_changes["violations"])
                integrity_check["warnings"].extend(date_changes.get("warnings", []))
            
            # Validar cambios de asignación
            if update_data.percentage_allocation or update_data.allocated_hours_per_day:
                allocation_changes = await self._validate_allocation_changes(
                    current_assignment, update_data
                )
                integrity_check["update_analysis"]["allocation_changes"] = allocation_changes
                if not allocation_changes["is_valid"]:
                    integrity_check["is_valid"] = False
                    integrity_check["violations"].extend(allocation_changes["violations"])
                integrity_check["warnings"].extend(allocation_changes.get("warnings", []))
            
            # Validar cambios de rol
            if update_data.role_in_project:
                role_changes = await self._validate_role_changes(
                    current_assignment, update_data
                )
                integrity_check["update_analysis"]["role_changes"] = role_changes
                if not role_changes["is_valid"]:
                    integrity_check["is_valid"] = False
                    integrity_check["violations"].extend(role_changes["violations"])
                integrity_check["warnings"].extend(role_changes.get("warnings", []))
            
            # Evaluar impacto de los cambios
            integrity_check["impact_assessment"] = await self._assess_update_impact(
                current_assignment, update_data
            )
            
            # Validar que la actualización no genere conflictos
            if integrity_check["is_valid"]:
                # Crear datos temporales para validación de conflictos
                temp_assignment_data = self._create_temp_assignment_for_validation(
                    current_assignment, update_data
                )
                
                conflict_check = await self.check_assignment_conflicts(
                    temp_assignment_data, exclude_assignment_id=assignment_id
                )
                
                if conflict_check["has_conflicts"]:
                    integrity_check["is_valid"] = False
                    integrity_check["violations"].append({
                        "rule": "update_conflicts",
                        "message": "La actualización generaría conflictos con otras asignaciones",
                        "severity": "error",
                        "details": conflict_check["conflicts"]
                    })
            
            self._logger.info(
                f"Validación de integridad de actualización completada: "
                f"{'válida' if integrity_check['is_valid'] else 'inválida'} "
                f"({len(integrity_check['violations'])} violaciones)"
            )
            
            return integrity_check
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al validar integridad de actualización: {e}")
            raise RepositoryError(
                message=f"Error al validar integridad de actualización: {e}",
                operation="validate_assignment_update_integrity",
                entity_type="ProjectAssignment",
                entity_id=assignment_id,
                original_error=e
            )
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE VALIDACIÓN BÁSICA
    # ============================================================================
    
    async def _validate_basic_data(self, assignment_data: ProjectAssignmentCreate) -> Dict[str, Any]:
        """Valida datos básicos de la asignación."""
        validation = {"is_valid": True, "violations": [], "warnings": []}
        
        # Validar IDs
        if assignment_data.employee_id <= 0:
            validation["is_valid"] = False
            validation["violations"].append({
                "rule": "valid_employee_id",
                "message": "El ID del empleado debe ser un número positivo",
                "field": "employee_id",
                "value": assignment_data.employee_id
            })
        
        if assignment_data.project_id <= 0:
            validation["is_valid"] = False
            validation["violations"].append({
                "rule": "valid_project_id",
                "message": "El ID del proyecto debe ser un número positivo",
                "field": "project_id",
                "value": assignment_data.project_id
            })
        
        # Validar rol
        if not assignment_data.role_in_project or not assignment_data.role_in_project.strip():
            validation["is_valid"] = False
            validation["violations"].append({
                "rule": "required_role",
                "message": "El rol en el proyecto es obligatorio",
                "field": "role_in_project"
            })
        elif len(assignment_data.role_in_project.strip()) < 2:
            validation["warnings"].append({
                "rule": "role_length",
                "message": "El rol especificado es muy corto",
                "field": "role_in_project"
            })
        
        return validation
    
    async def _validate_dates(self, assignment_data: ProjectAssignmentCreate) -> Dict[str, Any]:
        """Valida las fechas de la asignación."""
        validation = {"is_valid": True, "violations": [], "warnings": []}
        
        if not assignment_data.start_date:
            validation["is_valid"] = False
            validation["violations"].append({
                "rule": "required_start_date",
                "message": "La fecha de inicio es obligatoria",
                "field": "start_date"
            })
        
        if not assignment_data.end_date:
            validation["is_valid"] = False
            validation["violations"].append({
                "rule": "required_end_date",
                "message": "La fecha de fin es obligatoria",
                "field": "end_date"
            })
        
        if assignment_data.start_date and assignment_data.end_date:
            if assignment_data.start_date >= assignment_data.end_date:
                validation["is_valid"] = False
                validation["violations"].append({
                    "rule": "date_order",
                    "message": "La fecha de inicio debe ser anterior a la fecha de fin",
                    "fields": ["start_date", "end_date"]
                })
        
        return validation
    
    async def _validate_allocation_percentage(self, assignment_data: ProjectAssignmentCreate) -> Dict[str, Any]:
        """Valida el porcentaje de asignación."""
        validation = {"is_valid": True, "violations": [], "warnings": []}
        
        percentage = assignment_data.percentage_allocation
        
        if percentage < self._business_rules["min_percentage_allocation"]:
            validation["is_valid"] = False
            validation["violations"].append({
                "rule": "minimum_percentage",
                "message": f"El porcentaje mínimo de asignación es {self._business_rules['min_percentage_allocation']}%",
                "field": "percentage_allocation",
                "value": percentage
            })
        
        if percentage > self._business_rules["max_allocation_percentage"]:
            validation["warnings"].append({
                "rule": "high_percentage",
                "message": f"Porcentaje de asignación alto ({percentage}%), verificar carga de trabajo",
                "field": "percentage_allocation",
                "value": percentage
            })
        
        return validation
    
    async def _validate_daily_hours(self, assignment_data: ProjectAssignmentCreate) -> Dict[str, Any]:
        """Valida las horas diarias asignadas."""
        validation = {"is_valid": True, "violations": [], "warnings": []}
        
        hours = assignment_data.allocated_hours_per_day
        
        if hours <= 0:
            validation["is_valid"] = False
            validation["violations"].append({
                "rule": "positive_hours",
                "message": "Las horas diarias deben ser un número positivo",
                "field": "allocated_hours_per_day",
                "value": hours
            })
        
        if hours > self._business_rules["max_daily_hours"]:
            validation["warnings"].append({
                "rule": "high_daily_hours",
                "message": f"Horas diarias altas ({hours}h), máximo recomendado: {self._business_rules['max_daily_hours']}h",
                "field": "allocated_hours_per_day",
                "value": hours
            })
        
        # Verificar consistencia entre porcentaje y horas
        expected_hours = (assignment_data.percentage_allocation / 100) * 8  # Asumiendo 8h día laboral
        if abs(hours - expected_hours) > 1:  # Tolerancia de 1 hora
            validation["warnings"].append({
                "rule": "percentage_hours_consistency",
                "message": f"Inconsistencia entre porcentaje ({assignment_data.percentage_allocation}%) y horas ({hours}h)",
                "expected_hours": round(expected_hours, 2)
            })
        
        return validation
    
    async def _validate_assignment_duration(self, assignment_data: ProjectAssignmentCreate) -> Dict[str, Any]:
        """Valida la duración de la asignación."""
        validation = {"is_valid": True, "violations": [], "warnings": []}
        
        if assignment_data.start_date and assignment_data.end_date:
            duration_days = (assignment_data.end_date - assignment_data.start_date).days + 1
            
            if duration_days < self._business_rules["min_assignment_duration_days"]:
                validation["is_valid"] = False
                validation["violations"].append({
                    "rule": "minimum_duration",
                    "message": f"Duración mínima: {self._business_rules['min_assignment_duration_days']} día(s)",
                    "current_duration": duration_days
                })
            
            if duration_days > self._business_rules["max_assignment_duration_days"]:
                validation["is_valid"] = False
                validation["violations"].append({
                    "rule": "maximum_duration",
                    "message": f"Duración máxima: {self._business_rules['max_assignment_duration_days']} días",
                    "current_duration": duration_days
                })
        
        return validation
    
    async def _validate_related_entities(self, assignment_data: ProjectAssignmentCreate) -> Dict[str, Any]:
        """Valida la existencia de entidades relacionadas."""
        validation = {"is_valid": True, "violations": [], "warnings": []}
        
        # Nota: En una implementación real, aquí se verificaría la existencia
        # del empleado y proyecto en sus respectivos repositorios
        # Por ahora, asumimos que existen si los IDs son válidos
        
        return validation
    
    async def _validate_role_specific_rules(self, assignment_data: ProjectAssignmentCreate) -> Dict[str, Any]:
        """Valida reglas específicas según el rol."""
        validation = {"is_valid": True, "violations": [], "warnings": []}
        
        role = assignment_data.role_in_project.lower()
        
        # Reglas específicas por rol (ejemplos)
        if "manager" in role or "lead" in role:
            if assignment_data.percentage_allocation < 50:
                validation["warnings"].append({
                    "rule": "manager_allocation",
                    "message": "Los roles de liderazgo típicamente requieren mayor dedicación (≥50%)",
                    "current_percentage": assignment_data.percentage_allocation
                })
        
        if "intern" in role or "junior" in role:
            if assignment_data.percentage_allocation > 80:
                validation["warnings"].append({
                    "rule": "junior_allocation",
                    "message": "Asignación alta para rol junior, considerar capacidad de aprendizaje",
                    "current_percentage": assignment_data.percentage_allocation
                })
        
        return validation
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE CARGA DE TRABAJO
    # ============================================================================
    
    def _calculate_current_workload(self, assignments: List[ProjectAssignment]) -> Dict[str, Any]:
        """Calcula la carga de trabajo actual."""
        if not assignments:
            return {
                "total_percentage": 0,
                "total_hours": 0,
                "assignment_count": 0,
                "active_assignments": []
            }
        
        today = date.today()
        active_assignments = [
            a for a in assignments
            if a.start_date <= today <= a.end_date
        ]
        
        total_percentage = sum(a.percentage_allocation for a in active_assignments)
        total_hours = sum(a.allocated_hours_per_day for a in active_assignments)
        
        return {
            "total_percentage": total_percentage,
            "total_hours": total_hours,
            "assignment_count": len(active_assignments),
            "active_assignments": [
                {
                    "id": a.id,
                    "project_id": a.project_id,
                    "role": a.role_in_project,
                    "percentage": a.percentage_allocation,
                    "hours": a.allocated_hours_per_day,
                    "start_date": a.start_date,
                    "end_date": a.end_date
                }
                for a in active_assignments
            ]
        }
    
    def _calculate_projected_workload(
        self, 
        existing_assignments: List[ProjectAssignment], 
        new_assignment: ProjectAssignmentCreate
    ) -> Dict[str, Any]:
        """Calcula la carga de trabajo proyectada con la nueva asignación."""
        # Simular la nueva asignación como ProjectAssignment
        temp_assignment = type('TempAssignment', (), {
            'id': -1,
            'employee_id': new_assignment.employee_id,
            'project_id': new_assignment.project_id,
            'role_in_project': new_assignment.role_in_project,
            'percentage_allocation': new_assignment.percentage_allocation,
            'allocated_hours_per_day': new_assignment.allocated_hours_per_day,
            'start_date': new_assignment.start_date,
            'end_date': new_assignment.end_date
        })()
        
        all_assignments = existing_assignments + [temp_assignment]
        
        # Calcular solapamientos en diferentes períodos
        periods = self._generate_analysis_periods(all_assignments)
        period_workloads = {}
        
        for period_start, period_end in periods:
            overlapping = [
                a for a in all_assignments
                if a.start_date <= period_end and a.end_date >= period_start
            ]
            
            period_key = f"{period_start}_{period_end}"
            period_workloads[period_key] = {
                "period_start": period_start,
                "period_end": period_end,
                "total_percentage": sum(a.percentage_allocation for a in overlapping),
                "total_hours": sum(a.allocated_hours_per_day for a in overlapping),
                "assignment_count": len(overlapping),
                "assignments": [a.id if hasattr(a, 'id') and a.id != -1 else 'new' for a in overlapping]
            }
        
        # Encontrar el período con mayor carga
        max_workload_period = max(
            period_workloads.values(),
            key=lambda p: p["total_percentage"]
        ) if period_workloads else None
        
        return {
            "period_analysis": period_workloads,
            "peak_workload": max_workload_period,
            "includes_new_assignment": True
        }
    
    def _generate_analysis_periods(self, assignments: List) -> List[Tuple[date, date]]:
        """Genera períodos de análisis basados en las fechas de las asignaciones."""
        if not assignments:
            return []
        
        # Obtener todas las fechas únicas
        dates = set()
        for assignment in assignments:
            dates.add(assignment.start_date)
            dates.add(assignment.end_date)
        
        sorted_dates = sorted(dates)
        
        # Crear períodos entre fechas consecutivas
        periods = []
        for i in range(len(sorted_dates) - 1):
            periods.append((sorted_dates[i], sorted_dates[i + 1]))
        
        return periods
    
    def _check_percentage_constraints(
        self, 
        current_workload: Dict[str, Any], 
        projected_workload: Dict[str, Any], 
        new_assignment: ProjectAssignmentCreate
    ) -> Dict[str, Any]:
        """Verifica restricciones de porcentaje de asignación."""
        check = {"is_valid": True, "violations": [], "warnings": []}
        
        peak_workload = projected_workload.get("peak_workload", {})
        peak_percentage = peak_workload.get("total_percentage", 0)
        
        if peak_percentage > 100:
            check["is_valid"] = False
            check["violations"].append({
                "rule": "percentage_overallocation",
                "message": f"La asignación resultaría en sobreasignación ({peak_percentage}%)",
                "current_total": current_workload.get("total_percentage", 0),
                "new_assignment_percentage": new_assignment.percentage_allocation,
                "projected_total": peak_percentage
            })
        elif peak_percentage > 90:
            check["warnings"].append({
                "rule": "high_percentage_utilization",
                "message": f"Alta utilización proyectada ({peak_percentage}%)",
                "projected_total": peak_percentage
            })
        
        return check
    
    def _check_daily_hours_constraints(
        self, 
        current_workload: Dict[str, Any], 
        projected_workload: Dict[str, Any], 
        new_assignment: ProjectAssignmentCreate
    ) -> Dict[str, Any]:
        """Verifica restricciones de horas diarias."""
        check = {"is_valid": True, "violations": [], "warnings": []}
        
        peak_workload = projected_workload.get("peak_workload", {})
        peak_hours = peak_workload.get("total_hours", 0)
        
        if peak_hours > self._business_rules["max_daily_hours"]:
            check["is_valid"] = False
            check["violations"].append({
                "rule": "hours_overallocation",
                "message": f"Las horas diarias excederían el máximo ({peak_hours}h > {self._business_rules['max_daily_hours']}h)",
                "current_total": current_workload.get("total_hours", 0),
                "new_assignment_hours": new_assignment.allocated_hours_per_day,
                "projected_total": peak_hours
            })
        elif peak_hours > self._business_rules["max_daily_hours"] * 0.9:
            check["warnings"].append({
                "rule": "high_hours_utilization",
                "message": f"Alta carga de horas diarias ({peak_hours}h)",
                "projected_total": peak_hours
            })
        
        return check
    
    def _check_concurrent_assignments_limit(
        self, 
        existing_assignments: List[ProjectAssignment], 
        new_assignment: ProjectAssignmentCreate
    ) -> Dict[str, Any]:
        """Verifica el límite de asignaciones concurrentes."""
        check = {"is_valid": True, "violations": [], "warnings": []}
        
        # Contar asignaciones que se superponen con la nueva
        overlapping_count = 0
        for assignment in existing_assignments:
            if (assignment.start_date <= new_assignment.end_date and 
                assignment.end_date >= new_assignment.start_date):
                overlapping_count += 1
        
        total_concurrent = overlapping_count + 1  # +1 por la nueva asignación
        
        if total_concurrent > self._business_rules["max_concurrent_assignments"]:
            check["is_valid"] = False
            check["violations"].append({
                "rule": "max_concurrent_assignments",
                "message": f"Excede el máximo de asignaciones concurrentes ({total_concurrent} > {self._business_rules['max_concurrent_assignments']})",
                "current_concurrent": overlapping_count,
                "projected_concurrent": total_concurrent
            })
        elif total_concurrent > self._business_rules["max_concurrent_assignments"] * 0.8:
            check["warnings"].append({
                "rule": "high_concurrent_assignments",
                "message": f"Alto número de asignaciones concurrentes ({total_concurrent})",
                "projected_concurrent": total_concurrent
            })
        
        return check
    
    async def _check_problematic_overlaps(
        self, 
        existing_assignments: List[ProjectAssignment], 
        new_assignment: ProjectAssignmentCreate
    ) -> Dict[str, Any]:
        """Verifica solapamientos problemáticos."""
        check = {"is_valid": True, "violations": [], "warnings": []}
        
        for assignment in existing_assignments:
            # Verificar solapamiento temporal
            if (assignment.start_date <= new_assignment.end_date and 
                assignment.end_date >= new_assignment.start_date):
                
                # Solapamiento en el mismo proyecto con diferente rol
                if (assignment.project_id == new_assignment.project_id and 
                    assignment.role_in_project != new_assignment.role_in_project):
                    check["warnings"].append({
                        "rule": "same_project_different_role",
                        "message": f"Múltiples roles en el mismo proyecto (actual: {assignment.role_in_project}, nuevo: {new_assignment.role_in_project})",
                        "conflicting_assignment_id": assignment.id,
                        "project_id": assignment.project_id
                    })
                
                # Solapamiento exacto (mismas fechas, mismo proyecto, mismo rol)
                if (assignment.project_id == new_assignment.project_id and 
                    assignment.role_in_project == new_assignment.role_in_project and
                    assignment.start_date == new_assignment.start_date and
                    assignment.end_date == new_assignment.end_date):
                    check["is_valid"] = False
                    check["violations"].append({
                        "rule": "duplicate_assignment",
                        "message": "Asignación duplicada (mismo proyecto, rol y fechas)",
                        "conflicting_assignment_id": assignment.id
                    })
        
        return check
    
    def _generate_workload_recommendations(
        self, 
        current_workload: Dict[str, Any], 
        projected_workload: Dict[str, Any], 
        violations: List[Dict[str, Any]]
    ) -> List[str]:
        """Genera recomendaciones para optimizar la carga de trabajo."""
        recommendations = []
        
        peak_workload = projected_workload.get("peak_workload", {})
        peak_percentage = peak_workload.get("total_percentage", 0)
        
        if peak_percentage > 100:
            excess = peak_percentage - 100
            recommendations.append(
                f"Reducir la asignación en {excess}% para evitar sobreasignación"
            )
            recommendations.append(
                "Considerar redistribuir carga entre otros miembros del equipo"
            )
        
        if peak_workload.get("assignment_count", 0) > 3:
            recommendations.append(
                "Alto número de asignaciones concurrentes, considerar consolidar proyectos"
            )
        
        if any(v["rule"] == "same_project_different_role" for v in violations):
            recommendations.append(
                "Evaluar si es necesario tener múltiples roles en el mismo proyecto"
            )
        
        if not recommendations:
            recommendations.append("La carga de trabajo proyectada es adecuada")
        
        return recommendations
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE CONFLICTOS
    # ============================================================================
    
    async def _get_overlapping_assignments(
        self, 
        assignment_data: ProjectAssignmentCreate, 
        exclude_assignment_id: Optional[int] = None
    ) -> List[ProjectAssignment]:
        """Obtiene asignaciones que se superponen temporalmente."""
        # Obtener asignaciones del empleado
        employee_assignments = await self._repository.queries.get_assignments_by_employee(
            employee_id=assignment_data.employee_id,
            include_inactive=True
        )
        
        # Filtrar por solapamiento temporal
        overlapping = []
        for assignment in employee_assignments:
            # Excluir asignación específica si se proporciona
            if exclude_assignment_id and assignment.id == exclude_assignment_id:
                continue
            
            # Verificar solapamiento
            if (assignment.start_date <= assignment_data.end_date and 
                assignment.end_date >= assignment_data.start_date):
                overlapping.append(assignment)
        
        return overlapping
    
    def _detect_temporal_conflicts(
        self, 
        assignment_data: ProjectAssignmentCreate, 
        overlapping_assignments: List[ProjectAssignment]
    ) -> List[Dict[str, Any]]:
        """Detecta conflictos temporales críticos."""
        conflicts = []
        
        for assignment in overlapping_assignments:
            # Conflicto: solapamiento completo
            if (assignment.start_date <= assignment_data.start_date and 
                assignment.end_date >= assignment_data.end_date):
                conflicts.append({
                    "type": "complete_overlap",
                    "severity": "high",
                    "message": "Solapamiento completo con asignación existente",
                    "conflicting_assignment": {
                        "id": assignment.id,
                        "project_id": assignment.project_id,
                        "role": assignment.role_in_project,
                        "start_date": assignment.start_date,
                        "end_date": assignment.end_date
                    },
                    "overlap_days": (assignment_data.end_date - assignment_data.start_date).days + 1
                })
            
            # Conflicto: solapamiento parcial significativo
            else:
                overlap_start = max(assignment.start_date, assignment_data.start_date)
                overlap_end = min(assignment.end_date, assignment_data.end_date)
                overlap_days = (overlap_end - overlap_start).days + 1
                
                if overlap_days > 7:  # Más de una semana de solapamiento
                    conflicts.append({
                        "type": "significant_overlap",
                        "severity": "medium",
                        "message": f"Solapamiento significativo de {overlap_days} días",
                        "conflicting_assignment": {
                            "id": assignment.id,
                            "project_id": assignment.project_id,
                            "role": assignment.role_in_project,
                            "start_date": assignment.start_date,
                            "end_date": assignment.end_date
                        },
                        "overlap_days": overlap_days,
                        "overlap_period": {
                            "start": overlap_start,
                            "end": overlap_end
                        }
                    })
        
        return conflicts
    
    def _detect_workload_conflicts(
        self, 
        assignment_data: ProjectAssignmentCreate, 
        overlapping_assignments: List[ProjectAssignment]
    ) -> List[Dict[str, Any]]:
        """Detecta conflictos de carga de trabajo."""
        conflicts = []
        
        for assignment in overlapping_assignments:
            # Calcular carga combinada durante el solapamiento
            combined_percentage = assignment.percentage_allocation + assignment_data.percentage_allocation
            combined_hours = assignment.allocated_hours_per_day + assignment_data.allocated_hours_per_day
            
            if combined_percentage > 100:
                conflicts.append({
                    "type": "percentage_overload",
                    "severity": "high",
                    "message": f"Sobreasignación de porcentaje ({combined_percentage}%)",
                    "conflicting_assignment": {
                        "id": assignment.id,
                        "project_id": assignment.project_id,
                        "percentage": assignment.percentage_allocation
                    },
                    "combined_percentage": combined_percentage,
                    "excess_percentage": combined_percentage - 100
                })
            
            if combined_hours > self._business_rules["max_daily_hours"]:
                conflicts.append({
                    "type": "hours_overload",
                    "severity": "high",
                    "message": f"Exceso de horas diarias ({combined_hours}h)",
                    "conflicting_assignment": {
                        "id": assignment.id,
                        "project_id": assignment.project_id,
                        "hours": assignment.allocated_hours_per_day
                    },
                    "combined_hours": combined_hours,
                    "excess_hours": combined_hours - self._business_rules["max_daily_hours"]
                })
        
        return conflicts
    
    def _detect_role_conflicts(
        self, 
        assignment_data: ProjectAssignmentCreate, 
        overlapping_assignments: List[ProjectAssignment]
    ) -> List[Dict[str, Any]]:
        """Detecta conflictos potenciales de rol."""
        conflicts = []
        
        for assignment in overlapping_assignments:
            # Mismo proyecto, diferentes roles
            if (assignment.project_id == assignment_data.project_id and 
                assignment.role_in_project != assignment_data.role_in_project):
                conflicts.append({
                    "type": "multiple_roles_same_project",
                    "severity": "low",
                    "message": f"Múltiples roles en el mismo proyecto",
                    "conflicting_assignment": {
                        "id": assignment.id,
                        "current_role": assignment.role_in_project,
                        "new_role": assignment_data.role_in_project
                    },
                    "project_id": assignment.project_id
                })
            
            # Roles incompatibles (ejemplo: manager y junior en proyectos diferentes)
            if self._are_incompatible_roles(assignment.role_in_project, assignment_data.role_in_project):
                conflicts.append({
                    "type": "incompatible_roles",
                    "severity": "medium",
                    "message": "Roles potencialmente incompatibles",
                    "conflicting_assignment": {
                        "id": assignment.id,
                        "role": assignment.role_in_project,
                        "project_id": assignment.project_id
                    },
                    "role_conflict": {
                        "existing_role": assignment.role_in_project,
                        "new_role": assignment_data.role_in_project
                    }
                })
        
        return conflicts
    
    def _detect_project_conflicts(
        self, 
        assignment_data: ProjectAssignmentCreate, 
        overlapping_assignments: List[ProjectAssignment]
    ) -> List[Dict[str, Any]]:
        """Detecta conflictos potenciales de proyecto."""
        conflicts = []
        
        # Agrupar por proyecto
        projects = {}
        for assignment in overlapping_assignments:
            if assignment.project_id not in projects:
                projects[assignment.project_id] = []
            projects[assignment.project_id].append(assignment)
        
        # Verificar si hay demasiados proyectos concurrentes
        if len(projects) >= 3:  # 3 o más proyectos diferentes
            conflicts.append({
                "type": "too_many_concurrent_projects",
                "severity": "medium",
                "message": f"Demasiados proyectos concurrentes ({len(projects) + 1})",
                "concurrent_projects": list(projects.keys()) + [assignment_data.project_id],
                "project_count": len(projects) + 1
            })
        
        return conflicts
    
    def _are_incompatible_roles(self, role1: str, role2: str) -> bool:
        """Determina si dos roles son incompatibles."""
        role1_lower = role1.lower()
        role2_lower = role2.lower()
        
        # Ejemplos de incompatibilidades
        incompatible_pairs = [
            (["manager", "lead", "senior"], ["intern", "junior", "trainee"]),
            (["architect", "designer"], ["tester", "qa"]),
            (["frontend", "ui"], ["backend", "database"])
        ]
        
        for group1, group2 in incompatible_pairs:
            role1_in_group1 = any(keyword in role1_lower for keyword in group1)
            role2_in_group2 = any(keyword in role2_lower for keyword in group2)
            role1_in_group2 = any(keyword in role1_lower for keyword in group2)
            role2_in_group1 = any(keyword in role2_lower for keyword in group1)
            
            if (role1_in_group1 and role2_in_group2) or (role1_in_group2 and role2_in_group1):
                return True
        
        return False
    
    def _generate_conflict_summary(
        self, 
        conflicts: List[Dict[str, Any]], 
        potential_conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Genera un resumen de conflictos."""
        summary = {
            "total_conflicts": len(conflicts),
            "total_potential_conflicts": len(potential_conflicts),
            "severity_breakdown": {"high": 0, "medium": 0, "low": 0},
            "conflict_types": {},
            "most_critical": None
        }
        
        # Analizar conflictos críticos
        for conflict in conflicts:
            severity = conflict.get("severity", "medium")
            summary["severity_breakdown"][severity] += 1
            
            conflict_type = conflict.get("type", "unknown")
            if conflict_type not in summary["conflict_types"]:
                summary["conflict_types"][conflict_type] = 0
            summary["conflict_types"][conflict_type] += 1
        
        # Analizar conflictos potenciales
        for conflict in potential_conflicts:
            severity = conflict.get("severity", "low")
            if severity in summary["severity_breakdown"]:
                summary["severity_breakdown"][severity] += 1
            
            conflict_type = conflict.get("type", "unknown")
            if conflict_type not in summary["conflict_types"]:
                summary["conflict_types"][conflict_type] = 0
            summary["conflict_types"][conflict_type] += 1
        
        # Identificar el conflicto más crítico
        high_severity_conflicts = [c for c in conflicts if c.get("severity") == "high"]
        if high_severity_conflicts:
            summary["most_critical"] = high_severity_conflicts[0]
        elif conflicts:
            summary["most_critical"] = conflicts[0]
        
        return summary
    
    # ============================================================================
    # MÉTODOS PRIVADOS DE UTILIDAD
    # ============================================================================
    
    def _calculate_business_days(self, start_date: date, end_date: date) -> int:
        """Calcula el número de días laborables entre dos fechas."""
        business_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Lunes a viernes
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
    
    def _validate_updatable_fields(self, update_data: ProjectAssignmentUpdate) -> Dict[str, Any]:
        """Valida que los campos a actualizar sean válidos."""
        validation = {"is_valid": True, "violations": [], "updatable_fields": []}
        
        # Campos que se pueden actualizar
        updatable_fields = [
            "start_date", "end_date", "percentage_allocation", 
            "allocated_hours_per_day", "role_in_project"
        ]
        
        # Verificar qué campos se están intentando actualizar
        for field in updatable_fields:
            if hasattr(update_data, field) and getattr(update_data, field) is not None:
                validation["updatable_fields"].append(field)
        
        if not validation["updatable_fields"]:
            validation["is_valid"] = False
            validation["violations"].append({
                "rule": "no_fields_to_update",
                "message": "No se especificaron campos válidos para actualizar",
                "available_fields": updatable_fields
            })
        
        return validation
    
    async def _validate_date_changes(
        self, 
        current_assignment: ProjectAssignment, 
        update_data: ProjectAssignmentUpdate
    ) -> Dict[str, Any]:
        """Valida cambios en las fechas de una asignación."""
        validation = {"is_valid": True, "violations": [], "warnings": []}
        
        new_start = update_data.start_date or current_assignment.start_date
        new_end = update_data.end_date or current_assignment.end_date
        
        # Validar orden de fechas
        if new_start >= new_end:
            validation["is_valid"] = False
            validation["violations"].append({
                "rule": "invalid_date_order",
                "message": "La nueva fecha de inicio debe ser anterior a la fecha de fin",
                "new_start_date": new_start,
                "new_end_date": new_end
            })
        
        # Validar que no se reduzca demasiado la duración
        current_duration = (current_assignment.end_date - current_assignment.start_date).days + 1
        new_duration = (new_end - new_start).days + 1
        
        if new_duration < current_duration * 0.5:  # Reducción mayor al 50%
            validation["warnings"].append({
                "rule": "significant_duration_reduction",
                "message": f"Reducción significativa de duración ({current_duration} → {new_duration} días)",
                "current_duration": current_duration,
                "new_duration": new_duration
            })
        
        return validation
    
    async def _validate_allocation_changes(
        self, 
        current_assignment: ProjectAssignment, 
        update_data: ProjectAssignmentUpdate
    ) -> Dict[str, Any]:
        """Valida cambios en la asignación de recursos."""
        validation = {"is_valid": True, "violations": [], "warnings": []}
        
        new_percentage = update_data.percentage_allocation or current_assignment.percentage_allocation
        new_hours = update_data.allocated_hours_per_day or current_assignment.allocated_hours_per_day
        
        # Validar rangos válidos
        if new_percentage < self._business_rules["min_percentage_allocation"]:
            validation["is_valid"] = False
            validation["violations"].append({
                "rule": "minimum_percentage",
                "message": f"El porcentaje mínimo es {self._business_rules['min_percentage_allocation']}%",
                "new_percentage": new_percentage
            })
        
        if new_percentage > self._business_rules["max_allocation_percentage"]:
            validation["warnings"].append({
                "rule": "high_percentage",
                "message": f"Porcentaje alto ({new_percentage}%)",
                "new_percentage": new_percentage
            })
        
        if new_hours > self._business_rules["max_daily_hours"]:
            validation["warnings"].append({
                "rule": "high_hours",
                "message": f"Horas diarias altas ({new_hours}h)",
                "new_hours": new_hours
            })
        
        # Verificar cambios significativos
        percentage_change = abs(new_percentage - current_assignment.percentage_allocation)
        if percentage_change > 25:  # Cambio mayor al 25%
            validation["warnings"].append({
                "rule": "significant_percentage_change",
                "message": f"Cambio significativo en porcentaje ({percentage_change}%)",
                "old_percentage": current_assignment.percentage_allocation,
                "new_percentage": new_percentage
            })
        
        return validation
    
    async def _validate_role_changes(
        self, 
        current_assignment: ProjectAssignment, 
        update_data: ProjectAssignmentUpdate
    ) -> Dict[str, Any]:
        """Valida cambios en el rol de una asignación."""
        validation = {"is_valid": True, "violations": [], "warnings": []}
        
        new_role = update_data.role_in_project
        current_role = current_assignment.role_in_project
        
        if new_role and new_role != current_role:
            # Verificar que el nuevo rol no esté vacío
            if not new_role.strip():
                validation["is_valid"] = False
                validation["violations"].append({
                    "rule": "empty_role",
                    "message": "El rol no puede estar vacío",
                    "new_role": new_role
                })
            
            # Advertir sobre cambios de rol significativos
            if self._are_incompatible_roles(current_role, new_role):
                validation["warnings"].append({
                    "rule": "incompatible_role_change",
                    "message": f"Cambio de rol potencialmente incompatible ({current_role} → {new_role})",
                    "old_role": current_role,
                    "new_role": new_role
                })
        
        return validation
    
    async def _assess_update_impact(
        self, 
        current_assignment: ProjectAssignment, 
        update_data: ProjectAssignmentUpdate
    ) -> Dict[str, Any]:
        """Evalúa el impacto de los cambios propuestos."""
        impact = {
            "impact_level": "low",
            "affected_areas": [],
            "recommendations": []
        }
        
        # Evaluar impacto de cambios de fecha
        if update_data.start_date or update_data.end_date:
            impact["affected_areas"].append("timeline")
            impact["impact_level"] = "medium"
            impact["recommendations"].append("Verificar dependencias del proyecto")
        
        # Evaluar impacto de cambios de asignación
        if update_data.percentage_allocation or update_data.allocated_hours_per_day:
            impact["affected_areas"].append("resource_allocation")
            if impact["impact_level"] == "low":
                impact["impact_level"] = "medium"
            impact["recommendations"].append("Revisar carga de trabajo del empleado")
        
        # Evaluar impacto de cambios de rol
        if update_data.role_in_project:
            impact["affected_areas"].append("team_structure")
            impact["impact_level"] = "high"
            impact["recommendations"].append("Comunicar cambio de rol al equipo del proyecto")
        
        return impact
    
    def _create_temp_assignment_for_validation(
        self, 
        current_assignment: ProjectAssignment, 
        update_data: ProjectAssignmentUpdate
    ) -> ProjectAssignmentCreate:
        """Crea datos temporales de asignación para validación."""
        return ProjectAssignmentCreate(
            employee_id=current_assignment.employee_id,
            project_id=current_assignment.project_id,
            role_in_project=update_data.role_in_project or current_assignment.role_in_project,
            start_date=update_data.start_date or current_assignment.start_date,
            end_date=update_data.end_date or current_assignment.end_date,
            percentage_allocation=update_data.percentage_allocation or current_assignment.percentage_allocation,
            allocated_hours_per_day=update_data.allocated_hours_per_day or current_assignment.allocated_hours_per_day
        )