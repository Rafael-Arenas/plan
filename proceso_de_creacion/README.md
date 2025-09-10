# 📋 Planificador AkGroup

> Sistema integral de planificación de equipos y proyectos desarrollado con Flet y Python 3.11+

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Poetry](https://img.shields.io/badge/Poetry-Dependency%20Management-blue.svg)](https://python-poetry.org/)
[![Flet](https://img.shields.io/badge/Flet-UI%20Framework-green.svg)](https://flet.dev)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red.svg)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Descripción

El **Planificador AkGroup** es una aplicación de escritorio multiplataforma diseñada para optimizar la gestión de equipos, proyectos y recursos en organizaciones. Proporciona una interfaz intuitiva para la planificación visual, seguimiento de progreso y análisis de productividad.

### ✨ Características Principales

- 🗓️ **Planificación Visual**: Calendario interactivo con vista Gantt
- 👥 **Gestión de Equipos**: Organización de empleados y asignaciones
- 📊 **Proyectos y Clientes**: Control completo del ciclo de vida
- 🏖️ **Gestión de Vacaciones**: Planificación y aprobación automatizada
- ⚡ **Detección de Conflictos**: Alertas inteligentes en tiempo real
- 📈 **Reportes y Analytics**: Métricas de productividad y rendimiento
- 🔍 **Auditoría Completa**: Trazabilidad de todos los cambios
- 🎨 **Interfaz Moderna**: Diseño responsivo y accesible

## 🚀 Instalación Rápida

### Prerrequisitos

- **Python 3.11+** ([Descargar](https://python.org/downloads/))
- **Poetry** ([Instalar Poetry](https://python-poetry.org/docs/#installation))
- **Git** ([Descargar Git](https://git-scm.com/downloads))

### 1. Clonar el Repositorio

```bash
git clone https://github.com/akgroup/planificador.git
cd planificador
```

### 2. Instalar Dependencias

```bash
# Instalar dependencias del proyecto
poetry install

# Activar el entorno virtual
poetry shell
```

### 3. Configurar el Entorno

```bash
# Copiar archivo de configuración
cp .env.example .env

# Editar configuración (opcional)
nano .env  # o tu editor preferido
```

### 4. Inicializar la Base de Datos

```bash
# Ejecutar migraciones
poetry run alembic upgrade head

# Configuración inicial (opcional)
poetry run setup-db
```

### 5. Ejecutar la Aplicación

```bash
# Modo desarrollo
poetry run python main.py

# O usando el script configurado
poetry run planificador
```

## 🛠️ Desarrollo

### Comandos de Desarrollo

```bash
# Instalar dependencias de desarrollo
poetry install --with dev

# Ejecutar tests
poetry run pytest

# Tests con cobertura
poetry run pytest --cov=src --cov-report=html

# Linting y formateo
poetry run ruff check src/
poetry run ruff format src/

# Type checking
poetry run mypy src/
```

## 📚 Documentación

- **Arquitectura Completa**: Ver [PLANTEAMIENTO_APLICACION_FLET.md](PLANTEAMIENTO_APLICACION_FLET.md)
- **Configuración**: Ver archivo [.env.example](.env.example)
- **API Reference**: Generar con `poetry run mkdocs serve`

## 🤝 Contribución

1. Fork el repositorio
2. Crear rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Añadir nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.