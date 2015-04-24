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
from datetime import date
import csv
import calendar

from artist import Plot
from numpy import nan, genfromtxt
from sapphire.api import Station
from sapphire.transformations.clock import gps_to_datetime, datetime_to_gps

STATIONS = [502, 503, 504, 505, 506, 508, 509]


def get_detector_offsets(station):
    offsets = genfromtxt('offsets_%d.csv' % station, delimiter='\t',
                         names=('timestamp', 'd0', 'd1', 'd2', 'd3'))
    return offsets


def get_station_offsets(station):
    offsets = genfromtxt('offsets_s%d.csv' % station, delimiter='\t',
                         names=('station', 'timestamp', 'n', 'offset'))
    return offsets


def get_n_events(station):
    n = genfromtxt('n_month_%d.csv' % station, delimiter='\t',
                   names=('timestamp', 'n'))
    return n


def save_n_events_month(station):
    s = Station(station)
    output = open('n_month_%d.csv' % station, 'wb')
    csvwriter = csv.writer(output, delimiter='\t')
    for y in range(2010, 2015):
        for m in range(1, 13):
            n = s.n_events(y, m) / float(calendar.monthrange(y, m)[1])
            t = datetime_to_gps(date(y, m, 1))
            csvwriter.writerow([t, n])
    output.close()


def save_n_events(station):
    s = Station(station)
    output = open('n_%d.csv' % station, 'wb')
    csvwriter = csv.writer(output, delimiter='\t')
    for y in range(2010, 2015):
        for m in range(1, 13):
            for d in range(1, calendar.monthrange(y, m)[1] + 1):
                n = s.n_events(y, m, d)
                t = datetime_to_gps(date(y, m, d))
                csvwriter.writerow([t, n])
    output.close()


if __name__ == '__main__':

#     save_n_events_month(501)
#     for station in STATIONS:
#         save_n_events_month(station)

    ref_s = Station(501)
    ref_gps = ref_s.gps_locations
    ref_voltages = ref_s.voltages
    ref_n = get_n_events(501)

    for station in STATIONS:
        s = Station(station)
        voltages = s.voltages
        gps = s.gps_locations
        # Determine offsets for first day of each month
        d_off = get_detector_offsets(station)
        s_off = get_station_offsets(station)
        n = get_n_events(station)

        graph = Plot()
        graph.scatter(ref_gps['timestamp'], [95] * len(ref_gps), mark='square', markstyle='purple,mark size=.5pt')
        graph.scatter(ref_voltages['timestamp'], [90] * len(ref_voltages), mark='triangle', markstyle='purple,mark size=.5pt')
        graph.scatter(gps['timestamp'], [85] * len(gps), mark='square', markstyle='gray,mark size=.5pt')
        graph.scatter(voltages['timestamp'], [80] * len(voltages), mark='triangle', markstyle='gray,mark size=.5pt')
#         graph.plot(ref_n['timestamp'], -ref_n['n'] / 1000, mark=None, use_steps=True, linestyle='gray')
#         graph.plot(n['timestamp'], n['n'] / 1000, mark=None, use_steps=True)
        graph.shade_region(n['timestamp'], -ref_n['n'] / 1000, n['n'] / 1000)
        graph.plot(d_off['timestamp'], d_off['d0'], markstyle='mark size=.5pt')
        graph.plot(d_off['timestamp'], d_off['d2'], markstyle='mark size=.5pt', linestyle='green')
        graph.plot(d_off['timestamp'], d_off['d3'], markstyle='mark size=.5pt', linestyle='blue')
        graph.plot(s_off['timestamp'], s_off['offset'], mark='*', markstyle='mark size=1pt', linestyle='red')
        graph.set_ylabel('$\Delta t$ [ns]')
        graph.set_xlabel('Date')
        graph.set_xlimits(1.25e9, 1.45e9)
        graph.set_ylimits(-100, 100)
        graph.save_as_pdf('offset_drift_months_%d' % station)
