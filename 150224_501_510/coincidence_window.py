"""Test time windows for coincidences

This script gets the number of found coincidences as a function of the
coincidence window.

TODO: Fix coincidences that are subsets. The number of coincidences
should not keep increasing, because at some point one coincidence might
contain another coincidences. e.g. 1, 3, 2 also includes 3, 2. This
should perhaps be counted as only 1 coincidence.

"""
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.gridspec as gridspec
import tables
import numpy

from sapphire.api import Station, Network
from sapphire.analysis import coincidences


EVENTDATA_PATH = '/Users/arne/Datastore/501_510/e_501_510_141101_150201.h5'


def coincidences_501_510():
    station_ids = [501, 510]
    coincidences_stations(station_ids)


def coincidences_stations(station_ids):

    filepath = EVENTDATA_PATH
    with tables.openFile(filepath, 'r') as data:
        coinc, event_tables = get_event_tables(data, station_ids)
        windows, counts, n_events = find_n_coincidences(coinc, event_tables)
        plot_coinc_window(windows, counts, n_events)


def get_event_tables(data, station_ids):

    station_groups = ['/s%d' % s for s in station_ids]
    coinc = coincidences.CoincidencesESD(data, None, station_groups)

    event_tables = []
    for station_group in coinc.station_groups:
        try:
            event_tables.append(coinc.data.get_node(station_group, 'events'))
        except tables.NoSuchNodeError:
            print 'No events for: %s' % station_group

    return coinc, event_tables


def find_n_coincidences(coinc, event_tables):
    timestamps = coinc._retrieve_timestamps(event_tables)
    ts_arr = numpy.array(timestamps, dtype='3u8')
    n_events = len(timestamps)

    del timestamps

    ts_diff = ts_arr[1:, 0] - ts_arr[:-1, 0]
#     not_same_station = ts_arr[1:, 1] != ts_arr[:-1, 1]
#     ts_diff = ts_diff[not_same_station]

    del ts_arr

    # 10^14 ns = 1.1 day
    windows = numpy.logspace(1, 14, 14 * 9 + 1)
    counts = [len(numpy.where(ts_diff < window)[0]) for window in windows]

    if sum(counts) == 0:
        return
    else:
        return windows, counts, n_events


def plot_coinc_window(windows, counts, n_events=0):
    counts = numpy.array(counts)
    plt.figure()
    grid = gridspec.GridSpec(2, 1, height_ratios=[4, 1])
    plt.subplot(grid[0])
    plt.plot(windows, counts)
    plt.yscale('log')
    plt.xscale('log')
    plt.annotate('501 and 510\n'
                 'Total n events: %d\n' % n_events,
                 (0.05, 0.8), xycoords='axes fraction')
    plt.title('Found coincidences versus coincidence window')
    plt.ylabel('Found coincidences')
    plt.ylim(ymin=1e3)


    plt.subplots_adjust(wspace=0, hspace=0)
    plt.gca().xaxis.set_major_formatter(ticker.NullFormatter())
    plt.subplot(grid[1])
    plt.plot(windows[:-1], counts[1:] - counts[:-1])
    plt.xlabel('Coincidence window (ns)')
    plt.gca().yaxis.tick_right()
    plt.ylim(ymin=1)
    plt.yscale('log')
    plt.xscale('log')

    plt.show()


if __name__ == '__main__':
    coincidences_501_510()

"""
Idea for faster coincidence finding

- Use numpy array
- Find where difference between subsequent elements is less than window
- Then find where difference between those that passed previous check
  also have less difference than window between next (idx+2) element
- ...

"""
