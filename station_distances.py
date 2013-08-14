"""Distances between combinations of 2 stations

This script collects coordinates of stations, then makes
all possible combinations of 2 different stations, it
calculates the distances of the combinations, and makes
a histogram to show these distances.

"""
from itertools import combinations

import matplotlib.pyplot as plt
import numpy

from sapphire.api import Station, Network


def distances_all_stations():
    network = Network()
    station_coords = []
    for station in network.all_stations:
        try:
            info = Station(station['number'])
        except:
            print 'Failed for %d' % station['number']
            continue
        station_coords.append(info.location())

    distances = distance_combinations(station_coords)
    plot_station_distances(distances)


def Dns(Dm):
    """Convert distance in meters to ns (light travel time)"""
    c = 0.3  # m/ns (or km/us)
    return Dm / c


def plot_station_distances(distances):
    fig = plt.figure()
    ax1 = plt.subplot(111) # y-axis in m
    bins = numpy.logspace(-2, 5, 71)
    plt.hist(distances, bins=bins, histtype='step')
    plt.title('Distances between all combinations of 2 stations')
    plt.xlabel('Distance (km)')
    plt.ylabel('Occurance')
    plt.xscale('log')
    # title.set_y(1.09)
    # plt.subplots_adjust(top=0.86)
    # ax2 = plt.twiny() # x-axis in us
    # x1, x2 = ax1.get_xlim()
    # ax2.set_xlim(Dns(x1), Dns(x2))
    plt.show()


def distance_combinations(coordinates):
    distances = [distance(s1, s2) for s1, s2 in combinations(coordinates, 2)]
    return distances


def distance(s1, s2):
    R = 6371  # km Radius of earth
    d_lat = numpy.radians(s2['latitude'] - s1['latitude'])
    d_lon = numpy.radians(s2['longitude'] - s1['longitude'])
    a = (numpy.sin(d_lat / 2) ** 2 + numpy.cos(numpy.radians(s1['latitude'])) *
         numpy.cos(numpy.radians(s2['latitude'])) * numpy.sin(d_lon / 2) ** 2)
    c = 2 * numpy.arctan2(numpy.sqrt(a), numpy.sqrt(1 - a))
    distance = R * c
    return distance


if __name__ == '__main__':
    distances_all_stations()
