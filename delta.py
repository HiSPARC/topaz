import warnings
import tables
import itertools
from hisparc.analysis.coincidences import search_coincidences as search

from paths import paths
from testlist import get_tests


class DeltaVal(tables.IsDescription):

    ext_timestamp = tables.UInt64Col()  # integer (unsigned double-precision)
    delta = tables.FloatCol()           # float (double-precision)


def calculate(data, group):
    """ Calculate the deltas for a test

    The deltas are calculated by subtracting the timestamp of the reference
    from the timestamp of the swap. This means that in case of positive delta
    the swap was later than the reference.

    This returns a list of ext_timestamps and deltas.

    """

    coincidences, timestamps = search(data,
                                      ['/refr/' + group, '/swap/' + group],
                                      window=400)
    deltas = []
    ext_timestamps = []

    for c in coincidences:
        t0 = long(timestamps[c[0]][0])
        station0 = timestamps[c[0]][1]
        t1 = long(timestamps[c[1]][0])
        station1 = timestamps[c[1]][1]
        # swap - refr
        if station0 == 0 and station1 == 1:
            deltas.append(t1 - t0)
            ext_timestamps.append(t0)
        elif station0 == 1 and station1 == 0:
            deltas.append(t0 - t1)
            ext_timestamps.append(t1)

    return ext_timestamps, deltas


def store(group):
    """ Stores the calculated deltas and timestamps in storage

    """

    warnings.simplefilter('ignore', tables.NaturalNameWarning)

    print 'tt_delta: Storing deltas for %s' % group
    with tables.openFile(paths('tt_data'), 'r') as data, \
         tables.openFile(paths('tt_delta'), 'a') as deltas:
        table = deltas.createTable("/" + group, 'delta', DeltaVal,
                                   createparents=True)
        ext_timestamps, deltas = calculate(data, group)
        delta_row = table.row
        for ext_timestamp, delta in itertools.izip(ext_timestamps, deltas):
            delta_row['ext_timestamp'] = ext_timestamp
            delta_row['delta'] = delta
            delta_row.append()
        table.flush()

    return ext_timestamps, deltas


def append_new(group=None):
    """ Add new deltas to the storage

    """

    added = "tt_delta: No new deltas to be added"
    with tables.openFile(paths('tt_delta'), 'a') as deltas:
        if group:
            try:
                deltas.getNode("/" + group, 'delta')
            except tables.NoSuchNodeError:
                store(group)
                added = "tt_delta: Added new deltas"
        else:
            for group in get_tests(subset='ALL', part="group", unique=True):
                try:
                    deltas.getNode("/" + group, 'delta')
                except tables.NoSuchNodeError:
                    store(group)
                    added = "tt_delta: Added new deltas"

    print added


def store_all():
    """" Get the average delta per test for all tests

    """

    with tables.openFile(paths('tt_delta'), 'w'):
        pass
    append_new()
    print "tt_delta: Calculated deltas for entire Tijd Test"


def get(group):
    """ Get ext_timestamps and deltas from the storage

    """

    if group in get_tests(subset='ALL', part='group'):
        with tables.openFile(paths('tt_delta'), 'r') as delta_data:
            try:
                delta_table = delta_data.getNode("/" + group, 'delta')
                ext_timestamps = [row['ext_timestamp'] for row in delta_table]
                deltas = [row['delta'] for row in delta_table]
            except tables.NoSuchNodeError:
                ext_timestamps, deltas = store(group)
    else:
        ext_timestamps = []
        deltas = []
        print "tt_delta: No such test"

    return ext_timestamps, deltas


if __name__ == '__main__':
    append_new()
