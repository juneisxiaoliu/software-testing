from online_shopping_cart.checkout.shopping_cart import ShoppingCart
from online_shopping_cart.product.product_data import get_products
from online_shopping_cart.user.user_interface import UserInterface
from online_shopping_cart.product.product import Product
from online_shopping_cart.user.user_logout import logout
from online_shopping_cart.user.user import User

############################
# CHECKOUT PROCESS GLOBALS #
############################


global_products: list[Product] = get_products()  # Load products from CSV
global_cart: ShoppingCart = ShoppingCart()


##############################
# CHECKOUT PROCESS FUNCTIONS #
##############################


def checkout(user, cart) -> None:
    """
    Complete the checkout process
    """
    global global_products

    if not cart.items:
        print('Your basket is empty. Please add items before checking out.')
        return

    total_price: float = cart.get_total_price()
    if total_price > user.wallet:
        print(f"You don't have enough money to complete the purchase. Please try again!")
        return
    user.wallet -= total_price  # Deduct the total price from the user's wallet
    cart.clear_items()  # Clear the cart

    print(f'Thank you for your purchase, {user.name}! Your remaining balance is {user.wallet}')


def display_cart_items(cart) -> None:
    print('\nItems in the cart:')
    for i, item in enumerate(cart.retrieve_items()):
        print(f'{i + 1}. {str(item)}')


def check_cart(user, cart) -> None | bool:
    """
    Print the cart and prompt user for proceeding to checkout
    """
    global global_products

    display_cart_items(cart)

    # Iteratively ask the user if they want to check out or remove an item from the cart, and if neither break from loop
    while True:
        if not cart.is_empty() and UserInterface.get_user_input(
                prompt='\nDo you want to checkout? - y/n: '
        ).lower().startswith('y'):
            return checkout(user=user, cart=cart)
        elif not cart.is_empty() and UserInterface.get_user_input(
                prompt='\nDo you want to remove an item? - y/n: '
        ).lower().startswith('y'):
            display_cart_items(cart)
            user_input: str = UserInterface.get_user_input(
                prompt='\nEnter item number to remove from cart (or c to display cart): '
            ).lower()
            if user_input.startswith('c'):
                display_cart_items(cart)
            elif user_input.isdigit() and 1 <= int(user_input) <= len(cart.retrieve_items()):
                selected_item: Product = cart.retrieve_items()[int(user_input) - 1]
                cart.remove_item(product=selected_item)
                [product.add_product_unit() for product in global_products if product.name == selected_item.name]
            else:
                print('Invalid input. Please try again.')
        else:
            return False


def display_products_available_for_purchase() -> None:
    """
    Display available products in the global_products list
    """
    global global_products

    print('\nAvailable products for purchase:')
    for i, product in enumerate(global_products):
        print(f'{i + 1}. {str(product)}')


def checkout_and_payment(login_info) -> None:
    """
    Main function for the shopping and checkout process
    """
    global global_products, global_cart

    user: User = User(
        name=login_info['username'],
        wallet=login_info['wallet']
    )

    # Get user input for either selecting a product by its number, checking their cart or logging out
    while True:
        choice: str = UserInterface.get_user_input(
            prompt='\nEnter product number or (d to display products, c to check cart, l to logout): '
        ).lower()
        if choice.startswith('d'):
            display_products_available_for_purchase()
        elif choice.startswith('c'):
            if check_cart(user=user, cart=global_cart) is False:
                continue  # The user has selected not to check out their cart
            else:
                pass  # TODO: Task 4: update the wallet information in the users.json file
        elif choice.startswith('l'):
            if logout(cart=global_cart):
                exit(0)  # The user has logged out
        elif choice.isdigit() and 1 <= int(choice) <= len(global_products):
            selected_product: Product = global_products[int(choice) - 1]
            if selected_product.units > 0:
                global_cart.add_item(product=selected_product.get_product_unit())  # Add selected product to the cart
                print(f'{selected_product.name} added to your cart.')
            else:
                print(f'Sorry, {selected_product.name} is out of stock.')
        else:
            print('Invalid input. Please try again.')
