import datetime

import numpy as np

from artist import Plot

from sapphire import Station
from sapphire.transformations.clock import datetime_to_gps, gps_to_datetime

from .get_aligned_eventtimes import get_aligned, get_station_numbers

YEARS = list(range(2004, datetime.date.today().year + 1))
YEARS_TICKS = np.array([datetime_to_gps(datetime.date(y, 1, 1)) for y in YEARS])
YEARS_LABELS = [str(y) for y in YEARS]


def normalize_event_rates(data, station_numbers):
    """Normalize event rates using the number of detectors

    Number per hour is divided by the expected number of events per hour for a
    station with a certain number of detectors.

    So after this a '1.3' would be on average 30% more events per hour than the
    expected number of events per hour for such a station.

    """
    scaled_data = data.copy()
    for i, s in enumerate(station_numbers):
        n = Station(s).n_detectors()
        if n == 2:
            scaled_data[i] /= 1200.0
        elif n == 4:
            scaled_data[i] /= 2500.0
    scaled_data = np.where(scaled_data > 2.0, 2.0, scaled_data)

    return scaled_data


def plot_histogram(data, timestamps, station_numbers):
    """Make a 2D histogram plot of the number of events over time per station

    :param data: list of lists, with the number of events.
    :param station_numbers: list of station numbers in the data list.

    """
    plot = Plot(width=r'\linewidth', height=r'1.3\linewidth')
    plot.histogram2d(
        data.T[::7][1:], timestamps[::7] / 1e9, np.arange(len(station_numbers) + 1), type='reverse_bw', bitmap=True
    )
    plot.set_label(gps_to_datetime(timestamps[-1]).date().isoformat(), 'upper left')
    plot.set_xlimits(min=YEARS_TICKS[0] / 1e9, max=timestamps[-1] / 1e9)
    plot.set_xticks(YEARS_TICKS / 1e9)
    plot.set_xtick_labels(YEARS_LABELS)
    plot.set_yticks(np.arange(0.5, len(station_numbers) + 0.5))
    plot.set_ytick_labels(['%d' % s for s in sorted(station_numbers)], style=r'font=\sffamily\tiny')
    plot.set_axis_options('ytick pos=right')
    plot.save_as_pdf('eventtime_histogram_network_hour')


if __name__ == "__main__":
    if 'aligned_data_all' not in globals():
        aligned_data, aligned_data_all, first, last = get_aligned()
        station_numbers = get_station_numbers()

    timestamps = np.arange(first, last + 3601, 3600)
    scaled_data = normalize_event_rates(aligned_data_all, station_numbers)
    plot_histogram(scaled_data, timestamps, station_numbers)
