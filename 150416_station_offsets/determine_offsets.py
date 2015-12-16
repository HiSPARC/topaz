"""Determine the change in station offsets over time

For various combinations of stations in compact clusters

- First determine dt for each station pair coincidence once
- Use detector offsets from API

"""
import itertools
from datetime import datetime, timedelta
import csv
import multiprocessing

from numpy import nan, log10
import tables

from sapphire import HiSPARCStations
from sapphire.analysis.calibration import determine_station_timing_offset
from sapphire.transformations.clock import datetime_to_gps

"""
Reference stations

501 for Science Park stations, data starting at 2010/1.
"""

SPA_STAT = [501, 502, 503, 504, 505, 506, 508, 509, 510]
CLUSTER = HiSPARCStations(SPA_STAT)
DATA_PATH = '/Users/arne/Datastore/station_offsets/'
DAYS = 10


def determine_offsets():
    args = [(ref_station, station)
            for ref_station, station in itertools.permutations(SPA_STAT, 2)]
    worker_pool = multiprocessing.Pool()
    worker_pool.map(determine_offsets_for_pair, args)
    worker_pool.close()
    worker_pool.join()


def determine_offsets_for_pair(stations):
    ref_station, station = stations
    path = DATA_PATH + 'dt_ref%d_%d.h5' % (ref_station, station)
    with tables.open_file(path, 'r') as data:
        table = data.get_node('/s%d' % station)
        offsets = []
        start = datetime(2010, 1, 1)
        end = datetime(2015, 4, 1)
        for dt0 in (start + timedelta(days=x)
                    for x in xrange(0, (end - start).days, 10)):
            ts0 = datetime_to_gps(dt0)
            CLUSTER.set_timestamp(ts0)
            # dz is z - z_ref
            r, _, dz = CLUSTER.calc_rphiz_for_stations(SPA_STAT.index(ref_station),
                                                       SPA_STAT.index(station))
            ts1 = datetime_to_gps(dt0 + timedelta(days=max(int(r ** 1.12 / DAYS), 7)))
            dt = table.read_where('(timestamp >= ts0) & (timestamp < ts1)',
                                  field='delta')
            if len(dt) < 100:
                s_off = nan
            else:
                s_off = determine_station_timing_offset(dt, dz)
            offsets.append((ts0, s_off))
        write_offets(station, ref_station, offsets)


def write_offets(station, ref_station, offsets):
    path = DATA_PATH + 'offsets_ref%d_s%d.tsv' % (ref_station, station)
    with open(path, 'wb') as output:
        csvwriter = csv.writer(output, delimiter='\t')
        csvwriter.writerows((ts, offset) for ts, offset in offsets)


if __name__ == '__main__':
    determine_offsets()
