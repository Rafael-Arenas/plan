"""Utilidades de logging específicas para testing."""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger


class TestLogger:
    """Configurador de logging para entorno de testing.
    
    Proporciona configuración específica de loguru para tests,
    incluyendo captura de logs y diferentes niveles de verbosidad.
    """
    
    def __init__(self):
        self.captured_logs: list[str] = []
        self.handler_id: Optional[int] = None
    
    def setup_test_logging(
        self,
        level: str = "DEBUG",
        capture: bool = True,
        file_output: bool = False,
        test_name: Optional[str] = None
    ) -> None:
        """Configura logging para testing.
        
        Args:
            level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            capture: Si capturar logs en memoria para assertions
            file_output: Si escribir logs a archivo
            test_name: Nombre del test para el archivo de log
        """
        # Remover handlers existentes
        logger.remove()
        
        # Configurar formato para testing
        test_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # Handler para captura en memoria
        if capture:
            self.handler_id = logger.add(
                sink=self._capture_log,
                level=level,
                format=test_format,
                backtrace=True,
                diagnose=True,
            )
        
        # Handler para consola (solo en modo verbose)
        if level == "DEBUG":
            logger.add(
                sink=sys.stderr,
                level=level,
                format=test_format,
                backtrace=True,
                diagnose=True,
            )
        
        # Handler para archivo (opcional)
        if file_output and test_name:
            log_file = Path("logs") / "tests" / f"{test_name}.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            logger.add(
                sink=str(log_file),
                level=level,
                format=test_format,
                rotation="10 MB",
                retention="1 week",
                backtrace=True,
                diagnose=True,
            )
    
    def _capture_log(self, message: str) -> None:
        """Captura logs en memoria para testing.
        
        Args:
            message: Mensaje de log a capturar
        """
        self.captured_logs.append(message.rstrip())
    
    def get_captured_logs(self, level: Optional[str] = None) -> list[str]:
        """Obtiene logs capturados, opcionalmente filtrados por nivel.
        
        Args:
            level: Nivel de log a filtrar (opcional)
            
        Returns:
            list[str]: Lista de logs capturados
        """
        if level is None:
            return self.captured_logs.copy()
        
        return [
            log for log in self.captured_logs
            if f"| {level.upper()} |" in log
        ]
    
    def clear_captured_logs(self) -> None:
        """Limpia los logs capturados."""
        self.captured_logs.clear()
    
    def assert_log_contains(
        self,
        message: str,
        level: Optional[str] = None,
        count: Optional[int] = None
    ) -> None:
        """Verifica que los logs contengan un mensaje específico.
        
        Args:
            message: Mensaje a buscar en los logs
            level: Nivel de log específico (opcional)
            count: Número esperado de ocurrencias (opcional)
            
        Raises:
            AssertionError: Si el mensaje no se encuentra o el count no coincide
        """
        logs = self.get_captured_logs(level)
        matching_logs = [log for log in logs if message in log]
        
        if count is not None:
            assert len(matching_logs) == count, (
                f"Expected {count} logs containing '{message}', "
                f"but found {len(matching_logs)}"
            )
        else:
            assert matching_logs, (
                f"No logs found containing '{message}'. "
                f"Available logs: {logs}"
            )
    
    def assert_no_errors(self) -> None:
        """Verifica que no haya logs de error.
        
        Raises:
            AssertionError: Si se encuentran logs de ERROR o CRITICAL
        """
        error_logs = self.get_captured_logs("ERROR")
        critical_logs = self.get_captured_logs("CRITICAL")
        
        all_error_logs = error_logs + critical_logs
        
        assert not all_error_logs, (
            f"Found unexpected error logs: {all_error_logs}"
        )
    
    def cleanup(self) -> None:
        """Limpia la configuración de logging."""
        if self.handler_id is not None:
            logger.remove(self.handler_id)
            self.handler_id = None
        
        self.clear_captured_logs()


# Instancia global para uso en tests
test_logger = TestLogger()


def setup_test_logging(
    level: str = "DEBUG",
    capture: bool = True,
    file_output: bool = False,
    test_name: Optional[str] = None
) -> TestLogger:
    """Función de conveniencia para configurar logging en tests.
    
    Args:
        level: Nivel de logging
        capture: Si capturar logs
        file_output: Si escribir a archivo
        test_name: Nombre del test
        
    Returns:
        TestLogger: Instancia configurada del logger de testing
    """
    test_logger.setup_test_logging(
        level=level,
        capture=capture,
        file_output=file_output,
        test_name=test_name
    )
    return test_logger


def cleanup_test_logging() -> None:
    """Función de conveniencia para limpiar logging después de tests."""
    test_logger.cleanup()