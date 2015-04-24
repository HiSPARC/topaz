import tables
from numpy import histogram, logspace

from artist import Plot

COIN_PATH = '/Users/arne/Datastore/esd_coincidences/sciencepark_n2_100101_150401.h5'


def plot_coincidence_intervals(coincidences):
    plot = Plot(axis='semilogx')
    bins = logspace(7, 15, 150)
    for n in [2, 3, 4, 5, 6, 7, 8]:
        dt = coincidence_interval(coincidences, n)
        counts, bins = histogram(dt, bins=bins)
        # The counts are multiplied by 3 ** n to make them more similar in size
        # Difference are cause by energy spectrum, station uptime and positions
        plot.histogram(counts * (3 ** n), bins, linestyle=r'black!%d0' % n)
        plot.draw_vertical_line(bins[counts.argmax()], linestyle=r'black!%d0' % n)
    plot.set_xlabel(r'Time between consecutive coincidences')
    plot.set_ylabel(r'Counts')
    plot.set_ylimits(min=0)
    plot.set_xlimits(min=bins[0], max=bins[-1])
    plot.save_as_pdf('coincidence_intervals_501')


def coincidence_interval(coincidences, n):
    if n == 0:
        ets = coincidences.col('ext_timestamp')
    else:
        ets = coincidences.read_where('(N == n) & s501', field='ext_timestamp')
    dt = ets[1:] - ets[:-1]
    return dt


if __name__ == "__main__":
    with tables.open_file(COIN_PATH, 'r') as data:
        coincidences = data.root.coincidences.coincidences
        plot_coincidence_intervals(coincidences)
