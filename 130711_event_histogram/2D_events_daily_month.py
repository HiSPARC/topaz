from calendar import monthrange
import os

import numpy as np
import matplotlib.pyplot as plt
import progressbar

from sapphire.api import Network, Station


LOCAL_DATA = '/Users/arne/Datastore/publicdb/n_events.npy'
YEARS = np.arange(2004, 2015)
MONTHS = np.arange(12) + 1


def get_number_of_events(station_number):
    try:
        station = Station(station_number)
        n_events = [station.n_events(year, month) / monthrange(year, month)[1]
                    for year in YEARS for month in MONTHS
                    if not (year == 2014 and month > 6)]
    except:
        n_events = [0
                    for year in YEARS for month in MONTHS
                    if not (year == 2014 and month > 6)]

    return n_events


def get_and_save_data(station_numbers):
    data = [get_number_of_events(number) for number in pbar(station_numbers)]
    np.save(LOCAL_DATA, data)


def pbar(iterator):
    """Get a new progressbar with our default widgets"""

    pb = progressbar.ProgressBar(widgets=[progressbar.ETA(), progressbar.Bar(),
                                          progressbar.Percentage()])
    return pb(iterator)


if __name__=="__main__":
    network = Network()
    station_numbers = network.stations_numbers()

    if not os.path.exists(LOCAL_DATA):
        get_and_save_data(station_numbers)

    data = np.load(LOCAL_DATA)

    f = plt.figure(figsize=(11, 12), facecolor='none', edgecolor='none')
    ax = f.add_subplot(111)
    ax.yaxis.tick_right()
    plt.imshow(data, interpolation='nearest', cmap=plt.get_cmap('Greys'),
               vmin=0, vmax=120000)
    plt.yticks(np.arange(len(station_numbers)), station_numbers, size='xx-small')
    plt.xticks((YEARS - YEARS[0]) * 12, YEARS, size='x-small')
    plt.title("Average daily number of events per month between %d and %d," %
              (YEARS[0], YEARS[-1]))
    plt.savefig('/Users/arne/Datastore/publicdb/all_station_daily_events_month.pdf',
                facecolor='none', edgecolor='none')
