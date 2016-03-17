from datetime import date
import os
import csv

from numpy import (sum, sin, linspace, random, searchsorted, split, nan, array,
                   empty, column_stack, genfromtxt)
import tables

from artist import Plot, MultiPlot

from sapphire.transformations.clock import datetime_to_gps
from sapphire.utils import pbar

from download_dataset import STATIONS, START, END


DATASTORE = "/Users/arne/Datastore/dataset"
DATA_PATH = os.path.join(DATASTORE,
                         'dataset_sciencepark_stations_110601_160201.h5')
COIN_PATH = os.path.join(DATASTORE, 'dataset_sciencepark_n2_110601_160201.h5')
TSV_PATH = os.path.join(DATASTORE, 'stats/s%d_%s.tsv')

# STATIONS = STATIONS[-2:]
START_TS = datetime_to_gps(date(*START, day=1))
END_TS = datetime_to_gps(date(*END, day=1))
BINS = linspace(START_TS, END_TS, 481)
BIN_WIDTH = BINS[1] - BINS[0]
COLORS = ['black', 'red', 'green', 'blue']

YEARS = range(2011, date.today().year + 1)
YEARS_TICKS = array([datetime_to_gps(date(y, 1, 1)) for y in YEARS])
YEARS_LABELS = [str(y) for y in YEARS]

FIELDS = ['integrals', 't_trigger', 'event_rate',
          ('t1', 't2', 't3', 't4'),
          ('n1', 'n2', 'n3', 'n4')]
FIELD_NAMES = [''.join(field) for field in FIELDS]


def frac_bad(values):
    """Get fraction of bad values in an array"""

    if len(values):
        return 100. * sum(values < 0, axis=0) / len(values)
    else:
        try:
            result = empty(values.shape[1])
            result.fill(nan)
            return result
        except:
            return nan


def binned_stat(x, values, func, bins):
    """Similar to binned_statistic but assumes sorted (sorted by x) data"""

    idx_ranges = searchsorted(x, bins[1:-1])
    return array([func(group) for group in split(values, idx_ranges)]).T


def binned_stat_idx(events, idx_ranges, station):

    stats = {}
    for field_name in FIELD_NAMES:
        if field_name == 'event_rate':
            stats[field_name] = get_event_rate(idx_ranges)
        else:
            stats[field_name] = []

    for start, stop in pbar(zip(idx_ranges[:-1], idx_ranges[1:])):
        slice = events.read(start, stop)
        for field, field_name in zip(FIELDS, FIELD_NAMES):
            if field_name == 'event_rate':
                continue
            elif isinstance(field, tuple):
                data = column_stack(slice[f] for f in field)
            else:
                data = slice[field]
            stats[field_name].append(frac_bad(data))

    for field_name in FIELD_NAMES:
        stats[field_name] = array(stats[field_name]).T

    return stats


def get_event_rate(idx_ranges):
    stat = (idx_ranges[1:] - idx_ranges[:-1]) / BIN_WIDTH
    return stat


def get_idx_ranges(events):
    ts = events.col('timestamp')
    idx_ranges = searchsorted(ts, BINS)
    return idx_ranges


def determine_station_stats(data, station):
    events = data.get_node('/s%d' % station, 'events')
    idx_ranges = get_idx_ranges(events)
    stats = binned_stat_idx(events, idx_ranges, station)

    save_station_stats(stats, station)

    return stats


def determine_all_stats(data):
    """

    Statistics is a dictionary which first contains stations, and
    each station contains fields, which contain the statistics arrays.

    """
    stats = {station: determine_station_stats(data, station)
             for station in STATIONS}

    return stats


def save_stat(stat, station, field_name):
    path = TSV_PATH % (station, field_name)
    with open(path, 'wb') as tsvfile:
        tsv = csv.writer(tsvfile, delimiter='\t')
        timestamped_stats = column_stack((BINS[:-1], stat.T))
        tsv.writerows(timestamped_stats)


def save_station_stats(stats, station):
    for field_name in FIELD_NAMES:
        save_stat(stats[field_name], station, field_name)


def save_stats(stats):
    for station in STATIONS:
        for field_name in FIELD_NAMES:
            save_stat(stats[station][field_name], station, field_name)


def get_stat(station, field_name):
    path = TSV_PATH % (station, field_name)
    stat = genfromtxt(path, delimiter='\t')
    # Check if the BINS have changed
    assert all(stat[:, 0] == BINS[:-1])

    return stat[:, 1:].T


def get_station_stats(station):
    print 'Reading stats for %d' % station
    try:
        stats = {field_name: get_stat(station, field_name)
                 for field_name in FIELD_NAMES}
    except (TypeError, IOError, AssertionError):
        print 'Determining stats for %d' % station
        with tables.open_file(DATA_PATH) as data:
            stats = determine_station_stats(data, station)

    return stats


def get_all_stats():
    """First try reading from TSV, if not available determine from data"""

    stats = {station: get_station_stats(station) for station in STATIONS}
    return stats


def plot_bad_value_timeline(stats, field_name, ylabel=None):
    step = 0.2 * BIN_WIDTH
    plot = MultiPlot(len(STATIONS), 1,
                     width=r'.67\textwidth', height=r'.05\paperheight')
    for splot, station in zip(plot.subplots, STATIONS):
        stat = stats[station][field_name]
        if len(stat.shape) == 2:
            for i, s in enumerate(stat):
                splot.histogram(s, BINS + (step * i), linestyle=COLORS[i])
        else:
            splot.histogram(stat, BINS)
        splot.set_ylabel(r'%d' % station)

    plot.set_xlimits_for_all(None, min=BINS[0], max=BINS[-1])
    plot.set_xticks_for_all(None, YEARS_TICKS)
    plot.subplots[-1].set_xtick_labels(YEARS_LABELS)
    plot.subplots[-1].show_xticklabels()

    plot.show_yticklabels_for_all(None)
    for row in range(0, len(plot.subplots), 2):
        plot.set_yticklabels_position(row, 0, 'left')
    for row in range(1, len(plot.subplots), 2):
        plot.set_yticklabels_position(row, 0, 'right')
    plot.set_ylimits_for_all(None, -1e-4)

    plot.set_xlabel(r'Timestamp')
    if ylabel is None:
        plot.set_ylabel(r'Fraction of bad %s data [\si{\percent}]' %
                        field_name.replace('_', ' '))
    else:
        plot.set_ylabel(ylabel)
    plot.save_as_pdf('bad_fraction_%s' % field_name)


def plot_bad_value_timelines(statistics):
    for field_name in FIELD_NAMES:
        if field_name == 'event_rate':
            ylabel = r'Event rate [\si{\hertz}]'
        else:
            ylabel = None
        plot_bad_value_timeline(statistics, field_name, ylabel)


if __name__ == "__main__":

    statistics = get_all_stats()

    plot_bad_value_timelines(statistics)
