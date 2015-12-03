"""Detect stations that may have issues with GPS locations"""

import itertools

import numpy

from sapphire import Network, Station
from sapphire.transformations.clock import gps_to_datetime

COLORS = ['black', 'red', 'green', 'blue']


def detect_problems(station):
    try:
        gps_locations = station.gps_locations
    except:
        print station.station, 'no GPS locations'
        return

    if len(gps_locations) < 2:
        return

    for p1, p2 in itertools.combinations(gps_locations, 2):
        d = distance(p1, p2)
        if d > .25:
            print station.station, d
            break


def distance(s1, s2):
    """
    returns distance in km
    """
    R = 6371  # km Radius of earth
    d_lat = numpy.radians(s2['latitude'] - s1['latitude'])
    d_lon = numpy.radians(s2['longitude'] - s1['longitude'])
    a = (numpy.sin(d_lat / 2) ** 2 + numpy.cos(numpy.radians(s1['latitude'])) *
         numpy.cos(numpy.radians(s2['latitude'])) * numpy.sin(d_lon / 2) ** 2)
    c = 2 * numpy.arctan2(numpy.sqrt(a), numpy.sqrt(1 - a))
    distance = R * c
    return distance


if __name__ == "__main__":
    for sn in Network().station_numbers():
        station = Station(sn)
        detect_problems(station)
