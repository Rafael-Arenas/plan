#!/usr/bin/env python3
# src/planificador/tests/unit/test_exceptions/run_tests.py

"""
Script para ejecutar tests del sistema de excepciones con coverage.

Este script proporciona una interfaz unificada para ejecutar todos los tests
del sistema de excepciones, generar reportes de coverage y validar que
todos los casos edge estén cubiertos.

Uso:
    python run_tests.py [opciones]
    
Ejemplos:
    python run_tests.py                    # Ejecutar todos los tests
    python run_tests.py --coverage         # Ejecutar con coverage
    python run_tests.py --html             # Generar reporte HTML
    python run_tests.py --verbose          # Modo verbose
    python run_tests.py --fast             # Solo tests rápidos
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional


def get_project_root() -> Path:
    """Obtiene la ruta raíz del proyecto."""
    current_path = Path(__file__).resolve()
    # Buscar hacia arriba hasta encontrar pyproject.toml
    for parent in current_path.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("No se pudo encontrar la raíz del proyecto (pyproject.toml)")


def run_command(command: List[str], cwd: Optional[Path] = None) -> int:
    """Ejecuta un comando y retorna el código de salida."""
    print(f"Ejecutando: {' '.join(command)}")
    if cwd:
        print(f"En directorio: {cwd}")
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=False
        )
        return result.returncode
    except FileNotFoundError as e:
        print(f"Error: Comando no encontrado: {e}")
        return 1
    except Exception as e:
        print(f"Error ejecutando comando: {e}")
        return 1


def run_tests_basic(project_root: Path, verbose: bool = False, fast: bool = False) -> int:
    """Ejecuta los tests básicos sin coverage."""
    test_dir = project_root / "src" / "planificador" / "tests" / "unit" / "test_exceptions"
    
    command = ["poetry", "run", "pytest"]
    
    if verbose:
        command.append("-v")
    else:
        command.append("-q")
    
    if fast:
        # Solo ejecutar tests que no sean de performance
        command.extend(["-k", "not performance"])
    
    # Agregar directorio de tests
    command.append(str(test_dir))
    
    # Configuración adicional
    command.extend([
        "--tb=short",  # Traceback corto
        "--strict-markers",  # Markers estrictos
        "--disable-warnings",  # Deshabilitar warnings
    ])
    
    return run_command(command, project_root)


def run_tests_with_coverage(
    project_root: Path, 
    html: bool = False, 
    verbose: bool = False,
    fast: bool = False
) -> int:
    """Ejecuta los tests con coverage."""
    test_dir = project_root / "src" / "planificador" / "tests" / "unit" / "test_exceptions"
    coverage_config = test_dir / ".coveragerc"
    
    # Comando base con coverage
    command = [
        "poetry", "run", "coverage", "run",
        f"--rcfile={coverage_config}",
        "-m", "pytest"
    ]
    
    if verbose:
        command.append("-v")
    else:
        command.append("-q")
    
    if fast:
        command.extend(["-k", "not performance"])
    
    # Agregar directorio de tests
    command.append(str(test_dir))
    
    # Configuración adicional
    command.extend([
        "--tb=short",
        "--strict-markers",
        "--disable-warnings",
    ])
    
    # Ejecutar tests con coverage
    exit_code = run_command(command, project_root)
    
    if exit_code != 0:
        print("\n❌ Los tests fallaron. No se generarán reportes de coverage.")
        return exit_code
    
    print("\n✅ Tests completados exitosamente. Generando reportes de coverage...")
    
    # Generar reporte de consola
    print("\n📊 Reporte de Coverage:")
    coverage_report_cmd = [
        "poetry", "run", "coverage", "report",
        f"--rcfile={coverage_config}",
        "--show-missing"
    ]
    run_command(coverage_report_cmd, project_root)
    
    # Generar reporte HTML si se solicita
    if html:
        print("\n🌐 Generando reporte HTML...")
        html_cmd = [
            "poetry", "run", "coverage", "html",
            f"--rcfile={coverage_config}"
        ]
        html_exit_code = run_command(html_cmd, project_root)
        
        if html_exit_code == 0:
            html_path = project_root / "htmlcov" / "index.html"
            print(f"\n✅ Reporte HTML generado en: {html_path}")
            print(f"   Abrir en navegador: file://{html_path.absolute()}")
        else:
            print("\n❌ Error generando reporte HTML")
    
    # Generar reporte XML para CI/CD
    xml_cmd = [
        "poetry", "run", "coverage", "xml",
        f"--rcfile={coverage_config}"
    ]
    run_command(xml_cmd, project_root)
    
    return exit_code


def validate_coverage_threshold(project_root: Path, threshold: float = 95.0) -> bool:
    """Valida que el coverage esté por encima del umbral especificado."""
    test_dir = project_root / "src" / "planificador" / "tests" / "unit" / "test_exceptions"
    coverage_config = test_dir / ".coveragerc"
    
    # Obtener porcentaje de coverage
    command = [
        "poetry", "run", "coverage", "report",
        f"--rcfile={coverage_config}",
        "--format=total"
    ]
    
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            coverage_percentage = float(result.stdout.strip())
            print(f"\n📈 Coverage actual: {coverage_percentage:.2f}%")
            print(f"📋 Umbral requerido: {threshold:.2f}%")
            
            if coverage_percentage >= threshold:
                print(f"✅ Coverage satisfactorio ({coverage_percentage:.2f}% >= {threshold:.2f}%)")
                return True
            else:
                print(f"❌ Coverage insuficiente ({coverage_percentage:.2f}% < {threshold:.2f}%)")
                return False
        else:
            print(f"❌ Error obteniendo coverage: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error validando coverage: {e}")
        return False


def check_dependencies(project_root: Path) -> bool:
    """Verifica que las dependencias necesarias estén instaladas."""
    print("🔍 Verificando dependencias...")
    
    required_packages = ["pytest", "coverage"]
    
    for package in required_packages:
        check_cmd = ["poetry", "run", "python", "-c", f"import {package}"]
        result = run_command(check_cmd, project_root)
        
        if result != 0:
            print(f"❌ Dependencia faltante: {package}")
            print(f"   Instalar con: poetry add --group dev {package}")
            return False
    
    print("✅ Todas las dependencias están disponibles")
    return True


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Ejecutar tests del sistema de excepciones",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_tests.py                    # Tests básicos
  python run_tests.py --coverage         # Tests con coverage
  python run_tests.py --coverage --html  # Tests con coverage y reporte HTML
  python run_tests.py --verbose          # Tests con output detallado
  python run_tests.py --fast             # Solo tests rápidos
  python run_tests.py --threshold 90     # Validar coverage mínimo del 90%
        """
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Ejecutar tests con análisis de coverage"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generar reporte HTML de coverage (requiere --coverage)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Output detallado de los tests"
    )
    
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Ejecutar solo tests rápidos (excluir tests de performance)"
    )
    
    parser.add_argument(
        "--threshold",
        type=float,
        default=95.0,
        help="Umbral mínimo de coverage requerido (default: 95.0)"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Solo verificar dependencias sin ejecutar tests"
    )
    
    args = parser.parse_args()
    
    try:
        project_root = get_project_root()
        print(f"📁 Proyecto encontrado en: {project_root}")
        
        # Verificar dependencias
        if not check_dependencies(project_root):
            return 1
        
        if args.check_deps:
            print("✅ Verificación de dependencias completada")
            return 0
        
        # Ejecutar tests
        if args.coverage:
            exit_code = run_tests_with_coverage(
                project_root, 
                html=args.html, 
                verbose=args.verbose,
                fast=args.fast
            )
            
            if exit_code == 0 and args.threshold > 0:
                if not validate_coverage_threshold(project_root, args.threshold):
                    return 1
        else:
            if args.html:
                print("⚠️  Opción --html ignorada (requiere --coverage)")
            
            exit_code = run_tests_basic(
                project_root, 
                verbose=args.verbose,
                fast=args.fast
            )
        
        if exit_code == 0:
            print("\n🎉 Todos los tests completados exitosamente!")
        else:
            print("\n💥 Algunos tests fallaron")
        
        return exit_code
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())