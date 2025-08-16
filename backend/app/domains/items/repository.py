"""Item repository."""

import uuid
from typing import List

from sqlmodel import Session

from app.domains.items.models import Item
from app.domains.items.schemas import ItemCreate, ItemUpdate
from app.domains.shared.repository import BaseRepository


class ItemRepository(BaseRepository[Item, ItemCreate, ItemUpdate]):
    """Item repository with item-specific operations."""
    
    def __init__(self, session: Session):
        super().__init__(Item, session)
    
    def get_by_owner(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Item]:
        """Get items by owner ID."""
        return self.get_multi(skip=skip, limit=limit, filters={"owner_id": owner_id})
    
    def count_by_owner(self, owner_id: uuid.UUID) -> int:
        """Count items by owner ID."""
        return self.count(filters={"owner_id": owner_id})