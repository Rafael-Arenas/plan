# Estrategia de Implementación de Servicios de Dominio

**Fecha de Creación:** Enero 2025  
**Versión:** 1.0.0  
**Estado:** Propuesta de Implementación

## Descripción General

Este documento define la estrategia para implementar los **Servicios de Dominio** en el sistema Planificador, basándose en la arquitectura modular existente de repositorios. Los servicios de dominio actuarán como una capa intermedia entre los controladores/UI y los repositorios, encapsulando la lógica de negocio compleja y coordinando operaciones entre múltiples entidades.

## Análisis de la Arquitectura Actual

### Repositorios Existentes

El sistema cuenta con repositorios bien estructurados que siguen el patrón **Facade** con módulos especializados:

#### Entidades Principales
- **Client**: Gestión de clientes con 8 módulos especializados
- **Employee**: Gestión de empleados con operaciones CRUD y relaciones
- **Project**: Gestión de proyectos con 19+ operaciones
- **ProjectAssignment**: Asignaciones de empleados a proyectos
- **Team**: Gestión de equipos y membresías
- **Workload**: Cargas de trabajo y análisis de capacidad
- **Schedule**: Horarios y planificación temporal
- **StatusCode**: Códigos de estado del sistema
- **Vacation**: Gestión de vacaciones
- **Alert**: Sistema de alertas y notificaciones

#### Módulos Especializados por Repositorio
Cada repositorio implementa módulos especializados siguiendo el patrón de **Separación de Responsabilidades**:

1. **CRUD Operations**: Operaciones básicas de persistencia
2. **Query Operations**: Consultas básicas y búsquedas
3. **Advanced Query Operations**: Consultas complejas y filtros avanzados
4. **Validation Operations**: Validaciones de datos y reglas de negocio
5. **Statistics Operations**: Métricas, análisis y estadísticas
6. **Relationship Operations**: Gestión de relaciones entre entidades
7. **Date Operations**: Operaciones especializadas en fechas y tiempo
8. **Health Operations**: Monitoreo y diagnósticos del sistema

## Arquitectura Propuesta para Servicios de Dominio

### Principios de Diseño

#### 1. **Capa de Abstracción**
Los servicios de dominio actuarán como una capa de abstracción entre la UI/API y los repositorios, encapsulando:
- Lógica de negocio compleja
- Coordinación entre múltiples repositorios
- Validaciones de dominio
- Transformaciones de datos
- Manejo de transacciones distribuidas

#### 2. **Patrón de Servicios Especializados**
Siguiendo el patrón exitoso de los repositorios, cada servicio de dominio se especializará en un área funcional específica:

```
src/planificador/services/domain/
├── __init__.py
├── base_domain_service.py
├── client/
│   ├── __init__.py
│   ├── client_domain_service.py
│   └── interfaces/
│       └── client_service_interface.py
├── employee/
│   ├── __init__.py
│   ├── employee_domain_service.py
│   └── interfaces/
│       └── employee_service_interface.py
├── project/
│   ├── __init__.py
│   ├── project_domain_service.py
│   └── interfaces/
│       └── project_service_interface.py
├── planning/
│   ├── __init__.py
│   ├── planning_domain_service.py
│   └── interfaces/
│       └── planning_service_interface.py
├── resource_management/
│   ├── __init__.py
│   ├── resource_management_service.py
│   └── interfaces/
│       └── resource_management_interface.py
└── analytics/
    ├── __init__.py
    ├── analytics_domain_service.py
    └── interfaces/
        └── analytics_service_interface.py
```

#### 3. **Servicios de Dominio Especializados**

##### **ClientDomainService**
- **Responsabilidad**: Lógica de negocio relacionada con clientes
- **Repositorios utilizados**: Client, Project, ProjectAssignment
- **Funcionalidades**:
  - Gestión completa del ciclo de vida del cliente
  - Análisis de rentabilidad por cliente
  - Gestión de proyectos asociados
  - Validaciones de negocio complejas

##### **EmployeeDomainService**
- **Responsabilidad**: Gestión integral de empleados
- **Repositorios utilizados**: Employee, Team, ProjectAssignment, Workload, Vacation
- **Funcionalidades**:
  - Gestión del perfil completo del empleado
  - Análisis de carga de trabajo y disponibilidad
  - Gestión de membresías de equipo
  - Planificación de vacaciones

##### **ProjectDomainService**
- **Responsabilidad**: Gestión completa de proyectos
- **Repositorios utilizados**: Project, ProjectAssignment, Client, Employee, StatusCode
- **Funcionalidades**:
  - Ciclo de vida completo del proyecto
  - Asignación y reasignación de recursos
  - Seguimiento de progreso y estados
  - Análisis de rentabilidad y performance

##### **PlanningDomainService**
- **Responsabilidad**: Planificación y programación de recursos
- **Repositorios utilizados**: Schedule, ProjectAssignment, Workload, Employee, Vacation
- **Funcionalidades**:
  - Planificación automática de recursos
  - Optimización de asignaciones
  - Detección de conflictos de horarios
  - Análisis de capacidad y disponibilidad

##### **ResourceManagementService**
- **Responsabilidad**: Gestión integral de recursos humanos
- **Repositorios utilizados**: Employee, Team, Workload, ProjectAssignment
- **Funcionalidades**:
  - Análisis de utilización de recursos
  - Balanceamiento de cargas de trabajo
  - Identificación de cuellos de botella
  - Recomendaciones de asignación

##### **AnalyticsDomainService**
- **Responsabilidad**: Análisis y métricas de negocio
- **Repositorios utilizados**: Todos los repositorios para análisis transversal
- **Funcionalidades**:
  - Dashboards ejecutivos
  - KPIs y métricas de performance
  - Análisis predictivo
  - Reportes personalizados

## Implementación Técnica

### Base Domain Service

```python
# src/planificador/services/domain/base_domain_service.py

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from planificador.config.config import settings
from planificador.exceptions import DomainServiceError

ServiceType = TypeVar('ServiceType')

class BaseDomainService(ABC):
    """
    Clase base para todos los servicios de dominio.
    
    Proporciona funcionalidades comunes como logging, manejo de errores,
    gestión de sesiones y patrones de validación.
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session
        self._logger = logger
        self._initialize_repositories()
    
    @abstractmethod
    def _initialize_repositories(self) -> None:
        """Inicializa los repositorios necesarios para el servicio."""
        pass
    
    async def _validate_business_rules(self, operation: str, data: Dict[str, Any]) -> None:
        """Valida reglas de negocio específicas del dominio."""
        pass
    
    async def _log_operation(self, operation: str, entity_id: Optional[int] = None, 
                           success: bool = True, details: Optional[Dict[str, Any]] = None) -> None:
        """Registra operaciones del servicio para auditoría."""
        pass
```

### Ejemplo de Implementación: ClientDomainService

```python
# src/planificador/services/domain/client/client_domain_service.py

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models import Client, Project, ProjectAssignment
from planificador.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from planificador.repositories.client import ClientRepositoryFacade
from planificador.repositories.project import ProjectRepositoryFacade
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.services.domain.base_domain_service import BaseDomainService
from planificador.exceptions import ClientDomainError, ValidationError

class ClientDomainService(BaseDomainService):
    """
    Servicio de dominio para la gestión integral de clientes.
    
    Encapsula la lógica de negocio compleja relacionada con clientes,
    coordinando operaciones entre múltiples repositorios y aplicando
    reglas de negocio específicas del dominio.
    """
    
    def _initialize_repositories(self) -> None:
        """Inicializa los repositorios necesarios."""
        self._client_repo = ClientRepositoryFacade(self._session)
        self._project_repo = ProjectRepositoryFacade(self._session)
        self._assignment_repo = ProjectAssignmentRepositoryFacade(self._session)
    
    async def create_client_with_initial_project(
        self, 
        client_data: ClientCreate, 
        initial_project_data: Optional[Dict[str, Any]] = None
    ) -> ClientResponse:
        """
        Crea un cliente y opcionalmente un proyecto inicial.
        
        Lógica de negocio:
        - Valida datos del cliente
        - Crea el cliente
        - Si se proporciona, crea el proyecto inicial
        - Establece relaciones apropiadas
        - Registra la operación para auditoría
        """
        try:
            # Validar reglas de negocio
            await self._validate_client_creation(client_data)
            
            # Crear cliente
            client = await self._client_repo.create_client(client_data.model_dump())
            
            # Crear proyecto inicial si se proporciona
            if initial_project_data:
                initial_project_data['client_id'] = client.id
                await self._project_repo.create_project(initial_project_data)
            
            # Registrar operación
            await self._log_operation(
                operation="create_client_with_project",
                entity_id=client.id,
                success=True,
                details={"has_initial_project": bool(initial_project_data)}
            )
            
            return ClientResponse.model_validate(client)
            
        except Exception as e:
            await self._log_operation(
                operation="create_client_with_project",
                success=False,
                details={"error": str(e)}
            )
            raise ClientDomainError(f"Error creating client: {e}") from e
    
    async def get_client_portfolio_analysis(self, client_id: int) -> Dict[str, Any]:
        """
        Análisis completo del portafolio de un cliente.
        
        Combina datos de múltiples repositorios para generar un análisis
        integral del cliente incluyendo proyectos, rentabilidad y métricas.
        """
        try:
            # Obtener datos del cliente
            client = await self._client_repo.get_client_by_id(client_id)
            if not client:
                raise ClientDomainError(f"Cliente {client_id} no encontrado")
            
            # Obtener proyectos del cliente
            projects = await self._project_repo.get_projects_by_client(client_id)
            
            # Obtener estadísticas de asignaciones
            assignment_stats = await self._assignment_repo.get_client_assignment_statistics(client_id)
            
            # Calcular métricas de negocio
            portfolio_metrics = await self._calculate_portfolio_metrics(client, projects, assignment_stats)
            
            return {
                "client": ClientResponse.model_validate(client),
                "projects_summary": {
                    "total_projects": len(projects),
                    "active_projects": len([p for p in projects if p.status == "active"]),
                    "completed_projects": len([p for p in projects if p.status == "completed"])
                },
                "assignment_statistics": assignment_stats,
                "portfolio_metrics": portfolio_metrics
            }
            
        except Exception as e:
            self._logger.error(f"Error en análisis de portafolio para cliente {client_id}: {e}")
            raise ClientDomainError(f"Error analyzing client portfolio: {e}") from e
    
    async def _validate_client_creation(self, client_data: ClientCreate) -> None:
        """Valida reglas de negocio para creación de clientes."""
        # Verificar unicidad de código de cliente
        existing_client = await self._client_repo.get_client_by_code(client_data.code)
        if existing_client:
            raise ValidationError(f"Ya existe un cliente con código {client_data.code}")
        
        # Validar formato de email si se proporciona
        if client_data.email:
            await self._client_repo.validate_email_format(client_data.email)
    
    async def _calculate_portfolio_metrics(
        self, 
        client: Client, 
        projects: List[Project], 
        assignment_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcula métricas de negocio del portafolio del cliente."""
        # Implementar cálculos específicos de negocio
        return {
            "total_revenue": sum(p.budget or 0 for p in projects),
            "average_project_duration": self._calculate_average_duration(projects),
            "resource_utilization": assignment_stats.get("total_hours", 0),
            "profitability_score": self._calculate_profitability_score(projects, assignment_stats)
        }
```

### Interfaces de Servicios

```python
# src/planificador/services/domain/client/interfaces/client_service_interface.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from planificador.schemas.client import ClientCreate, ClientUpdate, ClientResponse

class IClientDomainService(ABC):
    """Interfaz para el servicio de dominio de clientes."""
    
    @abstractmethod
    async def create_client_with_initial_project(
        self, 
        client_data: ClientCreate, 
        initial_project_data: Optional[Dict[str, Any]] = None
    ) -> ClientResponse:
        """Crea un cliente con un proyecto inicial opcional."""
        pass
    
    @abstractmethod
    async def get_client_portfolio_analysis(self, client_id: int) -> Dict[str, Any]:
        """Obtiene análisis completo del portafolio del cliente."""
        pass
    
    @abstractmethod
    async def transfer_client_projects(
        self, 
        source_client_id: int, 
        target_client_id: int, 
        project_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Transfiere proyectos entre clientes."""
        pass
```

## Patrones de Implementación

### 1. **Dependency Injection**
```python
class ProjectDomainService(BaseDomainService):
    def __init__(
        self, 
        session: AsyncSession,
        client_service: Optional[IClientDomainService] = None,
        employee_service: Optional[IEmployeeDomainService] = None
    ):
        super().__init__(session)
        self._client_service = client_service
        self._employee_service = employee_service
```

### 2. **Transaction Management**
```python
async def complex_business_operation(self, data: Dict[str, Any]) -> Any:
    """Operación compleja que requiere múltiples repositorios."""
    async with self._session.begin():
        try:
            # Operación 1
            result1 = await self._repo1.operation1(data)
            
            # Operación 2 que depende de result1
            result2 = await self._repo2.operation2(result1.id, data)
            
            # Validación de negocio
            await self._validate_complex_rules(result1, result2)
            
            return {"result1": result1, "result2": result2}
            
        except Exception as e:
            # El rollback es automático por el context manager
            self._logger.error(f"Error en operación compleja: {e}")
            raise DomainServiceError(f"Complex operation failed: {e}") from e
```

### 3. **Event-Driven Architecture** (Futuro)
```python
from planificador.events import DomainEvent, EventBus

class ClientDomainService(BaseDomainService):
    async def create_client(self, client_data: ClientCreate) -> ClientResponse:
        client = await self._client_repo.create_client(client_data.model_dump())
        
        # Emitir evento de dominio
        event = DomainEvent(
            event_type="client_created",
            entity_id=client.id,
            data={"client_code": client.code, "client_name": client.name}
        )
        await EventBus.publish(event)
        
        return ClientResponse.model_validate(client)
```

## Manejo de Errores y Excepciones

### Jerarquía de Excepciones de Dominio
```python
# src/planificador/exceptions/domain.py

class DomainServiceError(Exception):
    """Excepción base para errores de servicios de dominio."""
    pass

class ClientDomainError(DomainServiceError):
    """Errores específicos del dominio de clientes."""
    pass

class ProjectDomainError(DomainServiceError):
    """Errores específicos del dominio de proyectos."""
    pass

class PlanningDomainError(DomainServiceError):
    """Errores específicos del dominio de planificación."""
    pass

class BusinessRuleViolationError(DomainServiceError):
    """Error cuando se viola una regla de negocio."""
    pass
```

## Testing de Servicios de Dominio

### Estructura de Tests
```
src/planificador/tests/services/domain/
├── __init__.py
├── conftest.py
├── test_client_domain_service.py
├── test_employee_domain_service.py
├── test_project_domain_service.py
├── test_planning_domain_service.py
└── integration/
    ├── __init__.py
    └── test_cross_domain_operations.py
```

### Ejemplo de Test
```python
# src/planificador/tests/services/domain/test_client_domain_service.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from planificador.services.domain.client import ClientDomainService
from planificador.schemas.client import ClientCreate

@pytest.fixture
async def client_service(async_session):
    return ClientDomainService(async_session)

@pytest.mark.asyncio
async def test_create_client_with_initial_project(client_service):
    # Arrange
    client_data = ClientCreate(
        name="Test Client",
        code="TC001",
        email="test@example.com"
    )
    project_data = {"name": "Initial Project", "description": "Test project"}
    
    # Act
    result = await client_service.create_client_with_initial_project(
        client_data, project_data
    )
    
    # Assert
    assert result.name == "Test Client"
    assert result.code == "TC001"
    # Verificar que se creó el proyecto inicial
    projects = await client_service._project_repo.get_projects_by_client(result.id)
    assert len(projects) == 1
    assert projects[0].name == "Initial Project"
```

## Configuración y Deployment

### Configuración de Servicios
```python
# src/planificador/config/services_config.py

from pydantic import BaseSettings

class DomainServicesConfig(BaseSettings):
    """Configuración específica para servicios de dominio."""
    
    # Timeouts para operaciones complejas
    complex_operation_timeout: int = 30
    
    # Límites de procesamiento
    max_batch_size: int = 100
    max_concurrent_operations: int = 10
    
    # Configuración de cache
    enable_service_cache: bool = True
    cache_ttl_seconds: int = 300
    
    # Configuración de eventos
    enable_domain_events: bool = False
    event_bus_url: Optional[str] = None
    
    class Config:
        env_prefix = "DOMAIN_SERVICES_"
```

### Registro de Servicios
```python
# src/planificador/services/domain/__init__.py

from .client.client_domain_service import ClientDomainService
from .employee.employee_domain_service import EmployeeDomainService
from .project.project_domain_service import ProjectDomainService
from .planning.planning_domain_service import PlanningDomainService
from .resource_management.resource_management_service import ResourceManagementService
from .analytics.analytics_domain_service import AnalyticsDomainService

__all__ = [
    "ClientDomainService",
    "EmployeeDomainService", 
    "ProjectDomainService",
    "PlanningDomainService",
    "ResourceManagementService",
    "AnalyticsDomainService"
]

# Factory para servicios de dominio
class DomainServiceFactory:
    """Factory para crear instancias de servicios de dominio."""
    
    @staticmethod
    def create_client_service(session: AsyncSession) -> ClientDomainService:
        return ClientDomainService(session)
    
    @staticmethod
    def create_project_service(session: AsyncSession) -> ProjectDomainService:
        return ProjectDomainService(session)
    
    # ... otros servicios
```

## Roadmap de Implementación

### Fase 1: Fundación (Semana 1-2)
- [ ] Implementar `BaseDomainService`
- [ ] Crear estructura de directorios
- [ ] Implementar sistema de excepciones de dominio
- [ ] Configurar testing framework para servicios

### Fase 2: Servicios Core (Semana 3-4)
- [ ] Implementar `ClientDomainService`
- [ ] Implementar `ProjectDomainService`
- [ ] Crear tests unitarios y de integración
- [ ] Documentar APIs de servicios

### Fase 3: Servicios Avanzados (Semana 5-6)
- [ ] Implementar `EmployeeDomainService`
- [ ] Implementar `PlanningDomainService`
- [ ] Agregar validaciones de negocio complejas
- [ ] Optimizar performance de operaciones

### Fase 4: Servicios Especializados (Semana 7-8)
- [ ] Implementar `ResourceManagementService`
- [ ] Implementar `AnalyticsDomainService`
- [ ] Agregar cache y optimizaciones
- [ ] Implementar métricas y monitoreo

### Fase 5: Integración y Refinamiento (Semana 9-10)
- [ ] Integrar servicios con UI/API existente
- [ ] Optimizar performance end-to-end
- [ ] Completar documentación
- [ ] Preparar para producción

## Consideraciones de Performance

### 1. **Caching Estratégico**
- Cache de consultas frecuentes a nivel de servicio
- Invalidación inteligente basada en eventos de dominio
- Cache distribuido para operaciones costosas

### 2. **Optimización de Consultas**
- Uso de eager loading para relaciones frecuentes
- Consultas batch para operaciones múltiples
- Índices optimizados en base de datos

### 3. **Procesamiento Asíncrono**
- Operaciones largas en background tasks
- Queue system para operaciones diferidas
- Streaming de resultados para datasets grandes

## Monitoreo y Observabilidad

### Métricas Clave
- Tiempo de respuesta por operación de servicio
- Tasa de errores por tipo de servicio
- Utilización de recursos por servicio
- Throughput de operaciones de negocio

### Logging Estructurado
```python
self._logger.info(
    "Domain operation completed",
    service="ClientDomainService",
    operation="create_client_with_project",
    client_id=client.id,
    duration_ms=duration,
    success=True
)
```

## Conclusiones

La implementación de servicios de dominio proporcionará:

1. **Separación Clara de Responsabilidades**: Lógica de negocio separada de acceso a datos
2. **Reutilización de Código**: Operaciones complejas centralizadas y reutilizables
3. **Testabilidad Mejorada**: Lógica de negocio fácilmente testeable
4. **Mantenibilidad**: Código organizado y fácil de mantener
5. **Escalabilidad**: Arquitectura preparada para crecimiento futuro
6. **Consistencia**: Aplicación uniforme de reglas de negocio

Esta estrategia aprovecha la sólida base de repositorios existente y proporciona una evolución natural hacia una arquitectura más robusta y mantenible.