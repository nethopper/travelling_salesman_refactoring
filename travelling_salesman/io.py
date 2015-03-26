import argparse
import os
import pickle

def parse_args(args):
    """Parse input arguments, returning a map of their values. This function should take into account any default values or overrides."""
    parser = argparse.ArgumentParser(description='Solve a Travelling Salesman Problem using an Ant Colont Optimization algorithm.')
    parser.add_argument('-i', '--input-format', metavar='format', type=str, nargs='?',
                        choices=['csv'], help='Format of the input data')
    parser.add_argument('-o', '--output', metavar='file', type=str, nargs='?',
                        const='stdout', default='stdout', help='Path to the output file')
    parser.add_argument('-n', '--nodes', metavar='N', type=int, nargs='?',
                        const=10, default=10, help='The number of nodes to visit')
    parser.add_argument('input_file', metavar='input_file', type=str,
                        help='Path to the input file')
    return vars(parser.parse_args(args))

def output_results(path, filename):
    results = [path['path'], path['names'], path['cost']]
    pickle.dump(results, open(filename, 'w+'))

def read_pickled(input_file):
    [nodes, costs] = pickle.load(input_file)
    return {'nodes': nodes, 'costs': costs}

def input_reader(input_format):
    return AVAILABLE_INPUT_READERS.get(input_format, None)

def determine_input_reader(config):
    reader = None
    if 'input_format' in config:
        reader = input_reader(config['input_format'])
    else:
        file_extension = os.path.splitext(config['input_file'])[1].lower()[1:]
        reader = input_reader(file_extension)
    return reader

def read_input(config):
    input_file = open(config['input_file'], "r")
    input_reader = determine_input_reader(config)
    if input_reader is None:
        raise ValueError("The input format could not be recognized. Ensure that a supported type is specified either through the input file extension or command-line flag.")
    else:
        return input_reader(input_file)

AVAILABLE_INPUT_READERS = {'pickled': read_pickled}
