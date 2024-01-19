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

    # Regrouper les commandes par adresses
    locations = {}

    # Pour chaque commande
    for order in challenge.orders:
        if order.location not in locations.keys():
            locations[order.location] = [order]
        else:
            locations[order.location].append(order)

    # Pour chaque adresse
    for location, orders in locations.items():
        # Liste des warhouses trié du plus proche au plus éloigné
        warehouses = sorted(challenge.warehouses, key=lambda w:Drone.calculate_distance(w.location, location))
        # Pour chaque commande
        for order in orders:
            # Pour chaque objet demandé
            for product, amount in order.products.items():
                # Produits qu'il reste à trouver
                remaining = amount
                # Pour chaque warehouse tant que la quantité demandé n'est pas atteinte
                # Par définition, si l'on parcours tous les warehouses, il y aura ce qui est demandé
                for warehouse in warehouses:
                    # Si tous les produits ont été trouvé
                    if remaining == 0:
                        break

                    # Si le warehouse a des exemplaires du produit souhaité
                    if warehouse.products[product] > 0:
                        # On prend le nombre de produits nécessaire, ou tous si il n'y a pas tout ce qu'il faut
                        to_load = remaining if warehouse.products[product] >= remaining else warehouse.products[product]
                        remaining -= to_load
                        warehouse.products[product] -= to_load
                        
                        # Calcul du nombre de drones nécessaires pour transporter les produits de ce warehouse
                        nb_drones = math.ceil((to_load * int(challenge.product_weights[product])) / challenge.max_payload)
                        # Recherche des drones les plus proches du warehouse
                        drones = sorted(challenge.drones, key=lambda d:Drone.calculate_distance(d.current_location, warehouse.location))
                        # Sélection des drones conservés pour ce warehouse
                        for drone in [drones[i] for i in range(nb_drones)]:
                            # Divise la charge entre les différents drones
                            if (to_load * int(challenge.product_weights[product])) <= challenge.max_payload:
                                drone_load = to_load
                            else:
                                for i in range(to_load):
                                    if drone.can_load(product, 1, challenge.product_weights):
                                        drone_load += int(challenge.product_weights[product])
                                        to_load -= 1 

                            solutions.append([drone.id, 'L', warehouse.id, product, drone_load])
                            solutions.append([drone.id, 'D', order.id, product, drone_load])
                            challenge.drones[drone.id].current_location = location

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