import pytest

import online_shopping_cart.shop.shop_search_and_purchase as shop_module
from online_shopping_cart.shop.shop_search_and_purchase import search_and_purchase_product


def make_ui_input_mock(monkeypatch, answers):
    """
    Mock UserInterface.get_user_input to return a sequence of answers.
    """
    it = iter(answers)

    def fake_get_user_input(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise AssertionError(f"Unexpected extra prompt: {prompt!r}")

    monkeypatch.setattr(shop_module.UserInterface, "get_user_input", fake_get_user_input)


def make_login_mock(monkeypatch, return_values):
    """
    Mock login() to return a sequence of values (including None).
    """
    it = iter(return_values)

    calls = {"count": 0, "values": []}

    def fake_login():
        calls["count"] += 1
        try:
            val = next(it)
        except StopIteration:
            val = None
        calls["values"].append(val)
        return val

    monkeypatch.setattr(shop_module, "login", fake_login)
    return calls


def make_checkout_mock(monkeypatch):
    called = {"count": 0, "login_info": None}

    def fake_checkout_and_payment(login_info):
        called["count"] += 1
        called["login_info"] = login_info

    monkeypatch.setattr(shop_module, "checkout_and_payment", fake_checkout_and_payment)
    return called


def make_display_mocks(monkeypatch):
    calls = {"all": 0, "filtered": []}

    def fake_display_csv_as_table(csv_filename=None):
        calls["all"] += 1

    def fake_display_filtered_table(csv_filename=None, search_target=None):
        calls["filtered"].append(search_target)

    monkeypatch.setattr(shop_module, "display_csv_as_table", fake_display_csv_as_table)
    monkeypatch.setattr(shop_module, "display_filtered_table", fake_display_filtered_table)

    return calls


def test_search_and_purchase_login_success_first_try_all_inventory(monkeypatch):
    """
    Case 1:
    - login succeeds first try
    - user types 'all' and 'y'
    """

    login_info = {"username": "alice", "wallet": 100.0}
    login_calls = make_login_mock(monkeypatch, [login_info])
    checkout_calls = make_checkout_mock(monkeypatch)
    display_calls = make_display_mocks(monkeypatch)

    make_ui_input_mock(
        monkeypatch,
        [
            "all",  # search_target
            "y",    # Ready to shop
        ],
    )

    search_and_purchase_product()

    assert login_calls["count"] == 1
    assert display_calls["all"] == 1
    assert display_calls["filtered"] == []
    assert checkout_calls["count"] == 1
    assert checkout_calls["login_info"] == login_info


def test_search_and_purchase_login_fails_then_succeeds(monkeypatch):
    """
    Case 2:
    - login returns None once, then valid login
    - still ends with checkout using second login_info
    """

    first_none = None
    second_info = {"username": "bob", "wallet": 50.0}
    login_calls = make_login_mock(monkeypatch, [first_none, second_info])
    checkout_calls = make_checkout_mock(monkeypatch)
    display_calls = make_display_mocks(monkeypatch)

    make_ui_input_mock(
        monkeypatch,
        [
            "all",
            "y",
        ],
    )

    search_and_purchase_product()

    assert login_calls["count"] == 2
    assert login_calls["values"][0] is None
    assert login_calls["values"][1] == second_info
    assert checkout_calls["login_info"] == second_info
    assert display_calls["all"] == 1


def test_search_and_purchase_filtered_search_then_checkout(monkeypatch):
    """
    Case 3:
    - user searches 'apple' (not 'all') then confirms
    """

    login_info = {"username": "carol", "wallet": 30.0}
    make_login_mock(monkeypatch, [login_info])
    checkout_calls = make_checkout_mock(monkeypatch)
    display_calls = make_display_mocks(monkeypatch)

    make_ui_input_mock(
        monkeypatch,
        [
            "apple",
            "y",
        ],
    )

    search_and_purchase_product()

    # Should call filtered with lowercased search_target
    assert display_calls["all"] == 0
    assert display_calls["filtered"] == ["apple"]
    assert checkout_calls["count"] == 1


def test_search_and_purchase_multiple_searches_before_ready(monkeypatch):
    """
    Case 4:
    - user searches once, says 'n'
    - searches again, says 'y'
    """

    login_info = {"username": "dora", "wallet": 10.0}
    make_login_mock(monkeypatch, [login_info])
    checkout_calls = make_checkout_mock(monkeypatch)
    display_calls = make_display_mocks(monkeypatch)

    make_ui_input_mock(
        monkeypatch,
        [
            "apple",  # first search
            "n",      # not ready
            "all",    # second search
            "y",      # ready
        ],
    )

    search_and_purchase_product()

    # First search: filtered, second: all inventory
    assert display_calls["filtered"] == ["apple"]
    assert display_calls["all"] == 1
    assert checkout_calls["count"] == 1


def test_search_and_purchase_yes_variants(monkeypatch):
    """
    Case 5:
    - 'yes please' should also be treated as ready (startswith('y'))
    """

    login_info = {"username": "eve", "wallet": 5.0}
    make_login_mock(monkeypatch, [login_info])
    checkout_calls = make_checkout_mock(monkeypatch)
    display_calls = make_display_mocks(monkeypatch)

    make_ui_input_mock(
        monkeypatch,
        [
            "all",
            "yes please",
        ],
    )

    search_and_purchase_product()

    assert display_calls["all"] == 1
    assert checkout_calls["count"] == 1


def test_search_and_purchase_case_insensitive_all(monkeypatch):
    """
    Case 6:
    - user types 'ALL' → lowercased → should behave like 'all'
    """

    login_info = {"username": "frank", "wallet": 12.0}
    make_login_mock(monkeypatch, [login_info])
    checkout_calls = make_checkout_mock(monkeypatch)
    display_calls = make_display_mocks(monkeypatch)

    make_ui_input_mock(
        monkeypatch,
        [
            "ALL",  # becomes 'all'
            "Y",    # becomes 'y'
        ],
    )

    search_and_purchase_product()

    assert display_calls["all"] == 1
    assert display_calls["filtered"] == []
    assert checkout_calls["count"] == 1


def test_search_and_purchase_case_insensitive_ready(monkeypatch):
    """
    Case 7:
    - 'Y' and 'Yes' handling via lower() + startswith('y')
    """

    login_info = {"username": "gina", "wallet": 20.0}
    make_login_mock(monkeypatch, [login_info])
    checkout_calls = make_checkout_mock(monkeypatch)
    display_calls = make_display_mocks(monkeypatch)

    make_ui_input_mock(
        monkeypatch,
        [
            "apple",
            "Y",  # upper case
        ],
    )

    search_and_purchase_product()

    assert display_calls["filtered"] == ["apple"]
    assert checkout_calls["count"] == 1


def test_search_and_purchase_uses_same_login_info_object(monkeypatch):
    """
    Case 8:
    - ensure exact login_info dict object is passed to checkout_and_payment
    """

    login_info = {"username": "harry", "wallet": 77.0}
    make_login_mock(monkeypatch, [login_info])
    checkout_calls = make_checkout_mock(monkeypatch)
    make_display_mocks(monkeypatch)

    make_ui_input_mock(
        monkeypatch,
        [
            "all",
            "y",
        ],
    )

    search_and_purchase_product()

    assert checkout_calls["login_info"] is login_info


def test_search_and_purchase_prompts_sequence(monkeypatch, capsys):
    """
    Case 9:
    - we don't care about exact text, but we can verify that
      get_user_input is called twice per search iteration with some prompt.
    """

    login_info = {"username": "ivy", "wallet": 40.0}
    make_login_mock(monkeypatch, [login_info])
    checkout_calls = make_checkout_mock(monkeypatch)

    prompts = []

    def fake_get_user_input(prompt=""):
        prompts.append(prompt)
        if "Search for products" in prompt:
            return "all"
        else:
            return "y"

    monkeypatch.setattr(shop_module.UserInterface, "get_user_input", fake_get_user_input)
    make_display_mocks(monkeypatch)

    search_and_purchase_product()
    out = capsys.readouterr().out  # not strictly needed, but keeps capsys happy

    # At least one search prompt and one ready prompt
    assert any("Search for products" in p for p in prompts)
    assert any("Ready to shop?" in p for p in prompts)
    assert checkout_calls["count"] == 1


def test_search_and_purchase_login_three_attempts(monkeypatch):
    """
    Case 10:
    - login returns None twice, then valid login on third attempt
    """

    login_info = {"username": "jon", "wallet": 0.0}
    login_calls = make_login_mock(monkeypatch, [None, None, login_info])
    checkout_calls = make_checkout_mock(monkeypatch)
    make_display_mocks(monkeypatch)

    make_ui_input_mock(
        monkeypatch,
        [
            "all",
            "y",
        ],
    )

    search_and_purchase_product()

    assert login_calls["count"] == 3
    assert checkout_calls["count"] == 1
