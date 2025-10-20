"""
Test cases for the activities data model and business logic
"""

import pytest
from src.app import activities


class TestActivitiesData:
    """Test cases for activities data structure and validation"""

    def test_activities_structure(self):
        """Test that all activities have required fields"""
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str), f"Activity name should be string: {activity_name}"
            assert len(activity_name) > 0, "Activity name should not be empty"
            
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"

    def test_max_participants_positive(self):
        """Test that max_participants is always positive"""
        for activity_name, activity_data in activities.items():
            max_participants = activity_data["max_participants"]
            assert isinstance(max_participants, int), f"max_participants should be int in {activity_name}"
            assert max_participants > 0, f"max_participants should be positive in {activity_name}"

    def test_participants_list_format(self):
        """Test that participants is always a list of email strings"""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            assert isinstance(participants, list), f"participants should be list in {activity_name}"
            
            for participant in participants:
                assert isinstance(participant, str), f"participant should be string in {activity_name}"
                assert "@" in participant, f"participant should be email format in {activity_name}: {participant}"
                assert participant.endswith("@mergington.edu"), f"participant should use school domain in {activity_name}: {participant}"

    def test_no_duplicate_participants(self):
        """Test that no activity has duplicate participants"""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            unique_participants = set(participants)
            assert len(participants) == len(unique_participants), f"Duplicate participants found in {activity_name}"

    def test_participants_within_limit(self):
        """Test that current participants don't exceed max_participants"""
        for activity_name, activity_data in activities.items():
            current_count = len(activity_data["participants"])
            max_count = activity_data["max_participants"]
            assert current_count <= max_count, f"Too many participants in {activity_name}: {current_count}/{max_count}"

    def test_activity_descriptions(self):
        """Test that all activities have meaningful descriptions"""
        for activity_name, activity_data in activities.items():
            description = activity_data["description"]
            assert isinstance(description, str), f"description should be string in {activity_name}"
            assert len(description) > 10, f"description too short in {activity_name}: {description}"
            assert description[0].isupper(), f"description should start with capital letter in {activity_name}"

    def test_activity_schedules(self):
        """Test that all activities have schedule information"""
        for activity_name, activity_data in activities.items():
            schedule = activity_data["schedule"]
            assert isinstance(schedule, str), f"schedule should be string in {activity_name}"
            assert len(schedule) > 5, f"schedule too short in {activity_name}: {schedule}"

    def test_activity_categories(self):
        """Test that we have different categories of activities"""
        activity_names = list(activities.keys())
        
        # Check for sports activities
        sports_keywords = ["soccer", "basketball", "gym", "team", "sport"]
        sports_activities = [name for name in activity_names 
                           if any(keyword.lower() in name.lower() for keyword in sports_keywords)]
        assert len(sports_activities) > 0, "Should have sports activities"
        
        # Check for intellectual activities  
        intellectual_keywords = ["math", "science", "chess", "programming", "olympiad"]
        intellectual_activities = [name for name in activity_names 
                                 if any(keyword.lower() in name.lower() for keyword in intellectual_keywords)]
        assert len(intellectual_activities) > 0, "Should have intellectual activities"
        
        # Check for artistic activities
        artistic_keywords = ["art", "drama", "workshop"]
        artistic_activities = [name for name in activity_names 
                             if any(keyword.lower() in name.lower() for keyword in artistic_keywords)]
        assert len(artistic_activities) > 0, "Should have artistic activities"


class TestBusinessLogic:
    """Test cases for business logic validation"""

    def test_minimum_activities_available(self):
        """Test that we have a reasonable number of activities"""
        assert len(activities) >= 5, f"Should have at least 5 activities, found {len(activities)}"

    def test_reasonable_max_participants(self):
        """Test that max_participants values are reasonable"""
        for activity_name, activity_data in activities.items():
            max_participants = activity_data["max_participants"]
            assert 5 <= max_participants <= 50, f"max_participants should be between 5-50 in {activity_name}: {max_participants}"

    def test_school_email_domain(self):
        """Test that all participants use the school email domain"""
        school_domain = "@mergington.edu"
        
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert participant.endswith(school_domain), f"Invalid email domain in {activity_name}: {participant}"

    def test_unique_activity_names(self):
        """Test that all activity names are unique (case insensitive)"""
        activity_names_lower = [name.lower() for name in activities.keys()]
        unique_names_lower = set(activity_names_lower)
        assert len(activity_names_lower) == len(unique_names_lower), "Duplicate activity names found"

    def test_activities_have_variety(self):
        """Test that activities offer variety in schedules and sizes"""
        max_participants_values = [data["max_participants"] for data in activities.values()]
        unique_max_values = set(max_participants_values)
        
        # Should have variety in group sizes
        assert len(unique_max_values) > 1, "Activities should have different max_participants values"
        
        # Check for different schedule patterns
        schedules = [data["schedule"] for data in activities.values()]
        days_mentioned = []
        for schedule in schedules:
            schedule_lower = schedule.lower()
            if "monday" in schedule_lower: days_mentioned.append("monday")
            if "tuesday" in schedule_lower: days_mentioned.append("tuesday") 
            if "wednesday" in schedule_lower: days_mentioned.append("wednesday")
            if "thursday" in schedule_lower: days_mentioned.append("thursday")
            if "friday" in schedule_lower: days_mentioned.append("friday")
        
        unique_days = set(days_mentioned)
        assert len(unique_days) >= 3, f"Activities should span multiple days, found: {unique_days}"