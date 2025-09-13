from sqlalchemy.orm import joinedload
from planificador.repositories.base_repository import BaseRepository
from planificador.models.project import Project


class RelationshipOperations(BaseRepository):
    """
    Módulo para gestionar las relaciones del modelo Project.
    """

    def __init__(self, query_builder):
        self.query_builder = query_builder

    def with_client(self, query):
        """
        Añade la carga de la relación con el cliente.
        """
        return self.query_builder.with_client(query)

    def with_assignments(self, query):
        """
        Añade la carga de la relación con las asignaciones.
        """
        return self.query_builder.with_assignments(query)

    def with_full_details(self, query):
        """
        Añade la carga de todas las relaciones principales.
        """
        return self.query_builder.with_full_details(query)