#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module de résolution du projet Poly#.
"""
from utils.Drone import Drone
from utils.Order import Order
from utils.Warehouse import Warehouse
 
def save_solution (file_name, tab_solution) : 
    
    with open(f'{file_name}.txt', 'w') as outfile :
        outfile.write(str(len(tab_solution)) + '\n')
        for i in range(len(tab_solution)) : 
            for j in range(len(tab_solution[i])) :
                outfile.write(str(tab_solution[i][j]) + ' ')
            outfile.write('\n')

def solve(challenge):
    solutions = []

    drone = Drone(1, challenge.max_payload, (0, 0))

    order = challenge.orders[0]

    warehouses = sorted(challenge.warehouses, key=lambda w:Drone.calculate_distance(w.location, drone.current_location))

    warehouse_count = 0

    while not order.is_completed():
        while drone.current_load < challenge.max_payload and not drone.has_remaining(order):
            warehouse = warehouses[warehouse_count]

            for product, amount in order.products.items():
                if not drone.has_product_asked(product, amount) and warehouse.products[product] > 0:
                    to_load = amount if warehouse.products[product] >= amount else warehouse.products[product]
                        
                    if drone.can_load(product, to_load, challenge.product_weights):
                        drone.load(warehouse, product, to_load, challenge.product_weights, solutions)

            warehouse_count += 1

            if warehouse_count == len(warehouses):
                warehouse_count = 0
                break

        for product, quantity in drone.products.items():
            if product in order.products and order.products[product] > 0:
                to_deliver = quantity if order.products[product] >= quantity else order.products[product]
                drone.deliver(order, product, to_deliver, challenge.product_weights, solutions)

    return solutions

def score_solution():
    pass