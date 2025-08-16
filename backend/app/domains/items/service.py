"""Item service."""

import uuid

from sqlmodel import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.domains.items.models import Item
from app.domains.items.repository import ItemRepository
from app.domains.items.schemas import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.domains.shared.schemas import MessageResponse
from app.domains.users.models import User


class ItemService:
    """Item service handling item business logic."""
    
    def __init__(self, session: Session):
        self.session = session
        self.item_repository = ItemRepository(session)
    
    def get_items(self, current_user: User, skip: int = 0, limit: int = 100) -> ItemsPublic:
        """Get paginated list of items."""
        if current_user.is_superuser:
            # Superusers can see all items
            items = self.item_repository.get_multi(skip=skip, limit=limit)
            count = self.item_repository.count()
        else:
            # Regular users can only see their own items
            items = self.item_repository.get_by_owner(
                owner_id=current_user.id, skip=skip, limit=limit
            )
            count = self.item_repository.count_by_owner(owner_id=current_user.id)
        
        return ItemsPublic(data=items, count=count)
    
    def get_item_by_id(self, item_id: uuid.UUID, current_user: User) -> ItemPublic:
        """Get item by ID with permission check."""
        item = self.item_repository.get_or_404(item_id)
        
        # Check permissions: owner or superuser
        if not current_user.is_superuser and item.owner_id != current_user.id:
            raise ForbiddenError("Not enough permissions")
        
        return ItemPublic.model_validate(item)
    
    def create_item(self, item_data: ItemCreate, current_user: User) -> ItemPublic:
        """Create new item."""
        # Create item with current user as owner
        item_dict = item_data.model_dump()
        item_dict["owner_id"] = current_user.id
        
        db_item = Item(**item_dict)
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        
        return ItemPublic.model_validate(db_item)
    
    def update_item(
        self, item_id: uuid.UUID, item_data: ItemUpdate, current_user: User
    ) -> ItemPublic:
        """Update item by ID."""
        item = self.item_repository.get_or_404(item_id)
        
        # Check permissions: owner or superuser
        if not current_user.is_superuser and item.owner_id != current_user.id:
            raise ForbiddenError("Not enough permissions")
        
        updated_item = self.item_repository.update(db_obj=item, obj_in=item_data)
        return ItemPublic.model_validate(updated_item)
    
    def delete_item(self, item_id: uuid.UUID, current_user: User) -> MessageResponse:
        """Delete item by ID."""
        item = self.item_repository.get_or_404(item_id)
        
        # Check permissions: owner or superuser
        if not current_user.is_superuser and item.owner_id != current_user.id:
            raise ForbiddenError("Not enough permissions")
        
        self.item_repository.delete(id=item_id)
        return MessageResponse(message="Item deleted successfully")