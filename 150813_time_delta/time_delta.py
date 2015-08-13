from numpy import genfromtxt, where, histogram, arange, convolve, ones

from artist import Plot


def analyse():
    data = genfromtxt('time_delta.csv', delimiter=',', dtype=None,
                      names=['timestamp', 'nanoseconds', 'time_delta'])
    unsigned_time_delta = data['time_delta']
    time_delta = where(unsigned_time_delta > 100000,
                       unsigned_time_delta - 2 ** 32,
                       unsigned_time_delta)

    # Plot distribution
    counts, bins = histogram(time_delta, bins=arange(-10.5, 11.5, 1))
    plot = Plot()
    plot.histogram(counts, bins)
    plot.set_ylimits(min=0)
    plot.set_ylabel('counts')
    plot.set_xlabel(r'time delta [\si{\nano\second}]')
    plot.save_as_pdf('time_delta')

    # Plot moving average
    n = 5000
    skip = 100
    moving_average = convolve(time_delta, ones((n,)) / n, mode='valid')
    plot = Plot()
    plot.plot(data['timestamp'][:-n + 1:skip], moving_average[::skip], mark=None)
    plot.set_ylabel(r'time delta [\si{\nano\second}]')
    plot.set_xlabel('timestamp (GPS)')
    plot.save_as_pdf('moving_average')


if __name__ == "__main__":
    analyse()
