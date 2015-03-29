import argparse
import fileinput
import os
import sys
import pickle
import csv

def parse_args(args=None):
    """Parse input arguments, returning a map of their values. This function should take into account any default values or overrides."""
    parser = argparse.ArgumentParser(description='Solve a Travelling Salesman Problem using an Ant Colont Optimization algorithm.')

    # Algorithm parameter configuration
    parser.add_argument('-t', '--iterations', metavar='N', type=int,
                        default=20, help='The number of iterations in a single run')
    parser.add_argument('-r', '--repetitions', metavar='N', type=int,
                        default=1, help='The number of full runs')
    parser.add_argument('-n', '--nodes', metavar='N', type=int,
                        default=10, help='The number of nodes to visit')
    parser.add_argument('--num-ants', metavar='N', type=int,
                        default=20, help='The number of ants to use')
    parser.add_argument('--alpha', metavar='N', type=float, default=0.1,
                        help='Deposition impact on amount of pheromone on edge (0.0 - 1.0')
    parser.add_argument('--beta', metavar='N', type=float,
                        default=1.0, help='Adjusts the impact of distance on edge strength')
    parser.add_argument('--q0', metavar='N', type=float, default=0.5,
                        help='Likelihood of choosing exploration over exploitation (0.0 - 1.0)')
    parser.add_argument('--rho', metavar='N', type=float,
                        default=0.99, help='Impact of initial pheromone values on local updating rule')

    # Logging arguments
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print more information to the screen')
    parser.add_argument('-vv', '--very-verbose', action='store_true',
                        help='Print even more information to the screen')

    # Input and Output arguments
    parser.add_argument('-i', '--input-format', metavar='format', type=str, nargs='?',
                        choices=AVAILABLE_INPUT_READERS.keys(), help='Format of the input data')
    parser.add_argument('-o', '--output', metavar='file', type=str, nargs='?',
                        help='Path to the output file')
    parser.add_argument('input_file', metavar='input_file', type=str,
                        nargs='?', help='Path to the input file')
    if args is None:
        parsed_args = parser.parse_args()
    else:
        parsed_args = parser.parse_args(args)
    return vars(parsed_args)

def write_pickled(results, output_file):
    results = [results['path'], results['names'], results['cost']]
    pickle.dump(results, output_file)

def write_csv(results, output_file):
    writer = csv.writer(output_file)
    str_path = map(str, results['path'])
    rows = [[str(results['cost']), ';'.join(str_path)]]
    writer.writerows(rows)

def determine_output_writer(config):
    writer = None
    if config.get('output_format', None) is not None:
        writer = AVAILABLE_OUTPUT_WRITERS.get(config['output_format'], None)
    else:
        file_extension = os.path.splitext(config['output'])[1].lower()[1:]
        writer = AVAILABLE_OUTPUT_WRITERS.get(file_extension, None)
    return writer

def write_output(results, config):
    if config['output'] is None:
        output_file = sys.stdout
    else:
        output_file = open(config['output'], 'wb+')
    output_writer = determine_output_writer(config)
    if output_writer is None:
        raise ValueError("The output format could not be recognized. Ensure that a supported type is specified either through the output file extension or command-line flag.")
    output_writer(results, output_file)
    output_file.close()

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

def determine_input_reader(config):
    reader = None
    if config.get('input_format', None) is not None:
        reader = AVAILABLE_INPUT_READERS.get(config['input_format'], None)
    else:
        file_extension = os.path.splitext(config['input_file'])[1].lower()[1:]
        reader = AVAILABLE_INPUT_READERS.get(file_extension, None)
    return reader

def read_input(config):
    if config['input_file'] is None:
        input_file = sys.stdin
    else:
        input_file = open(config['input_file'], 'rb')
    input_reader = determine_input_reader(config)
    if input_reader is None:
        raise ValueError("The input format could not be recognized. Ensure that a supported type is specified either through the input file extension or command-line flag.")
    else:
        data = input_reader(input_file)
        input_file.close()
        return data

AVAILABLE_INPUT_READERS = {'pickled': read_pickled,
                           'csv': read_csv}
AVAILABLE_OUTPUT_WRITERS = {'pickled': write_pickled,
                            'csv': write_csv}
