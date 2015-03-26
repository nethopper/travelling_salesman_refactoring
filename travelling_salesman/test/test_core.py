import travelling_salesman.core as tsp

def test_cut_nodes():
    input_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert tsp.cut_nodes(input_matrix, 3) == input_matrix
    assert tsp.cut_nodes(input_matrix, 2) == [[1, 2], [4, 5]]
    assert tsp.cut_nodes(input_matrix, 5) == input_matrix
