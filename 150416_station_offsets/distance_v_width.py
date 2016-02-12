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

from numpy import sqrt, array, std, histogram, linspace
from scipy.optimize import curve_fit
from scipy.stats import norm
import tables

from artist import Plot

from sapphire import HiSPARCStations


DATA_PATH = '/Users/arne/Datastore/station_offsets/'
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

    for ref_station, station in itertools.combinations(SPA_STAT, 2):
        if ref_station == 501 and station == 509:
            continue
        distances.append(CLUSTER.calc_rphiz_for_stations(SPA_STAT.index(ref_station), SPA_STAT.index(station))[0])
        with tables.open_file(DATA_PATH + 'dt_ref%d_%d.h5' % (ref_station, station), 'r') as data:
            table = get_station_dt(data, station)
            ts1 = table[-1]['timestamp'] - WEEK
            ts0 = ts1 - QUARTER # * max(1, (distance / 100))
            dt = table.read_where('(timestamp > ts0) & (timestamp < ts1)',
                                  field='delta')
            pre_width = std(dt)
            counts, bins = histogram(dt, bins=linspace(-1.8*pre_width, 1.8*pre_width, 100), density=True)
            x = (bins[:-1] + bins[1:]) / 2
            popt, pcov = curve_fit(norm.pdf, x, counts, p0=(0., distances[-1]))
            widths.append(popt[1])
            print distances[-1], std(dt), popt[1]

    plot = Plot()
    popt, pcov = curve_fit(lin, distances, widths, p0=(1.1, 1))#, sigma=array(distances) ** 0.3)
    print popt, pcov
    plot.scatter(distances, widths)
    plot.plot([0, 600], [0, 600 / 0.3], mark=None, linestyle='gray')
    plot.plot([0, 600], [lin(0, *popt), lin(600, *popt)], mark=None)
    plot.set_xlimits(min=0, max=600)
    plot.set_ylimits(min=0, max=700)
    plot.set_xlabel(r'Distance [\si{\meter}]')
    plot.set_ylabel(r'Width of dt distribution [\si{\ns}]')
    plot.save_as_pdf('plots/distance_v_width_pr')


if __name__ == "__main__":
    plot_distance_width()
