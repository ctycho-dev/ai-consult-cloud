import pytest


@pytest.fixture
def report_payload(test_camera):
    """Report payload with all fields."""
    return {
        "cameraId": test_camera["id"],
        "fillPercentage": 75.5,
        "compliancePercentage": 92.3,
        "screenshotS3Url": "https://s3.example.com/screenshot.jpg",
        "analysisText": "Test analysis text"
    }


@pytest.fixture
def report_payload_minimal(test_camera):
    """Sample report payload with only required fields."""
    return {
        "cameraId": test_camera["id"]
    }


@pytest.fixture
def report_update_payload():
    """Sample report update payload."""
    return {
        "fillPercentage": 85.0,
        "compliancePercentage": 95.0,
        "analysisText": "Updated analysis text"
    }
