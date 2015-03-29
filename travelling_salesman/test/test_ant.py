import pytest
from copy import deepcopy
import travelling_salesman.ant as tsp

@pytest.fixture
def graph():
    return {'distances': [[1, 2, 3],
                          [4, 5, 6],
                          [7, 8, 9]],
            'pheromones': [[10, 20, 30],
                           [40, 50, 60],
                           [70, 80, 90]]}

@pytest.fixture
def config():
    return {'beta': 1.0, 'rho': 0.99, 'q0': 0}

@pytest.fixture
def ant(graph, config):
    return {'path_cost': 0,
            'path': [1],
            'path_matrix': [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            'nodes_to_visit': [0, 2],
            'current_node': 1,
            'graph': graph,
            'params': config}

def test_extend_path(ant):
    orig_graph = deepcopy(ant['graph'])
    results = tsp.extend_path(ant)
    assert results['path_cost'] == 6
    assert results['path'] == [1, 2]
    assert results['path_matrix'] == [[0, 0, 0], [0, 0, 1], [0, 0, 0]]
    assert results['nodes_to_visit'] == [0]
    assert results['current_node'] == 2
    assert results['graph']['distances'] == orig_graph['distances']
    assert results['graph']['pheromones'][0] == orig_graph['pheromones'][0]
    assert results['graph']['pheromones'][2] == orig_graph['pheromones'][2]
    assert results['graph']['pheromones'][1][0] == 40
    assert abs(results['graph']['pheromones'][1][2] -
               (0.01 * 60 + 0.99 * 0.133333333333)) < 0.00000001

def test_state_transition_rule(graph, config):
    nodes_to_visit = [0, 2]
    assert tsp.state_transition_rule(graph, 1, nodes_to_visit, config) == {'nodes_to_visit': [0], 'next': 2}

    nodes_to_visit = [0, 2]
    graph['pheromones'][1][0] = 60
    config['q0'] = 1 - config['q0']
    assert tsp.state_transition_rule(graph, 1, nodes_to_visit, config) == {'nodes_to_visit': [2], 'next': 0}


def test_exploit_best_edge(graph, config):
    nodes_to_visit = [0, 2]
    graph['pheromones'][1][0] = 60
    assert tsp.exploit_best_edge(graph, 1, nodes_to_visit, config['beta']) == 0
    graph['pheromones'][1][0] = 30
    assert tsp.exploit_best_edge(graph, 1, nodes_to_visit, config['beta']) == 2

def test_explore_new_edge(graph, config):
    nodes_to_visit = [0, 2]
    assert tsp.explore_new_edge(graph, 1, nodes_to_visit, config['beta']) == 2
    graph['distances'][1] = [1, 5, 10]
    assert tsp.explore_new_edge(graph, 1, nodes_to_visit, config['beta']) == 0

def test_path_strength(graph, config):
    assert abs(tsp.path_strength(graph, 0, 2, config['beta']) -
               (30 / 3.0)) < 0.00000001
    assert abs(tsp.path_strength(graph, 1, 2, config['beta']) -
               (50 / 5.0)) < 0.00000001

def test_local_updating_rule(graph, config):
    updated_graph = tsp.local_updating_rule(graph, 0, 2, config['rho'])
    assert updated_graph['pheromones'][0][0] == 10
    assert updated_graph['pheromones'][0][1] == 20
    assert abs(updated_graph['pheromones'][0][2] -
               (0.01*30 + 0.99*0.1333333333)) < 0.00000001
