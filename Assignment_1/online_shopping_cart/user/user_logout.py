from online_shopping_cart.user.user_interface import UserInterface

#########################
# USER LOGOUT FUNCTIONS #
#########################


def logout(cart) -> bool:
    if not cart.is_empty():
        # Retrieve cart items if cart is not empty
        print('Your cart is not empty. You have the following items:')
        for item in cart.retrieve_items():
            print(str(item))

    # Confirm whether to logout or not
    if UserInterface.get_user_input(prompt='Do you still want to logout? - y/n: ').lower().startswith('y'):
        print('You have been logged out.')
        return True
    else:
        return False
