"""
Interfaz para las operaciones CRUD de proyectos.

Esta interfaz define el contrato para todas las operaciones básicas de creación,
lectura, actualización y eliminación de proyectos.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date

from planificador.models.project import Project, ProjectStatus
from planificador.schemas.project.project import ProjectCreate, ProjectUpdate


class IProjectCrudOperations(ABC):
    """
    Interfaz abstracta para las operaciones CRUD de proyectos.
    
    Define el contrato para todas las operaciones básicas de gestión de proyectos
    incluyendo creación, lectura, actualización, eliminación, archivado y restauración.
    """

    # ==========================================
    # OPERACIONES DE CREACIÓN
    # ==========================================

    @abstractmethod
    async def create_project(self, project_data: ProjectCreate) -> Project:
        """
        Crea un nuevo proyecto en el sistema.
        
        Args:
            project_data (ProjectCreate): Datos del proyecto a crear
            
        Returns:
            Project: El proyecto creado con todos sus datos
            
        Raises:
            ValidationError: Si los datos del proyecto no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def duplicate_project(
        self, 
        project_id: int, 
        new_name: Optional[str] = None,
        new_code: Optional[str] = None
    ) -> Project:
        """
        Duplica un proyecto existente con nuevos identificadores.
        
        Args:
            project_id (int): ID del proyecto a duplicar
            new_name (str, optional): Nuevo nombre para el proyecto duplicado
            new_code (str, optional): Nuevo código para el proyecto duplicado
            
        Returns:
            Project: El proyecto duplicado
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si los nuevos datos no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # OPERACIONES DE LECTURA
    # ==========================================

    @abstractmethod
    async def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto por su ID.
        
        Args:
            project_id (int): ID del proyecto a buscar
            
        Returns:
            Optional[Project]: El proyecto encontrado o None si no existe
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_project_by_code(self, project_code: str) -> Optional[Project]:
        """
        Obtiene un proyecto por su código único.
        
        Args:
            project_code (str): Código del proyecto a buscar
            
        Returns:
            Optional[Project]: El proyecto encontrado o None si no existe
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_all_projects(
        self, 
        include_archived: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Project]:
        """
        Obtiene todos los proyectos del sistema.
        
        Args:
            include_archived (bool): Si incluir proyectos archivados
            limit (int, optional): Límite de resultados
            offset (int, optional): Desplazamiento para paginación
            
        Returns:
            List[Project]: Lista de proyectos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # OPERACIONES DE ACTUALIZACIÓN
    # ==========================================

    @abstractmethod
    async def update_project(
        self, 
        project_id: int, 
        project_data: ProjectUpdate
    ) -> Optional[Project]:
        """
        Actualiza un proyecto existente.
        
        Args:
            project_id (int): ID del proyecto a actualizar
            project_data (ProjectUpdate): Datos de actualización
            
        Returns:
            Optional[Project]: El proyecto actualizado o None si no existe
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si los datos de actualización no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def update_project_status(
        self, 
        project_id: int, 
        new_status: ProjectStatus
    ) -> Optional[Project]:
        """
        Actualiza únicamente el estado de un proyecto.
        
        Args:
            project_id (int): ID del proyecto
            new_status (ProjectStatus): Nuevo estado del proyecto
            
        Returns:
            Optional[Project]: El proyecto con el estado actualizado
            
        Raises:
            NotFoundError: Si el proyecto no existe
            ValidationError: Si la transición de estado no es válida
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # OPERACIONES DE ELIMINACIÓN
    # ==========================================

    @abstractmethod
    async def delete_project(self, project_id: int) -> bool:
        """
        Elimina permanentemente un proyecto del sistema.
        
        Args:
            project_id (int): ID del proyecto a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si no existía
            
        Raises:
            BusinessRuleError: Si el proyecto no puede ser eliminado
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def soft_delete_project(self, project_id: int) -> Optional[Project]:
        """
        Realiza una eliminación lógica del proyecto.
        
        Args:
            project_id (int): ID del proyecto a eliminar lógicamente
            
        Returns:
            Optional[Project]: El proyecto marcado como eliminado
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # OPERACIONES DE ARCHIVADO
    # ==========================================

    @abstractmethod
    async def archive_project(self, project_id: int) -> Optional[Project]:
        """
        Archiva un proyecto completado o cancelado.
        
        Args:
            project_id (int): ID del proyecto a archivar
            
        Returns:
            Optional[Project]: El proyecto archivado
            
        Raises:
            NotFoundError: Si el proyecto no existe
            BusinessRuleError: Si el proyecto no puede ser archivado
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def restore_project(self, project_id: int) -> Optional[Project]:
        """
        Restaura un proyecto archivado o eliminado lógicamente.
        
        Args:
            project_id (int): ID del proyecto a restaurar
            
        Returns:
            Optional[Project]: El proyecto restaurado
            
        Raises:
            NotFoundError: Si el proyecto no existe
            BusinessRuleError: Si el proyecto no puede ser restaurado
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # OPERACIONES DE VERIFICACIÓN
    # ==========================================

    @abstractmethod
    async def project_exists(self, project_id: int) -> bool:
        """
        Verifica si un proyecto existe en el sistema.
        
        Args:
            project_id (int): ID del proyecto a verificar
            
        Returns:
            bool: True si el proyecto existe, False en caso contrario
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def project_code_exists(self, project_code: str) -> bool:
        """
        Verifica si un código de proyecto ya está en uso.
        
        Args:
            project_code (str): Código del proyecto a verificar
            
        Returns:
            bool: True si el código existe, False en caso contrario
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass