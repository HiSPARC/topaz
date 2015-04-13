from calendar import monthrange
import os
import datetime

import numpy as np
import matplotlib.pyplot as plt
from artist import Plot

from sapphire.api import Network, Station
from sapphire.utils import pbar

LOCAL_DATA = '/Users/arne/Datastore/publicdb/n_events.npy'
TODAY = datetime.date.today()
YEARS = np.arange(2004, TODAY.year + 1)
MONTHS = np.arange(12) + 1


def get_number_of_events(station_number):
    """Get number of events per month for a station

    The number is divided by the number of days in that month, to get
    the average number of events per day that month. Then it is divided
    by the expected number of events per day for a station with a
    certain number of detectors.

    So '1.3' would be on average 30% more events per day than the
    expected number of events per day for such a station in that month.

    If the station can not be found or some other error occurs a list of
    zeroes will be returned.

    :param station_number: The station for which to get the counts.

    """
    try:
        station = Station(station_number)
        if station.n_detectors() == 4:
            # Expected number of events per day for 4 detector station
            scale = 60000.
        else:
            # Expected number of events per day for 2 detector station
            scale = 36000.
        n_events = [station.n_events(year, month) /
                    (monthrange(year, month)[1] * scale)
                    for year in YEARS for month in MONTHS
                    if not (year == TODAY.year and month >= TODAY.month)]
    except:
        n_events = [0] * ((len(YEARS) * 12) - (13 - TODAY.month))

    return n_events


def get_and_save_data(station_numbers):
    """Get number of events for each station in the list

    Once done the data is saved to a data file.

    :param station_numbers: list of station_number for which to call the
                            `get_number_of_events` function.

    """
    data = [get_number_of_events(number) for number in pbar(station_numbers)]
    np.savez(LOCAL_DATA, data=data, station_numbers=station_numbers)


def plot_histogram(data, station_numbers):
    """Make a 2D histogram plot of the number of events over time per station

    :param data: list of lists, with the number of events.
    :param station_numbers: list of station numbers in the data list.

    """
    f = plt.figure(figsize=(11, 12), facecolor='none', edgecolor='none')
    ax = f.add_subplot(111)
    ax.yaxis.tick_right()
    plt.imshow(data, interpolation='nearest', cmap=plt.get_cmap('Greys'),
               vmin=0, vmax=2)
    plt.yticks(np.arange(len(station_numbers)), station_numbers,
               size='xx-small')
    plt.xticks((YEARS - YEARS[0]) * 12, YEARS, size='x-small')
    plt.title("Fraction of expected number of events per month" %
              (YEARS[0], YEARS[-1]))
    plt.savefig('all_station_daily_events_month.pdf', facecolor='none',
                edgecolor='none')


if __name__ == "__main__":
    network = Network()
    station_numbers = network.stations_numbers()

    if not os.path.exists(LOCAL_DATA):
        get_and_save_data(station_numbers)

    stored_data = np.load(LOCAL_DATA)
    data = stored_data['data']
    station_numbers = stored_data['station_numbers']
    plot_histogram(data, station_numbers)
