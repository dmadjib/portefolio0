#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module de résolution du projet Poly#.
"""
from utils.Drone import Drone
from utils.Order import Order
from utils.Warehouse import Warehouse
import math
 
def save_solution (file_name, tab_solution) : 
    
    with open(f'{file_name}.txt', 'w') as outfile :
        outfile.write(str(len(tab_solution)) + '\n')
        for i in range(len(tab_solution)) : 
            for j in range(len(tab_solution[i])) :
                outfile.write(str(tab_solution[i][j]) + ' ')
            outfile.write('\n')

def solve(challenge):
    solutions = []

    for drone in challenge.drones:
        order = challenge.orders[drone.id]

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


def score_solution(solution, challenge):
    # Initialisation du score
    score = 0

    for drone in challenge.drones:
        # On ne garde que les opérations du drone en question
        moves = list(filter(lambda move: move[0] == drone.id, solution))

        turns = 0

        # Position initiale
        pos = challenge.warehouses[0].location

        for move in moves:
            # L'opération actuelle ne complète pas d'order par défaut
            completed = False

            if move[1] == 'L':
                # Si l'opération est une charge, alors le drone va vers un warehouse
                next_pos = challenge.warehouses[move[2]].location
            elif move[1] == 'D':
                # Si l'opération est un dépôt, alors le drone va vers une order
                next_pos = challenge.orders[move[2]].location
                # Retrait de la liste des commandes des items livrés
                challenge.orders[move[2]].products[move[3]] -= move[4]
                # Si après le dépôt l'order est complétée
                if challenge.orders[move[2]].is_completed():
                    completed = True

            # Ajout des tours pour le déplacement (après dépôt / charge)
            turns += math.ceil(Drone.calculate_distance(pos, next_pos))
            # Mise à jour de la localisation du drone
            pos = next_pos

            if completed:
                # Si l'order est complétée, alors ajout du score (prise en compte du déplacement mais pas du temps pris pour le dépôt)
                score += math.ceil(((challenge.deadline - turns) / challenge.deadline) * 100)

                # Pris en compte du tour passé à charger / déposer pour les prochaines opérations
            turns += 1

    return score