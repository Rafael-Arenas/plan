# src/planificador/models/team_membership.py

import enum
from datetime import date
from sqlalchemy import Column, Integer, ForeignKey, Date, Enum, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel, Base

class MembershipRole(enum.Enum):
    """Roles dentro de un equipo."""
    MEMBER = "member"
    LEAD = "lead"
    SUPERVISOR = "supervisor"
    COORDINATOR = "coordinator"

class TeamMembership(BaseModel):
    """Modelo para membresías de equipos (relación many-to-many con roles)."""
    __tablename__ = 'team_memberships'

    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id', ondelete='CASCADE'), nullable=False)
    role = Column(Enum(MembershipRole), default=MembershipRole.MEMBER, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relaciones
    employee = relationship("Employee", back_populates="team_memberships")
    team = relationship("Team", back_populates="memberships")

    # Métodos de utilidad
    @property
    def duration_days(self) -> int:
        """Duración de la membresía en días."""
        end = self.end_date or date.today()
        return (end - self.start_date).days
    
    @property
    def is_current(self) -> bool:
        """Verifica si la membresía está activa actualmente."""
        today = date.today()
        if not self.is_active:
            return False
        if self.start_date > today:
            return False
        if self.end_date and self.end_date < today:
            return False
        return True
    
    @property
    def is_future(self) -> bool:
        """Verifica si la membresía es futura."""
        return self.start_date > date.today()
    
    @property
    def is_past(self) -> bool:
        """Verifica si la membresía ya terminó."""
        if not self.end_date:
            return False
        return self.end_date < date.today()
    
    @property
    def is_indefinite(self) -> bool:
        """Verifica si la membresía es indefinida (sin fecha fin)."""
        return self.end_date is None
    
    @property
    def role_display(self) -> str:
        """Rol para mostrar en español."""
        role_translations = {
            MembershipRole.MEMBER: "Miembro",
            MembershipRole.LEAD: "Líder",
            MembershipRole.SUPERVISOR: "Supervisor",
            MembershipRole.COORDINATOR: "Coordinador"
        }
        return role_translations.get(self.role, self.role.value)
    
    @property
    def status_display(self) -> str:
        """Estado para mostrar en español."""
        if not self.is_active:
            return "Inactivo"
        elif self.is_future:
            return "Futuro"
        elif self.is_past:
            return "Finalizado"
        elif self.is_current:
            return "Activo"
        else:
            return "Pendiente"
    
    @property
    def membership_summary(self) -> str:
        """Resumen de la membresía."""
        return f"{self.role_display} - {self.status_display}"
    
    def days_until_start(self) -> int:
        """Días hasta el inicio de la membresía."""
        if self.start_date <= date.today():
            return 0
        return (self.start_date - date.today()).days
    
    def days_until_end(self) -> int:
        """Días hasta el fin de la membresía."""
        if not self.end_date:
            return -1  # Indefinida
        if self.end_date <= date.today():
            return 0
        return (self.end_date - date.today()).days
    
    def __repr__(self) -> str:
        return f"<TeamMembership(employee_id={self.employee_id}, team_id={self.team_id}, role='{self.role.value}')>"