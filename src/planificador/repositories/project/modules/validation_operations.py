from typing import Any, Dict

from loguru import logger
from sqlalchemy import select

from planificador.exceptions.base import ValidationError
from planificador.models.project import Project
from planificador.repositories.base_repository import BaseRepository


class ValidationOperations(BaseRepository):
    """
    Módulo para validar datos de proyectos.
    """

    def __init__(self, session):
        self.session = session
        self._logger = logger

    async def validate_project_creation(self, data: Dict[str, Any]):
        """
        Valida los datos para la creación de un nuevo proyecto.
        """
        await self._validate_required_fields(data)
        await self._validate_unique_fields(data)
        await self._validate_date_logic(data)

    async def validate_project_update(self, project_id: int, data: Dict[str, Any]):
        """
        Valida los datos para la actualización de un proyecto.
        """
        if "reference" in data:
            await self._validate_unique_field_on_update(
                project_id, "reference", data["reference"]
            )
        if "trigram" in data:
            await self._validate_unique_field_on_update(
                project_id, "trigram", data["trigram"]
            )
        if "start_date" in data or "end_date" in data:
            # Lógica simplificada: se necesitaría el proyecto para una validación completa
            pass

    async def _validate_required_fields(self, data: Dict[str, Any]):
        """
        Valida que los campos obligatorios estén presentes.
        """
        required_fields = ["name", "reference", "trigram", "client_id"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValidationError(
                f"Faltan campos obligatorios: {', '.join(missing_fields)}"
            )

    async def _validate_unique_fields(self, data: Dict[str, Any]):
        """
        Valida que los campos únicos no existan en la base de datos.
        """
        if await self._is_field_duplicate("reference", data["reference"]):
            raise ValidationError(
                f"La referencia '{data['reference']}' ya existe."
            )
        if await self._is_field_duplicate("trigram", data["trigram"]):
            raise ValidationError(f"El trigrama '{data['trigram']}' ya existe.")

    async def _validate_date_logic(self, data: Dict[str, Any]):
        """
        Valida la lógica de las fechas (ej: fecha de inicio antes que fecha de fin).
        """
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise ValidationError(
                "La fecha de inicio no puede ser posterior a la fecha de fin."
            )

    async def _is_field_duplicate(
        self, field_name: str, value: Any, project_id: int = None
    ) -> bool:
        """
        Verifica si un valor de campo ya existe en la base de datos, excluyendo un ID de proyecto si se proporciona.
        """
        query = select(Project).where(getattr(Project, field_name) == value)
        if project_id:
            query = query.where(Project.id != project_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def _validate_unique_field_on_update(
        self, project_id: int, field_name: str, value: Any
    ):
        """
        Valida un campo único al actualizar, asegurándose de que no pertenezca a otro proyecto.
        """
        if await self._is_field_duplicate(field_name, value, project_id):
            raise ValidationError(f"El campo '{field_name}' con valor '{value}' ya está en uso.")

    async def reference_exists(
        self, reference: str, exclude_id: int = None
    ) -> bool:
        """
        Verifica si una referencia de proyecto ya existe en la base de datos.
        
        Args:
            reference: Referencia del proyecto a verificar
            exclude_id: ID del proyecto a excluir de la búsqueda (para actualizaciones)
            
        Returns:
            bool: True si la referencia existe, False en caso contrario
        """
        return await self._is_field_duplicate("reference", reference, exclude_id)

    async def trigram_exists(
        self, trigram: str, exclude_id: int = None
    ) -> bool:
        """
        Verifica si un trigrama de proyecto ya existe en la base de datos.
        
        Args:
            trigram: Trigrama del proyecto a verificar
            exclude_id: ID del proyecto a excluir de la búsqueda (para actualizaciones)
            
        Returns:
            bool: True si el trigrama existe, False en caso contrario
        """
        return await self._is_field_duplicate("trigram", trigram, exclude_id)