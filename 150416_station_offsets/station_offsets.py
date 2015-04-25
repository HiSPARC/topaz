"""Determine the change in station offsets over time

For various combinations of stations in compact clusters


- First determine dt once - use detector_offset from 150416_offset_drift

"""
import itertools
from datetime import datetime
from bisect import bisect_right
import csv

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

501 for Science Park stations, data starting at 2010/1.
"""

SPA_DATA = '/Users/arne/Datastore/esd_coincidences/sciencepark_n2_100101_150401.h5'
SPA_STAT = [501, 502, 503, 504, 505, 506, 508, 509, 510]
CLUSTER = HiSPARCStations(SPA_STAT)


class DeltaVal(tables.IsDescription):
    ext_timestamp = tables.UInt64Col()
    timestamp = tables.UInt32Col()
    nanoseconds = tables.UInt32Col()
    delta = tables.FloatCol()


def determine_time_differences(coin_events, ref_station, station, ref_d_off, d_off):
    """Determine the offsets between the stations."""
    dt = []
    ets = []
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
        ets.append((ref_ts))
    return ets, dt


def get_detector_offsets(station):
    offsets = genfromtxt('offsets_%d.csv' % station, delimiter='\t')
    return offsets


def get_active_detector_offsets(offsets, timestamp):
    idx = bisect_right(offsets[:, 0], timestamp, lo=0)
    if idx == 0:
        idx = 1
    return offsets[idx - 1][1:]


def write_offets(station, offsets):
    output = open('offsets_s%d.csv' % station, 'wb')
    csvwriter = csv.writer(output, delimiter='\t')
    for ts, offset in offsets:
        csvwriter.writerow([ts, offset])
    output.close()


def store_dt(station, ext_timestamps, deltats):
    with tables.open_file('dt.h5', 'a') as data:
        try:
            table = data.get_node('/s%d' % station)
        except tables.NoSuchNodeError:
            table = data.create_table('/', 's%d' % station, DeltaVal,
                                      createparents=True)
        for ets, deltat in zip(ext_timestamps, deltats):
            delta_row = table.row
            delta_row['ext_timestamp'] = ets
            delta_row['timestamp'] = int(ets) / int(1e9)
            delta_row['nanoseconds'] = int(ets) - ((int(ets) / int(1e9)) * int(1e9))
            delta_row['delta'] = deltat
            delta_row.append()
        table.flush()


def main(data):
    cq = CoincidenceQuery(data)
    ref_station = 501
    ref_detector_offsets = get_detector_offsets(ref_station)
    for station in pbar(SPA_STAT):
        offsets = []
        detector_offsets = get_detector_offsets(station)
        if station == ref_station:
            continue
        for dt0, dt1 in monthrange((2010, 1), (2015, 4)):
            coins = cq.all([station, ref_station], start=dt0, stop=dt1, iterator=True)
            coin_events = cq.events_from_stations(coins, [station, ref_station])
            ref_d_off = get_active_detector_offsets(ref_detector_offsets, dt0)
            d_off = get_active_detector_offsets(detector_offsets, dt0)
            ets, dt = determine_time_differences(coin_events, ref_station, station, ref_d_off, d_off)
            store_dt(station, ets, dt)
            if len(dt) < 100:
                continue
            s_off = determine_station_timing_offset(dt)
            offsets.append((dt0, s_off))
        write_offets(station, offsets)


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
