"""
Este módulo expone la fachada del repositorio de proyectos, que actúa como
un punto de entrada único para todas las operaciones relacionadas con la
entidad `Project`.

La fachada (`ProjectRepositoryFacade`) integra y coordina varios módulos
especializados para proporcionar una interfaz cohesiva y de alto nivel.

Uso:
    from planificador.repositories.project import ProjectRepositoryFacade

    # Obtener una instancia de la fachada
    project_repo = ProjectRepositoryFacade(session, logger)

    # Usar sus métodos
    await project_repo.create_project(new_project)
"""

from .project_repository_facade import ProjectRepositoryFacade

__all__ = [
    "ProjectRepositoryFacade",
]