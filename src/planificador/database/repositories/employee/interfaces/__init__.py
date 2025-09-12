# src/planificador/database/repositories/employee/interfaces/__init__.py

from .crud_interface import IEmployeeCrudOperations
from .query_interface import IEmployeeQueryOperations
from .validation_interface import IEmployeeValidationOperations
from .statistics_interface import IEmployeeStatisticsOperations
from .relationship_interface import IEmployeeRelationshipOperations
from .date_interface import IEmployeeDateOperations

__all__ = [
    'IEmployeeCrudOperations',
    'IEmployeeQueryOperations', 
    'IEmployeeValidationOperations',
    'IEmployeeStatisticsOperations',
    'IEmployeeRelationshipOperations',
    'IEmployeeDateOperations'
]