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

    # Récupèrer une order à partir de son ID
    orders = {order.id:order for order in challenge.orders}
    
    # Sauvegarde des orders complétées pour empêcher de livrer dans une order complétée
    completed_orders = []

    # Enregistrement des tours où il y a eu une action de livraison
    order_turns = {}

    for drone in challenge.drones:
        # On ne garde que les opérations du drone en question
        moves = list(filter(lambda move: move[0] == drone.id, solution))

        turns = 0

        # Position initiale
        pos = challenge.warehouses[0].location

        for move in moves:
            if move[1] in {'L', 'U'}:
                # Si l'opération est une charge, alors le drone va vers un warehouse
                next_pos = list(filter(lambda w:w.id == move[2], challenge.warehouses))[0].location

                # Distance parcourue pour aller effectuer l'action ajoutées aux tours + 1 tour pour charger / décharger
                turns += Drone.calculate_distance(pos, next_pos) + 1

            elif move[1] == 'D':
                # Si l'opération est un dépôt, alors le drone va vers une order
                next_pos = orders[move[2]].location
                
                # Distance parcourue pour aller effectuer l'action ajoutées aux tours
                turns += Drone.calculate_distance(pos, next_pos)

                # Insérer la livraison dans la liste des actions de livraisons
                if move[2] not in completed_orders:
                    if move[2] not in order_turns.keys():
                        order_turns[move[2]] = [turns]
                    else:
                        order_turns[move[2]].append(turns)

                # Retrait de la liste des commandes des items livrés
                orders[move[2]].products[move[3]] -= move[4]

                # Ajout du tour de la livraison
                turns += 1

                # Si tous les produits ont été livrés (pas forcément dans le bon ordre)
                if move[2] not in completed_orders and orders[move[2]].is_completed():
                    completed_orders.append(move[2])

            elif move[1] == 'W':
                turns += move[2]
                break

            # Mise à jour de la localisation du drone
            pos = next_pos
    
    for order, turns in order_turns.items():
        if orders[order].is_completed():
            score += math.ceil(((challenge.deadline - max(turns)) / challenge.deadline) * 100)
    
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
        segments.append(Segment(Segment.get_location(actions[0], challenge), order.location, challenge, actions, order.id))

    # Trace du parcours de chaque drone
    paths = {drone.id:[] for drone in challenge.drones}
    # Sauvegarde du temps pris pour toutes les commandes d'un drone
    # Sert à ne pas recalculer à chaque itération
    lenght_paths = {drone.id:0 for drone in challenge.drones}
    # On choisi les NB DRONES segments les plus simples à finir
    simplest_segments = sorted(segments, key=lambda s:s.turns, reverse=True)

    for i in range(len(challenge.drones)):
        segment = simplest_segments.pop()
        segments.remove(segment)
        paths[i].append(segment)
        lenght_paths[i] += segment.turns

    # On cherche à attribuer tous les segments à des drones
    while len(segments) > 0:
        # Sélection du drone qui est le moins occupé
        id = min(lenght_paths, key=lenght_paths.get)

        # Choix du segment qui dure le moins longtemps
        segment = min(segments, key=lambda segment:segment.turns)
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

def diviser_tableau(tableau, n):
    taille_tableau = len(tableau)
    taille_sous_tableau = taille_tableau // n
    tableaux_resultats = []

    # Diviser le tableau en n parties
    for i in range(n):
        debut = i * taille_sous_tableau
        fin = (i + 1) * taille_sous_tableau

        # Pour le dernier morceau, inclure les éléments restants
        if i == n - 1:
            fin = taille_tableau

        sous_tableau = tableau[debut:fin]
        tableaux_resultats.append(sous_tableau)

    return tableaux_resultats

def main_warehouse_layers(challenge):
    solutions = []

    NB_ZONES = 3

    # Warehouse le plus au centre
    sorted_orders = sorted(challenge.orders, key=lambda o:Drone.calculate_distance(o.location, (challenge.rows_count / 2, challenge.columns_count / 2)))
    order_zones = diviser_tableau(sorted_orders,NB_ZONES)
    future_order_zones = copy.deepcopy(order_zones)
    
    zones_scores = []

    for i,zone in enumerate(order_zones):
        new_challenge = copy.deepcopy(challenge)
        new_challenge.orders = zone
        score_challenge = copy.deepcopy(new_challenge)
        zones_scores.append((i, score_solution(stack_segments(new_challenge), score_challenge)))
    sorted_zones_scores = sorted(zones_scores, key=lambda x: x[1], reverse=True)
    
    for id, score in sorted_zones_scores:
        challenge.orders = future_order_zones[id]
        local_solutions = workload_repartition(challenge)
        for solution in local_solutions:
            solutions.append(solution)

    return solutions

def workload_repartition(challenge):
    solutions = []

    # Si passer par un warehouse au passage pour aider l'order est RATIO fois plus court, alors le détour en vaut la peine
    LONGER_THAN_ORDER_RATIO = 3
    # Pourcentage du coefficient des orders qui représente la complétion d'une order
    RATIO_ORDER_COMPLETION = 0.76

    # Liste des segments
    segments = []

    # Accéder simplement à une order par son ID
    orders_by_id = {order.id:i for i, order in enumerate(challenge.orders)}

    # Construction de segments pour chaque order
    for order in challenge.orders:
        # Liste des ID des warhouses trié du plus proche au plus éloigné
        warehouses = list(map(lambda w: w.id, sorted(challenge.warehouses, key=lambda w:Drone.calculate_distance(w.location, order.location))))

        warehouse_count = 0

        # Produits à prendre dans chaque warehouse
        workload = {}

        # Produits à trouver
        products_remaining = order.products

        # Tant que tous les produits n'ont pas été trouvés
        while set(products_remaining.values()) != {0}:
            # Passage de warehouse en warehouse
            warehouse = warehouses[warehouse_count]
            
            # Pour chaque produit
            for product, amount in order.products.items():
                # Si la quantité de produit à trouver n'est pas atteinte et que le warehouse en a
                if products_remaining[product] > 0 and challenge.warehouses[warehouse].products[product] > 0:
                    # Calcul de la quantité à charger
                    if challenge.warehouses[warehouse].products[product] >= amount:
                        load = amount
                    else:
                        load = challenge.warehouses[warehouse].products[product]

                    # Renseignement des choses à prendre par warehouse
                    if warehouse not in workload.keys():
                        workload[warehouse] = {product:load}
                    else:
                        workload[warehouse][product] = load

                    # Mise à jour de ce qu'il reste à trouver
                    products_remaining[product] -= load

            # Warehouse suivant
            warehouse_count += 1

        # Tant qu'il reste des choses à attribuer à des drones
        while not all(all(q == 0 for q in w.values()) for w in workload.values()):
            # Liste des actions pour le segment
            actions = []

            # Place restante dans le drone
            remaining_load = challenge.max_payload

            # Pour chaque warehouse
            for warehouse, products in workload.items():
                # Calcul pour voir si le détour vaut le coup
                # Condition pour éviter les problèmes
                if len(actions) > 0:
                    d_warehouse = Drone.calculate_distance(Segment.get_location(actions[-1], challenge), challenge.warehouses[warehouse].location)
                    d_warehouse_to_order = Drone.calculate_distance(order.location, challenge.warehouses[warehouse].location)
                    d_order_from_current = Drone.calculate_distance(Segment.get_location(actions[-1], challenge), order.location)
                    
                # Si le drone est à vide ou
                if (len(actions) == 0 or (
                # Si le drone a déjà des produits, mais que le warehouse n'est pas très loin
                    len(actions) > 0 and d_warehouse + d_warehouse_to_order <= d_order_from_current * LONGER_THAN_ORDER_RATIO
                )):
                    # Pour chaque produit dans le warehouse
                    for product, quantity in products.items():
                        # Si le produit a été vidé du warehouse
                        if quantity == 0:
                            continue

                        # Quantité maximale chargeable du produit
                        can_load = (remaining_load // int(challenge.product_weights[product]))
                        
                        # Si rien ne peut être chargé
                        if can_load == 0:
                            continue

                        # Charge la quantité nécessaire
                        load = min(quantity, can_load)
                        
                        # Ajout du chargement dans la liste des actions du segment
                        # Faux id de drone
                        actions.append([99999, 'L', warehouse, product, load])
                        # Retrait des produits des produits à envoyer vers l'order
                        workload[warehouse][product] -= load
                        # Retrait des produits des warehouses de challenge
                        challenge.warehouses[warehouse].products[product] -= load
                        # Renseignement du nouveau poids
                        remaining_load -= int(challenge.product_weights[product]) * load
            
            # Quand le drone s'est chargé au maximum dans des warehouses pas trop éloignés de sa route entre le
            # premier warehouse et l'order
            
            # Compte de chaque produit à liver en quelle quantité
            product_list = {}

            for action in actions:
                if action[3] not in product_list.keys():
                    product_list[action[3]] = action[4]
                else:
                    product_list[action[3]] += action[4]
            
            # Ajout des actions de livraison
            for product, quantity in product_list.items():
                # Faux id de drone
                actions.append([99999, 'D', order.id, product, quantity])
            
            # Quand l'order est complétée, les actions sont converties en nouveau segment
            segments.append(Segment(Segment.get_location(actions[0], challenge), order.location, challenge, actions, order.id))

    # Trace du parcours de chaque drone
    paths = {drone.id:[] for drone in challenge.drones}
    # Sauvegarde du temps pris pour toutes les commandes d'un drone
    # Sert à ne pas recalculer à chaque itération
    lenght_paths = {drone.id:0 for drone in challenge.drones}
    
    # Nombre de segments par orders
    segments_per_orders = {id:len(list(filter(lambda s:s.order_id == id, segments))) for id in orders_by_id.keys()}
    
    # On choisi les NB DRONES segments les plus simples à finir
    simplest_segments = sorted(segments, key=lambda s:segments_per_orders[s.order_id], reverse=True)

    for i in range(len(challenge.drones)):
        if len(simplest_segments) > 0:
            segment = simplest_segments.pop()
            segments.remove(segment)
            paths[i].append(segment)
            lenght_paths[i] += segment.turns

    # Segment qui prend le plus de temps + plus longue distance possiblement parcourable
    if len(segments) > 0:
        longest_time = sorted(segments, key=lambda s:s.turns)[-1].turns + math.sqrt(challenge.rows_count ** 2 + challenge.columns_count ** 2)

    # On cherche à attribuer tous les segments à des drones
    while len(segments) > 0:
        # Sélection du drone qui est le moins occupé
        id = min(lenght_paths, key=lenght_paths.get)

        # Choix du segment en fonction de plusieurs facteurs
        # Si le segment appartient à une order qui se termine bientôt
        # Si le drone terminera le segment dans un long moment (temps de vol + déroulé du segment)
        # Score de 0 à 100
        next_segment = (-1, 100)

        for count, segment in enumerate(segments):
            order = challenge.orders[orders_by_id[segment.order_id]]
            # Pourcentage de complétion de la commande associée
            order_completion = ((order.initial_amount - sum(order.products)) / order.initial_amount) * 100
            time_spent = segment.turns + Drone.calculate_distance(segment.start, paths[id][-1].end)
            # Temps utilisé rapporté au temps maximal
            time_proportion = (time_spent / longest_time) * 100
            coefficient = RATIO_ORDER_COMPLETION * order_completion + (1 - RATIO_ORDER_COMPLETION) * time_proportion
            
            if coefficient < next_segment[1]:
                next_segment = (count, coefficient)
                
        segment = segments[next_segment[0]]
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

def solve(challenge):
    solvers = {}

    solvers['stack_segments'] = stack_segments(copy.deepcopy(challenge))
    solvers['naive'] = naive(copy.deepcopy(challenge))
    solvers['workload_repartition'] = workload_repartition(copy.deepcopy(challenge))
    solvers['main_warehouse_layers_stack_segments'] = main_warehouse_layers(copy.deepcopy(challenge))

    solutions = {}
    
    for algo, solution in solvers.items():
        solutions[algo] = score_solution(solvers[algo], copy.deepcopy(challenge))
        print(f'Solution \'{algo}\' : {solutions[algo]}')

    best_solution = max(solutions.keys(), key=lambda a:solutions[a])

    print('La meilleure solution est :', best_solution)

    return solvers[best_solution]
