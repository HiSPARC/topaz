"""Plot station dt vs time"""

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
YEAR = 365 * DAY

SPA_STAT = [501, 502, 503, 504, 505, 506, 508, 509, 510]
CLUSTER = HiSPARCStations(SPA_STAT)


def get_station_dt(data, station):
    table = data.get_node('/s%d' %station)
    return table


if __name__ == '__main__':
    t_start = datetime_to_gps(datetime(2010, 1, 1))
    t_end = datetime_to_gps(datetime(2015, 4, 1))

    with tables.open_file('data/dt.h5', 'r') as data:
        for i, station in enumerate(STATIONS, 1):
            distance, _, _ = CLUSTER.calc_rphiz_for_stations(i, 0)
            max_dt = max(distance / .3, 100) * 1.5
            table = get_station_dt(data, station)
            graph = Plot()
            ts0 = table[0]['timestamp'] + WEEK
            ts1 = ts0 + XWEEK # * max(1, (distance / 100))
            counts, bins = histogram(table.read_where('(timestamp > ts0) & (timestamp < ts1)',
                                                      field='delta'),
                                     bins=(linspace(-max_dt, max_dt, 150)))
            x = (bins[:-1] + bins[1:]) / 2
            popt, pcov = curve_fit(gauss, x, counts, p0=(sum(counts), 0., max_dt))
            graph.plot(x, gauss(x, *popt), mark=None, linestyle='gray')
            graph.set_label('$\mu$: %.2f, $\sigma$: %.2f' % (popt[1], popt[2]))

            graph.histogram(counts, bins)
            graph.set_xlabel('$\Delta t$ [ns]')
            graph.set_ylabel('Counts')
            graph.set_xlimits(-max_dt, max_dt)
            graph.set_ylimits(min=0)
            graph.save('plots/dt_%d_dist_xweek' % station)
