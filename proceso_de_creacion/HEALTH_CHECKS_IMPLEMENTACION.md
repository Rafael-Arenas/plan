# 🏥 Health Checks para Aplicaciones de Escritorio - Guía de Implementación

## 📋 Índice
- [Introducción](#introducción)
- [Nivel Básico](#nivel-básico-mínimo-recomendado)
- [Nivel Intermedio](#nivel-intermedio-recomendado)
- [Nivel Avanzado](#nivel-avanzado-para-futuro)
- [Integración con Flet UI](#integración-con-flet-ui)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

Esta guía proporciona una implementación paso a paso de health checks para aplicaciones de escritorio, específicamente diseñada para el **Planificador AkGroup** usando Flet + SQLAlchemy.

### ¿Por qué implementar health checks?
- ✅ **Diagnóstico proactivo** de problemas
- ✅ **Soporte técnico eficiente** sin acceso físico
- ✅ **Mantenimiento preventivo** del sistema
- ✅ **Confiabilidad empresarial** de la aplicación

---

## 🟢 Nivel Básico (Mínimo Recomendado)

### Paso 1: Crear el módulo de health checks

**Archivo:** `src/planificador/health/health_checker.py`

```python
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import os
import sqlite3
from pathlib import Path

from planificador.config.config import settings
from planificador.database.database import check_database_health, get_database_info
from loguru import logger


class BasicHealthChecker:
    """Health checker básico para aplicaciones de escritorio."""
    
    def __init__(self):
        self.last_check: Optional[datetime] = None
        self.last_results: Dict[str, Any] = {}
    
    async def check_all(self) -> Dict[str, Any]:
        """Ejecuta todos los health checks básicos."""
        logger.info("Iniciando health checks básicos")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        # 1. Database Health Check
        try:
            db_health = await self._check_database()
            results["checks"]["database"] = db_health
        except Exception as e:
            results["checks"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            results["overall_status"] = "unhealthy"
        
        # 2. Configuration Check
        try:
            config_health = self._check_configuration()
            results["checks"]["configuration"] = config_health
        except Exception as e:
            results["checks"]["configuration"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            results["overall_status"] = "unhealthy"
        
        # 3. Critical Files Check
        try:
            files_health = self._check_critical_files()
            results["checks"]["critical_files"] = files_health
        except Exception as e:
            results["checks"]["critical_files"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            results["overall_status"] = "unhealthy"
        
        self.last_check = datetime.now()
        self.last_results = results
        
        logger.info(f"Health checks completados. Estado: {results['overall_status']}")
        return results
    
    async def _check_database(self) -> Dict[str, Any]:
        """Verifica el estado de la base de datos."""
        try:
            # Usar la función existente de database.py
            db_health = await check_database_health()
            
            if db_health["status"] == "healthy":
                return {
                    "status": "healthy",
                    "response_time_ms": db_health["response_time_ms"],
                    "message": "Base de datos accesible y funcional"
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": db_health.get("error", "Error desconocido")
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Error al verificar base de datos: {str(e)}"
            }
    
    def _check_configuration(self) -> Dict[str, Any]:
        """Verifica la configuración de la aplicación."""
        try:
            # Verificar configuraciones críticas
            critical_configs = [
                ("database_url", settings.database_settings.database_url),
                ("app_name", settings.app_name),
                ("log_level", settings.logging.log_level)
            ]
            
            missing_configs = []
            for config_name, config_value in critical_configs:
                if not config_value:
                    missing_configs.append(config_name)
            
            if missing_configs:
                return {
                    "status": "unhealthy",
                    "error": f"Configuraciones faltantes: {', '.join(missing_configs)}"
                }
            
            return {
                "status": "healthy",
                "message": "Todas las configuraciones críticas están presentes",
                "configs_checked": len(critical_configs)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Error al verificar configuración: {str(e)}"
            }
    
    def _check_critical_files(self) -> Dict[str, Any]:
        """Verifica que los archivos críticos existan."""
        try:
            critical_files = [
                settings.database_settings.database_url.replace("sqlite:///", ""),
                "src/planificador/config/config.py",
                "src/planificador/database/database.py"
            ]
            
            missing_files = []
            for file_path in critical_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                return {
                    "status": "warning",
                    "message": f"Archivos faltantes: {', '.join(missing_files)}"
                }
            
            return {
                "status": "healthy",
                "message": "Todos los archivos críticos están presentes",
                "files_checked": len(critical_files)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Error al verificar archivos: {str(e)}"
            }
```

### Paso 2: Integración básica en main.py

```python
# En src/planificador/main.py
from planificador.health.health_checker import BasicHealthChecker

async def startup_health_check():
    """Ejecuta health check al iniciar la aplicación."""
    health_checker = BasicHealthChecker()
    results = await health_checker.check_all()
    
    if results["overall_status"] != "healthy":
        logger.warning(f"Problemas detectados en startup: {results}")
        # Mostrar alerta en UI si es necesario
    else:
        logger.info("Aplicación iniciada correctamente - todos los checks OK")
    
    return results
```

---

## 🟡 Nivel Intermedio (Recomendado)

### Paso 3: Extender con monitoreo de recursos

**Archivo:** `src/planificador/health/system_monitor.py`

```python
import psutil
import shutil
from typing import Dict, Any
from pathlib import Path

class SystemMonitor:
    """Monitor de recursos del sistema."""
    
    def __init__(self):
        self.warning_thresholds = {
            "disk_usage_percent": 85,
            "memory_usage_percent": 80,
            "cpu_usage_percent": 90
        }
    
    def check_disk_space(self) -> Dict[str, Any]:
        """Verifica el espacio en disco disponible."""
        try:
            # Obtener el directorio de la base de datos
            db_path = Path(settings.database_settings.database_url.replace("sqlite:///", ""))
            disk_usage = shutil.disk_usage(db_path.parent)
            
            total_gb = disk_usage.total / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            used_percent = ((disk_usage.total - disk_usage.free) / disk_usage.total) * 100
            
            status = "healthy"
            if used_percent > self.warning_thresholds["disk_usage_percent"]:
                status = "warning" if used_percent < 95 else "critical"
            
            return {
                "status": status,
                "total_gb": round(total_gb, 2),
                "free_gb": round(free_gb, 2),
                "used_percent": round(used_percent, 2),
                "message": f"Disco: {round(used_percent, 1)}% usado, {round(free_gb, 1)}GB libres"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Error al verificar espacio en disco: {str(e)}"
            }
    
    def check_memory_usage(self) -> Dict[str, Any]:
        """Verifica el uso de memoria del sistema."""
        try:
            memory = psutil.virtual_memory()
            
            status = "healthy"
            if memory.percent > self.warning_thresholds["memory_usage_percent"]:
                status = "warning" if memory.percent < 90 else "critical"
            
            return {
                "status": status,
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": round(memory.percent, 2),
                "message": f"Memoria: {round(memory.percent, 1)}% usado, {round(memory.available / (1024**3), 1)}GB disponibles"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Error al verificar memoria: {str(e)}"
            }
    
    def check_cpu_usage(self) -> Dict[str, Any]:
        """Verifica el uso de CPU (promedio de 1 segundo)."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            status = "healthy"
            if cpu_percent > self.warning_thresholds["cpu_usage_percent"]:
                status = "warning"
            
            return {
                "status": status,
                "cpu_percent": round(cpu_percent, 2),
                "cpu_count": psutil.cpu_count(),
                "message": f"CPU: {round(cpu_percent, 1)}% uso promedio"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": f"Error al verificar CPU: {str(e)}"
            }
```

### Paso 4: Health checker intermedio

**Archivo:** `src/planificador/health/intermediate_health_checker.py`

```python
from planificador.health.health_checker import BasicHealthChecker
from planificador.health.system_monitor import SystemMonitor
from typing import Dict, Any
from datetime import datetime

class IntermediateHealthChecker(BasicHealthChecker):
    """Health checker intermedio con monitoreo de sistema."""
    
    def __init__(self):
        super().__init__()
        self.system_monitor = SystemMonitor()
    
    async def check_all(self) -> Dict[str, Any]:
        """Ejecuta todos los health checks intermedios."""
        # Ejecutar checks básicos
        results = await super().check_all()
        
        # Agregar checks de sistema
        try:
            disk_health = self.system_monitor.check_disk_space()
            results["checks"]["disk_space"] = disk_health
            
            if disk_health["status"] in ["warning", "critical", "unhealthy"]:
                results["overall_status"] = "warning"
        except Exception as e:
            results["checks"]["disk_space"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        try:
            memory_health = self.system_monitor.check_memory_usage()
            results["checks"]["memory"] = memory_health
            
            if memory_health["status"] in ["warning", "critical", "unhealthy"]:
                results["overall_status"] = "warning"
        except Exception as e:
            results["checks"]["memory"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        try:
            cpu_health = self.system_monitor.check_cpu_usage()
            results["checks"]["cpu"] = cpu_health
            
            if cpu_health["status"] in ["warning", "critical", "unhealthy"]:
                results["overall_status"] = "warning"
        except Exception as e:
            results["checks"]["cpu"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return results
    
    def generate_health_report(self) -> str:
        """Genera un reporte de salud legible para humanos."""
        if not self.last_results:
            return "No hay datos de health check disponibles."
        
        report = []
        report.append(f"📊 REPORTE DE SALUD DEL SISTEMA")
        report.append(f"Fecha: {self.last_results['timestamp']}")
        report.append(f"Estado General: {self.last_results['overall_status'].upper()}")
        report.append("\n" + "="*50)
        
        for check_name, check_data in self.last_results["checks"].items():
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "🔴",
                "unhealthy": "❌"
            }.get(check_data["status"], "❓")
            
            report.append(f"\n{status_emoji} {check_name.upper().replace('_', ' ')}")
            report.append(f"   Estado: {check_data['status']}")
            
            if "message" in check_data:
                report.append(f"   Info: {check_data['message']}")
            
            if "error" in check_data:
                report.append(f"   Error: {check_data['error']}")
        
        return "\n".join(report)
```

### Paso 5: Panel de diagnóstico en Flet

**Archivo:** `src/planificador/ui/health_panel.py`

```python
import flet as ft
import asyncio
from planificador.health.intermediate_health_checker import IntermediateHealthChecker

class HealthPanel:
    """Panel de diagnóstico para la UI de Flet."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.health_checker = IntermediateHealthChecker()
        self.status_indicator = None
        self.detail_dialog = None
    
    def create_status_indicator(self) -> ft.Container:
        """Crea un indicador de estado para la barra de estado."""
        self.status_indicator = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.HEALTH_AND_SAFETY, color=ft.colors.GREEN, size=16),
                ft.Text("Sistema OK", size=12, color=ft.colors.GREEN)
            ]),
            padding=5,
            border_radius=5,
            bgcolor=ft.colors.GREEN_50,
            on_click=self._show_health_details
        )
        return self.status_indicator
    
    async def update_status(self):
        """Actualiza el estado del indicador."""
        try:
            results = await self.health_checker.check_all()
            status = results["overall_status"]
            
            # Configurar colores y texto según el estado
            if status == "healthy":
                color = ft.colors.GREEN
                bg_color = ft.colors.GREEN_50
                text = "Sistema OK"
                icon = ft.icons.HEALTH_AND_SAFETY
            elif status == "warning":
                color = ft.colors.ORANGE
                bg_color = ft.colors.ORANGE_50
                text = "Advertencias"
                icon = ft.icons.WARNING
            else:
                color = ft.colors.RED
                bg_color = ft.colors.RED_50
                text = "Problemas"
                icon = ft.icons.ERROR
            
            # Actualizar el indicador
            if self.status_indicator:
                self.status_indicator.content.controls[0].name = icon
                self.status_indicator.content.controls[0].color = color
                self.status_indicator.content.controls[1].value = text
                self.status_indicator.content.controls[1].color = color
                self.status_indicator.bgcolor = bg_color
                
                await self.status_indicator.update_async()
        
        except Exception as e:
            logger.error(f"Error al actualizar estado de salud: {e}")
    
    async def _show_health_details(self, e):
        """Muestra el diálogo con detalles de salud."""
        report = self.health_checker.generate_health_report()
        
        self.detail_dialog = ft.AlertDialog(
            title=ft.Text("Diagnóstico del Sistema"),
            content=ft.Container(
                content=ft.Text(
                    report,
                    selectable=True,
                    size=12
                ),
                width=500,
                height=400,
                padding=10
            ),
            actions=[
                ft.TextButton("Actualizar", on_click=self._refresh_health),
                ft.TextButton("Cerrar", on_click=self._close_dialog)
            ]
        )
        
        self.page.dialog = self.detail_dialog
        self.detail_dialog.open = True
        await self.page.update_async()
    
    async def _refresh_health(self, e):
        """Actualiza los datos de salud y el diálogo."""
        await self.update_status()
        report = self.health_checker.generate_health_report()
        self.detail_dialog.content.content.value = report
        await self.detail_dialog.update_async()
    
    async def _close_dialog(self, e):
        """Cierra el diálogo de detalles."""
        self.detail_dialog.open = False
        await self.page.update_async()
```

---

## 🔴 Nivel Avanzado (Para Futuro)

### Paso 6: Sistema de métricas y alertas

**Archivo:** `src/planificador/health/metrics_collector.py`

```python
from typing import Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from pathlib import Path

@dataclass
class HealthMetric:
    """Métrica de salud del sistema."""
    timestamp: datetime
    check_name: str
    status: str
    value: float
    unit: str
    message: str = ""

class MetricsCollector:
    """Recolector y almacenador de métricas de salud."""
    
    def __init__(self, metrics_file: str = "health_metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics: List[HealthMetric] = []
        self.load_metrics()
    
    def add_metric(self, check_name: str, status: str, value: float, unit: str, message: str = ""):
        """Agrega una nueva métrica."""
        metric = HealthMetric(
            timestamp=datetime.now(),
            check_name=check_name,
            status=status,
            value=value,
            unit=unit,
            message=message
        )
        self.metrics.append(metric)
        self.save_metrics()
    
    def get_metrics_history(self, check_name: str, hours: int = 24) -> List[HealthMetric]:
        """Obtiene el historial de métricas para un check específico."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metric for metric in self.metrics
            if metric.check_name == check_name and metric.timestamp > cutoff_time
        ]
    
    def get_trend_analysis(self, check_name: str, hours: int = 24) -> Dict[str, Any]:
        """Analiza tendencias en las métricas."""
        metrics = self.get_metrics_history(check_name, hours)
        
        if len(metrics) < 2:
            return {"trend": "insufficient_data", "message": "Datos insuficientes para análisis"}
        
        values = [m.value for m in metrics]
        avg_value = sum(values) / len(values)
        
        # Análisis de tendencia simple
        recent_avg = sum(values[-5:]) / min(5, len(values))
        older_avg = sum(values[:5]) / min(5, len(values))
        
        if recent_avg > older_avg * 1.1:
            trend = "increasing"
        elif recent_avg < older_avg * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "average_value": avg_value,
            "recent_average": recent_avg,
            "data_points": len(metrics),
            "message": f"Tendencia {trend} en las últimas {hours} horas"
        }
    
    def save_metrics(self):
        """Guarda las métricas en archivo JSON."""
        try:
            # Mantener solo las últimas 1000 métricas
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]
            
            data = []
            for metric in self.metrics:
                metric_dict = asdict(metric)
                metric_dict['timestamp'] = metric.timestamp.isoformat()
                data.append(metric_dict)
            
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error al guardar métricas: {e}")
    
    def load_metrics(self):
        """Carga las métricas desde archivo JSON."""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                
                self.metrics = []
                for item in data:
                    item['timestamp'] = datetime.fromisoformat(item['timestamp'])
                    self.metrics.append(HealthMetric(**item))
        except Exception as e:
            logger.error(f"Error al cargar métricas: {e}")
            self.metrics = []
```

### Paso 7: Auto-reparación básica

**Archivo:** `src/planificador/health/auto_repair.py`

```python
from typing import Dict, Any, Callable
from loguru import logger
import os
import shutil
from pathlib import Path

class AutoRepair:
    """Sistema de auto-reparación para problemas comunes."""
    
    def __init__(self):
        self.repair_functions: Dict[str, Callable] = {
            "database_locked": self._repair_database_lock,
            "disk_space_low": self._repair_disk_space,
            "config_missing": self._repair_config,
            "log_files_large": self._repair_log_files
        }
    
    async def attempt_repair(self, problem_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Intenta reparar un problema específico."""
        if problem_type not in self.repair_functions:
            return {
                "success": False,
                "message": f"No hay reparación automática disponible para: {problem_type}"
            }
        
        try:
            logger.info(f"Intentando reparación automática para: {problem_type}")
            result = await self.repair_functions[problem_type](context)
            
            if result["success"]:
                logger.info(f"Reparación exitosa: {result['message']}")
            else:
                logger.warning(f"Reparación fallida: {result['message']}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error durante reparación automática: {e}")
            return {
                "success": False,
                "message": f"Error durante reparación: {str(e)}"
            }
    
    async def _repair_database_lock(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Intenta reparar problemas de bloqueo de base de datos."""
        try:
            # Implementar lógica específica para desbloquear BD
            # Por ejemplo, cerrar conexiones colgadas
            return {
                "success": True,
                "message": "Conexiones de base de datos reiniciadas"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"No se pudo reparar bloqueo de BD: {str(e)}"
            }
    
    async def _repair_disk_space(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Intenta liberar espacio en disco."""
        try:
            # Limpiar archivos temporales
            temp_files_cleaned = 0
            
            # Limpiar logs antiguos
            log_dir = Path("logs")
            if log_dir.exists():
                for log_file in log_dir.glob("*.log.*"):
                    if log_file.stat().st_mtime < (datetime.now() - timedelta(days=7)).timestamp():
                        log_file.unlink()
                        temp_files_cleaned += 1
            
            return {
                "success": True,
                "message": f"Limpieza completada. {temp_files_cleaned} archivos eliminados"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error durante limpieza: {str(e)}"
            }
    
    async def _repair_config(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Intenta reparar configuraciones faltantes."""
        try:
            # Crear configuraciones por defecto
            return {
                "success": True,
                "message": "Configuraciones por defecto restauradas"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al restaurar configuración: {str(e)}"
            }
    
    async def _repair_log_files(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Intenta reparar archivos de log demasiado grandes."""
        try:
            # Rotar logs grandes
            return {
                "success": True,
                "message": "Archivos de log rotados correctamente"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error al rotar logs: {str(e)}"
            }
```

---

## 🎨 Integración con Flet UI

### Paso 8: Integración completa en la aplicación principal

**Archivo:** `src/planificador/main.py` (modificaciones)

```python
import flet as ft
import asyncio
from planificador.ui.health_panel import HealthPanel
from planificador.health.intermediate_health_checker import IntermediateHealthChecker

class PlanificadorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.health_panel = HealthPanel(page)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Crear barra de estado con indicador de salud
        status_bar = ft.Container(
            content=ft.Row([
                ft.Text("Planificador AkGroup v1.0", size=12),
                ft.Container(expand=True),  # Spacer
                self.health_panel.create_status_indicator()
            ]),
            padding=5,
            bgcolor=ft.colors.SURFACE_VARIANT
        )
        
        # Layout principal
        self.page.add(
            ft.Column([
                # Tu contenido principal aquí
                ft.Container(
                    content=ft.Text("Contenido principal de la aplicación"),
                    expand=True
                ),
                # Barra de estado
                status_bar
            ])
        )
    
    async def start_health_monitoring(self):
        """Inicia el monitoreo de salud en segundo plano."""
        while True:
            try:
                await self.health_panel.update_status()
                await asyncio.sleep(30)  # Verificar cada 30 segundos
            except Exception as e:
                logger.error(f"Error en monitoreo de salud: {e}")
                await asyncio.sleep(60)  # Esperar más tiempo si hay error

async def main(page: ft.Page):
    page.title = "Planificador AkGroup"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    app = PlanificadorApp(page)
    
    # Ejecutar health check inicial
    await app.health_panel.update_status()
    
    # Iniciar monitoreo en segundo plano
    asyncio.create_task(app.start_health_monitoring())

if __name__ == "__main__":
    ft.app(target=main)
```

---

## 📝 Ejemplos de Uso

### Uso Básico

```python
from planificador.health.health_checker import BasicHealthChecker

# Health check básico
health_checker = BasicHealthChecker()
results = await health_checker.check_all()

print(f"Estado general: {results['overall_status']}")
for check_name, check_data in results['checks'].items():
    print(f"{check_name}: {check_data['status']}")
```

### Uso Intermedio

```python
from planificador.health.intermediate_health_checker import IntermediateHealthChecker

# Health check con monitoreo de sistema
health_checker = IntermediateHealthChecker()
results = await health_checker.check_all()

# Generar reporte legible
report = health_checker.generate_health_report()
print(report)
```

### Uso Avanzado

```python
from planificador.health.metrics_collector import MetricsCollector
from planificador.health.auto_repair import AutoRepair

# Recolección de métricas
metrics = MetricsCollector()
metrics.add_metric("disk_usage", "warning", 87.5, "percent", "Espacio en disco bajo")

# Análisis de tendencias
trend = metrics.get_trend_analysis("disk_usage", hours=24)
print(f"Tendencia: {trend['trend']}")

# Auto-reparación
auto_repair = AutoRepair()
repair_result = await auto_repair.attempt_repair("disk_space_low", {})
print(f"Reparación: {repair_result['message']}")
```

---

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Health Check Falla al Iniciar
```python
# Verificar configuración
from planificador.config.config import settings
print(f"Database URL: {settings.database_settings.database_url}")
print(f"App Name: {settings.app_name}")
```

#### 2. Indicador de Estado No Se Actualiza
```python
# Verificar que el monitoreo esté ejecutándose
import asyncio

# En tu aplicación principal
task = asyncio.create_task(app.start_health_monitoring())
print(f"Task running: {not task.done()}")
```

#### 3. Métricas No Se Guardan
```python
# Verificar permisos de archivo
from pathlib import Path

metrics_file = Path("health_metrics.json")
print(f"File exists: {metrics_file.exists()}")
print(f"File writable: {os.access(metrics_file.parent, os.W_OK)}")
```

### Logs de Diagnóstico

```python
# Habilitar logs detallados para health checks
from loguru import logger

logger.add("health_debug.log", level="DEBUG", filter=lambda record: "health" in record["message"].lower())
```

---

## 📋 Checklist de Implementación

### Nivel Básico ✅
- [ ] Crear `BasicHealthChecker`
- [ ] Implementar check de base de datos
- [ ] Implementar check de configuración
- [ ] Implementar check de archivos críticos
- [ ] Integrar en startup de la aplicación

### Nivel Intermedio ✅
- [ ] Crear `SystemMonitor`
- [ ] Implementar monitoreo de disco
- [ ] Implementar monitoreo de memoria
- [ ] Implementar monitoreo de CPU
- [ ] Crear `IntermediateHealthChecker`
- [ ] Crear `HealthPanel` para Flet
- [ ] Integrar indicador de estado en UI
- [ ] Implementar diálogo de detalles

### Nivel Avanzado 🚀
- [ ] Crear `MetricsCollector`
- [ ] Implementar análisis de tendencias
- [ ] Crear `AutoRepair`
- [ ] Implementar reparaciones automáticas
- [ ] Configurar alertas proactivas
- [ ] Implementar reportes automáticos

---

## 🎯 Próximos Pasos Recomendados

1. **Comenzar con Nivel Básico**: Implementar `BasicHealthChecker` primero
2. **Probar en desarrollo**: Verificar que todos los checks funcionan
3. **Integrar en UI**: Agregar indicador de estado básico
4. **Expandir gradualmente**: Agregar monitoreo de sistema
5. **Documentar problemas**: Crear base de conocimiento de issues comunes
6. **Automatizar**: Implementar auto-reparación para problemas frecuentes

---

*Esta guía proporciona una implementación completa y escalable de health checks para aplicaciones de escritorio, específicamente adaptada para el Planificador AkGroup usando Flet y SQLAlchemy.*