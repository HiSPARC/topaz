from datetime import datetime as dt
import calendar

import tables
from hisparc.publicdb import download_data

from paths import paths
from testlist import get_tests


def download(storage, group, start, ended):
    """ Download data from the tijdtest stations

    This will download data in the given date range from both the swap and
    reference station into storage.

    """

    print 'tt_data: Downloading data for %s' % group
    download_data(storage, '/refr/' + group, 95, start, ended)
    download_data(storage, '/swap/' + group, 94, start, ended)


def check_downloaded(storage, group, start, ended):
    """ Check if any data already exists in group for the given date range

    This will simply look if there are any entries in the events table in the
    node 'group' that fall within the given date range (start-ended).

    If there is already data, it will return True, otherwise False

    """

    start = calendar.timegm(start)
    ended = calendar.timegm(ended)

    refr = storage.getNode('/refr/' + group + '/events')
    swap = storage.getNode('/swap/' + group + '/events')

    query = '(timestamp >= start) & (timestamp =< ended)'
    swap_inrange = swap.readWhere(query)
    refr_inrange = refr.readWhere(query)

    if len(swap_inrange) or len(refr_inrange):
        return True
    else:
        return False


def append_new(test=None):
    """ Add and download a new test to the storage

    Check if the data for test is already downloaded, if it is not add a new
    group for it and download the data into it.

    """

    added = "tt_data: No new data to be added"
    with tables.openFile(paths('tt_data'), 'a') as data:
        if test:
            try:
                data.getNode('/swap/' + test[0], 'events')
            except tables.NoSuchNodeError:
                download(data, test[0], dt(test[1]), dt(test[2]))
                added = "tt_data: Added new data"
        else:
            for test in get_tests(subset='ALL', unique=False):
                try:
                    data.getNode('/swap/' + test.group, 'events')
                except tables.NoSuchNodeError:
                    download(data, test.group, test.start, test.end)
                    added = "tt_data: Added new data"

    print added


def download_all():
    """ Download data for all tests in the testlist

    If a datafile exists, it will be overwritten

    """

    with tables.openFile(paths('tt_data'), 'w'):
        pass
    append_new()
    print 'tt_data: Downloaded entire Tijd Test'


if __name__ == '__main__':
    append_new()
