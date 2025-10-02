# src/planificador/services/domain/client/modules/statistics_operations.py

"""
Módulo de operaciones estadísticas para el servicio de dominio de cliente.

Este módulo implementa cálculos estadísticos, métricas y análisis de datos
para la entidad Cliente, proporcionando insights y reportes de negocio.
"""

from typing import Any, Dict, List, Optional

import pendulum
from loguru import logger

from planificador.exceptions import RepositoryError, ValidationError
from planificador.repositories.client.client_repository_facade import ClientRepositoryFacade
from planificador.schemas.client import ClientStatsResponse
from planificador.services.domain.client.interfaces.statistics_interface import IStatisticsOperations


class StatisticsOperations(IStatisticsOperations):
    """
    Implementación de operaciones estadísticas para el dominio de cliente.
    
    Esta clase encapsula cálculos estadísticos, métricas de rendimiento,
    análisis de crecimiento y generación de reportes para clientes.
    """

    def __init__(self, client_repository: ClientRepositoryFacade):
        """
        Inicializa el módulo de operaciones estadísticas.
        
        Args:
            client_repository: Facade del repositorio de cliente
        """
        self._client_repository = client_repository
        self._logger = logger

    async def count_clients_by_status(self, is_active: bool) -> int:
        """
        Cuenta clientes por estado activo/inactivo.
        
        Args:
            is_active: True para activos, False para inactivos
            
        Returns:
            int: Número de clientes con el estado especificado
        """
        try:
            self._logger.debug(f"Contando clientes por estado: {is_active}")
            
            filters = {"is_active": is_active}
            count = await self._client_repository.count_clients_by_filters(filters)
            
            self._logger.debug(f"Clientes {'activos' if is_active else 'inactivos'}: {count}")
            
            return count
            
        except Exception as e:
            self._logger.error(f"Error al contar clientes por estado: {e}")
            raise RepositoryError(
                message=f"Error al contar clientes por estado: {e}",
                operation="count_clients_by_status",
                entity_type="Client",
                original_error=e
            )

    async def count_clients_by_type(self, client_type: str) -> int:
        """
        Cuenta clientes por tipo específico.
        
        Args:
            client_type: Tipo de cliente a contar
            
        Returns:
            int: Número de clientes del tipo especificado
        """
        try:
            self._logger.debug(f"Contando clientes por tipo: {client_type}")
            
            # Nota: Esta funcionalidad está preparada para futuras extensiones
            # Por ahora retornamos 0 ya que no hay campo tipo en el modelo actual
            self._logger.warning("Funcionalidad de tipo de cliente no implementada aún")
            
            return 0
            
        except Exception as e:
            self._logger.error(f"Error al contar clientes por tipo: {e}")
            raise RepositoryError(
                message=f"Error al contar clientes por tipo: {e}",
                operation="count_clients_by_type",
                entity_type="Client",
                original_error=e
            )

    async def get_total_clients_count(self) -> int:
        """
        Obtiene el número total de clientes en el sistema.
        
        Returns:
            int: Número total de clientes
        """
        try:
            self._logger.debug("Obteniendo conteo total de clientes")
            
            count = await self._client_repository.count_clients_by_filters({})
            
            self._logger.debug(f"Total de clientes: {count}")
            
            return count
            
        except Exception as e:
            self._logger.error(f"Error al obtener conteo total: {e}")
            raise RepositoryError(
                message=f"Error al obtener conteo total: {e}",
                operation="get_total_clients_count",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_growth_stats(
        self,
        start_date: pendulum.DateTime,
        end_date: pendulum.DateTime,
        period: str = "monthly"
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de crecimiento de clientes en un período.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
            period: Período de agrupación ('daily', 'weekly', 'monthly')
            
        Returns:
            Dict[str, Any]: Estadísticas de crecimiento
        """
        try:
            self._logger.debug(f"Calculando estadísticas de crecimiento: {start_date} - {end_date}")
            
            # Validar rango de fechas
            if start_date > end_date:
                raise ValidationError(
                    message="La fecha de inicio debe ser anterior a la fecha de fin",
                    field="date_range",
                    value=f"{start_date} - {end_date}"
                )
            
            # Validar período
            valid_periods = ["daily", "weekly", "monthly"]
            if period not in valid_periods:
                raise ValidationError(
                    message=f"Período debe ser uno de: {valid_periods}",
                    field="period",
                    value=period
                )
            
            # Obtener clientes creados en el período
            filters = {
                "created_at__gte": start_date,
                "created_at__lte": end_date
            }
            
            clients_in_period = await self._client_repository.count_clients_by_filters(filters)
            
            # Obtener total antes del período
            filters_before = {"created_at__lt": start_date}
            clients_before = await self._client_repository.count_clients_by_filters(filters_before)
            
            # Calcular estadísticas
            total_current = clients_before + clients_in_period
            growth_rate = (clients_in_period / clients_before * 100) if clients_before > 0 else 0
            
            stats = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "period_type": period
                },
                "clients_before_period": clients_before,
                "clients_added_in_period": clients_in_period,
                "total_clients_current": total_current,
                "growth_rate_percentage": round(growth_rate, 2),
                "average_per_day": round(clients_in_period / (end_date - start_date).days, 2) if (end_date - start_date).days > 0 else 0
            }
            
            self._logger.debug(f"Estadísticas de crecimiento calculadas: {stats}")
            
            return stats
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al calcular estadísticas de crecimiento: {e}")
            raise RepositoryError(
                message=f"Error en estadísticas de crecimiento: {e}",
                operation="get_clients_growth_stats",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_activity_metrics(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de actividad de clientes.
        
        Args:
            days_back: Número de días hacia atrás para el análisis
            
        Returns:
            Dict[str, Any]: Métricas de actividad
        """
        try:
            self._logger.debug(f"Calculando métricas de actividad ({days_back} días)")
            
            if days_back < 1:
                raise ValidationError(
                    message="Los días hacia atrás deben ser mayor a 0",
                    field="days_back",
                    value=days_back
                )
            
            # Calcular fechas
            end_date = pendulum.now()
            start_date = end_date.subtract(days=days_back)
            
            # Obtener métricas básicas
            total_clients = await self.get_total_clients_count()
            active_clients = await self.count_clients_by_status(True)
            inactive_clients = await self.count_clients_by_status(False)
            
            # Clientes creados recientemente
            recent_filters = {
                "created_at__gte": start_date,
                "created_at__lte": end_date
            }
            recent_clients = await self._client_repository.count_clients_by_filters(recent_filters)
            
            # Clientes actualizados recientemente
            updated_filters = {
                "updated_at__gte": start_date,
                "updated_at__lte": end_date
            }
            updated_clients = await self._client_repository.count_clients_by_filters(updated_filters)
            
            # Calcular porcentajes
            active_percentage = (active_clients / total_clients * 100) if total_clients > 0 else 0
            recent_percentage = (recent_clients / total_clients * 100) if total_clients > 0 else 0
            
            metrics = {
                "analysis_period": {
                    "days_back": days_back,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "total_clients": total_clients,
                "active_clients": active_clients,
                "inactive_clients": inactive_clients,
                "active_percentage": round(active_percentage, 2),
                "recent_clients": recent_clients,
                "recent_percentage": round(recent_percentage, 2),
                "updated_clients": updated_clients,
                "activity_score": round((active_percentage + recent_percentage) / 2, 2)
            }
            
            self._logger.debug(f"Métricas de actividad calculadas: {metrics}")
            
            return metrics
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al calcular métricas de actividad: {e}")
            raise RepositoryError(
                message=f"Error en métricas de actividad: {e}",
                operation="get_clients_activity_metrics",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_distribution_by_region(self) -> Dict[str, int]:
        """
        Obtiene la distribución de clientes por región.
        
        Returns:
            Dict[str, int]: Distribución de clientes por región
        """
        try:
            self._logger.debug("Calculando distribución por región")
            
            # Nota: Esta funcionalidad requiere campo de región en el modelo
            # Por ahora retornamos distribución vacía
            self._logger.warning("Campo de región no implementado en el modelo actual")
            
            distribution = {
                "sin_region": await self.get_total_clients_count()
            }
            
            self._logger.debug(f"Distribución por región: {distribution}")
            
            return distribution
            
        except Exception as e:
            self._logger.error(f"Error al calcular distribución por región: {e}")
            raise RepositoryError(
                message=f"Error en distribución por región: {e}",
                operation="get_clients_distribution_by_region",
                entity_type="Client",
                original_error=e
            )

    async def calculate_client_retention_rate(
        self,
        period_months: int = 12
    ) -> float:
        """
        Calcula la tasa de retención de clientes.
        
        Args:
            period_months: Período en meses para el cálculo
            
        Returns:
            float: Tasa de retención como porcentaje
        """
        try:
            self._logger.debug(f"Calculando tasa de retención ({period_months} meses)")
            
            if period_months < 1:
                raise ValidationError(
                    message="El período debe ser mayor a 0 meses",
                    field="period_months",
                    value=period_months
                )
            
            # Calcular fechas
            end_date = pendulum.now()
            start_date = end_date.subtract(months=period_months)
            
            # Clientes al inicio del período
            filters_start = {"created_at__lt": start_date}
            clients_at_start = await self._client_repository.count_clients_by_filters(filters_start)
            
            # Clientes que siguen activos
            filters_retained = {
                "created_at__lt": start_date,
                "is_active": True
            }
            clients_retained = await self._client_repository.count_clients_by_filters(filters_retained)
            
            # Calcular tasa de retención
            retention_rate = (clients_retained / clients_at_start * 100) if clients_at_start > 0 else 0
            
            self._logger.debug(f"Tasa de retención: {retention_rate}%")
            
            return round(retention_rate, 2)
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al calcular tasa de retención: {e}")
            raise RepositoryError(
                message=f"Error en tasa de retención: {e}",
                operation="calculate_client_retention_rate",
                entity_type="Client",
                original_error=e
            )

    async def get_client_engagement_score(self, client_id: int) -> float:
        """
        Calcula el puntaje de engagement de un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            float: Puntaje de engagement (0.0 a 100.0)
        """
        try:
            self._logger.debug(f"Calculando puntaje de engagement para cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=client_id
                )
            
            # Calcular puntaje básico basado en estado y actividad reciente
            base_score = 50.0  # Puntaje base
            
            # Bonus por estar activo
            if client.is_active:
                base_score += 30.0
            
            # Bonus por actividad reciente (actualización en últimos 30 días)
            if client.updated_at:
                days_since_update = (pendulum.now() - client.updated_at).days
                if days_since_update <= 30:
                    base_score += 20.0 * (1 - days_since_update / 30)
            
            # TODO: Agregar más factores cuando estén disponibles:
            # - Número de proyectos activos
            # - Frecuencia de interacciones
            # - Valor de contratos
            
            engagement_score = min(100.0, max(0.0, base_score))
            
            self._logger.debug(f"Puntaje de engagement para cliente {client_id}: {engagement_score}")
            
            return round(engagement_score, 2)
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al calcular engagement del cliente {client_id}: {e}")
            raise RepositoryError(
                message=f"Error en cálculo de engagement: {e}",
                operation="get_client_engagement_score",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def get_top_clients_by_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene los clientes más activos.
        
        Args:
            limit: Número máximo de clientes a retornar
            
        Returns:
            List[Dict[str, Any]]: Lista de clientes más activos con métricas
        """
        try:
            self._logger.debug(f"Obteniendo top {limit} clientes por actividad")
            
            if limit < 1 or limit > 100:
                raise ValidationError(
                    message="El límite debe estar entre 1 y 100",
                    field="limit",
                    value=limit
                )
            
            # Obtener clientes activos ordenados por fecha de actualización
            filters = {"is_active": True}
            clients = await self._client_repository.get_clients_by_filters(
                filters=filters,
                limit=limit
            )
            
            # Calcular métricas para cada cliente
            top_clients = []
            for client in clients:
                engagement_score = await self.get_client_engagement_score(client.id)
                
                client_data = {
                    "id": client.id,
                    "name": client.name,
                    "code": client.code,
                    "email": client.email,
                    "engagement_score": engagement_score,
                    "created_at": client.created_at.isoformat() if client.created_at else None,
                    "updated_at": client.updated_at.isoformat() if client.updated_at else None,
                    "days_since_update": (pendulum.now() - client.updated_at).days if client.updated_at else None
                }
                
                top_clients.append(client_data)
            
            # Ordenar por puntaje de engagement
            top_clients.sort(key=lambda x: x["engagement_score"], reverse=True)
            
            self._logger.debug(f"Top clientes calculados: {len(top_clients)} resultados")
            
            return top_clients
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener top clientes: {e}")
            raise RepositoryError(
                message=f"Error al obtener top clientes: {e}",
                operation="get_top_clients_by_activity",
                entity_type="Client",
                original_error=e
            )

    async def generate_clients_summary_report(self) -> ClientStatsResponse:
        """
        Genera un reporte resumen completo de estadísticas de clientes.
        
        Returns:
            ClientStatsResponse: Reporte completo de estadísticas
        """
        try:
            self._logger.debug("Generando reporte resumen de clientes")
            
            # Obtener métricas básicas
            total_clients = await self.get_total_clients_count()
            active_clients = await self.count_clients_by_status(True)
            inactive_clients = await self.count_clients_by_status(False)
            
            # Obtener métricas de actividad (últimos 30 días)
            activity_metrics = await self.get_clients_activity_metrics(30)
            
            # Obtener tasa de retención (últimos 12 meses)
            retention_rate = await self.calculate_client_retention_rate(12)
            
            # Obtener distribución por región
            region_distribution = await self.get_clients_distribution_by_region()
            
            # Crear reporte usando el esquema existente
            report = ClientStatsResponse(
                total_clients=total_clients,
                active_clients=active_clients,
                inactive_clients=inactive_clients,
                growth_rate=activity_metrics.get("recent_percentage", 0.0),
                retention_rate=retention_rate
            )
            
            self._logger.debug("Reporte resumen generado exitosamente")
            
            return report
            
        except Exception as e:
            self._logger.error(f"Error al generar reporte resumen: {e}")
            raise RepositoryError(
                message=f"Error al generar reporte: {e}",
                operation="generate_clients_summary_report",
                entity_type="Client",
                original_error=e
            )