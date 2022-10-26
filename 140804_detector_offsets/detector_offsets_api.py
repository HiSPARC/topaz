"""Plot distribution off detector offsets"""

from datetime import date

from numpy import arange, histogram, isnan, mean, std
from scipy.optimize import curve_fit

from artist import Plot

from sapphire import Network, Station
from sapphire.transformations.clock import datetime_to_gps
from sapphire.utils import gauss

BIN_WIDTH = 0.625


def get_offsets_dict():
    offsets = {s: Station(s).detector_timing_offset for s in Network().station_numbers()}
    return offsets


def offsets_on_date(offsets, d, id):
    timestamp = datetime_to_gps(d)
    return [o(timestamp)[id] for o in list(offsets.values()) if not isnan(o(timestamp)[1])]


def fit_offsets(offsets):
    bins = arange(-50 + BIN_WIDTH / 2, 50, BIN_WIDTH)
    y, bins = histogram(offsets, bins=bins)
    x = (bins[:-1] + bins[1:]) / 2
    popt, pcov = curve_fit(gauss, x, y, p0=(len(offsets), 0.0, 2.5))
    return x, y, popt


def plot_data_and_fit(x, y, popt, plot):
    plot.plot(x - BIN_WIDTH / 2, y, mark=None, use_steps=True)
    fit_x = arange(min(x), max(x), 0.1)
    plot.plot(fit_x, gauss(fit_x, *popt), mark=None, linestyle='gray')


def plot_and_fit_offsets(x, y, popt, d, id):
    plot = Plot()
    plot_data_and_fit(x, y, popt, plot)
    plot.set_label(r'$\mu$: {:.2f}, $\sigma$: {:.2f}'.format(popt[1], popt[2]))
    plot.set_ylabel('Occurrence')
    plot.set_xlabel(r'$\Delta t$ [ns]')
    plot.set_ylimits(min=0)
    plot.save_as_pdf('api_detector_offset_distribution_%s_' % id + d.strftime('%Y%m%d'))


if __name__ == '__main__':
    offsets = get_offsets_dict()
    for id in [0, 2]:
        mu = []
        sigma = []
        for y in range(2008, 2016):
            for m in range(1, 13):
                d = date(y, m, 1)
                o = offsets_on_date(offsets, d, id)
                xx, yy, popt = fit_offsets(o)
                # plot_and_fit_offsets(xx, yy, popt, d, id)
                mu.append(popt[1])
                sigma.append(popt[2])
        print(['Primary', 'Reference', 'Secondary', 'Secondary'][id])
        print('mean: {:.3f} +/- {:.3f}, std:  {:.3f} +/- {:.3f} '.format(mean(mu), std(mu), mean(sigma), std(sigma)))
