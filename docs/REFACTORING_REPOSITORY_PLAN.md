# Plan de Implementación para la Refactorización de Repositorios

## 1. Introducción

Este documento describe el plan para refactorizar los repositorios de la aplicación `planificador` a una arquitectura modular y escalable, siguiendo el patrón de diseño Facade. El objetivo es mejorar la mantenibilidad, cohesión y reutilización del código.

## 2. Estructura de Destino

Cada repositorio (p. ej., `project`, `employee`, `client`) se organizará de la siguiente manera:

```
└── repositories/
    └── <entity>/
        ├── __init__.py
        ├── <entity>_repository_facade.py
        ├── interfaces/
        │   ├── __init__.py
        │   ├── i_<entity>_crud.py
        │   ├── i_<entity>_query.py
        │   └── ... (otras interfaces)
        └── modules/
            ├── __init__.py
            ├── crud_operations.py
            ├── query_operations.py
            └── ... (otras implementaciones)
```

## 3. Pasos de Implementación

### Fase 1: Creación de la Estructura de Directorios

1.  Para cada repositorio a refactorizar (p. ej., `project`), crear los siguientes directorios:
    *   `src/planificador/database/repositories/<entity>/interfaces/`
    *   `src/planificador/database/repositories/<entity>/modules/`

### Fase 2: Definición de Interfaces

1.  Dentro del directorio `interfaces`, crear interfaces de Python (`.py`) para cada grupo de funcionalidades. Las interfaces definirán los métodos públicos que la fachada del repositorio expondrá.

    La interfaz CRUD se centrará exclusivamente en las operaciones de **Crear, Actualizar y Eliminar**. La obtención de datos (lectura) se gestionará a través de interfaces de consulta más específicas.

    *Ejemplo: `i_project_crud.py`*

    ```python
    from abc import ABC, abstractmethod
    from typing import Any

    class IProjectCRUD(ABC):
        @abstractmethod
        async def create(self, data: dict) -> Any:
            pass

        @abstractmethod
        async def update(self, entity_id: int, data: dict) -> Any:
            pass

        @abstractmethod
        async def delete(self, entity_id: int) -> None:
            pass
    ```

### Fase 3: Implementación de Módulos

1.  Dentro del directorio `modules`, crear implementaciones concretas para cada interfaz. Cada módulo se centrará en una única responsabilidad.

    *Ejemplo: `crud_operations.py`*

    ```python
    from .interfaces.i_project_crud import IProjectCRUD
    from typing import Any

    class CRUDOperations(IProjectCRUD):
        def __init__(self, session):
            self.session = session

        async def create(self, data: dict) -> Any:
            # Lógica para crear un proyecto
            pass

        async def update(self, entity_id: int, data: dict) -> Any:
            # Lógica para actualizar un proyecto
            pass

        async def delete(self, entity_id: int) -> None:
            # Lógica para eliminar un proyecto
            pass
    ```

### Fase 4: Creación de la Fachada del Repositorio

1.  Crear el archivo `<entity>_repository_facade.py`. Esta clase será el punto de entrada único para interactuar con el repositorio.

2.  La fachada recibirá una sesión de base de datos y compondrá los diferentes módulos de implementación.

    *Ejemplo: `project_repository_facade.py`*

    ```python
    from .modules.crud_operations import CRUDOperations
    from .modules.query_operations import QueryOperations

    class ProjectRepositoryFacade:
        def __init__(self, session):
            self.crud = CRUDOperations(session)
            self.query = QueryOperations(session)

        # Métodos de la fachada que delegan a los módulos
        async def create_project(self, data: dict) -> dict:
            return await self.crud.create(data)

        async def find_project_by_name(self, name: str) -> dict:
            return await self.query.find_by_name(name)
    ```

### Fase 5: Migración de la Lógica Existente

1.  Mover la lógica de los archivos monolíticos existentes (p. ej., `project_repository.py`, `project_query_builder.py`) a los nuevos módulos.

2.  Asegurarse de que cada método se mueva al módulo correspondiente a su responsabilidad (CRUD, consultas, estadísticas, etc.).

### Fase 6: Eliminación de Archivos Antiguos

1.  Una vez que toda la lógica se haya migrado y las pruebas pasen correctamente, eliminar los archivos monolíticos antiguos.

## 4. Beneficios de la Nueva Arquitectura

*   **Bajo Acoplamiento:** Los módulos son independientes y se pueden modificar sin afectar a otros.
*   **Alta Cohesión:** Cada módulo tiene una única responsabilidad bien definida.
*   **Reutilización de Código:** Las interfaces y módulos se pueden reutilizar en diferentes contextos.
*   **Mantenibilidad:** Es más fácil encontrar y corregir errores en módulos pequeños y enfocados.
*   **Testabilidad:** Los módulos se pueden probar de forma aislada.