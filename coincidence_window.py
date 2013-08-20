"""Test time windows for coincidences

This script gets the number of found coincidences as a function of the
coincidence window.

TODO: Fix coincidences that are subsets. The number of coincidences
should not keep increasing, because at some point one coincidence might
contain another coincidences. e.g. 1, 3, 2 also includes 3, 2. This
should perhaps be counted as only 1 coincidence.

"""
import datetime
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.gridspec as gridspec
import tables
import numpy

from sapphire.api import Station, Network
from sapphire.analysis import coincidences


ESD_PATH = '/Users/arne/Datastore/esd'


def coincidences_all_stations():
    network = Network()
    station_ids = [station['number'] for station in network.all_stations]
    coincidences_stations(station_ids, group_name='All stations')


def coincidences_each_cluster():
    network = Network()
    for cluster in network.all_clusters:
        stations = network.stations(cluster=cluster['number'])
        station_ids = [station['number'] for station in stations]
        group_name = '%s cluster' % cluster['name']
        coincidences_stations(station_ids, group_name=group_name)


def coincidences_sciencepark():
    network = Network()
    stations = network.stations(subcluster=500)
    station_ids = [station['number'] for station in stations]
    group_name = 'Science Park subcluster'
    coincidences_stations(station_ids, group_name=group_name)


def coincidences_stations(station_ids, group_name='Specific stations',
                          date=None):
    if date is None:
        date = datetime.date(2013, 8, 1)
    stations_with_data = []
    cluster_groups = []
    for station_id in station_ids:
        try:
            info = Station(station_id)
        except:
            continue
        if info.has_data(year=date.year, month=date.month, day=date.day):
            cluster_groups.append(info.cluster.lower())
            stations_with_data.append(station_id)

    if len(stations_with_data) <= 1:
        return

    filepath = os.path.join(ESD_PATH, date.strftime('%Y/%-m/%Y_%-m_%-d.h5'))
    data = tables.openFile(filepath, 'r')
    coinc, event_tables = get_event_tables(data, cluster_groups, stations_with_data)
    windows, counts, n_events = find_n_coincidences(coinc, event_tables)
    plot_coinc_window(windows, counts, group_name, n_events, date)
    data.close()


def get_event_tables(data, cluster_groups, station_ids):
    station_groups = ['/hisparc/cluster_%s/station_%d' % (c, s)
                      for c, s in zip(cluster_groups, station_ids)]

    coinc = coincidences.Coincidences(data, None, station_groups)

    event_tables = []
    for station_group in coinc.station_groups:
        try:
            event_tables.append(coinc.data.getNode(station_group, 'events'))
        except tables.NoSuchNodeError:
            print 'No events for: %s' % station_group

    return coinc, event_tables


def find_n_coincidences(coinc, event_tables):
    timestamps = coinc._retrieve_timestamps(event_tables)
    ts_arr = numpy.array(timestamps, dtype='3u8')
    n_events = len(timestamps)

    del timestamps

    ts_diff = ts_arr[1:, 0] - ts_arr[:-1, 0]
    not_same_station = ts_arr[1:, 1] != ts_arr[:-1, 1]
    ts_diff = ts_diff[not_same_station]

    del ts_arr

    # 10^14 ns = 1.1 day
    windows = 10 ** numpy.arange(0, 14, 0.2)
    counts = [len(numpy.where(ts_diff < window)[0]) for window in windows]

    if sum(counts) == 0:
        return
    else:
        return windows, counts, n_events


def plot_coinc_window(windows, counts, group_name='', n_events=0,
                      date=datetime.date.today()):
    counts = numpy.array(counts)
    plt.figure()
    grid = gridspec.GridSpec(2, 1, height_ratios=[4, 1])
    plt.subplot(grid[0])
    plt.plot(windows, counts)
    plt.yscale('log')
    plt.xscale('log')
    plt.annotate('%s\n'
                 'Date: %s\n'
                 'Total n events: %d\n' %
                 (group_name, date.isoformat(), n_events),
                 (0.05, 0.7), xycoords='axes fraction')
    plt.title('Found coincidences versus coincidence window')
    plt.ylabel('Found coincidences')
    plt.ylim(ymin=1)


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
    # coincidences_each_cluster()
    # coincidences_all_stations()
    coincidences_sciencepark()

"""
Idea for faster cincidence finding

- Use numpy array
- Find where difference between subsequent elements is less than window
- Then find where difference between those that passed previous check
  also have less difference than window between next (idx+2) element
- ...

"""
