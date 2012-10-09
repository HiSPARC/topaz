from datetime import datetime as dt
import calendar

import tables
from hisparc.publicdb import download_data

from paths import paths
from testlist import get_tests


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

    refr = storage.getNode('/refr/t%d' % test.id + '/events')
    swap = storage.getNode('/swap/t%d' % test.id + '/events')

    query = '(timestamp >= start) & (timestamp =< end)'
    swap_inrange = swap.readWhere(query)
    refr_inrange = refr.readWhere(query)

    if len(swap_inrange) or len(refr_inrange):
        return True
    else:
        return False


def append_new(id=None):
    """ Add and download a new test to the storage

    Check if the data for test is already downloaded, if it is not add a new
    node for it and download the data into it.

    """
    added = "tt_data: No new data to be added"
    with tables.openFile(paths('tt_data'), 'a') as data:
        if id:
            try:
                data.getNode('/swap/t%d' % id, 'events')
            except tables.NoSuchNodeError:
                test = get_tests(id=id)
                download(data, test[0])
                added = "tt_data: Added new data"
        else:
            for test in get_tests(unique=False):
                try:
                    data.getNode('/swap/t%d' % test.id, 'events')
                except tables.NoSuchNodeError:
                    download(data, test)
                    added = "tt_data: Added new data"

    print added


def get(id=None):
    """

    """
    with tables.openFile(paths('tt_data'), 'a') as data:
        if id:
            try:
                node = eval('data.root.swap.t%d' % id)
            except tables.NoSuchNodeError:
                node = None
        else:
            node = []
            for test in get_tests(unique=False):
                try:
                    node.append(data.getNode('/swap/t%d' % test.id, 'events'))
                except tables.NoSuchNodeError:
                    node.append(None)

    return node


def download_all():
    """ Download data for all tests in the testlist

    If a datafile exists, it will be overwritten

    """
    with tables.openFile(paths('tt_data'), 'w'):
        pass
    append_new()
    print 'tt_data: Downloaded entire Tijd Test'


def remove(id):
    with tables.openFile(paths('tt_data'), 'a') as data:
        try:
            data.getNode('/swap/t%d' % id, 'delta')
            data.removeNode('/swap/t%d' % id, recursive=True)
            print "tt_data: Removed table /swap/t%d" % id
        except tables.NoSuchNodeError:
            print "tt_data: No such table in swap"
        try:
            data.getNode('/refr/t%d' % id, 'delta')
            data.removeNode('/refr/t%d' % id, recursive=True)
            print "tt_data: Removed table /refr/t%d" % id
        except tables.NoSuchNodeError:
            print "tt_data: No such table in refr"


if __name__ == '__main__':
    append_new()
