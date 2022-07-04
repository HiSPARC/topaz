"""Plot station dt vs time"""

from datetime import datetime

import tables

from numpy import arange, histogram2d, linspace

from artist import Plot

from sapphire import HiSPARCStations
from sapphire.transformations.clock import datetime_to_gps

STATIONS = [502, 503, 504, 505, 506, 508, 509, 510]
DAY = 86400
HALF_DAY = DAY / 2
WEEK = 7 * DAY
FORTNIGHT = 2 * WEEK
XWEEK = 3 * WEEK
MONTH = 30 * DAY
YEAR = 365 * DAY

SPA_STAT = [501, 502, 503, 504, 505, 506, 508, 509, 510]
CLUSTER = HiSPARCStations(SPA_STAT)

DATA_PATH = '/Users/arne/Datastore/station_offsets/'


def get_station_dt(data, station):
    table = data.get_node('/s%d' % station)
    return table


if __name__ == '__main__':
    t_start = datetime_to_gps(datetime(2010, 1, 1))
    t_end = datetime_to_gps(datetime(2015, 4, 1))

    for i, station in enumerate(STATIONS, 1):
        with tables.open_file(DATA_PATH + 'dt_ref501_%d.h5' % station, 'r') as data:
            distance, _, _ = CLUSTER.calc_rphiz_for_stations(i, 0)
            max_dt = max(distance / .3, 100) * 1.5
            table = get_station_dt(data, station)
            graph = Plot()
            counts, x, y = histogram2d(table.col('timestamp'),
                                       table.col('delta'),
                                       bins=(arange(t_start, t_end, XWEEK),
                                             linspace(-max_dt, max_dt, 150)))
            graph.histogram2d(counts, x, y, bitmap=True, type='color')
            graph.set_ylabel(r'$\Delta t$ [ns]')
            graph.set_xlabel('Timestamp [s]')
            graph.set_xlimits(t_start, t_end)
            graph.set_ylimits(-max_dt, max_dt)
            graph.save_as_pdf('plots/2d_distribution/dt_%d_xweek' % station)
