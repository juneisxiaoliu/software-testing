from online_shopping_cart.user.user_authentication import UserAuthenticator, PasswordValidator
from online_shopping_cart.user.user_interface import UserInterface
from online_shopping_cart.user.user_data import UserDataManager
########################
# USER LOGIN FUNCTIONS #
########################

def is_quit(input_argument: str) -> bool:
    return input_argument.lower() == 'q'

def login() -> dict[str, str | float] | None:
    username: str = UserInterface.get_user_input(prompt="Enter your username (or 'q' to quit): ")
    if is_quit(input_argument=username):
        exit(0)  # The user has quit

    # loading data
    user_data = UserDataManager.load_users()
    #Check whether the user exists
    user_exists = False
    for user in user_data:
        if user['username'] == username:
            user_exists = True
            break
    #Task 1: Handling Logic for Non-Existent Users
    if not user_exists:
        print(f"User '{username}' not found.")
        register_choice = UserInterface.get_user_input(prompt="Would you like to register another user? (y/n)")

        if register_choice.lower() in ['yes', 'y']:
            new_password = UserInterface.get_user_input(prompt="Enter a password for registration: ")
            if PasswordValidator.is_valid(new_password):
                # Task 1: extend registration to include credit card details
                cards_list = []
                print("\n--- Credit Card Setup ---")
                while True:
                    want_card = UserInterface.get_user_input(prompt="Do you want to add a credit card? (y/n): ")
                    if want_card.lower() not in ['y', 'yes']:
                        break  # Exit the loop if the user doesn't want to add more cards
                    c_num = UserInterface.get_user_input(prompt="Card Number: ")
                    c_expiry = UserInterface.get_user_input(prompt="Expiry Date (MM/YY): ")
                    c_name = UserInterface.get_user_input(prompt="Name on Card: ")
                    c_cvv = UserInterface.get_user_input(prompt="CVV: ")
                    print(f"Adding Card #{len(cards_list) + 1}:")
                    new_card = {
                        "card_number": c_num,
                        "expiry": c_expiry,
                        "name": c_name,
                        "cvv": c_cvv
                    }
                    cards_list.append(new_card)
                    print("Card added successfully!")
                UserAuthenticator.register(username, new_password, user_data, cards=cards_list)
                print("Registration successful! You are now logged in.")
                return {
                    "username": username,
                    "wallet": 0.0
                }
            else:
                print("Password validation failed. Requirements: Min 8 chars, 1 uppercase, 1 special symbol.")
                return None
        else:
            # user doesn't want to register
            return None


    #Only when the user exists should the original login process continue.
    password: str = UserInterface.get_user_input(prompt="Enter your password (or 'q' to quit): ")
    if is_quit(input_argument=password):
        exit(0)   # The user has quit

    is_authentic_user: dict[str, str | float] = UserAuthenticator().login(
        username=username,
        password=password,
        data=UserDataManager.load_users()
    )
    if is_authentic_user is not None:
        return is_authentic_user

    return None
if __name__ == "__main__":
    # Simple test for manual login
    print("--- Starting Manual Login Test ---")
    result = login()
    if result:
        print(f"\n[Debug Info] Logged in User Data: {result}")