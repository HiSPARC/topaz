from datetime import date
import os

from numpy import (sum, sin, linspace, random, searchsorted, split, nan, array,
                   empty, column_stack)
import tables

from artist import Plot, MultiPlot

from sapphire.transformations.clock import datetime_to_gps
from sapphire.utils import pbar

from download_dataset import STATIONS, START, END


DATASTORE = "/Users/arne/Datastore/dataset"
DATA_PATH = os.path.join(DATASTORE,
                         'dataset_sciencepark_stations_110601_160201.h5')
# STATIONS = STATIONS[-2:]
START_TS = datetime_to_gps(date(*START, day=1))
END_TS = datetime_to_gps(date(*END, day=1))
BINS = linspace(START_TS, END_TS, 241)
BIN_WIDTH = BINS[1] - BINS[0]
COLORS = ['black', 'red', 'green', 'blue']

YEARS = range(2011, date.today().year + 1)
YEARS_TICKS = array([datetime_to_gps(date(y, 1, 1)) for y in YEARS])
YEARS_LABELS = [str(y) for y in YEARS]


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


def get_stats(data, field):
    stats = {}
    for station in pbar(STATIONS):
        events = data.get_node('/s%d' % station, 'events')
        if isinstance(field, tuple):
            cdata = column_stack(events.col(f) for f in field)
            stat = binned_stat(events.col('timestamp'),
                               cdata, frac_bad, bins=BINS)
        else:
            stat = binned_stat(events.col('timestamp'),
                               events.col(field), frac_bad, bins=BINS)
        stats[station] = stat
    return stats


def get_event_rates(data):
    stats = {}
    for station in pbar(STATIONS):
        events = data.get_node('/s%d' % station, 'events')
        ts = events.col('timestamp')
        idx_ranges = searchsorted(ts, BINS)
        stat = (idx_ranges[1:] - idx_ranges[:-1]) / BIN_WIDTH
        stats[station] = stat
    return stats


def plot_bad_value_timeline(stats, field, ylabel=None):
    step = 0.2 * BIN_WIDTH
    plot = MultiPlot(len(STATIONS), 1,
                     width=r'.67\textwidth', height=r'.05\paperheight')
    for splot, station in zip(plot.subplots, STATIONS):
        stat = stats[station]
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
        plot.set_ylabel(r'Fraction of bad data [\si{\percent}]')
    else:
        plot.set_ylabel(ylabel)
    plot.save_as_pdf('bad_fraction_%s' % ''.join(field))


if __name__ == "__main__":
    if 'statistics' not in globals():
        fields = ['integrals', 't_trigger',
                  ('t1', 't2', 't3', 't4'),
                  ('n1', 'n2', 'n3', 'n4')]
        statistics = {}
        with tables.open_file(DATA_PATH) as data:
            statistics['event_rate'] = get_event_rates(data)
            plot_bad_value_timeline(statistics['event_rate'], 'event_rate',
                                    r'Event rate [\si{\hertz}]')
            for field in fields:
                statistics[field] = get_stats(data, field)
                plot_bad_value_timeline(statistics[field], field)

    plot_bad_value_timeline(statistics['event_rate'], 'event_rate',
                            r'Event rate [\si{\hertz}]')
    for field in fields:
        plot_bad_value_timeline(statistics[field], field)
