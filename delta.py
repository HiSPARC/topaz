import warnings
import tables
import itertools
from hisparc.analysis.coincidences import search_coincidences as search

from paths import paths
from testlist import get_tests


class DeltaVal(tables.IsDescription):

    ext_timestamp = tables.UInt64Col()  # integer (unsigned double-precision)
    delta = tables.FloatCol()           # float (double-precision)


def calculate(data, id):
    """ Calculate the deltas for a test

    The deltas are calculated by subtracting the timestamp of the reference
    from the timestamp of the swap. This means that in case of positive delta
    the swap was later than the reference.

    This returns a list of ext_timestamps and deltas.

    """
    coincidences, timestamps = search(data,
                                      ['/refr/t%d' % id, '/swap/t%d' % id],
                                      window=8000)
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


def store(id):
    """ Stores the calculated deltas and timestamps in storage

    """
    warnings.simplefilter('ignore', tables.NaturalNameWarning)

    print 'tt_delta: Storing deltas for test %s' % id
    with tables.open_file(paths('tt_data'), 'r') as data_file, \
         tables.open_file(paths('tt_delta'), 'a') as delta_file:
        table = delta_file.create_table('/t%d' % id, 'delta', DeltaVal,
                                       createparents=True)
        ext_timestamps, deltas = calculate(data_file, id)
        delta_row = table.row
        for ext_timestamp, delta in itertools.izip(ext_timestamps, deltas):
            delta_row['ext_timestamp'] = ext_timestamp
            delta_row['delta'] = delta
            delta_row.append()
        table.flush()

    return ext_timestamps, deltas


def append_new(id=None):
    """ Add new deltas to the storage

    """
    added = "tt_delta: No new deltas to be added"
    with tables.open_file(paths('tt_delta'), 'a') as delta_file:
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
    with tables.open_file(paths('tt_delta'), 'w'):
        pass
    append_new()
    print "tt_delta: Calculated deltas for entire Tijd Test"


def get(id, path=None):
    """ Get ext_timestamps and deltas from the storage

    """
    if not path:
        path = paths('tt_delta')

    if id in get_tests(part='id'):
        with tables.open_file(path, 'r') as delta_file:
            try:
                delta_table = delta_file.get_node('/t%d' % id, 'delta')
                ext_timestamps = [row['ext_timestamp'] for row in delta_table]
                deltas = [row['delta'] for row in delta_table]
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
    with tables.open_file(paths('tt_delta'), 'r') as delta_file:
        ids = [int(node._v_name[1:]) for node in delta_file.list_nodes('/')]
    ids.sort()

    return ids


def remove(id):
    with tables.open_file(paths('tt_delta'), 'a') as delta_file:
        try:
            delta_file.get_node('/t%d' % id, 'delta')
            delta_file.remove_node('/t%d' % id, recursive=True)
            print "tt_delta: Removed table /t%d" % id
        except tables.NoSuchNodeError:
            print "tt_delta: No such table"


if __name__ == '__main__':
    append_new()
