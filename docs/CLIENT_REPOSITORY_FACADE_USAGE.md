# Guía de Uso del ClientRepositoryFacade

## Descripción General

El `ClientRepositoryFacade` es la interfaz principal y unificada para todas las operaciones relacionadas con clientes en el sistema Planificador. Este facade encapsula y coordina múltiples componentes especializados, proporcionando una API simple y coherente.

## Arquitectura del Sistema

### Componentes Integrados

El facade integra los siguientes componentes especializados:

- **ClientCRUDOperations**: Operaciones básicas de creación, lectura, actualización y eliminación
- **ClientQueryBuilder**: Construcción de consultas complejas y filtros avanzados
- **ClientValidator**: Validación de datos y reglas de negocio
- **ClientDateOperations**: Operaciones especializadas en fechas y tiempo
- **ClientStatistics**: Generación de estadísticas y métricas de clientes

### Beneficios del Patrón Facade

1. **Interfaz Unificada**: Un solo punto de acceso para todas las operaciones de cliente
2. **Simplicidad**: Oculta la complejidad de múltiples componentes especializados
3. **Mantenibilidad**: Cambios internos no afectan el código cliente
4. **Consistencia**: Garantiza el uso correcto de los componentes subyacentes
5. **Testabilidad**: Facilita las pruebas unitarias y de integración

## Instalación y Configuración

### Dependencias Requeridas

```python
from sqlalchemy.ext.asyncio import AsyncSession
from planificador.database.repositories.client.client_repository_facade import ClientRepositoryFacade
```

### Inicialización

```python
# Crear una instancia del facade
facade = ClientRepositoryFacade(session=async_session)
```

## Operaciones Disponibles

### 1. Operaciones CRUD Básicas

#### Crear Cliente

```python
# Crear un nuevo cliente
client_data = {
    "name": "Empresa ABC",
    "email": "contacto@empresaabc.com",
    "phone": "+56912345678",
    "address": "Av. Principal 123",
    "is_active": True
}

new_client = await facade.create_client(client_data)
```

#### Crear Cliente con Validación Pendulum

```python
# Crear cliente con validación avanzada de fechas
client_data_with_dates = {
    "name": "Empresa XYZ",
    "email": "info@empresaxyz.com",
    "phone": "+56987654321",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
}

new_client = await facade.create_client_with_pendulum_validation(client_data_with_dates)
```

#### Obtener Cliente por ID

```python
# Buscar cliente por ID
client = await facade.get_client_by_id(client_id=1)
if client:
    print(f"Cliente encontrado: {client.name}")
```

#### Actualizar Cliente

```python
# Actualizar datos del cliente
update_data = {
    "email": "nuevo_email@empresa.com",
    "phone": "+56999888777"
}

updated_client = await facade.update_client(client_id=1, client_data=update_data)
```

#### Eliminar Cliente

```python
# Eliminar cliente (soft delete)
result = await facade.delete_client(client_id=1)
if result:
    print("Cliente eliminado exitosamente")
```

### 2. Consultas y Filtros Avanzados

#### Buscar por Nombre

```python
# Buscar cliente por nombre exacto
client = await facade.get_client_by_name("Empresa ABC")
```

#### Verificar Existencia por Nombre

```python
# Verificar si existe un cliente con ese nombre
exists = await facade.name_exists("Empresa ABC")
if exists:
    print("El nombre ya está en uso")
```

#### Verificar Existencia por Email

```python
# Verificar si existe un cliente con ese email
exists = await facade.email_exists("contacto@empresa.com")
```

#### Obtener Clientes Activos

```python
# Obtener todos los clientes activos
active_clients = await facade.get_active_clients()
print(f"Clientes activos: {len(active_clients)}")
```

#### Obtener Clientes por Rango de Fechas

```python
import pendulum

# Obtener clientes creados en un rango de fechas
start_date = pendulum.parse("2024-01-01")
end_date = pendulum.parse("2024-12-31")

clients = await facade.get_clients_by_date_range(start_date, end_date)
```

### 3. Validaciones

#### Validar Datos de Cliente

```python
# Validar datos antes de crear/actualizar
try:
    await facade.validate_client_data(client_data)
    print("Datos válidos")
except ClientValidationError as e:
    print(f"Error de validación: {e.message}")
```

#### Validar Formato de Email

```python
# Validar formato de email
is_valid = await facade.validate_email_format("test@example.com")
if is_valid:
    print("Email válido")
```

#### Validar Día Laboral

```python
import pendulum

# Validar si una fecha es día laboral
date = pendulum.now()
is_business_day = await facade.validate_business_day(date)
```

### 4. Operaciones de Fechas

#### Calcular Días Laborales

```python
# Calcular días laborales entre dos fechas
start = pendulum.parse("2024-01-01")
end = pendulum.parse("2024-01-31")

business_days = await facade.calculate_business_days_between(start, end)
print(f"Días laborales: {business_days}")
```

#### Obtener Próximo Día Laboral

```python
# Obtener el próximo día laboral desde una fecha
date = pendulum.now()
next_business_day = await facade.get_next_business_day(date)
```

### 5. Estadísticas y Métricas

#### Obtener Estadísticas de Cliente

```python
# Obtener estadísticas completas de un cliente
stats = await facade.get_client_statistics(client_id=1)
print(f"Estadísticas: {stats}")
```

#### Top Clientes por Actividad

```python
# Obtener los clientes más activos
top_clients = await facade.get_top_clients_by_activity(limit=10)
for client in top_clients:
    print(f"Cliente: {client.name}, Actividad: {client.activity_score}")
```

## Manejo de Errores

### Excepciones Comunes

```python
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientNotFoundError,
    ClientValidationError,
    ClientAlreadyExistsError
)

try:
    client = await facade.get_client_by_id(999)
except ClientNotFoundError:
    print("Cliente no encontrado")
except ClientValidationError as e:
    print(f"Error de validación: {e.message}")
except Exception as e:
    print(f"Error inesperado: {e}")
```

## Ejemplos de Uso Completos

### Ejemplo 1: Flujo Completo de Creación

```python
async def create_new_client_workflow():
    """Flujo completo para crear un nuevo cliente."""
    facade = ClientRepositoryFacade(session=session)
    
    client_data = {
        "name": "Nueva Empresa",
        "email": "contacto@nuevaempresa.com",
        "phone": "+56912345678",
        "address": "Calle Falsa 123"
    }
    
    try:
        # 1. Validar que el nombre no exista
        if await facade.name_exists(client_data["name"]):
            raise ClientAlreadyExistsError("El nombre ya está en uso")
        
        # 2. Validar que el email no exista
        if await facade.email_exists(client_data["email"]):
            raise ClientAlreadyExistsError("El email ya está en uso")
        
        # 3. Validar formato de datos
        await facade.validate_client_data(client_data)
        
        # 4. Crear el cliente
        new_client = await facade.create_client(client_data)
        
        print(f"Cliente creado exitosamente: {new_client.id}")
        return new_client
        
    except (ClientValidationError, ClientAlreadyExistsError) as e:
        print(f"Error en la creación: {e.message}")
        return None
```

### Ejemplo 2: Reporte de Actividad

```python
async def generate_activity_report():
    """Generar reporte de actividad de clientes."""
    facade = ClientRepositoryFacade(session=session)
    
    # Obtener clientes activos
    active_clients = await facade.get_active_clients()
    
    # Obtener top 5 clientes más activos
    top_clients = await facade.get_top_clients_by_activity(limit=5)
    
    # Generar estadísticas para cada cliente top
    report = {
        "total_active_clients": len(active_clients),
        "top_clients": []
    }
    
    for client in top_clients:
        stats = await facade.get_client_statistics(client.id)
        report["top_clients"].append({
            "name": client.name,
            "email": client.email,
            "statistics": stats
        })
    
    return report
```

## Mejores Prácticas

### 1. Gestión de Sesiones

```python
# Usar context manager para gestión automática de sesiones
async with AsyncSession(engine) as session:
    facade = ClientRepositoryFacade(session=session)
    # Realizar operaciones
    await session.commit()
```

### 2. Validación Proactiva

```python
# Siempre validar antes de operaciones críticas
await facade.validate_client_data(data)
await facade.validate_email_format(email)
```

### 3. Manejo de Errores Específicos

```python
# Capturar excepciones específicas para mejor UX
try:
    result = await facade.some_operation()
except ClientNotFoundError:
    # Manejar cliente no encontrado
except ClientValidationError:
    # Manejar error de validación
except Exception:
    # Manejar errores inesperados
```

### 4. Logging Estructurado

```python
from loguru import logger

# Usar logging para trazabilidad
logger.info(f"Creando cliente: {client_data['name']}")
result = await facade.create_client(client_data)
logger.success(f"Cliente creado con ID: {result.id}")
```

## Consideraciones de Performance

1. **Conexiones de BD**: Reutilizar sesiones cuando sea posible
2. **Consultas Batch**: Usar operaciones en lote para múltiples registros
3. **Índices**: Asegurar índices apropiados en campos de búsqueda frecuente
4. **Caching**: Considerar cache para consultas frecuentes de solo lectura

## Migración desde Repositorio Legacy

### Antes (Repositorio Monolítico)

```python
# Código legacy
repo = ClientRepository(session)
client = await repo.create_client(data)
stats = await repo.get_statistics(client.id)
```

### Después (Facade Modular)

```python
# Código con facade
facade = ClientRepositoryFacade(session)
client = await facade.create_client(data)
stats = await facade.get_client_statistics(client.id)
```

## Conclusión

El `ClientRepositoryFacade` proporciona una interfaz unificada y potente para todas las operaciones de cliente, manteniendo la simplicidad en el uso mientras ofrece funcionalidad avanzada a través de sus componentes especializados. Su diseño modular facilita el mantenimiento y la extensibilidad del sistema.