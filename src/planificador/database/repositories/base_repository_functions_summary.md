# Resumen de Funciones - BaseRepository

## Funciones CRUD Básicas

### create(entity: ModelType) -> ModelType
**Parámetros:** entity (instancia del modelo a crear)
**Retorna:** La entidad creada con ID asignado
**Descripción:** Crea una nueva entidad en la base de datos

### get_by_id(entity_id: Any) -> Optional[ModelType]
**Parámetros:** entity_id (ID de la entidad a buscar)
**Retorna:** La entidad encontrada o None si no existe
**Descripción:** Obtiene una entidad por su ID único

### get_all(skip: int = 0, limit: int = 100) -> List[ModelType]
**Parámetros:** skip (registros a omitir), limit (máximo de registros)
**Retorna:** Lista de entidades encontradas
**Descripción:** Obtiene todas las entidades con paginación opcional

### update(entity_id: Any, update_data: Dict[str, Any]) -> Optional[ModelType]
**Parámetros:** entity_id (ID de la entidad), update_data (datos a actualizar)
**Retorna:** La entidad actualizada o None si no existe
**Descripción:** Actualiza una entidad existente con nuevos datos

### delete(entity_id: Any) -> bool
**Parámetros:** entity_id (ID de la entidad a eliminar)
**Retorna:** True si se eliminó, False si no existía
**Descripción:** Elimina una entidad de la base de datos

## Funciones de Consulta Avanzada

### exists(entity_id: Any) -> bool
**Parámetros:** entity_id (ID de la entidad a verificar)
**Retorna:** True si existe, False si no existe
**Descripción:** Verifica si una entidad existe sin cargarla completamente

### count() -> int
**Parámetros:** Ninguno
**Retorna:** Número total de entidades
**Descripción:** Cuenta el total de entidades en la tabla

### find_by_criteria(criteria: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[ModelType]
**Parámetros:** criteria (criterios de búsqueda), skip (registros a omitir), limit (máximo de registros)
**Retorna:** Lista de entidades que cumplen los criterios
**Descripción:** Busca entidades que coincidan con criterios específicos

## Funciones de Transacción

### commit() -> None
**Parámetros:** Ninguno
**Retorna:** None
**Descripción:** Confirma los cambios pendientes en la sesión actual

### rollback() -> None
**Parámetros:** Ninguno
**Retorna:** None
**Descripción:** Revierte los cambios pendientes en la sesión actual

## Funciones de Utilidad

### _log_operation(operation: str, entity_type: str, entity_id: Any = None, duration: float = None) -> None
**Parámetros:** operation (nombre de la operación), entity_type (tipo de entidad), entity_id (ID opcional), duration (duración opcional)
**Retorna:** None
**Descripción:** Registra información de operaciones para auditoría y debugging

### _validate_entity(entity: ModelType) -> None
**Parámetros:** entity (entidad a validar)
**Retorna:** None (lanza excepción si es inválida)
**Descripción:** Valida que una entidad cumple con los requisitos básicos