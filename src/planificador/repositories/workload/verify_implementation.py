# src/planificador/repositories/workload/verify_implementation.py

"""
Script de Verificación de Implementación del Repositorio Workload.

Este script verifica que todas las 69 funciones documentadas en 
workload_available_functions.md estén correctamente implementadas
en los módulos correspondientes del repositorio Workload.

Funcionalidades:
    - Verificación de existencia de métodos en cada módulo
    - Validación de firmas de métodos (parámetros y tipos)
    - Verificación de documentación (docstrings)
    - Reporte detallado de funciones faltantes o incorrectas
    - Análisis de cobertura de implementación

Uso:
    ```python
    from planificador.repositories.workload.verify_implementation import (
        verify_workload_implementation
    )
    
    # Verificar toda la implementación
    report = verify_workload_implementation()
    print(report)
    
    # Verificar módulo específico
    report = verify_module_implementation("WorkloadCrudModule")
    print(report)
    ```

Autor: Planificador Development Team
Fecha: 2024-01-19
"""

import inspect
from typing import Dict, List, Any, Optional, Callable, Type
from pathlib import Path
import importlib.util
from loguru import logger

# Configurar path para imports absolutos
import sys
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

# Importar módulos a verificar
try:
    from planificador.repositories.workload.modules.crud_module import WorkloadCrudModule
    from planificador.repositories.workload.modules.query_module import WorkloadQueryModule
    from planificador.repositories.workload.modules.validation_module import WorkloadValidationModule
    from planificador.repositories.workload.modules.statistics_module import WorkloadStatisticsModule
    from planificador.repositories.workload.modules.relationship_module import WorkloadRelationshipModule
    from planificador.repositories.workload.workload_repository_facade import WorkloadRepositoryFacade
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    raise


class WorkloadImplementationVerifier:
    """
    Verificador de implementación del repositorio Workload.
    
    Valida que todas las funciones documentadas estén correctamente
    implementadas en los módulos correspondientes.
    """
    
    def __init__(self):
        """Inicializa el verificador con las definiciones esperadas."""
        self.expected_functions = self._load_expected_functions()
        self.modules_to_verify = {
            'WorkloadCrudModule': WorkloadCrudModule,
            'WorkloadQueryModule': WorkloadQueryModule,
            'WorkloadValidationModule': WorkloadValidationModule,
            'WorkloadStatisticsModule': WorkloadStatisticsModule,
            'WorkloadRelationshipModule': WorkloadRelationshipModule,
            'WorkloadRepositoryFacade': WorkloadRepositoryFacade
        }
    
    def _load_expected_functions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Carga las funciones esperadas basadas en la documentación.
        
        Returns:
            Dict con las funciones esperadas por módulo
        """
        return {
            'WorkloadCrudModule': [
                {
                    'name': 'create_workload',
                    'params': ['workload_data'],
                    'return_type': 'Workload',
                    'description': 'Crea una nueva carga de trabajo'
                },
                {
                    'name': 'update_workload',
                    'params': ['workload_id', 'update_data'],
                    'return_type': 'Workload',
                    'description': 'Actualiza una carga de trabajo existente'
                },
                {
                    'name': 'delete_workload',
                    'params': ['workload_id'],
                    'return_type': 'bool',
                    'description': 'Elimina una carga de trabajo'
                },
                {
                    'name': 'get_workload_by_id',
                    'params': ['workload_id'],
                    'return_type': 'Optional[Workload]',
                    'description': 'Obtiene una carga de trabajo por ID'
                },
                {
                    'name': 'get_by_unique_field',
                    'params': ['field_name', 'field_value'],
                    'return_type': 'Optional[Workload]',
                    'description': 'Obtiene carga por campo único'
                },
                # Alias para compatibilidad
                {
                    'name': 'add_workload',
                    'params': ['workload_data'],
                    'return_type': 'Workload',
                    'description': 'Alias para create_workload'
                },
                {
                    'name': 'find_workload_by_id',
                    'params': ['workload_id'],
                    'return_type': 'Optional[Workload]',
                    'description': 'Alias para get_workload_by_id'
                },
                {
                    'name': 'modify_workload',
                    'params': ['workload_id', 'update_data'],
                    'return_type': 'Workload',
                    'description': 'Alias para update_workload'
                },
                {
                    'name': 'remove_workload',
                    'params': ['workload_id'],
                    'return_type': 'bool',
                    'description': 'Alias para delete_workload'
                }
            ],
            'WorkloadQueryModule': [
                {
                    'name': 'get_workload_by_id',
                    'params': ['workload_id'],
                    'return_type': 'Optional[Workload]',
                    'description': 'Obtiene carga por ID'
                },
                {
                    'name': 'get_workloads_by_employee',
                    'params': ['employee_id', 'start_date', 'end_date'],
                    'return_type': 'List[Workload]',
                    'description': 'Obtiene cargas por empleado'
                },
                {
                    'name': 'get_workloads_by_project',
                    'params': ['project_id', 'start_date', 'end_date'],
                    'return_type': 'List[Workload]',
                    'description': 'Obtiene cargas por proyecto'
                },
                {
                    'name': 'get_workloads_by_date_range',
                    'params': ['start_date', 'end_date'],
                    'return_type': 'List[Workload]',
                    'description': 'Obtiene cargas por rango de fechas'
                },
                {
                    'name': 'search_workloads_by_criteria',
                    'params': ['criteria'],
                    'return_type': 'List[Workload]',
                    'description': 'Busca cargas por criterios'
                },
                {
                    'name': 'get_workloads_by_status',
                    'params': ['status', 'start_date', 'end_date'],
                    'return_type': 'List[Workload]',
                    'description': 'Obtiene cargas por estado'
                },
                {
                    'name': 'count_workloads',
                    'params': ['criteria'],
                    'return_type': 'int',
                    'description': 'Cuenta cargas por criterios'
                },
                {
                    'name': 'get_overloaded_employees',
                    'params': ['target_date', 'threshold_hours'],
                    'return_type': 'List[Dict[str, Any]]',
                    'description': 'Obtiene empleados sobrecargados'
                },
                {
                    'name': 'get_underutilized_employees',
                    'params': ['target_date', 'threshold_hours'],
                    'return_type': 'List[Dict[str, Any]]',
                    'description': 'Obtiene empleados subutilizados'
                }
            ],
            'WorkloadValidationModule': [
                {
                    'name': 'validate_workload_data',
                    'params': ['workload_data'],
                    'return_type': 'bool',
                    'description': 'Valida datos de carga de trabajo'
                },
                {
                    'name': 'validate_hours',
                    'params': ['hours'],
                    'return_type': 'bool',
                    'description': 'Valida horas de trabajo'
                },
                {
                    'name': 'validate_workload_status',
                    'params': ['status'],
                    'return_type': 'bool',
                    'description': 'Valida estado de carga'
                },
                {
                    'name': 'validate_description',
                    'params': ['description'],
                    'return_type': 'bool',
                    'description': 'Valida descripción'
                },
                {
                    'name': 'validate_date_range',
                    'params': ['start_date', 'end_date'],
                    'return_type': 'bool',
                    'description': 'Valida rango de fechas'
                },
                {
                    'name': 'check_duplicate_workload',
                    'params': ['employee_id', 'work_date', 'exclude_id'],
                    'return_type': 'bool',
                    'description': 'Verifica duplicados'
                },
                {
                    'name': 'validate_employee_daily_hours',
                    'params': ['employee_id', 'work_date', 'hours', 'exclude_id'],
                    'return_type': 'bool',
                    'description': 'Valida horas diarias del empleado'
                },
                {
                    'name': 'validate_workload_consistency',
                    'params': ['workload_data'],
                    'return_type': 'bool',
                    'description': 'Valida consistencia de datos'
                }
            ],
            'WorkloadStatisticsModule': [
                {
                    'name': 'get_employee_workload_statistics',
                    'params': ['employee_id', 'start_date', 'end_date'],
                    'return_type': 'Dict[str, Any]',
                    'description': 'Estadísticas por empleado'
                },
                {
                    'name': 'get_project_workload_statistics',
                    'params': ['project_id', 'start_date', 'end_date'],
                    'return_type': 'Dict[str, Any]',
                    'description': 'Estadísticas por proyecto'
                },
                {
                    'name': 'get_team_workload_statistics',
                    'params': ['team_id', 'start_date', 'end_date'],
                    'return_type': 'Dict[str, Any]',
                    'description': 'Estadísticas por equipo'
                },
                {
                    'name': 'analyze_workload_trends',
                    'params': ['employee_id', 'start_date', 'end_date'],
                    'return_type': 'Dict[str, Any]',
                    'description': 'Análisis de tendencias'
                },
                {
                    'name': 'get_workload_distribution',
                    'params': ['start_date', 'end_date'],
                    'return_type': 'Dict[str, Any]',
                    'description': 'Distribución de cargas'
                },
                {
                    'name': 'calculate_productivity_metrics',
                    'params': ['employee_id', 'start_date', 'end_date'],
                    'return_type': 'Dict[str, Any]',
                    'description': 'Métricas de productividad'
                }
            ],
            'WorkloadRelationshipModule': [
                {
                    'name': 'associate_employee_workload',
                    'params': ['workload_id', 'employee_id'],
                    'return_type': 'bool',
                    'description': 'Asocia empleado con carga'
                },
                {
                    'name': 'associate_project_workload',
                    'params': ['workload_id', 'project_id'],
                    'return_type': 'bool',
                    'description': 'Asocia proyecto con carga'
                },
                {
                    'name': 'associate_team_workload',
                    'params': ['workload_id', 'team_id'],
                    'return_type': 'bool',
                    'description': 'Asocia equipo con carga'
                },
                {
                    'name': 'validate_employee_project_relationship',
                    'params': ['employee_id', 'project_id'],
                    'return_type': 'bool',
                    'description': 'Valida relación empleado-proyecto'
                },
                {
                    'name': 'validate_team_member_relationship',
                    'params': ['employee_id', 'team_id'],
                    'return_type': 'bool',
                    'description': 'Valida relación empleado-equipo'
                },
                {
                    'name': 'analyze_workload_dependencies',
                    'params': ['workload_id'],
                    'return_type': 'Dict[str, Any]',
                    'description': 'Analiza dependencias de carga'
                }
            ],
            'WorkloadRepositoryFacade': [
                # Métodos CRUD
                {
                    'name': 'create_workload',
                    'params': ['workload_data'],
                    'return_type': 'Workload',
                    'description': 'Crea carga de trabajo'
                },
                {
                    'name': 'create_workload_with_validation',
                    'params': ['workload_data'],
                    'return_type': 'Workload',
                    'description': 'Crea carga con validación'
                },
                {
                    'name': 'get_workload_by_id',
                    'params': ['workload_id'],
                    'return_type': 'Optional[Workload]',
                    'description': 'Obtiene carga por ID'
                },
                {
                    'name': 'update_workload',
                    'params': ['workload_id', 'update_data'],
                    'return_type': 'Workload',
                    'description': 'Actualiza carga'
                },
                {
                    'name': 'delete_workload',
                    'params': ['workload_id'],
                    'return_type': 'bool',
                    'description': 'Elimina carga'
                },
                # Métodos de consulta
                {
                    'name': 'get_workloads_by_employee',
                    'params': ['employee_id', 'start_date', 'end_date'],
                    'return_type': 'List[Workload]',
                    'description': 'Obtiene cargas por empleado'
                },
                {
                    'name': 'get_workloads_by_project',
                    'params': ['project_id', 'start_date', 'end_date'],
                    'return_type': 'List[Workload]',
                    'description': 'Obtiene cargas por proyecto'
                },
                # Métodos estadísticos
                {
                    'name': 'get_employee_workload_statistics',
                    'params': ['employee_id', 'start_date', 'end_date'],
                    'return_type': 'Dict[str, Any]',
                    'description': 'Estadísticas por empleado'
                },
                {
                    'name': 'get_workload_dashboard_data',
                    'params': ['employee_id', 'start_date', 'end_date'],
                    'return_type': 'Dict[str, Any]',
                    'description': 'Datos del dashboard'
                }
            ]
        }
    
    def verify_module_implementation(self, module_name: str) -> Dict[str, Any]:
        """
        Verifica la implementación de un módulo específico.
        
        Args:
            module_name: Nombre del módulo a verificar
            
        Returns:
            Dict con el reporte de verificación
        """
        if module_name not in self.modules_to_verify:
            return {
                'module': module_name,
                'status': 'error',
                'message': f'Módulo {module_name} no encontrado'
            }
        
        module_class = self.modules_to_verify[module_name]
        expected_functions = self.expected_functions.get(module_name, [])
        
        # Obtener métodos implementados
        implemented_methods = [
            method for method in dir(module_class)
            if not method.startswith('_') and callable(getattr(module_class, method))
        ]
        
        # Verificar cada función esperada
        missing_functions = []
        implemented_functions = []
        incorrect_signatures = []
        
        for expected_func in expected_functions:
            func_name = expected_func['name']
            
            if func_name in implemented_methods:
                # Verificar firma del método
                method = getattr(module_class, func_name)
                signature = inspect.signature(method)
                
                # Verificar parámetros (excluyendo 'self')
                actual_params = list(signature.parameters.keys())[1:]  # Excluir 'self'
                expected_params = expected_func['params']
                
                if len(actual_params) >= len(expected_params):
                    implemented_functions.append({
                        'name': func_name,
                        'status': 'implemented',
                        'signature': str(signature),
                        'description': expected_func['description']
                    })
                else:
                    incorrect_signatures.append({
                        'name': func_name,
                        'expected_params': expected_params,
                        'actual_params': actual_params,
                        'signature': str(signature)
                    })
            else:
                missing_functions.append({
                    'name': func_name,
                    'expected_params': expected_func['params'],
                    'return_type': expected_func['return_type'],
                    'description': expected_func['description']
                })
        
        # Calcular estadísticas
        total_expected = len(expected_functions)
        total_implemented = len(implemented_functions)
        coverage_percentage = (total_implemented / total_expected * 100) if total_expected > 0 else 0
        
        return {
            'module': module_name,
            'status': 'success' if not missing_functions and not incorrect_signatures else 'partial',
            'coverage_percentage': coverage_percentage,
            'total_expected': total_expected,
            'total_implemented': total_implemented,
            'implemented_functions': implemented_functions,
            'missing_functions': missing_functions,
            'incorrect_signatures': incorrect_signatures,
            'all_methods': implemented_methods
        }
    
    def verify_all_modules(self) -> Dict[str, Any]:
        """
        Verifica la implementación de todos los módulos.
        
        Returns:
            Dict con el reporte completo de verificación
        """
        module_reports = {}
        total_functions = 0
        total_implemented = 0
        
        for module_name in self.modules_to_verify.keys():
            report = self.verify_module_implementation(module_name)
            module_reports[module_name] = report
            
            total_functions += report.get('total_expected', 0)
            total_implemented += report.get('total_implemented', 0)
        
        overall_coverage = (total_implemented / total_functions * 100) if total_functions > 0 else 0
        
        return {
            'overall_status': 'success' if overall_coverage >= 95 else 'partial',
            'overall_coverage_percentage': overall_coverage,
            'total_expected_functions': total_functions,
            'total_implemented_functions': total_implemented,
            'module_reports': module_reports,
            'summary': {
                'fully_implemented': [
                    name for name, report in module_reports.items()
                    if report.get('coverage_percentage', 0) == 100
                ],
                'partially_implemented': [
                    name for name, report in module_reports.items()
                    if 0 < report.get('coverage_percentage', 0) < 100
                ],
                'not_implemented': [
                    name for name, report in module_reports.items()
                    if report.get('coverage_percentage', 0) == 0
                ]
            }
        }
    
    def generate_implementation_report(self) -> str:
        """
        Genera un reporte legible de la verificación de implementación.
        
        Returns:
            String con el reporte formateado
        """
        verification_result = self.verify_all_modules()
        
        report_lines = [
            "=" * 80,
            "REPORTE DE VERIFICACIÓN DE IMPLEMENTACIÓN - REPOSITORIO WORKLOAD",
            "=" * 80,
            "",
            f"📊 RESUMEN GENERAL:",
            f"   • Estado: {verification_result['overall_status'].upper()}",
            f"   • Cobertura: {verification_result['overall_coverage_percentage']:.1f}%",
            f"   • Funciones esperadas: {verification_result['total_expected_functions']}",
            f"   • Funciones implementadas: {verification_result['total_implemented_functions']}",
            "",
            "📋 ESTADO POR MÓDULOS:",
        ]
        
        for module_name, report in verification_result['module_reports'].items():
            status_icon = "✅" if report['coverage_percentage'] == 100 else "⚠️" if report['coverage_percentage'] > 0 else "❌"
            report_lines.extend([
                f"   {status_icon} {module_name}:",
                f"      - Cobertura: {report['coverage_percentage']:.1f}%",
                f"      - Implementadas: {report['total_implemented']}/{report['total_expected']}",
            ])
            
            if report.get('missing_functions'):
                report_lines.append(f"      - Faltantes: {len(report['missing_functions'])}")
            
            if report.get('incorrect_signatures'):
                report_lines.append(f"      - Firmas incorrectas: {len(report['incorrect_signatures'])}")
        
        # Detalles de funciones faltantes
        report_lines.extend(["", "🔍 FUNCIONES FALTANTES POR MÓDULO:"])
        
        for module_name, report in verification_result['module_reports'].items():
            if report.get('missing_functions'):
                report_lines.extend([
                    f"",
                    f"   📦 {module_name}:"
                ])
                
                for missing_func in report['missing_functions']:
                    report_lines.append(
                        f"      ❌ {missing_func['name']}({', '.join(missing_func['expected_params'])}) -> {missing_func['return_type']}"
                    )
                    report_lines.append(f"         └─ {missing_func['description']}")
        
        # Recomendaciones
        report_lines.extend([
            "",
            "💡 RECOMENDACIONES:",
        ])
        
        if verification_result['overall_coverage_percentage'] < 100:
            report_lines.extend([
                "   1. Implementar las funciones faltantes listadas arriba",
                "   2. Verificar que las firmas de métodos coincidan con la documentación",
                "   3. Agregar tests unitarios para las nuevas implementaciones",
                "   4. Actualizar la documentación si es necesario"
            ])
        else:
            report_lines.extend([
                "   ✅ ¡Excelente! Todas las funciones están implementadas",
                "   📝 Considera agregar tests de integración",
                "   📚 Mantener la documentación actualizada"
            ])
        
        report_lines.extend([
            "",
            "=" * 80,
            f"Reporte generado: {Path(__file__).name}",
            "=" * 80
        ])
        
        return "\n".join(report_lines)


def verify_workload_implementation() -> str:
    """
    Función principal para verificar la implementación del repositorio Workload.
    
    Returns:
        String con el reporte de verificación
    """
    try:
        verifier = WorkloadImplementationVerifier()
        return verifier.generate_implementation_report()
    except Exception as e:
        logger.error(f"Error durante la verificación: {e}")
        return f"❌ Error durante la verificación: {e}"


def verify_module_implementation(module_name: str) -> Dict[str, Any]:
    """
    Verifica la implementación de un módulo específico.
    
    Args:
        module_name: Nombre del módulo a verificar
        
    Returns:
        Dict con el reporte de verificación del módulo
    """
    try:
        verifier = WorkloadImplementationVerifier()
        return verifier.verify_module_implementation(module_name)
    except Exception as e:
        logger.error(f"Error verificando módulo {module_name}: {e}")
        return {
            'module': module_name,
            'status': 'error',
            'message': str(e)
        }


if __name__ == "__main__":
    # Ejecutar verificación completa
    print(verify_workload_implementation())