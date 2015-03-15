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

# stuff = pickle.load(open("data/citiesAndDistances.pickled"))
# stuff

# pickle.load(open("data/output.pickled"))
# distances = stuff[1]
# len(distances)
# number_of_cities = 5
# distances = distances[0:number_of_cities]
# distances
# for i in range(0, number_of_cities):
#     distances[i] = distances[i][0:number_of_cities]

# tau_mat = []
# for i in range(0, number_of_cities):
#     tau_mat.append([0] * number_of_cities)

# tau_mat

# average_distance = float(sum([sum(city_distances) for city_distances in distances])) / (number_of_cities * number_of_cities)

# average_distance

# 1 / (0.5 * number_of_cities * average_distance)

# random.random()

# dist = -1
# for dist in distances:
#     x = 2 + 2

# dist
