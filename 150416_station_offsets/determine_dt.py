"""Determine the change in station offsets over time

For various combinations of stations in compact clusters

- First determine dt for each station pair coincidence once
- Use detector offsets from API

"""
import multiprocessing
import os

from datetime import datetime

import tables

from numpy import isnan

from sapphire import CoincidenceQuery, Station
from sapphire.analysis.event_utils import station_arrival_time
from sapphire.transformations.clock import datetime_to_gps

from station_distances import close_pairs_in_network

"""
Reference stations

501 for Science Park stations, data starting at 2010/1.
"""

PAIR_DATAPATH = '/Users/arne/Datastore/pairs/%d_%d.h5'

SPA_DATA = '/Users/arne/Datastore/esd_coincidences/sciencepark_n2_100101_150401.h5'
SPA_STAT = [501, 502, 503, 504, 505, 506, 508, 509, 510]
DATA_PATH = '/Users/arne/Datastore/station_offsets/'


class DeltaVal(tables.IsDescription):
    ext_timestamp = tables.UInt64Col(pos=0)
    timestamp = tables.UInt32Col(pos=1)
    nanoseconds = tables.UInt32Col(pos=2)
    delta = tables.FloatCol(pos=3)


def determine_time_differences(coin_events, ref_station, station, ref_d_off, d_off):
    """Determine the arrival time differences between two stations.

    :param coin_events: coincidence events.
    :param ref_station,station: station numbers.
    :param ref_d_off,d_off: `detector_timing_offset` methods of Station objects
        for the two stations, to retrieve applicable offsets.
    :return: extended timestamp of the first event and time difference,
             t - t_ref. Not corrected for altitude differences.

    """
    dt = []
    ets = []
    for events in coin_events:
        ref_ets = events[0][1]['ext_timestamp']
        ref_ts = ref_ets / int(1e9)
        # Filter for possibility of same station twice in coincidence
        if len(events) != 2:
            continue
        if events[0][0] == ref_station:
            ref_id = 0
            id = 1
        else:
            ref_id = 1
            id = 0
        ref_t = station_arrival_time(events[ref_id][1], ref_ets, [0, 1, 2, 3],
                                     ref_d_off(ref_ts))
        t = station_arrival_time(events[id][1], ref_ets, [0, 1, 2, 3],
                                 d_off(ref_ts))
        if isnan(t) or isnan(ref_t):
            continue
        dt.append(t - ref_t)
        ets.append(ref_ets)
    return ets, dt


def store_dt(ref_station, station, ext_timestamps, deltats):
    """Store determined dt values"""
    path = DATA_PATH + 'dt_ref%d_%d.h5' % (ref_station, station)
    with tables.open_file(path, 'a') as data:
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
    path = DATA_PATH + 'dt_ref%d_%d.h5' % stations
    if os.path.exists(path):
        print('dt data already exists for %d-%d' % stations)
        return

    ref_station, station = stations
    try:
        with tables.open_file(PAIR_DATAPATH % tuple(sorted(stations)), 'r') as data:
            cq = CoincidenceQuery(data)
            ref_detector_offsets = Station(ref_station).detector_timing_offset
            detector_offsets = Station(station).detector_timing_offset
            for dt0, dt1 in monthrange((2004, 1), (2015, 9)):
                coins = cq.all(stations, start=dt0, stop=dt1, iterator=True)
                coin_events = cq.events_from_stations(coins, stations)
                ets, dt = determine_time_differences(coin_events, ref_station, station,
                                                     ref_detector_offsets, detector_offsets)
                store_dt(ref_station, station, ets, dt)
    except Exception as e:
        print('Failed for %d, %d' % stations)
        print(e)
        return


def determine_dt():
    """Determine and store dt values using multiprocessing"""

    args = close_pairs_in_network(min=45, max=2e3)
    worker_pool = multiprocessing.Pool()
    worker_pool.map(determine_dt_for_pair, args)
    worker_pool.close()
    worker_pool.join()


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
