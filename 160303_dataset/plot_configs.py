from datetime import date

from numpy import array

from artist import MultiPlot

from sapphire import Station
from sapphire.transformations.clock import datetime_to_gps

from download_dataset import STATIONS, START, END


# STATIONS = STATIONS[-2:]
START_TS = datetime_to_gps(date(*START, day=1))
END_TS = datetime_to_gps(date(*END, day=1))
COLORS = ['black', 'red', 'green', 'blue']

YEARS = range(2011, date.today().year + 1)
YEARS_TICKS = array([datetime_to_gps(date(y, 1, 1)) for y in YEARS])
YEARS_LABELS = [str(y) for y in YEARS]

FIELDS = ['voltages', 'currents', 'detector_timing_offsets']
FIELD_NAMES = ['voltage%d', 'current%d', 'offset%d']


def get_all_configs():
    stats = {}
    for station in STATIONS:
        stats[station] = {}
        s = Station(station, force_stale=True)
        for field in FIELDS:
            timestamps = s.__getattribute__(field)['timestamp']
            filter = (timestamps >= START_TS) & (timestamps < END_TS)
            stats[station][field] = s.__getattribute__(field).compress(filter)
    return stats


def plot_configs_timeline(stats, field, field_name):
    step = 86400  # one day
    plot = MultiPlot(len(STATIONS), 1,
                     width=r'.67\textwidth', height=r'.05\paperheight')
    for splot, station in zip(plot.subplots, STATIONS):
        config = stats[station][field]
        for i in range(4):
            timestamps = list(config['timestamp'] + (i * step))
            timestamps.append(END_TS)
            splot.histogram(config[field_name % (i + 1)],
                            timestamps,
                            linestyle=COLORS[i])
        splot.set_ylabel(r'%d' % station)

    plot.set_xlimits_for_all(None, min=START_TS, max=END_TS)
    plot.set_xticks_for_all(None, YEARS_TICKS)
    plot.subplots[-1].set_xtick_labels(YEARS_LABELS)
    plot.subplots[-1].show_xticklabels()

    plot.show_yticklabels_for_all(None)
    for row in range(0, len(plot.subplots), 2):
        plot.set_yticklabels_position(row, 0, 'left')
    for row in range(1, len(plot.subplots), 2):
        plot.set_yticklabels_position(row, 0, 'right')

    if field == 'voltages':
        plot.set_ylimits_for_all(None, 300)
        plot.set_ylabel(r'PMT voltage \si{\volt}')
    elif field == 'currents':
        plot.set_ylimits_for_all(None, 0)
        plot.set_ylabel(r'PMT current \si{\milli\volt}')
    elif field == 'detector_timing_offsets':
        plot.set_ylabel(r'Detector timing offsets \si{\ns}')

    plot.set_xlabel(r'Timestamp')
    plot.save_as_pdf('plots/config_%s' % field)


def plot_configs_timelines(configs):
    for field, field_name in zip(FIELDS, FIELD_NAMES):
        plot_configs_timeline(configs, field, field_name)


if __name__ == "__main__":

    configs = get_all_configs()

    plot_configs_timelines(configs)
