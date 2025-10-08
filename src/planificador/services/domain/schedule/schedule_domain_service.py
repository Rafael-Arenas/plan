"""
Servicio de Dominio Principal para Schedule.

Este servicio actúa como el punto de entrada principal para todas las operaciones
del dominio Schedule, integrando todas las categorías de operaciones especializadas.
"""

from typing import Optional
from loguru import logger

from planificador.repositories.schedule.schedule_repository_facade import ScheduleRepositoryFacade
from planificador.services.domain.schedule.interfaces import (
    IScheduleDomainCrudOperations,
    IScheduleDomainEmployeeOperations,
    IScheduleDomainProjectOperations,
    IScheduleDomainTeamOperations,
    IScheduleDomainSearchOperations,
    IScheduleDomainConfirmationOperations,
    IScheduleDomainStatisticsOperations,
    IScheduleDomainProductivityOperations,
    IScheduleDomainValidationOperations,
    IScheduleDomainDiagnosticOperations
)
from planificador.services.domain.schedule.module import (
    ScheduleDomainCrudOperations,
    ScheduleDomainEmployeeOperations,
    ScheduleDomainProjectOperations,
    ScheduleDomainTeamOperations,
    ScheduleDomainSearchOperations,
    ScheduleDomainConfirmationOperations,
    ScheduleDomainStatisticsOperations,
    ScheduleDomainProductivityOperations,
    ScheduleDomainValidationOperations,
    ScheduleDomainDiagnosticOperations
)


class ScheduleDomainService:
    """
    Servicio de Dominio Principal para Schedule.
    
    Integra todas las operaciones especializadas del dominio Schedule
    proporcionando un punto de acceso unificado para la lógica de negocio.
    
    Attributes:
        crud: Operaciones CRUD básicas
        employee: Operaciones centradas en empleados
        project: Operaciones centradas en proyectos
        team: Operaciones centradas en equipos
        search: Operaciones de búsqueda y filtrado
        confirmation: Operaciones de confirmación y flujos de trabajo
        statistics: Operaciones de estadísticas y reportes
        productivity: Operaciones de análisis de productividad
        validation: Operaciones de validación y reglas de negocio
        diagnostic: Operaciones de diagnóstico y monitoreo
    """

    def __init__(self, repository_facade: Optional[ScheduleRepositoryFacade] = None):
        """
        Inicializa el servicio de dominio Schedule con todas sus operaciones.
        
        Args:
            repository_facade: Facade del repositorio de horarios.
                              Si no se proporciona, se creará una nueva instancia.
        """
        # Inicializar el facade del repositorio
        self._repository = repository_facade or ScheduleRepositoryFacade()
        
        # Inicializar todas las operaciones especializadas
        self._initialize_operations()
        
        logger.info("ScheduleDomainService inicializado con todas las operaciones")

    def _initialize_operations(self) -> None:
        """
        Inicializa todas las operaciones especializadas del servicio de dominio.
        """
        # Operaciones CRUD básicas
        self.crud: IScheduleDomainCrudOperations = ScheduleDomainCrudOperations(
            self._repository
        )
        
        # Operaciones centradas en empleados
        self.employee: IScheduleDomainEmployeeOperations = ScheduleDomainEmployeeOperations(
            self._repository
        )
        
        # Operaciones centradas en proyectos
        self.project: IScheduleDomainProjectOperations = ScheduleDomainProjectOperations(
            self._repository
        )
        
        # Operaciones centradas en equipos
        self.team: IScheduleDomainTeamOperations = ScheduleDomainTeamOperations(
            self._repository
        )
        
        # Operaciones de búsqueda y filtrado
        self.search: IScheduleDomainSearchOperations = ScheduleDomainSearchOperations(
            self._repository
        )
        
        # Operaciones de confirmación y flujos de trabajo
        self.confirmation: IScheduleDomainConfirmationOperations = ScheduleDomainConfirmationOperations(
            self._repository
        )
        
        # Operaciones de estadísticas y reportes
        self.statistics: IScheduleDomainStatisticsOperations = ScheduleDomainStatisticsOperations(
            self._repository
        )
        
        # Operaciones de análisis de productividad
        self.productivity: IScheduleDomainProductivityOperations = ScheduleDomainProductivityOperations(
            self._repository
        )
        
        # Operaciones de validación y reglas de negocio
        self.validation: IScheduleDomainValidationOperations = ScheduleDomainValidationOperations(
            self._repository
        )
        
        # Operaciones de diagnóstico y monitoreo
        self.diagnostic: IScheduleDomainDiagnosticOperations = ScheduleDomainDiagnosticOperations(
            self._repository
        )

    @property
    def repository(self) -> ScheduleRepositoryFacade:
        """
        Proporciona acceso directo al facade del repositorio si es necesario.
        
        Returns:
            Facade del repositorio de horarios
        """
        return self._repository

    async def health_check(self) -> dict:
        """
        Realiza una verificación básica de salud del servicio.
        
        Returns:
            Diccionario con el estado de salud del servicio
        """
        try:
            # TODO: Implementar verificación de salud básica
            # - Verificar conexión con el repositorio
            # - Validar configuraciones críticas
            # - Comprobar disponibilidad de dependencias
            
            logger.info("Verificación de salud del ScheduleDomainService completada")
            return {
                "status": "healthy",
                "service": "ScheduleDomainService",
                "operations_available": [
                    "crud", "employee", "project", "team", "search",
                    "confirmation", "statistics", "productivity", 
                    "validation", "diagnostic"
                ]
            }
        except Exception as e:
            logger.error(f"Error en verificación de salud: {str(e)}")
            return {
                "status": "unhealthy",
                "service": "ScheduleDomainService",
                "error": str(e)
            }

    def __repr__(self) -> str:
        """
        Representación string del servicio de dominio.
        
        Returns:
            Representación string del servicio
        """
        return f"ScheduleDomainService(operations=10, repository={type(self._repository).__name__})"