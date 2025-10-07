# Patrón de Servicios de Dominio con Facade e Interfaz

## Descripción General

Este documento describe el patrón arquitectónico utilizado para implementar servicios de dominio en el sistema, basado en el patrón Facade con interfaces modulares. Este enfoque proporciona una arquitectura escalable, mantenible y testeable para la lógica de negocio compleja.

El patrón combina:
- **Patrón Facade**: Proporciona una interfaz unificada para un conjunto complejo de operaciones
- **Segregación de Interfaces**: Divide las responsabilidades en interfaces específicas
- **Composición Modular**: Implementa cada conjunto de operaciones en módulos independientes
- **Inyección de Dependencias**: Facilita testing y desacoplamiento

---

## Estructura Básica del Servicio de Dominio

### 1. Arquitectura de Directorios

```
domain_service/
├── __init__.py
├── entity_domain_service.py          # Servicio principal (Facade)
├── interfaces/                       # Definición de contratos
│   ├── __init__.py
│   ├── entity_domain_interface.py    # Interfaz principal unificada
│   ├── crud_operations_interface.py  # Operaciones CRUD
│   ├── query_operations_interface.py # Consultas básicas
│   ├── advanced_query_operations_interface.py # Consultas avanzadas
│   ├── validation_operations_interface.py     # Validaciones
│   ├── statistics_operations_interface.py     # Estadísticas
│   ├── relationship_operations_interface.py   # Relaciones
│   ├── date_planning_operations_interface.py  # Planificación temporal
│   └── diagnostic_operations_interface.py     # Diagnósticos
└── modules/                          # Implementaciones modulares
    ├── crud_operations.py            # Implementación CRUD
    ├── query_operations.py           # Implementación consultas
    ├── advanced_query_operations.py  # Implementación consultas avanzadas
    ├── validation_operations.py      # Implementación validaciones
    ├── statistics_operations.py      # Implementación estadísticas
    ├── relationship_operations.py    # Implementación relaciones
    ├── date_planning_operations.py   # Implementación planificación
    └── diagnostic_operations.py      # Implementación diagnósticos
```

### 2. Principios de Diseño

#### Separación de Responsabilidades
- **CRUD Operations**: Operaciones básicas de creación, lectura, actualización y eliminación
- **Query Operations**: Consultas simples y filtros básicos
- **Advanced Query Operations**: Búsquedas complejas, análisis y reportes
- **Validation Operations**: Reglas de negocio y validaciones de integridad
- **Statistics Operations**: Métricas, conteos y análisis estadísticos
- **Relationship Operations**: Gestión de relaciones entre entidades
- **Date Planning Operations**: Operaciones temporales y planificación
- **Diagnostic Operations**: Monitoreo, salud del sistema y diagnósticos

#### Cohesión y Bajo Acoplamiento
- Cada módulo tiene una responsabilidad específica y bien definida
- Las dependencias se inyectan a través del constructor
- Las interfaces definen contratos claros entre componentes

---

## Definición de la Interfaz Principal

### 1. Interfaz Unificada (Facade Interface)

```python
# interfaces/entity_domain_interface.py
"""
Interfaz principal para el servicio de dominio de entidades.

Esta interfaz define el contrato completo para todas las operaciones
relacionadas con la gestión de entidades en el sistema.
Hereda de todas las interfaces específicas para mantener compatibilidad
y proporcionar una interfaz unificada.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple

# Importar esquemas específicos de la entidad
from planificador.schemas.entity.create import EntityCreateSchema
from planificador.schemas.entity.update import EntityUpdateSchema
from planificador.schemas.entity.response import EntityResponseSchema
from planificador.schemas.entity.query import EntityQuerySchema
from planificador.schemas.entity.statistics import EntityStatisticsSchema
from planificador.schemas.entity.validation import EntityValidationResult
from planificador.schemas.entity.diagnostic import EntityHealthReport

# Importar todas las interfaces específicas
from .crud_operations_interface import IEntityCrudOperations
from .query_operations_interface import IEntityQueryOperations
from .advanced_query_operations_interface import IEntityAdvancedQueryOperations
from .validation_operations_interface import IEntityValidationOperations
from .statistics_operations_interface import IEntityStatisticsOperations
from .relationship_operations_interface import IEntityRelationshipOperations
from .date_planning_operations_interface import IEntityDatePlanningOperations
from .diagnostic_operations_interface import IEntityDiagnosticOperations


class IEntityDomainService(
    IEntityCrudOperations,
    IEntityQueryOperations,
    IEntityAdvancedQueryOperations,
    IEntityValidationOperations,
    IEntityStatisticsOperations,
    IEntityRelationshipOperations,
    IEntityDatePlanningOperations,
    IEntityDiagnosticOperations,
    ABC
):
    """
    Interfaz principal del servicio de dominio de entidades.
    
    Combina todas las interfaces específicas en una interfaz unificada
    que define el contrato completo para la gestión de entidades.
    
    Esta interfaz actúa como Facade, proporcionando un punto de acceso
    único para todas las operaciones relacionadas con entidades.
    """
    
    @abstractmethod
    async def service_health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de salud general del servicio.
        
        Returns:
            Dict[str, Any]: Información del estado del servicio
        """
        pass
    
    @abstractmethod
    async def get_service_configuration(self) -> Dict[str, Any]:
        """
        Obtiene la configuración actual del servicio.
        
        Returns:
            Dict[str, Any]: Configuración del servicio
        """
        pass
```

### 2. Interfaces Específicas por Responsabilidad

#### Interfaz CRUD Operations

```python
# interfaces/crud_operations_interface.py
"""
Interfaz para las operaciones CRUD de entidades.

Esta interfaz define el contrato para todas las operaciones básicas de creación,
lectura, actualización y eliminación de entidades.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from planificador.schemas.entity.create import EntityCreateSchema
from planificador.schemas.entity.update import EntityUpdateSchema
from planificador.schemas.entity.response import EntityResponseSchema


class IEntityCrudOperations(ABC):
    """
    Interfaz abstracta para las operaciones CRUD de entidades.
    
    Define el contrato para todas las operaciones básicas de gestión de entidades
    incluyendo creación, lectura, actualización, eliminación, archivado y restauración.
    """

    # ==========================================
    # OPERACIONES DE CREACIÓN
    # ==========================================

    @abstractmethod
    async def create_entity(self, entity_data: EntityCreateSchema) -> EntityResponseSchema:
        """
        Crea una nueva entidad en el sistema.
        
        Args:
            entity_data: Datos de la entidad a crear
            
        Returns:
            EntityResponseSchema: La entidad creada con todos sus datos
            
        Raises:
            ValidationError: Si los datos de la entidad no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def bulk_create_entities(
        self, 
        entities_data: List[EntityCreateSchema]
    ) -> List[EntityResponseSchema]:
        """
        Crea múltiples entidades en una operación transaccional.
        
        Args:
            entities_data: Lista de datos de entidades a crear
            
        Returns:
            List[EntityResponseSchema]: Lista de entidades creadas
        """
        pass

    # ==========================================
    # OPERACIONES DE LECTURA
    # ==========================================

    @abstractmethod
    async def get_entity_by_id(self, entity_id: UUID) -> Optional[EntityResponseSchema]:
        """
        Obtiene una entidad por su ID único.
        
        Args:
            entity_id: ID único de la entidad
            
        Returns:
            Optional[EntityResponseSchema]: La entidad encontrada o None
        """
        pass

    @abstractmethod
    async def get_all_entities(
        self, 
        include_archived: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[EntityResponseSchema]:
        """
        Obtiene todas las entidades del sistema.
        
        Args:
            include_archived: Si incluir entidades archivadas
            limit: Límite de resultados
            offset: Desplazamiento para paginación
            
        Returns:
            List[EntityResponseSchema]: Lista de entidades
        """
        pass

    # ==========================================
    # OPERACIONES DE ACTUALIZACIÓN
    # ==========================================

    @abstractmethod
    async def update_entity(
        self, 
        entity_id: UUID, 
        entity_data: EntityUpdateSchema
    ) -> Optional[EntityResponseSchema]:
        """
        Actualiza una entidad existente.
        
        Args:
            entity_id: ID de la entidad a actualizar
            entity_data: Nuevos datos de la entidad
            
        Returns:
            Optional[EntityResponseSchema]: La entidad actualizada o None
        """
        pass

    # ==========================================
    # OPERACIONES DE ELIMINACIÓN
    # ==========================================

    @abstractmethod
    async def delete_entity(self, entity_id: UUID) -> bool:
        """
        Elimina permanentemente una entidad del sistema.
        
        Args:
            entity_id: ID de la entidad a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        pass

    @abstractmethod
    async def archive_entity(self, entity_id: UUID) -> Optional[EntityResponseSchema]:
        """
        Archiva una entidad (eliminación lógica).
        
        Args:
            entity_id: ID de la entidad a archivar
            
        Returns:
            Optional[EntityResponseSchema]: La entidad archivada o None
        """
        pass

    @abstractmethod
    async def restore_entity(self, entity_id: UUID) -> Optional[EntityResponseSchema]:
        """
        Restaura una entidad archivada.
        
        Args:
            entity_id: ID de la entidad a restaurar
            
        Returns:
            Optional[EntityResponseSchema]: La entidad restaurada o None
        """
        pass
```

---

## Implementación del Patrón Facade

### 1. Servicio Principal (Facade)

```python
# entity_domain_service.py
"""
Servicio de dominio para la gestión de entidades.

Este módulo proporciona la lógica de negocio para operaciones relacionadas con entidades,
incluyendo CRUD, consultas, validaciones, estadísticas y diagnósticos.
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from loguru import logger
from pendulum import DateTime

from planificador.repositories.entity.entity_repository_facade import EntityRepositoryFacade
from planificador.schemas.entity.create import EntityCreateSchema
from planificador.schemas.entity.update import EntityUpdateSchema
from planificador.schemas.entity.response import EntityResponseSchema
from planificador.schemas.entity.query import EntityQuerySchema
from planificador.schemas.entity.statistics import EntityStatisticsSchema
from planificador.schemas.entity.validation import EntityValidationResult
from planificador.schemas.entity.diagnostic import EntityHealthReport

from .interfaces.entity_domain_interface import IEntityDomainService
from .modules.crud_operations import EntityCrudOperations
from .modules.query_operations import EntityQueryOperations
from .modules.advanced_query_operations import EntityAdvancedQueryOperations
from .modules.validation_operations import EntityValidationOperations
from .modules.statistics_operations import EntityStatisticsOperations
from .modules.relationship_operations import EntityRelationshipOperations
from .modules.date_planning_operations import EntityDatePlanningOperations
from .modules.diagnostic_operations import EntityDiagnosticOperations


class EntityDomainService(IEntityDomainService):
    """
    Servicio de dominio principal para entidades.
    
    Implementa el patrón Facade proporcionando una interfaz unificada
    para todas las operaciones relacionadas con entidades. Coordina
    las operaciones entre múltiples módulos especializados.
    
    Características:
    - Composición modular de operaciones especializadas
    - Manejo centralizado de transacciones y errores
    - Logging estructurado y trazabilidad completa
    - Validaciones de negocio integradas
    - Gestión de dependencias por inyección
    """

    def __init__(self, repository_facade: EntityRepositoryFacade):
        """
        Inicializa el servicio de dominio con todas sus dependencias.
        
        Args:
            repository_facade: Facade del repositorio de entidades
        """
        self.repository = repository_facade
        self._logger = logger.bind(module="entity_domain_service")
        
        # Inicializar módulos especializados
        self._crud_ops = EntityCrudOperations(repository_facade)
        self._query_ops = EntityQueryOperations(repository_facade)
        self._advanced_query_ops = EntityAdvancedQueryOperations(repository_facade)
        self._validation_ops = EntityValidationOperations(repository_facade)
        self._statistics_ops = EntityStatisticsOperations(repository_facade)
        self._relationship_ops = EntityRelationshipOperations(repository_facade)
        self._date_planning_ops = EntityDatePlanningOperations(repository_facade)
        self._diagnostic_ops = EntityDiagnosticOperations(repository_facade)
        
        self._logger.info("Servicio de dominio de entidades inicializado correctamente")

    # ==========================================
    # OPERACIONES CRUD (Delegación a módulo CRUD)
    # ==========================================

    async def create_entity(self, entity_data: EntityCreateSchema) -> EntityResponseSchema:
        """Crea una nueva entidad con validaciones completas de negocio."""
        return await self._crud_ops.create_entity(entity_data)

    async def bulk_create_entities(
        self, 
        entities_data: List[EntityCreateSchema]
    ) -> List[EntityResponseSchema]:
        """Crea múltiples entidades en una operación transaccional."""
        return await self._crud_ops.bulk_create_entities(entities_data)

    async def get_entity_by_id(self, entity_id: UUID) -> Optional[EntityResponseSchema]:
        """Obtiene una entidad por su ID único."""
        return await self._crud_ops.get_entity_by_id(entity_id)

    async def update_entity(
        self, 
        entity_id: UUID, 
        entity_data: EntityUpdateSchema
    ) -> Optional[EntityResponseSchema]:
        """Actualiza una entidad existente con validaciones."""
        return await self._crud_ops.update_entity(entity_id, entity_data)

    async def delete_entity(self, entity_id: UUID) -> bool:
        """Elimina una entidad después de validar dependencias."""
        return await self._crud_ops.delete_entity(entity_id)

    # ==========================================
    # OPERACIONES DE CONSULTA (Delegación a módulo Query)
    # ==========================================

    async def search_entities(
        self,
        filters: Optional[EntityQuerySchema] = None,
        pagination: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[EntityResponseSchema], int]:
        """Busca entidades con filtros y paginación."""
        return await self._query_ops.search_entities(filters, pagination)

    # ==========================================
    # OPERACIONES DE VALIDACIÓN (Delegación a módulo Validation)
    # ==========================================

    async def validate_entity_creation(
        self,
        entity_data: EntityCreateSchema
    ) -> EntityValidationResult:
        """Valida los datos para creación de entidad."""
        return await self._validation_ops.validate_entity_creation(entity_data)

    # ==========================================
    # OPERACIONES DE ESTADÍSTICAS (Delegación a módulo Statistics)
    # ==========================================

    async def get_entity_statistics(self) -> EntityStatisticsSchema:
        """Obtiene estadísticas generales de entidades."""
        return await self._statistics_ops.get_entity_statistics()

    # ==========================================
    # OPERACIONES DE DIAGNÓSTICO (Delegación a módulo Diagnostic)
    # ==========================================

    async def service_health_check(self) -> Dict[str, Any]:
        """Verifica el estado de salud del servicio."""
        return await self._diagnostic_ops.service_health_check()

    async def get_service_configuration(self) -> Dict[str, Any]:
        """Obtiene la configuración del servicio."""
        return await self._diagnostic_ops.get_service_configuration()
```

### 2. Implementación de Módulos Especializados

#### Módulo CRUD Operations

```python
# modules/crud_operations.py
"""
Módulo de Operaciones CRUD para Entidades

Implementa las operaciones básicas de creación, lectura, actualización y eliminación
de entidades con validaciones de negocio y manejo robusto de errores.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from loguru import logger

from planificador.schemas.entity.create import EntityCreateSchema
from planificador.schemas.entity.update import EntityUpdateSchema
from planificador.schemas.entity.response import EntityResponseSchema
from planificador.repositories.entity.entity_repository_facade import EntityRepositoryFacade
from planificador.exceptions.domain.entity_domain_exceptions import (
    EntityValidationError,
    EntityNotFoundError,
    EntityBusinessRuleViolationError,
    create_entity_validation_error,
    create_entity_business_rule_error
)


class EntityCrudOperations:
    """
    Operaciones CRUD especializadas para entidades.
    
    Maneja las operaciones básicas de creación, lectura, actualización y eliminación
    de entidades con validaciones completas de negocio y transformación de datos.
    """

    def __init__(self, repository_facade: EntityRepositoryFacade):
        """
        Inicializa las operaciones CRUD.
        
        Args:
            repository_facade: Facade del repositorio de entidades
        """
        self.repository = repository_facade
        self._logger = logger.bind(module="entity_crud_operations")

    async def create_entity(self, entity_data: EntityCreateSchema) -> EntityResponseSchema:
        """
        Crea una nueva entidad con validaciones completas de negocio.
        
        Args:
            entity_data: Datos de la entidad a crear
            
        Returns:
            EntityResponseSchema: Entidad creada con información completa
            
        Raises:
            EntityValidationError: Si los datos no son válidos
            EntityBusinessRuleViolationError: Si viola reglas de negocio
        """
        self._logger.info(f"Iniciando creación de entidad: {entity_data.name}")
        
        try:
            # Validar datos de entrada
            await self._validate_create_data(entity_data)
            
            # Verificar duplicados
            await self._check_duplicates_for_create(entity_data)
            
            # Validar reglas de negocio específicas
            await self._validate_business_rules_for_create(entity_data)
            
            # Transformar datos para persistencia
            transformed_data = await self._transform_data_for_create(entity_data)
            
            # Crear entidad en repositorio
            created_entity = await self.repository.create_entity(transformed_data)
            
            self._logger.info(f"Entidad creada exitosamente: {created_entity.id}")
            return created_entity
            
        except Exception as e:
            self._logger.error(f"Error creando entidad: {e}")
            raise

    async def get_entity_by_id(self, entity_id: UUID) -> Optional[EntityResponseSchema]:
        """
        Obtiene una entidad por su ID único.
        
        Args:
            entity_id: ID único de la entidad
            
        Returns:
            Optional[EntityResponseSchema]: La entidad encontrada o None
        """
        self._logger.debug(f"Buscando entidad por ID: {entity_id}")
        
        try:
            entity = await self.repository.get_entity_by_id(entity_id)
            
            if entity:
                self._logger.debug(f"Entidad encontrada: {entity_id}")
            else:
                self._logger.debug(f"Entidad no encontrada: {entity_id}")
                
            return entity
            
        except Exception as e:
            self._logger.error(f"Error obteniendo entidad {entity_id}: {e}")
            raise

    # ==========================================
    # MÉTODOS PRIVADOS DE VALIDACIÓN
    # ==========================================

    async def _validate_create_data(self, entity_data: EntityCreateSchema) -> None:
        """Valida los datos básicos para creación."""
        if not entity_data.name or not entity_data.name.strip():
            raise create_entity_validation_error(
                "El nombre de la entidad es obligatorio",
                {"field": "name", "value": entity_data.name}
            )

    async def _check_duplicates_for_create(self, entity_data: EntityCreateSchema) -> None:
        """Verifica duplicados antes de crear."""
        existing = await self.repository.get_entity_by_name(entity_data.name)
        if existing:
            raise create_entity_business_rule_error(
                f"Ya existe una entidad con el nombre: {entity_data.name}",
                {"duplicate_field": "name", "existing_id": existing.id}
            )

    async def _validate_business_rules_for_create(self, entity_data: EntityCreateSchema) -> None:
        """Valida reglas de negocio específicas."""
        # Implementar validaciones específicas del dominio
        pass

    async def _transform_data_for_create(self, entity_data: EntityCreateSchema) -> Dict[str, Any]:
        """Transforma los datos para persistencia."""
        return {
            "name": entity_data.name.strip(),
            "description": entity_data.description.strip() if entity_data.description else None,
            "status": entity_data.status or "active",
            "created_at": DateTime.now(),
            "updated_at": DateTime.now()
        }
```

---

## Ejemplos de Métodos Esenciales

### 1. Operaciones CRUD Completas

```python
# Ejemplo de operaciones CRUD con validaciones completas
class EntityCrudOperations:
    
    async def create_entity_with_validation(
        self,
        entity_data: EntityCreateSchema,
        validate_business_rules: bool = True
    ) -> EntityResponseSchema:
        """
        Crea una entidad con validaciones opcionales de reglas de negocio.
        
        Args:
            entity_data: Datos de la entidad
            validate_business_rules: Si aplicar validaciones de negocio
            
        Returns:
            EntityResponseSchema: Entidad creada
        """
        # Validaciones básicas siempre aplicadas
        await self._validate_basic_data(entity_data)
        
        # Validaciones de negocio opcionales
        if validate_business_rules:
            await self._validate_business_rules(entity_data)
        
        # Crear entidad
        return await self.repository.create_entity(entity_data)

    async def update_entity_with_history(
        self,
        entity_id: UUID,
        entity_data: EntityUpdateSchema,
        track_changes: bool = True
    ) -> EntityResponseSchema:
        """
        Actualiza una entidad manteniendo historial de cambios.
        
        Args:
            entity_id: ID de la entidad
            entity_data: Nuevos datos
            track_changes: Si mantener historial
            
        Returns:
            EntityResponseSchema: Entidad actualizada
        """
        # Obtener entidad actual
        current_entity = await self.repository.get_entity_by_id(entity_id)
        if not current_entity:
            raise EntityNotFoundError(f"Entidad no encontrada: {entity_id}")
        
        # Registrar cambios si es necesario
        if track_changes:
            await self._track_entity_changes(current_entity, entity_data)
        
        # Actualizar entidad
        return await self.repository.update_entity(entity_id, entity_data)
```

### 2. Consultas Avanzadas con Filtros

```python
# Ejemplo de consultas avanzadas
class EntityAdvancedQueryOperations:
    
    async def search_entities_with_complex_criteria(
        self,
        criteria: EntityAdvancedSearchCriteria
    ) -> Tuple[List[EntityResponseSchema], int]:
        """
        Búsqueda avanzada con criterios complejos.
        
        Args:
            criteria: Criterios de búsqueda avanzada
            
        Returns:
            Tuple[List[EntityResponseSchema], int]: Entidades y total
        """
        # Construir filtros dinámicos
        filters = await self._build_dynamic_filters(criteria)
        
        # Aplicar ordenamiento
        sorting = await self._build_sorting_criteria(criteria.sort_options)
        
        # Ejecutar búsqueda
        entities, total = await self.repository.search_entities_advanced(
            filters=filters,
            sorting=sorting,
            pagination=criteria.pagination
        )
        
        return entities, total

    async def get_entities_dashboard_data(self) -> EntityDashboardData:
        """
        Obtiene datos completos para dashboard.
        
        Returns:
            EntityDashboardData: Datos del dashboard
        """
        # Obtener métricas en paralelo
        total_count = await self.repository.get_total_entities_count()
        active_count = await self.repository.get_active_entities_count()
        recent_entities = await self.repository.get_recent_entities(limit=10)
        status_distribution = await self.repository.get_entities_by_status_count()
        
        return EntityDashboardData(
            total_entities=total_count,
            active_entities=active_count,
            recent_entities=recent_entities,
            status_distribution=status_distribution
        )
```

### 3. Validaciones de Negocio

```python
# Ejemplo de validaciones complejas
class EntityValidationOperations:
    
    async def validate_entity_business_rules(
        self,
        entity_data: Dict[str, Any],
        exclude_id: Optional[UUID] = None
    ) -> EntityValidationResult:
        """
        Valida todas las reglas de negocio para una entidad.
        
        Args:
            entity_data: Datos de la entidad
            exclude_id: ID a excluir de validaciones (para updates)
            
        Returns:
            EntityValidationResult: Resultado de validación
        """
        validation_errors = []
        validation_warnings = []
        
        # Validar unicidad de nombre
        name_validation = await self._validate_name_uniqueness(
            entity_data.get("name"), exclude_id
        )
        if not name_validation.is_valid:
            validation_errors.extend(name_validation.errors)
        
        # Validar reglas de estado
        status_validation = await self._validate_status_rules(entity_data)
        if not status_validation.is_valid:
            validation_errors.extend(status_validation.errors)
        
        # Validar dependencias
        dependency_validation = await self._validate_dependencies(entity_data)
        if not dependency_validation.is_valid:
            validation_warnings.extend(dependency_validation.warnings)
        
        return EntityValidationResult(
            is_valid=len(validation_errors) == 0,
            errors=validation_errors,
            warnings=validation_warnings
        )

    async def validate_entity_deletion(
        self,
        entity_id: UUID
    ) -> EntityDeletionValidationResult:
        """
        Valida si una entidad puede ser eliminada.
        
        Args:
            entity_id: ID de la entidad
            
        Returns:
            EntityDeletionValidationResult: Resultado de validación
        """
        # Verificar dependencias activas
        active_dependencies = await self.repository.get_entity_dependencies(entity_id)
        
        # Verificar referencias en otras entidades
        references = await self.repository.get_entity_references(entity_id)
        
        can_delete = len(active_dependencies) == 0 and len(references) == 0
        
        return EntityDeletionValidationResult(
            can_delete=can_delete,
            blocking_dependencies=active_dependencies,
            references=references,
            suggested_action="archive" if not can_delete else "delete"
        )
```

---

## Buenas Prácticas de Implementación

### 1. Gestión de Errores y Logging

```python
# Ejemplo de manejo robusto de errores
class EntityDomainService:
    
    async def create_entity_with_error_handling(
        self,
        entity_data: EntityCreateSchema
    ) -> EntityResponseSchema:
        """
        Crea una entidad con manejo completo de errores.
        """
        operation_id = str(uuid4())
        self._logger.info(
            f"Iniciando creación de entidad",
            operation_id=operation_id,
            entity_name=entity_data.name
        )
        
        try:
            # Validaciones previas
            validation_result = await self._validation_ops.validate_entity_creation(entity_data)
            if not validation_result.is_valid:
                self._logger.warning(
                    f"Validación fallida para creación de entidad",
                    operation_id=operation_id,
                    errors=validation_result.errors
                )
                raise EntityValidationError(
                    message="Datos de entidad no válidos",
                    validation_errors=validation_result.errors
                )
            
            # Crear entidad
            created_entity = await self._crud_ops.create_entity(entity_data)
            
            self._logger.info(
                f"Entidad creada exitosamente",
                operation_id=operation_id,
                entity_id=created_entity.id
            )
            
            return created_entity
            
        except EntityValidationError:
            # Re-lanzar errores de validación sin modificar
            raise
        except RepositoryError as e:
            self._logger.error(
                f"Error de repositorio creando entidad",
                operation_id=operation_id,
                error=str(e)
            )
            raise EntityDomainError(
                message="Error interno creando entidad",
                original_error=e
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado creando entidad",
                operation_id=operation_id,
                error=str(e)
            )
            raise EntityDomainError(
                message="Error inesperado en el servicio",
                original_error=e
            )
```

### 2. Transacciones y Consistencia

```python
# Ejemplo de operaciones transaccionales
class EntityDomainService:
    
    async def bulk_create_entities_transactional(
        self,
        entities_data: List[EntityCreateSchema]
    ) -> List[EntityResponseSchema]:
        """
        Crea múltiples entidades en una transacción atómica.
        """
        self._logger.info(f"Iniciando creación masiva de {len(entities_data)} entidades")
        
        async with self.repository.transaction():
            try:
                created_entities = []
                
                # Validar todas las entidades antes de crear
                for i, entity_data in enumerate(entities_data):
                    validation_result = await self._validation_ops.validate_entity_creation(entity_data)
                    if not validation_result.is_valid:
                        raise EntityValidationError(
                            message=f"Entidad {i+1} no válida: {validation_result.errors}",
                            validation_errors=validation_result.errors
                        )
                
                # Crear todas las entidades
                for entity_data in entities_data:
                    created_entity = await self._crud_ops.create_entity(entity_data)
                    created_entities.append(created_entity)
                
                self._logger.info(f"Creación masiva completada: {len(created_entities)} entidades")
                return created_entities
                
            except Exception as e:
                self._logger.error(f"Error en creación masiva, rollback ejecutado: {e}")
                raise
```

### 3. Testing y Mocking

```python
# Ejemplo de estructura testeable
import pytest
from unittest.mock import AsyncMock, Mock

class TestEntityDomainService:
    
    @pytest.fixture
    def mock_repository_facade(self):
        """Mock del repository facade."""
        mock = AsyncMock(spec=EntityRepositoryFacade)
        return mock
    
    @pytest.fixture
    def entity_service(self, mock_repository_facade):
        """Instancia del servicio con dependencias mockeadas."""
        return EntityDomainService(mock_repository_facade)
    
    async def test_create_entity_success(self, entity_service, mock_repository_facade):
        """Test de creación exitosa de entidad."""
        # Arrange
        entity_data = EntityCreateSchema(name="Test Entity", description="Test")
        expected_entity = EntityResponseSchema(
            id=UUID("12345678-1234-5678-9012-123456789012"),
            name="Test Entity",
            description="Test"
        )
        
        mock_repository_facade.create_entity.return_value = expected_entity
        mock_repository_facade.get_entity_by_name.return_value = None  # No duplicados
        
        # Act
        result = await entity_service.create_entity(entity_data)
        
        # Assert
        assert result == expected_entity
        mock_repository_facade.create_entity.assert_called_once()
    
    async def test_create_entity_validation_error(self, entity_service):
        """Test de error de validación en creación."""
        # Arrange
        entity_data = EntityCreateSchema(name="", description="Test")  # Nombre vacío
        
        # Act & Assert
        with pytest.raises(EntityValidationError) as exc_info:
            await entity_service.create_entity(entity_data)
        
        assert "nombre" in str(exc_info.value).lower()
```

### 4. Configuración y Dependency Injection

```python
# Ejemplo de configuración e inyección de dependencias
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

class EntityContainer(containers.DeclarativeContainer):
    """Container de dependencias para entidades."""
    
    # Configuración
    config = providers.Configuration()
    
    # Repository
    entity_repository_facade = providers.Singleton(
        EntityRepositoryFacade,
        database_session=Provide["database.session"]
    )
    
    # Domain Service
    entity_domain_service = providers.Singleton(
        EntityDomainService,
        repository_facade=entity_repository_facade
    )

# Uso con inyección de dependencias
@inject
async def create_entity_endpoint(
    entity_data: EntityCreateSchema,
    entity_service: EntityDomainService = Provide[EntityContainer.entity_domain_service]
) -> EntityResponseSchema:
    """Endpoint para crear entidad con inyección de dependencias."""
    return await entity_service.create_entity(entity_data)
```

### 5. Monitoreo y Métricas

```python
# Ejemplo de monitoreo integrado
import time
from functools import wraps

def monitor_performance(operation_name: str):
    """Decorador para monitorear performance de operaciones."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            start_time = time.time()
            operation_id = str(uuid4())
            
            self._logger.info(
                f"Iniciando operación: {operation_name}",
                operation_id=operation_id
            )
            
            try:
                result = await func(self, *args, **kwargs)
                
                duration = time.time() - start_time
                self._logger.info(
                    f"Operación completada: {operation_name}",
                    operation_id=operation_id,
                    duration_seconds=duration
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                self._logger.error(
                    f"Operación fallida: {operation_name}",
                    operation_id=operation_id,
                    duration_seconds=duration,
                    error=str(e)
                )
                raise
                
        return wrapper
    return decorator

class EntityDomainService:
    
    @monitor_performance("create_entity")
    async def create_entity(self, entity_data: EntityCreateSchema) -> EntityResponseSchema:
        """Crear entidad con monitoreo de performance."""
        return await self._crud_ops.create_entity(entity_data)
```

---

## Resumen de Beneficios

### Ventajas del Patrón

1. **Separación Clara de Responsabilidades**
   - Cada módulo tiene una función específica y bien definida
   - Facilita el mantenimiento y la evolución del código
   - Reduce el acoplamiento entre componentes

2. **Escalabilidad y Extensibilidad**
   - Fácil agregar nuevas operaciones sin afectar existentes
   - Módulos independientes permiten desarrollo paralelo
   - Interfaces claras facilitan la integración

3. **Testabilidad Mejorada**
   - Cada módulo puede ser testeado independientemente
   - Mocking simplificado por interfaces bien definidas
   - Cobertura de pruebas más granular

4. **Mantenibilidad**
   - Código organizado y predecible
   - Fácil localización de funcionalidades específicas
   - Refactoring seguro por contratos bien definidos

5. **Reutilización de Código**
   - Módulos pueden ser reutilizados en diferentes contextos
   - Interfaces estándar facilitan la intercambiabilidad
   - Patrones consistentes en toda la aplicación

### Consideraciones de Implementación

1. **Complejidad Inicial**
   - Requiere más setup inicial que enfoques monolíticos
   - Necesita planificación cuidadosa de interfaces
   - Curva de aprendizaje para desarrolladores nuevos

2. **Overhead de Abstracción**
   - Múltiples capas pueden impactar performance mínimamente
   - Más archivos y clases para mantener
   - Debugging puede ser más complejo inicialmente

3. **Consistencia Requerida**
   - Todos los desarrolladores deben seguir el patrón
   - Documentación y ejemplos son críticos
   - Code reviews deben validar adherencia al patrón

---

## Conclusión

El patrón de Servicios de Dominio con Facade e Interfaz proporciona una arquitectura robusta y escalable para aplicaciones complejas. Su implementación requiere inversión inicial en diseño y estructura, pero los beneficios a largo plazo en mantenibilidad, testabilidad y escalabilidad justifican ampliamente este esfuerzo.

Este patrón es especialmente valioso en:
- Aplicaciones con lógica de negocio compleja
- Sistemas que requieren alta testabilidad
- Proyectos con múltiples desarrolladores
- Aplicaciones que necesitan evolucionar constantemente
- Sistemas que requieren alta confiabilidad y mantenibilidad

La clave del éxito está en la consistencia de implementación y la adherencia a los principios de diseño establecidos.