import numpy as np
import tables

from sapphire import download_data
from datetime import datetime

from artist import Plot


EVENTDATA_PATH = '/Users/arne/Datastore/501_510/e_501_510_141101_150201.h5'


def get_data(data):
    download_data(data, '/s1001', 1001,
                  datetime(2015, 3, 1), datetime(2015, 3, 20))


def plot_densities(data):
    """Make particle count plots for each detector to compare densities/responses"""

    n_min = 0.001  # remove peak at 0
    n_max = 9
    bins = np.linspace(n_min, n_max, 80)

    events = data.get_node('/s1001', 'events')
    sum_n = events.col('n1') + events.col('n2')
    n = [events.col('n1'), events.col('n2')]

    for minn in [0, 1, 2, 4, 8, 16]:
        filter = sum_n > minn
        plot = Plot(width=r'.25\linewidth', height=r'.25\linewidth')
        i = 0
        j = 1
        ncounts, x, y = np.histogram2d(n[i].compress(filter),
                                       n[j].compress(filter),
                                       bins=bins)
        plot.histogram2d(ncounts, x, y, type='reverse_bw',
                         bitmap=True)
        plot.set_xlimits(min=0, max=n_max)
        plot.set_ylimits(min=0, max=n_max)
        plot.set_xlabel('Number of particles in detector 1')
        plot.set_ylabel('Number of particles in detector 2')
        plot.save_as_pdf('plots/n_minn%d_1001' % minn)


if __name__ == '__main__':
#     with tables.open_file(EVENTDATA_PATH, 'a') as data:
#         get_data(data)
    with tables.open_file(EVENTDATA_PATH, 'r') as data:
        plot_densities(data)
