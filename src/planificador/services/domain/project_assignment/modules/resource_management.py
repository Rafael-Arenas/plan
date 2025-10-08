# src/planificador/services/domain/project_assignment/modules/resource_management.py

"""
Módulo de Gestión de Recursos para Asignaciones de Proyecto

Implementa funcionalidades de gestión de recursos según la documentación oficial,
incluyendo asignación de empleados, reasignación y cálculo de utilización.
"""

from typing import List, Dict, Any, Optional
from datetime import date
from decimal import Decimal
from loguru import logger

from planificador.schemas import ProjectAssignment
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.exceptions import RepositoryError, ValidationError, BusinessLogicError
from ..interfaces import IResourceManagement


class ResourceManagement(IResourceManagement):
    """
    Implementación de gestión de recursos según documentación oficial.
    
    Proporciona los 3 métodos documentados para gestión de recursos:
    - assign_employee_to_project
    - reassign_employee
    - calculate_employee_utilization
    """
    
    def __init__(self, repository_facade: ProjectAssignmentRepositoryFacade):
        """
        Inicializa el módulo de gestión de recursos.
        
        Args:
            repository_facade: Facade del repositorio de asignaciones
        """
        self._repository = repository_facade
        self._logger = logger.bind(module="project_assignment_resource_management")

    async def assign_employee_to_project(
        self,
        employee_id: int,
        project_id: int,
        assignment_data: Dict[str, Any]
    ) -> ProjectAssignment:
        """
        Asigna un empleado a un proyecto específico.
        
        Args:
            employee_id: ID del empleado a asignar
            project_id: ID del proyecto de destino
            assignment_data: Datos de la asignación (rol, fechas, etc.)
            
        Returns:
            ProjectAssignment: La asignación creada
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Parámetros de entrada inválidos
            BusinessLogicError: Error en la lógica de asignación
        """
        try:
            self._logger.info(
                f"Asignando empleado {employee_id} al proyecto {project_id}"
            )
            
            # Validar parámetros de entrada
            if not employee_id or not project_id:
                raise ValidationError(
                    message="Employee ID y Project ID son requeridos",
                    field="employee_id, project_id",
                    operation="assign_employee_to_project"
                )
            
            # Validar datos de asignación requeridos
            required_fields = ['role', 'start_date', 'end_date']
            for field in required_fields:
                if field not in assignment_data:
                    raise ValidationError(
                        message=f"Campo requerido faltante: {field}",
                        field=field,
                        operation="assign_employee_to_project"
                    )
            
            # Verificar si ya existe una asignación activa
            existing_assignments = await self._repository.get_assignments_by_employee(employee_id)
            active_assignments = [
                a for a in existing_assignments 
                if a.project_id == project_id and a.is_active
            ]
            
            if active_assignments:
                raise BusinessLogicError(
                    message=f"El empleado {employee_id} ya tiene una asignación activa en el proyecto {project_id}",
                    operation="assign_employee_to_project",
                    entity_type="ProjectAssignment",
                    entity_id=f"{employee_id}-{project_id}"
                )
            
            # Verificar disponibilidad del empleado en las fechas
            overlapping_assignments = await self._check_employee_availability(
                employee_id, 
                assignment_data['start_date'], 
                assignment_data['end_date']
            )
            
            if overlapping_assignments:
                raise BusinessLogicError(
                    message=f"El empleado {employee_id} tiene conflictos de horario en las fechas especificadas",
                    operation="assign_employee_to_project",
                    entity_type="ProjectAssignment",
                    entity_id=employee_id
                )
            
            # Crear la asignación
            assignment_data.update({
                'employee_id': employee_id,
                'project_id': project_id,
                'is_active': True
            })
            
            new_assignment = await self._repository.create_assignment(assignment_data)
            
            self._logger.info(
                f"Asignación creada exitosamente: empleado {employee_id} -> proyecto {project_id}"
            )
            
            return new_assignment
            
        except (RepositoryError, ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al asignar empleado: {e}")
            raise BusinessLogicError(
                message=f"Error inesperado al asignar empleado: {e}",
                operation="assign_employee_to_project",
                entity_type="ProjectAssignment",
                entity_id=f"{employee_id}-{project_id}",
                original_error=e
            )

    async def reassign_employee(
        self,
        assignment_id: int,
        new_project_id: int,
        reassignment_data: Optional[Dict[str, Any]] = None
    ) -> ProjectAssignment:
        """
        Reasigna un empleado de un proyecto a otro.
        
        Args:
            assignment_id: ID de la asignación actual
            new_project_id: ID del nuevo proyecto
            reassignment_data: Datos opcionales para la reasignación
            
        Returns:
            ProjectAssignment: La asignación actualizada
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Parámetros de entrada inválidos
            BusinessLogicError: Error en la lógica de reasignación
        """
        try:
            self._logger.info(
                f"Reasignando empleado de asignación {assignment_id} al proyecto {new_project_id}"
            )
            
            # Obtener asignación actual
            current_assignment = await self._repository.get_assignment_by_id(assignment_id)
            if not current_assignment:
                raise ValidationError(
                    message=f"Asignación {assignment_id} no encontrada",
                    field="assignment_id",
                    operation="reassign_employee"
                )
            
            # Verificar que el proyecto destino sea diferente
            if current_assignment.project_id == new_project_id:
                raise ValidationError(
                    message="El proyecto destino debe ser diferente al actual",
                    field="new_project_id",
                    operation="reassign_employee"
                )
            
            # Verificar disponibilidad en el nuevo proyecto
            employee_id = current_assignment.employee_id
            start_date = reassignment_data.get('start_date') if reassignment_data else current_assignment.start_date
            end_date = reassignment_data.get('end_date') if reassignment_data else current_assignment.end_date
            
            overlapping_assignments = await self._check_employee_availability(
                employee_id, 
                start_date, 
                end_date,
                exclude_assignment_id=assignment_id
            )
            
            if overlapping_assignments:
                raise BusinessLogicError(
                    message=f"El empleado tiene conflictos de horario para la reasignación",
                    operation="reassign_employee",
                    entity_type="ProjectAssignment",
                    entity_id=assignment_id
                )
            
            # Preparar datos de actualización
            update_data = {'project_id': new_project_id}
            if reassignment_data:
                # Actualizar campos permitidos
                allowed_fields = ['role', 'start_date', 'end_date', 'allocation_percentage']
                for field in allowed_fields:
                    if field in reassignment_data:
                        update_data[field] = reassignment_data[field]
            
            # Actualizar la asignación
            updated_assignment = await self._repository.update_assignment(assignment_id, update_data)
            
            self._logger.info(
                f"Empleado reasignado exitosamente: asignación {assignment_id} -> proyecto {new_project_id}"
            )
            
            return updated_assignment
            
        except (RepositoryError, ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al reasignar empleado: {e}")
            raise BusinessLogicError(
                message=f"Error inesperado al reasignar empleado: {e}",
                operation="reassign_employee",
                entity_type="ProjectAssignment",
                entity_id=assignment_id,
                original_error=e
            )

    async def calculate_employee_utilization(
        self,
        employee_id: int,
        date_range: Optional[Dict[str, date]] = None
    ) -> Dict[str, Any]:
        """
        Calcula la utilización de un empleado en un rango de fechas.
        
        Args:
            employee_id: ID del empleado
            date_range: Rango de fechas opcional (start_date, end_date)
            
        Returns:
            Dict con métricas de utilización del empleado
            
        Raises:
            RepositoryError: Error al acceder a los datos
            ValidationError: Parámetros de entrada inválidos
        """
        try:
            self._logger.info(f"Calculando utilización del empleado {employee_id}")
            
            # Obtener asignaciones del empleado
            assignments = await self._repository.get_assignments_by_employee(employee_id)
            
            # Filtrar por rango de fechas si se proporciona
            if date_range:
                start_date = date_range.get('start_date')
                end_date = date_range.get('end_date')
                
                if start_date and end_date:
                    assignments = [
                        a for a in assignments
                        if self._assignment_overlaps_period(a, start_date, end_date)
                    ]
            
            # Calcular métricas de utilización
            utilization_metrics = self._calculate_utilization_metrics(assignments, date_range)
            
            self._logger.info(f"Utilización calculada para empleado {employee_id}")
            
            return {
                'employee_id': employee_id,
                'date_range': date_range,
                'total_assignments': len(assignments),
                'active_assignments': len([a for a in assignments if a.is_active]),
                'utilization_metrics': utilization_metrics,
                'calculated_at': date.today().isoformat()
            }
            
        except (RepositoryError, ValidationError):
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado al calcular utilización: {e}")
            raise RepositoryError(
                message=f"Error inesperado al calcular utilización: {e}",
                operation="calculate_employee_utilization",
                entity_type="ProjectAssignment",
                entity_id=employee_id,
                original_error=e
            )

    # Métodos privados de apoyo

    async def _check_employee_availability(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_assignment_id: Optional[int] = None
    ) -> List[ProjectAssignment]:
        """
        Verifica la disponibilidad de un empleado en un rango de fechas.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio
            end_date: Fecha de fin
            exclude_assignment_id: ID de asignación a excluir de la verificación
            
        Returns:
            Lista de asignaciones que se superponen con el período
        """
        assignments = await self._repository.get_assignments_by_employee(employee_id)
        
        overlapping = []
        for assignment in assignments:
            if exclude_assignment_id and assignment.id == exclude_assignment_id:
                continue
                
            if self._assignment_overlaps_period(assignment, start_date, end_date):
                overlapping.append(assignment)
        
        return overlapping

    def _assignment_overlaps_period(
        self,
        assignment: ProjectAssignment,
        start_date: date,
        end_date: date
    ) -> bool:
        """
        Verifica si una asignación se superpone con un período de fechas.
        
        Args:
            assignment: Asignación a verificar
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            True si hay superposición, False en caso contrario
        """
        return (
            assignment.start_date <= end_date and
            assignment.end_date >= start_date
        )

    def _calculate_utilization_metrics(
        self,
        assignments: List[ProjectAssignment],
        date_range: Optional[Dict[str, date]] = None
    ) -> Dict[str, Any]:
        """
        Calcula métricas detalladas de utilización.
        
        Args:
            assignments: Lista de asignaciones
            date_range: Rango de fechas opcional
            
        Returns:
            Dict con métricas de utilización
        """
        if not assignments:
            return {
                'total_allocation_percentage': Decimal('0.00'),
                'average_allocation_percentage': Decimal('0.00'),
                'utilization_status': 'available',
                'project_count': 0,
                'workload_distribution': {}
            }
        
        # Calcular porcentajes de asignación
        total_allocation = sum(
            Decimal(str(a.allocation_percentage or 0)) for a in assignments
        )
        
        average_allocation = total_allocation / len(assignments) if assignments else Decimal('0.00')
        
        # Determinar estado de utilización
        utilization_status = self._determine_utilization_status(total_allocation)
        
        # Distribución de carga por proyecto
        workload_distribution = {}
        for assignment in assignments:
            project_id = assignment.project_id
            allocation = Decimal(str(assignment.allocation_percentage or 0))
            
            if project_id not in workload_distribution:
                workload_distribution[project_id] = {
                    'allocation_percentage': allocation,
                    'role': assignment.role,
                    'is_active': assignment.is_active
                }
            else:
                workload_distribution[project_id]['allocation_percentage'] += allocation
        
        return {
            'total_allocation_percentage': float(total_allocation),
            'average_allocation_percentage': float(average_allocation),
            'utilization_status': utilization_status,
            'project_count': len(set(a.project_id for a in assignments)),
            'workload_distribution': workload_distribution
        }

    def _determine_utilization_status(self, total_allocation: Decimal) -> str:
        """
        Determina el estado de utilización basado en el porcentaje total.
        
        Args:
            total_allocation: Porcentaje total de asignación
            
        Returns:
            Estado de utilización
        """
        if total_allocation == 0:
            return 'available'
        elif total_allocation <= 50:
            return 'underutilized'
        elif total_allocation <= 80:
            return 'optimal'
        elif total_allocation <= 100:
            return 'fully_utilized'
        else:
            return 'overallocated'