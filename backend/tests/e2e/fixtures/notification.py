import pytest
import random


@pytest.fixture
def notification_payload():
    """Sample notification payload with all fields."""
    return {
        "text": f"Test notification message {random.randint(1000, 9999)}",
        "status": "pending",
        "reportId": None
    }
