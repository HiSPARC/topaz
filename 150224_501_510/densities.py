import itertools

import numpy as np
from numpy import nan, isnan, arange, histogram, linspace, pi, array, sqrt, degrees
from scipy.optimize import curve_fit
import tables
import matplotlib.pyplot as plt

from artist import Plot, PolarPlot

from sapphire.clusters import HiSPARCStations
from sapphire.analysis.reconstructions import (ReconstructESDEvents,
                                               ReconstructESDCoincidences)

from sapphire.analysis.coincidence_queries import CoincidenceQuery
from sapphire.utils import pbar, gauss, ERR, angle_between


COINDATA_PATH = '/Users/arne/Datastore/501_510/c_501_510_150120_150201.h5'


def plot_densities(data):
    """Make particle count plots for each detector to compare densities/responses"""

    e501 = data.get_node('/hisparc/cluster_amsterdam/station_501', 'events')
    e510 = data.get_node('/hisparc/cluster_amsterdam/station_510', 'events')

    for i in range(1, 5):
        n501 = e501.col('n%d' % i)
        n510 = e510.col('n%d' % i)

        ncounts, x, y = np.histogram2d(n501, n510,
                                       bins=np.linspace(0.2, 10, 80))
        plot = Plot()
        plot.histogram2d(ncounts, x, y, type='reverse_bw', bitmap=True)
        plot.set_xlimits(min=0)
        plot.set_ylimits(min=0)
        plot.set_title('Particle counts for detector %d for station 501 and 510' % i)
        plot.set_xlabel('Number of particles 501')
        plot.set_ylabel('Number of particles 510')
        plot.save_as_pdf('n_501_510_d%d' % i)


    n501 = e501.col('n1') + e501.col('n2') + e501.col('n3') + e501.col('n4')
    n510 = e510.col('n1') + e510.col('n2') + e510.col('n3') + e510.col('n4')

    ncounts, x, y = np.histogram2d(n501, n510,
                                   bins=np.linspace(0, 20, 80))
    plot = Plot()
    plot.histogram2d(ncounts, x, y, type='reverse_bw', bitmap=True)
    plot.set_xlimits(min=0)
    plot.set_ylimits(min=0)
    plot.set_title('Particle counts for station 501 and 510')
    plot.set_xlabel('Number of particles 501')
    plot.set_ylabel('Number of particles 510')
    plot.save_as_pdf('n_501_510_sum')


if __name__ == '__main__':
    with tables.open_file(COINDATA_PATH, 'r') as data:
        plot_densities(data)
