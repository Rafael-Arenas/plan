"""
Interfaz para Operaciones de Gestión de Confirmaciones del Servicio de Dominio Schedule.

Define los contratos para el manejo de confirmaciones de horarios, estados de aprobación
y flujos de trabajo de validación con notificaciones automáticas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.schemas.schedule.schedule import Schedule
from planificador.schemas.response.response_schemas import ScheduleListResponse


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
        confirmed_by: int,
        confirmation_notes: Optional[str] = None
    ) -> Schedule:
        """
        Confirma un horario específico con validaciones de autorización.
        
        Args:
            schedule_id: ID del horario a confirmar
            confirmed_by: ID del usuario que confirma
            confirmation_notes: Notas adicionales de confirmación (opcional)
            
        Returns:
            Schedule: Detalles de la confirmación realizada
            
        Raises:
            ValidationError: Si el horario no puede ser confirmado
            AuthorizationError: Si el usuario no tiene permisos
            RepositoryError: Si hay error en la persistencia
        """
        pass

    @abstractmethod
    async def get_pending_confirmations(
        self,
        employee_id: Optional[int] = None,
        project_id: Optional[int] = None,
        start_date: Optional[date] = None
    ) -> List[ScheduleListResponse]:
        """
        Obtiene horarios pendientes de confirmación con filtros opcionales.
        
        Args:
            employee_id: ID del empleado para filtrar (opcional)
            project_id: ID del proyecto para filtrar (opcional)
            start_date: Fecha de inicio para filtrar (opcional)
            
        Returns:
            List[ScheduleListResponse]: Lista de horarios pendientes
            
        Raises:
            ValidationError: Si los filtros no son válidos
            RepositoryError: Si hay error en la consulta
        """
        pass

    @abstractmethod
    async def get_confirmation_workflow_status(
        self,
        schedule_id: int
    ) -> Schedule:
        """
        Obtiene el estado completo del flujo de trabajo de aprobación de un horario.
        
        Args:
            schedule_id: ID del horario
            
        Returns:
            Schedule: Estado del flujo de trabajo
            
        Raises:
            ValidationError: Si el schedule_id no es válido
            RepositoryError: Si hay error en la consulta
        """
        pass