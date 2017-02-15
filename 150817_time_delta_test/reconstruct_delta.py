import tables
from numpy import genfromtxt, histogram, where, array, arange, histogram2d, nan
from scipy.optimize import curve_fit

from artist import Plot, MultiPlot

from sapphire import load_data
from sapphire.utils import gauss


def load_dataset():
    with tables.open_file('data/data.h5', 'w') as data:
        load_data(data, '/s99', 'data/events-s99-20150817.tsv')


def combine_delta_data():
    delta_data = genfromtxt('data/time_delta.tsv', delimiter='\t', dtype=None,
                            names=['ext_timestamp', 'time_delta'])
    delta_data = {ets: td for ets, td in delta_data}

    tm = []
    ts = []
    td = []
    te = []
    with tables.open_file('data/data.h5', 'r') as data:
        for row in data.root.s99.events:
            ets = row['ext_timestamp']
            try:
                dt = delta_data[ets]
            except KeyError:
                continue
            tm.append(row['t1'])
            ts.append(row['t3'])
            td.append(dt)
            te.append(ets)
    tm = array(tm)
    ts = array(ts)
    td = array(td)
    te = array(te)
    filter = (tm >= 0) & (ts >= 0)
    tm = tm.compress(filter)
    ts = ts.compress(filter)
    td = td.compress(filter)
    te = te.compress(filter)

    bins = arange(-10.25, 10.26, .5)
    mplot = MultiPlot(3, 2, width=r'.4\linewidth', height=r'.3\linewidth')
    mplot.show_xticklabels_for_all([(2, 0), (2, 1)])
    mplot.show_yticklabels_for_all([(0, 0), (1, 1), (2, 0)])
    mplot.set_xlimits_for_all(min=-11, max=11)
    mplot.set_ylimits_for_all(min=0, max=1500)
    mplot.set_ylabel('Counts')
    mplot.set_xlabel(r'Time difference [\si{\nano\second}]')

    plot = mplot.get_subplot_at(0, 0)
    counts, bins = histogram(tm - ts, bins=bins)
    popt = fit_timing_offset(counts / 3., bins)
    plot.set_label(r'$t_{M} - t_{S}$, $%.1f\pm%.1f$\si{\nano\second}, scaled' %
                   (popt[1], popt[2]))
    plot.histogram(counts / 3., bins)
    plot.plot(bins, gauss(bins, *popt), mark=None, linestyle='gray')

    plot = mplot.get_subplot_at(1, 0)
    plot.set_label(r'$t_{\delta}$')
    plot.histogram(*histogram(td, bins=bins))

    plot = mplot.get_subplot_at(2, 0)
    counts, bins = histogram(tm - (ts + td), bins=bins)
    popt = fit_timing_offset(counts, bins)
    plot.set_label(r'$t_{M} - (t_{S} + t_{\delta})$, $%.1f\pm%.1f$\si{\nano\second}' %
                   (popt[1], popt[2]))
    plot.histogram(counts, bins)
    plot.plot(bins, gauss(bins, *popt), mark=None, linestyle='gray')

    plot = mplot.get_subplot_at(0, 1)
    plot.set_label(r'$t_{\delta}$ where $t_{M} - t_{S} == -5$')
    plot.draw_vertical_line(-5, linestyle='gray')
    plot.histogram(*histogram(td.compress(tm - ts == -5), bins=bins))
    plot = mplot.get_subplot_at(1, 1)
    plot.set_label(r'$t_{\delta}$ where $t_{M} - t_{S} == -2.5$')
    plot.draw_vertical_line(-2.5, linestyle='gray')
    plot.histogram(*histogram(td.compress(tm - ts == -2.5), bins=bins))
    plot = mplot.get_subplot_at(2, 1)
    plot.set_label(r'$t_{\delta}$ where $t_{M} - t_{S} == 0$')
    plot.draw_vertical_line(0, linestyle='gray')
    plot.histogram(*histogram(td.compress(tm - ts == 0), bins=bins))
    mplot.save_as_pdf('dt_time_delta')

    plot = Plot()

    counts, xbins, ybins = histogram2d(tm - ts, td, bins=bins)
    plot.histogram2d(counts, xbins, ybins, bitmap=True, type='reverse_bw')
    plot.set_xlabel(r'$t_{M} - t_{S}$ [\si{\nano\second}]')
    plot.set_ylabel(r'$t_{\delta}$ [\si{\nano\second}]')

    plot.save_as_pdf('dt_vs_time_delta')


def fit_timing_offset(counts, bins):
    y = counts
    x = (bins[:-1] + bins[1:]) / 2
    filter = counts > 0
    try:
        popt, pcov = curve_fit(gauss, x.compress(filter), y.compress(filter),
                               p0=(sum(counts), 0., 2.5))
    except RuntimeError:
        return (nan, nan, nan)
    return popt


if __name__ == "__main__":
    # load_dataset()
    combine_delta_data()
