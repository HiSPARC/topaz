"""Determine the change in station offsets over time

For various combinations of stations in compact clusters

- First determine dt for each station pair coincidence once
- Use detector offsets from API

"""
import itertools
from datetime import datetime
from bisect import bisect_right
import csv
import os
import multiprocessing

from numpy import nan, isnan, arange, histogram, linspace, genfromtxt
from scipy.optimize import curve_fit
import tables

from artist import Plot

from sapphire.transformations.clock import datetime_to_gps
from sapphire import CoincidenceQuery, HiSPARCStations, Station
from sapphire.analysis.event_utils import station_arrival_time
from sapphire.analysis.calibration import determine_station_timing_offset
from sapphire.utils import pbar, ERR

"""
Reference stations

501 for Science Park stations, data starting at 2010/1.
"""

SPA_DATA = '/Users/arne/Datastore/esd_coincidences/sciencepark_n2_100101_150401.h5'
SPA_STAT = [501, 502, 503, 504, 505, 506, 508, 509, 510]
CLUSTER = HiSPARCStations(SPA_STAT)
DATA_PATH = '/Users/arne/Datastore/station_offsets/'


class DeltaVal(tables.IsDescription):
    ext_timestamp = tables.UInt64Col(pos=0)
    timestamp = tables.UInt32Col(pos=1)
    nanoseconds = tables.UInt32Col(pos=2)
    delta = tables.FloatCol(pos=3)


def determine_time_differences(coin_events, ref_station, station, ref_d_off, d_off):
    """Determine the arrival time differences between two stations."""
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
                                     ref_d_off(ref_ts / int(1e9)))
        t = station_arrival_time(events[id][1], ref_ts, [0, 1, 2, 3],
                                 d_off(ref_ts / int(1e9)))
        if isnan(t) or isnan(ref_t):
            continue
        dt.append(t - ref_t)
        ets.append((ref_ts))
    return ets, dt


def write_offets(station, ref_station, offsets):
    path = DATA_PATH + 'offsets_ref%d_s%d.tsv' % (ref_station, station)
    with open(path, 'wb') as output:
        csvwriter = csv.writer(output, delimiter='\t')
        csvwriter.writerows((ts, offset) for ts, offset in offsets)


def store_dt(ref_station, station, ext_timestamps, deltats):
    with tables.open_file(DATA_PATH + 'dt_ref%d_%d.h5' % (ref_station, station), 'a') as data:
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


def determine_dt_for_pair(stations):
    """Determine and store dt for a pair of stations

    :param ref_station: reference station number to use as refernece
    :param station: station number to determine the dt for

    """
    ref_station, station = stations
    with tables.open_file(SPA_DATA, 'r') as data:
        cq = CoincidenceQuery(data)
        ref_detector_offsets = Station(ref_station).detector_timing_offset
        detector_offsets = Station(station).detector_timing_offset
        for dt0, dt1 in monthrange((2010, 1), (2015, 4)):
            coins = cq.all([station, ref_station], start=dt0, stop=dt1, iterator=True)
            coin_events = cq.events_from_stations(coins, [station, ref_station])
            ets, dt = determine_time_differences(coin_events, ref_station, station,
                                                 ref_detector_offsets, detector_offsets)
            store_dt(ref_station, station, ets, dt)


def determine_dt():
    args = [(ref_station, station)
            for ref_station, station in itertools.permutations(SPA_STAT, 2)]
    worker_pool = multiprocessing.Pool()
    worker_pool.map(determine_dt_for_pair, args)
    worker_pool.close()
    worker_pool.join()


def determine_offsets():
    for ref_station, station in itertools.permutations(SPA_STAT, 2):
        with tables.open_file(DATA_PATH + 'dt_ref%d_%d.h5' % (ref_station, station), 'r') as data:
            table = data.get_node('/s%d' % station)
            offsets = []
            for dt0, dt1 in pbar(monthrange((2010, 1), (2015, 4)), length=63):
                dt = table.read_where('(timestamp >= dt0) & (timestamp < dt1)',
                                      field='delta')
                if len(dt) < 100:
                    s_off = nan
                else:
                    s_off = determine_station_timing_offset(dt)
                offsets.append((dt0, s_off))
            write_offets(station, ref_station, offsets)


def monthrange(start, stop):
    """Generator for datetime month ranges

    This is a very specific generator for datetime ranges. Based on
    start and stop values, it generates one month intervals.

    :param start: a year, month tuple
    :param stop: a year, month tuple
    :return: generator for start and end timestamps of one month intervals

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
    determine_dt()
    determine_offsets()
