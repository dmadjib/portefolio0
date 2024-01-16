"""
@title : Order
@description : Class defining what an order is
@author : El ARAJNA Lina , FAKHFAKH Ahmed , LALANNE-TISNE Nino, Madjibaye Donatien
@date : Last Modification : 23/12/2023
"""


class Order:
    """
        Class is defined by:
            - id
            - x
            - y
            - products
        """

    """ Constructor """

    def __init__(self, id, x, y, products) -> None:
        self.id = id
        self.location = (x, y)
        self.amount = len(products)
        self.products = {product_type: products.count(product_type) for product_type in products}

    def is_completed(self):
        """
            - Check if an order is completed or not
            :return:        True if the drone is completed, False if it is not
        """
        return all(q == 0 for q in self.products.values())
