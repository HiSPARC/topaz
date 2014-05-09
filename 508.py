import warnings
import itertools

import tables
import numpy as np
import pylab as plt

from paths import paths
import plot_pref as pp
from hisparc import publicdb
from hisparc.analysis.coincidences import search_coincidences as search

from testlist import Tijdtest
import data
import delta
from delta import DeltaVal

from testlist import get_tests
from delta import get
from helper import nanoseconds_from_ext_timestamp, timestamps_from_ext_timestamp


def test_log_508():
    """ A log of davids tests

    In this program is a list of all available tests from the tijdtest project.

    """
    tests = (
        ( 1 , '317', '501', '',   (2013, 6,19, 13, 0), (2013, 6,29, 23, 0), ''),
        ( 2 , '317', '502', '',   (2013, 6,19, 13, 0), (2013, 6,29, 23, 0), ''),
        ( 3 , '317', '505', '',   (2013, 6,19, 13, 0), (2013, 6,29, 23, 0), ''),
        ( 4 , '317', '506', '',   (2013, 6,19, 13, 0), (2013, 6,29, 23, 0), ''),
        ( 5 , '317', '501', '',   (2013, 6,28,  0, 0), (2013, 6,29, 23, 0), ''),
        ( 6 , '317', '502', '',   (2013, 6,28,  0, 0), (2013, 6,29, 23, 0), ''),
        ( 7 , '317', '505', '',   (2013, 6,28,  0, 0), (2013, 6,29, 23, 0), ''),
        ( 8 , '317', '506', '',   (2013, 6,28,  0, 0), (2013, 6,29, 23, 0), ''))

    test_all = [Tijdtest(*test) for test in tests]

    return test_all


def download(storage, test):
    """ Download data from the tijdtest stations

    This will download data in the given date range from both the swap and
    reference station into storage.

    """
    print 'tt_data: Downloading data for test %d: %s' % (test.id, test.group)
    publicdb.download_data(storage, '/refr/t%d' % test.id, 508, test.start, test.end)
    publicdb.download_data(storage, '/swap/t%d' % test.id, int(test.gps), test.start, test.end)


def download_data():
    tests = test_log_508()
    with tables.openFile(paths('temp'), 'w') as storage:
        for test in tests:
            download(storage, test)


def calculate_delta():
    # Difference in length of cables to boxes in nano seconds, (swap - refr)
    tests = test_log_508()
    with tables.openFile(paths('temp'), 'r') as data_file, \
         tables.openFile(paths('temp2'), 'w') as delta_file:
        for test in tests:
            table = delta_file.createTable('/t%d' % test.id, 'delta',
                                           delta.DeltaVal, createparents=True)
            ext_timestamps, deltas = calculate(data_file, test.id)
            delta_row = table.row

            for ext_timestamp, delta_val in itertools.izip(ext_timestamps,
                                                           deltas):
                delta_row['ext_timestamp'] = ext_timestamp
                delta_row['delta'] = delta_val
                delta_row.append()
            table.flush()


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


def print_delta_results():
    """ Prints the average delta, the standard deviation and length in days

    """
    tests = test_log_508()

    for test in tests:
        with tables.openFile(paths('temp2'), 'r') as delta_file:
            delta_table = delta_file.getNode('/t%d' % test.id, 'delta')
            ext_timestamps = [row['ext_timestamp'] for row in delta_table]
            deltas = [row['delta'] for row in delta_table]
        print "    % 3d  %s  % 7.2f  % 6.2f  % 4.2f" % (
                test.id, test.group.ljust(13),
                round(np.average(deltas), 2), round(np.std(deltas), 2),
                (max(ext_timestamps) - min(ext_timestamps)) / 864e11)


def plot_delta_test():
    """ Plot the delta with std

    """
    #Define Bins
    low = -2000
    high = 2000
    bin_size = 10  # 2.5*n?
    bins = np.arange(low - .5 * bin_size, high + bin_size, bin_size)

    tests = test_log_508()

    #Begin Figure
    with pp.PlotFig(texttex=True, kind='pdf') as plot:
        for test in tests:
            with tables.openFile(paths('temp2'), 'r') as delta_file:
                delta_table = delta_file.getNode('/t%d' % test.id, 'delta')
                ext_timestamps = [row['ext_timestamp'] for row in delta_table]
                deltas = [row['delta'] for row in delta_table]
                plot.axe.hist(deltas, bins, normed=1, histtype='step', alpha=0.9,
                              label=test.gps)
        plt.title = 'Time difference coincidences 508'
        plt.xlabel(r'$\Delta$ t (station - 508) [ns]')
        plt.ylabel(r'p')
        plt.xlim(-2000, 2000)
        plt.ylim(0.0, 0.15)

        #Save Figure
        plot.path = paths('plot')
        plot.name = 'time_offset_508'
        plot.ltit = 'Tests'

    print 'Plotted histogram'


if __name__ in ('__main__'):
    #download_data()
    calculate_delta()
    print_delta_results()
    plot_delta_test()
