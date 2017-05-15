import itertools
import os

import numpy as np
import tables

from artist import Plot

from hisparc.analysis.coincidences import search_coincidences as search
from sapphire.esd import download_data

import delta

from testlist import Tijdtest

DATA_PATH = '/Users/arne/Datastore/gps_offsets/508_data.h5'
DELTAS_PATH = '/Users/arne/Datastore/gps_offsets/508_deltas.h5'


def test_log_508():
    """ A log of davids tests

    In this program is a list of all available tests from the tijdtest project.

    """
    tests = (
        (1, '317', '501', '', (2013, 6, 19, 13, 0), (2013, 6, 29, 23, 0), ''),
        (2, '317', '502', '', (2013, 6, 19, 13, 0), (2013, 6, 29, 23, 0), ''),
        (3, '317', '505', '', (2013, 6, 19, 13, 0), (2013, 6, 29, 23, 0), ''),
        (4, '317', '506', '', (2013, 6, 19, 13, 0), (2013, 6, 29, 23, 0), ''),
        (5, '317', '501', '', (2013, 6, 28, 0, 0), (2013, 6, 29, 23, 0), ''),
        (6, '317', '502', '', (2013, 6, 28, 0, 0), (2013, 6, 29, 23, 0), ''),
        (7, '317', '505', '', (2013, 6, 28, 0, 0), (2013, 6, 29, 23, 0), ''),
        (8, '317', '506', '', (2013, 6, 28, 0, 0), (2013, 6, 29, 23, 0), ''))

    test_all = [Tijdtest(*test) for test in tests]

    return test_all


def download(storage, test):
    """ Download data from the tijdtest stations

    This will download data in the given date range from both the swap and
    reference station into storage.

    """
    print 'tt_data: Downloading data for test %d: %s' % (test.id, test.group)
    download_data(storage, '/refr/t%d' % test.id, 508, test.start, test.end)
    download_data(storage, '/swap/t%d' % test.id, int(test.gps), test.start, test.end)


def download_test_data():
    tests = test_log_508()
    with tables.open_file(DATA_PATH, 'w') as storage:
        for test in tests:
            download(storage, test)


def calculate_delta():
    # Difference in length of cables to boxes in nano seconds, (swap - refr)
    tests = test_log_508()
    with tables.open_file(DATA_PATH, 'r') as data_file, \
            tables.open_file(DELTAS_PATH, 'w') as delta_file:
        for test in tests:
            table = delta_file.create_table('/t%d' % test.id, 'delta',
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
        with tables.open_file(DELTAS_PATH, 'r') as delta_file:
            delta_table = delta_file.get_node('/t%d' % test.id, 'delta')
            ext_timestamps = [row['ext_timestamp'] for row in delta_table]
            deltas = [row['delta'] for row in delta_table]
        print "    % 3d  %s  % 7.2f  % 6.2f  % 4.2f" % (
            test.id, test.group.ljust(13),
            round(np.average(deltas), 2), round(np.std(deltas), 2),
            (max(ext_timestamps) - min(ext_timestamps)) / 864e11)


def plot_delta_test():
    """ Plot the delta with std

    """
    # Define Bins
    low = -2000
    high = 2000
    bin_size = 10  # 2.5*n?
    bins = np.arange(low - .5 * bin_size, high + bin_size, bin_size)

    tests = test_log_508()

    # Begin Figure
    plot = Plot()
    with tables.open_file(DELTAS_PATH, 'r') as delta_file:
        for test in tests:
            delta_table = delta_file.get_node('/t%d' % test.id, 'delta')
            ext_timestamps = [row['ext_timestamp'] for row in delta_table]
            deltas = [row['delta'] for row in delta_table]
            bins = np.arange(low - 0.5 * bin_size, high + bin_size, bin_size)
            n, bins = np.histogram(deltas, bins)
            plot.histogram(n, bins)

    plot.set_title('Time difference coincidences 508')
    # plot.set_label(r'$\mu={1:.1f}$, $\sigma={2:.1f}$'.format(*popt))
    plot.set_xlabel(r'$\Delta$ t (station - 508) [\SI{\ns}]')
    plot.set_ylabel(r'p')
    plot.set_xlimits(low, high)
    plot.set_ylimits(min=0., max=0.15)
    plot.save_as_pdf('plots/508/histogram.pdf')


if __name__ in ('__main__'):
    if not os.path.exists(DATA_PATH):
        download_test_data()
    calculate_delta()
    print_delta_results()
    plot_delta_test()
