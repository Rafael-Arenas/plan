# src/planificador/database/repositories/employee/modules/validation_operations.py

import re
import json
from typing import List, Optional, Dict, Any
from loguru import logger

from .....exceptions import ValidationError
from .....models.employee import EmployeeStatus
from .....utils.date_utils import get_current_time
from ..interfaces.validation_interface import IEmployeeValidationOperations


class ValidationOperations(IEmployeeValidationOperations):
    """
    Implementación de operaciones de validación para empleados.
    
    Proporciona validaciones específicas para empleados incluyendo
    formato de datos, reglas de negocio y consistencia.
    """
    
    def __init__(self):
        self._logger = logger
        
        # Patrones de validación
        self._email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        self._phone_pattern = re.compile(
            r'^[\+]?[1-9]?[0-9]{7,15}$'
        )
        self._employee_code_pattern = re.compile(
            r'^[A-Z0-9]{3,10}$'
        )
    
    # ============================================================================
    # VALIDACIONES PRINCIPALES
    # ============================================================================
    
    def validate_create_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos para crear un nuevo empleado.
        
        Args:
            data: Diccionario con los datos del empleado
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        try:
            self._validate_required_fields_for_create(data)
            self._validate_employee_code(data.get('employee_code'))
            self._validate_full_name(data.get('full_name'))
            self._validate_first_name(data.get('first_name'))
            self._validate_last_name(data.get('last_name'))
            self._validate_email(data.get('email'))
            self._validate_phone(data.get('phone'))
            self._validate_department(data.get('department'))
            self._validate_position(data.get('position'))
            self._validate_hire_date(data.get('hire_date'))
            self._validate_salary(data.get('salary'))
            self._validate_status(data.get('status', EmployeeStatus.ACTIVE))
            self._validate_skills(data.get('skills'))
            
            self._logger.debug("Validación de datos de creación completada exitosamente")
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en validación de creación: {e}")
            raise ValidationError(f"Error en validación: {str(e)}")
    
    def validate_update_data(self, data: Dict[str, Any]) -> None:
        """
        Valida los datos para actualizar un empleado existente.
        
        Args:
            data: Diccionario con los datos a actualizar
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        try:
            # Para actualización, solo validamos los campos que están presentes
            if 'employee_code' in data:
                self._validate_employee_code(data['employee_code'])
            
            if 'full_name' in data:
                self._validate_full_name(data['full_name'])
            
            if 'first_name' in data:
                self._validate_first_name(data['first_name'])
            
            if 'last_name' in data:
                self._validate_last_name(data['last_name'])
            
            if 'email' in data:
                self._validate_email(data['email'])
            
            if 'phone' in data:
                self._validate_phone(data['phone'])
            
            if 'department' in data:
                self._validate_department(data['department'])
            
            if 'position' in data:
                self._validate_position(data['position'])
            
            if 'hire_date' in data:
                self._validate_hire_date(data['hire_date'])
            
            if 'salary' in data:
                self._validate_salary(data['salary'])
            
            if 'status' in data:
                self._validate_status(data['status'])
            
            if 'skills' in data:
                self._validate_skills(data['skills'])
            
            self._logger.debug("Validación de datos de actualización completada exitosamente")
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en validación de actualización: {e}")
            raise ValidationError(f"Error en validación: {str(e)}")
    
    def validate_skills_json(self, skills_json: Optional[str]) -> Optional[List[str]]:
        """
        Valida y convierte un JSON de habilidades a lista.
        
        Args:
            skills_json: JSON string con las habilidades
            
        Returns:
            Lista de habilidades o None
            
        Raises:
            ValidationError: Si el JSON no es válido
        """
        if not skills_json:
            return None
        
        try:
            skills = json.loads(skills_json)
            self._validate_skills(skills)
            return skills
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"El JSON de habilidades no es válido: {str(e)}")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error procesando habilidades: {str(e)}")
    
    def validate_search_term(self, search_term: str) -> str:
        """
        Valida y limpia un término de búsqueda.
        
        Args:
            search_term: Término de búsqueda
            
        Returns:
            Término de búsqueda limpio
            
        Raises:
            ValidationError: Si el término no es válido
        """
        if not search_term:
            raise ValidationError("El término de búsqueda es requerido")
        
        if not isinstance(search_term, str):
            raise ValidationError("El término de búsqueda debe ser una cadena")
        
        search_term = search_term.strip()
        if not search_term:
            raise ValidationError("El término de búsqueda no puede estar vacío")
        
        if len(search_term) < 2:
            raise ValidationError("El término de búsqueda debe tener al menos 2 caracteres")
        
        if len(search_term) > 100:
            raise ValidationError("El término de búsqueda no puede exceder 100 caracteres")
        
        return search_term
    
    def validate_employee_id(self, employee_id: int) -> None:
        """
        Valida un ID de empleado.
        
        Args:
            employee_id: ID del empleado
            
        Raises:
            ValidationError: Si el ID no es válido
        """
        if not isinstance(employee_id, int):
            raise ValidationError("El ID del empleado debe ser un número entero")
        
        if employee_id <= 0:
            raise ValidationError("El ID del empleado debe ser un número positivo")
    
    # ============================================================================
    # VALIDACIONES INTERNAS - CAMPOS REQUERIDOS
    # ============================================================================
    
    def _validate_required_fields_for_create(self, data: Dict[str, Any]) -> None:
        """
        Valida que estén presentes todos los campos requeridos para crear un empleado.
        
        Args:
            data: Diccionario con los datos del empleado
            
        Raises:
            ValidationError: Si falta algún campo requerido
        """
        required_fields = [
            'employee_code', 'full_name', 'first_name', 'last_name',
            'email', 'department', 'position', 'hire_date'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(
                f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            )
    
    # ============================================================================
    # VALIDACIONES INTERNAS - FORMATO DE DATOS
    # ============================================================================
    
    def _validate_employee_code(self, employee_code: str) -> None:
        """
        Valida el formato del código de empleado.
        
        Args:
            employee_code: Código del empleado
            
        Raises:
            ValidationError: Si el código no es válido
        """
        if not employee_code:
            raise ValidationError("El código de empleado es requerido")
        
        if not isinstance(employee_code, str):
            raise ValidationError("El código de empleado debe ser una cadena")
        
        employee_code = employee_code.strip()
        if not employee_code:
            raise ValidationError("El código de empleado no puede estar vacío")
        
        if not self._employee_code_pattern.match(employee_code):
            raise ValidationError(
                "El código de empleado debe tener entre 3-10 caracteres alfanuméricos en mayúsculas"
            )
    
    def _validate_full_name(self, full_name: str) -> None:
        """
        Valida el nombre completo del empleado.
        
        Args:
            full_name: Nombre completo del empleado
            
        Raises:
            ValidationError: Si el nombre no es válido
        """
        if not full_name:
            raise ValidationError("El nombre completo es requerido")
        
        if not isinstance(full_name, str):
            raise ValidationError("El nombre completo debe ser una cadena")
        
        full_name = full_name.strip()
        if not full_name:
            raise ValidationError("El nombre completo no puede estar vacío")
        
        if len(full_name) < 2:
            raise ValidationError("El nombre completo debe tener al menos 2 caracteres")
        
        if len(full_name) > 200:
            raise ValidationError("El nombre completo no puede exceder 200 caracteres")
    
    def _validate_first_name(self, first_name: str) -> None:
        """
        Valida el primer nombre del empleado.
        
        Args:
            first_name: Primer nombre del empleado
            
        Raises:
            ValidationError: Si el nombre no es válido
        """
        if not first_name:
            raise ValidationError("El primer nombre es requerido")
        
        if not isinstance(first_name, str):
            raise ValidationError("El primer nombre debe ser una cadena")
        
        first_name = first_name.strip()
        if not first_name:
            raise ValidationError("El primer nombre no puede estar vacío")
        
        if len(first_name) < 1:
            raise ValidationError("El primer nombre debe tener al menos 1 carácter")
        
        if len(first_name) > 100:
            raise ValidationError("El primer nombre no puede exceder 100 caracteres")
    
    def _validate_last_name(self, last_name: str) -> None:
        """
        Valida el apellido del empleado.
        
        Args:
            last_name: Apellido del empleado
            
        Raises:
            ValidationError: Si el apellido no es válido
        """
        if not last_name:
            raise ValidationError("El apellido es requerido")
        
        if not isinstance(last_name, str):
            raise ValidationError("El apellido debe ser una cadena")
        
        last_name = last_name.strip()
        if not last_name:
            raise ValidationError("El apellido no puede estar vacío")
        
        if len(last_name) < 1:
            raise ValidationError("El apellido debe tener al menos 1 carácter")
        
        if len(last_name) > 100:
            raise ValidationError("El apellido no puede exceder 100 caracteres")
    
    def _validate_email(self, email: str) -> None:
        """
        Valida el formato del email.
        
        Args:
            email: Email del empleado
            
        Raises:
            ValidationError: Si el email no es válido
        """
        if not email:
            raise ValidationError("El email es requerido")
        
        if not isinstance(email, str):
            raise ValidationError("El email debe ser una cadena")
        
        email = email.strip().lower()
        if not email:
            raise ValidationError("El email no puede estar vacío")
        
        if len(email) > 255:
            raise ValidationError("El email no puede exceder 255 caracteres")
        
        if not self._email_pattern.match(email):
            raise ValidationError("El formato del email no es válido")
    
    def _validate_phone(self, phone: Optional[str]) -> None:
        """
        Valida el formato del teléfono (opcional).
        
        Args:
            phone: Teléfono del empleado
            
        Raises:
            ValidationError: Si el teléfono no es válido
        """
        if phone is None:
            return  # El teléfono es opcional
        
        if not isinstance(phone, str):
            raise ValidationError("El teléfono debe ser una cadena")
        
        phone = phone.strip()
        if not phone:
            return  # Permitir cadena vacía como None
        
        if len(phone) > 20:
            raise ValidationError("El teléfono no puede exceder 20 caracteres")
        
        # Remover espacios y guiones para validación
        phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
        if not self._phone_pattern.match(phone_clean):
            raise ValidationError("El formato del teléfono no es válido")

    def _validate_department(self, department: str) -> None:
        """
        Valida el departamento del empleado.
        
        Args:
            department: Departamento del empleado
            
        Raises:
            ValidationError: Si el departamento no es válido
        """
        if not department:
            raise ValidationError("El departamento es requerido")
        
        if not isinstance(department, str):
            raise ValidationError("El departamento debe ser una cadena")
        
        department = department.strip()
        if not department:
            raise ValidationError("El departamento no puede estar vacío")
        
        if len(department) < 2:
            raise ValidationError("El departamento debe tener al menos 2 caracteres")
        
        if len(department) > 100:
            raise ValidationError("El departamento no puede exceder 100 caracteres")
    
    def _validate_position(self, position: str) -> None:
        """
        Valida la posición del empleado.
        
        Args:
            position: Posición del empleado
            
        Raises:
            ValidationError: Si la posición no es válida
        """
        if not position:
            raise ValidationError("La posición es requerida")
        
        if not isinstance(position, str):
            raise ValidationError("La posición debe ser una cadena")
        
        position = position.strip()
        if not position:
            raise ValidationError("La posición no puede estar vacía")
        
        if len(position) < 2:
            raise ValidationError("La posición debe tener al menos 2 caracteres")
        
        if len(position) > 100:
            raise ValidationError("La posición no puede exceder 100 caracteres")
    
    def _validate_hire_date(self, hire_date) -> None:
        """
        Valida la fecha de contratación.
        
        Args:
            hire_date: Fecha de contratación
            
        Raises:
            ValidationError: Si la fecha no es válida
        """
        if hire_date is None:
            raise ValidationError("La fecha de contratación es requerida")
        
        # Verificar que no sea una fecha futura
        current_date = get_current_time().date()
        if hire_date > current_date:
            raise ValidationError("La fecha de contratación no puede ser futura")
    
    # ============================================================================
    # VALIDACIONES INTERNAS - REGLAS DE NEGOCIO
    # ============================================================================

    def _validate_salary(self, salary: Optional[float]) -> None:
        """
        Valida el salario del empleado (opcional).
        
        Args:
            salary: Salario del empleado
            
        Raises:
            ValidationError: Si el salario no es válido
        """
        if salary is None:
            return  # El salario es opcional
        
        if not isinstance(salary, (int, float)):
            raise ValidationError("El salario debe ser un número")
        
        if salary < 0:
            raise ValidationError("El salario no puede ser negativo")
        
        if salary > 999999999.99:
            raise ValidationError("El salario excede el límite máximo")
    
    def _validate_status(self, status: EmployeeStatus) -> None:
        """
        Valida el estado del empleado.
        
        Args:
            status: Estado del empleado
            
        Raises:
            ValidationError: Si el estado no es válido
        """
        if not isinstance(status, EmployeeStatus):
            raise ValidationError("El estado debe ser un valor válido de EmployeeStatus")
    
    def _validate_skills(self, skills: Optional[List[str]]) -> None:
        """
        Valida las habilidades del empleado (opcional).
        
        Args:
            skills: Lista de habilidades del empleado
            
        Raises:
            ValidationError: Si las habilidades no son válidas
        """
        if skills is None:
            return  # Las habilidades son opcionales
        
        if not isinstance(skills, list):
            raise ValidationError("Las habilidades deben ser una lista")
        
        if len(skills) > 50:
            raise ValidationError("No se pueden especificar más de 50 habilidades")
        
        for i, skill in enumerate(skills):
            if not isinstance(skill, str):
                raise ValidationError(f"La habilidad en posición {i} debe ser una cadena")
            
            skill = skill.strip()
            if not skill:
                raise ValidationError(f"La habilidad en posición {i} no puede estar vacía")
            
            if len(skill) > 100:
                raise ValidationError(f"La habilidad en posición {i} no puede exceder 100 caracteres")