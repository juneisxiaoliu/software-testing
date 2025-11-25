###################
# PRODUCT CLASSES #
###################


class Product:
    """
    Product class to represent product information
    """

    def __init__(self, name: str, price: float, units: int) -> None:
        self.name: str = name
        self.price: float = price
        self.units: int = units

    def __str__(self) -> str:
        return f'{self.name} - ${self.price} - Units: {self.units}'

    def get_product_unit(self):
        self.units -= 1
        return Product(name=self.name, price=self.price, units=1)

    def add_product_unit(self) -> None:
        self.units += 1
