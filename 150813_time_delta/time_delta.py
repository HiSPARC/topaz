from numpy import arange, convolve, genfromtxt, histogram, ones
from scipy.optimize import curve_fit

from artist import Plot

from sapphire.utils import gauss


def analyse(name):
    data = genfromtxt('data/%s.tsv' % name, delimiter='\t', dtype=None,
                      names=['ext_timestamp', 'time_delta'])
    time_delta = data['time_delta']

    # Plot distribution
    counts, bins = histogram(time_delta, bins=arange(-10.5, 11.5, 1))
    plot = Plot()
    plot.histogram(counts, bins)
    x = (bins[1:] + bins[:-1]) / 2.
    popt, pcov = curve_fit(gauss, x, counts, p0=(sum(counts), 0., 2.5))
    plot.plot(x, gauss(x, *popt), mark=None)
    print(popt)
    plot.set_ylimits(min=0)
    plot.set_ylabel('Counts')
    plot.set_xlabel(r'Time delta [\si{\nano\second}]')
    plot.save_as_pdf(name)

    # Plot moving average
    n = 5000
    skip = 100
    moving_average = convolve(time_delta, ones((n,)) / n, mode='valid')
    plot = Plot()
    timestamps = (data['ext_timestamp'][:-n + 1:skip] -
                  data['ext_timestamp'][0]) / 1e9 / 3600.
    plot.plot(timestamps, moving_average[::skip], mark=None)
    plot.set_xlimits(min=0)
    plot.set_ylabel(r'time delta [\si{\nano\second}]')
    plot.set_xlabel(r'timestamp [\si{\hour}]')
    plot.save_as_pdf('moving_average_%s' % name)


if __name__ == "__main__":
    for path in ['time_delta', 'time_delta_510', 'time_delta_501']:
        analyse(path)
