"""Plot station dt distribution"""

import itertools
from datetime import datetime

import tables
from numpy import histogram, linspace, arange, sqrt
from artist import MultiPlot
from scipy.optimize import curve_fit
from scipy.stats import t, norm, tukeylambda

from sapphire import HiSPARCStations
from sapphire.utils import gauss

from station_distances import horizontal_distance_between_stations

STATIONS = [502, 503, 504, 505, 506, 508, 509, 510]
DAY = 86400.
HALF_DAY = DAY / 2
WEEK = 7 * DAY
FORTNIGHT = 2 * WEEK
XWEEK = 3 * WEEK
MONTH = 30 * DAY
QUARTER = 3 * MONTH
HALFYEAR = 6 * MONTH
YEAR = 365 * DAY

SPA_STAT = [501, 502, 503, 504, 505, 506, 508, 509, 510]
CLUSTER = HiSPARCStations(SPA_STAT)

DATA_PATH = '/Users/arne/Datastore/station_offsets/'
SIM_PATH = '/Users/arne/Datastore/expected_dt/test_station_dt_spa.h5'


def get_station_dt(data, station):
    table = data.get_node('/s%d' % station)
    return table


def tl(x, loc, scale):
    return tukeylambda.pdf(x, 0.27, loc, scale)


def plot_fits(plot, counts, bins):
    """Fit dt distribution and plot results"""

    colors = (c for c in ['gray', 'lightgray', 'blue', 'red'])
    x = (bins[:-1] + bins[1:]) / 2
    for fit_f, p0, offset_idx in [
        # (gauss, (sum(counts), 0., 30), 1),
        (norm.pdf, (0., 30.), 0),
        # (t.pdf, (1., 0., 1.), 0),
        # (tl, (0., 450.), 0)
    ]:
        popt, pcov = curve_fit(fit_f, x, counts, p0=p0)
        plot.plot(x - popt[offset_idx], fit_f(x, *popt), mark=None,
                  linestyle=colors.next())
        if fit_f == norm.pdf:
            plot.set_label('$\mu$: %.2f, $\sigma$: %.2f' % (popt[0], popt[1]))
            offset = popt[0]
    return offset


def plot_offset_distributions():
    with tables.open_file(SIM_PATH, 'r') as sim_data:
        for ref_station, station in itertools.combinations(SPA_STAT, 2):  # [(504, 509)]:
            if ref_station == 501 and station == 510:
                continue
            with tables.open_file(DATA_PATH + 'dt_ref%d_%d.h5' % (ref_station, station), 'r') as data:

                distance = horizontal_distance_between_stations(ref_station, station)
                max_dt = max(distance / .3, 100) * 1.5
                table = get_station_dt(data, station)
                ts1 = table[-1]['timestamp'] - WEEK
                ts0 = ts1 - YEAR  # * max(1, (distance / 100))
                dt = table.read_where('(timestamp > ts0) & (timestamp < ts1)',
                                      field='delta')

                sim_ref_events = sim_data.get_node('/flat/cluster_simulations/station_%d' % ref_station, 'events')
                sim_events = sim_data.get_node('/flat/cluster_simulations/station_%d' % station, 'events')
                sim_dt = (sim_ref_events.col('ext_timestamp').astype(int) -
                          sim_events.col('ext_timestamp').astype(int))

                bins = arange(-2000, 2000.1, 30)  # linspace(-max_dt, max_dt, 150)
                x = (bins[:-1] + bins[1:]) / 2

                sim_counts, bins = histogram(sim_dt, bins=bins, density=True)
                counts, bins = histogram(dt, bins=bins, density=True)

                sim_offset = curve_fit(norm.pdf, x, sim_counts, p0=(0., 30.))[0][0]
                offset = curve_fit(norm.pdf, x, counts, p0=(0., 30.))[0][0]

                sim_counts, bins = histogram(sim_dt - sim_offset, bins=bins, density=True)
                counts, bins = histogram(dt - offset, bins=bins, density=True)

                plot = MultiPlot(2, 1)
                splot = plot.get_subplot_at(0, 0)
                splot.histogram(counts, bins)
                splot.histogram(sim_counts, bins, linestyle='green')
#                 plot_fits(splot, counts, bins)
                splot.draw_vertical_line(distance * 3.5, linestyle='dashed')
                splot.draw_vertical_line(-distance * 3.5, linestyle='dashed')
                splot.set_ylabel('Counts')
                splot.set_ylimits(min=0)

                splot = plot.get_subplot_at(1, 0)
                splot.scatter(x, counts - sim_counts, markstyle='mark size=1pt')
                splot.draw_horizontal_line(0, linestyle='gray')
                splot.set_axis_options(r'height=0.2\textwidth')

                plot.show_xticklabels(1, 0)
                plot.show_yticklabels_for_all(None)
                plot.set_xlabel(r'$\Delta t$ [\si{\ns}]')
                plot.set_xlimits_for_all(None, -2000, 2000)
                plot.save_as_pdf('plots/distribution/dt_ref%d_%d_dist_width' % (ref_station, station))


if __name__ == '__main__':
    plot_offset_distributions()
