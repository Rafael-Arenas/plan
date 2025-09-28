"""Módulo de operaciones de validación para asignaciones de proyectos.

Este módulo implementa la interfaz IValidationOperations y proporciona
funcionalidades para validar datos y reglas de negocio de las asignaciones.

Versión: 1.0.0
"""

from typing import Any
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from planificador.models.project_assignment import ProjectAssignment
from planificador.models.employee import Employee
from planificador.models.project import Project
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions import ValidationError
from ..interfaces.validation_interface import IValidationOperations


class ValidationOperations(BaseRepository[ProjectAssignment], IValidationOperations):
    """Implementación de operaciones de validación para asignaciones de proyectos.

    Hereda de BaseRepository y se especializa en validar datos y reglas
    de negocio para las asignaciones de proyectos.
    """

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones de validación.

        Args:
            session: Sesión asíncrona de SQLAlchemy.
        """
        super().__init__(session, ProjectAssignment)
        self._logger = self._logger.bind(component="ProjectAssignmentValidationOperations")
        self._logger.debug("ValidationOperations para ProjectAssignment inicializado")

    async def validate_assignment_data(self, assignment_data: dict[str, Any]) -> bool:
        """Valida los datos básicos de una asignación.
        
        Args:
            assignment_data: Datos de la asignación a validar
            
        Returns:
            True si los datos son válidos
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        self._logger.debug(f"Validando datos de asignación: {assignment_data}")
        
        # Validar campos requeridos
        await self.validate_required_fields(assignment_data)
        
        # Validar rangos de fechas
        if "start_date" in assignment_data and "end_date" in assignment_data:
            await self.validate_date_range(
                assignment_data["start_date"], 
                assignment_data["end_date"]
            )
        
        # Validar porcentaje de asignación
        if "allocation_percentage" in assignment_data:
            await self.validate_allocation_percentage(assignment_data["allocation_percentage"])
        
        # Validar horas por día
        if "hours_per_day" in assignment_data:
            await self.validate_hours_per_day(assignment_data["hours_per_day"])
        
        # Validar existencia de empleado y proyecto
        if "employee_id" in assignment_data:
            await self.validate_employee_exists(assignment_data["employee_id"])
        
        if "project_id" in assignment_data:
            await self.validate_project_exists(assignment_data["project_id"])
        
        return True

    async def get_by_unique_field(self, field_name: str, value: Any) -> ProjectAssignment | None:
        """Obtiene una asignación por un campo único.
        
        Args:
            field_name: Nombre del campo único
            value: Valor a buscar
            
        Returns:
            La asignación encontrada o None si no existe
        """
        try:
            self._logger.debug(f"Buscando asignación por {field_name}={value}")
            
            # Verificar que el campo existe en el modelo
            if not hasattr(self.model_class, field_name):
                self._logger.warning(f"Campo {field_name} no existe en {self.model_class.__name__}")
                return None
            
            field = getattr(self.model_class, field_name)
            stmt = select(self.model_class).where(field == value)
            result = await self.session.execute(stmt)
            assignment = result.scalar_one_or_none()
            
            if assignment:
                self._logger.debug(f"Asignación encontrada: ID {assignment.id}")
            else:
                self._logger.debug(f"No se encontró asignación con {field_name}={value}")
                
            return assignment
            
        except Exception as e:
            self._logger.error(f"Error buscando por {field_name}: {e}")
            raise

    async def validate_workload_limits(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date | None,
        percentage_allocation: float | None,
        exclude_id: int | None = None
    ) -> None:
        """Valida que la carga de trabajo no exceda los límites.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio
            end_date: Fecha de fin
            percentage_allocation: Porcentaje de dedicación
            exclude_id: ID de asignación a excluir
            
        Raises:
            ValidationError: Si la carga de trabajo excede los límites
        """
        self._logger.debug(f"Validando límites de carga de trabajo para empleado {employee_id}")
        
        if percentage_allocation is None:
            return
        
        try:
            # Obtener asignaciones existentes que se superponen
            stmt = select(ProjectAssignment).where(
                ProjectAssignment.employee_id == employee_id,
                ProjectAssignment.start_date <= (end_date or date.max),
                (ProjectAssignment.end_date.is_(None) | 
                 (ProjectAssignment.end_date >= start_date))
            )
            
            if exclude_id:
                stmt = stmt.where(ProjectAssignment.id != exclude_id)
            
            result = await self.session.execute(stmt)
            overlapping_assignments = result.scalars().all()
            
            # Calcular la carga total
            total_allocation = percentage_allocation
            for assignment in overlapping_assignments:
                if assignment.allocation_percentage:
                    total_allocation += assignment.allocation_percentage
            
            # Validar que no exceda el 100%
            if total_allocation > 100:
                raise ValidationError(
                    message=f"La carga de trabajo total ({total_allocation}%) excede el 100%",
                    field_errors={
                        "allocation_percentage": f"Carga actual: {total_allocation - percentage_allocation}%, "
                                               f"nueva asignación: {percentage_allocation}%"
                    }
                )
            
            self._logger.debug(f"Validación de carga de trabajo exitosa: {total_allocation}%")
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error validando límites de carga de trabajo: {e}")
            raise ValidationError(
                message=f"Error validando límites de carga de trabajo: {e}",
                original_error=e
            )

    async def validate_required_fields(self, assignment_data: dict[str, Any]) -> bool:
        """Valida que los campos requeridos estén presentes.
        
        Args:
            assignment_data: Datos de la asignación
            
        Returns:
            True si todos los campos requeridos están presentes
            
        Raises:
            ValidationError: Si faltan campos requeridos
        """
        required_fields = ["employee_id", "project_id", "start_date"]
        missing_fields = []
        
        for field in required_fields:
            if field not in assignment_data or assignment_data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(
                message=f"Campos requeridos faltantes: {', '.join(missing_fields)}",
                field_errors={"missing_fields": missing_fields}
            )
        
        return True

    async def validate_date_range(self, start_date: date, end_date: date) -> bool:
        """Valida que el rango de fechas sea válido.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            True si el rango es válido
            
        Raises:
            ValidationError: Si el rango de fechas no es válido
        """
        if start_date > end_date:
            raise ValidationError(
                message="La fecha de inicio no puede ser posterior a la fecha de fin",
                field_errors={
                    "start_date": "Debe ser anterior o igual a la fecha de fin",
                    "end_date": "Debe ser posterior o igual a la fecha de inicio"
                }
            )
        
        # Validar que las fechas no sean muy antiguas (más de 10 años)
        today = date.today()
        max_past_date = date(today.year - 10, today.month, today.day)
        
        if start_date < max_past_date:
            raise ValidationError(
                message="La fecha de inicio no puede ser anterior a 10 años",
                field_errors={"start_date": "Fecha demasiado antigua"}
            )
        
        return True

    async def validate_allocation_percentage(self, allocation_percentage: float) -> bool:
        """Valida que el porcentaje de asignación sea válido.
        
        Args:
            allocation_percentage: Porcentaje de asignación
            
        Returns:
            True si el porcentaje es válido
            
        Raises:
            ValidationError: Si el porcentaje no es válido
        """
        if allocation_percentage < 0 or allocation_percentage > 100:
            raise ValidationError(
                message="El porcentaje de asignación debe estar entre 0 y 100",
                field_errors={"allocation_percentage": "Debe estar entre 0 y 100"}
            )
        
        return True

    async def validate_hours_per_day(self, hours_per_day: float) -> bool:
        """Valida que las horas por día sean válidas.
        
        Args:
            hours_per_day: Horas por día
            
        Returns:
            True si las horas son válidas
            
        Raises:
            ValidationError: Si las horas no son válidas
        """
        if hours_per_day < 0 or hours_per_day > 24:
            raise ValidationError(
                message="Las horas por día deben estar entre 0 y 24",
                field_errors={"hours_per_day": "Debe estar entre 0 y 24"}
            )
        
        return True

    async def validate_employee_exists(self, employee_id: int) -> bool:
        """Valida que el empleado exista.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            True si el empleado existe
            
        Raises:
            ValidationError: Si el empleado no existe
        """
        query = select(Employee).where(Employee.id == employee_id)
        result = await self.session.execute(query)
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise ValidationError(
                message=f"El empleado con ID {employee_id} no existe",
                field_errors={"employee_id": "Empleado no encontrado"}
            )
        
        return True

    async def validate_project_exists(self, project_id: int) -> bool:
        """Valida que el proyecto exista.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            True si el proyecto existe
            
        Raises:
            ValidationError: Si el proyecto no existe
        """
        query = select(Project).where(Project.id == project_id)
        result = await self.session.execute(query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise ValidationError(
                message=f"El proyecto con ID {project_id} no existe",
                field_errors={"project_id": "Proyecto no encontrado"}
            )
        
        return True

    async def validate_no_overlapping_assignments(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date, 
        exclude_assignment_id: int | None = None
    ) -> bool:
        """Valida que no haya asignaciones superpuestas para un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio de la nueva asignación
            end_date: Fecha de fin de la nueva asignación
            exclude_assignment_id: ID de asignación a excluir (para actualizaciones)
            
        Returns:
            True si no hay superposiciones
            
        Raises:
            ValidationError: Si hay asignaciones superpuestas
        """
        criteria = {
            "employee_id": employee_id,
            "start_date": {"operator": "<=", "value": end_date},
            "end_date": {"operator": ">=", "value": start_date}
        }
        
        if exclude_assignment_id is not None:
            criteria["id"] = {"operator": "!=", "value": exclude_assignment_id}
        
        overlapping = await self.find_by_criteria(criteria)
        
        if overlapping:
            assignment_ids = [str(a.id) for a in overlapping]
            raise ValidationError(
                message=f"El empleado ya tiene asignaciones superpuestas en este período",
                field_errors={
                    "date_range": f"Conflicto con asignaciones: {', '.join(assignment_ids)}"
                }
            )
        
        return True

    async def validate_workload_limit(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date, 
        allocation_percentage: float,
        exclude_assignment_id: int | None = None
    ) -> bool:
        """Valida que la carga de trabajo no exceda el 100%.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio
            end_date: Fecha de fin
            allocation_percentage: Porcentaje de la nueva asignación
            exclude_assignment_id: ID de asignación a excluir
            
        Returns:
            True si la carga de trabajo es válida
            
        Raises:
            ValidationError: Si la carga de trabajo excede el límite
        """
        criteria = {
            "employee_id": employee_id,
            "start_date": {"operator": "<=", "value": end_date},
            "end_date": {"operator": ">=", "value": start_date},
            "is_active": True
        }
        
        if exclude_assignment_id is not None:
            criteria["id"] = {"operator": "!=", "value": exclude_assignment_id}
        
        existing_assignments = await self.find_by_criteria(criteria)
        
        total_allocation = sum(a.allocation_percentage or 0 for a in existing_assignments)
        total_allocation += allocation_percentage
        
        if total_allocation > 100:
            raise ValidationError(
                message=f"La carga de trabajo total ({total_allocation}%) excede el 100%",
                field_errors={
                    "allocation_percentage": f"Excede el límite. Disponible: {100 - (total_allocation - allocation_percentage)}%"
                }
            )
        
        return True

    async def validate_assignment_deletion(self, assignment_id: int) -> bool:
        """Valida que una asignación pueda ser eliminada.
        
        Args:
            assignment_id: ID de la asignación
            
        Returns:
            True si la asignación puede ser eliminada
            
        Raises:
            ValidationError: Si la asignación no puede ser eliminada
        """
        assignment = await self.get_by_id(assignment_id)
        
        if not assignment:
            raise ValidationError(
                message=f"La asignación con ID {assignment_id} no existe",
                field_errors={"assignment_id": "Asignación no encontrada"}
            )
        
        # Validar que la asignación no esté en curso
        today = date.today()
        if assignment.start_date <= today <= assignment.end_date:
            raise ValidationError(
                message="No se puede eliminar una asignación que está en curso",
                field_errors={"status": "Asignación actualmente en curso"}
            )
        
        return True

    async def validate_business_rules(self, assignment_data: dict[str, Any]) -> bool:
        """Valida reglas de negocio específicas.
        
        Args:
            assignment_data: Datos de la asignación
            
        Returns:
            True si cumple todas las reglas de negocio
            
        Raises:
            ValidationError: Si no cumple alguna regla de negocio
        """
        self._logger.debug("Validando reglas de negocio")
        
        # Regla: No se pueden crear asignaciones con más de 2 años de duración
        if "start_date" in assignment_data and "end_date" in assignment_data:
            duration = (assignment_data["end_date"] - assignment_data["start_date"]).days
            if duration > 730:  # 2 años
                raise ValidationError(
                    message="Las asignaciones no pueden durar más de 2 años",
                    field_errors={"duration": "Duración máxima: 2 años"}
                )
        
        # Regla: Las asignaciones de tiempo completo (100%) no pueden tener rol vacío
        if (assignment_data.get("allocation_percentage") == 100 and 
            not assignment_data.get("role")):
            raise ValidationError(
                message="Las asignaciones de tiempo completo deben tener un rol definido",
                field_errors={"role": "Requerido para asignaciones de 100%"}
            )
        
        return True