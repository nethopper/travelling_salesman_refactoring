import pickle
import sys
import traceback
import random
import travelling_salesman.core as tsp

def save_outputs(filename):
    outputs = []
    already_seen = 0
    while already_seen < 1000:
        tsp.main([14, "data/citiesAndDistances.pickled", "data/output_all.pickled"])
        out = pickle.load(open("data/output_all.pickled"))
        if not out in outputs:
            outputs.append(out)
            print out
            already_seen = 0
        else:
            already_seen = already_seen + 1
    pickle.dump(outputs, open(filename, 'w'))
