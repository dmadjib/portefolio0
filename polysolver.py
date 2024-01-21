#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module de résolution du projet Poly#.
"""
from utils.Drone import Drone
from utils.Order import Order
from utils.Warehouse import Warehouse
from utils.Segment import Segment
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
    total_quantity ={}
    # Parcourir chaque commande et mettre à jour le dictionnaire
    for order in challenge.orders:
        for product, quantity in order.products.items():
            if product in total_quantity.keys():
                total_quantity[product] += quantity
            else:
                total_quantity[product] = quantity

    # Dictionnaire pour stocker les entrepôts pour chaque produit
    product_warehouses = {}

    # Parcourir chaque entrepôt et mettre à jour le dictionnaire
    for warehouse in challenge.warehouses:
        for product in range(len(warehouse.products)):
            if warehouse.products[product] > 0:
                if product in product_warehouses.keys():
                    product_warehouses[product].append(warehouse.id)
                else :
                    product_warehouses[product] = [warehouse.id]

    total_quantity_sorted = sorted(total_quantity.keys(), key=lambda p: total_quantity[p], reverse=True)
    
    last_drone = 0

    for product in total_quantity_sorted:
        can_load = challenge.max_payload // int(challenge.product_weights[product])
        while total_quantity[product] > 0:
            if last_drone >= len(challenge.drones):
                last_drone = 0

            drone = challenge.drones[last_drone]
                
            warehouses = sorted(product_warehouses[product], key=lambda id: Drone.calculate_distance(drone.location, challenge.warehouses[id].location))

            warehouse_count = 0

            while total_quantity[product] != 0 and drone.can_load(product, 1, challenge.product_weights):
                # Ne va jamais dépasser le nombre de warehouses
                warehouse = challenge.warehouses[warehouses[warehouse_count]]

                # 3 cas possibles
                # Soit ce qu'il reste à livrer
                # Soit ce qu'il reste dans le warehouse
                # Soit ce que le drone peut porter
                if can_load >= total_quantity[product] and warehouse.products[product] >= total_quantity[product]:
                    load = total_quantity[product]
                elif warehouse.products[product] < can_load:
                    load = warehouse.products[product]
                else:
                    load = can_load

                total_quantity[product] -= load
                drone.load(warehouse, product, load, challenge.product_weights, solutions)
            
                if warehouse.products[product] == 0:
                    product_warehouses[product].remove(warehouse.id)
            
                warehouse_count += 1
            
            orders = list(filter(lambda o: product in o.products.keys() and o.products[product] > 0, challenge.orders))

            orders = sorted(orders, key=lambda o: Drone.calculate_distance(o.location, drone.location))

            order_count = 0

            while drone.products[product] > 0:
                order = challenge.orders[orders[order_count].id]

                deliver = min(drone.products[product], order.products[product])

                drone.deliver(order, product, deliver, challenge.product_weights, solutions)

                order_count += 1

            last_drone += 1

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