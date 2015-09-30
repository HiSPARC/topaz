"""Distances between combinations of 2 stations

This script collects coordinates of stations, then makes
all possible combinations of 2 different stations, it
calculates the distances of the combinations, and makes
a histogram to show these distances.

"""
from itertools import combinations

import numpy

from sapphire import HiSPARCNetwork, HiSPARCStations

MIN_DISTANCE = 50
MAX_DISTANCE = 2e3


def distance_between_stations(s1, s2):
    cluster = HiSPARCStations([s1, s2])
    xyz = [numpy.array(s.get_coordinates()[-1]) for s in cluster.stations]
    return distance(*xyz)


def close_pairs_in_network(min=MIN_DISTANCE, max=MAX_DISTANCE):
    cluster = HiSPARCNetwork()
    return close_pairs_in_cluster(cluster, min, max)


def close_pairs_in_cluster(cluster, min=MIN_DISTANCE, max=MAX_DISTANCE):
    station_numbers = []
    coordinates = []
    for station in cluster.stations:
        try:
            numpy.testing.assert_allclose(station.get_lla_coordinates(),
                                          (0., 0., 0.), atol=1e-7)
        except AssertionError:
            # Not invalid GPS
            station_numbers.append(station.number)
            coordinates.append(numpy.array(station.get_coordinates()[:-1]))
    return get_close_pairs(zip(station_numbers, coordinates), min, max)


def get_close_pairs(coordinates, min=MIN_DISTANCE, max=MAX_DISTANCE):
    pairs = [(sc1[0], sc2[0]) for sc1, sc2 in combinations(coordinates, 2)
             if min < distance(sc1[1], sc2[1]) < max]
    return pairs


def distance(c1, c2):
    distance = numpy.sqrt(sum((c1 - c2) ** 2))
    return distance


if __name__ == '__main__':
    close_pairs_in_network()
