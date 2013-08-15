"""Test time windows for coincidences

This script gets the number of found coincidences as a function of the
coincidence window.

TODO: Fix removal of coincidences. Currently this script filters
'self-coindences' but by doing so also removes some potential
coincidences at smaller windows. This is because if station n has 2
events directly after eachother in the combined sorted timestamps list,
the first of those two is removed. This removes the possibility of the
event before that to have a coincidence with the removed event. Should
be fixed by not removing events but adding extra condition that the
stations are not equal in the where.

TODO: Fix coincidences that are subsets. The number of coincidences
should not keep increasing, because at some point one coincidence might
contain another coincidences. e.g. 1, 3, 2 also includes 3, 2. This
should perhaps be counted as only 1 coincidence.

"""
import datetime
import os

import matplotlib.pyplot as plt
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
    station_coords = []
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
    windows, counts, n_events, n_filtered = find_n_coincidences(coinc, event_tables)
    plot_coinc_window(windows, counts, group_name, n_events, n_filtered, date)
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

    same_station = numpy.where(ts_arr[:-1, 1] == ts_arr[1:, 1])[0]
    while len(same_station) > 0:
        ts_arr = numpy.delete(ts_arr, same_station, axis=0)
        same_station = numpy.where(ts_arr[:-1, 1] == ts_arr[1:, 1])[0]
    n_filtered = len(ts_arr)

    ts_diff = ts_arr[1:, 0] - ts_arr[:-1, 0]

    del ts_arr

    # 10^14 ns = 1.1 day
    windows = 10 ** numpy.arange(0, 14, 0.2)
    counts = [len(numpy.where(ts_diff < window)[0]) for window in windows]

    if sum(counts) == 0:
        return
    else:
        return windows, counts, n_events, n_filtered


def plot_coinc_window(windows, counts, group_name='', n_events=0, n_filtered=0,
                      date=datetime.date.today()):
    plt.figure()
    plt.plot(numpy.log10(windows), counts)
    plt.annotate('%s\n'
                 'Date: %s\n'
                 'Total n events: %d\n'
                 'Without self coincidence: %d\n' %
                 (group_name, date.isoformat(), n_events, n_filtered),
                 (0.05, 0.7), xycoords='axes fraction')
    plt.title('Found coincidences versus coincidence window')
    plt.xlabel('Coincidence window (10^x)')
    plt.ylabel('Found coincidences')
    plt.yscale('log')
    plt.ylim(ymin=0.1)
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
