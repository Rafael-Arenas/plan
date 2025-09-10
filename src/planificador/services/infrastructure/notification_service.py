# src/planificador/services/infrastructure/notification_service.py

"""
Servicio de notificaciones.

Este módulo proporciona una interfaz unificada para enviar
notificaciones a través de diferentes canales (email, SMS, push, etc.).
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from ...exceptions.infrastructure import (
    ExternalServiceError,
    create_external_service_error
)
from ...utils.date_utils import get_current_datetime


class NotificationType(Enum):
    """
    Tipos de notificaciones disponibles.
    """
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    """
    Prioridades de notificaciones.
    """
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(Enum):
    """
    Estados de las notificaciones.
    """
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class NotificationRecipient:
    """
    Información del destinatario de una notificación.
    """
    identifier: str  # Email, teléfono, user_id, etc.
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class NotificationContent:
    """
    Contenido de una notificación.
    """
    title: str
    body: str
    html_body: Optional[str] = None
    attachments: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class NotificationRequest:
    """
    Solicitud de notificación.
    """
    notification_type: NotificationType
    recipients: List[NotificationRecipient]
    content: NotificationContent
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class NotificationResult:
    """
    Resultado del envío de una notificación.
    """
    notification_id: str
    status: NotificationStatus
    sent_at: datetime
    recipient: NotificationRecipient
    error_message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None


class NotificationProvider(ABC):
    """
    Interfaz base para proveedores de notificaciones.
    """
    
    @abstractmethod
    async def send_notification(self, request: NotificationRequest) -> List[NotificationResult]:
        """
        Envía una notificación.
        
        Args:
            request: Solicitud de notificación.
            
        Returns:
            Lista de resultados del envío.
            
        Raises:
            ExternalServiceError: Si hay un error al enviar la notificación.
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Obtiene el nombre del proveedor.
        
        Returns:
            Nombre del proveedor.
        """
        pass
    
    @abstractmethod
    def supports_notification_type(self, notification_type: NotificationType) -> bool:
        """
        Verifica si el proveedor soporta un tipo de notificación.
        
        Args:
            notification_type: Tipo de notificación.
            
        Returns:
            True si soporta el tipo, False en caso contrario.
        """
        pass


class EmailProvider(NotificationProvider):
    """
    Proveedor de notificaciones por email (implementación mock).
    """
    
    def __init__(self, smtp_host: str = "localhost", smtp_port: int = 587,
                 username: Optional[str] = None, password: Optional[str] = None):
        """
        Inicializa el proveedor de email.
        
        Args:
            smtp_host: Host del servidor SMTP.
            smtp_port: Puerto del servidor SMTP.
            username: Usuario para autenticación.
            password: Contraseña para autenticación.
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    async def send_notification(self, request: NotificationRequest) -> List[NotificationResult]:
        """
        Envía notificaciones por email.
        
        Args:
            request: Solicitud de notificación.
            
        Returns:
            Lista de resultados del envío.
            
        Raises:
            ExternalServiceError: Si hay un error al enviar el email.
        """
        try:
            results = []
            
            for recipient in request.recipients:
                # Simulación de envío de email
                # En una implementación real, aquí se usaría una librería como aiosmtplib
                logger.info(
                    f"Enviando email a {recipient.identifier}: {request.content.title}"
                )
                
                # Simular éxito o fallo basado en validación básica
                if "@" in recipient.identifier and "." in recipient.identifier:
                    status = NotificationStatus.SENT
                    error_message = None
                else:
                    status = NotificationStatus.FAILED
                    error_message = "Dirección de email inválida"
                
                result = NotificationResult(
                    notification_id=f"email_{get_current_datetime().timestamp()}_{recipient.identifier}",
                    status=status,
                    sent_at=get_current_datetime(),
                    recipient=recipient,
                    error_message=error_message,
                    provider_response={"provider": "email_mock", "smtp_host": self.smtp_host}
                )
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error al enviar notificación por email: {e}")
            raise create_external_service_error(
                message=f"Error al enviar email: {e}",
                service_name="email_provider",
                operation="send_email",
                original_error=e
            )
    
    def get_provider_name(self) -> str:
        """
        Obtiene el nombre del proveedor.
        
        Returns:
            Nombre del proveedor.
        """
        return "email_provider"
    
    def supports_notification_type(self, notification_type: NotificationType) -> bool:
        """
        Verifica si el proveedor soporta un tipo de notificación.
        
        Args:
            notification_type: Tipo de notificación.
            
        Returns:
            True si soporta el tipo, False en caso contrario.
        """
        return notification_type == NotificationType.EMAIL


class InAppProvider(NotificationProvider):
    """
    Proveedor de notificaciones in-app.
    """
    
    def __init__(self):
        """
        Inicializa el proveedor de notificaciones in-app.
        """
        self.notifications_store: Dict[str, List[NotificationResult]] = {}
    
    async def send_notification(self, request: NotificationRequest) -> List[NotificationResult]:
        """
        Envía notificaciones in-app.
        
        Args:
            request: Solicitud de notificación.
            
        Returns:
            Lista de resultados del envío.
        """
        try:
            results = []
            
            for recipient in request.recipients:
                logger.info(
                    f"Enviando notificación in-app a {recipient.identifier}: {request.content.title}"
                )
                
                result = NotificationResult(
                    notification_id=f"inapp_{get_current_datetime().timestamp()}_{recipient.identifier}",
                    status=NotificationStatus.DELIVERED,
                    sent_at=get_current_datetime(),
                    recipient=recipient,
                    provider_response={"provider": "in_app", "stored": True}
                )
                
                # Almacenar la notificación para el usuario
                user_id = recipient.identifier
                if user_id not in self.notifications_store:
                    self.notifications_store[user_id] = []
                self.notifications_store[user_id].append(result)
                
                results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error al enviar notificación in-app: {e}")
            raise create_external_service_error(
                message=f"Error al enviar notificación in-app: {e}",
                service_name="in_app_provider",
                operation="send_in_app",
                original_error=e
            )
    
    def get_provider_name(self) -> str:
        """
        Obtiene el nombre del proveedor.
        
        Returns:
            Nombre del proveedor.
        """
        return "in_app_provider"
    
    def supports_notification_type(self, notification_type: NotificationType) -> bool:
        """
        Verifica si el proveedor soporta un tipo de notificación.
        
        Args:
            notification_type: Tipo de notificación.
            
        Returns:
            True si soporta el tipo, False en caso contrario.
        """
        return notification_type == NotificationType.IN_APP
    
    def get_user_notifications(self, user_id: str) -> List[NotificationResult]:
        """
        Obtiene las notificaciones de un usuario.
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            Lista de notificaciones del usuario.
        """
        return self.notifications_store.get(user_id, [])


class NotificationService:
    """
    Servicio principal de notificaciones.
    
    Gestiona múltiples proveedores y enruta las notificaciones
    al proveedor apropiado según el tipo.
    """
    
    def __init__(self):
        """
        Inicializa el servicio de notificaciones.
        """
        self.providers: Dict[NotificationType, NotificationProvider] = {}
        self._setup_default_providers()
    
    def _setup_default_providers(self) -> None:
        """
        Configura los proveedores por defecto.
        """
        # Configurar proveedor de email
        email_provider = EmailProvider()
        self.register_provider(NotificationType.EMAIL, email_provider)
        
        # Configurar proveedor in-app
        in_app_provider = InAppProvider()
        self.register_provider(NotificationType.IN_APP, in_app_provider)
        
        logger.info("Proveedores de notificaciones configurados")
    
    def register_provider(self, notification_type: NotificationType, 
                         provider: NotificationProvider) -> None:
        """
        Registra un proveedor para un tipo de notificación.
        
        Args:
            notification_type: Tipo de notificación.
            provider: Proveedor de notificaciones.
        """
        if not provider.supports_notification_type(notification_type):
            raise ValueError(
                f"El proveedor {provider.get_provider_name()} no soporta "
                f"notificaciones de tipo {notification_type.value}"
            )
        
        self.providers[notification_type] = provider
        logger.info(
            f"Proveedor registrado: {provider.get_provider_name()} "
            f"para tipo {notification_type.value}"
        )
    
    async def send_notification(self, request: NotificationRequest) -> List[NotificationResult]:
        """
        Envía una notificación.
        
        Args:
            request: Solicitud de notificación.
            
        Returns:
            Lista de resultados del envío.
            
        Raises:
            ExternalServiceError: Si no hay proveedor disponible o hay error al enviar.
        """
        try:
            provider = self.providers.get(request.notification_type)
            if not provider:
                raise ValueError(
                    f"No hay proveedor disponible para notificaciones de tipo "
                    f"{request.notification_type.value}"
                )
            
            logger.info(
                f"Enviando notificación {request.notification_type.value} "
                f"a {len(request.recipients)} destinatarios"
            )
            
            results = await provider.send_notification(request)
            
            # Log de resultados
            successful = sum(1 for r in results if r.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED])
            failed = len(results) - successful
            
            logger.info(
                f"Notificación enviada: {successful} exitosas, {failed} fallidas"
            )
            
            return results
        except ValueError as e:
            logger.error(f"Error de configuración en notificaciones: {e}")
            raise create_external_service_error(
                message=str(e),
                service_name="notification_service",
                operation="send_notification"
            )
        except Exception as e:
            logger.error(f"Error inesperado al enviar notificación: {e}")
            raise create_external_service_error(
                message=f"Error inesperado al enviar notificación: {e}",
                service_name="notification_service",
                operation="send_notification",
                original_error=e
            )
    
    async def send_email(self, recipients: List[str], title: str, body: str,
                        html_body: Optional[str] = None,
                        priority: NotificationPriority = NotificationPriority.NORMAL) -> List[NotificationResult]:
        """
        Método de conveniencia para enviar emails.
        
        Args:
            recipients: Lista de direcciones de email.
            title: Título del email.
            body: Cuerpo del email en texto plano.
            html_body: Cuerpo del email en HTML (opcional).
            priority: Prioridad del email.
            
        Returns:
            Lista de resultados del envío.
        """
        notification_recipients = [
            NotificationRecipient(identifier=email) for email in recipients
        ]
        
        content = NotificationContent(
            title=title,
            body=body,
            html_body=html_body
        )
        
        request = NotificationRequest(
            notification_type=NotificationType.EMAIL,
            recipients=notification_recipients,
            content=content,
            priority=priority
        )
        
        return await self.send_notification(request)
    
    async def send_in_app_notification(self, user_ids: List[str], title: str, body: str,
                                      priority: NotificationPriority = NotificationPriority.NORMAL) -> List[NotificationResult]:
        """
        Método de conveniencia para enviar notificaciones in-app.
        
        Args:
            user_ids: Lista de IDs de usuarios.
            title: Título de la notificación.
            body: Cuerpo de la notificación.
            priority: Prioridad de la notificación.
            
        Returns:
            Lista de resultados del envío.
        """
        notification_recipients = [
            NotificationRecipient(identifier=user_id) for user_id in user_ids
        ]
        
        content = NotificationContent(
            title=title,
            body=body
        )
        
        request = NotificationRequest(
            notification_type=NotificationType.IN_APP,
            recipients=notification_recipients,
            content=content,
            priority=priority
        )
        
        return await self.send_notification(request)
    
    def get_available_providers(self) -> Dict[str, str]:
        """
        Obtiene la lista de proveedores disponibles.
        
        Returns:
            Diccionario con tipos de notificación y nombres de proveedores.
        """
        return {
            notification_type.value: provider.get_provider_name()
            for notification_type, provider in self.providers.items()
        }
    
    def get_in_app_provider(self) -> Optional[InAppProvider]:
        """
        Obtiene el proveedor de notificaciones in-app.
        
        Returns:
            Proveedor in-app si está disponible, None en caso contrario.
        """
        provider = self.providers.get(NotificationType.IN_APP)
        if isinstance(provider, InAppProvider):
            return provider
        return None


# Instancia global del servicio de notificaciones
notification_service = NotificationService()