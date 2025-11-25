import pytest

import online_shopping_cart.product.product_search as product_search
from online_shopping_cart.product.product_search import (
    display_filtered_table,
    PRODUCT_HEADER_INDEX,
)


def test_display_filtered_table_calls_display_csv_as_table_when_search_target_none(monkeypatch):
    """
    Case 1:
    - search_target = None
    - Expected behaviour: delegate to display_csv_as_table without calling get_csv_data.
    """

    called = {"display_csv_as_table": False, "get_csv_data": False}

    def fake_display_csv_as_table(csv_filename=None):
        called["display_csv_as_table"] = True

    def fake_get_csv_data(csv_filename=None):
        called["get_csv_data"] = True
        return [], []

    monkeypatch.setattr(product_search, "display_csv_as_table", fake_display_csv_as_table)
    monkeypatch.setattr(product_search, "get_csv_data", fake_get_csv_data)

    display_filtered_table(csv_filename="ignored.csv", search_target=None)

    assert called["display_csv_as_table"] is True
    assert called["get_csv_data"] is False


@pytest.mark.parametrize(
    "header, rows, search_target, expected_indices, description",
    [
        # 2: basic match, one row
        (
            [PRODUCT_HEADER_INDEX, "Price"],
            [["App", "10.0"], ["Orange", "5.0"]],
            "Apple",
            [0],  # re.search("App", "Apple", IGNORECASE) matches
            "single-row match",
        ),
        # 3: no match
        (
            [PRODUCT_HEADER_INDEX, "Price"],
            [["Banana", "10.0"], ["Orange", "5.0"]],
            "Apple",
            [],
            "no rows match",
        ),
        # 4: multiple matches
        (
            [PRODUCT_HEADER_INDEX, "Price"],
            [["App", "10.0"], ["App", "15.0"]],
            "Apple",
            [0, 1],
            "multiple rows match",
        ),
        # 5: search_target shorter than product → no match with current pattern/string usage
        (
            [PRODUCT_HEADER_INDEX, "Price"],
            [["Apple", "10.0"]],
            "Ap",
            [],
            "search_target shorter than product",
        ),
        # 6: empty search_target string
        (
            [PRODUCT_HEADER_INDEX, "Price"],
            [["Apple", "10.0"]],
            "",
            [],  # pattern "Apple" in "" → no match
            "empty search target",
        ),
        # 7: case-insensitive match
        (
            [PRODUCT_HEADER_INDEX, "Price"],
            [["app", "10.0"]],
            "APPLE",
            [0],
            "case-insensitive match",
        ),
        # 8: Product column not first
        (
            ["Price", PRODUCT_HEADER_INDEX],
            [["10.0", "App"], ["5.0", "Orange"]],
            "Apple",
            [0],
            "product column at non-zero index",
        ),
        # 9: unicode product name
        (
            [PRODUCT_HEADER_INDEX, "Price"],
            [["Äpple", "10.0"]],
            "ÄppleXYZ",
            [0],
            "unicode match",
        ),
        # 10: empty product field
        (
            [PRODUCT_HEADER_INDEX, "Price"],
            [["", "10.0"]],
            "Anything",
            [0],  # regex with empty pattern matches any string → row is printed
            "empty product name",
        ),
    ],
)
def test_display_filtered_table_filters_rows(
    monkeypatch, capsys, header, rows, search_target, expected_indices, description
):
    """
    Input domain modelling:
    - Inputs: csv_filename, search_target (None handled separately)
    - Indirect input: header + rows from get_csv_data.
      We vary header structure and row contents to cover multiple equivalence classes.
    """

    def fake_get_csv_data(csv_filename=None):
        return header, rows

    monkeypatch.setattr(product_search, "get_csv_data", fake_get_csv_data)

    display_filtered_table(csv_filename="any.csv", search_target=search_target)

    out = capsys.readouterr().out

    # Header must always be printed
    assert str(header) in out, f"Header not printed for case: {description}"

    # Which rows appear?
    printed_indices = [i for i, row in enumerate(rows) if str(row) in out]

    assert printed_indices == expected_indices, (
        f"Unexpected rows printed for case '{description}': "
        f"expected {expected_indices}, got {printed_indices}"
    )


def test_display_filtered_table_raises_when_product_column_missing(monkeypatch):
    """
    Extra robustness test:
    - Header does not contain PRODUCT_HEADER_INDEX
    - Expect ValueError from header.index(PRODUCT_HEADER_INDEX)
    """

    header = ["Name", "Price"]  # no "Product"
    rows = [["Apple", "10.0"]]

    def fake_get_csv_data(csv_filename=None):
        return header, rows

    monkeypatch.setattr(product_search, "get_csv_data", fake_get_csv_data)

    with pytest.raises(ValueError):
        display_filtered_table(csv_filename="any.csv", search_target="Apple")
