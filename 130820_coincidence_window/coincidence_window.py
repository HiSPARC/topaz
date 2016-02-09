"""Test time windows for coincidences

This script gets the number of found coincidences as a function of the
coincidence window.

TODO: Fix coincidences that are subsets. The number of coincidences
should not keep increasing, because at some point one coincidence might
contain another coincidences. e.g. 1, 3, 2 also includes 3, 2. This
should perhaps be counted as only 1 coincidence.

Ideas for faster coincidence finding

- Use numpy array
- Find where difference between subsequent elements is less than window
- Then find where difference between those that passed previous check
  also have less difference than window between next (idx+2) element
- ...

Notes

- Lower than predicted background rate for Nijmegen due to low trigger rate


"""
import datetime
import os
from itertools import combinations

import tables
import numpy

from artist import MultiPlot

from sapphire import Station, Network, Coincidences


ESD_PATH = '/Users/arne/Datastore/esd'


def coincidences_all_stations():
    network = Network()
    station_numbers = [station for station in network.station_numbers()]
    coincidences_stations(station_numbers, group_name='All stations')


def coincidences_each_cluster():
    network = Network()
    for cluster in network.clusters():
        stations = network.stations(cluster=cluster['number'])
        station_numbers = [station['number'] for station in stations]
        group_name = '%s cluster' % cluster['name']
        coincidences_stations(station_numbers, group_name=group_name)


def coincidences_sciencepark():
    network = Network()
    stations = network.stations(subcluster=500)
    station_numbers = [station['number'] for station in stations]
    group_name = 'Science Park subcluster'
    coincidences_stations(station_numbers, group_name=group_name)


def coincidences_stations(station_numbers, group_name='Specific stations',
                          date=None):
    if date is None:
        date = datetime.date(2016, 2, 1)
    stations_with_data = []
    cluster_groups = []
    for station_id in station_numbers:
        try:
            info = Station(station_id)
        except:
            continue
        if info.has_data(year=date.year, month=date.month, day=date.day):
            cluster_groups.append(info.cluster().lower())
            stations_with_data.append(station_id)

    if len(stations_with_data) <= 1:
        return

    filepath = os.path.join(ESD_PATH, date.strftime('%Y/%-m/%Y_%-m_%-d.h5'))
    with tables.open_file(filepath, 'r') as data:
        coinc, event_tables = get_event_tables(data, cluster_groups, stations_with_data)
        windows, counts, n_events = find_n_coincidences(coinc, event_tables)
        n_stations = len(stations_with_data)
        plot_coinc_window(windows, counts, group_name, n_events, n_stations,
                          date)


def get_event_tables(data, cluster_groups, station_numbers):
    station_groups = ['/hisparc/cluster_%s/station_%d' % (c, s)
                      for c, s in zip(cluster_groups, station_numbers)]

    coinc = Coincidences(data, None, station_groups)

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

def plot_background_v_window(plot, windows, n_stations):
    low_rate = 0.3
    high_rate = 0.8
    n_pairs = len(list(combinations(range(n_stations), 2)))
    background_rate_low_pair = 2 * windows * 1e-9 * low_rate ** 2 * 86400
    background_rate_high_pair = 2 * windows * 1e-9 * high_rate ** 2 * 86400
    background_rate_low = background_rate_low_pair * n_pairs
    background_rate_high = background_rate_high_pair * n_pairs
    plot.shade_region(windows, background_rate_low, background_rate_high)


def plot_chosen_coincidence_window(plot):
    plot.draw_vertical_line(2e3)
    plot.draw_vertical_line(10e3)


def plot_coinc_window(windows, counts, group_name='', n_events=0, n_stations=0,
                      date=datetime.date.today()):
    counts = numpy.array(counts)
    plot = MultiPlot(2, 1, axis='loglog')

    splot = plot.get_subplot_at(0, 0)
    splot.plot(windows, counts)
    plot_background_v_window(splot, windows, n_stations)
    plot_chosen_coincidence_window(splot)
    splot = plot.get_subplot_at(1, 0)
    splot.plot(windows[:-1], counts[1:] - counts[:-1])
    splot.set_axis_options(r'height=0.2\textwidth')

    text = ('%s\nDate: %s\nTotal n events: %d' %
            (group_name, date.isoformat(), n_events))
    plot.set_label(0, 0, text, 'upper left')
    plot.set_xlimits_for_all(min=0.5, max=1e14)
    plot.set_ylimits(0, 0, max=1e8)
    plot.set_ylimits_for_all(min=1)
    plot.set_ylabel('Found coincidences')
    plot.set_xlabel(r'Coincidence window [\si{\ns}]')
    plot.show_xticklabels(1, 0)
    plot.show_yticklabels_for_all(None)
    plot.set_yticklabels_position(1, 0, 'right')

    plot.save_as_pdf('plots/coincidences_%s' % group_name)


if __name__ == '__main__':
    coincidences_each_cluster()
    coincidences_all_stations()
    coincidences_sciencepark()
