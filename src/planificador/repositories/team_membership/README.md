# Repositorio TeamMembership

## Descripción

El repositorio `TeamMembership` proporciona una interfaz completa para la gestión de membresías de equipos en el sistema de planificación. Implementa el patrón Repository con un diseño modular que separa las responsabilidades en diferentes módulos especializados.

## Arquitectura

### Patrón Facade
El repositorio utiliza el patrón Facade a través de `TeamMembershipRepositoryFacade`, que proporciona una interfaz unificada para todas las operaciones.

### Módulos Especializados

1. **CRUD Module** (`crud_module.py`): Operaciones básicas de creación, lectura, actualización y eliminación
2. **Query Module** (`query_module.py`): Operaciones de consulta y búsqueda avanzada
3. **Relationship Module** (`relationship_module.py`): Gestión de relaciones entre entidades
4. **Statistics Module** (`statistics_module.py`): Análisis estadístico y métricas
5. **Validation Module** (`validation_module.py`): Validación de datos y reglas de negocio

### Interfaces
Cada módulo implementa una interfaz específica que define su contrato:
- `ITeamMembershipCrudOperations`
- `ITeamMembershipQueryOperations`
- `ITeamMembershipRelationshipOperations`
- `ITeamMembershipStatisticsOperations`
- `ITeamMembershipValidationOperations`

## Instalación y Configuración

### Dependencias
```python
from sqlalchemy.ext.asyncio import AsyncSession
from planificador.repositories.team_membership import TeamMembershipRepositoryFacade
```

### Inicialización
```python
# Crear instancia del repositorio
async def create_repository(session: AsyncSession):
    repository = TeamMembershipRepositoryFacade(session)
    return repository
```

## Uso Básico

### Crear una Membresía
```python
from planificador.models.team_membership import MembershipRole
from datetime import date

# Datos de la nueva membresía
membership_data = {
    'employee_id': 1,
    'team_id': 1,
    'role': MembershipRole.MEMBER,
    'start_date': date.today(),
    'is_active': True
}

# Crear membresía
membership = await repository.create_membership(membership_data)
print(f"Membresía creada: {membership.id}")
```

### Consultar Membresías
```python
# Obtener por ID
membership = await repository.get_by_id(1)

# Obtener todas las membresías de un empleado
employee_memberships = await repository.get_by_employee_id(1)

# Obtener todas las membresías de un equipo
team_memberships = await repository.get_by_team_id(1)

# Obtener membresías activas
active_memberships = await repository.get_active_memberships()

# Búsqueda con filtros
filters = {
    'role': MembershipRole.LEAD,
    'is_active': True
}
leadership_memberships = await repository.search_memberships(filters)
```

### Actualizar Membresías
```python
# Actualizar datos generales
updates = {
    'role': MembershipRole.LEAD,
    'start_date': date(2024, 1, 1)
}
updated_membership = await repository.update_membership(1, updates)

# Cambiar rol específicamente
updated_membership = await repository.update_membership_role(1, MembershipRole.SUPERVISOR)

# Activar/Desactivar
await repository.activate_membership(1)
await repository.deactivate_membership(1)

# Finalizar membresía
await repository.end_membership(1, end_date=date.today())
```

## Operaciones Avanzadas

### Gestión de Relaciones
```python
# Obtener membresía con relaciones cargadas
membership_with_relations = await repository.get_membership_with_relations(
    membership_id=1,
    load_employee=True,
    load_team=True
)

# Transferir empleado entre equipos
old_membership, new_membership = await repository.transfer_employee_to_team(
    employee_id=1,
    from_team_id=1,
    to_team_id=2,
    new_role=MembershipRole.MEMBER,
    transfer_date=date.today()
)

# Detectar conflictos de membresías
conflicts = await repository.get_membership_conflicts(employee_id=1)
for membership1, membership2 in conflicts:
    print(f"Conflicto entre membresías {membership1.id} y {membership2.id}")
```

### Análisis Estadístico
```python
# Estadísticas básicas
active_count = await repository.count_by_status(is_active=True)
lead_count = await repository.count_by_role(MembershipRole.LEAD)

# Estadísticas de duración
duration_stats = await repository.get_membership_duration_stats()
print(f"Duración promedio: {duration_stats['average_duration_days']} días")

# Distribución de tamaños de equipos
size_distribution = await repository.get_team_size_distribution()
print(f"Tamaño promedio de equipo: {size_distribution['average_size']}")

# Tendencias temporales
trends = await repository.get_membership_trends(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 12, 31),
    granularity='month'
)

# Métricas de rotación
turnover = await repository.get_turnover_rate(team_id=1, period_months=12)
retention = await repository.get_retention_rate(team_id=1, period_months=12)
```

### Validaciones
```python
# Validar datos de membresía
membership_data = {
    'employee_id': 1,
    'team_id': 1,
    'role': MembershipRole.MEMBER,
    'start_date': date.today()
}

is_valid, errors = await repository.validate_membership_data(membership_data)
if not is_valid:
    print(f"Errores de validación: {errors}")

# Validar solapamiento
no_overlap, overlapping_memberships = await repository.validate_membership_overlap(
    employee_id=1,
    start_date=date.today(),
    end_date=date(2024, 12, 31)
)

# Validar asignación de liderazgo
valid_leadership, leadership_errors = await repository.validate_leadership_assignment(
    team_id=1,
    role=MembershipRole.LEAD
)

# Validar capacidad del equipo
within_capacity, capacity_stats = await repository.validate_team_capacity(
    team_id=1,
    max_capacity=50
)
```

## Manejo de Errores

### Excepciones Específicas
El repositorio utiliza excepciones específicas para diferentes tipos de errores:

```python
from planificador.exceptions.repository import TeamMembershipRepositoryError
from planificador.exceptions.validation import ValidationError

try:
    membership = await repository.create_membership(invalid_data)
except ValidationError as e:
    print(f"Error de validación: {e.message}")
    print(f"Detalles: {e.details}")
except TeamMembershipRepositoryError as e:
    print(f"Error del repositorio: {e.message}")
    print(f"Operación: {e.operation}")
    print(f"Entidad: {e.entity_type}")
```

### Logging
Todas las operaciones incluyen logging estructurado:

```python
from loguru import logger

# El repositorio registra automáticamente:
# - Operaciones exitosas (nivel DEBUG/INFO)
# - Errores y excepciones (nivel ERROR)
# - Métricas de performance (nivel DEBUG)
```

## Ejemplos de Casos de Uso

### Caso 1: Incorporación de Nuevo Empleado
```python
async def onboard_employee(employee_id: int, team_id: int):
    """Incorpora un nuevo empleado a un equipo."""
    
    # Validar capacidad del equipo
    within_capacity, stats = await repository.validate_team_capacity(team_id)
    if not within_capacity:
        raise ValueError(f"Equipo sin capacidad: {stats}")
    
    # Crear membresía
    membership_data = {
        'employee_id': employee_id,
        'team_id': team_id,
        'role': MembershipRole.MEMBER,
        'start_date': date.today(),
        'is_active': True
    }
    
    # Validar datos
    is_valid, errors = await repository.validate_membership_data(membership_data)
    if not is_valid:
        raise ValidationError(f"Datos inválidos: {errors}")
    
    # Crear membresía
    membership = await repository.create_membership(membership_data)
    return membership
```

### Caso 2: Promoción a Liderazgo
```python
async def promote_to_leadership(membership_id: int, new_role: MembershipRole):
    """Promueve un miembro a un rol de liderazgo."""
    
    # Obtener membresía actual
    membership = await repository.get_by_id(membership_id)
    if not membership:
        raise ValueError("Membresía no encontrada")
    
    # Validar asignación de liderazgo
    valid, errors = await repository.validate_leadership_assignment(
        membership.team_id,
        new_role,
        exclude_membership_id=membership_id
    )
    
    if not valid:
        raise ValidationError(f"No se puede asignar liderazgo: {errors}")
    
    # Actualizar rol
    updated_membership = await repository.update_membership_role(membership_id, new_role)
    return updated_membership
```

### Caso 3: Análisis de Equipo
```python
async def analyze_team_performance(team_id: int):
    """Analiza el rendimiento y composición de un equipo."""
    
    # Obtener composición actual
    composition = await repository.get_team_composition_analysis(team_id)
    
    # Obtener métricas de estabilidad
    stability = await repository.get_team_stability_metrics(team_id)
    
    # Obtener estadísticas de rotación
    turnover = await repository.get_turnover_rate(team_id, period_months=12)
    retention = await repository.get_retention_rate(team_id, period_months=12)
    
    return {
        'composition': composition,
        'stability': stability,
        'turnover': turnover,
        'retention': retention
    }
```

## Mejores Prácticas

### 1. Gestión de Sesiones
```python
# Siempre usar context managers para sesiones
async with async_session() as session:
    repository = TeamMembershipRepositoryFacade(session)
    
    # Realizar operaciones
    membership = await repository.create_membership(data)
    
    # La sesión se cierra automáticamente
```

### 2. Validación Previa
```python
# Siempre validar antes de operaciones críticas
is_valid, errors = await repository.validate_membership_data(data)
if not is_valid:
    # Manejar errores antes de proceder
    handle_validation_errors(errors)

# Proceder con la operación
membership = await repository.create_membership(data)
```

### 3. Manejo de Transacciones
```python
async def complex_membership_operation():
    async with async_session() as session:
        async with session.begin():  # Transacción automática
            repository = TeamMembershipRepositoryFacade(session)
            
            # Múltiples operaciones en una transacción
            membership1 = await repository.create_membership(data1)
            membership2 = await repository.update_membership(id2, updates)
            
            # Si cualquier operación falla, se hace rollback automático
```

### 4. Logging y Monitoreo
```python
from loguru import logger

# Configurar logging específico para el repositorio
logger.add(
    "team_membership_operations.log",
    filter=lambda record: "TeamMembership" in record["extra"].get("module", ""),
    level="INFO"
)
```

## Performance y Optimización

### Consultas Eficientes
```python
# Usar paginación para grandes conjuntos de datos
memberships = await repository.get_all(limit=100, offset=0)

# Cargar relaciones solo cuando sea necesario
membership = await repository.get_membership_with_relations(
    membership_id=1,
    load_employee=True,  # Solo si necesitas datos del empleado
    load_team=False      # Evitar carga innecesaria
)
```

### Operaciones en Lote
```python
# Para múltiples validaciones, usar operaciones específicas
employee_ids = [1, 2, 3, 4, 5]
for employee_id in employee_ids:
    is_valid = await repository.validate_employee_id(employee_id)
    # Procesar resultado
```

## Troubleshooting

### Problemas Comunes

1. **Error de Solapamiento de Membresías**
   ```python
   # Verificar solapamientos antes de crear
   no_overlap, overlapping = await repository.validate_membership_overlap(
       employee_id, start_date, end_date
   )
   ```

2. **Límites de Liderazgo Excedidos**
   ```python
   # Validar antes de asignar roles de liderazgo
   valid, errors = await repository.validate_leadership_assignment(team_id, role)
   ```

3. **Problemas de Capacidad**
   ```python
   # Verificar capacidad antes de agregar miembros
   within_capacity, stats = await repository.validate_team_capacity(team_id)
   ```

## Extensibilidad

### Agregar Nuevas Validaciones
```python
# Extender el módulo de validación
class CustomTeamMembershipValidationModule(TeamMembershipValidationModule):
    async def validate_custom_rule(self, data: Dict[str, Any]) -> bool:
        # Implementar validación personalizada
        pass
```

### Métricas Personalizadas
```python
# Extender el módulo de estadísticas
class CustomTeamMembershipStatisticsModule(TeamMembershipStatisticsModule):
    async def get_custom_metrics(self) -> Dict[str, Any]:
        # Implementar métricas personalizadas
        pass
```

## Contribución

Para contribuir al repositorio:

1. Seguir las convenciones de código establecidas
2. Agregar tests para nueva funcionalidad
3. Documentar cambios en este README
4. Usar logging estructurado para todas las operaciones
5. Implementar manejo robusto de errores

## Changelog

### v1.0.0 (2024-01-XX)
- Implementación inicial del repositorio TeamMembership
- Módulos CRUD, Query, Relationship, Statistics y Validation
- Facade pattern para interfaz unificada
- Documentación completa y ejemplos de uso