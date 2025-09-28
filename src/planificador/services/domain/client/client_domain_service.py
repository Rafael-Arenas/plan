# src/planificador/services/domain/client_domain_service.py

"""
Servicio de dominio para la gestión integral de clientes.

Este módulo implementa la lógica de negocio compleja para el dominio de clientes,
incluyendo operaciones CRUD avanzadas, coordinación entre dominios, análisis de negocio,
validaciones complejas y gestión del ciclo de vida de clientes.
"""

from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, date
from contextlib import asynccontextmanager

import pendulum
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .base_domain_service import BaseDomainService
from .client_domain_service_interface import IClientDomainService
from ...repositories.client.client_repository_facade import ClientRepositoryFacade
from ...schemas.client import (
    ClientCreateSchema, 
    ClientUpdateSchema, 
    ClientResponseSchema,
    ClientSearchSchema,
    ClientStatisticsSchema
)
from ...exceptions.domain.client_domain_exceptions import (
    ClientDomainError,
    ClientBusinessRuleViolationError,
    ClientDependencyError,
    ClientProjectTransferError,
    ClientDomainCoordinationError,
    ClientDataSynchronizationError,
    ClientAnalysisError,
    ClientReportGenerationError,
    create_client_business_rule_violation,
    create_client_dependency_error,
    create_client_project_transfer_error,
    create_client_analysis_error
)
from ...exceptions.repository.client_repository_exceptions import (
    ClientNotFoundError,
    ClientValidationError,
    ClientDuplicateError
)
from ...config.config import settings


class ClientDomainService(BaseDomainService[ClientCreateSchema, ClientUpdateSchema, ClientResponseSchema], IClientDomainService):
    """
    Servicio de dominio para la gestión integral de clientes.
    
    Implementa lógica de negocio compleja, coordinación entre dominios,
    análisis avanzado y gestión del ciclo de vida completo de clientes.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio de dominio de clientes.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session)
        self._client_repository = ClientRepositoryFacade(session)
        self._logger = logger.bind(service="ClientDomainService")
        
        # Configuración de reglas de negocio
        self._business_rules = {
            'min_name_length': 2,
            'max_name_length': 100,
            'required_fields': ['name', 'email'],
            'email_domains_allowed': settings.ALLOWED_EMAIL_DOMAINS if hasattr(settings, 'ALLOWED_EMAIL_DOMAINS') else None,
            'max_projects_per_client': settings.MAX_PROJECTS_PER_CLIENT if hasattr(settings, 'MAX_PROJECTS_PER_CLIENT') else 50,
            'client_status_transitions': {
                'active': ['inactive', 'suspended'],
                'inactive': ['active'],
                'suspended': ['active', 'inactive']
            }
        }

    # ============================================================================
    # OPERACIONES CRUD CON VALIDACIÓN Y DEPENDENCIAS
    # ============================================================================

    async def create_client_with_validation(
        self,
        client_data: ClientCreateSchema,
        validate_dependencies: bool = True,
        notify_stakeholders: bool = True
    ) -> ClientResponseSchema:
        """
        Crea un nuevo cliente con validaciones de negocio completas.
        
        Args:
            client_data: Datos del cliente a crear
            validate_dependencies: Si validar dependencias externas
            notify_stakeholders: Si notificar a stakeholders
            
        Returns:
            Cliente creado con información completa
            
        Raises:
            ClientBusinessRuleViolationError: Si viola reglas de negocio
            ClientValidationError: Si los datos no son válidos
            ClientDuplicateError: Si ya existe un cliente similar
        """
        self._logger.info(f"Iniciando creación de cliente con validación completa")
        
        try:
            # Validar reglas de negocio antes de la creación
            await self._validate_business_rules_for_creation(client_data)
            
            # Validar dependencias externas si es requerido
            if validate_dependencies:
                await self._validate_external_dependencies(client_data)
            
            # Verificar duplicados con lógica de negocio
            await self._check_for_business_duplicates(client_data)
            
            # Crear el cliente usando el repositorio
            created_client = await self._client_repository.create_client(client_data)
            
            # Ejecutar acciones post-creación
            await self._execute_post_creation_actions(
                created_client, 
                notify_stakeholders=notify_stakeholders
            )
            
            self._logger.info(f"Cliente creado exitosamente con ID: {created_client.id}")
            return created_client
            
        except (ClientValidationError, ClientDuplicateError) as e:
            self._logger.error(f"Error de validación en creación de cliente: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en creación de cliente: {e}")
            raise ClientDomainError(
                message=f"Error inesperado en creación de cliente: {e}",
                operation="create_client_with_validation",
                original_error=e
            )

    async def update_client_with_dependencies(
        self,
        client_id: int,
        update_data: ClientUpdateSchema,
        validate_impact: bool = True,
        cascade_updates: bool = True
    ) -> ClientResponseSchema:
        """
        Actualiza un cliente considerando dependencias y impacto en cascada.
        
        Args:
            client_id: ID del cliente a actualizar
            update_data: Datos de actualización
            validate_impact: Si validar impacto en entidades relacionadas
            cascade_updates: Si propagar cambios a entidades dependientes
            
        Returns:
            Cliente actualizado
            
        Raises:
            ClientNotFoundError: Si el cliente no existe
            ClientBusinessRuleViolationError: Si viola reglas de negocio
            ClientDependencyError: Si hay conflictos de dependencias
        """
        self._logger.info(f"Iniciando actualización de cliente {client_id} con dependencias")
        
        try:
            # Obtener cliente actual para comparación
            current_client = await self._client_repository.get_client_by_id(client_id)
            if not current_client:
                raise ClientNotFoundError(f"Cliente con ID {client_id} no encontrado")
            
            # Validar reglas de negocio para la actualización
            await self._validate_business_rules_for_update(current_client, update_data)
            
            # Validar impacto en dependencias si es requerido
            if validate_impact:
                await self._validate_update_impact(client_id, update_data)
            
            # Realizar la actualización
            updated_client = await self._client_repository.update_client(client_id, update_data)
            
            # Propagar cambios en cascada si es requerido
            if cascade_updates:
                await self._execute_cascade_updates(current_client, updated_client)
            
            self._logger.info(f"Cliente {client_id} actualizado exitosamente")
            return updated_client
            
        except (ClientNotFoundError, ClientBusinessRuleViolationError, ClientDependencyError) as e:
            self._logger.error(f"Error en actualización de cliente {client_id}: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en actualización de cliente {client_id}: {e}")
            raise ClientDomainError(
                message=f"Error inesperado en actualización de cliente: {e}",
                client_id=client_id,
                operation="update_client_with_dependencies",
                original_error=e
            )

    async def delete_client_with_cleanup(
        self,
        client_id: int,
        force_delete: bool = False,
        cleanup_related_data: bool = True
    ) -> bool:
        """
        Elimina un cliente con limpieza completa de datos relacionados.
        
        Args:
            client_id: ID del cliente a eliminar
            force_delete: Si forzar eliminación ignorando dependencias
            cleanup_related_data: Si limpiar datos relacionados
            
        Returns:
            True si la eliminación fue exitosa
            
        Raises:
            ClientNotFoundError: Si el cliente no existe
            ClientDependencyError: Si tiene dependencias que impiden la eliminación
        """
        self._logger.info(f"Iniciando eliminación de cliente {client_id} con limpieza")
        
        try:
            # Verificar existencia del cliente
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ClientNotFoundError(f"Cliente con ID {client_id} no encontrado")
            
            # Validar dependencias si no es eliminación forzada
            if not force_delete:
                await self._validate_deletion_dependencies(client_id)
            
            # Ejecutar limpieza de datos relacionados si es requerido
            if cleanup_related_data:
                await self._cleanup_related_data(client_id)
            
            # Realizar la eliminación
            success = await self._client_repository.delete_client(client_id)
            
            if success:
                # Ejecutar acciones post-eliminación
                await self._execute_post_deletion_actions(client)
                self._logger.info(f"Cliente {client_id} eliminado exitosamente")
            
            return success
            
        except (ClientNotFoundError, ClientDependencyError) as e:
            self._logger.error(f"Error en eliminación de cliente {client_id}: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en eliminación de cliente {client_id}: {e}")
            raise ClientDomainError(
                message=f"Error inesperado en eliminación de cliente: {e}",
                client_id=client_id,
                operation="delete_client_with_cleanup",
                original_error=e
            )

    # ============================================================================
    # BÚSQUEDA AVANZADA Y CONSULTAS COMPLEJAS
    # ============================================================================

    async def advanced_client_search(
        self,
        search_criteria: ClientSearchSchema,
        include_analytics: bool = False,
        include_relationships: bool = False
    ) -> Dict[str, Any]:
        """
        Realiza búsqueda avanzada de clientes con criterios complejos.
        
        Args:
            search_criteria: Criterios de búsqueda
            include_analytics: Si incluir datos analíticos
            include_relationships: Si incluir datos de relaciones
            
        Returns:
            Resultados de búsqueda con metadatos
        """
        self._logger.info("Ejecutando búsqueda avanzada de clientes")
        
        try:
            # Realizar búsqueda base
            clients = await self._client_repository.search_clients_advanced(search_criteria)
            
            # Enriquecer resultados si es requerido
            enriched_results = []
            for client in clients:
                enriched_client = client.dict()
                
                if include_analytics:
                    analytics = await self._get_client_analytics(client.id)
                    enriched_client['analytics'] = analytics
                
                if include_relationships:
                    relationships = await self._get_client_relationships(client.id)
                    enriched_client['relationships'] = relationships
                
                enriched_results.append(enriched_client)
            
            # Generar metadatos de búsqueda
            search_metadata = await self._generate_search_metadata(search_criteria, len(clients))
            
            return {
                'clients': enriched_results,
                'metadata': search_metadata,
                'total_count': len(clients),
                'search_criteria': search_criteria.dict(),
                'timestamp': pendulum.now().isoformat()
            }
            
        except Exception as e:
            self._logger.error(f"Error en búsqueda avanzada de clientes: {e}")
            raise ClientDomainError(
                message=f"Error en búsqueda avanzada: {e}",
                operation="advanced_client_search",
                original_error=e
            )

    async def get_clients_by_complex_criteria(
        self,
        criteria: Dict[str, Any],
        sort_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[ClientResponseSchema]:
        """
        Obtiene clientes usando criterios complejos de filtrado.
        
        Args:
            criteria: Criterios de filtrado complejos
            sort_by: Campo de ordenamiento
            limit: Límite de resultados
            offset: Desplazamiento de resultados
            
        Returns:
            Lista de clientes que cumplen los criterios
        """
        self._logger.info(f"Obteniendo clientes con criterios complejos: {criteria}")
        
        try:
            # Procesar y validar criterios
            processed_criteria = await self._process_complex_criteria(criteria)
            
            # Ejecutar consulta con criterios procesados
            clients = await self._client_repository.find_clients_by_criteria(
                criteria=processed_criteria,
                sort_by=sort_by,
                limit=limit,
                offset=offset
            )
            
            return clients
            
        except Exception as e:
            self._logger.error(f"Error obteniendo clientes con criterios complejos: {e}")
            raise ClientDomainError(
                message=f"Error en consulta compleja: {e}",
                operation="get_clients_by_complex_criteria",
                original_error=e
            )

    # ============================================================================
    # GESTIÓN DE PROYECTOS Y TRANSFERENCIAS
    # ============================================================================

    async def transfer_projects_between_clients(
        self,
        from_client_id: int,
        to_client_id: int,
        project_ids: Optional[List[int]] = None,
        validate_business_rules: bool = True
    ) -> Dict[str, Any]:
        """
        Transfiere proyectos entre clientes con validaciones de negocio.
        
        Args:
            from_client_id: ID del cliente origen
            to_client_id: ID del cliente destino
            project_ids: IDs específicos de proyectos (None = todos)
            validate_business_rules: Si validar reglas de negocio
            
        Returns:
            Resultado de la transferencia con detalles
            
        Raises:
            ClientProjectTransferError: Si falla la transferencia
            ClientNotFoundError: Si algún cliente no existe
        """
        self._logger.info(f"Transfiriendo proyectos del cliente {from_client_id} al {to_client_id}")
        
        try:
            # Validar existencia de clientes
            from_client = await self._client_repository.get_client_by_id(from_client_id)
            to_client = await self._client_repository.get_client_by_id(to_client_id)
            
            if not from_client:
                raise ClientNotFoundError(f"Cliente origen {from_client_id} no encontrado")
            if not to_client:
                raise ClientNotFoundError(f"Cliente destino {to_client_id} no encontrado")
            
            # Validar reglas de negocio si es requerido
            if validate_business_rules:
                await self._validate_project_transfer_rules(from_client_id, to_client_id, project_ids)
            
            # Ejecutar transferencia
            transfer_result = await self._execute_project_transfer(
                from_client_id, to_client_id, project_ids
            )
            
            # Registrar evento de transferencia
            await self._register_transfer_event(from_client_id, to_client_id, transfer_result)
            
            self._logger.info(f"Transferencia completada: {transfer_result['transferred_count']} proyectos")
            return transfer_result
            
        except (ClientNotFoundError, ClientProjectTransferError) as e:
            self._logger.error(f"Error en transferencia de proyectos: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en transferencia de proyectos: {e}")
            raise create_client_project_transfer_error(
                from_client_id=from_client_id,
                to_client_id=to_client_id,
                project_ids=project_ids,
                reason=f"Error inesperado: {e}"
            )

    async def analyze_client_project_portfolio(
        self,
        client_id: int,
        analysis_type: str = "comprehensive",
        date_range: Optional[Tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Analiza el portafolio de proyectos de un cliente.
        
        Args:
            client_id: ID del cliente
            analysis_type: Tipo de análisis (comprehensive, financial, timeline)
            date_range: Rango de fechas para el análisis
            
        Returns:
            Análisis completo del portafolio
            
        Raises:
            ClientNotFoundError: Si el cliente no existe
            ClientAnalysisError: Si falla el análisis
        """
        self._logger.info(f"Analizando portafolio de proyectos del cliente {client_id}")
        
        try:
            # Verificar existencia del cliente
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ClientNotFoundError(f"Cliente {client_id} no encontrado")
            
            # Obtener datos del portafolio
            portfolio_data = await self._get_client_portfolio_data(client_id, date_range)
            
            # Ejecutar análisis según el tipo
            analysis_result = await self._execute_portfolio_analysis(
                portfolio_data, analysis_type
            )
            
            # Enriquecer con insights de negocio
            enriched_analysis = await self._enrich_portfolio_analysis(
                client_id, analysis_result
            )
            
            return enriched_analysis
            
        except (ClientNotFoundError, ClientAnalysisError) as e:
            self._logger.error(f"Error en análisis de portafolio del cliente {client_id}: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en análisis de portafolio: {e}")
            raise create_client_analysis_error(
                analysis_type="portfolio_analysis",
                client_id=client_id,
                reason=f"Error inesperado: {e}"
            )

    # ============================================================================
    # ANÁLISIS Y ESTADÍSTICAS DE NEGOCIO
    # ============================================================================

    async def generate_client_business_report(
        self,
        client_id: int,
        report_type: str = "comprehensive",
        include_projections: bool = True,
        date_range: Optional[Tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Genera un reporte de negocio completo para un cliente.
        
        Args:
            client_id: ID del cliente
            report_type: Tipo de reporte
            include_projections: Si incluir proyecciones
            date_range: Rango de fechas
            
        Returns:
            Reporte de negocio completo
        """
        self._logger.info(f"Generando reporte de negocio para cliente {client_id}")
        
        try:
            # Obtener datos base del cliente
            client_data = await self._get_comprehensive_client_data(client_id)
            
            # Generar secciones del reporte
            report_sections = {}
            
            # Sección de información general
            report_sections['general_info'] = await self._generate_general_info_section(client_data)
            
            # Sección de análisis financiero
            report_sections['financial_analysis'] = await self._generate_financial_analysis_section(
                client_id, date_range
            )
            
            # Sección de análisis de proyectos
            report_sections['project_analysis'] = await self._generate_project_analysis_section(
                client_id, date_range
            )
            
            # Sección de métricas de rendimiento
            report_sections['performance_metrics'] = await self._generate_performance_metrics_section(
                client_id, date_range
            )
            
            # Proyecciones si son requeridas
            if include_projections:
                report_sections['projections'] = await self._generate_projections_section(
                    client_id, report_type
                )
            
            # Ensamblar reporte final
            business_report = {
                'client_id': client_id,
                'report_type': report_type,
                'generated_at': pendulum.now().isoformat(),
                'date_range': {
                    'start': date_range[0].isoformat() if date_range else None,
                    'end': date_range[1].isoformat() if date_range else None
                },
                'sections': report_sections,
                'metadata': {
                    'version': '1.0',
                    'generator': 'ClientDomainService',
                    'includes_projections': include_projections
                }
            }
            
            return business_report
            
        except Exception as e:
            self._logger.error(f"Error generando reporte de negocio para cliente {client_id}: {e}")
            raise ClientReportGenerationError(
                report_type=report_type,
                client_id=client_id,
                reason=f"Error en generación: {e}"
            )

    async def calculate_client_performance_metrics(
        self,
        client_id: int,
        metrics_types: List[str],
        comparison_period: Optional[Tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Calcula métricas de rendimiento específicas para un cliente.
        
        Args:
            client_id: ID del cliente
            metrics_types: Tipos de métricas a calcular
            comparison_period: Período de comparación
            
        Returns:
            Métricas de rendimiento calculadas
        """
        self._logger.info(f"Calculando métricas de rendimiento para cliente {client_id}")
        
        try:
            metrics_results = {}
            
            for metric_type in metrics_types:
                metric_result = await self._calculate_specific_metric(
                    client_id, metric_type, comparison_period
                )
                metrics_results[metric_type] = metric_result
            
            # Agregar métricas comparativas si hay período de comparación
            if comparison_period:
                comparative_metrics = await self._calculate_comparative_metrics(
                    client_id, metrics_results, comparison_period
                )
                metrics_results['comparative_analysis'] = comparative_metrics
            
            return {
                'client_id': client_id,
                'metrics': metrics_results,
                'calculated_at': pendulum.now().isoformat(),
                'comparison_period': {
                    'start': comparison_period[0].isoformat() if comparison_period else None,
                    'end': comparison_period[1].isoformat() if comparison_period else None
                }
            }
            
        except Exception as e:
            self._logger.error(f"Error calculando métricas para cliente {client_id}: {e}")
            raise create_client_analysis_error(
                analysis_type="performance_metrics",
                client_id=client_id,
                reason=f"Error en cálculo de métricas: {e}"
            )

    async def get_client_dashboard_data(
        self,
        client_id: int,
        dashboard_type: str = "executive"
    ) -> Dict[str, Any]:
        """
        Obtiene datos para el dashboard ejecutivo de un cliente.
        
        Args:
            client_id: ID del cliente
            dashboard_type: Tipo de dashboard
            
        Returns:
            Datos estructurados para el dashboard
        """
        self._logger.info(f"Obteniendo datos de dashboard para cliente {client_id}")
        
        try:
            dashboard_data = {}
            
            # Datos básicos del cliente
            dashboard_data['client_info'] = await self._get_dashboard_client_info(client_id)
            
            # KPIs principales
            dashboard_data['key_metrics'] = await self._get_dashboard_key_metrics(client_id)
            
            # Gráficos y visualizaciones
            dashboard_data['charts_data'] = await self._get_dashboard_charts_data(client_id)
            
            # Alertas y notificaciones
            dashboard_data['alerts'] = await self._get_dashboard_alerts(client_id)
            
            # Acciones recomendadas
            dashboard_data['recommended_actions'] = await self._get_recommended_actions(client_id)
            
            return {
                'client_id': client_id,
                'dashboard_type': dashboard_type,
                'data': dashboard_data,
                'last_updated': pendulum.now().isoformat()
            }
            
        except Exception as e:
            self._logger.error(f"Error obteniendo datos de dashboard para cliente {client_id}: {e}")
            raise ClientDomainError(
                message=f"Error obteniendo datos de dashboard: {e}",
                client_id=client_id,
                operation="get_client_dashboard_data",
                original_error=e
            )

    # ============================================================================
    # VALIDACIONES Y REGLAS DE NEGOCIO
    # ============================================================================

    async def validate_complex_business_rules(
        self,
        client_id: int,
        operation: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valida reglas de negocio complejas para operaciones de cliente.
        
        Args:
            client_id: ID del cliente
            operation: Tipo de operación
            data: Datos a validar
            
        Returns:
            Resultado de validación con detalles
            
        Raises:
            ClientBusinessRuleViolationError: Si viola reglas de negocio
        """
        self._logger.info(f"Validando reglas de negocio para cliente {client_id}, operación: {operation}")
        
        try:
            validation_results = {
                'is_valid': True,
                'violations': [],
                'warnings': [],
                'recommendations': []
            }
            
            # Ejecutar validaciones según la operación
            if operation == 'create':
                await self._validate_creation_rules(data, validation_results)
            elif operation == 'update':
                await self._validate_update_rules(client_id, data, validation_results)
            elif operation == 'delete':
                await self._validate_deletion_rules(client_id, validation_results)
            elif operation == 'project_transfer':
                await self._validate_transfer_rules(client_id, data, validation_results)
            
            # Validaciones generales aplicables a todas las operaciones
            await self._validate_general_business_rules(client_id, data, validation_results)
            
            # Si hay violaciones críticas, lanzar excepción
            critical_violations = [v for v in validation_results['violations'] if v.get('severity') == 'critical']
            if critical_violations:
                raise create_client_business_rule_violation(
                    rule_name="multiple_business_rules",
                    rule_description=f"Se encontraron {len(critical_violations)} violaciones críticas",
                    client_id=client_id,
                    violated_data={'violations': critical_violations}
                )
            
            return validation_results
            
        except ClientBusinessRuleViolationError as e:
            self._logger.error(f"Violación de reglas de negocio para cliente {client_id}: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en validación de reglas de negocio: {e}")
            raise ClientDomainError(
                message=f"Error en validación de reglas de negocio: {e}",
                client_id=client_id,
                operation="validate_complex_business_rules",
                original_error=e
            )

    async def check_client_constraints(
        self,
        client_id: int,
        constraint_types: List[str]
    ) -> Dict[str, Any]:
        """
        Verifica restricciones específicas de un cliente.
        
        Args:
            client_id: ID del cliente
            constraint_types: Tipos de restricciones a verificar
            
        Returns:
            Estado de las restricciones verificadas
        """
        self._logger.info(f"Verificando restricciones para cliente {client_id}")
        
        try:
            constraints_status = {}
            
            for constraint_type in constraint_types:
                status = await self._check_specific_constraint(client_id, constraint_type)
                constraints_status[constraint_type] = status
            
            return {
                'client_id': client_id,
                'constraints': constraints_status,
                'checked_at': pendulum.now().isoformat(),
                'overall_status': all(c.get('is_satisfied', False) for c in constraints_status.values())
            }
            
        except Exception as e:
            self._logger.error(f"Error verificando restricciones para cliente {client_id}: {e}")
            raise ClientDomainError(
                message=f"Error verificando restricciones: {e}",
                client_id=client_id,
                operation="check_client_constraints",
                original_error=e
            )

    # ============================================================================
    # COORDINACIÓN ENTRE DOMINIOS
    # ============================================================================

    async def coordinate_client_lifecycle_events(
        self,
        client_id: int,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordina eventos del ciclo de vida del cliente con otros dominios.
        
        Args:
            client_id: ID del cliente
            event_type: Tipo de evento
            event_data: Datos del evento
            
        Returns:
            Resultado de la coordinación
        """
        self._logger.info(f"Coordinando evento '{event_type}' para cliente {client_id}")
        
        try:
            coordination_results = {
                'event_type': event_type,
                'client_id': client_id,
                'coordinated_domains': [],
                'success': True,
                'errors': []
            }
            
            # Coordinar con dominio de proyectos
            if event_type in ['client_created', 'client_updated', 'client_deleted']:
                project_result = await self._coordinate_with_project_domain(
                    client_id, event_type, event_data
                )
                coordination_results['coordinated_domains'].append({
                    'domain': 'projects',
                    'result': project_result
                })
            
            # Coordinar con dominio de equipos
            if event_type in ['client_created', 'client_deleted']:
                team_result = await self._coordinate_with_team_domain(
                    client_id, event_type, event_data
                )
                coordination_results['coordinated_domains'].append({
                    'domain': 'teams',
                    'result': team_result
                })
            
            # Coordinar con servicios externos
            external_result = await self._coordinate_with_external_services(
                client_id, event_type, event_data
            )
            coordination_results['coordinated_domains'].append({
                'domain': 'external_services',
                'result': external_result
            })
            
            return coordination_results
            
        except Exception as e:
            self._logger.error(f"Error coordinando evento '{event_type}' para cliente {client_id}: {e}")
            raise ClientDomainCoordinationError(
                coordination_type="lifecycle_events",
                target_domain="multiple",
                client_id=client_id,
                coordination_data=event_data,
                reason=f"Error en coordinación: {e}"
            )

    async def synchronize_client_data_across_domains(
        self,
        client_id: int,
        sync_targets: List[str],
        force_sync: bool = False
    ) -> Dict[str, Any]:
        """
        Sincroniza datos del cliente a través de múltiples dominios.
        
        Args:
            client_id: ID del cliente
            sync_targets: Dominios objetivo para sincronización
            force_sync: Si forzar sincronización ignorando conflictos
            
        Returns:
            Resultado de la sincronización
        """
        self._logger.info(f"Sincronizando datos del cliente {client_id} con dominios: {sync_targets}")
        
        try:
            sync_results = {
                'client_id': client_id,
                'sync_targets': sync_targets,
                'results': {},
                'overall_success': True,
                'sync_timestamp': pendulum.now().isoformat()
            }
            
            # Obtener datos actuales del cliente
            client_data = await self._client_repository.get_client_by_id(client_id)
            if not client_data:
                raise ClientNotFoundError(f"Cliente {client_id} no encontrado")
            
            # Sincronizar con cada dominio objetivo
            for target in sync_targets:
                try:
                    target_result = await self._sync_with_specific_domain(
                        client_id, target, client_data, force_sync
                    )
                    sync_results['results'][target] = target_result
                except Exception as e:
                    sync_results['results'][target] = {
                        'success': False,
                        'error': str(e)
                    }
                    sync_results['overall_success'] = False
                    self._logger.error(f"Error sincronizando con dominio {target}: {e}")
            
            return sync_results
            
        except Exception as e:
            self._logger.error(f"Error en sincronización de datos del cliente {client_id}: {e}")
            raise ClientDataSynchronizationError(
                synchronization_target=", ".join(sync_targets),
                client_id=client_id,
                reason=f"Error en sincronización: {e}"
            )

    # ============================================================================
    # MÉTODOS PRIVADOS DE APOYO
    # ============================================================================

    async def _validate_business_rules_for_creation(self, client_data: ClientCreateSchema) -> None:
        """Valida reglas de negocio específicas para creación de clientes."""
        # Validar longitud del nombre
        if len(client_data.name) < self._business_rules['min_name_length']:
            raise create_client_business_rule_violation(
                rule_name="min_name_length",
                rule_description=f"El nombre debe tener al menos {self._business_rules['min_name_length']} caracteres",
                violated_data={'name': client_data.name, 'length': len(client_data.name)}
            )
        
        if len(client_data.name) > self._business_rules['max_name_length']:
            raise create_client_business_rule_violation(
                rule_name="max_name_length",
                rule_description=f"El nombre no puede exceder {self._business_rules['max_name_length']} caracteres",
                violated_data={'name': client_data.name, 'length': len(client_data.name)}
            )
        
        # Validar dominios de email permitidos si están configurados
        if self._business_rules['email_domains_allowed'] and client_data.email:
            email_domain = client_data.email.split('@')[1] if '@' in client_data.email else ''
            if email_domain not in self._business_rules['email_domains_allowed']:
                raise create_client_business_rule_violation(
                    rule_name="email_domain_restriction",
                    rule_description=f"El dominio de email '{email_domain}' no está permitido",
                    violated_data={'email': client_data.email, 'domain': email_domain}
                )

    async def _validate_business_rules_for_update(
        self, 
        current_client: ClientResponseSchema, 
        update_data: ClientUpdateSchema
    ) -> None:
        """Valida reglas de negocio específicas para actualización de clientes."""
        # Validar transiciones de estado si se está actualizando el estado
        if hasattr(update_data, 'status') and update_data.status:
            current_status = getattr(current_client, 'status', 'active')
            allowed_transitions = self._business_rules['client_status_transitions'].get(current_status, [])
            
            if update_data.status not in allowed_transitions:
                raise create_client_business_rule_violation(
                    rule_name="invalid_status_transition",
                    rule_description=f"No se puede cambiar de estado '{current_status}' a '{update_data.status}'",
                    client_id=current_client.id,
                    violated_data={
                        'current_status': current_status,
                        'requested_status': update_data.status,
                        'allowed_transitions': allowed_transitions
                    }
                )

    async def _validate_external_dependencies(self, client_data: ClientCreateSchema) -> None:
        """Valida dependencias externas antes de crear un cliente."""
        # Aquí se implementarían validaciones con servicios externos
        # Por ejemplo, validación de CRM, sistemas de facturación, etc.
        pass

    async def _check_for_business_duplicates(self, client_data: ClientCreateSchema) -> None:
        """Verifica duplicados usando lógica de negocio específica."""
        # Buscar clientes con nombre similar
        similar_clients = await self._client_repository.search_clients_by_name(client_data.name)
        
        if similar_clients:
            # Aplicar lógica de negocio para determinar si es duplicado
            for similar_client in similar_clients:
                similarity_score = await self._calculate_client_similarity(client_data, similar_client)
                if similarity_score > 0.8:  # Umbral de similitud
                    raise ClientDuplicateError(
                        f"Cliente similar ya existe: {similar_client.name}",
                        existing_client_id=similar_client.id
                    )

    async def _execute_post_creation_actions(
        self, 
        created_client: ClientResponseSchema, 
        notify_stakeholders: bool
    ) -> None:
        """Ejecuta acciones posteriores a la creación de un cliente."""
        # Registrar evento de creación
        await self.coordinate_client_lifecycle_events(
            created_client.id,
            'client_created',
            {'client_data': created_client.dict()}
        )
        
        # Notificar stakeholders si es requerido
        if notify_stakeholders:
            await self._notify_client_creation(created_client)

    async def _validate_update_impact(self, client_id: int, update_data: ClientUpdateSchema) -> None:
        """Valida el impacto de una actualización en entidades relacionadas."""
        # Obtener proyectos relacionados
        related_projects = await self._client_repository.get_client_projects(client_id)
        
        # Validar impacto en proyectos si se cambian datos críticos
        if hasattr(update_data, 'name') and update_data.name and related_projects:
            # Verificar si el cambio de nombre afecta proyectos activos
            active_projects = [p for p in related_projects if p.status == 'active']
            if active_projects:
                self._logger.warning(
                    f"Cambio de nombre del cliente {client_id} afectará {len(active_projects)} proyectos activos"
                )

    async def _execute_cascade_updates(
        self, 
        current_client: ClientResponseSchema, 
        updated_client: ClientResponseSchema
    ) -> None:
        """Ejecuta actualizaciones en cascada a entidades dependientes."""
        # Coordinar actualizaciones con otros dominios
        await self.coordinate_client_lifecycle_events(
            updated_client.id,
            'client_updated',
            {
                'previous_data': current_client.dict(),
                'updated_data': updated_client.dict()
            }
        )

    async def _validate_deletion_dependencies(self, client_id: int) -> None:
        """Valida dependencias que podrían impedir la eliminación."""
        # Verificar proyectos activos
        active_projects = await self._client_repository.get_active_projects_count(client_id)
        if active_projects > 0:
            raise create_client_dependency_error(
                dependency_type="active_projects",
                dependency_details={
                    'active_projects_count': active_projects,
                    'message': 'No se puede eliminar cliente con proyectos activos'
                },
                client_id=client_id,
                operation="delete_validation"
            )

    async def _cleanup_related_data(self, client_id: int) -> None:
        """Limpia datos relacionados antes de eliminar un cliente."""
        # Limpiar datos de proyectos completados
        await self._client_repository.cleanup_completed_projects(client_id)
        
        # Limpiar datos históricos si es necesario
        await self._client_repository.cleanup_historical_data(client_id)

    async def _execute_post_deletion_actions(self, deleted_client: ClientResponseSchema) -> None:
        """Ejecuta acciones posteriores a la eliminación de un cliente."""
        # Registrar evento de eliminación
        await self.coordinate_client_lifecycle_events(
            deleted_client.id,
            'client_deleted',
            {'deleted_client_data': deleted_client.dict()}
        )

    # Métodos adicionales de apoyo continuarían aquí...
    # (Por brevedad, no incluyo todos los métodos privados, pero seguirían el mismo patrón)

    async def _get_client_analytics(self, client_id: int) -> Dict[str, Any]:
        """Obtiene datos analíticos de un cliente."""
        return await self._client_repository.get_client_analytics(client_id)

    async def _get_client_relationships(self, client_id: int) -> Dict[str, Any]:
        """Obtiene datos de relaciones de un cliente."""
        return await self._client_repository.get_client_relationships(client_id)

    async def _generate_search_metadata(
        self, 
        search_criteria: ClientSearchSchema, 
        results_count: int
    ) -> Dict[str, Any]:
        """Genera metadatos para resultados de búsqueda."""
        return {
            'search_executed_at': pendulum.now().isoformat(),
            'results_count': results_count,
            'search_duration_ms': 0,  # Se calcularía el tiempo real
            'criteria_summary': search_criteria.dict()
        }

    async def _process_complex_criteria(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa y valida criterios complejos de búsqueda."""
        # Implementar lógica de procesamiento de criterios
        return criteria

    async def _calculate_client_similarity(
        self, 
        client_data: ClientCreateSchema, 
        existing_client: ClientResponseSchema
    ) -> float:
        """Calcula la similitud entre dos clientes."""
        # Implementar algoritmo de similitud
        return 0.0

    async def _notify_client_creation(self, client: ClientResponseSchema) -> None:
        """Notifica la creación de un cliente a stakeholders."""
        # Implementar lógica de notificación
        pass