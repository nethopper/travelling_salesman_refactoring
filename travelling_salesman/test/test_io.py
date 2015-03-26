import pytest
import os
import pickle
import csv
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

def prep_csv_input(input_file, input_data):
    input_file.ensure()
    with open(str(input_file), 'wb') as csv_file:
        test_writer = csv.writer(csv_file)
        [test_writer.writerow(row) for row in input_data]

def test_read_csv(tmpdir):
    input1 = [['Node 1', 'Node 2'], [1, 2], [4, 5]]
    input2 = [['Berlin', 'Paris', 'Tokyo'],
              [0, 5, 0], [4, 20, 10], [1, 2, 3]]

    input1_file = tmpdir.join('input1.csv')
    input2_file = tmpdir.join('input2.csv')
    prep_csv_input(input1_file, input1)
    prep_csv_input(input2_file, input2)

    with open(str(input1_file), 'rb') as csv_file:
        assert (tsp.read_csv(csv_file)
                ==
                {'nodes': ['Node 1', 'Node 2'],
                 'costs': [[1, 2], [4, 5]]})

    with open(str(input2_file), 'rb') as csv_file:
        assert (tsp.read_csv(csv_file)
                ==
                {'nodes': ['Berlin', 'Paris', 'Tokyo'],
                 'costs': [[0, 5, 0], [4, 20, 10], [1, 2, 3]]})
