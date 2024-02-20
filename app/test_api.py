from fastapi.testclient import TestClient
from app.main import app  # This works when test_api.py is in the same directory as main.py


client = TestClient(app)

# `GET /users`

def test_get_all_users_with_default_parameters():
    """
    Test fetching all users with default parameters.
    """
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 100

def test_pagination_with_skip_and_limit():
    """
    Test pagination by using the skip and limit query parameters.
    """
    # Fetch the first 5 users
    response_first_5 = client.get("/users?skip=0&limit=5")
    assert response_first_5.status_code == 200
    data_first_5 = response_first_5.json()
    assert len(data_first_5) == 5
    
    # Fetch the next 5 users
    response_next_5 = client.get("/users?skip=5&limit=5")
    assert response_next_5.status_code == 200
    data_next_5 = response_next_5.json()
    assert len(data_next_5) == 5
    
    # Ensure that the two sets are different, implying pagination works
    for user_first_5, user_next_5 in zip(data_first_5, data_next_5):
        assert user_first_5['email'] != user_next_5['email']

def test_checked_in_only_filter():
    """
    Test the checked_in_only filter.
    """
    # Assuming you have some logic to check in a user or ensure some users are checked in within your test setup
    # This test fetches only checked-in users
    response = client.get("/users?checked_in_only=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # This assertion depends on having known checked-in users in your test database
    assert len(data) == 0  # Adjust based on your test data setup
    for user in data:
        assert user['checked_in'] is True 

def test_get_users_invalid_limit():
    """
    Test fetching users with an invalid limit parameter.
    """
    response = client.get("/users?limit=-1")
    assert response.status_code == 400

# `GET /users/{user_id}`
def test_get_user_by_valid_id():
    """
    Test fetching a user by a valid user ID.
    """
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    
    # Validate the response structure matches the expected format
    assert 'name' in data
    assert 'company' in data
    assert 'email' in data
    assert 'phone' in data
    assert 'checked_in' in data
    assert 'skills' in data
    assert isinstance(data['skills'], list)

    # Additional checks can be performed based on known data for user ID 1
    assert data['name'] == "Breanna Dillon"
    assert data['email'] == "lorettabrown@example.net"

def test_get_user_by_invalid_id():
    """
    Test fetching a user by an invalid/non-existent user ID.
    """
    # Assuming an ID that does not exist in the database
    response = client.get("/users/9999")
    assert response.status_code == 404
    data = response.json()
    assert 'detail' in data

def test_get_user_response_structure():
    """
    Test the structure of the response for a valid user request.
    """
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    
    # Validate that the response contains all the expected keys
    expected_keys = {"name", "company", "email", "phone", "checked_in", "skills"}
    assert all(key in data for key in expected_keys)

    # Validate the structure of the skills list
    if data['skills']:  # If there are skills
        first_skill = data['skills'][0]
        assert 'skill' in first_skill and 'rating' in first_skill


# `PUT /users/{user_id}`
def test_update_user_phone():
    """
    Test updating the phone number of an existing user.
    """
    # Save current state
    original_response = client.get("/users/1")
    original_data = original_response.json()

    # Perform update
    user_update = {"phone": "123-456-7890"}
    update_response = client.put("/users/1", json=user_update)
    assert update_response.status_code == 200
    
    # Validate update
    updated_response = client.get("/users/1")
    updated_data = updated_response.json()
    assert updated_data['phone'] == "123-456-7890"

    # Restore original state
    restore_response = client.put("/users/1", json=original_data)
    assert restore_response.status_code == 200


def test_add_new_skill_to_user():
    """
    Test adding a new skill to the user's existing skills.
    """
    new_skill = {"skills": [{"skill": "Python", "rating": 5}]}
    response = client.put("/users/1", json=new_skill)
    assert response.status_code == 200
    data = response.json()
    assert any(skill['skill'] == "Python" for skill in data['skills'])

def test_update_existing_skill_rating():
    """
    Test updating the rating of an existing skill for a user.
    """
    updated_skill = {"skills": [{"skill": "Swift", "rating": 5}]}
    response = client.put("/users/1", json=updated_skill)
    assert response.status_code == 200
    data = response.json()
    assert any(skill['skill'] == "Swift" and skill['rating'] == 5 for skill in data['skills'])

def test_update_user_with_invalid_rating():
    """
    Test updating a user with an invalid skill rating.
    """
    invalid_rating = {"skills": [{"skill": "Python", "rating": 6}]}  # Assuming ratings must be between 1 and 5
    response = client.put("/users/1", json=invalid_rating)
    assert response.status_code == 400

def test_update_user_with_nonexistent_id():
    """
    Test updating a user with a non-existent ID.
    """
    user_update = {"phone": "987-654-3210"}
    response = client.put("/users/9999", json=user_update)  # Assuming user ID 9999 does not exist
    assert response.status_code == 404

def test_update_user_with_multiple_fields():
    """
    Test updating a user with multiple fields (e.g., name, email, and a new skill).
    """
    update_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "skills": [{"skill": "Docker", "rating": 4}]
    }
    response = client.put("/users/100", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == "John Doe"
    assert data['email'] == "john.doe@example.com"
    assert any(skill['skill'] == "Docker" for skill in data['skills'])


# `GET /skills`
def test_get_all_skills():
    """
    Test fetching all skills without any filters.
    """
    response = client.get("/skills")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check that each item in the response has the expected keys
    for item in data:
        assert 'skill_name' in item and 'frequency' in item

def test_get_skills_with_frequency_range():
    """
    Test fetching skills filtered by a specific frequency range.
    """
    min_freq = 10
    max_freq = 15
    response = client.get(f"/skills/?min_frequency={min_freq}&max_frequency={max_freq}")
    assert response.status_code == 200
    data = response.json()
    # Verify that all returned skills fall within the specified frequency range
    for skill in data:
        assert min_freq <= skill['frequency'] <= max_freq

def test_get_skills_with_min_frequency_only():
    """
    Test fetching skills with only the minimum frequency specified.
    """
    min_freq = 5
    response = client.get(f"/skills/?min_frequency={min_freq}")
    assert response.status_code == 200
    data = response.json()
    # Ensure that all skills have a frequency greater than or equal to min_freq
    for skill in data:
        assert skill['frequency'] >= min_freq

def test_get_skills_with_max_frequency_only():
    """
    Test fetching skills with only the maximum frequency specified.
    """
    max_freq = 20
    response = client.get(f"/skills/?max_frequency={max_freq}")
    assert response.status_code == 200
    data = response.json()
    # Ensure that all skills have a frequency less than or equal to max_freq
    for skill in data:
        assert skill['frequency'] <= max_freq

def test_get_skills_with_invalid_frequency_range():
    """
    Test fetching skills with an invalid frequency range (e.g., min_frequency > max_frequency).
    """
    response = client.get("/skills/?min_frequency=15&max_frequency=10")
    # Assuming your API validates the query parameters and returns a 400 for invalid ranges
    assert response.status_code == 400


# `PUT /users/{user_id}/checkin`
    
def test_check_in_user():
    """
    Test checking in a user successfully.
    """
    # Assuming user_id 1 is not checked in; adjust as necessary for your test setup.
    response = client.put("/users/1/checkin")
    assert response.status_code == 200
    data = response.json()
    assert data['checked_in'] == True, "User was not checked in successfully."

def test_check_in_already_checked_in_user():
    """
    Test attempting to check in a user who is already checked in.
    """
    # Ensure the user is checked in first. This might be redundant if the user is already checked in.
    client.put("/users/1/checkin")
    
    # Attempt to check in the user again
    second_response = client.put("/users/1/checkin")
    assert second_response.status_code == 400, "Expected a 400 Bad Request for already checked-in user."

def test_check_in_non_existent_user():
    """
    Test attempting to check in a non-existent user.
    """
    # Assuming user_id 9999 does not exist
    response = client.put("/users/9999/checkin")
    assert response.status_code == 404, "Expected a 404 Not Found for a non-existent user."


# `POST /scan`
def test_scan_user_into_event():
    """
    Test scanning a user into an event successfully.
    """
    # Setup: Ensure the user and event exist and the user is not already scanned into this event.
    user_id = 1
    event_id = 1

    response = client.post(f"/scan/?user_id={user_id}&event_id={event_id}")
    assert response.status_code == 200
    data = response.json()
    assert data['message'] == "User scanned successfully", "Expected success message after scanning."

def test_scan_user_into_nonexistent_event():
    """
    Test scanning a user into a nonexistent event.
    """
    # Assuming user_id 1 exists but event_id 9999 does not
    user_id = 1
    event_id = 9999

    response = client.post(f"/scan/?user_id={user_id}&event_id={event_id}")
    # Assuming your API returns a 404 Not Found for nonexistent events
    assert response.status_code == 404, "Expected a 404 Not Found for a nonexistent event."

def test_scan_nonexistent_user_into_event():
    """
    Test scanning a nonexistent user into an event.
    """
    # Assuming user_id 9999 does not exist but event_id 1 does
    user_id = 9999
    event_id = 1

    response = client.post(f"/scan/?user_id={user_id}&event_id={event_id}")
    # Assuming your API returns a 404 Not Found for nonexistent users
    assert response.status_code == 404, "Expected a 404 Not Found for a nonexistent user."

def test_scan_already_scanned_user():
    """
    Test scanning a user who is already scanned into the event.
    """
    # Setup: Ensure the user is already scanned into the event.
    # This might require calling the POST /scan endpoint or setting up the state directly in the database.
    user_id = 2
    event_id = 1
    # Initial scan - assuming this setup is necessary for the test and succeeds.
    client.post(f"/scan/?user_id={user_id}&event_id={event_id}")

    # Attempt to scan again
    second_response = client.post(f"/scan/?user_id={user_id}&event_id={event_id}")
    # Assuming your API returns a 400 Bad Request for scanning an already scanned user
    assert second_response.status_code == 400, "Expected a 400 Bad Request for scanning an already scanned user."


# `GET /users/{user_id}/events/`
def test_retrieve_events_for_user():
    """
    Test retrieving events for a user who has been scanned into events.
    """
    # Assuming user_id 1 has been scanned into at least one event; adjust as necessary.
    user_id = 1

    response = client.get(f"/users/{user_id}/events/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list), "Expected a list of events"
    # Further checks could be added to verify the content of the events, such as:
    if data:  # If there are any events returned
        assert 'name' in data[0]
        assert 'description' in data[0]
        assert 'event_id' in data[0]

def test_retrieve_events_for_nonexistent_user():
    """
    Test retrieving events for a nonexistent user.
    """
    # Assuming user_id 9999 does not exist.
    user_id = 9999

    response = client.get(f"/users/{user_id}/events/")
    # Assuming your API returns a 404 Not Found for nonexistent users.
    assert response.status_code == 404, "Expected a 404 Not Found for a nonexistent user."

def test_user_with_no_events():
    """
    Test retrieving events for a user who has not been scanned into any events.
    """
    # Assuming user_id 2 exists but has not been scanned into any events; adjust as necessary.
    user_id = 5

    response = client.get(f"/users/{user_id}/events/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list), "Expected a list of events"
    assert len(data) == 0, "Expected no events for a user with no scans"


# `POST /hardware/{hardware_id}/signout`
def test_sign_out_hardware_success():
    """
    Test successfully signing out a piece of hardware by a user.
    """
    hardware_id = 1  # Assuming this hardware exists and is available for sign out
    user_id = 1  # Assuming this user exists

    response = client.post(f"/hardware/{hardware_id}/signout/?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "signed out by user" in data['message'], "Hardware was not signed out successfully."

def test_sign_out_nonexistent_hardware():
    """
    Test attempting to sign out a piece of hardware that does not exist.
    """
    hardware_id = 9999  # Assuming this hardware does not exist
    user_id = 1  # Assuming this user exists

    response = client.post(f"/hardware/{hardware_id}/signout/?user_id={user_id}")
    # Assuming your API returns a 404 Not Found for nonexistent hardware
    assert response.status_code == 404, "Expected a 404 Not Found for nonexistent hardware."

def test_sign_out_hardware_by_nonexistent_user():
    """
    Test attempting to sign out hardware by a user that does not exist.
    """
    hardware_id = 1  # Assuming this hardware exists
    user_id = 9999  # Assuming this user does not exist

    response = client.post(f"/hardware/{hardware_id}/signout/?user_id={user_id}")
    # Assuming your API returns a 404 Not Found for nonexistent users
    assert response.status_code == 404, "Expected a 404 Not Found for nonexistent user."

def test_sign_out_already_signed_out_hardware():
    """
    Test attempting to sign out hardware that is already signed out.
    """
    # Setup: Ensure the hardware is signed out first.
    hardware_id = 1
    user_id = 1
    # Initial sign out
    client.post(f"/hardware/{hardware_id}/signout/?user_id={user_id}")

    # Attempt to sign out again
    second_response = client.post(f"/hardware/{hardware_id}/signout/?user_id={user_id}")
    # Assuming your API handles this scenario with a specific status code or message
    assert second_response.status_code == 400, "Expected a failure when signing out already signed-out hardware."


# `POST /hardware/{hardware_id}/return`
def test_return_hardware_success():
    """
    Test successfully returning a piece of hardware.
    """
    hardware_id = 1  # Assuming this hardware was previously signed out
    user_id = 1  # Assuming this user exists and had signed out the hardware
    
    # First, ensure the hardware is signed out to make the return meaningful
    client.post(f"/hardware/{hardware_id}/signout/?user_id={user_id}")
    
    # Now, attempt to return the hardware
    response = client.post(f"/hardware/{hardware_id}/return")
    assert response.status_code == 200
    data = response.json()
    assert "returned" in data['message'], "Hardware was not returned successfully."

def test_return_nonexistent_hardware():
    """
    Test attempting to return a piece of hardware that does not exist.
    """
    hardware_id = 9999  # Assuming this hardware does not exist

    response = client.post(f"/hardware/{hardware_id}/return")
    # Assuming your API returns a 404 Not Found for nonexistent hardware
    assert response.status_code == 404, "Expected a 404 Not Found for nonexistent hardware."

def test_return_hardware_not_signed_out():
    """
    Test attempting to return hardware that is not signed out.
    """
    hardware_id = 2  # Assuming this hardware exists but is not currently signed out
    
    response = client.post(f"/hardware/{hardware_id}/return")
    # Adjust the assertion based on your API's expected behavior in this scenario
    # For example, if your API returns a specific message or status code for hardware not signed out:
    assert response.status_code == 400, "Expected a failure when returning hardware not signed out."

# `GET /hacker/{user_id}/dashboard`

def test_retrieve_dashboard_for_existing_user():
    """
    Test retrieving dashboard information for an existing user.
    """
    user_id = 1  # Assuming this user exists; adjust as necessary.
    
    response = client.get(f"/hacker/{user_id}/dashboard")
    assert response.status_code == 200
    data = response.json()
    
    # Check if the response includes necessary keys
    assert 'user_info' in data, "User info not found in dashboard data."
    assert 'signed_out_hardware' in data, "Signed out hardware list not found in dashboard data."
    assert 'checked_in_events' in data, "Checked in events list not found in dashboard data."
    
    # Optionally, validate the structure of the user_info, signed_out_hardware, and checked_in_events
    assert 'name' in data['user_info'], "User name not found in user info."
    assert isinstance(data['signed_out_hardware'], list), "Signed out hardware should be a list."
    assert isinstance(data['checked_in_events'], list), "Checked in events should be a list."


def test_retrieve_dashboard_for_nonexistent_user():
    """
    Test retrieving dashboard information for a nonexistent user.
    """
    user_id = 9999  # Assuming this user does not exist
    
    response = client.get(f"/hacker/{user_id}/dashboard")
    # Assuming your API returns a 404 Not Found for nonexistent users
    assert response.status_code == 404, "Expected a 404 Not Found for a nonexistent user."


def test_dashboard_content_for_user_without_events_or_hardware():
    """
    Test dashboard content for a user without checked-in events or signed-out hardware.
    """
    user_id = 10  # Adjust based on your test setup for a user without events or hardware
    
    response = client.get(f"/hacker/{user_id}/dashboard")
    assert response.status_code == 200
    data = response.json()
    
    assert data['signed_out_hardware'] == [], "Expected no signed-out hardware for the user."
    assert data['checked_in_events'] == [], "Expected no checked-in events for the user."

