# src/planificador/models/employee.py

import enum
from sqlalchemy import Column, String, Date, Boolean, Text, Enum, Integer, Numeric, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel, Base

class EmployeeStatus(enum.Enum):
    """Estados posibles de un empleado."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    ON_VACATION = "on_vacation"
    TERMINATED = "terminated"

class Employee(BaseModel):
    """Modelo para gestión de empleados."""
    __tablename__ = 'employees'

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    full_name = Column(String(255), nullable=False, unique=True)
    employee_code = Column(String(20), nullable=True, unique=True)
    email = Column(String(100), nullable=True, unique=True)
    phone = Column(String(20), nullable=True)
    hire_date = Column(Date, nullable=True)
    position = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    qualification_level = Column(String(10))
    qualification_type = Column(String(50))
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False)
    skills = Column(JSON, nullable=True)
    certifications = Column(JSON, nullable=True)
    special_training = Column(JSON, nullable=True)
    weekly_hours = Column(Integer, default=40, nullable=False)
    hourly_rate = Column(Numeric(8, 2), nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)

    # Relaciones
    team_memberships = relationship("TeamMembership", back_populates="employee", cascade="all, delete-orphan")
    project_assignments = relationship("ProjectAssignment", back_populates="employee", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="employee", cascade="all, delete-orphan")
    vacations = relationship("Vacation", back_populates="employee", cascade="all, delete-orphan")
    workloads = relationship("Workload", back_populates="employee", cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs):
        # Solo generar full_name automáticamente si no se proporciona
        if 'first_name' in kwargs and 'last_name' in kwargs and 'full_name' not in kwargs:
            kwargs['full_name'] = f"{kwargs['first_name']} {kwargs['last_name']}"
        super().__init__(*args, **kwargs)

    @property
    def display_name(self) -> str:
        """Nombre completo dinámico basado en first_name y last_name actuales."""
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self) -> str:
        """Iniciales del empleado."""
        first_initial = self.first_name[0].upper() if self.first_name else ""
        last_initial = self.last_name[0].upper() if self.last_name else ""
        return f"{first_initial}{last_initial}"

    @property
    def is_active_status(self) -> bool:
        """Verifica si el empleado está en estado activo."""
        return self.status == EmployeeStatus.ACTIVE

    @property
    def contact_info(self) -> dict:
        """Información de contacto del empleado."""
        return {
            "email": self.email,
            "phone": self.phone,
            "full_name": self.display_name
        }

    def update_full_name(self) -> None:
        """Actualiza el campo full_name basado en first_name y last_name actuales."""
        self.full_name = f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, full_name='{self.full_name}')>"