"""
Pytest configuration and fixtures for FastAPI testing
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Sample activities data for testing"""
    return {
        "Test Activity": {
            "description": "A test activity for testing purposes",
            "schedule": "Test schedule",
            "max_participants": 5,
            "participants": ["test1@mergington.edu", "test2@mergington.edu"]
        },
        "Empty Activity": {
            "description": "An empty activity with no participants",
            "schedule": "Empty schedule", 
            "max_participants": 10,
            "participants": []
        }
    }


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    from src.app import activities
    
    # Store original activities
    original_activities = activities.copy()
    
    yield
    
    # Restore original activities after test
    activities.clear()
    activities.update(original_activities)