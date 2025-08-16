"""Import all domain models to ensure SQLModel registration."""

# Import all models to ensure they are registered with SQLModel
from app.domains.items.models import Item  # noqa
from app.domains.users.models import User  # noqa

__all__ = ["User", "Item"]