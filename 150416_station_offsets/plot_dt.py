"""Plot station dt vs time"""

import tables
from numpy import histogram2d, linspace, arange
from artist import Plot

from sapphire.clusters import HiSPARCStations

STATIONS = [502, 503, 504, 505, 506, 508, 509, 510]
DAY = 86400
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
    t_start = 1.25e9
    t_end = 1.45e9

    with tables.open_file('dt.h5', 'r') as data:
        for i, station in enumerate(STATIONS, 1):
            distance, _, _ = CLUSTER.calc_rphiz_for_stations(i, 0)
            max_dt = max(distance / .3, 100) * 1.5
            table = get_station_dt(data, station)
            graph = Plot()
            counts, x, y = histogram2d(table.col('timestamp'),
                                       table.col('delta'),
                                       bins=(arange(t_start, t_end, XWEEK),
                                             linspace(-max_dt, max_dt, 100)))
            graph.histogram2d(counts, x, y, bitmap=True, type='coolwarm')
            graph.set_ylabel('$\Delta t$ [ns]')
            graph.set_xlabel('Timestamp [s]')
            graph.set_xlimits(t_start, t_end)
            graph.set_ylimits(-max_dt, max_dt)
            graph.save_as_pdf('dt_%d_xweek' % station)
