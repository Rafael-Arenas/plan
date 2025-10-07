"""
Interfaz para las operaciones de planificación de fechas de proyectos.

Esta interfaz define el contrato para la planificación temporal avanzada,
cálculos de fechas, gestión de calendarios y análisis de cronogramas.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime
from decimal import Decimal

from planificador.schemas.project.date_planning import (
    ProjectDateSuggestion,
    ProjectTimelineAnalysis,
    ProjectScheduleValidation,
    ProjectCalendarView,
    ProjectDateConflict
)


class IProjectDatePlanningOperations(ABC):
    """
    Interfaz abstracta para las operaciones de planificación de fechas de proyectos.
    
    Define el contrato para toda la planificación temporal avanzada, cálculos de fechas,
    gestión de calendarios y análisis de cronogramas de proyectos.
    """

    # ==========================================
    # CÁLCULOS DE DURACIÓN Y FECHAS
    # ==========================================

    @abstractmethod
    async def calculate_project_duration(
        self,
        start_date: date,
        end_date: date,
        exclude_weekends: bool = True,
        exclude_holidays: bool = True
    ) -> Dict[str, Any]:
        """
        Calcula la duración de un proyecto considerando días laborables.
        
        Args:
            start_date (date): Fecha de inicio
            end_date (date): Fecha de finalización
            exclude_weekends (bool): Excluir fines de semana
            exclude_holidays (bool): Excluir días festivos
            
        Returns:
            Dict[str, Any]: Información detallada de duración
            
        Raises:
            ValidationError: Si las fechas son inválidas
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def calculate_working_days(
        self,
        start_date: date,
        end_date: date,
        country_code: str = "CL"
    ) -> int:
        """
        Calcula días laborables entre dos fechas.
        
        Args:
            start_date (date): Fecha de inicio
            end_date (date): Fecha de finalización
            country_code (str): Código de país para días festivos
            
        Returns:
            int: Número de días laborables
            
        Raises:
            ValidationError: Si las fechas son inválidas
        """
        pass

    @abstractmethod
    async def add_working_days(
        self,
        start_date: date,
        working_days: int,
        country_code: str = "CL"
    ) -> date:
        """
        Añade días laborables a una fecha.
        
        Args:
            start_date (date): Fecha de inicio
            working_days (int): Días laborables a añadir
            country_code (str): Código de país para días festivos
            
        Returns:
            date: Fecha resultante
            
        Raises:
            ValidationError: Si los parámetros son inválidos
        """
        pass

    @abstractmethod
    async def subtract_working_days(
        self,
        end_date: date,
        working_days: int,
        country_code: str = "CL"
    ) -> date:
        """
        Resta días laborables de una fecha.
        
        Args:
            end_date (date): Fecha de finalización
            working_days (int): Días laborables a restar
            country_code (str): Código de país para días festivos
            
        Returns:
            date: Fecha resultante
            
        Raises:
            ValidationError: Si los parámetros son inválidos
        """
        pass

    # ==========================================
    # SUGERENCIAS DE FECHAS ÓPTIMAS
    # ==========================================

    @abstractmethod
    async def suggest_optimal_start_date(
        self,
        project_data: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> ProjectDateSuggestion:
        """
        Sugiere fecha de inicio óptima para un proyecto.
        
        Args:
            project_data (Dict[str, Any]): Datos del proyecto
            constraints (Dict[str, Any], optional): Restricciones adicionales
            
        Returns:
            ProjectDateSuggestion: Sugerencia de fecha de inicio
            
        Raises:
            ValidationError: Si los datos son inválidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def suggest_optimal_end_date(
        self,
        project_data: Dict[str, Any],
        start_date: date,
        constraints: Optional[Dict[str, Any]] = None
    ) -> ProjectDateSuggestion:
        """
        Sugiere fecha de finalización óptima para un proyecto.
        
        Args:
            project_data (Dict[str, Any]): Datos del proyecto
            start_date (date): Fecha de inicio del proyecto
            constraints (Dict[str, Any], optional): Restricciones adicionales
            
        Returns:
            ProjectDateSuggestion: Sugerencia de fecha de finalización
            
        Raises:
            ValidationError: Si los datos son inválidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def suggest_project_timeline(
        self,
        project_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> ProjectDateSuggestion:
        """
        Sugiere cronograma completo para un proyecto.
        
        Args:
            project_data (Dict[str, Any]): Datos del proyecto
            preferences (Dict[str, Any], optional): Preferencias de planificación
            
        Returns:
            ProjectDateSuggestion: Sugerencia de cronograma completo
            
        Raises:
            ValidationError: Si los datos son inválidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ANÁLISIS DE FACTIBILIDAD TEMPORAL
    # ==========================================

    @abstractmethod
    async def analyze_timeline_feasibility(
        self,
        project_id: int,
        proposed_start_date: date,
        proposed_end_date: date
    ) -> ProjectTimelineAnalysis:
        """
        Analiza la factibilidad de un cronograma propuesto.
        
        Args:
            project_id (int): ID del proyecto
            proposed_start_date (date): Fecha de inicio propuesta
            proposed_end_date (date): Fecha de finalización propuesta
            
        Returns:
            ProjectTimelineAnalysis: Análisis de factibilidad
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si las fechas son inválidas
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def check_resource_availability(
        self,
        start_date: date,
        end_date: date,
        required_resources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verifica disponibilidad de recursos en un período.
        
        Args:
            start_date (date): Fecha de inicio
            end_date (date): Fecha de finalización
            required_resources (List[Dict[str, Any]]): Recursos requeridos
            
        Returns:
            Dict[str, Any]: Análisis de disponibilidad de recursos
            
        Raises:
            ValidationError: Si los parámetros son inválidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_schedule_conflicts(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> List[ProjectDateConflict]:
        """
        Analiza conflictos de cronograma con otros proyectos.
        
        Args:
            project_id (int): ID del proyecto
            start_date (date): Fecha de inicio
            end_date (date): Fecha de finalización
            
        Returns:
            List[ProjectDateConflict]: Lista de conflictos encontrados
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si las fechas son inválidas
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # VALIDACIÓN DE FECHAS
    # ==========================================

    @abstractmethod
    async def validate_project_dates(
        self,
        project_data: Dict[str, Any],
        business_rules: Optional[Dict[str, Any]] = None
    ) -> ProjectScheduleValidation:
        """
        Valida fechas de proyecto según reglas de negocio.
        
        Args:
            project_data (Dict[str, Any]): Datos del proyecto con fechas
            business_rules (Dict[str, Any], optional): Reglas de negocio específicas
            
        Returns:
            ProjectScheduleValidation: Resultado de validación
            
        Raises:
            ValidationError: Si los datos son inválidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_date_dependencies(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Valida dependencias de fechas con otros proyectos.
        
        Args:
            project_id (int): ID del proyecto
            start_date (date): Fecha de inicio
            end_date (date): Fecha de finalización
            
        Returns:
            Dict[str, Any]: Resultado de validación de dependencias
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si las fechas son inválidas
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_milestone_dates(
        self,
        project_id: int,
        milestones: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Valida fechas de hitos del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            milestones (List[Dict[str, Any]]): Lista de hitos con fechas
            
        Returns:
            Dict[str, Any]: Resultado de validación de hitos
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si los hitos son inválidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # GESTIÓN DE CALENDARIOS
    # ==========================================

    @abstractmethod
    async def get_project_calendar_view(
        self,
        start_date: date,
        end_date: date,
        view_type: str = "month",
        filters: Optional[Dict[str, Any]] = None
    ) -> ProjectCalendarView:
        """
        Obtiene vista de calendario de proyectos.
        
        Args:
            start_date (date): Fecha de inicio de la vista
            end_date (date): Fecha de finalización de la vista
            view_type (str): Tipo de vista (day, week, month, quarter)
            filters (Dict[str, Any], optional): Filtros adicionales
            
        Returns:
            ProjectCalendarView: Vista de calendario
            
        Raises:
            ValidationError: Si los parámetros son inválidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_project_timeline_view(
        self,
        project_ids: Optional[List[int]] = None,
        date_range: Optional[Tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene vista de línea de tiempo de proyectos.
        
        Args:
            project_ids (List[int], optional): IDs de proyectos específicos
            date_range (Tuple[date, date], optional): Rango de fechas
            
        Returns:
            Dict[str, Any]: Vista de línea de tiempo
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_critical_dates_calendar(
        self,
        date_range: Tuple[date, date],
        include_milestones: bool = True,
        include_deadlines: bool = True
    ) -> Dict[str, Any]:
        """
        Obtiene calendario de fechas críticas.
        
        Args:
            date_range (Tuple[date, date]): Rango de fechas
            include_milestones (bool): Incluir hitos
            include_deadlines (bool): Incluir fechas límite
            
        Returns:
            Dict[str, Any]: Calendario de fechas críticas
            
        Raises:
            ValidationError: Si el rango de fechas es inválido
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ANÁLISIS DE CRONOGRAMAS
    # ==========================================

    @abstractmethod
    async def analyze_project_schedule_performance(
        self,
        project_id: int
    ) -> Dict[str, Any]:
        """
        Analiza el rendimiento del cronograma de un proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Análisis de rendimiento del cronograma
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_schedule_variance_analysis(
        self,
        project_id: int
    ) -> Dict[str, Any]:
        """
        Obtiene análisis de varianza del cronograma.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Análisis de varianza
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def predict_project_completion_date(
        self,
        project_id: int,
        current_progress: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Predice fecha de finalización basada en progreso actual.
        
        Args:
            project_id (int): ID del proyecto
            current_progress (Decimal, optional): Progreso actual (0-100)
            
        Returns:
            Dict[str, Any]: Predicción de fecha de finalización
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # OPTIMIZACIÓN DE CRONOGRAMAS
    # ==========================================

    @abstractmethod
    async def optimize_project_schedule(
        self,
        project_id: int,
        optimization_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimiza el cronograma de un proyecto.
        
        Args:
            project_id (int): ID del proyecto
            optimization_criteria (Dict[str, Any]): Criterios de optimización
            
        Returns:
            Dict[str, Any]: Cronograma optimizado
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si los criterios son inválidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def suggest_schedule_adjustments(
        self,
        project_id: int,
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Sugiere ajustes al cronograma del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            constraints (Dict[str, Any], optional): Restricciones para ajustes
            
        Returns:
            List[Dict[str, Any]]: Lista de sugerencias de ajuste
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def rebalance_project_timelines(
        self,
        project_ids: List[int],
        rebalance_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Rebalancea cronogramas de múltiples proyectos.
        
        Args:
            project_ids (List[int]): IDs de proyectos a rebalancear
            rebalance_criteria (Dict[str, Any]): Criterios de rebalanceo
            
        Returns:
            Dict[str, Any]: Resultado del rebalanceo
            
        Raises:
            NotFoundError: Si algún proyecto no existe
            ValidationError: Si los criterios son inválidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # GESTIÓN DE DÍAS FESTIVOS Y LABORABLES
    # ==========================================

    @abstractmethod
    async def get_holidays_in_range(
        self,
        start_date: date,
        end_date: date,
        country_code: str = "CL"
    ) -> List[Dict[str, Any]]:
        """
        Obtiene días festivos en un rango de fechas.
        
        Args:
            start_date (date): Fecha de inicio
            end_date (date): Fecha de finalización
            country_code (str): Código de país
            
        Returns:
            List[Dict[str, Any]]: Lista de días festivos
            
        Raises:
            ValidationError: Si el rango de fechas es inválido
        """
        pass

    @abstractmethod
    async def configure_working_calendar(
        self,
        calendar_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configura calendario laboral personalizado.
        
        Args:
            calendar_config (Dict[str, Any]): Configuración del calendario
            
        Returns:
            Dict[str, Any]: Calendario configurado
            
        Raises:
            ValidationError: Si la configuración es inválida
        """
        pass

    @abstractmethod
    async def get_working_calendar_info(
        self,
        calendar_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene información del calendario laboral.
        
        Args:
            calendar_id (int, optional): ID del calendario específico
            
        Returns:
            Dict[str, Any]: Información del calendario
            
        Raises:
            NotFoundError: Si el calendario no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass