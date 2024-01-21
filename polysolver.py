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

    # À partir de ce nombre de warehouses visités en moyenne, il y aura des drones alloués aux échanges inter-warehouses
    DEADLINE = 2
    # Quand il y a les échanges d'activés, il y aura RATIO fois le nombre de warehouses visités en moyenne de drones
    RATIO = 3
    # La proportion maximale de drones alloués aux échanges inter-warehouses
    MAX_DRONES = 3/4

    # Calcul du nombre de drones affecté aux échanges inter-warehouses

    # Tri des orders (du plus proche au plus éloigné d'un warehouse, peu importe lequel)
    sorted_orders = sorted(challenge.orders, key=lambda o:min([Drone.calculate_distance(o.location, w.location) for w in challenge.warehouses]))

    # Récupération du nombre de warehouses à visiter pour finir chaque commande
    needed_warehouses = {order.id:[] for order in challenge.orders}
    warehouses = challenge.warehouses

    # Pour chaque order (en partant des plus proches d'un warehouse)
    for o_count, order in enumerate(sorted_orders):
        # Tri des warehouses en fonction de leur distance avec l'order
        sorted_warehouses = sorted(challenge.warehouses, key=lambda w:Drone.calculate_distance(w.location, order.location))

        # Pour chaque warehouse
        for w_count, warehouse in enumerate(warehouses):
            # Pour chaque produit
            for product, amount in order.products.items():
                # Si il est présent dans le warehouse, et qu'il est demandé dans l'order
                if warehouse.products[product] > 0 and order.products[product] > 0:
                    # Le produit est retiré du warehouse et de l'order
                    load = amount if warehouse.products[product] >= amount else warehouse.products[product]
                    sorted_orders[o_count].products[product] -= load
                    sorted_warehouses[w_count].products[product] -= load
                    
                    # Le warehouse est ajouté à la liste des warehouses visité
                    needed_warehouses[order.id].append(warehouse.id)

    # Nombre moyen de différents warehouses visités (arrondi à l'unité)
    average_warehouses = round(sum([len(set(w)) for w in needed_warehouses.values()])) / len(needed_warehouses.keys())

    # Détermine si il y aura des drones utilisés pour l'échange inter-warehouses
    has_exchanges = average_warehouses > DEADLINE

    if has_exchanges:
        # Nombre de drones alloués à l'échange inter-warehouses
        # Plafonne le nombre de drones alloués
        nb_drones = min(len(challenge.drones) * RATIO, round(len(challenge.drones) * MAX_DRONES))

        # Déclare les drones alloués
        for i in range(nb_drones):
            challenge.drones[i].is_exchanging = True

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

            if move[1] in {'L', 'U'}:
                # Si l'opération est une charge ou décharge, alors le drone va vers un warehouse
                next_pos = challenge.warehouses[move[2]].location
            elif move[1] == 'D':
                # Si l'opération est un dépôt, alors le drone va vers une order
                next_pos = challenge.orders[move[2]].location
                # Retrait de la liste des commandes des items livrés
                challenge.orders[move[2]].products[move[3]] -= move[4]
                # Si après le dépôt l'order est complétée
                if challenge.orders[move[2]].is_completed():
                    completed = True
            elif move[1] == 'W':
                # Si l'opération est une attente, alors on ajoute le nombre de tours à attendre
                turns += move[2]
                continue

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