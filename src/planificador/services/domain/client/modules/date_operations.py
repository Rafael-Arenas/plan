# src/planificador/services/domain/client/modules/date_operations.py

"""
Módulo de operaciones de fechas para el servicio de dominio de cliente.

Este módulo implementa la gestión de fechas y tiempo relacionadas con clientes,
utilizando Pendulum para manejo robusto de fechas y zonas horarias.
"""

from typing import Any, Dict, List, Optional

import pendulum
from loguru import logger

from planificador.exceptions import RepositoryError, ValidationError
from planificador.repositories.client.client_repository_facade import ClientRepositoryFacade
from planificador.schemas import Client
from planificador.services.domain.client.interfaces.date_interface import IDateOperations


class DateOperations(IDateOperations):
    """
    Implementación de operaciones de fechas para el dominio de cliente.
    
    Esta clase encapsula la gestión de fechas y tiempo relacionadas con clientes,
    proporcionando métodos para consultas temporales y cálculos de fechas.
    """

    def __init__(self, client_repository: ClientRepositoryFacade):
        """
        Inicializa el módulo de operaciones de fechas.
        
        Args:
            client_repository: Facade del repositorio de cliente
        """
        self._client_repository = client_repository
        self._logger = logger

    async def get_clients_created_in_period(
        self,
        start_date: pendulum.DateTime,
        end_date: pendulum.DateTime
    ) -> List[Client]:
        """
        Obtiene clientes creados en un período específico.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            List[Client]: Lista de clientes creados en el período
        """
        try:
            self._logger.debug(f"Obteniendo clientes creados entre {start_date} y {end_date}")
            
            # Validar fechas
            if start_date > end_date:
                raise ValidationError(
                    message="La fecha de inicio debe ser anterior a la fecha de fin",
                    field="start_date",
                    value=str(start_date)
                )
            
            # Convertir a datetime nativo para compatibilidad con SQLAlchemy
            start_datetime = start_date.to_datetime_string()
            end_datetime = end_date.to_datetime_string()
            
            # TODO: Implementar filtro por fecha de creación cuando esté disponible en el modelo
            self._logger.warning("Filtro por fecha de creación no implementado - campo created_at no disponible")
            
            # Por ahora retornamos todos los clientes como placeholder
            clients = await self._client_repository.get_all_clients()
            result = [Client.model_validate(client) for client in clients]
            
            self._logger.debug(f"Clientes en período (placeholder): {len(result)}")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener clientes por período de creación: {e}")
            raise RepositoryError(
                message=f"Error al filtrar por período: {e}",
                operation="get_clients_created_in_period",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_updated_in_period(
        self,
        start_date: pendulum.DateTime,
        end_date: pendulum.DateTime
    ) -> List[Client]:
        """
        Obtiene clientes actualizados en un período específico.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            List[Client]: Lista de clientes actualizados en el período
        """
        try:
            self._logger.debug(f"Obteniendo clientes actualizados entre {start_date} y {end_date}")
            
            # Validar fechas
            if start_date > end_date:
                raise ValidationError(
                    message="La fecha de inicio debe ser anterior a la fecha de fin",
                    field="start_date",
                    value=str(start_date)
                )
            
            # TODO: Implementar filtro por fecha de actualización cuando esté disponible en el modelo
            self._logger.warning("Filtro por fecha de actualización no implementado - campo updated_at no disponible")
            
            # Por ahora retornamos clientes activos como placeholder
            filters = {"is_active": True}
            clients = await self._client_repository.get_clients_by_filters(filters)
            result = [Client.model_validate(client) for client in clients]
            
            self._logger.debug(f"Clientes actualizados en período (placeholder): {len(result)}")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener clientes por período de actualización: {e}")
            raise RepositoryError(
                message=f"Error al filtrar por período de actualización: {e}",
                operation="get_clients_updated_in_period",
                entity_type="Client",
                original_error=e
            )

    async def calculate_client_age_in_days(self, client_id: int) -> int:
        """
        Calcula la edad de un cliente en días desde su creación.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            int: Edad del cliente en días
        """
        try:
            self._logger.debug(f"Calculando edad del cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=client_id
                )
            
            # TODO: Implementar cálculo real cuando esté disponible created_at
            self._logger.warning("Cálculo de edad no implementado - campo created_at no disponible")
            
            # Por ahora retornamos un valor placeholder
            age_days = 30  # Placeholder: 30 días
            
            self._logger.debug(f"Edad del cliente {client_id}: {age_days} días")
            
            return age_days
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al calcular edad del cliente {client_id}: {e}")
            raise RepositoryError(
                message=f"Error al calcular edad: {e}",
                operation="calculate_client_age_in_days",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def get_clients_older_than_days(self, days: int) -> List[Client]:
        """
        Obtiene clientes que tienen más de X días desde su creación.
        
        Args:
            days: Número de días
            
        Returns:
            List[Client]: Lista de clientes más antiguos que el número de días especificado
        """
        try:
            self._logger.debug(f"Obteniendo clientes con más de {days} días")
            
            if days < 0:
                raise ValidationError(
                    message="El número de días debe ser mayor o igual a 0",
                    field="days",
                    value=days
                )
            
            # Calcular fecha límite
            cutoff_date = pendulum.now().subtract(days=days)
            
            # TODO: Implementar filtro real cuando esté disponible created_at
            self._logger.warning("Filtro por antigüedad no implementado - campo created_at no disponible")
            
            # Por ahora retornamos lista vacía
            return []
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener clientes antiguos: {e}")
            raise RepositoryError(
                message=f"Error al filtrar por antigüedad: {e}",
                operation="get_clients_older_than_days",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_newer_than_days(self, days: int) -> List[Client]:
        """
        Obtiene clientes que tienen menos de X días desde su creación.
        
        Args:
            days: Número de días
            
        Returns:
            List[Client]: Lista de clientes más recientes que el número de días especificado
        """
        try:
            self._logger.debug(f"Obteniendo clientes con menos de {days} días")
            
            if days < 0:
                raise ValidationError(
                    message="El número de días debe ser mayor o igual a 0",
                    field="days",
                    value=days
                )
            
            # Calcular fecha límite
            cutoff_date = pendulum.now().subtract(days=days)
            
            # TODO: Implementar filtro real cuando esté disponible created_at
            self._logger.warning("Filtro por recencia no implementado - campo created_at no disponible")
            
            # Por ahora retornamos todos los clientes activos como placeholder
            filters = {"is_active": True}
            clients = await self._client_repository.get_clients_by_filters(filters)
            result = [Client.model_validate(client) for client in clients]
            
            self._logger.debug(f"Clientes recientes (placeholder): {len(result)}")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener clientes recientes: {e}")
            raise RepositoryError(
                message=f"Error al filtrar por recencia: {e}",
                operation="get_clients_newer_than_days",
                entity_type="Client",
                original_error=e
            )

    async def get_client_timeline_events(self, client_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene eventos de la línea de tiempo de un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            List[Dict[str, Any]]: Lista de eventos de la línea de tiempo
        """
        try:
            self._logger.debug(f"Obteniendo línea de tiempo del cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=client_id
                )
            
            # Crear eventos básicos de línea de tiempo
            timeline_events = []
            
            # Evento de creación (placeholder)
            creation_event = {
                "event_type": "client_created",
                "event_date": pendulum.now().subtract(days=30).to_iso8601_string(),  # Placeholder
                "description": f"Cliente '{client.name}' fue creado",
                "details": {
                    "client_name": client.name,
                    "client_code": client.code,
                    "initial_status": "active" if client.is_active else "inactive"
                }
            }
            timeline_events.append(creation_event)
            
            # TODO: Agregar más eventos cuando estén disponibles los campos de auditoría
            # - Eventos de actualización
            # - Eventos de cambio de estado
            # - Eventos de asignación de proyectos
            # - Eventos de modificación de datos
            
            self._logger.debug(f"Eventos de línea de tiempo para cliente {client_id}: {len(timeline_events)}")
            
            return timeline_events
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener línea de tiempo: {e}")
            raise RepositoryError(
                message=f"Error en línea de tiempo: {e}",
                operation="get_client_timeline_events",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def calculate_client_activity_period(self, client_id: int) -> Dict[str, Any]:
        """
        Calcula el período de actividad de un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Dict[str, Any]: Información del período de actividad
        """
        try:
            self._logger.debug(f"Calculando período de actividad del cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=client_id
                )
            
            # Calcular período de actividad (placeholder)
            now = pendulum.now()
            creation_date = now.subtract(days=30)  # Placeholder
            last_activity_date = now.subtract(days=1)  # Placeholder
            
            activity_period = {
                "client_id": client_id,
                "client_name": client.name,
                "creation_date": creation_date.to_iso8601_string(),
                "last_activity_date": last_activity_date.to_iso8601_string(),
                "total_days_active": (last_activity_date - creation_date).days,
                "is_currently_active": client.is_active,
                "activity_status": "active" if client.is_active else "inactive",
                "days_since_last_activity": (now - last_activity_date).days
            }
            
            # TODO: Implementar cálculos reales cuando estén disponibles los campos de auditoría
            self._logger.warning("Cálculo de período de actividad usando datos placeholder")
            
            self._logger.debug(f"Período de actividad calculado para cliente {client_id}")
            
            return activity_period
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al calcular período de actividad: {e}")
            raise RepositoryError(
                message=f"Error en período de actividad: {e}",
                operation="calculate_client_activity_period",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def get_client_anniversary_dates(self, client_id: int) -> Dict[str, Any]:
        """
        Obtiene fechas de aniversario relevantes para un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Dict[str, Any]: Fechas de aniversario del cliente
        """
        try:
            self._logger.debug(f"Obteniendo fechas de aniversario del cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=client_id
                )
            
            # Calcular fechas de aniversario (placeholder)
            now = pendulum.now()
            creation_date = now.subtract(days=30)  # Placeholder
            
            anniversary_dates = {
                "client_id": client_id,
                "client_name": client.name,
                "creation_anniversary": {
                    "original_date": creation_date.to_iso8601_string(),
                    "next_anniversary": creation_date.add(years=1).to_iso8601_string(),
                    "days_until_next": (creation_date.add(years=1) - now).days,
                    "years_since_creation": (now - creation_date).days // 365
                },
                "milestones": [
                    {
                        "milestone": "30_days",
                        "date": creation_date.add(days=30).to_iso8601_string(),
                        "achieved": True,
                        "description": "30 días desde la creación"
                    },
                    {
                        "milestone": "90_days",
                        "date": creation_date.add(days=90).to_iso8601_string(),
                        "achieved": (now - creation_date).days >= 90,
                        "description": "90 días desde la creación"
                    },
                    {
                        "milestone": "1_year",
                        "date": creation_date.add(years=1).to_iso8601_string(),
                        "achieved": (now - creation_date).days >= 365,
                        "description": "1 año desde la creación"
                    }
                ]
            }
            
            # TODO: Agregar más fechas de aniversario cuando estén disponibles
            # - Primer proyecto asignado
            # - Última actualización importante
            # - Cambios de estado significativos
            
            self._logger.debug(f"Fechas de aniversario obtenidas para cliente {client_id}")
            
            return anniversary_dates
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener fechas de aniversario: {e}")
            raise RepositoryError(
                message=f"Error en fechas de aniversario: {e}",
                operation="get_client_anniversary_dates",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def schedule_client_date_reminders(self, client_id: int) -> List[Dict[str, Any]]:
        """
        Programa recordatorios basados en fechas para un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            List[Dict[str, Any]]: Lista de recordatorios programados
        """
        try:
            self._logger.debug(f"Programando recordatorios de fechas para cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=client_id
                )
            
            # Obtener fechas de aniversario
            anniversary_data = await self.get_client_anniversary_dates(client_id)
            
            # Crear recordatorios
            reminders = []
            
            # Recordatorio de aniversario de creación
            next_anniversary = pendulum.parse(anniversary_data["creation_anniversary"]["next_anniversary"])
            reminder_date = next_anniversary.subtract(days=7)  # 7 días antes
            
            if reminder_date > pendulum.now():
                reminders.append({
                    "reminder_id": f"anniversary_{client_id}_{next_anniversary.year}",
                    "client_id": client_id,
                    "reminder_type": "creation_anniversary",
                    "reminder_date": reminder_date.to_iso8601_string(),
                    "event_date": next_anniversary.to_iso8601_string(),
                    "title": f"Aniversario de creación - {client.name}",
                    "description": f"El cliente '{client.name}' cumple {anniversary_data['creation_anniversary']['years_since_creation'] + 1} años",
                    "priority": "medium",
                    "is_active": True
                })
            
            # Recordatorios de hitos
            for milestone in anniversary_data["milestones"]:
                if not milestone["achieved"]:
                    milestone_date = pendulum.parse(milestone["date"])
                    if milestone_date > pendulum.now():
                        reminder_date = milestone_date.subtract(days=1)  # 1 día antes
                        
                        reminders.append({
                            "reminder_id": f"milestone_{client_id}_{milestone['milestone']}",
                            "client_id": client_id,
                            "reminder_type": "milestone",
                            "reminder_date": reminder_date.to_iso8601_string(),
                            "event_date": milestone_date.to_iso8601_string(),
                            "title": f"Hito próximo - {client.name}",
                            "description": milestone["description"],
                            "priority": "low",
                            "is_active": True
                        })
            
            # TODO: Agregar más tipos de recordatorios
            # - Recordatorios de renovación
            # - Recordatorios de seguimiento
            # - Recordatorios de revisión de datos
            
            self._logger.debug(f"Recordatorios programados para cliente {client_id}: {len(reminders)}")
            
            return reminders
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al programar recordatorios: {e}")
            raise RepositoryError(
                message=f"Error en programación de recordatorios: {e}",
                operation="schedule_client_date_reminders",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )