# -*- coding: utf-8 -*-
"""
Utilidades para manejo de archivos y sistema de archivos.

Este módulo proporciona funciones de alto nivel para operaciones comunes
con archivos y directorios, con manejo robusto de errores usando el
sistema de excepciones de infraestructura.

Author: Sistema de Planificación
Date: 2024
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Generator
from datetime import datetime

from loguru import logger

from ..exceptions import (
    FileSystemError,
    ValidationError,
    create_file_system_error
)


# Tipos de archivos comunes
PathLike = Union[str, Path]


def ensure_directory(path: PathLike) -> Path:
    """
    Asegura que un directorio exista, creándolo si es necesario.
    
    Args:
        path: Ruta del directorio a crear.
        
    Returns:
        Path: Objeto Path del directorio creado.
        
    Raises:
        FileSystemError: Si no se puede crear el directorio.
        ValidationError: Si la ruta es inválida.
        
    Examples:
        >>> ensure_directory('/tmp/mi_directorio')
        Path('/tmp/mi_directorio')
    """
    if not path:
        raise ValidationError(
            message="La ruta del directorio no puede estar vacía",
            field="path",
            value=path
        )
    
    try:
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directorio asegurado: {path_obj}")
        return path_obj
    except (OSError, IOError) as e:
        logger.error(f"Error al crear directorio {path}: {e}")
        raise create_file_system_error(
            message=f"No se pudo crear el directorio: {path}",
            operation="create_directory",
            path=str(path),
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al crear directorio {path}: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al crear directorio: {e}",
            operation="create_directory",
            path=str(path),
            original_error=e
        )


def read_text_file(file_path: PathLike, encoding: str = 'utf-8') -> str:
    """
    Lee el contenido completo de un archivo de texto.
    
    Args:
        file_path: Ruta del archivo a leer.
        encoding: Codificación del archivo (por defecto UTF-8).
        
    Returns:
        str: Contenido del archivo.
        
    Raises:
        FileSystemError: Si no se puede leer el archivo.
        ValidationError: Si la ruta es inválida.
        
    Examples:
        >>> content = read_text_file('config.txt')
        >>> print(content)
    """
    if not file_path:
        raise ValidationError(
            message="La ruta del archivo no puede estar vacía",
            field="file_path",
            value=file_path
        )
    
    try:
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileSystemError(
                message=f"El archivo no existe: {file_path}",
                operation="read_file",
                path=str(file_path)
            )
        
        if not path_obj.is_file():
            raise FileSystemError(
                message=f"La ruta no es un archivo: {file_path}",
                operation="read_file",
                path=str(file_path)
            )
        
        content = path_obj.read_text(encoding=encoding)
        logger.debug(f"Archivo leído: {file_path} ({len(content)} caracteres)")
        return content
    except FileSystemError:
        # Re-lanzar errores de sistema de archivos
        raise
    except (OSError, IOError, UnicodeDecodeError) as e:
        logger.error(f"Error al leer archivo {file_path}: {e}")
        raise create_file_system_error(
            message=f"No se pudo leer el archivo: {file_path}",
            operation="read_file",
            path=str(file_path),
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al leer archivo {file_path}: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al leer archivo: {e}",
            operation="read_file",
            path=str(file_path),
            original_error=e
        )


def write_text_file(
    file_path: PathLike,
    content: str,
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> None:
    """
    Escribe contenido a un archivo de texto.
    
    Args:
        file_path: Ruta del archivo a escribir.
        content: Contenido a escribir.
        encoding: Codificación del archivo (por defecto UTF-8).
        create_dirs: Si crear directorios padre si no existen.
        
    Raises:
        FileSystemError: Si no se puede escribir el archivo.
        ValidationError: Si los parámetros son inválidos.
        
    Examples:
        >>> write_text_file('output.txt', 'Hola mundo')
        >>> write_text_file('logs/app.log', 'Log entry', create_dirs=True)
    """
    if not file_path:
        raise ValidationError(
            message="La ruta del archivo no puede estar vacía",
            field="file_path",
            value=file_path
        )
    
    if content is None:
        raise ValidationError(
            message="El contenido no puede ser None",
            field="content",
            value=content
        )
    
    try:
        path_obj = Path(file_path)
        
        # Crear directorios padre si es necesario
        if create_dirs and path_obj.parent != path_obj:
            ensure_directory(path_obj.parent)
        
        path_obj.write_text(content, encoding=encoding)
        logger.debug(f"Archivo escrito: {file_path} ({len(content)} caracteres)")
    except (OSError, IOError, UnicodeEncodeError) as e:
        logger.error(f"Error al escribir archivo {file_path}: {e}")
        raise create_file_system_error(
            message=f"No se pudo escribir el archivo: {file_path}",
            operation="write_file",
            path=str(file_path),
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al escribir archivo {file_path}: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al escribir archivo: {e}",
            operation="write_file",
            path=str(file_path),
            original_error=e
        )


def copy_file(source: PathLike, destination: PathLike, overwrite: bool = False) -> None:
    """
    Copia un archivo de origen a destino.
    
    Args:
        source: Ruta del archivo origen.
        destination: Ruta del archivo destino.
        overwrite: Si sobrescribir el archivo destino si existe.
        
    Raises:
        FileSystemError: Si no se puede copiar el archivo.
        ValidationError: Si las rutas son inválidas.
        
    Examples:
        >>> copy_file('source.txt', 'backup.txt')
        >>> copy_file('data.json', 'backup/data.json', overwrite=True)
    """
    if not source or not destination:
        raise ValidationError(
            message="Las rutas de origen y destino no pueden estar vacías",
            field="paths",
            value=f"{source} -> {destination}"
        )
    
    try:
        source_path = Path(source)
        dest_path = Path(destination)
        
        if not source_path.exists():
            raise FileSystemError(
                message=f"El archivo origen no existe: {source}",
                operation="copy_file",
                path=str(source)
            )
        
        if not source_path.is_file():
            raise FileSystemError(
                message=f"La ruta origen no es un archivo: {source}",
                operation="copy_file",
                path=str(source)
            )
        
        if dest_path.exists() and not overwrite:
            raise FileSystemError(
                message=f"El archivo destino ya existe: {destination}",
                operation="copy_file",
                path=str(destination)
            )
        
        # Crear directorio destino si es necesario
        if dest_path.parent != dest_path:
            ensure_directory(dest_path.parent)
        
        shutil.copy2(source_path, dest_path)
        logger.debug(f"Archivo copiado: {source} -> {destination}")
    except FileSystemError:
        # Re-lanzar errores de sistema de archivos
        raise
    except (OSError, IOError, shutil.Error) as e:
        logger.error(f"Error al copiar archivo {source} -> {destination}: {e}")
        raise create_file_system_error(
            message=f"No se pudo copiar el archivo: {source} -> {destination}",
            operation="copy_file",
            path=f"{source} -> {destination}",
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al copiar archivo {source} -> {destination}: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al copiar archivo: {e}",
            operation="copy_file",
            path=f"{source} -> {destination}",
            original_error=e
        )


def move_file(source: PathLike, destination: PathLike, overwrite: bool = False) -> None:
    """
    Mueve un archivo de origen a destino.
    
    Args:
        source: Ruta del archivo origen.
        destination: Ruta del archivo destino.
        overwrite: Si sobrescribir el archivo destino si existe.
        
    Raises:
        FileSystemError: Si no se puede mover el archivo.
        ValidationError: Si las rutas son inválidas.
        
    Examples:
        >>> move_file('temp.txt', 'final.txt')
        >>> move_file('old/data.json', 'new/data.json', overwrite=True)
    """
    if not source or not destination:
        raise ValidationError(
            message="Las rutas de origen y destino no pueden estar vacías",
            field="paths",
            value=f"{source} -> {destination}"
        )
    
    try:
        source_path = Path(source)
        dest_path = Path(destination)
        
        if not source_path.exists():
            raise FileSystemError(
                message=f"El archivo origen no existe: {source}",
                operation="move_file",
                path=str(source)
            )
        
        if not source_path.is_file():
            raise FileSystemError(
                message=f"La ruta origen no es un archivo: {source}",
                operation="move_file",
                path=str(source)
            )
        
        if dest_path.exists() and not overwrite:
            raise FileSystemError(
                message=f"El archivo destino ya existe: {destination}",
                operation="move_file",
                path=str(destination)
            )
        
        # Crear directorio destino si es necesario
        if dest_path.parent != dest_path:
            ensure_directory(dest_path.parent)
        
        shutil.move(str(source_path), str(dest_path))
        logger.debug(f"Archivo movido: {source} -> {destination}")
    except FileSystemError:
        # Re-lanzar errores de sistema de archivos
        raise
    except (OSError, IOError, shutil.Error) as e:
        logger.error(f"Error al mover archivo {source} -> {destination}: {e}")
        raise create_file_system_error(
            message=f"No se pudo mover el archivo: {source} -> {destination}",
            operation="move_file",
            path=f"{source} -> {destination}",
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al mover archivo {source} -> {destination}: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al mover archivo: {e}",
            operation="move_file",
            path=f"{source} -> {destination}",
            original_error=e
        )


def delete_file(file_path: PathLike, missing_ok: bool = False) -> None:
    """
    Elimina un archivo.
    
    Args:
        file_path: Ruta del archivo a eliminar.
        missing_ok: Si no lanzar error si el archivo no existe.
        
    Raises:
        FileSystemError: Si no se puede eliminar el archivo.
        ValidationError: Si la ruta es inválida.
        
    Examples:
        >>> delete_file('temp.txt')
        >>> delete_file('maybe_exists.txt', missing_ok=True)
    """
    if not file_path:
        raise ValidationError(
            message="La ruta del archivo no puede estar vacía",
            field="file_path",
            value=file_path
        )
    
    try:
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            if missing_ok:
                logger.debug(f"Archivo no existe (ignorado): {file_path}")
                return
            else:
                raise FileSystemError(
                    message=f"El archivo no existe: {file_path}",
                    operation="delete_file",
                    path=str(file_path)
                )
        
        if not path_obj.is_file():
            raise FileSystemError(
                message=f"La ruta no es un archivo: {file_path}",
                operation="delete_file",
                path=str(file_path)
            )
        
        path_obj.unlink()
        logger.debug(f"Archivo eliminado: {file_path}")
    except FileSystemError:
        # Re-lanzar errores de sistema de archivos
        raise
    except (OSError, IOError) as e:
        logger.error(f"Error al eliminar archivo {file_path}: {e}")
        raise create_file_system_error(
            message=f"No se pudo eliminar el archivo: {file_path}",
            operation="delete_file",
            path=str(file_path),
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al eliminar archivo {file_path}: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al eliminar archivo: {e}",
            operation="delete_file",
            path=str(file_path),
            original_error=e
        )


def delete_directory(dir_path: PathLike, missing_ok: bool = False) -> None:
    """
    Elimina un directorio y todo su contenido.
    
    Args:
        dir_path: Ruta del directorio a eliminar.
        missing_ok: Si no lanzar error si el directorio no existe.
        
    Raises:
        FileSystemError: Si no se puede eliminar el directorio.
        ValidationError: Si la ruta es inválida.
        
    Examples:
        >>> delete_directory('temp_dir')
        >>> delete_directory('maybe_exists_dir', missing_ok=True)
    """
    if not dir_path:
        raise ValidationError(
            message="La ruta del directorio no puede estar vacía",
            field="dir_path",
            value=dir_path
        )
    
    try:
        path_obj = Path(dir_path)
        
        if not path_obj.exists():
            if missing_ok:
                logger.debug(f"Directorio no existe (ignorado): {dir_path}")
                return
            else:
                raise FileSystemError(
                    message=f"El directorio no existe: {dir_path}",
                    operation="delete_directory",
                    path=str(dir_path)
                )
        
        if not path_obj.is_dir():
            raise FileSystemError(
                message=f"La ruta no es un directorio: {dir_path}",
                operation="delete_directory",
                path=str(dir_path)
            )
        
        shutil.rmtree(path_obj)
        logger.debug(f"Directorio eliminado: {dir_path}")
    except FileSystemError:
        # Re-lanzar errores de sistema de archivos
        raise
    except (OSError, IOError, shutil.Error) as e:
        logger.error(f"Error al eliminar directorio {dir_path}: {e}")
        raise create_file_system_error(
            message=f"No se pudo eliminar el directorio: {dir_path}",
            operation="delete_directory",
            path=str(dir_path),
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al eliminar directorio {dir_path}: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al eliminar directorio: {e}",
            operation="delete_directory",
            path=str(dir_path),
            original_error=e
        )


def list_files(
    directory: PathLike,
    pattern: str = '*',
    recursive: bool = False,
    files_only: bool = True
) -> List[Path]:
    """
    Lista archivos en un directorio.
    
    Args:
        directory: Directorio a listar.
        pattern: Patrón de archivos a buscar (por defecto todos).
        recursive: Si buscar recursivamente en subdirectorios.
        files_only: Si incluir solo archivos (no directorios).
        
    Returns:
        List[Path]: Lista de rutas encontradas.
        
    Raises:
        FileSystemError: Si no se puede acceder al directorio.
        ValidationError: Si la ruta es inválida.
        
    Examples:
        >>> files = list_files('/tmp')
        >>> py_files = list_files('.', '*.py', recursive=True)
    """
    if not directory:
        raise ValidationError(
            message="La ruta del directorio no puede estar vacía",
            field="directory",
            value=directory
        )
    
    try:
        path_obj = Path(directory)
        
        if not path_obj.exists():
            raise FileSystemError(
                message=f"El directorio no existe: {directory}",
                operation="list_files",
                path=str(directory)
            )
        
        if not path_obj.is_dir():
            raise FileSystemError(
                message=f"La ruta no es un directorio: {directory}",
                operation="list_files",
                path=str(directory)
            )
        
        if recursive:
            paths = list(path_obj.rglob(pattern))
        else:
            paths = list(path_obj.glob(pattern))
        
        if files_only:
            paths = [p for p in paths if p.is_file()]
        
        logger.debug(f"Listados {len(paths)} elementos en {directory} (patrón: {pattern})")
        return sorted(paths)
    except FileSystemError:
        # Re-lanzar errores de sistema de archivos
        raise
    except (OSError, IOError) as e:
        logger.error(f"Error al listar directorio {directory}: {e}")
        raise create_file_system_error(
            message=f"No se pudo listar el directorio: {directory}",
            operation="list_files",
            path=str(directory),
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar directorio {directory}: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al listar directorio: {e}",
            operation="list_files",
            path=str(directory),
            original_error=e
        )


def get_file_info(file_path: PathLike) -> Dict[str, Any]:
    """
    Obtiene información detallada de un archivo.
    
    Args:
        file_path: Ruta del archivo.
        
    Returns:
        Dict[str, Any]: Información del archivo (tamaño, fechas, permisos, etc.).
        
    Raises:
        FileSystemError: Si no se puede acceder al archivo.
        ValidationError: Si la ruta es inválida.
        
    Examples:
        >>> info = get_file_info('document.pdf')
        >>> print(f"Tamaño: {info['size']} bytes")
    """
    if not file_path:
        raise ValidationError(
            message="La ruta del archivo no puede estar vacía",
            field="file_path",
            value=file_path
        )
    
    try:
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            raise FileSystemError(
                message=f"El archivo no existe: {file_path}",
                operation="get_file_info",
                path=str(file_path)
            )
        
        stat = path_obj.stat()
        
        info = {
            'path': str(path_obj.absolute()),
            'name': path_obj.name,
            'stem': path_obj.stem,
            'suffix': path_obj.suffix,
            'size': stat.st_size,
            'is_file': path_obj.is_file(),
            'is_dir': path_obj.is_dir(),
            'is_symlink': path_obj.is_symlink(),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'accessed': datetime.fromtimestamp(stat.st_atime),
            'permissions': oct(stat.st_mode)[-3:],
        }
        
        logger.debug(f"Información obtenida para: {file_path}")
        return info
    except FileSystemError:
        # Re-lanzar errores de sistema de archivos
        raise
    except (OSError, IOError) as e:
        logger.error(f"Error al obtener información de {file_path}: {e}")
        raise create_file_system_error(
            message=f"No se pudo obtener información del archivo: {file_path}",
            operation="get_file_info",
            path=str(file_path),
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al obtener información de {file_path}: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al obtener información: {e}",
            operation="get_file_info",
            path=str(file_path),
            original_error=e
        )


def create_temp_file(
    suffix: str = '',
    prefix: str = 'tmp',
    dir: Optional[PathLike] = None,
    text: bool = True
) -> Path:
    """
    Crea un archivo temporal.
    
    Args:
        suffix: Sufijo del archivo temporal.
        prefix: Prefijo del archivo temporal.
        dir: Directorio donde crear el archivo (por defecto temp del sistema).
        text: Si el archivo es de texto (afecta el modo de apertura).
        
    Returns:
        Path: Ruta del archivo temporal creado.
        
    Raises:
        FileSystemError: Si no se puede crear el archivo temporal.
        
    Examples:
        >>> temp_file = create_temp_file(suffix='.txt')
        >>> write_text_file(temp_file, 'Contenido temporal')
    """
    try:
        fd, temp_path = tempfile.mkstemp(
            suffix=suffix,
            prefix=prefix,
            dir=str(dir) if dir else None,
            text=text
        )
        
        # Cerrar el descriptor de archivo
        os.close(fd)
        
        path_obj = Path(temp_path)
        logger.debug(f"Archivo temporal creado: {path_obj}")
        return path_obj
    except (OSError, IOError) as e:
        logger.error(f"Error al crear archivo temporal: {e}")
        raise create_file_system_error(
            message=f"No se pudo crear archivo temporal: {e}",
            operation="create_temp_file",
            path="temp",
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al crear archivo temporal: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al crear archivo temporal: {e}",
            operation="create_temp_file",
            path="temp",
            original_error=e
        )


def create_temp_directory(prefix: str = 'tmpdir', dir: Optional[PathLike] = None) -> Path:
    """
    Crea un directorio temporal.
    
    Args:
        prefix: Prefijo del directorio temporal.
        dir: Directorio padre donde crear el directorio (por defecto temp del sistema).
        
    Returns:
        Path: Ruta del directorio temporal creado.
        
    Raises:
        FileSystemError: Si no se puede crear el directorio temporal.
        
    Examples:
        >>> temp_dir = create_temp_directory(prefix='myapp_')
        >>> ensure_directory(temp_dir / 'subdir')
    """
    try:
        temp_path = tempfile.mkdtemp(
            prefix=prefix,
            dir=str(dir) if dir else None
        )
        
        path_obj = Path(temp_path)
        logger.debug(f"Directorio temporal creado: {path_obj}")
        return path_obj
    except (OSError, IOError) as e:
        logger.error(f"Error al crear directorio temporal: {e}")
        raise create_file_system_error(
            message=f"No se pudo crear directorio temporal: {e}",
            operation="create_temp_directory",
            path="temp",
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al crear directorio temporal: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al crear directorio temporal: {e}",
            operation="create_temp_directory",
            path="temp",
            original_error=e
        )


def safe_filename(filename: str, replacement: str = '_') -> str:
    """
    Convierte un nombre de archivo en uno seguro para el sistema de archivos.
    
    Args:
        filename: Nombre de archivo original.
        replacement: Carácter de reemplazo para caracteres inválidos.
        
    Returns:
        str: Nombre de archivo seguro.
        
    Examples:
        >>> safe_filename('archivo con espacios.txt')
        'archivo_con_espacios.txt'
        >>> safe_filename('archivo/con\\caracteres:inválidos.txt')
        'archivo_con_caracteres_inválidos.txt'
    """
    if not filename:
        return 'unnamed'
    
    # Caracteres no permitidos en nombres de archivo
    invalid_chars = '<>:"/\\|?*'
    
    # Reemplazar caracteres inválidos
    safe_name = filename
    for char in invalid_chars:
        safe_name = safe_name.replace(char, replacement)
    
    # Reemplazar espacios múltiples y caracteres de control
    safe_name = ''.join(c if c.isprintable() and c != ' ' else replacement for c in safe_name)
    
    # Eliminar puntos al inicio y final
    safe_name = safe_name.strip('.')
    
    # Asegurar que no esté vacío
    if not safe_name:
        safe_name = 'unnamed'
    
    # Limitar longitud (255 es el límite común)
    if len(safe_name) > 255:
        name_part = safe_name[:200]
        ext_part = safe_name[-50:] if '.' in safe_name[-50:] else ''
        safe_name = name_part + ext_part
    
    logger.debug(f"Nombre de archivo sanitizado: '{filename}' -> '{safe_name}'")
    return safe_name


def file_exists(file_path: PathLike) -> bool:
    """
    Verifica si un archivo existe.
    
    Args:
        file_path: Ruta del archivo a verificar.
        
    Returns:
        bool: True si el archivo existe, False en caso contrario.
        
    Examples:
        >>> if file_exists('config.json'):
        ...     config = read_text_file('config.json')
    """
    try:
        return Path(file_path).is_file() if file_path else False
    except Exception:
        return False


def directory_exists(dir_path: PathLike) -> bool:
    """
    Verifica si un directorio existe.
    
    Args:
        dir_path: Ruta del directorio a verificar.
        
    Returns:
        bool: True si el directorio existe, False en caso contrario.
        
    Examples:
        >>> if directory_exists('logs'):
        ...     log_files = list_files('logs', '*.log')
    """
    try:
        return Path(dir_path).is_dir() if dir_path else False
    except Exception:
        return False


def get_file_size(file_path: PathLike) -> int:
    """
    Obtiene el tamaño de un archivo en bytes.
    
    Args:
        file_path: Ruta del archivo.
        
    Returns:
        int: Tamaño del archivo en bytes.
        
    Raises:
        FileSystemError: Si no se puede acceder al archivo.
        ValidationError: Si la ruta es inválida.
        
    Examples:
        >>> size = get_file_size('document.pdf')
        >>> print(f"El archivo tiene {size} bytes")
    """
    if not file_path:
        raise ValidationError(
            message="La ruta del archivo no puede estar vacía",
            field="file_path",
            value=file_path
        )
    
    try:
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            raise FileSystemError(
                message=f"El archivo no existe: {file_path}",
                operation="get_file_size",
                path=str(file_path)
            )
        
        if not path_obj.is_file():
            raise FileSystemError(
                message=f"La ruta no es un archivo: {file_path}",
                operation="get_file_size",
                path=str(file_path)
            )
        
        size = path_obj.stat().st_size
        logger.debug(f"Tamaño de archivo {file_path}: {size} bytes")
        return size
    except FileSystemError:
        # Re-lanzar errores de sistema de archivos
        raise
    except (OSError, IOError) as e:
        logger.error(f"Error al obtener tamaño de {file_path}: {e}")
        raise create_file_system_error(
            message=f"No se pudo obtener el tamaño del archivo: {file_path}",
            operation="get_file_size",
            path=str(file_path),
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al obtener tamaño de {file_path}: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al obtener tamaño: {e}",
            operation="get_file_size",
            path=str(file_path),
            original_error=e
        )


def read_lines(file_path: PathLike, encoding: str = 'utf-8') -> Generator[str, None, None]:
    """
    Lee un archivo línea por línea (generador para archivos grandes).
    
    Args:
        file_path: Ruta del archivo a leer.
        encoding: Codificación del archivo.
        
    Yields:
        str: Cada línea del archivo.
        
    Raises:
        FileSystemError: Si no se puede leer el archivo.
        ValidationError: Si la ruta es inválida.
        
    Examples:
        >>> for line in read_lines('large_file.txt'):
        ...     process_line(line)
    """
    if not file_path:
        raise ValidationError(
            message="La ruta del archivo no puede estar vacía",
            field="file_path",
            value=file_path
        )
    
    try:
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            raise FileSystemError(
                message=f"El archivo no existe: {file_path}",
                operation="read_lines",
                path=str(file_path)
            )
        
        if not path_obj.is_file():
            raise FileSystemError(
                message=f"La ruta no es un archivo: {file_path}",
                operation="read_lines",
                path=str(file_path)
            )
        
        with path_obj.open('r', encoding=encoding) as file:
            for line_num, line in enumerate(file, 1):
                yield line.rstrip('\n\r')
        
        logger.debug(f"Archivo leído línea por línea: {file_path}")
    except FileSystemError:
        # Re-lanzar errores de sistema de archivos
        raise
    except (OSError, IOError, UnicodeDecodeError) as e:
        logger.error(f"Error al leer líneas de {file_path}: {e}")
        raise create_file_system_error(
            message=f"No se pudo leer el archivo línea por línea: {file_path}",
            operation="read_lines",
            path=str(file_path),
            original_error=e
        )
    except Exception as e:
        logger.error(f"Error inesperado al leer líneas de {file_path}: {e}")
        raise create_file_system_error(
            message=f"Error inesperado al leer líneas: {e}",
            operation="read_lines",
            path=str(file_path),
            original_error=e
        )