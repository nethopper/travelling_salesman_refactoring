import logging
import sys
import random
import graph as g
import ant as a

def create_colony(graph, params):
    """Returns a new colony with the given graph and parameters."""
    return {'graph': graph, 'params': params, 'best_path': empty_path()}

def empty_path():
    """Return a best_path structure for an initial empty path, signifying that none has been found yet."""
    return {'cost': sys.maxint,
            'path': None,
            'matrix': None}

def reset(colony):
    """Bring colony back to initial state. Returns the colony, but modified."""
    colony.pop('ants', None)
    colony.pop('avg_path_cost', None)
    colony['best_path'] = empty_path()
    colony['iteration'] = 0
    return colony

def run(colony):
    """Perform the requested number of iterations over all ants. Returns the colony, with the best path information."""
    while not done(colony):
        colony['ants'] = create_workers(colony['graph'], colony['params'])
        colony = perform_iteration(colony)
        # Note that this will help refine the results future iterations.
        colony = global_updating_rule(colony)
    return colony

def perform_iteration(colony):
    """Perform an interation of the algorithm over all ants. Each ant moves, leaves pheromone, and finds a path. The best is saved if it is better than what we currently have."""
    colony['iteration'] += 1
    for ant in colony['ants']:
        colony = update(colony, a.run(ant))
    colony['avg_path_cost'] = sum(ant['path_cost'] for ant in colony['ants']) / len(colony['ants'])
    logging.debug("Best path found: %s", colony['best_path'])
    logging.debug("Average path cost: %s", colony['avg_path_cost'])
    return colony

def update(colony, ant):
    """Update the best path with the ant's path if necessary. Returns the same colony, possibly with a new best_path."""
    logging.debug("Update called by %s", ant['ID'])
    if ant['path_cost'] < colony['best_path']['cost']:
            best_path = best_path_data(ant)
            colony['best_path'] = best_path
            colony['best_path'].update({'iteration': colony['iteration']})
    return colony

def best_path_data(ant):
    """Convert ant path data to colony best path structure."""
    return {'cost': ant['path_cost'],
            'matrix': ant['path_matrix'],
            'path': ant['path']}

def done(colony):
    """True if the number of iterations specified in parameters has been reached or surpassed, false otherwise."""
    return colony['iteration'] >= colony['params']['iterations']

def create_workers(graph, params):
    """Create the number of ants required by params['num_ants']. Return the list of ants."""
    ants = []
    ant_params =  dict((param, params[param]) for param in a.required_params)
    for i in range(params['num_ants']):
        ant = a.create_ant(i, random.randint(0, g.size(graph) - 1),
                           graph, ant_params)
        ants.append(ant)
    return ants

def global_updating_rule(colony):
    """Update pheromone between all nodes according to the global updating rule, with evaporation and deposition of pheromone. Returns the same colony, with new pheromone values."""
    node_list = range(g.size(colony['graph']))
    for start in node_list:
        for end in node_list:
            if start != end:
                colony = update_pheromone_between(colony, start, end)
    return colony

def update_pheromone_between(colony, start, end):
    """Update amount of pheromone between start and end by calculating evaporation and deposition. A constant (Alpha) percentage evaporates. Deposition is inversely proportional to total path length, but 0 if this is not one the best paths found."""
    delt_pheromone = colony['best_path']['matrix'][start][end] / colony['best_path']['cost']
    evaporation = (1 - colony['params']['alpha']) * colony['graph']['pheromones'][start][end]
    deposition = colony['params']['alpha'] * delt_pheromone
    colony['graph']['pheromones'][start][end] = evaporation + deposition
    return colony
