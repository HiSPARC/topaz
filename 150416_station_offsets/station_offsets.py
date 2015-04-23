"""Determine the change in station offsets over time

For various combinations of stations in compact clusters


- First determine dt once - use detector_offset from 150416_offset_drift

"""
import itertools
from datetime import datetime
from bisect import bisect_right

from numpy import nan, isnan, arange, histogram, linspace, genfromtxt
from scipy.optimize import curve_fit
import tables

from sapphire.transformations.clock import datetime_to_gps
from sapphire.analysis.coincidence_queries import CoincidenceQuery
from sapphire.analysis.event_utils import station_arrival_time
from sapphire.analysis.calibration import (determine_station_timing_offset,
                                           determine_detector_timing_offsets)
from sapphire.utils import pbar, ERR
from sapphire.clusters import HiSPARCStations
from artist import Plot


"""
Reference stations

102 for Zaanlands stations, data starting at 2012/6.
501 for Science Park stations, data starting at 2010/1.
7001 for Twente University stations, data starting at 2011/8.
8001 for Eindhoven University stations, data starting at 2011/10.
"""

SPA_DATA = '/Users/arne/Datastore/esd_coincidences/sciencepark_n2_100101_150401.h5'
# ZAA_DATA = '/Users/arne/Datastore/esd_coincidences/zaanlands_n2_120601_140801.h5'
# TWE_DATA = '/Users/arne/Datastore/esd_coincidences/twente_n2_110801_140801.h5'
# ALP_DATA = '/Users/arne/Datastore/esd_coincidences/alphen_n2_101201_140801.h5'

# SPA_STAT = [501, 502, 503, 504, 505, 506, 508, 509, 510]
SPA_STAT = [501, 502, 503, 504, 505, 506, 508, 509]
ZAA_STAT = [102, 104, 105]
TWE_STAT = [7001, 7002, 7003]
ALP_STAT = [8001, 8004, 8008, 8009]

COLORS = ['black', 'green', 'blue', 'teal', 'orange', 'purple', 'cyan', 'red',
          'gray']

CLUSTER = HiSPARCStations(SPA_STAT + ZAA_STAT + TWE_STAT + ALP_STAT)

OFFSETS = {102: [-3.1832, 0.0000, 0.0000, 0.0000],
           104: [-1.5925, -5.0107, 0.0000, 0.0000],
           105: [-14.1325, -10.9451, 0.0000, 0.0000],
           501: [-1.10338, 0.0000, 5.35711, 3.1686],
           502: [-8.11711, -8.5528, -8.72451, -9.3388],
           503: [-22.9796, -26.6098, -22.7522, -21.8723],
           504: [-15.4349, -15.2281, -15.1860, -16.5545],
           505: [-21.6035, -21.3060, -19.6826, -25.5366],
           506: [-20.2320, -15.8309, -14.1818, -14.1548],
           508: [-26.2402, -24.9859, -24.0131, -23.2882],
           509: [-24.8369, -23.0218, -20.6011, -24.3757],
           7001: [4.5735, 0.0000, 0.0000, 0.0000],
           7002: [45.0696, 47.8311, 0.0000, 0.0000],
           7003: [-2.2674, -4.9578, 0.0000, 0.0000],
           8001: [2.5733, 0.0000, 0.0000, 0.0000],
           8004: [-39.3838, -36.1131, 0.0000, 0.0000],
           8008: [57.3990, 58.1135, 0.0000, 0.0000],
           8009: [-20.3489, -16.9938, 0.0000, 0.0000]}


def determine_time_differences(coin_events, ref_station, station, ref_d_off, d_off):
    """Determine the offsets between the stations."""
    dt = []
    for events in coin_events:
        ref_ts = events[0][1]['ext_timestamp']
        # Filter for possibility of same station twice in coincidence
        if len(events) is not 2:
            continue
        if events[0][0] == ref_station:
            ref_id = 0
            id = 1
        else:
            ref_id = 1
            id = 0
        ref_t = station_arrival_time(events[ref_id][1], ref_ts, [0, 1, 2, 3],
                                     ref_d_off)
        t = station_arrival_time(events[id][1], ref_ts, [0, 1, 2, 3], d_off)
        if isnan(t) or isnan(ref_t):
            continue
        dt.append(t - ref_t)
    return dt


def get_detector_offsets(station):
    offsets = genfromtxt('offsets_%d.csv' % station, delimiter='\t')
    return offsets


def get_active_detector_offsets(offsets, timestamp):
    idx = bisect_right(offsets[:,0], timestamp, lo=0)
    if idx == 0:
        idx = 1
    return offsets[idx - 1][1:]


def main(data):
    offsets = {}
    cq = CoincidenceQuery(data)
    ref_station = 501
    ref_detector_offsets = get_detector_offsets(ref_station)
    for station in SPA_STAT:
        detector_offsets = get_detector_offsets(station)
        if station == ref_station:
            continue
        o = []
        for dt0, dt1 in monthrange((2010, 1), (2015, 1)):
            coins = cq.all([station, ref_station], start=dt0, stop=dt1, iterator=True)
            coin_events = cq.events_from_stations(coins, [station, ref_station])
            ref_d_off = get_active_detector_offsets(ref_detector_offsets, dt0)
            d_off = get_active_detector_offsets(detector_offsets, dt0)
            dt = determine_time_differences(coin_events, ref_station, station, ref_d_off, d_off)
            if len(dt) < 100:
                print station, dt0, len(dt), 'To few events'
                continue
            s_off = determine_station_timing_offset(dt)
            print station, dt0, len(dt), s_off
            o.append(s_off)
        offsets[station] = o
    print offsets

def monthrange(start, stop):
    """Generator for datetime month ranges

    This is a very specific generator for datetime ranges. Based on
    start and stop values, it generates one month intervals.

    :param start: a year, month tuple
    :param stop: a year, month tuple

    The stop is the last end of the range.

    """
    startdt = datetime(start[0], start[1], 1)
    stopdt = datetime(stop[0], stop[1], 1)

    if stopdt < startdt:
        return

    if start == stop:
        yield (datetime_to_gps(datetime(start[0], start[1], 1)),
               datetime_to_gps(datetime(start[0], start[1] + 1, 1)))
        return
    else:
        current_year, current_month = start

        while (current_year, current_month) != stop:
            if current_month < 12:
                next_year = current_year
                next_month = current_month + 1
            else:
                next_year = current_year + 1
                next_month = 1
            yield (datetime_to_gps(datetime(current_year, current_month, 1)),
                   datetime_to_gps(datetime(next_year, next_month, 1)))

            current_year = next_year
            current_month = next_month
        return


if __name__ == '__main__':
    with tables.open_file(SPA_DATA, 'r') as data:
        main(data)
