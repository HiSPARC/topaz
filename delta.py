import warnings
import tables
import itertools
from sapphire.analysis.coincidences import CoincidencesESD

from helper import (nanoseconds_from_ext_timestamp,
                    timestamps_from_ext_timestamp)
from testlist import get_tests
from data import DATA_PATH


DELTA_DATA =  '/Users/arne/Datastore/tijdtest/tijdtest_delta.h5'


class DeltaVal(tables.IsDescription):

    ext_timestamp = tables.UInt64Col()
    timestamp = tables.UInt32Col()
    nanoseconds = tables.UInt32Col()
    delta = tables.FloatCol()


def calculate(data, id):
    """ Calculate the deltas for a test

    The deltas are calculated by subtracting the timestamp of the reference
    from the timestamp of the swap. This means that in case of positive delta
    the swap was later than the reference.

    dt = t_swap - t_refr

    This returns a list of ext_timestamps and deltas. The ext_timestamps
    are those of the reference.

    """
    coin = CoincidencesESD(data, None, ['/refr/t%d' % id, '/swap/t%d' % id])
    coin.search_coincidences(window=300)

    coincidences = coin._src_c_index
    timestamps = coin._src_timestamps

    deltas = []
    ext_timestamps = []

    for c in coincidences:
        t0 = int(timestamps[c[0]][0])
        station0 = timestamps[c[0]][1]
        t1 = int(timestamps[c[1]][0])
        station1 = timestamps[c[1]][1]
        # swap - refr
        if station0 == 0 and station1 == 1:
            deltas.append(t1 - t0)
            ext_timestamps.append(t0)
        elif station0 == 1 and station1 == 0:
            deltas.append(t0 - t1)
            ext_timestamps.append(t1)

    return ext_timestamps, deltas


def store(id):
    """ Stores the calculated deltas and timestamps in storage

    """
    warnings.simplefilter('ignore', tables.NaturalNameWarning)

    print 'tt_delta: Storing deltas for test %s' % id
    with tables.open_file(DATA_PATH, 'r') as data_file, \
         tables.open_file(DELTA_DATA, 'a') as delta_file:
        table = delta_file.create_table('/t%d' % id, 'delta', DeltaVal,
                                        createparents=True)
        ext_timestamps, deltas = calculate(data_file, id)
        timestamps = timestamps_from_ext_timestamp(ext_timestamps)
        nanoseconds = nanoseconds_from_ext_timestamp(ext_timestamps)
        delta_row = table.row
        for ext_ts, ts, ns, delta in itertools.izip(ext_timestamps, timestamps,
                                                    nanoseconds, deltas):
            delta_row['ext_timestamp'] = ext_ts
            delta_row['timestamp'] = ts
            delta_row['nanoseconds'] = ns
            delta_row['delta'] = delta
            delta_row.append()
        table.flush()

    return ext_timestamps, deltas


def append_new(id=None):
    """ Add new deltas to the storage

    """
    added = "tt_delta: No new deltas to be added"
    with tables.open_file(DELTA_DATA, 'a') as delta_file:
        if id:
            try:
                delta_file.get_node('/t%d' % id, 'delta')
            except tables.NoSuchNodeError:
                store(id)
                added = "tt_delta: Added new deltas"
        else:
            for id in get_tests(part="id", unique=True):
                try:
                    delta_file.get_node('/t%d' % id, 'delta')
                except tables.NoSuchNodeError:
                    store(id)
                    added = "tt_delta: Added new deltas"

    print added


def store_all():
    """" Calculate and store the deltas for all tests

    """
    with tables.open_file(DELTA_DATA, 'w'):
        pass
    append_new()
    print "tt_delta: Calculated deltas for entire Tijd Test"


def get(id, path=None):
    """ Get ext_timestamps and deltas from the storage

    """
    if not path:
        path = DELTA_DATA

    if id in get_tests(part='id'):
        with tables.open_file(path, 'r') as delta_file:
            try:
                delta_table = delta_file.get_node('/t%d' % id, 'delta')
                ext_timestamps = delta_table.col('ext_timestamp')
                deltas = delta_table.col('delta')
            except tables.NoSuchNodeError:
                ext_timestamps, deltas = store(id)
    else:
        ext_timestamps = []
        deltas = []
        print "tt_delta: No such test"

    return ext_timestamps, deltas


def get_ids():
    """ Get list of all test ids in the data file

    """
    with tables.open_file(DELTA_DATA, 'r') as delta_file:
        ids = [int(node._v_name[1:]) for node in delta_file.list_nodes('/')]
    ids.sort()

    return ids


def remove(id):
    with tables.open_file(DELTA_DATA, 'a') as delta_file:
        try:
            delta_file.get_node('/t%d' % id, 'delta')
            delta_file.remove_node('/t%d' % id, recursive=True)
            print "tt_delta: Removed table /t%d" % id
        except tables.NoSuchNodeError:
            print "tt_delta: No such table"


if __name__ == '__main__':
    append_new()
