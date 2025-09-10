# src/planificador/database/repositories/client/client_statistics.py

from typing import Dict, List, Optional, Any, Union
from datetime import date
from sqlalchemy import func, and_, or_, case, text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger
import pendulum

from ....models.client import Client
from ....models.project import Project
from ....utils.date_utils import (
    get_current_time,
    calculate_business_days,
    is_business_day
)
from ....exceptions.repository import convert_sqlalchemy_error
from ....exceptions.repository.client_repository_exceptions import create_client_statistics_error


class ClientStatistics:
    """
    Gestor de estadísticas y métricas de clientes.
    
    Proporciona métodos para generar estadísticas, tendencias
    y métricas de rendimiento relacionadas con clientes.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Client
        self._logger = logger.bind(component="ClientStatistics")
    
    # ============================================================================
    # ESTADÍSTICAS POR CLIENTE (1 función)
    # ============================================================================
    
    async def get_client_stats(self, client_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con estadísticas del cliente
        """
        try:
            # Contar proyectos totales
            total_projects_query = select(func.count(Project.id)).where(
                Project.client_id == client_id
            )
            total_projects_result = await self.session.execute(total_projects_query)
            total_projects = total_projects_result.scalar() or 0
            
            # Contar proyectos activos
            active_projects_query = select(func.count(Project.id)).where(
                and_(
                    Project.client_id == client_id,
                    Project.status.in_(['planned', 'in_progress'])
                )
            )
            active_projects_result = await self.session.execute(active_projects_query)
            active_projects = active_projects_result.scalar() or 0
            
            # Contar proyectos completados
            completed_projects_query = select(func.count(Project.id)).where(
                and_(
                    Project.client_id == client_id,
                    Project.status == 'completed'
                )
            )
            completed_projects_result = await self.session.execute(completed_projects_query)
            completed_projects = completed_projects_result.scalar() or 0
            
            stats = {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'completion_rate': (
                    (completed_projects / total_projects * 100) 
                    if total_projects > 0 else 0
                )
            }
            
            self._logger.debug(f"Estadísticas calculadas para cliente {client_id}: {stats}")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos calculando estadísticas del cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_stats",
                entity_type="Client",
                entity_id=client_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado calculando estadísticas del cliente {client_id}: {e}")
            raise create_client_statistics_error(
                message=f"Error calculando estadísticas del cliente {client_id}: {e}",
                original_error=e
            )
    
    # ============================================================================
    # ESTADÍSTICAS POR CATEGORÍAS (1 función)
    # ============================================================================
    
    async def get_client_counts_by_status(self) -> Dict[str, int]:
        """
        Obtiene el conteo de clientes por estado (activo/inactivo).
        
        Returns:
            Diccionario con el conteo por estado
        """
        try:
            # Contar clientes activos
            active_query = select(func.count(Client.id)).where(Client.is_active == True)
            active_result = await self.session.execute(active_query)
            active_count = active_result.scalar() or 0
            
            # Contar clientes inactivos
            inactive_query = select(func.count(Client.id)).where(Client.is_active == False)
            inactive_result = await self.session.execute(inactive_query)
            inactive_count = inactive_result.scalar() or 0
            
            counts = {
                'active': active_count,
                'inactive': inactive_count,
                'total': active_count + inactive_count
            }
            
            self._logger.debug(f"Conteos por estado obtenidos: {counts}")
            return counts
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo conteos por estado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_counts_by_status",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo conteos por estado: {e}")
            raise create_client_statistics_error(
                message=f"Error obteniendo conteos por estado: {e}",
                original_error=e
            )
    
    # ============================================================================
    # ESTADÍSTICAS TEMPORALES (1 función)
    # ============================================================================
    
    async def get_client_creation_trends(
        self, 
        days: int = 30,
        group_by: str = 'day'
    ) -> List[Dict[str, Any]]:
        """
        Obtiene tendencias de creación de clientes.
        
        Args:
            days: Número de días hacia atrás
            group_by: Agrupación ('day', 'week', 'month')
            
        Returns:
            Lista con tendencias de creación
        """
        try:
            current_time = get_current_time()
            start_date = current_time.subtract(days=days)
            
            # Determinar formato de agrupación
            if group_by == 'day':
                date_format = '%Y-%m-%d'
                date_trunc = 'day'
            elif group_by == 'week':
                date_format = '%Y-W%U'
                date_trunc = 'week'
            elif group_by == 'month':
                date_format = '%Y-%m'
                date_trunc = 'month'
            else:
                raise ValueError(f"group_by no válido: {group_by}")
            
            # Consulta de tendencias
            query = select(
                func.date_trunc(date_trunc, Client.created_at).label('period'),
                func.count(Client.id).label('count')
            ).where(
                Client.created_at >= start_date
            ).group_by(
                func.date_trunc(date_trunc, Client.created_at)
            ).order_by(
                func.date_trunc(date_trunc, Client.created_at)
            )
            
            result = await self.session.execute(query)
            trends = []
            
            for row in result:
                period_date = row.period
                formatted_period = period_date.strftime(date_format)
                
                trends.append({
                    'period': formatted_period,
                    'date': period_date.isoformat(),
                    'count': row.count,
                    'group_by': group_by
                })
            
            self._logger.debug(f"Tendencias de creación obtenidas: {len(trends)} períodos")
            return trends
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo tendencias de creación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_creation_trends",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo tendencias de creación: {e}")
            raise create_client_statistics_error(
                message=f"Error obteniendo tendencias de creación: {e}",
                original_error=e
            )
    
    # ============================================================================
    # ESTADÍSTICAS DE RELACIONES (2 funciones)
    # ============================================================================
    
    async def get_client_relationship_duration_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de duración de relaciones con clientes.
        
        Returns:
            Diccionario con estadísticas de duración
        """
        try:
            current_date = get_current_time().date()
            
            # Obtener todos los clientes con fecha de creación
            query = select(Client).where(Client.created_at.isnot(None))
            result = await self.session.execute(query)
            clients = result.scalars().all()
            
            if not clients:
                return {
                    'total_clients': 0,
                    'avg_relationship_days': 0,
                    'avg_relationship_years': 0,
                    'longest_relationship_days': 0,
                    'shortest_relationship_days': 0,
                    'clients_by_duration': {}
                }
            
            # Calcular duraciones
            durations = []
            for client in clients:
                if client.created_at:
                    created_date = client.created_at.date() if hasattr(client.created_at, 'date') else client.created_at
                    duration_days = (current_date - created_date).days
                    durations.append(duration_days)
            
            # Estadísticas básicas
            avg_duration = sum(durations) / len(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            min_duration = min(durations) if durations else 0
            
            # Agrupar por rangos de duración
            duration_ranges = {
                'menos_de_1_año': 0,
                '1_a_2_años': 0,
                '2_a_5_años': 0,
                'más_de_5_años': 0
            }
            
            for duration in durations:
                years = duration / 365.25
                if years < 1:
                    duration_ranges['menos_de_1_año'] += 1
                elif years < 2:
                    duration_ranges['1_a_2_años'] += 1
                elif years < 5:
                    duration_ranges['2_a_5_años'] += 1
                else:
                    duration_ranges['más_de_5_años'] += 1
            
            stats = {
                'total_clients': len(clients),
                'avg_relationship_days': round(avg_duration, 2),
                'avg_relationship_years': round(avg_duration / 365.25, 2),
                'longest_relationship_days': max_duration,
                'shortest_relationship_days': min_duration,
                'clients_by_duration': duration_ranges
            }
            
            self._logger.debug(f"Estadísticas de duración calculadas: {stats}")
            return stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos calculando estadísticas de duración: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_relationship_duration_stats",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado calculando estadísticas de duración: {e}")
            raise create_client_statistics_error(
                message=f"Error calculando estadísticas de duración: {e}",
                original_error=e
            )
    
    async def get_clients_by_relationship_duration(
        self,
        min_years: float = 0.0,
        max_years: Optional[float] = None,
        is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene clientes por duración de relación.
        
        Args:
            min_years: Duración mínima de relación en años
            max_years: Duración máxima de relación en años (opcional)
            is_active: Estado del cliente (opcional)
            
        Returns:
            Lista de clientes con información de duración de relación
        """
        try:
            # Construir consulta base
            query = select(Client).where(Client.created_at.isnot(None))
            
            if is_active is not None:
                query = query.where(Client.is_active == is_active)
            
            result = await self.session.execute(query)
            all_clients = result.scalars().all()
            
            # Filtrar por duración de relación y calcular estadísticas
            current_date = get_current_time().date()
            filtered_clients = []
            
            for client in all_clients:
                if not client.created_at:
                    continue
                
                created_date = client.created_at.date() if hasattr(client.created_at, 'date') else client.created_at
                relationship_days = (current_date - created_date).days
                relationship_years = relationship_days / 365.25
                
                # Aplicar filtros de duración
                if relationship_years < min_years:
                    continue
                if max_years is not None and relationship_years > max_years:
                    continue
                
                client_info = {
                    'id': client.id,
                    'name': client.name,
                    'code': client.code,
                    'is_active': client.is_active,
                    'created_at': created_date.isoformat(),
                    'relationship_days': relationship_days,
                    'relationship_years': round(relationship_years, 2),
                    'relationship_business_days': get_business_days(created_date, current_date)
                }
                
                filtered_clients.append(client_info)
            
            # Ordenar por duración de relación (más antiguos primero)
            filtered_clients.sort(key=lambda x: x['relationship_years'], reverse=True)
            
            self._logger.debug(
                f"Encontrados {len(filtered_clients)} clientes con relación "
                f"entre {min_years} y {max_years or 'sin límite'} años"
            )
            
            return filtered_clients
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo clientes por duración de relación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_by_relationship_duration",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes por duración de relación: {e}")
            raise create_client_statistics_error(
                message=f"Error obteniendo clientes por duración de relación: {e}",
                original_error=e
            )
    
    # ============================================================================
    # ESTADÍSTICAS POR PROYECTOS (1 función)
    # ============================================================================
    
    async def get_clients_by_project_count(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene clientes ordenados por número de proyectos.
        
        Args:
            limit: Número máximo de clientes a retornar
            
        Returns:
            Lista de clientes con conteo de proyectos
        """
        try:
            query = select(
                Client.id,
                Client.name,
                Client.code,
                Client.is_active,
                func.count(Project.id).label('project_count')
            ).outerjoin(
                Project, Client.id == Project.client_id
            ).group_by(
                Client.id, Client.name, Client.code, Client.is_active
            ).order_by(
                func.count(Project.id).desc()
            ).limit(limit)
            
            result = await self.session.execute(query)
            
            # Obtener los clientes completos para acceder a las propiedades
            client_ids = [row.id for row in result]
            clients_query = select(Client).where(Client.id.in_(client_ids))
            clients_result = await self.session.execute(clients_query)
            clients = {client.id: client for client in clients_result.scalars().all()}
            
            # Volver a ejecutar la consulta original para obtener los conteos
            result = await self.session.execute(query)
            clients_stats = []
            
            for row in result:
                client = clients.get(row.id)
                client_data = {
                    'id': row.id,
                    'name': row.name,
                    'code': row.code,
                    'is_active': row.is_active,
                    'project_count': row.project_count
                }
                
                # Agregar propiedades del modelo si el cliente existe
                if client:
                    client_data.update({
                        'display_name': client.display_name,
                        'status_display': client.status_display,
                        'has_contact_info': client.has_contact_info,
                        'contact_summary': client.contact_summary
                    })
                
                clients_stats.append(client_data)
            
            self._logger.debug(f"Obtenidos {len(clients_stats)} clientes por conteo de proyectos")
            return clients_stats
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos obteniendo clientes por conteo de proyectos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_by_project_count",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo clientes por conteo de proyectos: {e}")
            raise create_client_statistics_error(
                message=f"Error obteniendo clientes por conteo de proyectos: {e}",
                original_error=e
            )
    
    # ============================================================================
    # ESTADÍSTICAS DE INFORMACIÓN DE CONTACTO (1 función)
    # ============================================================================
    
    async def get_contact_info_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre información de contacto de clientes.
        Utiliza las propiedades has_contact_info y contact_summary del modelo.
        
        Returns:
            Diccionario con estadísticas de información de contacto
        """
        try:
            # Obtener todos los clientes activos
            query = select(Client).where(Client.is_active == True)
            result = await self.session.execute(query)
            active_clients = result.scalars().all()
            
            # Calcular estadísticas usando las propiedades del modelo
            total_active = len(active_clients)
            with_contact_info = sum(1 for client in active_clients if client.has_contact_info)
            without_contact_info = total_active - with_contact_info
            
            # Estadísticas por tipo de contacto
            with_email = sum(1 for client in active_clients if client.email)
            with_phone = sum(1 for client in active_clients if client.phone)
            with_contact_person = sum(1 for client in active_clients if client.contact_person)
            
            # Clientes con información completa (todos los campos)
            complete_contact_info = sum(
                1 for client in active_clients 
                if client.email and client.phone and client.contact_person
            )
            
            # Porcentajes
            contact_info_percentage = (with_contact_info / total_active * 100) if total_active > 0 else 0
            email_percentage = (with_email / total_active * 100) if total_active > 0 else 0
            phone_percentage = (with_phone / total_active * 100) if total_active > 0 else 0
            contact_person_percentage = (with_contact_person / total_active * 100) if total_active > 0 else 0
            complete_info_percentage = (complete_contact_info / total_active * 100) if total_active > 0 else 0
            
            self._logger.debug(f"Estadísticas de contacto calculadas para {total_active} clientes activos")
            
            return {
                'total_active_clients': total_active,
                'clients_with_contact_info': with_contact_info,
                'clients_without_contact_info': without_contact_info,
                'contact_info_percentage': round(contact_info_percentage, 2),
                'contact_breakdown': {
                    'with_email': with_email,
                    'with_phone': with_phone,
                    'with_contact_person': with_contact_person,
                    'complete_contact_info': complete_contact_info
                },
                'contact_percentages': {
                    'email_percentage': round(email_percentage, 2),
                    'phone_percentage': round(phone_percentage, 2),
                    'contact_person_percentage': round(contact_person_percentage, 2),
                    'complete_info_percentage': round(complete_info_percentage, 2)
                },
                'timestamp': get_current_time().isoformat()
            }
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo estadísticas de información de contacto: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_contact_info_statistics",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo estadísticas de contacto: {e}")
            raise create_client_statistics_error(
                message=f"Error obteniendo estadísticas de contacto: {e}",
                original_error=e
            )
    
    # ============================================================================
    # RESUMEN DE ACTIVIDAD (1 función)
    # ============================================================================
    
    async def get_client_activity_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de actividad de clientes.
        
        Returns:
            Diccionario con resumen de actividad
        """
        try:
            current_time = get_current_time()
            
            # Clientes creados esta semana
            start_of_week = current_time.start_of('week')
            clients_this_week_query = select(func.count(Client.id)).where(
                Client.created_at >= start_of_week
            )
            clients_this_week_result = await self.session.execute(clients_this_week_query)
            clients_this_week = clients_this_week_result.scalar() or 0
            
            # Clientes creados este mes
            start_of_month = current_time.start_of('month')
            clients_this_month_query = select(func.count(Client.id)).where(
                Client.created_at >= start_of_month
            )
            clients_this_month_result = await self.session.execute(clients_this_month_query)
            clients_this_month = clients_this_month_result.scalar() or 0
            
            # Clientes con proyectos activos
            clients_with_active_projects_query = select(
                func.count(func.distinct(Client.id))
            ).select_from(
                Client
            ).join(
                Project, Client.id == Project.client_id
            ).where(
                Project.status.in_(['planned', 'in_progress'])
            )
            clients_with_active_projects_result = await self.session.execute(clients_with_active_projects_query)
            clients_with_active_projects = clients_with_active_projects_result.scalar() or 0
            
            # Total de clientes
            total_clients_query = select(func.count(Client.id))
            total_clients_result = await self.session.execute(total_clients_query)
            total_clients = total_clients_result.scalar() or 0
            
            # Clientes activos
            active_clients_query = select(func.count(Client.id)).where(Client.is_active == True)
            active_clients_result = await self.session.execute(active_clients_query)
            active_clients = active_clients_result.scalar() or 0
            
            summary = {
                'total_clients': total_clients,
                'active_clients': active_clients,
                'inactive_clients': total_clients - active_clients,
                'clients_created_this_week': clients_this_week,
                'clients_created_this_month': clients_this_month,
                'clients_with_active_projects': clients_with_active_projects,
                'activity_rate': (
                    (clients_with_active_projects / total_clients * 100)
                    if total_clients > 0 else 0
                ),
                'generated_at': current_time.isoformat()
            }
            
            self._logger.debug(f"Resumen de actividad generado: {summary}")
            return summary
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos generando resumen de actividad: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_activity_summary",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado generando resumen de actividad: {e}")
            raise create_client_statistics_error(
                message=f"Error generando resumen de actividad: {e}",
                original_error=e
            )
    
    # ============================================================================
    # ANÁLISIS AVANZADO DE DATOS (4 funciones nuevas)
    # ============================================================================
    
    async def get_client_segmentation_analysis(self) -> Dict[str, Any]:
        """
        Realiza análisis de segmentación de clientes basado en múltiples criterios.
        
        Returns:
            Diccionario con análisis de segmentación detallado
        """
        try:
            # Obtener todos los clientes activos con sus proyectos
            query = select(
                Client.id,
                Client.name,
                Client.code,
                Client.created_at,
                Client.email,
                Client.phone,
                Client.contact_person,
                func.count(Project.id).label('project_count'),
                func.coalesce(func.sum(Project.estimated_hours), 0).label('total_estimated_hours'),
                func.max(Project.created_at).label('last_project_date')
            ).outerjoin(
                Project, Client.id == Project.client_id
            ).where(
                Client.is_active == True
            ).group_by(
                Client.id, Client.name, Client.code, Client.created_at,
                Client.email, Client.phone, Client.contact_person
            )
            
            result = await self.session.execute(query)
            clients_data = result.all()
            
            if not clients_data:
                return {
                    'total_clients_analyzed': 0,
                    'segments': {},
                    'analysis_timestamp': get_current_time().isoformat()
                }
            
            current_time = get_current_time()
            segments = {
                'high_value': [],      # Muchos proyectos y horas
                'growing': [],         # Clientes recientes con actividad
                'established': [],     # Clientes antiguos con actividad constante
                'dormant': [],         # Sin actividad reciente
                'new': []             # Clientes muy recientes
            }
            
            # Calcular métricas para segmentación
            project_counts = [row.project_count for row in clients_data]
            avg_projects = sum(project_counts) / len(project_counts) if project_counts else 0
            
            for row in clients_data:
                client_age_days = (current_time.date() - row.created_at.date()).days if row.created_at else 0
                client_age_months = client_age_days / 30.44  # Promedio de días por mes
                
                has_contact_info = bool(row.email or row.phone or row.contact_person)
                
                client_info = {
                    'id': row.id,
                    'name': row.name,
                    'code': row.code,
                    'project_count': row.project_count,
                    'total_estimated_hours': float(row.total_estimated_hours or 0),
                    'client_age_months': round(client_age_months, 1),
                    'has_contact_info': has_contact_info,
                    'last_project_date': row.last_project_date.isoformat() if row.last_project_date else None
                }
                
                # Lógica de segmentación
                if client_age_months < 1:  # Menos de 1 mes
                    segments['new'].append(client_info)
                elif row.project_count >= avg_projects * 1.5 and row.total_estimated_hours > 100:
                    segments['high_value'].append(client_info)
                elif client_age_months < 6 and row.project_count > 0:
                    segments['growing'].append(client_info)
                elif client_age_months >= 6 and row.project_count > 0:
                    # Verificar actividad reciente (últimos 6 meses)
                    if row.last_project_date:
                        last_activity = current_time.subtract(months=6)
                        if row.last_project_date >= last_activity.date():
                            segments['established'].append(client_info)
                        else:
                            segments['dormant'].append(client_info)
                    else:
                        segments['dormant'].append(client_info)
                else:
                    segments['dormant'].append(client_info)
            
            # Calcular estadísticas por segmento
            segment_stats = {}
            for segment_name, clients in segments.items():
                if clients:
                    total_projects = sum(c['project_count'] for c in clients)
                    total_hours = sum(c['total_estimated_hours'] for c in clients)
                    avg_age = sum(c['client_age_months'] for c in clients) / len(clients)
                    contact_info_rate = sum(1 for c in clients if c['has_contact_info']) / len(clients) * 100
                    
                    segment_stats[segment_name] = {
                        'count': len(clients),
                        'percentage': round(len(clients) / len(clients_data) * 100, 2),
                        'total_projects': total_projects,
                        'total_estimated_hours': total_hours,
                        'avg_projects_per_client': round(total_projects / len(clients), 2),
                        'avg_hours_per_client': round(total_hours / len(clients), 2),
                        'avg_client_age_months': round(avg_age, 1),
                        'contact_info_completion_rate': round(contact_info_rate, 2),
                        'clients': clients[:5]  # Solo los primeros 5 para el reporte
                    }
                else:
                    segment_stats[segment_name] = {
                        'count': 0,
                        'percentage': 0,
                        'clients': []
                    }
            
            analysis = {
                'total_clients_analyzed': len(clients_data),
                'segments': segment_stats,
                'analysis_timestamp': current_time.isoformat(),
                'segmentation_criteria': {
                    'high_value': 'Clientes con >= 150% del promedio de proyectos y > 100 horas',
                    'growing': 'Clientes < 6 meses con al menos 1 proyecto',
                    'established': 'Clientes >= 6 meses con actividad en últimos 6 meses',
                    'dormant': 'Clientes sin actividad reciente o sin proyectos',
                    'new': 'Clientes con menos de 1 mes de antigüedad'
                }
            }
            
            self._logger.debug(f"Análisis de segmentación completado para {len(clients_data)} clientes")
            return analysis
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en análisis de segmentación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_segmentation_analysis",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en análisis de segmentación: {e}")
            raise create_client_statistics_error(
                message=f"Error en análisis de segmentación: {e}",
                original_error=e
            )
    
    async def get_client_value_analysis(self) -> Dict[str, Any]:
        """
        Analiza el valor de los clientes basado en proyectos y horas estimadas.
        
        Returns:
            Diccionario con análisis de valor de clientes
        """
        try:
            # Consulta para obtener métricas de valor por cliente
            query = select(
                Client.id,
                Client.name,
                Client.code,
                Client.created_at,
                func.count(Project.id).label('project_count'),
                func.coalesce(func.sum(Project.estimated_hours), 0).label('total_hours'),
                func.coalesce(func.avg(Project.estimated_hours), 0).label('avg_hours_per_project'),
                func.min(Project.created_at).label('first_project_date'),
                func.max(Project.created_at).label('last_project_date')
            ).outerjoin(
                Project, Client.id == Project.client_id
            ).where(
                Client.is_active == True
            ).group_by(
                Client.id, Client.name, Client.code, Client.created_at
            ).having(
                func.count(Project.id) > 0  # Solo clientes con proyectos
            )
            
            result = await self.session.execute(query)
            clients_with_projects = result.all()
            
            if not clients_with_projects:
                return {
                    'total_clients_with_projects': 0,
                    'value_tiers': {},
                    'analysis_timestamp': get_current_time().isoformat()
                }
            
            # Calcular percentiles para clasificación de valor
            total_hours_list = [float(row.total_hours) for row in clients_with_projects]
            project_counts_list = [row.project_count for row in clients_with_projects]
            
            # Ordenar para calcular percentiles
            sorted_hours = sorted(total_hours_list)
            sorted_projects = sorted(project_counts_list)
            
            # Calcular percentiles (75% y 90%)
            p75_hours = sorted_hours[int(len(sorted_hours) * 0.75)] if sorted_hours else 0
            p90_hours = sorted_hours[int(len(sorted_hours) * 0.90)] if sorted_hours else 0
            p75_projects = sorted_projects[int(len(sorted_projects) * 0.75)] if sorted_projects else 0
            
            # Clasificar clientes por valor
            value_tiers = {
                'premium': [],     # Top 10% en horas o proyectos
                'high_value': [],  # Top 25% en horas o proyectos
                'standard': [],    # Resto con actividad
                'low_engagement': []  # Pocos proyectos/horas
            }
            
            current_time = get_current_time()
            
            for row in clients_with_projects:
                total_hours = float(row.total_hours)
                project_count = row.project_count
                
                # Calcular métricas adicionales
                client_age_days = (current_time.date() - row.created_at.date()).days if row.created_at else 0
                
                # Calcular frecuencia de proyectos (proyectos por año)
                if client_age_days > 0:
                    projects_per_year = (project_count / client_age_days) * 365.25
                else:
                    projects_per_year = 0
                
                client_info = {
                    'id': row.id,
                    'name': row.name,
                    'code': row.code,
                    'project_count': project_count,
                    'total_hours': total_hours,
                    'avg_hours_per_project': round(float(row.avg_hours_per_project), 2),
                    'projects_per_year': round(projects_per_year, 2),
                    'client_age_days': client_age_days,
                    'first_project_date': row.first_project_date.isoformat() if row.first_project_date else None,
                    'last_project_date': row.last_project_date.isoformat() if row.last_project_date else None
                }
                
                # Clasificación por valor
                if total_hours >= p90_hours or project_count >= p75_projects:
                    value_tiers['premium'].append(client_info)
                elif total_hours >= p75_hours or project_count >= p75_projects:
                    value_tiers['high_value'].append(client_info)
                elif project_count >= 2 and total_hours >= 10:
                    value_tiers['standard'].append(client_info)
                else:
                    value_tiers['low_engagement'].append(client_info)
            
            # Calcular estadísticas por tier
            tier_stats = {}
            total_clients = len(clients_with_projects)
            
            for tier_name, clients in value_tiers.items():
                if clients:
                    total_tier_hours = sum(c['total_hours'] for c in clients)
                    total_tier_projects = sum(c['project_count'] for c in clients)
                    avg_projects_per_year = sum(c['projects_per_year'] for c in clients) / len(clients)
                    
                    tier_stats[tier_name] = {
                        'count': len(clients),
                        'percentage': round(len(clients) / total_clients * 100, 2),
                        'total_hours': total_tier_hours,
                        'total_projects': total_tier_projects,
                        'avg_hours_per_client': round(total_tier_hours / len(clients), 2),
                        'avg_projects_per_client': round(total_tier_projects / len(clients), 2),
                        'avg_projects_per_year': round(avg_projects_per_year, 2),
                        'top_clients': sorted(clients, key=lambda x: x['total_hours'], reverse=True)[:3]
                    }
                else:
                    tier_stats[tier_name] = {
                        'count': 0,
                        'percentage': 0,
                        'top_clients': []
                    }
            
            analysis = {
                'total_clients_with_projects': total_clients,
                'value_tiers': tier_stats,
                'benchmarks': {
                    'p75_total_hours': p75_hours,
                    'p90_total_hours': p90_hours,
                    'p75_project_count': p75_projects,
                    'avg_hours_per_client': round(sum(total_hours_list) / len(total_hours_list), 2),
                    'avg_projects_per_client': round(sum(project_counts_list) / len(project_counts_list), 2)
                },
                'analysis_timestamp': current_time.isoformat()
            }
            
            self._logger.debug(f"Análisis de valor completado para {total_clients} clientes")
            return analysis
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en análisis de valor: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_value_analysis",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en análisis de valor: {e}")
            raise create_client_statistics_error(
                message=f"Error en análisis de valor: {e}",
                original_error=e
            )
    
    async def get_client_retention_analysis(self) -> Dict[str, Any]:
        """
        Analiza la retención de clientes basado en actividad de proyectos.
        
        Returns:
            Diccionario con análisis de retención de clientes
        """
        try:
            current_time = get_current_time()
            
            # Definir períodos de análisis
            periods = {
                'last_30_days': current_time.subtract(days=30),
                'last_90_days': current_time.subtract(days=90),
                'last_180_days': current_time.subtract(days=180),
                'last_365_days': current_time.subtract(days=365)
            }
            
            # Obtener clientes con su último proyecto
            query = select(
                Client.id,
                Client.name,
                Client.code,
                Client.created_at,
                func.count(Project.id).label('total_projects'),
                func.max(Project.created_at).label('last_project_date'),
                func.min(Project.created_at).label('first_project_date')
            ).outerjoin(
                Project, Client.id == Project.client_id
            ).where(
                Client.is_active == True
            ).group_by(
                Client.id, Client.name, Client.code, Client.created_at
            )
            
            result = await self.session.execute(query)
            all_clients = result.all()
            
            if not all_clients:
                return {
                    'total_clients_analyzed': 0,
                    'retention_analysis': {},
                    'analysis_timestamp': current_time.isoformat()
                }
            
            # Analizar retención por período
            retention_data = {}
            
            for period_name, period_start in periods.items():
                active_in_period = []
                inactive_in_period = []
                new_in_period = []
                
                for client in all_clients:
                    # Cliente creado en este período
                    if client.created_at and client.created_at >= period_start.date():
                        new_in_period.append({
                            'id': client.id,
                            'name': client.name,
                            'code': client.code,
                            'created_at': client.created_at.isoformat(),
                            'total_projects': client.total_projects
                        })
                    
                    # Cliente con actividad en este período
                    elif client.last_project_date and client.last_project_date >= period_start.date():
                        active_in_period.append({
                            'id': client.id,
                            'name': client.name,
                            'code': client.code,
                            'last_project_date': client.last_project_date.isoformat(),
                            'total_projects': client.total_projects
                        })
                    
                    # Cliente sin actividad en este período
                    elif client.total_projects > 0:  # Solo considerar clientes que han tenido proyectos
                        inactive_in_period.append({
                            'id': client.id,
                            'name': client.name,
                            'code': client.code,
                            'last_project_date': client.last_project_date.isoformat() if client.last_project_date else None,
                            'total_projects': client.total_projects
                        })
                
                total_existing_clients = len([c for c in all_clients if c.created_at and c.created_at < period_start.date()])
                retention_rate = (
                    (len(active_in_period) / total_existing_clients * 100)
                    if total_existing_clients > 0 else 0
                )
                
                retention_data[period_name] = {
                    'active_clients': len(active_in_period),
                    'inactive_clients': len(inactive_in_period),
                    'new_clients': len(new_in_period),
                    'total_existing_clients': total_existing_clients,
                    'retention_rate': round(retention_rate, 2),
                    'churn_rate': round(100 - retention_rate, 2),
                    'sample_active_clients': active_in_period[:3],
                    'sample_inactive_clients': inactive_in_period[:3],
                    'sample_new_clients': new_in_period[:3]
                }
            
            # Calcular tendencias de retención
            retention_trend = {
                'improving': retention_data['last_30_days']['retention_rate'] > retention_data['last_90_days']['retention_rate'],
                'stable': abs(retention_data['last_30_days']['retention_rate'] - retention_data['last_90_days']['retention_rate']) <= 5,
                'declining': retention_data['last_30_days']['retention_rate'] < retention_data['last_90_days']['retention_rate']
            }
            
            analysis = {
                'total_clients_analyzed': len(all_clients),
                'retention_by_period': retention_data,
                'retention_trend': retention_trend,
                'analysis_timestamp': current_time.isoformat(),
                'methodology': {
                    'active_definition': 'Clientes con al menos un proyecto en el período',
                    'retention_calculation': 'Clientes activos / Total clientes existentes antes del período',
                    'churn_calculation': '100% - Tasa de retención'
                }
            }
            
            self._logger.debug(f"Análisis de retención completado para {len(all_clients)} clientes")
            return analysis
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos en análisis de retención: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_retention_analysis",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en análisis de retención: {e}")
            raise create_client_statistics_error(
                message=f"Error en análisis de retención: {e}",
                original_error=e
            )
    
    async def get_comprehensive_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas comprehensivas para un dashboard ejecutivo.
        
        Returns:
            Diccionario con todas las métricas principales para dashboard
        """
        try:
            self._logger.debug("Iniciando generación de métricas comprehensivas para dashboard")
            
            # Ejecutar todos los análisis en paralelo para mejor performance
            import asyncio
            
            basic_stats_task = self.get_client_counts_by_status()
            activity_summary_task = self.get_client_activity_summary()
            creation_trends_task = self.get_client_creation_trends(group_by='month', limit=6)
            contact_stats_task = self.get_contact_info_statistics()
            segmentation_task = self.get_client_segmentation_analysis()
            value_analysis_task = self.get_client_value_analysis()
            retention_analysis_task = self.get_client_retention_analysis()
            
            # Ejecutar todas las tareas de forma concurrente
            (
                basic_stats,
                activity_summary,
                creation_trends,
                contact_stats,
                segmentation,
                value_analysis,
                retention_analysis
            ) = await asyncio.gather(
                basic_stats_task,
                activity_summary_task,
                creation_trends_task,
                contact_stats_task,
                segmentation_task,
                value_analysis_task,
                retention_analysis_task
            )
            
            # Calcular KPIs principales
            current_time = get_current_time()
            
            # KPIs de crecimiento
            monthly_trends = creation_trends[-2:] if len(creation_trends) >= 2 else creation_trends
            growth_rate = 0
            if len(monthly_trends) == 2:
                current_month = monthly_trends[1]['count']
                previous_month = monthly_trends[0]['count']
                growth_rate = ((current_month - previous_month) / previous_month * 100) if previous_month > 0 else 0
            
            # KPIs de valor
            total_value_clients = sum(tier['count'] for tier in value_analysis['value_tiers'].values())
            premium_percentage = (
                value_analysis['value_tiers']['premium']['percentage']
                if 'premium' in value_analysis['value_tiers'] else 0
            )
            
            # KPIs de retención
            retention_30_days = (
                retention_analysis['retention_by_period']['last_30_days']['retention_rate']
                if 'last_30_days' in retention_analysis['retention_by_period'] else 0
            )
            
            dashboard_metrics = {
                'executive_summary': {
                    'total_clients': basic_stats['total'],
                    'active_clients': basic_stats['active'],
                    'monthly_growth_rate': round(growth_rate, 2),
                    'retention_rate_30_days': retention_30_days,
                    'premium_clients_percentage': premium_percentage,
                    'contact_completion_rate': contact_stats['contact_info_percentage'],
                    'clients_with_active_projects': activity_summary['clients_with_active_projects']
                },
                'detailed_analytics': {
                    'basic_statistics': basic_stats,
                    'activity_summary': activity_summary,
                    'creation_trends': creation_trends,
                    'contact_statistics': contact_stats,
                    'client_segmentation': segmentation,
                    'value_analysis': value_analysis,
                    'retention_analysis': retention_analysis
                },
                'alerts_and_insights': {
                    'low_retention_alert': retention_30_days < 70,
                    'growth_stagnation_alert': abs(growth_rate) < 5,
                    'contact_info_incomplete_alert': contact_stats['contact_info_percentage'] < 80,
                    'dormant_clients_count': segmentation['segments']['dormant']['count'],
                    'high_value_clients_count': (
                        segmentation['segments']['high_value']['count'] +
                        segmentation['segments']['premium']['count'] if 'premium' in segmentation['segments'] else 0
                    )
                },
                'generated_at': current_time.isoformat(),
                'data_freshness': {
                    'last_updated': current_time.isoformat(),
                    'analysis_period': 'Last 12 months',
                    'next_update_recommended': current_time.add(days=7).isoformat()
                }
            }
            
            self._logger.debug("Métricas comprehensivas de dashboard generadas exitosamente")
            return dashboard_metrics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos generando métricas de dashboard: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_comprehensive_dashboard_metrics",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado generando métricas de dashboard: {e}")
            raise create_client_statistics_error(
                message=f"Error generando métricas de dashboard: {e}",
                original_error=e
            )
    
    # ============================================================================
    # MÉTRICAS DE RENDIMIENTO (1 función)
    # ============================================================================
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento del sistema de clientes.
        
        Returns:
            Diccionario con métricas de rendimiento
        """
        try:
            current_time = get_current_time()
            
            # Métricas básicas
            basic_stats = await self.get_client_counts_by_status()
            activity_summary = await self.get_client_activity_summary()
            duration_stats = await self.get_client_relationship_duration_stats()
            
            # Métricas de crecimiento (últimos 30 días vs 30 días anteriores)
            thirty_days_ago = current_time.subtract(days=30)
            sixty_days_ago = current_time.subtract(days=60)
            
            # Clientes últimos 30 días
            recent_clients_query = select(func.count(Client.id)).where(
                Client.created_at >= thirty_days_ago
            )
            recent_clients_result = await self.session.execute(recent_clients_query)
            recent_clients = recent_clients_result.scalar() or 0
            
            # Clientes 30-60 días atrás
            previous_clients_query = select(func.count(Client.id)).where(
                and_(
                    Client.created_at >= sixty_days_ago,
                    Client.created_at < thirty_days_ago
                )
            )
            previous_clients_result = await self.session.execute(previous_clients_query)
            previous_clients = previous_clients_result.scalar() or 0
            
            # Calcular tasa de crecimiento
            growth_rate = (
                ((recent_clients - previous_clients) / previous_clients * 100)
                if previous_clients > 0 else 0
            )
            
            metrics = {
                'basic_statistics': basic_stats,
                'activity_summary': activity_summary,
                'relationship_duration': duration_stats,
                'growth_metrics': {
                    'clients_last_30_days': recent_clients,
                    'clients_previous_30_days': previous_clients,
                    'growth_rate_percentage': round(growth_rate, 2)
                },
                'generated_at': current_time.isoformat(),
                'period_analyzed': {
                    'start_date': sixty_days_ago.isoformat(),
                    'end_date': current_time.isoformat()
                }
            }
            
            self._logger.debug("Métricas de rendimiento generadas exitosamente")
            return metrics
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos generando métricas de rendimiento: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_performance_metrics",
                entity_type="Client"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado generando métricas de rendimiento: {e}")
            raise create_client_statistics_error(
                message=f"Error generando métricas de rendimiento: {e}",
                original_error=e
            )