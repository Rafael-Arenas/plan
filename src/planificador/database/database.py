# src/planificador/database/database.py

from typing import Annotated, AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DatabaseError as SQLDatabaseError

from loguru import logger

from ..config.config import settings
from ..exceptions.infrastructure import (
    DatabaseError,
    DatabaseConnectionError,
    create_database_error,
    create_database_connection_error
)

# Base es una clase base para nuestros modelos ORM.
# SQLAlchemy la utiliza para mapear las clases a las tablas de la base de datos.
Base = declarative_base()


class DatabaseManager:
    """
    Gestor centralizado de conexiones a la base de datos.
    Implementa el patrón Singleton para garantizar una única instancia del engine.
    """
    
    _instance = None
    _engine: AsyncEngine = None
    _session_factory: async_sessionmaker[AsyncSession] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """
        Inicializa el engine de base de datos con configuraciones optimizadas.
        """
        try:
            # Configuraciones específicas para SQLite asíncrono
            connect_args = {}
            engine_kwargs = {
                "echo": settings.debug_mode if hasattr(settings, 'debug_mode') else False,
                "future": True,  # Habilita características de SQLAlchemy 2.0
            }
            
            # Configuraciones específicas para SQLite
            if "sqlite" in settings.database_url:
                connect_args.update({
                    "check_same_thread": False,  # Permite uso en múltiples threads
                })
                # Para SQLite, usamos StaticPool para evitar problemas de concurrencia
                engine_kwargs["poolclass"] = StaticPool
                engine_kwargs["connect_args"] = connect_args
            else:
                # Para bases de datos de producción (PostgreSQL, MySQL, etc.)
                engine_kwargs.update({
                    "pool_size": 20,  # Número de conexiones en el pool
                    "max_overflow": 30,  # Conexiones adicionales permitidas
                    "pool_pre_ping": True,  # Verifica conexiones antes de usar
                    "pool_recycle": 3600,  # Recicla conexiones cada hora
                })
            
            self._engine = create_async_engine(
                settings.database_url,
                **engine_kwargs
            )
            
            # Crea la fábrica de sesiones con configuraciones optimizadas
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,  # Mantiene objetos accesibles después del commit
                autoflush=True,  # Auto-flush antes de queries
                autocommit=False,  # Control manual de transacciones
            )
            
            logger.info(f"Engine de base de datos inicializado: {settings.database_url}")
            
        except OperationalError as e:
            logger.error(f"Error de conexión al inicializar engine: {e}")
            raise create_database_connection_error(
                message=f"No se pudo conectar a la base de datos: {e}",
                host=self._extract_host_from_url(settings.database_url),
                port=self._extract_port_from_url(settings.database_url),
                database=self._extract_database_from_url(settings.database_url),
                original_error=e
            )
        except SQLAlchemyError as e:
            logger.error(f"Error de SQLAlchemy al inicializar engine: {e}")
            raise create_database_error(
                message=f"Error al configurar el engine de base de datos: {e}",
                operation="initialize_engine",
                original_error=e
            )
        except Exception as e:
            logger.error(f"Error inesperado al inicializar engine: {e}")
            raise create_database_error(
                message=f"Error inesperado al inicializar engine de base de datos: {e}",
                operation="initialize_engine",
                original_error=e
            )
    
    def _extract_host_from_url(self, url: str) -> str:
        """
        Extrae el host de la URL de la base de datos.
        """
        try:
            if "sqlite" in url:
                return "localhost"
            # Para URLs como postgresql://user:pass@host:port/db
            if "://" in url and "@" in url:
                return url.split("@")[1].split(":")[0].split("/")[0]
            return "unknown"
        except Exception:
            return "unknown"
    
    def _extract_port_from_url(self, url: str) -> int:
        """
        Extrae el puerto de la URL de la base de datos.
        """
        try:
            if "sqlite" in url:
                return 0
            # Para URLs como postgresql://user:pass@host:port/db
            if "://" in url and "@" in url and ":" in url.split("@")[1]:
                port_part = url.split("@")[1].split(":")[1].split("/")[0]
                return int(port_part)
            return 0
        except Exception:
            return 0
    
    def _extract_database_from_url(self, url: str) -> str:
        """
        Extrae el nombre de la base de datos de la URL.
        """
        try:
            if "sqlite" in url:
                # Para SQLite, extraer el nombre del archivo
                return url.split("/")[-1].replace(".db", "")
            # Para URLs como postgresql://user:pass@host:port/db
            if "://" in url and "/" in url.split("://")[1]:
                return url.split("/")[-1]
            return "unknown"
        except Exception:
            return "unknown"
    
    @property
    def engine(self) -> AsyncEngine:
        """Retorna la instancia del engine."""
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Retorna la fábrica de sesiones."""
        return self._session_factory
    
    async def close(self) -> None:
        """
        Cierra todas las conexiones del engine.
        Debe llamarse al finalizar la aplicación.
        """
        if self._engine:
            await self._engine.dispose()
            logger.info("Conexiones de base de datos cerradas")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager para obtener una sesión de base de datos.
        Garantiza el cierre automático de la sesión.
        """
        async with self._session_factory() as session:
            try:
                yield session
            except OperationalError as e:
                await session.rollback()
                logger.error(f"Error de conexión en sesión de base de datos: {e}")
                raise create_database_connection_error(
                    message=f"Error de conexión durante la sesión de base de datos: {e}",
                    host=self._extract_host_from_url(settings.database_url),
                    port=self._extract_port_from_url(settings.database_url),
                    database=self._extract_database_from_url(settings.database_url),
                    original_error=e
                )
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Error de SQLAlchemy en sesión de base de datos: {e}")
                raise create_database_error(
                    message=f"Error de base de datos durante la sesión: {e}",
                    operation="database_session",
                    original_error=e
                )
            except Exception as e:
                await session.rollback()
                logger.exception(f"Error inesperado en sesión de base de datos: {e}")
                raise create_database_error(
                    message=f"Error inesperado durante la sesión de base de datos: {e}",
                    operation="database_session",
                    original_error=e
                )
            finally:
                await session.close()


# Configuración del motor de base de datos usando las nuevas configuraciones
def create_database_engine() -> AsyncEngine:
    """
    Crea y configura el motor de base de datos con optimizaciones específicas.
    """
    db_settings = settings.database_settings
    
    # Configuraciones base para todos los tipos de base de datos
    engine_kwargs = {
        "echo": db_settings.echo,
        "future": True,  # Usa la nueva API de SQLAlchemy 2.0
    }
    
    # Configuraciones específicas según el tipo de base de datos
    if settings.database_url.startswith("sqlite"):
        # Configuraciones optimizadas para SQLite
        engine_kwargs.update({
            "connect_args": {
                "check_same_thread": False,  # Permite uso en múltiples threads
                "timeout": 20,  # Timeout de conexión en segundos
            },
            "pool_pre_ping": db_settings.pool_pre_ping,
        })
    else:
        # Configuraciones para bases de datos con pool de conexiones (PostgreSQL, MySQL)
        engine_kwargs.update({
            "pool_size": db_settings.pool_size,
            "max_overflow": db_settings.max_overflow,
            "pool_recycle": db_settings.pool_recycle,
            "pool_pre_ping": db_settings.pool_pre_ping,
            "pool_timeout": 30,  # Timeout para obtener conexión del pool
        })
    
    return create_async_engine(settings.database_url, **engine_kwargs)


# Crear el motor de base de datos
engine = create_database_engine()

# Configuración del sessionmaker asíncrono
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Evita que los objetos expiren después del commit
    autoflush=False,  # Control manual del flush para mejor rendimiento
)


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()


# Funciones de utilidad para manejo de la base de datos


# Función para inicializar la base de datos al inicio de la aplicación
async def initialize_database() -> None:
    """
    Inicializa la base de datos creando las tablas necesarias.
    Debe llamarse al inicio de la aplicación.
    """
    try:
        logger.info("🔄 Inicializando base de datos...")
        
        # Crear tablas si no existen
        await create_tables()
        
        logger.info(f"✅ Base de datos inicializada correctamente")
            
    except DatabaseConnectionError:
        # Re-lanzar errores de conexión sin modificar
        raise
    except DatabaseError:
        # Re-lanzar errores de base de datos sin modificar
        raise
    except Exception as e:
        logger.exception(f"❌ Error inicializando base de datos: {e}")
        raise create_database_error(
            message=f"Error inesperado durante la inicialización de la base de datos: {e}",
            operation="initialize_database",
            original_error=e
        )


# Función para cerrar conexiones de base de datos de forma limpia
async def close_database() -> None:
    """
    Cierra todas las conexiones de base de datos de forma limpia.
    Debe llamarse al cerrar la aplicación.
    """
    try:
        logger.info("🔄 Cerrando conexiones de base de datos...")
        await engine.dispose()
        logger.info("✅ Conexiones de base de datos cerradas correctamente")
    except SQLAlchemyError as e:
        logger.error(f"Error de SQLAlchemy al cerrar la base de datos: {e}")
        raise create_database_error(
            message=f"Error al cerrar la conexión a la base de datos: {e}",
            operation="close_database",
            original_error=e
        )
    except Exception as e:
        logger.exception(f"❌ Error cerrando conexiones de base de datos: {e}")
        raise create_database_error(
            message=f"Error inesperado al cerrar la base de datos: {e}",
            operation="close_database",
            original_error=e
        )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency de FastAPI para obtener una sesión de base de datos.
    
    Utiliza el patrón de dependency injection con yield para:
    - Crear una nueva sesión para cada request
    - Garantizar el cierre automático de la sesión
    - Manejar rollback automático en caso de errores
    - Proporcionar logging de errores
    
    Yields:
        AsyncSession: Sesión de base de datos lista para usar
    
    Example:
        ```python
        @app.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    """
    async with db_manager.get_session() as session:
        yield session


# Type alias para dependency injection más limpia
# DatabaseDep = Annotated[AsyncSession, Depends(get_db)]


async def create_tables() -> None:
    """
    Crea todas las tablas definidas en los modelos.
    Debe llamarse durante la inicialización de la aplicación.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tablas de base de datos creadas")
    except OperationalError as e:
        logger.error(f"Error de conexión al crear tablas: {e}")
        raise create_database_connection_error(
            message=f"No se pudo conectar a la base de datos para crear tablas: {e}",
            host=db_manager._extract_host_from_url(settings.database_url),
            port=db_manager._extract_port_from_url(settings.database_url),
            database=db_manager._extract_database_from_url(settings.database_url),
            original_error=e
        )
    except SQLAlchemyError as e:
        logger.error(f"Error de SQLAlchemy al crear tablas: {e}")
        raise create_database_error(
            message=f"Error al crear las tablas de la base de datos: {e}",
            operation="create_tables",
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al crear tablas: {e}")
        raise create_database_error(
            message=f"Error inesperado al crear las tablas: {e}",
            operation="create_tables",
            original_error=e
        )


async def drop_tables() -> None:
    """
    Elimina todas las tablas de la base de datos.
    ⚠️ CUIDADO: Esta operación es destructiva e irreversible.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("⚠️ Todas las tablas han sido eliminadas de la base de datos")
    except OperationalError as e:
        logger.error(f"Error de conexión al eliminar tablas: {e}")
        raise create_database_connection_error(
            message=f"No se pudo conectar a la base de datos para eliminar tablas: {e}",
            host=db_manager._extract_host_from_url(settings.database_url),
            port=db_manager._extract_port_from_url(settings.database_url),
            database=db_manager._extract_database_from_url(settings.database_url),
            original_error=e
        )
    except SQLAlchemyError as e:
        logger.error(f"Error de SQLAlchemy al eliminar tablas: {e}")
        raise create_database_error(
            message=f"Error al eliminar las tablas de la base de datos: {e}",
            operation="drop_tables",
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al eliminar tablas: {e}")
        raise create_database_error(
            message=f"Error inesperado al eliminar las tablas: {e}",
            operation="drop_tables",
            original_error=e
        )