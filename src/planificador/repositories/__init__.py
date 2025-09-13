"""
Este paquete contiene todos los repositorios de la aplicación.

Cada subpaquete representa un repositorio para una entidad específica y
expone una fachada (`Facade`) como punto de entrada único para todas las
operaciones de esa entidad.

Uso:
    from planificador.repositories.project import ProjectRepositoryFacade
    from planificador.repositories.client import ClientRepositoryFacade
    from planificador.repositories.employee import EmployeeRepositoryFacade
"""

__all__ = [
    "ProjectRepositoryFacade",
    "ClientRepositoryFacade",
    "EmployeeRepositoryFacade",
]

from .client.client_repository_facade import ClientRepositoryFacade
from .employee.employee_repository_facade import EmployeeRepositoryFacade
from .project.project_repository_facade import ProjectRepositoryFacade