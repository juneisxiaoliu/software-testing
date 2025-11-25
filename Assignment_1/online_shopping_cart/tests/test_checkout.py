# online_shopping_cart/tests/test_checkout.py
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
from online_shopping_cart.checkout.checkout_process import checkout
from online_shopping_cart.checkout.shopping_cart import ShoppingCart  # Fixed here
from online_shopping_cart.product.product import Product
from online_shopping_cart.user.user import User

class TestCheckout:
    """Test checkout function (10 test cases, covering input domain equivalence classes)"""

    def setup_method(self):
        """Reset cart and user before each test to avoid interference"""
        self.cart = ShoppingCart()
        self.user = User(name="TestUser", wallet=100.0)
        self.apple = Product(name="Apple", price=1.5, units=1)
        self.banana = Product(name="Banana", price=0.8, units=1)

    def test_checkout_normal_valid_cart(self):
        """1. Normal case: cart has items and sufficient balance"""
        self.cart.add_item(self.apple)
        self.cart.add_item(self.banana)
        initial_wallet = self.user.wallet
        checkout(self.user, self.cart)
        assert self.user.wallet == initial_wallet - 2.3
        assert self.cart.is_empty()

    def test_checkout_empty_cart(self, capsys):
        """2. Boundary case: empty cart (no items to checkout)"""
        checkout(self.user, self.cart)
        captured = capsys.readouterr()
        assert "Your basket is empty" in captured.out
        assert not self.user.wallet < 100.0  # Balance unchanged

    def test_checkout_insufficient_funds(self, capsys):
        """3. Exception case: insufficient funds (total amount > wallet)"""
        expensive_item = Product(name="Laptop", price=200.0, units=1)
        self.cart.add_item(expensive_item)
        initial_wallet = self.user.wallet
        checkout(self.user, self.cart)
        assert self.user.wallet == initial_wallet  # Balance not deducted
        assert not self.cart.is_empty()  # Cart not cleared
        captured = capsys.readouterr()
        assert "You don't have enough money" in captured.out

    def test_checkout_exact_funds(self):
        """4. Boundary case: balance exactly equals total amount"""
        self.user.wallet = 2.3  # Same as total item price
        self.cart.add_item(self.apple)
        self.cart.add_item(self.banana)
        checkout(self.user, self.cart)
        assert self.user.wallet == 0.0
        assert self.cart.is_empty()

    def test_checkout_single_item(self):
        """5. Normal case: cart contains only 1 item"""
        self.cart.add_item(self.apple)
        initial_wallet = self.user.wallet
        checkout(self.user, self.cart)
        assert self.user.wallet == initial_wallet - 1.5
        assert self.cart.is_empty()

    def test_checkout_negative_price_item(self):
        """6. Exception case: item price is negative (valid type but invalid business logic)"""
        negative_item = Product(name="Defective", price=-1.0, units=1)
        self.cart.add_item(negative_item)
        initial_wallet = self.user.wallet
        checkout(self.user, self.cart)
        assert self.user.wallet == initial_wallet - (-1.0)  # Balance increases (business logic doesn't check negative)
        assert self.cart.is_empty()

    def test_checkout_zero_price_item(self):
        """7. Boundary case: item price is 0 (free item)"""
        free_item = Product(name="Gift", price=0.0, units=1)
        self.cart.add_item(free_item)
        initial_wallet = self.user.wallet
        checkout(self.user, self.cart)
        assert self.user.wallet == initial_wallet  # Balance unchanged
        assert self.cart.is_empty()

    def test_checkout_user_wallet_zero(self, capsys):
        """8. Exception case: user wallet balance is 0 and cart has items"""
        self.user.wallet = 0.0
        self.cart.add_item(self.apple)
        checkout(self.user, self.cart)
        captured = capsys.readouterr()
        assert "You don't have enough money" in captured.out
        assert not self.cart.is_empty()

    def test_checkout_multiple_same_items(self):
        """9. Normal case: cart contains multiple identical items"""
        for _ in range(3):
            self.cart.add_item(self.apple)  # 3 Apples, total price 4.5
        initial_wallet = self.user.wallet
        checkout(self.user, self.cart)
        assert self.user.wallet == initial_wallet - 4.5
        assert self.cart.is_empty()

    def test_checkout_wallet_negative_initial(self):
        """10. Exception case: user initial balance is negative"""
        self.user.wallet = -10.0
        self.cart.add_item(self.apple)
        checkout(self.user, self.cart)
        assert self.user.wallet == -10.0  # Balance unchanged (still insufficient)
        assert not self.cart.is_empty()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])