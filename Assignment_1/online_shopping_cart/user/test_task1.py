import pytest
from unittest.mock import MagicMock
from online_shopping_cart.user import user_login
from online_shopping_cart.user.user_data import UserDataManager
from online_shopping_cart.user.user_interface import UserInterface
from online_shopping_cart.user.user_authentication import UserAuthenticator, PasswordValidator

@pytest.fixture
def mock_user_data(monkeypatch):
    # Simulate UserDataManager to prevent reading real files
    #fake user info
    fake_users = [{"username": "ExistingUser", "password": "Password1!", "wallet": 100.0}]
    #Simulate load_users to return dummy data
    monkeypatch.setattr(UserDataManager, 'load_users', lambda: fake_users)
    #Simulate save_users (we need to verify whether it is invoked)
    mock_save = MagicMock()
    monkeypatch.setattr(UserDataManager, 'save_users', mock_save)
    return mock_save, fake_users


def mock_inputs(inputs, monkeypatch):
# Auxiliary function: Simulate UserInterface input
    input_iterator = iter(inputs)
    monkeypatch.setattr(UserInterface, 'get_user_input', lambda prompt="": next(input_iterator))

#test case 1 user register successfully
def test_register_success(mock_user_data, monkeypatch):
    inputs = ["NewUser", "yes", "StrongP@ss1"]
    mock_inputs(inputs, monkeypatch)
    user = user_login.login()

#Assertion 1: Successful login returns a user object
    assert user is not None
    assert user['username'] == "NewUser"

#Assertion 2: Verification data saved (This confirms that the save operation within UserAuthenticator.register has been executed)
    mock_save, fake_users_list = mock_user_data
    mock_save.assert_called_once()
    assert fake_users_list[-1]['username'] == "NewUser"

def test_validate_password_logic():
    # invalid password
    assert PasswordValidator.is_valid("short") is False
    assert PasswordValidator.is_valid("nouppercase1!") is False
    assert PasswordValidator.is_valid("NoSpecialChar1") is False
    # valid password
    assert PasswordValidator.is_valid("ValidP@ss1") is True


# Test case 2: Registration Failed - Password Too Weak
def test_register_fail_weak_password(mock_user_data, monkeypatch):
    # Scenario: Enter new username -> Yes -> Password is too short
    inputs = ["NewUser", "yes", "short"]
    mock_inputs(inputs, monkeypatch)

    user = user_login.login()

    #Assertion: Registration failure returns None
    assert user is None

    #Assertion: save_users was not called (file unchanged)
    mock_save, _ = mock_user_data
    mock_save.assert_not_called()

# Test case 3: User does not exist and does not register
def test_user_not_found_no_register(mock_user_data, monkeypatch):
    # Scenario: Enter new username -> No
    inputs = ["NewUser", "no"]
    mock_inputs(inputs, monkeypatch)

    user = user_login.login()

    assert user is None


# Test case 4:Existing User Login (Integrated Test UserAuthenticator)
def test_existing_user_login(mock_user_data, monkeypatch):
    # Scenario: Enter an existing username -> Enter the correct password
    inputs = ["ExistingUser", "Password1!"]
    mock_inputs(inputs, monkeypatch)

    # Mock UserAuthenticator
    mock_auth_instance = MagicMock()
    # Have login return a dictionary of successful users
    mock_auth_instance.login.return_value = {"username": "ExistingUser", "password": "Password1!", "wallet": 100.0}

    # Replace the UserAuthenticator class so that it returns our mock instance.
    monkeypatch.setattr(user_login, 'UserAuthenticator', lambda: mock_auth_instance)

    user = user_login.login()

    assert user is not None
    assert user['username'] == "ExistingUser"


# Test case 5: Logout functionality
def test_logout(monkeypatch):
    # import logout
    from online_shopping_cart.user import user_logout

    # Simulate user input 'y' to confirm logout
    mock_inputs(['y'], monkeypatch)

    # Mock Cart object.
    mock_cart = MagicMock()
    mock_cart.is_empty.return_value = True  # assume shopping cart is empty

    result = user_logout.logout(mock_cart)

    assert result is True

#Test case 7: Registration failed - Missing uppercase letter (Invalid Class)
def test_register_fail_no_uppercase(mock_user_data, monkeypatch):
    # Scenario: Password is sufficiently long, contains special characters, but is entirely lowercase -> Should fail
    inputs = ["NewUser2", "yes", "weakpass1!"]
    mock_inputs(inputs, monkeypatch)

    user = user_login.login()
    assert user is None
# Test case 8: Registration failure - Missing special character (Invalid Class)
def test_register_fail_no_special_char(mock_user_data, monkeypatch):
    # Scenario: Password is sufficiently long, contains uppercase letters, but lacks special characters -> Should fail
    inputs = ["NewUser3", "yes", "WeakPass123"]
    mock_inputs(inputs, monkeypatch)

    user = user_login.login()
    assert user is None
# Test case 9: Boundary value testing - Password length exactly 8 characters
def test_register_boundary_length(mock_user_data, monkeypatch):
    # Scenario: Password length is exactly 8 characters and meets all other requirements -> Should succeed
    inputs = ["BoundUser", "yes", "A!bcdefg"]
    mock_inputs(inputs, monkeypatch)

    user = user_login.login()
    assert user is not None
    assert user['username'] == "BoundUser"

 #Test case 10: Input robustness test - Enter uppercase "YES" during registration (Robustness)
def test_register_case_insensitive_input(mock_user_data, monkeypatch):
    #Scenario: User inputs "YES" or "y" instead of "yes" -> The programme should recognise this and proceed.
    inputs = ["RobustUser", "YES", "StrongP@ss1"]
    mock_inputs(inputs, monkeypatch)

    user = user_login.login()
    assert user is not None
    assert user['username'] == "RobustUser"
