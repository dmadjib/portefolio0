"""
@title : Warehouse
@description : Class defining what a warehouse is
@author : El ARAJNA Lina , FAKHFAKH Ahmed , LALANNE-TISNE Nino, Madjibaye Donatien
@date : Last Modification : 23/12/2023
"""


class Warehouse:
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
        self.products = products
