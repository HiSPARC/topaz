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
import multiprocessing
import datetime

import tables

from sapphire import download_coincidences
from sapphire.utils import pbar
from sapphire.transformations.clock import gps_to_datetime

from eventtime_ranges import get_timestamp_ranges, get_total_exposure
from station_distances import close_pairs_in_network, distance_between_stations


DATAPATH = '/Users/arne/Datastore/pairs/%d_%d.h5'


def download_coincidences_pairs(close_pairs):
#     worker_pool = multiprocessing.Pool(4)
#     worker_pool.map(download_coincidences_pair, close_pairs)
#     worker_pool.close()
#     worker_pool.join()
    for close_pair in close_pairs:
        download_coincidences_pair(close_pair)


def download_coincidences_pair(pair):
    path = DATAPATH % tuple(pair)
    tmp_path = path + '_tmp'
    if os.path.exists(path):
        print 'Already exists', pair
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
        rate = data.root.coincidences.coincidences.nrows / total_exposure
        data.set_node_attr('/', 'n_rate', rate)
    os.rename(tmp_path, path)
    print 'Finished', pair, datetime.datetime.now()

if __name__ == "__main__":
    close_pairs = close_pairs_in_network(min=30, max=15e3)
    download_coincidences_pairs(close_pairs)
