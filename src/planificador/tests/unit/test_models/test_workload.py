"""Tests para el modelo Workload.

Este módulo contiene tests comprehensivos para el modelo Workload,
incluyendo creación, validación, propiedades calculadas, métodos
personalizados y relaciones.
"""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.workload import Workload
from planificador.models.employee import Employee
from planificador.models.project import Project


class TestWorkloadModel:
    """Tests para el modelo Workload."""
    
    @pytest.fixture
    def sample_workload_data(self) -> dict:
        """Datos de prueba para crear un workload.
        
        Returns:
            dict: Diccionario con datos válidos para crear un workload
        """
        return {
            "date": date(2024, 1, 15),
            "week_number": 3,
            "month": 1,
            "year": 2024,
            "planned_hours": Decimal('8.0'),
            "actual_hours": Decimal('7.5'),
            "utilization_percentage": Decimal('93.75'),
            "efficiency_score": Decimal('85.0'),
            "productivity_index": Decimal('88.0'),
            "is_billable": True,
            "notes": "Workload de prueba"
        }
    
    async def test_create_workload_with_minimal_fields(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test creación de workload con campos mínimos requeridos."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.id is not None
        assert workload.employee_id == sample_employee.id
        assert workload.project_id == sample_project.id
        assert workload.date == date(2024, 1, 15)
        assert workload.planned_hours == Decimal('8.0')
        assert workload.actual_hours is None
        assert workload.is_billable is False  # Valor por defecto
    
    async def test_create_workload_with_all_fields(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project,
        sample_workload_data: dict
    ):
        """Test creación de workload con todos los campos."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            **sample_workload_data
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.id is not None
        assert workload.employee_id == sample_employee.id
        assert workload.project_id == sample_project.id
        assert workload.date == sample_workload_data["date"]
        assert workload.planned_hours == sample_workload_data["planned_hours"]
        assert workload.actual_hours == sample_workload_data["actual_hours"]
        assert workload.is_billable == sample_workload_data["is_billable"]
        assert workload.notes == sample_workload_data["notes"]


class TestWorkloadValidation:
    """Tests para validación de campos del modelo Workload."""
    
    async def test_employee_id_required(
        self,
        test_session: AsyncSession,
        sample_project: Project
    ):
        """Test que employee_id es requerido."""
        workload = Workload(
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()
    
    async def test_project_id_optional(
        self,
        test_session: AsyncSession,
        sample_employee: Employee
    ):
        """Test que project_id es opcional (nullable=True)."""
        workload = Workload(
            employee_id=sample_employee.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.project_id is None
    
    async def test_date_required(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test que date es requerido."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        
        with pytest.raises(IntegrityError):
            await test_session.flush()
    
    async def test_planned_hours_optional(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test que planned_hours es opcional (nullable=True)."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.planned_hours is None
    
    async def test_default_values(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test valores por defecto de los campos."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.is_billable is False
        assert workload.actual_hours is None
        assert workload.utilization_percentage is None
        assert workload.efficiency_score is None
        assert workload.productivity_index is None
        assert workload.notes is None


class TestWorkloadCalculatedProperties:
    """Tests para propiedades calculadas del modelo Workload."""
    
    async def test_hours_variance_with_actual_hours(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test cálculo de hours_variance cuando hay actual_hours."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0'),
            actual_hours=Decimal('7.5')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.hours_variance == Decimal('-0.5')
    
    async def test_hours_variance_without_actual_hours(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test hours_variance cuando no hay actual_hours."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.hours_variance is None
    
    async def test_efficiency_category_high(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test efficiency_category para puntuación alta."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0'),
            efficiency_score=Decimal('95.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.efficiency_category == "Alta"
    
    async def test_efficiency_category_medium(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test efficiency_category para puntuación media."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0'),
            efficiency_score=Decimal('75.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.efficiency_category == "Media"
    
    async def test_efficiency_category_low(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test efficiency_category para puntuación baja."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0'),
            efficiency_score=Decimal('55.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.efficiency_category == "Baja"
    
    async def test_efficiency_category_none(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test efficiency_category cuando no hay efficiency_score."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.efficiency_category == "Sin datos"
    
    async def test_productivity_category_high(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test productivity_category para índice alto."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0'),
            productivity_index=Decimal('92.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.productivity_category == "Alta"
    
    async def test_utilization_category_optimal(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test utilization_category para porcentaje óptimo."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0'),
            utilization_percentage=Decimal('85.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.utilization_category == "Óptima"
    
    async def test_billable_status_billable(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test billable_status para trabajo facturable."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0'),
            is_billable=True
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.billable_status == "Facturable"
    
    async def test_billable_status_non_billable(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test billable_status para trabajo no facturable."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0'),
            is_billable=False
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.billable_status == "No facturable"


class TestWorkloadMethods:
    """Tests para métodos personalizados del modelo Workload."""
    
    async def test_is_weekend_saturday(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test is_weekend para sábado."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 13),  # Sábado
            week_number=2,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.is_weekend is True
    
    async def test_is_weekend_sunday(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test is_weekend para domingo."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 14),  # Domingo
            week_number=2,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.is_weekend is True
    
    async def test_is_weekend_weekday(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test is_weekend para día de semana."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),  # Lunes
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.is_weekend is False
    
    async def test_get_quarter_q1(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test get_quarter para primer trimestre."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 2, 15),
            week_number=7,
            month=2,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.get_quarter() == 1
    
    async def test_get_quarter_q2(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test get_quarter para segundo trimestre."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 5, 15),
            week_number=20,
            month=5,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.get_quarter() == 2
    
    async def test_get_quarter_q3(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test get_quarter para tercer trimestre."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 8, 15),
            week_number=33,
            month=8,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.get_quarter() == 3
    
    async def test_get_quarter_q4(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test get_quarter para cuarto trimestre."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 11, 15),
            week_number=46,
            month=11,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.get_quarter() == 4
    
    async def test_calculate_efficiency_score_with_actual_hours(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test calculate_efficiency_score con actual_hours."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0'),
            actual_hours=Decimal('6.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        efficiency = workload.calculate_efficiency_score()
        # calculate_efficiency_score devuelve float, no Decimal
        assert abs(efficiency - 75.0) < 0.01  # (6.0 / 8.0) * 100
    
    async def test_calculate_efficiency_score_without_actual_hours(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test calculate_efficiency_score sin actual_hours."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        efficiency = workload.calculate_efficiency_score()
        assert efficiency is None
    
    async def test_calculate_efficiency_score_zero_actual_hours(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test calculate_efficiency_score con actual_hours cero."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0'),
            actual_hours=Decimal('0.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        efficiency = workload.calculate_efficiency_score()
        assert efficiency is None
    
    async def test_performance_summary_complete(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test performance_summary con todos los datos."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0'),
            actual_hours=Decimal('7.5'),
            utilization_percentage=Decimal('93.75'),
            efficiency_score=Decimal('85.0'),
            productivity_index=Decimal('88.0'),
            is_billable=True
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        # performance_summary devuelve un string con formato específico
        expected = "Eficiencia: Media | Productividad: Media | Utilización: Óptima"
        assert workload.performance_summary == expected
    
    async def test_performance_summary_minimal(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test performance_summary con datos mínimos."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        # performance_summary devuelve un string, no un diccionario
        assert workload.performance_summary == "Sin métricas disponibles"


# Tests de relaciones eliminados - ahora centralizados en test_model_relationships.py
# Ver TestProjectWorkloadRelationship y TestEmployeeWorkloadRelationship en test_model_relationships.py


class TestWorkloadRepr:
    """Tests para representación del modelo Workload."""
    
    async def test_workload_repr(
        self,
        test_session: AsyncSession,
        sample_workload: Workload
    ):
        """Test representación string del workload."""
        repr_str = repr(sample_workload)
        
        assert "Workload" in repr_str
        assert str(sample_workload.id) in repr_str
        assert str(sample_workload.employee_id) in repr_str
        assert str(sample_workload.project_id) in repr_str
        assert str(sample_workload.date) in repr_str


class TestWorkloadEdgeCases:
    """Tests para casos extremos del modelo Workload."""
    
    async def test_workload_with_zero_planned_hours(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test workload con planned_hours cero."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('0.0'),
            actual_hours=Decimal('2.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.planned_hours == Decimal('0.0')
        assert workload.hours_variance == Decimal('2.0')  # actual - planned
        # calculate_efficiency_score retorna None cuando planned_hours es 0
        assert workload.calculate_efficiency_score() is None
    
    async def test_workload_with_high_decimal_precision(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test workload con alta precisión decimal."""
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=date(2024, 1, 15),
            week_number=3,
            month=1,
            year=2024,
            planned_hours=Decimal('8.123456'),
            actual_hours=Decimal('7.987654'),
            efficiency_score=Decimal('98.765432')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.planned_hours == Decimal('8.123456')
        assert workload.actual_hours == Decimal('7.987654')
        # efficiency_score se almacena con precisión de 2 decimales (Numeric(5, 2))
        assert workload.efficiency_score == Decimal('98.77')
        assert workload.hours_variance == -0.135802  # 7.987654 - 8.123456
    
    async def test_workload_future_date(
        self,
        test_session: AsyncSession,
        sample_employee: Employee,
        sample_project: Project
    ):
        """Test workload con fecha futura."""
        future_date = date(2025, 12, 31)
        
        workload = Workload(
            employee_id=sample_employee.id,
            project_id=sample_project.id,
            date=future_date,
            week_number=53,
            month=12,
            year=2025,
            planned_hours=Decimal('8.0')
        )
        
        test_session.add(workload)
        await test_session.flush()
        await test_session.refresh(workload)
        
        assert workload.date == future_date
        assert workload.get_quarter() == 4
        assert workload.is_weekend is False  # 31 de diciembre de 2025 es martes