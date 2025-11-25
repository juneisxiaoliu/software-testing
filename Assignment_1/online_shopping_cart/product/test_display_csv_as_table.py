import pytest

# Adjust this import if your path/module name is different
import online_shopping_cart.product.product_search as product_search
from online_shopping_cart.product.product_search import display_csv_as_table


@pytest.mark.parametrize(
    "csv_filename, header, rows, description",
    [
        # 1: single row
        ("file1.csv", ["Product", "Price"], [["Apple", "10.0"]], "one simple row"),
        # 2: two rows
        ("file2.csv", ["Product", "Price"], [["Apple", "10.0"], ["Orange", "5.0"]], "two rows"),
        # 3: no data rows
        ("file3.csv", ["Product", "Price"], [], "no data rows"),
        # 4: product names with spaces
        ("file4.csv", ["Product", "Price"], [["Red Apple", "10.0"]], "spaces in product name"),
        # 5: unicode characters
        ("file5.csv", ["Product", "Price"], [["Äpple", "12.0"]], "unicode characters"),
        # 6: numeric-only product id
        ("file6.csv", ["Product", "Price"], [["12345", "99.99"]], "numeric product id"),
        # 7: zero price
        ("file7.csv", ["Product", "Price"], [["Apple", "0.0"]], "zero price"),
        # 8: many columns
        ("file8.csv", ["Product", "Price", "Stock"], [["Apple", "10.0", "3"]], "extra column"),
        # 9: empty product field
        ("file9.csv", ["Product", "Price"], [["", "10.0"]], "empty product name"),
        # 10: duplicate rows
        ("file10.csv", ["Product", "Price"],
         [["Apple", "10.0"], ["Apple", "10.0"]], "duplicate rows"),
    ],
)
def test_display_csv_as_table_prints_header_and_rows(
    monkeypatch, capsys, csv_filename, header, rows, description
):
    """
    Input domain modelling:
    - Inputs: csv_filename (string)
    - Indirect input via get_csv_data: header + rows.
      We cover 0/1/many rows, special characters, empty fields, extra columns, etc.
    """

    called_with = []

    def fake_get_csv_data(csv_filename=None):
        called_with.append(csv_filename)
        return header, rows

    # Stub file access so no real CSV is touched
    monkeypatch.setattr(product_search, "get_csv_data", fake_get_csv_data)

    # Act
    display_csv_as_table(csv_filename=csv_filename)

    # Assert: correct filename passed
    assert called_with == [csv_filename], f"Wrong csv_filename for case: {description}"

    # Assert: printed header + rows
    out = capsys.readouterr().out

    # Header should appear once
    assert str(header) in out, f"Header not printed for case: {description}"

    # Every row from our stubbed CSV should be printed
    for row in rows:
        assert str(row) in out, f"Row {row} not printed for case: {description}"
