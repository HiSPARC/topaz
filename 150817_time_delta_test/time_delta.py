from numpy import arange, convolve, genfromtxt, histogram, ones

from artist import Plot


def analyse(name):
    data = genfromtxt('data/%s.tsv' % name, delimiter='\t', dtype=None, names=['ext_timestamp', 'time_delta'])
    time_delta = data['time_delta']

    # Plot distribution
    counts, bins = histogram(time_delta, bins=arange(-10.5, 11.5, 1))
    plot = Plot()
    plot.histogram(counts, bins)
    plot.set_ylimits(min=0)
    plot.set_ylabel('counts')
    plot.set_xlabel(r'time delta [\si{\nano\second}]')
    plot.save_as_pdf(name)

    # Plot moving average
    n = 300
    skip = 20
    moving_average = convolve(time_delta, ones((n,)) / n, mode='valid')
    plot = Plot()
    timestamps = (data['ext_timestamp'][: -n + 1 : skip] - data['ext_timestamp'][0]) / 1e9 / 3600.0
    plot.plot(timestamps, moving_average[::skip], mark=None)
    plot.set_xlimits(min=0)
    plot.set_ylabel(r'time delta [\si{\nano\second}]')
    plot.set_xlabel(r'timestamp [\si{\hour}]')
    plot.save_as_pdf('moving_average_%s' % name)


if __name__ == "__main__":
    for path in ['time_delta']:
        analyse(path)
