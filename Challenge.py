"""
@title : Challenge
@description : Class defining what a challenge is
@author : El ARAJNA Lina , FAKHFAKH Ahmed , LALANNE-TISNE Nino, Madjibaye Donatien
@date : Last Modification : 23/12/2023
"""

from utils.Drone import Drone


class Challenge:
    """
        Class is defined by:
            - row_count
            - columns_count
            - drone_count
            - deadline
            - max_payload
            - product_weights
            - warehouses
            - orders
        """

    """ Constructor """

    def __init__(self, rows_count, columns_count, drone_count, deadline, max_payload, product_weights, warehouses,
                 orders):
        self.rows_count = rows_count
        self.columns_count = columns_count
        self.drone_count = drone_count
        self.deadline = deadline
        self.max_payload = max_payload
        self.product_weights = product_weights
        self.warehouses = warehouses
        self.orders = orders
        self.drones = []
        for i in range(drone_count):
            self.drones.append(Drone(i, self.max_payload, self.warehouses[0].location))
