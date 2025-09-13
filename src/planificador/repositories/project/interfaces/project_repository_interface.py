from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional

from planificador.models.project import Project
from planificador.models.project import ProjectStatus, ProjectPriority


class IProjectRepository(ABC):
    """
    Interfaz para el repositorio de proyectos.
    """

    @abstractmethod
    async def create_project(self, project_data: Dict[str, Any]) -> Project:
        """
        Crea un nuevo proyecto.
        """
        pass

    @abstractmethod
    async def get_by_id(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto por su ID.
        """
        pass

    @abstractmethod
    async def update_project(
        self, project_id: int, updated_data: Dict[str, Any]
    ) -> Optional[Project]:
        """
        Actualiza un proyecto existente.
        """
        pass

    @abstractmethod
    async def delete_project(self, project_id: int) -> bool:
        """
        Elimina un proyecto.
        """
        pass

    @abstractmethod
    async def archive_project(self, project_id: int) -> Optional[Project]:
        """
        Archiva un proyecto.
        """
        pass

    @abstractmethod
    def format_project_dates(self, project: Project) -> Dict[str, Optional[str]]:
        """
        Formatea las fechas de un proyecto.
        """
        pass

    @abstractmethod
    async def get_by_reference(self, reference: str) -> Optional[Project]:
        """
        Obtiene un proyecto por su referencia.
        """
        pass

    @abstractmethod
    async def get_by_trigram(self, trigram: str) -> Optional[Project]:
        """
        Obtiene un proyecto por su trigrama.
        """
        pass

    @abstractmethod
    async def search_by_name(self, search_term: str) -> List[Project]:
        """
        Busca proyectos por nombre.
        """
        pass

    @abstractmethod
    async def get_by_client(self, client_id: int) -> List[Project]:
        """
        Obtiene proyectos por cliente.
        """
        pass

    @abstractmethod
    async def get_by_status(self, status: ProjectStatus) -> List[Project]:
        """
        Obtiene proyectos por estado.
        """
        pass

    @abstractmethod
    async def get_active_projects(self) -> List[Project]:
        """
        Obtiene todos los proyectos activos.
        """
        pass

    @abstractmethod
    async def get_by_priority(self, priority: ProjectPriority) -> List[Project]:
        """
        Obtiene proyectos por prioridad.
        """
        pass

    @abstractmethod
    async def get_by_date_range(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[Project]:
        """
        Obtiene proyectos en un rango de fechas.
        """
        pass

    @abstractmethod
    async def get_overdue_projects(
        self, reference_date: Optional[date] = None
    ) -> List[Project]:
        """
        Obtiene proyectos atrasados.
        """
        pass

    @abstractmethod
    async def get_projects_starting_current_week(self, **kwargs) -> List[Project]:
        """
        Obtiene proyectos que inician en la semana actual.
        """
        pass

    @abstractmethod
    async def get_projects_ending_current_week(self, **kwargs) -> List[Project]:
        """
        Obtiene proyectos que terminan en la semana actual.
        """
        pass

    @abstractmethod
    async def get_projects_starting_current_month(self, **kwargs) -> List[Project]:
        """
        Obtiene proyectos que inician en el mes actual.
        """
        pass

    @abstractmethod
    async def get_projects_starting_business_days_only(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs,
    ) -> List[Project]:
        """
        Obtiene proyectos que inician en días hábiles.
        """
        pass

    @abstractmethod
    async def get_with_client(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto con su cliente.
        """
        pass

    @abstractmethod
    async def get_with_assignments(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto con sus asignaciones.
        """
        pass

    @abstractmethod
    async def get_with_full_details(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto con todos sus detalles.
        """
        pass

    @abstractmethod
    async def reference_exists(
        self, reference: str, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si una referencia de proyecto existe.
        """
        pass

    @abstractmethod
    async def trigram_exists(
        self, trigram: str, exclude_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si un trigrama de proyecto existe.
        """
        pass

    @abstractmethod
    async def get_project_performance_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de rendimiento de un proyecto.
        """
        pass

    @abstractmethod
    async def get_projects_by_status_summary(self) -> Dict[str, int]:
        """
        Obtiene un resumen de proyectos por estado.
        """
        pass

    @abstractmethod
    async def get_project_workload_stats(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de carga de trabajo de un proyecto.
        """
        pass

    @abstractmethod
    async def get_project_duration_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de duración de un proyecto.
        """
        pass

    @abstractmethod
    async def get_monthly_project_stats(
        self, year: int, month: int
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas mensuales de proyectos.
        """
        pass

    @abstractmethod
    async def get_client_project_stats(self, client_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos de un cliente.
        """
        pass

    @abstractmethod
    async def get_overdue_projects_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de proyectos atrasados.
        """
        pass