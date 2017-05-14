"""Determine detector offset drift over time

This determines the detector offsets for several stations on various dates.

The offsets seems fairly constant over time, within a nanosecond. A day
of data seems enough to accurately determine the offsets, If a detector
is not working properly it may result in a completely wrong offset,
though there might not be any good data for which the offset would be
needed. However, if the bad detector is detector 2, it might be
difficult to determine the offsets for the other detectors.

Causes for changing offsets at some points:
- When swapping HiSPARC electronics (e.g. 501, 502, 504)
- When swapping PMTs or a PMT is not working well (e.g. 503, 505, 508)

"""
import csv
import os

from datetime import date

import tables

from numpy import nan

from artist import Plot

from sapphire.analysis.calibration import determine_detector_timing_offsets
from sapphire.clusters import Station
from sapphire.transformations.clock import datetime_to_gps
from sapphire.utils import pbar

DATA_PATH = '/Users/arne/Datastore/esd/'
STATIONS = [501, 502, 503, 504, 505, 506, 508, 509, 510, 1006]

O = (0, 0, 0)
STATION = Station(None, 0, O,
                  detectors=[(O, 'UD'), (O, 'UD'), (O, 'LR'), (O, 'LR')])
LIMITS = 15


def determine_offset(data, station):
    station_events = data.get_node('/station_%d' % station, 'events')
    offsets = determine_detector_timing_offsets(station_events, STATION)
    offsets = [round(o, 2) for o in offsets]
    return offsets


def plot_detector_offsets(offsets, type='month'):
    d1, d2, d3, d4 = zip(*offsets)
    x = range(len(d1))
    graph = Plot()
    graph.plot(x, d1, markstyle='mark size=.5pt')
    graph.plot(x, d2, markstyle='mark size=.5pt', linestyle='red')
    graph.plot(x, d3, markstyle='mark size=.5pt', linestyle='green')
    graph.plot(x, d4, markstyle='mark size=.5pt', linestyle='blue')
    graph.set_ylabel('$\Delta t$ [ns]')
    graph.set_xlabel('Date')
    graph.set_xlimits(0, max(x))
    graph.set_ylimits(-LIMITS, LIMITS)
    graph.save_as_pdf('detector_offset_drift_%s_%d' % (type, station))


if __name__ == '__main__':

    for station in pbar(STATIONS):
        # Determine offsets for first day of each month
        output = open('offsets_%d.tsv' % station, 'wb')
        csvwriter = csv.writer(output, delimiter='\t')
        offsets = []
        timestamps = []
        for y in range(2010, 2016):
            for m in range(1, 13):
                if y == 2015 and m >= 4:
                    continue
                timestamps.append(datetime_to_gps(date(y, m, 1)))
                path = os.path.join(DATA_PATH, str(y), str(m), '%d_%d_1.h5' % (y, m))
                with tables.open_file(path, 'r') as data:
                    offsets.append(determine_offset(data, station))
                csvwriter.writerow([timestamps[-1]] + offsets[-1])
        output.close()
        plot_detector_offsets(offsets, 'month')

        # Determine offsets for each day in one month
        offsets = []
        y = 2013
        m = 1
        for d in range(1, 32):
            path = os.path.join(DATA_PATH, str(y), str(m), '%d_%d_%d.h5' % (y, m, d))
            with tables.open_file(path, 'r') as data:
                offsets.append(determine_offset(data, station))
        plot_detector_offsets(offsets, 'daily')
