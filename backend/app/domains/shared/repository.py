"""Base repository pattern implementation."""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlmodel import Session, SQLModel, select

from app.core.exceptions import NotFoundError

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session
    
    def get(self, id: uuid.UUID) -> Optional[ModelType]:
        """Get entity by ID."""
        return self.session.get(self.model, id)
    
    def get_or_404(self, id: uuid.UUID) -> ModelType:
        """Get entity by ID or raise 404."""
        entity = self.get(id)
        if not entity:
            raise NotFoundError(f"{self.model.__name__} not found")
        return entity
    
    def get_multi(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple entities with pagination and filters."""
        query = select(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        return list(self.session.exec(query).all())
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters."""
        from sqlmodel import func
        
        query = select(func.count()).select_from(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        return self.session.exec(query).one()
    
    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Create new entity."""
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj
    
    def update(
        self, 
        *, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> ModelType:
        """Update existing entity."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        db_obj.sqlmodel_update(update_data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj
    
    def delete(self, *, id: uuid.UUID) -> ModelType:
        """Delete entity by ID."""
        obj = self.get_or_404(id)
        self.session.delete(obj)
        self.session.commit()
        return obj