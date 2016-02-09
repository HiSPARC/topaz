import os
import datetime
from urllib2 import urlopen, HTTPError, URLError

import numpy as np
import matplotlib.pyplot as plt
from artist import Plot

from sapphire import Network, Station
from sapphire.utils import pbar
from sapphire.transformations.clock import datetime_to_gps

from get_aligned_eventtimes import get_aligned, get_station_numbers


YEARS = range(2004, 2017)
YEARS_TICKS = [datetime_to_gps(datetime.date(y, 1, 1)) for y in YEARS]
YEARS_LABELS = [str(y) for y in YEARS]


def plot_histogram(data, timestamps, station_numbers):
    """Make a 2D histogram plot of the number of events over time per station

    :param data: list of lists, with the number of events.
    :param station_numbers: list of station numbers in the data list.

    """
    plot = Plot(width=r'\linewidth', height=r'1.3\linewidth')
    plot.histogram2d(data.T[::7][:-1], timestamps[::7], np.arange(len(station_numbers) + 1),
                     type='reverse_bw', bitmap=True)
    plot.set_xticks(YEARS_TICKS)
    plot.set_xtick_labels(YEARS_LABELS)
    plot.set_yticks(np.arange(0.5, len(station_numbers) + 0.5))
    plot.set_ytick_labels(['%d' % s for s in sorted(station_numbers)], style=r'font=\sffamily\tiny')
    plot.save_as_pdf('all_station_daily_events_day')


if __name__ == "__main__":
    if 'aligned_data_all' not in globals():
        aligned_data, aligned_data_all, first, last = get_aligned()
        station_numbers = get_station_numbers()

    timestamps = range(first, last + 3601, 3600)

    plot_histogram(aligned_data, timestamps, station_numbers)
