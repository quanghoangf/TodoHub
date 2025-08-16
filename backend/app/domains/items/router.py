"""Items router."""

import uuid
from typing import Any

from fastapi import APIRouter

from app.core.container import ServiceContainerDep
from app.domains.items.schemas import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.domains.shared.dependencies import CurrentUser
from app.domains.shared.schemas import MessageResponse

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    container: ServiceContainerDep,
    current_user: CurrentUser, 
    skip: int = 0, 
    limit: int = 100
) -> Any:
    """Retrieve items."""
    return container.item_service.get_items(current_user, skip=skip, limit=limit)


@router.get("/{id}", response_model=ItemPublic)
def read_item(
    container: ServiceContainerDep,
    current_user: CurrentUser, 
    id: uuid.UUID
) -> Any:
    """Get item by ID."""
    return container.item_service.get_item_by_id(id, current_user)


@router.post("/", response_model=ItemPublic)
def create_item(
    *, 
    container: ServiceContainerDep,
    current_user: CurrentUser, 
    item_in: ItemCreate
) -> Any:
    """Create new item."""
    return container.item_service.create_item(item_in, current_user)


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    container: ServiceContainerDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """Update an item."""
    return container.item_service.update_item(id, item_in, current_user)


@router.delete("/{id}", response_model=MessageResponse)
def delete_item(
    container: ServiceContainerDep,
    current_user: CurrentUser, 
    id: uuid.UUID
) -> MessageResponse:
    """Delete an item."""
    return container.item_service.delete_item(id, current_user)