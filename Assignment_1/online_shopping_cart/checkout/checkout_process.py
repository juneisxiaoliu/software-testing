from partd.utils import suffix

from online_shopping_cart.checkout.shopping_cart import ShoppingCart
from online_shopping_cart.product.product_data import get_products
from online_shopping_cart.user.user_data import UserDataManager
from online_shopping_cart.user.user_interface import UserInterface
from online_shopping_cart.product.product import Product
from online_shopping_cart.user.user_logout import logout
from online_shopping_cart.user.user import User
from online_shopping_cart.user.user_profile import manage_credit_cards

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
    [Task 1 Implementation 2] Added logic to choose between Wallet and Credit Card.
    """
    global global_products

    if not cart.items:
        print('Your basket is empty. Please add items before checking out.')
        return

    total_price: float = cart.get_total_price()

    # --- [Task 1] Implementation 2: Payment System Start ---
    print(f"\nTotal amount to pay: ${total_price}")
    print("Select Payment Method:")
    print("1. Wallet Balance")
    print("2. Credit Card")
    payment_choice = UserInterface.get_user_input(prompt="Enter choice 1 or 2: ")
    if payment_choice == '1':
        if total_price > user.wallet:
            print(f"You don't have enough money in your wallet to complete the purchase. Please try again!")
            return
        user.wallet -= total_price  # Deduct the total price from the user's wallet
        all_users = UserDataManager.load_users()
        for u in all_users:
            if u['username'] == user.name:
                u['wallet'] = user.wallet
                break
        UserDataManager.save_users(all_users)
        print(f'Paid ${total_price} using Wallet. Remaining balance: ${user.wallet}')
    elif payment_choice == '2':
        if not user.cards:
            print("No credit cards available. Please add a credit card in your profile.")
            return
        print("\nSelect a card to pay with:")
        for idx, card in enumerate(user.cards):
            #show only last 4 digits for security
            suffix = card.get('card_number')[-4:]
            print(f"{idx + 1}. {card.get('name')} (Ends in {suffix})")
        card_idx = UserInterface.get_user_input(prompt="Enter choice (e.g., 1): ")
        if card_idx.isdigit() and 1 <= int(card_idx) <= len(user.cards):
            selected_card = user.cards[int(card_idx) - 1]
            print(f'Paid ${total_price} using Credit Card ending in {selected_card.get("card_number")[-4:]}.')
            print("Payment successful!")
        else:
            print("Invalid card selection. Payment cancelled.")
            return
    else:
        print("Invalid payment method selected. Please try again.")
        return
    # --- [Task 1] Implementation 2: Payment System End ---
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
        wallet=login_info['wallet'],
        cards = login_info.get('cards', [])
    )

    # Get user input for either selecting a product by its number, checking their cart or logging out
    while True:
        choice: str = UserInterface.get_user_input(
            prompt='\nEnter product number or (d to display products, c to check cart, p to profile/cards, l to logout): '
        ).lower()
        if choice.startswith('d'):
            display_products_available_for_purchase()
        elif choice.startswith('c'):
            if check_cart(user=user, cart=global_cart) is False:
                continue  # The user has selected not to check out their cart
            else:
                pass
               #check_cart does not return false if the user cannot check out because of invalid balance
                #pass  # TODO: Task 4: update the wallet information in the users.json file
                #new_balance = user.wallet - global_cart.get_total_price()
                #if new_balance < 0:
                    #continue
                #else:
                    #users = UserDataManager.load_users()
                    #for oneuser in users:
                        #if oneuser['username'] == user.name:
                            #oneuser['wallet'] = new_balance
                    #UserDataManager.save_users(users)"""

# [Task 1 Implementation] Implement the entry point for managing credit cards
        elif choice.startswith('p') :
            manage_credit_cards(user.name)
            latest_data = UserDataManager.load_users()
            for u in latest_data:
                if u['username'] == user.name:
                    user.cards = u.get('cards', [])
                    print(f"\n[System] Profile synced. Local cards updated: {len(user.cards)}")
                    break
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
# manual for testing
if __name__ == "__main__":
    fake_login_info = {
        'username': 'Ramanathan',
        'wallet': 100.0,
        'cards': [{"card_number": "88888888",
                "expiry": "12/30",
                "name": "Test Rama",
                "cvv": "123"}]
    }
    print("--- Starting Checkout Test ---")
    checkout_and_payment(fake_login_info)
