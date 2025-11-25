from online_shopping_cart.product.product_search import display_csv_as_table, display_filtered_table
from online_shopping_cart.checkout.checkout_process import checkout_and_payment
from online_shopping_cart.user.user_interface import UserInterface
from online_shopping_cart.user.user_login import login

######################################
# SHOP SEARCH AND PURCHASE FUNCTIONS #
######################################


def search_and_purchase_product() -> None:
    """
    Search for a product and buy it
    """
    while True:
        login_info: dict[str, str | float] | None = login()  # Login as a user
        if login_info is not None:
            break

    # Search for products then begin to shop
    while True:
        search_target: str = UserInterface.get_user_input(
            prompt="Search for products in inventory (type 'all' for the whole inventory): "
        ).lower()
        if search_target == 'all':
            display_csv_as_table()
        else:
            display_filtered_table(search_target=search_target)

        check: str = UserInterface.get_user_input(prompt='\nReady to shop? - y/n: ').lower()
        if check.startswith('y'):
            break
    checkout_and_payment(login_info=login_info)
