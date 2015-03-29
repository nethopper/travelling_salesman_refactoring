import pytest
from copy import deepcopy
import travelling_salesman.colony as tsp

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
    return {'alpha': 0.1, 'beta': 1.0, 'rho': 0.99, 'q0': 0, 'num_ants': 2}

@pytest.fixture
def colony(graph, config):
    return {'best_path': [1, 2, 0],
            'best_path_cost': 15.0,
            'best_path_matrix': [[0, 0, 0], [0, 0, 1], [1, 0, 0]],
            'best_path_iteration': 1,
            'graph': graph,
            'params': config}

def test_create_workers(graph, config):
    ant1, ant2 = tsp.create_workers(graph, config)

    assert 2 >= ant1['start_node'] >= 0
    assert ant1['ID'] == 0
    assert ant1['graph'] is graph
    assert ant1['params'] == {'beta': 1.0, 'rho': 0.99, 'q0': 0}

    assert 2 >= ant2['start_node'] >= 0
    assert ant2['ID'] == 1
    assert ant2['graph'] is graph
    assert ant2['params'] == {'beta': 1.0, 'rho': 0.99, 'q0': 0}

def test_update_pheromone_between(colony):
    orig_graph = deepcopy(colony['graph'])

    # Between nodes on current best path
    # Should return same graph with evaporate and deposited
    # pheromone between given nodes
    res = tsp.update_pheromone_between(colony, 1, 2)
    assert res['graph']['distances'] == orig_graph['distances']
    assert res['graph']['pheromones'][0] == orig_graph['pheromones'][0]
    assert res['graph']['pheromones'][2] == orig_graph['pheromones'][2]
    assert abs(res['graph']['pheromones'][1][2] - (54 + 0.006666666667)) < 0.0000001

    # Between nodes on current best path
    # Should return same graph with only evaporated
    # pheromone between given nodes
    res = tsp.update_pheromone_between(colony, 1, 0)
    assert res['graph']['distances'] == orig_graph['distances']
    assert res['graph']['pheromones'][0] == orig_graph['pheromones'][0]
    assert res['graph']['pheromones'][2] == orig_graph['pheromones'][2]
    assert abs(res['graph']['pheromones'][1][0] - 36) < 0.0000001
