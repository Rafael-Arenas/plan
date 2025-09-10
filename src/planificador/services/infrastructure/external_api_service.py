# src/planificador/services/infrastructure/external_api_service.py

"""
Servicio de integración con APIs externas.

Este módulo proporciona una interfaz unificada para comunicarse
con servicios externos y APIs de terceros.
"""

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

import aiohttp
from loguru import logger

from ...exceptions.infrastructure import (
    ExternalServiceError,
    NetworkError,
    create_external_service_error,
    create_network_error
)
from ...utils.date_utils import get_current_datetime


class HttpMethod(Enum):
    """
    Métodos HTTP soportados.
    """
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthenticationType(Enum):
    """
    Tipos de autenticación soportados.
    """
    NONE = "none"
    BEARER_TOKEN = "bearer_token"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"
    CUSTOM_HEADER = "custom_header"


@dataclass
class ApiCredentials:
    """
    Credenciales para autenticación con APIs.
    """
    auth_type: AuthenticationType
    token: Optional[str] = None
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    expires_at: Optional[datetime] = None


@dataclass
class ApiRequest:
    """
    Solicitud a una API externa.
    """
    method: HttpMethod
    url: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    data: Optional[Union[Dict[str, Any], str, bytes]] = None
    json_data: Optional[Dict[str, Any]] = None
    timeout: int = 30
    retries: int = 3
    retry_delay: float = 1.0
    credentials: Optional[ApiCredentials] = None


@dataclass
class ApiResponse:
    """
    Respuesta de una API externa.
    """
    status_code: int
    headers: Dict[str, str]
    content: bytes
    text: str
    json_data: Optional[Dict[str, Any]] = None
    request_duration: float = 0.0
    request_url: str = ""
    request_method: str = ""
    timestamp: datetime = field(default_factory=get_current_datetime)


class RateLimiter:
    """
    Limitador de velocidad para APIs.
    """
    
    def __init__(self, max_requests: int, time_window: int):
        """
        Inicializa el limitador de velocidad.
        
        Args:
            max_requests: Número máximo de requests permitidos.
            time_window: Ventana de tiempo en segundos.
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[datetime] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """
        Adquiere permiso para hacer una request.
        
        Raises:
            ExternalServiceError: Si se excede el límite de velocidad.
        """
        async with self._lock:
            now = get_current_datetime()
            
            # Limpiar requests antiguos
            cutoff_time = now - timedelta(seconds=self.time_window)
            self.requests = [req_time for req_time in self.requests if req_time > cutoff_time]
            
            # Verificar límite
            if len(self.requests) >= self.max_requests:
                oldest_request = min(self.requests)
                wait_time = (oldest_request + timedelta(seconds=self.time_window) - now).total_seconds()
                
                if wait_time > 0:
                    logger.warning(f"Rate limit alcanzado, esperando {wait_time:.2f} segundos")
                    await asyncio.sleep(wait_time)
            
            # Registrar nueva request
            self.requests.append(now)


class ApiClient:
    """
    Cliente HTTP para comunicación con APIs externas.
    """
    
    def __init__(self, base_url: Optional[str] = None,
                 default_headers: Optional[Dict[str, str]] = None,
                 default_timeout: int = 30,
                 rate_limiter: Optional[RateLimiter] = None):
        """
        Inicializa el cliente de API.
        
        Args:
            base_url: URL base para todas las requests.
            default_headers: Headers por defecto.
            default_timeout: Timeout por defecto en segundos.
            rate_limiter: Limitador de velocidad opcional.
        """
        self.base_url = base_url.rstrip('/') if base_url else None
        self.default_headers = default_headers or {}
        self.default_timeout = default_timeout
        self.rate_limiter = rate_limiter
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """
        Entrada del context manager.
        """
        await self.start_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Salida del context manager.
        """
        await self.close_session()
    
    async def start_session(self) -> None:
        """
        Inicia la sesión HTTP.
        """
        if not self.session or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            timeout = aiohttp.ClientTimeout(total=self.default_timeout)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.default_headers
            )
    
    async def close_session(self) -> None:
        """
        Cierra la sesión HTTP.
        """
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    def _build_url(self, url: str) -> str:
        """
        Construye la URL completa.
        
        Args:
            url: URL relativa o absoluta.
            
        Returns:
            URL completa.
        """
        if url.startswith(('http://', 'https://')):
            return url
        
        if self.base_url:
            return f"{self.base_url}/{url.lstrip('/')}"
        
        return url
    
    def _apply_authentication(self, headers: Dict[str, str], 
                            credentials: Optional[ApiCredentials]) -> Dict[str, str]:
        """
        Aplica autenticación a los headers.
        
        Args:
            headers: Headers existentes.
            credentials: Credenciales de autenticación.
            
        Returns:
            Headers con autenticación aplicada.
        """
        if not credentials or credentials.auth_type == AuthenticationType.NONE:
            return headers
        
        auth_headers = headers.copy()
        
        if credentials.auth_type == AuthenticationType.BEARER_TOKEN and credentials.token:
            auth_headers['Authorization'] = f'Bearer {credentials.token}'
        
        elif credentials.auth_type == AuthenticationType.API_KEY and credentials.api_key:
            auth_headers['X-API-Key'] = credentials.api_key
        
        elif credentials.auth_type == AuthenticationType.BASIC_AUTH:
            if credentials.username and credentials.password:
                import base64
                credentials_str = f"{credentials.username}:{credentials.password}"
                encoded_credentials = base64.b64encode(credentials_str.encode()).decode()
                auth_headers['Authorization'] = f'Basic {encoded_credentials}'
        
        elif credentials.auth_type == AuthenticationType.CUSTOM_HEADER and credentials.custom_headers:
            auth_headers.update(credentials.custom_headers)
        
        return auth_headers
    
    async def make_request(self, request: ApiRequest) -> ApiResponse:
        """
        Realiza una request HTTP.
        
        Args:
            request: Configuración de la request.
            
        Returns:
            Respuesta de la API.
            
        Raises:
            NetworkError: Si hay problemas de conectividad.
            ExternalServiceError: Si hay errores en la API externa.
        """
        if not self.session:
            await self.start_session()
        
        # Aplicar rate limiting
        if self.rate_limiter:
            await self.rate_limiter.acquire()
        
        url = self._build_url(request.url)
        headers = request.headers or {}
        headers = self._apply_authentication(headers, request.credentials)
        
        # Configurar datos de la request
        kwargs = {
            'params': request.params,
            'headers': headers,
            'timeout': aiohttp.ClientTimeout(total=request.timeout)
        }
        
        if request.json_data is not None:
            kwargs['json'] = request.json_data
        elif request.data is not None:
            kwargs['data'] = request.data
        
        start_time = get_current_datetime()
        
        for attempt in range(request.retries + 1):
            try:
                logger.debug(f"Realizando {request.method.value} request a {url} (intento {attempt + 1})")
                
                async with self.session.request(
                    method=request.method.value,
                    url=url,
                    **kwargs
                ) as response:
                    content = await response.read()
                    text = await response.text()
                    
                    # Intentar parsear JSON
                    json_data = None
                    if response.content_type and 'json' in response.content_type:
                        try:
                            json_data = await response.json()
                        except (json.JSONDecodeError, aiohttp.ContentTypeError):
                            logger.warning(f"No se pudo parsear JSON de la respuesta: {text[:200]}")
                    
                    duration = (get_current_datetime() - start_time).total_seconds()
                    
                    api_response = ApiResponse(
                        status_code=response.status,
                        headers=dict(response.headers),
                        content=content,
                        text=text,
                        json_data=json_data,
                        request_duration=duration,
                        request_url=str(response.url),
                        request_method=request.method.value
                    )
                    
                    # Verificar si la respuesta indica error
                    if response.status >= 400:
                        error_message = f"HTTP {response.status}: {text[:500]}"
                        
                        if response.status >= 500:
                            # Error del servidor, reintentar
                            if attempt < request.retries:
                                wait_time = request.retry_delay * (2 ** attempt)
                                logger.warning(
                                    f"Error del servidor ({response.status}), "
                                    f"reintentando en {wait_time}s"
                                )
                                await asyncio.sleep(wait_time)
                                continue
                        
                        raise create_external_service_error(
                            message=error_message,
                            service_name=url,
                            operation=request.method.value,
                            status_code=response.status,
                            response_data=json_data or text
                        )
                    
                    logger.debug(
                        f"Request exitosa: {request.method.value} {url} "
                        f"-> {response.status} ({duration:.2f}s)"
                    )
                    
                    return api_response
            
            except aiohttp.ClientConnectorError as e:
                if attempt < request.retries:
                    wait_time = request.retry_delay * (2 ** attempt)
                    logger.warning(f"Error de conexión, reintentando en {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                    continue
                
                logger.error(f"Error de conexión a {url}: {e}")
                raise create_network_error(
                    message=f"No se pudo conectar a {url}: {e}",
                    host=url,
                    operation=request.method.value,
                    original_error=e
                )
            
            except aiohttp.ClientTimeout as e:
                if attempt < request.retries:
                    wait_time = request.retry_delay * (2 ** attempt)
                    logger.warning(f"Timeout, reintentando en {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                    continue
                
                logger.error(f"Timeout en request a {url}: {e}")
                raise create_network_error(
                    message=f"Timeout en request a {url}: {e}",
                    host=url,
                    operation=request.method.value,
                    original_error=e
                )
            
            except Exception as e:
                logger.error(f"Error inesperado en request a {url}: {e}")
                raise create_external_service_error(
                    message=f"Error inesperado en request: {e}",
                    service_name=url,
                    operation=request.method.value,
                    original_error=e
                )
        
        # Si llegamos aquí, se agotaron todos los reintentos
        raise create_external_service_error(
            message=f"Se agotaron los reintentos para {request.method.value} {url}",
            service_name=url,
            operation=request.method.value
        )


class ExternalApiService:
    """
    Servicio principal para integración con APIs externas.
    
    Proporciona una interfaz de alto nivel para comunicarse
    con servicios externos de manera robusta y escalable.
    """
    
    def __init__(self):
        """
        Inicializa el servicio de APIs externas.
        """
        self.clients: Dict[str, ApiClient] = {}
        self.default_rate_limiter = RateLimiter(max_requests=100, time_window=60)
    
    def register_client(self, name: str, client: ApiClient) -> None:
        """
        Registra un cliente de API.
        
        Args:
            name: Nombre del cliente.
            client: Instancia del cliente.
        """
        self.clients[name] = client
        logger.info(f"Cliente de API registrado: {name}")
    
    def create_client(self, name: str, base_url: str,
                     default_headers: Optional[Dict[str, str]] = None,
                     rate_limit_requests: int = 100,
                     rate_limit_window: int = 60) -> ApiClient:
        """
        Crea y registra un nuevo cliente de API.
        
        Args:
            name: Nombre del cliente.
            base_url: URL base del servicio.
            default_headers: Headers por defecto.
            rate_limit_requests: Límite de requests por ventana.
            rate_limit_window: Ventana de tiempo en segundos.
            
        Returns:
            Cliente de API creado.
        """
        rate_limiter = RateLimiter(
            max_requests=rate_limit_requests,
            time_window=rate_limit_window
        )
        
        client = ApiClient(
            base_url=base_url,
            default_headers=default_headers,
            rate_limiter=rate_limiter
        )
        
        self.register_client(name, client)
        return client
    
    async def make_request(self, client_name: str, request: ApiRequest) -> ApiResponse:
        """
        Realiza una request usando un cliente específico.
        
        Args:
            client_name: Nombre del cliente a usar.
            request: Configuración de la request.
            
        Returns:
            Respuesta de la API.
            
        Raises:
            ExternalServiceError: Si el cliente no existe o hay error en la request.
        """
        client = self.clients.get(client_name)
        if not client:
            raise create_external_service_error(
                message=f"Cliente de API no encontrado: {client_name}",
                service_name=client_name,
                operation="get_client"
            )
        
        try:
            return await client.make_request(request)
        except Exception as e:
            logger.error(f"Error en request con cliente {client_name}: {e}")
            raise
    
    async def get_json(self, client_name: str, url: str,
                      params: Optional[Dict[str, Any]] = None,
                      headers: Optional[Dict[str, str]] = None,
                      credentials: Optional[ApiCredentials] = None) -> Dict[str, Any]:
        """
        Método de conveniencia para GET requests que retornan JSON.
        
        Args:
            client_name: Nombre del cliente.
            url: URL del endpoint.
            params: Parámetros de query.
            headers: Headers adicionales.
            credentials: Credenciales de autenticación.
            
        Returns:
            Datos JSON de la respuesta.
            
        Raises:
            ExternalServiceError: Si hay error en la request o no hay datos JSON.
        """
        request = ApiRequest(
            method=HttpMethod.GET,
            url=url,
            params=params,
            headers=headers,
            credentials=credentials
        )
        
        response = await self.make_request(client_name, request)
        
        if response.json_data is None:
            raise create_external_service_error(
                message="La respuesta no contiene datos JSON válidos",
                service_name=client_name,
                operation="parse_json",
                response_data=response.text[:500]
            )
        
        return response.json_data
    
    async def post_json(self, client_name: str, url: str,
                       data: Dict[str, Any],
                       headers: Optional[Dict[str, str]] = None,
                       credentials: Optional[ApiCredentials] = None) -> Dict[str, Any]:
        """
        Método de conveniencia para POST requests con JSON.
        
        Args:
            client_name: Nombre del cliente.
            url: URL del endpoint.
            data: Datos a enviar como JSON.
            headers: Headers adicionales.
            credentials: Credenciales de autenticación.
            
        Returns:
            Datos JSON de la respuesta.
        """
        request = ApiRequest(
            method=HttpMethod.POST,
            url=url,
            json_data=data,
            headers=headers,
            credentials=credentials
        )
        
        response = await self.make_request(client_name, request)
        return response.json_data or {}
    
    async def close_all_clients(self) -> None:
        """
        Cierra todas las sesiones de los clientes.
        """
        for name, client in self.clients.items():
            try:
                await client.close_session()
                logger.debug(f"Cliente cerrado: {name}")
            except Exception as e:
                logger.warning(f"Error al cerrar cliente {name}: {e}")
    
    def get_client_names(self) -> List[str]:
        """
        Obtiene los nombres de todos los clientes registrados.
        
        Returns:
            Lista de nombres de clientes.
        """
        return list(self.clients.keys())


# Instancia global del servicio de APIs externas
external_api_service = ExternalApiService()