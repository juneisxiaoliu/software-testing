import pytest
from unittest.mock import MagicMock, patch
from online_shopping_cart.user.user import User
from online_shopping_cart.checkout.shopping_cart import ShoppingCart
from online_shopping_cart.product.product import Product
from online_shopping_cart.checkout.checkout_process import checkout
from online_shopping_cart.user.user_profile import manage_credit_cards
from online_shopping_cart.user.user_authentication import UserAuthenticator


# Helper to mock user input sequence
def mock_inputs(inputs, monkeypatch):
    input_iterator = iter(inputs)
    monkeypatch.setattr('online_shopping_cart.user.user_interface.UserInterface.get_user_input',
                        lambda prompt="": next(input_iterator))


@pytest.fixture
def setup_data():
    user = User("TestUser", 100.0, cards=[])
    cart = ShoppingCart()
    product = Product("Apple", 2.0, 1)
    return user, cart, product


# PART 1: 5 Selected Regression Tests (Old Functionality)


def test_1_old_checkout_wallet_success(setup_data, monkeypatch):
    """Regression: Verify wallet payment still works."""
    user, cart, product = setup_data
    cart.add_item(product)

    # Input '1' to select Wallet payment
    mock_inputs(['1'], monkeypatch)

    # Mock saving to file to avoid touching real json
    with patch('online_shopping_cart.user.user_data.UserDataManager.save_users'):
        checkout(user, cart)

    assert user.wallet == 98.0  # 100 - 2
    assert cart.is_empty()


def test_2_old_checkout_insufficient_funds(setup_data, monkeypatch):
    """Regression: Verify insufficient funds logic."""
    user, cart, product = setup_data
    expensive_item = Product("Laptop", 200.0, 1)
    cart.add_item(expensive_item)

    # Input '1' for Wallet
    mock_inputs(['1'], monkeypatch)

    checkout(user, cart)

    assert user.wallet == 100.0  # Unchanged
    assert not cart.is_empty()


def test_3_old_checkout_empty_cart(setup_data):
    """Regression: Verify empty cart logic."""
    user, cart, _ = setup_data
    # No inputs needed as it returns early
    checkout(user, cart)
    # Output is handled by print, asserting state didn't change
    assert user.wallet == 100.0


def test_4_old_register_logic(monkeypatch):
    """Regression: Verify basic registration flow (without cards)."""
    # Mock data list
    fake_data = []

    # Register "OldStyleUser"
    UserAuthenticator.register("OldStyleUser", "Pass123!", fake_data)

    assert len(fake_data) == 1
    assert fake_data[0]['username'] == "OldStyleUser"
    assert fake_data[0]['wallet'] == 0.0


def test_5_old_cart_add_item(setup_data):
    """Regression: Verify adding item to cart."""
    _, cart, product = setup_data
    cart.add_item(product)
    assert len(cart.items) == 1
    assert cart.items[0].name == "Apple"


# PART 2: 3 New Tests for Implementation 1 (User Profile/Cards)


def test_6_new_manage_cards_add(monkeypatch):
    """Impl 1: Test adding a card via manage_credit_cards module."""
    # Inputs: 'a' (add), details..., 'b' (back)
    inputs = ['a', '12345678', '12/25', 'Test Name', '123', 'b']
    mock_inputs(inputs, monkeypatch)

    # Mock loading users to return a fake user list containing our user
    fake_user_entry = {'username': 'TestUser', 'wallet': 100.0, 'cards': []}

    with patch('online_shopping_cart.user.user_data.UserDataManager.load_users', return_value=[fake_user_entry]), \
            patch('online_shopping_cart.user.user_data.UserDataManager.save_users') as mock_save:
        manage_credit_cards('TestUser')

        # Assert save was called
        mock_save.assert_called()
        # Assert card was added to the entry
        assert len(fake_user_entry['cards']) == 1
        assert fake_user_entry['cards'][0]['card_number'] == '12345678'


def test_7_new_register_with_cards(monkeypatch):
    """Impl 1: Test registering a new user WITH cards."""
    fake_data = []
    cards_input = [{'card_number': '8888', 'expiry': '12/30', 'name': 'New', 'cvv': '000'}]

    UserAuthenticator.register("NewUser", "Pass123!", fake_data, cards=cards_input)

    assert fake_data[0]['username'] == "NewUser"
    assert len(fake_data[0]['cards']) == 1
    assert fake_data[0]['cards'][0]['card_number'] == '8888'


def test_8_new_user_class_cards_init():
    """Impl 1: Test User class initializes cards correctly."""
    u = User("Test", 100.0, cards=[{'num': '123'}])
    assert len(u.cards) == 1

    u_empty = User("Test", 100.0)  # Default None
    assert u_empty.cards == []


# ==========================================
# PART 3: 3 New Tests for Implementation 2 (Payment System)
# ==========================================

def test_9_new_checkout_credit_card_success(setup_data, monkeypatch):
    """Impl 2: Test paying with Credit Card (Success)."""
    user, cart, product = setup_data
    cart.add_item(product)

    # Add a fake card to the user
    user.cards = [{'card_number': '9999', 'name': 'Visa'}]

    # Inputs: '2' (Select Card Payment), '1' (Select first card)
    mock_inputs(['2', '1'], monkeypatch)

    checkout(user, cart)

    assert user.wallet == 100.0  # Balance MUST NOT change
    assert cart.is_empty()  # Cart MUST be empty


def test_10_new_checkout_credit_card_no_cards(setup_data, monkeypatch):
    """Impl 2: Test paying with Credit Card but user has no cards."""
    user, cart, product = setup_data
    cart.add_item(product)
    user.cards = []  # No cards

    # Inputs: '2' (Select Card Payment)
    mock_inputs(['2'], monkeypatch)

    checkout(user, cart)

    assert not cart.is_empty()  # Should fail, items remain
    assert user.wallet == 100.0


def test_11_new_checkout_credit_card_invalid_selection(setup_data, monkeypatch):
    """Impl 2: Test paying with Credit Card but selecting invalid index."""
    user, cart, product = setup_data
    cart.add_item(product)
    user.cards = [{'card_number': '1111'}]

    # Inputs: '2' (Card), '99' (Invalid index)
    mock_inputs(['2', '99'], monkeypatch)

    checkout(user, cart)

    assert not cart.is_empty()  # Should fail