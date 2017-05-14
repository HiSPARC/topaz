"""Show overall offset distribution
"""

from glob import glob

from numpy import arange, genfromtxt, histogram, isnan
from scipy.optimize import curve_fit

from artist import Plot

from sapphire.utils import gauss

from plot_offsets import get_available_station_pairs

OFF_DATAPATH_GLOB = '/Users/arne/Datastore/station_offsets/offsets_ref*_s*.tsv'


def plot_distribution():
    offsets = []
    for path in glob(OFF_DATAPATH_GLOB):
        data = genfromtxt(path)
        fdata = data[~isnan(data[:, 1]), 1]
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
    plot_distribution()
