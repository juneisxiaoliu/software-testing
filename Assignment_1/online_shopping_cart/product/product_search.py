from online_shopping_cart.product.product_data import get_csv_data, PRODUCTS_FILE_PATHNAME
from re import search, IGNORECASE

############################
# PRODUCT SEARCH CONSTANTS #
############################


PRODUCT_HEADER_INDEX: str = 'Product'


############################
# PRODUCT SEARCH FUNCTIONS #
############################


def display_csv_as_table(csv_filename=PRODUCTS_FILE_PATHNAME) -> None:
    """
    Display all the products row by row, starting with the header
    """
    header, csv_reader = get_csv_data(csv_filename=csv_filename)
    print(f'\n{header}')
    for row in csv_reader:
        print(row)


def display_filtered_table(csv_filename=PRODUCTS_FILE_PATHNAME, search_target=None) -> None:
    """
    Display products filtered by name row by row, starting with the header
    """
    if search_target is None:
        display_csv_as_table(csv_filename=csv_filename)
    else:
        header, csv_reader = get_csv_data(csv_filename=csv_filename)
        print(f'\n{header}')

        condition_index: int = header.index(PRODUCT_HEADER_INDEX)
        for i, row in enumerate(csv_reader):
            if search(pattern=row[condition_index], string=search_target.capitalize(), flags=IGNORECASE):
                print(row)
