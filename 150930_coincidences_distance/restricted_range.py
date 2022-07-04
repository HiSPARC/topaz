from datetime import date
from itertools import combinations

import tables

from sapphire.transformations.clock import datetime_to_gps

from eventtime_ranges import get_timestamp_ranges, get_total_exposure


def modify_range(ts_range, start_ts):
    """Cut timestamp ranges to only include after a certain timestamp

    Only time ranges after start_ts are included, it start_ts is inside
    a range the start of that range is set to start_ts.

    """
    return [(ts1 if ts1 > start_ts else start_ts, ts2) for ts1, ts2 in ts_range if ts2 > start_ts]


def get_coin_count(s1, s2, start_ts):
    """Get number of coincidences after a given timestamp"""

    path = '/Users/arne/Datastore/pairs/%d_%d.h5' % (s1, s2)
    with tables.open_file(path, 'r') as data:
        coin = data.root.coincidences.coincidences
        return len(coin.get_where_list('timestamp >= start_ts'))


def coin_rate_since(start_ts=None):
    """Get coincidence rate since a given timestamp"""

    if start_ts is None:
        start_ts = datetime_to_gps(date(2015, 1, 1))

    for s1, s2 in combinations([7001, 7002, 7003], 2):
        ts12 = get_timestamp_ranges([s1, s2])
        mts12 = modify_range(ts12, start_ts)
        tot12 = get_total_exposure(mts12)
        n_coin = get_coin_count(s1, s2, start_ts)
        print(s1, s2, tot12, n_coin, n_coin / tot12, tot12 / n_coin)


def get_intervals(s1, s2):
    """Get times between concecutive coincidences"""

    path = '/Users/arne/Datastore/pairs/%d_%d.h5' % (s1, s2)
    with tables.open_file(path, 'r') as data:
        ts = data.root.coincidences.coincidences.col('ext_timestamp')
        intervals = ts[1:] - ts[:-1]
        return intervals


if __name__ == "__main__":
    coin_rate_since()
