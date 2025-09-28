# Patrones y Arquitectura de Servicios de Dominio

**Fecha de Creación:** Enero 2025  
**Versión:** 1.0.0  
**Documento Complementario:** ESTRATEGIA_SERVICIOS_DOMINIO.md

## Descripción General

Este documento define los **patrones de diseño específicos** y la **arquitectura detallada** para la implementación de servicios de dominio en el sistema Planificador. Complementa la estrategia general proporcionando guías técnicas concretas y ejemplos de implementación.

## Patrones de Diseño Fundamentales

### 1. **Patrón Service Layer (Capa de Servicios)**

#### Definición
Los servicios de dominio actúan como una capa intermedia que encapsula la lógica de negocio compleja y coordina operaciones entre múltiples repositorios.

#### Estructura
```python
# Patrón básico de Service Layer
class DomainService:
    def __init__(self, repositories: Dict[str, Repository]):
        self._repositories = repositories
        self._logger = logger
    
    async def business_operation(self, data: BusinessData) -> BusinessResult:
        # 1. Validación de entrada
        await self._validate_input(data)
        
        # 2. Lógica de negocio
        result = await self._execute_business_logic(data)
        
        # 3. Persistencia coordinada
        await self._persist_changes(result)
        
        # 4. Eventos de dominio (opcional)
        await self._emit_domain_events(result)
        
        return result
```

#### Beneficios
- **Separación de responsabilidades**: Lógica de negocio separada de acceso a datos
- **Reutilización**: Operaciones complejas centralizadas
- **Testabilidad**: Lógica de negocio fácilmente testeable
- **Transaccionalidad**: Coordinación de operaciones múltiples

### 2. **Patrón Facade para Servicios**

#### Definición
Cada servicio de dominio actúa como una facade que simplifica el acceso a múltiples repositorios y operaciones complejas.

#### Implementación
```python
class ProjectDomainService(BaseDomainService):
    """
    Facade que simplifica operaciones complejas de proyectos
    coordinando múltiples repositorios.
    """
    
    def _initialize_repositories(self) -> None:
        self._project_repo = ProjectRepositoryFacade(self._session)
        self._client_repo = ClientRepositoryFacade(self._session)
        self._employee_repo = EmployeeRepositoryFacade(self._session)
        self._assignment_repo = ProjectAssignmentRepositoryFacade(self._session)
    
    async def create_project_with_team(
        self, 
        project_data: ProjectCreate,
        team_assignments: List[TeamAssignment]
    ) -> ProjectWithTeamResponse:
        """
        Operación compleja que coordina múltiples repositorios
        para crear un proyecto con su equipo inicial.
        """
        async with self._session.begin():
            # Crear proyecto
            project = await self._project_repo.create_project(project_data.model_dump())
            
            # Validar disponibilidad del equipo
            await self._validate_team_availability(team_assignments, project.start_date)
            
            # Crear asignaciones
            assignments = []
            for assignment in team_assignments:
                assignment_data = {
                    "project_id": project.id,
                    "employee_id": assignment.employee_id,
                    "role": assignment.role,
                    "allocation_percentage": assignment.allocation_percentage
                }
                assignment_obj = await self._assignment_repo.create_assignment(assignment_data)
                assignments.append(assignment_obj)
            
            # Actualizar estadísticas del proyecto
            await self._project_repo.update_project_statistics(project.id)
            
            return ProjectWithTeamResponse(
                project=project,
                assignments=assignments,
                team_size=len(assignments)
            )
```

### 3. **Patrón Strategy para Lógica de Negocio**

#### Definición
Permite intercambiar algoritmos de lógica de negocio sin modificar el servicio principal.

#### Implementación
```python
from abc import ABC, abstractmethod
from typing import Protocol

class PlanningStrategy(Protocol):
    """Estrategia para algoritmos de planificación."""
    
    async def calculate_optimal_assignments(
        self, 
        project_requirements: List[ProjectRequirement],
        available_resources: List[EmployeeAvailability]
    ) -> List[OptimalAssignment]:
        """Calcula asignaciones óptimas según la estrategia."""
        ...

class CapacityBasedPlanningStrategy:
    """Estrategia basada en capacidad disponible."""
    
    async def calculate_optimal_assignments(
        self, 
        project_requirements: List[ProjectRequirement],
        available_resources: List[EmployeeAvailability]
    ) -> List[OptimalAssignment]:
        # Algoritmo basado en capacidad
        assignments = []
        for requirement in project_requirements:
            best_match = self._find_best_capacity_match(requirement, available_resources)
            if best_match:
                assignments.append(OptimalAssignment(
                    employee_id=best_match.employee_id,
                    project_id=requirement.project_id,
                    allocation_score=best_match.capacity_score
                ))
        return assignments

class SkillBasedPlanningStrategy:
    """Estrategia basada en habilidades requeridas."""
    
    async def calculate_optimal_assignments(
        self, 
        project_requirements: List[ProjectRequirement],
        available_resources: List[EmployeeAvailability]
    ) -> List[OptimalAssignment]:
        # Algoritmo basado en habilidades
        assignments = []
        for requirement in project_requirements:
            best_match = self._find_best_skill_match(requirement, available_resources)
            if best_match:
                assignments.append(OptimalAssignment(
                    employee_id=best_match.employee_id,
                    project_id=requirement.project_id,
                    allocation_score=best_match.skill_score
                ))
        return assignments

class PlanningDomainService(BaseDomainService):
    """Servicio que utiliza diferentes estrategias de planificación."""
    
    def __init__(self, session: AsyncSession, planning_strategy: PlanningStrategy):
        super().__init__(session)
        self._planning_strategy = planning_strategy
    
    async def optimize_resource_allocation(
        self, 
        project_ids: List[int]
    ) -> ResourceAllocationResult:
        """Optimiza asignación de recursos usando la estrategia configurada."""
        
        # Obtener requerimientos de proyectos
        requirements = await self._get_project_requirements(project_ids)
        
        # Obtener recursos disponibles
        available_resources = await self._get_available_resources()
        
        # Aplicar estrategia de planificación
        optimal_assignments = await self._planning_strategy.calculate_optimal_assignments(
            requirements, available_resources
        )
        
        # Validar y aplicar asignaciones
        validated_assignments = await self._validate_assignments(optimal_assignments)
        
        return ResourceAllocationResult(
            assignments=validated_assignments,
            optimization_score=self._calculate_optimization_score(validated_assignments)
        )
```

### 4. **Patrón Command para Operaciones Complejas**

#### Definición
Encapsula operaciones complejas como objetos, permitiendo parametrización, cola de ejecución y deshacer operaciones.

#### Implementación
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass

class DomainCommand(ABC):
    """Comando base para operaciones de dominio."""
    
    @abstractmethod
    async def execute(self) -> Any:
        """Ejecuta el comando."""
        pass
    
    @abstractmethod
    async def undo(self) -> Any:
        """Deshace el comando (opcional)."""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Valida que el comando puede ejecutarse."""
        pass

@dataclass
class CreateProjectWithTeamCommand(DomainCommand):
    """Comando para crear proyecto con equipo inicial."""
    
    project_data: ProjectCreate
    team_assignments: List[TeamAssignment]
    service: 'ProjectDomainService'
    
    def __post_init__(self):
        self._created_project_id: Optional[int] = None
        self._created_assignment_ids: List[int] = []
    
    async def execute(self) -> ProjectWithTeamResponse:
        """Ejecuta la creación del proyecto con equipo."""
        if not self.validate():
            raise CommandValidationError("Command validation failed")
        
        result = await self.service.create_project_with_team(
            self.project_data, 
            self.team_assignments
        )
        
        # Guardar IDs para posible rollback
        self._created_project_id = result.project.id
        self._created_assignment_ids = [a.id for a in result.assignments]
        
        return result
    
    async def undo(self) -> None:
        """Deshace la creación del proyecto."""
        if self._created_project_id:
            # Eliminar asignaciones
            for assignment_id in self._created_assignment_ids:
                await self.service._assignment_repo.delete_assignment(assignment_id)
            
            # Eliminar proyecto
            await self.service._project_repo.delete_project(self._created_project_id)
    
    def validate(self) -> bool:
        """Valida que el comando puede ejecutarse."""
        return (
            self.project_data is not None and
            len(self.team_assignments) > 0 and
            all(a.employee_id > 0 for a in self.team_assignments)
        )

class CommandExecutor:
    """Ejecutor de comandos con soporte para rollback."""
    
    def __init__(self):
        self._executed_commands: List[DomainCommand] = []
    
    async def execute_command(self, command: DomainCommand) -> Any:
        """Ejecuta un comando y lo registra para posible rollback."""
        try:
            result = await command.execute()
            self._executed_commands.append(command)
            return result
        except Exception as e:
            # Rollback de comandos ejecutados
            await self._rollback_commands()
            raise e
    
    async def _rollback_commands(self) -> None:
        """Ejecuta rollback de todos los comandos en orden inverso."""
        for command in reversed(self._executed_commands):
            try:
                await command.undo()
            except Exception as e:
                logger.error(f"Error during rollback of command {type(command).__name__}: {e}")
        
        self._executed_commands.clear()
```

### 5. **Patrón Observer para Eventos de Dominio**

#### Definición
Permite notificar a múltiples componentes cuando ocurren eventos importantes en el dominio.

#### Implementación
```python
from typing import List, Callable, Any
from dataclasses import dataclass
from enum import Enum

class DomainEventType(Enum):
    """Tipos de eventos de dominio."""
    CLIENT_CREATED = "client_created"
    PROJECT_STARTED = "project_started"
    PROJECT_COMPLETED = "project_completed"
    EMPLOYEE_ASSIGNED = "employee_assigned"
    WORKLOAD_EXCEEDED = "workload_exceeded"

@dataclass
class DomainEvent:
    """Evento de dominio."""
    event_type: DomainEventType
    entity_id: int
    entity_type: str
    data: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None

class DomainEventHandler(ABC):
    """Handler base para eventos de dominio."""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Maneja el evento de dominio."""
        pass
    
    @abstractmethod
    def can_handle(self, event_type: DomainEventType) -> bool:
        """Determina si puede manejar el tipo de evento."""
        pass

class ProjectCompletionHandler(DomainEventHandler):
    """Handler para eventos de finalización de proyecto."""
    
    def __init__(self, analytics_service: AnalyticsDomainService):
        self._analytics_service = analytics_service
    
    async def handle(self, event: DomainEvent) -> None:
        """Maneja la finalización de un proyecto."""
        if event.event_type == DomainEventType.PROJECT_COMPLETED:
            # Actualizar métricas de proyecto
            await self._analytics_service.update_project_completion_metrics(
                event.entity_id
            )
            
            # Liberar recursos asignados
            await self._analytics_service.release_project_resources(
                event.entity_id
            )
    
    def can_handle(self, event_type: DomainEventType) -> bool:
        return event_type == DomainEventType.PROJECT_COMPLETED

class DomainEventBus:
    """Bus de eventos de dominio."""
    
    def __init__(self):
        self._handlers: List[DomainEventHandler] = []
    
    def register_handler(self, handler: DomainEventHandler) -> None:
        """Registra un handler de eventos."""
        self._handlers.append(handler)
    
    async def publish(self, event: DomainEvent) -> None:
        """Publica un evento a todos los handlers interesados."""
        for handler in self._handlers:
            if handler.can_handle(event.event_type):
                try:
                    await handler.handle(event)
                except Exception as e:
                    logger.error(f"Error handling event {event.event_type}: {e}")

# Uso en servicios de dominio
class ProjectDomainService(BaseDomainService):
    def __init__(self, session: AsyncSession, event_bus: DomainEventBus):
        super().__init__(session)
        self._event_bus = event_bus
    
    async def complete_project(self, project_id: int) -> ProjectResponse:
        """Completa un proyecto y emite evento de dominio."""
        
        # Actualizar estado del proyecto
        project = await self._project_repo.update_project_status(
            project_id, 
            "completed"
        )
        
        # Emitir evento de dominio
        event = DomainEvent(
            event_type=DomainEventType.PROJECT_COMPLETED,
            entity_id=project_id,
            entity_type="Project",
            data={
                "project_name": project.name,
                "completion_date": project.end_date.isoformat(),
                "client_id": project.client_id
            },
            timestamp=datetime.now()
        )
        
        await self._event_bus.publish(event)
        
        return ProjectResponse.model_validate(project)
```

## Arquitectura de Capas Detallada

### Diagrama de Arquitectura
```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│                  (FastAPI Controllers)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Application Layer                           │
│              (API Route Handlers)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Domain Services                           │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│   │   Client    │ │   Project   │ │     Planning        │   │
│   │   Service   │ │   Service   │ │     Service         │   │
│   └─────────────┘ └─────────────┘ └─────────────────────┘   │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│   │  Employee   │ │  Resource   │ │    Analytics        │   │
│   │   Service   │ │ Management  │ │     Service         │   │
│   └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Repository Layer                             │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│   │   Client    │ │   Project   │ │   ProjectAssignment │   │
│   │ Repository  │ │ Repository  │ │    Repository       │   │
│   └─────────────┘ └─────────────┘ └─────────────────────┘   │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│   │  Employee   │ │    Team     │ │      Workload       │   │
│   │ Repository  │ │ Repository  │ │     Repository      │   │
│   └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Data Layer                               │
│              (SQLAlchemy Models)                           │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos
1. **Request**: Controller recibe petición HTTP
2. **Validation**: Validación de entrada con Pydantic
3. **Service Call**: Controller llama al servicio de dominio apropiado
4. **Business Logic**: Servicio ejecuta lógica de negocio
5. **Repository Coordination**: Servicio coordina múltiples repositorios
6. **Data Persistence**: Repositorios persisten cambios
7. **Event Emission**: Servicio emite eventos de dominio (opcional)
8. **Response**: Controller retorna respuesta HTTP

## Patrones de Validación

### 1. **Validación en Capas**
```python
class ClientDomainService(BaseDomainService):
    async def create_client(self, client_data: ClientCreate) -> ClientResponse:
        # Capa 1: Validación de esquema (Pydantic - automática)
        # client_data ya está validado por Pydantic
        
        # Capa 2: Validación de reglas de negocio
        await self._validate_business_rules(client_data)
        
        # Capa 3: Validación de integridad referencial
        await self._validate_referential_integrity(client_data)
        
        # Proceder con la creación
        return await self._create_client_internal(client_data)
    
    async def _validate_business_rules(self, client_data: ClientCreate) -> None:
        """Valida reglas de negocio específicas."""
        # Regla: Código de cliente único
        existing = await self._client_repo.get_client_by_code(client_data.code)
        if existing:
            raise BusinessRuleViolationError(
                f"Client code {client_data.code} already exists"
            )
        
        # Regla: Email válido y único si se proporciona
        if client_data.email:
            if not self._is_valid_email(client_data.email):
                raise ValidationError("Invalid email format")
            
            existing_email = await self._client_repo.get_client_by_email(client_data.email)
            if existing_email:
                raise BusinessRuleViolationError(
                    f"Email {client_data.email} already in use"
                )
    
    async def _validate_referential_integrity(self, client_data: ClientCreate) -> None:
        """Valida integridad referencial."""
        # Validar que el país existe si se especifica
        if client_data.country_id:
            country = await self._country_repo.get_by_id(client_data.country_id)
            if not country:
                raise ValidationError(f"Country {client_data.country_id} not found")
```

### 2. **Validación Condicional**
```python
class ProjectDomainService(BaseDomainService):
    async def assign_employee_to_project(
        self, 
        project_id: int, 
        employee_id: int,
        assignment_data: ProjectAssignmentCreate
    ) -> ProjectAssignmentResponse:
        
        # Obtener entidades
        project = await self._project_repo.get_by_id(project_id)
        employee = await self._employee_repo.get_by_id(employee_id)
        
        # Validaciones condicionales basadas en estado del proyecto
        if project.status == "completed":
            raise BusinessRuleViolationError(
                "Cannot assign employees to completed projects"
            )
        
        if project.status == "planning":
            # En fase de planificación, validaciones más flexibles
            await self._validate_planning_phase_assignment(project, employee, assignment_data)
        elif project.status == "active":
            # En fase activa, validaciones más estrictas
            await self._validate_active_phase_assignment(project, employee, assignment_data)
        
        # Proceder con la asignación
        return await self._create_assignment(project, employee, assignment_data)
```

## Patrones de Transacciones

### 1. **Transacciones Simples**
```python
async def simple_business_operation(self, data: BusinessData) -> BusinessResult:
    """Operación simple con transacción automática."""
    async with self._session.begin():
        # Todas las operaciones dentro de esta transacción
        entity = await self._repo.create_entity(data.entity_data)
        await self._repo.update_related_entity(entity.id, data.related_data)
        
        return BusinessResult(entity=entity)
    # Commit automático al salir del context manager
```

### 2. **Transacciones Complejas con Savepoints**
```python
async def complex_business_operation(self, data: ComplexBusinessData) -> ComplexBusinessResult:
    """Operación compleja con savepoints para rollback parcial."""
    async with self._session.begin():
        results = []
        
        for item in data.items:
            # Crear savepoint antes de cada operación crítica
            savepoint = await self._session.begin_nested()
            
            try:
                # Operación que puede fallar
                result = await self._process_critical_item(item)
                results.append(result)
                
                # Commit del savepoint si todo va bien
                await savepoint.commit()
                
            except CriticalBusinessError as e:
                # Rollback solo de este savepoint
                await savepoint.rollback()
                logger.warning(f"Failed to process item {item.id}: {e}")
                # Continuar con el siguiente item
                continue
        
        return ComplexBusinessResult(results=results)
```

### 3. **Transacciones Distribuidas (Saga Pattern)**
```python
from typing import List, Callable, Any

class SagaStep:
    """Paso de una saga con operación y compensación."""
    
    def __init__(
        self, 
        operation: Callable[[], Any], 
        compensation: Callable[[], Any],
        description: str
    ):
        self.operation = operation
        self.compensation = compensation
        self.description = description
        self.executed = False
        self.result = None

class SagaOrchestrator:
    """Orquestador de sagas para transacciones distribuidas."""
    
    def __init__(self):
        self._steps: List[SagaStep] = []
    
    def add_step(self, step: SagaStep) -> None:
        """Agrega un paso a la saga."""
        self._steps.append(step)
    
    async def execute(self) -> Any:
        """Ejecuta la saga completa."""
        executed_steps = []
        
        try:
            for step in self._steps:
                logger.info(f"Executing saga step: {step.description}")
                step.result = await step.operation()
                step.executed = True
                executed_steps.append(step)
            
            return [step.result for step in executed_steps]
            
        except Exception as e:
            logger.error(f"Saga failed at step '{step.description}': {e}")
            
            # Ejecutar compensaciones en orden inverso
            await self._compensate(executed_steps)
            raise e
    
    async def _compensate(self, executed_steps: List[SagaStep]) -> None:
        """Ejecuta compensaciones en orden inverso."""
        for step in reversed(executed_steps):
            try:
                logger.info(f"Compensating step: {step.description}")
                await step.compensation()
            except Exception as e:
                logger.error(f"Compensation failed for step '{step.description}': {e}")

# Uso en servicios de dominio
class ProjectDomainService(BaseDomainService):
    async def create_project_with_full_setup(
        self, 
        project_data: ProjectCreate,
        team_data: List[TeamAssignment],
        budget_data: BudgetAllocation
    ) -> ProjectSetupResult:
        """Crea proyecto con configuración completa usando saga."""
        
        saga = SagaOrchestrator()
        
        # Paso 1: Crear proyecto
        saga.add_step(SagaStep(
            operation=lambda: self._project_repo.create_project(project_data.model_dump()),
            compensation=lambda: self._project_repo.delete_project(project.id),
            description="Create project"
        ))
        
        # Paso 2: Asignar equipo
        saga.add_step(SagaStep(
            operation=lambda: self._create_team_assignments(project.id, team_data),
            compensation=lambda: self._remove_team_assignments(project.id),
            description="Assign team"
        ))
        
        # Paso 3: Configurar presupuesto
        saga.add_step(SagaStep(
            operation=lambda: self._budget_service.allocate_budget(project.id, budget_data),
            compensation=lambda: self._budget_service.deallocate_budget(project.id),
            description="Allocate budget"
        ))
        
        # Ejecutar saga
        results = await saga.execute()
        
        return ProjectSetupResult(
            project=results[0],
            assignments=results[1],
            budget_allocation=results[2]
        )
```

## Patrones de Cache

### 1. **Cache Decorador**
```python
from functools import wraps
from typing import Optional, Any, Callable
import hashlib
import json

class ServiceCache:
    """Cache simple para servicios de dominio."""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, datetime] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del cache si no ha expirado."""
        if key in self._cache:
            if key in self._ttl and datetime.now() > self._ttl[key]:
                # Expirado
                del self._cache[key]
                del self._ttl[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Establece valor en cache con TTL."""
        self._cache[key] = value
        self._ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def invalidate(self, pattern: str) -> None:
        """Invalida entradas que coincidan con el patrón."""
        keys_to_remove = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self._cache[key]
            if key in self._ttl:
                del self._ttl[key]

def cached_service_method(ttl_seconds: int = 300, cache_key_func: Optional[Callable] = None):
    """Decorador para cachear métodos de servicios de dominio."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            # Generar clave de cache
            if cache_key_func:
                cache_key = cache_key_func(self, *args, **kwargs)
            else:
                # Clave por defecto basada en nombre del método y argumentos
                args_str = json.dumps([str(arg) for arg in args], sort_keys=True)
                kwargs_str = json.dumps(kwargs, sort_keys=True)
                cache_key = f"{self.__class__.__name__}.{func.__name__}:{hashlib.md5((args_str + kwargs_str).encode()).hexdigest()}"
            
            # Intentar obtener del cache
            if hasattr(self, '_cache'):
                cached_result = self._cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Ejecutar método y cachear resultado
            result = await func(self, *args, **kwargs)
            
            if hasattr(self, '_cache'):
                self._cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator

# Uso en servicios
class AnalyticsDomainService(BaseDomainService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._cache = ServiceCache()
    
    @cached_service_method(ttl_seconds=600)  # Cache por 10 minutos
    async def get_project_performance_metrics(self, project_id: int) -> ProjectMetrics:
        """Obtiene métricas de performance del proyecto (cacheado)."""
        # Operación costosa que se beneficia del cache
        return await self._calculate_complex_metrics(project_id)
    
    async def invalidate_project_cache(self, project_id: int) -> None:
        """Invalida cache relacionado con un proyecto específico."""
        self._cache.invalidate(f"project_{project_id}")
```

## Patrones de Testing

### 1. **Test Fixtures para Servicios**
```python
# conftest.py para servicios de dominio

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.services.domain.client import ClientDomainService
from planificador.repositories.client import ClientRepositoryFacade

@pytest.fixture
async def mock_session():
    """Mock de sesión de base de datos."""
    session = AsyncMock(spec=AsyncSession)
    session.begin.return_value.__aenter__ = AsyncMock()
    session.begin.return_value.__aexit__ = AsyncMock()
    return session

@pytest.fixture
async def mock_client_repo():
    """Mock del repositorio de clientes."""
    repo = AsyncMock(spec=ClientRepositoryFacade)
    return repo

@pytest.fixture
async def client_service(mock_session, mock_client_repo):
    """Servicio de dominio de clientes con mocks."""
    service = ClientDomainService(mock_session)
    service._client_repo = mock_client_repo
    return service

@pytest.fixture
def sample_client_data():
    """Datos de ejemplo para tests."""
    return ClientCreate(
        name="Test Client",
        code="TC001",
        email="test@example.com",
        phone="+1234567890"
    )
```

### 2. **Tests de Integración**
```python
# test_client_domain_service_integration.py

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.services.domain.client import ClientDomainService
from planificador.schemas.client import ClientCreate

@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_client_with_project_integration(
    async_session: AsyncSession,
    sample_client_data: ClientCreate
):
    """Test de integración para creación de cliente con proyecto."""
    
    # Arrange
    service = ClientDomainService(async_session)
    project_data = {
        "name": "Initial Project",
        "description": "Test project for new client",
        "start_date": "2025-02-01",
        "estimated_end_date": "2025-06-01"
    }
    
    # Act
    result = await service.create_client_with_initial_project(
        sample_client_data, 
        project_data
    )
    
    # Assert
    assert result.id is not None
    assert result.name == sample_client_data.name
    assert result.code == sample_client_data.code
    
    # Verificar que se creó el proyecto
    projects = await service._project_repo.get_projects_by_client(result.id)
    assert len(projects) == 1
    assert projects[0].name == "Initial Project"
    
    # Verificar integridad referencial
    client_from_db = await service._client_repo.get_client_by_id(result.id)
    assert client_from_db is not None
    assert client_from_db.code == sample_client_data.code
```

### 3. **Tests de Performance**
```python
# test_service_performance.py

import pytest
import asyncio
from time import time
from typing import List

@pytest.mark.asyncio
@pytest.mark.performance
async def test_bulk_client_creation_performance(
    client_service: ClientDomainService,
    generate_client_data: Callable[[int], List[ClientCreate]]
):
    """Test de performance para creación masiva de clientes."""
    
    # Arrange
    client_count = 100
    client_data_list = generate_client_data(client_count)
    
    # Act
    start_time = time()
    
    # Crear clientes en paralelo (limitado)
    semaphore = asyncio.Semaphore(10)  # Máximo 10 concurrentes
    
    async def create_client_with_semaphore(client_data):
        async with semaphore:
            return await client_service.create_client(client_data)
    
    tasks = [
        create_client_with_semaphore(client_data) 
        for client_data in client_data_list
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time()
    duration = end_time - start_time
    
    # Assert
    successful_creations = [r for r in results if not isinstance(r, Exception)]
    assert len(successful_creations) == client_count
    
    # Performance assertion: debe completarse en menos de 30 segundos
    assert duration < 30.0, f"Bulk creation took {duration:.2f} seconds, expected < 30s"
    
    # Throughput assertion: al menos 3 clientes por segundo
    throughput = client_count / duration
    assert throughput >= 3.0, f"Throughput was {throughput:.2f} clients/sec, expected >= 3.0"
```

## Conclusiones

Los patrones definidos en este documento proporcionan:

1. **Consistencia Arquitectónica**: Patrones uniformes en todos los servicios
2. **Mantenibilidad**: Código organizado y fácil de modificar
3. **Testabilidad**: Patrones que facilitan testing unitario e integración
4. **Escalabilidad**: Arquitectura preparada para crecimiento
5. **Robustez**: Manejo robusto de errores y transacciones
6. **Performance**: Optimizaciones de cache y procesamiento asíncrono

Estos patrones deben ser aplicados consistentemente en toda la implementación de servicios de dominio para garantizar una arquitectura sólida y mantenible.