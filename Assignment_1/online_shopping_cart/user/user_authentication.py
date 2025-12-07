###############################
# USER AUTHENTICATION CLASSES #
###############################
from online_shopping_cart.user.user_data import UserDataManager
import string

class PasswordValidator:

    @staticmethod
    def is_valid(password) -> bool:
        pass  # TODO: Task 1: validate password for registration
        if len(password) < 8:
            return False

        has_upper = any(char.isupper() for char in password)
        # string.punctuation contains common punctuation marks
        has_special = any(char in string.punctuation for char in password)

        return has_upper and has_special


class UserAuthenticator:

    @staticmethod
    def login(username, password, data) -> dict[str, str | float] | None:
        is_user_registered: bool = False

        for entry in data:
            if entry['username'].lower() == username.lower():
                is_user_registered = True
            if is_user_registered:
                if entry['password'].lower() == password.lower():
                    print('Successfully logged in.')
                    return {
                        'username': entry['username'],
                        'wallet': entry['wallet'],
                        'cards': entry.get('cards', [])
                    }
                break

        if not is_user_registered:
            print('User is not registered.')
        else:
            print('Login failed.')
        return None

    @staticmethod
    def register(username, password, data, cards = None) -> None:
        if cards is None: cards = []
        new_user = {
             "username": username,
             "password": password,
             "cards": cards,
             "wallet": 0.0
         }
        data.append(new_user)
        UserDataManager.save_users(data)
