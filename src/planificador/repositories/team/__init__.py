# src/planificador/repositories/team/__init__.py

"""
Repositorio Team - Patrón Facade.

Este módulo implementa el patrón Facade para la gestión completa de equipos
y membresías en el sistema de planificación. Proporciona una interfaz
unificada y simplificada para todas las operaciones relacionadas con equipos.

Arquitectura:
    - Facade Principal: TeamRepositoryFacade
    - Interfaces Especializadas: CRUD, Query, Validation, Relationship, Statistics
    - Módulos de Implementación: Cada uno maneja un aspecto específico
    - Base Repository: Funcionalidad común y manejo de sesiones

Componentes Principales:
    - TeamRepositoryFacade: Punto de entrada único para todas las operaciones
    - Interfaces: Contratos bien definidos para cada tipo de operación
    - Módulos: Implementaciones especializadas y cohesivas
    - Excepciones: Manejo de errores específico del dominio

Principios de Diseño:
    - Single Responsibility: Cada módulo tiene una responsabilidad específica
    - Interface Segregation: Interfaces pequeñas y específicas
    - Dependency Injection: Módulos inyectados como dependencias
    - Open/Closed: Extensible sin modificar código existente
    - DRY: Reutilización de código común en base repository

Uso Básico:
    ```python
    from planificador.repositories.team import TeamRepositoryFacade
    from planificador.database.session import get_async_session
    
    async with get_async_session() as session:
        team_repo = TeamRepositoryFacade(session)
        
        # Operaciones CRUD
        team = await team_repo.create_team({
            'name': 'Desarrollo Backend',
            'description': 'Equipo de desarrollo de APIs',
            'department': 'Tecnología'
        })
        
        # Gestión de membresías
        membership = await team_repo.add_team_member(
            team_id=team.id,
            employee_id=123,
            role='Developer',
            is_leader=False
        )
        
        # Consultas avanzadas
        teams = await team_repo.get_teams_by_department('Tecnología')
        
        # Estadísticas
        stats = await team_repo.generate_teams_summary_report()
        
        # Validaciones
        validation = await team_repo.validate_team_data(team_data)
    ```

Uso Avanzado:
    ```python
    # Operaciones con validación completa
    result = await team_repo.create_team_with_validation(team_data)
    if result['success']:
        team = result['team']
    else:
        errors = result['validation_errors']
    
    # Información completa de equipo
    team_info = await team_repo.get_complete_team_info(team_id)
    
    # Dashboard de equipos
    dashboard = await team_repo.get_team_dashboard_data(
        department='Tecnología'
    )
    
    # Operaciones en lote
    results = await team_repo.bulk_team_operation(
        operation='create',
        team_data_list=[team1_data, team2_data, team3_data]
    )
    ```

Funcionalidades Disponibles:

1. **Operaciones CRUD**:
   - create_team(): Crear nuevos equipos
   - update_team(): Actualizar equipos existentes
   - delete_team(): Eliminar equipos
   - get_team_by_id(): Obtener equipo por ID
   - get_team_by_name(): Obtener equipo por nombre

2. **Consultas Avanzadas**:
   - get_teams_by_department(): Equipos por departamento
   - search_teams_by_criteria(): Búsqueda con criterios
   - get_teams_with_pagination(): Consultas paginadas
   - get_active_teams() / get_inactive_teams(): Por estado

3. **Gestión de Membresías**:
   - add_team_member(): Agregar miembros
   - remove_team_member(): Remover miembros
   - assign_team_leader(): Asignar líderes
   - get_team_members(): Obtener miembros
   - get_employee_teams(): Equipos de un empleado
   - update_member_role(): Actualizar roles

4. **Estadísticas y Reportes**:
   - count_total_teams(): Conteo de equipos
   - get_team_size_distribution(): Distribución de tamaños
   - get_membership_trends(): Tendencias de membresías
   - get_leadership_statistics(): Estadísticas de liderazgo
   - generate_teams_summary_report(): Reporte completo

5. **Validaciones**:
   - validate_team_data(): Validar datos de equipos
   - validate_membership_data(): Validar membresías
   - check_membership_conflicts(): Verificar conflictos
   - validate_business_rules(): Reglas de negocio
   - validate_data_consistency(): Consistencia de datos

6. **Operaciones Compuestas**:
   - get_complete_team_info(): Información completa
   - create_team_with_validation(): Creación con validación
   - add_team_member_with_validation(): Membresía con validación
   - get_team_dashboard_data(): Datos para dashboard
   - bulk_team_operation(): Operaciones en lote

Manejo de Errores:
    Todas las operaciones manejan errores de forma consistente:
    - TeamRepositoryError: Errores específicos del repositorio
    - ValidationError: Errores de validación de datos
    - BusinessRuleError: Violaciones de reglas de negocio
    - DatabaseError: Errores de base de datos
    - Logging estructurado con contexto completo
    - Rollback automático en operaciones transaccionales

Performance:
    - Consultas optimizadas con SQLAlchemy
    - Operaciones asíncronas para I/O no bloqueante
    - Lazy loading para relaciones cuando es apropiado
    - Paginación para consultas grandes
    - Cache de consultas frecuentes (cuando se implemente)

Seguridad:
    - Validación de datos de entrada
    - Sanitización de parámetros de consulta
    - Verificación de permisos (cuando se implemente)
    - Auditoría de operaciones críticas

Extensibilidad:
    - Interfaces bien definidas para nuevas funcionalidades
    - Módulos independientes y cohesivos
    - Patrón Strategy para diferentes tipos de validación
    - Hooks para auditoría y logging personalizado
"""

# Importar la fachada principal
from .team_repository_facade import TeamRepositoryFacade

# Importar interfaces para uso avanzado
from .interfaces import (
    ITeamCrudOperations,
    ITeamQueryOperations,
    ITeamValidationOperations,
    ITeamRelationshipOperations,
    ITeamStatisticsOperations
)

# Importar módulos para uso especializado
from .modules import (
    TeamCrudModule,
    TeamQueryModule,
    TeamValidationModule,
    TeamRelationshipModule,
    TeamStatisticsModule
)

# Definir la API pública del módulo
__all__ = [
    # Fachada principal (punto de entrada recomendado)
    'TeamRepositoryFacade',
    
    # Interfaces (para uso avanzado y testing)
    'ITeamCrudOperations',
    'ITeamQueryOperations',
    'ITeamValidationOperations',
    'ITeamRelationshipOperations',
    'ITeamStatisticsOperations',
    
    # Módulos especializados (para uso directo cuando sea necesario)
    'TeamCrudModule',
    'TeamQueryModule',
    'TeamValidationModule',
    'TeamRelationshipModule',
    'TeamStatisticsModule'
]

# Información del módulo
__version__ = '1.0.0'
__author__ = 'AkGroup Development Team'
__description__ = 'Repositorio Team con patrón Facade para gestión completa de equipos y membresías'

# Configuración de logging para el módulo
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Módulo {__name__} inicializado - Versión {__version__}")