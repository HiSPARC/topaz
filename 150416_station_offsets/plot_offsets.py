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
from artist import Plot
from numpy import nan, genfromtxt

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



if __name__ == '__main__':

    for station in STATIONS:
        # Determine offsets for first day of each month
        d_off = get_detector_offsets(station)
        s_off = get_station_offsets(station)

        graph = Plot()
        graph.plot(d_off['timestamp'], d_off['d0'], markstyle='mark size=.5pt')
        graph.plot(d_off['timestamp'], d_off['d2'], markstyle='mark size=.5pt', linestyle='green')
        graph.plot(d_off['timestamp'], d_off['d3'], markstyle='mark size=.5pt', linestyle='blue')
        graph.plot(s_off['timestamp'], s_off['offset'], mark='*', markstyle='mark size=1pt', linestyle='red')
        graph.set_ylabel('$\Delta t$ [ns]')
        graph.set_xlabel('Date')
#         graph.set_xlimits(0, max(x))
        graph.set_ylimits(-100, 100)
        graph.save_as_pdf('offset_drift_months_%d' % station)
