# -*- coding: utf-8 -*-
"""
Date Operations Interface for Client Domain Service

Define las operaciones relacionadas con fechas y tiempo para la entidad Client
con lógica de negocio y cálculos temporales.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID

from planificador.schemas.client import Client


class IDateOperations(ABC):
    """
    Interfaz para operaciones de fechas del dominio Client.
    
    Define métodos para gestionar fechas, períodos y cálculos
    temporales relacionados con clientes.
    """

    @abstractmethod
    async def get_clients_created_in_period(
        self,
        start_date: datetime,
        end_date: datetime,
        include_inactive: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes creados en un período específico.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes creados en el período
        """
        pass

    @abstractmethod
    async def get_clients_updated_in_period(
        self,
        start_date: datetime,
        end_date: datetime,
        include_inactive: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes actualizados en un período específico.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes actualizados en el período
        """
        pass

    @abstractmethod
    async def get_clients_by_creation_date(
        self,
        target_date: date,
        include_inactive: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes creados en una fecha específica.
        
        Args:
            target_date: Fecha específica de creación
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes creados en la fecha
        """
        pass

    @abstractmethod
    async def calculate_client_age_in_days(
        self,
        client_id: UUID,
        reference_date: Optional[datetime] = None
    ) -> int:
        """
        Calcula la edad de un cliente en días.
        
        Args:
            client_id: ID del cliente
            reference_date: Fecha de referencia (None = fecha actual)
            
        Returns:
            int: Edad del cliente en días
        """
        pass

    @abstractmethod
    async def get_clients_older_than_days(
        self,
        days: int,
        include_inactive: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes con más de X días de antigüedad.
        
        Args:
            days: Número de días de antigüedad mínima
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes con la antigüedad especificada
        """
        pass

    @abstractmethod
    async def get_clients_newer_than_days(
        self,
        days: int,
        include_inactive: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes con menos de X días de antigüedad.
        
        Args:
            days: Número de días de antigüedad máxima
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes recientes
        """
        pass

    @abstractmethod
    async def get_client_timeline_events(
        self,
        client_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene la línea de tiempo de eventos de un cliente.
        
        Args:
            client_id: ID del cliente
            start_date: Fecha de inicio del período (None = desde creación)
            end_date: Fecha de fin del período (None = hasta ahora)
            
        Returns:
            List[Dict[str, Any]]: Lista de eventos ordenados cronológicamente
        """
        pass

    @abstractmethod
    async def calculate_client_activity_periods(
        self,
        client_id: UUID,
        period_type: str = "month"
    ) -> Dict[str, Any]:
        """
        Calcula los períodos de actividad de un cliente.
        
        Args:
            client_id: ID del cliente
            period_type: Tipo de período (day, week, month, year)
            
        Returns:
            Dict[str, Any]: Análisis de períodos de actividad
        """
        pass

    @abstractmethod
    async def get_clients_anniversary_dates(
        self,
        month: Optional[int] = None,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Obtiene fechas de aniversario de clientes.
        
        Args:
            month: Mes específico (1-12, None para todos)
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            List[Dict[str, Any]]: Lista de clientes con fechas de aniversario
        """
        pass

    @abstractmethod
    async def schedule_client_date_reminders(
        self,
        client_id: UUID,
        reminder_types: List[str],
        advance_days: int = 7
    ) -> Dict[str, Any]:
        """
        Programa recordatorios basados en fechas del cliente.
        
        Args:
            client_id: ID del cliente
            reminder_types: Tipos de recordatorios a programar
            advance_days: Días de anticipación para los recordatorios
            
        Returns:
            Dict[str, Any]: Información de recordatorios programados
        """
        pass
