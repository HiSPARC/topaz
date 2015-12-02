"""This script is for analysis of events in Test 3

Test 3 uses 4 muonlab detectors, which makes it capable of detecting air
showers by itself. This analysis takes that fact into account and
also uses the 2 additional muon paths for time differences.

"""
import itertools

from artist import Plot
import tables
import numpy as np

from sapphire import CoincidenceQuery


EVENTDATA_PATH = '/Users/arne/Datastore/muonlab_test3.h5'


def analyse(data):
    # Time differences all 3 combinations
    # Only one of the roof detectors with signal
    # Compare showers (i.e. at least 2 on roof) with 501/510 coincidences
    # ...

    event_node = data.get_node('/station_99/events')
    print 'Total number of events: %d' % event_node.nrows

    plot = Plot()
    bins = np.arange(-100, 100, 2.5)
    for i, j in itertools.combinations(range(4), 2):
        selection = event_node.read_where('(t%d > 0) & (t%d > 0)' % i, j)
        dt = selection['t%d' % i] - selection['t%d' % j]
        counts, bins = np.histogram(dt, bins=bins)
        plot.histogram(counts, bins)
    plot.set_ylimits(min=0)
    plot.set_ylabel('Counts')
    plot.set_xlabel('Time difference [ns]')
    plot.save_as_pdf('muonlab_t3_dt')


if __name__ == '__main__':
    with tables.open_file(EVENTDATA_PATH, 'r') as data:
        analyse(data)
