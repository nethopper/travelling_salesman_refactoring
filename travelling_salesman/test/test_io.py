import pytest
import os
import pickle
import csv
import travelling_salesman.io as tsp

def default_parse_arg_values(config, excluded=None):
    defaults = {'input_file': None,
                'output': None,
                'nodes': 10,
                'input_format': None}
    if excluded is not None:
        defaults.pop(excluded, None)
    for key, expected in defaults.iteritems():
        assert config[key] == expected


def test_parse_args():

    # When no arguments are specified
    # Then use all default values
    config = tsp.parse_args(''.split())
    default_parse_arg_values(config, None)

    # When only input file specified
    # Then use the specified input file
    # And use default values for the rest
    config = tsp.parse_args('input_file.txt'.split())
    assert config['input_file'] == 'input_file.txt'
    default_parse_arg_values(config, 'input_file')

    # When number of nodes is specified
    # Then use the specified number of nodes
    # And use default values for the rest
    config = tsp.parse_args('--nodes 1'.split())
    assert config['nodes'] == 1
    default_parse_arg_values(config, 'nodes')

    # When output file is specified
    # Then use the specified output file
    # And use default values for the rest
    config = tsp.parse_args('--output output_file.txt'.split())
    assert config['output'] == 'output_file.txt'
    default_parse_arg_values(config, 'output')

    # When input format is specified
    # Then use the specified input format
    # And use default values for the rest
    config = tsp.parse_args('--input-format csv'.split())
    assert config['input_format'] == 'csv'
    default_parse_arg_values(config, 'input_format')

    # When all arguments are specified
    # Then use all specified values
    args = '--input-format csv --nodes 5 --output outfile.txt input_file.txt'
    config = tsp.parse_args(args.split())
    assert config['input_format'] == 'csv'
    assert config['nodes'] == 5
    assert config['output'] == 'outfile.txt'
    assert config['input_file'] == 'input_file.txt'

    # When input format is not supported
    # Then exit and output help
    with pytest.raises(SystemExit):
        tsp.parse_args('--input-format txt input_file.txt'.split())

def test_determine_input_reader():
    # When no input format is specified
    # And input file name is specified
    # Then choose by extension
    assert tsp.determine_input_reader({'input_file': 'input.pickled'}) == tsp.read_pickled

    # When input format is None
    # And input file name is specified
    # Then choose by extension
    assert (tsp.determine_input_reader({'input_format': None,
                                       'input_file': 'input.pickled'})
            ==
            tsp.read_pickled)

    # When input format is specified
    # And no input file name is specified
    # Then choose using the format
    assert tsp.determine_input_reader({'input_format': 'csv'}) == tsp.read_csv

    # When input format is specified
    # And input file name is specified
    # Then choose only by input format
    assert (tsp.determine_input_reader({'input_format': 'pickled',
                                       'input_file': 'input.csv'})
            ==
            tsp.read_pickled)


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

@pytest.fixture
def some_results():
    return {'names': ['Node 1', 'Node 2', 'Node 3'],
            'path': [0, 2, 1],
            'cost': 115}

@pytest.fixture
def output_filepath(tmpdir):
    output_filepath = tmpdir.join('output_file.pickled')
    output_filepath.ensure()
    return output_filepath

def test_output_pickled(some_results, output_filepath):
    # Given some results
    # And output file
    # When I output pickled
    # Then the contents of the file are correct
    with open(str(output_filepath), 'wb') as output_file:
        tsp.write_pickled(some_results, output_file)

    with open(str(output_filepath), 'rb') as output_file:
        received = pickle.load(output_file)

    assert received[0] == some_results['path']
    assert received[1] == some_results['names']
    assert received[2] == some_results['cost']

def test_write_csv(some_results, output_filepath):
    # Given some results
    # And output file
    # When I output csv
    # Then the contents of the file are correct
    with open(str(output_filepath), 'wb') as output_file:
        tsp.write_csv(some_results, output_filepath)

    with open(str(output_filepath), 'rb') as output_file:
        reader = csv.reader(output_file)
        contents = reader.next()

    assert contents[0] == '115'
    assert contents[1] == '0;2;1'

def test_determine_output_writer():
    # When no output format is specified
    # And output file name is specified
    # Then choose by extension
    assert tsp.determine_output_writer({'output': 'output.pickled'}) == tsp.write_pickled

    # When output format is None
    # And output file name is specified
    # Then choose by extension
    assert (tsp.determine_output_writer({'output_format': None,
                                       'output': 'output.pickled'})
            ==
            tsp.write_pickled)

    # When output format is specified
    # And no output file name is specified
    # Then choose using the format
    assert tsp.determine_output_writer({'output_format': 'csv'}) == tsp.write_csv

    # When output format is specified
    # And output file name is specified
    # Then choose only by output format
    assert (tsp.determine_output_writer({'output_format': 'pickled',
                                       'output': 'output.csv'})
            ==
            tsp.write_pickled)
