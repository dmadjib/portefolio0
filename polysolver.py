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
 
def save_solution (file_name, tab_solution): 
    with open(f'{file_name}.txt', 'w') as outfile :
        outfile.write(str(len(tab_solution)) + '\n')
        for i in range(len(tab_solution)) : 
            for j in range(len(tab_solution[i])) :
                outfile.write(str(tab_solution[i][j]) + ' ')
            outfile.write('\n')

def score_solution(solution, challenge):
    # Initialisation du score
    score = 0

    completed_orders = []

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
                # Si l'opération est une charge, alors le drone va vers un warehouse
                next_pos = challenge.warehouses[move[2]].location
            elif move[1] == 'D':
                # Si l'opération est un dépôt, alors le drone va vers une order
                next_pos = challenge.orders[move[2]].location
                # Retrait de la liste des commandes des items livrés
                challenge.orders[move[2]].products[move[3]] -= move[4]
                # Si après le dépôt l'order est complétée
                if challenge.orders[move[2]] not in completed_orders and challenge.orders[move[2]].is_completed():
                    completed = True
                    completed_orders.append(challenge.orders[move[2]])
            elif move[1] == 'W':
                turns += move[2]
                break

            # Distance parcourue pour aller effectuer l'action
            distance = Drone.calculate_distance(pos, next_pos)
            # Mise à jour de la localisation du drone
            pos = next_pos

            # Ajout des tours pour le déplacement
            turns += distance

            if completed:
                # Si l'order est complétée, alors ajout du score (prise en compte du déplacement mais pas du temps pris pour le dépôt)
                score += math.ceil(((challenge.deadline - turns) / challenge.deadline) * 100)

            # Temps utilisé pour livrer, charger ou décharger
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
        lenght_paths[id] += segment.turns + Drone.calculate_distance(segment.start, paths[id][-1].end)

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

def product_by_product(challenge):
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
    
    for product in total_quantity_sorted:
        can_load = challenge.max_payload // int(challenge.product_weights[product])
        while total_quantity[product] > 0:
            for drone in challenge.drones:
                if total_quantity[product] == 0:
                    break
                    
                warehouses = sorted(product_warehouses[product], key=lambda id: Drone.calculate_distance(drone.location, challenge.warehouses[id].location))

                warehouse_count = 0
                load_remaining = can_load

                while total_quantity[product] != 0 and load_remaining > 0:
                    # Ne va jamais dépasser le nombre de warehouses
                    warehouse = challenge.warehouses[warehouses[warehouse_count]]

                    # 3 cas possibles
                    # Soit ce qu'il reste à livrer
                    # Soit ce qu'il reste dans le warehouse
                    # Soit ce que le drone peut porter
                    if load_remaining >= total_quantity[product] and warehouse.products[product] >= total_quantity[product]:
                        load = total_quantity[product]
                    elif warehouse.products[product] < load_remaining:
                        load = warehouse.products[product]
                    else:
                        load = load_remaining

                    total_quantity[product] -= load
                    load_remaining -= load
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

    return solutions

def optimised_product_by_product(challenge):
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

def workload_repartition(challenge):
    solutions = []

    product_warehouses = {}

    for warehouse in challenge.warehouses:
            for product in range(len(warehouse.products)):
                if warehouse.products[product] > 0:
                    if product in product_warehouses.keys():
                        product_warehouses[product].append(warehouse.id)
                    else :
                        product_warehouses[product] = [warehouse.id]

    for order in challenge.orders:
        nearest_warehouse = sorted(challenge.warehouses, lambda w: Drone.calculate_distance(order.location, w.location))[0]

        # Soit prendre les plus proche
        # Soit les plus chargés
        # Pour chaque order on garde la solution la plus rapide
                        
        # Déterminer le nombre de drones, et l'ordre de quel wharehouse visiter dans quel ordre

        # Trouver des drones qui seront dispo le plus vite possible pour les transferts

        # Si c'est trop long, le drone de l'order ira lui même, sinon il va wait (si c'est juste un peu)

        # Faire qqch de similaire que stack strace

    return solutions

def solve(challenge):
    solvers = {}

    solvers['stack_segments'] = stack_segments(copy.deepcopy(challenge))
    solvers['optimised_product_by_product'] = optimised_product_by_product(copy.deepcopy(challenge))
    solvers['naive'] = naive(copy.deepcopy(challenge))
    solvers['product_by_product'] = product_by_product(copy.deepcopy(challenge))
    solvers['workload_repartition'] = workload_repartition(copy.deepcopy(challenge))

    solutions = {}
    
    for algo, solution in solvers.items():
        solutions[algo] = score_solution(solvers[algo], copy.deepcopy(challenge))
        print(f'Solution \'{algo}\' : {solutions[algo]}')

    best_solution = max(solutions.keys(), key=lambda a:solutions[a])

    print('La meilleure solution est :', best_solution)

    return solvers[best_solution]
