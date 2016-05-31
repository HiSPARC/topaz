from datetime import date
import os
import csv
import itertools

from numpy import (sum, sin, arange, random, searchsorted, split, nan, array,
                   empty, column_stack, genfromtxt, histogram2d)
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
BINS = arange(START_TS, END_TS + 1, 86400)
BIN_WIDTH = BINS[1] - BINS[0]
COLORS = ['black', 'red', 'green', 'blue']

YEARS = range(2011, date.today().year + 1)
YEARS_TICKS = array([datetime_to_gps(date(y, 1, 1)) for y in YEARS])
YEARS_LABELS = [str(y) for y in YEARS]

FIELDS = ['event_rate', 'mpv',
          'integrals', 't_trigger',
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


def reconstruct_mpv(slice):
    """Get first events in slice with a positive value in number of particles

    A positive (non-zero) n# is required to determine the MPV from the
    intergrals and n#. If the slice contains no applicable events
    the returned value will be nan.

    Works best for slices of a day because the MPV for the ESD is determined
    daily.

    """
    mpvs = []
    for detector_id in range(4):
        try:
            event = next(e for e in slice
                         if e['n%d' % (detector_id + 1)] > 0.1)
        except:
            mpvs.append(nan)
        else:
            mpv = (event['integrals'][detector_id] /
                   event['n%d' % (detector_id + 1)])
            mpvs.append(int(mpv))
    return mpvs


def binned_stat(x, values, func, bins):
    """Similar to binned_statistic but assumes sorted (sorted by x) data"""

    idx_ranges = searchsorted(x, bins[1:-1])
    return array([func(group) for group in split(values, idx_ranges)]).T


def binned_stat_idx(events, idx_ranges):

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
                # Event time determined above
                continue
            elif field_name == 'mpv':
                # Simply the MPV value, not fraction of bad MPV
                mpvs = reconstruct_mpv(slice)
                stats[field_name].append(mpvs)
            elif isinstance(field, tuple):
                data = column_stack(slice[f] for f in field)
                stats[field_name].append(frac_bad(data))
            else:
                data = slice[field]
                stats[field_name].append(frac_bad(data))

    for field_name in FIELD_NAMES:
        stats[field_name] = array(stats[field_name]).T

    return stats


def get_event_rate(idx_ranges):
    stat = (idx_ranges[1:] - idx_ranges[:-1]) / float(BIN_WIDTH)
    return stat


def get_idx_ranges(events):
    ts = events.col('timestamp')
    idx_ranges = searchsorted(ts, BINS)
    return idx_ranges


def determine_station_stats(data, station):
    events = data.get_node('/s%d' % station, 'events')
    idx_ranges = get_idx_ranges(events)
    stats = binned_stat_idx(events, idx_ranges)

    save_idx_ranges(idx_ranges, station)
    save_station_stats(stats, station)

    return stats


def save_idx_ranges(idx_ranges, station):
    path = TSV_PATH % (station, 'idx_ranges')
    with open(path, 'wb') as tsvfile:
        tsv = csv.writer(tsvfile, delimiter='\t')
        timestamped_stats = column_stack((BINS[:-1], idx_ranges[:-1]))
        tsv.writerows(timestamped_stats)


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


def plot_timeline(stats, field_name):
    step = 0.2 * BIN_WIDTH

    plot = MultiPlot(len(STATIONS), 1,
                     width=r'.67\textwidth', height=r'.075\paperheight')
#     if field_name in ['event_rate', 'mpv']:
#         plot = MultiPlot(len(STATIONS), 1,
#                          width=r'.67\textwidth', height=r'.05\paperheight')
#     else:
#         plot = MultiPlot(len(STATIONS), 1, 'semilogy',
#                          width=r'.67\textwidth', height=r'.05\paperheight')

    for splot, station in zip(plot.subplots, STATIONS):
        stat = stats[station][field_name]
        if len(stat.shape) == 2:
            for i, s in enumerate(stat):
                splot.histogram(s, BINS + (step * i),
                                linestyle='thin,' + COLORS[i])
        else:
            splot.histogram(stat, BINS, linestyle='thin')
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

#     if field_name not in ['event_rate', 'mpv']:
#         plot.set_ylimits_for_all(None, 1e-4, 100)

    plot.set_xlabel(r'Timestamp')

    if field_name == 'event_rate':
        ylabel = r'Event rate [\si{\hertz}]'
    elif field_name == 'mpv':
        ylabel = r'MPV [ADC.ns]'
    else:
        ylabel = (r'Fraction of bad %s data [\si{\percent}]' %
                  field_name.replace('_', ' '))
    plot.set_ylabel(ylabel)

    if field_name in ['event_rate', 'mpv']:
        plot.save_as_pdf('plots/%s' % field_name)
    else:
        plot.save_as_pdf('plots/bad_fraction_%s' % field_name)


def plot_timelines(statistics):
    for field_name in FIELD_NAMES:
        plot_timeline(statistics, field_name)


def plot_comparison(stats, field_name):
    plot = MultiPlot(len(STATIONS), len(STATIONS),
                     width=r'.06\textwidth', height=r'.06\textwidth')
    bins = arange(0, 1.2, .03)
    for i, ref_station in enumerate(STATIONS):
        ref_stat = stats[ref_station][field_name][0]
        ref_filter = ref_stat > 0
        for j, station in enumerate(STATIONS):
            if i == j:
                plot.set_empty(i, j)
                plot.set_label(r'%d' % station, location='center')
                continue
            splot = plot.get_subplot_at(i, j)
            stat = stats[station][field_name][0]

            tmp_stat = stat.compress(ref_filter & (stat > 0))
            tmp_ref_stat = ref_stat.compress(ref_filter & (stat > 0))
            counts, xbin, ybin = histogram2d(tmp_stat, tmp_ref_stat, bins=bins)
            splot.histogram2d(counts, xbin, ybin, type='reverse_bw', bitmap=True)
            splot.plot([0, 1.2], [0, 1.2], mark=None, linestyle='red, very thin')
#     plot.set_xlimits_for_all(None, min=bins[0], max=bins[-1])
#     plot.set_ylimits_for_all(None, min=bins[0], max=bins[-1])
#     plot.subplots[-1].set_xtick_labels(YEARS_LABELS)
#     plot.subplots[-1].show_xticklabels()
#
#     plot.show_yticklabels_for_all(None)
#     for row in range(0, len(plot.subplots), 2):
#         plot.set_yticklabels_position(row, 0, 'left')
#     for row in range(1, len(plot.subplots), 2):
#         plot.set_yticklabels_position(row, 0, 'right')
#     plot.set_ylimits_for_all(None, -1e-4)


    if field_name == 'event_rate':
        label = r'Event rate [\si{\hertz}]'
    elif field_name == 'mpv':
        label = r'MPV [ADC.ns]'
    else:
        label = (r'Fraction of bad %s data [\si{\percent}]' %
                 field_name.replace('_', ' '))
    plot.set_ylabel(label)
    plot.set_xlabel(label)

    if field_name in ['event_rate', 'mpv']:
        plot.save_as_pdf('plots/compare_%s' % field_name)
    else:
        plot.save_as_pdf('plots/compare_bad_fraction_%s' % field_name)


def plot_comparison_501_510(stats, field_name):
    plot = Plot()
    bins = arange(0, 1, .02)

    ref_stat = stats[501][field_name][0]
    stat = stats[510][field_name][0]

    tmp_stat = stat.compress((ref_stat > 0) & (stat > 0))
    tmp_ref_stat = ref_stat.compress((ref_stat > 0) & (stat > 0))
    counts, xbin, ybin = histogram2d(tmp_stat, tmp_ref_stat, bins=bins)
    plot.histogram2d(counts, xbin, ybin, type='reverse_bw', bitmap=True)
    plot.plot([0, 1.2], [0, 1.2], mark=None, linestyle='red, very thin')

    if field_name == 'event_rate':
        label = r'Event rate [\si{\hertz}]'
    elif field_name == 'mpv':
        label = r'MPV [ADC.ns]'
    else:
        label = (r'Fraction of bad %s data [\si{\percent}]' %
                 field_name.replace('_', ' '))
    plot.set_ylabel(label)
    plot.set_xlabel(label)

    if field_name in ['event_rate', 'mpv']:
        plot.save_as_pdf('plots_501_510/compare_%s' % field_name)
    else:
        plot.save_as_pdf('plots_501_510/compare_bad_fraction_%s' % field_name)


if __name__ == "__main__":
    statistics = get_all_stats()
    plot_timelines(statistics)
    plot_comparison(statistics, 'event_rate')
    plot_comparison_501_510(statistics, 'event_rate')
