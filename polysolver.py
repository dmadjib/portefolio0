#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module de résolution du projet Poly#.
"""
from utils.Drone import Drone
from utils.Order import Order
from utils.Warehouse import Warehouse
from utils.Segment import Segment
import math
import copy
 
def save_solution (file_name, tab_solution) : 
    with open(f'{file_name}.txt', 'w') as outfile :
        outfile.write(str(len(tab_solution)) + '\n')
        for i in range(len(tab_solution)) : 
            for j in range(len(tab_solution[i])) :
                outfile.write(str(tab_solution[i][j]) + ' ')
            outfile.write('\n')

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

def naive(challenge):
    solutions = []

    for count, order in enumerate(challenge.orders):
        drone = challenge.drones[count%len(challenge.drones)]

        warehouses = sorted(challenge.warehouses, key=lambda w:Drone.calculate_distance(w.location, drone.location))

        warehouse_count = 0

        while not order.is_completed():
            while drone.current_load < challenge.max_payload and not drone.has_remaining(order):
                warehouse = warehouses[warehouse_count]

                for product, amount in order.products.items():
                    if not drone.has_product_asked(product, amount) and warehouse.products[product] > 0:
                        to_load = amount if warehouse.products[product] >= amount else warehouse.products[product]

                        for _ in range(to_load):
                            if drone.can_load(product, 1, challenge.product_weights):
                                drone.load(warehouse, product, 1, challenge.product_weights, solutions)

                warehouse_count += 1

                if warehouse_count == len(warehouses):
                    warehouse_count = 0
                    break

            for product, quantity in drone.products.items():
                if product in order.products and order.products[product] > 0:
                    to_deliver = quantity if order.products[product] >= quantity else order.products[product]
                    drone.deliver(order, product, to_deliver, challenge.product_weights, solutions)

    return solutions

def stack_segments(challenge):
    solutions = []

    # Liste des segments
    segments = []

    # Construction d'un segment pour chaque order
    for order in challenge.orders:
        # Liste des ID des warhouses trié du plus proche au plus éloigné
        warehouses = list(map(lambda w: w.id, sorted(challenge.warehouses, key=lambda w:Drone.calculate_distance(w.location, order.location))))

        warehouse_count = 0

        # Liste des actions à réaliser pour ce segment
        actions = []

        # Faux drone utilisé pour tracer l'itinéraire à réaliser pour une order
        drone = challenge.drones[0]

        while not order.is_completed():
            # Tant que le drone n'est pas plein ou n'a pas tout
            while drone.current_load < challenge.max_payload and not drone.has_remaining(order):
                # ID du warehouse suivant à vérifier
                warehouse = warehouses[warehouse_count]

                # Pour chaque produit
                for product, amount in order.products.items():
                    # Si le drone n'a pas le produit demandé et que le warehouse l'a
                    if not drone.has_product_asked(product, amount) and challenge.warehouses[warehouse].products[product] > 0:
                        # Calcul de la quantité à charger
                        if challenge.warehouses[warehouse].products[product] >= amount:
                            to_load = amount
                        else:
                            to_load = challenge.warehouses[warehouse].products[product]

                        # Chargement de ce qui est possible
                        for _ in range(to_load):
                            if drone.can_load(product, 1, challenge.product_weights):
                                drone.load(challenge.warehouses[warehouse], product, 1, challenge.product_weights, actions)


                # Warehouse suivant
                warehouse_count += 1

                if warehouse_count == len(warehouses):
                    warehouse_count = 0
                    break

            # Livraison de chaque item à l'order
            for product, quantity in drone.products.items():
                if product in order.products and order.products[product] > 0 and quantity > 0:
                    to_deliver = quantity if order.products[product] >= quantity else order.products[product]
                    drone.deliver(order, product, to_deliver, challenge.product_weights, actions)

        # Quand l'order est complétée, son chemin (actions) est ajouté en tant que nouveau segment
        segments.append(Segment(Segment.get_location(actions[0], challenge), order.location, challenge, actions))

    # Trace du parcours de chaque drone
    paths = {drone.id:[] for drone in challenge.drones}
    # Sauvegarde du temps pris pour toutes les commandes d'un drone
    # Sert à ne pas recalculer à chaque itération
    lenght_paths = {drone.id:0 for drone in challenge.drones}

    # Solution temporaire pour répartir les drones dans la carte à la première itération
    # (On mise sur le fait que la localisation des orders n'est pas correlé à sa place dans la liste des orders de challenge)
    for id in sorted(paths.keys()):
        # ID vaut 0...len(drones)
        # Le if est pour les cas où il y a moins de commandes que de drones
        if len(segments) > 0:        
            segment = segments.pop()
            paths[id].append(segment)
            lenght_paths[id] += segment.turns

    # On cherche à attribuer tous les segments à des drones
    while len(segments) > 0:
        # Sélection du drone qui est le moins occupé
        id = min(lenght_paths, key=lenght_paths.get)

        # Choix du segment qui commence le plus proche de lui
        segment = min(segments, key=lambda segment:Drone.calculate_distance(segment.start, paths[id][-1].end))
        # On retire le segment de la liste des segments à attribuer
        segments.remove(segment)
        # Ajout du segment à la liste des segments visités par le drone
        paths[id].append(segment)
        # Ajout du temps de déplacement vers le segment et celui du segment
        lenght_paths[id] += segment.turns + math.ceil(Drone.calculate_distance(segment.start, paths[id][-1].end))

    # Quand tous les segments ont été attribués
    # Ajout de toutes les actions à la liste des solutions

    # Pour chaque drone
    for id, segments in paths.items():
        # Pour chaque segment
        for segment in segments:
            # Pour chaque action
            for action in segment.actions:
                # Ajout dans les solutions en renseignant l'ID du drone
                solutions.append([id, action[1], action[2], action[3], action[4]])
    
    return solutions

def solve(challenge):
    solvers = {}

    solvers['stack_segments'] = stack_segments(copy.deepcopy(challenge))
    solvers['product_by_product'] = []
    solvers['naive'] = naive(copy.deepcopy(challenge))

    best_solution = max(solvers.keys(), key=lambda a: score_solution(solvers[a], copy.deepcopy(challenge)))

    print('La meilleure solution est :', best_solution)

    return solvers[best_solution]
