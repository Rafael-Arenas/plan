"""
Interfaz para las operaciones de validación de proyectos.

Esta interfaz define el contrato para todas las operaciones de validación
de datos, reglas de negocio y restricciones de proyectos.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import date

from planificador.models.project import ProjectStatus
from planificador.schemas.project.project import ValidationResultSchema


class IProjectValidationOperations(ABC):
    """
    Interfaz abstracta para las operaciones de validación de proyectos.
    
    Define el contrato para todas las operaciones de validación de datos,
    reglas de negocio, restricciones y verificaciones de integridad.
    """

    # ==========================================
    # VALIDACIONES DE CREACIÓN
    # ==========================================

    @abstractmethod
    async def validate_project_creation(
        self, 
        project_data: Dict[str, Any]
    ) -> ValidationResultSchema:
        """
        Valida todos los aspectos de la creación de un proyecto.
        
        Args:
            project_data (Dict[str, Any]): Datos del proyecto a validar
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            ValidationError: Si hay errores críticos de validación
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_project_data_integrity(
        self, 
        project_data: Dict[str, Any]
    ) -> ValidationResultSchema:
        """
        Valida la integridad de los datos del proyecto.
        
        Args:
            project_data (Dict[str, Any]): Datos del proyecto
            
        Returns:
            ValidationResultSchema: Resultado de la validación de integridad
            
        Raises:
            ValidationError: Si hay errores de integridad
        """
        pass

    # ==========================================
    # VALIDACIONES DE ACTUALIZACIÓN
    # ==========================================

    @abstractmethod
    async def validate_project_update(
        self, 
        project_id: int,
        update_data: Dict[str, Any]
    ) -> ValidationResultSchema:
        """
        Valida la actualización de un proyecto existente.
        
        Args:
            project_id (int): ID del proyecto a actualizar
            update_data (Dict[str, Any]): Datos de actualización
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si hay errores de validación
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_status_transition(
        self, 
        project_id: int,
        current_status: ProjectStatus,
        new_status: ProjectStatus
    ) -> ValidationResultSchema:
        """
        Valida si una transición de estado es permitida.
        
        Args:
            project_id (int): ID del proyecto
            current_status (ProjectStatus): Estado actual
            new_status (ProjectStatus): Estado objetivo
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            BusinessRuleError: Si la transición no está permitida
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # VALIDACIONES DE FECHAS
    # ==========================================

    @abstractmethod
    async def validate_project_dates(
        self, 
        start_date: date, 
        end_date: date, 
        project_id: Optional[int] = None
    ) -> ValidationResultSchema:
        """
        Valida las fechas de un proyecto.
        
        Args:
            start_date (date): Fecha de inicio
            end_date (date): Fecha de finalización
            project_id (int, optional): ID del proyecto (para actualizaciones)
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            ValidationError: Si las fechas no son válidas
        """
        pass

    @abstractmethod
    async def validate_date_constraints(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> ValidationResultSchema:
        """
        Valida restricciones de fechas específicas del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            start_date (date): Fecha de inicio propuesta
            end_date (date): Fecha de fin propuesta
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si hay conflictos de fechas
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_timeline_feasibility(
        self,
        project_id: int,
        proposed_timeline: Dict[str, Any]
    ) -> ValidationResultSchema:
        """
        Valida la factibilidad de un cronograma propuesto.
        
        Args:
            project_id (int): ID del proyecto
            proposed_timeline (Dict[str, Any]): Cronograma propuesto
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si el cronograma no es factible
        """
        pass

    # ==========================================
    # VALIDACIONES DE CÓDIGOS Y IDENTIFICADORES
    # ==========================================

    @abstractmethod
    async def validate_project_code(
        self, 
        project_code: str,
        project_id: Optional[int] = None
    ) -> ValidationResultSchema:
        """
        Valida el código único del proyecto.
        
        Args:
            project_code (str): Código del proyecto
            project_id (int, optional): ID del proyecto (para actualizaciones)
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            ValidationError: Si el código no es válido o ya existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_project_trigram(
        self, 
        trigram: str,
        project_id: Optional[int] = None
    ) -> ValidationResultSchema:
        """
        Valida el trigrama del proyecto.
        
        Args:
            trigram (str): Trigrama del proyecto
            project_id (int, optional): ID del proyecto (para actualizaciones)
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            ValidationError: Si el trigrama no es válido o ya existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # VALIDACIONES DE REGLAS DE NEGOCIO
    # ==========================================

    @abstractmethod
    async def validate_project_business_rules(
        self, 
        project_data: Dict[str, Any]
    ) -> ValidationResultSchema:
        """
        Valida todas las reglas de negocio aplicables al proyecto.
        
        Args:
            project_data (Dict[str, Any]): Datos del proyecto
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            BusinessRuleError: Si se violan reglas de negocio
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_client_project_rules(
        self,
        client_id: int,
        project_data: Dict[str, Any]
    ) -> ValidationResultSchema:
        """
        Valida reglas específicas del cliente para el proyecto.
        
        Args:
            client_id (int): ID del cliente
            project_data (Dict[str, Any]): Datos del proyecto
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            NotFoundError: Si el cliente no existe
            BusinessRuleError: Si se violan reglas del cliente
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_project_capacity_rules(
        self,
        project_data: Dict[str, Any]
    ) -> ValidationResultSchema:
        """
        Valida reglas de capacidad y recursos del proyecto.
        
        Args:
            project_data (Dict[str, Any]): Datos del proyecto
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            BusinessRuleError: Si se excede la capacidad disponible
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # VALIDACIONES DE DEPENDENCIAS
    # ==========================================

    @abstractmethod
    async def validate_project_dependencies(self, project_id: int) -> ValidationResultSchema:
        """
        Valida las dependencias del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si hay dependencias circulares o inválidas
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_circular_dependencies(
        self,
        project_id: int,
        dependency_ids: List[int]
    ) -> ValidationResultSchema:
        """
        Valida que no existan dependencias circulares.
        
        Args:
            project_id (int): ID del proyecto
            dependency_ids (List[int]): IDs de proyectos dependientes
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            ValidationError: Si se detectan dependencias circulares
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # VALIDACIONES DE RECURSOS
    # ==========================================

    @abstractmethod
    async def validate_resource_allocation(self, project_id: int) -> ValidationResultSchema:
        """
        Valida la asignación de recursos del proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si hay conflictos de recursos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_employee_availability(
        self,
        employee_id: int,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> ValidationResultSchema:
        """
        Valida la disponibilidad de un empleado para el proyecto.
        
        Args:
            employee_id (int): ID del empleado
            project_id (int): ID del proyecto
            start_date (date): Fecha de inicio de la asignación
            end_date (date): Fecha de fin de la asignación
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            NotFoundError: Si el empleado o proyecto no existe
            ValidationError: Si hay conflictos de disponibilidad
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # VALIDACIONES DE INTEGRIDAD DEL SISTEMA
    # ==========================================

    @abstractmethod
    async def check_project_data_integrity(self) -> ValidationResultSchema:
        """
        Verifica la integridad de todos los datos de proyectos.
        
        Returns:
            ValidationResultSchema: Resultado de la verificación
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_project_constraints(self, project_id: int) -> ValidationResultSchema:
        """
        Valida todas las restricciones aplicables al proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            ValidationResultSchema: Resultado de la validación
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si se violan restricciones
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def validate_system_consistency(self) -> ValidationResultSchema:
        """
        Valida la consistencia general del sistema de proyectos.
        
        Returns:
            ValidationResultSchema: Resultado de la validación del sistema
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass