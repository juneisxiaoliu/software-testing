from online_shopping_cart.product.product import Product
from csv import DictReader, reader

##########################
# PRODUCT DATA CONSTANTS #
##########################


PRODUCTS_FILE_PATHNAME: str = './files/products.csv'


##########################
# PRODUCT DATA FUNCTIONS #
##########################


def get_csv_data(csv_filename=PRODUCTS_FILE_PATHNAME, is_dict=False) -> (list[dict[str, str | float]] |
                                                                         tuple[list[str], list[reader]]):
    with open(file=csv_filename, mode='r', newline='') as csv_file:
        if is_dict:
            return list(DictReader(csv_file))
        csv_reader: reader = reader(csv_file)
        return next(csv_reader), list(csv_reader)


def get_products(file_name=PRODUCTS_FILE_PATHNAME) -> list[Product]:
    """
    Load products from a CSV file
    """
    products: list[Product] = []
    for row in get_csv_data(csv_filename=file_name, is_dict=True):
        products.append(Product(
            name=row['Product'],
            price=float(row['Price']),
            units=int(row['Units'])
        ))
    return products
