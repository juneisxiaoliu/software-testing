################
# USER CLASSES #
################


class User:
    """
    User class to represent user information
    """

    def __init__(self, name, wallet,cards = None) -> None:
        self.name: str = name
        self.wallet: float = wallet
        self.cards: list = cards if cards is not None else []
