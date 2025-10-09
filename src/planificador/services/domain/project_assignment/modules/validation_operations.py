# src/planificador/services/domain/project_assignment/modules/validation_operations.py

"""
Módulo de Operaciones de Validación para Asignaciones de Proyecto

Implementa validaciones de reglas de negocio según la documentación oficial,
incluyendo validación de reglas de negocio, solapamientos, límites de carga,
eliminación de asignaciones y disponibilidad de empleados.
"""

from typing import Dict, Any, Optional
from datetime import date
from loguru import logger

from planificador.schemas import ProjectAssignment
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.exceptions import ValidationError, RepositoryError, BusinessLogicError
from ..interfaces import IValidationOperations


class ValidationOperations(IValidationOperations):
    """
    Implementación de operaciones de validación según documentación oficial.
    
    Proporciona los 5 métodos documentados para validación de reglas de negocio,
    solapamientos, límites de carga, eliminación y disponibilidad.
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
            "max_concurrent_assignments": 5,
            "min_percentage_allocation": 1,
            "max_percentage_allocation": 100,
            "overlap_tolerance_days": 0
        }

    async def validate_assignment_business_rules(
        self, 
        assignment_data: Dict[str, Any], 
        exclude_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Valida todas las reglas de negocio para asignaciones.
        
        Verifica que los datos de la asignación cumplan con todas las reglas
        de negocio establecidas, incluyendo porcentajes, fechas y restricciones.
        
        Args:
            assignment_data: Datos de la asignación a validar
            exclude_id: ID de asignación a excluir de validaciones (para actualizaciones)
            
        Returns:
            Dict con resultado de validación y detalles de errores si los hay
            
        Raises:
            ValidationError: Si los datos no cumplen las reglas de negocio
            RepositoryError: Si hay errores de acceso a datos
        """
        try:
            self._logger.info(f"Validando reglas de negocio para asignación")
            
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Validar porcentaje de asignación
            allocation_percentage = assignment_data.get("allocation_percentage", 0)
            if allocation_percentage < self._business_rules["min_percentage_allocation"]:
                validation_result["errors"].append(
                    f"El porcentaje de asignación debe ser al menos {self._business_rules['min_percentage_allocation']}%"
                )
                validation_result["is_valid"] = False
                
            if allocation_percentage > self._business_rules["max_percentage_allocation"]:
                validation_result["errors"].append(
                    f"El porcentaje de asignación no puede exceder {self._business_rules['max_percentage_allocation']}%"
                )
                validation_result["is_valid"] = False
            
            # Validar fechas
            start_date = assignment_data.get("start_date")
            end_date = assignment_data.get("end_date")
            
            if start_date and end_date:
                if start_date >= end_date:
                    validation_result["errors"].append(
                        "La fecha de inicio debe ser anterior a la fecha de fin"
                    )
                    validation_result["is_valid"] = False
            
            # Validar empleado y proyecto existen
            employee_id = assignment_data.get("employee_id")
            project_id = assignment_data.get("project_id")
            
            if employee_id and project_id:
                # Verificar límites de asignaciones concurrentes
                if start_date and end_date:
                    overlapping = await self._repository.get_overlapping_assignments(
                        employee_id=employee_id,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    # Excluir la asignación actual si se está actualizando
                    if exclude_id:
                        overlapping = [a for a in overlapping if a.id != exclude_id]
                    
                    if len(overlapping) >= self._business_rules["max_concurrent_assignments"]:
                        validation_result["errors"].append(
                            f"El empleado ya tiene el máximo de asignaciones concurrentes permitidas ({self._business_rules['max_concurrent_assignments']})"
                        )
                        validation_result["is_valid"] = False
            
            self._logger.info(f"Validación de reglas de negocio completada: {validation_result['is_valid']}")
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error validando reglas de negocio: {e}")
            raise ValidationError(
                message=f"Error en validación de reglas de negocio: {e}",
                operation="validate_assignment_business_rules",
                entity_type="ProjectAssignment",
                original_error=e
            )

    async def validate_no_overlapping_assignments(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Valida que no existan solapamientos de asignaciones.
        
        Verifica que el empleado no tenga asignaciones que se solapen
        con el período especificado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            exclude_id: ID de asignación a excluir de la validación
            
        Returns:
            True si no hay solapamientos, False si los hay
            
        Raises:
            ValidationError: Si hay errores en la validación
            RepositoryError: Si hay errores de acceso a datos
        """
        try:
            self._logger.info(f"Validando solapamientos para empleado {employee_id}")
            
            # Obtener asignaciones superpuestas
            overlapping_assignments = await self._repository.get_overlapping_assignments(
                employee_id=employee_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Excluir la asignación actual si se especifica
            if exclude_id:
                overlapping_assignments = [
                    assignment for assignment in overlapping_assignments 
                    if assignment.id != exclude_id
                ]
            
            has_overlaps = len(overlapping_assignments) > 0
            
            if has_overlaps:
                self._logger.warning(
                    f"Se encontraron {len(overlapping_assignments)} asignaciones superpuestas "
                    f"para empleado {employee_id} en período {start_date} - {end_date}"
                )
            else:
                self._logger.info(f"No se encontraron solapamientos para empleado {employee_id}")
            
            return not has_overlaps
            
        except Exception as e:
            self._logger.error(f"Error validando solapamientos: {e}")
            raise ValidationError(
                message=f"Error validando solapamientos: {e}",
                operation="validate_no_overlapping_assignments",
                entity_type="ProjectAssignment",
                entity_id=employee_id,
                original_error=e
            )

    async def validate_workload_limits(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date, 
        allocation_percentage: float
    ) -> bool:
        """
        Valida que la carga de trabajo no exceda límites establecidos.
        
        Verifica que la suma de porcentajes de asignación del empleado
        no exceda el 100% en el período especificado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            allocation_percentage: Porcentaje de asignación a validar
            
        Returns:
            True si la carga está dentro de límites, False si los excede
            
        Raises:
            ValidationError: Si hay errores en la validación
            RepositoryError: Si hay errores de acceso a datos
        """
        try:
            self._logger.info(
                f"Validando límites de carga para empleado {employee_id}, "
                f"asignación {allocation_percentage}%"
            )
            
            # Obtener asignaciones existentes en el período
            existing_assignments = await self._repository.get_overlapping_assignments(
                employee_id=employee_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Calcular carga total actual
            current_workload = sum(
                assignment.percentage_allocation 
                for assignment in existing_assignments
            )
            
            # Calcular carga total proyectada
            projected_workload = current_workload + allocation_percentage
            
            # Validar límites
            within_limits = projected_workload <= self._business_rules["max_allocation_percentage"]
            
            if not within_limits:
                self._logger.warning(
                    f"Carga de trabajo excede límites: actual {current_workload}% + "
                    f"nueva {allocation_percentage}% = {projected_workload}% "
                    f"(máximo: {self._business_rules['max_allocation_percentage']}%)"
                )
            else:
                self._logger.info(
                    f"Carga de trabajo dentro de límites: {projected_workload}%"
                )
            
            return within_limits
            
        except Exception as e:
            self._logger.error(f"Error validando límites de carga: {e}")
            raise ValidationError(
                message=f"Error validando límites de carga: {e}",
                operation="validate_workload_limits",
                entity_type="ProjectAssignment",
                entity_id=employee_id,
                original_error=e
            )

    async def validate_assignment_deletion(self, assignment_id: int) -> Dict[str, Any]:
        """
        Valida si una asignación puede ser eliminada sin impacto crítico.
        
        Verifica dependencias, impacto en proyectos y restricciones
        antes de permitir la eliminación de una asignación.
        
        Args:
            assignment_id: ID de la asignación a validar para eliminación
            
        Returns:
            Dict con resultado de validación y detalles del impacto
            
        Raises:
            ValidationError: Si hay errores en la validación
            RepositoryError: Si hay errores de acceso a datos
        """
        try:
            self._logger.info(f"Validando eliminación de asignación {assignment_id}")
            
            # Obtener la asignación
            assignment = await self._repository.get_assignment_by_id(assignment_id)
            if not assignment:
                raise ValidationError(
                    message=f"Asignación {assignment_id} no encontrada",
                    operation="validate_assignment_deletion",
                    entity_type="ProjectAssignment",
                    entity_id=assignment_id
                )
            
            validation_result = {
                "can_delete": True,
                "warnings": [],
                "impact_analysis": {
                    "project_impact": "low",
                    "employee_impact": "low",
                    "dependencies": []
                }
            }
            
            # Verificar si la asignación está activa
            if assignment.status == "active":
                validation_result["warnings"].append(
                    "La asignación está activa y su eliminación puede afectar el proyecto"
                )
                validation_result["impact_analysis"]["project_impact"] = "medium"
            
            # Verificar si es la única asignación del empleado al proyecto
            project_assignments = await self._repository.get_assignments_by_project(
                assignment.project_id
            )
            employee_assignments_in_project = [
                a for a in project_assignments 
                if a.employee_id == assignment.employee_id
            ]
            
            if len(employee_assignments_in_project) == 1:
                validation_result["warnings"].append(
                    "Esta es la única asignación del empleado en el proyecto"
                )
                validation_result["impact_analysis"]["employee_impact"] = "high"
            
            # Verificar porcentaje de asignación alto
            if assignment.percentage_allocation >= 50:
                validation_result["warnings"].append(
                    f"La asignación tiene un porcentaje alto ({assignment.percentage_allocation}%)"
                )
                validation_result["impact_analysis"]["project_impact"] = "high"
            
            self._logger.info(
                f"Validación de eliminación completada para asignación {assignment_id}: "
                f"puede eliminar = {validation_result['can_delete']}"
            )
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Error validando eliminación de asignación: {e}")
            raise ValidationError(
                message=f"Error validando eliminación: {e}",
                operation="validate_assignment_deletion",
                entity_type="ProjectAssignment",
                entity_id=assignment_id,
                original_error=e
            )

    async def validate_employee_availability(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """
        Valida la disponibilidad del empleado para nuevas asignaciones.
        
        Analiza la carga actual del empleado y determina su disponibilidad
        para aceptar nuevas asignaciones en el período especificado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict con información de disponibilidad y capacidad restante
            
        Raises:
            ValidationError: Si hay errores en la validación
            RepositoryError: Si hay errores de acceso a datos
        """
        try:
            self._logger.info(
                f"Validando disponibilidad de empleado {employee_id} "
                f"para período {start_date} - {end_date}"
            )
            
            # Obtener asignaciones existentes en el período
            existing_assignments = await self._repository.get_overlapping_assignments(
                employee_id=employee_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Calcular carga actual
            current_workload = sum(
                assignment.percentage_allocation 
                for assignment in existing_assignments
            )
            
            # Calcular disponibilidad
            available_capacity = max(0, self._business_rules["max_allocation_percentage"] - current_workload)
            
            availability_result = {
                "is_available": available_capacity > 0,
                "current_workload_percentage": current_workload,
                "available_capacity_percentage": available_capacity,
                "existing_assignments_count": len(existing_assignments),
                "can_accept_full_time": available_capacity >= 100,
                "can_accept_part_time": available_capacity > 0,
                "recommendations": []
            }
            
            # Generar recomendaciones
            if current_workload == 0:
                availability_result["recommendations"].append(
                    "Empleado completamente disponible para nuevas asignaciones"
                )
            elif current_workload < 50:
                availability_result["recommendations"].append(
                    "Empleado tiene buena disponibilidad para asignaciones adicionales"
                )
            elif current_workload < 80:
                availability_result["recommendations"].append(
                    "Empleado tiene disponibilidad limitada, considerar asignaciones de tiempo parcial"
                )
            elif current_workload < 100:
                availability_result["recommendations"].append(
                    "Empleado casi a capacidad máxima, solo asignaciones menores"
                )
            else:
                availability_result["recommendations"].append(
                    "Empleado a capacidad máxima, no puede aceptar nuevas asignaciones"
                )
            
            self._logger.info(
                f"Disponibilidad de empleado {employee_id}: "
                f"{available_capacity}% disponible ({current_workload}% ocupado)"
            )
            
            return availability_result
            
        except Exception as e:
            self._logger.error(f"Error validando disponibilidad de empleado: {e}")
            raise ValidationError(
                message=f"Error validando disponibilidad: {e}",
                operation="validate_employee_availability",
                entity_type="Employee",
                entity_id=employee_id,
                original_error=e
            )