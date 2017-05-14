"""Coincidence intervals

Coincidence intervals for coincidences at Science Park with n stations in
coincidence (where 501 is at least one of the stations).

Be careful with adding 510.

"""
import tables

from numpy import histogram, logspace

from artist import Plot

COIN_PATH = '/Users/arne/Datastore/esd_coincidences/sciencepark_n2_100101_150401.h5'


def plot_coincidence_intervals(coincidences):
    plot = Plot(axis='semilogx')
    bins = logspace(7, 15, 150)
    minn, maxn = (2, 10)
    for n in range(minn, maxn + 1):
        dt = coincidence_interval(coincidences, n)
        counts, bins = histogram(dt, bins=bins)
        # The counts are multiplied by 3 ** n to make them more similar in size
        # Difference are cause by energy spectrum, station uptime and positions
        greyness = r'black!%d' % (n * 100 / maxn)
        plot.histogram(counts * (3 ** n), bins, linestyle=greyness)
        plot.draw_vertical_line(bins[counts.argmax()], linestyle=greyness)
    plot.set_xlabel(r'Time between consecutive coincidences')
    plot.set_ylabel(r'Counts')
    plot.set_ylimits(min=0)
    plot.set_xlimits(min=bins[0], max=bins[-1])
    plot.save_as_pdf('coincidence_intervals_501')


def coincidence_interval(coincidences, n):
    if n == 0:
        ets = coincidences.col('ext_timestamp')
    else:
        ets = coincidences.read_where('(N == n) & s501 & ~s510 & ~s507',
                                      field='ext_timestamp')
    dt = ets[1:] - ets[:-1]
    return dt


if __name__ == "__main__":
    with tables.open_file(COIN_PATH, 'r') as data:
        coincidences = data.root.coincidences.coincidences
        plot_coincidence_intervals(coincidences)
