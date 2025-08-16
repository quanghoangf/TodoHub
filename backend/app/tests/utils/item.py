from sqlmodel import Session

from app.domains.items.models import Item
from app.domains.items.schemas import ItemCreate
from app.domains.items.service import ItemService
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_item(db: Session) -> Item:
    user = create_random_user(db)
    assert user.id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    
    item_service = ItemService(db)
    item_public = item_service.create_item(item_in, user)
    
    # Return the actual Item model for tests
    from app.domains.items.repository import ItemRepository
    item_repo = ItemRepository(db)
    return item_repo.get_or_404(item_public.id)
