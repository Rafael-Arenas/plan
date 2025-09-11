#!/usr/bin/env python3
"""Script temporal para probar el health_check del ClientRepositoryFacade."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from planificador.database.repositories.client.client_repository_facade import ClientRepositoryFacade


async def test_health_check():
    """Prueba el health_check del facade."""
    try:
        # Crear engine en memoria para prueba
        engine = create_async_engine('sqlite+aiosqlite:///:memory:')
        
        async with AsyncSession(engine) as session:
            facade = ClientRepositoryFacade(session)
            health = await facade.health_check()
            
            print("Health Check Results:")
            print("=" * 50)
            
            for key, value in health.items():
                if key == "modules" and isinstance(value, dict):
                    print(f"{key}:")
                    for module_name, module_status in value.items():
                        status_icon = "✅" if module_status == "healthy" else "❌"
                        print(f"  {status_icon} {module_name}: {module_status}")
                else:
                    print(f"{key}: {value}")
                    
    except Exception as e:
        print(f"Error durante health check: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_health_check())