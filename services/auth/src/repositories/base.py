from abc import ABC
from typing import Generic, Type, TypeVar, get_args

from pydantic import BaseModel
from sqlalchemy import delete, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class RepositoryDB(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Abstract base class for database repositories.

    Provides common CRUD operations for SQLAlchemy models using
    Pydantic schemas.
    """

    def __init__(self):
        """
        Initialize the repository by dynamically determining the model type.
        """
        self._model: Type[ModelType] = get_args(self.__orig_bases__[0])[0]  # type: ignore

    async def get(self, db: AsyncSession, pk: int) -> ModelType | None:
        """
        Retrieve a single record by its primary key.

        Args:
            db (AsyncSession): The database session.
            pk (int): The primary key of the record.

        Returns:
            Optional[ModelType]: The retrieved record, or None if not found.
        """
        return await db.get(self._model, pk)

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record in the database.

        Args:
            db (AsyncSession): The database session.
            obj_in (CreateSchemaType): The input data for creating the record.

        Returns:
            ModelType: The newly created record.

        Raises:
            ValueError: If the record could not be created.
        """
        query = insert(self._model).values(**obj_in.model_dump()).returning(self._model)
        result = await db.scalar(query)
        await db.flush()

        if result is None:
            raise ValueError("Failed to create the object.")
        return result

    async def create_many(
        self, db: AsyncSession, objs_in: list[CreateSchemaType]
    ) -> list[ModelType]:
        """
        Create multiple records in the database.

        Args:
            db (AsyncSession): The database session.
            objs_in (list[CreateSchemaType]): A list of input data for
            creating the records.

        Returns:
            list[ModelType]: A list of newly created records.
        """
        values = [obj.model_dump() for obj in objs_in]
        query = insert(self._model).values(values).returning(self._model)
        results = await db.scalars(query)
        await db.flush()
        return list(results)

    async def update(self, db: AsyncSession, pk: int, obj_in: UpdateSchemaType) -> ModelType:
        """
        Update an existing record in the database.

        Args:
            db (AsyncSession): The database session.
            pk (int): The primary key of the record to update.
            obj_in (UpdateSchemaType): The input data for updating the record.

        Returns:
            ModelType: The updated record.

        Raises:
            ValueError: If the record could not be updated.
        """
        query = (
            update(self._model)
            .where(self._model.id == pk)
            .values(**obj_in.model_dump(exclude_unset=True))
            .returning(self._model)
        )
        result = await db.scalar(query)
        await db.flush()

        if result is None:
            raise ValueError("Failed to update the object.")
        return result

    async def delete(self, db: AsyncSession, pk: int) -> None:
        """
        Delete a record from the database by its primary key.

        Args:
            db (AsyncSession): The database session.
            pk (int): The primary key of the record to delete.
        """
        statement = delete(self._model).where(self._model.id == pk)
        await db.execute(statement)
        await db.flush()
