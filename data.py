from datetime import datetime as dt
import calendar

import tables
from sapphire.esd import download_data

from testlist import get_tests


DATA_PATH = '/Users/arne/Datastore/tijdtest/tijdtest_data.h5'


def download(storage, test):
    """ Download data from the tijdtest stations

    This will download data in the given date range from both the swap and
    reference station into storage.

    """
    print 'tt_data: Downloading data for test %d: %s' % (test.id, test.group)
    download_data(storage, '/refr/t%d' % test.id, 95, test.start, test.end)
    download_data(storage, '/swap/t%d' % test.id, 94, test.start, test.end)


def check_downloaded(storage, test):
    """ Check if any data already exists in node for the given date range

    This will simply look if there are any entries in the events table in the
    node 'id' that fall within the given date range (start-end).

    If there is already data, it will return True, otherwise False

    """
    start = calendar.timegm(test.start)
    ended = calendar.timegm(test.end)

    refr = storage.get_node('/refr/t%d' % test.id + '/events')
    swap = storage.get_node('/swap/t%d' % test.id + '/events')

    query = '(timestamp >= start) & (timestamp =< end)'
    swap_inrange = swap.readWhere(query)
    refr_inrange = refr.readWhere(query)

    if len(swap_inrange) or len(refr_inrange):
        return True
    else:
        return False


def append_new(id=None, path=None):
    """Download and add new test data to the storage

    Check if the data for test is already downloaded, if it is not add a new
    node for it and download the data into it.

    """
    added = "tt_data: No new data to be added"
    if not path:
        path = DATA_PATH
    with tables.open_file(path, 'a') as data_file:
        if id:
            try:
                data_file.get_node('/swap/t%d' % id, 'events')
            except tables.NoSuchNodeError:
                test = get_tests(id=id)
                download(data, test[0])
                added = "tt_data: Added new data"
        else:
            for test in get_tests(unique=False):
                try:
                    data_file.get_node('/swap/t%d' % test.id, 'events')
                except tables.NoSuchNodeError:
                    download(data, test)
                    added = "tt_data: Added new data"

    print added


def get(id=None, path=None):
    """ Get the events node of a certain id

    """
    if not path:
        path = DATA_PATH

    with tables.open_file(path, 'a') as data_file:
        if id:
            try:
                node = data_file.get_node('/swap/t%d' % id, 'events')
            except tables.NoSuchNodeError:
                node = None
        else:
            node = []
            for test in get_tests(unique=False):
                try:
                    node.append(data_file.get_node('/swap/t%d' % test.id,
                                'events'))
                except tables.NoSuchNodeError:
                    node.append(None)

    return node


def get_ids(path=None):
    """ Get list of all test ids in the data file

    """
    if not path:
        path = DATA_PATH

    with tables.open_file(path, 'r') as data_file:
        ids_swap = [int(node._v_name[1:])
                    for node in data_file.list_nodes('/swap/')]
        ids_refr = [int(node._v_name[1:])
                    for node in data_file.list_nodes('/refr/')]
    ids_swap.sort()
    ids_refr.sort()

    return (ids_swap, ids_refr)


def download_all(path=None):
    """ Download data for all tests in the testlist

    NOTE: If a datafile already exists, it will be overwritten

    """
    if not path:
        path = DATA_PATH

    with tables.open_file(path, 'w'):
        pass
    append_new()
    print 'tt_data: Downloaded entire Tijd Test'


def remove(id, path=None):
    """ Remove nodes with downloaded data for given ids

    """
    if not path:
        path = DATA_PATH

    with tables.openFile(path, 'a') as data_file:
        try:
            data_file.get_node('/swap/t%d' % id, 'events')
            data_file.remove_node('/swap/t%d' % id, recursive=True)
            print "tt_data: Removed table /swap/t%d" % id
        except tables.NoSuchNodeError:
            print "tt_data: No such table in swap"
        try:
            data_file.get_node('/refr/t%d' % id, 'events')
            data_file.remove_node('/refr/t%d' % id, recursive=True)
            print "tt_data: Removed table /refr/t%d" % id
        except tables.NoSuchNodeError:
            print "tt_data: No such table in refr"


if __name__ == '__main__':
    append_new()
