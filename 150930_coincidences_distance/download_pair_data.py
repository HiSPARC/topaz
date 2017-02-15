""" Coincidence rate as function of distance

This script downloads coincidences for all station pairs which have a certain
distance to each other (up to 15000 m). It specifically downloads for
timestamp ranges for which both have event data.

Then the coincidence rate is determined from the total time both had data and
the number of found coincidences. Additionally a coincidence rate is
determined based on the time between coincidences. This is then plotted
against the distance between the stations.

"""
from __future__ import division

import os
import multiprocessing
import datetime

import tables

from sapphire import download_coincidences
from sapphire.transformations.clock import gps_to_datetime

from eventtime_ranges import get_timestamp_ranges, get_total_exposure
from station_distances import close_pairs_in_network, distance_between_stations
from rate_from_intervals import determine_rate


DATAPATH = '/Users/arne/Datastore/pairs/%d_%d.h5'


def download_coincidences_pairs_multi(close_pairs):
    """Like download_coincidences_pairs, but multithreaded"""

    worker_pool = multiprocessing.Pool(4)
    worker_pool.map(download_coincidences_pair, close_pairs)
    worker_pool.close()
    worker_pool.join()


def download_coincidences_pairs(close_pairs):
    """Download coincidences for the given pairs"""

    for close_pair in close_pairs:
        download_coincidences_pair(close_pair)


def download_coincidences_pair(pair):
    path = DATAPATH % tuple(pair)
    tmp_path = path + '_tmp'
    if os.path.exists(path):
        print 'Skipping', pair
        return
    print 'Starting', pair, datetime.datetime.now()
    distance = distance_between_stations(*pair)
    timestamp_ranges = get_timestamp_ranges(pair)
    total_exposure = get_total_exposure(timestamp_ranges)
    with tables.open_file(tmp_path, 'w') as data:
        data.set_node_attr('/', 'total_exposure', total_exposure)
        data.set_node_attr('/', 'distance', distance)
        for ts_start, ts_end in timestamp_ranges:
            download_coincidences(data, stations=list(pair),
                                  start=gps_to_datetime(ts_start),
                                  end=gps_to_datetime(ts_end),
                                  progress=False)
        try:
            coin = data.get_node('/coincidences')
        except tables.NoSuchNodeError:
            print 'No coincidences for', pair
            os.rename(tmp_path, path)
            return
        rate = coin.coincidences.nrows / total_exposure
        data.set_node_attr('/', 'n_rate', rate)
        data.set_node_attr('/', 'n_coincidences', coin.coincidences.nrows)
    os.rename(tmp_path, path)
    determine_rate(path)
    print 'Finished', pair, datetime.datetime.now()


if __name__ == "__main__":
    close_pairs = close_pairs_in_network(min=0, max=15e3)
    todo_pairs = [pair for pair in close_pairs if not os.path.exists(DATAPATH % tuple(pair))]
#     print todo_pairs
#     download_coincidences_pairs(todo_pairs)
    download_coincidences_pairs_multi(todo_pairs)
