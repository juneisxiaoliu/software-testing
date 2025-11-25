# online_shopping_cart/tests/test_check_cart.py
import pytest
import sys
import os
from unittest.mock import patch
from typing import List

# Path configuration (keep unchanged)
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
online_shopping_cart_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(online_shopping_cart_dir)
sys.path.insert(0, project_root)

# Fix import paths (add checkout level)
from online_shopping_cart.checkout.checkout_process import check_cart, global_products
from online_shopping_cart.checkout.shopping_cart import ShoppingCart  # Fixed here
from online_shopping_cart.product.product import Product
from online_shopping_cart.user.user import User
from online_shopping_cart.user.user_interface import UserInterface

class TestCheckCart:
    """Test check_cart function (10 test cases, covering input domain and user interaction)"""

    def setup_method(self):
        """Reset dependencies before each test"""
        self.cart = ShoppingCart()
        self.user = User(name="TestUser", wallet=100.0)
        # Initialize global products (simulate inventory)
        global global_products
        global_products = [
            Product(name="Apple", price=1.5, units=10),
            Product(name="Banana", price=0.8, units=20)
        ]
        # Add initial items to cart
        self.apple = Product(name="Apple", price=1.5, units=1)
        self.banana = Product(name="Banana", price=0.8, units=1)
        self.cart.add_item(self.apple)
        self.cart.add_item(self.banana)

    def test_check_cart_choose_checkout(self):
        """1. Normal case: user chooses checkout (input y → execute checkout)"""
        with patch.object(UserInterface, "get_user_input") as mock_input:
            mock_input.side_effect = ["y"]  # Simulate user input "y"
            check_cart(self.user, self.cart)
            assert self.cart.is_empty()  # Cart cleared
            assert self.user.wallet == 100.0 - 2.3  # Balance deducted

    def test_check_cart_choose_remove_valid_item(self):
        """2. Normal case: user chooses to remove valid item (n→y→1→n→n)"""
        with patch.object(UserInterface, "get_user_input") as mock_input:
            # Add final loop exit input: after removal, ask "checkout?"→"n", "remove?"→"n"
            mock_input.side_effect = ["n", "y", "1", "n", "n"]
            initial_apple_stock = next(p for p in global_products if p.name == "Apple").units
            check_cart(self.user, self.cart)
            # Assert: cart has 1 item remaining (Banana)
            assert len(self.cart.items) == 1 and self.cart.items[0].name == "Banana"
            # Assert: global inventory restored (Apple stock +1)
            assert next(p for p in global_products if p.name == "Apple").units == initial_apple_stock + 1

    def test_check_cart_choose_cancel_all(self):
        """3. Boundary case: user cancels checkout and removal (n→n→return False)"""
        with patch.object(UserInterface, "get_user_input") as mock_input:
            mock_input.side_effect = ["n", "n"]
            result = check_cart(self.user, self.cart)
            assert result is False
            assert len(self.cart.items) == 2  # Cart unchanged

    def test_check_cart_remove_invalid_number(self, capsys):
        """4. Exception case: input invalid number when removing (n→y→0→n→n)"""
        with patch.object(UserInterface, "get_user_input") as mock_input:
            mock_input.side_effect = ["n", "y", "0", "n", "n"]
            check_cart(self.user, self.cart)
            captured = capsys.readouterr()
            assert "Invalid input. Please try again." in captured.out
            assert len(self.cart.items) == 2  # Item not removed

    def test_check_cart_remove_out_of_range_number(self, capsys):
        """5. Exception case: input out-of-range number when removing (n→y→3→n→n)"""
        with patch.object(UserInterface, "get_user_input") as mock_input:
            mock_input.side_effect = ["n", "y", "3", "n", "n"]
            check_cart(self.user, self.cart)
            captured = capsys.readouterr()
            assert "Invalid input. Please try again." in captured.out
            assert len(self.cart.items) == 2

    def test_check_cart_remove_non_numeric_input(self, capsys):
        """6. Exception case: input non-numeric when removing (n→y→abc→n→n)"""
        with patch.object(UserInterface, "get_user_input") as mock_input:
            mock_input.side_effect = ["n", "y", "abc", "n", "n"]
            check_cart(self.user, self.cart)
            captured = capsys.readouterr()
            assert "Invalid input. Please try again." in captured.out
            assert len(self.cart.items) == 2

    def test_check_cart_display_cart_after_remove(self):
        """7. Normal case: choose to display cart when removing (n→y→c→return to re-operate)"""
        with patch.object(UserInterface, "get_user_input") as mock_input:
            mock_input.side_effect = ["n", "y", "c", "n", "n"]
            check_cart(self.user, self.cart)
            assert len(self.cart.items) == 2  # Cart unchanged

    def test_check_cart_empty_cart(self):
        """8. Boundary case: empty cart (no items to operate)"""
        self.cart.clear_items()  # Clear cart
        with patch.object(UserInterface, "get_user_input") as mock_input:
            mock_input.side_effect = ["y", "n"]  # Empty cart checkout invalid, then cancel
            result = check_cart(self.user, self.cart)
            assert result is False
            assert self.cart.is_empty()

    def test_check_cart_multiple_remove_operations(self):
        """9. Normal case: multiple remove operations (n→y→1→n→y→1→n→n)"""
        with patch.object(UserInterface, "get_user_input") as mock_input:
            mock_input.side_effect = ["n", "y", "1", "n", "y", "1", "n", "n"]
            check_cart(self.user, self.cart)
            assert self.cart.is_empty()  # Cart empty after two removals

    def test_check_cart_checkout_after_remove(self):
        """10. Normal case: choose checkout after removing item (n→y→1→y)"""
        with patch.object(UserInterface, "get_user_input") as mock_input:
            mock_input.side_effect = ["n", "y", "1", "y"]
            check_cart(self.user, self.cart)
            assert self.cart.is_empty()  # Cart cleared after checkout
            assert self.user.wallet == 100.0 - 0.8  # Only Banana price deducted

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])