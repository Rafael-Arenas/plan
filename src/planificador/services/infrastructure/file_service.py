# src/planificador/services/infrastructure/file_service.py

"""
Servicio de manejo de archivos y sistema de archivos.

Este módulo proporciona una interfaz unificada para operaciones
de archivos con manejo robusto de errores y logging.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Union, BinaryIO, TextIO
from contextlib import contextmanager

from loguru import logger

from ...exceptions.infrastructure import (
    FileSystemError,
    create_file_system_error
)
from ...config.config import settings


class FileService:
    """
    Servicio para operaciones de archivos y directorios.
    
    Proporciona métodos seguros para crear, leer, escribir,
    mover y eliminar archivos con manejo robusto de errores.
    """
    
    def __init__(self, base_directory: Optional[Path] = None):
        """
        Inicializa el servicio de archivos.
        
        Args:
            base_directory: Directorio base para operaciones relativas.
                          Si no se proporciona, usa settings.base_directory.
        """
        self.base_directory = base_directory or Path(settings.base_directory)
        self._ensure_base_directory()
    
    def _ensure_base_directory(self) -> None:
        """
        Asegura que el directorio base existe.
        """
        try:
            self.base_directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directorio base verificado: {self.base_directory}")
        except OSError as e:
            logger.error(f"Error al crear directorio base: {e}")
            raise create_file_system_error(
                message=f"No se pudo crear el directorio base: {e}",
                operation="create_base_directory",
                file_path=str(self.base_directory),
                original_error=e
            )
    
    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """
        Resuelve una ruta relativa al directorio base.
        
        Args:
            path: Ruta a resolver.
            
        Returns:
            Ruta absoluta resuelta.
        """
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj
        return self.base_directory / path_obj
    
    def create_directory(self, directory_path: Union[str, Path], 
                        parents: bool = True, exist_ok: bool = True) -> Path:
        """
        Crea un directorio.
        
        Args:
            directory_path: Ruta del directorio a crear.
            parents: Si crear directorios padre si no existen.
            exist_ok: Si no fallar si el directorio ya existe.
            
        Returns:
            Ruta del directorio creado.
            
        Raises:
            FileSystemError: Si no se puede crear el directorio.
        """
        try:
            resolved_path = self._resolve_path(directory_path)
            resolved_path.mkdir(parents=parents, exist_ok=exist_ok)
            logger.info(f"Directorio creado: {resolved_path}")
            return resolved_path
        except OSError as e:
            logger.error(f"Error al crear directorio {directory_path}: {e}")
            raise create_file_system_error(
                message=f"No se pudo crear el directorio: {e}",
                operation="create_directory",
                file_path=str(directory_path),
                original_error=e
            )
    
    def write_file(self, file_path: Union[str, Path], content: Union[str, bytes],
                   encoding: str = "utf-8", create_parents: bool = True) -> Path:
        """
        Escribe contenido a un archivo.
        
        Args:
            file_path: Ruta del archivo.
            content: Contenido a escribir.
            encoding: Codificación para archivos de texto.
            create_parents: Si crear directorios padre si no existen.
            
        Returns:
            Ruta del archivo escrito.
            
        Raises:
            FileSystemError: Si no se puede escribir el archivo.
        """
        try:
            resolved_path = self._resolve_path(file_path)
            
            if create_parents:
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, str):
                resolved_path.write_text(content, encoding=encoding)
            else:
                resolved_path.write_bytes(content)
            
            logger.info(f"Archivo escrito: {resolved_path}")
            return resolved_path
        except OSError as e:
            logger.error(f"Error al escribir archivo {file_path}: {e}")
            raise create_file_system_error(
                message=f"No se pudo escribir el archivo: {e}",
                operation="write_file",
                file_path=str(file_path),
                original_error=e
            )
    
    def read_file(self, file_path: Union[str, Path], 
                  encoding: str = "utf-8", binary: bool = False) -> Union[str, bytes]:
        """
        Lee el contenido de un archivo.
        
        Args:
            file_path: Ruta del archivo.
            encoding: Codificación para archivos de texto.
            binary: Si leer en modo binario.
            
        Returns:
            Contenido del archivo.
            
        Raises:
            FileSystemError: Si no se puede leer el archivo.
        """
        try:
            resolved_path = self._resolve_path(file_path)
            
            if not resolved_path.exists():
                raise FileNotFoundError(f"El archivo no existe: {resolved_path}")
            
            if binary:
                content = resolved_path.read_bytes()
            else:
                content = resolved_path.read_text(encoding=encoding)
            
            logger.debug(f"Archivo leído: {resolved_path}")
            return content
        except (OSError, FileNotFoundError) as e:
            logger.error(f"Error al leer archivo {file_path}: {e}")
            raise create_file_system_error(
                message=f"No se pudo leer el archivo: {e}",
                operation="read_file",
                file_path=str(file_path),
                original_error=e
            )
    
    def copy_file(self, source_path: Union[str, Path], 
                  destination_path: Union[str, Path],
                  create_parents: bool = True) -> Path:
        """
        Copia un archivo.
        
        Args:
            source_path: Ruta del archivo origen.
            destination_path: Ruta del archivo destino.
            create_parents: Si crear directorios padre si no existen.
            
        Returns:
            Ruta del archivo copiado.
            
        Raises:
            FileSystemError: Si no se puede copiar el archivo.
        """
        try:
            source_resolved = self._resolve_path(source_path)
            dest_resolved = self._resolve_path(destination_path)
            
            if not source_resolved.exists():
                raise FileNotFoundError(f"El archivo origen no existe: {source_resolved}")
            
            if create_parents:
                dest_resolved.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source_resolved, dest_resolved)
            logger.info(f"Archivo copiado: {source_resolved} -> {dest_resolved}")
            return dest_resolved
        except (OSError, FileNotFoundError, shutil.Error) as e:
            logger.error(f"Error al copiar archivo {source_path} -> {destination_path}: {e}")
            raise create_file_system_error(
                message=f"No se pudo copiar el archivo: {e}",
                operation="copy_file",
                file_path=str(source_path),
                original_error=e
            )
    
    def move_file(self, source_path: Union[str, Path], 
                  destination_path: Union[str, Path],
                  create_parents: bool = True) -> Path:
        """
        Mueve un archivo.
        
        Args:
            source_path: Ruta del archivo origen.
            destination_path: Ruta del archivo destino.
            create_parents: Si crear directorios padre si no existen.
            
        Returns:
            Ruta del archivo movido.
            
        Raises:
            FileSystemError: Si no se puede mover el archivo.
        """
        try:
            source_resolved = self._resolve_path(source_path)
            dest_resolved = self._resolve_path(destination_path)
            
            if not source_resolved.exists():
                raise FileNotFoundError(f"El archivo origen no existe: {source_resolved}")
            
            if create_parents:
                dest_resolved.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_resolved), str(dest_resolved))
            logger.info(f"Archivo movido: {source_resolved} -> {dest_resolved}")
            return dest_resolved
        except (OSError, FileNotFoundError, shutil.Error) as e:
            logger.error(f"Error al mover archivo {source_path} -> {destination_path}: {e}")
            raise create_file_system_error(
                message=f"No se pudo mover el archivo: {e}",
                operation="move_file",
                file_path=str(source_path),
                original_error=e
            )
    
    def delete_file(self, file_path: Union[str, Path]) -> None:
        """
        Elimina un archivo.
        
        Args:
            file_path: Ruta del archivo a eliminar.
            
        Raises:
            FileSystemError: Si no se puede eliminar el archivo.
        """
        try:
            resolved_path = self._resolve_path(file_path)
            
            if not resolved_path.exists():
                logger.warning(f"El archivo no existe, no se puede eliminar: {resolved_path}")
                return
            
            resolved_path.unlink()
            logger.info(f"Archivo eliminado: {resolved_path}")
        except OSError as e:
            logger.error(f"Error al eliminar archivo {file_path}: {e}")
            raise create_file_system_error(
                message=f"No se pudo eliminar el archivo: {e}",
                operation="delete_file",
                file_path=str(file_path),
                original_error=e
            )
    
    def delete_directory(self, directory_path: Union[str, Path], 
                        recursive: bool = False) -> None:
        """
        Elimina un directorio.
        
        Args:
            directory_path: Ruta del directorio a eliminar.
            recursive: Si eliminar recursivamente el contenido.
            
        Raises:
            FileSystemError: Si no se puede eliminar el directorio.
        """
        try:
            resolved_path = self._resolve_path(directory_path)
            
            if not resolved_path.exists():
                logger.warning(f"El directorio no existe, no se puede eliminar: {resolved_path}")
                return
            
            if recursive:
                shutil.rmtree(resolved_path)
            else:
                resolved_path.rmdir()
            
            logger.info(f"Directorio eliminado: {resolved_path}")
        except OSError as e:
            logger.error(f"Error al eliminar directorio {directory_path}: {e}")
            raise create_file_system_error(
                message=f"No se pudo eliminar el directorio: {e}",
                operation="delete_directory",
                file_path=str(directory_path),
                original_error=e
            )
    
    def list_files(self, directory_path: Union[str, Path], 
                   pattern: str = "*", recursive: bool = False) -> List[Path]:
        """
        Lista archivos en un directorio.
        
        Args:
            directory_path: Ruta del directorio.
            pattern: Patrón de archivos a buscar.
            recursive: Si buscar recursivamente.
            
        Returns:
            Lista de rutas de archivos encontrados.
            
        Raises:
            FileSystemError: Si no se puede listar el directorio.
        """
        try:
            resolved_path = self._resolve_path(directory_path)
            
            if not resolved_path.exists():
                raise FileNotFoundError(f"El directorio no existe: {resolved_path}")
            
            if recursive:
                files = list(resolved_path.rglob(pattern))
            else:
                files = list(resolved_path.glob(pattern))
            
            # Filtrar solo archivos (no directorios)
            files = [f for f in files if f.is_file()]
            
            logger.debug(f"Archivos listados en {resolved_path}: {len(files)} archivos")
            return files
        except (OSError, FileNotFoundError) as e:
            logger.error(f"Error al listar archivos en {directory_path}: {e}")
            raise create_file_system_error(
                message=f"No se pudo listar el directorio: {e}",
                operation="list_files",
                file_path=str(directory_path),
                original_error=e
            )
    
    def file_exists(self, file_path: Union[str, Path]) -> bool:
        """
        Verifica si un archivo existe.
        
        Args:
            file_path: Ruta del archivo.
            
        Returns:
            True si el archivo existe, False en caso contrario.
        """
        try:
            resolved_path = self._resolve_path(file_path)
            return resolved_path.exists() and resolved_path.is_file()
        except Exception as e:
            logger.error(f"Error al verificar existencia de archivo {file_path}: {e}")
            return False
    
    def directory_exists(self, directory_path: Union[str, Path]) -> bool:
        """
        Verifica si un directorio existe.
        
        Args:
            directory_path: Ruta del directorio.
            
        Returns:
            True si el directorio existe, False en caso contrario.
        """
        try:
            resolved_path = self._resolve_path(directory_path)
            return resolved_path.exists() and resolved_path.is_dir()
        except Exception as e:
            logger.error(f"Error al verificar existencia de directorio {directory_path}: {e}")
            return False
    
    def get_file_size(self, file_path: Union[str, Path]) -> int:
        """
        Obtiene el tamaño de un archivo en bytes.
        
        Args:
            file_path: Ruta del archivo.
            
        Returns:
            Tamaño del archivo en bytes.
            
        Raises:
            FileSystemError: Si no se puede obtener el tamaño del archivo.
        """
        try:
            resolved_path = self._resolve_path(file_path)
            
            if not resolved_path.exists():
                raise FileNotFoundError(f"El archivo no existe: {resolved_path}")
            
            size = resolved_path.stat().st_size
            logger.debug(f"Tamaño de archivo {resolved_path}: {size} bytes")
            return size
        except (OSError, FileNotFoundError) as e:
            logger.error(f"Error al obtener tamaño de archivo {file_path}: {e}")
            raise create_file_system_error(
                message=f"No se pudo obtener el tamaño del archivo: {e}",
                operation="get_file_size",
                file_path=str(file_path),
                original_error=e
            )
    
    @contextmanager
    def open_file(self, file_path: Union[str, Path], mode: str = "r", 
                  encoding: str = "utf-8", create_parents: bool = True):
        """
        Context manager para abrir archivos de forma segura.
        
        Args:
            file_path: Ruta del archivo.
            mode: Modo de apertura del archivo.
            encoding: Codificación para archivos de texto.
            create_parents: Si crear directorios padre si no existen.
            
        Yields:
            Objeto de archivo abierto.
            
        Raises:
            FileSystemError: Si no se puede abrir el archivo.
        """
        resolved_path = self._resolve_path(file_path)
        
        try:
            if create_parents and ("w" in mode or "a" in mode):
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
            
            if "b" in mode:
                file_obj = open(resolved_path, mode)
            else:
                file_obj = open(resolved_path, mode, encoding=encoding)
            
            logger.debug(f"Archivo abierto: {resolved_path} (modo: {mode})")
            yield file_obj
        except OSError as e:
            logger.error(f"Error al abrir archivo {file_path}: {e}")
            raise create_file_system_error(
                message=f"No se pudo abrir el archivo: {e}",
                operation="open_file",
                file_path=str(file_path),
                original_error=e
            )
        finally:
            try:
                if 'file_obj' in locals():
                    file_obj.close()
                    logger.debug(f"Archivo cerrado: {resolved_path}")
            except Exception as e:
                logger.error(f"Error al cerrar archivo {file_path}: {e}")


# Instancia global del servicio de archivos
file_service = FileService()