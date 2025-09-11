"""Ejemplos prácticos de uso del ClientRepositoryFacade.

Este módulo contiene ejemplos completos y casos de uso reales
para demostrar las capacidades del ClientRepositoryFacade.

Autor: Sistema de Modularización
Fecha: 10 de septiembre de 2025
"""

import asyncio
from typing import Dict, List, Optional, Any

import pendulum
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from planificador.database.repositories.client.client_repository_facade import (
    ClientRepositoryFacade,
)
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientNotFoundError,
    ClientValidationError,
    ClientAlreadyExistsError,
)
from planificador.models.client import Client


class ClientManagementService:
    """Servicio de ejemplo que utiliza ClientRepositoryFacade.
    
    Demuestra patrones de uso comunes y mejores prácticas
    para la gestión de clientes en aplicaciones reales.
    """

    def __init__(self, session: AsyncSession):
        """Inicializar el servicio con una sesión de base de datos.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self.facade = ClientRepositoryFacade(session=session)
        self._session = session

    async def create_client_with_validation(
        self, client_data: Dict[str, Any]
    ) -> Optional[Client]:
        """Crear un cliente con validación completa.
        
        Este ejemplo demuestra un flujo completo de creación
        con todas las validaciones necesarias.
        
        Args:
            client_data: Datos del cliente a crear
            
        Returns:
            Cliente creado o None si hay errores
        """
        try:
            logger.info(f"Iniciando creación de cliente: {client_data.get('name')}")
            
            # 1. Validar que el nombre no exista
            if await self.facade.name_exists(client_data["name"]):
                logger.warning(f"Nombre ya existe: {client_data['name']}")
                raise ClientAlreadyExistsError(
                    f"Ya existe un cliente con el nombre: {client_data['name']}"
                )
            
            # 2. Validar que el email no exista
            if await self.facade.email_exists(client_data["email"]):
                logger.warning(f"Email ya existe: {client_data['email']}")
                raise ClientAlreadyExistsError(
                    f"Ya existe un cliente con el email: {client_data['email']}"
                )
            
            # 3. Validar formato de email
            if not await self.facade.validate_email_format(client_data["email"]):
                raise ClientValidationError(
                    f"Formato de email inválido: {client_data['email']}"
                )
            
            # 4. Validar todos los datos
            await self.facade.validate_client_data(client_data)
            
            # 5. Crear el cliente
            new_client = await self.facade.create_client(client_data)
            
            logger.success(f"Cliente creado exitosamente: ID {new_client.id}")
            return new_client
            
        except (ClientValidationError, ClientAlreadyExistsError) as e:
            logger.error(f"Error de validación al crear cliente: {e.message}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al crear cliente: {e}")
            return None

    async def update_client_safely(
        self, client_id: int, update_data: Dict[str, Any]
    ) -> Optional[Client]:
        """Actualizar un cliente con validaciones de seguridad.
        
        Args:
            client_id: ID del cliente a actualizar
            update_data: Datos a actualizar
            
        Returns:
            Cliente actualizado o None si hay errores
        """
        try:
            logger.info(f"Actualizando cliente ID: {client_id}")
            
            # 1. Verificar que el cliente existe
            existing_client = await self.facade.get_client_by_id(client_id)
            if not existing_client:
                logger.warning(f"Cliente no encontrado: ID {client_id}")
                return None
            
            # 2. Si se actualiza el email, validar que no exista
            if "email" in update_data:
                email_exists = await self.facade.email_exists(update_data["email"])
                if email_exists and update_data["email"] != existing_client.email:
                    logger.warning(f"Email ya existe: {update_data['email']}")
                    raise ClientAlreadyExistsError(
                        f"El email {update_data['email']} ya está en uso"
                    )
            
            # 3. Validar formato de email si se proporciona
            if "email" in update_data:
                if not await self.facade.validate_email_format(update_data["email"]):
                    raise ClientValidationError(
                        f"Formato de email inválido: {update_data['email']}"
                    )
            
            # 4. Actualizar el cliente
            updated_client = await self.facade.update_client(client_id, update_data)
            
            logger.success(f"Cliente actualizado exitosamente: ID {client_id}")
            return updated_client
            
        except (ClientNotFoundError, ClientValidationError, ClientAlreadyExistsError) as e:
            logger.error(f"Error al actualizar cliente: {e.message}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al actualizar cliente: {e}")
            return None

    async def get_client_dashboard_data(self, client_id: int) -> Optional[Dict[str, Any]]:
        """Obtener datos completos para el dashboard de un cliente.
        
        Este ejemplo demuestra cómo combinar múltiples operaciones
        del facade para crear vistas complejas.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con datos del dashboard o None si no existe
        """
        try:
            logger.info(f"Obteniendo datos de dashboard para cliente: {client_id}")
            
            # 1. Obtener datos básicos del cliente
            client = await self.facade.get_client_by_id(client_id)
            if not client:
                logger.warning(f"Cliente no encontrado: ID {client_id}")
                return None
            
            # 2. Obtener estadísticas del cliente
            statistics = await self.facade.get_client_statistics(client_id)
            
            # 3. Calcular días desde la creación
            created_date = pendulum.instance(client.created_at)
            days_since_creation = (pendulum.now() - created_date).days
            
            # 4. Verificar si hoy es día laboral
            is_business_day = await self.facade.validate_business_day(pendulum.now())
            
            # 5. Obtener próximo día laboral
            next_business_day = await self.facade.get_next_business_day(pendulum.now())
            
            dashboard_data = {
                "client_info": {
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                    "phone": client.phone,
                    "address": client.address,
                    "is_active": client.is_active,
                    "created_at": client.created_at.isoformat(),
                    "updated_at": client.updated_at.isoformat(),
                },
                "statistics": statistics,
                "time_info": {
                    "days_since_creation": days_since_creation,
                    "is_business_day_today": is_business_day,
                    "next_business_day": next_business_day.isoformat(),
                },
                "status": "active" if client.is_active else "inactive",
            }
            
            logger.success(f"Dashboard data obtenido para cliente: {client_id}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error al obtener dashboard data: {e}")
            return None

    async def generate_activity_report(
        self, limit: int = 10
    ) -> Dict[str, Any]:
        """Generar reporte de actividad de clientes.
        
        Args:
            limit: Número máximo de clientes top a incluir
            
        Returns:
            Diccionario con el reporte de actividad
        """
        try:
            logger.info(f"Generando reporte de actividad (top {limit})")
            
            # 1. Obtener todos los clientes activos
            active_clients = await self.facade.get_active_clients()
            
            # 2. Obtener top clientes por actividad
            top_clients = await self.facade.get_top_clients_by_activity(limit=limit)
            
            # 3. Generar estadísticas para cada cliente top
            top_clients_data = []
            for client in top_clients:
                stats = await self.facade.get_client_statistics(client.id)
                top_clients_data.append({
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                    "statistics": stats,
                })
            
            # 4. Calcular métricas generales
            total_clients = len(active_clients)
            
            report = {
                "generated_at": pendulum.now().isoformat(),
                "summary": {
                    "total_active_clients": total_clients,
                    "top_clients_count": len(top_clients_data),
                },
                "top_clients": top_clients_data,
                "metadata": {
                    "report_type": "activity_report",
                    "version": "1.0",
                },
            }
            
            logger.success(f"Reporte generado con {total_clients} clientes activos")
            return report
            
        except Exception as e:
            logger.error(f"Error al generar reporte de actividad: {e}")
            return {"error": str(e)}

    async def bulk_client_operations(
        self, clients_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Realizar operaciones en lote para múltiples clientes.
        
        Args:
            clients_data: Lista de datos de clientes a procesar
            
        Returns:
            Resumen de las operaciones realizadas
        """
        results = {
            "created": [],
            "errors": [],
            "total_processed": len(clients_data),
        }
        
        logger.info(f"Iniciando operaciones en lote para {len(clients_data)} clientes")
        
        for i, client_data in enumerate(clients_data):
            try:
                # Crear cada cliente individualmente
                new_client = await self.create_client_with_validation(client_data)
                
                if new_client:
                    results["created"].append({
                        "index": i,
                        "id": new_client.id,
                        "name": new_client.name,
                    })
                else:
                    results["errors"].append({
                        "index": i,
                        "name": client_data.get("name", "Unknown"),
                        "error": "Validation failed",
                    })
                    
            except Exception as e:
                results["errors"].append({
                    "index": i,
                    "name": client_data.get("name", "Unknown"),
                    "error": str(e),
                })
        
        # Commit de todas las operaciones exitosas
        if results["created"]:
            await self._session.commit()
            logger.success(f"Creados {len(results['created'])} clientes exitosamente")
        
        if results["errors"]:
            logger.warning(f"Errores en {len(results['errors'])} clientes")
        
        return results

    async def search_clients_advanced(
        self, 
        name_pattern: Optional[str] = None,
        email_pattern: Optional[str] = None,
        active_only: bool = True,
        date_range: Optional[tuple] = None
    ) -> List[Client]:
        """Búsqueda avanzada de clientes con múltiples filtros.
        
        Args:
            name_pattern: Patrón para buscar en el nombre
            email_pattern: Patrón para buscar en el email
            active_only: Solo clientes activos
            date_range: Tupla con (fecha_inicio, fecha_fin)
            
        Returns:
            Lista de clientes que coinciden con los criterios
        """
        try:
            logger.info("Iniciando búsqueda avanzada de clientes")
            
            results = []
            
            # Si se especifica búsqueda por nombre
            if name_pattern:
                client = await self.facade.get_client_by_name(name_pattern)
                if client:
                    results.append(client)
            
            # Si solo se quieren clientes activos
            if active_only and not name_pattern:
                results = await self.facade.get_active_clients()
            
            # Filtrar por rango de fechas si se especifica
            if date_range and len(date_range) == 2:
                start_date, end_date = date_range
                date_filtered = await self.facade.get_clients_by_date_range(
                    start_date, end_date
                )
                
                if results:
                    # Intersección de resultados
                    result_ids = {client.id for client in results}
                    date_filtered_ids = {client.id for client in date_filtered}
                    common_ids = result_ids.intersection(date_filtered_ids)
                    results = [client for client in results if client.id in common_ids]
                else:
                    results = date_filtered
            
            logger.success(f"Búsqueda completada: {len(results)} clientes encontrados")
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda avanzada: {e}")
            return []


# Ejemplos de uso directo

async def example_basic_operations():
    """Ejemplo básico de operaciones CRUD."""
    print("\n=== Ejemplo: Operaciones Básicas ===")
    
    # Configuración de base de datos (ejemplo)
    engine = create_async_engine("sqlite+aiosqlite:///example.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        facade = ClientRepositoryFacade(session=session)
        
        # Datos de ejemplo
        client_data = {
            "name": "Empresa Ejemplo",
            "email": "contacto@ejemplo.com",
            "phone": "+56912345678",
            "address": "Av. Ejemplo 123",
            "is_active": True,
        }
        
        try:
            # Crear cliente
            print("Creando cliente...")
            new_client = await facade.create_client(client_data)
            print(f"Cliente creado: ID {new_client.id}, Nombre: {new_client.name}")
            
            # Obtener cliente
            print("\nObteniendo cliente...")
            retrieved_client = await facade.get_client_by_id(new_client.id)
            print(f"Cliente obtenido: {retrieved_client.name}")
            
            # Actualizar cliente
            print("\nActualizando cliente...")
            update_data = {"phone": "+56987654321"}
            updated_client = await facade.update_client(new_client.id, update_data)
            print(f"Cliente actualizado: Nuevo teléfono {updated_client.phone}")
            
            # Obtener estadísticas
            print("\nObteniendo estadísticas...")
            stats = await facade.get_client_statistics(new_client.id)
            print(f"Estadísticas: {stats}")
            
            await session.commit()
            
        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()


async def example_service_usage():
    """Ejemplo usando el servicio de gestión de clientes."""
    print("\n=== Ejemplo: Uso del Servicio ===")
    
    # Configuración de base de datos (ejemplo)
    engine = create_async_engine("sqlite+aiosqlite:///example.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        service = ClientManagementService(session)
        
        # Datos de múltiples clientes
        clients_data = [
            {
                "name": "Tech Solutions",
                "email": "info@techsolutions.com",
                "phone": "+56911111111",
                "address": "Tech Street 100",
            },
            {
                "name": "Creative Agency",
                "email": "hello@creative.com",
                "phone": "+56922222222",
                "address": "Creative Ave 200",
            },
            {
                "name": "Business Corp",
                "email": "contact@business.com",
                "phone": "+56933333333",
                "address": "Business Blvd 300",
            },
        ]
        
        try:
            # Operaciones en lote
            print("Realizando operaciones en lote...")
            bulk_results = await service.bulk_client_operations(clients_data)
            print(f"Resultados: {bulk_results['total_processed']} procesados, "
                  f"{len(bulk_results['created'])} creados, "
                  f"{len(bulk_results['errors'])} errores")
            
            # Generar reporte de actividad
            print("\nGenerando reporte de actividad...")
            report = await service.generate_activity_report(limit=5)
            print(f"Reporte generado: {report['summary']['total_active_clients']} clientes activos")
            
            # Búsqueda avanzada
            print("\nRealizando búsqueda avanzada...")
            search_results = await service.search_clients_advanced(
                active_only=True,
                date_range=(pendulum.now().subtract(days=30), pendulum.now())
            )
            print(f"Búsqueda completada: {len(search_results)} clientes encontrados")
            
        except Exception as e:
            print(f"Error en el servicio: {e}")


async def example_date_operations():
    """Ejemplo de operaciones con fechas usando Pendulum."""
    print("\n=== Ejemplo: Operaciones de Fechas ===")
    
    # Configuración de base de datos (ejemplo)
    engine = create_async_engine("sqlite+aiosqlite:///example.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        facade = ClientRepositoryFacade(session=session)
        
        try:
            # Validar día laboral
            today = pendulum.now()
            is_business_day = await facade.validate_business_day(today)
            print(f"¿Hoy es día laboral? {is_business_day}")
            
            # Obtener próximo día laboral
            next_business_day = await facade.get_next_business_day(today)
            print(f"Próximo día laboral: {next_business_day.format('YYYY-MM-DD')}")
            
            # Calcular días laborales entre fechas
            start_date = pendulum.parse("2024-01-01")
            end_date = pendulum.parse("2024-01-31")
            business_days = await facade.calculate_business_days_between(
                start_date, end_date
            )
            print(f"Días laborales en enero 2024: {business_days}")
            
            # Obtener clientes por rango de fechas
            recent_clients = await facade.get_clients_by_date_range(
                pendulum.now().subtract(days=7), pendulum.now()
            )
            print(f"Clientes creados en los últimos 7 días: {len(recent_clients)}")
            
        except Exception as e:
            print(f"Error en operaciones de fechas: {e}")


if __name__ == "__main__":
    """Ejecutar ejemplos."""
    # Configurar logging
    logger.add(
        "client_facade_examples.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    
    # Ejecutar ejemplos
    asyncio.run(example_basic_operations())
    asyncio.run(example_service_usage())
    asyncio.run(example_date_operations())
    
    print("\n=== Ejemplos completados ===")