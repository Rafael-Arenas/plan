"""Módulo especializado para operaciones temporales de clientes.

Este módulo contiene todas las operaciones relacionadas con fechas, tiempo
y consultas temporales de clientes, extraídas del ClientRepository original
para mejorar la modularidad y especialización en manejo de fechas.

Autor: Sistema de Modularización
Fecha: 21 de agosto de 2025
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import pendulum
from pendulum import DateTime

from planificador.models.client import Client
from planificador.exceptions.repository_exceptions import (
    RepositoryError,
    convert_sqlalchemy_error
)
from planificador.database.repositories.client.client_query_builder import ClientQueryBuilder


class ClientDateOperations:
    """Clase especializada para operaciones temporales de clientes.
    
    Esta clase encapsula todas las operaciones relacionadas con fechas,
    tiempo y consultas temporales, proporcionando funcionalidades avanzadas
    para filtrado y análisis temporal de clientes.
    
    Attributes:
        session: Sesión asíncrona de SQLAlchemy
        query_builder: Constructor de consultas especializado
        _logger: Logger estructurado para la clase
    """
    
    def __init__(self, session: AsyncSession, query_builder: ClientQueryBuilder):
        """Inicializa las operaciones temporales de clientes.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
            query_builder: Constructor de consultas especializado
        """
        self.session = session
        self.query_builder = query_builder
        self._logger = logger.bind(component="ClientDateOperations")
    
    async def get_clients_created_current_week(self) -> List[Client]:
        """Obtiene clientes creados en la semana actual.
        
        Utiliza Pendulum para cálculos precisos de la semana actual,
        considerando el inicio de semana configurado.
        
        Returns:
            Lista de clientes creados en la semana actual
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            # Calcular inicio y fin de semana actual con Pendulum
            now = pendulum.now()
            week_start = now.start_of('week')
            week_end = now.end_of('week')
            
            self._logger.debug(
                f"Buscando clientes creados entre {week_start} y {week_end}"
            )
            
            # Construir consulta usando query_builder
            query = await self.query_builder.build_date_range_query(
                date_field='created_at',
                start_date=week_start,
                end_date=week_end
            )
            
            # Ejecutar consulta
            result = await self.session.execute(query)
            clients = result.scalars().all()
            
            self._logger.info(
                f"Encontrados {len(clients)} clientes creados en la semana actual"
            )
            return list(clients)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo clientes de semana actual: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_created_current_week",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes de semana actual: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo clientes de semana actual: {e}",
                operation="get_clients_created_current_week",
                entity_type="Client",
                original_error=e
            )
    
    async def get_clients_created_current_month(self) -> List[Client]:
        """Obtiene clientes creados en el mes actual.
        
        Utiliza Pendulum para cálculos precisos del mes actual,
        manejando correctamente los límites del mes.
        
        Returns:
            Lista de clientes creados en el mes actual
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            # Calcular inicio y fin de mes actual con Pendulum
            now = pendulum.now()
            month_start = now.start_of('month')
            month_end = now.end_of('month')
            
            self._logger.debug(
                f"Buscando clientes creados entre {month_start} y {month_end}"
            )
            
            # Construir consulta usando query_builder
            query = await self.query_builder.build_date_range_query(
                date_field='created_at',
                start_date=month_start,
                end_date=month_end
            )
            
            # Ejecutar consulta
            result = await self.session.execute(query)
            clients = result.scalars().all()
            
            self._logger.info(
                f"Encontrados {len(clients)} clientes creados en el mes actual"
            )
            return list(clients)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo clientes de mes actual: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_created_current_month",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes de mes actual: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo clientes de mes actual: {e}",
                operation="get_clients_created_current_month",
                entity_type="Client",
                original_error=e
            )
    
    async def get_clients_created_business_days_only(self) -> List[Client]:
        """Obtiene clientes creados solo en días laborables.
        
        Filtra clientes creados únicamente en días laborables (lunes a viernes),
        excluyendo fines de semana.
        
        Returns:
            Lista de clientes creados en días laborables
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            # Construir consulta para días laborables
            query = select(Client).where(
                and_(
                    # Lunes = 1, Viernes = 5 en Pendulum
                    func.strftime('%w', Client.created_at).between('1', '5'),
                    Client.created_at.isnot(None)
                )
            ).order_by(Client.created_at.desc())
            
            # Ejecutar consulta
            result = await self.session.execute(query)
            clients = result.scalars().all()
            
            # Filtrar adicionalmente con Pendulum para mayor precisión
            business_day_clients = []
            for client in clients:
                if client.created_at:
                    client_date = pendulum.parse(str(client.created_at))
                    if client_date.weekday() < 5:  # 0-4 son días laborables en Pendulum
                        business_day_clients.append(client)
            
            self._logger.info(
                f"Encontrados {len(business_day_clients)} clientes creados en días laborables"
            )
            return business_day_clients
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo clientes de días laborables: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_created_business_days_only",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes de días laborables: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo clientes de días laborables: {e}",
                operation="get_clients_created_business_days_only",
                entity_type="Client",
                original_error=e
            )
    
    async def get_clients_by_date_range(
        self, 
        start_date: DateTime, 
        end_date: DateTime,
        date_field: str = 'created_at'
    ) -> List[Client]:
        """Obtiene clientes en un rango de fechas específico.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            date_field: Campo de fecha a filtrar (por defecto 'created_at')
            
        Returns:
            Lista de clientes en el rango de fechas
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            # Validar fechas
            if start_date > end_date:
                raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
            
            self._logger.debug(
                f"Buscando clientes por {date_field} entre {start_date} y {end_date}"
            )
            
            # Construir consulta usando query_builder
            query = await self.query_builder.build_date_range_query(
                date_field=date_field,
                start_date=start_date,
                end_date=end_date
            )
            
            # Ejecutar consulta
            result = await self.session.execute(query)
            clients = result.scalars().all()
            
            self._logger.info(
                f"Encontrados {len(clients)} clientes en rango de fechas"
            )
            return list(clients)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo clientes por rango de fechas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_by_date_range",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes por rango de fechas: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo clientes por rango de fechas: {e}",
                operation="get_clients_by_date_range",
                entity_type="Client",
                original_error=e
            )
    
    async def get_client_creation_trends(
        self, 
        period: str = 'month',
        limit: int = 12
    ) -> List[Dict[str, Any]]:
        """Obtiene tendencias de creación de clientes por período.
        
        Args:
            period: Período de agrupación ('day', 'week', 'month', 'year')
            limit: Número máximo de períodos a retornar
            
        Returns:
            Lista de diccionarios con tendencias de creación
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            # Mapear períodos a formatos de fecha
            period_formats = {
                'day': '%Y-%m-%d',
                'week': '%Y-%W',
                'month': '%Y-%m',
                'year': '%Y'
            }
            
            if period not in period_formats:
                raise ValueError(f"Período no válido: {period}")
            
            format_str = period_formats[period]
            
            # Construir consulta de tendencias
            query = select(
                func.strftime(format_str, Client.created_at).label('period'),
                func.count(Client.id).label('count')
            ).where(
                Client.created_at.isnot(None)
            ).group_by(
                func.strftime(format_str, Client.created_at)
            ).order_by(
                func.strftime(format_str, Client.created_at).desc()
            ).limit(limit)
            
            # Ejecutar consulta
            result = await self.session.execute(query)
            trends_data = result.all()
            
            # Formatear resultados
            trends = []
            for row in trends_data:
                trend_item = {
                    'period': row.period,
                    'count': row.count,
                    'period_type': period
                }
                
                # Agregar fecha formateada con Pendulum
                try:
                    if period == 'day':
                        parsed_date = pendulum.parse(row.period)
                        trend_item['formatted_date'] = parsed_date.format('DD/MM/YYYY')
                    elif period == 'month':
                        year, month = row.period.split('-')
                        parsed_date = pendulum.create(int(year), int(month), 1)
                        trend_item['formatted_date'] = parsed_date.format('MMMM YYYY')
                    elif period == 'year':
                        trend_item['formatted_date'] = row.period
                except Exception:
                    trend_item['formatted_date'] = row.period
                
                trends.append(trend_item)
            
            self._logger.info(
                f"Obtenidas {len(trends)} tendencias de creación por {period}"
            )
            return trends
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo tendencias de creación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_creation_trends",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo tendencias de creación: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo tendencias de creación: {e}",
                operation="get_client_creation_trends",
                entity_type="Client",
                original_error=e
            )
    
    async def get_clients_by_age_range(
        self, 
        min_age: int, 
        max_age: int
    ) -> List[Client]:
        """Obtiene clientes en un rango de edad específico.
        
        Args:
            min_age: Edad mínima
            max_age: Edad máxima
            
        Returns:
            Lista de clientes en el rango de edad
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            # Calcular fechas límite con Pendulum
            now = pendulum.now()
            max_birth_date = now.subtract(years=min_age)
            min_birth_date = now.subtract(years=max_age + 1)
            
            self._logger.debug(
                f"Buscando clientes con edad entre {min_age} y {max_age} años"
            )
            
            # Construir consulta
            query = select(Client).where(
                and_(
                    Client.birth_date.isnot(None),
                    Client.birth_date >= min_birth_date.date(),
                    Client.birth_date <= max_birth_date.date()
                )
            ).order_by(Client.birth_date.desc())
            
            # Ejecutar consulta
            result = await self.session.execute(query)
            clients = result.scalars().all()
            
            self._logger.info(
                f"Encontrados {len(clients)} clientes en rango de edad {min_age}-{max_age}"
            )
            return list(clients)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo clientes por rango de edad: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_by_age_range",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes por rango de edad: {e}")
            raise RepositoryError(
                message=f"Error inesperado obteniendo clientes por rango de edad: {e}",
                operation="get_clients_by_age_range",
                entity_type="Client",
                original_error=e
            )
    
    async def calculate_client_age(self, client_id: int) -> Optional[int]:
        """Calcula la edad actual de un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Edad del cliente en años o None si no tiene fecha de nacimiento
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        try:
            # Obtener cliente
            client = await self.session.get(Client, client_id)
            if not client or not client.birth_date:
                return None
            
            # Calcular edad con Pendulum
            birth_date = pendulum.parse(str(client.birth_date))
            now = pendulum.now()
            age = now.diff(birth_date).in_years()
            
            self._logger.debug(f"Cliente {client_id} tiene {age} años")
            return age
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error calculando edad del cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="calculate_client_age",
                entity_type="Client",
                entity_id=str(client_id)
            )
        except Exception as e:
            self._logger.error(f"Error inesperado calculando edad del cliente {client_id}: {e}")
            raise RepositoryError(
                message=f"Error inesperado calculando edad del cliente {client_id}: {e}",
                operation="calculate_client_age",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )