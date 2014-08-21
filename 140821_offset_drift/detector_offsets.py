"""
TODO: Use all data (not just events in coincidences) from different days.
Currently the data may be susceptible to the uptime of other stations.
The coincidences may have a prefered direction.

"""
from numpy import arange, linspace, histogram
from scipy.optimize import curve_fit
import tables

from sapphire.utils import gauss


bins = arange(-100 + 1.25, 100, 2.5)
filepath = '/Users/arne/Datastore/esd_coincidences/coincidences_n2_100101_140601.h5'

with tables.open_file(filepath, 'r') as data:
    for s in [501, 502, 503, 504, 505, 506, 508, 509]:
        events = data.get_node('/hisparc/cluster_amsterdam/station_%d' % s, 'events')
        t2 = events.col('t2')
        print 'Station %d' % s
        for detector in [0, 2, 3]:
            offsets = []
            timings = events.col('t%d' % (detector + 1))
            dt = (timings - t2).compress((t2 >= 0) & (timings >= 0))
            b = 0
            for e in linspace(0, len(dt), 10):
                if e == 0:
                    continue
                y, bins = histogram(dt[b:e], bins=bins)
                x = (bins[:-1] + bins[1:]) / 2
                popt, pcov = curve_fit(gauss, x, y, p0=(len(dt), 0., 10.))
                offsets.append(popt[1])
                b = e
            print '%d-1: ' % detector, [round(o, 1) for o in offsets]
