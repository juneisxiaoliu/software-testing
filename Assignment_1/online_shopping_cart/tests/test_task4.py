import builtins
from io import StringIO

import pytest
from unittest.mock import MagicMock

from online_shopping_cart.checkout.shopping_cart import ShoppingCart
from online_shopping_cart.product.product_data import get_products
from online_shopping_cart.user import user_login
from online_shopping_cart.user.user_data import UserDataManager
from online_shopping_cart.user.user_interface import UserInterface
from online_shopping_cart.user.user_authentication import UserAuthenticator, PasswordValidator
from online_shopping_cart.checkout import checkout_process
from online_shopping_cart.user import user_logout

@pytest.fixture(autouse=True)
def mock_user_data(monkeypatch):
    # Simulate UserDataManager to prevent reading real files
    #fake user info
    fake_users = [{"username": "ExistingUser", "password": "Password1!", "wallet": 10.0}]
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

@pytest.fixture(autouse=True)
def set_exit_behaviour(monkeypatch):
    monkeypatch.setattr(
        builtins,
        "exit",
        lambda code=0: (_ for _ in ()).throw(SystemExit(code))
    )
@pytest.fixture(autouse=True)
def mock_shopping_cart(monkeypatch):
    test_cart = ShoppingCart()
    checkout_process.global_cart = test_cart
    checkout_process.global_products= get_products()
    return test_cart

login_info = {
        "username": "ExistingUser",
        "wallet": 10.0,
    }

#Test1 not enough balance to check out
def test_less_wallet_than_cart(monkeypatch):

    inputs = ["6","20"]
    mock_inputs(inputs, monkeypatch)
    assert checkout_process.check_cart(login_info, checkout_process.global_cart) == False

#Test2 make sure wallet was saved, balance 0 as edge case
def test_wallet_zero_balance_saved(mock_user_data, monkeypatch):

    inputs = ["6", "c","y","l","y"]

    mock_inputs(inputs, monkeypatch)
    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    mock_save, fake_users_list = mock_user_data
    mock_save.assert_called_once()
    assert fake_users_list[-1]['wallet'] == 0.0

#Test3 wallet saved (non-zero)
def test_wallet_balance_saved(mock_user_data,monkeypatch):
    inputs = ["1", "c", "y", "l", "y"]

    mock_inputs(inputs, monkeypatch)
    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    mock_save, fake_users_list = mock_user_data
    mock_save.assert_called_once()
    assert fake_users_list[-1]['wallet'] == 8.0

#Test4 add multiple products to cart
def test_buy_multiple_products_saved(monkeypatch, mock_shopping_cart,capsys):
    inputs = ["6", "1","2", "l", "y"]

    mock_inputs(inputs, monkeypatch)
    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    captured = capsys.readouterr()
    assert "Watermelon added to your cart." in captured.out
    assert "Apple added to your cart." in captured.out
    assert "Banana added to your cart." in captured.out
    assert len(mock_shopping_cart.items) == 3

#Test5 display products with d
def test_products_displayed(monkeypatch,capsys):
    inputs = ["d", "l", "y"]

    mock_inputs(inputs, monkeypatch)
    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    captured = capsys.readouterr()
    assert "Available products for purchase:" in captured.out

#Test6 go to checkout with c
def test_user_can_checkout_cart(monkeypatch,capsys):
    inputs = ["c", "l", "y"]

    mock_inputs(inputs, monkeypatch)
    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    captured = capsys.readouterr()
    assert "Items in the cart:" in captured.out

#Test7 go to logout with l
def test_user_chose_logout(monkeypatch,capsys):
    inputs = ["l", "y"]

    iterate_in = iter(inputs)
    prompts = []

    # different input mock so that we can read the prompts as check_cart / logout confirm do not write to stdout
    def fake_input(prompt):
        prompts.append(prompt)
        return next(iterate_in)

    monkeypatch.setattr(UserInterface, "get_user_input", fake_input)

    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    assert "Do you still want to logout? - y/n: " in prompts

#Test8 add product to cart
def test_product_added_to_cart(monkeypatch,capsys,mock_shopping_cart):
    #"Apple added to your cart."
    inputs = ["1", "l", "y"]

    mock_inputs(inputs, monkeypatch)
    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    captured = capsys.readouterr()
    assert "Apple added to your cart." in captured.out
    assert len(mock_shopping_cart.items) == 1

#Test9 invalid input
def test_invalid_input(monkeypatch,capsys):
    inputs = ["x", "l", "y"]

    mock_inputs(inputs, monkeypatch)
    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    captured = capsys.readouterr()
    assert "Invalid input. Please try again." in captured.out

#Test10 chosen product out of stock
def test_add_product_out_of_stock(monkeypatch, mock_shopping_cart, capsys):
    inputs = ["6", "6", "l", "y"]

    mock_inputs(inputs, monkeypatch)
    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    captured = capsys.readouterr()
    assert "Watermelon added to your cart." in captured.out
    assert "Sorry, Watermelon is out of stock." in captured.out
    assert len(mock_shopping_cart.items) == 1

#Test11 check cart cancelled
def test_cancel_check_cart(monkeypatch, capsys):

    inputs = ["1","1", "c", "n", "y","1","y","l","y"]
    iterate_in = iter(inputs)
    prompts=[]
    #different input mock so that we can read the prompts as check_cart / logout confirm do not write to stdout
    def fake_input(prompt):
        prompts.append(prompt)
        return next(iterate_in)

    monkeypatch.setattr(UserInterface,"get_user_input", fake_input)

    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    captured = capsys.readouterr()

    assert "Apple added to your cart." in captured.out
    assert "\nDo you want to remove an item? - y/n: " in prompts
    assert "\nEnter item number to remove from cart (or c to display cart): " in prompts


#Test12 check cart - remove item
def test_check_cart_remove(mock_user_data, monkeypatch):

    inputs = ["1","1", "c", "n", "y","1","y","l","y"]

    mock_inputs(inputs, monkeypatch)
    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    mock_save, fake_users_list = mock_user_data
    mock_save.assert_called_once()
    assert fake_users_list[-1]['wallet'] == 8.0 #only payed for one item

#Test13 try checkout empty cart
def test_checkout_empty_cart():
    checkout_process.global_cart = ShoppingCart()
    assert checkout_process.check_cart(login_info, checkout_process.global_cart) == False

#Test14 try logout with non-empty cart
def test_logout_non_empty_cart(monkeypatch, capsys):
    inputs = ["6", "l", "y"]

    mock_inputs(inputs, monkeypatch)
    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    captured = capsys.readouterr()
    assert "Your cart is not empty. You have the following items:" in captured.out

#Test15 logout successful
def test_user_logged_out(monkeypatch, capsys):
    inputs = ["l", "y"]

    mock_inputs(inputs, monkeypatch)
    with pytest.raises(SystemExit):
        checkout_process.checkout_and_payment(login_info)

    captured = capsys.readouterr()
    assert "You have been logged out." in captured.out