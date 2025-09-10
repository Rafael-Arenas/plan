# src/planificador/database/repositories/client/client_repository.py

from typing import List, Optional, Dict, Any, Union
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import pendulum
from pendulum import DateTime, Date

from ..base_repository import BaseRepository
from ....models.client import Client
from ....models.project import Project
from ....exceptions import (
    ClientNotFoundError,
    ClientValidationError,
    ClientConflictError,
    ValidationError
)
from ....exceptions.repository import (
    convert_sqlalchemy_error,
    RepositoryError,
    create_client_query_error,
    create_client_statistics_error,
    create_client_validation_repository_error,
    create_client_relationship_error,
    create_client_bulk_operation_error,
    create_client_date_range_error
)
from ....utils.date_utils import (
    get_current_time,
    format_datetime,
    is_business_day,
    calculate_business_days
)

# Importar clases especializadas
from .client_query_builder import ClientQueryBuilder
from .client_validator import ClientValidator
from .client_statistics import ClientStatistics
from .client_relationship_manager import ClientRelationshipManager


class ClientRepository(BaseRepository[Client]):
    """
    Repositorio principal para la gestión de clientes.
    
    Actúa como orquestador de las clases especializadas:
    - ClientQueryBuilder: Constructor de consultas complejas
    - ClientValidator: Validador de datos y reglas de negocio
    - ClientStatistics: Generador de estadísticas y métricas
    - ClientRelationshipManager: Gestor de relaciones con proyectos
    
    Proporciona una interfaz unificada para todas las operaciones
    relacionadas con clientes, manteniendo la compatibilidad con
    la API existente mientras mejora la organización del código.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Client, session)
        
        # Inicializar componentes especializados
        self.query_builder = ClientQueryBuilder(session)
        self.validator = ClientValidator(session)
        self.statistics = ClientStatistics(session)
        self.relationship_manager = ClientRelationshipManager(session)
        
        self._logger = logger.bind(component="ClientRepository")
    
    # ==========================================
    # OPERACIONES CRUD BÁSICAS (4 funciones)
    # ==========================================
    
    async def create_client(self, client_data: Dict[str, Any]) -> Client:
        """
        Crea un nuevo cliente con validaciones.
        
        Args:
            client_data: Datos del cliente
            
        Returns:
            Cliente creado
            
        Raises:
            ClientValidationError: Si hay errores de validación
            ClientValidationRepositoryError: Si hay errores específicos del repositorio
        """
        try:
            # Validar datos del cliente
            await self.validator.validate_client_data(client_data)
            
            # Crear cliente usando el método base
            client = await self.create(client_data)
            
            self._logger.info(f"Cliente creado exitosamente: {client.name} (ID: {client.id})")
            return client
            
        except ClientValidationError:
            # Re-lanzar errores de validación de dominio directamente
            raise
        except ValidationError as e:
            # Convertir ValidationError en ClientValidationRepositoryError específico
            self._logger.error(f"Error de validación creando cliente: {e}")
            raise create_client_validation_repository_error(
                field="validation",
                value=client_data,
                reason=str(e),
                operation="create_client"
            )
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            await self.session.rollback()
            self._logger.error(f"Error de base de datos creando cliente: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_client",
                entity_type="Client"
            )
        except Exception as e:
            # Manejar otros errores como errores generales del repositorio
            await self.session.rollback()
            self._logger.error(f"Error inesperado creando cliente: {e}")
            raise create_client_validation_repository_error(
                field="general",
                value=client_data,
                reason=f"Error inesperado: {str(e)}",
                operation="create_client"
            )
    
    async def update_client(self, client_id: int, update_data: Dict[str, Any]) -> Optional[Client]:
        """
        Actualiza un cliente con validaciones.
        
        Args:
            client_id: ID del cliente
            update_data: Datos a actualizar
            
        Returns:
            Cliente actualizado o None si no existe
            
        Raises:
            ClientNotFoundError: Si el cliente no existe
            ClientValidationError: Si hay errores de validación
            ClientValidationRepositoryError: Si hay errores específicos del repositorio
        """
        try:
            # Primero verificar si el cliente existe
            existing_client = await self.get_by_id(client_id)
            if not existing_client:
                raise ClientNotFoundError(client_id)
            
            # Validar datos de actualización
            await self.validator.validate_client_update_data(update_data, client_id)
            
            # Actualizar cliente usando el método base
            client = await self.update(client_id, update_data)
            
            if client:
                self._logger.info(f"Cliente actualizado exitosamente: {client.name} (ID: {client.id})")
            
            return client
            
        except ClientNotFoundError:
            # Re-lanzar errores de cliente no encontrado directamente
            raise
        except ClientValidationError:
            # Re-lanzar errores de validación de dominio directamente
            raise
        except ValidationError as e:
            # Convertir ValidationError en ClientValidationRepositoryError específico
            self._logger.error(f"Error de validación actualizando cliente {client_id}: {e}")
            raise create_client_validation_repository_error(
                field="validation",
                value={"client_id": client_id, **update_data},
                reason=str(e),
                operation="update_client",
                client_id=client_id
            )
    
    async def create_client_with_pendulum_validation(
        self,
        client_data: Dict[str, Any],
        validate_business_day: bool = False
    ) -> Client:
        """
        Crea un cliente con validaciones avanzadas usando Pendulum.
        
        Args:
            client_data: Datos del cliente
            validate_business_day: Si validar que la creación sea en día laborable
            
        Returns:
            Cliente creado
            
        Raises:
            ClientValidationError: Si hay validaciones fallidas
        """
        try:
            # Obtener timestamp actual con Pendulum
            current_time = get_current_time()
            
            # Validar día laborable si se requiere
            if validate_business_day and not is_business_day(current_time.date()):
                raise ClientValidationError(
                    f"Los clientes solo pueden crearse en días laborables. "
                    f"Hoy es {current_time.format('dddd')}"
                )
            
            # Agregar timestamp de creación con Pendulum
            client_data_with_timestamp = {
                **client_data,
                'created_at': current_time.to_datetime_string(),
                'timezone_created': str(current_time.timezone)
            }
            
            # Crear usando el método existente con validaciones
            client = await self.create_client(client_data_with_timestamp)
            
            self._logger.info(
                f"Cliente creado con validación Pendulum: {format_datetime(current_time)} "
                f"(Zona: {current_time.timezone})"
            )
            
            return client
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            await self.session.rollback()
            self._logger.error(f"Error de base de datos creando cliente con validación Pendulum: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_client_with_pendulum_validation",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error creando cliente con validación Pendulum: {e}")
            if isinstance(e, ClientValidationError):
                raise
            await self.session.rollback()
            raise ClientValidationError(f"Error creando cliente con validación Pendulum: {e}")
    
    # ==========================================
    # CONSULTAS POR IDENTIFICADORES ÚNICOS (2 funciones)
    # ==========================================
    
    async def get_by_name(self, name: str) -> Optional[Client]:
        """
        Busca un cliente por su nombre exacto.
        
        Args:
            name: Nombre del cliente
            
        Returns:
            Cliente encontrado o None
        """
        return await self.query_builder.get_by_name(name)
    
    async def get_by_code(self, code: str) -> Optional[Client]:
        """
        Busca un cliente por su código.
        
        Args:
            code: Código del cliente
            
        Returns:
            Cliente encontrado o None
        """
        return await self.query_builder.get_by_code(code)
    
    # ==========================================
    # CONSULTAS POR ATRIBUTOS (7 funciones)
    # ==========================================
    
    async def search_by_name(self, search_term: str) -> List[Client]:
        """
        Busca clientes cuyo nombre contenga el término de búsqueda.
        
        Args:
            search_term: Término a buscar en el nombre
            
        Returns:
            Lista de clientes que coinciden
            
        Raises:
            ClientQueryError: Si hay errores en la consulta
        """
        try:
            return await self.query_builder.search_by_name(search_term)
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos buscando clientes por nombre '{search_term}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_by_name",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando clientes por nombre '{search_term}': {e}")
            raise create_client_query_error(
                query_type="search_by_name",
                parameters={"search_term": search_term},
                reason=str(e)
            )
    
    async def get_active_clients(self) -> List[Client]:
        """
        Obtiene todos los clientes activos.
        
        Returns:
            Lista de clientes activos
        """
        return await self.query_builder.get_active_clients()
    
    async def get_with_projects(self, client_id: int) -> Optional[Client]:
        """
        Obtiene un cliente con todos sus proyectos cargados.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Cliente con proyectos cargados o None
            
        Raises:
            ClientRelationshipError: Si hay errores cargando las relaciones
        """
        try:
            return await self.query_builder.get_with_projects(client_id)
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos cargando cliente {client_id} con proyectos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_projects",
                entity_type="Client",
                entity_id=client_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado cargando cliente {client_id} con proyectos: {e}")
            raise create_client_relationship_error(
                relationship_type="projects",
                client_id=client_id,
                related_entity_type="Project",
                reason=str(e)
            )
    
    async def get_client_relationship_duration(
        self,
        client_id: int
    ) -> Dict[str, Any]:
        """
        Calcula la duración de la relación con un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con estadísticas de duración de relación
        """
        try:
            client = await self.get_by_id(client_id)
            if not client or not client.created_at:
                return {
                    'client_found': False,
                    'has_creation_date': False,
                    'relationship_days': 0,
                    'relationship_business_days': 0,
                    'relationship_years': 0.0,
                    'created_at': None
                }
            
            # Convertir fecha de creación a date si es necesario
            created_date = client.created_at.date() if hasattr(client.created_at, 'date') else client.created_at
            current_date = get_current_time().date()
            
            # Calcular duración de relación
            relationship_days = (current_date - created_date).days
            relationship_business_days = get_business_days(created_date, current_date)
            relationship_years = relationship_days / 365.25
            
            # Determinar si fue creado en día laborable
            created_on_business_day = is_business_day(created_date)
            
            stats = {
                'client_found': True,
                'has_creation_date': True,
                'client_name': client.name,
                'client_code': client.code,
                'created_at': created_date.isoformat(),
                'current_date': current_date.isoformat(),
                'relationship_days': relationship_days,
                'relationship_business_days': relationship_business_days,
                'relationship_years': round(relationship_years, 2),
                'relationship_months': round(relationship_years * 12, 1),
                'created_on_business_day': created_on_business_day,
                'is_active': client.is_active
            }
            
            self._logger.debug(f"Estadísticas de relación calculadas para cliente {client_id}")
            return stats
            
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos calculando duración de relación - Cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="calculate_relationship_duration",
                entity_type="Client",
                entity_id=client_id
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado calculando duración de relación - Cliente {client_id}: {e}")
            raise
    
    async def get_clients_with_contact_info(self, include_inactive: bool = False) -> List[Client]:
        """
        Obtiene clientes que tienen información de contacto.
        Utiliza la propiedad has_contact_info del modelo.
        
        Args:
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            Lista de clientes con información de contacto
        """
        try:
            return await self.query_builder.find_clients_with_contact_info(include_inactive)
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo clientes con información de contacto: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_with_contact_info",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes con información de contacto: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado obteniendo clientes con información de contacto: {e}",
                operation="get_clients_with_contact_info",
                entity_type="Client",
                original_error=e
            )
    
    async def get_clients_without_contact_info(self, include_inactive: bool = False) -> List[Client]:
        """
        Obtiene clientes que NO tienen información de contacto.
        Útil para identificar clientes que necesitan actualización de datos.
        
        Args:
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            Lista de clientes sin información de contacto
        """
        try:
            return await self.query_builder.find_clients_without_contact_info(include_inactive)
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo clientes sin información de contacto: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_without_contact_info",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes sin información de contacto: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado obteniendo clientes sin información de contacto: {e}",
                operation="get_clients_without_contact_info",
                entity_type="Client",
                original_error=e
            )
    
    async def get_clients_display_summary(self, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de clientes con información formateada para mostrar.
        Utiliza las propiedades display_name, status_display y contact_summary del modelo.
        
        Args:
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            Lista de diccionarios con información formateada de clientes
        """
        try:
            clients = await self.get_all()
            if not include_inactive:
                clients = [client for client in clients if client.is_active]
            
            summary_data = []
            for client in clients:
                client_summary = {
                    'id': client.id,
                    'display_name': client.display_name,
                    'status_display': client.status_display,
                    'has_contact_info': client.has_contact_info,
                    'contact_summary': client.contact_summary,
                    'created_at': client.created_at,
                    'updated_at': client.updated_at
                }
                summary_data.append(client_summary)
            
            self._logger.debug(f"Generado resumen para {len(summary_data)} clientes")
            return summary_data
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo resumen de clientes: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_display_summary",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo resumen de clientes: {e}")
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado obteniendo resumen de clientes: {e}",
                operation="get_clients_display_summary",
                entity_type="Client",
                original_error=e
            )
    
    # ==========================================
    # CONSULTAS TEMPORALES (3 funciones)
    # ==========================================
    
    async def get_clients_created_current_week(self, **kwargs) -> List[Client]:
        """
        Obtiene clientes creados en la semana actual.
        
        Args:
            **kwargs: Criterios adicionales de filtrado
            
        Returns:
            Lista de clientes creados esta semana
        """
        return await self.query_builder.find_clients_created_current_week(**kwargs)
    
    async def get_clients_created_current_month(self, **kwargs) -> List[Client]:
        """
        Obtiene clientes creados en el mes actual.
        
        Args:
            **kwargs: Criterios adicionales de filtrado
            
        Returns:
            Lista de clientes creados este mes
        """
        return await self.query_builder.find_clients_created_current_month(**kwargs)
    
    async def get_clients_created_business_days_only(
        self, 
        start_date: Union[date, str, None] = None,
        end_date: Union[date, str, None] = None,
        **kwargs
    ) -> List[Client]:
        """
        Obtiene clientes creados solo en días laborables.
        
        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            **kwargs: Criterios adicionales
            
        Returns:
            Lista de clientes creados en días laborables
            
        Raises:
            ClientDateRangeError: Si hay errores con el rango de fechas
        """
        try:
            return await self.query_builder.find_clients_created_business_days_only(
                start_date, end_date, **kwargs
            )
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo clientes por días laborables: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_created_business_days_only",
                entity_type="Client"
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(f"Error inesperado obteniendo clientes por días laborables: {e}")
            # Convertir fechas a datetime para la excepción
            from datetime import datetime
            default_start = datetime.now().replace(day=1)  # Primer día del mes actual
            default_end = datetime.now()  # Fecha actual
            
            raise create_client_date_range_error(
                start_date=start_date if isinstance(start_date, datetime) else default_start,
                end_date=end_date if isinstance(end_date, datetime) else default_end,
                operation="get_clients_created_business_days_only",
                reason=str(e)
            )
    
    # ==========================================
    # VALIDACIONES DE UNICIDAD (2 funciones)
    # ==========================================
    
    async def name_exists(self, name: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si ya existe un cliente con el nombre especificado.
        
        Args:
            name: Nombre a verificar
            exclude_id: ID a excluir de la verificación (para actualizaciones)
            
        Returns:
            True si el nombre ya existe
        """
        return await self.query_builder.name_exists(name, exclude_id)
    
    async def code_exists(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica si ya existe un cliente con el código especificado.
        
        Args:
            code: Código a verificar
            exclude_id: ID a excluir de la verificación (para actualizaciones)
            
        Returns:
            True si el código ya existe
        """
        return await self.query_builder.code_exists(code, exclude_id)
    
    # ==========================================
    # ESTADÍSTICAS Y MÉTRICAS (8 funciones)
    # ==========================================
    
    async def get_client_stats(self, client_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con estadísticas del cliente
            
        Raises:
            ClientNotFoundError: Si el cliente no existe
            ClientStatisticsError: Si hay errores calculando estadísticas
        """
        try:
            return await self.statistics.get_client_stats(client_id)
        except ClientNotFoundError:
            # Re-lanzar errores de cliente no encontrado directamente
            raise
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo estadísticas del cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_statistics",
                entity_type="Client",
                entity_id=client_id
            )
        except Exception as e:
            # Convertir otros errores en ClientStatisticsError específico
            self._logger.error(f"Error inesperado obteniendo estadísticas del cliente {client_id}: {e}")
            raise create_client_statistics_error(
                statistic_type="get_client_stats",
                parameters={"client_id": client_id},
                reason=str(e)
            )
    
    async def get_clients_by_relationship_duration(
        self,
        min_years: float = 0.0,
        max_years: Optional[float] = None,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene clientes por duración de relación.
        
        Args:
            min_years: Duración mínima de relación en años
            max_years: Duración máxima de relación en años (opcional)
            is_active: Estado del cliente (opcional)
            
        Returns:
            Lista de clientes con información de duración de relación
        """
        return await self.statistics.get_clients_by_relationship_duration(
            min_years, max_years, is_active
        )
    
    async def get_client_counts_by_status(self) -> Dict[str, int]:
        """
        Obtiene el conteo de clientes por estado.
        
        Returns:
            Diccionario con el conteo por estado
        """
        return await self.statistics.get_client_counts_by_status()
    
    async def get_client_creation_trends(
        self, 
        days: int = 30,
        group_by: str = 'day'
    ) -> List[Dict[str, Any]]:
        """
        Obtiene tendencias de creación de clientes.
        
        Args:
            days: Número de días hacia atrás
            group_by: Agrupación ('day', 'week', 'month')
            
        Returns:
            Lista con tendencias de creación
            
        Raises:
            ClientStatisticsError: Si hay errores en el cálculo de estadísticas
        """
        try:
            return await self.statistics.get_client_creation_trends(days, group_by)
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo tendencias de creación de clientes: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_creation_trends",
                entity_type="Client"
            )
        except Exception as e:
            # Convertir errores en ClientStatisticsError específico
            self._logger.error(f"Error obteniendo tendencias de creación de clientes: {e}")
            raise create_client_statistics_error(
                statistic_type="get_client_creation_trends",
                parameters={
                    "days": days,
                    "group_by": group_by
                },
                reason=str(e)
            )
    
    async def get_clients_by_project_count(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene clientes ordenados por número de proyectos.
        
        Args:
            limit: Número máximo de clientes a retornar
            
        Returns:
            Lista de clientes con conteo de proyectos
        """
        return await self.statistics.get_clients_by_project_count(limit)
    
    async def get_client_activity_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de actividad de clientes.
        
        Returns:
            Diccionario con resumen de actividad
        """
        return await self.statistics.get_client_activity_summary()
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento del sistema de clientes.
        
        Returns:
            Diccionario con métricas de rendimiento
            
        Raises:
            ClientStatisticsError: Si hay errores en el cálculo de métricas
        """
        try:
            return await self.statistics.get_performance_metrics()
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos obteniendo métricas de rendimiento: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_performance_metrics",
                entity_type="Client"
            )
        except Exception as e:
            # Convertir errores en ClientStatisticsError específico
            self._logger.error(f"Error obteniendo métricas de rendimiento: {e}")
            raise create_client_statistics_error(
                statistic_type="get_performance_metrics",
                parameters={"metric_type": "performance"},
                reason=str(e)
            )
    
    async def get_contact_info_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre información de contacto de clientes.
        Utiliza las propiedades del modelo Client para generar métricas detalladas.
        
        Returns:
            Diccionario con estadísticas de información de contacto
        """
        return await self.statistics.get_contact_info_statistics()
    
    # ==========================================
    # GESTIÓN DE RELACIONES CON PROYECTOS (4 funciones)
    # ==========================================
    
    async def get_client_projects(
        self,
        client_id: int,
        status_filter: Optional[List[str]] = None,
        include_inactive: bool = False,
        load_details: bool = False
    ) -> List[Project]:
        """
        Obtiene todos los proyectos de un cliente.
        
        Args:
            client_id: ID del cliente
            status_filter: Lista de estados de proyecto a filtrar (opcional)
            include_inactive: Si incluir proyectos inactivos
            load_details: Si cargar detalles completos del proyecto
            
        Returns:
            Lista de proyectos del cliente
        """
        return await self.relationship_manager.get_client_projects(
            client_id, status_filter, include_inactive, load_details
        )
    
    async def get_client_project_summary(self, client_id: int) -> Dict[str, Any]:
        """
        Obtiene un resumen de proyectos de un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con resumen de proyectos
        """
        return await self.relationship_manager.get_client_project_summary(client_id)
    
    async def transfer_projects_to_client(
        self,
        source_client_id: int,
        target_client_id: int,
        project_ids: Optional[List[int]] = None,
        validate_transfer: bool = True
    ) -> Dict[str, Any]:
        """
        Transfiere proyectos de un cliente a otro.
        
        Args:
            source_client_id: ID del cliente origen
            target_client_id: ID del cliente destino
            project_ids: IDs específicos de proyectos a transferir (opcional)
            validate_transfer: Si validar la transferencia
            
        Returns:
            Diccionario con resultado de la transferencia
            
        Raises:
            ClientNotFoundError: Si alguno de los clientes no existe
            ClientBulkOperationError: Si hay errores en la operación bulk
        """
        try:
            return await self.relationship_manager.transfer_projects_to_client(
                source_client_id, target_client_id, project_ids, validate_transfer
            )
        except ClientNotFoundError:
            # Re-lanzar errores de cliente no encontrado directamente
            raise
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            await self.session.rollback()
            self._logger.error(f"Error de base de datos transfiriendo proyectos de cliente {source_client_id} a {target_client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="transfer_projects_to_client",
                entity_type="Client",
                entity_id=f"{source_client_id}->{target_client_id}"
            )
        except Exception as e:
            # Convertir otros errores en ClientBulkOperationError específico
            await self.session.rollback()
            self._logger.error(f"Error transfiriendo proyectos de cliente {source_client_id} a {target_client_id}: {e}")
            raise create_client_bulk_operation_error(
                operation_type="transfer_projects_to_client",
                total_items=len(project_ids) if project_ids else 1,
                failed_items=[{
                    "source_client_id": source_client_id,
                    "target_client_id": target_client_id,
                    "project_ids": project_ids,
                    "error": str(e)
                }],
                reason=f"Error transfiriendo proyectos: {str(e)}"
            )
    
    async def validate_client_project_integrity(self, client_id: int) -> Dict[str, Any]:
        """
        Valida la integridad de las relaciones cliente-proyecto.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con resultado de la validación
            
        Raises:
            ClientNotFoundError: Si el cliente no existe
            ClientValidationRepositoryError: Si hay errores en la validación
        """
        try:
            return await self.relationship_manager.validate_client_project_integrity(client_id)
        except ClientNotFoundError:
            # Re-lanzar errores de cliente no encontrado directamente
            raise
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(f"Error de base de datos validando integridad del cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_client_project_integrity",
                entity_type="Client",
                entity_id=str(client_id)
            )
        except Exception as e:
            # Convertir otros errores en ClientValidationRepositoryError específico
            self._logger.error(f"Error validando integridad del cliente {client_id}: {e}")
            raise create_client_validation_repository_error(
                field="project_integrity",
                value={"client_id": client_id},
                reason=str(e),
                operation="validate_client_project_integrity",
                client_id=client_id
            )
    
