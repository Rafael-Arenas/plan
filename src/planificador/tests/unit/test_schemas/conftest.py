"""
Este archivo conftest.py sirve como punto de entrada para cargar todos los fixtures
de los módulos de fixtures especializados.

Al importar los fixtures de otros archivos, pytest los descubre y los hace
disponibles para todas las pruebas en el directorio y subdirectorios.
"""

# Importar todos los fixtures de los módulos de fixtures
from .fixtures.base import *
from .fixtures.alert import *
from .fixtures.assignment import *
from .fixtures.client import *
from .fixtures.project import *
from .fixtures.team import *
from .fixtures.employee import *
from .fixtures.schedule import *
from .fixtures.vacation import *
from .fixtures.workload import *
from .fixtures.response import *