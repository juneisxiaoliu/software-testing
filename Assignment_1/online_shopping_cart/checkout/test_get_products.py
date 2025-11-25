# online_shopping_cart/tests/test_get_products.py
import pytest
import sys
import os
from unittest.mock import patch
from typing import List

# Path configuration (adapt to assignment directory structure)
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
online_shopping_cart_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(online_shopping_cart_dir)
sys.path.insert(0, project_root)

# Import dependencies
from online_shopping_cart.product.product_data import get_products
from online_shopping_cart.product.product import Product

class TestGetProducts:
    """Test get_products function (10 test cases covering input domain equivalence classes)"""

    def test_get_products_normal_valid_data(self):
        """1. Normal case: Valid CSV data (correct column names + legal format)"""
        with patch('online_shopping_cart.product.product_data.get_csv_data') as mock_csv:
            mock_csv.return_value = [
                {'Product': 'Apple', 'Price': '1.5', 'Units': '10'},
                {'Product': 'Banana', 'Price': '0.8', 'Units': '20'}
            ]
            products = get_products()
            assert len(products) == 2
            assert products[0].name == 'Apple' and products[0].price == 1.5 and products[0].units == 10

    def test_get_products_empty_csv_file(self):
        """2. Boundary case: Empty CSV file (no data rows)"""
        with patch('online_shopping_cart.product.product_data.get_csv_data') as mock_csv:
            mock_csv.return_value = []
            products = get_products()
            assert len(products) == 0

    def test_get_products_file_not_found(self):
        """3. Exception case: File not found (get_csv_data raises FileNotFoundError)"""
        with patch('online_shopping_cart.product.product_data.get_csv_data') as mock_csv:
            mock_csv.side_effect = FileNotFoundError("File not found")
            with pytest.raises(FileNotFoundError):
                get_products()

    def test_get_products_missing_product_column(self):
        """4. Exception case: Missing Product column (required field missing)"""
        with patch('online_shopping_cart.product.product_data.get_csv_data') as mock_csv:
            mock_csv.return_value = [{'Price': '1.5', 'Units': '10'}]  # Missing Product
            with pytest.raises(KeyError):
                get_products()

    def test_get_products_missing_price_column(self):
        """5. Exception case: Missing Price column (required field missing)"""
        with patch('online_shopping_cart.product.product_data.get_csv_data') as mock_csv:
            mock_csv.return_value = [{'Product': 'Apple', 'Units': '10'}]  # Missing Price
            with pytest.raises(KeyError):
                get_products()

    def test_get_products_invalid_price_non_numeric(self):
        """6. Exception case: Price is non-numeric string (illegal format)"""
        with patch('online_shopping_cart.product.product_data.get_csv_data') as mock_csv:
            mock_csv.return_value = [{'Product': 'Apple', 'Price': 'abc', 'Units': '10'}]
            with pytest.raises(ValueError):
                get_products()

    def test_get_products_invalid_units_non_integer(self):
        """7. Exception case: Units is non-integer string (illegal format)"""
        with patch('online_shopping_cart.product.product_data.get_csv_data') as mock_csv:
            mock_csv.return_value = [{'Product': 'Apple', 'Price': '1.5', 'Units': 'ten'}]
            with pytest.raises(ValueError):
                get_products()

    def test_get_products_negative_price(self):
        """8. Boundary case: Negative Price (valid type but business-invalid)"""
        with patch('online_shopping_cart.product.product_data.get_csv_data') as mock_csv:
            mock_csv.return_value = [{'Product': 'Defective', 'Price': '-2.0', 'Units': '5'}]
            products = get_products()
            assert products[0].price == -2.0  # Only assert return value, not business rationality

    def test_get_products_custom_filename(self):
        """9. Normal case: Use custom CSV filename (valid parameter)"""
        with patch('online_shopping_cart.product.product_data.get_csv_data') as mock_csv:
            mock_csv.return_value = [{'Product': 'Test', 'Price': '3.0', 'Units': '1'}]
            custom_file = './files/custom_products.csv'
            get_products(file_name=custom_file)
            mock_csv.assert_called_once_with(csv_filename=custom_file, is_dict=True)

    def test_get_products_special_characters_in_name(self):
        """10. Boundary case: Product name contains special characters (valid format)"""
        with patch('online_shopping_cart.product.product_data.get_csv_data') as mock_csv:
            mock_csv.return_value = [{'Product': 'Café&Co', 'Price': '2.5', 'Units': '15'}]
            products = get_products()
            assert products[0].name == 'Café&Co'

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])