"""
@title : Warehouse
@description : Class defining what is a warehouse
@author : El ARAJNA Lina , FAKHFAKH Ahmed , LALANNE-TISNE Nino, Madjibaye Donatien
@date : Last Modification : 25/01/2024
"""

from utils.types import Location


class Warehouse:
    """
    Class is defined by:
        - id
        - location
        - products
    """

    """ Constructor """

    def __init__(self, warehouse_id: int, location: Location, products: list[int]):
        self.id = warehouse_id
        self.location = location
        self.products = products
