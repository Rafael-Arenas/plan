# src/planificador/repositories/vacation/vacation_repository_facade.py

"""
Fachada del Repositorio Vacation.

Este módulo implementa el patrón Facade para el repositorio de vacaciones,
proporcionando una interfaz unificada y simplificada para todas las
operaciones relacionadas con la gestión de vacaciones de empleados.

Arquitectura:
    - Implementa múltiples interfaces especializadas
    - Delega operaciones a módulos específicos
    - Maneja la sesión de base de datos de forma centralizada
    - Proporciona logging y manejo de errores consistente

Principios de Diseño:
    - Single Responsibility: Cada módulo tiene una responsabilidad específica
    - Dependency Injection: Los módulos se inyectan como dependencias
    - Interface Segregation: Interfaces pequeñas y específicas
    - Open/Closed: Extensible sin modificar código existente

Uso:
    ```python
    async with get_async_session() as session:
        facade = VacationRepositoryFacade(session)
        vacation = await facade.create_vacation(vacation_data)
        vacations = await facade.get_vacations_by_employee(employee_id)
        conflicts = await facade.check_vacation_conflicts(employee_id, start_date, end_date)
    ```
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from planificador.models.vacation import Vacation, VacationStatus, VacationType
from planificador.repositories.vacation.interfaces import (
    IVacationCrudOperations,
    IVacationQueryOperations,
    IVacationValidationOperations,
    IVacationRelationshipOperations,
    IVacationStatisticsOperations
)
from planificador.repositories.vacation.modules import (
    VacationCrudModule,
    VacationQueryModule,
    VacationValidationModule,
    VacationRelationshipModule,
    VacationStatisticsModule
)
from planificador.exceptions.repository import VacationRepositoryError


class VacationRepositoryFacade(
    IVacationCrudOperations,
    IVacationQueryOperations,
    IVacationValidationOperations,
    IVacationRelationshipOperations,
    IVacationStatisticsOperations
):
    """
    Fachada del repositorio Vacation que unifica todas las operaciones.
    
    Implementa las interfaces de CRUD, consultas, validación, relaciones y estadísticas,
    delegando las operaciones a los módulos especializados correspondientes.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        crud_module: Módulo para operaciones CRUD
        query_module: Módulo para operaciones de consulta
        validation_module: Módulo para operaciones de validación
        relationship_module: Módulo para operaciones de relaciones
        statistics_module: Módulo para operaciones de estadísticas
    """

    def __init__(self, session: AsyncSession):
        """Inicializa la fachada con sesión de BD y módulos especializados."""
        self.session = session
        self._logger = logger.bind(module="vacation_repository_facade")
        
        # Inicializar módulos especializados
        self._crud_operations = VacationCrudModule(session)
        self._query_operations = VacationQueryModule(session)
        self._validation_operations = VacationValidationModule(session)
        self._relationship_operations = VacationRelationshipModule(session)
        self._statistics_operations = VacationStatisticsModule(session)
        
        self._logger.debug("VacationRepositoryFacade inicializada")

    # =============================================================================
    # OPERACIONES CRUD
    # =============================================================================

    async def create_vacation(self, vacation_data: Dict[str, Any]) -> Vacation:
        """Crea una nueva vacación."""
        return await self._crud_operations.create_vacation(vacation_data)

    async def update_vacation(
        self,
        vacation_id: int,
        vacation_data: Dict[str, Any]
    ) -> Vacation:
        """Actualiza una vacación existente."""
        return await self._crud_operations.update_vacation(vacation_id, vacation_data)

    async def delete_vacation(self, vacation_id: int) -> bool:
        """Elimina una vacación."""
        return await self._crud_operations.delete_vacation(vacation_id)

    async def get_vacation_by_id(self, vacation_id: int) -> Optional[Vacation]:
        """Obtiene una vacación por su ID."""
        return await self._crud_operations.get_vacation_by_id(vacation_id)

    async def get_by_unique_field(
        self,
        field_name: str,
        field_value: Any
    ) -> Optional[Vacation]:
        """Obtiene una vacación por un campo único."""
        return await self._crud_operations.get_by_unique_field(field_name, field_value)

    # =============================================================================
    # OPERACIONES DE CONSULTA
    # =============================================================================

    async def get_vacations_by_employee(
        self,
        employee_id: int,
        active_only: bool = True
    ) -> List[Vacation]:
        """Obtiene vacaciones por empleado."""
        return await self._query_operations.get_vacations_by_employee(employee_id, active_only)

    async def get_vacations_by_date_range(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> List[Vacation]:
        """Obtiene vacaciones por rango de fechas."""
        return await self._query_operations.get_vacations_by_date_range(
            start_date, end_date, employee_id
        )

    async def get_vacations_by_status(
        self,
        status: str,
        employee_id: Optional[int] = None
    ) -> List[Vacation]:
        """Obtiene vacaciones por estado."""
        return await self._query_operations.get_vacations_by_status(status, employee_id)

    async def get_vacations_by_type(
        self,
        vacation_type: str,
        employee_id: Optional[int] = None
    ) -> List[Vacation]:
        """Obtiene vacaciones por tipo."""
        return await self._query_operations.get_vacations_by_type(vacation_type, employee_id)

    async def search_vacations_by_criteria(
        self,
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Vacation]:
        """Busca vacaciones por criterios específicos."""
        return await self._query_operations.search_vacations_by_criteria(criteria, limit, offset)

    async def get_vacations_with_pagination(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Vacation], int]:
        """Obtiene vacaciones con paginación."""
        return await self._query_operations.get_vacations_with_pagination(page, page_size, filters)

    async def count_vacations(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Cuenta vacaciones con filtros opcionales."""
        return await self._query_operations.count_vacations(filters)

    # =============================================================================
    # OPERACIONES DE VALIDACIÓN
    # =============================================================================

    async def validate_vacation_data(self, vacation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida datos de vacación."""
        return await self._validation_operations.validate_vacation_data(vacation_data)

    async def validate_vacation_request(
        self,
        employee_id: int,
        vacation_type: str,
        start_date: date,
        end_date: date,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Valida una solicitud de vacación."""
        return await self._validation_operations.validate_vacation_request(
            employee_id, start_date, end_date, vacation_type
        )

    async def validate_vacation_id(self, vacation_id: int) -> Dict[str, Any]:
        """Valida que un ID de vacación existe."""
        return await self._validation_operations.validate_vacation_id(vacation_id)

    async def check_vacation_conflicts(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_vacation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Verifica conflictos de vacaciones."""
        return await self._validation_operations.check_vacation_conflicts(
            employee_id, start_date, end_date, exclude_vacation_id
        )

    async def validate_business_rules(
        self,
        operation: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida reglas de negocio."""
        return await self._validation_operations.validate_business_rules(operation, data)

    async def validate_data_consistency(self) -> Dict[str, Any]:
        """Valida consistencia de datos."""
        return await self._validation_operations.validate_data_consistency()

    # =============================================================================
    # OPERACIONES DE RELACIONES
    # =============================================================================

    async def get_vacation_with_employee_details(
        self,
        vacation_id: int
    ) -> Optional[Dict[str, Any]]:
        """Obtiene vacación con detalles del empleado."""
        return await self._relationship_operations.get_vacation_with_employee_details(vacation_id)

    async def validate_employee_exists(self, employee_id: int) -> bool:
        """Valida que un empleado existe."""
        return await self._relationship_operations.validate_employee_exists(employee_id)

    async def get_overlapping_vacations(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_vacation_id: Optional[int] = None
    ) -> List[Vacation]:
        """Obtiene vacaciones que se solapan."""
        return await self._relationship_operations.get_overlapping_vacations(
            employee_id, start_date, end_date, exclude_vacation_id
        )

    async def get_vacations_with_relationships(
        self,
        vacation_ids: Optional[List[int]] = None,
        include_employee: bool = True
    ) -> List[Dict[str, Any]]:
        """Obtiene vacaciones con relaciones cargadas."""
        return await self._relationship_operations.get_vacations_with_relationships(
            vacation_ids, include_employee
        )

    async def get_employee_vacation_summary(
        self,
        employee_id: int,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obtiene resumen de vacaciones del empleado."""
        return await self._relationship_operations.get_employee_vacation_summary(employee_id, year)

    # =============================================================================
    # OPERACIONES DE ESTADÍSTICAS
    # =============================================================================

    async def get_employee_vacation_statistics(
        self,
        employee_id: int,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de vacaciones del empleado."""
        return await self._statistics_operations.get_employee_vacation_statistics(employee_id, year)

    async def get_team_vacation_balance(
        self,
        team_id: int,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obtiene balance de vacaciones del equipo."""
        return await self._statistics_operations.get_team_vacation_balance(team_id, year)

    async def get_vacation_trends(
        self,
        start_date: date,
        end_date: date,
        granularity: str = "monthly"
    ) -> List[Dict[str, Any]]:
        """Obtiene tendencias de vacaciones."""
        return await self._statistics_operations.get_vacation_trends(start_date, end_date, granularity)

    async def get_vacation_patterns_analysis(
        self,
        employee_id: Optional[int] = None,
        team_id: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obtiene análisis de patrones de vacaciones."""
        return await self._statistics_operations.get_vacation_patterns_analysis(
            employee_id, team_id, year
        )

    async def generate_vacation_summary_report(
        self,
        year: Optional[int] = None,
        include_projections: bool = False
    ) -> Dict[str, Any]:
        """Genera reporte resumen de vacaciones."""
        return await self._statistics_operations.generate_vacation_summary_report(
            year, include_projections
        )

    # =============================================================================
    # MÉTODOS COMPUESTOS DE ALTO NIVEL
    # =============================================================================

    async def create_vacation_with_validation(
        self,
        vacation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea una vacación con validación completa.
        
        Realiza todas las validaciones necesarias antes de crear la vacación,
        incluyendo validación de datos, reglas de negocio y conflictos.
        
        Args:
            vacation_data: Datos de la vacación a crear
            
        Returns:
            Dict con resultado de la operación y datos de la vacación creada
        """
        try:
            self._logger.info(f"Iniciando creación de vacación con validación completa")
            
            # Validar datos básicos
            validation_result = await self.validate_vacation_data(vacation_data)
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': 'Datos de vacación inválidos',
                    'validation_errors': validation_result['errors'],
                    'vacation': None
                }
            
            # Validar reglas de negocio
            business_validation = await self.validate_business_rules('create', vacation_data)
            if not business_validation['is_valid']:
                return {
                    'success': False,
                    'error': 'Violación de reglas de negocio',
                    'validation_errors': business_validation['errors'],
                    'vacation': None
                }
            
            # Verificar conflictos
            conflicts = await self.check_vacation_conflicts(
                vacation_data['employee_id'],
                vacation_data['start_date'],
                vacation_data['end_date']
            )
            
            if conflicts['has_conflicts']:
                return {
                    'success': False,
                    'error': 'Conflictos detectados con vacaciones existentes',
                    'conflicts': conflicts['conflicts'],
                    'vacation': None
                }
            
            # Crear la vacación
            vacation = await self.create_vacation(vacation_data)
            
            self._logger.info(f"Vacación creada exitosamente: {vacation.id}")
            
            return {
                'success': True,
                'message': 'Vacación creada exitosamente',
                'vacation': vacation,
                'validation_result': validation_result
            }
            
        except Exception as e:
            self._logger.error(f"Error en creación de vacación con validación: {e}")
            raise VacationRepositoryError(
                message=f"Error en creación de vacación con validación: {e}",
                operation="create_vacation_with_validation",
                entity_type="Vacation",
                original_error=e
            )

    async def get_vacation_dashboard_data(
        self,
        employee_id: Optional[int] = None,
        team_id: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene datos completos para dashboard de vacaciones.
        
        Recopila estadísticas, tendencias y resúmenes para mostrar
        en un dashboard de vacaciones.
        
        Args:
            employee_id: ID del empleado (opcional)
            team_id: ID del equipo (opcional)
            year: Año para el análisis (opcional)
            
        Returns:
            Dict con datos completos del dashboard
        """
        try:
            self._logger.info(f"Obteniendo datos de dashboard - Employee: {employee_id}, Team: {team_id}, Year: {year}")
            
            dashboard_data = {
                'summary': {},
                'statistics': {},
                'trends': [],
                'patterns': {},
                'recent_vacations': []
            }
            
            # Estadísticas generales
            if employee_id:
                dashboard_data['statistics'] = await self.get_employee_vacation_statistics(
                    employee_id, year
                )
                dashboard_data['summary'] = await self.get_employee_vacation_summary(
                    employee_id, year
                )
            elif team_id:
                dashboard_data['statistics'] = await self.get_team_vacation_balance(
                    team_id, year
                )
            
            # Análisis de patrones
            dashboard_data['patterns'] = await self.get_vacation_patterns_analysis(
                employee_id, team_id, year
            )
            
            # Vacaciones recientes
            if employee_id:
                recent_vacations = await self.get_vacations_by_employee(employee_id)
                dashboard_data['recent_vacations'] = recent_vacations[:10]  # Últimas 10
            
            # Tendencias (últimos 12 meses)
            from pendulum import now
            end_date = now().date()
            start_date = end_date.subtract(months=12)
            
            dashboard_data['trends'] = await self.get_vacation_trends(
                start_date, end_date, "monthly"
            )
            
            self._logger.info("Datos de dashboard obtenidos exitosamente")
            
            return dashboard_data
            
        except Exception as e:
            self._logger.error(f"Error obteniendo datos de dashboard: {e}")
            raise VacationRepositoryError(
                message=f"Error obteniendo datos de dashboard: {e}",
                operation="get_vacation_dashboard_data",
                entity_type="Vacation",
                original_error=e
            )

    async def bulk_vacation_operation(
        self,
        operation: str,
        vacation_data_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Realiza operaciones en lote sobre vacaciones.
        
        Permite crear, actualizar o eliminar múltiples vacaciones
        en una sola operación transaccional.
        
        Args:
            operation: Tipo de operación ('create', 'update', 'delete')
            vacation_data_list: Lista de datos de vacaciones
            
        Returns:
            Lista con resultados de cada operación
        """
        try:
            self._logger.info(f"Iniciando operación en lote: {operation} - {len(vacation_data_list)} elementos")
            
            results = []
            
            for i, vacation_data in enumerate(vacation_data_list):
                try:
                    if operation == 'create':
                        result = await self.create_vacation_with_validation(vacation_data)
                        results.append({
                            'index': i,
                            'success': result['success'],
                            'vacation_id': result['vacation'].id if result['success'] else None,
                            'error': result.get('error'),
                            'data': vacation_data
                        })
                    
                    elif operation == 'update':
                        vacation_id = vacation_data.get('id')
                        if not vacation_id:
                            results.append({
                                'index': i,
                                'success': False,
                                'vacation_id': None,
                                'error': 'ID de vacación requerido para actualización',
                                'data': vacation_data
                            })
                            continue
                        
                        vacation = await self.update_vacation(vacation_id, vacation_data)
                        results.append({
                            'index': i,
                            'success': True,
                            'vacation_id': vacation.id,
                            'error': None,
                            'data': vacation_data
                        })
                    
                    elif operation == 'delete':
                        vacation_id = vacation_data.get('id')
                        if not vacation_id:
                            results.append({
                                'index': i,
                                'success': False,
                                'vacation_id': None,
                                'error': 'ID de vacación requerido para eliminación',
                                'data': vacation_data
                            })
                            continue
                        
                        success = await self.delete_vacation(vacation_id)
                        results.append({
                            'index': i,
                            'success': success,
                            'vacation_id': vacation_id,
                            'error': None if success else 'Error eliminando vacación',
                            'data': vacation_data
                        })
                    
                    else:
                        results.append({
                            'index': i,
                            'success': False,
                            'vacation_id': None,
                            'error': f'Operación no soportada: {operation}',
                            'data': vacation_data
                        })
                
                except Exception as e:
                    self._logger.error(f"Error en elemento {i} de operación en lote: {e}")
                    results.append({
                        'index': i,
                        'success': False,
                        'vacation_id': None,
                        'error': str(e),
                        'data': vacation_data
                    })
            
            successful_operations = sum(1 for r in results if r['success'])
            self._logger.info(f"Operación en lote completada: {successful_operations}/{len(vacation_data_list)} exitosas")
            
            return results
            
        except Exception as e:
            self._logger.error(f"Error en operación en lote: {e}")
            raise VacationRepositoryError(
                message=f"Error en operación en lote: {e}",
                operation="bulk_vacation_operation",
                entity_type="Vacation",
                original_error=e
            )

    # ========================================
    # Métodos Faltantes de las Interfaces
    # ========================================

    async def check_vacation_overlap(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_vacation_id: Optional[int] = None
    ) -> bool:
        """
        Verifica solapamiento de vacaciones.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio de la vacación
            end_date: Fecha de fin de la vacación
            exclude_vacation_id: ID de vacación a excluir (opcional)
        
        Returns:
            bool: True si hay solapamiento, False en caso contrario
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la verificación
        """
        overlapping_vacations = await self._relationship_operations.get_overlapping_vacations(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            exclude_vacation_id=exclude_vacation_id
        )
        return len(overlapping_vacations) > 0

    async def get_by_date_range(self, start_date: date, end_date: date) -> List[Vacation]:
        """
        Obtiene vacaciones en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
        
        Returns:
            List[Vacation]: Lista de vacaciones en el rango especificado
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        return await self._query_operations.get_by_date_range(
            start_date=start_date,
            end_date=end_date
        )

    async def validate_create_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos para crear una nueva vacación.
        
        Args:
            data: Diccionario con los datos de la vacación
        
        Raises:
            VacationRepositoryError: Si los datos no son válidos
        """
        validation_result = await self._validation_operations.validate_vacation_data(data)
        if not validation_result['is_valid']:
            raise VacationRepositoryError(
                message=f"Datos de vacación inválidos: {validation_result['errors']}",
                operation="validate_create_data",
                entity_type="Vacation"
            )

    # ========================================
    # Métodos Faltantes de Query Interface
    # ========================================

    async def get_by_employee_id(self, employee_id: int) -> List[Vacation]:
        """Obtiene vacaciones por ID de empleado."""
        return await self._query_operations.get_by_employee_id(employee_id)

    async def get_by_status(self, status: VacationStatus) -> List[Vacation]:
        """Obtiene vacaciones por estado."""
        return await self._query_operations.get_by_status(status)

    async def get_by_type(self, vacation_type: VacationType) -> List[Vacation]:
        """Obtiene vacaciones por tipo."""
        return await self._query_operations.get_by_type(vacation_type)

    async def get_by_employee_and_date_range(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[Vacation]:
        """Obtiene vacaciones por empleado y rango de fechas."""
        return await self._query_operations.get_by_employee_and_date_range(
            employee_id, start_date, end_date
        )

    async def search_vacations(
        self,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[VacationStatus] = None,
        vacation_type: Optional[VacationType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Vacation]:
        """Busca vacaciones con múltiples filtros."""
        return await self._query_operations.search_vacations(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            status=status,
            vacation_type=vacation_type,
            limit=limit,
            offset=offset
        )

    async def get_employee_vacations(
        self, 
        employee_id: int, 
        year: Optional[int] = None
    ) -> List[Vacation]:
        """Obtiene vacaciones de un empleado por año."""
        return await self._query_operations.get_employee_vacations(employee_id, year)

    async def get_pending_approvals(self, limit: int = 50) -> List[Vacation]:
        """Obtiene vacaciones pendientes de aprobación."""
        return await self._query_operations.get_pending_approvals(limit)

    async def get_current_month_vacations(self) -> List[Vacation]:
        """Obtiene vacaciones del mes actual."""
        return await self._query_operations.get_current_month_vacations()

    async def get_upcoming_vacations(self, days_ahead: int = 30) -> List[Vacation]:
        """Obtiene vacaciones próximas."""
        return await self._query_operations.get_upcoming_vacations(days_ahead)

    async def get_with_relations(self, vacation_id: int) -> Optional[Vacation]:
        """Obtiene vacación con todas las relaciones cargadas."""
        return await self._query_operations.get_with_relations(vacation_id)

    # ========================================
    # Métodos Faltantes de Validation Interface
    # ========================================

    async def validate_update_data(self, vacation_id: int, data: Dict[str, Any]) -> None:
        """Valida los datos para actualizar una vacación."""
        await self._validation_operations.validate_update_data(data)

    # ========================================
    # Métodos Faltantes de Relationship Interface
    # ========================================

    async def get_vacation_with_employee(self, vacation_id: int) -> Optional[Vacation]:
        """Obtiene vacación con información del empleado."""
        return await self._relationship_operations.get_vacation_with_employee(vacation_id)

    async def get_vacation_with_all_relations(self, vacation_id: int) -> Optional[Vacation]:
        """Obtiene vacación con todas las relaciones cargadas."""
        return await self._relationship_operations.get_vacation_with_all_relations(vacation_id)

    async def validate_vacation_exists(self, vacation_id: int) -> Vacation:
        """Valida la existencia de una vacación por ID."""
        return await self._relationship_operations.validate_vacation_exists(vacation_id)

    async def get_vacation_conflicts(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_vacation_id: Optional[int] = None
    ) -> List[Vacation]:
        """Obtiene conflictos de vacaciones."""
        return await self._relationship_operations.get_vacation_conflicts(
            employee_id, start_date, end_date, exclude_vacation_id
        )

    async def get_employee_vacations_with_details(self, employee_id: int) -> List[Vacation]:
        """Obtiene vacaciones de empleado con detalles completos."""
        return await self._relationship_operations.get_employee_vacations_with_details(employee_id)

    # ========================================
    # Métodos Faltantes de Statistics Interface
    # ========================================

    async def get_vacation_summary_by_employee(self, employee_id: int, year: int) -> Dict[str, Any]:
        """Obtiene resumen de vacaciones por empleado."""
        return await self._statistics_operations.get_vacation_summary_by_employee(employee_id, year)

    async def get_team_vacation_summary(self, team_id: int, year: int) -> Dict[str, Any]:
        """Obtiene resumen de vacaciones por equipo."""
        return await self._statistics_operations.get_team_vacation_summary(team_id, year)

    async def get_vacation_balance_analysis(self, employee_id: int, year: int) -> Dict[str, Any]:
        """Obtiene análisis de balance de vacaciones."""
        return await self._statistics_operations.get_vacation_balance_analysis(employee_id, year)

    async def get_vacation_trends_by_employee(
        self, 
        employee_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Obtiene tendencias de vacaciones por empleado."""
        return await self._statistics_operations.get_vacation_trends_by_employee(
            employee_id, start_date, end_date
        )

    async def get_team_vacation_statistics(self, team_id: int, year: int) -> Dict[str, Any]:
        """Obtiene estadísticas de vacaciones por equipo."""
        return await self._statistics_operations.get_team_vacation_statistics(team_id, year)

    async def get_team_vacations_summary(
        self, 
        team_id: int, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Obtiene resumen de vacaciones del equipo."""
        return await self._statistics_operations.get_team_vacations_summary(
            team_id, start_date, end_date
        )

    # =============================================================================
    # OPERACIONES ESPECIALES
    # =============================================================================

    async def approve_vacation(
        self, 
        vacation_id: int, 
        approved_by: str, 
        notes: Optional[str] = None
    ) -> Optional[Vacation]:
        """
        Aprueba una vacación específica.
        
        Args:
            vacation_id: ID de la vacación a aprobar
            approved_by: Usuario que aprueba la vacación
            notes: Notas opcionales sobre la aprobación
            
        Returns:
            Vacación aprobada o None si no se encuentra
        """
        from pendulum import now
        
        # Obtener la vacación actual
        vacation = await self._crud_operations.get_vacation_by_id(vacation_id)
        if not vacation:
            return None
            
        # Actualizar el estado y datos de aprobación
        update_data = {
            "status": VacationStatus.APPROVED,
            "approved_by": approved_by,
            "approved_at": now(),
            "notes": notes
        }
        
        return await self._crud_operations.update_vacation(vacation_id, update_data)

    async def reject_vacation(
        self, 
        vacation_id: int, 
        rejected_by: str, 
        reason: Optional[str] = None
    ) -> Optional[Vacation]:
        """
        Rechaza una vacación específica.
        
        Args:
            vacation_id: ID de la vacación a rechazar
            rejected_by: Usuario que rechaza la vacación
            reason: Razón del rechazo
            
        Returns:
            Vacación rechazada o None si no se encuentra
        """
        from pendulum import now
        
        # Obtener la vacación actual
        vacation = await self._crud_operations.get_vacation_by_id(vacation_id)
        if not vacation:
            return None
            
        # Actualizar el estado y datos de rechazo
        update_data = {
            "status": VacationStatus.REJECTED,
            "rejected_by": rejected_by,
            "rejected_at": now(),
            "rejection_reason": reason
        }
        
        return await self._crud_operations.update_vacation(vacation_id, update_data)

    async def cancel_vacation(
        self, 
        vacation_id: int, 
        cancelled_by: Optional[int] = None, 
        reason: Optional[str] = None
    ) -> Optional[Vacation]:
        """
        Cancela una vacación específica.
        
        Args:
            vacation_id: ID de la vacación a cancelar
            cancelled_by: ID del usuario que cancela la vacación
            reason: Razón de la cancelación
            
        Returns:
            Vacación cancelada o None si no se encuentra
        """
        from pendulum import now
        
        # Obtener la vacación actual
        vacation = await self._crud_operations.get_vacation_by_id(vacation_id)
        if not vacation:
            return None
            
        # Actualizar el estado y datos de cancelación
        update_data = {
            "status": VacationStatus.CANCELLED,
            "cancelled_by": cancelled_by,
            "cancelled_at": now(),
            "cancellation_reason": reason
        }
        
        return await self._crud_operations.update_vacation(vacation_id, update_data)