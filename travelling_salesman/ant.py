import math
import random
import logging
import graph as g
from copy import deepcopy

required_params = ['beta', 'rho', 'q0']

def create_ant(ID, start_node, graph, params):
    ant = {'ID': ID,
           'start_node': start_node,
           'path': [start_node],
           'path_cost': 0,
           'path_matrix': [],
           'nodes_to_visit': [],
           'current_node': start_node,
           'graph': graph,
           'params': params}
    ant = reset_nodes_to_visit(ant)
    ant = reset_path_matrix(ant)
    return ant

def reset_nodes_to_visit(ant):
    # map of city_id -> city_id, without start city
    # during transitions, the node that an ant moves to
    # is removed
    ant['nodes_to_visit'] = [n for n in range(g.size(ant['graph'])) if n != ant['start_node']]
    return ant


def reset_path_matrix(ant):
    num_nodes = g.size(ant['graph'])
    ant['path_matrix'] = [[0 for x in range(num_nodes)] for y in range(num_nodes)]
    return ant


def run(ant):
    """Move to new city found through state_transition_rule and remember the distance. The new city is added to the path vector. The route is marked on the path matrix."""
    while not end(ant['nodes_to_visit']):
        ant = extend_path(ant)
    ant['path_cost'] += cost_of_return(ant)
    ant['path_matrix'] = deepcopy(ant['path_matrix'])
    ant['path'] = deepcopy(ant['path'])
    return dict((key, ant[key]) for key in ['ID', 'path_cost', 'path_matrix', 'path'])


def cost_of_return(ant):
    return ant['graph']['distances'][ant['path'][-1]][ant['path'][0]]

def extend_path(ant):
    transition = state_transition_rule(ant['graph'], ant['current_node'], ant['nodes_to_visit'], ant['params'])
    ant['nodes_to_visit'] = transition['nodes_to_visit']
    new_node = transition['next']
    ant['path_cost'] += ant['graph']['distances'][ant['current_node']][new_node]
    ant['path'].append(new_node)
    ant['path_matrix'][ant['current_node']][new_node] = 1
    local_updating_rule(ant['graph'], ant['current_node'], new_node, ant['params']['rho'])
    ant['current_node'] = new_node
    return ant

def end(nodes_to_visit):
    return not nodes_to_visit

def state_transition_rule(graph, current_node, nodes_to_visit, params):
    """Returns a city to move to by using either exploitation (choosing edge with highest strength), or exploration (choosing any good edge)"""
    max_node = None
    if should_use_exploitation(params['q0']):
        print 'exploitation!'
        max_node = exploit_best_edge(graph, current_node, nodes_to_visit, params['beta'])
    else:
        print 'exploration!'
        max_node = explore_new_edge(graph, current_node, nodes_to_visit, params['beta'])
    if max_node is None:
        raise Exception("max_node not found")
    nodes_to_visit.remove(max_node)
    return {'next': max_node, 'nodes_to_visit': nodes_to_visit}

def should_use_exploitation(q0):
    return random.random() < q0

def exploit_best_edge(graph, current_node, nodes_to_visit, beta):
    """We will move to city with highest: pheromone*(1/distance)"""
    logging.debug("Exploitation")
    strength_to = lambda node : path_strength(graph, current_node, node, beta)
    return max(nodes_to_visit, key=strength_to)

def explore_new_edge(graph, current_node, nodes_to_visit, beta):
    """Paper describes moving from current city c to a random city s with the probability distribution p(s) = cost(c, s)/ sum of cost(c, r) over visited cities r. Here we find the average cost of travelling from c to all other not yet visited cities and choose the last node that has a cost higher than the average. If none meet this criterion, we choose the very last node"""
    logging.debug("Exploration")
    max_node = nodes_to_visit[-1]

    avg_strength = sum(path_strength(graph, current_node, node, beta) for node in nodes_to_visit) / len(nodes_to_visit)

    logging.debug("avg = %s", avg_strength)

    is_eligible = lambda n: path_strength(graph, current_node, n, beta) > avg_strength
    eligible_nodes = filter(is_eligible, nodes_to_visit)

    if eligible_nodes:
        return eligible_nodes[-1]
    else:
        return nodes_to_visit[-1]

def path_strength(graph, start, end, beta):
    """Calculate the strength of the path from start to end. This is determined by the amount of pheromone and distance. Parameter beta changes how important the distance is (lower beta = less important)."""
    return graph['pheromones'][start][end] * math.pow(g.inverse_distance(graph, start, end), beta)

def local_updating_rule(graph, current_node, next_node, rho):
    """Update the pheromones on the pheromone matrix to represent transitions of the ants"""
    new_strength = (1 - rho) * graph['pheromones'][current_node][next_node] + (rho * g.base_pheromone(graph))
    graph['pheromones'][current_node][next_node] = new_strength
    return graph
