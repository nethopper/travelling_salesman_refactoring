import travelling_salesman.utils as tsp

def test_cut_to_size():
    input_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert tsp.cut_to_size(input_matrix, 3) == input_matrix
    assert tsp.cut_to_size(input_matrix, 2) == [[1, 2], [4, 5]]
    assert tsp.cut_to_size(input_matrix, 5) == input_matrix

def test_create_matrix():
    assert tsp.create_matrix(2, 0) == [[0, 0], [0, 0]]
    assert tsp.create_matrix(3, 15) == [[15, 15, 15],
                                        [15, 15, 15],
                                        [15, 15, 15]]
