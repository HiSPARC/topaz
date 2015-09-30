""" Coincidence rate as function of distance

This script downloads coincidences for all station pairs which have a certain
distance to eachother (between 50 and 2000 m). It specifically downloads for
timestamp ranges for which both have event data.

Then the coincidence rate is determined from the total time both had data and
the number of found coincidences. This is then plotted against the distance
between the stations.

"""
import os

import tables
from artist import Plot
from numpy import array

from sapphire import download_coincidences
from sapphire.utils import pbar
from sapphire.transformations.clock import gps_to_datetime

from eventtime_ranges import get_timestamp_ranges
from station_distances import close_pairs_in_network, distance_between_stations

DATAPATH = '/Users/arne/Datastore/pairs/%d_%d.h5'


def download_pair_coincidences():
    close_pairs = close_pairs_in_network(min=50, max=2e3)

    for pair in pbar(close_pairs):
        path = DATAPATH % tuple(pair)
        if os.path.exists(path):
            continue
        timestamp_ranges = get_timestamp_ranges(pair)
        with tables.open_file(path, 'w') as data:
            for ts_start, ts_end in timestamp_ranges:
                print ts_start, ts_end
                download_coincidences(data, stations=list(pair),
                                      start=gps_to_datetime(ts_start),
                                      end=gps_to_datetime(ts_end),
                                      progress=False)


def get_coincidence_count():
    close_pairs = close_pairs_in_network(min=50, max=2e3)
    distances = []
    coincidence_rates = []
    for pair in pbar(close_pairs):
        distances.append(distance_between_stations(*pair))

        timestamp_ranges = array(get_timestamp_ranges(pair))
        total_exposure = (timestamp_ranges[:,1] - timestamp_ranges[:,0]).sum()

        print pair, total_exposure / 3600. / 24. / 365.

        path = DATAPATH % tuple(pair)
        if not os.path.exists(path):
            continue
        with tables.open_file(path, 'r') as data:
            n_coincidences = data.root.coincidences.coincidences.nrows

        coincidence_rates.append(n_coincidences / total_exposure)

    return distances, coincidence_rates


def plot_coincidence_rate_distance(distance, coincidence_rate):
    plot = Plot()
    plot.scatter(distance, coincidence_rate)
    plot.set_xlabel(r'Distance between stations \si{\meter}')
    plot.set_ylabel(r'Coincidence rate \si{\hertz}')
    plot.save_as_pdf('distance_v_coincidence_rate')


if __name__ == "__main__":
    download_pair_coincidences()
    plot_coincidence_rate_distance()
