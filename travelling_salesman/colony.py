import logging
import sys
import random
import graph as g
import ant as a

class Colony:
    def __init__(self, graph, num_ants, num_iterations, params):
        self.graph = graph
        self.num_ants = num_ants
        self.Alpha = params['alpha']
        self.colony = self.reset()
        params['num_ants'] = num_ants
        self.colony.update({'graph': graph, 'params': params})
        self.colony['num_iterations'] = num_iterations
        self.params = params

    def reset(self):
        return {'best_path_cost': sys.maxint,
                'best_path': None,
                'best_path_matrix': None,
                'best_path_iteration': 0}

    def start(self):
        self.reset()
        colony = self.colony
        colony['iteration'] = 0

        while not done(colony):
            colony['ants'] = create_workers(colony['graph'], colony['params'])
            colony = self.perform_iteration(colony)
            # Note that this will help refine the results future iterations.
            colony = global_updating_rule(colony)
        return colony

    def perform_iteration(self, colony):
        self.avg_path_cost = 0
        self.ant_counter = 0
        colony['iteration'] += 1
        for ant in colony['ants']:
            colony = self.update(colony, a.run(ant), colony['iteration'])
        return colony


    def num_ants(self):
        return len(self.ants)

    def num_iterations(self):
        return self.num_iterations

    def iteration_counter(self):
        return self.iteration

    def update(self, colony, ant, iteration):
        logging.debug("Update called by %s", ant['ID'])
        self.ant_counter += 1
        self.avg_path_cost += ant['path_cost']
        if ant['path_cost'] < colony['best_path_cost']:
                best_path = best_path_data(ant, iteration)
                colony.update(best_path)
        if self.ant_counter == len(colony['ants']):
            self.avg_path_cost /= len(colony['ants'])
            logging.debug("Best: %s, %s, %s, %s",
                          colony['best_path'], colony['best_path_cost'], colony['iteration'], self.avg_path_cost)
        return colony

def best_path_data(ant, iteration):
    return {'best_path_cost': ant['path_cost'],
            'best_path_matrix': ant['path_matrix'],
            'best_path': ant['path'],
            'best_path_iteration': iteration}

def done(colony):
    return colony['iteration'] >= colony['num_iterations']

def create_workers(graph, params):
    ants = []
    ant_params =  dict((param, params[param]) for param in a.required_params)
    for i in range(params['num_ants']):
        ant = a.create_ant(i, random.randint(0, g.size(graph) - 1),
                           graph, ant_params)
        ants.append(ant)
    return ants

def global_updating_rule(colony):
    node_list = range(g.size(colony['graph']))
    for start in node_list:
        for end in node_list:
            if start != end:
                colony = update_pheromone_between(colony, start, end)
    return colony

def update_pheromone_between(colony, start, end):
    """Update amount of pheromone between start and end by calculating evaporation and deposition. A constant (Alpha) percentage evaporates. Deposition is inversely proportional to total path length, but 0 if this is not one the best paths found."""
    delt_pheromone = colony['best_path_matrix'][start][end] / colony['best_path_cost']
    evaporation = (1 - colony['params']['alpha']) * colony['graph']['pheromones'][start][end]
    deposition = colony['params']['alpha'] * delt_pheromone
    colony['graph']['pheromones'][start][end] = evaporation + deposition
    return colony
