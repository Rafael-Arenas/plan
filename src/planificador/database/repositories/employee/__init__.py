# src/planificador/database/repositories/employee/__init__.py
"""
Módulo de repositorio de empleados refactorizado.

Este módulo proporciona una implementación modular del repositorio de empleados,
separando las responsabilidades en componentes especializados:

- EmployeeRepository: Repositorio principal
- EmployeeQueryBuilder: Constructor de consultas especializadas
- EmployeeValidator: Validaciones de negocio
- EmployeeRelationshipManager: Gestión de relaciones
- EmployeeStatistics: Cálculos estadísticos

Ejemplo de uso:
    from planificador.database.repositories.employee import EmployeeRepository
    
    repo = EmployeeRepository(session)
    employee = await repo.get_by_employee_code("EMP001")
"""

from .employee_repository import EmployeeRepository

__all__ = ['EmployeeRepository']