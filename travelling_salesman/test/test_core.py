import pytest
import travelling_salesman.core as tsp

def test_parse_args():
    config = tsp.parse_args('input_file.txt output_file.txt 1'.split())
    assert config.input_file == 'input_file.txt'
    assert config.output_file == 'output_file.txt'
    assert config.nodes_to_visit == 1


    config = tsp.parse_args('input_file.txt output_file.txt'.split())
    assert config.input_file == 'input_file.txt'
    assert config.output_file == 'output_file.txt'
    assert config.nodes_to_visit == 10

    with pytest.raises(SystemExit):
        tsp.parse_args('input_file.txt'.split())

    with pytest.raises(SystemExit):
        tsp.parse_args('')

def test_cut_nodes():
    input_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert tsp.cut_nodes(input_matrix, 3) == input_matrix
    assert tsp.cut_nodes(input_matrix, 2) == [[1, 2], [4, 5]]
    assert tsp.cut_nodes(input_matrix, 5) == input_matrix
