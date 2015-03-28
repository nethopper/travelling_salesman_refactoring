import pytest
import pyrsistent as pst
from pyrsistent import m, v
import travelling_salesman.graph as tsp

@pytest.fixture
def distance_matrix3():
    return [[1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]]

@pytest.fixture
def pheromone_matrix3():
    return [[10, 20, 30],
            [40, 50, 60],
            [70, 80, 90]]

@pytest.fixture
def distance_matrix4():
    return [[1,  2,  3,  4],
            [5,  6,  7,  8],
            [9,  10, 11, 12],
            [13, 14, 15, 16]]

@pytest.fixture
def sample_graph():
    return m(distances = v(v(1, 2, 3),
                          v(4, 5, 6),
                          v(7, 8, 9)),
             pheromones = v(v(10, 20, 30),
                            v(40, 50, 60),
                            v(70, 80, 90)))

def test_to_persistent():
    assert tsp.to_persistent([]) == v()
    assert tsp.to_persistent([[1]]) == v(v(1))
    assert tsp.to_persistent([[1, 2], [3, 4]]) == v(v(1, 2), v(3, 4))
    assert (tsp.to_persistent([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
            ==
            v(v(1, 2, 3), v(4, 5, 6), v(7, 8, 9), v(10, 11, 12)))

def test_empty_matrix():
    assert tsp.empty_matrix(2) == v(v(0, 0), v(0, 0))
    assert tsp.empty_matrix(3) == v(v(0, 0, 0), v(0, 0, 0), v(0, 0, 0))

def test_create_graph_distance3(distance_matrix3):
    # Given a 3x3 distance matrix
    # When I create a graph
    # Then I get a map containing a distance matrix and a zero pheromone matrix
    assert (tsp.create_graph(distance_matrix3)
            ==
            m(distances = tsp.to_persistent(distance_matrix3),
              pheromones = tsp.empty_matrix(3)))

def test_create_graph_distance4(distance_matrix4):
    # Given a 4x4 distance matrix
    # When I create a graph
    # Then I get a map containing a distance matrix and a zero pheromone matrix
    assert (tsp.create_graph(distance_matrix4)
            ==
            m(distances = tsp.to_persistent(distance_matrix4),
              pheromones = tsp.empty_matrix(4)))

def test_create_graph_both(distance_matrix3, pheromone_matrix3):
    # Given a 4x4 distance matrix
    # When I create a graph
    # Then I get a map containing the distance matrix and the pheromone matrix
    assert (tsp.create_graph(distance_matrix3, pheromone_matrix3)
            ==
            m(distances = tsp.to_persistent(distance_matrix3),
              pheromones = tsp.to_persistent(pheromone_matrix3)))

def test_create_graph_invalid_size():
    # Given a non-square distance matrix
    # When I create a graph
    # Then an exception is raised
    distances = [[1, 2, 3], [4, 5, 6]]
    with pytest.raises(ValueError):
        tsp.create_graph(distances)

    # Given a 3x3 distance matrix and 2x2 pheromone matrix
    # When I create a graph
    # Then an exception is raised
    distances = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    pheromones = [[1, 2], [3, 4]]
    with pytest.raises(ValueError):
        tsp.create_graph(distances, pheromones)

def test_average(distance_matrix3, pheromone_matrix3):
    assert tsp.average(distance_matrix3) == 5.0
    assert tsp.average(pheromone_matrix3) == 50.0

def test_base_pheromone(sample_graph):
    assert abs(tsp.base_pheromone(sample_graph) - (1.0 / (3 * 0.5 * 5))) < 0.00001
    new_graph = sample_graph.set_in(('distances', 0, 0), 10)
    assert abs(tsp.base_pheromone(new_graph) - (1.0 / (3 * 0.5 * 6))) < 0.00001

