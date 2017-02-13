from __future__ import division

from datetime import datetime
import zlib

import tables
import numpy as np
from artist import Plot

from sapphire.publicdb import download_data

DATA = '/Users/arne/Datastore/dead_time.h5'
STATION = 99
TESTS = ((1, datetime(2015, 5, 22, 11, 10), datetime(2015, 5, 22, 11, 15)),
         (2, datetime(2015, 5, 22, 11, 24), datetime(2015, 5, 22, 11, 26)),
         (3, datetime(2015, 5, 22, 11, 27), datetime(2015, 5, 22, 11, 29)),
         (4, datetime(2015, 5, 22, 11, 32), datetime(2015, 5, 22, 11, 34)))
TIME_WINDOWS = ((1, 2., 1., 0.),
                (2, 1., 1., 1.),
                (3, 1., 1., 1.),
                (4, .5, 1., 0.))


def download_tests():
    with tables.open_file(DATA, 'w') as data:
        for i, start, end in TESTS:
            download_data(data, '/t%d' % i, STATION, start, end, get_blobs=True)


def check_intervals():
    with tables.open_file(DATA, 'r') as data:
        for i in range(1, 5):
            ets = data.get_node('/t%d' % i).events.col('ext_timestamp')
            ets.sort()
            dt = ets[1:] - ets[:-1]
            n, bins = np.histogram(dt, bins=np.logspace(1, 10, 100))
            plot = Plot('semilogx')
            plot.histogram(n, bins)
            plot.set_ylabel('Number of events')
            plot.set_xlabel('Time between subsequent events')
            plot.set_ylimits(min=0)
            plot.set_xlimits(min=1, max=1e10)
            plot.save_as_pdf('interval_%d' % i)


def check_peaks():
    with tables.open_file(DATA, 'r') as data:
        for i in range(1, 5):
            # pin = data.get_node('/t%d' % i).events.col('integrals')[:,1]
            npk = data.get_node('/t%d' % i).events.col('n_peaks')[:, 1]
            print 'Test %d' % i
            print 'Fraction of events with 1 pulse:  %.2f' % (npk.tolist().count(1) / len(npk))
            print 'Fraction of events with 2 pulses: %.2f' % (npk.tolist().count(2) / len(npk))


def plot_traces():

    with tables.open_file(DATA, 'r') as data:
        for i, pre, coin, post in TIME_WINDOWS:
            test_node = data.get_node('/t%d' % i)
            events = test_node.events.read()
            events.sort(order='ext_timestamp')
            blobs = test_node.blobs
            for e_idx in [0, 1]:
                t_idx = events[e_idx]['traces'][1]
                extts = events[e_idx]['ext_timestamp']
                try:
                    trace = zlib.decompress(blobs[t_idx]).split(',')
                except zlib.error:
                    trace = zlib.decompress(blobs[t_idx][1:-1]).split(',')
                if trace[-1] == '':
                    del trace[-1]
                trace = [int(x) for x in trace]
                plot = Plot()
                plot.plot(range(len(trace)), trace, mark=None)
                plot.set_label('%d' % extts)
                microsec_to_sample = 400
                plot.draw_vertical_line(pre * 400, linestyle='thick,red,semitransparent')
                plot.draw_vertical_line((pre + coin) * 400, linestyle='thick,blue,semitransparent')
                plot.set_ylabel('Signal strength [ADCcounts]')
                plot.set_xlabel('Sample [2.5ns]')
                plot.set_ylimits(min=150, max=1500)
                plot.set_xlimits(min=0, max=len(trace))
                plot.save_as_pdf('trace_%d_%d' % (i, e_idx))


if __name__ == "__main__":
    # download_tests()
    # check_intervals()
    check_peaks()
    plot_traces()
