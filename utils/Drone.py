"""
@title : Drone
@description : Class defining what a drone is
@author : El ARAJNA Lina , FAKHFAKH Ahmed , LALANNE-TISNE Nino, Madjibaye Donatien
@date : Last Modification : 23/12/2023
"""

import math


class Drone:
    """
        Class is defined by:
            - drone_id
            - max_payload
            - initial_location
        """

    """ Constructor """

    def __init__(self, drone_id, max_payload, initial_location):
        self.id = drone_id
        self.max_payload = max_payload
        self.location = initial_location
        self.current_load = 0
        self.available_turn = 0
        self.products = {}

    def available(self, current_turn):
        """
            - Check if a drone is available or not
            :return:        True if the drone is available, False if it is not
        """
        return current_turn >= self.available_turn

    def can_load(self, product_type, quantity, product_weights):
        """
            - Check if a drone can load a specific quantity of a product
            :return:        True if the drone can load, False if it can not
        """
        incoming_weight = quantity * int(product_weights[product_type])
        return self.current_load + incoming_weight <= self.max_payload

    def has_remaining(self, order):
        """
            - Check for each product in an order, if the drone has the required quantity of this product
            :return:        True if the drone has the required quantity of all the product of the order ,
                            False if it has not
        """
        return all(self.has_product_asked(p, q) for p, q in order.products.items())

    def has_product_asked(self, product, quantity):
        """
            - Check if a drone has the required quantity of a product
            :return:        True if the drone has the required quantity of a product , False if it has not
        """
        return product in self.products and self.products[product] >= quantity

    def fly_to(self, location):
        """
            - Update the turn of the drone
        """
        distance = Drone.calculate_distance(self.location, location)
        self.available_turn += int(math.ceil(distance))

    def load(self, warehouse, product_type, quantity, product_weights, history):
        """
            - Try to load a specific quantity of a product from a warehouse
            - Update the solution with the appropriate command if the drone has loaded the product
        """
        total_weight = quantity * int(product_weights[product_type])
        self.current_load += total_weight
        history.append([self.id, 'L', warehouse.id, product_type, quantity])
        self.location = warehouse.location

        try:
            self.products[product_type] += quantity
        except KeyError:
            self.products[product_type] = quantity

        warehouse.products[product_type] -= quantity

    def deliver(self, order, product_type, quantity, product_weights, history):
        """
            - Update the solution with the appropriate command after the drone has delivered the product
        """
        order.products[product_type] -= quantity
        self.current_load -= quantity * int(product_weights[product_type])
        self.products[product_type] -= quantity
        history.append([self.id, 'D', order.id, product_type, quantity])
        self.location = order.location

    """ Static Method """
    @staticmethod
    def calculate_distance(location1, location2):
        """
            - Calculate the distance between two location
            :return:        The distance
        """
        return math.sqrt((location1[0] - location2[0]) ** 2 + (location1[1] - location2[1]) ** 2)
