# src/planificador/init_db.py

import logging
import asyncio
from .database.database import engine, Base
from .models import __all__ as all_models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    """
    Genera el esquema de la base de datos creando todas las tablas de forma asíncrona.
    """
    logger.info("Creando tablas en la base de datos...")
    try:
        async with engine.begin() as conn:
            # El import de los modelos es necesario para que Base los reconozca
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tablas creadas exitosamente.")
    except Exception as e:
        logger.error(f"Error al crear las tablas: {e}")

if __name__ == "__main__":
    asyncio.run(init_db())