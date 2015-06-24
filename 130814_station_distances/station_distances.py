"""Distances between combinations of 2 stations

This script collects coordinates of stations, then makes
all possible combinations of 2 different stations, it
calculates the distances of the combinations, and makes
a histogram to show these distances.

"""
from itertools import combinations

from artist import Plot
import numpy

from sapphire import Station, Network


def distances_sciencepark():
    network = Network()
    station_ids = [station['number'] for station in network.stations(subcluster=500)]
    distances_stations(station_ids, name='_sciencepark')


def distances_all_stations():
    network = Network()
    station_ids = [station for station in network.station_numbers()]
    distances_stations(station_ids, name='_all')


def distances_stations(station_ids, name=''):
    station_coords = []
    for station_id in station_ids:
        try:
            info = Station(station_id)
        except:
            print 'Failed for %d' % station_id
            continue
        station_coords.append(info.location())

    distances = distance_combinations(station_coords)
    plot_station_distances(distances, name=name)


def Dns(Dm):
    """Convert distance in meters to ns (light travel time)"""
    c = 0.3  # m/ns (or km/us)
    return Dm / c


def plot_station_distances(distances, name=''):
    plot = Plot('semilogx')
    bins = numpy.logspace(-3, 5, 71)
    counts, bins = numpy.histogram(distances, bins=bins)
    plot.histogram(counts, bins)
    plot.set_title('Distances between all combinations of 2 stations')
    plot.set_xlabel('Distance (km)')
    plot.set_ylabel('Occurance')
    plot.set_ylimits(min=0)
    plot.set_xlimits(min=1e-3, max=1e5)
    plot.save_as_pdf('station_distances' + name)


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
    distances_sciencepark()
    distances_all_stations()
