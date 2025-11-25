from online_shopping_cart.product.product import Product

##################################
# CHECKOUT SHOPPING CART CLASSES #
##################################


class ShoppingCart:
    """
    ShoppingCart class to represent the user's shopping cart
    """

    def __init__(self) -> None:
        self.items: list[Product] = list()

    def __get_product_by_name(self, product_search: Product) -> list[Product]:
        return [product_i for product_i in self.items if product_i.name == product_search.name]

    def add_item(self, product) -> None:
        """
        Add a product to the cart if not already there, otherwise increment the number of units
        """
        product_in_items: list[Product] = self.__get_product_by_name(product)
        if not product_in_items:
            self.items.append(product)
        else:
            product_in_items[0].units += 1

    def remove_item(self, product: Product) -> None:
        """
        Remove a product from the cart
        """
        product_in_items: list[Product] = self.__get_product_by_name(product)
        product_in_items[0].units -= 1
        if product_in_items[0].units == 0:
            self.items.remove(product)

    def retrieve_items(self) -> list[Product]:
        """
        Retrieve the items in the cart
        """
        return self.items

    def clear_items(self) -> None:
        """
        Clear all items from the cart
        """
        self.items = list()

    def is_empty(self) -> bool:
        """
        Checks if the cart is empty
        """
        return self.items == []

    def get_total_price(self) -> float:
        """
        Calculate the total price of items in the cart
        """
        return sum(item.price * item.units for item in self.items)
