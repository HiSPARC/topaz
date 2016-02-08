"""Determine detector offset drift over time

This determines the detector offsets for several stations on various dates.

The offsets seems fairly constant over time, within a nanosecond. A day
of data seems enough to accurately determine the offsets, If a detector
is not working properly it may result in a completely wrong offset,
though there might not be any good data for which the offset would be
needed. However, if the bad detector is detector 2, it might be
difficult to determine the offsets for the other detectors.

Causes for changing offsets at some points:
- Use a temporary GPS with bad view of the sky (501)
- When swapping HiSPARC electronics (e.g. 501, 502, 504)
- When swapping PMTs or a PMT is not working well (e.g. 503, 505, 508)

"""
import itertools
from datetime import date
import csv
import calendar
from glob import glob
import re

from artist import Plot
from numpy import nan, genfromtxt, histogram, arange

from sapphire.api import Station
from sapphire.transformations.clock import gps_to_datetime, datetime_to_gps


STATIONS = [501, 502, 503, 504, 505, 506, 508, 509, 510]
OFF_DATAPATH_GLOB = '/Users/arne/Datastore/station_offsets/offsets_ref*_s*.tsv'
DATA_PATH = '/Users/arne/Datastore/station_offsets/offsets_ref%d_s%d.tsv'


def get_available_station_pairs():
    paths = glob(OFF_DATAPATH_GLOB)
    pairs = [(int(s1), int(s2))
             for s1, s2 in [re.findall(r'\d+', path)
              for path in paths]]
    return pairs


def get_station_offsets(ref_station, station):
    offsets = genfromtxt(DATA_PATH  % (ref_station, station), delimiter='\t',
                         names=('timestamp', 'offset'))
    return offsets


def plot_offset_timeline(ref_station, station):
    ref_s = Station(ref_station)
    s = Station(station)
#         ref_gps = ref_s.gps_locations
#         ref_voltages = ref_s.voltages
#         ref_n = get_n_events(ref_station)
#         gps = s.gps_locations
#         voltages = s.voltages
#         n = get_n_events(station)
    # Determine offsets for first day of each month
#         d_off = s.detector_timing_offsets
    s_off = get_station_offsets(ref_station, station)
    graph = Plot(width=r'.6\textwidth')
#         graph.scatter(ref_gps['timestamp'], [95] * len(ref_gps), mark='square', markstyle='purple,mark size=.5pt')
#         graph.scatter(ref_voltages['timestamp'], [90] * len(ref_voltages), mark='triangle', markstyle='purple,mark size=.5pt')
#         graph.scatter(gps['timestamp'], [85] * len(gps), mark='square', markstyle='gray,mark size=.5pt')
#         graph.scatter(voltages['timestamp'], [80] * len(voltages), mark='triangle', markstyle='gray,mark size=.5pt')
#         graph.shade_region(n['timestamp'], -ref_n['n'] / 1000, n['n'] / 1000, color='lightgray,const plot')
#         graph.plot(d_off['timestamp'], d_off['d0'], markstyle='mark size=.5pt')
#         graph.plot(d_off['timestamp'], d_off['d2'], markstyle='mark size=.5pt', linestyle='green')
#         graph.plot(d_off['timestamp'], d_off['d3'], markstyle='mark size=.5pt', linestyle='blue')
    graph.plot(s_off['timestamp'], s_off['offset'], mark='*',
               markstyle='mark size=1.25pt', linestyle=None)
    graph.set_ylabel('$\Delta t$ [ns]')
    graph.set_xlabel('Date')
    graph.set_xticks([datetime_to_gps(date(y, 1, 1)) for y in range(2010, 2016)])
    graph.set_xtick_labels(['%d' % y for y in range(2010, 2016)])
    graph.set_xlimits(1.25e9, 1.45e9)
    graph.set_ylimits(-150, 150)
    graph.save_as_pdf('plots/offsets_ref%d_%d' %
                      (ref_station, station))

#     plot = Plot(width=r'.6\textwidth')
#     plot.histogram(*histogram(s_off['offset'], bins=arange(-80, 80, 5)))
#     plot.set_xlabel('$\Delta t$ [ns]')
#     plot.set_ylabel('Counts')
#     plot.set_xlimits(-80, 80)
#     plot.set_ylimits(min=0)
#     plot.save_as_pdf('plots/offsets_ref%d_%d_dist_r' %
#                       (ref_station, station))


if __name__ == '__main__':
    for ref_station, station in get_available_station_pairs():
        plot_offset_timeline(ref_station, station)
