# Métodos de Dominio de Empleado

## Descripción General

Esta es una selección de métodos de dominio de empleado derivados de la propuesta del **Employee Domain Service**. Estos métodos proporcionan una capa de servicio fundamental para operaciones comunes relacionadas con la gestión de empleados, siguiendo el patrón establecido en el Client Domain Service.

---

## Métodos Disponibles

### 1. Operaciones CRUD Principales (4 métodos)

1.  `create_employee(employee_data: EmployeeCreate) -> Employee` - Crea un nuevo empleado.
2.  `get_employee_by_id(employee_id: int) -> Optional[Employee]` - Obtiene un empleado por su ID.
3.  `update_employee(employee_id: int, employee_data: EmployeeUpdate) -> Optional[Employee]` - Actualiza un empleado existente.
4.  `delete_employee(employee_id: int) -> bool` - Elimina un empleado.

### 2. Operaciones CRUD Especializadas (4 métodos)

5.  `create_employee_with_validation(employee_data: EmployeeCreate) -> Employee` - Crea un empleado con validaciones adicionales de negocio.
6.  `bulk_create_employees(employees_data: List[EmployeeCreate]) -> List[Employee]` - Crea múltiples empleados en una sola operación.
7.  `soft_delete_employee(employee_id: int) -> bool` - Elimina un empleado de forma lógica (soft delete).
8.  `restore_employee(employee_id: int) -> Optional[Employee]` - Restaura un empleado eliminado lógicamente.

### 3. Operaciones de Consulta Básica (6 métodos)

9.  `search_employees(filters: EmployeeFilter) -> List[Employee]` - Busca empleados aplicando filtros específicos.
10. `get_employees_by_status(status: EmployeeStatus) -> List[Employee]` - Obtiene empleados por su estado.
11. `get_employees_by_department(department: str) -> List[Employee]` - Obtiene empleados por departamento.
12. `search_employees_by_name(name: str) -> List[Employee]` - Busca empleados por nombre.
13. `get_active_employees() -> List[Employee]` - Obtiene todos los empleados activos.
14. `get_employees_paginated(skip: int, limit: int) -> List[Employee]` - Obtiene empleados con paginación.

### 4. Operaciones de Búsqueda Avanzada (3 métodos)

15. `advanced_employee_search(filters: Dict[str, Any]) -> List[Employee]` - Búsqueda avanzada con múltiples filtros complejos.
16. `get_employees_with_skills(skills: List[str]) -> List[Employee]` - Obtiene empleados que poseen habilidades específicas.
17. `get_employees_by_salary_range(min_salary: float, max_salary: float) -> List[Employee]` - Obtiene empleados dentro de un rango salarial.

### 5. Operaciones de Fechas (4 métodos)

18. `get_employees_hired_in_period(start_date: date, end_date: date) -> List[Employee]` - Obtiene empleados contratados en un período específico.
19. `get_employees_by_tenure_range(min_years: float, max_years: float) -> List[Employee]` - Obtiene empleados por rango de antigüedad.
20. `calculate_employee_tenure(employee_id: int) -> Dict[str, Any]` - Calcula la antigüedad detallada de un empleado.
21. `get_employees_hired_current_month() -> List[Employee]` - Obtiene empleados contratados en el mes actual.

### 6. Operaciones de Relaciones (3 métodos)

22. `get_employee_teams(employee_id: int) -> List[Dict[str, Any]]` - Obtiene los equipos a los que pertenece un empleado.
23. `get_employee_projects(employee_id: int) -> List[Dict[str, Any]]` - Obtiene los proyectos asignados a un empleado.
24. `validate_employee_dependencies(employee_id: int) -> Dict[str, bool]` - Valida las dependencias de un empleado antes de operaciones críticas.

### 7. Operaciones de Estadísticas (3 métodos)

25. `get_employee_statistics() -> EmployeeStatsResponse` - Obtiene estadísticas generales de empleados.
26. `get_comprehensive_employee_stats() -> Dict[str, Any]` - Obtiene estadísticas completas y detalladas del sistema de empleados.
27. `get_employee_performance_metrics(employee_id: int) -> Dict[str, Any]` - Obtiene métricas de rendimiento para un empleado específico.

### 8. Operaciones de Validación (2 métodos)

28. `validate_employee_business_rules(employee_data: Dict[str, Any]) -> bool` - Valida las reglas de negocio para datos de empleado (método principal).
29. `validate_employee_business_rules(employee_data: Dict[str, Any]) -> ValidationResult` - Valida las reglas de negocio con resultado detallado (método especializado).

### 9. Operaciones de Diagnóstico y Salud (1 método)

30. `health_check() -> Dict[str, Any]` - Verifica el estado de salud del servicio de empleados y sus dependencias.

---

## Resumen por Categorías

| Categoría | Cantidad | Descripción |
|-----------|----------|-------------|
| **CRUD Principales** | 4 | Operaciones básicas de creación, lectura, actualización y eliminación |
| **CRUD Especializadas** | 4 | Operaciones CRUD con lógica de negocio adicional |
| **Consulta Básica** | 6 | Búsquedas y filtros simples |
| **Búsqueda Avanzada** | 3 | Consultas complejas con múltiples criterios |
| **Operaciones de Fechas** | 4 | Gestión de períodos, antigüedad y fechas |
| **Gestión de Relaciones** | 3 | Manejo de relaciones con equipos y proyectos |
| **Estadísticas** | 3 | Métricas y análisis de datos |
| **Validación** | 2 | Verificación de reglas de negocio |
| **Diagnóstico** | 1 | Monitoreo de salud del servicio |
| **Total** | **30** | **Métodos propuestos** |

---

## Características Técnicas

### Schemas Utilizados
- **EmployeeCreate**: Esquema para creación de empleados
- **EmployeeUpdate**: Esquema para actualización de empleados
- **EmployeeFilter**: Esquema para filtros de búsqueda
- **EmployeeStatsResponse**: Esquema para respuestas de estadísticas
- **EmployeeStatus**: Enum para estados de empleados
- **ValidationResult**: Esquema para resultados de validación

### Patrones Implementados
- **Facade Pattern**: Unifica acceso a múltiples módulos especializados
- **Repository Pattern**: Abstrae el acceso a datos
- **Async/Await**: Operaciones asíncronas optimizadas
- **Dependency Injection**: Desacoplamiento de componentes
- **Type Hints**: Tipado completo para mejor mantenibilidad

### Integración con el Sistema
- Utiliza `EmployeeRepositoryFacade` para persistencia de datos
- Integra con el sistema de excepciones del proyecto
- Implementa logging estructurado con Loguru
- Sigue las mejores prácticas de Python 3.13 del proyecto

---

## Notas de Implementación

1. **Consistencia Arquitectónica**: Sigue el mismo patrón establecido en el Client Domain Service
2. **Escalabilidad**: Diseño modular que permite agregar nuevas funcionalidades fácilmente
3. **Testabilidad**: Interfaces bien definidas que facilitan el testing unitario
4. **Mantenibilidad**: Separación clara de responsabilidades entre módulos
5. **Performance**: Operaciones optimizadas con soporte asíncrono nativo

Esta documentación proporciona una guía completa de los métodos disponibles en el Employee Domain Service, facilitando su uso e integración en el sistema de planificación.