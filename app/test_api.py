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
    assert len(data) > 0  # Adjust based on your test data setup
    for user in data:
        assert user['checked_in'] is True 

def test_get_users_invalid_limit():
    """
    Test fetching users with an invalid limit parameter.
    """
    response = client.get("/users?limit=-1")
    assert response.status_code == 400  # Assuming your application validates query parameters and returns 422 for invalid values

# `GET /users/{user_id}`
def test_get_user_by_valid_id():
    """
    Test fetching a user by a valid user ID.
    """
    # You need to ensure a user with a specific ID exists in your test setup.
    # For demonstration, assuming there's a user with ID 1.
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    
    # Validate the response structure matches the expected format
    assert 'name' in data
    assert 'company' in data
    assert 'email' in data
    assert 'phone' in data
    assert 'skills' in data
    assert isinstance(data['skills'], list)  # Assuming 'skills' is a list of skill objects

    # Additional checks can be performed based on known data for user ID 1
    assert data['name'] == "Emily May"
    assert data['email'] == "estradadana@example.org"

def test_get_user_by_invalid_id():
    """
    Test fetching a user by an invalid/non-existent user ID.
    """
    # Assuming an ID that does not exist in the database
    response = client.get("/users/9999")
    assert response.status_code == 404
    data = response.json()
    assert 'detail' in data
    assert data['detail'] == "User not found"  # Adjust based on your actual error message

def test_get_user_response_structure():
    """
    Test the structure of the response for a valid user request.
    """
    # Again, assuming there's a user with ID 1
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    
    # Validate that the response contains all the expected keys
    expected_keys = {"name", "company", "email", "phone", "skills"}
    assert all(key in data for key in expected_keys)

    # Validate the structure of the skills list
    if data['skills']:  # If there are skills
        first_skill = data['skills'][0]
        assert 'skill' in first_skill and 'rating' in first_skill
