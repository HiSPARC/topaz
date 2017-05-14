"""Distances between combinations of 2 stations

This script collects coordinates of stations, then makes
all possible combinations of 2 different stations, it
calculates the distances of the combinations, and makes
a histogram to show these distances.

"""
from itertools import combinations

import numpy

from artist import Plot

from sapphire import HiSPARCNetwork, HiSPARCStations, Network, ScienceParkCluster
from sapphire.utils import c


def distances_sciencepark():
    cluster = ScienceParkCluster(force_stale=True)
    distances_stations(cluster, name='_sciencepark')


def distances_netherlands():
    sn = Network(force_stale=True).station_numbers(country=0)
    cluster = HiSPARCStations(sn, force_stale=True, skip_missing=True)
    distances_stations(cluster, name='_netherlands')


def distances_all_stations():
    cluster = HiSPARCNetwork(force_stale=True)
    distances_stations(cluster, name='_all')


def distances_stations(cluster, name=''):
    coordinates = []
    for station in cluster.stations:
        try:
            numpy.testing.assert_allclose(station.get_lla_coordinates(),
                                          (0., 0., 0.), atol=1e-7)
        except AssertionError:
            # Not invalid GPS
            coordinates.append(
                numpy.array(station.calc_center_of_mass_coordinates()))
    distances = distance_combinations(coordinates)
    plot_station_distances(distances, name=name)


def distance_to_ns(distance):
    """Convert distance in meters to ns (light travel time)"""

    return distance / c


def plot_station_distances(distances, name=''):
    plot = Plot('semilogx')
    bins = numpy.logspace(0, 7, 41)
    counts, bins = numpy.histogram(distances, bins=bins)
    plot.histogram(counts, bins / 1e3)
    plot.set_xlabel(r'Distance [\si{\kilo\meter}]')
    plot.set_ylabel('Occurance')
    plot.set_ylimits(min=0)
    plot.set_xlimits(min=1e-3, max=2e3)
    plot.save_as_pdf('station_distances' + name)


def distance_combinations(coordinates):
    distances = [distance(c1, c2) for c1, c2 in combinations(coordinates, 2)]
    return distances


def distance(c1, c2):
    distance = numpy.sqrt(sum((c1 - c2) ** 2))
    return distance


if __name__ == '__main__':
    distances_sciencepark()
    distances_netherlands()
    distances_all_stations()
