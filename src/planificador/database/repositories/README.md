# Repositorios de Base de Datos - Planificador

*Última actualización: 21 de agosto de 2025*

## Descripción General

Este módulo contiene la implementación del repositorio base (`BaseRepository`) que proporciona operaciones CRUD estándar y manejo robusto de errores para todos los repositorios del sistema Planificador.

## Características Principales

### ✅ Operaciones CRUD Completas
- **Create**: Creación de entidades con validación automática
- **Read**: Consultas por ID, criterios específicos y listado completo
- **Update**: Actualización de entidades existentes
- **Delete**: Eliminación segura con verificación de existencia

### ✅ Manejo Robusto de Errores
- Conversión automática de errores SQLAlchemy a excepciones personalizadas
- Logging estructurado con contexto detallado
- Rollback automático en operaciones transaccionales
- Preservación de errores originales para debugging

### ✅ Operaciones Asíncronas
- Compatibilidad completa con `async/await`
- Optimizado para operaciones no bloqueantes
- Gestión eficiente de sesiones SQLAlchemy asíncronas

### ✅ Consultas Avanzadas
- Búsqueda por criterios múltiples
- Paginación y ordenamiento
- Conteo con filtros opcionales
- Verificación de existencia optimizada

### ✅ Logging Estructurado
- Integración con Loguru
- Contexto enriquecido para debugging
- Niveles de log apropiados según el entorno

## Estructura del Archivo

```
base_repository.py
├── Imports y Type Hints
├── Clase BaseRepository (Generic[ModelType])
│   ├── __init__: Inicialización con sesión y modelo
│   ├── OPERACIONES CRUD BÁSICAS
│   │   ├── create(): Creación de entidades
│   │   ├── get_by_id(): Búsqueda por ID
│   │   ├── get_all(): Listado con paginación
│   │   ├── update(): Actualización de entidades
│   │   └── delete(): Eliminación por ID
│   ├── OPERACIONES DE CONSULTA AVANZADAS
│   │   ├── exists(): Verificación de existencia
│   │   ├── count(): Conteo con filtros
│   │   └── find_by_criteria(): Búsqueda avanzada
│   ├── OPERACIONES DE TRANSACCIÓN
│   │   ├── commit(): Confirmación de transacciones
│   │   └── rollback(): Reversión de transacciones
│   ├── MÉTODOS ABSTRACTOS
│   │   └── get_by_unique_field(): Para implementación específica
│   └── MÉTODOS DE UTILIDAD
│       ├── _build_select_statement(): Constructor de consultas
│       ├── _log_operation_*(): Métodos de logging
│       ├── _validate_entity(): Validación de entidades
│       ├── get_model_class(): Getter del modelo
│       └── get_session(): Getter de la sesión
```

## Uso Básico

### 1. Implementación de un Repositorio Específico

```python
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.project import Project
from .base_repository import BaseRepository
from ...exceptions import convert_sqlalchemy_error, RepositoryError

class ProjectRepository(BaseRepository[Project]):
    """Repositorio específico para la entidad Project."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Project)
    
    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[Project]:
        """Implementación específica para campos únicos de Project."""
        try:
            if field_name == "name":
                stmt = select(self.model_class).where(self.model_class.name == value)
            elif field_name == "code":
                stmt = select(self.model_class).where(self.model_class.code == value)
            else:
                raise RepositoryError(
                    message=f"Campo único '{field_name}' no soportado",
                    operation="get_by_unique_field",
                    entity_type=self.model_class.__name__
                )
            
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error al buscar por {field_name}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type=self.model_class.__name__
            )
    
    async def get_active_projects(self) -> List[Project]:
        """Obtiene todos los proyectos activos."""
        return await self.find_by_criteria({"is_active": True})
    
    async def get_projects_by_client(self, client_id: int) -> List[Project]:
        """Obtiene proyectos de un cliente específico."""
        return await self.find_by_criteria({"client_id": client_id})
```

### 2. Uso en Servicios

```python
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.database import DatabaseManager
from ..database.repositories import ProjectRepository
from ..models.project import Project

class ProjectService:
    """Servicio para gestión de proyectos."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    async def create_project(self, project_data: dict) -> Project:
        """Crea un nuevo proyecto."""
        async with self.db_manager.get_session() as session:
            repository = ProjectRepository(session)
            
            # Crear entidad
            project = Project(**project_data)
            
            # Guardar en base de datos
            created_project = await repository.create(project)
            
            # Confirmar transacción
            await repository.commit()
            
            return created_project
    
    async def get_project(self, project_id: int) -> Optional[Project]:
        """Obtiene un proyecto por ID."""
        async with self.db_manager.get_session() as session:
            repository = ProjectRepository(session)
            return await repository.get_by_id(project_id)
    
    async def update_project(self, project_id: int, update_data: dict) -> Project:
        """Actualiza un proyecto existente."""
        async with self.db_manager.get_session() as session:
            repository = ProjectRepository(session)
            
            # Obtener proyecto existente
            project = await repository.get_by_id(project_id)
            if not project:
                raise NotFoundError(
                    message=f"Proyecto con ID {project_id} no encontrado",
                    entity_type="Project",
                    entity_id=project_id
                )
            
            # Actualizar campos
            for field, value in update_data.items():
                if hasattr(project, field):
                    setattr(project, field, value)
            
            # Guardar cambios
            updated_project = await repository.update(project)
            await repository.commit()
            
            return updated_project
```

## Operaciones Avanzadas

### Búsqueda por Criterios

```python
# Búsqueda simple
active_projects = await repository.find_by_criteria({"is_active": True})

# Búsqueda con operadores
recent_projects = await repository.find_by_criteria({
    "created_at": {
        "operator": "gte",
        "value": datetime.now() - timedelta(days=30)
    }
})

# Búsqueda con múltiples valores
specific_projects = await repository.find_by_criteria({
    "status": ["active", "pending", "in_progress"]
})

# Búsqueda con paginación
projects_page = await repository.find_by_criteria(
    criteria={"client_id": 123},
    limit=10,
    offset=20,
    order_by="created_at"
)
```

### Operadores Soportados

- `like`: Búsqueda de texto parcial
- `gt`: Mayor que
- `gte`: Mayor o igual que
- `lt`: Menor que
- `lte`: Menor o igual que
- `ne`: No igual
- `in`: Valor en lista (automático para listas)

## Manejo de Errores

### Jerarquía de Excepciones

```python
try:
    project = await repository.create(new_project)
except IntegrityConstraintError as e:
    # Error de restricción de integridad (duplicados, FK, etc.)
    logger.error(f"Error de integridad: {e.message}")
except DatabaseConnectionError as e:
    # Error de conexión a la base de datos
    logger.error(f"Error de conexión: {e.message}")
except RepositoryError as e:
    # Error general del repositorio
    logger.error(f"Error del repositorio: {e.message}")
```

### Logging Automático

Todos los errores se registran automáticamente con contexto detallado:

```python
# Ejemplo de log generado automáticamente
{
    "level": "ERROR",
    "message": "Error al crear Project: UNIQUE constraint failed",
    "repository": "ProjectRepository",
    "model": "Project",
    "operation": "create",
    "error_type": "IntegrityError",
    "timestamp": "2025-08-21T15:33:02-04:00"
}
```

## Mejores Prácticas

### ✅ Recomendado

1. **Usar gestores de contexto** para sesiones:
   ```python
   async with db_manager.get_session() as session:
       repository = ProjectRepository(session)
       # operaciones...
   ```

2. **Confirmar transacciones explícitamente**:
   ```python
   await repository.create(entity)
   await repository.commit()  # Confirmar cambios
   ```

3. **Manejar excepciones específicas**:
   ```python
   try:
       await repository.create(entity)
   except IntegrityConstraintError:
       # Manejar duplicados específicamente
   except RepositoryError:
       # Manejar otros errores del repositorio
   ```

4. **Implementar métodos específicos** en repositorios derivados:
   ```python
   async def get_by_email(self, email: str) -> Optional[User]:
       return await self.get_by_unique_field("email", email)
   ```

### ❌ Evitar

1. **No usar try/catch genérico**:
   ```python
   # MAL
   try:
       await repository.create(entity)
   except Exception:  # Muy genérico
       pass
   ```

2. **No olvidar el commit**:
   ```python
   # MAL - Los cambios no se persisten
   await repository.create(entity)
   # Falta: await repository.commit()
   ```

3. **No reutilizar sesiones entre operaciones**:
   ```python
   # MAL
   session = await db_manager.get_session()
   repo1 = ProjectRepository(session)
   repo2 = UserRepository(session)  # Riesgo de conflictos
   ```

## Configuración y Dependencias

### Dependencias Requeridas

- `SQLAlchemy` (>=2.0): ORM asíncrono
- `aiosqlite`: Driver asíncrono para SQLite
- `loguru`: Logging estructurado
- `pydantic`: Validación de configuración

### Configuración en `config.py`

El repositorio utiliza automáticamente la configuración del sistema:

```python
# Configuración de base de datos
settings.database.url          # URL de conexión
settings.database.echo         # Logging de SQL
settings.database.pool_size    # Tamaño del pool

# Configuración de logging
settings.debug_mode           # Nivel de logging detallado
settings.logging_level        # Nivel mínimo de logs
```

## Testing

### Ejemplo de Test Unitario

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from ..repositories.project_repository import ProjectRepository
from ..models.project import Project

@pytest.fixture
async def mock_session():
    session = AsyncMock(spec=AsyncSession)
    return session

@pytest.fixture
def project_repository(mock_session):
    return ProjectRepository(mock_session)

@pytest.mark.asyncio
async def test_create_project(project_repository, mock_session):
    # Arrange
    project_data = {"name": "Test Project", "description": "Test"}
    project = Project(**project_data)
    
    # Act
    result = await project_repository.create(project)
    
    # Assert
    mock_session.add.assert_called_once_with(project)
    mock_session.flush.assert_called_once()
    mock_session.refresh.assert_called_once_with(project)
    assert result == project

@pytest.mark.asyncio
async def test_get_by_id_found(project_repository, mock_session):
    # Arrange
    project_id = 1
    expected_project = Project(id=project_id, name="Test")
    
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = expected_project
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await project_repository.get_by_id(project_id)
    
    # Assert
    assert result == expected_project
    mock_session.execute.assert_called_once()
```

## Extensibilidad

El `BaseRepository` está diseñado para ser extendido fácilmente:

### Agregar Métodos Específicos

```python
class ProjectRepository(BaseRepository[Project]):
    
    async def get_projects_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Project]:
        """Obtiene proyectos en un rango de fechas."""
        return await self.find_by_criteria({
            "created_at": {"operator": "gte", "value": start_date},
            "created_at": {"operator": "lte", "value": end_date}
        })
    
    async def get_project_statistics(self) -> dict:
        """Obtiene estadísticas de proyectos."""
        total = await self.count()
        active = await self.count({"is_active": True})
        
        return {
            "total": total,
            "active": active,
            "inactive": total - active
        }
```

### Personalizar Manejo de Errores

```python
class ProjectRepository(BaseRepository[Project]):
    
    async def create(self, entity: Project) -> Project:
        """Creación con validaciones específicas de proyecto."""
        try:
            # Validaciones específicas
            if await self.get_by_unique_field("name", entity.name):
                raise ProjectAlreadyExistsError(
                    message=f"Ya existe un proyecto con el nombre '{entity.name}'",
                    project_name=entity.name
                )
            
            # Llamar al método base
            return await super().create(entity)
            
        except ProjectAlreadyExistsError:
            raise  # Re-lanzar excepciones específicas
        except Exception as e:
            self._logger.error(f"Error específico en creación de proyecto: {e}")
            raise
```

---

## Soporte y Contribución

Para reportar problemas o sugerir mejoras, consulta la documentación del proyecto principal o contacta al equipo de desarrollo.

**Versión del Repositorio Base**: 1.0.0  
**Compatibilidad**: Python 3.11+, SQLAlchemy 2.0+  
**Última Revisión**: 21 de agosto de 2025