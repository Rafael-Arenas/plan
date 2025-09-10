# Funcionalidades Disponibles en `ClientRepositoryFacade`

**Versión:** 1.0.0
**Fecha de Actualización:** 2024-07-29

## Introducción

`ClientRepositoryFacade` actúa como una interfaz unificada para todas las operaciones relacionadas con la gestión de clientes. Centraliza la lógica de negocio, el acceso a datos y las validaciones, coordinando un conjunto de módulos especializados para ofrecer una API robusta y coherente.

Este documento describe en detalle cada una de las funcionalidades expuestas por el facade, organizadas por categoría.

---

## 1. Operaciones CRUD (Crear, Leer, Actualizar, Eliminar)

Estas son las operaciones básicas para la gestión de clientes.

### `create_client`
- **Descripción:** Crea un nuevo cliente en la base de datos con validación de datos básicos.
- **Parámetros:** `client_data` (schema `ClientCreate`)
- **Retorna:** Objeto `Client` creado.
- **Manejo de Errores:** `ClientValidationError`, `ClientDuplicateError`, `RepositoryError`.

### `create_client_with_pendulum_validation`
- **Descripción:** Crea un cliente utilizando validaciones de fecha avanzadas con `Pendulum` para garantizar la integridad temporal.
- **Parámetros:** `client_data` (schema `ClientCreate`)
- **Retorna:** Objeto `Client` creado.
- **Manejo de Errores:** `ClientValidationError`, `RepositoryError`.

### `get_client_by_id`
- **Descripción:** Obtiene un cliente por su ID.
- **Parámetros:** `client_id` (int)
- **Retorna:** Objeto `Client` o `None` si no se encuentra.
- **Manejo de Errores:** `RepositoryError`.

### `update_client`
- **Descripción:** Actualiza los datos de un cliente existente.
- **Parámetros:** `client_id` (int), `client_data` (schema `ClientUpdate`)
- **Retorna:** Objeto `Client` actualizado o `None`.
- **Manejo de Errores:** `ClientNotFoundError`, `ClientValidationError`, `RepositoryError`.

### `delete_client`
- **Descripción:** Elimina un cliente de la base de datos.
- **Parámetros:** `client_id` (int)
- **Retorna:** `True` si se eliminó, `False` en caso contrario.
- **Manejo de Errores:** `ClientNotFoundError`, `RepositoryError`.

---

## 2. Consultas Especializadas

Funciones para búsquedas y filtros avanzados.

### `get_client_by_name`
- **Descripción:** Busca un cliente por su nombre exacto.
- **Parámetros:** `name` (str)
- **Retorna:** Objeto `Client` o `None`.

### `get_client_by_code`
- **Descripción:** Busca un cliente por su código exacto.
- **Parámetros:** `code` (str)
- **Retorna:** Objeto `Client` o `None`.

### `search_clients_by_name`
- **Descripción:** Busca clientes cuyo nombre contenga el texto proporcionado.
- **Parámetros:** `name_pattern` (str)
- **Retorna:** Lista de objetos `Client`.

### `get_active_clients`
- **Descripción:** Obtiene una lista de todos los clientes activos.
- **Retorna:** Lista de objetos `Client`.

### `search_with_advanced_filters`
- **Descripción:** Realiza una búsqueda avanzada con múltiples criterios de filtrado, ordenamiento y paginación.
- **Parámetros:** `filters` (dict), `order_by` (str), `limit` (int), `offset` (int)
- **Retorna:** Lista de objetos `Client`.

---

## 3. Operaciones Temporales (Basadas en Fechas)

Funcionalidades que dependen de fechas, utilizando `Pendulum`.

### `get_clients_created_current_week`
- **Descripción:** Obtiene los clientes creados en la semana actual.
- **Retorna:** Lista de objetos `Client`.

### `get_clients_created_current_month`
- **Descripción:** Obtiene los clientes creados en el mes actual.
- **Retorna:** Lista de objetos `Client`.

### `get_clients_by_date_range`
- **Descripción:** Obtiene clientes creados en un rango de fechas específico.
- **Parámetros:** `start_date` (str), `end_date` (str)
- **Retorna:** Lista de objetos `Client`.

### `get_clients_by_age_range`
- **Descripción:** Obtiene clientes cuyo registro se encuentra dentro de un rango de antigüedad (en días).
- **Parámetros:** `min_age_days` (int), `max_age_days` (int)
- **Retorna:** Lista de objetos `Client`.

---

## 4. Estadísticas y Métricas

Funciones para análisis y obtención de métricas clave.

### `get_client_statistics`
- **Descripción:** Obtiene estadísticas básicas sobre los clientes (total, activos, inactivos).
- **Retorna:** Diccionario con estadísticas.

### `get_comprehensive_dashboard_metrics`
- **Descripción:** Proporciona un conjunto completo de métricas para un panel de control.
- **Retorna:** Diccionario con métricas detalladas.

### `get_client_segmentation_analysis`
- **Descripción:** Realiza un análisis de segmentación de clientes basado en criterios predefinidos.
- **Retorna:** Diccionario con el análisis de segmentación.

### `get_client_value_analysis`
- **Descripción:** Analiza el valor del cliente, posiblemente basado en proyectos o interacciones.
- **Retorna:** Diccionario con el análisis de valor.

### `get_client_retention_analysis`
- **Descripción:** Analiza la retención de clientes a lo largo del tiempo.
- **Retorna:** Diccionario con el análisis de retención.

---

## 5. Validaciones

Funciones para validar datos antes de realizar operaciones.

### `validate_client_name_unique`
- **Descripción:** Verifica si un nombre de cliente ya existe.
- **Parámetros:** `name` (str), `exclude_id` (Optional[int])
- **Retorna:** `True` si es único, `False` si no.

### `validate_client_code_unique`
- **Descripción:** Verifica si un código de cliente ya existe.
- **Parámetros:** `code` (str), `exclude_id` (Optional[int])
- **Retorna:** `True` si es único, `False` si no.

---

## 6. Operaciones Complejas Coordinadas

Funciones que orquestan múltiples módulos para realizar tareas complejas.

### `create_client_with_full_validation`
- **Descripción:** Crea un cliente aplicando un conjunto completo de validaciones, incluyendo unicidad de nombre/código y reglas de negocio (formato de email/teléfono).
- **Parámetros:** `client_data` (schema `ClientCreate`), `validate_business_rules` (bool)
- **Retorna:** Objeto `Client` creado.
- **Manejo de Errores:** `ClientRepositoryError` si alguna validación falla.

### `get_client_complete_profile`
- **Descripción:** Obtiene un perfil completo y enriquecido de un cliente, combinando datos básicos, estadísticas y cálculo de antigüedad.
- **Parámetros:** `client_id` (int)
- **Retorna:** Diccionario con el perfil completo o `None`.

---

## 7. Utilidad y Estado del Sistema

Funciones para monitorear la salud y configuración del facade.

### `health_check`
- **Descripción:** Verifica el estado de salud de todos los módulos internos del facade.
- **Retorna:** Diccionario con el estado de cada componente.

### `get_module_info`
- **Descripción:** Obtiene información sobre los módulos que componen el facade.
- **Retorna:** Diccionario con los nombres de las clases de los módulos cargados.
