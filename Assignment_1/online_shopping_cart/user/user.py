################
# USER CLASSES #
################


class User:
    """
    User class to represent user information
    """

    def __init__(self, name, wallet) -> None:
        self.name: str = name
        self.wallet: float = wallet
