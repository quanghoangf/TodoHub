"""Example test showing dependency injection benefits."""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.core.container import ServiceContainer
from app.core.protocols import UserServiceProtocol
from app.main import app


class MockUserService:
    """Mock user service for testing."""
    
    def get_users(self, skip: int = 0, limit: int = 100):
        return {
            "data": [{"id": "123", "email": "test@example.com"}],
            "count": 1
        }


def test_dependency_injection_with_mocks():
    """Test showing how easy it is to mock services with proper DI."""
    
    # Create a mock service container
    mock_container = Mock(spec=ServiceContainer)
    mock_container.user_service = MockUserService()
    
    # Override the dependency
    from app.core.container import get_service_container
    
    def get_mock_container():
        return mock_container
    
    app.dependency_overrides[get_service_container] = get_mock_container
    
    # Test with mocked dependencies
    client = TestClient(app)
    
    # This would call the mock service instead of real service
    # response = client.get("/api/v1/users/", headers=auth_headers)
    # assert response.status_code == 200
    
    # Clean up
    app.dependency_overrides.clear()


def test_service_isolation():
    """Test showing service isolation benefits."""
    
    # Each test can have its own service configuration
    # Services are properly scoped to request lifecycle
    # No global state pollution between tests
    
    pass  # Placeholder for actual test implementation