from online_shopping_cart.user.user_data import UserDataManager
from online_shopping_cart.user.user_interface import UserInterface


def manage_credit_cards(current_username: str):
    """
    Allow the logged-in user to view and add credit cards.
    Task 1 Requirement: "Add a module that allows the user to change these details in the file."
    """
    print(f"\n--- Managing Credit Cards for User: {current_username} ---")

    # 1. reload the latest data to ensure data consistency
    all_users = UserDataManager.load_users()

    # 2. fined the current user object
    target_user = None
    for user in all_users:
        if user['username'] == current_username:
            target_user = user
            break

    if not target_user:
        print("Error: User profile not found in database.")
        return

    # 3. Ensure 'cards' key exists
    if 'cards' not in target_user:
        target_user['cards'] = []

    # 4. loop for managing cards
    while True:
        # 4.1 show existing cards
        current_cards = target_user['cards']
        if not current_cards:
            print("\n[Status] No saved credit cards.")
        else:
            print(f"\n[Status] You have {len(current_cards)} saved card(s):")
            for idx, card in enumerate(current_cards):
                # only show last 4 digits for security
                masked_num = card.get('card_number', '****')[-4:]
                print(f"  {idx + 1}. {card.get('name')} (Ends in {masked_num}) - Exp: {card.get('expiry')}")

        # 4.2 ask for user action
        choice = UserInterface.get_user_input(
            prompt="\nOptions: (a) Add new card, (b) Back to main menu: "
        ).lower()

        if choice == 'a':
            # --- add new card logic  ---
            print("Enter new card details:")
            c_num = UserInterface.get_user_input(prompt="Card Number: ")
            c_expiry = UserInterface.get_user_input(prompt="Expiry Date (MM/YY): ")
            c_name = UserInterface.get_user_input(prompt="Name on Card: ")
            c_cvv = UserInterface.get_user_input(prompt="CVV: ")

            new_card = {
                "card_number": c_num,
                "expiry": c_expiry,
                "name": c_name,
                "cvv": c_cvv
            }
            # add to user's card list
            target_user['cards'].append(new_card)

            # save updated users data
            UserDataManager.save_users(all_users)
            print("✅ Card added and saved successfully!")

        elif choice == 'b':
            # return to main menu
            break
        else:
            print("Invalid option. Please try again.")