# Planificador - Módulo de Repositorio de Empleados

Este módulo está diseñado para la gestión integral de los empleados dentro de la aplicación, abarcando desde operaciones CRUD básicas hasta análisis estadísticos complejos y gestión de relaciones con otras entidades como equipos y proyectos.

## Arquitectura y Diseño

Siguiendo el patrón de la aplicación, el módulo de empleados utiliza una **arquitectura modular basada en el patrón Facade**. Esta estructura promueve una clara separación de responsabilidades, lo que facilita el mantenimiento, la escalabilidad y las pruebas del código.

### Componentes Principales

#### 1. `EmployeeRepositoryFacade`
Es el punto de entrada único para todas las operaciones relacionadas con los empleados. Orquesta las llamadas a los módulos especializados y unifica la interfaz de acceso a los datos.

- **Más de 60 funciones públicas** categorizadas por funcionalidad.
- **Delegación** a módulos internos para cada tipo de operación.
- **Manejo de errores** centralizado y logging estructurado.
- **Type hints** y documentación completa para un código robusto y legible.
- Soporte completo para operaciones **asíncronas**.

#### 2. Módulos Especializados
Cada módulo tiene una responsabilidad única y bien definida:

- **`CrudOperations`**: Operaciones básicas de Crear, Actualizar y Eliminar.
- **`DateOperations`**: Lógica de negocio relacionada con fechas (contratación, antigüedad).
- **`QueryOperations`**: Consultas y búsquedas, desde las más simples a las más complejas.
- **`RelationshipOperations`**: Gestión de las relaciones del empleado con equipos, proyectos y vacaciones.
- **`StatisticsOperations`**: Cálculos estadísticos, métricas y agregaciones.
- **`ValidationOperations`**: Reglas de validación para los datos de entrada.

#### 3. Interfaces Especializadas
Cada módulo implementa una interfaz que define un contrato claro, permitiendo la inversión de dependencias y facilitando las pruebas unitarias.

- `IEmployeeCrudOperations`
- `IEmployeeDateOperations`
- `IEmployeeQueryOperations`
- `IEmployeeRelationshipOperations`
- `IEmployeeStatisticsOperations`
- `IEmployeeValidationOperations`

### Funcionalidades por Categoría

Para una descripción detallada de todas las funciones, consulta el documento:
**[Funciones Disponibles en `EmployeeRepositoryFacade`](./employee_available_functions.md)**

## Características Principales del Módulo

### 🔍 Consultas y Búsquedas Flexibles
- Búsqueda por ID, nombre completo, email, código de empleado.
- Filtros por estado, departamento, posición y rango salarial.
- Búsqueda por habilidades (`skills`).
- Búsqueda avanzada con múltiples filtros combinados.

### 📊 Análisis Estadístico Avanzado
- Conteo de empleados por estado, departamento y posición.
- Estadísticas salariales (mínimo, máximo, promedio).
- Distribución de contrataciones a lo largo del tiempo.
- Estadísticas de participación en equipos y proyectos.
- Análisis de solicitudes de vacaciones.
- Distribución de habilidades más comunes en la organización.
- Resumen integral de métricas clave.

### ✅ Validaciones y Reglas de Negocio
- Validación de datos antes de la creación y actualización.
- Validación de formato para campos como `skills` (JSON).
- Verificación de unicidad para `full_name`, `email` y `employee_code`.

### 🔗 Gestión Completa de Relaciones
- Obtención de equipos, proyectos y vacaciones de un empleado.
- Verificación de pertenencia a equipos o asignación a proyectos.
- Búsqueda de empleados por equipo o proyecto.
- Carga de todas las relaciones de un empleado en una sola consulta.
- Verificación de dependencias antes de la eliminación.

### 📅 Operaciones Basadas en Fechas
- Búsqueda de empleados contratados en la semana o mes actual.
- Filtro de contrataciones solo en días laborables.
- Cálculo y consulta por antigüedad (tenure).
- Formateo de fechas personalizable.

## Tech Stack

- **Python 3.13**
- **SQLAlchemy**: ORM para la interacción con la base de datos.
- **Pydantic**: Para la validación de datos.
- **Loguru**: Para logging estructurado.
- **Pendulum**: Para el manejo avanzado de fechas y horas.
- **Pytest**: Para tests unitarios y de integración.
- **Poetry**: Para la gestión de dependencias.

## Estructura del Módulo de Empleados

```
├── employee/
│   ├── __init__.py
│   ├── README.md
│   ├── employee_available_functions.md
│   ├── employee_repository_facade.py
│   │
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── crud_interface.py
│   │   ├── date_interface.py
│   │   ├── query_interface.py
│   │   ├── relationship_interface.py
│   │   ├── statistics_interface.py
│   │   └── validation_interface.py
│   │
│   └── modules/
│       ├── __init__.py
│       ├── crud_operations.py
│       ├── date_operations.py
│       ├── query_operations.py
│       ├── relationship_operations.py
│       ├── statistics_operations.py
│       └── validation_operations.py
```

## Uso del Módulo

### Inicialización
```python
from planificador.repositories.employee import EmployeeRepositoryFacade
from planificador.database.session import get_async_session

async def main():
    async with get_async_session() as session:
        employee_repo = EmployeeRepositoryFacade(session)
        
        # Ejemplo de uso
        active_employees = await employee_repo.get_active_employees()
        print(f"Hay {len(active_employees)} empleados activos.")
```

### Ejemplo de Operaciones
```python
# Obtener estadísticas de salarios
stats = await employee_repo.get_salary_statistics()
print(f"Salario promedio: {stats.get('avg_salary')}")

# Búsqueda avanzada
filters = {"department": "IT", "status": "ACTIVE"}
it_employees = await employee_repo.advanced_search(filters)

# Validar datos antes de crear un empleado
try:
    employee_data = {
        "full_name": "Nuevo Empleado", 
        "email": "nuevo@example.com",
        # ... otros datos
    }
    employee_repo.validate_create_data(employee_data)
    new_employee = await employee_repo.create_employee(employee_data)
    print(f"Empleado {new_employee.full_name} creado con éxito.")
except ValueError as e:
    print(f"Error de validación: {e}")
```