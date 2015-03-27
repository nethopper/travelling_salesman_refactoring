import pytest
import travelling_salesman.core as tsp
import os
import pickle
import random

@pytest.fixture
def input_data():
    return (['Bergen', 'Hammerfest', 'Kirkenes', 'Kristiansand', 'Lillehammer', 'Oslo', 'Stavanger', 'Troms\xf8', 'Trondheim', '\xc5lesund', 'Vinje', 'Fl\xe5m', 'Sogndal', 'Vang'], [[0, 2196, 2258, 439, 440, 496, 207, 1808, 662, 432, 274, 167, 219, 278], [2170, 0, 480, 2191, 1813, 1870, 2404, 377, 1537, 1834, 2100, 2034, 1951, 1918], [2232, 480, 0, 2222, 1844, 1901, 2435, 806, 1598, 1895, 2131, 2095, 2012, 1980], [439, 2193, 2224, 0, 503, 321, 231, 1962, 816, 820, 266, 487, 584, 521], [440, 1827, 1848, 505, 0, 184, 546, 1484, 338, 381, 363, 277, 279, 162], [496, 1872, 1903, 321, 181, 0, 535, 1640, 495, 562, 230, 333, 333, 236], [207, 2407, 2437, 231, 546, 534, 0, 1975, 830, 638, 250, 343, 395, 454], [1782, 378, 806, 1962, 1484, 1641, 1962, 0, 1148, 1445, 1820, 1645, 1562, 1530], [636, 1537, 1599, 817, 339, 496, 816, 1148, 0, 300, 674, 500, 417, 384], [432, 1834, 1896, 820, 381, 563, 638, 1445, 300, 0, 601, 347, 275, 355], [275, 2103, 2134, 244, 363, 230, 279, 1821, 675, 601, 0, 275, 327, 348], [167, 2033, 2095, 517, 277, 333, 348, 1645, 499, 347, 275, 0, 72, 115], [219, 1951, 2012, 585, 279, 334, 400, 1562, 417, 275, 327, 72, 0, 117], [278, 1918, 1980, 521, 162, 237, 459, 1529, 384, 355, 347, 115, 117, 0]])

@pytest.fixture
def output_expected_single():
    return [[2, 1, 7, 8, 9, 13, 12, 11, 0, 6, 3, 10, 5, 4], ['Kirkenes', 'Hammerfest', 'Troms\xf8', 'Trondheim', '\xc5lesund', 'Vang', 'Sogndal', 'Fl\xe5m', 'Bergen', 'Stavanger', 'Kristiansand', 'Vinje', 'Oslo', 'Lillehammer'], 5979]

@pytest.mark.slowtest
def test_end_to_end_single(tmpdir, input_data, output_expected_single):
    cities_to_visit = 14

    input_file = tmpdir.join("input.pickled")
    input_file.ensure()

    output_file = tmpdir.join("output.pickled")
    pickle.dump(input_data, open(str(input_file), 'w'))

    random.seed(1)
    tsp.main({'nodes': cities_to_visit,
              'output': str(output_file),
              'input_file': str(input_file)})
    assert pickle.load(open(str(output_file))) == output_expected_single

@pytest.mark.slowtest
def test_end_to_end_all(tmpdir, input_data):
    cities_to_visit = 14

    input_file = tmpdir.join("input.pickled")
    input_file.ensure()

    output_file = tmpdir.join("output.pickled")
    pickle.dump(input_data, open(str(input_file), 'w'))
    output_expected = pickle.load(open("data/outputs14-all-1000.pickled"))

    tsp.main({'nodes': cities_to_visit,
              'output': str(output_file),
              'input_file': str(input_file)})
    assert pickle.load(open(str(output_file))) in output_expected
