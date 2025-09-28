"""
Facade del repositorio de asignaciones de proyecto, compatible con la arquitectura modular.

Este facade actúa como un punto de entrada único para todas las operaciones
relacionadas con la entidad `ProjectAssignment`. Su propósito es abstraer la complejidad
interna de los diferentes módulos de repositorio y proporcionar una interfaz
coherente y simplificada.

Arquitectura y Principios:
- **Delegación de responsabilidades**: En lugar de contener la lógica de
  negocio, este facade delega las llamadas a los módulos especializados
  correspondientes (CRUD, consultas, validaciones, etc.).
- **Módulos especializados**: Los módulos se inicializan con un prefijo `_`
  (ej: `_crud_operations`) para indicar que son la implementación principal.
- **Manejo de errores centralizado**: Aunque los módulos internos manejan sus
  propias excepciones, el facade puede actuar como una capa adicional de
  control.
- **Interfaz pública estable**: Los métodos públicos del facade mantienen su
  firma para garantizar que los servicios que lo consumen no necesiten
  modificaciones.

Módulos Delegados:
- `_crud_operations`: Operaciones básicas de Crear, Leer, Actualizar, Eliminar.
- `_query_operations`: Consultas comunes y optimizadas.
- `_relationship_operations`: Gestión de relaciones con empleados y proyectos.
- `_statistics_operations`: Cálculos de métricas y estadísticas.
- `_validation_operations`: Validaciones de negocio y reglas de asignación.
"""

from datetime import date, datetime
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models import ProjectAssignment
from planificador.schemas.project_assignment import ProjectAssignmentCreate, ProjectAssignmentUpdate

# Módulos especializados
from .modules.crud_operations import CrudOperations
from .modules.query_operations import QueryOperations
from .modules.relationship_operations import RelationshipOperations
from .modules.statistics_operations import StatisticsOperations
from .modules.validation_operations import ValidationOperations


class ProjectAssignmentRepositoryFacade:
    """
    Facade que unifica el acceso a las operaciones del repositorio de asignaciones de proyecto.

    Este facade implementa una arquitectura modular, delegando la ejecución de
    operaciones a módulos especializados para mantener el código organizado
    y facilitar el mantenimiento.
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el facade y todos los módulos de operaciones.

        Args:
            session: La sesión de base de datos asíncrona.
        """
        self._session = session
        self._logger = logger

        # Inicialización de los módulos especializados
        self._crud_operations = CrudOperations(session)
        self._query_operations = QueryOperations(session)
        self._relationship_operations = RelationshipOperations(session)
        self._statistics_operations = StatisticsOperations(session)
        self._validation_operations = ValidationOperations(session)

    # ==================== OPERACIONES CRUD ====================

    async def create_assignment(self, assignment_data: ProjectAssignmentCreate) -> ProjectAssignment:
        """
        Crea una nueva asignación de proyecto.

        Args:
            assignment_data: Datos para crear la asignación.

        Returns:
            La asignación creada.

        Raises:
            ValidationError: Si los datos no son válidos.
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._crud_operations.create_assignment(assignment_data)

    async def update_assignment(
        self, assignment_id: int, assignment_data: ProjectAssignmentUpdate
    ) -> ProjectAssignment | None:
        """
        Actualiza una asignación existente.

        Args:
            assignment_id: ID de la asignación a actualizar.
            assignment_data: Datos de actualización.

        Returns:
            La asignación actualizada o None si no existe.

        Raises:
            ValidationError: Si los datos no son válidos.
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._crud_operations.update_assignment(assignment_id, assignment_data)

    async def delete_assignment(self, assignment_id: int) -> bool:
        """
        Elimina una asignación por su ID.

        Args:
            assignment_id: ID de la asignación a eliminar.

        Returns:
            True si se eliminó correctamente, False si no existe.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._crud_operations.delete_assignment(assignment_id)

    async def get_assignment_by_id(self, assignment_id: int) -> ProjectAssignment | None:
        """
        Obtiene una asignación por su ID.

        Args:
            assignment_id: ID de la asignación.

        Returns:
            La asignación encontrada o None si no existe.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._crud_operations.get_assignment_by_id(assignment_id)

    # ==================== OPERACIONES DE CONSULTA ====================

    async def get_all_assignments(
        self, limit: int | None = None, offset: int = 0
    ) -> list[ProjectAssignment]:
        """
        Obtiene todas las asignaciones con paginación opcional.

        Args:
            limit: Número máximo de resultados.
            offset: Número de resultados a omitir.

        Returns:
            Lista de asignaciones.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._query_operations.get_all_assignments(limit, offset)

    async def get_assignments_by_employee(self, employee_id: int) -> list[ProjectAssignment]:
        """
        Obtiene todas las asignaciones de un empleado específico.

        Args:
            employee_id: ID del empleado.

        Returns:
            Lista de asignaciones del empleado.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._query_operations.get_assignments_by_employee(employee_id)

    async def get_assignments_by_project(self, project_id: int) -> list[ProjectAssignment]:
        """
        Obtiene todas las asignaciones de un proyecto específico.

        Args:
            project_id: ID del proyecto.

        Returns:
            Lista de asignaciones del proyecto.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._query_operations.get_assignments_by_project(project_id)

    async def get_active_assignments(self) -> list[ProjectAssignment]:
        """
        Obtiene todas las asignaciones activas.

        Returns:
            Lista de asignaciones activas.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._query_operations.get_active_assignments()

    async def get_assignments_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[ProjectAssignment]:
        """
        Obtiene asignaciones que se superponen con un rango de fechas.

        Args:
            start_date: Fecha de inicio del rango.
            end_date: Fecha de fin del rango.

        Returns:
            Lista de asignaciones en el rango.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._query_operations.get_assignments_by_date_range(start_date, end_date)

    async def get_assignments_by_role(self, role: str) -> list[ProjectAssignment]:
        """
        Obtiene asignaciones por rol específico.

        Args:
            role: Rol a buscar.

        Returns:
            Lista de asignaciones con el rol especificado.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._query_operations.get_assignments_by_role(role)

    async def get_assignments_with_filters(
        self,
        employee_id: int | None = None,
        project_id: int | None = None,
        status: str | None = None,
        role: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        allocation_category: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[ProjectAssignment]:
        """
        Obtiene asignaciones aplicando múltiples filtros.

        Args:
            employee_id: ID del empleado (opcional).
            project_id: ID del proyecto (opcional).
            status: Estado de la asignación (opcional).
            role: Rol en la asignación (opcional).
            start_date: Fecha de inicio mínima (opcional).
            end_date: Fecha de fin máxima (opcional).
            allocation_category: Categoría de asignación (opcional).
            limit: Número máximo de resultados.
            offset: Número de resultados a omitir.

        Returns:
            Lista de asignaciones que cumplen los filtros.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._query_operations.get_assignments_with_filters(
            employee_id=employee_id,
            project_id=project_id,
            status=status,
            role=role,
            start_date=start_date,
            end_date=end_date,
            allocation_category=allocation_category,
            limit=limit,
            offset=offset,
        )

    async def get_overlapping_assignments(
        self, employee_id: int, start_date: date, end_date: date, exclude_id: int | None = None
    ) -> list[ProjectAssignment]:
        """
        Obtiene asignaciones que se superponen para un empleado en un período.

        Args:
            employee_id: ID del empleado.
            start_date: Fecha de inicio del período.
            end_date: Fecha de fin del período.
            exclude_id: ID de asignación a excluir (opcional).

        Returns:
            Lista de asignaciones superpuestas.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._query_operations.get_overlapping_assignments(
            employee_id, start_date, end_date, exclude_id
        )

    # ==================== OPERACIONES DE RELACIONES ====================

    async def get_assignments_with_employee_data(
        self, limit: int | None = None, offset: int = 0
    ) -> list[ProjectAssignment]:
        """
        Obtiene asignaciones con datos del empleado incluidos.

        Args:
            limit: Número máximo de resultados.
            offset: Número de resultados a omitir.

        Returns:
            Lista de asignaciones con datos del empleado.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._relationship_operations.get_assignments_with_employee_data(limit, offset)

    async def get_assignments_with_project_data(
        self, limit: int | None = None, offset: int = 0
    ) -> list[ProjectAssignment]:
        """
        Obtiene asignaciones con datos del proyecto incluidos.

        Args:
            limit: Número máximo de resultados.
            offset: Número de resultados a omitir.

        Returns:
            Lista de asignaciones con datos del proyecto.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._relationship_operations.get_assignments_with_project_data(limit, offset)

    async def get_assignments_with_full_data(
        self, limit: int | None = None, offset: int = 0
    ) -> list[ProjectAssignment]:
        """
        Obtiene asignaciones con datos completos de empleado y proyecto.

        Args:
            limit: Número máximo de resultados.
            offset: Número de resultados a omitir.

        Returns:
            Lista de asignaciones con datos completos.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._relationship_operations.get_assignments_with_full_data(limit, offset)

    async def transfer_employee_assignments(
        self, from_employee_id: int, to_employee_id: int, project_id: int | None = None
    ) -> bool:
        """
        Transfiere asignaciones de un empleado a otro.

        Args:
            from_employee_id: ID del empleado origen.
            to_employee_id: ID del empleado destino.
            project_id: ID del proyecto específico (opcional).

        Returns:
            True si se transfirieron correctamente.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._relationship_operations.transfer_employee_assignments(
            from_employee_id, to_employee_id, project_id
        )

    async def reassign_project_assignments(
        self, from_project_id: int, to_project_id: int, employee_id: int | None = None
    ) -> bool:
        """
        Reasigna asignaciones de un proyecto a otro.

        Args:
            from_project_id: ID del proyecto origen.
            to_project_id: ID del proyecto destino.
            employee_id: ID del empleado específico (opcional).

        Returns:
            True si se reasignaron correctamente.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._relationship_operations.reassign_project_assignments(
            from_project_id, to_project_id, employee_id
        )

    async def get_employee_workload_summary(self, employee_id: int) -> dict[str, Any]:
        """
        Obtiene un resumen de la carga de trabajo de un empleado.

        Args:
            employee_id: ID del empleado.

        Returns:
            Diccionario con el resumen de carga de trabajo.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._relationship_operations.get_employee_workload_summary(employee_id)

    async def get_project_team_summary(self, project_id: int) -> dict[str, Any]:
        """
        Obtiene un resumen del equipo de un proyecto.

        Args:
            project_id: ID del proyecto.

        Returns:
            Diccionario con el resumen del equipo.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._relationship_operations.get_project_team_summary(project_id)

    # ==================== OPERACIONES DE ESTADÍSTICAS ====================

    async def get_total_assignments_count(self) -> int:
        """
        Obtiene el número total de asignaciones.

        Returns:
            Número total de asignaciones.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_total_assignments_count()

    async def get_active_assignments_count(self) -> int:
        """
        Obtiene el número de asignaciones activas.

        Returns:
            Número de asignaciones activas.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_active_assignments_count()

    async def get_assignments_by_status_count(self) -> dict[str, int]:
        """
        Obtiene el conteo de asignaciones por estado.

        Returns:
            Diccionario con el conteo por estado.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_assignments_by_status_count()

    async def get_assignments_by_allocation_category_count(self) -> dict[str, int]:
        """
        Obtiene el conteo de asignaciones por categoría de asignación.

        Returns:
            Diccionario con el conteo por categoría.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_assignments_by_allocation_category_count()

    async def get_employee_assignment_stats(self, employee_id: int) -> dict[str, Any]:
        """
        Obtiene estadísticas de asignaciones para un empleado específico.

        Args:
            employee_id: ID del empleado.

        Returns:
            Diccionario con las estadísticas del empleado.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_employee_assignment_stats(employee_id)

    async def get_project_assignment_stats(self, project_id: int) -> dict[str, Any]:
        """
        Obtiene estadísticas de asignaciones para un proyecto específico.

        Args:
            project_id: ID del proyecto.

        Returns:
            Diccionario con las estadísticas del proyecto.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_project_assignment_stats(project_id)

    async def get_assignment_duration_stats(self) -> dict[str, Any]:
        """
        Obtiene estadísticas de duración de asignaciones.

        Returns:
            Diccionario con estadísticas de duración.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_assignment_duration_stats()

    async def get_workload_distribution_stats(self) -> dict[str, Any]:
        """
        Obtiene estadísticas de distribución de carga de trabajo.

        Returns:
            Diccionario con estadísticas de distribución.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_workload_distribution_stats()

    async def get_assignment_trends(self, days: int = 30) -> list[dict[str, Any]]:
        """
        Obtiene tendencias de asignaciones en un período.

        Args:
            days: Número de días para el análisis de tendencias.

        Returns:
            Lista con datos de tendencias.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_assignment_trends(days)

    async def get_overlap_statistics(self) -> dict[str, Any]:
        """
        Obtiene estadísticas de superposición de asignaciones.

        Returns:
            Diccionario con estadísticas de superposición.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_overlap_statistics()

    async def get_role_distribution_stats(self) -> dict[str, int]:
        """
        Obtiene estadísticas de distribución por roles.

        Returns:
            Diccionario con la distribución por roles.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_role_distribution_stats()

    async def get_comprehensive_dashboard_metrics(self) -> dict[str, Any]:
        """
        Obtiene métricas completas para el dashboard.

        Returns:
            Diccionario con métricas completas.

        Raises:
            RepositoryError: Si ocurre un error en la base de datos.
        """
        return await self._statistics_operations.get_comprehensive_dashboard_metrics()

    # ==================== OPERACIONES DE VALIDACIÓN ====================

    async def validate_assignment_data(
        self, assignment_data: dict[str, Any], exclude_id: int | None = None
    ) -> None:
        """
        Valida los datos básicos de una asignación.

        Args:
            assignment_data: Datos de la asignación a validar.
            exclude_id: ID de asignación a excluir de validaciones (opcional).

        Raises:
            ValidationError: Si los datos no son válidos.
        """
        await self._validation_operations.validate_assignment_data(assignment_data, exclude_id)

    def validate_required_fields(self, assignment_data: dict[str, Any]) -> None:
        """
        Valida que los campos requeridos estén presentes.

        Args:
            assignment_data: Datos de la asignación.

        Raises:
            ValidationError: Si faltan campos requeridos.
        """
        self._validation_operations.validate_required_fields(assignment_data)

    def validate_date_range(self, start_date: date, end_date: date) -> None:
        """
        Valida que el rango de fechas sea válido.

        Args:
            start_date: Fecha de inicio.
            end_date: Fecha de fin.

        Raises:
            ValidationError: Si el rango de fechas no es válido.
        """
        self._validation_operations.validate_date_range(start_date, end_date)

    def validate_allocation_percentage(self, allocation_percentage: float) -> None:
        """
        Valida que el porcentaje de asignación sea válido.

        Args:
            allocation_percentage: Porcentaje de asignación.

        Raises:
            ValidationError: Si el porcentaje no es válido.
        """
        self._validation_operations.validate_allocation_percentage(allocation_percentage)

    def validate_hours_per_day(self, hours_per_day: float) -> None:
        """
        Valida que las horas por día sean válidas.

        Args:
            hours_per_day: Horas por día.

        Raises:
            ValidationError: Si las horas no son válidas.
        """
        self._validation_operations.validate_hours_per_day(hours_per_day)

    async def validate_employee_exists(self, employee_id: int) -> None:
        """
        Valida que el empleado exista.

        Args:
            employee_id: ID del empleado.

        Raises:
            ValidationError: Si el empleado no existe.
        """
        await self._validation_operations.validate_employee_exists(employee_id)

    async def validate_project_exists(self, project_id: int) -> None:
        """
        Valida que el proyecto exista.

        Args:
            project_id: ID del proyecto.

        Raises:
            ValidationError: Si el proyecto no existe.
        """
        await self._validation_operations.validate_project_exists(project_id)

    async def validate_no_overlapping_assignments(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_id: int | None = None,
    ) -> None:
        """
        Valida que no haya asignaciones superpuestas.

        Args:
            employee_id: ID del empleado.
            start_date: Fecha de inicio.
            end_date: Fecha de fin.
            exclude_id: ID de asignación a excluir (opcional).

        Raises:
            ValidationError: Si hay asignaciones superpuestas.
        """
        await self._validation_operations.validate_no_overlapping_assignments(
            employee_id, start_date, end_date, exclude_id
        )

    async def validate_workload_limits(
        self, employee_id: int, start_date: date, end_date: date, allocation_percentage: float
    ) -> None:
        """
        Valida que no se excedan los límites de carga de trabajo.

        Args:
            employee_id: ID del empleado.
            start_date: Fecha de inicio.
            end_date: Fecha de fin.
            allocation_percentage: Porcentaje de asignación.

        Raises:
            ValidationError: Si se exceden los límites.
        """
        await self._validation_operations.validate_workload_limits(
            employee_id, start_date, end_date, allocation_percentage
        )

    async def validate_assignment_deletion(self, assignment_id: int) -> None:
        """
        Valida que una asignación pueda ser eliminada.

        Args:
            assignment_id: ID de la asignación.

        Raises:
            ValidationError: Si la asignación no puede ser eliminada.
        """
        await self._validation_operations.validate_assignment_deletion(assignment_id)

    async def validate_business_rules(
        self, assignment_data: dict[str, Any], exclude_id: int | None = None
    ) -> None:
        """
        Valida reglas de negocio específicas.

        Args:
            assignment_data: Datos de la asignación.
            exclude_id: ID de asignación a excluir (opcional).

        Raises:
            ValidationError: Si no se cumplen las reglas de negocio.
        """
        await self._validation_operations.validate_business_rules(assignment_data, exclude_id)