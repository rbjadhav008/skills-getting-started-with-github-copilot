import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create a test client
client = TestClient(app)

# Original activities data for resetting (copy from app.py)
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Basketball training and games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu", "james@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Tennis skills training and friendly competitions",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
        "max_participants": 16,
        "participants": ["sarah@mergington.edu"]
    },
    "Art Studio": {
        "description": "Painting, drawing, and mixed media projects",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Drama Club": {
        "description": "Theater productions and acting workshops",
        "schedule": "Thursdays and Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["maya@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 14,
        "participants": ["andrew@mergington.edu", "jessica@mergington.edu"]
    },
    "Science Club": {
        "description": "Hands-on experiments and science projects",
        "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["ryan@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data before each test to ensure isolation."""
    from src.app import activities
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES)

def test_get_activities():
    """Test retrieving all activities."""
    # Arrange: No special setup needed (fixture handles data reset)
    
    # Act: Make GET request to /activities
    response = client.get("/activities")
    
    # Assert: Check response status and structure
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]

def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange: Define test data
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Check response and data update
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    
    # Verify the participant was added
    response2 = client.get("/activities")
    data = response2.json()
    assert email in data[activity_name]["participants"]

def test_signup_duplicate():
    """Test signing up for an activity when already signed up."""
    # Arrange: Use an email already in the activity
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in Chess Club
    
    # Act: Attempt to signup again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert: Check for error response
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]

def test_signup_activity_not_found():
    """Test signing up for a non-existent activity."""
    # Arrange: Use invalid activity name
    invalid_activity = "NonExistent Activity"
    email = "test@mergington.edu"
    
    # Act: Make POST request
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")
    
    # Assert: Check for 404 error
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_unregister_success():
    """Test successful unregistration from an activity."""
    # Arrange: Define test data
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Act: Make DELETE request to unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert: Check response and data update
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    
    # Verify the participant was removed
    response2 = client.get("/activities")
    data = response2.json()
    assert email not in data[activity_name]["participants"]

def test_unregister_not_signed_up():
    """Test unregistering when not signed up."""
    # Arrange: Use email not in the activity
    activity_name = "Chess Club"
    email = "notsigned@mergington.edu"
    
    # Act: Make DELETE request
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert: Check for error response
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]

def test_unregister_activity_not_found():
    """Test unregistering from a non-existent activity."""
    # Arrange: Use invalid activity name
    invalid_activity = "NonExistent Activity"
    email = "test@mergington.edu"
    
    # Act: Make DELETE request
    response = client.delete(f"/activities/{invalid_activity}/unregister?email={email}")
    
    # Assert: Check for 404 error
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_root_redirect():
    """Test that the root endpoint redirects to the static index page."""
    # Arrange: No special setup
    
    # Act: Make GET request to root without following redirects
    response = client.get("/", follow_redirects=False)
    
    # Assert: Check for redirect response
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]