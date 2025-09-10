"""Configuración global de pytest y fixtures compartidas."""

import asyncio
import pytest
import pytest_asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger

from planificador.config.config import settings
from planificador.database.database import Base, get_db, db_manager

# Importar fixtures desde el módulo fixtures
from planificador.tests.fixtures.database import *


# Configuración de pytest
pytest_plugins = ["pytest_asyncio"]

# Configuración de pytest-asyncio para evitar warnings
pytestmark = pytest.mark.asyncio(scope="session")


@pytest.fixture(scope="session")
async def test_engine():
    """Fixture para el motor de base de datos de testing.
    
    Crea un motor SQLAlchemy asíncrono específico para testing
    usando una base de datos en memoria.
    """
    # Base de datos en memoria para testing
    test_database_url = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(
        test_database_url,
        echo=False,  # Cambiar a True para debug SQL
        future=True,
    )
    
    # Crear todas las tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Fixture para sesión de base de datos de testing.
    
    Proporciona una sesión SQLAlchemy asíncrona que se revierte
    automáticamente al final de cada test.
    """
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        # Iniciar transacción
        transaction = await session.begin()
        
        try:
            yield session
        finally:
            # Rollback automático al final del test
            await transaction.rollback()
            await session.close()


@pytest.fixture(scope="function")
def override_get_session(test_session: AsyncSession):
    """Fixture para sobrescribir la dependencia de sesión.
    
    Permite que los tests usen la sesión de testing en lugar
    de la sesión de producción.
    """
    async def _override_get_session():
        yield test_session
    
    return _override_get_session


@pytest_asyncio.fixture
async def db_session():
    """Fixture que proporciona una sesión de base de datos con rollback automático."""
    async with db_manager.get_session() as session:
        # Iniciar una transacción que se puede hacer rollback
        transaction = await session.begin()
        try:
            yield session
        finally:
            # Hacer rollback de la transacción para limpiar los datos de prueba
            await transaction.rollback()


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Fixture para configurar logging específico para testing.
    
    Se ejecuta automáticamente antes de cada test.
    """
    # Configurar loguru para testing
    logger.remove()  # Remover handlers existentes
    
    # Agregar handler para testing con nivel DEBUG
    logger.add(
        sink=lambda msg: None,  # No output durante tests
        level="DEBUG",
        format="{time} | {level} | {name}:{function}:{line} | {message}",
        backtrace=True,
        diagnose=True,
    )
    
    yield
    
    # Cleanup después del test
    logger.remove()


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Fixture que proporciona el directorio de datos de testing.
    
    Returns:
        Path: Ruta al directorio de datos de testing
    """
    return Path(__file__).parent / "fixtures" / "data"


# Configuración de marcadores pytest
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.slow = pytest.mark.slow