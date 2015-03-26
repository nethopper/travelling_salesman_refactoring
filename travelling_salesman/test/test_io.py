import pytest
import os
import pickle
import travelling_salesman.io as tsp

def test_parse_args():
    config = tsp.parse_args('input_file.txt'.split())
    assert config['input_file'] == 'input_file.txt'
    assert config['output'] == 'stdout'
    assert config['nodes'] == 10
    assert config['input_format'] is None

    config = tsp.parse_args('--nodes 1 input_file.txt'.split())
    assert config['input_file'] == 'input_file.txt'
    assert config['nodes'] == 1

    config = tsp.parse_args('--output output_file.txt input_file.txt'.split())
    assert config['input_file'] == 'input_file.txt'
    assert config['output'] == 'output_file.txt'

    config = tsp.parse_args('--input-format csv input_file.txt'.split())
    assert config['input_format'] == 'csv'

    with pytest.raises(SystemExit):
        tsp.parse_args('--input-format txt input_file.txt'.split())

    with pytest.raises(SystemExit):
        tsp.parse_args('')

def test_determine_input_reader():
    assert tsp.determine_input_reader({'input_file': 'input.pickled'}) == tsp.read_pickled

def test_read_pickled(tmpdir):
    input_data = (['Node 1', 'Node 2'],
                  [[1, 2], [4, 5]])

    input_file = tmpdir.join("input.pickled")
    input_file.ensure()
    pickle.dump(input_data, open(str(input_file), 'w'))

    assert (tsp.read_pickled(open(str(input_file)))
            ==
            {'nodes': input_data[0], 'costs': input_data[1]})
