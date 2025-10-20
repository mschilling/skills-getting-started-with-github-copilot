"""
Test cases for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestAPI:
    """Test cases for API endpoints"""

    def test_root_redirect(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that we have some activities
        assert len(data) > 0
        
        # Check structure of first activity
        first_activity = list(data.values())[0]
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for field in required_fields:
            assert field in first_activity

    def test_get_activities_content(self, client):
        """Test that activities contain expected data structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check specific activities exist
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Check Chess Club details
        chess_club = data["Chess Club"]
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Test cases for activity signup functionality"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify student was added to activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_duplicate_participant(self, client):
        """Test signup when student is already registered"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "multistudent@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]


class TestUnregister:
    """Test cases for activity unregister functionality"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # Verify student is initially registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Unregister the student
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify student was removed from activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistration from non-existent activity"""
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_not_registered(self, client):
        """Test unregistration when student is not registered"""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_signup_and_unregister_flow(self, client):
        """Test complete signup and unregister flow"""
        email = "flowtest@mergington.edu"
        activity = "Programming Class"
        
        # First, sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify registration
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Then, unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]


class TestDataIntegrity:
    """Test cases for data integrity and edge cases"""

    def test_special_characters_in_email(self, client):
        """Test signup with special characters in email"""
        email = "test.student.123@mergington.edu"  # Use dots instead of + to avoid URL encoding issues
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify in activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]

    def test_activity_with_spaces(self, client):
        """Test signup for activity with spaces in name"""
        email = "spacetest@mergington.edu"
        activity = "Programming Class"  # Has space in name
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200

    def test_case_sensitivity(self, client):
        """Test that activity names are case sensitive"""
        email = "casetest@mergington.edu"
        
        # Try with wrong case
        response = client.post("/activities/chess club/signup?email=" + email)
        assert response.status_code == 404
        
        # Try with correct case
        response = client.post("/activities/Chess Club/signup?email=" + email)
        assert response.status_code == 200

    def test_empty_participants_list(self, client):
        """Test activities with no participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Find an activity with empty participants list
        empty_activities = [name for name, details in data.items() if not details["participants"]]
        
        if empty_activities:
            activity_name = empty_activities[0]
            activity_data = data[activity_name]
            assert activity_data["participants"] == []
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0