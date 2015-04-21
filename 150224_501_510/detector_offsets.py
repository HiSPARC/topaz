from numpy import arange, histogram
from scipy.optimize import curve_fit
import tables

from sapphire.utils import gauss
from artist import Plot


EVENTDATA_PATH = '/Users/arne/Datastore/501_510/e_501_510_141101_150201.h5'
COLORS = ['black', 'green', 'blue', 'teal', 'orange', 'purple', 'cyan', 'red',
          'gray']


def determine_detector_timing_offsets(s, events):
    """Determine the offsets between the station detectors.

    ADL: Currently assumes detector 1 is a good reference.
    But this is not always the best choice. Perhaps it should be
    determined using more data (more than one day) to be more
    accurate.

    """
    bins = arange(-100 + 1.25, 100, 2.5)
    col = (cl for cl in COLORS)
    graph = Plot()
    ids = range(1, 5)
    reference = 2
    for j in [1, 3, 4]:
        if j == reference:
            continue
        tref = events.col('t%d' % reference)
        tj = events.col('t%d' % j)
        dt = (tj - tref).compress((tref >= 0) & (tj >= 0))
        y, bins = histogram(dt, bins=bins)
        c = col.next()
        graph.histogram(y, bins, linestyle='%s' % c)
        x = (bins[:-1] + bins[1:]) / 2
        try:
            popt, pcov = curve_fit(gauss, x, y, p0=(len(dt), 0., 10.))
            graph.draw_vertical_line(popt[1], linestyle='%s' % c)
            print '%d-%d: %f (%f)' % (j, reference, popt[1], popt[2])
        except (IndexError, RuntimeError):
            print '%d-%d: failed' % (j, reference)
    graph.set_title('Time difference, station %d' % (s))
    graph.set_xlimits(-100, 100)
    graph.set_ylimits(min=0)
    graph.set_xlabel('$\Delta t$')
    graph.set_ylabel('Counts')
    graph.save_as_pdf('detector_offsets_%s' % s)


if __name__ == '__main__':
    with tables.open_file(EVENTDATA_PATH, 'r') as data:
        for s in [501, 510]:
            print 'Station: %d' % s
            e = data.get_node('/s%d/events' % s)
            determine_detector_timing_offsets(s, e)
