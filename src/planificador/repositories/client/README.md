# Planificador - Módulo de Repositorio de Clientes

Módulo especializado para la gestión completa de clientes en la aplicación de planificación de horarios, diseñado para optimizar la gestión de personal y proyectos.

## Arquitectura y Diseño

El módulo de clientes implementa una **arquitectura modular y desacoplada** basada en el patrón Facade, con separación clara de responsabilidades para facilitar el mantenimiento, escalabilidad y testabilidad.

### Componentes Principales

#### 1. ClientRepositoryFacade
**Punto de entrada único** que orquesta todas las operaciones de clientes, delegando responsabilidades a módulos especializados:

- **39 funciones públicas** organizadas en 8 categorías funcionales
- **Delegación inteligente** a módulos especializados
- **Manejo centralizado de excepciones** con logging estructurado
- **Type hints completos** y documentación exhaustiva
- **Compatibilidad asíncrona** para operaciones de base de datos

#### 2. Módulos Especializados

- **`AdvancedQueryOperations`**: Búsquedas complejas, filtros múltiples y consultas con relaciones
- **`CRUDOperations`**: Operaciones básicas de Crear, Leer, Actualizar y Eliminar
- **`DateOperations`**: Lógica de negocio relacionada con fechas y rangos temporales
- **`HealthOperations`**: Verificación de estado y diagnósticos del sistema
- **`QueryOperations`**: Consultas básicas por ID, nombre, código y email
- **`RelationshipOperations`**: Gestión de relaciones con proyectos y transferencias
- **`StatisticsOperations`**: Métricas, análisis estadísticos y tendencias
- **`ValidationOperations`**: Validaciones de datos, formatos y reglas de negocio

#### 3. Interfaces Especializadas

Cada módulo implementa interfaces específicas que definen contratos claros:

- **`AdvancedQueryInterface`**: Contratos para búsquedas avanzadas
- **`CRUDInterface`**: Operaciones básicas de persistencia
- **`DateInterface`**: Operaciones temporales
- **`HealthInterface`**: Diagnósticos del sistema
- **`QueryInterface`**: Consultas básicas
- **`RelationshipInterface`**: Gestión de relaciones
- **`StatisticsInterface`**: Análisis y métricas
- **`ValidationInterface`**: Validaciones y reglas de negocio

### Funcionalidades por Categoría

#### Advanced Query Operations (5 funciones)
- Búsqueda por texto en campos específicos
- Filtros múltiples con paginación
- Carga de relaciones (proyectos, contactos)
- Conteo con filtros
- Búsqueda difusa por similitud

#### CRUD Operations (3 funciones)
- Creación con validación completa
- Actualización de datos existentes
- Eliminación segura con verificaciones

#### Date Operations (2 funciones)
- Consultas por rangos de fechas de creación
- Consultas por rangos de fechas de actualización

#### Health Operations (2 funciones)
- Verificación de estado de todos los módulos
- Información detallada del sistema

#### Query Operations (6 funciones)
- Búsqueda por ID, nombre, código, email
- Búsqueda por patrones de nombre
- Listado completo con paginación

#### Relationship Operations (3 funciones)
- Transferencia de proyectos entre clientes
- Obtención de proyectos asociados
- Conteo de proyectos por cliente

#### Statistics Operations (7 funciones)
- Estadísticas generales y por estado
- Conteo total de clientes
- Estadísticas específicas por cliente
- Tendencias de creación
- Ranking por cantidad de proyectos
- Métricas completas para dashboard

#### Validation Operations (11 funciones)
- Validación de campos únicos
- Validación de formatos (email, teléfono, código)
- Validación de campos requeridos y longitudes
- Validación completa de datos
- Validación de reglas de negocio
- Verificación de unicidad
- Validación de posibilidad de eliminación

Para una descripción detallada de todas las funciones disponibles, consulta:
**[Funcionalidades Completas del Módulo](./client_available_functions.md)**

## Características Principales del Módulo

### 🔍 Búsquedas y Consultas Avanzadas
- **Búsqueda por texto** en campos específicos con paginación
- **Filtros múltiples** con ordenamiento personalizable
- **Búsqueda difusa** por similitud de texto
- **Carga de relaciones** (proyectos, contactos) con eager loading
- **Consultas básicas** por ID, nombre, código, email
- **Conteo eficiente** con filtros aplicados

### 📊 Análisis y Estadísticas
- **Métricas completas** para dashboard ejecutivo
- **Tendencias de creación** con agrupación temporal
- **Estadísticas por estado** de clientes
- **Ranking por proyectos** asociados
- **Análisis específico** por cliente individual
- **Conteos generales** y segmentados

### ✅ Validaciones Robustas
- **Validación de unicidad** para campos críticos
- **Validación de formatos** (email, teléfono, código)
- **Validación de longitudes** y campos requeridos
- **Reglas de negocio** personalizadas
- **Validación completa** de datos antes de persistir
- **Verificación de eliminación** segura

### 🔄 Operaciones CRUD Completas
- **Creación** con validación automática
- **Actualización** de datos existentes
- **Eliminación** con verificaciones de seguridad
- **Consultas** optimizadas con índices

### 📅 Gestión Temporal
- **Consultas por rangos** de fechas de creación
- **Filtros temporales** de actualización
- **Análisis de tendencias** temporales
- **Soporte completo** para zonas horarias con Pendulum

### 🔗 Gestión de Relaciones
- **Transferencia de proyectos** entre clientes
- **Consulta de proyectos** asociados
- **Conteo de relaciones** eficiente
- **Gestión de dependencias** entre entidades

### 🏥 Diagnósticos y Salud
- **Health checks** de todos los módulos
- **Información del sistema** detallada
- **Monitoreo de estado** en tiempo real
- **Diagnósticos automáticos** de problemas

### 🛡️ Seguridad y Robustez
- **Manejo de excepciones** jerárquico y estructurado
- **Logging detallado** con contexto enriquecido
- **Rollback automático** en transacciones fallidas
- **Validación de entrada** en todos los puntos de acceso
- **Type safety** completo con hints de Python 3.13

## Tech Stack

- **Python 3.13**
- **Flet**: Para la interfaz gráfica de usuario.
- **SQLAlchemy**: ORM para la interacción con la base de datos SQLite.
- **Pydantic**: Para la validación de datos y la configuración.
- **Loguru**: Para un logging estructurado y sencillo.
- **Alembic**: Para migraciones de base de datos.
- **Poetry**: Para la gestión de dependencias.
- **Pytest**: Para la ejecución de tests unitarios y de integración.
- **Pendulum**: Para manipulación avanzada de fechas y tiempos.



## Estructura del Módulo de Clientes

```
├── client/                       # Módulo de repositorio de clientes
│   ├── __init__.py              # Exportaciones públicas del módulo
│   ├── README.md                # Documentación del módulo (este archivo)
│   ├── client_available_functions.md # Listado completo de funciones
│   ├── client_repository_facade.py   # Facade principal con 39 funciones
│   │
│   ├── interfaces/               # Contratos e interfaces
│   │   ├── __init__.py
│   │   ├── advanced_query_interface.py
│   │   ├── crud_interface.py
│   │   ├── date_interface.py
│   │   ├── health_interface.py
│   │   ├── i_client_query_builder.py
│   │   ├── i_client_statistics.py
│   │   ├── i_client_validator.py
│   │   ├── query_interface.py
│   │   ├── relationship_interface.py
│   │   ├── search_interface.py
│   │   ├── statistics_interface.py
│   │   └── validation_interface.py
│   │
│   ├── modules/                  # Implementaciones especializadas
│   │   ├── __init__.py
│   │   ├── advanced_query_operations.py  # Búsquedas complejas
│   │   ├── crud_operations.py           # Operaciones CRUD
│   │   ├── date_operations.py           # Operaciones de fechas
│   │   ├── health_operations.py         # Diagnósticos del sistema
│   │   ├── query_operations.py          # Consultas básicas
│   │   ├── relationship_operations.py   # Gestión de relaciones
│   │   ├── statistics_operations.py     # Análisis y métricas
│   │   └── validation_operations.py     # Validaciones y reglas
│   │
│   ├── client_repository_facade/        # Módulos auxiliares del facade
│   │   └── modules/
│   │       ├── search_operations.py     # Operaciones de búsqueda
│   │       └── validation_operations.py # Validaciones auxiliares
│   │
│   └── factories/                # Factories para creación de instancias
│       └── __init__.py
```

## Estructura General del Proyecto

```
├── src/planificador/
│   ├── api/                      # Endpoints de la API (WIP)
│   ├── config/                   # Módulos de configuración (logging, Pydantic)
│   ├── database/
│   │   ├── repositories/
│   │   │   └── client/           # Módulo completo de clientes (ver arriba)
│   │   └── ...
│   ├── models/                   # Modelos de SQLAlchemy
│   ├── schemas/                  # Esquemas de Pydantic para validación
│   ├── services/                 # Lógica de negocio
│   ├── ui/                       # Componentes de la interfaz de usuario (Flet)
│   ├── tests/                    # Tests unitarios y de integración
│   ├── utils/                    # Funciones de utilidad
│   ├── main.py                   # Punto de entrada de la aplicación
│   └── init_db.py                # Script para inicializar la BD
├── data/                         # Base de datos SQLite y otros datos
├── docs/                         # Documentación general del proyecto
├── examples/                     # Scripts de ejemplo de uso de los servicios
└── scripts/                      # Scripts auxiliares
```

## Patrones y Mejores Prácticas Implementadas

### 1. Patrón Facade
- **Punto de entrada único** que simplifica la interacción con múltiples subsistemas
- **Delegación inteligente** a módulos especializados según responsabilidad
- **Interfaz consistente** para todas las operaciones de clientes

### 2. Separación de Responsabilidades (SRP)
- **Módulos especializados** con una única responsabilidad bien definida
- **Interfaces específicas** que definen contratos claros
- **Cohesión alta** dentro de cada módulo, **acoplamiento bajo** entre módulos

### 3. Manejo Robusto de Excepciones
- **Jerarquía de excepciones** SQLAlchemyError → Exception
- **Rollback automático** en métodos transaccionales
- **Logging estructurado** con contexto enriquecido
- **Conversión inteligente** de errores de base de datos

### 4. Type Safety y Documentación
- **Type hints completos** en todas las funciones públicas
- **Docstrings formato Google** con Args, Returns y Raises
- **Validación de parámetros** con Pydantic cuando corresponde
- **Documentación exhaustiva** de comportamientos y excepciones

### 5. Arquitectura Asíncrona
- **Compatibilidad async/await** para operaciones de base de datos
- **Operaciones no bloqueantes** con aiosqlite
- **Gestión eficiente de conexiones** con SQLAlchemy async

### 6. Principios SOLID
- **Single Responsibility**: Cada módulo tiene una responsabilidad específica
- **Open/Closed**: Extensible sin modificar código existente
- **Liskov Substitution**: Interfaces intercambiables
- **Interface Segregation**: Interfaces específicas y cohesivas
- **Dependency Inversion**: Dependencias de abstracciones, no implementaciones

## Configuración y Dependencias

### Configuración del Sistema
La configuración se gestiona a través de variables de entorno validadas con Pydantic:

- `src/planificador/config/config.py`: Configuraciones generales del sistema
- `src/planificador/config/logging_config.py`: Configuración de logging con Loguru

### Dependencias Principales
- **SQLAlchemy**: ORM asíncrono para operaciones de base de datos
- **aiosqlite**: Driver asíncrono para SQLite
- **Pydantic**: Validación de datos y configuración
- **Loguru**: Logging estructurado y sencillo
- **Pendulum**: Manipulación avanzada de fechas y tiempos

## Uso del Módulo

### Inicialización Básica
```python
from planificador.repositories.client import ClientRepositoryFacade
from planificador.database.session import get_async_session

# Crear instancia del facade
async with get_async_session() as session:
    client_repo = ClientRepositoryFacade(session)
    
    # Usar cualquiera de las 39 funciones disponibles
    clients = await client_repo.get_all_clients(limit=10)
    stats = await client_repo.get_client_statistics()
```

### Ejemplo de Operaciones Avanzadas
```python
# Búsqueda avanzada con filtros
filters = {"status": "active", "city": "Santiago"}
clients = await client_repo.get_clients_by_filters(
    filters=filters,
    limit=50,
    order_by="created_at"
)

# Validación completa de datos
try:
    await client_repo.validate_client_data(
        client_data={"name": "Empresa ABC", "email": "contact@abc.com"},
        validate_uniqueness=True
    )
except ValidationError as e:
    print(f"Error de validación: {e}")

# Estadísticas y métricas
metrics = await client_repo.get_comprehensive_dashboard_metrics()
trends = await client_repo.get_client_creation_trends(days=30)
```

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un *issue* para discutir los cambios propuestos o envía un *pull request*.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.