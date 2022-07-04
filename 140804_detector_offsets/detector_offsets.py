""" Determine detector offset distribution

This determines the detector offsets for all stations in an ESD datafile.
These offsets are then fitted and the results are shown.

Having run this script on several datasets the expected distribution
has a mean of 0 ns and a sigma of 2.7 ns.

"""
from datetime import date

import tables

from numpy import arange, histogram
from scipy.optimize import curve_fit

from artist import Plot

from sapphire.analysis.calibration import determine_detector_timing_offsets
from sapphire.clusters import Station
from sapphire.utils import gauss

DATA_PATH = '/Users/arne/Datastore/esd/'
BIN_WIDTH = 1.25

O = (0, 0, 0)
STATION = Station(None, 0, O,
                  detectors=[(O, 'UD'), (O, 'UD'), (O, 'LR'), (O, 'LR')])


def determine_offset(data, s_path):
    events = data.get_node(s_path, 'events')
    offsets = [offset
               for offset in determine_detector_timing_offsets(events, STATION)
               if offset != 0.0]
    return offsets


def determine_offsets(data):
    detector_offsets = []
    for s_path in data.root.coincidences.s_index:
        detector_offsets.extend(determine_offset(data, s_path))
    return detector_offsets


def fit_offsets(offsets):
    bins = arange(-50 + BIN_WIDTH / 2, 50, BIN_WIDTH)
    y, bins = histogram(offsets, bins=bins)
    x = (bins[:-1] + bins[1:]) / 2
    popt, pcov = curve_fit(gauss, x, y, p0=(len(offsets), 0., 2.5))
    return x, y, popt


def plot_fit(x, y, popt, graph):
    graph.plot(x - BIN_WIDTH / 2, y, mark=None, use_steps=True)
    fit_x = arange(min(x), max(x), 0.1)
    graph.plot(fit_x, gauss(fit_x, *popt), mark=None, linestyle='gray')


if __name__ == '__main__':

    dates = [(2013, 3, 19), (2013, 10, 28), (2014, 1, 1), (2014, 1, 2),
             (2014, 1, 3), (2014, 1, 4), (2014, 1, 10), (2014, 1, 20),
             (2014, 1, 30)]
    files = [date(y, m, d) for y, m, d in dates]
    for f in files:
        path = DATA_PATH + f.strftime('%Y/%-m/%Y_%-m_%-d.h5')
        with tables.open_file(path, 'r') as data:
            offsets = determine_offsets(data)

        graph = Plot()
        x, y, popt = fit_offsets(offsets)
        plot_fit(x, y, popt, graph)
        graph.set_label(r'$\mu$: {:.2f}, $\sigma$: {:.2f}'.format(popt[1], popt[2]))
        graph.set_ylabel('Occurrence')
        graph.set_xlabel(r'$\Delta t$ [ns]')
        graph.set_ylimits(min=0)
        graph.save_as_pdf('detector_offset_distribution_' +
                          f.strftime('%Y%m%d'))
