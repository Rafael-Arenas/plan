# examples/client_domain_service_examples.py

"""
Ejemplos de Uso del ClientDomainService

Este archivo contiene ejemplos prácticos de cómo utilizar el nuevo servicio de dominio
cliente, demostrando las diferentes capacidades y patrones de uso recomendados.

Características demostradas:
- Operaciones CRUD básicas
- Consultas simples y avanzadas
- Validaciones de negocio
- Estadísticas y métricas
- Manejo de errores
- Operaciones en lote
- Monitoreo de salud
"""

import asyncio
from uuid import UUID, uuid4
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from loguru import logger

from planificador.config.config import settings
from planificador.services.domain.client import ClientDomainService
from planificador.schemas.client import ClientCreate, ClientUpdate
from planificador.exceptions.repository_exceptions import RepositoryError
from planificador.exceptions.validation_exceptions import ValidationError
from planificador.exceptions.business_exceptions import BusinessRuleError


class ClientDomainServiceExamples:
    """
    Clase con ejemplos de uso del ClientDomainService.
    
    Demuestra patrones comunes de uso y mejores prácticas para
    interactuar con el servicio de dominio cliente.
    """
    
    def __init__(self):
        """Inicializa los ejemplos con configuración de base de datos."""
        self.engine = create_async_engine(
            settings.database_url,
            echo=settings.debug_mode
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def ejemplo_operaciones_crud_basicas(self):
        """
        Ejemplo: Operaciones CRUD básicas con el servicio de dominio.
        
        Demuestra cómo crear, leer, actualizar y eliminar clientes
        usando el ClientDomainService.
        """
        logger.info("=== Ejemplo: Operaciones CRUD Básicas ===")
        
        async with self.async_session() as session:
            # Inicializar el servicio de dominio
            client_service = ClientDomainService(session)
            
            try:
                # 1. Crear un nuevo cliente
                logger.info("1. Creando nuevo cliente...")
                client_data = ClientCreate(
                    name="Empresa Ejemplo S.A.",
                    code="EMP001",
                    email="contacto@empresa-ejemplo.com",
                    is_active=True,
                    notes="Cliente de ejemplo para demostración"
                )
                
                new_client = await client_service.create_client(client_data)
                logger.info(f"Cliente creado: {new_client.name} (ID: {new_client.id})")
                
                # 2. Obtener cliente por ID
                logger.info("2. Obteniendo cliente por ID...")
                retrieved_client = await client_service.get_client_by_id(new_client.id)
                if retrieved_client:
                    logger.info(f"Cliente encontrado: {retrieved_client.name}")
                
                # 3. Actualizar cliente
                logger.info("3. Actualizando cliente...")
                update_data = ClientUpdate(
                    name="Empresa Ejemplo Actualizada S.A.",
                    notes="Cliente actualizado con nueva información"
                )
                
                updated_client = await client_service.update_client(new_client.id, update_data)
                if updated_client:
                    logger.info(f"Cliente actualizado: {updated_client.name}")
                
                # 4. Eliminar cliente
                logger.info("4. Eliminando cliente...")
                deleted = await client_service.delete_client(new_client.id)
                logger.info(f"Cliente eliminado: {deleted}")
                
                await session.commit()
                
            except ValidationError as e:
                logger.error(f"Error de validación: {e.message}")
                await session.rollback()
            except BusinessRuleError as e:
                logger.error(f"Error de regla de negocio: {e.message}")
                await session.rollback()
            except RepositoryError as e:
                logger.error(f"Error de repositorio: {e.message}")
                await session.rollback()
    
    async def ejemplo_consultas_avanzadas(self):
        """
        Ejemplo: Consultas avanzadas y búsquedas.
        
        Demuestra el uso de filtros, ordenamiento, paginación
        y búsquedas difusas.
        """
        logger.info("=== Ejemplo: Consultas Avanzadas ===")
        
        async with self.async_session() as session:
            client_service = ClientDomainService(session)
            
            try:
                # 1. Búsqueda básica
                logger.info("1. Búsqueda básica de clientes...")
                basic_results = await client_service.search_clients_basic("Empresa")
                logger.info(f"Resultados básicos encontrados: {len(basic_results)}")
                
                # 2. Búsqueda avanzada con filtros
                logger.info("2. Búsqueda avanzada con filtros...")
                advanced_results = await client_service.search_clients_advanced(
                    filters={
                        "is_active": True,
                        "name_contains": "S.A."
                    },
                    sort_by="name",
                    sort_order="asc",
                    page=1,
                    page_size=10
                )
                logger.info(f"Resultados avanzados: {advanced_results['total']} total, "
                          f"{len(advanced_results['items'])} en página")
                
                # 3. Obtener clientes paginados
                logger.info("3. Obteniendo clientes con paginación...")
                paginated_results = await client_service.get_clients_paginated(
                    page=1,
                    page_size=5,
                    sort_by="name"
                )
                logger.info(f"Página 1: {len(paginated_results['items'])} clientes")
                
                # 4. Búsqueda difusa
                logger.info("4. Búsqueda difusa...")
                fuzzy_results = await client_service.search_clients_fuzzy(
                    "Empres",  # Término con error tipográfico
                    threshold=0.6
                )
                logger.info(f"Resultados difusos encontrados: {len(fuzzy_results)}")
                
                # 5. Consultas por criterios específicos
                logger.info("5. Consultas por criterios específicos...")
                active_clients = await client_service.get_active_clients()
                inactive_clients = await client_service.get_inactive_clients()
                logger.info(f"Clientes activos: {len(active_clients)}, "
                          f"Clientes inactivos: {len(inactive_clients)}")
                
            except Exception as e:
                logger.error(f"Error en consultas avanzadas: {e}")
    
    async def ejemplo_validaciones_negocio(self):
        """
        Ejemplo: Validaciones de reglas de negocio.
        
        Demuestra cómo usar las validaciones integradas
        del servicio de dominio.
        """
        logger.info("=== Ejemplo: Validaciones de Negocio ===")
        
        async with self.async_session() as session:
            client_service = ClientDomainService(session)
            
            try:
                # 1. Validar datos de creación
                logger.info("1. Validando datos de creación...")
                client_data = ClientCreate(
                    name="Cliente Validación",
                    code="VAL001",
                    email="validacion@ejemplo.com",
                    is_active=True
                )
                
                validation_result = await client_service.validate_client_creation(client_data)
                logger.info(f"Validación de creación: {validation_result}")
                
                # 2. Validar unicidad de email
                logger.info("2. Validando unicidad de email...")
                email_unique = await client_service.validate_email_uniqueness(
                    "nuevo@ejemplo.com"
                )
                logger.info(f"Email único: {email_unique}")
                
                # 3. Validar reglas de negocio
                logger.info("3. Validando reglas de negocio...")
                business_validation = await client_service.validate_business_rules(client_data)
                logger.info(f"Validación de negocio: {business_validation}")
                
                # 4. Crear cliente si las validaciones pasan
                if validation_result.get("is_valid", False):
                    logger.info("4. Creando cliente después de validaciones...")
                    new_client = await client_service.create_client(client_data)
                    logger.info(f"Cliente creado exitosamente: {new_client.id}")
                    await session.commit()
                
            except ValidationError as e:
                logger.error(f"Error de validación: {e.message}")
                logger.error(f"Detalles: {e.details}")
            except Exception as e:
                logger.error(f"Error en validaciones: {e}")
    
    async def ejemplo_estadisticas_metricas(self):
        """
        Ejemplo: Estadísticas y métricas del dominio cliente.
        
        Demuestra cómo obtener diferentes tipos de estadísticas
        y métricas de negocio.
        """
        logger.info("=== Ejemplo: Estadísticas y Métricas ===")
        
        async with self.async_session() as session:
            client_service = ClientDomainService(session)
            
            try:
                # 1. Estadísticas generales
                logger.info("1. Obteniendo estadísticas generales...")
                general_stats = await client_service.get_client_statistics()
                logger.info(f"Estadísticas generales: {general_stats}")
                
                # 2. Conteo por estado
                logger.info("2. Contando clientes por estado...")
                status_counts = await client_service.count_clients_by_status()
                logger.info(f"Conteo por estado: {status_counts}")
                
                # 3. Estadísticas de crecimiento
                logger.info("3. Analizando crecimiento (últimos 30 días)...")
                growth_stats = await client_service.get_client_growth_statistics(30)
                logger.info(f"Estadísticas de crecimiento: {growth_stats}")
                
                # 4. Métricas de actividad
                logger.info("4. Obteniendo métricas de actividad...")
                activity_metrics = await client_service.get_client_activity_metrics()
                logger.info(f"Métricas de actividad: {activity_metrics}")
                
            except Exception as e:
                logger.error(f"Error obteniendo estadísticas: {e}")
    
    async def ejemplo_operaciones_lote(self):
        """
        Ejemplo: Operaciones en lote optimizadas.
        
        Demuestra cómo crear múltiples clientes de manera
        eficiente usando operaciones en lote.
        """
        logger.info("=== Ejemplo: Operaciones en Lote ===")
        
        async with self.async_session() as session:
            client_service = ClientDomainService(session)
            
            try:
                # Preparar datos para creación en lote
                logger.info("Preparando datos para creación en lote...")
                clients_data = [
                    ClientCreate(
                        name=f"Cliente Lote {i}",
                        code=f"LOTE{i:03d}",
                        email=f"cliente{i}@lote.com",
                        is_active=True,
                        notes=f"Cliente {i} creado en lote"
                    )
                    for i in range(1, 6)  # Crear 5 clientes
                ]
                
                # Crear clientes en lote
                logger.info("Creando clientes en lote...")
                created_clients = await client_service.bulk_create_clients(clients_data)
                logger.info(f"Clientes creados en lote: {len(created_clients)}")
                
                # Mostrar resultados
                for client in created_clients:
                    logger.info(f"- {client.name} (ID: {client.id})")
                
                await session.commit()
                
            except Exception as e:
                logger.error(f"Error en operaciones en lote: {e}")
                await session.rollback()
    
    async def ejemplo_monitoreo_salud(self):
        """
        Ejemplo: Monitoreo de salud del servicio.
        
        Demuestra cómo usar las funciones de monitoreo
        y diagnóstico del servicio de dominio.
        """
        logger.info("=== Ejemplo: Monitoreo de Salud ===")
        
        async with self.async_session() as session:
            client_service = ClientDomainService(session)
            
            try:
                # 1. Verificar salud del servicio
                logger.info("1. Verificando salud del servicio...")
                service_health = await client_service.check_service_health()
                logger.info(f"Salud del servicio: {service_health}")
                
                # 2. Verificar conectividad de base de datos
                logger.info("2. Verificando conectividad de base de datos...")
                db_connectivity = await client_service.check_database_connectivity()
                logger.info(f"Conectividad BD: {db_connectivity}")
                
                # 3. Generar reporte completo de salud
                logger.info("3. Generando reporte completo de salud...")
                health_report = await client_service.generate_health_report()
                logger.info(f"Reporte de salud: {health_report}")
                
                # 4. Obtener información del servicio
                logger.info("4. Obteniendo información del servicio...")
                service_info = await client_service.get_service_info()
                logger.info(f"Información del servicio: {service_info}")
                
            except Exception as e:
                logger.error(f"Error en monitoreo de salud: {e}")
    
    async def ejemplo_manejo_errores(self):
        """
        Ejemplo: Manejo robusto de errores.
        
        Demuestra cómo manejar diferentes tipos de errores
        que pueden ocurrir en el servicio de dominio.
        """
        logger.info("=== Ejemplo: Manejo de Errores ===")
        
        async with self.async_session() as session:
            client_service = ClientDomainService(session)
            
            # 1. Error de validación - datos inválidos
            logger.info("1. Probando error de validación...")
            try:
                invalid_client = ClientCreate(
                    name="",  # Nombre vacío - debería fallar
                    code="",  # Código vacío - debería fallar
                    email="email-invalido",  # Email inválido
                    is_active=True
                )
                await client_service.create_client(invalid_client)
            except ValidationError as e:
                logger.warning(f"Error de validación capturado: {e.message}")
            except Exception as e:
                logger.error(f"Error inesperado: {e}")
            
            # 2. Error de entidad no encontrada
            logger.info("2. Probando error de entidad no encontrada...")
            try:
                non_existent_id = uuid4()
                client = await client_service.get_client_by_id(non_existent_id)
                if client is None:
                    logger.info("Cliente no encontrado (comportamiento esperado)")
            except Exception as e:
                logger.error(f"Error inesperado: {e}")
            
            # 3. Error de regla de negocio
            logger.info("3. Probando error de regla de negocio...")
            try:
                # Intentar crear cliente con email duplicado
                duplicate_client = ClientCreate(
                    name="Cliente Duplicado",
                    code="DUP001",
                    email="existente@ejemplo.com",  # Asumiendo que ya existe
                    is_active=True
                )
                await client_service.create_client(duplicate_client)
            except BusinessRuleError as e:
                logger.warning(f"Error de regla de negocio capturado: {e.message}")
            except ValidationError as e:
                logger.warning(f"Error de validación capturado: {e.message}")
            except Exception as e:
                logger.error(f"Error inesperado: {e}")
    
    async def ejecutar_todos_ejemplos(self):
        """
        Ejecuta todos los ejemplos en secuencia.
        
        Método principal que demuestra todas las capacidades
        del ClientDomainService.
        """
        logger.info("🚀 Iniciando ejemplos del ClientDomainService")
        
        try:
            await self.ejemplo_operaciones_crud_basicas()
            await self.ejemplo_consultas_avanzadas()
            await self.ejemplo_validaciones_negocio()
            await self.ejemplo_estadisticas_metricas()
            await self.ejemplo_operaciones_lote()
            await self.ejemplo_monitoreo_salud()
            await self.ejemplo_manejo_errores()
            
            logger.info("✅ Todos los ejemplos ejecutados exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error ejecutando ejemplos: {e}")
        finally:
            await self.engine.dispose()


async def main():
    """
    Función principal para ejecutar los ejemplos.
    
    Configura el logging y ejecuta todos los ejemplos
    del ClientDomainService.
    """
    # Configurar logging
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level="INFO"
    )
    
    # Ejecutar ejemplos
    examples = ClientDomainServiceExamples()
    await examples.ejecutar_todos_ejemplos()


if __name__ == "__main__":
    """
    Punto de entrada para ejecutar los ejemplos.
    
    Uso:
        poetry run python examples/client_domain_service_examples.py
    """
    asyncio.run(main())