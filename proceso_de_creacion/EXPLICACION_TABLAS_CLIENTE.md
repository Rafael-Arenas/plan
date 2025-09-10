# Sistema de Planificación AkGroup - Explicación de las Tablas de Datos

## 🎯 Objetivo del Nuevo Sistema

El nuevo sistema de planificación digital reemplaza completamente el archivo Excel actual, organizando toda la información en **12 tablas especializadas** que trabajan juntas para ofrecer una gestión más eficiente, precisa y escalable de sus proyectos y personal.

---

## 📊 Comparación: Excel Actual vs. Nuevo Sistema

### ❌ Limitaciones del Excel Actual
- **Una sola hoja** con toda la información mezclada
- **52 columnas** difíciles de gestionar
- **Duplicación** de datos (clientes, empleados repetidos)
- **Sin validaciones** automáticas
- **Conflictos** al trabajar varias personas
- **Búsquedas lentas** y complicadas
- **Sin historial** de cambios
- **Reportes manuales** y propensos a errores

### ✅ Ventajas del Nuevo Sistema
- **12 tablas especializadas** cada una con su función específica
- **Datos únicos** sin duplicación
- **Validaciones automáticas** que previenen errores
- **Trabajo colaborativo** sin conflictos
- **Búsquedas instantáneas** y filtros avanzados
- **Historial completo** de todos los cambios
- **Reportes automáticos** y dashboards en tiempo real
- **Alertas inteligentes** para prevenir problemas

---

## 🏗️ Las 12 Tablas del Sistema

### 1. 👥 **CLIENTES** - Información de Empresas
**¿Qué hace?** Almacena todos los datos de las empresas que contratan sus servicios.

**¿Qué reemplaza del Excel?** La columna "CLIENT" (E) que se repetía en cada fila.

**Beneficios:**
- ✅ Cada cliente se registra **una sola vez**
- ✅ Información completa: contactos, teléfonos, emails
- ✅ Historial de todos los proyectos por cliente
- ✅ Fácil búsqueda y filtrado

**Información que guarda:**
- Nombre de la empresa
- Código interno único
- Persona de contacto
- Email y teléfono
- Estado (activo/inactivo)
- Observaciones

---

### 2. 🏗️ **PROYECTOS** - Gestión de Trabajos
**¿Qué hace?** Centraliza toda la información de cada proyecto o trabajo.

**¿Qué reemplaza del Excel?** Las columnas A-K (Référence, TRI-GRAMME, Nom du projet, JOB, etc.)

**Beneficios:**
- ✅ **Información completa** de cada proyecto en un lugar
- ✅ **Estados automáticos**: planificado, en progreso, completado
- ✅ **Fechas controladas** con validaciones
- ✅ **Seguimiento de responsables** y actualizaciones

**Información que guarda:**
- Referencia única del proyecto
- Trigrama (código de 3 letras)
- Nombre del proyecto/central
- Cliente asociado
- Fechas de inicio y fin
- Personal requerido
- Formación especial necesaria
- Estado actual y prioridad
- Responsable del proyecto

---

### 3. 👷 **EMPLEADOS** - Personal de la Empresa
**¿Qué hace?** Gestiona toda la información del personal y sus cualificaciones.

**¿Qué reemplaza del Excel?** La columna "Personnel" (G) y información dispersa del personal.

**Beneficios:**
- ✅ **Perfil completo** de cada empleado
- ✅ **Cualificaciones claras** (HN1, HN2, montador, supervisor)
- ✅ **Disponibilidad en tiempo real**
- ✅ **Historial de formaciones** y certificaciones

**Información que guarda:**
- Datos personales y contacto
- Código de empleado único
- Puesto y departamento
- Nivel de cualificación (HN1, HN2, etc.)
- Tipo de cualificación (montador, supervisor)
- Habilidades y certificaciones
- Horas semanales y tarifa
- Estado y disponibilidad

---

### 4. 👥 **EQUIPOS** - Grupos de Trabajo
**¿Qué hace?** Organiza a los empleados en equipos de trabajo especializados.

**¿Qué reemplaza del Excel?** Información implícita sobre agrupaciones de personal.

**Beneficios:**
- ✅ **Equipos especializados** por tipo de trabajo
- ✅ **Gestión visual** con colores identificativos
- ✅ **Roles definidos** dentro de cada equipo
- ✅ **Planificación por equipos** completos

**Información que guarda:**
- Nombre del equipo
- Código identificativo
- Descripción y especialidad
- Color para identificación visual
- Número máximo de miembros
- Estado activo/inactivo

---

### 5. 🔗 **MEMBRESÍAS DE EQUIPO** - Quién Pertenece a Qué Equipo
**¿Qué hace?** Conecta empleados con equipos, definiendo roles y períodos.

**¿Qué reemplaza del Excel?** Relaciones implícitas entre personal y grupos.

**Beneficios:**
- ✅ **Roles claros** en cada equipo (miembro, líder, supervisor)
- ✅ **Historial temporal** de pertenencia a equipos
- ✅ **Flexibilidad** para cambios de equipo
- ✅ **Múltiples equipos** por empleado si es necesario

---

### 6. 📋 **ASIGNACIONES DE PROYECTO** - Quién Trabaja en Qué
**¿Qué hace?** Registra qué empleados están asignados a qué proyectos y con qué dedicación.

**¿Qué reemplaza del Excel?** Información dispersa sobre asignaciones de personal.

**Beneficios:**
- ✅ **Control preciso** de asignaciones
- ✅ **Porcentajes de dedicación** por proyecto
- ✅ **Fechas exactas** de inicio y fin
- ✅ **Roles específicos** en cada proyecto

**Información que guarda:**
- Empleado asignado
- Proyecto correspondiente
- Fechas de asignación
- Horas diarias asignadas
- Porcentaje de dedicación
- Rol en el proyecto

---

### 7. 📅 **HORARIOS** - Planificación Diaria
**¿Qué hace?** Gestiona la planificación día a día de cada empleado.

**¿Qué reemplaza del Excel?** Las múltiples columnas de fechas y planificación temporal.

**Beneficios:**
- ✅ **Vista de calendario** clara y visual
- ✅ **Códigos de estado** con colores
- ✅ **Conflictos automáticamente detectados**
- ✅ **Planificación flexible** por empleado, proyecto o equipo

**Información que guarda:**
- Empleado programado
- Fecha específica
- Proyecto o equipo asignado
- Horario de inicio y fin
- Código de estado de la actividad
- Ubicación del trabajo
- Confirmación del horario

---

### 8. 🏷️ **CÓDIGOS DE ESTADO** - Estados Configurables
**¿Qué hace?** Define todos los posibles estados de actividades (trabajo, vacaciones, formación, etc.).

**¿Qué reemplaza del Excel?** Estados y códigos dispersos sin organización clara.

**Beneficios:**
- ✅ **Estados personalizables** según sus necesidades
- ✅ **Colores identificativos** para cada estado
- ✅ **Control de facturación** (qué es facturable y qué no)
- ✅ **Configuración flexible** sin programación

**Información que guarda:**
- Código único del estado
- Nombre descriptivo
- Color para visualización
- Si es facturable o no
- Si es productivo
- Si requiere aprobación
- Orden de visualización

---

### 9. 🏖️ **VACACIONES** - Gestión de Ausencias
**¿Qué hace?** Controla todas las vacaciones y ausencias del personal.

**¿Qué reemplaza del Excel?** Información de vacaciones mezclada con la planificación.

**Beneficios:**
- ✅ **Proceso de aprobación** automático
- ✅ **Cálculo automático** de días laborables
- ✅ **Detección de conflictos** con proyectos
- ✅ **Diferentes tipos** de ausencias

**Información que guarda:**
- Empleado solicitante
- Fechas de inicio y fin
- Tipo de vacación (anual, enfermedad, personal)
- Estado de aprobación
- Responsable de aprobación
- Días totales y laborables
- Motivo y observaciones

---

### 10. 📊 **CARGAS DE TRABAJO** - Métricas y Seguimiento
**¿Qué hace?** Registra y analiza la carga de trabajo real vs. planificada.

**¿Qué reemplaza del Excel?** Cálculos manuales de horas y eficiencia.

**Beneficios:**
- ✅ **Métricas automáticas** de productividad
- ✅ **Comparación** planificado vs. real
- ✅ **Indicadores de eficiencia** por empleado
- ✅ **Reportes de utilización** de recursos

**Información que guarda:**
- Empleado y proyecto
- Fecha específica
- Horas planificadas vs. reales
- Porcentaje de utilización
- Índices de eficiencia
- Observaciones del trabajo

---

### 11. 📝 **REGISTRO DE CAMBIOS** - Auditoría Completa
**¿Qué hace?** Registra automáticamente todos los cambios realizados en el sistema.

**¿Qué reemplaza del Excel?** La columna "Auteur MAJ" y "Date MAJ" limitadas.

**Beneficios:**
- ✅ **Historial completo** de todos los cambios
- ✅ **Trazabilidad total** de modificaciones
- ✅ **Responsabilidad clara** de cada cambio
- ✅ **Auditoría automática** sin intervención manual

**Información que guarda:**
- Qué se cambió (tabla y registro)
- Qué campo se modificó
- Valor anterior y nuevo
- Quién hizo el cambio
- Cuándo se realizó
- Razón del cambio
- Información técnica de la sesión

---

### 12. 🚨 **ALERTAS** - Sistema de Notificaciones
**¿Qué hace?** Genera automáticamente alertas para prevenir problemas y conflictos.

**¿Qué reemplaza del Excel?** Detección manual de problemas y conflictos.

**Beneficios:**
- ✅ **Prevención automática** de conflictos
- ✅ **Alertas prioritarias** para situaciones críticas
- ✅ **Notificaciones inteligentes** según el contexto
- ✅ **Seguimiento de resolución** de problemas

**Tipos de alertas:**
- Conflictos de planificación
- Personal insuficiente para proyectos
- Sobreasignación de recursos
- Advertencias de fechas límite
- Errores de validación
- Cambios críticos en proyectos
- Disponibilidad incierta de empleados

---

## 🔄 Cómo Trabajan Juntas las Tablas

### Flujo de Trabajo Típico:

1. **📝 Registro Inicial**
   - Se registra un **Cliente** una sola vez
   - Se crea un **Proyecto** asociado al cliente
   - Se definen los **Empleados** con sus cualificaciones

2. **👥 Organización**
   - Se forman **Equipos** especializados
   - Se establecen **Membresías** de empleados en equipos
   - Se crean **Asignaciones** de empleados a proyectos

3. **📅 Planificación**
   - Se programa **Horarios** diarios usando códigos de estado
   - Se gestionan **Vacaciones** con proceso de aprobación
   - Se registran **Cargas de Trabajo** reales

4. **🔍 Seguimiento Automático**
   - El **Registro de Cambios** documenta todo automáticamente
   - Las **Alertas** previenen conflictos y problemas
   - Los reportes se generan en tiempo real

---

## 🎯 Beneficios Inmediatos para AkGroup

### ⚡ Eficiencia Operativa
- **90% menos tiempo** en búsquedas de información
- **Eliminación total** de datos duplicados
- **Validaciones automáticas** que previenen errores
- **Reportes instantáneos** sin trabajo manual

### 👥 Gestión de Personal
- **Visibilidad completa** de disponibilidad en tiempo real
- **Cualificaciones claras** para asignación óptima
- **Historial completo** de cada empleado
- **Planificación visual** con códigos de color

### 📊 Control de Proyectos
- **Seguimiento preciso** del progreso
- **Alertas automáticas** para problemas potenciales
- **Métricas de eficiencia** por proyecto y empleado
- **Trazabilidad completa** de cambios

### 🔒 Seguridad y Auditoría
- **Historial inmutable** de todos los cambios
- **Control de acceso** por roles de usuario
- **Backup automático** de toda la información
- **Cumplimiento** de estándares de auditoría

---

## 🚀 Migración del Excel Actual

### Proceso de Transición:

1. **📥 Importación Automática**
   - Los datos del Excel actual se importan automáticamente
   - Se eliminan duplicados y se organizan en las tablas correspondientes
   - Se valida la integridad de toda la información

2. **🔧 Configuración Inicial**
   - Se definen los códigos de estado personalizados
   - Se establecen las cualificaciones del personal
   - Se configuran los equipos de trabajo

3. **✅ Validación y Pruebas**
   - Se verifica que toda la información esté correctamente migrada
   - Se realizan pruebas de funcionamiento
   - Se capacita al personal en el nuevo sistema

4. **🎯 Puesta en Producción**
   - Se activa el sistema nuevo
   - Se archiva el Excel como respaldo histórico
   - Se inicia el trabajo con el nuevo sistema

---

## 📈 Escalabilidad Futura

El nuevo sistema está diseñado para crecer con AkGroup:

- ✅ **Más empleados** sin límites
- ✅ **Más proyectos** simultáneos
- ✅ **Nuevas funcionalidades** sin afectar datos existentes
- ✅ **Integración** con otros sistemas empresariales
- ✅ **Módulos adicionales** (financiero, inventario, etc.)
- ✅ **Acceso móvil** para trabajo en campo
- ✅ **API** para integraciones futuras

---

## 🎉 Conclusión

El nuevo sistema de 12 tablas especializadas transforma completamente la gestión de AkGroup, pasando de un Excel limitado y propenso a errores a una solución robusta, escalable y automatizada que:

- **Elimina** la duplicación de datos
- **Automatiza** validaciones y cálculos
- **Previene** conflictos y errores
- **Proporciona** visibilidad total en tiempo real
- **Facilita** la toma de decisiones con datos precisos
- **Escala** con el crecimiento de la empresa

Cada tabla tiene un propósito específico y trabaja en conjunto con las demás para ofrecer una experiencia de gestión superior, más eficiente y confiable que el sistema actual.