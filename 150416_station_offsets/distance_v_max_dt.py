"""Width of dt distribution vs distance

Fokkema 2012 and Bosboom 2011 found that 1 ns / m fits the data.
For me 1.17 ns / m seems to be a better fit.
Partially explained by more stations used in the analysis,
with increased maximum distance. At higher distances the width increases due
to shower front shape and rise time are more pronounced.
At low distance (2 m) the width is still present due to small low density
showers and angled showers.

Might need a better fit than linear to account for the changing
contributions.

"""
import itertools

from numpy import array, percentile
from scipy.optimize import curve_fit
from scipy.stats import norm
import tables

from artist import MultiPlot

from sapphire import HiSPARCStations


DATA_PATH = '/Users/arne/Datastore/station_offsets/'
SIM_PATH = '/Users/arne/Datastore/expected_dt/test_station_dt_spa.h5'

SPA_STAT = [501, 502, 503, 504, 505, 506, 508, 509, 510, 511]
CLUSTER = HiSPARCStations(SPA_STAT)
DAY = 86400.
HALF_DAY = DAY / 2
WEEK = 7 * DAY
FORTNIGHT = 2 * WEEK
XWEEK = 3 * WEEK
MONTH = 30 * DAY
QUARTER = 3 * MONTH
HALFYEAR = 6 * MONTH
YEAR = 365 * DAY


def get_station_dt(data, station):
    table = data.get_node('/s%d' % station)
    return table


def lin(x, a, b):
    return x * a + b


def plot_distance_width():

    distances = []
    widths = []
    sim_widths = []

    with tables.open_file(SIM_PATH, 'r') as sim_data:
        for ref_station, station in itertools.combinations(SPA_STAT, 2):
            if ref_station == 501 and station == 509:
                continue
            if ref_station == 501 and station == 510:
                continue
            if ref_station == 505 and station == 509:
                continue
            distances.append(CLUSTER.calc_rphiz_for_stations(SPA_STAT.index(ref_station), SPA_STAT.index(station))[0])
            with tables.open_file(DATA_PATH + 'dt_ref%d_%d.h5' % (ref_station, station), 'r') as data:

                table = get_station_dt(data, station)
                ts1 = table[-1]['timestamp'] - WEEK
                ts0 = ts1 - HALFYEAR  # * max(1, (distance / 100))
                dt = table.read_where('(timestamp > ts0) & (timestamp < ts1)',
                                      field='delta')

                sim_ref_events = sim_data.get_node('/flat/cluster_simulations/station_%d' % ref_station, 'events')
                sim_events = sim_data.get_node('/flat/cluster_simulations/station_%d' % station, 'events')
                sim_dt = (sim_ref_events.col('ext_timestamp').astype(int) -
                          sim_events.col('ext_timestamp').astype(int))

                high = 94
                low = 6
                width = percentile(sorted(dt), high) - percentile(sorted(dt), low)
                widths.append(width)
                sim_width = percentile(sim_dt, high) - percentile(sim_dt, low)
                sim_widths.append(sim_width)

    widths = array(widths)
    sim_widths = array(sim_widths)

    popt, pcov = curve_fit(lin, distances, widths, p0=(1.1, 1), sigma=array(distances) ** 0.3)
    print popt, pcov

    plot = MultiPlot(2, 1)
    splot = plot.get_subplot_at(0, 0)
    splot.scatter(distances, widths)
    splot.scatter(distances, sim_widths, markstyle='green')
    splot.plot([0, 600], [0, 600 / 0.3], mark=None, linestyle='gray')
    splot.plot([0, 600], [lin(0, *popt), lin(600, *popt)], mark=None)
    splot.set_ylimits(min=0, max=700 / 0.3)

    splot = plot.get_subplot_at(1, 0)
    splot.scatter(distances, widths - sim_widths, markstyle='mark size=1pt')
    splot.draw_horizontal_line(0, linestyle='gray')
    splot.set_axis_options(r'height=0.2\textwidth')

    plot.show_xticklabels(1, 0)
    plot.show_yticklabels_for_all(None)
    plot.set_xlimits_for_all(None, min=0, max=600)
    plot.set_xlabel(r'Distance [\si{\meter}]')
    plot.set_ylabel(r'Width of $\Delta t$ distribution [\si{\ns}]')
    plot.save_as_pdf('plots/distance_v_maxdt_sim')


if __name__ == "__main__":
    plot_distance_width()
