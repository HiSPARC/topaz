import os
import datetime
from urllib2 import urlopen, HTTPError, URLError

import numpy as np
import matplotlib.pyplot as plt
from artist import Plot

from sapphire import Network, Station
from sapphire.utils import pbar

LOCAL_DATA = '/Users/arne/Datastore/publicdb/n_events_day.npz'
TODAY = datetime.date.today()
START = datetime.date(2008, 1, 1)
DATERANGE = [START + datetime.timedelta(days=d)
             for d in range((TODAY-START).days)]


def get_number_of_events(station_number):
    """Get number of events per day for a station

    Then it is divided by the expected number of events per day for a
    station with a certain number of detectors.

    So '1.3' would be on average 30% more events per day than the
    expected number of events per day for such a station.

    If the station can not be found or some other error occurs a list of
    zeroes will be returned.

    :param station_number: The station for which to get the counts.

    """
    try:
        station = Station(station_number)
    except:
        print 'failed to get station info for %d' % station_number
        n_events = [0] * (TODAY-START).days
        return n_events


    if station.n_detectors() == 4:
        # Expected number of events per day for 4 detector station
        scale = 60000.
    else:
        # Expected number of events per day for 2 detector station
        scale = 36000.

    try:
        n_events = [min(station.n_events(d.year, d.month, d.day) / scale, 2)
                    for d in DATERANGE]
    except:
        print ('failed to get event counts for %d, for %d-%d-%d' %
               (station_number, d.year, d.month, d.day))
        n_events = [0] * (TODAY-START).days

    return n_events


def get_and_save_data(station_numbers=None):
    """Get number of events for each station in the list

    Once done the data is saved to a data file.

    :param station_numbers: list of station_number for which to call the
                            `get_number_of_events` function.

    """
    if station_numbers is None:
        station_numbers = Network().station_numbers()
    data = [get_number_of_events(number) for number in pbar(station_numbers)]
    np.savez(LOCAL_DATA, data=data, station_numbers=station_numbers)


def plot_histogram(data, station_numbers):
    """Make a 2D histogram plot of the number of events over time per station

    :param data: list of lists, with the number of events.
    :param station_numbers: list of station numbers in the data list.

    """
    plot = Plot(width=r'\linewidth', height=r'1.35\linewidth')
    plot.histogram2d(data.T, np.arange(len(data[0]) + 1),
                     np.arange(len(station_numbers) + 1),
                     type='reverse_bw', bitmap=True)
#     plot.set_xticks()
#     plot.set_xtick_labels(['%d' % y for y in YEARS])
    plot.set_yticks(np.arange(0.5, len(station_numbers) + 0.5))
    plot.set_ytick_labels(['%d' % s for s in station_numbers], style=r'font=\sffamily\tiny')
    plot.save_as_pdf('all_station_daily_events_day')


if __name__ == "__main__":

    if not os.path.exists(LOCAL_DATA):
        get_and_save_data()

    stored_data = np.load(LOCAL_DATA)
    data = stored_data['data']
    station_numbers = stored_data['station_numbers']
    plot_histogram(data, station_numbers)
