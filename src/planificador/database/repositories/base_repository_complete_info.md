# BaseRepository - Información Completa

## Descripción General
Clase base abstracta para operaciones CRUD asíncronas con SQLAlchemy, manejo robusto de errores, logging estructurado y optimizaciones de performance.

## Arquitectura
- **Patrón**: Repository Pattern con Generic Types
- **Tipo**: Clase abstracta genérica `BaseRepository[ModelType]`
- **Herencia**: Debe ser heredada por repositorios específicos
- **Asíncrono**: Todas las operaciones son async/await

## Dependencias Principales
- **SQLAlchemy**: ORM para operaciones de base de datos
- **AsyncSession**: Sesiones asíncronas de SQLAlchemy
- **Loguru**: Sistema de logging estructurado
- **Pydantic**: Validación de configuraciones
- **Pendulum**: Manejo avanzado de fechas y tiempo

## Configuración Requerida
- **settings**: Instancia global de configuración del sistema
- **DatabaseManager**: Gestor singleton de conexiones a BD
- **Excepciones personalizadas**: Sistema de errores del proyecto

## Características Principales

### 1. Operaciones CRUD Completas
- **Create**: Creación de entidades con validación
- **Read**: Lectura por ID, listado con paginación, búsqueda por criterios
- **Update**: Actualización parcial con merge automático
- **Delete**: Eliminación lógica o física

### 2. Manejo de Errores Robusto
- **SQLAlchemyError**: Conversión automática a excepciones personalizadas
- **Rollback automático**: En métodos transaccionales
- **Contexto enriquecido**: operation, entity_type, entity_id
- **Preservación de errores originales**: Para debugging

### 3. Logging Estructurado
- **Niveles apropiados**: DEBUG, INFO, WARNING, ERROR
- **Contexto completo**: Operación, entidad, duración, parámetros
- **Modo debug**: Logging detallado cuando está habilitado
- **Performance tracking**: Medición de tiempos de operación

### 4. Optimizaciones de Performance
- **Lazy loading**: Carga diferida por defecto
- **Eager loading**: Disponible para relaciones específicas
- **Paginación eficiente**: Con skip/limit
- **Consultas optimizadas**: Uso de exists() para verificaciones
- **Connection pooling**: Gestión automática de conexiones

## Funciones Disponibles

### CRUD Básico
- `create(entity)` - Crear nueva entidad
- `get_by_id(id)` - Obtener por ID
- `get_all(skip, limit)` - Listar con paginación
- `update(id, data)` - Actualizar entidad
- `delete(id)` - Eliminar entidad

### Consultas Avanzadas
- `exists(id)` - Verificar existencia
- `count()` - Contar total de registros
- `find_by_criteria(criteria, skip, limit)` - Búsqueda personalizada

### Transacciones
- `commit()` - Confirmar cambios
- `rollback()` - Revertir cambios

### Utilidades
- `_log_operation()` - Logging de operaciones
- `_validate_entity()` - Validación de entidades

## Sistema de Excepciones

### Jerarquía de Errores
1. **SQLAlchemyError** → `convert_sqlalchemy_error()`
   - IntegrityError → RepositoryIntegrityError
   - OperationalError → RepositoryOperationalError
   - TimeoutError → RepositoryTimeoutError

2. **Exception genérica** → `RepositoryError`
   - Errores inesperados con contexto completo

### Información de Contexto
- **operation**: Nombre de la operación (create, update, delete, etc.)
- **entity_type**: Tipo de entidad (Project, Employee, etc.)
- **entity_id**: ID de la entidad afectada
- **original_error**: Excepción original para debugging

## Uso Básico

### Implementación de Repositorio Específico
```python
class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Project)
```

### Uso en Servicios
```python
async def create_project(project_data: dict):
    async with DatabaseManager().get_session() as session:
        repo = ProjectRepository(session)
        project = Project(**project_data)
        return await repo.create(project)
```

## Configuración de Logging
- **Debug Mode**: Logging detallado de todas las operaciones
- **Production Mode**: Solo errores y warnings
- **Formato estructurado**: JSON con contexto completo
- **Rotación automática**: Gestión de archivos de log

## Validaciones Automáticas
- **Entidad válida**: Verificación de instancia correcta
- **ID no nulo**: Para operaciones que requieren ID
- **Datos de actualización**: Validación de diccionario no vacío
- **Sesión activa**: Verificación de conexión a BD

## Integración con el Sistema
- **BaseModel**: Compatible con modelos que heredan de BaseModel
- **Audit fields**: Manejo automático de created_at, updated_at
- **Configuración global**: Uso de settings del sistema
- **Excepciones del proyecto**: Integración completa con sistema de errores

## Extensibilidad
- **Métodos personalizados**: Agregar funciones específicas en repositorios hijos
- **Validaciones adicionales**: Override de _validate_entity()
- **Logging personalizado**: Extensión de _log_operation()
- **Manejo de errores específicos**: Captura de excepciones particulares

## Consideraciones de Seguridad
- **SQL Injection**: Protección automática via SQLAlchemy ORM
- **Validación de entrada**: Verificación de tipos y valores
- **Transacciones seguras**: Rollback automático en errores
- **Logging seguro**: Sin exposición de datos sensibles

## Performance Tips
- **Usar exists()** en lugar de get_by_id() para verificaciones
- **Implementar paginación** en consultas grandes
- **Usar find_by_criteria()** para búsquedas complejas
- **Gestionar transacciones** apropiadamente con commit/rollback
- **Monitorear logs** para identificar operaciones lentas

## Requisitos del Sistema
- **Python 3.13+**
- **SQLAlchemy 2.0+** con soporte async
- **aiosqlite** para SQLite asíncrono
- **Loguru** para logging
- **Pendulum** para fechas
- **Pydantic** para configuración

## Estado del Proyecto
- **Estable**: Implementación completa y probada
- **Documentado**: README y ejemplos disponibles
- **Testeado**: Cobertura de pruebas unitarias
- **Optimizado**: Performance validada en producción