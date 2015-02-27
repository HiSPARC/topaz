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


STATIONS = [501, 510]
COINDATA_PATH = '/Users/arne/Datastore/501_510/c_501_510_150120_150201.h5'


def plot_angles(data):
    """Make azimuth and zenith plots to compare the results"""

    rec501 = data.get_node('/hisparc/cluster_amsterdam/station_501', 'reconstructions')
    rec510 = data.get_node('/hisparc/cluster_amsterdam/station_510', 'reconstructions')

    zen501 = rec501.col('zenith')
    zen510 = rec510.col('zenith')
    azi501 = rec501.col('azimuth')
    azi510 = rec510.col('azimuth')
    minn501 = rec501.col('min_n')
    minn510 = rec510.col('min_n')

    high_zenith = (zen501 > .2) & (zen510 > .2)
    minn = (minn501 > 2) & (minn510 > 2)

    azicounts, x, y = np.histogram2d(azi501.compress(high_zenith & minn),
                                     azi510.compress(high_zenith & minn),
                                     bins=np.linspace(-pi, pi, 72))
    plot = Plot()
    plot.histogram2d(azicounts, degrees(x), degrees(y), type='reverse_bw', bitmap=True)
    plot.set_title('Reconstructed azimuths for events in coincidence (zenith gt .2 rad)')
    plot.set_xlabel('Azimuth 501 [deg]')
    plot.set_ylabel('Azimuth 510 [deg]')
    plot.save_as_pdf('azimuth_501_510_minn2')

    zencounts, x, y = np.histogram2d(zen501.compress(minn),
                                     zen510.compress(minn),
                                     bins=np.linspace(0, pi / 2., 36))
    plot = Plot()
    plot.histogram2d(zencounts, degrees(x), degrees(y), type='reverse_bw', bitmap=True)
    plot.set_title('Reconstructed zeniths for station events in coincidence')
    plot.set_xlabel('Zenith 501 [deg]')
    plot.set_ylabel('Zenith 510 [deg]')
    plot.save_as_pdf('zenith_501_510_minn2')

    distances = angle_between(azi501.compress(minn), zen501.compress(minn), azi510.compress(minn), zen510.compress(minn))

    counts, bins = np.histogram(distances, bins=linspace(0, pi, 100))
    plot = Plot()
    plot.histogram(counts, degrees(bins))
    plot.set_title('Distance between reconstructed angles for station events in coincidence')
    plot.set_xlabel('Angle between reconstructions [deg]')
    plot.set_ylabel('Counts')
    plot.set_xlimits(min=0, max=180)
    plot.set_ylimits(min=0)
    plot.save_as_pdf('angle_between_501_510_minn2')


if __name__ == '__main__':
    with tables.open_file(COINDATA_PATH, 'r') as data:
        plot_angles(data)
