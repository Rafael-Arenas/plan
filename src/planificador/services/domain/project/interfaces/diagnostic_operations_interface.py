"""
Interfaz para las operaciones de diagnóstico de proyectos.

Esta interfaz define el contrato para el diagnóstico de salud de proyectos,
detección de anomalías y generación de reportes de estado.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import date

from planificador.schemas.project.diagnostic import (
    ProjectHealthReport,
    ProjectAnomalyReport,
    ProjectPerformanceAnalysis,
    ProjectStatusReport,
    DiagnosticSeverity,
    DiagnosticCategory
)


class IProjectDiagnosticOperations(ABC):
    """
    Interfaz abstracta para las operaciones de diagnóstico de proyectos.
    
    Define el contrato para el diagnóstico completo de salud de proyectos,
    detección de anomalías, análisis de rendimiento y generación de reportes.
    """

    # ==========================================
    # DIAGNÓSTICO DE SALUD DE PROYECTOS
    # ==========================================

    @abstractmethod
    async def diagnose_project_health(self, project_id: int) -> ProjectHealthReport:
        """
        Realiza diagnóstico completo de salud de un proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            ProjectHealthReport: Reporte completo de salud del proyecto
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_project_health_score(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene puntuación de salud del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Puntuación y métricas de salud
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_project_risks(self, project_id: int) -> Dict[str, Any]:
        """
        Analiza riesgos identificados en el proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Análisis de riesgos del proyecto
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def check_project_compliance(self, project_id: int) -> Dict[str, Any]:
        """
        Verifica cumplimiento de estándares y políticas.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Reporte de cumplimiento
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # DETECCIÓN DE ANOMALÍAS
    # ==========================================

    @abstractmethod
    async def detect_project_anomalies(self, project_id: int) -> ProjectAnomalyReport:
        """
        Detecta anomalías en el proyecto usando algoritmos avanzados.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            ProjectAnomalyReport: Reporte de anomalías detectadas
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def detect_schedule_anomalies(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Detecta anomalías específicas en el cronograma.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            List[Dict[str, Any]]: Lista de anomalías de cronograma
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def detect_resource_anomalies(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Detecta anomalías en la asignación de recursos.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            List[Dict[str, Any]]: Lista de anomalías de recursos
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def detect_budget_anomalies(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Detecta anomalías en el presupuesto del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            List[Dict[str, Any]]: Lista de anomalías presupuestarias
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def detect_quality_anomalies(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Detecta anomalías en la calidad del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            List[Dict[str, Any]]: Lista de anomalías de calidad
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ANÁLISIS DE RENDIMIENTO
    # ==========================================

    @abstractmethod
    async def analyze_project_performance(
        self, 
        project_id: int
    ) -> ProjectPerformanceAnalysis:
        """
        Analiza el rendimiento integral del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            ProjectPerformanceAnalysis: Análisis completo de rendimiento
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_schedule_performance(self, project_id: int) -> Dict[str, Any]:
        """
        Analiza rendimiento específico del cronograma.
        
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
    async def analyze_cost_performance(self, project_id: int) -> Dict[str, Any]:
        """
        Analiza rendimiento de costos del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Análisis de rendimiento de costos
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_resource_performance(self, project_id: int) -> Dict[str, Any]:
        """
        Analiza rendimiento de recursos del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Análisis de rendimiento de recursos
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_quality_performance(self, project_id: int) -> Dict[str, Any]:
        """
        Analiza rendimiento de calidad del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Análisis de rendimiento de calidad
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # GENERACIÓN DE REPORTES DE ESTADO
    # ==========================================

    @abstractmethod
    async def generate_project_status_report(
        self, 
        project_id: int,
        report_type: str = "comprehensive"
    ) -> ProjectStatusReport:
        """
        Genera reporte completo de estado del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            report_type (str): Tipo de reporte (summary, detailed, comprehensive)
            
        Returns:
            ProjectStatusReport: Reporte de estado del proyecto
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def generate_executive_summary(self, project_id: int) -> Dict[str, Any]:
        """
        Genera resumen ejecutivo del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Resumen ejecutivo
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def generate_technical_report(self, project_id: int) -> Dict[str, Any]:
        """
        Genera reporte técnico detallado del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Reporte técnico detallado
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def generate_stakeholder_report(
        self,
        project_id: int,
        stakeholder_type: str = "client"
    ) -> Dict[str, Any]:
        """
        Genera reporte específico para stakeholders.
        
        Args:
            project_id (int): ID del proyecto
            stakeholder_type (str): Tipo de stakeholder (client, management, team)
            
        Returns:
            Dict[str, Any]: Reporte para stakeholders
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # DIAGNÓSTICOS COMPARATIVOS
    # ==========================================

    @abstractmethod
    async def compare_project_health(
        self,
        project_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Compara salud entre múltiples proyectos.
        
        Args:
            project_ids (List[int]): IDs de proyectos a comparar
            
        Returns:
            Dict[str, Any]: Comparación de salud de proyectos
            
        Raises:
            NotFoundError: Si algún proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def benchmark_project_performance(
        self,
        project_id: int,
        benchmark_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compara rendimiento del proyecto con benchmarks.
        
        Args:
            project_id (int): ID del proyecto
            benchmark_criteria (Dict[str, Any], optional): Criterios de benchmark
            
        Returns:
            Dict[str, Any]: Comparación con benchmarks
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_portfolio_health(
        self,
        portfolio_filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analiza salud del portafolio de proyectos.
        
        Args:
            portfolio_filters (Dict[str, Any], optional): Filtros para el portafolio
            
        Returns:
            Dict[str, Any]: Análisis de salud del portafolio
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # DIAGNÓSTICOS PREDICTIVOS
    # ==========================================

    @abstractmethod
    async def predict_project_outcomes(self, project_id: int) -> Dict[str, Any]:
        """
        Predice resultados futuros del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Predicciones de resultados
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def forecast_project_risks(self, project_id: int) -> Dict[str, Any]:
        """
        Pronostica riesgos futuros del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Pronóstico de riesgos
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def predict_resource_needs(self, project_id: int) -> Dict[str, Any]:
        """
        Predice necesidades futuras de recursos.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Predicción de necesidades de recursos
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # RECOMENDACIONES Y ACCIONES CORRECTIVAS
    # ==========================================

    @abstractmethod
    async def generate_improvement_recommendations(
        self,
        project_id: int
    ) -> List[Dict[str, Any]]:
        """
        Genera recomendaciones de mejora para el proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            List[Dict[str, Any]]: Lista de recomendaciones
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def suggest_corrective_actions(
        self,
        project_id: int,
        issue_categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Sugiere acciones correctivas para problemas identificados.
        
        Args:
            project_id (int): ID del proyecto
            issue_categories (List[str], optional): Categorías de problemas específicos
            
        Returns:
            List[Dict[str, Any]]: Lista de acciones correctivas
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def prioritize_action_items(
        self,
        project_id: int,
        action_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prioriza elementos de acción basado en impacto y urgencia.
        
        Args:
            project_id (int): ID del proyecto
            action_items (List[Dict[str, Any]]): Elementos de acción a priorizar
            
        Returns:
            List[Dict[str, Any]]: Elementos priorizados
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si los elementos de acción son inválidos
        """
        pass

    # ==========================================
    # MONITOREO CONTINUO
    # ==========================================

    @abstractmethod
    async def setup_health_monitoring(
        self,
        project_id: int,
        monitoring_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configura monitoreo continuo de salud del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            monitoring_config (Dict[str, Any]): Configuración de monitoreo
            
        Returns:
            Dict[str, Any]: Configuración de monitoreo establecida
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si la configuración es inválida
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_monitoring_alerts(
        self,
        project_id: int,
        severity_filter: Optional[DiagnosticSeverity] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene alertas de monitoreo del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            severity_filter (DiagnosticSeverity, optional): Filtro por severidad
            
        Returns:
            List[Dict[str, Any]]: Lista de alertas
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def update_diagnostic_thresholds(
        self,
        project_id: int,
        thresholds: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza umbrales de diagnóstico del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            thresholds (Dict[str, Any]): Nuevos umbrales de diagnóstico
            
        Returns:
            Dict[str, Any]: Umbrales actualizados
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si los umbrales son inválidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass