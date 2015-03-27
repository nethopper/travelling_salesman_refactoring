import argparse
import fileinput
import os
import sys
import pickle
import csv

def parse_args(args=None):
    """Parse input arguments, returning a map of their values. This function should take into account any default values or overrides."""
    parser = argparse.ArgumentParser(description='Solve a Travelling Salesman Problem using an Ant Colont Optimization algorithm.')
    parser.add_argument('-i', '--input-format', metavar='format', type=str, nargs='?',
                        choices=AVAILABLE_INPUT_READERS.keys(), help='Format of the input data')
    parser.add_argument('-o', '--output', metavar='file', type=str, nargs='?',
                        help='Path to the output file')
    parser.add_argument('-n', '--nodes', metavar='N', type=int, nargs='?',
                        const=10, default=10, help='The number of nodes to visit')
    parser.add_argument('input_file', metavar='input_file', type=str,
                        nargs='?', help='Path to the input file')
    if args is None:
        parsed_args = parser.parse_args()
    else:
        parsed_args = parser.parse_args(args)
    return vars(parsed_args)

def output_results(path, filename):
    if filename is None:
        output_file = sys.stdout
    else:
        output_file = open(filename, 'w+')
    results = [path['path'], path['names'], path['cost']]
    pickle.dump(results, output_file)

def read_pickled(input_file):
    [nodes, costs] = pickle.load(input_file)
    return {'nodes': nodes, 'costs': costs}

def read_csv(input_file):
    reader = csv.reader(input_file)
    data = {'nodes': reader.next(),
            'costs': []}
    for row in reader:
        data['costs'].append([float(cost) for cost in row])
    return data

def input_reader(input_format):
    return AVAILABLE_INPUT_READERS.get(input_format, None)

def determine_input_reader(config):
    reader = None
    if config.get('input_format', None) is not None:
        reader = input_reader(config['input_format'])
    else:
        file_extension = os.path.splitext(config['input_file'])[1].lower()[1:]
        reader = input_reader(file_extension)
    return reader

def read_input(config):
    if config['input_file'] is None:
        input_file = sys.stdin
    else:
        input_file = open(config['input_file'], 'r')
    input_reader = determine_input_reader(config)
    if input_reader is None:
        raise ValueError("The input format could not be recognized. Ensure that a supported type is specified either through the input file extension or command-line flag.")
    else:
        data = input_reader(input_file)
        input_file.close()
        return data

AVAILABLE_INPUT_READERS = {'pickled': read_pickled,
                           'csv': read_csv}
