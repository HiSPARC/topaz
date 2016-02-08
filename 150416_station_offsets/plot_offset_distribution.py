"""Show overall offset distribution
"""

import itertools
from datetime import date
import csv
import calendar
from glob import glob
import re

from artist import Plot
from numpy import nan, genfromtxt, histogram, arange, isnan, genfromtxt
from scipy.optimize import curve_fit

from sapphire.utils import gauss

OFF_DATAPATH_GLOB = '/Users/arne/Datastore/station_offsets/offsets_ref*_s*.tsv'


def plot_distribution():
    offsets = []
    for path in glob(OFF_DATAPATH_GLOB):
        data = genfromtxt(path)
        fdata = data[~isnan(data[:,1]),1]
        if len(fdata):
            offsets.append(fdata[-1])
    mindt = -200
    maxdt = 200
    plot = Plot()
    counts, bins = histogram(offsets, bins=arange(mindt, maxdt, 10))
    popt, pcov = curve_fit(gauss, (bins[:-1] + bins[1:]) / 2, counts)
    plot.histogram(counts, bins)
    x = arange(mindt, maxdt, 0.1)
    plot.plot(x, gauss(x, *popt), mark=None)
    plot.set_label(r'$\mu$ = %.1f, $\sigma$ = %.1f' % tuple(popt[1:].tolist()))
    plot.set_xlabel(r'Station offset [\si{\ns}]')
    plot.set_ylabel(r'Counts')
    plot.set_ylimits(min=0)
    plot.save_as_pdf('plots/offset_distribution')


if __name__ == '__main__':
    for ref_station, station in get_available_station_pairs():
        plot_offset_timeline(ref_station, station)
