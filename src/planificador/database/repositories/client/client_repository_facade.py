"""Facade para el repositorio de clientes que unifica todos los módulos especializados.

Este módulo implementa el patrón Facade para proporcionar una interfaz unificada
y simplificada para todas las operaciones relacionadas con clientes, coordinando
los diferentes módulos especializados.

Autor: Sistema de Modularización
Fecha: 2025-01-21
Versión: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

# Importaciones de modelos y esquemas
from planificador.models.client import Client
from planificador.schemas.client import ClientCreate, ClientUpdate

# Importaciones de módulos especializados
from .client_crud_operations import ClientCRUDOperations
from .client_date_operations import ClientDateOperations
from .client_exception_handler import ClientExceptionHandler
from .client_query_builder import ClientQueryBuilder
from .client_statistics import ClientStatistics
from .client_validator import ClientValidator

# Importaciones de utilidades
from planificador.utils.time_utils import get_current_time
from planificador.exceptions.client_exceptions import (
    ClientRepositoryError,
    create_client_repository_error
)
from planificador.exceptions.database_exceptions import (
    convert_sqlalchemy_error
)
from sqlalchemy.exc import SQLAlchemyError


class ClientRepositoryFacade:
    """
    Facade que unifica todas las operaciones de clientes a través de módulos especializados.
    
    Esta clase actúa como punto de entrada único para todas las operaciones relacionadas
    con clientes, delegando a los módulos especializados apropiados y coordinando
    operaciones complejas que requieren múltiples módulos.
    
    Attributes:
        session: Sesión asíncrona de SQLAlchemy
        crud_ops: Operaciones CRUD especializadas
        date_ops: Operaciones relacionadas con fechas
        exception_handler: Manejador centralizado de excepciones
        query_builder: Constructor de consultas especializadas
        statistics: Generador de estadísticas y métricas
        validator: Validador de datos de clientes
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el facade con todos los módulos especializados.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self.session = session
        self._logger = logger.bind(component="ClientRepositoryFacade")
        
        # Inicializar módulos especializados
        self.crud_ops = ClientCRUDOperations(session)
        self.date_ops = ClientDateOperations(session)
        self.exception_handler = ClientExceptionHandler(session)
        self.query_builder = ClientQueryBuilder(session)
        self.statistics = ClientStatistics(session)
        self.validator = ClientValidator(session)
        
        self._logger.debug("ClientRepositoryFacade inicializado con todos los módulos especializados")
    
    # ============================================================================
    # OPERACIONES CRUD UNIFICADAS
    # ============================================================================
    
    async def create_client(self, client_data: ClientCreate) -> Client:
        """
        Crea un nuevo cliente con validaciones completas.
        
        Args:
            client_data: Datos del cliente a crear
            
        Returns:
            Cliente creado
            
        Raises:
            ClientRepositoryError: Si ocurre un error en la creación
        """
        try:
            return await self.crud_ops.create_client(client_data)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="create_client",
                context={"client_data": client_data.model_dump() if hasattr(client_data, 'model_dump') else str(client_data)}
            )
    
    async def create_client_with_pendulum_validation(self, client_data: ClientCreate) -> Client:
        """
        Crea un cliente con validaciones avanzadas de fecha usando Pendulum.
        
        Args:
            client_data: Datos del cliente a crear
            
        Returns:
            Cliente creado con validaciones de fecha
        """
        try:
            return await self.crud_ops.create_client_with_pendulum_validation(client_data)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="create_client_with_pendulum_validation",
                context={"client_data": client_data.model_dump() if hasattr(client_data, 'model_dump') else str(client_data)}
            )
    
    async def get_client_by_id(self, client_id: int) -> Optional[Client]:
        """
        Obtiene un cliente por su ID.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Cliente encontrado o None
        """
        try:
            return await self.crud_ops.get_client_by_id(client_id)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_by_id",
                context={"client_id": client_id}
            )
    
    async def update_client(self, client_id: int, client_data: ClientUpdate) -> Optional[Client]:
        """
        Actualiza un cliente existente.
        
        Args:
            client_id: ID del cliente a actualizar
            client_data: Datos de actualización
            
        Returns:
            Cliente actualizado o None si no existe
        """
        try:
            return await self.crud_ops.update_client(client_id, client_data)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="update_client",
                context={"client_id": client_id, "client_data": client_data.model_dump() if hasattr(client_data, 'model_dump') else str(client_data)}
            )
    
    async def delete_client(self, client_id: int) -> bool:
        """
        Elimina un cliente (soft delete).
        
        Args:
            client_id: ID del cliente a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            return await self.crud_ops.delete_client(client_id)
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="delete_client",
                context={"client_id": client_id}
            )
            return False
    
    # ============================================================================
    # CONSULTAS ESPECIALIZADAS
    # ============================================================================
    
    async def get_client_by_name(self, name: str) -> Optional[Client]:
        """
        Busca un cliente por nombre exacto.
        
        Args:
            name: Nombre del cliente
            
        Returns:
            Cliente encontrado o None
        """
        try:
            return await self.query_builder.get_by_name(name)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_by_name",
                context={"name": name}
            )
    
    async def get_client_by_code(self, code: str) -> Optional[Client]:
        """
        Busca un cliente por código único.
        
        Args:
            code: Código del cliente
            
        Returns:
            Cliente encontrado o None
        """
        try:
            return await self.query_builder.get_by_code(code)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_by_code",
                context={"code": code}
            )
    
    async def search_clients_by_name(self, name_pattern: str) -> List[Client]:
        """
        Busca clientes por patrón de nombre.
        
        Args:
            name_pattern: Patrón de búsqueda
            
        Returns:
            Lista de clientes que coinciden
        """
        try:
            return await self.query_builder.search_by_name(name_pattern)
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="search_clients_by_name",
                context={"name_pattern": name_pattern}
            )
            return []
    
    async def get_active_clients(self) -> List[Client]:
        """
        Obtiene todos los clientes activos.
        
        Returns:
            Lista de clientes activos
        """
        try:
            return await self.query_builder.get_active_clients()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_active_clients",
                context={}
            )
            return []
    
    async def search_with_advanced_filters(
        self,
        name_pattern: Optional[str] = None,
        code_pattern: Optional[str] = None,
        has_email: Optional[bool] = None,
        has_phone: Optional[bool] = None,
        has_contact_person: Optional[bool] = None,
        is_active: Optional[bool] = None,
        min_projects: Optional[int] = None,
        max_projects: Optional[int] = None,
        created_after: Optional[date] = None,
        created_before: Optional[date] = None,
        order_by: str = "name",
        order_direction: str = "asc",
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Client]:
        """
        Búsqueda avanzada de clientes con múltiples filtros.
        
        Args:
            name_pattern: Patrón de búsqueda en nombre
            code_pattern: Patrón de búsqueda en código
            has_email: Filtrar por presencia de email
            has_phone: Filtrar por presencia de teléfono
            has_contact_person: Filtrar por presencia de persona de contacto
            is_active: Filtrar por estado activo
            min_projects: Número mínimo de proyectos
            max_projects: Número máximo de proyectos
            created_after: Fecha de creación posterior a
            created_before: Fecha de creación anterior a
            order_by: Campo de ordenamiento
            order_direction: Dirección de ordenamiento
            limit: Límite de resultados
            offset: Desplazamiento de resultados
            
        Returns:
            Lista de clientes que coinciden con los filtros
        """
        try:
            return await self.query_builder.search_with_advanced_filters(
                name_pattern=name_pattern,
                code_pattern=code_pattern,
                has_email=has_email,
                has_phone=has_phone,
                has_contact_person=has_contact_person,
                is_active=is_active,
                min_projects=min_projects,
                max_projects=max_projects,
                created_after=created_after,
                created_before=created_before,
                order_by=order_by,
                order_direction=order_direction,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="search_with_advanced_filters",
                context={
                    "filters": {
                        "name_pattern": name_pattern,
                        "code_pattern": code_pattern,
                        "has_email": has_email,
                        "has_phone": has_phone,
                        "has_contact_person": has_contact_person,
                        "is_active": is_active,
                        "min_projects": min_projects,
                        "max_projects": max_projects,
                        "created_after": created_after.isoformat() if created_after else None,
                        "created_before": created_before.isoformat() if created_before else None,
                        "order_by": order_by,
                        "order_direction": order_direction,
                        "limit": limit,
                        "offset": offset
                    }
                }
            )
            return []
    
    # ============================================================================
    # OPERACIONES TEMPORALES
    # ============================================================================
    
    async def get_clients_created_current_week(self) -> List[Client]:
        """
        Obtiene clientes creados en la semana actual.
        
        Returns:
            Lista de clientes creados esta semana
        """
        try:
            return await self.date_ops.get_clients_created_current_week()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_created_current_week",
                context={}
            )
            return []
    
    async def get_clients_created_current_month(self) -> List[Client]:
        """
        Obtiene clientes creados en el mes actual.
        
        Returns:
            Lista de clientes creados este mes
        """
        try:
            return await self.date_ops.get_clients_created_current_month()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_created_current_month",
                context={}
            )
            return []
    
    async def get_clients_by_date_range(self, start_date: date, end_date: date) -> List[Client]:
        """
        Obtiene clientes creados en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Returns:
            Lista de clientes en el rango de fechas
        """
        try:
            return await self.date_ops.get_clients_by_date_range(start_date, end_date)
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_by_date_range",
                context={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
            )
            return []
    
    async def get_clients_by_age_range(self, min_age_days: int, max_age_days: int) -> List[Client]:
        """
        Obtiene clientes por rango de antigüedad.
        
        Args:
            min_age_days: Edad mínima en días
            max_age_days: Edad máxima en días
            
        Returns:
            Lista de clientes en el rango de antigüedad
        """
        try:
            return await self.date_ops.get_clients_by_age_range(min_age_days, max_age_days)
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_by_age_range",
                context={"min_age_days": min_age_days, "max_age_days": max_age_days}
            )
            return []
    
    # ============================================================================
    # ESTADÍSTICAS Y MÉTRICAS
    # ============================================================================
    
    async def get_client_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas básicas de clientes.
        
        Returns:
            Diccionario con estadísticas básicas
        """
        try:
            return await self.statistics.get_client_counts_by_status()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_statistics",
                context={}
            )
            return {}
    
    async def get_comprehensive_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas comprehensivas para dashboard ejecutivo.
        
        Returns:
            Diccionario con todas las métricas para dashboard
        """
        try:
            return await self.statistics.get_comprehensive_dashboard_metrics()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_comprehensive_dashboard_metrics",
                context={}
            )
            return {}
    
    async def get_client_segmentation_analysis(self) -> Dict[str, Any]:
        """
        Obtiene análisis de segmentación de clientes.
        
        Returns:
            Diccionario con análisis de segmentación
        """
        try:
            return await self.statistics.get_client_segmentation_analysis()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_segmentation_analysis",
                context={}
            )
            return {}
    
    async def get_client_value_analysis(self) -> Dict[str, Any]:
        """
        Obtiene análisis de valor de clientes.
        
        Returns:
            Diccionario con análisis de valor
        """
        try:
            return await self.statistics.get_client_value_analysis()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_value_analysis",
                context={}
            )
            return {}
    
    async def get_client_retention_analysis(self) -> Dict[str, Any]:
        """
        Obtiene análisis de retención de clientes.
        
        Returns:
            Diccionario con análisis de retención
        """
        try:
            return await self.statistics.get_client_retention_analysis()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_retention_analysis",
                context={}
            )
            return {}
    
    # ============================================================================
    # VALIDACIONES
    # ============================================================================
    
    async def validate_client_name_unique(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Valida que el nombre del cliente sea único.
        
        Args:
            name: Nombre a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)
            
        Returns:
            True si el nombre es único
        """
        try:
            return await self.validator.validate_name_unique(name, exclude_id)
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="validate_client_name_unique",
                context={"name": name, "exclude_id": exclude_id}
            )
            return False
    
    async def validate_client_code_unique(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Valida que el código del cliente sea único.
        
        Args:
            code: Código a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)
            
        Returns:
            True si el código es único
        """
        try:
            return await self.validator.validate_code_unique(code, exclude_id)
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="validate_client_code_unique",
                context={"code": code, "exclude_id": exclude_id}
            )
            return False
    
    # ============================================================================
    # OPERACIONES COMPLEJAS COORDINADAS
    # ============================================================================
    
    async def create_client_with_full_validation(
        self,
        client_data: ClientCreate,
        validate_business_rules: bool = True
    ) -> Client:
        """
        Crea un cliente con validaciones completas y reglas de negocio.
        
        Esta operación coordina múltiples módulos para realizar una creación
        completa con todas las validaciones necesarias.
        
        Args:
            client_data: Datos del cliente a crear
            validate_business_rules: Si aplicar reglas de negocio adicionales
            
        Returns:
            Cliente creado
            
        Raises:
            ClientRepositoryError: Si falla alguna validación o la creación
        """
        try:
            self._logger.debug(f"Iniciando creación completa de cliente: {client_data.name}")
            
            # Validar unicidad de nombre y código
            if not await self.validator.validate_name_unique(client_data.name):
                raise create_client_repository_error(
                    message=f"El nombre '{client_data.name}' ya existe",
                    operation="create_client_with_full_validation",
                    entity_id=None
                )
            
            if not await self.validator.validate_code_unique(client_data.code):
                raise create_client_repository_error(
                    message=f"El código '{client_data.code}' ya existe",
                    operation="create_client_with_full_validation",
                    entity_id=None
                )
            
            # Aplicar reglas de negocio adicionales si se solicita
            if validate_business_rules:
                # Validar formato de email si se proporciona
                if hasattr(client_data, 'email') and client_data.email:
                    if not await self.validator.validate_email_format(client_data.email):
                        raise create_client_repository_error(
                            message=f"Formato de email inválido: {client_data.email}",
                            operation="create_client_with_full_validation",
                            entity_id=None
                        )
                
                # Validar formato de teléfono si se proporciona
                if hasattr(client_data, 'phone') and client_data.phone:
                    if not await self.validator.validate_phone_format(client_data.phone):
                        raise create_client_repository_error(
                            message=f"Formato de teléfono inválido: {client_data.phone}",
                            operation="create_client_with_full_validation",
                            entity_id=None
                        )
            
            # Crear el cliente usando validaciones de Pendulum
            client = await self.crud_ops.create_client_with_pendulum_validation(client_data)
            
            # Registrar éxito de la operación
            await self.exception_handler.log_operation_success(
                operation="create_client_with_full_validation",
                entity_type="Client",
                entity_id=client.id,
                details=f"Cliente '{client.name}' creado exitosamente con validaciones completas"
            )
            
            self._logger.info(f"Cliente creado exitosamente con validaciones completas: {client.name} (ID: {client.id})")
            return client
            
        except ClientRepositoryError:
            # Re-lanzar errores de repositorio sin modificar
            raise
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="create_client_with_full_validation",
                context={
                    "client_data": client_data.model_dump() if hasattr(client_data, 'model_dump') else str(client_data),
                    "validate_business_rules": validate_business_rules
                }
            )
    
    async def get_client_complete_profile(self, client_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene el perfil completo de un cliente incluyendo estadísticas.
        
        Esta operación coordina múltiples módulos para obtener información
        comprehensiva sobre un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con perfil completo del cliente o None si no existe
        """
        try:
            self._logger.debug(f"Obteniendo perfil completo para cliente ID: {client_id}")
            
            # Obtener datos básicos del cliente
            client = await self.crud_ops.get_client_by_id(client_id)
            if not client:
                self._logger.warning(f"Cliente no encontrado: {client_id}")
                return None
            
            # Obtener estadísticas específicas del cliente
            client_stats = await self.statistics.get_client_stats(client_id)
            
            # Calcular edad del cliente
            client_age = await self.date_ops.calculate_client_age(client_id)
            
            # Construir perfil completo
            complete_profile = {
                'basic_info': {
                    'id': client.id,
                    'name': client.name,
                    'code': client.code,
                    'email': client.email,
                    'phone': client.phone,
                    'contact_person': client.contact_person,
                    'is_active': client.is_active,
                    'created_at': client.created_at.isoformat() if client.created_at else None,
                    'updated_at': client.updated_at.isoformat() if client.updated_at else None
                },
                'statistics': client_stats,
                'age_info': {
                    'age_days': client_age,
                    'age_months': round(client_age / 30.44, 1) if client_age else 0,
                    'age_years': round(client_age / 365.25, 1) if client_age else 0
                },
                'profile_generated_at': get_current_time().isoformat()
            }
            
            self._logger.debug(f"Perfil completo generado para cliente: {client.name}")
            return complete_profile
            
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_complete_profile",
                context={"client_id": client_id}
            )
            return None
    
    # ============================================================================
    # MÉTODOS DE UTILIDAD Y ESTADO
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud de todos los módulos del facade.
        
        Returns:
            Diccionario con estado de salud de cada módulo
        """
        try:
            health_status = {
                'facade_status': 'healthy',
                'modules': {},
                'timestamp': get_current_time().isoformat()
            }
            
            # Verificar cada módulo realizando una operación simple
            try:
                await self.statistics.get_client_counts_by_status()
                health_status['modules']['statistics'] = 'healthy'
            except Exception as e:
                health_status['modules']['statistics'] = f'error: {str(e)}'
            
            try:
                await self.query_builder.get_active_clients()
                health_status['modules']['query_builder'] = 'healthy'
            except Exception as e:
                health_status['modules']['query_builder'] = f'error: {str(e)}'
            
            # Verificar validador
            try:
                await self.validator.validate_name_unique("__health_check_test__")
                health_status['modules']['validator'] = 'healthy'
            except Exception as e:
                health_status['modules']['validator'] = f'error: {str(e)}'
            
            # Determinar estado general
            unhealthy_modules = [k for k, v in health_status['modules'].items() if v != 'healthy']
            if unhealthy_modules:
                health_status['facade_status'] = f'degraded - modules with issues: {", ".join(unhealthy_modules)}'
            
            self._logger.debug(f"Health check completado - Estado: {health_status['facade_status']}")
            return health_status
            
        except Exception as e:
            self._logger.error(f"Error en health check: {e}")
            return {
                'facade_status': f'error: {str(e)}',
                'modules': {},
                'timestamp': get_current_time().isoformat()
            }
    
    def get_module_info(self) -> Dict[str, str]:
        """
        Obtiene información sobre los módulos cargados.
        
        Returns:
            Diccionario con información de módulos
        """
        return {
            'crud_operations': self.crud_ops.__class__.__name__,
            'date_operations': self.date_ops.__class__.__name__,
            'exception_handler': self.exception_handler.__class__.__name__,
            'query_builder': self.query_builder.__class__.__name__,
            'statistics': self.statistics.__class__.__name__,
            'validator': self.validator.__class__.__name__,
            'facade_version': '1.0.0',
            'initialized_at': get_current_time().isoformat()
        }