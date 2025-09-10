# Planificador

Aplicación de planificación de horarios diseñada para optimizar la gestión de personal y proyectos.

## Arquitectura y Diseño

El sistema sigue una arquitectura modular y desacoplada, centrada en la separación de responsabilidades para facilitar el mantenimiento, la escalabilidad y la testabilidad.

### Módulo de Clientes

El módulo de gestión de clientes es un ejemplo clave de esta arquitectura. Se compone de:

- **`ClientRepositoryFacade`**: Actúa como un punto de entrada único para todas las operaciones de clientes. Orquesta la colaboración entre los siguientes componentes especializados.
- **`ClientCRUDOperations`**: Gestiona las operaciones básicas de Crear, Leer, Actualizar y Eliminar.
- **`ClientQueryBuilder`**: Construye y ejecuta consultas complejas y dinámicas.
- **`ClientDateOperations`**: Maneja toda la lógica de negocio relacionada con fechas.
- **`ClientStatistics`**: Calcula y provee métricas y análisis estadísticos.
- **`ClientValidator`**: Realiza validaciones de datos y reglas de negocio.
- **`ClientRelationshipManager`**: Gestiona las relaciones entre clientes y otros módulos (ej. proyectos).
- **`ClientExceptionHandler`**: Centraliza el manejo de excepciones para el módulo.

Para una descripción detallada de todas las funciones disponibles, consulta el documento:
**[Funcionalidades del Módulo de Clientes](./docs/client_available_functions.md)**

## Características Principales

- **Gestión de Clientes**: Administración completa de la información de clientes con operaciones CRUD, búsquedas avanzadas, estadísticas y validaciones.
- **Gestión de Proyectos**: Creación y seguimiento de proyectos.
- **Planificación de Horarios**: Asignación de personal a proyectos y turnos.
- **Gestión de Vacaciones**: Solicitud y aprobación de vacaciones.
- **Asignación de Equipos**: Conformación de equipos de trabajo.
- **Gestión de Carga de Trabajo**: Monitoreo y balance de la carga de trabajo.
- **Alertas y Notificaciones**: Sistema de alertas para eventos importantes.
- **Interfaz de Usuario**: Interfaz gráfica interactiva construida con Flet.

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



## Estructura del Proyecto

```
├── src/planificador/
│   ├── api/                      # Endpoints de la API (WIP)
│   ├── config/                   # Módulos de configuración (logging, Pydantic)
│   ├── database/
│   │   ├── repositories/
│   │   │   └── client/           # Módulo de repositorio de clientes
│   │   │       ├── __init__.py
│   │   │       ├── client_crud_operations.py
│   │   │       ├── client_date_operations.py
│   │   │       ├── client_exception_handler.py
│   │   │       ├── client_query_builder.py
│   │   │       ├── client_relationship_manager.py
│   │   │       ├── client_repository_facade.py
│   │   │       ├── client_statistics.py
│   │   │       └── client_validator.py
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
├── docs/
│   └── client_available_functions.md # Documentación del Facade de Clientes
├── examples/                     # Scripts de ejemplo de uso de los servicios
└── scripts/                      # Scripts auxiliares
```

## Configuración

La configuración del sistema se gestiona a través de variables de entorno y se valida con Pydantic. Los archivos de configuración principales se encuentran en `src/planificador/config/`.

-   `config.py`: Configuraciones generales del sistema.
-   `logging_config.py`: Configuración del sistema de logging con Loguru.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un *issue* para discutir los cambios propuestos o envía un *pull request*.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.