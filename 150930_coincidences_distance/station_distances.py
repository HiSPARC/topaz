"""Distances between combinations of 2 stations

This script collects coordinates of stations, then makes
all possible combinations of 2 different stations, it
calculates the distances of the combinations, and makes
a histogram to show these distances.

"""
from itertools import combinations

from numpy import array, sqrt, testing

from sapphire import HiSPARCNetwork, HiSPARCStations

MIN_DISTANCE = 0
MAX_DISTANCE = 2e3


def distance_between_stations(s1, s2):
    cluster = HiSPARCStations([s1, s2], force_stale=True)
    xyz = [array(s.calc_center_of_mass_coordinates())
           for s in cluster.stations]
    return distance(*xyz)


def horizontal_distance_between_stations(s1, s2):
    cluster = HiSPARCStations([s1, s2], force_stale=True)
    xy = [array(s.calc_center_of_mass_coordinates()[:-1])
          for s in cluster.stations]
    return distance(*xy)


def close_pairs_in_network(min=MIN_DISTANCE, max=MAX_DISTANCE):
    cluster = HiSPARCNetwork(force_stale=True)
    return close_pairs_in_cluster(cluster, min, max)


def close_pairs_in_cluster(cluster, min=MIN_DISTANCE, max=MAX_DISTANCE):
    station_numbers = []
    coordinates = []
    for station in cluster.stations:
        try:
            testing.assert_allclose(station.get_lla_coordinates(),
                                    (0., 0., 0.), atol=1e-7)
        except AssertionError:
            # Valid GPS
            station_numbers.append(station.number)
            coordinates.append(array(station.calc_center_of_mass_coordinates()))
    return get_close_pairs(zip(station_numbers, coordinates), min, max)


def get_close_pairs(coordinates, min=MIN_DISTANCE, max=MAX_DISTANCE):
    pairs = [(sc1[0], sc2[0]) for sc1, sc2 in combinations(coordinates, 2)
             if min < distance(sc1[1], sc2[1]) < max]
    return pairs


def close_triples_in_network(min=MIN_DISTANCE, max=MAX_DISTANCE):
    """Find triples of stations

    The distances between each of the station pairs in the set must be within
    the min and max value.

    """
    cluster = HiSPARCNetwork(force_stale=True)
    return close_triples_in_cluster(cluster, min, max)


def close_triples_in_cluster(cluster, min=MIN_DISTANCE, max=MAX_DISTANCE):
    station_numbers = []
    coordinates = []
    for station in cluster.stations:
        try:
            testing.assert_allclose(station.get_lla_coordinates(),
                                    (0., 0., 0.), atol=1e-7)
        except AssertionError:
            # Not invalid GPS
            station_numbers.append(station.number)
            coordinates.append(array(station.calc_center_of_mass_coordinates()))
    return get_close_triples(zip(station_numbers, coordinates), min, max)


def get_close_triples(coordinates, min=MIN_DISTANCE, max=MAX_DISTANCE):
    triples = [(sc1[0], sc2[0], sc3[0]) for sc1, sc2, sc3 in combinations(coordinates, 3)
               if all(min < distance(sp1, sp2) < max
                      for sp1, sp2 in combinations((sc1[1], sc2[1], sc3[1]), 2))]
    return triples



def distance(c1, c2):
    distance = sqrt(sum((c1 - c2) ** 2))
    return distance


if __name__ == '__main__':
    close_pairs_in_network()
