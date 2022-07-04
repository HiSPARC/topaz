"""Test time windows for coincidences

This script gets the number of found coincidences as a function of the
coincidence window.

TODO: Fix coincidences that are subsets. The number of coincidences
should not keep increasing, because at some point one coincidence might
contain another coincidences. e.g. 1, 3, 2 also includes 3, 2. This
should perhaps be counted as only 1 coincidence.

"""
import numpy
import tables

from artist import MultiPlot

from sapphire import CoincidencesESD

EVENTDATA_PATH = '/Users/arne/Datastore/501_510/e_501_510_141101_150201.h5'


def coincidences_501_510():
    station_ids = [501, 510]
    coincidences_stations(station_ids)


def coincidences_stations(station_ids):

    with tables.open_file(EVENTDATA_PATH, 'r') as data:
        coinc, event_tables = get_event_tables(data, station_ids)
        windows, counts, n_events = find_n_coincidences(coinc, event_tables)
        plot_coinc_window(windows, counts, n_events)


def get_event_tables(data, station_ids):

    station_groups = ['/s%d' % s for s in station_ids]
    coinc = CoincidencesESD(data, None, station_groups)

    event_tables = []
    for station_group in coinc.station_groups:
        try:
            event_tables.append(coinc.data.get_node(station_group, 'events'))
        except tables.NoSuchNodeError:
            print('No events for: %s' % station_group)

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

    plot = MultiPlot(2, 1, axis='semilogx',
                     width=r'.8\linewidth', height=r'.5\linewidth')
    plot.set_title(0, 0, 'Number of coincidences as function of coincidence window')
    plot.set_xlabel('Coincidence window (ns)')
    plot.show_xticklabels(1, 0)
    plot.show_yticklabels_for_all()
    plot.set_xlimits_for_all(min=1e1, max=1e8)
    plot.set_ylimits(1, 0, min=0)

    counts = numpy.array(counts)

    subplot = plot.get_subplot_at(0, 0)
    subplot.set_ylabel('Found coincidences')
    subplot.plot(windows, counts, mark=None)

    subplot = plot.get_subplot_at(1, 0)
    subplot.set_ylabel('Delta found coincidences')
    subplot.plot(windows[:-1], counts[1:] - counts[:-1], mark=None)

    plot.save_as_pdf('coincidence_window')


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
