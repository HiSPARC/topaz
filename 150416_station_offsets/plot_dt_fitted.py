"""Plot station dt distribution"""

import itertools
from datetime import datetime

import tables
from numpy import histogram, linspace, arange
from artist import Plot
from scipy.optimize import curve_fit

from sapphire import HiSPARCStations
from sapphire.utils import gauss
from sapphire.transformations.clock import datetime_to_gps

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


def get_station_dt(data, station):
    table = data.get_node('/s%d' %station)
    return table


if __name__ == '__main__':
    t_start = datetime_to_gps(datetime(2010, 1, 1))
    t_end = datetime_to_gps(datetime(2015, 4, 1))

    for ref_station, station in itertools.permutations(SPA_STAT, 2):
        with tables.open_file(DATA_PATH + 'dt_ref%d_%d.h5' % (ref_station, station), 'r') as data:
            distance, _, _ = CLUSTER.calc_rphiz_for_stations(SPA_STAT.index(ref_station), SPA_STAT.index(station))
            max_dt = max(distance / .3, 100) * 1.5
            table = get_station_dt(data, station)
            graph = Plot()
            ts1 = table[-1]['timestamp'] - WEEK
            ts0 = ts1 - QUARTER # * max(1, (distance / 100))
            counts, bins = histogram(table.read_where('(timestamp > ts0) & (timestamp < ts1)',
                                                      field='delta'),
                                     bins=(linspace(-max_dt, max_dt, 150)))
            x = (bins[:-1] + bins[1:]) / 2
            popt, pcov = curve_fit(gauss, x, counts, p0=(sum(counts), 0., max_dt))

            # print ref_station, station, distance, popt[-1]

            graph.plot(x, gauss(x, *popt), mark=None, linestyle='gray')
            graph.set_label('$\mu$: %.2f, $\sigma$: %.2f' % (popt[1], popt[2]))

            graph.histogram(counts, bins)
            graph.set_xlabel('$\Delta t$ [ns]')
            graph.set_ylabel('Counts')
            graph.set_xlimits(-max_dt, max_dt)
            graph.set_ylimits(min=0)
            graph.save_as_pdf('plots/dt_ref%d_%d_dist_3month' % (ref_station, station))
