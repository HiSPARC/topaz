""" Coincidence rate as function of distance

This script downloads coincidences for all station pairs which have a certain
distance to eachother (between 50 and 2000 m). It specifically downloads for
timestamp ranges for which both have event data.

Then the coincidence rate is determined from the total time both had data and
the number of found coincidences. This is then plotted against the distance
between the stations.

"""
from __future__ import division

import os

import tables
from artist import Plot
from numpy import array, sqrt

from sapphire import download_coincidences, HiSPARCNetwork
from sapphire.utils import pbar
from sapphire.transformations.clock import gps_to_datetime

from eventtime_ranges import get_timestamp_ranges, get_total_exposure
from station_distances import close_pairs_in_network, distance_between_stations

DATAPATH = '/Users/arne/Datastore/pairs/%d_%d.h5'


def download_pair_coincidences(close_pairs):
    for pair in pbar(close_pairs):
        path = DATAPATH % tuple(pair)
        if os.path.exists(path):
            continue
        distance = distance_between_stations(*pair)
        timestamp_ranges = get_timestamp_ranges(pair)
        total_exposure = get_total_exposure(timestamp_ranges)
        with tables.open_file(path, 'w') as data:
            for ts_start, ts_end in timestamp_ranges:
                print ts_start, ts_end
                download_coincidences(data, stations=list(pair),
                                      start=gps_to_datetime(ts_start),
                                      end=gps_to_datetime(ts_end),
                                      progress=False)
            data.set_node_attr('/', 'total_exposure', total_exposure)
            data.set_node_attr('/', 'distance', distance)


def get_coincidence_count(close_pairs):
    network = HiSPARCNetwork()
    distances = {4: [], 6: [], 8:[]}
    coincidence_rates = {4: [], 6: [], 8:[]}
    coincidence_rates_err = {4: [], 6: [], 8:[]}
    for pair in pbar(close_pairs, show=False):
        path = DATAPATH % tuple(pair)
        if not os.path.exists(path):
            continue
        if 507 in pair:
            continue
        with tables.open_file(path, 'r') as data:
            total_exposure = data.get_node_attr('/', 'total_exposure')
            distance = data.get_node_attr('/', 'distance')
            try:
                n_coincidences = data.root.coincidences.coincidences.nrows
            except tables.NoSuchNodeError:
                continue
            if not n_coincidences:
                continue
        n = (len(network.get_station(pair[0]).detectors) +
             len(network.get_station(pair[1]).detectors))
        distances[n].append(distance)
        rate = n_coincidences / total_exposure
        coincidence_rates[n].append(rate)
        err = sqrt(n_coincidences + 1) / total_exposure
        if err > rate:
            err = rate - 1e-15
        coincidence_rates_err[n].append(err)

    return distances, coincidence_rates, coincidence_rates_err


def plot_coincidence_rate_distance(distances, coincidence_rates, rate_errors):
    markers = {4: 'o', 6: 'triangle', 8: 'square'}
    background_4 = 2 * .7 ** 2 * 2e-6
    background_2 = 2 * .4 ** 2 * 2e-6
    background_2_4 = 2 * .4 * .7 * 2e-6
    plot = Plot('loglog')
    plot.draw_horizontal_line(background_4)
    plot.draw_horizontal_line(background_2)
    plot.draw_horizontal_line(background_2_4)
    for n in distances.keys():
        plot.scatter(distances[n], coincidence_rates[n], yerr=rate_errors[n],
                     mark=markers[n], markstyle='mark size=.75pt')
    plot.set_xlabel(r'Distance between stations [\si{\meter}]')
    plot.set_ylabel(r'Coincidence rate [\si{\hertz}]')
    plot.set_axis_options('log origin y=infty')
    plot.set_xlimits(min=10, max=3e4)
    plot.save_as_pdf('distance_v_coincidence_rate')
#     plot.save_as_document('distance_v_coincidence_rate')


if __name__ == "__main__":
    close_pairs = close_pairs_in_network(min=45, max=2e3)
    close_pairs += close_pairs_in_network(min=9e3, max=1e4)
    close_pairs += close_pairs_in_network(min=1.2e4, max=1.5e4)

    download_pair_coincidences(close_pairs)
    distances, rates, rate_errors = get_coincidence_count(close_pairs)
    plot_coincidence_rate_distance(distances, rates, rate_errors)
