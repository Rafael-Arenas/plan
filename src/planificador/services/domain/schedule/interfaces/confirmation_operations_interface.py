"""
Interfaz para Operaciones de Gestión de Confirmaciones del Servicio de Dominio Schedule.

Define los contratos para el manejo de confirmaciones de horarios, estados de aprobación
y flujos de trabajo de validación con notificaciones automáticas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.schemas.schedule.schedule_response import ScheduleResponseSchema
from planificador.schemas.schedule.schedule_confirmation import (
    ScheduleConfirmationSchema,
    BulkConfirmationSchema,
    BulkConfirmationResultSchema,
    PendingConfirmationSchema
)


class IScheduleDomainConfirmationOperations(ABC):
    """
    Interfaz para operaciones de gestión de confirmaciones del servicio de dominio Schedule.
    
    Define los métodos para el manejo de confirmaciones, aprobaciones
    y flujos de trabajo de validación de horarios.
    """

    @abstractmethod
    async def confirm_schedule(
        self,
        schedule_id: int,
        confirmation_data: ScheduleConfirmationSchema
    ) -> ScheduleResponseSchema:
        """
        Confirma un horario específico con datos adicionales de validación.
        
        Args:
            schedule_id: ID del horario a confirmar
            confirmation_data: Datos de confirmación con validaciones adicionales
            
        Returns:
            ScheduleResponseSchema: Horario confirmado con detalles actualizados
            
        Raises:
            ValidationError: Si los datos de confirmación no son válidos
            NotFoundError: Si el horario no existe
            RepositoryError: Si hay error en la persistencia
        """
        pass

    @abstractmethod
    async def bulk_confirm_schedules(
        self,
        schedule_ids: List[int],
        confirmation_data: BulkConfirmationSchema
    ) -> BulkConfirmationResultSchema:
        """
        Confirma múltiples horarios en una operación transaccional.
        
        Args:
            schedule_ids: Lista de IDs de horarios a confirmar
            confirmation_data: Datos de confirmación masiva
            
        Returns:
            BulkConfirmationResultSchema: Resultado de la confirmación masiva
            
        Raises:
            ValidationError: Si los datos de confirmación no son válidos
            RepositoryError: Si hay error en la operación transaccional
        """
        pass

    @abstractmethod
    async def get_pending_confirmations(
        self,
        employee_id: Optional[int] = None,
        days_ahead: int = 7
    ) -> List[PendingConfirmationSchema]:
        """
        Obtiene horarios pendientes de confirmación con alertas de vencimiento.
        
        Args:
            employee_id: ID del empleado para filtrar (opcional)
            days_ahead: Días hacia adelante para buscar confirmaciones pendientes
            
        Returns:
            List[PendingConfirmationSchema]: Lista de horarios pendientes con alertas
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass