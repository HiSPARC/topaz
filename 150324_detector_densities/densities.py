import itertools

import numpy as np
from numpy import nan, isnan, arange, histogram, linspace, pi, array, sqrt, degrees
from scipy.optimize import curve_fit
import tables

from artist import Plot, MultiPlot


EVENTDATA_PATH = '/Users/arne/Datastore/501_510/e_501_510_141101_150201.h5'


def plot_densities(data):
    """Make particle count plots for each detector to compare densities/responses"""

    n_min = 0.001  # remove peak at 0
    n_max = 9
    bins = np.linspace(n_min, n_max, 60)

    for station_number in [501, 510]:
        events = data.get_node('/s%d' % station_number, 'events')
        sum_n = events.col('n1') + events.col('n2') + events.col('n3') + events.col('n4')
        n = [events.col('n1'), events.col('n2'), events.col('n3'), events.col('n4')]

        for minn in [0, 1, 2, 4, 8, 16]:
            filter = sum_n > minn
            plot = MultiPlot(4, 4, width=r'.25\linewidth',
                                   height=r'.25\linewidth')
            for i in range(4):
                for j in range(4):
                    if i == j:
                        continue
                    ncounts, x, y = np.histogram2d(n[i].compress(filter),
                                                   n[j].compress(filter),
                                                   bins=bins)
                    subplot = plot.get_subplot_at(i, j)
                    subplot.histogram2d(ncounts, x, y, type='reverse_bw',
                                        bitmap=True)
            plot.set_xlimits_for_all(min=0, max=n_max)
            plot.set_ylimits_for_all(min=0, max=n_max)
            plot.show_xticklabels_for_all([(3, 0), (3, 1), (3, 2), (3, 3)])
            plot.show_yticklabels_for_all([(0, 3), (1, 3), (2, 3), (3, 3)])
        #     plot.set_title(0, 1, 'Particle counts for station 501 and 510')
            for i in range(4):
                plot.set_subplot_xlabel(0, i, 'detector %d' % (i + 1))
                plot.set_subplot_ylabel(i, 0, 'detector %d' % (i + 1))
            plot.set_xlabel('Number of particles')
            plot.set_ylabel('Number of particles')
            plot.save_as_pdf('n_minn%d_%d' % (minn, station_number))


if __name__ == '__main__':
    with tables.open_file(EVENTDATA_PATH, 'r') as data:
        plot_densities(data)