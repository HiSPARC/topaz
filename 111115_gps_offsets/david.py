import itertools

import numpy as np
import tables

from sapphire.esd import download_data

from .delta import DeltaVal, calculate
from .testlist import Tijdtest

DATA_PATH = '/Users/arne/Datastore/tijdtest/tijdtest_data_david.h5'
DELTA_PATH = '/Users/arne/Datastore/tijdtest/tijdtest_delta_david.h5'


def test_log_david():
    """ A log of davids tests

    In this program is a list of all available tests from the tijdtest project.

    """
    tests = (
        (1, '018', '501', 'EXT', (2011, 10, 21, 11, 0), (2011, 10, 23, 14, 0), 'rext r502 rmas050'),
        (2, '018', '501', 'EXT', (2011, 10, 23, 15, 0), (2011, 10, 24, 13, 0), 'rext r502 rmas050 rgpslost'),
        (3, '050', '501', 'EXT', (2011, 10, 28, 17, 30), (2011, 10, 31, 12, 0), 'rext r502 rmas018'))

    test_all = [Tijdtest(*test) for test in tests]

    return test_all


def download(storage, test):
    """ Download data from the tijdtest stations

    This will download data in the given date range from both the swap and
    reference station into storage.

    """
    print('tt_data: Downloading data for test %d: %s' % (test.id, test.group))
    download_data(storage, '/refr/t%d' % test.id, 95, test.start, test.end)
    download_data(storage, '/swap/t%d' % test.id, 94, test.start, test.end)


def download_data():
    tests = test_log_david()
    with tables.open_file(DATA_PATH, 'w') as storage:
        for test in tests:
            download(storage, test)


def calculate_delta():
    # Difference in length of cables to boxes in nano seconds, (swap - refr)
    cable_length = 435.
    tests = test_log_david()
    with tables.open_file(DATA_PATH, 'r') as data_file, \
            tables.open_file(DELTA_PATH, 'w') as delta_file:
        for test in tests:
            table = delta_file.create_table('/t%d' % test.id, 'delta',
                                            DeltaVal, createparents=True)
            ext_timestamps, deltas = calculate(data_file, test.id)
            delta_row = table.row

            for ext_timestamp, delta_val in zip(ext_timestamps, deltas):
                delta_row['ext_timestamp'] = ext_timestamp
                delta_row['delta'] = delta_val + cable_length
                delta_row.append()
            table.flush()


def print_delta_results():
    """ Prints the average delta, the standard deviation and length in days

    """
    tests = test_log_david()

    for test in tests:
        with tables.open_file(DELTA_PATH, 'r') as delta_file:
            delta_table = delta_file.get_node('/t%d' % test.id, 'delta')
            ext_timestamps = [row['ext_timestamp'] for row in delta_table]
            deltas = [row['delta'] for row in delta_table]
        print("    % 3d  %s  % 7.2f  % 6.2f  % 4.2f" % (
            test.id, test.group.ljust(13),
            round(np.average(deltas), 2), round(np.std(deltas), 2),
            (max(ext_timestamps) - min(ext_timestamps)) / 864e11))


if __name__ in ('__main__'):
    # download_data()
    calculate_delta()
    print_delta_results()
