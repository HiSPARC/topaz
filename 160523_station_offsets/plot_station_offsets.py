from datetime import date
from itertools import chain

from numpy import array

from artist import MultiPlot

from sapphire import Station
from sapphire.transformations.clock import datetime_to_gps, gps_to_datetime


YEARS = range(2011, date.today().year + 1)
YEARS_TICKS = array([datetime_to_gps(date(y, 1, 1)) for y in YEARS])
YEARS_LABELS = [str(y) for y in YEARS]

STATIONS = [501, 502, 503, 504, 505, 506, 508, 509, 510, 511]


def plot_station_offset_matrix():
    n = len(STATIONS)
    stations = {station: Station(station, force_stale=True)
                for station in STATIONS}

    for type in ['offset']: #, 'rchi2']:
        plot = MultiPlot(n, n, width=r'.08\textwidth', height=r'.08\textwidth')

        for i, station in enumerate(STATIONS):
            for j, ref_station in enumerate(STATIONS):
                splot = plot.get_subplot_at(i, j)
                if i == n:
                    splot.show_xticklabels()
                if station == ref_station:
                    splot.set_empty()
                    splot.set_label(r'%d' % station, location='center')
                    continue
                offsets = stations[station].station_timing_offsets(ref_station)
                bins = list(offsets['timestamp'])
                bins += [bins[-1] + 86400]
                splot.histogram(offsets[type], bins, linestyle='very thin')
                splot.set_axis_options('line join=round')
                plot_cuts_vertically(splot, stations, station, ref_station)

        # Even/row rows/columns
        for row in range(0, n, 2):
            plot.set_yticklabels_position(row, n - 1, 'right')
            plot.set_xticklabels_position(n - 1, row, 'bottom')
            plot.show_yticklabels(row, n - 1)
            #plot.show_xticklabels(n - 1, row)

        for row in range(1, n, 2):
            plot.set_yticklabels_position(row, 0, 'left')
            plot.set_xticklabels_position(0, row, 'top')
            plot.show_yticklabels(row, 0)
            #plot.show_xticklabels(0, row)


        if type == 'offset':
            plot.set_ylimits_for_all(None, min=-70, max=70)
        else:
            plot.set_ylimits_for_all(None, min=0, max=10)
        plot.set_xlimits_for_all(None, min=datetime_to_gps(date(2011, 1, 1)),
                                 max=datetime_to_gps(date.today()))
        plot.set_xticks_for_all(None, YEARS_TICKS)
        # plot.set_xtick_labels_for_all(YEARS_LABELS)

        plot.set_xlabel(r'Date')
        plot.set_ylabel(r'Station offset [\si{\ns}]')

        plot.save_as_pdf('station_offsets_%s' % type)


def plot_cuts_vertically(splot, stations, station, ref_station):
    cuts = {ts for ts in chain(stations[station].gps_locations['timestamp'],
                               stations[station].electronics['timestamp'],
                               stations[ref_station].gps_locations['timestamp'],
                               stations[ref_station].electronics['timestamp'])}
    for cut in cuts:
        splot.draw_vertical_line(cut, linestyle='red, ultra thin')



if __name__ == "__main__":
    plot_station_offset_matrix()
