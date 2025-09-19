# src/planificador/repositories/status_code/modules/statistics_module.py

"""
Módulo de estadísticas para operaciones de análisis y métricas del repositorio StatusCode.

Este módulo implementa las operaciones de estadísticas, análisis de distribución,
métricas de rendimiento y reportes de integridad para códigos de estado.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de estadísticas y análisis
    - Performance Optimization: Consultas optimizadas para análisis de datos
    - Data Analytics: Implementación de métricas y análisis estadísticos

Uso:
    ```python
    stats_module = StatusCodeStatisticsModule(session)
    total = await stats_module.get_total_count()
    distribution = await stats_module.get_status_distribution()
    metrics = await stats_module.get_performance_metrics()
    ```
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy import select, func, and_, or_, case, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.status_code import StatusCode
from planificador.repositories.status_code.interfaces.statistics_interface import IStatusCodeStatisticsOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    StatusCodeRepositoryError,
    convert_sqlalchemy_error
)


class StatusCodeStatisticsModule(BaseRepository[StatusCode], IStatusCodeStatisticsOperations):
    """
    Módulo para operaciones de estadísticas del repositorio StatusCode.
    
    Implementa las operaciones de análisis estadístico, métricas de rendimiento,
    distribución de datos y reportes de integridad para códigos de estado.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo StatusCode
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de estadísticas para StatusCode.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, StatusCode)

    async def get_total_count(self) -> int:
        """
        Obtiene el número total de códigos de estado.
        
        Returns:
            int: Número total de códigos de estado
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo conteo total de códigos de estado")
            
            stmt = select(func.count(StatusCode.id))
            result = await self.session.execute(stmt)
            total = result.scalar() or 0
            
            self._logger.debug(f"Total de códigos de estado: {total}")
            return total
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener conteo total: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_total_count",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener conteo total: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener conteo total: {e}",
                operation="get_total_count",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_active_count(self) -> int:
        """
        Obtiene el número de códigos de estado activos.
        
        Returns:
            int: Número de códigos de estado activos
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo conteo de códigos de estado activos")
            
            stmt = select(func.count(StatusCode.id)).where(StatusCode.is_active == True)
            result = await self.session.execute(stmt)
            active_count = result.scalar() or 0
            
            self._logger.debug(f"Códigos de estado activos: {active_count}")
            return active_count
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener conteo de activos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_active_count",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener conteo de activos: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener conteo de activos: {e}",
                operation="get_active_count",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_status_distribution(self) -> Dict[str, int]:
        """
        Obtiene la distribución de códigos por estado (activo/inactivo).
        
        Returns:
            Dict[str, int]: Distribución de estados {'active': count, 'inactive': count}
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo distribución de estados")
            
            stmt = select(
                StatusCode.is_active,
                func.count(StatusCode.id).label('count')
            ).group_by(StatusCode.is_active)
            
            result = await self.session.execute(stmt)
            rows = result.all()
            
            distribution = {'active': 0, 'inactive': 0}
            for row in rows:
                key = 'active' if row.is_active else 'inactive'
                distribution[key] = row.count
            
            self._logger.debug(f"Distribución de estados: {distribution}")
            return distribution
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener distribución de estados: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_status_distribution",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener distribución de estados: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener distribución de estados: {e}",
                operation="get_status_distribution",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_default_status_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene información del código de estado por defecto.
        
        Returns:
            Optional[Dict[str, Any]]: Información del código por defecto o None
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo información del código de estado por defecto")
            
            stmt = select(StatusCode).where(StatusCode.is_default == True)
            result = await self.session.execute(stmt)
            default_status = result.scalar_one_or_none()
            
            if default_status:
                info = {
                    'id': default_status.id,
                    'code': default_status.code,
                    'name': default_status.name,
                    'is_active': default_status.is_active,
                    'display_order': default_status.display_order
                }
                self._logger.debug(f"Código por defecto encontrado: {default_status.code}")
                return info
            
            self._logger.debug("No se encontró código de estado por defecto")
            return None
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener información por defecto: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_default_status_info",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener información por defecto: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener información por defecto: {e}",
                operation="get_default_status_info",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_display_order_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre el orden de visualización.
        
        Returns:
            Dict[str, Any]: Estadísticas de display_order
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo estadísticas de display_order")
            
            # Estadísticas básicas
            stmt = select(
                func.min(StatusCode.display_order).label('min_order'),
                func.max(StatusCode.display_order).label('max_order'),
                func.avg(StatusCode.display_order).label('avg_order'),
                func.count(StatusCode.id).label('total_count'),
                func.count(StatusCode.display_order).label('with_order_count')
            ).where(StatusCode.display_order.isnot(None))
            
            result = await self.session.execute(stmt)
            stats_row = result.first()
            
            # Contar duplicados
            duplicates_stmt = select(
                StatusCode.display_order,
                func.count(StatusCode.id).label('count')
            ).where(
                StatusCode.display_order.isnot(None)
            ).group_by(
                StatusCode.display_order
            ).having(
                func.count(StatusCode.id) > 1
            )
            
            duplicates_result = await self.session.execute(duplicates_stmt)
            duplicates = list(duplicates_result.all())
            
            statistics = {
                'min_order': stats_row.min_order if stats_row else None,
                'max_order': stats_row.max_order if stats_row else None,
                'avg_order': float(stats_row.avg_order) if stats_row and stats_row.avg_order else None,
                'total_with_order': stats_row.with_order_count if stats_row else 0,
                'duplicates_count': len(duplicates),
                'duplicate_orders': [{'order': dup.display_order, 'count': dup.count} for dup in duplicates]
            }
            
            self._logger.debug(f"Estadísticas de display_order: {statistics}")
            return statistics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener estadísticas de display_order: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_display_order_statistics",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener estadísticas de display_order: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener estadísticas de display_order: {e}",
                operation="get_display_order_statistics",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento del repositorio.
        
        Returns:
            Dict[str, Any]: Métricas de rendimiento y uso
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo métricas de rendimiento")
            
            # Métricas básicas
            total_count = await self.get_total_count()
            active_count = await self.get_active_count()
            
            # Análisis de longitud de códigos y nombres
            length_stmt = select(
                func.avg(func.length(StatusCode.code)).label('avg_code_length'),
                func.max(func.length(StatusCode.code)).label('max_code_length'),
                func.avg(func.length(StatusCode.name)).label('avg_name_length'),
                func.max(func.length(StatusCode.name)).label('max_name_length')
            )
            
            length_result = await self.session.execute(length_stmt)
            length_row = length_result.first()
            
            # Análisis de unicidad
            unique_codes_stmt = select(func.count(distinct(StatusCode.code)))
            unique_codes_result = await self.session.execute(unique_codes_stmt)
            unique_codes = unique_codes_result.scalar() or 0
            
            unique_names_stmt = select(func.count(distinct(StatusCode.name)))
            unique_names_result = await self.session.execute(unique_names_stmt)
            unique_names = unique_names_result.scalar() or 0
            
            metrics = {
                'total_records': total_count,
                'active_records': active_count,
                'inactive_records': total_count - active_count,
                'activity_rate': (active_count / total_count * 100) if total_count > 0 else 0,
                'unique_codes': unique_codes,
                'unique_names': unique_names,
                'code_uniqueness_rate': (unique_codes / total_count * 100) if total_count > 0 else 0,
                'name_uniqueness_rate': (unique_names / total_count * 100) if total_count > 0 else 0,
                'avg_code_length': float(length_row.avg_code_length) if length_row and length_row.avg_code_length else 0,
                'max_code_length': length_row.max_code_length if length_row else 0,
                'avg_name_length': float(length_row.avg_name_length) if length_row and length_row.avg_name_length else 0,
                'max_name_length': length_row.max_name_length if length_row else 0
            }
            
            self._logger.debug(f"Métricas de rendimiento calculadas: {len(metrics)} métricas")
            return metrics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener métricas de rendimiento: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_performance_metrics",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener métricas de rendimiento: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener métricas de rendimiento: {e}",
                operation="get_performance_metrics",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_integrity_report(self) -> Dict[str, Any]:
        """
        Genera un reporte de integridad de los datos.
        
        Returns:
            Dict[str, Any]: Reporte completo de integridad
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la generación
        """
        try:
            self._logger.debug("Generando reporte de integridad")
            
            # Verificar códigos duplicados
            duplicate_codes_stmt = select(
                StatusCode.code,
                func.count(StatusCode.id).label('count')
            ).group_by(StatusCode.code).having(func.count(StatusCode.id) > 1)
            
            duplicate_codes_result = await self.session.execute(duplicate_codes_stmt)
            duplicate_codes = list(duplicate_codes_result.all())
            
            # Verificar nombres duplicados
            duplicate_names_stmt = select(
                StatusCode.name,
                func.count(StatusCode.id).label('count')
            ).group_by(StatusCode.name).having(func.count(StatusCode.id) > 1)
            
            duplicate_names_result = await self.session.execute(duplicate_names_stmt)
            duplicate_names = list(duplicate_names_result.all())
            
            # Verificar múltiples códigos por defecto
            default_count_stmt = select(func.count(StatusCode.id)).where(StatusCode.is_default == True)
            default_count_result = await self.session.execute(default_count_stmt)
            default_count = default_count_result.scalar() or 0
            
            # Verificar códigos sin display_order
            no_order_stmt = select(func.count(StatusCode.id)).where(StatusCode.display_order.is_(None))
            no_order_result = await self.session.execute(no_order_stmt)
            no_order_count = no_order_result.scalar() or 0
            
            # Obtener estadísticas de display_order
            order_stats = await self.get_display_order_statistics()
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_records': await self.get_total_count(),
                'integrity_issues': {
                    'duplicate_codes': {
                        'count': len(duplicate_codes),
                        'details': [{'code': dup.code, 'occurrences': dup.count} for dup in duplicate_codes]
                    },
                    'duplicate_names': {
                        'count': len(duplicate_names),
                        'details': [{'name': dup.name, 'occurrences': dup.count} for dup in duplicate_names]
                    },
                    'multiple_defaults': {
                        'count': max(0, default_count - 1),
                        'total_defaults': default_count
                    },
                    'missing_display_order': {
                        'count': no_order_count
                    },
                    'display_order_duplicates': {
                        'count': order_stats.get('duplicates_count', 0),
                        'details': order_stats.get('duplicate_orders', [])
                    }
                },
                'health_score': self._calculate_health_score(
                    len(duplicate_codes),
                    len(duplicate_names),
                    max(0, default_count - 1),
                    order_stats.get('duplicates_count', 0)
                )
            }
            
            self._logger.debug(f"Reporte de integridad generado. Health score: {report['health_score']}")
            return report
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al generar reporte de integridad: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_integrity_report",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al generar reporte de integridad: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al generar reporte de integridad: {e}",
                operation="get_integrity_report",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    def _calculate_health_score(
        self, 
        duplicate_codes: int, 
        duplicate_names: int, 
        multiple_defaults: int, 
        order_duplicates: int
    ) -> float:
        """
        Calcula un puntaje de salud basado en los problemas de integridad.
        
        Args:
            duplicate_codes: Número de códigos duplicados
            duplicate_names: Número de nombres duplicados
            multiple_defaults: Número de códigos por defecto adicionales
            order_duplicates: Número de órdenes de visualización duplicados
            
        Returns:
            float: Puntaje de salud (0-100)
        """
        # Puntaje base
        base_score = 100.0
        
        # Penalizaciones
        penalties = {
            'duplicate_codes': duplicate_codes * 20,  # Crítico
            'duplicate_names': duplicate_names * 15,  # Alto
            'multiple_defaults': multiple_defaults * 25,  # Crítico
            'order_duplicates': order_duplicates * 5   # Medio
        }
        
        total_penalty = sum(penalties.values())
        health_score = max(0.0, base_score - total_penalty)
        
        return round(health_score, 2)